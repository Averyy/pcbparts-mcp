"""CSE answers kept across restarts (cse_store.py): a year for a search where every part has a
model and for KiCad files, a week for a search with a part that has no model yet or no parts."""

import io
import time
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pcbparts_mcp.config import CSE_FOUND_TTL, CSE_NOT_FOUND_TTL
from pcbparts_mcp.cse import CSEClient
from pcbparts_mcp.cse_store import CSEStore, query_key

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

    def test_kicad_files_kept_a_year(self, tmp_path):
        store = CSEStore(tmp_path / "cse.db")
        files = {"kicad_symbol": "(sym)", "kicad_footprint": "(mod)"}
        store.put_kicad(12345, files, fetched_at=0)
        assert store.get_kicad("12345", now=CSE_FOUND_TTL - DAY) == files
        assert store.get_kicad(12345, now=CSE_FOUND_TTL + DAY) is None

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
        assert store.counts() == {"searches": 1, "kicad": 1}

    def test_unusable_path_never_raises(self, tmp_path):
        blocker = tmp_path / "file"
        blocker.write_text("not a directory")
        store = CSEStore(blocker / "cse.db")
        assert not store.enabled
        assert store.get_search("LM358P", 0) is None
        assert store.put_search("LM358P", 0, {"results": []}) is False
        assert store.counts() == {"searches": 0, "kicad": 0}

    def test_query_key(self):
        assert query_key("  LM358P ") == query_key("lm358p") == "lm358p"
        assert query_key("LM358 P") == "lm358 p"


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

    async def test_failed_search_not_stored(self, tmp_path):
        client = client_with(tmp_path / "cse.db", lambda url: response({"status": "Error"}))
        await client.search("LM358P")
        assert CSEStore(tmp_path / "cse.db").counts()["searches"] == 0

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
        assert client.store_counts() == {"searches": 1, "kicad": 0}
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
