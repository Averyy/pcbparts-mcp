#!/usr/bin/env python3
"""Strip IMPORTANT NOTICE boilerplate blocks from raw_sources/*.md files.

Handles two cases:
1. Notice at END of file → truncate at the notice heading
2. Notice at BEGINNING → remove just the notice block, keep content after

Detection: if >50% of non-frontmatter content comes after the notice, it's a
beginning notice (remove block). Otherwise it's an end notice (truncate).

The notice block ends at the next markdown heading (# at start of line) or at
a line matching common post-notice markers (Contents, Copyright, Mailing Address).
"""

import re
import sys
from pathlib import Path

RAW_SOURCES = Path(__file__).resolve().parent.parent / "raw_sources"

NOTICE_RE = re.compile(r'^#{1,6}\s*(?:<[^>]+>\s*)*\**\s*IMPORTANT NOTICE', re.IGNORECASE)
HEADING_RE = re.compile(r'^#{1,6}\s+')


def find_notice_block(lines: list[str]) -> tuple[int, int] | None:
    """Find the start and end line indices of the IMPORTANT NOTICE block.

    Returns (start, end) where start is the notice heading line and end is
    the line AFTER the last line of the notice block (i.e., lines[start:end]
    is the block to remove).
    """
    # Find the notice heading
    notice_idx = None
    for i, line in enumerate(lines):
        if NOTICE_RE.match(line.strip()):
            notice_idx = i
            break

    if notice_idx is None:
        return None

    # Find end of notice block: look for next markdown heading after the notice
    # Skip blank lines and legal paragraphs
    block_end = len(lines)  # default: goes to end of file
    for i in range(notice_idx + 1, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        # A new markdown heading that ISN'T another notice variant
        if HEADING_RE.match(line) and 'IMPORTANT NOTICE' not in line.upper():
            block_end = i
            break

    # Also eat any trailing blank lines before the next content
    # (go backwards from block_end to trim trailing blanks of the notice)
    # Actually, let's also eat leading blank lines before the notice heading
    start = notice_idx
    while start > 0 and lines[start - 1].strip() == '':
        start -= 1

    return (start, block_end)


def process_file(path: Path, dry_run: bool = False) -> dict:
    """Process a single file. Returns info dict."""
    text = path.read_text()
    lines = text.split('\n')

    result = find_notice_block(lines)
    if result is None:
        return {"file": str(path), "action": "no-notice"}

    start, end = result

    # Split into frontmatter and content
    # Find the closing --- of YAML frontmatter
    fm_end = 0
    if lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                fm_end = i + 1
                break

    content_before = lines[fm_end:start]
    notice_block = lines[start:end]
    content_after = lines[end:]

    chars_before = sum(len(l) for l in content_before)
    chars_after = sum(len(l) for l in content_after)

    # Decide: truncate vs remove block
    if chars_after > chars_before:
        # Beginning notice — remove block, keep both sides
        action = "remove-block"
        new_content_lines = lines[:start] + lines[end:]
    else:
        # End notice — truncate
        action = "truncate"
        new_content_lines = lines[:start]

    # Strip trailing blank lines
    while new_content_lines and new_content_lines[-1].strip() == '':
        new_content_lines.pop()

    # Recalculate chars for frontmatter
    new_text = '\n'.join(new_content_lines) + '\n'

    # Extract content after frontmatter for char count
    content_for_chars = '\n'.join(new_content_lines[fm_end:])
    new_chars = len(content_for_chars)

    # Update chars: in frontmatter
    new_text = re.sub(r'^(chars:\s*)\d+', f'\\g<1>{new_chars}', new_text, count=1, flags=re.MULTILINE)

    removed_chars = len(text) - len(new_text)
    removed_lines = len(notice_block)

    if not dry_run:
        path.write_text(new_text)

    return {
        "file": path.name,
        "action": action,
        "notice_at_line": start + 1,
        "block_lines": removed_lines,
        "chars_removed": removed_chars,
        "new_chars": new_chars,
    }


def main():
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    # Find all files with IMPORTANT NOTICE
    files = []
    for md in sorted(RAW_SOURCES.rglob('*.md')):
        text = md.read_text()
        if 'IMPORTANT NOTICE' in text:
            files.append(md)

    if not files:
        print("No files with IMPORTANT NOTICE found.")
        return

    print(f"{'[DRY RUN] ' if dry_run else ''}Processing {len(files)} files...\n")

    total_removed = 0
    for f in files:
        info = process_file(f, dry_run=dry_run)
        if info["action"] == "no-notice":
            print(f"  SKIP  {info['file']} (no notice heading found)")
        else:
            rel = f.relative_to(RAW_SOURCES)
            action_str = "BLOCK-RM" if info["action"] == "remove-block" else "TRUNCATE"
            print(f"  {action_str:8s} {rel}  (line {info['notice_at_line']}, "
                  f"-{info['block_lines']} lines, -{info['chars_removed']} chars)")
            total_removed += info["chars_removed"]

    print(f"\nTotal: {len(files)} files, {total_removed} chars removed")
    if dry_run:
        print("(dry run — no files modified)")


if __name__ == "__main__":
    main()
