"""Validate changelog sections and print notes for a minor or major release."""

import argparse
from datetime import date
from pathlib import Path
import re
import sys


VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
HEADING = re.compile(rf"## ({VERSION}) \(([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})\)")


def release_notes(changelog: str, version: str, last_release: str | None = None) -> str | None:
    """Return newest-first notes, excluding last_release; patches validate but return None.

    Validate only the selected entries and boundary: older changelog history can use
    legacy headings. With no previous release, every entry from version onward is selected.
    """
    if not re.fullmatch(VERSION, version):
        raise ValueError(f"invalid release version {version!r}; expected X.Y.Z")
    headings = list(re.finditer(r"^[ \t]*##(?!#)[^\r\n]*", changelog, re.MULTILINE))

    def find_heading(wanted: str, label: str) -> int:
        matches = [i for i, heading in enumerate(headings)
                   if re.match(rf"[ \t]*##[ \t]*{re.escape(wanted)}(?=\s|$)", heading[0])]
        if not matches:
            raise ValueError(f"missing {label} heading for {wanted}; expected ## {wanted} (YYYY-MM-DD)")
        if len(matches) != 1:
            raise ValueError(f"duplicate heading for {wanted}")
        return matches[0]

    def validate_heading(index: int) -> str:
        text = headings[index][0]
        match = HEADING.fullmatch(text)
        if not match:
            raise ValueError(f"malformed heading {text!r}; expected ## X.Y.Z (YYYY-MM-DD)")
        entry_version, entry_date = match.groups()
        try:
            date.fromisoformat(entry_date)
        except ValueError:
            raise ValueError(f"malformed date in heading {text!r}; expected a valid YYYY-MM-DD") from None
        find_heading(entry_version, "release")  # Also reject a duplicate outside the selected range.
        return entry_version

    start = find_heading(version, "current-version")
    patch = int(version.rsplit(".", 1)[1]) != 0
    stop = start + 1 if patch else len(headings)
    if not patch and last_release:
        if not re.fullmatch(VERSION, last_release):
            raise ValueError(f"invalid previous-release version {last_release!r}; expected X.Y.Z")
        stop = find_heading(last_release, "previous-release boundary")
        validate_heading(stop)
        if stop <= start or tuple(map(int, last_release.split("."))) >= tuple(map(int, version.split("."))):
            raise ValueError(f"previous-release boundary {last_release} must be older than {version}")

    for index in range(start, stop):
        entry_version = validate_heading(index)
        end = headings[index + 1].start() if index + 1 < len(headings) else len(changelog)
        body = changelog[headings[index].end():end]
        if not any(line.strip() and not line.lstrip().startswith("#") for line in body.splitlines()):
            raise ValueError(f"empty notes for {entry_version}")

    if patch:
        return None
    end = headings[stop].start() if stop < len(headings) else len(changelog)
    return changelog[headings[start].start():end].strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("--last-release", default=None)
    parser.add_argument("--changelog", type=Path, default=Path("CHANGELOG.md"))
    args = parser.parse_args(argv)
    try:
        notes = release_notes(args.changelog.read_text(encoding="utf-8"), args.version, args.last_release)
    except (OSError, ValueError) as error:
        print(f"release notes: {error}", file=sys.stderr)
        return 1
    if notes is not None:
        print(notes, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
