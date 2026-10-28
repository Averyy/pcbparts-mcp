# Changelog

Notable changes to PCB Parts MCP, newest first. The hosted server at pcbparts.dev always runs the latest version.

Versions follow semver. While the project is in beta (0.x), a minor release such as 0.7.0 can change replies; its **Breaking** section lists what to check. Patch releases don't change tool names, arguments or reply fields, except where noted. Entries before 0.6.0 are brief; the commit history has the details.

## 0.7.3 (2026-10-28)

### Fixed

- **LCSC codes passed as `mpn`:** `jlc_get_part(mpn="C2040")` returned RP2040 plus resistors whose LCSC codes start with C2040. An LCSC code that's in the catalog now returns only that part, with `match: "lcsc"` and a note pointing to `jlc_get_part(lcsc=...)`. A part number that looks like a code still wins: `C1815` returns 2SC1815 transistors, not the capacitor LCSC C1815. A code that isn't in the catalog no longer matches other parts' codes, and the hint suggests the live `lcsc` lookup.
- **BOM placeholders:** `jlc_get_part(mpn="N/A")` returned JST connectors whose part numbers end in -N-A, and `NC`, `NF`, `NP`, `TBD` and `DNF` returned other unrelated parts. Placeholders now find nothing, with a hint to search by value and package.
- **Parts numbered after another maker's part:** when `ICM-42688-P` finds only `ICM-42688-P(TOKMAS)`, the note now says that part is made by another manufacturer (Tokmas) and to check its datasheet before substituting. This applies to any part whose number ends in its maker's name or initials, such as UMW's `MAX3485ESA(UMW)`, lingxingic's `INA180A1IDBVR(LX)` and XBLW's; packing codes such as `(LF)(SN)` don't count.
- **CAD footprint names in a search:** `KMR2 BTN_KMR2 switch` found nothing because `BTN_KMR2` was treated as a part number and required text. Footprint names (`BTN_`, `SW_`, `R_`, `LED_` and similar prefixes) are no longer part numbers, and a search they leave empty is retried without them (`relaxed.dropped_text` names them): it now finds the 12 KMR2 tactile switches. `strict=true` doesn't retry.
- **Resistor packs:** `10kohm RESPACK resistor` returned single chip resistors. `respack` and `resistor pack` now mean resistor networks, as `resistor array` already did.

## 0.7.2 (2026-10-28)

### Fixed

- **Part numbers spelled differently**: `jlc_get_part(mpn=...)` finds the part when the spelling differs from JLCPCB's. Of 971 part numbers from the reference boards that found nothing, about 150 now find the part:
  - dashes, spaces, underscores or slashes: `ERJ-2RKF2702X` → `ERJ2RKF2702X`, `104031-0811` → `1040310811`
  - another reel or packing code from the same manufacturer: `AD8630ARZ-REEL7` → `AD8630ARZ`, `TPS562208DDCT` → `TPS562208DDCR`, `RC0603FR-1015KL` → `RC0603FR-0715KL`
  - ordering names: `VL53L0X` → `VL53L0CXV0DH/1`, `SCD-41` → `SCD41-D-R2`
  - BOM notes and alternatives: `TL074 OP AMP`, `AMC1301 or AMC1302`, `MCU-STM32F407VGT6`

  Packing codes match only within the same manufacturer, and a different temperature or performance grade is never substituted. Lookups that already found parts return the same parts.
- `NRF24L01+` no longer includes the non-plus NRF24L01.
- **Full part numbers in a search:** `jlc_search` used to search only the family of a part number it shortened, by stock, so `LM1117-3.3` listed adjustable and 5V parts in its top five, `AMS1117-3.3` put AMS1117-5.0 second, and `BC817-40` came back with BC817-16 and -25. Now the parts with that full part number come first, then parts that keep all of its suffixes (`LM1117IMPX-3.3/NOPB`), then the rest of the family. The total and the family results are unchanged.
- **Connectors:** pin or contact count and pitch in a query are now filters. `USB-C 16 pin connector` returned 6-contact parts, `JST PH 2 pin` returned 1.25mm 4-pin parts, and `qwiic connector` returned a 3.96mm VH part; now every result has the requested count and pitch. Qwiic, STEMMA QT, easyC and Grove supply their pitch and pin count. A series (PH, SH, XH) ranks matching parts first instead of hiding the half of connectors that don't list a series, and a query that says JST ranks JST's own parts first, with compatible parts from other makers after them. Where a part type rarely lists the count or pitch, the value is left out and reported in `parsed.adjusted_filters`.
- **Packages:** a full package keeps its body size and exposed pad. `package="QFN-24-EP(4x4)"` returned 3.5x5.5mm bodies first, because only `QFN-24` reached the VQFN/WQFN/TQFN spellings; now every result is a 4x4 body with an exposed pad. `4x4mm`, `4.0x4.0` and a rotated `5.5x3.5` spell the same body. If no part in the catalog uses the requested body, the family is matched and `parsed.adjusted_filters` says so. A bare family name (`QFN-32`) matches any body, also covers ST's UFQFPN and NXP's HVQFN spellings, and says so in `parsed.adjusted_filters`; `STM32G0 QFN-32` found nothing and now finds the UFQFPN-32 parts.
- **Fuses:** the current in a fuse search was dropped: fuses were matched on `Hold Current`, which only resettable fuses list, so `15A fuse` returned 3.15A and 500mA fuses first. One-time fuses now match the exact current rating (a 20A fuse doesn't protect a 15A circuit; `500mA` matches 0.5A) and a voltage rating at least the one asked for, using each fuse type's own attribute names. PTC, polyfuse, polyswitch or resettable anywhere in the query selects resettable fuses, which keep matching Hold Current at or above the value. A part-number search that moves to another fuse type uses that type's attributes, and `filters_applied` names the type each filter applies to.
  - A fuse search in a package that only resettable fuses come in (1812, 1210, 2920) searches resettable fuses, and `parsed.adjusted_filters` says so. `1812 fuse` and `1A 1812 fuse` found nothing; `2920` is now read as a package.
  - `fuses` means the same as `fuse`. `1A 1812 fuses` returned ferrite beads.
- **Words copied from a BOM line:** `red LED 0603 diode` and `LED1 0603 diode` returned 1N4148 switching diodes; LED now wins over diode, and the red color filter applies. `USB C`, `USBC`, `Type C` and `typec` select Type-C connectors (`USB C` returned a USB-UART chip first, `Type C receptacle` nothing). JST footprint names such as `JST_SH4_RA` and `JSTPH2_BATT` supply the series, pitch and pin count.
- **USB PD controllers:** `USB-C PD controller sink 20V 3A` returned USB-C connectors, and `PD sink` found nothing. PD with controller, sink, source or trigger now means a USB PD controller, even next to USB-C. Sink and trigger queries rank receiver controllers first and source queries supply controllers; a sink voltage ranks parts that can negotiate it (`20V` matches `5V、9V、12V、15V、20V`) instead of filtering the chip's supply voltage. Most PD parts don't list their role, so these rank rather than filter, and `parsed.adjusted_filters` says so.
- **Logic-level MOSFETs:** in `logic level n-channel mosfet 3.3V 5A`, the 3.3V became a `Vds >= 3.3V` filter, and nothing checked how the parts behave at a 3.3V gate drive. A voltage next to a gate cue is now the gate drive: up to 5V with logic level, GPIO or MCU, up to 20V with gate or Vgs. Other voltages stay drain voltage, so `logic level mosfet 30V` still means Vds >= 30V. Parts that list RDS(on) at or below that gate voltage come first; the rest stay in the results, since many good parts list RDS(on) only at 4.5V or 10V.

### Added

- `mpn_match` on each result and `mpn_matches` counts on `jlc_search` replies whose part number was shortened.
- `rds_on_at_drive` on MOSFET results when the query gives a gate drive: the listed RDS(on) at the highest gate voltage at or below it, or null when RDS(on) is only listed at higher gate voltages.
- `match` and `matched_mpn` on MPN replies that aren't exact matches. `related` replies (full-text matches) add a `note` naming the part types returned: `SSD1306` returns an OLED display and power inductors.

### Self-hosting

Rebuild `data/components.db` (`.venv/bin/python scripts/build_database.py`) for fast separator-insensitive MPN lookups, connector filters and MOSFET gate-drive ranking. An older database gives the same answers more slowly and logs a warning.

## 0.7.1 (2026-10-27)

### Fixed

- **Dimensions:** Height and Diameter range filters recover electrolytics whose dimensions are recorded only in the package string. Capped scans still report partial counts.
- **Part numbers:** a part number in a search is never relaxed away. `UWT1H220MCL 25V capacitor` used to drop the part number and return 100nF MLCCs. Now, when the part number isn't listed under the part type its words suggest, every part type is searched, and only parts whose MPN matches it are returned. That's UWT1H220MCL6GS here; `SMBJ18CA diode` and `BLM18AG102SH1D 0603 inductor` work the same way. If none match, the reply is empty with a hint naming the part number, instead of unrelated parts.
  - A token counts as a part number when it has 6+ letters and digits and isn't a package name (`SOT-416`, `LQFP-48`), a standard (`AEC-Q100`) or a BOM reference designator (`R1`, `LED1`). Shorter part numbers (LM358, BAV99) count when the parser recognizes them as a model.
  - The retry may drop parsed spec filters only for such a full part number.
  - Explicit arguments, a caller's subcategory and strict mode are never overridden.
- **Empty replies:** MPN lookup misses and empty searches give a next step for search help, constraints or low-stock parts. MPN error text and usage-stat outcomes are unchanged.

### Added

- `hint` on empty search replies and MPN lookup misses, with a suggested next step.
- `relaxed.dropped_filters` lists parsed spec filters omitted by a part-number retry.

### CI

- Daily component scrapes stop before commit and deploy if the part count drops more than 5%. A manual `allow_part_drop` input permits deliberate drops.
- Workflows use the Node 24 releases of their actions: checkout and setup-python v7, and the Docker login, metadata, Buildx and build-push actions.

## 0.7.0 (2026-10-27)

Fixes from a user-perspective review: about 20 searches that found nothing or the wrong parts, alternatives that weren't real replacements, and replies an assistant had to guess at.

### Breaking

- `jlc_search` returns 20 results by default, down from 50. An explicit `limit` still goes up to 100.
- `price_10` is removed; it wasn't the price at quantity 10. Use the quantity tiers in `prices`.
- `total_per_unit` is removed from alternatives savings, since it mixed a one-time fee with a unit price. Savings now use order quantity and placements per board.
- Part replies omit `description` when `specs` is nonempty.
- Invalid argument values return an error with `valid_values` instead of being ignored. This applies to:
  - `library_type`, `sort_by`
  - malformed `spec_filters`, `packages` and `manufacturers`
  - board, sensor and design-rule enums

  Obvious spellings and case are normalized first.
- Resistance prefixes are case-sensitive: `1M` is a megohm and `1m` a milliohm. Resistance matches are exact, so a 1 MΩ search no longer includes 990 kΩ or 1.01 MΩ parts, and alternatives don't count them as verified.
- In a query, `64Mb`-style sizes are megabits, `64MB` megabytes, and all-lowercase `64mb` megabytes.
- `board_get` consensus `count` and `pct` count boards instead of components, so `pct` never exceeds 100%.
- Usage stats (`/mcp/stats`) add the outcome `similar_only`: alternatives that returned comparison candidates but no verified replacement. Earlier days are unchanged.
- Self-hosting: `docker-compose.yml` publishes port 8080 on `127.0.0.1` only. To reach the server from other machines, change the mapping to `"8080:8080"`.

### Added

- `strict` argument on `jlc_search`. With `strict=true` a search never relaxes, and it returns an error when a constraint can't be applied.
- New reply fields:

  | Field | Meaning |
  |---|---|
  | `unverified_alternatives` | candidates missing a spec needed to verify them |
  | `counts_complete` | `false` when library counts come from a capped scan |
  | `valid_values` | accepted values, on argument errors |
  | `relaxed.dropped_part_type` | a part type the search dropped (see Fixed) |
  | consensus `boards` and `quantities` | which boards support a pin choice, and how many of the part each uses |

- Library and price words in a query set the defaults and are reported in `parsed`: "basic", "preferred" and "no assembly fee" set the library; "cheapest" sorts by price.
- "0402 or 0603" is an OR package constraint.
- New part-type aliases: USB PD, eFuse, fuel gauge, MEMS microphone, polymer capacitor. A supercapacitor search says JLCPCB doesn't stock them and points to Mouser/DigiKey.
- Tool descriptions and the server instructions explain the reply fields and the usual workflow.

### Fixed

- **Megohms read as milliohms** ([#17](https://github.com/Averyy/pcbparts-mcp/issues/17)): `1M resistor`, `1Mohm` and `1M ohm` searches, and `spec_filters` values such as `1MOhm`, returned 1 mΩ resistors or nothing. The parser checked for "mohm" after lowercasing, so `1MOhm` became 1 mΩ.
- **Values:** `1M`, `4u7`, `6V3`, `µF`/`μF`/`Ω`, bare farads and metric `1005` sizes parse. Part numbers such as `AMS1117-3V3` and `ESP-12F` are left alone.
- **Part types:**
  - Crystal capacitance means load capacitance.
  - Motor driver, h-bridge, stepper and BLDC searches find motor drivers.
  - Buck-boost converters stay buck-boost.
  - Level-shifter direction and VCCA/VCCB apply to the right side.
  - Through-hole resistors and electrolytics find through-hole parts.
- **Voltage and current:** "input up to 24V" sets the input, not a second output. Quiescent and standby current searches compare the right spec.
- **Memory sizes** apply to the MCU or module instead of selecting NOR flash. ESP32 N/R codes give flash and PSRAM size; N without R means no PSRAM.
- **Part numbers:** one with no match under its query's part type (`FUSB302B USB PD`) is searched across all part types, and the reply says so in `relaxed`.
- **Filter reporting:** explicit filters on attributes a part type rarely or never lists are reported in `ignored_filters`, with suggested real names; matching is unchanged. `Gate Threshold` works like `Vgs(th)`.
- **Counts:** `library_type_counts` and `no_fee_available` follow every constraint.
- **Alternatives:** candidates must match where it matters:
  - connectors: contact count, mounting and series
  - battery ICs: function
  - modules: chip and at least the original's memory
  - regulators: both ends of the input/output ranges

  Passives and crystals rank the original's package first.
- MPN lookups are fast (LM358 went from about 700 ms to under 1 ms), and slow searches no longer hold up other requests or `/health`.
- Sensor searches with two names for the same measure ("heart rate" + "blood oxygen") work. Design-rule keys returned by the tool can be passed back. Recovery hints name tools that exist.

### Self-hosting

The server logs a warning if `data/components.db` was built by an older version. Rebuild it with `.venv/bin/python scripts/build_database.py` to get fast MPN lookups and complete quiescent-current matches. Docker images build it fresh.

## 0.6.6 (2026-10-17)

- CSE searches and KiCad files are kept across restarts in a SQLite store (`CSE_STORE_PATH`, on the cache volume). Uncached searches take 11–15 s; cached ones about 55 ms.

## 0.6.5 (2026-10-17)

- `jlc_find_alternatives` uses real candidates from the local database. It checks:
  - transistor polarity
  - MOSFET gate threshold
  - TVS polarity and type
  - module chip
  - RF connector series

  It also compares dropout, Vf and RDS(on) at matching test conditions.
- `jlc_search` relaxes words that found nothing (`relaxed`), reports unapplied filters (`ignored_filters`, `parsed.adjusted_filters`), and `total` counts what the search matches.

## 0.6.4 (2026-10-17)

- Usage stats split each tool's calls into outcomes that add up, and add totals and calls per UTC hour. The `/mcp/stats` JSON changed shape.

## 0.6.3 (2026-10-17)

- Shorter, more accurate tool descriptions: the tool list is about 15% smaller.
- `mouser_get_part` checks batches of up to 10 parts.
- DigiKey requests are spaced to 5 a second, and "not found" answers are cached for 10 minutes.
- Anonymous daily usage stats at `/mcp/stats`.

## 0.6.2 (2026-10-16)

- Mouser is paused when it refuses for its limit (a 403 with `TooManyRequests`), instead of being called again.

## 0.6.1 (2026-10-16)

- Mouser and DigiKey request counts and pauses survive restarts (`DISTRIBUTOR_QUOTA_PATH`). The limit errors suggest self-hosting with your own key.

## 0.6.0 (2026-10-16)

- EasyEDA footprint answers are seeded for 397,062 parts and kept across restarts on the `pcbparts-cache` volume. `/health` reports `easyeda_footprints`.
- `jlc_get_pinout` follows a part's new symbol when EasyEDA has one.
- The Docker image shrank from about 3.2 GB to 1.8 GB. Building it needs BuildKit.
- Self-hosting: a `components.db` from before 0.6.0 has no footprint seed; rebuild it.

## 0.5.x (July–October 2026)

- **0.5.6:** EasyEDA footprint checks stay under EasyEDA's rate limit, with one request each and a pause after a block.
- **0.5.5:** Linux and Windows unit-test CI; PR Docker builds fixed.
- **0.5.4:** Windows fixes for design rules, database builds and scrapers.
- **0.5.3:** `mouser_get_part` returns `unit_weight_g`.
- **0.5.2:** Sensor scrapes no longer hang on a slow site; wafer 0.4.6.
- **0.5.1:** Height and Diameter range filters; `jlc_search_help` sorts numeric values.
- **0.5.0:** A hardening release:
  - error masking, host and origin allowlists, limit and list caps, request body limit
  - atomic database builds and a gate on the sensor scrape pipeline
  - exact dependency pins
  - a `jlc_get_part` crash on parts without prices fixed

## 0.4.x (February–March 2026)

- **0.4.5:** KiCad 10 boards.
- **0.4.4:** Board neighborhoods keep ICs that were filtered out as passives; board data fixes.
- **0.4.3:** `get_design_rules`: 41 curated PCB design reference files.
- **0.4.2:** `sensor_recommend`: 1,500+ sensor ICs across 56 measure types.
- **0.4.1:** Longer CSE timeout, configurable.
- **0.4.0:** HTTP moved from curl_cffi to wafer-py. Version numbers restarted at 0.4.0 here.

## Before 0.4.0 (January–February 2026)

Released as a JLCPCB MCP server, versions 1.0.0 to 3.1.0:

- **1.x:**
  - JLCPCB part search
  - EasyEDA footprint availability (1.6)
  - BOM tools (1.7)
  - `get_pinout` (1.8)
  - spec-aware alternatives (1.10)
- **2.0:** local SQLite database with parametric search.
- **2.4:** Mouser, DigiKey, CSE and MPN lookup.
- **3.0:** renamed to PCB Parts MCP.
- **3.1:** stock history and FastMCP 3.0.
