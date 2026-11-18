"""The AI platforms' published outbound address ranges, which get a higher per-address rate limit
(server.RateLimitMiddleware) because many of their users share each address: claude.ai and ChatGPT
connectors call us from the platform's servers, not the user's machine.

- Anthropic: two ranges, kept in config (ANTHROPIC_IP_RANGES), which Anthropic says won't change
  without notice (https://platform.claude.com/docs/en/api/ip-addresses).
- OpenAI: its ChatGPT connectors list (https://openai.com/chatgpt-connectors.json), which it says
  can change. docker-build.yml downloads it on every image build and checks it with this file
  (`python3 -I src/pcbparts_mcp/platform_ranges.py FILE`), keeping the committed copy in
  data/platform_ranges/ when the download fails or doesn't check out. The server never downloads it.

An address missing from a list just gets the normal limit, so a stale list degrades gently.
Standard library only, so the CI check runs without installing anything.
"""

import bisect
import ipaddress
import json
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple

Network = ipaddress.IPv4Network | ipaddress.IPv6Network

# The keys an entry of OpenAI's "prefixes" list may have, and the IP version each one holds
OPENAI_PREFIX_KEYS = {"ipv4Prefix": 4, "ipv6Prefix": 6}
# What a plausible list holds, per IP version: no prefix shorter than this, and at most this many
# addresses in all (overlaps counted once). Every address in the list gets the platform limit, so a
# list such as 0.0.0.0/0 (a bad download or a changed format) would give it to everyone. The
# 2026-11 list: 289 IPv4 prefixes, the largest a /16 and a /23, 69,243 addresses, no IPv6.
OPENAI_SHORTEST_PREFIX = {4: 12, 6: 32}
OPENAI_MAX_ADDRESSES = {4: 2 ** 22, 6: 2 ** 100}  # four /12s; sixteen /32s


class OpenAIList(NamedTuple):
    prefixes: list[Network]
    created: str | None  # the file's creationTime, as given


def parse_openai_list(data: Any) -> OpenAIList:
    """The prefixes of OpenAI's chatgpt-connectors.json, already parsed from JSON:
    {"creationTime": "...", "prefixes": [{"ipv4Prefix": "a.b.c.d/n"}, {"ipv6Prefix": "..."}, ...]}.

    Raises ValueError unless it's an object with a non-empty "prefixes" list in which every entry
    has exactly one of ipv4Prefix/ipv6Prefix holding a prefix of that IP version (other keys are
    ignored), so a changed format is noticed instead of half read, and the list is plausible: no
    prefix shorter than OPENAI_SHORTEST_PREFIX, no more addresses than OPENAI_MAX_ADDRESSES. Host
    bits after the prefix length are ignored."""
    if not isinstance(data, dict):
        raise ValueError("not a JSON object")
    entries = data.get("prefixes")
    if not isinstance(entries, list) or not entries:
        raise ValueError("no prefixes list, or an empty one")
    prefixes = []
    for number, entry in enumerate(entries, 1):
        keys = [key for key in OPENAI_PREFIX_KEYS if isinstance(entry, dict) and key in entry]
        if len(keys) != 1:
            raise ValueError(f"prefix {number} doesn't have exactly one of ipv4Prefix and ipv6Prefix: "
                             f"{str(entry)[:80]}")
        key = keys[0]
        value = entry[key]
        if not isinstance(value, str) or "/" not in value:
            raise ValueError(f"prefix {number} ({key}) isn't an address/length: {str(value)[:80]}")
        try:
            network = ipaddress.ip_network(value.strip(), strict=False)
        except ValueError as e:
            raise ValueError(f"prefix {number} ({key}): {e}") from None
        if network.version != OPENAI_PREFIX_KEYS[key]:
            raise ValueError(f"prefix {number} is under {key} but is IPv{network.version}: {value}")
        if network.prefixlen < OPENAI_SHORTEST_PREFIX[network.version]:
            raise ValueError(f"prefix {number} ({network}) is wider than a "
                             f"/{OPENAI_SHORTEST_PREFIX[network.version]}: not a plausible connector range")
        prefixes.append(network)
    for version, most in OPENAI_MAX_ADDRESSES.items():
        size = sum(network.num_addresses for network in ipaddress.collapse_addresses(
            network for network in prefixes if network.version == version))
        if size > most:
            raise ValueError(f"the IPv{version} prefixes cover {size:,} addresses, more than {most:,}: "
                             "not a plausible connector list")
    created = data.get("creationTime")
    return OpenAIList(prefixes, created if isinstance(created, str) else None)


def read_openai_list(path: str | Path) -> OpenAIList:
    """Read and check OpenAI's list from a file. Raises OSError or ValueError."""
    return parse_openai_list(json.loads(Path(path).read_text(encoding="utf-8")))


def parse_ranges(values: Iterable[str]) -> tuple[list[Network], list[str]]:
    """Ranges given as text (ANTHROPIC_IP_RANGES): the ones that parse, and one problem for each
    that doesn't (skipped)."""
    networks, problems = [], []
    for value in values:
        try:
            networks.append(ipaddress.ip_network(value.strip(), strict=False))
        except ValueError as e:
            problems.append(f"{value!r}: {e}")
    return networks, problems


class PlatformRanges:
    """Address ranges by platform, answering `ip in ranges` with a binary search per IP version."""

    def __init__(self, ranges: Mapping[str, Sequence[Network]] | None = None):
        ranges = dict(ranges or {})
        self.counts = {name: len(networks) for name, networks in ranges.items()}
        # Per IP version, the merged ranges as sorted, non-overlapping (first, last) address ints
        self._starts: dict[int, list[int]] = {}
        self._ends: dict[int, list[int]] = {}
        for version in (4, 6):
            merged = list(ipaddress.collapse_addresses(
                network for networks in ranges.values() for network in networks if network.version == version))
            self._starts[version] = [int(network.network_address) for network in merged]
            self._ends[version] = [int(network.broadcast_address) for network in merged]

    def __contains__(self, ip: object) -> bool:
        if not isinstance(ip, str):
            return False
        try:
            address = ipaddress.ip_address(ip.strip())
        except ValueError:  # "unknown", a hostname, garbage
            return False
        if address.version == 6 and address.ipv4_mapped is not None:  # ::ffff:a.b.c.d is a.b.c.d
            address = address.ipv4_mapped
        value, starts = int(address), self._starts[address.version]
        index = bisect.bisect_right(starts, value) - 1
        return index >= 0 and value <= self._ends[address.version][index]

    def __len__(self) -> int:
        return sum(self.counts.values())


class Loaded(NamedTuple):
    ranges: PlatformRanges
    summary: str  # one line for the startup log
    warnings: list[str]


def load(anthropic: Iterable[str], openai_file: str | Path | None) -> Loaded:
    """The platform ranges from config: Anthropic's as text, OpenAI's from its file (None or empty:
    not used). Never raises: a bad Anthropic value is skipped and a missing or bad OpenAI file
    leaves OpenAI out, each with a warning, and those addresses get the normal limit."""
    warnings = []
    anthropic_ranges, problems = parse_ranges(anthropic)
    warnings += [f"ANTHROPIC_IP_RANGES: skipped {problem}" for problem in problems]
    openai_ranges: list[Network] = []
    if not openai_file:
        openai_note = "OpenAI's list not used (OPENAI_IP_RANGES_FILE is empty)"
    else:
        try:
            openai_list = read_openai_list(openai_file)
        except (OSError, ValueError) as e:
            warnings.append(f"OpenAI's address list {openai_file} can't be used ({e}): "
                            "OpenAI's addresses get the normal limit")
            openai_note = "OpenAI's list not loaded"
        else:
            openai_ranges = openai_list.prefixes
            openai_note = f"{len(openai_ranges)} OpenAI (list created {openai_list.created or 'at an unknown time'})"
    summary = f"{len(anthropic_ranges)} Anthropic, {openai_note}"
    return Loaded(PlatformRanges({"anthropic": anthropic_ranges, "openai": openai_ranges}), summary, warnings)


def main(argv: list[str]) -> int:
    """`platform_ranges.py FILE`: exit 0 and print the count if FILE is a usable OpenAI list, else
    exit 1 with the reason (docker-build.yml's check of a fresh download)."""
    if len(argv) != 1:
        print("usage: platform_ranges.py OPENAI_LIST.json", file=sys.stderr)
        return 2
    try:
        openai_list = read_openai_list(argv[0])
    except (OSError, ValueError) as e:
        print(f"not a usable OpenAI address list: {e}", file=sys.stderr)
        return 1
    print(f"{len(openai_list.prefixes)} prefixes, created {openai_list.created or 'unknown'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
