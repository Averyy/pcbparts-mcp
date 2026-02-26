"""Test all MCP tools against local Docker container on port 18080.

Uses the official MCP Python client for proper protocol handling.

Usage: .venv/bin/python scripts/test_local_tools.py
"""

import asyncio
import json
import sys
import traceback

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

BASE_URL = "http://localhost:18080/mcp"
PASS = 0
FAIL = 0


def has_key(key):
    return lambda r: f"missing '{key}'" if key not in r else None

def key_gt(key, val):
    return lambda r: f"{key}={r.get(key)} not > {val}" if r.get(key, 0) <= val else None

def key_eq(key, val):
    return lambda r: f"{key}={r.get(key)!r} != {val!r}" if r.get(key) != val else None

def results_not_empty():
    return lambda r: "results is empty" if not r.get("results") else None

def no_error():
    return lambda r: f"error: {r.get('error')}" if "error" in r else None

def result_has_field(field):
    def check(r):
        results = r.get("results", [])
        if not results:
            return f"no results to check for '{field}'"
        if field not in results[0]:
            return f"first result missing '{field}'"
        return None
    return check


async def call_tool(session: ClientSession, tool_name: str, arguments: dict) -> dict:
    """Call an MCP tool and return parsed result."""
    result = await session.call_tool(tool_name, arguments)
    for item in result.content:
        if item.type == "text":
            try:
                return json.loads(item.text)
            except json.JSONDecodeError:
                return {"_raw_text": item.text}
    return {"_empty": True}


async def test_tool(session: ClientSession, name: str, tool: str, args: dict, checks: list):
    """Run a single tool test with validation checks."""
    global PASS, FAIL
    try:
        result = await call_tool(session, tool, args)

        errors = []
        for check_fn in checks:
            err = check_fn(result)
            if err:
                errors.append(err)

        if errors:
            print(f"  FAIL {name}: {'; '.join(errors)}")
            FAIL += 1
        else:
            print(f"  PASS {name}")
            PASS += 1
        return result

    except Exception as e:
        print(f"  FAIL {name}: Exception: {e}")
        traceback.print_exc()
        FAIL += 1
        return {}


async def main():
    global PASS, FAIL

    print("=" * 60)
    print("TESTING ALL MCP TOOLS AGAINST LOCAL DOCKER (port 18080)")
    print("=" * 60)

    async with streamablehttp_client(BASE_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # List available tools first
            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            print(f"\nAvailable tools ({len(tool_names)}): {', '.join(tool_names)}")

            # ============================================================
            # 1. jlc_search (DB search)
            # ============================================================
            print("\n--- jlc_search (DB search) ---")

            await test_tool(session, "basic keyword search", "jlc_search", {
                "query": "ESP32"
            }, [no_error(), results_not_empty(), has_key("total")])

            r = await test_tool(session, "natural language: 10k 0603 1%", "jlc_search", {
                "query": "10k resistor 0603 1%"
            }, [no_error(), results_not_empty(), has_key("parsed")])

            await test_tool(session, "subcategory_name filter", "jlc_search", {
                "subcategory_name": "MOSFETs",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "spec_filters (Vgs(th) < 2.5V)", "jlc_search", {
                "subcategory_name": "MOSFETs",
                "spec_filters": [{"name": "Vgs(th)", "op": "<", "value": "2.5V"}],
                "limit": 5,
            }, [no_error(), results_not_empty(), has_key("filters_applied")])

            await test_tool(session, "library_type=no_fee", "jlc_search", {
                "query": "capacitor 100nF",
                "library_type": "no_fee",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "package filter SOT-23", "jlc_search", {
                "subcategory_name": "MOSFETs",
                "package": "SOT-23",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "packages filter [0402, 0603]", "jlc_search", {
                "query": "resistor 10k",
                "packages": ["0402", "0603"],
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "manufacturer filter", "jlc_search", {
                "query": "STM32",
                "manufacturer": "STMicroelectronics",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "sort_by=price", "jlc_search", {
                "query": "100nF capacitor",
                "sort_by": "price",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "match_all_terms=False", "jlc_search", {
                "query": "ESP32 WROOM",
                "match_all_terms": False,
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "NL: 100nF 25V capacitor", "jlc_search", {
                "query": "100nF 25V capacitor"
            }, [no_error(), results_not_empty(), has_key("parsed")])

            await test_tool(session, "NL: qwiic connector", "jlc_search", {
                "query": "qwiic connector"
            }, [no_error(), has_key("parsed")])

            await test_tool(session, "library_type=extended", "jlc_search", {
                "query": "RP2040",
                "library_type": "extended",
                "limit": 5,
            }, [no_error()])

            await test_tool(session, "browse: subcategory only", "jlc_search", {
                "subcategory_name": "Chip Resistor - Surface Mount",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            # Library type basic
            await test_tool(session, "library_type=basic", "jlc_search", {
                "query": "10uF capacitor",
                "library_type": "basic",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            # Library type preferred
            await test_tool(session, "library_type=preferred", "jlc_search", {
                "query": "LED red",
                "library_type": "preferred",
                "limit": 5,
            }, [no_error()])

            # prefer_no_fee=False
            await test_tool(session, "prefer_no_fee=False", "jlc_search", {
                "query": "capacitor 10uF",
                "prefer_no_fee": False,
                "limit": 5,
            }, [no_error(), results_not_empty()])

            # NL: n-channel mosfet SOT-23
            await test_tool(session, "NL: n-channel mosfet SOT-23", "jlc_search", {
                "query": "n-channel mosfet SOT-23",
            }, [no_error(), results_not_empty(), has_key("parsed")])

            # ============================================================
            # 2. jlc_stock_check (Live API search)
            # ============================================================
            print("\n--- jlc_stock_check (Live API) ---")

            await test_tool(session, "basic stock check", "jlc_stock_check", {
                "query": "ESP32",
                "limit": 5,
            }, [no_error(), results_not_empty(), has_key("total")])

            await test_tool(session, "category_name filter", "jlc_stock_check", {
                "query": "resistor",
                "category_name": "Resistors",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "subcategory_name filter", "jlc_stock_check", {
                "subcategory_name": "MOSFETs",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "library_type=basic", "jlc_stock_check", {
                "query": "10uF capacitor",
                "library_type": "basic",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "library_type=no_fee", "jlc_stock_check", {
                "query": "AMS1117",
                "library_type": "no_fee",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "sort_by=price", "jlc_stock_check", {
                "query": "100nF 0402",
                "sort_by": "price",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "min_stock=0 (out of stock)", "jlc_stock_check", {
                "query": "STM32F103C8T6",
                "min_stock": 0,
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "package filter", "jlc_stock_check", {
                "query": "MOSFET",
                "package": "SOT-23",
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "manufacturer filter", "jlc_stock_check", {
                "query": "LM358",
                "manufacturer": "Texas Instruments",
                "limit": 5,
            }, [no_error()])

            await test_tool(session, "pagination page=2", "jlc_stock_check", {
                "query": "capacitor",
                "page": 2,
                "limit": 5,
            }, [no_error(), results_not_empty()])

            # ============================================================
            # 3. jlc_search_help (Categories/Attributes)
            # ============================================================
            print("\n--- jlc_search_help (Browse/Help) ---")

            await test_tool(session, "list all categories", "jlc_search_help", {
            }, [no_error(), has_key("categories"), lambda r: "no categories" if not r.get("categories") else None])

            await test_tool(session, "subcategories of Transistors", "jlc_search_help", {
                "category": "Transistors/Thyristors",
            }, [no_error(), has_key("subcategories")])

            await test_tool(session, "category by ID", "jlc_search_help", {
                "category": 5,
            }, [no_error(), has_key("subcategories")])

            await test_tool(session, "attributes for MOSFETs", "jlc_search_help", {
                "subcategory": "MOSFETs",
            }, [no_error(), has_key("attributes")])

            await test_tool(session, "attributes by subcategory ID", "jlc_search_help", {
                "subcategory": 2954,
            }, [no_error(), has_key("attributes")])

            await test_tool(session, "invalid category returns error", "jlc_search_help", {
                "category": "NonExistentCategory12345",
            }, [has_key("error")])

            # ============================================================
            # 4. jlc_get_part (Part details)
            # ============================================================
            print("\n--- jlc_get_part ---")

            r = await test_tool(session, "get part by LCSC (C82899)", "jlc_get_part", {
                "lcsc": "C82899",
            }, [no_error(), has_key("lcsc"), has_key("model"), has_key("price")])

            await test_tool(session, "get part by MPN (LM358)", "jlc_get_part", {
                "mpn": "LM358",
            }, [no_error(), results_not_empty()])

            await test_tool(session, "no lcsc/mpn returns error", "jlc_get_part", {
            }, [has_key("error")])

            await test_tool(session, "non-existent LCSC returns error", "jlc_get_part", {
                "lcsc": "C99999999",
            }, [has_key("error")])

            # Check part detail fields
            if r and "lcsc" in r:
                checks_fields = ["lcsc", "model", "manufacturer", "package", "stock",
                                 "price", "library_type", "description", "has_easyeda_footprint"]
                missing = [f for f in checks_fields if f not in r]
                if missing:
                    print(f"  WARN get_part response missing fields: {missing}")

            # ============================================================
            # 5. jlc_find_alternatives
            # ============================================================
            print("\n--- jlc_find_alternatives ---")

            await test_tool(session, "find alternatives for C2557", "jlc_find_alternatives", {
                "lcsc": "C2557",
            }, [no_error(), has_key("original"), has_key("alternatives")])

            await test_tool(session, "alternatives same_package", "jlc_find_alternatives", {
                "lcsc": "C2557",
                "same_package": True,
                "limit": 5,
            }, [no_error(), has_key("alternatives")])

            await test_tool(session, "alternatives library_type=no_fee", "jlc_find_alternatives", {
                "lcsc": "C2557",
                "library_type": "no_fee",
                "limit": 5,
            }, [no_error(), has_key("alternatives")])

            # ============================================================
            # 6. jlc_get_pinout
            # ============================================================
            print("\n--- jlc_get_pinout ---")

            await test_tool(session, "pinout STM32F103 (C8304)", "jlc_get_pinout", {
                "lcsc": "C8304",
            }, [no_error(), has_key("pins"), has_key("pin_count"),
                lambda r: "no pins" if not r.get("pins") else None])

            await test_tool(session, "pinout MOSFET AO3400A (C20917)", "jlc_get_pinout", {
                "lcsc": "C20917",
            }, [no_error(), has_key("pins"), key_eq("pin_count", 3)])

            await test_tool(session, "no lcsc/uuid returns error", "jlc_get_pinout", {
            }, [has_key("error")])

            # ============================================================
            # 7. mouser_get_part
            # ============================================================
            print("\n--- mouser_get_part ---")

            await test_tool(session, "mouser get part", "mouser_get_part", {
                "part_number": "LM358P",
            }, [
                lambda r: None if r.get("results") is not None or "API key" in r.get("error", "") else f"unexpected: {list(r.keys())}",
            ])

            # ============================================================
            # 8. digikey_get_part
            # ============================================================
            print("\n--- digikey_get_part ---")

            await test_tool(session, "digikey get part", "digikey_get_part", {
                "product_number": "LM358P",
            }, [
                lambda r: None if r.get("results") is not None or "credentials" in r.get("error", "").lower() or r.get("digikey_pn") else f"unexpected: {list(r.keys())}",
            ])

            # ============================================================
            # 9. cse_search (ComponentSearchEngine)
            # ============================================================
            print("\n--- cse_search ---")

            await test_tool(session, "CSE search", "cse_search", {
                "query": "LM358",
                "limit": 3,
            }, [no_error(), results_not_empty()])

            # ============================================================
            # 10. cse_get_kicad
            # ============================================================
            print("\n--- cse_get_kicad ---")

            r = await test_tool(session, "CSE get KiCad by query", "cse_get_kicad", {
                "query": "LM358P",
            }, [
                lambda r: None if r.get("kicad_symbol") or "error" in r else "missing kicad_symbol",
            ])
            if r.get("kicad_symbol"):
                print(f"    (got {len(r['kicad_symbol'])} chars of .kicad_sym)")
            elif r.get("error"):
                print(f"    ({r['error'][:80]})")

            # ============================================================
            # Edge cases & validation
            # ============================================================
            print("\n--- Edge cases ---")

            await test_tool(session, "query too long (>500 chars)", "jlc_search", {
                "query": "x" * 501,
            }, [has_key("error")])

            await test_tool(session, "JSON string packages param", "jlc_search", {
                "query": "resistor",
                "packages": '["0402", "0603"]',
                "limit": 5,
            }, [no_error(), results_not_empty()])

            await test_tool(session, "JSON string spec_filters", "jlc_search", {
                "subcategory_name": "MOSFETs",
                "spec_filters": '[{"name": "Vgs(th)", "op": "<", "value": "2.5V"}]',
                "limit": 5,
            }, [no_error(), results_not_empty()])

            # jlc_stock_check: invalid category name
            await test_tool(session, "API: invalid category_name", "jlc_stock_check", {
                "category_name": "FakeCategory999",
            }, [has_key("error")])

            # jlc_stock_check: invalid subcategory_name
            await test_tool(session, "API: invalid subcategory_name", "jlc_stock_check", {
                "subcategory_name": "FakeSubcategory999",
            }, [has_key("error")])

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 60)
    print(f"RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
    print("=" * 60)

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
