"""CSE answers kept across restarts (cse_store.py): a year for a search where every part has a
model and for KiCad files, a week for a search with a part that has no model yet or no parts."""

import asyncio
from contextlib import asynccontextmanager
import io
import json
import logging
import sys
import threading
from types import SimpleNamespace
import time
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastmcp import Client

from pcbparts_mcp.config import CSE_FOUND_TTL, CSE_NOT_FOUND_TTL
from pcbparts_mcp.cse import CSEClient
from pcbparts_mcp.cse_store import CSEStore, query_key
from pcbparts_mcp import config, cse as cse_module, cse_archive, cse_store, server, stats

DAY = 86400


def part(part_id, has_model=True):
    return {"PartNo": f"P{part_id}", "Manuf": "TI", "PartID": part_id, "Desc": "",
            "ECAD_M": f"https://componentsearchengine.com/model.php?partID={part_id}" if has_model else "",
            "Has3D": "N", "Quality": 3 if has_model else 0, "PinCount": 8}


def response(json_data=None, content=None, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
    if content is not None:
        mock.content = content
    return mock


def kicad_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("P1/KiCad/P1.kicad_sym", "(kicad_symbol_lib)")
        zf.writestr("P1/KiCad/P1.kicad_mod", "(module P1)")
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _close_stores(monkeypatch):
    """Close every store a test opens: each holds its SQLite file open (Windows can't remove it)."""
    opened = []
    original = CSEStore.__init__

    def tracking_init(self, *args, **kwargs):
        original(self, *args, **kwargs)
        opened.append(self)

    monkeypatch.setattr(CSEStore, "__init__", tracking_init)
    yield
    for store in opened:
        store.close()


def client_with(store_path, answers):
    """A CSEClient whose HTTP calls return answers(url) and are counted in .urls."""
    client = CSEClient(store_path=str(store_path))
    client.urls = []

    async def get(url, **kwargs):
        client.urls.append(str(url))
        return answers(str(url))

    client._http = AsyncMock()
    client._http.get = get
    return client


class TestStore:
    def test_search_with_models_kept_a_year(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        result = {"results": [{"has_model": True}, {"has_model": True}], "total": 2}
        store.put_search("LM358P", 0, result, fetched_at=0)
        assert store.get_search("lm358p", 0, now=CSE_FOUND_TTL - DAY) == result
        assert store.get_search("lm358p", 0, now=CSE_FOUND_TTL + DAY) is None

    def test_search_with_a_part_without_model_kept_a_week(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        store.put_search("NE555", 0, {"results": [{"has_model": True}, {"has_model": False}]}, fetched_at=0)
        assert store.get_search("NE555", 0, now=6 * DAY) is not None
        assert store.get_search("NE555", 0, now=CSE_NOT_FOUND_TTL + DAY) is None

    def test_empty_search_kept_a_week(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        store.put_search("NOPE123", 0, {"results": [], "total": 0}, fetched_at=0)
        assert store.get_search("NOPE123", 0, now=6 * DAY) is not None
        assert store.get_search("NOPE123", 0, now=8 * DAY) is None

    def test_kicad_files_kept_for_good(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        files = {"kicad_symbol": "(sym)", "kicad_footprint": "(mod)"}
        store.put_kicad(12345, files, fetched_at=0)  # stored in 1970: far past any TTL
        assert store.get_kicad("12345") == files and store.get_kicad(12345) == files
        store.prune()
        assert store.get_kicad(12345) == files

    def test_kept_across_instances(self, tmp_path):
        CSEStore(tmp_path / "cse.db").put_search("LM358P", 0, {"results": [{"has_model": True}]})
        assert CSEStore(tmp_path / "cse.db").get_search("LM358P", 0) is not None

    def test_pages_are_separate(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        store.put_search("LM358P", 0, {"results": [{"has_model": True}]})
        assert store.get_search("LM358P", 10) is None

    def test_prune_and_counts(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        now = time.time()
        store.put_search("old-incomplete", 0, {"results": []}, fetched_at=now - 8 * DAY)
        store.put_search("old-complete", 0, {"results": [{"has_model": True}]}, fetched_at=now - 8 * DAY)
        store.put_kicad(1, {"kicad_symbol": "x"}, fetched_at=now - 400 * DAY)
        store.put_kicad(2, {"kicad_symbol": "y"}, fetched_at=now)
        store.prune(now=now)
        assert store.counts() == {"searches": 1, "kicad": 2, "wanted": 0}  # KiCad files have no TTL

    def test_unusable_path_never_raises(self, tmp_path):
        blocker = tmp_path / "file"
        blocker.write_text("not a directory")
        store = CSEStore(blocker / "cse.db")
        assert not store.enabled
        assert store.get_search("LM358P", 0) is None
        assert store.put_search("LM358P", 0, {"results": []}) is False
        assert store.counts() == {"searches": 0, "kicad": 0, "wanted": 0}

    def test_query_key(self):
        assert query_key("  LM358P ") == query_key("lm358p") == "lm358p"
        assert query_key("LM358 P") == "lm358 p"


@pytest.fixture
def no_retry_wait():
    with patch("pcbparts_mcp.cse.CSE_STATUS_RETRY_DELAY", 0):
        yield


class TestClient:
    async def test_search_survives_a_restart(self, tmp_path):
        """A new client (a restart) answers from the store without asking CSE."""
        answer = {"status": "Success", "partCount": 1, "parts": [part(1)]}
        first = client_with(tmp_path / "cse.db", lambda url: response(answer))
        await first.search("LM358P")
        assert len(first.urls) == 1

        second = client_with(tmp_path / "cse.db", lambda url: response(answer))
        result = await second.search("lm358p")
        assert second.urls == []
        assert result["results"][0]["cse_part_id"] == 1

    async def test_case_shares_the_memory_cache(self, tmp_path):
        answer = {"status": "Success", "partCount": 1, "parts": [part(1)]}
        client = CSEClient()
        client.urls = []

        async def get(url, **kwargs):
            client.urls.append(url)
            return response(answer)

        client._http = AsyncMock()
        client._http.get = get
        await client.search("LM358P")
        await client.search(" lm358p ")
        assert len(client.urls) == 1

    async def test_failed_search_not_stored(self, tmp_path, no_retry_wait):
        client = client_with(tmp_path / "cse.db", lambda url: response({"status": "Error"}))
        with pytest.raises(ValueError, match="no usable answer"):
            await client.search("LM358P")
        assert len(client.urls) == 2
        assert CSEStore(tmp_path / "cse.db").counts()["searches"] == 0

    @pytest.mark.parametrize("status", ["F0R0", "R0F0"])
    async def test_a_part_found_only_on_the_second_ask_is_returned(self, tmp_path, no_retry_wait, status):
        """GD32F103CBT6 and MP2315GJ-Z came back this way, and read as "no parts found"."""
        answers = iter([response({"status": status, "partCount": 3, "parts": [part(9)]}),
                        response({"status": "Success", "partCount": 0, "parts": [part(1)]})])
        client = client_with(tmp_path / "cse.db", lambda url: next(answers))
        result = await client.search("GD32F103CBT6")
        assert len(client.urls) == 2
        assert [p["cse_part_id"] for p in result["results"]] == [1]  # the first answer's parts are dropped
        assert CSEStore(tmp_path / "cse.db").counts()["searches"] == 1

    async def test_unrelated_parts_in_a_first_answer_are_not_returned(self, tmp_path, no_retry_wait):
        """blorptastic9: status F0R0 and 10 unrelated parts, then Success and none."""
        answers = iter([response({"status": "F0R0", "partCount": 700, "parts": [part(9)]}),
                        response({"status": "Success", "partCount": 0, "parts": []})])
        client = client_with(tmp_path / "cse.db", lambda url: next(answers))
        assert (await client.search("blorptastic9"))["results"] == []

    async def test_a_success_answer_is_not_asked_twice(self, tmp_path, no_retry_wait):
        client = client_with(tmp_path / "cse.db", lambda url: response({"status": "Success", "parts": [part(1)]}))
        await client.search("LM358P")
        assert len(client.urls) == 1

    async def test_kicad_lookup_does_not_report_a_retried_part_as_missing(self, tmp_path, no_retry_wait):
        answers = iter([response({"status": "R0F0", "parts": []}),
                        response({"status": "Success", "partCount": 1, "parts": [part(1)]})])
        client = client_with(tmp_path / "cse.db", lambda url: response(content=kicad_zip()) if "model.php" in url else next(answers))
        with patch("pcbparts_mcp.cse.CSE_USER", "u"), patch("pcbparts_mcp.cse.CSE_PASS", "p"):
            result = await client.get_kicad(query="P1")
        assert "error" not in result and result["kicad_footprint"] == "(module P1)"

    async def test_kicad_files_survive_a_restart(self, tmp_path):
        search = {"status": "Success", "partCount": 1, "parts": [part(1)]}

        def answers(url):
            return response(search) if "alligator" in url else response(content=kicad_zip())

        with patch("pcbparts_mcp.cse.CSE_USER", "user"), patch("pcbparts_mcp.cse.CSE_PASS", "pass"):
            first = client_with(tmp_path / "cse.db", answers)
            await first.get_kicad(query="P1")
            assert len(first.urls) == 2  # search, download

            second = client_with(tmp_path / "cse.db", answers)
            result = await second.get_kicad(query="P1")
        assert second.urls == []
        assert result["kicad_symbol"] == "(kicad_symbol_lib)"

    async def test_store_counts(self, tmp_path):
        assert CSEClient().store_counts() is None
        client = client_with(tmp_path / "cse.db", lambda url: response({"status": "Success", "parts": [part(1)]}))
        await client.search("P1")
        assert client.store_counts() == {"searches": 1, "kicad": 0, "wanted": 0}
        await client.close()


@pytest.mark.parametrize("parts,expected", [
    ([part(1), part(2)], CSE_FOUND_TTL),
    ([part(1), part(2, has_model=False)], CSE_NOT_FOUND_TTL),
    ([], CSE_NOT_FOUND_TTL),
])
async def test_lifetime_follows_models(tmp_path, parts, expected):
    client = client_with(tmp_path / "cse.db", lambda url: response({"status": "Success", "parts": parts}))
    await client.search("Q")
    store = CSEStore(tmp_path / "cse.db")
    now = time.time()
    assert store.get_search("Q", 0, now=now + expected - DAY) is not None
    assert store.get_search("Q", 0, now=now + expected + DAY) is None


QUOTA = ("SamacSys's daily model download limit for this shared server is used up; "
         "the KiCad model couldn't be downloaded. Try again at {} (UTC), when this server next checks the quota. "
         "KiCad files pcbparts already has stored still work.")
QUOTA_BODY = b"Error: Daily part download quota exceeded"


@pytest.fixture
async def model_client(tmp_path, monkeypatch):
    monkeypatch.setattr(cse_module, "CSE_USER", "test-login@example.com")
    monkeypatch.setattr(cse_module, "CSE_PASS", "s3cr3t<value>")
    monkeypatch.setattr(cse_module, "CSE_RATE_LIMIT", 0)
    now, answers, downloads = [1793546220.0], [], []

    async def sleep(seconds):  # a retry's wait: the fake clock
        now[0] += seconds

    client = CSEClient(str(tmp_path / "cse.db"), clock=lambda: now[0], sleep=sleep, monotonic=lambda: now[0])

    def answer(request):
        if "model.php" in request.url.path:
            downloads.append(request.url.params["partID"])
            now[0] += 0.5
            body = answers.pop(0)
            return httpx.Response(200, content=body, headers={"content-type": "text/plain;charset=UTF-8"})
        return httpx.Response(200, json={"status": "Success", "parts": [part(1)]})

    client._http = httpx.AsyncClient(transport=httpx.MockTransport(answer))
    yield client, now, answers, downloads
    await client.close()


class TestDownloadRefusals:
    @pytest.mark.parametrize("path", ["paused", "queued", "upstream"])
    @pytest.mark.parametrize("known", [False, True], ids=["unknown", "known"])
    async def test_quota_store_work_runs_off_loop_and_looks_up_once(self, model_client, path, known):
        client, now, answers, downloads = model_client
        store = client._store
        # A full scan is costly on a real store; exercise it without wall-clock assertions.
        store._conn.executemany("INSERT INTO searches VALUES (?, 0, ?, 1, ?)", (
            (f"search-{i}", json.dumps({"results": [cse_module._normalize_part(part(i))]}), now[0])
            for i in range(1, 20_001)
        ))
        store._conn.commit()
        if path != "upstream":
            client._quota_until = now[0] + config.CSE_QUOTA_RETRY_SECONDS
        if path == "paused":
            client._refused_since = now[0]
        if path == "upstream":
            answers.append(QUOTA_BODY)
        requested = 20_000 if known else -1
        loop_thread = threading.get_ident()
        statements = []
        store._conn.set_trace_callback(lambda sql: statements.append((sql, threading.get_ident())))
        try:
            reply = await client.get_kicad(part_id=requested)
        finally:
            store._conn.set_trace_callback(None)

        scans = [sql for sql, _ in statements if sql.startswith("SELECT result FROM searches")]
        assert len(scans) == 1
        assert statements and all(thread != loop_thread for _, thread in statements)
        assert reply["part_id"] == requested and "daily model download limit" in reply["error"]
        assert reply.get("mfr_part_number") == ("P20000" if known else None)
        assert len(store.wanted()) == int(known)
        assert downloads == ([str(requested)] if path == "upstream" else [])

    async def test_quota_search_metadata_is_passed_through_without_lookup(self, model_client, monkeypatch):
        client, now, answers, downloads = model_client
        client._refused_since = now[0]
        client._quota_until = now[0] + config.CSE_QUOTA_RETRY_SECONDS
        monkeypatch.setattr(client._store, "part_info", lambda *_: pytest.fail("repeated metadata lookup"))
        loop_thread = threading.get_ident()
        statements = []
        client._store._conn.set_trace_callback(lambda sql: statements.append((sql, threading.get_ident())))
        try:
            reply = await client.get_kicad(query="P1")
        finally:
            client._store._conn.set_trace_callback(None)
        assert reply["mfr_part_number"] == "P1" and "daily model download limit" in reply["error"]
        assert statements and all(thread != loop_thread for _, thread in statements)
        assert client._store.wanted()[0]["part_number"] == "P1"
        assert downloads == []

    async def test_health_reads_cse_counts_off_loop(self, model_client, monkeypatch):
        client, _, _, _ = model_client
        monkeypatch.setattr(server, "_cse_client", client)
        monkeypatch.setattr(server, "_cse_stored", (float("-inf"), None))
        loop_thread = threading.get_ident()
        threads = []
        client._store._conn.set_trace_callback(lambda _: threads.append(threading.get_ident()))
        try:
            reply = await server.health(None)
        finally:
            client._store._conn.set_trace_callback(None)
        assert json.loads(reply.body)["cse_stored"] == {"searches": 0, "kicad": 0, "wanted": 0}
        assert threads and all(thread != loop_thread for thread in threads)

    async def test_download_completed_during_metadata_lookup_is_not_wanted(self, model_client, monkeypatch):
        client, now, _, _ = model_client
        store = client._store
        store.put_search("P1", 0, {"results": [cse_module._normalize_part(part(1))]})
        client._refused_since = now[0]
        client._quota_until = now[0] + config.CSE_QUOTA_RETRY_SECONDS
        original = store.part_info

        def completed_download(part_id):
            info = original(part_id)
            store.put_kicad(part_id, {"kicad_symbol": "completed"})
            return info

        monkeypatch.setattr(store, "part_info", completed_download)
        await client.get_kicad(part_id=1)
        assert store.get_kicad(1) == {"kicad_symbol": "completed"}
        assert store.wanted() == []

    @pytest.mark.parametrize("body", [QUOTA_BODY, b"Error: denied", b"invalid archive"],
                             ids=["quota", "refused", "invalid"])
    async def test_wanted_only_grows_for_search_known_parts(self, model_client, body):
        client, now, answers, downloads = model_client
        row = cse_module._normalize_part(part(1))
        client._store.put_search("P1", 0, {"results": [row]})
        answers.extend([body] * 132)  # an invalid archive is downloaded twice (until the retry guard is on)
        for requested in (-1, 1, *range(-32, -1), *range(2, 34), 1):
            assert "error" in await client.get_kicad(part_id=requested)
        wanted = client._store.wanted()
        assert [(r["part_id"], r["part_number"], r["times_asked"]) for r in wanted] == [("1", "P1", 2)]
        assert client.store_counts()["wanted"] == 1
        client._store.put_kicad(1, {"kicad_symbol": "seeded"})
        assert client._store.wanted() == []

    async def test_reported_quota_pause_renewal_and_recovery(self, model_client, caplog):
        client, now, answers, downloads = model_client
        caplog.set_level(logging.INFO, logger="pcbparts_mcp")
        answers.extend([QUOTA_BODY, QUOTA_BODY, kicad_zip()])
        client._store.put_kicad(90, {"kicad_symbol": "stored"}, fetched_at=now[0] - 100)
        client._store.put_kicad(91, {"kicad_symbol": "old"}, fetched_at=now[0] - DAY - 1)
        expected = QUOTA.format("2026-11-01T15:47:00Z")
        assert (await client.get_kicad(query="P1"))["error"] == expected
        first_refused = now[0]
        assert downloads == ["1"]
        row = client._store.wanted()[0]
        assert row["part_number"] == "P1" and row["manufacturer"] == "TI" and row["reason"] == "quota"
        assert row["times_asked"] == 1
        assert "HTTP 200; content type text/plain;charset=UTF-8; 41 bytes; 0.500 seconds" in caplog.text
        assert "CSE daily download quota refused at 2026-11-01T15:17:00Z: 1 downloads stored in the last 24 h; next try at 2026-11-01T15:47:00Z" in caplog.text
        assert "CSE model wanted: part 1 (P1): quota" in caplog.text
        assert (await client.get_kicad(part_id=90))["kicad_symbol"] == "stored"
        assert (await client.get_kicad(query="P-1"))["error"] == expected  # searches still run
        assert (await client.get_kicad(part_id=1))["error"] == expected
        assert downloads == ["1"]
        assert client._store.wanted()[0]["times_asked"] == 3
        now[0] = first_refused + config.CSE_QUOTA_RETRY_SECONDS
        assert (await client.get_kicad(part_id=1))["error"] == QUOTA.format("2026-11-01T16:17:01Z")
        assert client._refused_since == first_refused
        now[0] += config.CSE_QUOTA_RETRY_SECONDS
        assert (await client.get_kicad(part_id=1))["kicad_symbol"] == "(kicad_symbol_lib)"
        assert client._refused_since is None and client._store.wanted() == []
        assert downloads == ["1", "1", "1"]
        assert sum("CSE downloads accepted again at" in record.message for record in caplog.records) == 1
        assert sum("CSE daily download quota refused at" in record.message for record in caplog.records) == 2
        assert sum("CSE model wanted:" in record.message for record in caplog.records) == 1
        upstream = stats.usage.summary()["totals"]["upstream"]["cse"]
        assert upstream["sent"] == 5 and upstream["rate_limited"] == 4 and upstream["cached"] >= 1

    async def test_only_one_probe_after_pause(self, model_client, monkeypatch):
        client, now, answers, downloads = model_client
        answers.extend([QUOTA_BODY, kicad_zip()])
        await client.get_kicad(part_id=1)
        now[0] += config.CSE_QUOTA_RETRY_SECONDS
        started, release = asyncio.Event(), asyncio.Event()
        original = client._http.get

        async def delayed(url, **kwargs):
            if "model.php" in url:
                started.set()
                await release.wait()
            return await original(url, **kwargs)

        monkeypatch.setattr(client._http, "get", delayed)
        probe = asyncio.create_task(client.get_kicad(part_id=2))
        await started.wait()
        assert "checking whether downloads are available again; try again shortly" in (
            await client.get_kicad(part_id=3))["error"]
        assert "checking whether downloads are available again; try again shortly" in (
            await client.get_kicad(query="P-1"))["error"]
        release.set()
        assert "error" not in await probe
        assert downloads == ["1", "2"]

    async def test_no_part_data_is_not_found_and_not_wanted(self, model_client, caplog):
        client, now, answers, downloads = model_client
        answers.append(b"Error: no part data available for partID 999999999")
        assert await client.get_kicad(part_id=999999999) == {"error": "No ECAD model available for part 999999999"}
        assert client._store.wanted() == [] and client._refused_since is None
        assert "HTTP 200" in caplog.text and "999999999" in caplog.text

    @pytest.mark.parametrize("body,reason,error", [
        (b"<html><b>Error:</b> denied test-login@example.com s3cr3t&lt;value&gt; other@example.org\n now</html>",
         "refused", "CSE refused the model download for part 1: Error: denied *** *** *** now"),
        (b"<html>Something   unexpected</html>", "invalid_zip", "CSE returned invalid zip file"),
    ], ids=["refused", "invalid"])
    async def test_cleaned_refusal_or_invalid_reply(self, model_client, caplog, body, reason, error):
        client, now, answers, downloads = model_client
        client._store.put_search("P1", 0, {"results": [cse_module._normalize_part(part(1))]})
        answers.extend([body, body])
        assert (await client.get_kicad(part_id=1))["error"] == error
        assert client._store.wanted()[0]["reason"] == reason
        # A refusal is final; an invalid reply is downloaded once more: each logged, the retry, and
        # retries off after those two failures in a row
        retried = reason == "invalid_zip"
        assert len(downloads) == 1 + retried
        assert len([r for r in caplog.records if r.levelno == logging.WARNING]) == (4 if retried else 1)
        assert "test-login" not in caplog.text and "s3cr3t" not in caplog.text and "other@example.org" not in caplog.text
        assert "<html>" not in caplog.text

    async def test_refusal_text_is_limited(self, model_client, caplog):
        client, now, answers, downloads = model_client
        answers.append(b"Error: " + b"x" * 400)
        reply = await client.get_kicad(part_id=1)
        assert len(reply["error"].split(": ", 1)[1]) == 150
        assert len(caplog.records[0].message.rsplit("; ", 1)[1]) == 200

    async def test_metadata_from_stored_search_for_part_id(self, model_client):
        client, now, answers, downloads = model_client
        client._store.put_search("stored", 0, {"results": [{"cse_part_id": "1", "mfr_part_number": "P1",
                                                          "manufacturer": "Maker", "has_model": True}]})
        answers.append(QUOTA_BODY)
        reply = await client.get_kicad(part_id=1)
        assert reply["part_id"] == 1 and reply["mfr_part_number"] == "P1" and reply["manufacturer"] == "Maker"
        assert client._store.wanted()[0]["part_number"] == "P1"
        assert client._store.wanted()[0]["manufacturer"] == "Maker"

    @pytest.mark.parametrize("source", ["memory", "store"])
    async def test_paused_live_search_returns_stored_files(self, model_client, monkeypatch, source):
        client, now, answers, downloads = model_client
        row = cse_module._normalize_part(part(1))
        client._store.put_search("P1", 0, {"results": [row], "total": 1})
        files = {"kicad_symbol": "stored symbol", "kicad_footprint": "stored footprint"}
        if source == "memory":
            client._kicad_cache.set("kicad:1", files)
        else:
            client._store.put_kicad(1, files)
        client._refused_since = now[0]
        client._quota_until = now[0] + config.CSE_QUOTA_RETRY_SECONDS
        get = AsyncMock(wraps=client._http.get)
        monkeypatch.setattr(client._http, "get", get)
        assert client._cache.get("cse:p-1:0") is None
        assert client._store.get_search("P-1", 0) is None
        started = now[0]

        reply = await client.get_kicad(query="P-1")

        assert reply == {"part_id": 1, **row, **files}
        get.assert_awaited_once_with(cse_module._CSE_API_URL, params={"searchString": "P-1", "country": "US"})
        assert downloads == [] and now[0] == started

    @pytest.mark.parametrize("parts,error", [
        ([], "No parts found for 'P-1'"),
        ([part(1, has_model=False)], "No ECAD model available for 'P-1'"),
    ], ids=["empty", "no_models"])
    async def test_paused_live_search_keeps_not_found_errors(self, model_client, monkeypatch, parts, error):
        client, now, answers, downloads = model_client
        client._refused_since = now[0]
        client._quota_until = now[0] + config.CSE_QUOTA_RETRY_SECONDS
        get = AsyncMock(return_value=httpx.Response(200, json={"status": "Success", "parts": parts}))
        monkeypatch.setattr(client._http, "get", get)
        started = now[0]

        assert await client.get_kicad(query="P-1") == {"error": error}

        get.assert_awaited_once_with(cse_module._CSE_API_URL, params={"searchString": "P-1", "country": "US"})
        assert downloads == [] and now[0] == started
        assert client._store.wanted() == []

    async def test_quota_envelope_and_paused_downloads_do_not_wait(self, model_client, monkeypatch):
        client, now, answers, downloads = model_client
        answers.append(QUOTA_BODY)

        @asynccontextmanager
        async def lifespan(app):
            yield {}

        monkeypatch.setattr(server.mcp, "_lifespan", lifespan)
        monkeypatch.setattr(server, "_cse_client", client)
        async with Client(server.mcp) as mcp:
            first = await mcp.call_tool("cse_get_kicad", {"query": "P1"})
            expected = {"part_id": 1, **cse_module._normalize_part(part(1)),
                        "error": QUOTA.format("2026-11-01T15:47:00Z")}
            assert first.is_error is False
            assert first.structured_content == json.loads(first.content[0].text) == expected

            def unexpected(*args, **kwargs):
                pytest.fail("paused download waited or contacted CSE")

            monkeypatch.setattr(client, "_get_semaphore", unexpected)
            monkeypatch.setattr(client, "_get_http", unexpected)
            monkeypatch.setattr(cse_module, "asyncio", SimpleNamespace(sleep=unexpected, to_thread=asyncio.to_thread))
            started = now[0]
            for args in ({"query": "P1"}, {"part_id": 1}):
                reply = await mcp.call_tool("cse_get_kicad", args)
                content = json.loads(reply.content[0].text)
                assert reply.is_error is False and reply.structured_content == content
                assert content == expected
            assert now[0] == started and downloads == ["1"]
            assert client._store.wanted()[0]["times_asked"] == 3

        day = stats.usage.summary()["days"][0]
        assert day["tools"]["cse_get_kicad"]["rate_limited"] == 3
        assert day["tools"]["cse_get_kicad"]["failed"] == 0
        assert day["reasons"] == {} and day["latency"] == {}

    @pytest.mark.parametrize("source", ["memory", "store"])
    @pytest.mark.parametrize("files", [False, True], ids=["missing", "stored"])
    async def test_paused_cache_hits_keep_details_and_files(self, model_client, monkeypatch, source, files):
        client, now, answers, downloads = model_client
        row = cse_module._normalize_part(part(1))
        result = {"results": [row], "total": 1}
        if source == "memory":
            client._cache.set("cse:p1:0", result)
            if files:
                client._kicad_cache.set("kicad:1", {"kicad_symbol": "stored"})
        else:
            client._store.put_search("P1", 0, result)
            if files:
                client._store.put_kicad(1, {"kicad_symbol": "stored"})
        client._refused_since = now[0]
        client._quota_until = now[0] + 1800
        monkeypatch.setattr(client, "_get_http", lambda: pytest.fail("paused download contacted CSE"))
        started = now[0]
        reply = await client.get_kicad(query=" p1 ", manufacturer="TI")
        assert reply == {"part_id": 1, **row, **(
            {"kicad_symbol": "stored", "kicad_footprint": None} if files else
            {"error": QUOTA.format("2026-11-01T15:47:00Z")})}
        assert now[0] == started and downloads == []
        upstream = stats.usage.summary()["totals"]["upstream"]["cse"]
        assert upstream["cached"] == (2 if files else 1)
        assert upstream["rate_limited"] == (0 if files else 1)

    async def test_nonzip_http_failure_is_logged_without_changing_its_error(self, model_client, monkeypatch, caplog):
        client, now, answers, downloads = model_client
        monkeypatch.setattr(client._http, "get", AsyncMock(return_value=httpx.Response(
            503, content=b"<p>Unavailable test-login@example.com</p>", headers={"content-type": "text/html"})))
        assert (await client.get_kicad(part_id=1))["error"] == "CSE model download failed (HTTP 503)"
        assert "HTTP 503; content type text/html" in caplog.text
        assert "Unavailable ***" in caplog.text and "test-login" not in caplog.text
        assert client._store.wanted() == []

    def test_email_masking_before_a_credential_can_break_up_the_address(self, monkeypatch):
        monkeypatch.setattr(cse_module, "CSE_USER", "fake-login")
        monkeypatch.setattr(cse_module, "CSE_PASS", "example")
        assert cse_module._clean_body(b"Error: ask support@example.com, fake-login example") == "Error: ask ***, *** ***"


class TestWantedStore:
    def test_upsert_count_order_and_removal(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        assert store.mark_wanted(1, "quota", {"mfr_part_number": "P1", "manufacturer": "TI"}, now=10)
        store.mark_wanted(2, "refused", {}, now=20)
        store.mark_wanted(1, "invalid_zip", {}, now=30)
        rows = store.wanted()
        assert [r["part_id"] for r in rows] == ["1", "2"]
        assert rows[0] == dict(part_id="1", part_number="P1", manufacturer="TI", reason="invalid_zip",
                               first_asked=10, last_asked=30, times_asked=2)
        assert store.counts()["wanted"] == 2
        store.put_kicad(1, {"kicad_symbol": "x"}, fetched_at=40)
        assert store.counts()["wanted"] == 1 and store.wanted()[0]["part_id"] == "2"

    def test_recent_count_boundaries(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        for part_id, at in enumerate([0, 86400, 86401, 172800, 172801]):
            store.put_kicad(part_id, {"kicad_symbol": "x"}, fetched_at=at)
        assert store.kicad_last_24h(now=172800) == 2

    def test_unavailable_and_broken_store_never_raise(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        store._conn.execute("DROP TABLE wanted")
        store._conn.execute("DROP TABLE kicad")
        store._conn.execute("DROP TABLE searches")
        assert store.wanted() == [] and store.kicad_last_24h(0) == 0
        assert store.part_info(1) == {} and not store.mark_wanted(1, "quota", {}, now=0)
        store.close()
        assert store.wanted() == [] and store.kicad_last_24h(0) == 0
        assert not store.mark_wanted(1, "quota", {}, now=0)


class TestStoreCLI:
    @pytest.fixture
    def store(self, tmp_path, monkeypatch):
        path = tmp_path / "cse.db"
        monkeypatch.setattr(config, "CSE_STORE_PATH", str(path))
        return CSEStore(path)

    def test_wanted_tsv(self, store, capsys):
        store.mark_wanted(1, "quota", {"mfr_part_number": "P1"}, now=0)
        store.mark_wanted(2, "refused", {}, now=60)
        assert cse_store.main(["wanted"]) == 0
        lines = capsys.readouterr().out.splitlines()
        assert lines[0] == "part_id\tpart_number\tmanufacturer\treason\tfirst_asked\tlast_asked\ttimes_asked"
        assert lines[1].startswith("2\t\t\trefused\t1970-01-01T00:01:00Z")
        assert lines[2].endswith("1970-01-01T00:00:00Z\t1970-01-01T00:00:00Z\t1")

    @pytest.mark.parametrize("filename,number", [("arbitrary.zip", "p1"), ("LIB_p1.zip", "P1")], ids=["folder", "file"])
    async def test_import_matches_and_serves_without_network(self, store, tmp_path, monkeypatch, filename, number):
        store.mark_wanted(1, "quota", {"mfr_part_number": number}, now=0)
        incoming = tmp_path / filename
        incoming.write_bytes(kicad_zip())
        assert cse_store.main(["import", str(incoming)]) == 0
        assert store.wanted() == [] and store.get_kicad(1)["kicad_symbol"] == "(kicad_symbol_lib)"
        client = CSEClient(str(store.path))
        client._http = AsyncMock()
        monkeypatch.setattr(cse_module, "CSE_USER", "fake")
        monkeypatch.setattr(cse_module, "CSE_PASS", "fake")
        try:
            assert (await client.get_kicad(part_id=1))["kicad_footprint"] == "(module P1)"
            client._http.get.assert_not_called()
        finally:
            await client.close()

    @pytest.mark.parametrize("ambiguous", [False, True], ids=["missing", "ambiguous"])
    def test_import_needs_explicit_id_when_not_unique(self, store, tmp_path, capsys, ambiguous):
        if ambiguous:
            for part_id in (1, 2):
                store.mark_wanted(part_id, "quota", {"mfr_part_number": "P1"}, now=0)
        incoming = tmp_path / "LIB_P1.zip"
        incoming.write_bytes(kicad_zip())
        assert cse_store.main(["import", str(incoming)]) == 1
        assert "pass --part-id" in capsys.readouterr().err
        assert cse_store.main(["import", "--part-id", "17", str(incoming)]) == 0
        assert store.get_kicad(17)

    def test_stdin_and_mixed_file_failures(self, store, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(kicad_zip())))
        assert cse_store.main(["import", "--part-id", "1", "-"]) == 0
        assert store.get_kicad(1)
        incoming = tmp_path / "LIB_P1.zip"
        incoming.write_bytes(kicad_zip())
        store.mark_wanted(2, "quota", {"mfr_part_number": "P1"}, now=0)
        assert cse_store.main(["import", str(incoming), str(tmp_path / "missing.zip")]) == 1
        output = capsys.readouterr()
        assert "stored kicad_footprint, kicad_symbol" in output.out and "missing.zip" in output.err
        assert store.get_kicad(2)

    @pytest.mark.parametrize("args", [["import", "-"], ["import", "--part-id", "1", "a.zip", "b.zip"]], ids=["stdin", "multi"])
    def test_invalid_arguments(self, store, args):
        with pytest.raises(SystemExit) as error:
            cse_store.main(args)
        assert error.value.code == 2

    def test_import_uses_shared_extraction_rules(self, store, tmp_path, monkeypatch):
        monkeypatch.setattr(cse_archive, "MAX_KICAD_FILE_SIZE", 5)
        incoming = tmp_path / "LIB_P1.zip"
        with zipfile.ZipFile(incoming, "w") as archive:
            archive.writestr("P1/KiCad/good.kicad_mod", "abc")
            archive.writestr("P1/KiCad/huge.kicad_sym", "too long")
            archive.writestr("P1/Altium/wrong.kicad_sym", "abc")
            archive.writestr("P1/KiCad/other.step", "abc")
        assert cse_store.main(["import", "--part-id", "1", str(incoming)]) == 0
        assert store.get_kicad(1) == {"kicad_footprint": "abc"}
        monkeypatch.setattr(cse_archive, "MAX_ZIP_SIZE", 10)
        assert cse_store.main(["import", "--part-id", "2", str(incoming)]) == 1
        assert store.get_kicad(2) is None
