"""The AI platforms' higher per-address rate limit (0.10.0): Anthropic's and OpenAI's published
address ranges (platform_ranges.py), the OpenAI file and its checks, the config settings, and what
RateLimitMiddleware does with them (_limit_for, _refusal_group, headers, 429s, the refusal split in
/mcp/stats). No network: ASGI test clients, a fake clock, files in tmp_path."""

import datetime
import ipaddress
import json
import logging
import os
import runpy
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from pcbparts_mcp import config, platform_ranges, server, stats
from pcbparts_mcp.cache import SELF_HOSTING_URL, CallerTally
from pcbparts_mcp.platform_ranges import PlatformRanges, load, parse_openai_list
from pcbparts_mcp.stats import UsageStats

ROOT = Path(__file__).resolve().parent.parent
COMMITTED = ROOT / "data" / "platform_ranges" / "openai-chatgpt-connectors.json"
UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 18, 20, 5, tzinfo=UTC).timestamp()
ANTHROPIC = ["160.79.104.0/21", "153.61.208.0/20"]
OTHER = "203.0.113.7"


class Clock:
    def __init__(self, now: float = NOW):
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def nets(*values: str):
    return [ipaddress.ip_network(value) for value in values]


def openai_json(*entries) -> dict:
    return {"creationTime": "2026-11-06T18:26:55.215535", "prefixes": list(entries)}


def write(path: Path, data) -> Path:
    path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
    return path


class TestMatching:
    ranges = PlatformRanges({"anthropic": nets(*ANTHROPIC),
                             "openai": nets("100.31.168.162/32", "104.192.219.204/30", "2001:db8:10::/48")})

    @pytest.mark.parametrize("ip, inside", [
        ("160.79.104.0", True),  # first address of the /21
        ("160.79.111.255", True),  # last
        ("160.79.103.255", False),  # just below
        ("160.79.112.0", False),  # just above
        ("153.61.215.9", True),
        ("153.61.224.0", False),
        ("100.31.168.162", True),  # a /32
        ("100.31.168.163", False),
        ("104.192.219.207", True),  # last of a /30
        ("104.192.219.208", False),
        ("2001:db8:10::", True),
        ("2001:db8:10:ffff:ffff:ffff:ffff:ffff", True),
        ("2001:db8:11::", False),
        ("2001:DB8:10::1", True),  # any spelling of the address
        ("::ffff:160.79.104.10", True),  # IPv4-mapped IPv6 is the IPv4 address
        (" 160.79.104.10 ", True),
        (OTHER, False),
        ("::1", False),
        ("unknown", False),
        ("", False),
        ("160.79.104.0/21", False),  # a range isn't an address
    ], ids=lambda value: None if isinstance(value, bool) else "ip")
    def test_ip(self, ip, inside):
        assert (ip in self.ranges) is inside

    def test_not_a_string(self):
        assert None not in self.ranges and 1 not in self.ranges

    def test_empty(self):
        assert "160.79.104.10" not in PlatformRanges()
        assert len(PlatformRanges()) == 0

    def test_overlaps_merge(self):
        ranges = PlatformRanges({"a": nets("10.0.0.0/8"), "b": nets("10.1.0.0/16", "11.0.0.0/8")})
        assert ranges.counts == {"a": 1, "b": 2} and len(ranges) == 3
        assert "10.1.2.3" in ranges and "11.255.255.255" in ranges and "12.0.0.0" not in ranges


class TestOpenAIList:
    def test_shape(self):
        parsed = parse_openai_list(openai_json({"ipv4Prefix": "1.2.3.0/24"}, {"ipv6Prefix": "2001:db8::/32"},
                                               {"ipv4Prefix": "5.6.7.8/32", "region": "x"}))  # other keys ignored
        assert parsed.prefixes == nets("1.2.3.0/24", "2001:db8::/32", "5.6.7.8/32")
        assert parsed.created == "2026-11-06T18:26:55.215535"
        assert parse_openai_list({"prefixes": [{"ipv4Prefix": "1.2.3.4/24"}]}).prefixes == nets("1.2.3.0/24")
        assert parse_openai_list({"prefixes": [{"ipv4Prefix": "1.2.3.0/24"}]}).created is None

    @pytest.mark.parametrize("data", [
        [], "x", None,
        {"creationTime": "2026-11-06"},  # no prefixes
        {"prefixes": []},
        {"prefixes": {"ipv4Prefix": "1.2.3.0/24"}},
        openai_json({"ipv4Prefix": "1.2.3.0/24"}, "1.2.3.0/24"),
        openai_json({"prefix": "1.2.3.0/24"}),
        openai_json({"ipv4Prefix": "1.2.3.0/24", "ipv6Prefix": "2001:db8::/32"}),
        openai_json({"ipv4Prefix": "2001:db8::/32"}),  # wrong version for the key
        openai_json({"ipv6Prefix": "1.2.3.0/24"}),
        openai_json({"ipv4Prefix": "1.2.3.4"}),  # an address, not a prefix
        openai_json({"ipv4Prefix": "1.2.3.0/33"}),
        openai_json({"ipv4Prefix": "openai.com/24"}),
        openai_json({"ipv4Prefix": 16909056}),
    ], ids=range(15))
    def test_rejected(self, data):
        with pytest.raises(ValueError):
            parse_openai_list(data)

    @pytest.mark.parametrize("entries", [
        [{"ipv4Prefix": "0.0.0.0/0"}],
        [{"ipv4Prefix": "1.2.3.0/24"}, {"ipv4Prefix": "10.0.0.0/11"}],
        [{"ipv6Prefix": "::/0"}],
        [{"ipv6Prefix": "2001:db8::/31"}],
        [{"ipv4Prefix": f"{n}.0.0.0/12"} for n in (10, 20, 30, 40, 50)],  # each allowed, too many in all
        [{"ipv6Prefix": f"2001:{n:x}::/32"} for n in range(17)],
    ], ids=["all4", "wide4", "all6", "wide6", "sum4", "sum6"])
    def test_implausible_lists_rejected(self, entries):
        """Every address listed gets the platform limit: a list that would cover far more than
        OpenAI's connectors can't be used (docker-build.yml then keeps the committed copy)."""
        with pytest.raises(ValueError, match="plausible"):
            parse_openai_list(openai_json(*entries))

    def test_widest_plausible_prefixes_pass(self):
        entries = [{"ipv4Prefix": f"{n}.0.0.0/12"} for n in (10, 20, 30, 40)] + [
            {"ipv4Prefix": "10.0.0.0/12"},  # an overlap counts once
            *({"ipv6Prefix": f"2001:{n:x}::/32"} for n in range(16))]
        assert len(parse_openai_list(openai_json(*entries)).prefixes) == 21

    @pytest.mark.parametrize("created, kept", [
        ("2026-11-06T18:26:55.215535", True), ("2026-11-06T18:26:55+00:00", True), ("2026-11-06", True),
        ("x\n::error::forged", False), ("::add-mask::secret", False), ("2026-11-06 18:26", False),
        ("", False), ("1" * 41, False), (20261106, False), (None, False),
    ], ids=["iso", "offset", "date", "newline", "mask", "space", "empty", "long", "number", "none"])
    def test_creation_time_only_when_it_looks_like_one(self, created, kept):
        """creationTime is printed in CI logs and the server log: text that isn't an ISO time
        (a newline and ::error::, say) could be read as a workflow command, so it's dropped."""
        parsed = parse_openai_list({"creationTime": created, "prefixes": [{"ipv4Prefix": "1.2.3.0/24"}]})
        assert parsed.created == (created if kept else None)

    @pytest.mark.parametrize("entry", [{"ipv4Prefix": "1.2.3.0/24\n::error::x"}, {"x": "y\n::error::x"},
                                       {"ipv4Prefix": "2001:db8::/32\n::error::x"}], ids=["value", "entry", "version"])
    def test_errors_never_print_a_raw_newline(self, entry):
        with pytest.raises(ValueError) as error:
            parse_openai_list(openai_json(entry))
        assert "\n" not in str(error.value)

    def test_deep_nesting_and_byte_order_mark(self, tmp_path, capsys):
        """JSON nested past Python's recursion limit is a ValueError (load() never raises, and the CI
        check prints a reason, not a traceback); a UTF-8 byte order mark is fine."""
        nested = write(tmp_path / "nested.json", "[" * 100_000 + "]" * 100_000)
        with pytest.raises(ValueError, match="nested"):
            platform_ranges.read_openai_list(nested)
        loaded = load(ANTHROPIC, nested)
        assert loaded.ranges.counts["openai"] == 0 and "can't be used" in loaded.warnings[0]
        assert platform_ranges.main([str(nested)]) == 1
        assert "not a usable OpenAI address list" in capsys.readouterr().err
        bom = tmp_path / "bom.json"
        bom.write_bytes(b"\xef\xbb\xbf" + json.dumps(openai_json({"ipv4Prefix": "1.2.3.0/24"})).encode())
        assert platform_ranges.read_openai_list(bom).prefixes == nets("1.2.3.0/24")

    def test_load_never_raises(self, tmp_path, monkeypatch):
        def broken(path):
            raise RuntimeError("unforeseen")

        monkeypatch.setattr(platform_ranges, "read_openai_list", broken)
        loaded = load(ANTHROPIC, tmp_path / "x.json")
        assert loaded.ranges.counts == {"anthropic": 2, "openai": 0}
        assert "RuntimeError: unforeseen" in loaded.warnings[0]

    def test_committed_copy(self):
        """The fallback copy the image ships when CI can't refresh it, and config's default."""
        parsed = platform_ranges.read_openai_list(COMMITTED)
        assert len(parsed.prefixes) >= 100 and parsed.created
        assert Path(config.OPENAI_IP_RANGES_FILE) == COMMITTED

    def test_check_command(self, tmp_path, capsys):
        """docker-build.yml's check of a download: exit 0 for a usable list, 1 otherwise."""
        assert platform_ranges.main([str(COMMITTED)]) == 0
        assert "prefixes, created " in capsys.readouterr().out
        assert platform_ranges.main([str(write(tmp_path / "page.json", "<html>blocked</html>"))]) == 1
        assert platform_ranges.main([str(write(tmp_path / "empty.json", {"prefixes": []}))]) == 1
        assert platform_ranges.main([str(tmp_path / "missing.json")]) == 1
        assert "not a usable OpenAI address list" in capsys.readouterr().err
        assert platform_ranges.main([]) == 2

    def test_build_and_image_use_it(self):
        """CI checks the download with this module and replaces the committed copy; the image ships
        data/platform_ranges/ where config looks for it."""
        workflow = (ROOT / ".github" / "workflows" / "docker-build.yml").read_text(encoding="utf-8")
        assert "python3 -I src/pcbparts_mcp/platform_ranges.py" in workflow
        assert "committed=data/platform_ranges/openai-chatgpt-connectors.json" in workflow
        assert "https://openai.com/chatgpt-connectors.json" in workflow
        assert workflow.index("Refresh OpenAI's address list") < workflow.index("Build and push Docker image")
        step = workflow[workflow.index("Refresh OpenAI's address list"):workflow.index("Log in to the Container")]
        assert "--proto '=https' --proto-redir '=https'" in step  # never a plain-http redirect
        # The check's output (downloaded text) becomes one printable line before it's echoed
        assert "tr -c '[:print:]' ' ' | cut -c1-300" in step
        assert "about a day old at most" not in step
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        assert "COPY --chown=appuser:appuser data/platform_ranges/ /app/data/platform_ranges/" in dockerfile

    def test_stdlib_only(self):
        """CI runs it with the runner's bare python3, nothing installed."""
        source = (ROOT / "src" / "pcbparts_mcp" / "platform_ranges.py").read_text(encoding="utf-8")
        imports = {line.split()[1].split(".")[0] for line in source.splitlines()
                   if line.startswith(("import ", "from "))}
        assert imports <= {"bisect", "ipaddress", "json", "sys", "collections", "pathlib", "typing"}


class TestLoad:
    def test_both(self, tmp_path):
        path = write(tmp_path / "openai.json", openai_json({"ipv4Prefix": "100.31.168.162/32"}))
        loaded = load(ANTHROPIC, path)
        assert loaded.warnings == []
        assert loaded.openai_created == "2026-11-06T18:26:55.215535"
        assert loaded.ranges.counts == {"anthropic": 2, "openai": 1}
        assert loaded.summary == "2 Anthropic, 1 OpenAI (list created 2026-11-06T18:26:55.215535)"
        assert "160.79.104.1" in loaded.ranges and "100.31.168.162" in loaded.ranges

    @pytest.mark.parametrize("content", [None, "", "{", '{"prefixes": []}', '{"prefixes": [{"ipv4Prefix": "x/1"}]}'],
                             ids=["missing", "blank", "broken", "empty", "bad"])
    def test_unusable_file_leaves_openai_out(self, tmp_path, content):
        path = tmp_path / "openai.json"
        if content is not None:
            write(path, content)
        loaded = load(ANTHROPIC, path)
        assert loaded.ranges.counts == {"anthropic": 2, "openai": 0}
        assert "160.79.104.1" in loaded.ranges  # Anthropic's still apply
        assert len(loaded.warnings) == 1 and "OpenAI's addresses get the normal limit" in loaded.warnings[0]
        assert loaded.summary == "2 Anthropic, OpenAI's list not loaded"

    def test_turned_off(self):
        loaded = load([], "")
        assert (len(loaded.ranges), loaded.warnings) == (0, [])
        assert loaded.summary == "0 Anthropic, OpenAI's list not used (OPENAI_IP_RANGES_FILE is empty)"

    def test_bad_anthropic_value_skipped(self):
        loaded = load(["160.79.104.0/21", "not-a-range", "153.61.208.0/33"], None)
        assert loaded.ranges.counts["anthropic"] == 1
        assert len(loaded.warnings) == 2 and all(w.startswith("ANTHROPIC_IP_RANGES: skipped") for w in loaded.warnings)


class TestSettings:
    @staticmethod
    def settings(**env) -> dict:
        """config as a fresh process reads it with these environment variables (unset: None)."""
        environ = {k: v for k, v in os.environ.items()
                   if k not in ("PLATFORM_RATE_LIMIT", "RATE_LIMIT_REQUESTS", "ANTHROPIC_IP_RANGES",
                                "OPENAI_IP_RANGES_FILE")}
        environ.update({k: v for k, v in env.items() if v is not None})
        code = ("import json; from pcbparts_mcp import config as c; print(json.dumps([c.PLATFORM_RATE_LIMIT, "
                "c.RATE_LIMIT_REQUESTS, c.ANTHROPIC_IP_RANGES, c.OPENAI_IP_RANGES_FILE]))")
        done = subprocess.run([sys.executable, "-c", code], env=environ, capture_output=True, text=True,
                              encoding="utf-8", timeout=60, check=True)
        return dict(zip(("platform", "normal", "anthropic", "openai"), json.loads(done.stdout)))

    def test_defaults(self):
        got = self.settings()
        assert (got["platform"], got["normal"]) == (1000, 200)
        assert got["anthropic"] == ANTHROPIC
        assert Path(got["openai"]) == COMMITTED

    def test_overrides(self, tmp_path):
        got = self.settings(PLATFORM_RATE_LIMIT="1234", ANTHROPIC_IP_RANGES=" 10.0.0.0/8 , ,2001:db8::/32",
                            OPENAI_IP_RANGES_FILE=str(tmp_path / "x.json"))
        assert got["platform"] == 1234
        assert got["anthropic"] == ["10.0.0.0/8", "2001:db8::/32"]
        assert got["openai"] == str(tmp_path / "x.json")

    def test_empty_turns_lists_off(self):
        got = self.settings(ANTHROPIC_IP_RANGES="", OPENAI_IP_RANGES_FILE="")
        assert (got["anthropic"], got["openai"]) == ([], "")

    @pytest.mark.parametrize("name,value,used,warned", [
        ("PLATFORM_RATE_LIMIT", "", 1000, False),  # empty: the default (was a ValueError at import)
        ("PLATFORM_RATE_LIMIT", "1,000", 1000, True),
        ("PLATFORM_RATE_LIMIT", "1e3", 1000, True),
        ("PLATFORM_RATE_LIMIT", "0", 1, True),  # 0 refused every platform request
        ("PLATFORM_RATE_LIMIT", "2500", 2500, False),
        ("RATE_LIMIT_REQUESTS", "-5", 1, True),
        ("RATE_LIMIT_REQUESTS", "abc", 200, True),
        ("RATE_LIMIT_REQUESTS", " 250 ", 250, False),
    ], ids=["empty", "comma", "exp", "zero", "ok", "neg", "text", "padded"])
    def test_bad_limits_fall_back(self, monkeypatch, name, value, used, warned):
        monkeypatch.setenv(name, value)
        settings = runpy.run_path(config.__file__)
        assert settings[name] == used
        assert any(w.startswith(f"{name}=") for w in settings["CONFIG_WARNINGS"]) is warned


# The middleware

@pytest.fixture(autouse=True)
def tally(monkeypatch):
    """Refusals go to a fresh hourly tally, not the server's."""
    tally = CallerTally("Per-IP rate limit", Clock(), what="refusals")
    monkeypatch.setattr(server, "_refused_callers", tally)
    return tally


@pytest.fixture
def usage(monkeypatch):
    usage = UsageStats(clock=Clock())
    monkeypatch.setattr(stats, "usage", usage)
    return usage


PLATFORM_V4, PLATFORM_V6 = "160.79.104.10", "2001:db8:10::5"
RANGES = PlatformRanges({"anthropic": nets("160.79.104.0/21"), "openai": nets("2001:db8:10::/48")})


async def _ok(request):
    return PlainTextResponse("ok")


def app_with(clock: Clock, normal: int = 2, platform: int = 4, ranges: PlatformRanges | None = RANGES) -> Starlette:
    return Starlette(routes=[Route("/mcp", _ok, methods=["POST"]), Route("/health", _ok)],
                     middleware=[Middleware(server.RateLimitMiddleware, requests_per_minute=normal, clock=clock,
                                            wall_clock=clock, platform_per_minute=platform,
                                            platform_addresses=ranges)])


def client(app) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://localhost")


def limits(reply: httpx.Response) -> tuple[str | None, ...]:
    return tuple(reply.headers.get(f"x-ratelimit-{name}") for name in ("limit", "remaining", "reset"))


def post(c: httpx.AsyncClient, ip: str):
    return c.post("/mcp", headers={"X-Forwarded-For": ip})


class TestMiddleware:
    def test_limit_and_group(self):
        middleware = server.RateLimitMiddleware(None, requests_per_minute=100, platform_per_minute=2500,
                                                platform_addresses=RANGES)
        for ip in (PLATFORM_V4, PLATFORM_V6, "::ffff:160.79.104.10"):
            assert (middleware._limit_for(ip), middleware._refusal_group(ip)) == (2500, "platform_ranges")
        for ip in (OTHER, "160.79.112.1", "2001:db8:11::1", "unknown"):
            assert (middleware._limit_for(ip), middleware._refusal_group(ip)) == (100, "everyone_else")

    async def test_headers_and_refusals(self, usage):
        clock = Clock()
        async with client(app_with(clock)) as c:
            platform = [await post(c, PLATFORM_V4) for _ in range(5)]
            other = [await post(c, OTHER) for _ in range(3)]
            ipv6 = [await post(c, PLATFORM_V6) for _ in range(5)]
            health = await c.get("/health", headers={"X-Forwarded-For": PLATFORM_V4})
        assert [r.status_code for r in platform] == [200] * 4 + [429]
        assert [limits(r) for r in platform[:2]] == [("4", "3", "60"), ("4", "2", "60")]
        assert [r.status_code for r in other] == [200, 200, 429]
        assert limits(other[0]) == ("2", "1", "60")
        assert [r.status_code for r in ipv6] == [200] * 4 + [429]
        assert limits(health) == ("4", "0", "60")
        body = platform[-1].json()
        assert (body["error"], body["retry_after"], body["reason"]) == ("Rate limit exceeded", 60, "per_ip_rate_limit")
        assert body["tell_user"] == (
            "pcbparts allows 4 requests a minute per address, and this address is shared by many users of the "
            f"same AI platform; try again in 60 seconds, or run your own copy for heavy use: {SELF_HOSTING_URL}")
        assert other[-1].json()["tell_user"].startswith("pcbparts allows 2 requests a minute per address; try again")
        # The refusals are split by group in /mcp/stats, without IPs
        assert usage.summary()["days"][0]["per_ip_refusals"] == {"total": 3, "everyone_else": 1, "platform_ranges": 2, "server_busy": 0, "too_many_clients": 0}

    async def test_thousands_in_tell_user(self):
        clock = Clock()
        async with client(app_with(clock, platform=2500)) as c:
            for _ in range(2500):
                await post(c, PLATFORM_V4)
            refused = await post(c, PLATFORM_V4)
        assert limits(refused) == ("2500", "0", "60")
        assert refused.json()["tell_user"].startswith("pcbparts allows 2,500 requests a minute per address, and this")

    async def test_no_ranges_means_normal_limit(self):
        clock = Clock()
        async with client(app_with(clock, ranges=PlatformRanges())) as c:
            assert [(await post(c, PLATFORM_V4)).status_code for _ in range(3)] == [200, 200, 429]

    async def test_loads_config_once_at_start(self, tmp_path, monkeypatch, caplog):
        """Without platform_addresses the middleware reads config's ranges when Starlette builds it
        (the app's start), logs how many, and keeps them."""
        path = write(tmp_path / "openai.json", openai_json({"ipv6Prefix": "2001:db8:10::/48"}))
        monkeypatch.setattr(server, "ANTHROPIC_IP_RANGES", ["160.79.104.0/21"])
        monkeypatch.setattr(server, "OPENAI_IP_RANGES_FILE", str(path))
        monkeypatch.setattr(server, "PLATFORM_RATE_LIMIT", 3)
        monkeypatch.setattr(server, "RATE_LIMIT_REQUESTS", 1)
        app = Starlette(routes=[Route("/mcp", _ok, methods=["POST"])],
                        middleware=[Middleware(server.RateLimitMiddleware, requests_per_minute=1,
                                               platform_per_minute=3, clock=Clock())])
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.server"):
            async with client(app) as c:
                assert limits(await post(c, PLATFORM_V6)) == ("3", "2", "60")
                path.unlink()  # read once: later requests don't need the file
                assert limits(await post(c, PLATFORM_V4)) == ("3", "2", "60")
                assert limits(await post(c, OTHER)) == ("1", "0", "60")
        assert [m for m in caplog.messages if m.startswith("Platform address ranges")] == [
            "Platform address ranges: 1 Anthropic, 1 OpenAI (list created 2026-11-06T18:26:55.215535); "
            "3 requests a minute per platform address, 1 for others"]

    async def test_bad_file_warns_and_degrades(self, tmp_path, monkeypatch, caplog):
        monkeypatch.setattr(server, "ANTHROPIC_IP_RANGES", ["160.79.104.0/21"])
        monkeypatch.setattr(server, "OPENAI_IP_RANGES_FILE", str(write(tmp_path / "openai.json", "<html>")))
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.server"):
            ranges = server._load_platform_ranges()
        assert ranges.counts == {"anthropic": 1, "openai": 0}
        assert any(r.levelno == logging.WARNING and "can't be used" in r.getMessage() for r in caplog.records)

    async def test_real_app(self):
        """The app as served: the committed OpenAI copy and Anthropic's ranges from config."""
        committed = platform_ranges.read_openai_list(COMMITTED)
        openai_address = str(committed.prefixes[0].network_address)
        async with client(server.create_app()) as c:
            for ip in ("160.79.104.10", "153.61.208.1", openai_address):
                health = await c.get("/health", headers={"X-Forwarded-For": ip})
                assert limits(health)[0] == str(server.PLATFORM_RATE_LIMIT), ip
            health = await c.get("/health", headers={"X-Forwarded-For": OTHER})
            assert limits(health)[0] == str(server.RATE_LIMIT_REQUESTS)
        # /health says which OpenAI list the server runs with, so a refresh that keeps failing shows
        assert health.json()["platform_ranges"] == {
            "anthropic": 2, "openai": len(committed.prefixes), "openai_list_created": committed.created}
