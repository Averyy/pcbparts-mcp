"""0.7.1 regressions against the local catalog; no live distributor requests."""

import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
import yaml

import pcbparts_mcp.server as server
from pcbparts_mcp.parsers import parse_dimensions_from_package, parse_length_mm, parse_voltage
from pcbparts_mcp.search import engine
from pcbparts_mcp.smart_parser import parse_smart_query

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline


@pytest.fixture(autouse=True)
async def no_network():
    # Async so the event loop exists first: on Windows its socket pair is built with connect()
    with offline():
        yield


@pytest.mark.parametrize("kind", ["SMD", "Leaded"])
@pytest.mark.parametrize("field,maximum", [("Height", 5.4), ("Height", 7), ("Height", 11), ("Diameter", 6.3)])
async def test_electrolytic_dimensions(kind, field, maximum):
    category = f"Aluminum Electrolytic Capacitors - {kind}"
    result = await server.jlc_search(subcategory_name=category, limit=100,
                                     spec_filters=[{"name": field, "op": "<=", "value": f"{maximum}mm"}])
    assert result["results"]
    assert result.get("counts_complete", True)
    assert sum(result["library_type_counts"].values()) == result["total"]
    # Height also reads the seated height, which some electrolytics list instead (0.7.4).
    names = [field, "Height - Seated (Max)"] if field == "Height" else [field]
    for part in result["results"]:
        value = next((v for n in names if (v := parse_length_mm(part["specs"].get(n, ""))) is not None), None)
        if value is None:
            dimensions = parse_dimensions_from_package(part["package"])
            value = dimensions[0 if field == "Diameter" else 1]
        assert value is not None and value <= maximum, part
    # Independently count the whole category, including rows without the attribute.
    db = server.get_db()
    rows = db._conn.execute("SELECT attributes, package FROM components WHERE subcategory_id = ? AND stock >= 10",
                            [db.resolve_subcategory_name(category)])
    expected = 0
    for attributes, package in rows:
        specs = dict(json.loads(attributes))
        value = next((v for n in names if (v := parse_length_mm(specs.get(n, ""))) is not None), None)
        if value is None:
            value = parse_dimensions_from_package(package or "")[0 if field == "Diameter" else 1]
        expected += value is not None and value <= maximum
    assert result["total"] == expected


async def test_dimension_scan_cap_is_disclosed(monkeypatch):
    monkeypatch.setattr(engine, "POST_FILTER_SCAN_ROWS", 5)
    result = await server.jlc_search(subcategory_name="Aluminum Electrolytic Capacitors - SMD",
                                     spec_filters=[{"name": "Height", "op": "<=", "value": "11mm"}])
    assert result["counts_complete"] is False
    assert result["total"] <= 5


async def test_switch_height_is_unchanged():
    result = await server.jlc_search(subcategory_name="Tactile Switches", limit=100,
                                     spec_filters=[{"name": "Switch Height", "op": "=", "value": "1.5mm"}])
    assert result["results"]
    assert all(p["specs"]["Switch Height"] == "1.5mm" for p in result["results"])
    db = server.get_db()
    expected = db._conn.execute("SELECT COUNT(*) FROM components WHERE subcategory_id = ? AND stock >= 10 AND attributes LIKE ?",
                               [db.resolve_subcategory_name("Tactile Switches"), '%"Switch Height", "1.5mm"%']).fetchone()[0]
    assert result["total"] == expected


@pytest.mark.parametrize("query,mpn", [
    ("UWT1H220MCL 25V capacitor", "UWT1H220MCL"),
    ("PSM712LFT7 SOT-23 diode", "PSM712LFT7"),
    ("G6K-2F-5DC relay", "G6K-2F-5DC"),
])
async def test_part_numbers_are_never_dropped(query, mpn):
    result = await server.jlc_search(query=query, limit=100)
    assert all(p["model"].upper().startswith(mpn) for p in result["results"])
    assert "dropped_text" not in result.get("relaxed", {})
    if mpn == "UWT1H220MCL":
        assert result["results"]
        assert result["relaxed"]["dropped_part_type"]
        assert "dropped_filters" not in result["relaxed"]
        assert all(parse_voltage(p["specs"]["Voltage Rating"]) >= 25 for p in result["results"])
    if not result["total"]:
        assert "jlc_stock_check" in result["hint"]


@pytest.mark.parametrize("query", ["R1 1MΩ 0603 1%", "LED1 0603 LED", "LED123 0603 LED"])
async def test_bom_designators_still_relax(query):
    result = await server.jlc_search(query=query, limit=100)
    control = await server.jlc_search(query=query.split(maxsplit=1)[1], limit=100)
    assert result["results"] == control["results"]
    assert result["total"] == control["total"] > 0
    assert result["relaxed"]["dropped_text"] == query.split()[0]


@pytest.mark.parametrize("token", ["R1", "C10", "LED1", "U3", "SW2", "J12", "Q4", "D7", "TP3", "FB1", "IC2", "CN1", "JP1", "RN1", "K1", "F1", "Y1", "X1", "LED123"])
def test_reference_designators_are_not_protected(token):
    assert server._protected_mpn_tokens(token, parse_smart_query(token)) == []


@pytest.mark.parametrize("token", ["UWT1H220MCL", "G6K-2F-5DC", "PSM712LFT7", "SC16IS752", "ISO7721"])
def test_full_and_hyphenated_mpn_tokens_are_protected(token):
    assert server._protected_mpn_tokens(token, parse_smart_query(token)) == [token]


@pytest.mark.parametrize("token", ["SOT-416", "LQFP-48", "TO-220", "AEC-Q100", "M205", "CL10", "C0402", "IP67"])
def test_packages_standards_and_short_words_are_not_protected(token):
    assert server._protected_mpn_tokens(token, parse_smart_query(token)) == []


@pytest.mark.parametrize("query", ["LM358", "BAV99", "NE555", "TL431"])
def test_short_part_numbers_come_from_the_parsed_model(query):
    assert parse_smart_query(query).model_number == query


@pytest.mark.parametrize("query,subcategory", [
    ("8MHz SOT-416 crystal", "crystal"),
    ("M205 2A fuse", "fuse"),
    ("AEC-Q100 CAN transceiver", "can"),
])
async def test_descriptive_tokens_keep_the_part_type(query, subcategory):
    result = await server.jlc_search(query=query, limit=100)
    assert result["results"] and "dropped_part_type" not in result.get("relaxed", {})
    assert all(subcategory in p["subcategory"].lower() for p in result["results"])


async def test_short_model_never_costs_the_parsed_values():
    result = await server.jlc_search(query="CL10 10uH SD73 inductor", limit=100)
    assert not any("capacitor" in p["subcategory"].lower() for p in result["results"])
    assert "dropped_filters" not in result.get("relaxed", {})


async def test_missing_part_number_hint_names_it():
    result = await server.jlc_search(query="PSM712LFT7 SOT-23 diode", limit=5)
    assert result["total"] == 0
    assert result["hint"].startswith("No in-stock part matches PSM712LFT7")
    assert 'jlc_stock_check(query="PSM712LFT7")' in result["hint"]


@pytest.mark.parametrize("query", ["25V capacitor", "100nF 0603 capacitor", "SOT-23 diode", "0603 1MΩ 1% resistor"])
def test_consumed_tokens_are_not_part_numbers(query):
    assert server._protected_mpn_tokens(query, parse_smart_query(query)) == []


async def test_lm358_is_unchanged():
    result = await server.jlc_search(query="LM358 op amp", limit=100)
    control = server.get_db().search(query="LM358", subcategory_name="operational amplifier", limit=100)
    assert result["results"] == control["results"]
    assert result["total"] == control["total"] > 0
    assert "relaxed" not in result


async def test_part_number_retry_drops_only_parsed_filters():
    result = await server.jlc_search(query="UWT1H220MCL 999V capacitor", limit=100)
    assert result["results"]
    assert all(p["model"].startswith("UWT1H220MCL") for p in result["results"])
    assert result["relaxed"]["dropped_filters"] == [{"name": "Voltage Rating", "op": ">=", "value": "999V"}]
    explicit = await server.jlc_search(query="UWT1H220MCL 25V capacitor",
                                       spec_filters=[{"name": "Voltage Rating", "op": ">=", "value": "999V"}])
    assert explicit["total"] == 0 and "relaxed" not in explicit
    assert explicit["filters_applied"]["spec_filters"] == [{"name": "Voltage Rating", "op": ">=", "value": "999V"}]


@pytest.mark.parametrize("constraint", ["strict", "subcategory_name", "subcategory_id"])
async def test_part_number_retry_respects_strict_and_caller_category(constraint):
    values = {"strict": True, "subcategory_name": "capacitor",
              "subcategory_id": server.get_db().resolve_subcategory_name("capacitor")}
    result = await server.jlc_search(query="UWT1H220MCL 25V capacitor", **{constraint: values[constraint]})
    assert result["total"] == 0
    assert "relaxed" not in result


@pytest.mark.parametrize("drop_specs", [False, True])
async def test_part_number_retry_order_and_explicit_constraints(monkeypatch, drop_specs):
    db = server.get_db()
    calls = []

    def search(**args):
        calls.append(args)
        found = not args["subcategory_name"] and (not drop_specs or len(args["spec_filters"]) == 1)
        return {"results": [{"model": "UWT1H220MCL6GS"}] if found else [], "total": int(found)}

    monkeypatch.setattr(db, "search", search)
    result = await server.jlc_search(query="UWT1H220MCL 25V capacitor", package="SMD", manufacturer="Nichicon",
                                     library_type="extended", min_stock=50, prefer_no_fee=False,
                                     spec_filters=[{"name": "Capacitance", "op": "=", "value": "22uF"}])
    assert result["total"] == 1
    assert len(calls) == (3 if drop_specs else 2)
    assert len(calls[1]["spec_filters"]) == 2
    assert all(c["query"] == "UWT1H220MCL" and c["package"] == "SMD" and c["manufacturer"] == "Nichicon"
               and c["library_type"] == "extended" and c["min_stock"] == 50 and not c["prefer_no_fee"] for c in calls)
    assert ("dropped_filters" in result["relaxed"]) is drop_specs
    if drop_specs:
        assert [f.to_dict() for f in calls[-1]["spec_filters"]] == [{"name": "Capacitance", "op": "=", "value": "22uF"}]
        assert result["relaxed"]["dropped_filters"] == [{"name": "Voltage Rating", "op": ">=", "value": "25V"}]


async def test_empty_mpn_lookup_keeps_error_and_adds_hint():
    mpn = "ZZNOEXIST123456789"
    result = await server.jlc_get_part(mpn=mpn)
    assert result["error"] == f"No JLCPCB parts found for MPN '{mpn}'"
    assert "stock >= 10" in result["hint"] and f'jlc_stock_check(query="{mpn}")' in result["hint"]
    assert "mouser_get_part" in result["hint"] and "digikey_get_part" in result["hint"]
    assert server._call_outcome(SimpleNamespace(structured_content=result)) == "not_found"


@pytest.mark.parametrize("strict", [False, True])
async def test_empty_search_hint_uses_actual_constraints(strict):
    result = await server.jlc_search(subcategory_name="MOSFETs", strict=strict, package="NoSuchPackage",
                                     packages=["AlsoNoSuchPackage"], library_type="basic", manufacturer="NoSuchManufacturer")
    assert result["total"] == 0 and "error" not in result
    hint = result["hint"]
    assert 'jlc_search_help(subcategory="MOSFETs")' in hint
    assert all(name in hint for name in ["library_type", "package", "manufacturer", "jlc_stock_check"])
    assert server._call_outcome(SimpleNamespace(structured_content=result)) == "not_found"


async def test_empty_search_hint_points_to_ignored_filters():
    result = await server.jlc_search(subcategory_name="Tactile Switches",
                                     spec_filters=[{"name": "Height", "op": "<=", "value": "0.001mm"}])
    assert result["total"] == 0 and result["ignored_filters"]
    assert "ignored_filters" in result["hint"]


async def test_existing_supercapacitor_hint_is_preserved():
    result = await server.jlc_search(query="supercapacitor")
    assert result["hint"] == "JLCPCB has no supercapacitor subcategory in this catalog; try Mouser or DigiKey."


@pytest.mark.parametrize("total,allow,success", [(96, False, True), (95, False, True), (94, False, False), (94, True, True)])
def test_scrape_part_count_guard(monkeypatch, tmp_path, total, allow, success):
    workflow = yaml.safe_load(Path(".github/workflows/scrape-components.yml").read_text())
    assert workflow[True]["workflow_dispatch"]["inputs"]["allow_part_drop"]["default"] is False
    steps = workflow["jobs"]["scrape"]["steps"]
    guard = next(s for s in steps if s["name"] == "Check part count")
    assert steps.index(guard) < next(i for i, s in enumerate(steps) if s["name"] == "Commit and push data files")
    # Run the heredoc's Python directly: Windows runners have no usable bash on PATH
    assert guard["run"].startswith("python - <<'PY'\n") and guard["run"].rstrip().endswith("\nPY")
    script = guard["run"].split("\n", 1)[1].rstrip().removesuffix("PY")
    (tmp_path / "data").mkdir()
    manifest = tmp_path / "data/manifest.json"
    manifest.write_text(json.dumps({"total_parts": 100}))
    git = ["git", "-C", str(tmp_path), "-c", "user.name=test", "-c", "user.email=test@example.com",
           "-c", "commit.gpgsign=false"]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "data/manifest.json"], check=True)
    subprocess.run([*git, "commit", "-q", "--no-verify", "-m", "previous scrape"], check=True)
    manifest.write_text(json.dumps({"total_parts": total}))
    monkeypatch.setenv("ALLOW_PART_DROP", str(allow).lower())
    result = subprocess.run([sys.executable, "-c", script], cwd=tmp_path, capture_output=True, text=True)
    assert (result.returncode == 0) is success, result.stderr
    assert "100" in result.stdout and str(total) in result.stdout


async def test_misparsed_suffix_searches_the_surviving_part_number():
    # "40W" is read as a power rating; the part number left is BC817, listed as BC817-40
    assert server._protected_mpn_tokens("BC817-40W", parse_smart_query("BC817-40W")) == ["BC817"]
    result = await server.jlc_search(query="BC817-40W SOT-23 transistor", limit=100)
    assert result["results"] and all(p["model"].upper().startswith("BC817") for p in result["results"])


@pytest.mark.parametrize("query", ["YS-SK6812MINI-E LED", "VS-E7FX0212-M3/I diode", "DR73-100-R inductor"])
async def test_part_number_retry_rejects_unrelated_prefix_matches(query):
    # The engine's MPN fallback shortens part numbers to prefixes ("YS") that match other parts
    result = await server.jlc_search(query=query, limit=100)
    mpn = query.split()[0].replace("-", "").upper()
    assert all(mpn[:8] in p["model"].replace("-", "").upper() for p in result["results"])
    if not result["total"]:
        assert result["hint"].startswith("No in-stock part matches")


async def test_part_number_retry_counts_follow_kept_parts():
    result = await server.jlc_search(query="SMBJ18CA diode", limit=5)
    assert result["relaxed"]["dropped_part_type"]
    assert sum(result["library_type_counts"].values()) == result["total"] >= len(result["results"])
    assert all(p["model"].upper().startswith("SMBJ18CA") for p in result["results"])
