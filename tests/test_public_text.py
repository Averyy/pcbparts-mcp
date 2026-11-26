"""Keep public distributor wording independent of credential topology."""

from pathlib import Path
import re
import subprocess

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

# Source files also contain the existing API configuration identifiers. Guard extension
# wording separately so that checking source text doesn't require renaming that interface.
_PROVIDER_NEAR = (r"(?:browsers?|headless|Chrome|Xvfb|scrap\w*|website|site[-_ ]path|Cloudflare|bypass\w*|"
                  r"challenge[-_ ]solv\w*|solv\w*\s+(?:the\s+)?challenges?|no\s+API\s+key)")
PROVIDER_FORBIDDEN = re.compile(
    r"\b(?:keyless|credentials?[-_ ]free|no[-_ ]credentials(?:[-_ ]mode)?)\b|"
    r"(?<![a-z0-9])(?:without|no)[_\s]+(?:DigiKey[_\s]+)?(?:API[_\s]+)?credentials\b|"
    r"\bDigiKey(?:['’]s)?\s+without\s+an?\s+(?:API\s+)?key\b|"
    r"\bdigikey[_ ]site\b|\bDIGIKEY_LOOKUP(?:_\w+)?\b|\bBrowserSolver\b|\bpatchright\b|"
    r"digikey\.\w+/products/api\b|"
    # Matched across line breaks: a phrase wrapped onto the next line must not slip through.
    rf"\bDigiKey\b[^.]{{0,80}}\b{_PROVIDER_NEAR}|"
    rf"\b{_PROVIDER_NEAR}[^.]{{0,80}}\bDigiKey\b|"
    r"\bspend(?:s)? no daily limit\b",
    re.IGNORECASE,
)
PROVIDER_ALLOWED = {
    # This test checks the unrelated SamacSys login requirement.
    "tests/test_distributors.py": re.compile(r"\btest_get_kicad_no_credentials\b"),
}


def provider_leaks_in(text, path=""):
    if allowed := PROVIDER_ALLOWED.get(path):
        text = allowed.sub(lambda match: " " * len(match.group()), text)
    return [(text.count("\n", 0, match.start()) + 1, match.group())
            for match in PROVIDER_FORBIDDEN.finditer(text)]


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


def test_source_and_tests_keep_extension_wording_generic():
    # Include new, not-yet-staged source files too; ignored local files are not project inputs.
    listed = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "src/", "tests/"],
        cwd=ROOT).decode("utf-8").split("\0")
    paths = [ROOT / name for name in set(listed) if name]
    # Public documents, the landing site, workflows and container files too.
    paths += [ROOT / name for name in ("README.md", "CHANGELOG.md", "CLAUDE.md", "CONTRIBUTING.md",
                                       "Dockerfile", "docker-compose.yml", "docker-compose.local.yml")]
    paths += list((ROOT / "landing").rglob("*")) + list((ROOT / ".github").rglob("*"))
    paths += [path for path in (ROOT / "docs").glob("*.md") if path.name != "do-later.md"]
    paths += list((ROOT / "dashboard").glob("*.md")) + list((ROOT / "dashboard/docs").rglob("*.md"))
    leaks = []
    for path in set(paths):
        if (not path.is_file() or path == Path(__file__).resolve()
                or (path.suffix not in {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".html", ".toml"}
                    and path.name not in {"Dockerfile"})):
            continue
        for number, text in provider_leaks_in(path.read_text(encoding="utf-8"), path.relative_to(ROOT).as_posix()):
            leaks.append(f"{path.relative_to(ROOT)}:{number}: {text}")
    assert not leaks, "\n".join(sorted(leaks))


@pytest.mark.parametrize("text", [
    "For authenticated /mcp/stats without credentials", "no credentials: no daily limit to spend",
    "spend no daily limit", "test_server_extension_without_credentials",
    "DigiKey without credentials and no Mouser key", "DigiKey site path", "DigiKey browser solve",
    "scraping DigiKey", "DigiKey Cloudflare bypass", "digikey_site", "DIGIKEY_LOOKUP",
    "keyless DigiKey", "credential-free DigiKey", "DigiKey without an API key", "BrowserSolver", "patchright",
    "without DigiKey credentials", "with no DigiKey API credentials set", "credentials-free", "no-credentials mode",
    "scrape DigiKey", "the DigiKey scraper", "DigiKey's website", "https://www.digikey.com/products/api/v5",
    "DigiKey lookups\nthrough a headless browser", "DigiKey (no API key)",
])
def test_source_guard_catches_provider_disclosures(text):
    assert provider_leaks_in(text)


@pytest.mark.parametrize("text", [
    "DigiKey backup", "optional extension provider", "DigiKey API credentials not configured",
    "Cloudflare response from JLCPCB", "Open the dashboard in your browser", "DIGIKEY_LOCALE_SITE",
    "the daily JLCPCB scrape", "DigiKey API credentials (free at https://developer.digikey.com)",
    "Mouser and DigiKey answers are kept per part number. The scrape runs daily",
])
def test_source_guard_allows_unrelated_wording(text):
    assert not provider_leaks_in(text)


def test_source_guard_allowlist_is_specific_to_the_samacsys_test():
    text = "def test_get_kicad_no_credentials():"
    assert not provider_leaks_in(text, "tests/test_distributors.py")
    assert provider_leaks_in(text, "tests/test_extensions.py")
    assert provider_leaks_in("DigiKey without credentials", "tests/test_distributors.py")


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
    assert "300 Mouser and DigiKey lookups combined per UTC day; retries don't count" in reference
    assert '"This address has used its 300 Mouser and DigiKey lookups for today..."' in reference
    assert '"Live Mouser and DigiKey lookups are turned off for this address..."' in reference
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
