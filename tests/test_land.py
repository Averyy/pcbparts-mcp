"""find_alternatives(land_compatible=true): footprint pad comparison (land.py), the pad store, the
budgeted footprint fetch, and ranking. Pads are real EasyEDA footprints for C295747 (JST
S2B-PH-SM4-TB) and alternatives a design session checked by hand (todo-idea, 2026-11-17).
Fake clocks and sessions only; no network.
"""

import types

import pytest

from pcbparts_mcp import client as client_module
from pcbparts_mcp.cache import Cooldown, SlidingWindowBudget
from pcbparts_mcp.client import JLCPCBClient
from pcbparts_mcp.config import (
    EASYEDA_COOLDOWN_BASE,
    EASYEDA_COOLDOWN_MAX,
    EASYEDA_LAND_BUDGET,
    EASYEDA_LAND_MAX_CHECKS,
    EASYEDA_LAND_WINDOW,
)
from pcbparts_mcp.easyeda_store import EasyEDAStore, pack_pads, unpack_pads
from pcbparts_mcp.land import CONNECTOR_LAND_HINT, LAND_NOTE, compare_land, first_pad, land_rank

# EasyEDA footprints as parse_easyeda_footprint() gives them (mm, y down)
FOOTPRINTS = {
    "C295747": [("1", -1.0, -2.925), ("2", 1.0, -2.925), ("3", 3.35, 2.925), ("4", -3.35, 2.925)],
    "C2905019": [("1", -1.0, -2.85), ("2", 1.0, -2.85), ("3", 3.3, 2.85), ("4", -3.3, 2.85)],
    "C3029440": [("1", -1.0, -2.85), ("2", 1.0, -2.85), ("3", -3.35, 2.85), ("4", 3.35, 2.85)],
    "C668620": [("1", 1.0, 2.85), ("2", -1.0, 2.85), ("3", 3.35, -2.85), ("4", -3.35, -2.85)],
    "C23397052": [("1", 1.0, -2.875), ("2", -1.0, -2.875), ("3", -3.3, 2.875), ("4", 3.3, 2.875)],
    "C2764211": [("1", -1.002, 2.943), ("2", 0.998, 2.943), ("3", 3.409, -2.943), ("4", -3.409, -2.943)],
    "C7433648": [("1", -1.0, -2.85), ("2", 1.0, -2.85), ("3", 3.75, 2.85), ("4", -3.75, 2.85)],
    "C225233": [("1", -1.0, -2.914), ("2", 1.0, -2.914), ("3", 3.35, 2.914), ("4", -3.35, 2.914)],
}
UUIDS = {code: f"{n:032x}" for n, code in enumerate(FOOTPRINTS, 1)}


def pads(code: str, offset: tuple[float, float] = (0.0, 0.0)) -> list[dict]:
    return [{"number": n, "x": x + offset[0], "y": y + offset[1]} for n, x, y in FOOTPRINTS[code]]


def land(code: str) -> dict:
    return compare_land(pads("C295747"), pads(code))


class TestCompareLand:
    def test_same_land(self):
        assert land("C225233") == {"fits": True, "turn": 0, "max_offset_mm": 0.011}
        assert land("C2905019") == {"fits": True, "turn": 0, "max_offset_mm": 0.09}

    def test_tabs_renumbered(self):
        assert land("C3029440") == {"fits": True, "turn": 0, "max_offset_mm": 0.075,
                                    "renumbered": {"3": "4", "4": "3"}}

    def test_drawn_turned(self):
        result = land("C668620")
        assert result["fits"] and result["turn"] == 180
        assert result["renumbered"] == {"3": "4", "4": "3"}  # pads 1 and 2 keep their places

    def test_pin1_moved(self):
        # The top-ranked alternative before land checks: fits the copper, pad 1 where the original has 2
        result = land("C23397052")
        assert result["fits"] and result["turn"] == 0
        assert result["renumbered"] == {"1": "2", "2": "1", "3": "4", "4": "3"}

    def test_turned_and_pin1_moved(self):
        result = land("C2764211")
        assert result["fits"] and result["turn"] == 180 and result["renumbered"]["1"] == "2"

    def test_tabs_too_far(self):
        assert land("C7433648") == {"fits": False, "turn": 0, "max_offset_mm": 0.407}

    def test_origin_doesnt_matter(self):
        moved = compare_land(pads("C295747"), pads("C225233", offset=(12.5, -40.0)))
        assert moved == land("C225233")

    def test_pad_count(self):
        result = compare_land(pads("C295747"), pads("C225233")[:3])
        assert result == {"fits": False, "pads": "3 pads, original has 4"}

    def test_hole_vs_surface(self):
        tht = [dict(p, hole=True) for p in pads("C225233")]
        result = compare_land(pads("C295747"), tht)
        assert result["fits"] is False and "through-hole" in result["pads"]

    def test_symmetric_keeps_numbers(self):
        # A two-pad passive lines up at 0 and 180 degrees; the turn that keeps the numbers wins
        r0805 = [{"number": "1", "x": -0.95, "y": 0.0}, {"number": "2", "x": 0.95, "y": 0.0}]
        assert compare_land(r0805, list(reversed(r0805))) == {"fits": True, "turn": 0, "max_offset_mm": 0.0}

    def test_quarter_turn(self):
        turned = [{"number": n, "x": y, "y": -x} for n, x, y in FOOTPRINTS["C225233"]]
        result = compare_land(pads("C295747"), turned)
        assert result["fits"] and result["turn"] in (90, 270) and "renumbered" not in result

    def test_unnumbered_pads_not_renumbered(self):
        orig = pads("C295747")
        for pad in orig[2:]:
            pad["number"] = ""
        result = compare_land(orig, pads("C3029440"))
        assert result["fits"] and "renumbered" not in result

    def test_shared_number_mismatch(self):
        # Two pads numbered 1: the one landing on the candidate's pad 2 must still show
        orig = [{"number": "1", "x": 0.0, "y": 0.0}, {"number": "1", "x": 2.0, "y": 0.0},
                {"number": "3", "x": 0.0, "y": 3.0}]
        cand = [{"number": "2", "x": 0.0, "y": 0.0}, {"number": "1", "x": 2.0, "y": 0.0},
                {"number": "3", "x": 0.0, "y": 3.0}]
        result = compare_land(orig, cand)
        assert result["renumbered"] == {"1": "1/2"}
        assert land_rank(result, "1") == 2

    def test_shared_number_same(self):
        tabs = [{"number": "1", "x": 0.0, "y": 0.0}, {"number": "5", "x": -3.0, "y": 2.0},
                {"number": "5", "x": 3.0, "y": 2.0}]
        assert "renumbered" not in compare_land(tabs, list(reversed(tabs)))

    def test_stacked_pads_any_order(self):
        # A surface pad and a through-hole pad at the same spot, listed in either order
        stacked = [{"number": "1", "x": 0.0, "y": 0.0}, {"number": "1", "x": 0.0, "y": 0.0, "hole": True},
                   {"number": "2", "x": 2.0, "y": 3.0}]
        result = compare_land(stacked, [stacked[1], stacked[0], stacked[2]])
        assert result == {"fits": True, "turn": 0, "max_offset_mm": 0.0}

    def test_nothing_to_compare(self):
        assert compare_land([], pads("C225233")) is None
        assert compare_land(pads("C295747"), []) is None
        many = [{"number": str(i), "x": float(i), "y": 0.0} for i in range(301)]
        assert compare_land(many, many) is None


class TestRank:
    def test_order(self):
        pin1 = first_pad(pads("C295747"))
        ranks = {code: land_rank(land(code), pin1) for code in FOOTPRINTS if code != "C295747"}
        assert ranks == {"C2905019": 5, "C225233": 5, "C3029440": 4, "C668620": 3,
                         "C23397052": 2, "C2764211": 2, "C7433648": 0}
        assert land_rank(None, pin1) == 1

    def test_first_pad(self):
        assert first_pad(pads("C295747")) == "1"
        assert first_pad([{"number": "A2"}, {"number": "A1"}, {"number": ""}]) == "A1"
        assert first_pad([{"number": ""}]) is None


class TestPadStore:
    def test_pack_round_trip(self):
        packed = pack_pads([{"number": "1", "x": -1.0, "y": 2.5, "size": [1, 2]},
                            {"number": "", "x": 0.0, "y": 0.0, "hole": 0.9}])
        assert unpack_pads(packed) == [{"number": "1", "x": -1.0, "y": 2.5},
                                       {"number": "", "x": 0.0, "y": 0.0, "hole": True}]
        assert unpack_pads("not json") is None

    def test_put_get(self, tmp_path):
        store = EasyEDAStore(tmp_path / "easyeda.db")
        try:
            assert store.get_pads(UUIDS["C225233"]) is None
            assert store.put_pads(UUIDS["C225233"], pads("C225233"), fetched_at=123.0)
            assert store.put_pads(UUIDS["C3029440"], [], fetched_at=124.0)
            assert not store.put_pads("not-a-uuid", pads("C225233"))
            assert store.get_pads(UUIDS["C225233"]) == (pads("C225233"), 123.0)
            assert store.get_pads(UUIDS["C3029440"]) == ([], 124.0)
        finally:
            store.close()


# --- footprint fetches -------------------------------------------------------------


class FakeClock:
    def __init__(self, start: float = 1_000_000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict | None:
        return self._payload


def footprint_reply(code: str) -> dict:
    """An /api/components reply for a footprint: PAD shapes in 10-mil units around the origin."""
    shapes = [f"PAD~RECT~{x / 0.254:.4f}~{y / 0.254:.4f}~3.937~13.78~1~~{n}~0~~0~id{n}~0~~Y~0~0~0.4~"
              for n, x, y in FOOTPRINTS[code]]
    return {"success": True, "result": {"title": code, "dataStr": {"head": {"x": 0, "y": 0}, "shape": shapes}}}


class FakeSession:
    def __init__(self, respond):
        self.respond = respond
        self.urls: list[str] = []

    async def get(self, url: str):
        self.urls.append(url)
        return self.respond(url)


def code_of(url: str) -> str:
    uuid = url.rsplit("/", 1)[1]
    return next(code for code, u in UUIDS.items() if u == uuid)


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(client_module, "time", types.SimpleNamespace(time=fake))
    return fake


def make_client(clock, respond, store=None) -> tuple[JLCPCBClient, FakeSession]:
    client = JLCPCBClient()
    client._easyeda_store = store
    client._easyeda_land_budget = SlidingWindowBudget(EASYEDA_LAND_BUDGET, EASYEDA_LAND_WINDOW, clock)
    client._easyeda_land_cooldown = Cooldown(EASYEDA_COOLDOWN_BASE, EASYEDA_COOLDOWN_MAX, clock)
    session = FakeSession(respond)
    client._easyeda_land_session = session
    return client, session


class TestFootprintPads:
    async def test_fetch_then_memory(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, footprint_reply(code_of(url))))
        got, status = await client.footprint_pads(UUIDS["C225233"])
        assert status == "fetched" and compare_land(pads("C295747"), got)["max_offset_mm"] == 0.011
        assert (await client.footprint_pads(UUIDS["C225233"]))[1] == "cached"
        assert len(session.urls) == 1

    async def test_store_survives_restart(self, clock, tmp_path):
        store = EasyEDAStore(tmp_path / "easyeda.db")
        try:
            client, _ = make_client(clock, lambda url: FakeResponse(200, footprint_reply(code_of(url))), store)
            await client.footprint_pads(UUIDS["C225233"])
            fresh, session = make_client(clock, lambda url: FakeResponse(500), store)
            clock.now += 400 * 86400  # kept whatever their age: refreshing is the seed script's job
            assert (await fresh.footprint_pads(UUIDS["C225233"]))[1] == "stored"
            assert session.urls == []
        finally:
            store.close()

    async def test_seed(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(500))
        client.set_easyeda_pads_seed(lambda uuid: (pads("C225233"), 5.0) if uuid == UUIDS["C225233"] else None)
        assert await client.footprint_pads(UUIDS["C225233"]) == (pads("C225233"), "seeded")
        assert (await client.footprint_pads(UUIDS["C225233"]))[1] == "cached"
        assert session.urls == []

    async def test_newer_of_store_and_seed(self, clock, tmp_path):
        store = EasyEDAStore(tmp_path / "easyeda.db")
        try:
            store.put_pads(UUIDS["C225233"], pads("C2905019"), fetched_at=10.0)  # a later fetch on prod
            client, _ = make_client(clock, lambda url: FakeResponse(500), store)
            client.set_easyeda_pads_seed(lambda uuid: (pads("C225233"), 5.0))
            assert await client.footprint_pads(UUIDS["C225233"]) == (pads("C2905019"), "stored")
            client2, _ = make_client(clock, lambda url: FakeResponse(500), store)
            client2.set_easyeda_pads_seed(lambda uuid: (pads("C225233"), 20.0))
            assert await client2.footprint_pads(UUIDS["C225233"]) == (pads("C225233"), "seeded")
        finally:
            store.close()

    async def test_broken_seed_falls_through(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, footprint_reply(code_of(url))))

        def broken(uuid):
            raise RuntimeError("db gone")
        client.set_easyeda_pads_seed(broken)
        assert (await client.footprint_pads(UUIDS["C225233"]))[1] == "fetched"
        assert len(session.urls) == 1

    @pytest.mark.parametrize("reply", [FakeResponse(404), FakeResponse(200, {"success": False, "code": 404})])
    async def test_missing_footprint(self, clock, reply):
        client, session = make_client(clock, lambda url: reply)
        assert await client.footprint_pads(UUIDS["C225233"]) == ([], "fetched")
        assert await client.footprint_pads(UUIDS["C225233"]) == ([], "cached")
        assert len(session.urls) == 1

    @pytest.mark.parametrize("status_code", [403, 429])
    async def test_block_pauses(self, clock, status_code):
        client, session = make_client(clock, lambda url: FakeResponse(status_code))
        assert await client.footprint_pads(UUIDS["C225233"]) == (None, "blocked")
        assert await client.footprint_pads(UUIDS["C2905019"]) == (None, "cooldown")
        assert len(session.urls) == 1

    async def test_budget(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, footprint_reply("C225233")))
        for n in range(EASYEDA_LAND_BUDGET):
            await client.footprint_pads(f"{n + 100:032x}")
        assert await client.footprint_pads(f"{999:032x}") == (None, "budget")
        assert len(session.urls) == EASYEDA_LAND_BUDGET

    async def test_invalid_uuid(self, clock):
        client, session = make_client(clock, lambda url: FakeResponse(200, {}))
        assert await client.footprint_pads("../etc") == (None, "invalid")
        assert session.urls == []


# --- find_alternatives -------------------------------------------------------------

ORIGINAL = {"lcsc": "C295747", "subcategory": "Test Connectors", "category": "Connectors",
            "package": "SMD,P=2mm", "library_type": "extended", "price": 0.2, "stock": 0, "specs": {},
            "easyeda_footprint_uuid": UUIDS["C295747"]}
# Ranked by stock without land checks: the pin-1 swap first, the exact fit last
CANDIDATES = ["C23397052", "C7433648", "C668620", "C3029440", "C2764211", "C2905019", "C225233"]


def stub(client, monkeypatch, original=ORIGINAL, unknown=()):
    candidates = [{"lcsc": code, "package": "SMD,P=2mm", "library_type": "extended", "price": 0.1,
                   "stock": 100_000 - 1000 * i, "specs": {},
                   **({} if code in unknown else {"easyeda_footprint_uuid": UUIDS[code]})}
                  for i, code in enumerate(CANDIDATES)]

    async def get_part(lcsc):
        return dict(original)

    async def search(**kwargs):
        return {"results": [dict(c) for c in candidates]}

    async def ensure_categories():
        return None

    async def stored_footprint(lcsc, now):
        return None

    monkeypatch.setattr(client, "get_part", get_part)
    monkeypatch.setattr(client, "search", search)
    monkeypatch.setattr(client, "_ensure_categories", ensure_categories)
    monkeypatch.setattr(client, "_stored_footprint", stored_footprint)


class TestFindAlternativesLand:
    async def test_fits_first(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, footprint_reply(code_of(url))))
        stub(client, monkeypatch)
        result = await client.find_alternatives("C295747", limit=10, land_compatible=True)
        listed = [p["lcsc"] for p in result["similar_parts"]]
        assert listed == ["C2905019", "C225233", "C3029440", "C668620", "C23397052", "C2764211", "C7433648"]
        stage = result["summary"]["stages"]["land"]
        assert stage == {"requested": True, "checked": 7, "fits": 3, "fits_turned": 1, "pin1_moved": 2,
                         "no_fit": 1, "unknown": 0, "limit": EASYEDA_LAND_MAX_CHECKS, "fetched": 8,
                         "not_checked_cap": 0}
        assert result["summary"]["land_note"] == LAND_NOTE
        assert len(session.urls) == 8  # the original plus 7 candidates, one request each

    async def test_off_by_default(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, footprint_reply(code_of(url))))
        stub(client, monkeypatch)
        result = await client.find_alternatives("C295747", limit=10)
        assert [p["lcsc"] for p in result["similar_parts"]] == CANDIDATES
        assert "land" not in result["summary"]["stages"]
        assert all("land" not in p for p in result["similar_parts"])
        assert result["summary"]["land_note"] == CONNECTOR_LAND_HINT
        assert session.urls == []

    async def test_no_hint_off_connectors(self, clock, monkeypatch):
        client, _ = make_client(clock, lambda url: FakeResponse(500))
        stub(client, monkeypatch, original={**ORIGINAL, "category": "Resistors"})
        result = await client.find_alternatives("C295747", limit=10)
        assert "land_note" not in result["summary"]

    async def test_unknown_footprint_id(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, footprint_reply(code_of(url))))
        stub(client, monkeypatch, unknown={"C225233"})
        result = await client.find_alternatives("C295747", limit=10, land_compatible=True)
        part = next(p for p in result["similar_parts"] if p["lcsc"] == "C225233")
        assert part["land"] is None
        stage = result["summary"]["stages"]["land"]
        assert stage["unknown"] == 1 and stage["unknown_reasons"] == {"no_footprint_id": 1}
        assert len(session.urls) == 7  # no /api/products lookup for the unknown one

    async def test_original_unknown(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(200, footprint_reply(code_of(url))))
        original = {k: v for k, v in ORIGINAL.items() if k != "easyeda_footprint_uuid"}
        stub(client, monkeypatch, original=original)
        result = await client.find_alternatives("C295747", limit=10, land_compatible=True)
        stage = result["summary"]["stages"]["land"]
        assert stage["original"] == "no known EasyEDA footprint" and stage["unknown"] == 7
        assert [p["lcsc"] for p in result["similar_parts"]] == CANDIDATES  # order unchanged

    async def test_block_leaves_rest_unknown(self, clock, monkeypatch):
        client, session = make_client(clock, lambda url: FakeResponse(403))
        stub(client, monkeypatch)
        result = await client.find_alternatives("C295747", limit=10, land_compatible=True)
        assert result["summary"]["stages"]["land"]["original"] == "footprint couldn't be fetched"
        # The first wave went out together; nothing after the block
        assert len(session.urls) <= 5

    async def test_connector_unchecked(self):
        from pcbparts_mcp.alternatives import is_compatible_alternative
        _, info = is_compatible_alternative(
            {"category": "Connectors", "specs": {"Pitch": "2mm"}}, {"specs": {"Pitch": "2mm"}},
            "Wire To Board Connector")
        assert "land pattern and pin 1 position" in info["unchecked_requirements"]
        _, info = is_compatible_alternative(
            {"category": "Resistors", "specs": {}}, {"specs": {}}, "Chip Resistor - Surface Mount")
        assert "land pattern and pin 1 position" not in info["unchecked_requirements"]
