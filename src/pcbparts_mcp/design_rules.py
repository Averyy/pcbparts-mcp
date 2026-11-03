"""Design rules lookup — serves curated PCB design reference files."""

import logging
import os
import re
from pathlib import Path, PurePath

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
    # Words the file names don't contain; 16% of lookups found nothing (lipo, type-c, pull-up ...)
    "lipo": ["power/battery"],
    "li-po": ["power/battery"],
    "li-ion": ["power/battery"],
    "liion": ["power/battery"],
    "lithium": ["power/battery"],
    "18650": ["power/battery"],
    "charger": ["power/battery"],
    "charging": ["power/battery"],
    "fuel gauge": ["power/battery"],
    "ntc": ["power/battery"],
    "thermistor": ["power/battery"],
    "lifepo4": ["power/battery-chemistry"],
    "lfp": ["power/battery-chemistry"],
    "type-c": ["interfaces/usb"],
    "typec": ["interfaces/usb"],
    "pull-up": ["interfaces/i2c"],
    "pull-ups": ["interfaces/i2c"],
    "pullup": ["interfaces/i2c"],
    "pullups": ["interfaces/i2c"],
    "pull up": ["interfaces/i2c"],
    "stepper": ["misc/motor-control"],
    "bldc": ["misc/motor-control"],
    "rs485": ["interfaces/uart"],
    "rs-485": ["interfaces/uart"],
    "solar": ["power/power-path"],
    "mppt": ["power/power-path"],
    "layer": ["guides/pcb-layout"],
    "layers": ["guides/pcb-layout"],
    "2-layer": ["guides/pcb-layout"],
    "4-layer": ["guides/pcb-layout"],
    "6-layer": ["guides/pcb-layout"],
    "4 layer": ["guides/pcb-layout"],
    # "brown-out" found nothing: no file mentions it often enough for the text lookup
    **{word: ["protection/voltage-supervisor"] for word in (
        "brown-out", "brownout", "brown out", "brown-outs", "brownouts", "reset ic", "reset supervisor")},
    "strapping": ["mcus/esp32"],
    "strapping pins": ["mcus/esp32"],
    "jlcpcb": ["guides/dfm"],
    "pcba": ["guides/dfm"],
    "assembly": ["guides/dfm"],
    "dfa": ["guides/dfm"],
    "manufacturing": ["guides/dfm"],
}

_MAX_FULL_CONTENT = 3  # Return file list instead of content when more matches


def _rule_key(path: PurePath, rules_dir: PurePath) -> str:
    """Relative path without .md, e.g. "power/ldo".

    Always "/"-separated: str() would give "power\\ldo" on Windows, which
    _match_word and the _ALIASES keys don't recognize.
    """
    return path.relative_to(rules_dir).with_suffix("").as_posix()


def _build_index(rules_dir: Path) -> dict[str, Path]:
    """Glob all .md files, map category/stem to path, exclude non-rule files."""
    idx: dict[str, Path] = {}
    for p in sorted(rules_dir.rglob("*.md")):
        if p.name.upper() in _EXCLUDED_FILES:
            continue
        idx[_rule_key(p, rules_dir)] = p
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
    # A part number finds its family's file: "stm32g0" → mcus/stm32, "esp32s3" → mcus/esp32
    return word in tokens or any(
        len(t) >= 4 and any(c.isdigit() for c in t) and word.startswith(t) for t in tokens)


# A topic no file name or keyword covers is looked up in the text, scored by mentions (a heading
# counts _HEADING_WEIGHT). A file counts only if a heading names the topic or the text mentions it
# _MIN_MENTIONS times, and scores at least a third of the best file: "led" is mentioned in passing
# (Ethernet link LEDs, optocouplers) and finds nothing, rather than those files.
_HEADING_WEIGHT = 5
_MIN_MENTIONS = 8


def _topic_pattern(topic: str) -> re.Pattern | None:
    """"rs485" also matches "RS-485" and "pull up" "pull-up": parts joined by optional space or hyphen."""
    parts = [p for w in re.split(r"[\s\-]+", topic.lower()) for p in re.findall(r"[a-z]+|\d+(?:\.\d+)?|[^\sa-z\d]+", w)]
    if not parts:
        return None
    return re.compile(r"(?<![a-z\d])" + r"[\s\-]*".join(map(re.escape, parts)) + r"s?(?![a-z\d])", re.IGNORECASE)


def _mentioned_in(topic: str, idx: dict[str, Path]) -> list[str]:
    """Rule files that discuss the topic most, best first (at most _MAX_FULL_CONTENT)."""
    pattern = _topic_pattern(topic)
    if pattern is None:
        return []
    scores: dict[str, int] = {}
    for key, path in idx.items():
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        mentions = len(pattern.findall(text))
        headings = sum(len(pattern.findall(line)) for line in text.splitlines() if line.startswith("#"))
        if headings or mentions >= _MIN_MENTIONS:
            scores[key] = mentions + headings * (_HEADING_WEIGHT - 1)
    if not scores:
        return []
    floor = max(scores.values()) / 3
    ranked = sorted((k for k, v in scores.items() if v >= floor), key=lambda k: (-scores[k], k))
    return ranked[:_MAX_FULL_CONTENT]


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
    if not topic.strip() or topic.strip().casefold() == "index.md":
        content = index_path.read_text(encoding="utf-8") if index_path.exists() else "No INDEX.md found."
        return {"content": content, "matched_files": ["INDEX.md"], "topic": topic if topic.strip() else ""}

    # Cap input length (consistent with other tools)
    topic = topic[:500]

    # Keys returned by discovery are directly usable, including their category prefix.
    exact_key = next((key for key in idx if key.casefold() == topic.strip().casefold()), None)

    # Resolve aliases first (the whole topic, then each word as written, so "type-c" and
    # "4 layer" are found), then fall back to word matching. Remaining words are split on
    # hyphens too, so "op-amp" matches "op-amp-basics"
    alias_keys: set[str] = set(_ALIASES.get(" ".join(topic.lower().split()), []))
    unresolved_words: list[str] = []
    if not alias_keys:
        for word in topic.lower().split():
            if word in _ALIASES:
                alias_keys.update(_ALIASES[word])
                continue
            for w in (w for w in word.split("-") if w):
                if w in _ALIASES:
                    alias_keys.update(_ALIASES[w])
                else:
                    unresolved_words.append(w)

    # Collect matches: alias hits + word-boundary matches for remaining words
    matched_set: dict[str, Path] = {}
    for k, p in idx.items():
        if exact_key is not None:
            if k == exact_key:
                matched_set[k] = p
        elif k in alias_keys:
            matched_set[k] = p
        elif unresolved_words and any(_match_word(w, k.lower()) for w in unresolved_words):
            matched_set[k] = p

    matches = list(matched_set.items())
    note = None
    if not matches:
        # "strapping pins", "boot mode": no file is named for it, but one discusses it
        mentioned = _mentioned_in(topic, idx)
        matches = [(k, idx[k]) for k in mentioned]
        if mentioned:
            note = (f"No rule file is named for '{topic}'; these discuss it most. "
                    "An empty topic lists every rule file.")

    if not matches:
        index_content = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
        content = f"No rules found matching '{topic}'. Available rules:\n\n{index_content}"
        return {"content": content, "matched_files": [], "topic": topic}

    if note is None:
        matches = sorted(matches)  # text matches stay best first
    matched_keys = [k for k, _ in matches]

    if len(matches) > _MAX_FULL_CONTENT:
        content = (
            f"Found {len(matches)} rule files matching '{topic}'. "
            f"Call again with a more specific topic to get full content:\n\n"
            + "\n".join(f"- {k}" for k in matched_keys)
        )
        return {"content": content, "matched_files": matched_keys, "topic": topic}

    # Read and concatenate matched files
    parts = []
    for key, path in matches:
        try:
            parts.append(path.read_text(encoding="utf-8"))
        except OSError:
            logger.warning(f"Design rule file not readable: {key}")
            parts.append(f"(File {key} could not be read)")

    content = "\n\n---\n\n".join(parts)
    result = {"content": content, "matched_files": matched_keys, "topic": topic}
    if note:
        result["note"] = note
    return result
