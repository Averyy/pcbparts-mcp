"""SamacSys searches and model downloads: one retry for a 5xx, a dropped connection or an
unreadable reply, never during an outage (the retry guard). HTTP mock transports, a fake clock
and fake sleeps only."""

import io
import logging
import zipfile

import httpx
import pytest

from pcbparts_mcp import cse as cse_module, stats
from pcbparts_mcp.cse import CSEClient

NOW = 1_793_546_220.0
SUCCESS = {"status": "Success", "partCount": 1,
           "parts": [{"PartNo": "P1", "Manuf": "TI", "PartID": 1, "ECAD_M": "x", "Quality": 3}]}


def kicad_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("P1/KiCad/P1.kicad_sym", "(kicad_symbol_lib)")
        zf.writestr("P1/KiCad/P1.kicad_mod", "(module P1)")
    return buf.getvalue()


class Fake:
    """A CSEClient answering from a list of replies (an httpx.Response, or an exception to raise),
    with the fake clock its waits move."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.requests: list[httpx.Request] = []
        self.waits: list[float] = []
        self.now = NOW

        async def sleep(seconds):
            self.waits.append(seconds)
            self.now += seconds

        self.client = CSEClient(clock=lambda: self.now, sleep=sleep)
        self.client._http = httpx.AsyncClient(transport=httpx.MockTransport(self.answer))

    def answer(self, request):
        self.requests.append(request)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


@pytest.fixture
async def fake(monkeypatch):
    monkeypatch.setattr(cse_module, "CSE_RATE_LIMIT", 0)
    monkeypatch.setattr(cse_module, "CSE_USER", "user")
    monkeypatch.setattr(cse_module, "CSE_PASS", "pass")
    made = []

    def create(*replies):
        made.append(Fake(*replies))
        return made[-1]

    yield create
    for item in made:
        await item.client.close()


def sent() -> int:
    return stats.usage.summary()["totals"]["upstream"]["cse"]["sent"]


def retries() -> int:
    """upstream.cse.retries: the requests this server itself sent again (also in sent)."""
    return stats.usage.summary()["totals"]["upstream"]["cse"]["retries"]


def ok():
    return httpx.Response(200, json=SUCCESS)


TRANSIENT = {
    "5xx": lambda: httpx.Response(503, text="<p>Service Unavailable</p>"),
    "conn": lambda: httpx.ConnectError("refused"),
    "html": lambda: httpx.Response(200, text="<html>maintenance</html>"),
    "list": lambda: httpx.Response(200, json=["not", "an", "object"]),
}
SEARCH_ERRORS = {"5xx": "CSE API returned HTTP 503", "conn": "CSE API request failed (network/connection error)",
                 "html": "CSE API returned an unreadable reply (HTTP 200)",
                 "list": "CSE API returned an unreadable reply (HTTP 200)"}


class TestSearch:
    @pytest.mark.parametrize("kind", list(TRANSIENT))
    async def test_one_failure_then_success(self, fake, kind, caplog):
        f = fake(TRANSIENT[kind](), ok())
        with caplog.at_level(logging.WARNING, logger="pcbparts_mcp.cse"):
            result = await f.client.search("P1")
        assert [r["cse_part_id"] for r in result["results"]] == [1]
        assert len(f.requests) == 2 and f.waits == [3.0] and sent() == 2 and retries() == 1
        assert "sending it again in 3 s" in caplog.text

    @pytest.mark.parametrize("kind", list(TRANSIENT))
    async def test_two_failures_give_the_clear_error(self, fake, kind):
        f = fake(TRANSIENT[kind](), TRANSIENT[kind]())
        with pytest.raises(ValueError) as raised:
            await f.client.search("P1")
        assert str(raised.value) == SEARCH_ERRORS[kind]
        assert len(f.requests) == 2 and f.waits == [3.0] and sent() == 2 and retries() == 1

    async def test_a_timeout_is_not_sent_again(self, fake):
        f = fake(httpx.ReadTimeout("slow"))
        with pytest.raises(ValueError, match=r"network/connection error"):
            await f.client.search("P1")
        assert len(f.requests) == 1 and f.waits == [] and sent() == 1 and retries() == 0

    async def test_the_second_ask_after_a_status_answer_is_not_a_retry(self, fake):
        f = fake(httpx.Response(200, json={"status": "F0R0", "parts": []}), ok())
        assert (await f.client.search("P1"))["total"] == 1
        assert sent() == 2 and retries() == 0

    @pytest.mark.parametrize("status", [400, 404, 429])
    async def test_a_4xx_is_not_sent_again(self, fake, status):
        f = fake(httpx.Response(status))
        with pytest.raises(ValueError, match=f"CSE API returned HTTP {status}"):
            await f.client.search("P1")
        assert len(f.requests) == 1 and f.waits == []

    @pytest.mark.parametrize("after,waits", [("2", [2.0]), ("0", [0.0]), ("3", [3.0]), ("4", []), ("120", [])],
                             ids=["2", "0", "3", "4", "120"])
    async def test_retry_after_up_to_3_s_is_the_wait(self, fake, after, waits):
        f = fake(httpx.Response(503, headers={"Retry-After": after}), ok())
        if waits:
            assert (await f.client.search("P1"))["total"] == 1
        else:
            with pytest.raises(ValueError, match="HTTP 503"):
                await f.client.search("P1")
        assert f.waits == waits and len(f.requests) == 1 + bool(waits)

    async def test_failure_then_a_status_answer_stays_within_two_requests(self, fake):
        f = fake(httpx.Response(502), httpx.Response(200, json={"status": "F0R0", "parts": []}))
        with pytest.raises(ValueError, match=r"no usable answer \(status other than Success\)$"):
            await f.client.search("P1")
        assert len(f.requests) == 2

    async def test_a_status_answer_then_a_failure_stays_within_two_requests(self, fake):
        f = fake(httpx.Response(200, json={"status": "R0F0", "parts": []}), httpx.Response(503))
        with pytest.raises(ValueError, match="HTTP 503"):
            await f.client.search("P1")
        assert len(f.requests) == 2 and f.waits == [3.0]


def model(content=None, status=200):
    return httpx.Response(status, content=kicad_zip() if content is None else content,
                          headers={"content-type": "application/zip" if content is None else "text/plain"})


DOWNLOAD_TRANSIENT = {
    "5xx": lambda: httpx.Response(503, text="<p>Unavailable</p>"),
    "conn": lambda: httpx.RemoteProtocolError("dropped"),
    "html": lambda: model(b"<html>maintenance</html>"),
}
DOWNLOAD_ERRORS = {"5xx": "CSE model download failed (HTTP 503)",
                   "conn": "CSE model download failed (network/connection error)",
                   "html": "CSE returned invalid zip file"}


class TestDownload:
    @pytest.mark.parametrize("kind", list(DOWNLOAD_TRANSIENT))
    async def test_one_failure_then_the_files(self, fake, kind):
        f = fake(DOWNLOAD_TRANSIENT[kind](), model())
        result = await f.client.get_kicad(part_id=7)
        assert result["kicad_footprint"] == "(module P1)" and "error" not in result
        assert len(f.requests) == 2 and f.waits == [3.0] and sent() == 2 and retries() == 1

    @pytest.mark.parametrize("kind", list(DOWNLOAD_TRANSIENT))
    async def test_two_failures_give_the_clear_error(self, fake, kind):
        f = fake(DOWNLOAD_TRANSIENT[kind](), DOWNLOAD_TRANSIENT[kind]())
        assert (await f.client.get_kicad(part_id=7)) == {"error": DOWNLOAD_ERRORS[kind]}
        assert len(f.requests) == 2 and f.waits == [3.0] and sent() == 2 and retries() == 1

    async def test_a_retry_the_quota_pause_stops_is_neither_sent_nor_counted(self, fake):
        f = fake(httpx.Response(503))

        async def sleep(seconds):  # meanwhile another download was refused for the quota
            f.client._quota_until = f.now + 1800

        f.client._sleep = sleep
        assert "daily model download limit" in (await f.client.get_kicad(part_id=7))["error"]
        assert len(f.requests) == 1 and sent() == 1 and retries() == 0

    @pytest.mark.parametrize("reply,error", [
        (lambda: httpx.ReadTimeout("slow"), "CSE model download failed (network/connection error)"),
        (lambda: httpx.Response(404), "CSE model download failed (HTTP 404)"),
        (lambda: httpx.Response(401), "CSE authentication failed. Check CSEARCH_USER and CSEARCH_PASS."),
        (lambda: model(b"Error: no part data available for partID 7"), "No ECAD model available for part 7"),
        (lambda: model(b"Error: access denied"), "CSE refused the model download for part 7: Error: access denied"),
        (lambda: httpx.Response(503, text="Error: Daily part download quota exceeded"),
         "CSE model download failed (HTTP 503)"),
    ], ids=["timeout", "404", "401", "nodata", "refused", "quota5xx"])
    async def test_not_sent_again(self, fake, reply, error):
        f = fake(reply())
        assert (await f.client.get_kicad(part_id=7))["error"] == error
        assert len(f.requests) == 1 and f.waits == []

    async def test_a_quota_refusal_is_never_sent_again(self, fake):
        f = fake(model(b"Error: Daily part download quota exceeded"))
        reply = await f.client.get_kicad(part_id=7)
        assert "daily model download limit" in reply["error"]
        assert len(f.requests) == 1 and f.waits == []

    async def test_a_quota_refusal_on_the_retry_pauses_downloads(self, fake):
        f = fake(httpx.Response(500), model(b"Error: Daily part download quota exceeded"))
        assert "daily model download limit" in (await f.client.get_kicad(part_id=7))["error"]
        assert len(f.requests) == 2 and f.client._quota_until > f.now
        assert "daily model download limit" in (await f.client.get_kicad(part_id=8))["error"]
        assert len(f.requests) == 2  # paused: nothing more goes out

    async def test_a_lookup_by_query_sends_at_most_two_of_each(self, fake):
        f = fake(httpx.Response(503), ok(), httpx.ConnectError("refused"), httpx.ConnectError("refused"))
        reply = await f.client.get_kicad(query="P1")
        assert reply["error"] == "CSE model download failed (network/connection error)"
        assert [r.url.path for r in f.requests] == ["/alligatorHandler.php"] * 2 + ["/ga/model.php"] * 2


class TestRetryGuard:
    async def test_no_retries_during_a_run_of_failures_until_it_clears(self, fake, caplog):
        # Five searches failing twice each: 10 transient failures of 10 attempts turn retries off
        f = fake(*(httpx.Response(503) for _ in range(10)))
        with caplog.at_level(logging.INFO, logger="pcbparts_mcp.cse"):
            for _ in range(5):
                with pytest.raises(ValueError, match="HTTP 503"):
                    await f.client.search("P1")
            assert len(f.requests) == 10 and f.client._guard.disabled()
            assert "CSE retry guard entered: 10/10 transient failures" in caplog.text
            # Searches and downloads share it: each sends once now
            f.replies.extend([httpx.Response(503), httpx.Response(502)])
            with pytest.raises(ValueError, match="HTTP 503"):
                await f.client.search("P2")
            assert (await f.client.get_kicad(part_id=7))["error"] == "CSE model download failed (HTTP 502)"
            assert len(f.requests) == 12 and len(f.waits) == 5 and retries() == 5
            # Five minutes later the failures have aged out: a failure is retried again
            f.now += 301
            f.replies.extend([httpx.Response(503), ok()])
            assert (await f.client.search("P3"))["total"] == 1
            assert len(f.requests) == 14 and f.waits[-1] == 3.0 and retries() == 6
            assert "CSE retry guard cleared" in caplog.text

    async def test_successes_keep_retries_on(self, fake):
        f = fake(*(ok() for _ in range(9)), httpx.Response(503), ok())
        for number in range(9):
            await f.client.search(f"P{number}")
        assert (await f.client.search("P9"))["total"] == 1
        assert len(f.requests) == 11 and f.waits == [3.0]

    async def test_an_outage_that_begins_during_the_wait_stops_the_retry(self, fake):
        f = fake(httpx.Response(503))

        async def sleep(seconds):  # meanwhile, other requests fail
            for _ in range(10):
                f.client._guard.record(transient=True)

        f.client._sleep = sleep
        with pytest.raises(ValueError, match="HTTP 503"):
            await f.client.search("P1")
        assert len(f.requests) == 1

    @pytest.mark.parametrize("reply,transient", [
        (lambda: httpx.Response(503), True), (lambda: httpx.ConnectError("x"), True),
        (lambda: httpx.Response(200, text="<html>"), True), (lambda: ok(), False),
        (lambda: httpx.Response(404), False), (lambda: httpx.ReadTimeout("x"), False),
    ], ids=["5xx", "conn", "html", "ok", "404", "timeout"])
    async def test_every_sent_search_records_an_outcome(self, fake, reply, transient):
        f = fake(reply(), ok())
        try:
            await f.client.search("P1")
        except ValueError:
            pass
        outcomes = [row[1:] for row in f.client._guard.outcomes]
        assert outcomes == ([[1, 2]] if transient else [[0, 1]])

    @pytest.mark.parametrize("reply,transient", [
        (lambda: httpx.Response(503), True), (lambda: model(b"<html>"), True), (lambda: model(), False),
        (lambda: httpx.Response(401), False), (lambda: model(b"Error: Daily part download quota exceeded"), False),
    ], ids=["5xx", "html", "zip", "401", "quota"])
    async def test_every_sent_download_records_an_outcome(self, fake, reply, transient):
        f = fake(reply(), model())
        await f.client.get_kicad(part_id=7)
        outcomes = [row[1:] for row in f.client._guard.outcomes]
        assert outcomes == ([[1, 2]] if transient else [[0, 1]])
