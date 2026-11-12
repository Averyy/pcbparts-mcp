"""Why calls found nothing or failed, in /mcp/stats: fixed labels, one a call, never what users typed."""

from contextlib import closing
import datetime
import json
import sys
from pathlib import Path
from types import SimpleNamespace

from fastmcp import Client
import pytest

import pcbparts_mcp.server as server
from pcbparts_mcp import stats
from pcbparts_mcp.stats import REASONS, WHY_EMPTY_RESULTS, UsageStats
from test_usage_stats import ERROR_REPLIES, EXCEPTION_MESSAGES, _render

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from search_baseline import offline


NOW = datetime.datetime(2026, 11, 9, 12, tzinfo=datetime.timezone.utc).timestamp()


def fresh() -> UsageStats:
    return UsageStats(clock=lambda: NOW)


class TestCounts:
    def test_counted_per_tool_commonest_first_and_in_totals(self):
        usage = fresh()
        for reason in ("no_results", "no_part_type", "no_part_type"):
            usage.record_call("jlc_search", "not_found", 1, reason=reason)
        usage.record_call("board_get", "not_found", 1, reason="board_not_found")
        summary = usage.summary()
        expected = {"board_get": {"board_not_found": 1}, "jlc_search": {"no_part_type": 2, "no_results": 1}}
        assert summary["days"][0]["reasons"] == expected and summary["totals"]["reasons"] == expected
        assert list(summary["days"][0]["reasons"]["jlc_search"]) == ["no_part_type", "no_results"]

    def test_a_label_outside_the_list_is_other_so_typed_text_cannot_be_stored(self, tmp_path):
        usage = fresh()
        usage.open(tmp_path / "usage.json")
        usage.record_call("jlc_search", "not_found", 1, reason="SECRET-PN-123")
        usage.save()
        assert usage.summary()["days"][0]["reasons"] == {"jlc_search": {"other": 1}}
        assert "SECRET-PN-123" not in (tmp_path / "usage.json").read_text(encoding="utf-8")

    def test_unknown_tool_names_share_one_row(self):
        usage = fresh()
        usage.tools = {"jlc_search"}
        usage.record_call("made_up_tool", "not_found", 1, reason="no_results")
        assert usage.summary()["days"][0]["reasons"] == {"unknown": {"no_results": 1}}

    def test_survives_a_restart_and_drops_labels_not_in_the_list(self, tmp_path):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-11-09": {
            "tools": {}, "apps": {}, "callers": 0, "distributors": {"digikey": {"sent": 3, "retry_found": 1}},
            "reasons": {"jlc_search": {"no_results": 4, "typed by a user": 9}, "bad": 7},
            "why_empty": {"complete": 2, "typed by a user": 5}}}}), encoding="utf-8")
        usage = UsageStats(clock=lambda: NOW)
        usage.open(path)
        usage.record_call("jlc_search", "not_found", 1, reason="no_results")
        usage.record_why_empty("complete")
        day = usage.summary()["days"][0]
        assert day["reasons"] == {"jlc_search": {"no_results": 5}}
        assert day["why_empty"] == {"complete": 3}
        assert day["distributors"]["digikey"] == {"sent": 3, "cached": 0, "rate_limited": 0, "retry_found": 1}

    def test_days_saved_before_this_release_have_none(self, tmp_path):
        path = tmp_path / "usage.json"
        path.write_text(json.dumps({"days": {"2026-11-08": {"tools": {}, "apps": {}, "callers": 0,
                                                            "distributors": {"mouser": {"sent": 1}}}}}), encoding="utf-8")
        usage = UsageStats(clock=lambda: NOW)
        usage.open(path)
        day = usage.summary()["days"][0]
        assert day["reasons"] == {} and day["why_empty"] == {}
        assert day["distributors"]["mouser"] == {"sent": 1, "cached": 0, "rate_limited": 0}

    def test_retry_events_add_up_in_totals(self):
        usage = fresh()
        usage.record_distributor("digikey", "retry_found")
        usage.record_distributor("digikey", "retry_found")
        usage.record_distributor("mouser", "sent")
        totals = usage.summary()["totals"]["distributors"]
        assert totals["digikey"]["retry_found"] == 2 and "retry_found" not in totals["mouser"]

    def test_a_call_and_its_reason_land_on_the_same_day_across_utc_midnight(self):
        ticks = iter([datetime.datetime(2026, 11, 9, 23, 59, 59, 999_999, tzinfo=datetime.timezone.utc).timestamp(),
                      datetime.datetime(2026, 11, 10, 0, 0, 1, tzinfo=datetime.timezone.utc).timestamp()])
        usage = UsageStats(clock=lambda: next(ticks))
        usage.record_call("jlc_search", "not_found", 1, reason="no_results")
        days = usage.summary()["days"]
        assert len(days) == 1 and days[0]["date"] == "2026-11-09"
        assert days[0]["tools"]["jlc_search"]["not_found"] == 1
        assert days[0]["reasons"] == {"jlc_search": {"no_results": 1}}

    def test_a_call_with_no_reason_records_none(self):
        usage = fresh()
        usage.record_call("jlc_search", "ok", 1)
        assert usage.summary()["days"][0]["reasons"] == {}

    def test_unknown_why_empty_result_is_not_stored(self):
        usage = fresh()
        usage.record_why_empty("not a result")
        assert usage.summary()["totals"]["why_empty"] == {}


BLOCK = {"why_empty": {"blocking": [{"constraint": "package"}]}}
TWO = {"why_empty": {"blocking": [{"constraint": "package"}, {"constraint": "min_stock"}]}}
EMPTY = {"results": [], "total": 0}


@pytest.mark.parametrize("content,reason", [
    ({"results": [], "total": 9}, "offset_past_end"),
    ({**EMPTY, **BLOCK}, "blocked_by_package"),
    ({**EMPTY, **TWO}, "blocked_by_several"),
    ({**EMPTY, "why_empty": {"blocking": [{"constraint": "library_type"}]}}, "blocked_by_library_type"),
    ({**EMPTY, "why_empty": {"blocking": [{"constraint": "min_stock"}]}}, "blocked_by_min_stock"),
    # a blocking filter names more than the hint does
    ({**EMPTY, **BLOCK, "hint": "No in-stock part matches X; try"}, "blocked_by_package"),
    ({**EMPTY, "hint": "3 in-stock parts match NE555, but none with the package given"}, "part_number_filtered_out"),
    ({**EMPTY, "hint": "1 in-stock part match NE555, but"}, "part_number_filtered_out"),
    ({**EMPTY, "hint": "No in-stock part matches X; try jlc_stock_check"}, "part_number_not_in_stock"),
    ({**EMPTY, "hint": "No part's description has all of the words \"a b\"; without"}, "words_unmatched"),
    ({**EMPTY, "hint": "No part type matched \"x\", so"}, "no_part_type"),
    ({**EMPTY, "hint": "No no-fee part matches TL431; 3 extended"}, "blocked_by_library_type"),
    ({**EMPTY, "hint": "No basic part matches; 3 extended"}, "blocked_by_library_type"),
    ({**EMPTY, "hint": "JLCPCB has no supercapacitor subcategory"}, "no_catalog_subcategory"),
    ({**EMPTY, "hint": "No part C1 with stock >= 10. min_stock=0"}, "stock_below_minimum"),
    ({**EMPTY, "hint": "JLCPCB's search matches whole part numbers and"}, "part_number_fragment"),
    # the hint's opening decides, not words later in it
    ({**EMPTY, "hint": "Try jlc_search_help. No part type matched \"x\""}, "no_results"),
    ({**EMPTY, "unlisted": [{"filter": "ESR", "parts": 3}], "hint": "3 parts meet the other"}, "value_not_listed"),
    ({**EMPTY, "ignored_filters": [{"filter": "Bogus"}]}, "filter_ignored_or_sparse"),
    ({**EMPTY, "filters_applied": {"spec_filters": [{"name": "ESR"}]}}, "spec_filters_no_match"),
    ({**EMPTY, "filters_applied": {"spec_filters": []}}, "no_results"),
    (EMPTY, "no_results"),
    ({"matched_files": []}, "no_results"),
    ({"alternatives": [], "similar_parts": []}, "no_alternatives"),
    ({"error": "No part found in the local snapshot for MPN 'X'", "next_call": {"tool": "jlc_stock_check"},
      "hint": "The local catalog"}, "mpn_not_in_snapshot"),
    ({"error": "No part found in the local snapshot for MPN 'DNP'", "next_call": None, "hint": "'DNP' is"}, "placeholder_mpn"),
    ({"error": "No part found in the local snapshot for MPN 'C5'", "next_call": {"tool": "jlc_stock_check"},
      "hint": "'C5' looks like an LCSC code: jlc"}, "lcsc_code_as_mpn"),
    ({"error": "Part C5 not found"}, "lcsc_not_found"),
    ({"error": "Part not found: 209"}, "part_not_found"),
    ({"error": "No ECAD model available for 'X'"}, "no_ecad_model"),
    ({"error": "No KiCad files found in model archive for part 7"}, "no_kicad_in_archive"),
])
def test_empty_reasons(content, reason):
    assert server._empty_reason(content) == reason
    assert reason in REASONS


@pytest.mark.parametrize("message,reason", [
    ("CSE model download failed (HTTP 404)", "cse_download_http_4xx"),
    ("CSE model download failed (HTTP 503)", "cse_download_http_5xx"),
    ("CSE model download failed (HTTP 302)", "cse_download_http"),
    ("CSE model download failed (network/connection error)", "cse_download_network"),
    ("CSE get_kicad failed. Check server logs for details.", "cse_lookup_failed"),
    ("JLCPCB blocked request with WAF challenge — try again later", "jlcpcb_waf"),
    ("Something nobody expected", "unexpected_error"),
])
def test_failed_reasons(message, reason):
    assert server._call_reason("failed", {"error": message}, None) == reason


def test_a_raised_exception_is_counted_as_one():
    assert server._call_reason("failed", {}, RuntimeError("boom")) == "exception"


@pytest.mark.parametrize("why_empty,result", [
    ({"status": "budget_exhausted_or_busy", "diagnostics_complete": False, "extra_queries": 1}, "budget_exhausted_or_busy"),
    ({"status": "diagnostic_failed", "diagnostics_complete": False, "extra_queries": 0}, "diagnostic_failed"),
    ({"diagnostics_complete": True, "extra_queries": 0}, "no_counterfactual"),
    ({"diagnostics_complete": True, "extra_queries": 2}, "complete"),
    ({"diagnostics_complete": False, "extra_queries": 3}, "incomplete"),
])
def test_why_empty_results(why_empty, result):
    assert server._why_empty_result(why_empty) == result
    assert result in WHY_EMPTY_RESULTS


class TestEveryMessageHasAReason:
    """A new not_found or failed message has to be given a label, as ERROR_REPLIES makes it be sorted."""

    def test_not_found_messages(self):
        messages = [t for t, kind in {**ERROR_REPLIES, **EXCEPTION_MESSAGES}.items() if kind == "not_found"]
        assert messages
        missing = [t for t in messages if server._first_reason(server._NOT_FOUND_REASONS, _render(t)) is None]
        assert missing == []

    def test_failed_messages(self):
        messages = [t for t, kind in {**ERROR_REPLIES, **EXCEPTION_MESSAGES}.items() if kind == "failed"]
        assert messages
        missing = [t for t in messages if server._first_reason(server._FAILED_REASONS, _render(t)) is None]
        assert missing == []

    def test_every_table_label_is_storable(self):
        # labels written out in _empty_reason and _call_reason are checked by the parametrized tests above
        tables = (server._NOT_FOUND_REASONS, server._FAILED_REASONS, server._EMPTY_HINT_REASONS)
        assert {reason for table in tables for reason, _ in table} - REASONS == set()

    def test_blocking_constraints_tested_all_have_labels(self):
        source = (Path(server.__file__).parent / "search" / "diagnostics.py").read_text(encoding="utf-8")
        for name in ("library_type", "package", "min_stock"):
            assert f"('{name}'" in source and f"blocked_by_{name}" in REASONS


def recorded(tool="jlc_search"):
    day = stats.usage.summary()["days"][0]
    return day["reasons"].get(tool, {}), day["tools"][tool], day


@pytest.fixture
async def local_client():
    with offline():
        async with Client(server.mcp) as client:
            yield client


@pytest.mark.parametrize("args,reason", [
    ({"query": "ZZQ9981XK"}, "part_number_not_in_stock"),
    ({"subcategory_name": "Ferrite Beads", "min_stock": 99_999_999}, "blocked_by_min_stock"),
    ({"query": "quantum sparkle", "subcategory_name": "Ferrite Beads"}, "words_unmatched"),
    ({"query": "wobbler gizmoflux"}, "no_part_type"),
    ({"subcategory_name": "Ferrite Beads", "offset": 9_000_000}, "offset_past_end"),
    ({"query": "supercapacitor"}, "no_catalog_subcategory"),
])
async def test_real_empty_searches(local_client, args, reason):
    await local_client.call_tool("jlc_search", args, raise_on_error=False)
    reasons, counts, _ = recorded()
    assert reasons == {reason: 1} and counts["not_found"] == 1


@pytest.mark.parametrize("mpn,reason", [
    ("DNP", "placeholder_mpn"), ("ZZQ9981XK", "mpn_not_in_snapshot"), ("C1234567890", "lcsc_code_as_mpn"),
])
async def test_real_mpn_misses(local_client, mpn, reason):
    await local_client.call_tool("jlc_get_part", {"mpn": mpn}, raise_on_error=False)
    assert recorded("jlc_get_part")[0] == {reason: 1}


async def test_labels_add_up_to_outcomes_and_nothing_typed_is_kept(local_client, tmp_path):
    stats.usage.open(tmp_path / "usage.json")
    queries = [{"query": "ZZQ9981XK"}, {"query": "wobbler gizmoflux"}, {"query": "quantum sparkle", "subcategory_name": "Ferrite Beads"},
               {"subcategory_name": "Ferrite Beads", "min_stock": 99_999_999}, {"query": "resistor 10k 0402"}]
    for args in queries:
        await local_client.call_tool("jlc_search", args, raise_on_error=False)
    reasons, counts, day = recorded()
    assert sum(reasons.values()) == counts["not_found"] + counts["failed"] == 4 and counts["calls"] == 5
    assert sum(day["why_empty"].values()) == 4
    stats.usage.save()
    saved = (tmp_path / "usage.json").read_text(encoding="utf-8")
    for typed in ("ZZQ9981XK", "wobbler", "gizmoflux", "quantum", "sparkle"):
        assert typed not in saved and typed not in json.dumps(stats.usage.summary())


async def test_a_successful_search_records_no_reason(local_client):
    await local_client.call_tool("jlc_search", {"query": "resistor 10k 0402"}, raise_on_error=False)
    day = stats.usage.summary()["days"][0]
    assert day["reasons"] == {} and day["why_empty"] == {}


async def test_counting_never_breaks_a_call(local_client, monkeypatch):
    def broken(*_args):
        raise RuntimeError("stats down")
    monkeypatch.setattr(stats.usage, "record_call", broken)
    result = await local_client.call_tool("jlc_search", {"query": "ZZQ9981XK"}, raise_on_error=False)
    assert result.structured_content["total"] == 0


def test_middleware_records_an_exception_reason():
    context = SimpleNamespace(message=SimpleNamespace(name="jlc_search"))
    server.UsageStatsMiddleware._record(context, 0.0, error=RuntimeError("boom"))
    assert recorded()[0] == {"exception": 1}


# ---- sensors: datasheet facts ----

async def sensor(client, name):
    result = (await client.call_tool("sensor_recommend", {"query": name})).structured_content
    return next(p for p in result["results"] if p["id"] == name.lower())


async def ids(client, measure):
    result = (await client.call_tool("sensor_recommend", {"measure": measure, "limit": 50})).structured_content
    return {p["id"] for p in result["results"]}


@pytest.mark.parametrize("name,measures,inputs", [
    ("ENS160", {"eco2", "gas", "voc"}, ["humidity", "temperature"]),
    ("SGP30", {"eco2", "gas", "voc"}, ["humidity"]),
])
async def test_estimated_co2_parts_report_what_their_datasheets_say(local_client, name, measures, inputs):
    part = await sensor(local_client, name)
    assert set(part["measures"]) == measures
    assert part["compensation_inputs"] == inputs
    assert part["capability_note"] and part["voltage_evidence"]["source_url"].startswith("https://")


async def test_ens160_voltage_is_its_core_supply(local_client):
    part = await sensor(local_client, "ENS160")
    assert part["voltage"] == "1.71-1.98"
    assert "VDDIO" in part["capability_note"] and "VDDIO 1.71-3.6V" in part["voltage_evidence"]["recommended_operating"]


async def test_sgp30_voltage_unchanged(local_client):
    assert (await sensor(local_client, "SGP30"))["voltage"] == "1.62-1.98"


async def test_co2_search_keeps_real_co2_sensors_and_drops_estimates(local_client):
    direct = await ids(local_client, "co2")
    assert not {"ens160", "sgp30", "ccs811"} & direct
    assert {"scd4x", "scd30"} & direct
    assert {"ens160", "sgp30", "ccs811"} <= await ids(local_client, "eco2")


async def test_capability_notes_are_copies(local_client):
    first = await sensor(local_client, "SGP30")
    first["compensation_inputs"].append("changed")
    assert (await sensor(local_client, "SGP30"))["compensation_inputs"] == ["humidity"]


ESTIMATED_CO2 = ["iaqcore", "apc1", "ens160", "sgp30", "ccs811", "sm300d2"]


@pytest.mark.parametrize("sensor_id", ESTIMATED_CO2)
async def test_calculated_co2_is_listed_as_eco2(local_client, sensor_id):
    assert sensor_id not in await ids_all(local_client, "co2")
    assert sensor_id in await ids_all(local_client, "eco2")


async def ids_all(_client, measure):
    """Every id tagged with a measure: the tool's replies are capped, so this reads the database."""
    import sqlite3
    with closing(sqlite3.connect(f"file:{Path('data/sensor.db').resolve()}?mode=ro", uri=True)) as conn, conn:
        return {row[0] for row in conn.execute("SELECT sensor_id FROM sensor_measures WHERE measure = ?", (measure,))}


async def test_bosch_bsec_is_software_on_the_sensor_record(local_client):
    # 0.9.0: the BSEC/BSEC2 software records are excluded (not parts); the note moved to the sensors
    for sensor_id in ("bme680", "bme688"):
        result = (await local_client.call_tool("sensor_recommend", {"query": sensor_id, "limit": 20})).structured_content
        part = next(p for p in result["results"] if p["id"] == sensor_id)
        assert "BSEC" in part["capability_note"] and "eco2" not in part["measures"] and "co2" not in part["measures"]
    assert not {"bme680bsec", "bme68xbsec2"} & (await ids_all(local_client, "gas"))


@pytest.mark.parametrize("sensor_id", ["md62", "sen6x", "scd30", "scd4x"])
async def test_real_co2_sensors_stay_under_co2(local_client, sensor_id):
    assert sensor_id in await ids_all(local_client, "co2")


@pytest.mark.parametrize("sensor_id,voltage", [("ens160", "1.71-1.98"), ("ens161", "1.71-1.98"), ("sciosenseens16x", "1.71-1.98")])
async def test_scioSense_voltage_is_the_core_supply(local_client, sensor_id, voltage):
    result = (await local_client.call_tool("sensor_recommend", {"query": sensor_id, "limit": 20})).structured_content
    assert next(p for p in result["results"] if p["id"] == sensor_id)["voltage"] == voltage


@pytest.mark.parametrize("not_a_sensor", [
    "number", "dewpoint", "motion", "duco", "ecocomfort2", "emontx", "haierwaterheater", "mk2pvrouter", "renogyinverterble",
    "systabus", "vevordtx", "fusb302b", "tmc2209", "waveshareioch32v003", "pca9536", "cd74hc4067", "cc1101", "pid5sensors",
    "ximu3", "rk182xexamples", "zi100zi101", "zi121", "co2", "tsen", "emu", "bcm283xvcthermal",
])
async def test_things_that_are_not_sensors_are_gone(local_client, not_a_sensor):
    result = (await local_client.call_tool("sensor_recommend", {"query": not_a_sensor, "limit": 50})).structured_content
    assert not_a_sensor not in {p["id"] for p in result["results"]}


@pytest.mark.parametrize("sensor_id,voltage", [
    ("iaqcore", "3.2-3.4"),     # ams iAQ-Core v1-00 p.3: 3.3V ±0.1V
    ("sm300d2", "4.8-5.2"),     # module parameter table: 5 ±0.2V
    ("max32664", "1.71-3.63"),  # MAX32664 Rev 4 p.7: VDD
    ("max32664c", "1.71-3.63"),
])
async def test_supply_ranges_match_the_datasheets(local_client, sensor_id, voltage):
    result = (await local_client.call_tool("sensor_recommend", {"query": sensor_id, "limit": 20})).structured_content
    assert next(p for p in result["results"] if p["id"] == sensor_id)["voltage"] == voltage


@pytest.mark.parametrize("sensor_id,wrong", [
    ("ad7193", "sound"), ("ad7194", "sound"), ("ads122c04", "sound"),  # "low noise" ADCs
    ("mcp3427", "weight"), ("i2cirsense", "weight"),  # Iowa Scaled Engineering boards
    ("tla2021", "force"),  # PGA/FSR is full-scale range
    ("max32664c", "acceleration"),  # a sensor hub that reads an accelerometer
    ("max30101", "particulate"),  # MAX30105 is the smoke-detection sibling
])
async def test_parts_are_not_listed_under_measures_they_do_not_take(local_client, sensor_id, wrong):
    assert sensor_id not in await ids_all(local_client, wrong)


@pytest.mark.parametrize("sensor_id", ["ad7194", "ads122c04", "mcp3427", "tla2021", "adc128d818", "ads1258", "ads1115"])
async def test_general_purpose_adcs_are_listed_under_voltage(local_client, sensor_id):
    assert sensor_id in await ids_all(local_client, "voltage")


@pytest.mark.parametrize("sensor_id", ["hx711", "nau7802", "max31855", "max31865", "ads1292r"])
async def test_sensor_front_ends_keep_their_measure(local_client, sensor_id):
    measure = {"hx711": "weight", "nau7802": "weight", "max31855": "temperature", "max31865": "temperature",
               "ads1292r": "biometric"}[sensor_id]
    assert sensor_id in await ids_all(local_client, measure)


async def test_sensor_hubs_say_what_they_need(local_client):
    for sensor_id in ("max32664", "max32664c"):
        part = await sensor(local_client, sensor_id.upper())
        assert part["type"] == "sensor_hub" and "sensor hub" in part["capability_note"]
        assert {"biometric"} == set(part["measures"])


async def test_sm300d2_is_not_credited_to_amphenol(local_client):
    part = await sensor(local_client, "SM300D2")
    assert part["manufacturer"] == "Generic" and "co2" not in part["measures"] and "eco2" in part["measures"]
    assert "calculated from the TVOC" in part["capability_note"]


@pytest.mark.parametrize("sensor_id", ["max30001", "max30003"])
async def test_ecg_front_ends_are_not_optical(local_client, sensor_id):
    assert (await sensor(local_client, sensor_id.upper()))["type"] == "adc"


def test_error_kind_matches_echoed_input_with_a_newline():
    """"Board 'a\\nb' not found" counted as failed/unexpected_error (server review, 2026-11-10)."""
    from pcbparts_mcp import server
    assert server._error_kind("Board 'a\nb' not found") == "not_found"
