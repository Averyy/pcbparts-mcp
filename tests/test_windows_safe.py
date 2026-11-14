"""Patterns that pass on macOS and Linux but break or flake on the Windows CI runner.

- Wall-clock timing: Windows clocks tick every ~15.6 ms and CI runners stall, so a test that
  measures real elapsed time or sleeps to let time pass flakes there (0.9.3: a 20 ms pacing gap
  measured 14.99 ms; 0.7.1: a 0.25 s latency bound measured 0.76 s). Inject a fake clock instead:
  Pacer, DailyQuota, QuotaPool and SlidingWindowBudget take clock= (Pacer also sleep=), and a slow
  step in a test can advance that clock.
- Text reads without an encoding: Windows reads them as cp1252, so non-ASCII files fail to decode
  (0.9.0: the sensor tests failed to collect). Pass encoding="utf-8".

Other Windows rules the CI has taught, not checked here: close SQLite connections before deleting
their files, keep test ids short (path length), and don't run bash from a test (it starts WSL).
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
WALL_CLOCK = re.compile(r"\btime\.sleep\(|\bmonotonic\(\)|\bperf_counter\(\)")
WALL_CLOCK_ALLOWED = {
    "test_db_offload.py": "measures that a slow query in a worker thread keeps the event loop and "
                          "/health responsive; only real threads and real time can show that",
    "test_distributors.py": "TTLCache takes no clock; the expiry test sleeps 20 ms past a 10 ms TTL, "
                            "more than one Windows clock tick",
    "test_windows_safe.py": "this file",
}
BARE_READ = re.compile(r"\.read_text\(\)")


def _lines(paths):
    for path in paths:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            yield path, number, line


def test_tests_use_fake_clocks():
    tests = [p for p in sorted((ROOT / "tests").rglob("*.py")) if p.name not in WALL_CLOCK_ALLOWED]
    offenders = [f"{path.relative_to(ROOT).as_posix()}:{number}: {line.strip()}"
                 for path, number, line in _lines(tests) if WALL_CLOCK.search(line)]
    assert not offenders, ("Use an injected fake clock, not wall-clock time (see this test's "
                           "docstring):\n" + "\n".join(offenders))


def test_text_reads_say_utf8():
    files = sorted(p for folder in ("src", "scripts", "tests") for p in (ROOT / folder).rglob("*.py"))
    offenders = [f"{path.relative_to(ROOT).as_posix()}:{number}: {line.strip()}"
                 for path, number, line in _lines(files) if BARE_READ.search(line)]
    assert not offenders, 'Pass encoding="utf-8" (Windows reads text as cp1252):\n' + "\n".join(offenders)
