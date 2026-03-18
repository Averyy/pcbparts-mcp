#!/usr/bin/env python3
"""Extract and clean text from design rule source URLs.

Fetches HTML pages (strongly preferred) and PDFs (via pdfplumber),
strips boilerplate, cleans extraction artifacts, and outputs clean
markdown suitable for LLM consumption.

Extracted files are saved to raw_sources/ with stable, human-readable
filenames derived from the source name. Already-extracted sources are
skipped (additive — only new sources get fetched).

Usage:
    # Extract all sources for a topic (skips existing)
    python scripts/extract_source.py --topic i2c

    # Extract all sources for all topics
    python scripts/extract_source.py --all

    # Re-extract even if files exist
    python scripts/extract_source.py --topic ldo --force

    # Show what would be extracted (dry run)
    python scripts/extract_source.py --topic ldo --dry-run

    # Extract only HTML sources (skip PDFs)
    python scripts/extract_source.py --all --html-only

    # Extract PDF batch 3 of 10 (balanced by page count)
    python scripts/extract_source.py --batch 3/10

    # Dry-run a batch to see which PDFs it contains
    python scripts/extract_source.py --batch 3/10 --dry-run

    # Extract a single URL (prints to stdout)
    python scripts/extract_source.py "https://www.ti.com/lit/an/slva689/slva689.pdf"
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wafer import SyncSession

# Paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = PROJECT_ROOT / "design-rules" / "verified-sources.md"
RAW_SOURCES_DIR = PROJECT_ROOT / "raw_sources"


# ---------------------------------------------------------------------------
# Boilerplate patterns to strip
# ---------------------------------------------------------------------------

# TI "IMPORTANT NOTICE" page — appears at end of every TI app note/datasheet
TI_NOTICE_PATTERNS = [
    # Full-page notice block
    re.compile(
        r"IMPORTANT NOTICE FOR TI DESIGN INFORMATION AND RESOURCES.*",
        re.DOTALL | re.IGNORECASE,
    ),
    # Shorter variant
    re.compile(
        r"IMPORTANT NOTICE AND DISCLAIMER.*",
        re.DOTALL | re.IGNORECASE,
    ),
    # TI standard footer
    re.compile(
        r"TEXAS INSTRUMENTS INCORPORATED.*?(?:Dallas,? Texas|www\.ti\.com)\s*$",
        re.DOTALL | re.IGNORECASE | re.MULTILINE,
    ),
]

# ST legal boilerplate
ST_NOTICE_PATTERNS = [
    re.compile(
        r"IMPORTANT NOTICE – PLEASE READ CAREFULLY.*",
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        r"STMicroelectronics NV and its subsidiaries.*?(?:Geneva|Switzerland)\s*$",
        re.DOTALL | re.IGNORECASE | re.MULTILINE,
    ),
]

# ADI / Analog Devices
ADI_NOTICE_PATTERNS = [
    re.compile(
        r"©\s*\d{4}\s*Analog Devices,?\s*Inc\.?\s*All rights reserved\..*",
        re.DOTALL | re.IGNORECASE,
    ),
]

# Infineon
INFINEON_NOTICE_PATTERNS = [
    re.compile(
        r"IMPORTANT NOTICE.*?Infineon Technologies AG.*",
        re.DOTALL | re.IGNORECASE,
    ),
]

# NXP / Nexperia
NXP_NOTICE_PATTERNS = [
    re.compile(
        r"IMPORTANT NOTICE.*?NXP Semiconductors.*",
        re.DOTALL | re.IGNORECASE,
    ),
]

# ON Semi
ONSEMI_NOTICE_PATTERNS = [
    re.compile(
        r"onsemi.*?PUBLICATION ORDERING INFORMATION.*",
        re.DOTALL | re.IGNORECASE,
    ),
]

# Generic markdown-heading variant
# Catches: #### **IMPORTANT NOTICE**, #### <span>**IMPORTANT NOTICE – READ CAREFULLY**, etc.
GENERIC_NOTICE_PATTERNS = [
    re.compile(
        r"#{1,6}\s*(?:<[^>]+>\s*)*\**\s*IMPORTANT NOTICE.*",
        re.DOTALL | re.IGNORECASE,
    ),
]

ALL_BOILERPLATE_PATTERNS = (
    GENERIC_NOTICE_PATTERNS
    + TI_NOTICE_PATTERNS
    + ST_NOTICE_PATTERNS
    + ADI_NOTICE_PATTERNS
    + INFINEON_NOTICE_PATTERNS
    + NXP_NOTICE_PATTERNS
    + ONSEMI_NOTICE_PATTERNS
)

# Known TI docs with HTML document viewer versions (auto-discovered at runtime too).
# Policy: HTML is strongly preferred over PDF. The extractor always probes for HTML
# first via the ti.com/document-viewer/lit/html/{DOCID} pattern; this set is informational only.
TI_HTML_KNOWN = {
    "SLVA689", "SLVA704", "SLVAE57B", "SCEA135", "SLYY109B",
}


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------


def strip_boilerplate(text: str) -> str:
    """Remove known manufacturer boilerplate from extracted text.

    Safety: boilerplate patterns use re.DOTALL and match everything to EOF.
    Only applies a pattern if the match starts after 40% of the document,
    preventing catastrophic content loss when notices appear early
    (e.g., TI SZZA009 has IMPORTANT NOTICE on page 2 of 23).
    """
    min_pos = int(len(text) * 0.4)
    for pattern in ALL_BOILERPLATE_PATTERNS:
        m = pattern.search(text)
        if m and m.start() >= min_pos:
            text = pattern.sub("", text)
    return text


# TI page header/footer lines (www.ti.com SectionTitle)
_TI_HEADER_PLAIN_RE = re.compile(
    r"^(?:www\.ti\.com\s+\S.*|.*\S\s+www\.ti\.com)$",
    re.MULTILINE,
)

# ST page footer lines — handles plain, bold, and markdown link page numbers
_ST_FOOTER_RE = re.compile(
    r"^"
    r"\*?\*?AN\d+\*?\*?"
    r"\s*[-:]?\s*"
    r"Rev\.?\s*\d+"
    r"(?:"
    r"\s+(?:page\s*)?"
    r"\d+/"
    r"(?:\[\d+\]\([^)]*\)|\d+)"
    r")?"
    r"\s*$",
    re.MULTILINE | re.IGNORECASE,
)

# ST page header lines (standalone bold lines like **AN2867 List of figures**)
_ST_HEADER_RE = re.compile(
    r"^\*\*AN\d+\s+[A-Z][^*]+\*\*\s*$",
    re.MULTILINE,
)

# Trademark boilerplate (universal — appears in TI, ST, NXP docs)
_TRADEMARK_RE = re.compile(
    r"(?:^#*\s*\*?\*?(?:\d+\.\d+\s+)?Trademarks\*?\*?\s*\n+)?"
    r"(?:^[^\n]{0,120}registered trademark[^\n]*\n)*"
    r"^All trademarks are the property of their respective owners\.?\s*$",
    re.MULTILINE,
)

# VIDEO placeholder lines from HTML extraction
_VIDEO_RE = re.compile(r"^VIDEO\s*$", re.MULTILINE)

# WHITE PAPER labels
_WHITE_PAPER_RE = re.compile(r"^WHITE PAPER\s*$", re.MULTILINE)

# TI support boilerplate (end-of-document)
_TI_SUPPORT_RE = re.compile(
    r"^#{1,4}\s*\*?TI Worldwide Technical Support\*?\s*\n.*",
    re.MULTILINE | re.DOTALL,
)

# Revision History sections (end-of-document)
_REVISION_HISTORY_RE = re.compile(
    r"^#{1,6}\s*\*?\*?(?:(?:\d+\.?\s+)|(?:Appendix\s+\w+\s*[-–:]\s*(?:Application Note\s+)?))?Revision History\*?\*?\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def _strip_repeated_headers(text: str) -> str:
    """Remove lines that appear 3+ times (page headers/footers extracted as content).

    Handles both markdown headings (## Title) and plain-text repeated lines
    from pdfplumber extraction. Keeps the first occurrence.
    """
    from collections import Counter

    lines = text.split("\n")

    # Count short non-empty lines (page headers are typically short)
    line_counts: Counter[str] = Counter()
    for line in lines:
        s = line.strip()
        if s and len(s) < 100:  # noqa: PLR2004
            norm = re.sub(r"\*\*", "", s).strip()
            line_counts[norm] += 1

    repeated = {h for h, c in line_counts.items() if c >= 3}
    if not repeated:
        return text

    seen: set[str] = set()
    new_lines = []
    for line in lines:
        s = line.strip()
        if s and len(s) < 100:  # noqa: PLR2004
            norm = re.sub(r"\*\*", "", s).strip()
            if norm in repeated:
                if norm in seen:
                    continue
                seen.add(norm)
        new_lines.append(line)
    return "\n".join(new_lines)


def clean_text(text: str) -> str:
    """Light cleanup on extracted text. Safe for all extraction methods."""
    # Strip trademark boilerplate (universal across vendors)
    text = _TRADEMARK_RE.sub("", text)

    # Strip standalone VIDEO placeholder lines (HTML extraction artifact)
    text = _VIDEO_RE.sub("", text)

    # Strip WHITE PAPER labels (Vishay)
    text = _WHITE_PAPER_RE.sub("", text)

    # Strip TI support boilerplate (end-of-document)
    m = _TI_SUPPORT_RE.search(text)
    if m:
        text = text[:m.start()].rstrip()

    # Strip Revision History sections (end-of-document, no design value)
    m = _REVISION_HISTORY_RE.search(text)
    if m:
        after = text[m.end():]
        heading_after = re.search(r"^#{1,6}\s+(?!\*?\*?(?:Appendix|Revision))", after, re.MULTILINE)
        if heading_after:
            text = text[:m.start()].rstrip() + text[m.end() + heading_after.start():]
        else:
            text = text[:m.start()].rstrip()

    # Collapse double blank lines to single (saves LLM tokens, no semantic difference)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # Strip <br> tags outside markdown table rows (HTML artifacts)
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        if not line.strip().startswith("|"):
            line = re.sub(r"<br\s*/?>", "", line, flags=re.IGNORECASE)
        cleaned.append(line)
    text = "\n".join(cleaned)

    return text.strip()


@dataclass
class ExtractionResult:
    """Result of extracting content from a URL."""
    text: str
    method: str  # ti-html | readability | pdfplumber | raw-md


def _preprocess_html(html: str) -> str:
    """Pre-process HTML before readability extraction.

    Fixes known issues:
    - Unwraps <a> tags inside headings (Altium wraps headings in <a id="...">
      which readability strips, losing section headers entirely).
    """
    # Unwrap <a> tags inside headings: <h2><a id="foo">Text</a></h2> → <h2>Text</h2>
    html = re.sub(
        r"(<h[1-6][^>]*>)\s*<a[^>]*>(.*?)</a>\s*(</h[1-6]>)",
        r"\1\2\3",
        html,
        flags=re.DOTALL,
    )
    return html


def _extract_html_content(html: str, *, url: str = "") -> str | None:
    """Extract main content from HTML to clean markdown.

    Uses readability-lxml (Mozilla Readability algorithm) for article extraction
    then markdownify to convert to markdown with proper headers, tables, bold,
    lists, and code blocks.

    Requires: pip install readability-lxml markdownify
    """
    from readability import Document
    from markdownify import markdownify

    # Strip null bytes / control chars that crash lxml (binary PDF misdetected as HTML)
    html = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", html)

    # Pre-process to fix known issues (e.g., Altium anchor-wrapped headings)
    html = _preprocess_html(html)

    # Extract article content with readability
    doc = Document(html)
    content_html = doc.summary()

    # Convert to markdown, preserving sub/sup tags for technical notation
    text = markdownify(
        content_html,
        heading_style="atx",
        strip=["img", "script", "style"],
    )

    # If readability found too little, markdownify the full HTML directly
    # (handles Adafruit multi-page tutorials, bigmessowires, other unusual structures)
    if not text or len(text) < 100:  # noqa: PLR2004
        text = markdownify(
            html,
            heading_style="atx",
            strip=["img", "script", "style", "nav", "footer", "header"],
        )

    if not text or len(text) < 100:  # noqa: PLR2004
        return None

    # Quality gate: reject JavaScript garbage (JS SPAs where readability
    # extracted script content instead of article text, e.g., coilcraft.com)
    js_count = text.count("function(") + text.count("function (")
    if js_count > 10:  # noqa: PLR2004
        return None

    # Apply domain-specific cleanup
    if url:
        text = _apply_domain_cleanup(text, url)

    return text


# ---------------------------------------------------------------------------
# Domain-specific markdown cleaners
# ---------------------------------------------------------------------------

def _clean_altium(text: str) -> str:
    """Strip Altium author bios, related articles, and product ads."""
    # Author byline at top: "[Author Name](/experts/...)"
    text = re.sub(r"^\[[\w\s]+\]\(/experts/[^)]+\)\s*\n", "", text)
    # Created/Updated metadata block
    text = re.sub(r"^\|\s*Created:.*?(?=\n\n)", "", text, flags=re.DOTALL | re.MULTILINE)
    # Tail: "Related Resources", "Related Technical Documentation", ads
    text = re.sub(r"\n## Related Resources.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\n## Related Technical Documentation.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\n## Don't miss updates.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\n## Table of Contents.*", "", text, flags=re.DOTALL)
    # Altium product pitch at end
    text = re.sub(
        r"\n(?:Whether you need|Use Altium|Altium Develop).*?(?:Experience Altium|altium\.com)[^\n]*",
        "", text, flags=re.DOTALL,
    )
    return text


def _clean_espressif(text: str) -> str:
    """Strip Sphinx navigation and build info from Espressif docs."""
    # "Built with Sphinx" footer
    text = re.sub(r"\nBuilt with Sphinx.*", "", text, flags=re.DOTALL)
    # Sphinx prev/next navigation
    text = re.sub(r"\n(?:Previous|Next):\s*\[.*?\]\(.*?\)\s*", "", text)
    # Chinese translation link (various formats: [中文版], [[中文]](...), etc.)
    text = re.sub(r"^\[?\[中文版?\]\]?\(?[^)]*\)?\s*\n", "", text, flags=re.MULTILINE)
    return text


def _clean_sparkfun(text: str) -> str:
    """Strip SparkFun contributor info and suggested reading cards."""
    # "Contributors:" line
    text = re.sub(r"^Contributors:\s*\n\s*\w+\s*\n\n", "", text, flags=re.MULTILINE)
    # "Suggested Reading" cards with nested links
    text = re.sub(
        r"### Suggested Reading\b.*?(?=\n## |\Z)",
        "", text, flags=re.DOTALL,
    )
    return text


def _clean_murata(text: str) -> str:
    """Strip Murata related products/articles, series nav, and metadata."""
    text = re.sub(r"\n## Related products.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\n## Related articles.*", "", text, flags=re.DOTALL)
    # Breadcrumb remnants
    text = re.sub(r"^(?:Home|Categories)\s*\n", "", text, flags=re.MULTILINE)
    # Category tag line before title (e.g., "Noise Suppression Filter Guide")
    text = re.sub(r"^[A-Z][\w\s]+Guide\s*\n(?=\n?#)", "", text, flags=re.MULTILINE)
    # Date line after title (e.g., "10/28/2010")
    text = re.sub(r"^\d{1,2}/\d{1,2}/\d{4}\s*\n", "", text, flags=re.MULTILINE)
    # Series navigation box at end (e.g., '"Basics of Noise..." series')
    text = re.sub(r'\n"[^"]+"\s*series\s*$', "", text, flags=re.MULTILINE)
    # Disclaimer line
    text = re.sub(r"\n\\\*The information presented.*?latest information\.\s*", "\n", text)
    # Angle brackets in headings: ### <Introduction> → ### Introduction
    text = re.sub(r"^(#{1,6}\s+)<(.+?)>\s*$", r"\1\2", text, flags=re.MULTILINE)
    # Orphaned figure-caption headings (h4+ with no content before next heading or EOF)
    # Murata uses h4 for figure captions; when images are stripped these become empty sections
    text = re.sub(r"^#{4,6}\s+.+\n\n+(?=#{1,6}\s|\Z)", "", text, flags=re.MULTILINE)
    return text


def _clean_hackaday(text: str) -> str:
    """Strip Hackaday post metadata."""
    # "Posted in:" categories
    text = re.sub(r"\nPosted in:.*?\n", "\n", text)
    return text


def _clean_allaboutcircuits(text: str) -> str:
    """Strip AllAboutCircuits sidebar and author info."""
    text = re.sub(r"\nby\s+\w[\w\s]*?\n", "\n", text, count=1)
    return text


def _clean_henry_ott(text: str) -> str:
    """Strip Henry Ott site header, nav footer, copyright, and address."""
    # Site header block: "# Henry Ott Consultants\n**Electromagnetic...Training**\n---"
    text = re.sub(
        r"^#\s+Henry Ott Consultants\s*\n\*\*Electromagnetic.*?\*\*\s*\n+---\s*\n*",
        "", text, flags=re.DOTALL,
    )
    # "Return to top/HOC home page" nav
    text = re.sub(r"\n\*?\*?\[Return to.*", "", text, flags=re.DOTALL)
    # Copyright block (may be bold-wrapped: **© 2000 Henry W. Ott...**)
    text = re.sub(r"\n\*{0,2}©.*?Henry W\.?\s*Ott.*", "", text, flags=re.DOTALL)
    # Address block
    text = re.sub(r"\nHenry Ott Consultants\s*[\n,].*", "", text, flags=re.DOTALL)
    # Bold inside headings: ## **Part 1. Introduction** → ## Part 1. Introduction
    text = re.sub(r"^(#{1,6}\s+)\*\*(.+?)\*\*\s*$", r"\1\2", text, flags=re.MULTILINE)
    # Unwrap hard-wrapped paragraphs (~72 char lines from old HTML source).
    # First, ensure headings have a blank line after them (so they don't get joined)
    text = re.sub(r"^(#{1,6}\s+.+)\n(?!\n)", r"\1\n\n", text, flags=re.MULTILINE)
    # Replace single newlines with spaces, preserving paragraph breaks (\n\n)
    # and markdown block elements (headings, blockquotes, lists, HRs).
    text = re.sub(
        r"(?<!\n)\n(?!\n|#|>|\*|- |\||\d+\.\s|---)",
        " ", text,
    )
    # Clean up double/triple spaces from joining
    text = re.sub(r"  +", " ", text)
    return text


def _clean_protoexpress(text: str) -> str:
    """Strip Sierra Circuits / ProtoExpress share buttons, CTAs, and author info."""
    # Share buttons
    text = re.sub(r"\n(?:Share|Tweet|Pin|Email)\s*\n", "\n", text)
    # Author bio block
    text = re.sub(r"\n### About the Author.*", "", text, flags=re.DOTALL)
    # CTA download boxes: "### PCB Via Design Guide\n\n 7 Chapters...Download Now"
    text = re.sub(
        r"#{2,5}\s+(?:PCB [\w\s]+(?:Guide|Handbook)|Design for Manufacturing Handbook)"
        r".*?\[#{0,5}\s*Download Now\]\([^)]+\)",
        "", text, flags=re.DOTALL,
    )
    # Tool promotion boxes: "### PCB DESIGN TOOL\n\n## ... Calculator\n\n[TRY TOOL](...)"
    text = re.sub(
        r"#{2,5}\s+PCB DESIGN TOOL.*?\[TRY TOOL\]\([^)]+\)",
        "", text, flags=re.DOTALL,
    )
    # Standalone TRY TOOL links
    text = re.sub(r"\[TRY TOOL\]\([^)]+\)\s*\n", "", text)
    # Bold inside headings: ## **Title** → ## Title
    text = re.sub(r"^(#{1,6}\s+)\*\*(.+?)\*\*\s*$", r"\1\2", text, flags=re.MULTILINE)
    return text


def _clean_analog(text: str) -> str:
    """Strip ADI product pitch, navigation, and CTAs from analog.com articles."""
    # Orphaned figure captions from hero images: "#### Figure 1" between title and abstract
    text = re.sub(r"\n+####\s+Figure\s+\d+\s*\n", "\n\n", text)
    # Trailing ADI sales pitch (often mid-paragraph, no newline before it):
    # "For any questions or support needed, feel free to consult..."
    text = re.sub(r"For any questions or support needed.*", "", text, flags=re.DOTALL)
    # "Please see the [Parametric Search]..." product links at tail
    text = re.sub(r"Please see the \[.*?Parametric Search\].*", "", text, flags=re.DOTALL)
    # "Visit [analog.com/...]" or "visit analog.com" product links
    text = re.sub(r"\n[Vv]isit \[?analog\.com.*", "", text, flags=re.DOTALL)
    # "For more information..." trailing CTA
    text = re.sub(r"\nFor more information,? (?:visit|see|consult).*", "", text, flags=re.DOTALL)
    # Trailing author bio: "[Name] received his/her B.S./M.S. degree from..."
    text = re.sub(
        r"\n+\w[\w\s.]+ received (?:his|her|their) \w[\w.]*\s+degree.*",
        "", text, flags=re.DOTALL,
    )
    return text


def _clean_ecsxtal(text: str) -> str:
    """Strip ECS author bylines and company address block."""
    # Author byline: "*Written by Name, Title at ECS...*"
    text = re.sub(r"^\*Written by .*?ECS.*?\*\s*\n+", "", text)
    # Company address block at tail: "ECS Inc. International\n15351..."
    text = re.sub(r"\nECS Inc\. International\s*\n.*", "", text, flags=re.DOTALL)
    # "Please contact us" CTA — \xa0 (non-breaking space) common in ECS pages
    text = re.sub(r"\nPlease[\s\xa0]+\[?contact us\]?.*", "", text, flags=re.DOTALL)
    return text


def _clean_edn(text: str) -> str:
    """Strip EDN editor's notes and author bylines."""
    # Editor's note at top — handles both straight and curly apostrophes
    text = re.sub(r"^\*\*Editor['\u2019]s note:\*\*.*?\n\n", "", text, flags=re.DOTALL)
    # Author byline: "—Steve Taranovich" or "—[Author Name](url)"
    text = re.sub(r"^—\[?[\w\s.]+\]?\(?[^)]*\)?\s*\n", "", text, flags=re.MULTILINE)
    return text


# Map domain substrings to cleaner functions
DOMAIN_CLEANERS: dict[str, callable] = {
    "resources.altium.com": _clean_altium,
    "docs.espressif.com": _clean_espressif,
    "learn.sparkfun.com": _clean_sparkfun,
    "article.murata.com": _clean_murata,
    "hackaday.com": _clean_hackaday,
    "allaboutcircuits.com": _clean_allaboutcircuits,
    "hott.shielddigitaldesign.com": _clean_henry_ott,
    "protoexpress.com": _clean_protoexpress,
    "sierracircuits.com": _clean_protoexpress,
    "analog.com": _clean_analog,
    "ecsxtal.com": _clean_ecsxtal,
    "edn.com": _clean_edn,
}


def _generic_cleanup(text: str) -> str:
    """Strip common boilerplate patterns found across many domains.

    Applied after domain-specific cleaners to catch remaining fluff:
    copyright lines, author bios, navigation, disclaimers, etc.
    """
    # --- Section-level removals (strip everything from pattern to end) ---
    # "Author Profile" or "About the Author" tail sections
    text = re.sub(r"\n+(?:#{2,5}\s+)?Author Profile\b.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\n+#{2,5}\s+About the Authors?\b.*", "", text, flags=re.DOTALL)

    # Legal disclaimer blocks at tail — matches common component vendor patterns:
    # "The data in this document is believed to be accurate and reliable..."
    # "All statements...believed to be accurate and reliable..."
    text = re.sub(
        r"\n+[^\n]*believed to be accurate and reliable.*",
        "", text, flags=re.DOTALL,
    )

    # CTA: "If you're looking to learn more..." (handles curly apostrophes)
    text = re.sub(
        r"\nIf you['\u2019]re looking to learn more about how .*",
        "", text, flags=re.DOTALL,
    )

    # --- Head-of-text removals ---
    # Standalone "[Available in PDF Format]" links
    text = re.sub(r"^\[Available in PDF Format\]\([^)]+\)\s*\n+", "", text)

    # --- Tail-line stripping (iterative, bottom-up) ---
    # These patterns only match at the very end of the text (\Z).
    # We iterate because stripping one line may expose another underneath.
    _TAIL_PATTERNS = [
        r"\*{0,2}©\s*\d{4}[^\n]*",                # © 2020 Author Name
        r"Page last edited[^\n]*",                   # Page last edited March 2024
        r"Last updated[^\n]*",                       # Last updated 2024
        r"Text editor powered by[^\n]*",             # Text editor powered by tinymce
        r"(?:Next|Previous):\s*\[.*?\]\(.*?\)[^\n]*",  # Next: [Title](url)
        r"---+",                                     # trailing horizontal rule
    ]

    for _ in range(5):  # noqa: PLR2004
        changed = False
        for pat in _TAIL_PATTERNS:
            new = re.sub(r"\n+" + pat + r"\s*\Z", "", text)
            if new != text:
                text = new
                changed = True
                break  # restart from top pattern
        if not changed:
            break

    return text


def _apply_domain_cleanup(text: str, url: str) -> str:
    """Apply domain-specific cleanup, then generic cleanup."""
    for domain, cleaner in DOMAIN_CLEANERS.items():
        if domain in url:
            text = cleaner(text)
            break
    text = _generic_cleanup(text)
    return text


def detect_format(url: str) -> str:
    """Detect if URL points to PDF, HTML, or raw markdown."""
    from urllib.parse import urlparse
    parsed = urlparse(url.lower())
    path = parsed.path
    if path.endswith(".pdf") or path.endswith(".ashx"):
        return "pdf"
    # TI /lit/ URLs are PDFs unless they're the HTML viewer path
    if "ti.com" in parsed.netloc and "/lit/" in path and "/lit/html/" not in path:
        return "pdf"
    # Raw markdown files (GitHub raw content, .md files)
    if path.endswith(".md") or "raw.githubusercontent.com" in parsed.netloc:
        return "raw-md"
    # TE DocumentDelivery URLs serve PDFs via query-string
    if "te.com" in parsed.netloc and "documentdelivery" in path:
        return "pdf"
    return "html"


def slugify(name: str) -> str:
    """Convert source name to a filesystem-safe slug.

    Examples:
        "Murata -- DC Bias Voltage Characteristics" → "murata-dc-bias-voltage-characteristics"
        "ADI Tutorial 5527 -- Why Your 4.7uF Becomes 0.33uF" → "adi-tutorial-5527-why-your-4-7uf-becomes-0-33uf"
        "TI SLVA689 -- I2C Bus Pullup Resistor Calculation" → "ti-slva689-i2c-bus-pullup-resistor-calculation"
    """
    slug = name.lower()
    slug = re.sub(r"\s*--\s*", "-", slug)  # " -- " separator
    slug = re.sub(r"[^a-z0-9]+", "-", slug)  # non-alphanumeric → hyphen
    slug = re.sub(r"-+", "-", slug)  # collapse multiple hyphens
    slug = slug.strip("-")
    if len(slug) > 80:  # noqa: PLR2004
        slug = slug[:80].rsplit("-", 1)[0]  # truncate at word boundary
    return slug


def extract_ti_docid(url: str) -> str | None:
    """Extract TI document ID from a ti.com URL.

    Examples:
        https://www.ti.com/lit/pdf/slva689 → SLVA689
        https://www.ti.com/lit/an/slva689/slva689.pdf → SLVA689
        https://www.ti.com/lit/ds/symlink/bq24210.pdf → BQ24210
        https://www.ti.com/document-viewer/lit/html/SLOA101 → SLOA101
    """
    if "ti.com" not in url.lower():
        return None

    # document-viewer/lit/html/{docid} (JS SPA — needs section extraction)
    m = re.search(r"document-viewer/lit/html/([\w]+)", url, re.IGNORECASE)
    if m:
        return m.group(1).upper()

    # /lit/pdf/{docid}
    m = re.search(r"/lit/pdf/([\w]+)", url, re.IGNORECASE)
    if m:
        return m.group(1).upper()

    # /lit/{type}/{folder}/{filename}.pdf — use the filename
    m = re.search(r"/lit/\w+/[\w]+/([\w]+)\.pdf", url, re.IGNORECASE)
    if m:
        return m.group(1).upper()

    return None


def _fetch_ti_section(docid: str, slug: str) -> str | None:
    """Fetch a single TI HTML section. Used by ThreadPoolExecutor.

    Uses wafer.get() (thread-safe one-shot) since this runs in ThreadPoolExecutor.
    SyncSession is NOT thread-safe per wafer docs.
    """
    import wafer
    from wafer import WaferError

    section_url = f"https://www.ti.com/document-viewer/lit/html/{docid}/{slug}?raw=1"
    try:
        resp = wafer.get(section_url, timeout=10)
    except WaferError:
        return None
    if resp.status_code != 200:
        return None
    return resp.text


def _try_ti_html(docid: str, *, timeout: int = 30, session: "SyncSession | None" = None) -> str | None:
    """Try TI HTML document viewer (strongly preferred over PDF).

    Returns cleaned text or None if no HTML version exists (falls back to PDF).
    TI hosts some docs as HTML at document-viewer/lit/html/{DOCID}.
    The viewer is a JS SPA, but section slugs are embedded in the initial HTML
    and each section can be fetched as clean HTML fragments via ?raw=1.

    Pipeline:
      1. Fetch the SPA shell → extract section slugs from embedded links
      2. Fetch each section with ?raw=1 in parallel → clean HTML fragments
      3. Concatenate into full HTML page → readability + markdownify

    Uses session for the shell fetch (sequential), wafer.get() for parallel
    section fetches (SyncSession is not thread-safe).
    """
    url = f"https://www.ti.com/document-viewer/lit/html/{docid}"
    shell_html = _cffi_get(url, timeout=timeout, session=session)
    if not shell_html:
        return None

    # If response starts with %PDF, no HTML version
    if shell_html[:5] == "%PDF-":
        return None

    if "<html" not in shell_html.lower():
        return None

    # Extract section slugs from links in the SPA shell
    # Pattern: document-viewer/lit/html/SLVA689/introduction-slva6895438
    slug_pattern = re.compile(
        rf"document-viewer/lit/html/{re.escape(docid)}/([^\"#?\s]+)",
        re.IGNORECASE,
    )
    slugs = list(dict.fromkeys(slug_pattern.findall(shell_html)))  # dedupe, preserve order

    if not slugs:
        return None

    # Skip boilerplate sections
    skip = {"trademarks-tm", "important_notice"}
    content_slugs = [s for s in slugs if not any(s.startswith(sk) for sk in skip)]

    if not content_slugs:
        return None

    # Fetch all sections in parallel (up to 6 concurrent requests)
    sections: list[str] = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(_fetch_ti_section, docid, slug) for slug in content_slugs]
        for future in futures:
            result = future.result()
            if result:
                sections.append(result)

    if not sections:
        return None

    # Convert sections directly to markdown — skip readability since these are
    # already clean content fragments from ?raw=1 (readability would pick one
    # section as "the article" and discard the rest)
    from markdownify import markdownify

    combined_html = "\n".join(sections)
    text = markdownify(
        combined_html,
        heading_style="atx",
        strip=["img", "script", "style"],
    )

    if not text:
        return None

    # Apply TI-specific cleanup
    text = _apply_domain_cleanup(text, f"ti.com/lit/html/{docid}")

    # Must be substantial — if very little content, fall back to PDF
    if len(text) < 500:  # noqa: PLR2004
        return None

    return text


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------


def fetch_url(
    url: str,
    *,
    timeout: int = 30,
    session: "SyncSession | None" = None,
) -> ExtractionResult | None:
    """Fetch a URL and return extracted text with method metadata.

    HTML sources are strongly preferred. For TI URLs, always probes for
    HTML document viewer first (structured HTML >> PDF extraction quality).
    Falls back to PDF via pdfplumber when no HTML version exists.
    For raw markdown (.md URLs), fetches as-is.

    Pass a SyncSession to reuse TLS identity and cookies across requests.
    """
    from wafer import WaferError

    text = None
    method = "unknown"

    # For TI URLs, always try HTML document viewer first (strongly preferred over PDF)
    ti_docid = extract_ti_docid(url)
    if ti_docid:
        text = _try_ti_html(ti_docid, timeout=timeout, session=session)
        if text:
            method = "ti-html"
            print(f"  → TI HTML viewer ({ti_docid})", file=sys.stderr)

    # If TI HTML failed but we have a docid, fall back to PDF before generic fetch
    if not text and ti_docid:
        pdf_url = f"https://www.ti.com/lit/pdf/{ti_docid}"
        print(f"  → TI HTML failed, trying PDF fallback ({pdf_url})", file=sys.stderr)
        try:
            text = _fetch_pdf(pdf_url, timeout=timeout, session=session)
            method = "pdfplumber"
        except WaferError as e:
            print(f"  → TI PDF fallback failed: {e}", file=sys.stderr)

    # Fall back to direct fetch
    if not text:
        fmt = detect_format(url)
        try:
            if fmt == "pdf":
                text = _fetch_pdf(url, timeout=timeout, session=session)
                method = "pdfplumber"
            elif fmt == "raw-md":
                text = _fetch_raw_md(url, timeout=timeout, session=session)
                method = "raw-md"
            else:
                # Fetch the response and check Content-Type before choosing
                # extraction method. Some URLs serve PDF without a .pdf
                # extension (e.g. docs.broadcom.com/doc/*, ARM static/*).
                text, method = _fetch_html_or_pdf(
                    url, timeout=timeout, session=session,
                )
        except WaferError as e:
            print(f"  ERROR fetching {url}: {e}", file=sys.stderr)
            return None

    if not text:
        return None

    return ExtractionResult(text=text, method=method)


def _extract_pdf_text(pdf_bytes: bytes, *, x_tolerance: float = 3) -> list[str]:
    """Extract text from PDF bytes using pdfplumber. Returns list of page texts."""
    from io import BytesIO
    import pdfplumber

    text_parts = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=x_tolerance)
            if page_text:
                text_parts.append(page_text)
    return text_parts


def _count_collapsed_words(text: str) -> int:
    """Count words with 25+ lowercase chars — a sign of missing word breaks."""
    return len(re.findall(r"[a-z]{25,}", text))


def _fetch_pdf(
    url: str,
    *,
    timeout: int = 30,
    session: "SyncSession | None" = None,
) -> str | None:
    """Download PDF and extract text via pdfplumber.

    Downloads PDF bytes with wafer (TLS fingerprint impersonation),
    extracts text with pdfplumber, then applies PDF-specific cleanup
    (page headers/footers, repeated headings).
    If collapsed word spacing is detected, re-extracts with tighter x_tolerance.
    """
    import wafer
    from wafer import WaferError

    try:
        if session:
            response = session.get(url, timeout=max(timeout, 120))
        else:
            response = wafer.get(url, timeout=max(timeout, 120))
    except WaferError as e:
        print(f"  → wafer error: {e}", file=sys.stderr)
        return None
    if response.status_code != 200:
        return None
    if response.was_retried:
        print(f"  → wafer: {response.retries} retries, {response.rotations} rotations", file=sys.stderr)
    pdf_bytes = response.content

    if not pdf_bytes:
        return None

    # Extract text with pdfplumber (same approach as fetchaller)
    try:
        text_parts = _extract_pdf_text(pdf_bytes)
    except Exception as e:
        print(f"  ERROR: pdfplumber extraction failed: {e}", file=sys.stderr)
        return None

    if not text_parts:
        return None

    text = "\n\n".join(text_parts)

    # Detect collapsed word spacing and retry with tighter x_tolerance
    collapsed = _count_collapsed_words(text)
    if collapsed > 10:  # noqa: PLR2004
        print(f"  → collapsed words detected ({collapsed}), retrying with x_tolerance=1.5",
              file=sys.stderr)
        try:
            retry_parts = _extract_pdf_text(pdf_bytes, x_tolerance=1.5)
            if retry_parts:
                retry_text = "\n\n".join(retry_parts)
                retry_collapsed = _count_collapsed_words(retry_text)
                if retry_collapsed < collapsed:
                    text = retry_text
                    print(f"  → retry improved: {collapsed} → {retry_collapsed} collapsed words",
                          file=sys.stderr)
        except Exception:
            pass  # keep original extraction

    if len(text) < 50:  # noqa: PLR2004
        return None

    # --- PDF-specific cleanup ---

    # Strip repeated page headers extracted as content (3+ identical lines)
    text = _strip_repeated_headers(text)

    # Strip TI page header/footer lines (www.ti.com SectionTitle)
    text = _TI_HEADER_PLAIN_RE.sub("", text)

    # Strip TI document ID + date header/footer lines
    # "SLVA521–March 2013"  (standalone, no title)
    # "SLVA521–March2013 Setting the SVS Voltage Monitor Threshold 1"
    # "SLDA039B–June 2015–Revised January 2020 How to Design ... 1"
    # "SSZB130E – AUGUST 2025 System-Level ESD Protection Guide 3"
    _MONTH = (
        r"(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER"
        r"|January|February|March|April|May|June|July|August|September|October|November|December)"
    )
    _TI_DOCID_DATE = (
        r"[A-Z]{2,8}\d{3,5}[A-Z]?\s*[–-]\s*" + _MONTH + r"\s*\d{4}"
        r"(?:\s*[–-]\s*(?:Revised\s+)?" + _MONTH + r"\s*\d{4})?"
    )
    text = re.sub(
        r"^" + _TI_DOCID_DATE + r"(?:\s+.{5,80}\s+\d{1,3})?\s*$",
        "", text, flags=re.MULTILINE,
    )
    # Reverse: "3 System-Level ESD Protection Guide SSZB130E – AUGUST 2025"
    text = re.sub(
        r"^\d{1,3}\s+.{5,80}\s+" + _TI_DOCID_DATE + r"\s*$",
        "", text, flags=re.MULTILINE,
    )

    # Strip TI "Submit Document(ation) Feedback" lines
    text = re.sub(r"^Submit Document(?:ation)? Feedback\s*$", "", text, flags=re.MULTILINE)

    # Strip TI copyright lines (both spaced and collapsed variants)
    text = re.sub(
        r"^Copyright\s*©?\s*\d{4}[\s,–-]*(?:\d{4}[\s,–-]*)?"
        r"Texas Instruments Incorporated\s*$",
        "", text, flags=re.MULTILINE,
    )

    # Strip ST page footer lines (AN1234 - Rev N page X/Y)
    text = _ST_FOOTER_RE.sub("", text)

    # Strip ST page header lines (**AN1234 SectionName**)
    text = _ST_HEADER_RE.sub("", text)

    # Strip ST plain-text header lines: "AN5241" alone on a line (repeated per page)
    text = re.sub(r"^AN\d{4,5}\s*$", "", text, flags=re.MULTILINE)

    # Strip ST "Rev N - Month YYYY www.st.com" footer lines
    text = re.sub(
        r"^AN\d{4,5}\s*-\s*Rev\s*\d+\s*-\s*\w+\s*\d{4}\s*www\.st\.com\s*$",
        "", text, flags=re.MULTILINE,
    )

    # Strip ST "For further information contact..." boilerplate
    text = re.sub(
        r"^For further information contact your local STMicroelectronics sales office\.\s*$",
        "", text, flags=re.MULTILINE,
    )

    # Strip ROHM page footer: "© YYYY ROHM Co., Ltd. No. 66AN046E Rev.001"
    text = re.sub(
        r"^©\s*\d{4}\s*ROHM\s+Co\.,?\s*Ltd\.?\s*No\.\s*\w+\s*Rev\.\d+\s*$",
        "", text, flags=re.MULTILINE,
    )

    # Strip standalone page numbers between blank lines
    lines = text.split("\n")
    new_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"^\d{1,4}$", stripped):
            prev_blank = (i == 0) or (lines[i - 1].strip() == "")
            next_blank = (i == len(lines) - 1) or (lines[i + 1].strip() == "")
            if prev_blank and next_blank:
                continue
        new_lines.append(line)
    text = "\n".join(new_lines)

    print(f"  → pdfplumber ({len(text)} chars)", file=sys.stderr)
    return text


def _cffi_get(
    url: str,
    *,
    timeout: int = 30,
    session: "SyncSession | None" = None,
) -> str | None:
    """Fetch URL with wafer TLS fingerprint impersonation.

    Uses session if provided (reuses TLS identity + cookies), otherwise
    falls back to wafer.get() one-shot (creates a fresh session per call).
    """
    import wafer
    from wafer import WaferError

    try:
        if session:
            resp = session.get(url, timeout=timeout)
        else:
            resp = wafer.get(url, timeout=timeout)
    except WaferError:
        return None
    if resp.status_code != 200:
        return None
    if resp.was_retried:
        print(f"  → wafer: {resp.retries} retries, {resp.rotations} rotations", file=sys.stderr)
    return resp.text


def _fetch_raw_md(
    url: str,
    *,
    timeout: int = 30,
    session: "SyncSession | None" = None,
) -> str | None:
    """Fetch raw markdown file (e.g., from GitHub). No conversion needed."""
    return _cffi_get(url, timeout=timeout, session=session)


def _fetch_html_or_pdf(
    url: str,
    *,
    timeout: int = 30,
    session: "SyncSession | None" = None,
) -> tuple[str | None, str]:
    """Fetch a URL expected to be HTML, but check Content-Type first.

    Some URLs serve PDF without a .pdf extension (e.g. docs.broadcom.com/doc/*,
    documentation-service.arm.com/static/*). If the response Content-Type is
    application/pdf, routes to pdfplumber extraction instead of readability.

    Returns (text, method) tuple.
    """
    import wafer
    from wafer import WaferError

    try:
        if session:
            resp = session.get(url, timeout=timeout)
        else:
            resp = wafer.get(url, timeout=timeout)
    except WaferError:
        return None, "unknown"
    if resp.status_code != 200:
        return None, "unknown"
    if resp.was_retried:
        print(f"  → wafer: {resp.retries} retries, {resp.rotations} rotations", file=sys.stderr)

    content_type = resp.headers.get("content-type", "").lower()

    if "application/pdf" in content_type:
        print("  → Content-Type is PDF, using pdfplumber", file=sys.stderr)
        pdf_bytes = resp.content
        if not pdf_bytes:
            return None, "pdfplumber"
        try:
            text_parts = _extract_pdf_text(pdf_bytes)
        except Exception as e:
            print(f"  ERROR: pdfplumber extraction failed: {e}", file=sys.stderr)
            return None, "pdfplumber"
        if not text_parts:
            return None, "pdfplumber"
        text = "\n\n".join(text_parts)
        # Check for collapsed words and retry with tighter tolerance
        collapsed = _count_collapsed_words(text)
        if collapsed > 10:
            retry_parts = _extract_pdf_text(pdf_bytes, x_tolerance=1.5)
            retry_text = "\n\n".join(retry_parts) if retry_parts else text
            retry_collapsed = _count_collapsed_words(retry_text)
            print(
                f"  → collapsed words detected ({collapsed}),"
                f" retrying with x_tolerance=1.5",
                file=sys.stderr,
            )
            print(
                f"  → retry improved: {collapsed} → {retry_collapsed}"
                f" collapsed words",
                file=sys.stderr,
            )
            if retry_collapsed < collapsed:
                text = retry_text
        print(f"  → pdfplumber ({len(text)} chars)", file=sys.stderr)
        return text, "pdfplumber"

    # Not PDF — treat as HTML
    html = resp.text
    if not html:
        return None, "readability"
    text = _extract_html_content(html, url=url)
    return text, "readability"


def _fetch_html(
    url: str,
    *,
    timeout: int = 30,
    session: "SyncSession | None" = None,
) -> str | None:
    """Fetch HTML page and extract main content via readability + markdownify."""
    html = _cffi_get(url, timeout=timeout, session=session)
    if not html:
        return None
    return _extract_html_content(html, url=url)


# ---------------------------------------------------------------------------
# Source index parser
# ---------------------------------------------------------------------------


def parse_sources_index() -> dict[str, list[dict]]:
    """Parse verified-sources.md and return sources grouped by topic.

    Returns:
        {"guides/passives.md": [{"num": 1, "name": "...", "format": "...", "url": "..."}, ...], ...}
    """
    if not SOURCES_FILE.exists():
        print(f"ERROR: {SOURCES_FILE} not found", file=sys.stderr)
        sys.exit(1)

    text = SOURCES_FILE.read_text(encoding="utf-8")
    topics: dict[str, list[dict]] = {}
    current_topic = None

    for line in text.split("\n"):
        # Detect topic headers like "## guides/passives.md"
        topic_match = re.match(r"^##\s+(\w+/[\w.-]+\.md)\s*$", line)
        if topic_match:
            current_topic = topic_match.group(1)
            topics[current_topic] = []
            continue

        # Detect table rows like "| 1 | Source Name | PDF 25pp | `https://...` |"
        if current_topic and line.startswith("|") and not line.startswith("| #") and not line.startswith("|--"):
            parts = [p.strip() for p in line.split("|")]
            # parts[0] is empty (before first |), parts[-1] is empty (after last |)
            parts = [p for p in parts if p]
            if len(parts) >= 4:  # noqa: PLR2004
                try:
                    num = int(parts[0])
                except ValueError:
                    continue
                name = parts[1]
                fmt = parts[2]
                url = parts[3].strip("`")
                topics[current_topic].append(
                    {"num": num, "name": name, "format": fmt, "url": url}
                )

    return topics


# ---------------------------------------------------------------------------
# Extraction pipeline
# ---------------------------------------------------------------------------


def extract_source(
    url: str,
    *,
    verbose: bool = True,
    session: "SyncSession | None" = None,
) -> ExtractionResult | None:
    """Fetch, clean, and return extracted text from a source URL."""
    if verbose:
        print(f"  Fetching: {url}")

    result = fetch_url(url, session=session)
    if not result:
        return None

    if verbose:
        print(f"  Raw: {len(result.text)} chars ({result.method})")

    text = strip_boilerplate(result.text)
    text = clean_text(text)

    if verbose:
        print(f"  Cleaned: {len(text)} chars")

    return ExtractionResult(text=text, method=result.method)


def extract_topic(
    topic: str,
    sources: list[dict],
    *,
    output_dir: Path = RAW_SOURCES_DIR,
    force: bool = False,
    verbose: bool = True,
    html_only: bool = False,
    dedup_cache: dict[str, Path] | None = None,
    session: "SyncSession | None" = None,
) -> None:
    """Extract all sources for a topic. Skips already-extracted unless force=True."""
    print(f"\n{'='*60}")
    print(f"Topic: {topic}")
    print(f"Sources: {len(sources)}")
    print(f"{'='*60}")

    # "guides/passives.md" → "guides/passives"
    topic_dir = output_dir / topic.replace(".md", "")
    topic_dir.mkdir(parents=True, exist_ok=True)

    extracted = 0
    skipped = 0
    failed = 0
    pdf_skipped = 0

    for src in sources:
        slug = slugify(src["name"])
        out_file = topic_dir / f"{slug}.md"

        if out_file.exists() and not force:
            print(f"\n  [SKIP] {src['name']}")
            skipped += 1
            continue

        # Skip PDFs in html-only mode
        fmt = detect_format(src["url"])
        if html_only and fmt == "pdf":
            print(f"\n  [PDF-SKIP] {src['name']}")
            pdf_skipped += 1
            continue

        # Check dedup cache — if another topic already extracted this URL, copy it
        if dedup_cache is not None and src["url"] in dedup_cache:
            cached_path = dedup_cache[src["url"]]
            if cached_path.exists():
                shutil.copy2(cached_path, out_file)
                rel = out_file.relative_to(output_dir)
                print(f"\n  [DEDUP] {src['name']} → copied from {cached_path.name}")
                extracted += 1
                continue

        print(f"\n[{src['num']}] {src['name']}")
        result = extract_source(src["url"], verbose=verbose, session=session)
        if result:
            header = (
                f"---\n"
                f"source: \"{src['name']}\"\n"
                f"url: \"{src['url']}\"\n"
                f"format: \"{src['format']}\"\n"
                f"method: \"{result.method}\"\n"
                f"extracted: {date.today().isoformat()}\n"
                f"chars: {len(result.text)}\n"
                f"---\n\n"
            )
            out_file.write_text(header + result.text, encoding="utf-8")
            rel = out_file.relative_to(output_dir)
            print(f"  OK → {rel} ({len(result.text)} chars)")
            extracted += 1

            # Register in dedup cache
            if dedup_cache is not None:
                dedup_cache[src["url"]] = out_file
        else:
            print("  FAILED")
            failed += 1

    parts = [f"{extracted} extracted", f"{skipped} skipped", f"{failed} failed"]
    if pdf_skipped:
        parts.append(f"{pdf_skipped} PDFs skipped")
    print(f"\n  Result: {', '.join(parts)}")


# ---------------------------------------------------------------------------
# Topic name matching
# ---------------------------------------------------------------------------

# Short names that map to full topic paths
TOPIC_ALIASES = {
    # guides/
    "passives": "guides/passives.md",
    "connectors": "guides/connectors.md",
    "power-architecture": "guides/power-architecture.md",
    "thermal": "guides/thermal.md",
    "checklist": "guides/checklist.md",
    "pcb-layout": "guides/pcb-layout.md",
    "signal-integrity": "guides/signal-integrity.md",
    "emc": "guides/emc.md",
    "dfm": "guides/dfm.md",
    # interfaces/
    "i2c": "interfaces/i2c.md",
    "spi": "interfaces/spi.md",
    "uart": "interfaces/uart.md",
    "usb": "interfaces/usb.md",
    "usb-c": "interfaces/usb.md",  # renamed from usb-c.md
    # power/
    "decoupling": "power/decoupling.md",
    "ldo": "power/ldo.md",
    "switching": "power/switching.md",
    "battery": "power/battery.md",
    "power-path": "power/power-path.md",
    # protection/
    "esd": "protection/esd.md",
    "reverse-polarity": "protection/reverse-polarity.md",
    "voltage-supervisor": "protection/voltage-supervisor.md",
    "supervisor": "protection/voltage-supervisor.md",
    # mcus/
    "esp32": "mcus/esp32.md",
    "stm32": "mcus/stm32.md",
    "rp2040": "mcus/rp2040.md",
    # misc/
    "crystal": "misc/crystal.md",
    "level-shifting": "misc/level-shifting.md",
    "mosfet": "misc/mosfet-circuits.md",
    "mosfet-circuits": "misc/mosfet-circuits.md",
    "rf-antenna": "misc/rf-antenna.md",
    "rf": "misc/rf-antenna.md",
    "antenna": "misc/rf-antenna.md",
    "op-amp": "misc/op-amp-basics.md",
    "op-amp-basics": "misc/op-amp-basics.md",
    "opamp": "misc/op-amp-basics.md",
    "schematic-practices": "guides/schematic-practices.md",
    "schematic": "guides/schematic-practices.md",
    "test-debug": "guides/test-debug.md",
    "adc-dac": "misc/adc-dac.md",
    "adc": "misc/adc-dac.md",
    "dac": "misc/adc-dac.md",
    "gnss-integration": "misc/gnss-integration.md",
    "gnss": "misc/gnss-integration.md",
    "ev-power-systems": "misc/ev-power-systems.md",
    "ev": "misc/ev-power-systems.md",
    "sensor-modules": "misc/sensor-modules.md",
    "sensors": "misc/sensor-modules.md",
    "battery-chemistry": "power/battery-chemistry.md",
    # Phase 10 additions
    "can": "interfaces/can.md",
    "ethernet": "interfaces/ethernet.md",
    "isolation": "protection/isolation.md",
    "fpga": "mcus/fpga.md",
    "motor-control": "misc/motor-control.md",
    "motor": "misc/motor-control.md",
    "audio": "misc/audio.md",
    "display": "misc/display.md",
}


def resolve_topic(name: str) -> str | None:
    """Resolve a short topic name to full path."""
    # Direct match
    if name in TOPIC_ALIASES:
        return TOPIC_ALIASES[name]
    # Try with .md suffix
    for alias, full in TOPIC_ALIASES.items():
        if full == name or full.endswith(f"/{name}"):
            return full
    return None


# ---------------------------------------------------------------------------
# Batch splitting (PDF groups for parallel extraction runs)
# ---------------------------------------------------------------------------


def _parse_page_count(fmt: str) -> int:
    """Extract page count from format string like 'PDF 25pp'. Returns 1 if unknown."""
    m = re.search(r"(\d+)\s*pp", fmt)
    return int(m.group(1)) if m else 1


def _collect_all_pdfs(topics: dict[str, list[dict]]) -> list[tuple[str, dict]]:
    """Collect all PDF sources across all topics as (topic, source) pairs."""
    pdfs = []
    for topic, sources in sorted(topics.items()):
        for src in sources:
            if detect_format(src["url"]) == "pdf":
                pdfs.append((topic, src))
    return pdfs


def _bin_pack_pdfs(
    pdfs: list[tuple[str, dict]], num_groups: int
) -> list[list[tuple[str, dict]]]:
    """Greedy bin-packing: assign PDFs (sorted largest-first) to group with fewest pages.

    Returns list of num_groups groups, each a list of (topic, source) pairs.
    """
    # Sort by page count descending for better balance
    pdfs_sorted = sorted(pdfs, key=lambda x: _parse_page_count(x[1]["format"]), reverse=True)

    groups: list[list[tuple[str, dict]]] = [[] for _ in range(num_groups)]
    group_pages = [0] * num_groups

    for item in pdfs_sorted:
        # Find the group with the fewest pages
        min_idx = group_pages.index(min(group_pages))
        groups[min_idx].append(item)
        group_pages[min_idx] += _parse_page_count(item[1]["format"])

    return groups


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Extract and clean text from design rule sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="Single URL to extract",
    )
    parser.add_argument(
        "--topic", "-t",
        help="Extract all sources for a topic (e.g., 'i2c', 'ldo', 'passives')",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Extract all sources for all topics",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be extracted without fetching",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Re-extract sources even if already extracted",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Skip PDF sources (extract HTML-only sources first; PDFs are fallback only)",
    )
    parser.add_argument(
        "--batch",
        metavar="N/M",
        help="Process PDF batch N of M (e.g., --batch 1/10). "
             "Splits all PDFs into M balanced groups by page count and processes group N.",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=RAW_SOURCES_DIR,
        help=f"Output directory (default: {RAW_SOURCES_DIR})",
    )
    parser.add_argument(
        "--list-topics",
        action="store_true",
        help="List all available topics and exit",
    )

    args = parser.parse_args()

    # List topics
    if args.list_topics:
        topics = parse_sources_index()
        for topic, sources in sorted(topics.items()):
            print(f"  {topic:35s} ({len(sources)} sources)")
        print(f"\n  Total: {sum(len(s) for s in topics.values())} sources across {len(topics)} topics")
        return

    # Single URL mode
    if args.url:
        from wafer import SyncSession

        with SyncSession(cache_dir=None) as session:
            result = extract_source(args.url, session=session)
        if result:
            print(f"\n{'='*60}")
            print(f"Method: {result.method}")
            print(f"{'='*60}\n")
            print(result.text)
        else:
            print("Extraction failed.", file=sys.stderr)
            sys.exit(1)
        return

    # Topic or all mode — parse the index
    topics = parse_sources_index()

    # Parse --batch N/M
    batch_group = None
    batch_total = None
    if args.batch:
        m = re.match(r"^(\d+)/(\d+)$", args.batch)
        if not m:
            print("ERROR: --batch must be N/M format (e.g., --batch 1/10)", file=sys.stderr)
            sys.exit(1)
        batch_group = int(m.group(1))
        batch_total = int(m.group(2))
        if batch_group < 1 or batch_group > batch_total:
            print(f"ERROR: batch group must be 1-{batch_total}, got {batch_group}", file=sys.stderr)
            sys.exit(1)

    if args.topic:
        resolved = resolve_topic(args.topic)
        if not resolved or resolved not in topics:
            print(f"ERROR: Unknown topic '{args.topic}'", file=sys.stderr)
            print("Available topics:", file=sys.stderr)
            for t in sorted(topics):
                print(f"  {t}", file=sys.stderr)
            sys.exit(1)
        selected = {resolved: topics[resolved]}
    elif args.all or args.batch:
        selected = topics
    else:
        parser.print_help()
        return

    # --batch mode: bin-pack PDFs into groups, select one group
    if batch_group is not None:
        all_pdfs = _collect_all_pdfs(selected)
        groups = _bin_pack_pdfs(all_pdfs, batch_total)
        my_group = groups[batch_group - 1]  # 1-indexed → 0-indexed

        # Show all groups summary
        print(f"PDF Batch {batch_group}/{batch_total}")
        print(f"Total PDFs: {len(all_pdfs)}")
        total_pages = sum(_parse_page_count(s["format"]) for _, s in all_pdfs)
        print(f"Total pages: {total_pages}\n")
        for i, g in enumerate(groups, 1):
            pages = sum(_parse_page_count(s["format"]) for _, s in g)
            marker = " ◀" if i == batch_group else ""
            print(f"  Group {i:2d}: {len(g):3d} PDFs, {pages:4d} pages{marker}")

        my_pages = sum(_parse_page_count(s["format"]) for _, s in my_group)
        print(f"\nProcessing group {batch_group}: {len(my_group)} PDFs, {my_pages} pages")

        if args.dry_run:
            print()
            for topic, src in my_group:
                pages = _parse_page_count(src["format"])
                print(f"  [{pages:3d}pp] {src['name']}")
                print(f"         {topic} | {src['url']}")
            return

        # Build a filtered selected dict with only this batch's PDFs
        selected = {}
        for topic, src in my_group:
            selected.setdefault(topic, []).append(src)

    # Dry run (non-batch)
    elif args.dry_run:
        pdf_count = 0
        html_count = 0
        for topic, sources in sorted(selected.items()):
            print(f"\n{topic}:")
            for s in sources:
                fmt = detect_format(s["url"])
                skip_marker = " [PDF-SKIP]" if args.html_only and fmt == "pdf" else ""
                print(f"  [{s['num']}] {s['name']}{skip_marker}")
                print(f"      {s['url']}")
                if fmt == "pdf":
                    pdf_count += 1
                else:
                    html_count += 1
        total = sum(len(s) for s in selected.values())
        msg = f"\nWould extract {total} sources across {len(selected)} topics"
        msg += f" ({html_count} HTML, {pdf_count} PDF)"
        if args.html_only:
            msg += f"\n  --html-only: {pdf_count} PDFs will be skipped"
        print(msg)
        return

    # Build dedup cache for shared URLs across topics
    dedup_cache: dict[str, Path] = {}

    # Extract — reuse a single SyncSession across all topics for TLS identity + cookie reuse.
    # SyncSession has no cleanup needed (no browser solver), so context manager is optional,
    # but we use it for clarity.
    from wafer import SyncSession

    with SyncSession(cache_dir=None) as session:
        for topic, sources in sorted(selected.items()):
            extract_topic(
                topic, sources,
                output_dir=args.output,
                force=args.force,
                html_only=args.html_only,
                dedup_cache=dedup_cache,
                session=session,
            )

    total = sum(len(s) for s in selected.values())
    print(f"\n{'='*60}")
    print(f"Done. Processed {total} sources across {len(selected)} topics.")
    print(f"Output: {args.output}")
    if dedup_cache:
        print(f"Dedup cache: {len(dedup_cache)} unique URLs")


if __name__ == "__main__":
    main()
