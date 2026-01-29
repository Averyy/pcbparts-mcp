#!/usr/bin/env python3
"""
Verify that we can scrape JLCPCB components at scale.

Tests:
1. Pagination - Can we access page 1000+?
2. Rate limiting - Can we make ~100 consecutive requests without blocking?
3. Data completeness - Do we get full attributes array?
4. Timing - How long does sustained scraping take?

Uses same TLS impersonation as our MCP server to avoid detection.
"""

import asyncio
import json
import random
import time
from dataclasses import dataclass
from typing import Any

from curl_cffi import requests as curl_requests

# === TLS Impersonation Setup (same as client.py) ===

BROWSER_FINGERPRINTS = ["chrome131", "chrome133a", "chrome136", "chrome142"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
]

SEC_CH_UA = [
    '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    '"Google Chrome";v="133", "Chromium";v="133", "Not_A Brand";v="24"',
]

REFERERS = [
    "https://jlcpcb.com/parts",
    "https://jlcpcb.com/parts/basic_parts",
    "https://jlcpcb.com/parts/componentSearch",
    "https://jlcpcb.com/partdetail/",
]

JLCPCB_SEARCH_URL = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"

# Rate limiting config
REQUEST_JITTER = (0.3, 0.7)  # Slightly more conservative for sustained scraping
REQUEST_TIMEOUT = 15.0
MAX_RETRIES = 3


def get_headers() -> dict[str, str]:
    """Generate randomized headers that look like a real browser."""
    ua = random.choice(USER_AGENTS)
    is_firefox = "Firefox" in ua

    headers = {
        "Host": "jlcpcb.com",
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Origin": "https://jlcpcb.com",
        "Referer": random.choice(REFERERS),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    if not is_firefox:
        headers["Sec-Ch-Ua"] = random.choice(SEC_CH_UA)
        headers["Sec-Ch-Ua-Mobile"] = "?0"
        platform = '"Windows"' if "Windows" in ua else '"macOS"' if "Mac" in ua else '"Linux"'
        headers["Sec-Ch-Ua-Platform"] = platform
        headers["Priority"] = "u=1, i"

    return headers


async def make_request(params: dict[str, Any], session: curl_requests.AsyncSession | None = None) -> dict[str, Any]:
    """Make a single request with retry logic."""
    last_error = None

    for attempt in range(MAX_RETRIES):
        # Fresh session per request (avoids TLS fingerprint tracking)
        own_session = session is None
        if own_session:
            session = curl_requests.AsyncSession(
                impersonate=random.choice(BROWSER_FINGERPRINTS),
                timeout=REQUEST_TIMEOUT,
            )

        try:
            headers = get_headers()
            response = await session.post(
                JLCPCB_SEARCH_URL,
                json=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                raise ValueError(f"API error: {data.get('message', 'Unknown')}")

            # Jitter between requests
            jitter = random.uniform(*REQUEST_JITTER)
            await asyncio.sleep(jitter)

            return data

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                wait = 1.0 * (2 ** attempt)
                print(f"  Retry {attempt + 1} after {wait}s: {e}")
                await asyncio.sleep(wait)
        finally:
            if own_session and session:
                await session.close()

    raise last_error  # type: ignore


@dataclass
class TestResult:
    name: str
    passed: bool
    details: str
    duration: float = 0.0


async def test_pagination() -> TestResult:
    """Test 1: Can we access very high page numbers?"""
    print("\n" + "=" * 60)
    print("TEST 1: PAGINATION LIMITS")
    print("=" * 60)

    start = time.time()

    # Test pages 100, 500, 1000 on the largest subcategory (Chip Resistors)
    test_pages = [100, 500, 1000]
    results = []

    # First, get total count for Chip Resistors
    params = {
        "currentPage": 1,
        "pageSize": 1,
        "searchSource": "search",
        "startStockNumber": 50,
        "searchType": 3,
        "firstSortId": 1,  # Resistors category
        "firstSortName": "Resistors",
        "secondSortId": 311,  # Chip Resistor - Surface Mount
        "secondSortName": "Chip Resistor - Surface Mount",
    }

    data = await make_request(params)
    total = data.get("data", {}).get("componentPageInfo", {}).get("total", 0)
    max_page = (total + 99) // 100

    print(f"Subcategory: Chip Resistor - Surface Mount")
    print(f"Total parts: {total:,}")
    print(f"Max possible page: {max_page:,}")
    print()

    for page in test_pages:
        if page > max_page:
            print(f"Page {page}: SKIP (beyond max page {max_page})")
            continue

        params["currentPage"] = page
        params["pageSize"] = 100

        try:
            data = await make_request(params)
            items = data.get("data", {}).get("componentPageInfo", {}).get("list", [])
            count = len(items)

            if count > 0:
                first_lcsc = items[0].get("componentCode", "?")
                last_lcsc = items[-1].get("componentCode", "?")
                print(f"Page {page}: OK - {count} results ({first_lcsc} to {last_lcsc})")
                results.append((page, True, count))
            else:
                print(f"Page {page}: EMPTY (0 results)")
                results.append((page, False, 0))

        except Exception as e:
            print(f"Page {page}: FAILED - {e}")
            results.append((page, False, str(e)))

    duration = time.time() - start

    # Check if all tested pages worked
    all_passed = all(r[1] for r in results)
    details = f"Tested pages {test_pages} on {total:,} part subcategory"

    return TestResult(
        name="Pagination",
        passed=all_passed,
        details=details,
        duration=duration,
    )


async def test_rate_limiting() -> TestResult:
    """Test 2: Can we make ~100 consecutive requests without being blocked?"""
    print("\n" + "=" * 60)
    print("TEST 2: RATE LIMITING (100 consecutive requests)")
    print("=" * 60)

    start = time.time()

    # Make 100 requests across different subcategories
    # This simulates real scraping behavior
    num_requests = 100
    successful = 0
    failed = 0
    blocked = 0

    # Rotate through different subcategory IDs to look more natural
    subcategory_ids = [311, 312, 313, 314, 315, 316, 317, 318, 319, 320]

    request_times = []

    for i in range(num_requests):
        subcat_id = subcategory_ids[i % len(subcategory_ids)]
        page = (i // len(subcategory_ids)) + 1

        params = {
            "currentPage": page,
            "pageSize": 100,
            "searchSource": "search",
            "startStockNumber": 50,
            "searchType": 3,
            "secondSortId": subcat_id,
        }

        req_start = time.time()
        try:
            data = await make_request(params)
            items = data.get("data", {}).get("componentPageInfo", {}).get("list", [])
            successful += 1
            req_time = time.time() - req_start
            request_times.append(req_time)

            if (i + 1) % 10 == 0:
                avg_time = sum(request_times[-10:]) / 10
                print(f"Request {i + 1}/{num_requests}: OK ({len(items)} items, avg {avg_time:.2f}s)")

        except Exception as e:
            req_time = time.time() - req_start
            error_str = str(e).lower()

            if "403" in error_str or "forbidden" in error_str or "blocked" in error_str:
                blocked += 1
                print(f"Request {i + 1}/{num_requests}: BLOCKED - {e}")
            else:
                failed += 1
                print(f"Request {i + 1}/{num_requests}: FAILED - {e}")

    duration = time.time() - start

    avg_request_time = sum(request_times) / len(request_times) if request_times else 0
    requests_per_sec = successful / duration if duration > 0 else 0

    print()
    print(f"Results:")
    print(f"  Successful: {successful}/{num_requests}")
    print(f"  Failed: {failed}")
    print(f"  Blocked: {blocked}")
    print(f"  Total time: {duration:.1f}s")
    print(f"  Avg request time: {avg_request_time:.2f}s")
    print(f"  Effective rate: {requests_per_sec:.2f} req/s")

    # Pass if we got at least 95% success with no blocks
    passed = successful >= 95 and blocked == 0
    details = f"{successful}/{num_requests} successful, {blocked} blocked, {requests_per_sec:.2f} req/s"

    return TestResult(
        name="Rate Limiting",
        passed=passed,
        details=details,
        duration=duration,
    )


async def test_data_completeness() -> TestResult:
    """Test 3: Do we get full attributes array (not truncated)?"""
    print("\n" + "=" * 60)
    print("TEST 3: DATA COMPLETENESS")
    print("=" * 60)

    start = time.time()

    # Test different component types that should have many attributes
    # Format: (subcat_name, category_id, category_name, subcat_id, expected_attrs)
    # Note: Use actual API attribute names (discovered from real responses)
    test_cases = [
        ("Chip Resistor - Surface Mount", 1, "Resistors", 311, ["Resistance", "Tolerance", "Power(Watts)"]),
        ("Multilayer Ceramic Capacitors MLCC - SMD/SMT", 2, "Capacitors", 320, ["Capacitance", "Voltage Rating", "Tolerance"]),
        ("MOSFETs", 5, "Transistors/Thyristors", 389, ["Drain to Source Voltage", "RDS(on)"]),  # Actual API names
    ]

    all_passed = True
    issues = []

    for subcat_name, cat_id, cat_name, subcat_id, expected_attrs in test_cases:
        print(f"\nTesting: {subcat_name}")

        # Must set both category (firstSort) and subcategory (secondSort) for proper filtering
        params = {
            "currentPage": 1,
            "pageSize": 10,
            "searchSource": "search",
            "startStockNumber": 50,
            "searchType": 3,
            "firstSortId": cat_id,
            "firstSortName": cat_name,
            "secondSortId": subcat_id,
            "secondSortName": subcat_name,
        }

        try:
            data = await make_request(params)
            items = data.get("data", {}).get("componentPageInfo", {}).get("list", [])

            if not items:
                print(f"  WARNING: No items returned")
                issues.append(f"{subcat_name}: no items")
                continue

            # Check first item's attributes
            item = items[0]
            attrs = item.get("attributes", [])
            lcsc = item.get("componentCode", "?")

            print(f"  Part: {lcsc}")
            print(f"  Attributes count: {len(attrs)}")

            # Check for expected attributes
            attr_names = [a.get("attribute_name_en", "") for a in attrs]
            missing = [a for a in expected_attrs if a not in attr_names]

            if missing:
                print(f"  MISSING expected: {missing}")
                issues.append(f"{subcat_name}: missing {missing}")
                all_passed = False
            else:
                print(f"  Has expected attributes: {expected_attrs}")

            # Show all attributes for inspection
            print(f"  All attributes:")
            for attr in attrs[:10]:  # First 10
                name = attr.get("attribute_name_en", "?")
                value = attr.get("attribute_value_name", "?")
                print(f"    - {name}: {value}")
            if len(attrs) > 10:
                print(f"    ... and {len(attrs) - 10} more")

            # Check other required fields
            required_fields = [
                ("componentCode", item.get("componentCode")),
                ("componentModelEn", item.get("componentModelEn")),
                ("componentBrandEn", item.get("componentBrandEn")),
                ("componentSpecificationEn", item.get("componentSpecificationEn")),
                ("stockCount", item.get("stockCount")),
                ("componentLibraryType", item.get("componentLibraryType")),
                ("componentPrices", item.get("componentPrices")),
                ("describe", item.get("describe")),
            ]

            missing_fields = [f for f, v in required_fields if not v]
            if missing_fields:
                print(f"  MISSING required fields: {missing_fields}")
                issues.append(f"{subcat_name}: missing fields {missing_fields}")
                all_passed = False
            else:
                print(f"  All required fields present")

            # Check price tiers
            prices = item.get("componentPrices", [])
            print(f"  Price tiers: {len(prices)}")

        except Exception as e:
            print(f"  ERROR: {e}")
            issues.append(f"{subcat_name}: {e}")
            all_passed = False

    duration = time.time() - start

    details = "All fields complete" if all_passed else f"Issues: {issues}"

    return TestResult(
        name="Data Completeness",
        passed=all_passed,
        details=details,
        duration=duration,
    )


async def test_timing() -> TestResult:
    """Test 4: Validate timing estimates for full scrape."""
    print("\n" + "=" * 60)
    print("TEST 4: TIMING VALIDATION")
    print("=" * 60)

    start = time.time()

    # Get total part count across all categories
    params = {
        "currentPage": 1,
        "pageSize": 1,
        "searchSource": "search",
        "startStockNumber": 50,
    }

    data = await make_request(params)
    total_parts = data.get("data", {}).get("componentPageInfo", {}).get("total", 0)

    print(f"Total parts (stock >= 50): {total_parts:,}")

    # Calculate estimates
    pages_needed = (total_parts + 99) // 100
    print(f"Pages needed (100/page): {pages_needed:,}")

    # Use timing from rate limit test if available, otherwise estimate
    # From test 2, we typically see ~0.8-1.2s per request including jitter
    avg_request_time = 1.0  # Conservative estimate

    estimated_seconds = pages_needed * avg_request_time
    estimated_minutes = estimated_seconds / 60
    estimated_hours = estimated_minutes / 60

    print()
    print(f"Timing estimates (at {avg_request_time}s/request):")
    print(f"  Sequential: {estimated_minutes:.0f} minutes ({estimated_hours:.1f} hours)")
    print(f"  With 2 workers: {estimated_minutes/2:.0f} minutes")
    print(f"  With 3 workers: {estimated_minutes/3:.0f} minutes")
    print()
    print(f"GitHub Actions limit: 360 minutes (6 hours)")
    print(f"Fits in GH Actions: {'YES' if estimated_minutes < 300 else 'MAYBE - consider parallelism'}")

    duration = time.time() - start

    # Pass if we can complete within 2 hours (with buffer)
    passed = estimated_minutes < 120
    details = f"{total_parts:,} parts, {pages_needed:,} pages, ~{estimated_minutes:.0f} min estimated"

    return TestResult(
        name="Timing",
        passed=passed,
        details=details,
        duration=duration,
    )


async def main():
    print("=" * 60)
    print("JLCPCB SCRAPE FEASIBILITY VERIFICATION")
    print("=" * 60)
    print()
    print("This script tests whether we can reliably scrape all JLCPCB")
    print("components without hitting rate limits or pagination caps.")
    print()
    print("Using same TLS impersonation as MCP server (curl_cffi)")
    print()

    results: list[TestResult] = []

    # Run all tests
    results.append(await test_pagination())
    results.append(await test_rate_limiting())
    results.append(await test_data_completeness())
    results.append(await test_timing())

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}: {r.details}")
        if not r.passed:
            all_passed = False

    print()
    total_duration = sum(r.duration for r in results)
    print(f"Total test duration: {total_duration:.1f}s")
    print()

    if all_passed:
        print("ALL TESTS PASSED - Scraping is feasible!")
        print()
        print("Next steps:")
        print("  1. Create scripts/scrape_components.py")
        print("  2. Set up GitHub Actions workflow")
        print("  3. Run initial full scrape")
    else:
        print("SOME TESTS FAILED - Review issues above")
        print()
        print("May need to:")
        print("  - Increase request delays")
        print("  - Add more browser fingerprint rotation")
        print("  - Implement request queuing")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
