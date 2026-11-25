"""Keep public distributor wording independent of credential topology."""

from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN = re.compile(
    r"MOUSER_API_KEY_\d+|MOUSER_EXTRA_API_KEYS|MouserKeyPool|\bper[- ]key\b|"
    r"\bMouser(?:['’]s)?\s+(?:API\s+)?keys\b|\bkey\s*#?\s*\d+\b|"
    r"\b(?:next|each|other|active|remaining|spare|refused|both|every|all|per)\s+(?:Mouser\s+|API\s+)?keys?\b|"
    r"\b(?:a key refused|key numbers?|episodes per key)\b|\bswitch(?:es|ing)?\s+keys\b|\bquarantin\w*|"
    r"\b(?:multiple|several|extra|second|another)\s+(?:Mouser\s+|API\s+)?keys?\b|"
    r"DIGIKEY_(?:CLIENT_ID|CLIENT_SECRET)_\d+|\bsecond\s+DigiKey\s+app\b|"
    r"\bDigiKey(?:['’]s)?\s+(?:second|extra|another)\s+app\b|"
    r"\b(?:keyless|credential[- ]free)\s+DigiKey\b|"
    r"\bDigiKey(?:['’]s)?\s+(?:without\s+(?:credentials|an?\s+(?:API\s+)?key)|keyless|credential[- ]free)\b",
    re.IGNORECASE,
)
ALLOWED = re.compile(
    r"\byour own keys?\b|\bNo API key required\b|"
    # Catalog names, limiter dictionary ordering and stored JSON record merging.
    r"every key against `data/subcategories\.json`|"
    r"each key's last request|each key of the stored record",
    re.IGNORECASE,
)


def leaks_in(text):
    text = ALLOWED.sub(lambda match: re.sub(r"[^\n]", " ", match.group()), text)
    return [(text.count("\n", 0, match.start()) + 1, match.group()) for match in FORBIDDEN.finditer(text)]


def test_public_text_does_not_describe_multiple_mouser_credentials():
    paths = [ROOT / name for name in (
        "README.md", "CHANGELOG.md", "landing/llms.txt", "dashboard/README.md", "CLAUDE.md", "CONTRIBUTING.md")
             if (ROOT / name).exists()]
    paths.extend((ROOT / "landing").glob("*.html"))
    paths.extend(path for path in (ROOT / "docs").glob("*.md") if path.name != "do-later.md")
    # do-later.md is the deliberately uncommitted private backlog.
    paths.extend((ROOT / "dashboard/docs").rglob("*.md"))
    paths.extend(path for path in (ROOT / "dashboard/src").rglob("*")
                 if path.suffix in {".js", ".html", ".css", ".svg", ".py"})
    leaks = []
    for path in paths:
        for number, text in leaks_in(path.read_text(encoding="utf-8")):
            leaks.append(f"{path.relative_to(ROOT)}:{number}: {text}")
    assert not leaks, "\n".join(leaks)


@pytest.mark.parametrize("text", [
    "Mouser keys", "Mouser's keys", "Mouser’s API keys", "Mouser\nAPI keys", "key 2", "key #2", "key2",
    *[f"{word} {kind}key{plural}" for word in
      ("next", "each", "other", "active", "remaining", "spare", "refused", "both", "every", "all", "per")
      for kind in ("", "Mouser ", "API ") for plural in ("", "s")],
    "second DigiKey app", "DigiKey's second app", "keyless DigiKey", "DigiKey without credentials",
    "credential-free DigiKey", "DigiKey's credential-free path", "rejections stay quarantined",
])
def test_public_text_guard_detects_credential_disclosures(text):
    assert leaks_in(text)


@pytest.mark.parametrize("text", ["your own key", "your own keys", "No API key required",
                                "Mouser lookups", "DigiKey API", "JSON object keys",
                                "every key against `data/subcategories.json`",
                                "each key's last request", "each key of the stored record"])
def test_public_text_guard_allows_unrelated_wording(text):
    assert not leaks_in(text)


def test_distributor_retry_and_reset_docs_cover_the_release():
    reference = (ROOT / "landing/llms.txt").read_text(encoding="utf-8")
    assert "1,000 Mouser and DigiKey lookups combined per UTC day; retries don't count" in reference
    assert '"This address has used its 1000 Mouser and DigiKey lookups for today..."' in reference
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release = changelog.split("## 0.10.9 (", 1)[1].split("\n## ", 1)[0]
    breaking = release.split("### Breaking", 1)[1].split("### Added", 1)[0]
    assert "**`/health`**: no longer has `distributor_quota`" in breaking
    assert "distributor pauses, reset times and daily counts" in breaking
    assert "daily counts are in the authenticated `/mcp/stats`" in breaking
    added, rest = release.split("### Added", 1)[1].split("### Changed", 1)
    changed, fixed = rest.split("### Fixed", 1)
    assert "**`/mcp/stats`**: `distributor_quota` gives each distributor's daily count" in added
    assert "**Usage dashboard**" in changed and "**Usage dashboard**" not in fixed
    assert "per-address daily cap counts lookups; retries don't count" in changed
    assert "second request" in fixed and "per-address cap partway through" in fixed
