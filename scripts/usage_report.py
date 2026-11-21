"""Private call-log report, standard library only.

Run: docker exec pcbparts-mcp python /app/scripts/usage_report.py --date 2026-11-21
Or: python scripts/usage_report.py --dir ./call-log --days 7
Dates are UTC. --days ends today; --date selects one day. No raw data is served over HTTP.
"""

import argparse
import datetime as dt
import gzip
import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path


def report(directory: Path, dates: list[str]) -> str:
    calls, apps, refusals, failures = Counter(), Counter(), Counter(), Counter()
    times, reasons, bad_reasons = defaultdict(list), defaultdict(Counter), defaultdict(Counter)
    malformed = 0
    for date in dates:
        source = directory / f"calls-{date}.jsonl"
        if not source.exists():
            source = source.with_suffix(".jsonl.gz")
        if source.exists():
            opener = gzip.open if source.suffix == ".gz" else open
            # Decode one line at a time so a crash in the middle of UTF-8 also stays local.
            with opener(source, "rb") as stream:
                for line in stream:
                    try:
                        row = json.loads(line.decode("utf-8"))
                        if not isinstance(row, dict):
                            raise ValueError("invalid row")
                        if "refused" in row:
                            if not isinstance(row["refused"], str) or type(row.get("count", 1)) is not int:
                                raise ValueError("invalid refusal")
                        elif (not isinstance(row["tool"], str) or not isinstance(row["outcome"], str)
                              or not isinstance(row["ms"], (int, float)) or not math.isfinite(row["ms"])
                              or any(row.get(key) is not None and not isinstance(row[key], str)
                                     for key in ("app", "reason", "bad_request_reason"))):
                            raise ValueError("invalid call")
                    except (ValueError, UnicodeError, KeyError, TypeError):
                        malformed += 1
                        continue
                    if "refused" in row:
                        refusals[row["refused"]] += row.get("count", 1)
                        continue
                    tool = row["tool"]
                    calls[tool, row["outcome"]] += 1
                    apps[row.get("app") or "unknown", tool] += 1
                    times[tool].append(row["ms"])
                    if row.get("reason"):
                        reasons[tool][row["reason"]] += 1
                    if row.get("bad_request_reason"):
                        bad_reasons[tool][row["bad_request_reason"]] += 1
        source = directory / f"failed-{date}.json"
        if source.exists():
            data = json.loads(source.read_text(encoding="utf-8"))
            for row in data["queries"]:
                failures[row["tool"], row["reason"], row["text"]] += row["count"]
    lines = [f"UTC dates: {', '.join(dates)}", "Calls by tool / outcome"]
    if malformed:
        lines.insert(1, f"Malformed call-log lines skipped: {malformed}")
    lines.extend(f"  {tool} / {outcome}: {count}" for (tool, outcome), count in sorted(calls.items()))
    lines.append("Calls by app / tool (top 20)")
    lines.extend(f"  {app} / {tool}: {count}" for (app, tool), count in apps.most_common(20))
    lines.append("Latency ms by tool (all calls; nearest-rank p50 / p95 / p99)")
    for tool, values in sorted(times.items()):
        values.sort()
        percentiles = [values[math.ceil(len(values) * p / 100) - 1] for p in (50, 95, 99)]
        lines.append(f"  {tool}: " + " / ".join(map(str, percentiles)))
    for title, groups in (("Top reasons by tool", reasons), ("Top bad_request reasons by tool", bad_reasons)):
        lines.append(title)
        for tool, counts in sorted(groups.items()):
            lines.extend(f"  {tool} / {reason}: {count}" for reason, count in counts.most_common(20))
    lines.append("Refusals")
    lines.extend(f"  {reason}: {count}" for reason, count in refusals.most_common())
    lines.append("Failed queries (top 50)")
    # JSON escaping makes control characters in a hand-edited file harmless in a terminal.
    lines.extend(f"  {tool} / {reason}: {count} {json.dumps(text, ensure_ascii=True)}"
                 for (tool, reason, text), count in failures.most_common(50))
    return "\n".join(lines)


def main(argv=None, *, today: dt.date | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", type=Path, default=os.getenv("CALL_LOG_DIR") or "/app/cache/call-log")
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--date", type=dt.date.fromisoformat, help="one UTC date, YYYY-MM-DD")
    choice.add_argument("--days", type=int, help="number of UTC days ending today")
    args = parser.parse_args(argv)
    if args.days is not None and args.days < 1:
        parser.error("--days must be at least 1")
    today = today or dt.datetime.now(dt.timezone.utc).date()
    dates = ([args.date.isoformat()] if args.date else
             [(today - dt.timedelta(days=i)).isoformat() for i in range(args.days or 1)])
    try:
        print(report(args.dir, dates))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Could not read usage files: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
