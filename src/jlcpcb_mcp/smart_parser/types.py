"""Component type and mounting type extraction for smart query parsing."""

import re

from ..subcategory_aliases import SUBCATEGORY_ALIASES


# Pre-sorted by length (longest first) for correct matching
_SUBCATEGORY_KEYWORDS_BY_LENGTH = sorted(SUBCATEGORY_ALIASES.keys(), key=len, reverse=True)


def extract_component_type(query: str) -> tuple[str | None, str, str | None]:
    """Extract component type from query.

    Args:
        query: The search query string

    Returns:
        Tuple of (subcategory_name, remaining_query, matched_keyword)
    """
    query_lower = query.lower()

    for keyword in _SUBCATEGORY_KEYWORDS_BY_LENGTH:
        if keyword in query_lower:
            # Remove the keyword from query
            # Use word boundaries to avoid partial matches
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            remaining = pattern.sub('', query).strip()
            remaining = re.sub(r'\s+', ' ', remaining)
            return SUBCATEGORY_ALIASES[keyword], remaining, keyword

    return None, query, None


# Mounting type patterns: PTH/THT -> Through Hole, SMD/SMT -> SMD
_MOUNTING_TYPE_PATTERNS = [
    (re.compile(r'\b(PTH|THT|through[- ]?hole|leaded)\b', re.IGNORECASE), "Through Hole"),
    (re.compile(r'\b(SMD|SMT|surface[- ]?mount)\b', re.IGNORECASE), "SMD"),
]


def extract_mounting_type(query: str) -> tuple[str | None, str]:
    """Extract mounting type from query.

    Args:
        query: The search query string

    Returns:
        Tuple of (mounting_type, remaining_query)
        Where mounting_type is "SMD" or "Through Hole" or None.
    """
    for pattern, mount_type in _MOUNTING_TYPE_PATTERNS:
        match = pattern.search(query)
        if match:
            remaining = query[:match.start()] + query[match.end():]
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            return mount_type, remaining
    return None, query
