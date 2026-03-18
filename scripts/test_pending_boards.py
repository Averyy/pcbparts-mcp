#!/usr/bin/env python3
"""Test-parse boards from BOARDS-pending.md without modifying BOARDS.md.

Reads pending board entries, clones repos, runs the parser in dry-run mode,
and reports which boards produce good output vs failures.

Usage:
    uv run python scripts/test_pending_boards.py
    uv run python scripts/test_pending_boards.py --board "TPA3255 PBTL"
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

# Ensure scripts/ is on sys.path
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from parse_boards import process_board, clone_repo, parse_boards_md

ROOT = Path(__file__).resolve().parent.parent
PENDING_MD = ROOT / "data" / "boards" / "BOARDS-pending.md"

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def parse_pending_md(path: Path) -> list[dict]:
    """Parse BOARDS-pending.md table rows into board info dicts."""
    boards = []
    text = path.read_text()

    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("| Board") or line.startswith("|---"):
            continue

        cols = [c.strip() for c in line.split("|")]
        # cols[0] is empty (before first |), cols[-1] is empty (after last |)
        if len(cols) < 7:
            continue

        name = cols[1]
        org = cols[2]
        repo = cols[3].strip("`")
        fmt = cols[4].lower()
        sch_path = cols[5]
        key_coverage = cols[6]

        # Clean up schematic path — strip sheet count annotations
        sch_path = re.sub(r"\s*\(.*?\)\s*$", "", sch_path).strip("`").strip()
        # If multiple paths (+ separated), take the first one
        if " + " in sch_path:
            sch_path = sch_path.split(" + ")[0].strip("`").strip()

        boards.append({
            "name": name,
            "repo": repo,
            "format": fmt,
            "schematic_path": sch_path,
            "key_coverage": key_coverage,
        })

    return boards


def main():
    parser = argparse.ArgumentParser(description="Test-parse pending boards")
    parser.add_argument("--board", help="Only test a specific board (substring match on name)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    boards = parse_pending_md(PENDING_MD)
    if not boards:
        print("No boards found in BOARDS-pending.md")
        return

    if args.board:
        boards = [b for b in boards if args.board.lower() in b["name"].lower()]
        if not boards:
            print(f"No board matching '{args.board}'")
            return

    print(f"Testing {len(boards)} pending boards...\n")

    results = {"pass": [], "fail": [], "error": []}

    for info in boards:
        name = info["name"]
        fmt = info["format"]
        repo = info["repo"]

        try:
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            board = process_board(slug, info, dry_run=True)

            if board is None:
                results["fail"].append((name, repo, "parser returned None"))
                print(f"  FAIL  {name} — parser returned None")
            elif len(board.components) < 3:
                results["fail"].append((name, repo, f"only {len(board.components)} components"))
                print(f"  FAIL  {name} — only {len(board.components)} components")
            elif len(board.nets) == 0 and len(board.components) > 10:
                results["fail"].append((name, repo, f"{len(board.components)} components but 0 nets"))
                print(f"  WARN  {name} — {len(board.components)} components but 0 nets")
            else:
                results["pass"].append((name, repo, len(board.components), len(board.nets), len(board.positions)))
                print(f"  OK    {name} — {len(board.components)} components, {len(board.nets)} nets, {len(board.positions)} positions")

        except Exception as e:
            results["error"].append((name, repo, str(e)))
            print(f"  ERROR {name} — {e}")

    # Summary
    print(f"\n{'='*60}")
    print(f"PASSED: {len(results['pass'])}")
    print(f"FAILED: {len(results['fail'])}")
    print(f"ERRORS: {len(results['error'])}")

    if results["fail"]:
        print(f"\nFailed boards:")
        for name, repo, reason in results["fail"]:
            print(f"  - {name} ({repo}): {reason}")

    if results["error"]:
        print(f"\nErrored boards:")
        for name, repo, reason in results["error"]:
            print(f"  - {name} ({repo}): {reason}")


if __name__ == "__main__":
    main()
