"""Load test for a LOCAL pcbparts-mcp container: how many database-served tool calls a minute it
sustains (todo-platform-rate-limits.md). A tool, not a unit test; never point it at pcbparts.dev.

Each tool call is what a stateless MCP client sends: initialize, the initialized notification and
tools/call, three HTTP requests. Calls arrive at a fixed rate per step (open loop, like many
independent users), so past capacity they queue and the latency shows it.

Only tools that answer from the server's databases are called; anything that would make the server
send a JLCPCB, LCSC, EasyEDA, Mouser, DigiKey or SamacSys request is refused here
(jlc_get_part(lcsc=...), jlc_stock_check, jlc_find_alternatives, jlc_get_pinout, cse_*, mouser_*,
digikey_*, part_lifecycle). As a second guard, /mcp/stats' upstream and distributor `sent` counts
are read before the test and after every step, and the test stops if any rose.

Run the container with prod's limits and the per-address limits raised so they don't cap the test:

    docker build -t pcbparts-mcp:loadtest .
    docker run -d --name pcbparts-loadtest --cpus 1 --memory 1g -p 127.0.0.1:18080:8080 \\
        -e RATE_LIMIT_REQUESTS=1000000 -e PLATFORM_RATE_LIMIT=1000000 pcbparts-mcp:loadtest
    uv run python scripts/load_test.py --url http://127.0.0.1:18080 --container pcbparts-loadtest \\
        --rates 60,120,240,480 --step-seconds 60 --out /tmp/load.jsonl

--xff sends an X-Forwarded-For address (default: one of Anthropic's), so the platform path of the
rate limiter is the one exercised, as for claude.ai traffic from one address.
"""

import argparse
import asyncio
import json
import math
import random
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ROOT / "tests" / "baseline" / "queries.jsonl"
MPNS = ROOT / "tests" / "baseline" / "mpn_recoveries.jsonl"

# The only tools this script calls: they answer from the databases (jlc_get_part only with mpn=)
DATABASE_TOOLS = {"jlc_search", "jlc_get_part", "jlc_get_parts", "jlc_stock_history", "get_design_rules",
                  "sensor_recommend", "board_search"}

# The traffic mix (share of calls), from /mcp/stats on 2026-11-17 (jlc_get_part 45%, jlc_search 19%,
# jlc_stock_check 11%, jlc_stock_history 10%, the rest boards, rules, sensors and distributors) with
# each live lookup moved to its database-served counterpart: jlc_get_part(lcsc) to jlc_get_part(mpn)
# and jlc_get_parts, jlc_stock_check to jlc_get_parts.
MIXES = {
    "traffic": {"jlc_get_part_mpn": 35, "jlc_get_parts": 15, "jlc_search": 20, "jlc_stock_history": 10,
                "jlc_stock_history_batch": 5, "get_design_rules": 5, "sensor_recommend": 5, "board_search": 5},
    "search": {"jlc_search": 100},
    "history": {"jlc_stock_history": 100},  # one part per call: compare with prod's per-tool averages
    "light": {"jlc_get_part_mpn": 40, "jlc_get_parts": 20, "jlc_stock_history": 20, "jlc_stock_history_batch": 10,
              "get_design_rules": 10},
}

ACCEPT = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
PROTOCOL = "2025-06-18"


class Inputs:
    """Tool arguments: the baseline query corpus, MPNs from the MPN corpus, and LCSC codes collected
    from jlc_search answers during the warm-up."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.by_tool: dict[str, list[dict]] = defaultdict(list)
        for line in QUERIES.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entry = json.loads(line)
                if entry["tool"] in DATABASE_TOOLS and not (entry["tool"] == "jlc_get_part" and "lcsc" in entry["args"]):
                    self.by_tool[entry["tool"]].append(entry["args"])
        self.mpns = [a["mpn"] for a in self.by_tool.pop("jlc_get_part", []) if a.get("mpn")]
        self.mpns += [json.loads(line)["input"] for line in MPNS.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.lcsc: list[str] = []

    def call(self, kind: str) -> tuple[str, dict]:
        rng = self.rng
        if kind == "jlc_get_part_mpn":
            return "jlc_get_part", {"mpn": rng.choice(self.mpns)}
        if kind == "jlc_get_parts":
            count = rng.randint(10, 50)
            parts = [rng.choice(self.lcsc) if rng.random() < 0.8 else rng.choice(self.mpns) for _ in range(count)]
            return "jlc_get_parts", {"parts": parts}
        if kind == "jlc_stock_history":
            return "jlc_stock_history", {"lcsc": rng.choice(self.lcsc)}
        if kind == "jlc_stock_history_batch":
            return "jlc_stock_history", {"lcsc": rng.sample(self.lcsc, min(len(self.lcsc), rng.randint(10, 50)))}
        return kind, dict(rng.choice(self.by_tool[kind]))


def check_database_only(tool: str, arguments: dict) -> None:
    if tool not in DATABASE_TOOLS or (tool == "jlc_get_part" and arguments.get("lcsc")):
        raise SystemExit(f"refusing {tool}({arguments}): it could send a live request")


def sse_messages(reply: httpx.Response) -> list[dict]:
    if reply.headers.get("content-type", "").startswith("application/json"):
        return [reply.json()]
    return [json.loads(line[6:]) for line in reply.text.splitlines() if line.startswith("data: ")]


class Step:
    def __init__(self, rate: float):
        self.rate = rate  # calls a minute asked for
        self.started = self.ok = self.tool_errors = self.skipped = 0
        self.failures: Counter = Counter()
        self.latency: list[float] = []  # whole calls, seconds
        self.call_latency: list[float] = []  # the tools/call request alone
        self.per_tool: dict[str, list[float]] = defaultdict(list)
        self.memory: list[float] = []  # MiB
        self.cpu: list[float] = []  # percent of one CPU


async def mcp_call(client: httpx.AsyncClient, headers: dict, tool: str, arguments: dict, step: Step) -> dict | None:
    """One stateless tool call: initialize, notifications/initialized, tools/call."""
    check_database_only(tool, arguments)
    start = time.perf_counter()
    try:
        init = await client.post("/mcp", headers=headers, json={
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": PROTOCOL, "capabilities": {},
                       "clientInfo": {"name": "pcbparts-load-test", "version": "1"}}})
        if init.status_code != 200:
            step.failures[f"initialize HTTP {init.status_code}"] += 1
            return None
        call_headers = {**headers, "mcp-protocol-version": PROTOCOL}
        note = await client.post("/mcp", headers=call_headers,
                                 json={"jsonrpc": "2.0", "method": "notifications/initialized"})
        if note.status_code not in (200, 202):
            step.failures[f"initialized HTTP {note.status_code}"] += 1
            return None
        call_start = time.perf_counter()
        reply = await client.post("/mcp", headers=call_headers, json={
            "jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": tool, "arguments": arguments}})
        done = time.perf_counter()
        if reply.status_code != 200:
            step.failures[f"tools/call HTTP {reply.status_code}"] += 1
            return None
        messages = [m for m in sse_messages(reply) if m.get("id") == 2]
        if not messages or "result" not in messages[0]:
            step.failures["tools/call no result" if not messages else f"JSON-RPC error {messages[0].get('error')}"] += 1
            return None
    except httpx.TimeoutException:
        step.failures["timeout"] += 1
        return None
    except httpx.HTTPError as e:
        step.failures[type(e).__name__] += 1
        return None
    result = messages[0]["result"]
    step.ok += 1
    step.tool_errors += bool(result.get("isError"))
    step.latency.append(done - start)
    step.call_latency.append(done - call_start)
    step.per_tool[tool + ("(batch)" if isinstance(arguments.get("lcsc"), list) else "")].append(done - start)
    return result


async def upstream_sent(client: httpx.AsyncClient, headers: dict) -> dict[str, int]:
    """Every upstream and distributor `sent` count in /mcp/stats, since the container started."""
    reply = await client.get("/mcp/stats", params={"days": 30}, headers=headers)
    reply.raise_for_status()
    totals = reply.json()["totals"]
    sent = {f"upstream.{name}": counts.get("sent", 0) for name, counts in (totals.get("upstream") or {}).items()}
    sent |= {f"distributors.{name}": counts.get("sent", 0) for name, counts in (totals.get("distributors") or {}).items()}
    return sent


def rose(before: dict[str, int], after: dict[str, int]) -> dict[str, tuple[int, int]]:
    return {key: (before.get(key, 0), value) for key, value in after.items() if value > before.get(key, 0)}


async def sample_container(container: str, step: Step, stop: asyncio.Event) -> None:
    """docker stats every few seconds: memory (MiB) and CPU (% of one CPU)."""
    units = {"B": 1 / 2**20, "KiB": 1 / 1024, "MiB": 1, "GiB": 1024}
    while not stop.is_set():
        process = await asyncio.create_subprocess_exec(
            "docker", "stats", "--no-stream", "--format", "{{.MemUsage}}|{{.CPUPerc}}", container,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        out, _ = await process.communicate()
        if match := re.match(r"([\d.]+)(\w+)\s*/.*\|([\d.]+)%", out.decode().strip()):
            step.memory.append(float(match[1]) * units.get(match[2], 1))
            step.cpu.append(float(match[3]))
        try:
            await asyncio.wait_for(stop.wait(), 3)
        except TimeoutError:
            pass


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, math.ceil(p / 100 * len(ordered)) - 1))]


def summary(step: Step, seconds: float, drain: float, p95_limit: float) -> dict:
    ms = lambda v: None if v is None else round(v * 1000)  # noqa: E731
    failed = sum(step.failures.values())
    p95 = percentile(step.latency, 95)
    return {
        "target_calls_min": step.rate,
        "started": step.started, "ok": step.ok, "failed": failed, "skipped_inflight_cap": step.skipped,
        "tool_errors": step.tool_errors,
        "achieved_calls_min": round(step.ok / (seconds + drain) * 60),
        "achieved_requests_min": round(3 * step.ok / (seconds + drain) * 60),
        "drain_s": round(drain, 1),
        "p50_ms": ms(percentile(step.latency, 50)), "p90_ms": ms(percentile(step.latency, 90)),
        "p95_ms": ms(p95), "p99_ms": ms(percentile(step.latency, 99)),
        "max_ms": ms(max(step.latency) if step.latency else None),
        "tools_call_p50_ms": ms(percentile(step.call_latency, 50)),
        "tools_call_p95_ms": ms(percentile(step.call_latency, 95)),
        "per_tool_p50_p95_ms": {tool: [ms(percentile(v, 50)), ms(percentile(v, 95)), len(v)]
                                for tool, v in sorted(step.per_tool.items())},
        "failures": dict(step.failures),
        "memory_max_mib": round(max(step.memory)) if step.memory else None,
        "cpu_avg_pct": round(statistics.mean(step.cpu)) if step.cpu else None,
        "sustained": failed == 0 and step.skipped == 0 and p95 is not None and p95 < p95_limit
                     and step.ok >= 0.95 * step.started,
    }


async def run_step(client, headers, inputs: Inputs, mix: dict[str, int], rate: float, seconds: float,
                   max_inflight: int, container: str | None, rng: random.Random, timeout: float) -> tuple[Step, float]:
    step = Step(rate)
    kinds, weights = zip(*mix.items())
    stop = asyncio.Event()
    sampler = asyncio.create_task(sample_container(container, step, stop)) if container else None
    tasks: set[asyncio.Task] = set()
    interval = 60 / rate
    begin = time.perf_counter()
    next_at = begin
    while (now := time.perf_counter()) < begin + seconds:
        if now < next_at:
            await asyncio.sleep(next_at - now)
            continue
        next_at += interval
        if len(tasks) >= max_inflight:
            step.skipped += 1
            continue
        tool, arguments = inputs.call(rng.choices(kinds, weights)[0])
        step.started += 1
        task = asyncio.create_task(mcp_call(client, headers, tool, arguments, step))
        tasks.add(task)
        task.add_done_callback(tasks.discard)
    drain_start = time.perf_counter()
    if tasks:
        await asyncio.wait(set(tasks), timeout=timeout * 3 + 5)
    drain = time.perf_counter() - drain_start
    stop.set()
    if sampler:
        await sampler
    return step, drain


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default="http://127.0.0.1:18080")
    parser.add_argument("--rates", default="60,120,240", help="calls a minute for each step, comma-separated")
    parser.add_argument("--step-seconds", type=float, default=60)
    parser.add_argument("--mix", choices=sorted(MIXES), default="traffic")
    parser.add_argument("--xff", default="160.79.104.10", help="X-Forwarded-For address; empty: none")
    parser.add_argument("--container", help="docker container to sample memory and CPU from")
    parser.add_argument("--max-inflight", type=int, default=300)
    parser.add_argument("--timeout", type=float, default=30, help="seconds per HTTP request")
    parser.add_argument("--p95-limit", type=float, default=2.0, help="seconds; a step above it isn't sustained")
    parser.add_argument("--stop-after-unsustained", type=int, default=2)
    parser.add_argument("--pause", type=float, default=10, help="seconds between steps")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", help="append one JSON line per step here")
    args = parser.parse_args()
    if re.search(r"pcbparts\.dev", args.url):
        raise SystemExit("this is for a local container only")

    rng = random.Random(args.seed)
    inputs = Inputs(rng)
    headers = {**ACCEPT, **({"X-Forwarded-For": args.xff} if args.xff else {})}
    limits = httpx.Limits(max_connections=args.max_inflight, max_keepalive_connections=args.max_inflight)
    async with httpx.AsyncClient(base_url=args.url, timeout=args.timeout, limits=limits) as client:
        before = await upstream_sent(client, headers)
        print(f"upstream/distributor sent before: {before or 'none'}")
        # Warm-up: LCSC codes for the history and batch calls, and the databases' pages in memory
        warm = Step(0)
        for query in inputs.by_tool["jlc_search"][:40]:
            result = await mcp_call(client, headers, "jlc_search", query, warm)
            content = (result or {}).get("structuredContent") or {}
            inputs.lcsc += [part["lcsc"] for part in content.get("results", []) if part.get("lcsc")]
        inputs.lcsc = sorted(set(inputs.lcsc))
        print(f"warm-up: {warm.ok} searches ok, {sum(warm.failures.values())} failed, {len(inputs.lcsc)} LCSC codes, "
              f"{len(inputs.mpns)} MPNs; mix {args.mix}: {MIXES[args.mix]}")
        if len(inputs.lcsc) < 50:
            raise SystemExit("too few LCSC codes from the warm-up")
        after_warm = await upstream_sent(client, headers)
        if changed := rose(before, after_warm):
            print(f"STOP: upstream requests were sent during the warm-up: {changed}")
            return 3

        unsustained = 0
        for rate in [float(r) for r in args.rates.split(",")]:
            step, drain = await run_step(client, headers, inputs, MIXES[args.mix], rate, args.step_seconds,
                                         args.max_inflight, args.container, rng, args.timeout)
            result = {"mix": args.mix, "step_seconds": args.step_seconds, **summary(step, args.step_seconds, drain,
                                                                                   args.p95_limit)}
            after = await upstream_sent(client, headers)
            result["upstream_sent_rose"] = rose(before, after)
            print(json.dumps(result), flush=True)
            if args.out:
                with open(args.out, "a", encoding="utf-8") as out:
                    out.write(json.dumps(result) + "\n")
            if result["upstream_sent_rose"]:
                print(f"STOP: upstream requests were sent: {result['upstream_sent_rose']}")
                return 3
            unsustained = 0 if result["sustained"] else unsustained + 1
            if unsustained >= args.stop_after_unsustained:
                print(f"stopping: {unsustained} steps in a row not sustained")
                break
            await asyncio.sleep(args.pause)
        print(f"upstream/distributor sent after: {await upstream_sent(client, headers) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
