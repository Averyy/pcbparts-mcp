"""Design rules lookup — serves curated PCB design reference files."""

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)

_RULES_DIR = Path(
    os.environ.get(
        "DESIGN_RULES_DIR",
        str(Path(__file__).parent.parent.parent / "data" / "design-rules" / "rules"),
    )
)

# Lazy-built file index: "category/stem" -> Path
_index: dict[str, Path] | None = None


# Files in the rules dir that aren't actual design rules
_EXCLUDED_FILES = {"INDEX.MD", "DESIGN-STYLE-GUIDE.MD", "VERIFIED-SOURCES.MD"}

# Aliases: common search terms → file keys they should match
_ALIASES: dict[str, list[str]] = {
    "buck": ["power/switching"],
    "boost": ["power/switching"],
    "flyback": ["power/switching"],
    "buck-boost": ["power/switching"],
    "usb-c": ["interfaces/usb"],
    "usbc": ["interfaces/usb"],
    "opamp": ["misc/op-amp-basics"],
    "fet": ["misc/mosfet-circuits"],
    "nmos": ["misc/mosfet-circuits"],
    "pmos": ["misc/mosfet-circuits"],
    "jtag": ["guides/test-debug"],
    "swd": ["guides/test-debug"],
    "gps": ["misc/gnss-integration"],
    "impedance": ["guides/signal-integrity"],
    "differential": ["guides/signal-integrity"],
    "crosstalk": ["guides/signal-integrity"],
    "termination": ["guides/signal-integrity"],
    "ground": ["guides/pcb-layout"],
    "stackup": ["guides/pcb-layout"],
    "trace": ["guides/pcb-layout"],
    "via": ["guides/pcb-layout"],
    "pmic": ["guides/power-architecture"],
    "sequencing": ["guides/power-architecture"],
    "inrush": ["guides/power-architecture"],
    "aliasing": ["misc/adc-dac"],
    "sampling": ["misc/adc-dac"],
}

_MAX_FULL_CONTENT = 3  # Return file list instead of content when more matches


def _build_index(rules_dir: Path) -> dict[str, Path]:
    """Glob all .md files, map category/stem to path, exclude non-rule files."""
    idx: dict[str, Path] = {}
    for p in sorted(rules_dir.rglob("*.md")):
        if p.name.upper() in _EXCLUDED_FILES:
            continue
        # key = relative path without .md, e.g. "power/ldo"
        rel = p.relative_to(rules_dir).with_suffix("")
        idx[str(rel)] = p
    return idx


def _match_word(word: str, key: str) -> bool:
    """Check if a word matches a key, requiring word-boundary alignment.

    Matches against path segments split by / and - to avoid substring false
    positives like "rf" matching "interfaces".
    """
    # Split key into individual tokens: "interfaces/rf-antenna" → ["interfaces", "rf", "antenna"]
    tokens = []
    for segment in key.split("/"):
        tokens.extend(segment.split("-"))
    return word in tokens


def get_design_rules(topic: str = "", rules_dir: Path | None = None) -> dict:
    """Look up PCB design rules by topic.

    Args:
        topic: Substring to match against rule file keys (e.g. "ldo", "power", "usb").
               Empty string returns the INDEX.
        rules_dir: Override rules directory (for testing).

    Returns:
        {"content": str, "matched_files": list[str], "topic": str}
    """
    global _index
    rd = rules_dir or _RULES_DIR

    if not rd.is_dir():
        return {
            "error": "Design rules are not available.",
            "matched_files": [],
            "topic": topic,
        }

    # Build or use cached index (only cache for default dir)
    if rules_dir is not None:
        idx = _build_index(rd)
    else:
        if _index is None:
            _index = _build_index(rd)
        idx = _index

    index_path = rd / "INDEX.md"

    # Empty topic → return INDEX
    if not topic.strip():
        content = index_path.read_text(encoding="utf-8") if index_path.exists() else "No INDEX.md found."
        return {"content": content, "matched_files": ["INDEX.md"], "topic": ""}

    # Cap input length (consistent with other tools)
    topic = topic[:500]

    # Resolve aliases first, then fall back to word matching
    # Split on whitespace and hyphens so "op-amp" matches "op-amp-basics"
    words = re.split(r'[\s-]+', topic.strip().lower())
    words = [w for w in words if w]  # drop empty strings
    alias_keys: set[str] = set()
    unresolved_words: list[str] = []
    for w in words:
        if w in _ALIASES:
            alias_keys.update(_ALIASES[w])
        else:
            unresolved_words.append(w)

    # Collect matches: alias hits + word-boundary matches for remaining words
    matched_set: dict[str, Path] = {}
    for k, p in idx.items():
        if k in alias_keys:
            matched_set[k] = p
        elif unresolved_words and any(_match_word(w, k.lower()) for w in unresolved_words):
            matched_set[k] = p

    matches = list(matched_set.items())

    if not matches:
        index_content = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
        content = f"No rules found matching '{topic}'. Available rules:\n\n{index_content}"
        return {"content": content, "matched_files": [], "topic": topic}

    matched_keys = [k for k, _ in sorted(matches)]

    if len(matches) > _MAX_FULL_CONTENT:
        content = (
            f"Found {len(matches)} rule files matching '{topic}'. "
            f"Call again with a more specific topic to get full content:\n\n"
            + "\n".join(f"- {k}" for k in matched_keys)
        )
        return {"content": content, "matched_files": matched_keys, "topic": topic}

    # Read and concatenate matched files
    parts = []
    for key, path in sorted(matches):
        try:
            parts.append(path.read_text(encoding="utf-8"))
        except OSError:
            logger.warning(f"Design rule file not readable: {key}")
            parts.append(f"(File {key} could not be read)")

    content = "\n\n---\n\n".join(parts)
    return {"content": content, "matched_files": matched_keys, "topic": topic}
