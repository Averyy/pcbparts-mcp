"""Unit tests for boards_db — search, get_board, get_consensus, get_stats, build."""

import json
import sqlite3
import textwrap
from pathlib import Path

import pytest
import yaml

from pcbparts_mcp.boards_db import BoardsDatabase
from pcbparts_mcp.boards_db.search import _sanitize_fts_query, _escape_like


# ---------------------------------------------------------------------------
# Fixtures — in-memory boards database from synthetic YAML data
# ---------------------------------------------------------------------------

SAMPLE_BOARDS = [
    {
        "name": "Test ESP32 Board",
        "slug": "test-esp32-board",
        "source": "testorg/test-esp32",
        "format": "kicad7",
        "description": "An ESP32 devkit with WiFi and battery charging",
        "tags": ["sensors", "battery-charging"],
        "key_ics": ["ESP32-S3", "MCP73831"],
        "components": [
            {"ref": "U1", "value": "ESP32-S3", "footprint": "QFN-48"},
            {"ref": "U2", "value": "MCP73831", "footprint": "SOT-23-5"},
            {"ref": "R1", "value": "10kohm", "footprint": "0402"},
            {"ref": "R2", "value": "4.7kohm", "footprint": "0402"},
            {"ref": "C1", "value": "100nF", "footprint": "0402", "decouples": "U1"},
            {"ref": "C2", "value": "10uF", "footprint": "0805", "decouples": "U2"},
            {"ref": "C3", "value": "4.7uF", "footprint": "0402"},
            {"ref": "R3", "value": "100kohm", "footprint": "0402", "pullup": "SDA"},
        ],
        "nets": [
            {"name": "SDA", "pins": ["U1.SDA", "R3.1"]},
            {"name": "SCL", "pins": ["U1.SCL", "R1.1"]},
            {"name": "PROG", "pins": ["U2.PROG", "R2.1"]},
            {"name": "3V3", "pins": ["U1.VCC", "C1.1", "U2.VCC", "C2.1"]},
            {"name": "GND", "pins": ["U1.GND", "C1.2", "U2.GND", "C2.2"]},
        ],
        "positions": [
            {"ref": "U1", "x": 10.0, "y": 10.0},
            {"ref": "U2", "x": 20.0, "y": 10.0},
        ],
        "copper_pours": [{"layer": "B.Cu", "net": "GND"}],
        "outline": {"width_mm": 50.0, "height_mm": 25.0},
        "design_rules": {"layers": 4, "min_trace": "0.15mm", "min_clearance": "0.15mm"},
    },
    {
        "name": "Adafruit Motor Shield",
        "slug": "adafruit-motor-shield",
        "source": "adafruit/Motor-Shield",
        "format": "eagle",
        "description": "A motor driver shield for Arduino with DRV8825",
        "tags": ["motor-control"],
        "key_ics": ["DRV8825"],
        "components": [
            {"ref": "U1", "value": "DRV8825", "footprint": "HTSSOP-28"},
            {"ref": "C1", "value": "100nF", "footprint": "0402", "decouples": "U1"},
            {"ref": "C2", "value": "47uF", "footprint": "1206", "decouples": "U1"},
            {"ref": "R1", "value": "10kohm", "footprint": "0402", "pulldown": "STEP"},
        ],
        "nets": [
            {"name": "STEP", "pins": ["U1.STEP", "R1.1"]},
            {"name": "GND", "pins": ["U1.GND", "C1.2", "C2.2", "R1.2"]},
        ],
        "positions": [],
        "copper_pours": [],
        "outline": {"width_mm": 68.6, "height_mm": 53.3},
        "design_rules": {"layers": 2},
    },
    {
        "name": "SparkFun MCP73831 Charger",
        "slug": "sparkfun-mcp73831-charger",
        "source": "sparkfun/MCP73831-Charger",
        "format": "eagle",
        "description": "A simple LiPo charger breakout with MCP73831",
        "tags": ["battery-charging", "power-supply"],
        "key_ics": ["MCP73831"],
        "components": [
            {"ref": "U1", "value": "MCP73831", "footprint": "SOT-23-5"},
            {"ref": "C1", "value": "4.7uF", "footprint": "0402", "decouples": "U1"},
            {"ref": "R1", "value": "2kohm", "footprint": "0402"},
            {"ref": "D1", "value": "red LED", "footprint": "0603"},
        ],
        "nets": [
            {"name": "PROG", "pins": ["U1.PROG", "R1.1"]},
            {"name": "STAT", "pins": ["U1.STAT", "D1.1"]},
            {"name": "VCC", "pins": ["U1.VCC", "C1.1"]},
            {"name": "GND", "pins": ["U1.GND", "C1.2", "R1.2", "D1.2"]},
        ],
        "positions": [],
        "copper_pours": [],
        "outline": {},
        "design_rules": {"layers": 2},
    },
    {
        "name": "Minimal LED Driver",
        "slug": "minimal-led-driver",
        "source": "maker/led-driver",
        "format": "eagle",
        "description": "A simple constant-current LED driver with TPS61169",
        "tags": ["led-driver"],
        "key_ics": ["TPS61169"],
        "components": [
            {"ref": "U1", "value": "TPS61169", "footprint": "SOT-23-5"},
            {"ref": "L1", "value": "10uH", "footprint": "1210"},
            {"ref": "R1", "value": "1ohm", "footprint": "0402"},
        ],
        # No nets → no neighborhoods will be built
        "nets": [],
        "positions": [],
        "copper_pours": [],
        "outline": {},
        "design_rules": {"layers": 2},
    },
    {
        "name": "BLE Sensor Node",
        "slug": "ble-sensor-node",
        "source": "SolderedElectronics/BLE-Sensor",
        "format": "kicad7",
        "description": "A Bluetooth Low Energy sensor node with BME280",
        "tags": ["sensors", "bluetooth"],
        "key_ics": ["nRF52840", "BME280"],
        "components": [
            {"ref": "U1", "value": "nRF52840", "footprint": "QFN-48"},
            {"ref": "U2", "value": "BME280", "footprint": "LGA-8"},
            {"ref": "C1", "value": "100nF", "footprint": "0402", "decouples": "U1"},
            {"ref": "C2", "value": "100nF", "footprint": "0402", "decouples": "U2"},
        ],
        "nets": [
            {"name": "SDA", "pins": ["U1.SDA", "U2.SDA"]},
            {"name": "SCL", "pins": ["U1.SCL", "U2.SCL"]},
            {"name": "3V3", "pins": ["U1.VCC", "C1.1", "U2.VCC", "C2.1"]},
            {"name": "GND", "pins": ["U1.GND", "C1.2", "U2.GND", "C2.2"]},
        ],
        "positions": [],
        "copper_pours": [],
        "outline": {"width_mm": 30.0, "height_mm": 20.0},
        "design_rules": {"layers": 4},
    },
]

BOARDS_MD = textwrap.dedent("""\
    # Reference Boards

    | Board | Org | Repo | Format | Schematic Path | Key Coverage |
    |-------|-----|------|--------|---------------|-------------|
    | Test ESP32 Board | testorg | `testorg/test-esp32` | kicad7 | `test.kicad_sch` | ESP32-S3 WiFi devkit with MCP73831 battery charging |
    | Adafruit Motor Shield | Adafruit | `adafruit/Motor-Shield` | eagle | `motor.sch` | DRV8825 stepper motor driver |
    | SparkFun MCP73831 Charger | SparkFun | `sparkfun/MCP73831-Charger` | eagle | `charger.sch` | MCP73831 LiPo charging circuit |
    | Minimal LED Driver | maker | `maker/led-driver` | eagle | `led.sch` | TPS61169 constant-current LED driver |
    | BLE Sensor Node | SolderedElectronics | `SolderedElectronics/BLE-Sensor` | kicad7 | `ble.kicad_sch` | nRF52840 BLE with BME280 sensor |
""")


@pytest.fixture(scope="module")
def boards_db(tmp_path_factory) -> BoardsDatabase:
    """Build a test boards.db from synthetic data."""
    data_dir = tmp_path_factory.mktemp("data")
    boards_dir = data_dir / "boards"
    boards_dir.mkdir()

    for board in SAMPLE_BOARDS:
        yaml_file = boards_dir / f"{board['slug']}.yaml"
        yaml_file.write_text(yaml.dump(board, default_flow_style=False))

    boards_md = boards_dir / "BOARDS.md"
    boards_md.write_text(BOARDS_MD)

    db_path = data_dir / "boards.db"
    db = BoardsDatabase(db_path=db_path, data_dir=data_dir)
    db._ensure_db()
    yield db
    db.close()


# ---------------------------------------------------------------------------
# _sanitize_fts_query
# ---------------------------------------------------------------------------

class TestSanitizeFtsQuery:
    def test_simple_terms(self):
        assert _sanitize_fts_query("ESP32 WiFi") == '"ESP32"* AND "WiFi"*'

    def test_empty_string(self):
        assert _sanitize_fts_query("") == ""

    def test_only_stop_words(self):
        assert _sanitize_fts_query("the and for") == ""

    def test_domain_stop_words(self):
        assert _sanitize_fts_query("board design circuit") == ""

    def test_single_char_dropped(self):
        assert _sanitize_fts_query("a b c") == ""

    def test_quotes_stripped(self):
        assert _sanitize_fts_query('"hello"') == '"hello"*'

    def test_alias_expansion(self):
        result = _sanitize_fts_query("bluetooth")
        assert "BLE" in result

    def test_synonym_eink(self):
        result = _sanitize_fts_query("eink")
        # Should expand to OR group with ink, paper, EPD, eink
        assert "ink" in result
        assert "paper" in result
        assert "OR" in result

    def test_synonym_e_paper(self):
        result = _sanitize_fts_query("e-paper")
        assert "ink" in result and "paper" in result and "OR" in result

    def test_alias_amplifier(self):
        result = _sanitize_fts_query("amplifier")
        assert "amp" in result

    def test_power_not_stop_word(self):
        """'power' and 'driver' should NOT be stop words."""
        result = _sanitize_fts_query("USB power delivery")
        assert "power" in result
        assert "delivery" in result

    def test_driver_not_stop_word(self):
        result = _sanitize_fts_query("motor driver")
        assert "motor" in result
        assert "driver" in result

    def test_alias_esp32s3(self):
        result = _sanitize_fts_query("esp32s3")
        assert "ESP32" in result and "S3" in result

    def test_hyphenated_split(self):
        result = _sanitize_fts_query("ESP32-S3")
        assert "ESP32" in result and "S3" in result

    def test_mixed_terms_and_stop_words(self):
        result = _sanitize_fts_query("the ESP32 board for WiFi")
        assert "ESP32" in result
        assert "WiFi" in result
        assert "the" not in result
        assert "board" not in result


# ---------------------------------------------------------------------------
# _escape_like
# ---------------------------------------------------------------------------

class TestEscapeLike:
    def test_no_escaping(self):
        assert _escape_like("MCP73831") == "MCP73831"

    def test_percent(self):
        assert _escape_like("100%") == "100\\%"

    def test_underscore(self):
        assert _escape_like("STM32_F4") == "STM32\\_F4"

    def test_backslash(self):
        assert _escape_like("path\\to") == "path\\\\to"


# ---------------------------------------------------------------------------
# get_stats
# ---------------------------------------------------------------------------

class TestGetStats:
    def test_total_boards(self, boards_db):
        stats = boards_db.get_stats()
        assert stats["total_boards"] == 5

    def test_formats(self, boards_db):
        stats = boards_db.get_stats()
        assert "kicad7" in stats["formats"]
        assert "eagle" in stats["formats"]
        assert stats["formats"]["kicad7"] == 2
        assert stats["formats"]["eagle"] == 3  # motor-shield, sparkfun-mcp73831, minimal-led-driver

    def test_top_tags(self, boards_db):
        stats = boards_db.get_stats()
        assert "sensors" in stats["top_tags"]
        assert "battery-charging" in stats["top_tags"]


# ---------------------------------------------------------------------------
# search — free text
# ---------------------------------------------------------------------------

class TestSearchFreeText:
    def test_basic_fts(self, boards_db):
        r = boards_db.search(query="ESP32")
        assert r["total"] >= 1
        slugs = [b["slug"] for b in r["results"]]
        assert "test-esp32-board" in slugs

    def test_description_match(self, boards_db):
        r = boards_db.search(query="motor driver")
        assert r["total"] >= 1
        slugs = [b["slug"] for b in r["results"]]
        assert "adafruit-motor-shield" in slugs

    def test_key_coverage_match(self, boards_db):
        r = boards_db.search(query="stepper")
        assert r["total"] >= 1

    def test_no_results(self, boards_db):
        r = boards_db.search(query="zxynonexistent12345")
        assert r["total"] == 0
        assert r["results"] == []

    def test_empty_query_returns_all(self, boards_db):
        r = boards_db.search()
        assert r["total"] == 5

    def test_empty_string_query_returns_all(self, boards_db):
        r = boards_db.search(query="")
        assert r["total"] == 5

    def test_only_stop_words_returns_all(self, boards_db):
        r = boards_db.search(query="the board design")
        assert r["total"] == 5  # all stop words → no FTS filter


# ---------------------------------------------------------------------------
# search — component filter
# ---------------------------------------------------------------------------

class TestSearchComponent:
    def test_component_match(self, boards_db):
        r = boards_db.search(component="MCP73831")
        assert r["total"] >= 2
        slugs = [b["slug"] for b in r["results"]]
        assert "test-esp32-board" in slugs
        assert "sparkfun-mcp73831-charger" in slugs

    def test_partial_component_match(self, boards_db):
        r = boards_db.search(component="MCP73")
        assert r["total"] >= 2

    def test_empty_component_returns_all(self, boards_db):
        """Empty component string should be treated as no filter."""
        r = boards_db.search(component="")
        assert r["total"] == 5  # all boards, no filter

    def test_nonexistent_component(self, boards_db):
        r = boards_db.search(component="NONEXISTENT999")
        assert r["total"] == 0


# ---------------------------------------------------------------------------
# search — tag filter
# ---------------------------------------------------------------------------

class TestSearchTag:
    def test_single_tag(self, boards_db):
        r = boards_db.search(tag="sensors")
        assert r["total"] == 2
        slugs = {b["slug"] for b in r["results"]}
        assert "test-esp32-board" in slugs
        assert "ble-sensor-node" in slugs

    def test_multi_tag_and(self, boards_db):
        r = boards_db.search(tag=["battery-charging", "sensors"])
        assert r["total"] == 1
        assert r["results"][0]["slug"] == "test-esp32-board"

    def test_nonexistent_tag(self, boards_db):
        r = boards_db.search(tag="nonexistent-tag")
        assert r["total"] == 0

    def test_tag_list_limit(self, boards_db):
        """Tag list is capped at 10."""
        many_tags = [f"tag{i}" for i in range(15)]
        r = boards_db.search(tag=many_tags)
        assert r["total"] == 0  # None match


# ---------------------------------------------------------------------------
# search — org filter
# ---------------------------------------------------------------------------

class TestSearchOrg:
    def test_org_by_slug(self, boards_db):
        r = boards_db.search(org="adafruit")
        assert r["total"] == 1
        assert r["results"][0]["slug"] == "adafruit-motor-shield"

    def test_org_by_display_name(self, boards_db):
        r = boards_db.search(org="Adafruit")
        assert r["total"] == 1

    def test_org_case_insensitive(self, boards_db):
        r = boards_db.search(org="ADAFRUIT")
        assert r["total"] == 1

    def test_empty_org_returns_all(self, boards_db):
        r = boards_db.search(org="")
        assert r["total"] == 5

    def test_org_soldered(self, boards_db):
        r = boards_db.search(org="Soldered Electronics")
        assert r["total"] == 1


# ---------------------------------------------------------------------------
# search — layers filter
# ---------------------------------------------------------------------------

class TestSearchLayers:
    def test_4_layer(self, boards_db):
        r = boards_db.search(layers=4)
        assert r["total"] == 2

    def test_2_layer(self, boards_db):
        r = boards_db.search(layers=2)
        assert r["total"] == 3  # motor-shield, sparkfun-mcp73831, minimal-led-driver

    def test_nonexistent_layers(self, boards_db):
        r = boards_db.search(layers=8)
        assert r["total"] == 0


# ---------------------------------------------------------------------------
# search — combined filters
# ---------------------------------------------------------------------------

class TestSearchCombined:
    def test_tag_and_org(self, boards_db):
        r = boards_db.search(tag="sensors", org="Soldered Electronics")
        assert r["total"] == 1
        assert r["results"][0]["slug"] == "ble-sensor-node"

    def test_query_and_tag(self, boards_db):
        r = boards_db.search(query="ESP32", tag="battery-charging")
        assert r["total"] >= 1
        assert r["results"][0]["slug"] == "test-esp32-board"

    def test_all_filters_no_match(self, boards_db):
        r = boards_db.search(query="ESP32", tag="motor-control")
        assert r["total"] == 0


# ---------------------------------------------------------------------------
# search — limit
# ---------------------------------------------------------------------------

class TestSearchLimit:
    def test_limit_respected(self, boards_db):
        r = boards_db.search(limit=2)
        assert len(r["results"]) == 2
        assert r["total"] == 5  # total is unaffected

    def test_limit_1(self, boards_db):
        r = boards_db.search(limit=1)
        assert len(r["results"]) == 1


# ---------------------------------------------------------------------------
# search — result shape
# ---------------------------------------------------------------------------

class TestSearchResultShape:
    def test_result_fields(self, boards_db):
        r = boards_db.search(limit=1)
        b = r["results"][0]
        expected_fields = {
            "slug", "name", "org", "org_display", "source", "source_url",
            "format", "description", "key_coverage", "tags", "key_ics",
            "layers", "width_mm", "height_mm", "component_count", "ic_count",
        }
        assert expected_fields.issubset(set(b.keys()))

    def test_org_and_org_display_differ(self, boards_db):
        """org should be slug, org_display should be human-readable."""
        r = boards_db.search(org="Adafruit", limit=1)
        b = r["results"][0]
        assert b["org"] == "adafruit"
        assert b["org_display"] == "Adafruit"

    def test_source_url_format(self, boards_db):
        r = boards_db.search(limit=1)
        b = r["results"][0]
        if b["source"]:
            assert b["source_url"].startswith("https://github.com/")

    def test_matched_by_on_component_search(self, boards_db):
        """Component search results should include matched_by hints."""
        r = boards_db.search(component="MCP73831")
        for b in r["results"]:
            assert "matched_by" in b
            assert any("MCP73831" in h for h in b["matched_by"])

    def test_matched_by_on_fts_search(self, boards_db):
        """FTS search results should include 'text match' hint."""
        r = boards_db.search(query="ESP32")
        for b in r["results"]:
            assert "matched_by" in b
            assert "text match" in b["matched_by"]

    def test_matched_by_on_tag_search(self, boards_db):
        """Tag search results should include tag hint."""
        r = boards_db.search(tag="sensors")
        for b in r["results"]:
            assert "matched_by" in b
            assert any("sensors" in h for h in b["matched_by"])

    def test_no_matched_by_on_unfiltered(self, boards_db):
        """Unfiltered search should not include matched_by."""
        r = boards_db.search()
        for b in r["results"]:
            assert "matched_by" not in b

    def test_matched_by_key_ic_vs_component(self, boards_db):
        """Key IC matches should say 'key IC', not just 'component'."""
        r = boards_db.search(component="ESP32-S3")
        esp32_board = next(b for b in r["results"] if b["slug"] == "test-esp32-board")
        assert any("key IC" in h for h in esp32_board["matched_by"])


# ---------------------------------------------------------------------------
# get_board — default mode
# ---------------------------------------------------------------------------

class TestGetBoard:
    def test_basic(self, boards_db):
        b = boards_db.get_board("test-esp32-board")
        assert b is not None
        assert b["name"] == "Test ESP32 Board"
        assert b["slug"] == "test-esp32-board"

    def test_components_filtered_by_default(self, boards_db):
        """Default mode filters plain passives, keeps ICs + annotated passives."""
        b = boards_db.get_board("test-esp32-board")
        assert "components" in b
        refs = [c["ref"] for c in b["components"]]
        # ICs always included
        assert "U1" in refs
        assert "U2" in refs
        # Annotated passives included (decouples/pullup)
        assert "C1" in refs  # decouples U1
        assert "C2" in refs  # decouples U2
        assert "R3" in refs  # pullup SDA
        # Plain passives filtered out
        assert "R1" not in refs
        assert "R2" not in refs
        assert "C3" not in refs
        assert b["passives_omitted"] == 3

    def test_include_bom_returns_all(self, boards_db):
        """include_bom=True returns all components including plain passives."""
        b = boards_db.get_board("test-esp32-board", include_bom=True)
        assert "components" in b
        assert len(b["components"]) == 8
        assert "passives_omitted" not in b

    def test_neighborhoods_summary(self, boards_db):
        b = boards_db.get_board("test-esp32-board")
        assert "neighborhoods" in b
        for hood in b["neighborhoods"]:
            assert "ref" in hood
            assert "value" in hood
            assert "pin_count" in hood

    def test_no_nets_in_default(self, boards_db):
        b = boards_db.get_board("test-esp32-board")
        assert "nets" not in b
        assert "positions" not in b
        assert "copper_pours" not in b

    def test_tags_and_key_ics(self, boards_db):
        b = boards_db.get_board("test-esp32-board")
        assert "sensors" in b["tags"]
        assert "ESP32-S3" in b["key_ics"]

    def test_none_values_stripped(self, boards_db):
        """Component fields with None values should be excluded."""
        b = boards_db.get_board("test-esp32-board")
        for comp in b["components"]:
            for v in comp.values():
                assert v is not None

    def test_nonexistent_returns_none(self, boards_db):
        assert boards_db.get_board("nonexistent-slug-12345") is None

    def test_empty_slug_returns_none(self, boards_db):
        assert boards_db.get_board("") is None


# ---------------------------------------------------------------------------
# get_board — focus mode
# ---------------------------------------------------------------------------

class TestGetBoardFocus:
    def test_focus_by_ic_name(self, boards_db):
        b = boards_db.get_board("test-esp32-board", focus="ESP32-S3")
        assert b is not None
        assert "focus" in b
        assert b["focus"]["value"] == "ESP32-S3"
        assert "components" not in b  # No full BOM in focus mode

    def test_focus_by_ref(self, boards_db):
        b = boards_db.get_board("test-esp32-board", focus="U1")
        assert b is not None
        assert "focus" in b
        assert b["focus"]["ref"] == "U1"

    def test_focus_partial_match(self, boards_db):
        b = boards_db.get_board("test-esp32-board", focus="ESP32")
        assert b is not None
        assert "focus" in b  # Should match ESP32-S3

    def test_focus_nonexistent_ic(self, boards_db):
        b = boards_db.get_board("test-esp32-board", focus="NONEXISTENT_IC")
        assert b is not None
        assert "focus_error" in b
        assert "available_ics" in b

    def test_focus_pins_present(self, boards_db):
        b = boards_db.get_board("test-esp32-board", focus="MCP73831")
        assert b is not None
        if "focus" in b:
            assert "pins" in b["focus"]

    def test_focus_auto_consensus(self, boards_db):
        """Focus on MCP73831 should auto-include consensus (2+ boards use it)."""
        b = boards_db.get_board("test-esp32-board", focus="MCP73831")
        assert b is not None
        assert "focus" in b
        assert "consensus" in b
        assert b["consensus"]["ic"] == "MCP73831"
        assert b["consensus"]["board_count"] == 2

    def test_focus_no_consensus_for_single_board_ic(self, boards_db):
        """Focus on DRV8825 should NOT include consensus (only 1 board)."""
        b = boards_db.get_board("adafruit-motor-shield", focus="DRV8825")
        assert b is not None
        assert "focus" in b
        assert "consensus" not in b

    # --- focus_match_type tests (Priority 5) ---

    def test_match_type_ref(self, boards_db):
        """Matching by ref should return match_type='ref'."""
        b = boards_db.get_board("test-esp32-board", focus="U1")
        assert b is not None
        assert b.get("focus_match_type") == "ref"

    def test_match_type_exact(self, boards_db):
        """Matching by exact IC name should return match_type='exact'."""
        b = boards_db.get_board("test-esp32-board", focus="ESP32-S3")
        assert b is not None
        assert b.get("focus_match_type") == "exact"

    def test_match_type_partial(self, boards_db):
        """Matching by partial IC name should return match_type='partial'."""
        b = boards_db.get_board("test-esp32-board", focus="ESP32")
        assert b is not None
        assert b.get("focus_match_type") == "partial"

    def test_match_type_not_present_on_miss(self, boards_db):
        """No match_type when focus fails."""
        b = boards_db.get_board("test-esp32-board", focus="NONEXISTENT_IC")
        assert b is not None
        assert "focus_match_type" not in b

    def test_partial_match_consensus_fallback(self, boards_db):
        """Partial match 'MCP73' → 'MCP73831': exact variant has consensus,
        so fallback shouldn't fire. But verify consensus is still present."""
        b = boards_db.get_board("test-esp32-board", focus="MCP73")
        assert b is not None
        assert b.get("focus_match_type") == "partial"
        # MCP73831 has consensus in test data (2 boards), so it should be found
        # either via exact variant or fallback
        assert "consensus" in b

    def test_no_alternatives_for_unique_partial(self, boards_db):
        """Partial match with only one hit should not include focus_alternatives."""
        b = boards_db.get_board("test-esp32-board", focus="ESP32")
        assert b is not None
        assert "focus" in b
        assert "focus_alternatives" not in b

    def test_no_alternatives_for_exact_match(self, boards_db):
        """Exact match never shows alternatives."""
        b = boards_db.get_board("test-esp32-board", focus="MCP73831")
        assert b is not None
        assert b.get("focus_match_type") == "exact"
        assert "focus_alternatives" not in b

    def test_focus_on_no_neighborhood_board(self, boards_db):
        """Board with no neighborhoods should fail gracefully with key_ics fallback."""
        b = boards_db.get_board("minimal-led-driver", focus="TPS61169")
        assert b is not None
        assert "focus_error" in b
        assert "no parsed IC neighborhoods" in b["focus_error"]
        # Should fall back to key_ics
        assert len(b["available_ics"]) >= 1
        avail_values = [a["value"] for a in b["available_ics"]]
        assert "TPS61169" in avail_values


# ---------------------------------------------------------------------------
# get_board — raw mode (include_nets)
# ---------------------------------------------------------------------------

class TestGetBoardRaw:
    def test_raw_mode(self, boards_db):
        b = boards_db.get_board("test-esp32-board", include_raw=True)
        assert b is not None
        assert "nets" in b
        assert "positions" in b
        assert "copper_pours" in b
        assert len(b["nets"]) == 5
        assert len(b["positions"]) == 2
        assert len(b["copper_pours"]) == 1

    def test_raw_plus_focus(self, boards_db):
        b = boards_db.get_board("test-esp32-board", include_raw=True, focus="ESP32-S3")
        assert b is not None
        assert "focus" in b
        assert "nets" in b  # raw data present even with focus


# ---------------------------------------------------------------------------
# get_consensus
# ---------------------------------------------------------------------------

class TestGetConsensus:
    def test_consensus_found(self, boards_db):
        c = boards_db.get_consensus("MCP73831")
        assert c is not None
        assert c["ic"] == "MCP73831"
        assert c["board_count"] == 2

    def test_consensus_boards(self, boards_db):
        c = boards_db.get_consensus("MCP73831")
        assert c is not None
        assert set(c["boards"]) == {"test-esp32-board", "sparkfun-mcp73831-charger"}

    def test_consensus_decoupling(self, boards_db):
        c = boards_db.get_consensus("MCP73831")
        assert c is not None
        if c["decoupling"]:
            for entry in c["decoupling"]:
                assert "value" in entry
                assert "boards" in entry
                assert "pct" in entry
                assert entry["pct"] <= 100

    def test_consensus_pins(self, boards_db):
        c = boards_db.get_consensus("MCP73831")
        assert c is not None
        if c["pins"]:
            for pin_name, pin_data in c["pins"].items():
                assert "boards_with_pin" in pin_data
                assert "top_choices" in pin_data

    def test_consensus_nonexistent(self, boards_db):
        assert boards_db.get_consensus("NONEXISTENT_IC_99999") is None

    def test_consensus_single_board_returns_none(self, boards_db):
        """Consensus requires 2+ boards, DRV8825 is only on 1 board."""
        assert boards_db.get_consensus("DRV8825") is None


# ---------------------------------------------------------------------------
# get_tag_consensus
# ---------------------------------------------------------------------------

class TestGetTagConsensus:
    def test_battery_charging_consensus(self, boards_db):
        """battery-charging tag has 2 boards → should return consensus."""
        c = boards_db.get_tag_consensus("battery-charging")
        assert c is not None
        assert c["tag"] == "battery-charging"
        assert c["board_count"] == 2
        # MCP73831 is on both battery-charging boards
        ics = [entry["ic"] for entry in c["top_ics"]]
        assert "MCP73831" in ics

    def test_top_ics_shape(self, boards_db):
        c = boards_db.get_tag_consensus("battery-charging")
        assert c is not None
        for entry in c["top_ics"]:
            assert "ic" in entry
            assert "boards" in entry
            assert "pct" in entry
            assert "example_boards" in entry
            assert entry["pct"] <= 100

    def test_nonexistent_tag(self, boards_db):
        assert boards_db.get_tag_consensus("nonexistent-tag-xyz") is None

    def test_motor_control_single_board(self, boards_db):
        """motor-control has only 1 board in test data → None (need 2+)."""
        c = boards_db.get_tag_consensus("motor-control")
        assert c is None

    def test_sensors_consensus(self, boards_db):
        """sensors tag has 2 boards → should return consensus."""
        c = boards_db.get_tag_consensus("sensors")
        assert c is not None
        assert c["board_count"] == 2


# ---------------------------------------------------------------------------
# Build script — neighborhood extraction
# ---------------------------------------------------------------------------

class TestNeighborhoodExtraction:
    def test_neighborhoods_built(self, boards_db):
        b = boards_db.get_board("test-esp32-board")
        assert b is not None
        # Should have neighborhoods for ESP32-S3 and MCP73831
        hood_values = [h["value"] for h in b["neighborhoods"]]
        assert any("ESP32" in v for v in hood_values)
        assert any("MCP73831" in v for v in hood_values)

    def test_decoupling_caps_tracked(self, boards_db):
        """Decoupling caps should appear in neighborhood pins."""
        b = boards_db.get_board("test-esp32-board", focus="MCP73831")
        assert b is not None
        if "focus" in b:
            pins = b["focus"]["pins"]
            all_values = []
            for pin_comps in pins.values():
                for c in pin_comps:
                    all_values.append(c["value"])
            # Should see the 10uF decoupling cap
            assert any("10uF" in v for v in all_values) or "_decoupling" in pins

    def test_power_nets_excluded(self, boards_db):
        """Power nets (3V3, GND) should not appear as pin connections."""
        b = boards_db.get_board("test-esp32-board", focus="ESP32-S3")
        if b and "focus" in b:
            pin_names = list(b["focus"]["pins"].keys())
            # Should not have pins named for power nets
            for pn in pin_names:
                assert pn not in ("3V3", "GND", "VCC")


# ---------------------------------------------------------------------------
# Build script — org extraction
# ---------------------------------------------------------------------------

class TestOrgExtraction:
    def test_known_org(self, boards_db):
        b = boards_db.get_board("adafruit-motor-shield")
        assert b is not None
        assert b["org"] == "adafruit"
        assert b["org_display"] == "Adafruit"

    def test_sparkfun_org(self, boards_db):
        b = boards_db.get_board("sparkfun-mcp73831-charger")
        assert b is not None
        assert b["org"] == "sparkfun"
        assert b["org_display"] == "SparkFun"

    def test_soldered_org(self, boards_db):
        b = boards_db.get_board("ble-sensor-node")
        assert b is not None
        assert b["org"] == "SolderedElectronics"
        assert b["org_display"] == "Soldered Electronics"

    def test_unknown_org_fallback(self, boards_db):
        b = boards_db.get_board("test-esp32-board")
        assert b is not None
        assert b["org"] == "testorg"
        assert b["org_display"] == "Testorg"  # capitalize fallback


# ---------------------------------------------------------------------------
# Thread safety — close and reopen
# ---------------------------------------------------------------------------

class TestThreadSafety:
    def test_close_and_reopen(self, boards_db):
        """Closing and re-ensuring should work without error."""
        boards_db.close()
        boards_db._ensure_db()
        stats = boards_db.get_stats()
        assert stats["total_boards"] == 5
