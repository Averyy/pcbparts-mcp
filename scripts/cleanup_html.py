#!/usr/bin/env python3
"""Clean HTML-extracted source files: strip product listings, site chrome, etc.

Targets SparkFun and Adafruit-specific noise patterns in readability-extracted files.
"""

import re
import sys
from pathlib import Path

RAW_SOURCES = Path(__file__).resolve().parent.parent / "raw_sources"


def strip_sparkfun_products(text: str) -> tuple[str, int]:
    """Remove SparkFun product listing blocks.

    Pattern: ### Product Name\n\nSKU-CODE\n\nDescription...\n\n[**Retired**]
    SKU codes match: PRT-xxxxx, BOB-xxxxx, COM-xxxxx, CAB-xxxxx, WRL-xxxxx,
                     GPS-xxxxx, TOL-xxxxx, DEV-xxxxx, SEN-xxxxx, KIT-xxxxx,
                     PGM-xxxxx, LCD-xxxxx, ROB-xxxxx
    """
    count = 0
    SKU = r'(?:PRT|BOB|COM|CAB|WRL|GPS|TOL|DEV|SEN|KIT|PGM|LCD|ROB)-\d{4,6}'

    # Match heading + SKU + description + optional Retired (any heading level)
    # Also handle indented product blocks (inside list items)
    pattern = re.compile(
        r'\n\s*#{2,4} [^\n]+\n\n'     # ## or ### or #### Product Name
        r'\s*' + SKU + r'\n\n'        # SKU code
        r'[^\n]+(?:\n[^\n]+)*?'       # Description (may wrap)
        r'(?:\n\n\s*\*\*Retired\*\*)?' # Optional Retired tag
        r'(?=\n\n|\n\s*#|\Z)',        # Lookahead: next block
        re.MULTILINE
    )
    text, n = pattern.subn('\n', text)
    count += n
    return text, count


def strip_sparkfun_going_further(text: str) -> tuple[str, int]:
    """Remove 'Resources and Going Further' sections."""
    pattern = re.compile(
        r'\n## Resources and Going Further\n.*',
        re.DOTALL
    )
    text, n = pattern.subn('\n', text)
    return text, n


def strip_sparkfun_promos(text: str) -> tuple[str, int]:
    """Remove SparkFun promotional blocks."""
    count = 0

    # "Looking to explore different X?" blocks
    pattern = re.compile(
        r'\n## Looking to explore[^\n]*\n\nWe\'ve got you covered!\n',
        re.MULTILINE
    )
    text, n = pattern.subn('\n', text)
    count += n

    # "Expecting a Pay Wall?" blocks
    pattern = re.compile(
        r'\n\*\*Heads up!\*\*\n\nExpecting a Pay Wall\?[^\n]*\n',
        re.MULTILINE
    )
    text, n = pattern.subn('\n', text)
    count += n

    # "Add it to your cart" shopping language lines
    pattern = re.compile(
        r'\n[^\n]*Add it to your cart[^\n]*\n',
        re.MULTILINE
    )
    text, n = pattern.subn('\n', text)
    count += n

    # "If you are looking for..." buying guide lines
    pattern = re.compile(
        r'\n(?:If you are looking for|check out our)[^\n]*(?:Buying Guide|catalog)[^\n]*\n',
        re.MULTILINE
    )
    text, n = pattern.subn('\n', text)
    count += n

    # "Need Help?" support boilerplate (both ### and ** variants)
    pattern = re.compile(
        r'\n(?:###\s*)?\*?\*?Need Help\??\*?\*?\n.*?(?=\n## |\Z)',
        re.DOTALL
    )
    text, n = pattern.subn('\n', text)
    count += n

    # Contributor attribution blocks at start of file (after frontmatter)
    # Pattern: "Contributors:\n\n Name\n\n,\n\n Name\n\n"
    pattern = re.compile(
        r'(?<=---\n)Contributors:\n(?:\n\s*\w[\w -]*\n\n,?\n?)*',
        re.MULTILINE
    )
    text, n = pattern.subn('', text)
    count += n

    # Standalone contributor fragments: ", bitsmashed" at start
    pattern = re.compile(r'(?<=---\n),\s*\n\n\s*\w+\n\n', re.MULTILINE)
    text, n = pattern.subn('', text)
    count += n

    # Qwiic Connect System marketing blocks (## or ### heading)
    pattern = re.compile(
        r'\n#{2,3}\s*(?:The\s+)?Qwiic Connect System\n.*?(?=\n## |\Z)',
        re.DOTALL
    )
    text, n = pattern.subn('\n', text)
    count += n

    return text, count


def strip_adafruit_noise(text: str) -> tuple[str, int]:
    """Remove Adafruit-specific noise."""
    count = 0

    # "Page last edited" + "Text editor powered by tinymce"
    pattern = re.compile(
        r'\nPage last edited[^\n]*\n\nText editor powered by \[tinymce\]\([^\)]*\)\.\n',
        re.MULTILINE
    )
    text, n = pattern.subn('\n', text)
    count += n

    # Related Guides sections
    pattern = re.compile(r'\nRelated Guides\n.*', re.DOTALL)
    text, n = pattern.subn('\n', text)
    count += n

    return text, count


def strip_horizontal_rules_between_removed(text: str) -> tuple[str, int]:
    """Remove orphaned horizontal rules (---) that separated product blocks."""
    # Remove --- lines that are alone between blank lines
    pattern = re.compile(r'\n\n---\n\n(?=\n|\Z)')
    text, n = pattern.subn('\n\n', text)
    return text, n


def collapse_blank_lines(text: str) -> str:
    """Collapse 3+ consecutive blank lines to 2."""
    return re.sub(r'\n{4,}', '\n\n\n', text)


def update_char_count(text: str) -> str:
    """Update the chars field in YAML frontmatter (content after frontmatter only)."""
    # Count only content after closing --- of frontmatter
    lines = text.split('\n')
    fm_end = 0
    if lines and lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                fm_end = i + 1
                break
    content = '\n'.join(lines[fm_end:])
    actual = len(content)
    return re.sub(r'(chars:\s*)\d+', rf'\g<1>{actual}', text, count=1)


def process_file(path: Path, dry_run: bool = False) -> dict:
    """Process a single file. Returns dict of changes made."""
    text = path.read_text()
    original_len = len(text)
    changes = {}

    # SparkFun patterns
    text, n = strip_sparkfun_products(text)
    if n: changes['products_removed'] = n

    text, n = strip_sparkfun_going_further(text)
    if n: changes['going_further_removed'] = n

    text, n = strip_sparkfun_promos(text)
    if n: changes['promos_removed'] = n

    # Adafruit patterns
    text, n = strip_adafruit_noise(text)
    if n: changes['adafruit_noise_removed'] = n

    # Cleanup
    text, n = strip_horizontal_rules_between_removed(text)
    if n: changes['orphan_rules_removed'] = n

    text = collapse_blank_lines(text)
    text = update_char_count(text)

    new_len = len(text)
    if new_len != original_len:
        changes['chars_removed'] = original_len - new_len
        if not dry_run:
            path.write_text(text)

    return changes


def main():
    dry_run = '--dry-run' in sys.argv

    # Process all readability-extracted files
    total_changes = 0
    for path in sorted(RAW_SOURCES.rglob("*.md")):
        text = path.read_text()
        if 'method: "readability"' not in text[:500]:
            continue

        changes = process_file(path, dry_run=dry_run)
        if changes:
            rel = path.relative_to(RAW_SOURCES)
            print(f"  {rel}: {changes}")
            total_changes += 1

    action = "would change" if dry_run else "changed"
    print(f"\n{action} {total_changes} files")


if __name__ == "__main__":
    main()
