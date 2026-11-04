# Changelog

Notable changes to PCB Parts MCP, newest first. The hosted server at pcbparts.dev always runs the latest version.

Versions follow semver. While the project is in beta (0.x), a minor release such as 0.7.0 can change replies; its **Breaking** section lists what to check. Patch releases don't change tool names, arguments or reply fields, except where noted. Entries before 0.6.0 are brief; the commit history has the details.

## 0.8.11 (2026-11-04)

New reply fields, all optional. One value changes: the neighborhood summary's `pin_count`.

### Fixed

- **`board_get` names a part's unconnected pins:** focus on the DT1042-04 on SparkFun's Thing Plus ESP32-S3 showed 4 of its 6 pins, so its two spare channels, left unconnected, looked the same as pins the extraction had dropped, and checking took the full netlist. A focused part now has `pin_count`, its own pin count, and `nc_pins`, its pins on no net by pad (`{"I/O1": "1", "I/O2": "3"}`; `{}` when every pin is connected). They come from each board's footprints (KiCad, PADS) or symbols (Eagle): 5,438 parts on 285 boards, 95% of the ICs on boards with a netlist, 1,735 of them with NC pins. Eagle supply pins join the net of their name without a wire, so they're never listed as NC; footprint pads that aren't pins (a mounting tab outside the symbol, an unplated hole, a PADS terminal with no copper) don't count.
- **Neighborhood `pin_count`** in the `board_get` summary is the part's own pin count where known (the DT1042-04: 6), not its pins in the netlist (4).
- **Board parser:** `openpyxl` is in the dev dependencies; re-parsing an Espressif board failed without it (it reads their BOM spreadsheets). `parse_boards.py --pins` adds the pin fields to existing board files from the cached sources without re-parsing them, so hand fixes stay.

## 0.8.10 (2026-11-04)

### Fixed

- **`jlc_get_part` datasheet and specs from LCSC when JLCPCB lists none:** YY-0807RGBJ26-07-FJ (C54796803) came back with `datasheet: null`, no specs and a note to find the datasheet on the maker's site, while LCSC's page linked a 14-page datasheet and listed its rise and fall times. JLCPCB lists no datasheet for about 18% of parts, and LCSC had one for 9 of 12 sampled. When JLCPCB has neither a PDF nor a maker link, or no specs, the part's LCSC product data fills `datasheet_pdf` (LCSC's PDF, linked directly since it doesn't expire) and an empty `specs`, and `datasheet_note` / `specs_note` say they're LCSC's. It's one LCSC request per part per hour at most, and the reply is as before when LCSC doesn't answer.
- **Inductor DCR and Current Rating:** LCSC lists the typical DCR on some inductors and the maximum on others (Bourns SRP4020TA-1R0M: 27 mOhm, its maximum; 22 typical), and an inductor's Current Rating is usually its Irms for a temperature rise (5 A at 40 C there; Isat is 8.5 A), with neither labelled. `jlc_get_part`'s `specs_note` for inductors says so, and DCR sorts say to compare the datasheets' max columns.

## 0.8.9 (2026-11-04)

### Fixed

- **`board_get` consensus for a partial focus:** 0.8.8's ESP32-S3-DevKitM-1 made ESP32-S3-MINI-1 a two-board consensus, which then replaced the 33-board ESP32 one that `focus="ESP32"` on Adafruit's ESP32-S3 Feather returned. A partial focus now uses its family's consensus when the exact part's covers fewer than 3 boards and the family's covers more. Exact and ref focus are unchanged.

## 0.8.8 (2026-11-04)

New boards and reply fields, all optional.

### Added

- **Espressif's own DevKits as reference boards:** ESP32-S3-DevKitC-1 v1.1, ESP32-S3-DevKitM-1 and ESP32-DevKitC V4 (ESP32-WROOM-32D), from the reference-design ZIPs Espressif publishes (a PADS layout and a BOM spreadsheet; the board parser reads both now). `board_search(org="Espressif")` found nothing, and "what does Espressif do" for native USB, ESD, the CHIP_PU RC and auto-reset fell back to reading schematic PDFs. Parts the schematic marks not fitted say so in their description. The links point to Espressif's download; the ZIPs state no license, and only the parts and connections are kept.
- **`pin_nets` in `board_get` focus:** each pin's net. Numbered pins (an ESP32 module's, a KiCad pad's) now say what they are: on the S3 DevKitC-1 the module's pin 3 is CHIP_PU and 27 is GPIO0.

### Fixed

- **ZIP-download boards' links and makers:** the Raspberry Pi CM4/CM5 IO boards and Seeed's XIAO ESP32-S3 Sense linked to github.com pages that don't exist (`https://github.com/rpi-cm4io`), and their org read "Rpi-cm4io", so `org="Raspberry Pi"` missed them. They now link the maker's download and list as Raspberry Pi and Seeed Studio.

### Design rules

- **ESP32 USB and reset, from Espressif's DevKits:** one LESD5D5.0CT1G (5 V, 15 pF) on each of VBUS, D- and D+ per USB port and nothing on CC; the ESP32-C6-DevKitC-1 v1.4's two USB-C ports with 5.1 kohm Rd, SBU unconnected, shell to GND through 0 ohm and Schottky OR-ing into 5 V (from its schematic, which is published only as a PDF); and the DevKits' 10 kohm + 1 uF on CHIP_PU with an unfitted 0.1 uF beside it.

## 0.8.7 (2026-11-04)

Nothing existing changes shape.

### Added

- **Sort by gate charge:** `sort_spec="Gate Charge"` (or `Qg`, or "lowest gate charge" in a query). 0.8.5 refused it as unlisted, but 30,000 MOSFETs list it as "Gate Charge(Qg)"; the database read only "Total Gate Charge(Qg)", so its column was empty. Listings give it at different gate voltages, and `sort.note` says so.

### Fixed

- **MOSFET RDS(on) and Vgs(th) mix typical and maximum figures:** LCSC takes them from different datasheet columns on different listings. AO3401A lists 47 mΩ at 10 V (its 4.5 V typical) and its 4.5 V and 2.5 V maxima, while HL3415A lists typicals, so a gate-drive ranking put HL3415A 2.1x ahead at 2.5 V when max against max it's 1.5x; LBSS84LT1G's Vgs(th) is the maximum and AO3401A's the typical. `jlc_get_part` adds a `specs_note` for MOSFETs saying so, and that the Vgs rating is on about a third of listings and gate leakage on none; RDS(on) sorts and the `jlc_search` description say to compare the datasheets' max columns. The figures themselves are LCSC's.

## 0.8.6 (2026-11-04)

New reply fields, all optional. One count changes meaning: see Changed.

### Added

- **`board_get` focus on any part:** `focus="J1"` answered "IC 'J1' not found on this board", though the description said a ref works, so the only way to see a USB-C receptacle's CC resistors, ESD parts and VBUS path was the 100 KB+ netlist. Focus now takes any part's ref (`J1`, `D2`) or words in its value, description or footprint (`USB-C`, `USB`, `Type-C` find the receptacle; connectors come first), and builds its pin neighborhood from the netlist. A focus that matches nothing lists `available_refs` (connectors, diodes, switches and the like) beside `available_ics`.
- **Ground and supply pins in focus:** `power_pins` gives each pin on a ground or supply rail its net, with the net's parts when there are few (VBUS through a diode) or `part_count` when there are many (GND). IC neighborhoods left these out, so a focused ESD array showed no GND pin. `pins_in_nets` counts the part's pins in the netlist, so a pin in neither `pins` nor `power_pins` is in no net: the DT1042-04 on SparkFun's Thing Plus ESP32-S3 shows 4 of its 6 pins, and I/O1 and I/O2 are left unconnected.

### Changed

- **`pin_count` in `board_get` neighborhood summaries** now counts the IC's pins in the netlist, ground and supply included. It counted only pins with a signal connection, plus a `_decoupling` group that isn't a pin, so the DT1042-04 above showed 3.

### Design rules

- **USB-C CC protection:** the rule said a CC TVS needs VRWM <= 5 V. CC1/CC2 sit next to VBUS in the receptacle and can short to it directly, and non-compliant adapters start at 20 V even into a 5 V-only port, so TI requires CC protection at least 22 V DC tolerant (TPD2S300 datasheet 7.1). A 5.5 V clamp survives VBUS through a cable's 56 kohm but fails on a direct short. The rule now says to use a 24 V clamp (ESD752, ESD2CAN24) or a short-to-VBUS protector (TPD2S300, TPD4S311), never a spare channel of the D+/D- array, and that a sink with only Rd on CC needs none, as on the ESP32-S3 reference boards. The ESD rule's ESD441 line said the same 5.5 V part suits SBU; TI's pick there is ESD341.
- **USB-C sink CC windows:** the figures were right, but they're the Type-C R2.5 Table 4-36 worked example for a ±10% Rd, not fixed limits. The rule now says so, gives the threshold bands (0.613-0.745 V and 1.165-1.368 V, disconnect below 0.276 V) and Table 4-28's 2.04 V / 2.18 V pin maximums, and notes the older R1.x table with fixed 0.66 V and 1.23 V thresholds. Its "0.20 V Ra/Rd threshold" is now the R2.5 band where a source sets it (0.144-0.271 V).

## 0.8.5 (2026-11-03)

New arguments and reply fields, all optional; nothing existing changes shape.

### Added

- **Sort `jlc_search` by a spec:** `sort_spec` (`sort_by="spec"` is implied) and `sort_order` (`asc`, the default, or `desc`). "Lowest Iq 3.3V LDO", "lowest RDS(on) in SOT-23" and "highest Isat 4.7 µH" couldn't be answered by stock or price order. Parts that don't list the spec come last, then library tier and stock break ties. Each row's `sort_value` is the figure it was sorted on, as listed with its test condition, and `sort` says what was compared. 34 specs sort, from RDS(on), Iq, dropout, Vf, Isat, DCR, ESR, GBW and crystal ppm to flash, RAM and CPU speed; `jlc_search_help(subcategory=...)` marks them with `sort_spec`. Ranges (supply or adjustable output voltage, Vgs(th)) and figures the catalog lists in mixed units (slew rate in V/µs, V/ms and V/ns) are refused with the reason. A listed 0 (38 parts list "0uA" Iq) counts as not listed.
- **Sorting at a test condition:** RDS(on), dropout and Vf are listed at different conditions (`9.8mΩ@10V`, `180mV@(300mA)`, `450mV@300mA`), so a plain sort compares a 10 V figure with a 2.5 V one. `RDS(on)@4.5V` uses the figure listed at the highest gate voltage at or below the drive, `Dropout@500mA` the figure listed at or above the load (or a lower one scaled up linearly, leaving out parts rated below it), and `Vf@1A` the figure listed at 1 A or more. Without one, the condition comes from the search when it has one (the query's gate drive, a Dropout filter's load, an Output Current or If filter), and otherwise `sort.note` says the order is the catalog figures', not a like-for-like comparison.
- **Sort words in queries:** `lowest Iq`, `highest Isat`, `smallest DCR`, `tightest tolerance`, `most flash` and `longest life` sort by that spec, and `parsed.detected.sort` says so. They used to stay in the searched words, find nothing and be dropped. When no match lists the spec ("lowest ESR 100uF capacitor" searches MLCCs), `sort.note` says so and names the part types that list it.

## 0.8.4 (2026-11-03)

New arguments and reply fields, all optional; nothing existing changes shape.

### Added

- **`pcba_type` on parts, and a `jlc_search` filter:** JLCPCB's PCBA Type, `economic` (its Economic and Standard assembly both place the part) or `standard_only`. One Standard-only part moves the whole order to Standard assembly, with its higher setup, stencil and fixture fees, and it can't be predicted from family, maker or MSL: Espressif's ESP32-S3 modules are Standard only, the bare S3 chips and DOIT's ESPS3-32E modules aren't. A design was costed on Economic fees for two days before its MCU module turned out to be Standard only. It's on `jlc_get_part`, stock-check, search and alternatives rows, and `jlc_search(pcba_type="economic")` keeps only parts Economic assembly takes. Search rows get it with the next daily parts update.
- **`no_datasheet` on search rows:** `true` when JLCPCB lists no datasheet for the part (a fifth of WiFi modules and addressable LEDs, mostly newer listings), so it's seen before a lookup.
- **`jlc_get_pinout(lcsc, footprint=true)`:** the EasyEDA footprint's name, the document it was drawn from, pad count, pitch, pad sizes and every pad's position, size, layer and hole. A slide switch's pins with numbers only (SK13D07VG4) can then be matched to the datasheet drawing, and a footprint drawn for another part shows: SIM7080G-M's is named for 72 pads, has 77, and links a SIM7020G document. It reads the footprint from the same EasyEDA endpoint as the symbol, not the rate-limited one.
- **LDO dropout at a load:** `{"name": "Dropout", "op": "<=", "value": "0.3V@500mA"}`. LDOs list dropout at their own test current (`180mV@(300mA)`, `1.1V@(800mA)`), so a plain `<= 0.3V` compared parts at different loads and put a 25 mV at 1 mA part first. The filter uses a figure listed at or above the load, or scales a lower one up linearly, leaves out parts rated below the load, and `dropout_at_load` shows which figure was used.
- **`summary.extended_examples` in `jlc_find_alternatives`:** with `library_type="no_fee"` and no basic or preferred match, the reply named only a count of extended matches (C13564: 23). It now lists the best three and says to rerun with `library_type="extended"` for the rest. Listed alternatives also carry `has_easyeda_footprint` where the footprint store already knows it, without an EasyEDA request, and the score breakdown no longer shows `easyeda: 0` for parts that weren't checked.
- **What a listing leaves out, in `specs_note`:** an inductor's Isat is the maker's own definition (the inductance drop it's measured at, typical or minimum); class II MLCC capacitance is the value at 0 V and drops under DC bias; an RF cable's listing doesn't say whether each end is a bulkhead or PCB-mount, jack or plug, SMA or RP-SMA. The tool descriptions also say that lifecycle (NRND, obsolete) comes from `mouser_get_part` or `digikey_get_part`.

### Fixed

- **Schmitt-trigger logic:** `schmitt trigger logic` with `library_type="no_fee"` found nothing, though the basic 74HC14D is a Schmitt inverter. `schmitt trigger`, `schmitt logic` or `schmitt IC` now search Inverters, Logic Gates and Buffers by their Schmitt-trigger input type (half the Logic Gates don't say it in their descriptions); `schmitt inverter` and `schmitt buffer` search their own part type. A gate type still means Logic Gates.

### Design rules

- **ESP32 eFuses:** burn them with the eFuse supply at 3.3 V or less (VDD3P3_CPU on S3/C3, VDDPST2 on C6), per each datasheet's Table 5-2 note, even though the chips run up to 3.6 V.
- **ESP32 reset RC:** 10 kohm/1 uF on CHIP_PU only covers a 3V3 rail that rises in under about 7 ms; a soft-started regulator needs a bigger RC, its power-good, or a supervisor. The rule had said the RC "ensures" the startup delay. Adds the formula: tau >= 1.65 * ((2.8 V / V_final) * T_ramp + 50 us).
- **DFM:** JLCPCB's published limits (trace and space, drills, vias, annular rings, clearances, silkscreen, mask), the no-surcharge via size, and the JLC04161H-7628 and -3313 4-layer stackups with layer thicknesses and Er. `jlc stackup` and `efuse` find these.

## 0.8.3 (2026-11-02)

### Fixed

- **`power mux`:** returned signal multiplexers. `power mux`, `power multiplexer`, `power path switch` and `power selector` now search like `ideal diode`: ORing controllers (where LCSC files TPS2121 and LM66100) and the ideal diodes among load switches.
- **Connector orientation:** `JST ZH ... SMD right angle` dropped "right angle" (JST's descriptions don't say it) and listed a vertical header first. In connector searches, `right angle`, `horizontal`, `side entry`, `vertical`, `straight` and `top entry` rank parts whose `Mounting Type` says so first, ahead of the maker and series preferences. Parts that don't state an orientation stay in the results, and the words still narrow the search where descriptions have them.
- **A pitch without "mm":** `female header 2.54` read the 2 as a pin count and dropped ".54". Common pitches (2.54, 1.27, 2.0 and others) written bare in a connector search are the pitch.
- **A query naming another part type than the subcategory given:** `addressable RGB LED` with `subcategory_id=71` (discrete LEDs) returned the whole subcategory with no explanation. `parsed.detected.not_searched` now says the words name RGB LEDs(Built-in IC), not the subcategory given. A generic word in the same family (`capacitor` with Tantalum Capacitors) isn't noted.
- **ESP32 chips:** `ESP32-S3 chip QFN` returned modules, and the four S3 chips are filed under three part types (one as a WiFi Module). `chip`, `SoC`, `IC` or `QFN` beside an ESP32 part number now searches QFN packages in every part type.
- **`jlc_stock_check` with a part-number fragment:** `2812` found only capacitors in a 2812 case, because JLCPCB matches whole part numbers and their starts. When no result contains the fragment, `hint` names in-stock parts that do (WS2812B-2020-V6, XL-5050RGBC-2812B).
- **Busy datasheet links:** "try again in a minute" now says how many seconds (also in `Retry-After` and `retry_after`), that the limit is 20 new links a minute for all users, and that a `datasheet_pdf` link `jlc_get_part` returned in the last 25 minutes opens without using one.
- **`maker_datasheet` for TI part-number links:** 0.8.2 turned TI's `lit/gpn/<part>` links into `lit/ds/symlink/<part>.pdf`, which is a 404 when the datasheet has another name (LM73100's is `lm7310.pdf`). They're now TI's English `lit/gpn/<part>` link, which redirects to the right PDF.

## 0.8.2 (2026-11-02)

### Added

- **`maker_datasheet` in `jlc_get_part`:** the manufacturer's own datasheet where JLCPCB lists one, mostly TI parts. TPS61023DRLR (C919459) had no datasheet link at all; it now gets `https://www.ti.com/lit/ds/symlink/tps61023.pdf`. TI links are rewritten to that stable English form. With no PDF of either kind, `datasheet_note` says so; with no specs, `specs_note` does.
- **`not_found` in `mouser_get_part`:** the part numbers in a batch that no result matches. Mouser leaves them out without a word, so in a batch of 10 a missing part looked checked. The docstring also says a number can match another maker's part (Mouser's SRV05-4 is onsemi's).
- **`most_stocked` in `jlc_search`'s `unlisted`:** up to three of the parts a filter left out for listing no value, by LCSC code and model, so they can be checked by hand (several WS2812 variants list no supply voltage).

### Fixed

- **"NAND" in a logic query:** `74HC132 quad NAND schmitt` searched NAND flash, and `quad NAND gate` returned flash chips. With gate words (gate, schmitt, quad, dual, hex, 2-input) or a 74/4000-series part number, NAND, NOR and XOR mean Logic Gates, and the gate type, gate count, inputs per gate and Schmitt inputs become filters. `NAND flash`, `SLC NAND` and `quad SPI NOR flash` are unchanged.
- **Switch circuits:** `Circuit = DP3T` found 5 slide switches; `Double pole triple throw` found 443. JLCPCB writes the same circuit several ways (SPDT, 1P2T, "Double pole triple throw", "triple-pole/single-throw"), and the filter now compares poles and throws. In switch searches, `2P3T` or `double pole double throw` in the query becomes the filter instead of being dropped. SPST-NO and SPST-NC still match only parts that say so.
- **OVP load switches:** `OVP load switch` dropped "OVP" and returned high-side USB switches. In load-switch searches, OVP, reverse current blocking, reverse voltage protection, soft-start and output discharge are matched against the parts' Features (WS3222D's description says it only in Chinese), and `OVP switch` finds load switches.
- **Two values for one supply range:** `OVP switch 28V input ... 5V` matched only parts listing exactly "5V". Two values for a supply range now each have to fall inside it. Fixes a related bug: a second filter of the same name and operator was dropped, so the result depended on their order.
- **Parts with no specs** (7% of stocked parts) follow documented ones on stock-ordered searches. JMEconn's SK23D07 (C56164084: 5,000 in stock, no specs, datasheet or footprint) led its search. Price-sorted searches are unchanged.
- **`jlc_find_alternatives` for part types without compatibility rules:** only the original maker's parts were searched. Every maker's parts in the original's package now come next, after part-family matches (Maxinmicro's MX22917 for the TPS22917, TUOZHAN's 2020 RGB LED for the WS2812B-2020); a maker's copy that carries the original's number (XL-2020RGBC-WS2812B) counts as a family match. Packages that only say "SMD" don't count.
- **The empty-tier hint:** "No basic part matches; 16 parts do in other library tiers (extended parts add an assembly fee)" when one of the 16 was a Preferred part with no fee. The hint now gives the no-fee count apart and points to `library_type="no_fee"`.
- **Words left out silently:** a hyphenated maker name beside a part number (`ESP32-S3 Ai-Thinker`) was dropped without a `not_searched` note, and a second part number (`WS2812 SK6812`) was reported as a stray word. The note now names it as a part number to search separately.
- **`get_design_rules` keys:** the keys the index prints (`guides/dfm.md`, with or without backticks) found nothing and returned the whole index.
- **Design rule text:** ESP32 boot buttons wired through 10 kohm against a 10 kohm pull-up can't enter download mode (the pin sits at VDD/2, above VIL max); the rule now says to wire the button straight to GND. USB series resistors on ESP32s are footprints to reserve, as Espressif's checklist says, not required parts. Semtech's SRV05-4 is 3 pF typical, not 0.85 pF, and the JLC parts sold as SRV05-4 are copies with their own figures.
- **Downtime during deploys:** the deploy stopped the server before downloading the new image, so calls in that window got an empty 502 (`Error POSTing to endpoint:` in MCP clients, and from `/mcp/datasheet/<lcsc>`). The image is now pulled first and the container swapped after.

## 0.8.1 (2026-11-02)

### Fixed

- **A colour beside a part number:** `NE555 red`, `TP4056 blue module` and `STM32F103C8T6 blue pill` found nothing. The colour became an LED colour filter (`Illumination Color`) on every part, and the hint said the part wasn't in stock. Without an LED part type the colour is now listed in `parsed.detected.not_searched`; `KT-0603R red LED` keeps it. When a part number is in stock but the filters beside it match nothing (`NE555 0201`), the hint says so rather than pointing to `jlc_stock_check`.
- **`jlc_get_pinout` on multi-unit symbols:** MIMXRT1052CVL5B (BGA-196) returned "missing pin data", because EasyEDA keeps such a symbol's pins in its units. All 196 pins come back now, with BGA balls in order (A1, A2 ... A10, B1).
- **Connector alternatives and mounting:** audio jacks, RF coax, IDC and circular connectors and jumpers don't list `Mounting Type`, so it was never checked and every candidate was unverified. The SMD PJ-320D jack was offered the through-hole PJ-320A-4P first. When the original lists no mounting type, the one read from the package (SMD or Plugin) is compared. Audio jacks must also have the same contacts (`Rank Number`: TS, TRS, TRRS), so a 3-contact jack isn't offered for a headset (TRRS) one.
- **NTC thermistor alternatives:** only the 25/100°C B constant was compared, and only 190 stocked NTCs list it (1,114 list 25/50°C). A 10k B3950 thermistor (MF52A103F3950, 25/50°C only) had no verified alternative, and B3435 parts ranked beside B3950 ones. The first temperature pair both parts list is compared now; C13879 gets five B3950 parts.
- **A part number filed under another part type:** `WS2812B LED` found 18 of the 19 WS2812B parts. It left out WS2812B-V6 (C52917433, 122k in stock), which JLCPCB files as an indicator LED. When a part number is found under the named part type, its parts in other subcategories of the same category join the search, and `parsed.subcategories` lists them.
- **Cell counts:** `2S lithium battery charger` left out `2S` and listed single-cell TP4056 chargers first. `1S` to `8S` are cell counts in battery part searches.
- **`board_get` part numbers on PowerFeather PowerUPS:** its design files put Mouser order numbers in the MPN field (`187-CL21A226MAYNNNE`, `595-BQ25622RYKR`), and they came back as `mpn`. They're `mouser` now, and the one DigiKey number `digikey`.
- **`M4` in a query:** M4, M7 and M8 were read as diode packages (SMA, SMB) in every query, so `ARM Cortex M4 microcontroller` searched SMA microcontrollers and found nothing. They're packages only beside a diode word (`M7 diode`, `schottky M4`).
- **Dual-rail outputs listed as two values:** TRACO's TMR 3-2422WI (`-12V、+12V`) still met `Output Voltage = 12V` and was missed by `±12V`. A pair with the plus written, or on an isolated module listing two outputs, is a ±12V rail. On a non-isolated regulator, `-12V、12V` (K7812-500R3) is still one output that can be wired either way.
- **Metric threads:** `M2 standoff SMT` also found an M2.5 nut.
- **`single supply` with op amps and comparators:** the words were reported as left out. They now mean a part listing a single-supply range (NE5532 lists none); a voltage beside them is matched against that range, as before.
- **`get_design_rules`:** `brown-out` found nothing. `brown-out`, `brownout` and `reset IC` now find the voltage supervisor rules.
- **`mounting_type`:** about 2,400 stocked parts were `not_sure`: SMD parts in LCC, TOLL, PowerPAK, PowerDI, SC-70, SC-59, WLP, DO-221 and similar packages, and through-hole ones in P600, TO-46 and GBL/GBP/KBJ.
- **Package warnings in alternatives:** BQ25620RYKR (`WQFN-18`) was a "Different package" from BQ25622ERYKR (`WQFN-18(3x2.5)`), though it's the same package listed without its body size. The warning now says only the size is missing.

## 0.8.0 (2026-11-02)

### Breaking

- **`datasheet_pdf` is a short, stable link** (`jlc_get_part`, and `original` in `jlc_find_alternatives`): `https://pcbparts.dev/mcp/datasheet/C15127` redirects to a freshly signed PDF on each visit, so it can be kept in a BOM. It was JLCPCB's 1.2KB signed link, valid for 30 minutes; `datasheet_pdf_expires` is gone.
- **`attributes` removed** from the same replies: it repeated `specs`. C15127's reply went from 3,272 to 1,395 bytes.

### Added

- **`/mcp/datasheet/<lcsc>`:** redirects to the part's datasheet PDF (404 if JLCPCB has none). Held links are reused; a new one takes one JLCPCB request, never EasyEDA, and the server signs at most 20 a minute for all callers (429 beyond that).
- **Operating temperature filter:** `Operating Temperature` takes range operators in °C in `spec_filters` (`<= -40` is rated down to -40°C, `= "-40~85"` covers both ends), under every spelling of the attribute. `-40°C`, `105C` and `-40~85℃` in a query do the same.
- **`unlisted` in `jlc_search`:** per range filter, how many parts meet every other constraint but list no value for it, and an empty reply's hint names them. AO3401A was silently left out of a -40°C MOSFET search because LCSC lists its temperature as "-", as for about 16% of MOSFETs.
- **`likely_drop_in` in `jlc_find_alternatives`:** for part types without compatibility rules, parts in the original's package and part family come first (the SIM7080G for the SIM7080G-M; it ranked behind a 24x24mm module).
- **Isolated parts and power modules:** `isolated` picks the isolated part type (DC-DC, RS-485, CAN, I2C, SPI, USB, ADCs, gate drivers, amplifiers), `DC-DC module`, `AC-DC module` and `power module` search the module types, and `3kV` is an isolation rating. `isolated DC-DC module 5V input 12V output 2W` searched 2,083 non-isolated ICs.
- **More query words:** supervisors (a bare voltage is the threshold), common mode chokes, standoffs and SMT nuts, chargers, comparators, multiplexers, LoRa, cell counts, audio amp class and power, relay current, op amp single supply, ideal diodes, `ESP32-C3 module`, and nA currents (2,843 parts listing an nA quiescent current were missing from every Iq filter).
- **Seven reference boards:** Adafruit QT Py ESP32-S3, SparkFun Thing Plus ESP32-S3, Seeed XIAO ESP32-S3 Sense, PowerFeather PowerUPS, Botletics SIM7000 shield, Adafruit BQ24074 solar charger and SparkFun Sunny Buddy, with a `cellular` tag.
- **Part numbers in `board_get`:** components and a focused IC carry the design files' own `mpn`, `manufacturer`, `lcsc`, `mouser` and `digikey` (121 boards), which the build dropped, so agents guessed parts from values like "MBR540 / SOD-123".
- **`offset` in `jlc_search`:** pages through the rest of a search. Agents copied `page=` from `jlc_stock_check` and got a validation error.
- **Board search hints:** an empty `board_search` names the words no board matches and what leaving them out finds (`ESP32-S3 battery solar` came back empty with no hint), and an unknown `board_get` slug adds `did_you_mean` (`adafruit-feather-esp32s3` → `adafruit-esp32-s3-feather`).

### Changed

- **`jlc_stock_check`** lists the most stock first unless `sort_by` is given. JLCPCB orders by LCSC code, which put SMF18A's top Preferred part on page 2.
- **A part type the search doesn't know:** `gizmo 3.3V 2A` dropped "gizmo" and returned XH connectors. Words are now dropped only when the query names a known part type; otherwise the reply is empty, with a hint.

### Fixed

- **`jlc_get_pinout` pin numbers and names:** numbers came from a hidden symbol field, so SIM7080G had 58 of 77 pins numbered `0` and XC6206P332MR had VIN and VOUT swapped; names were lost on RP2040 and on BGA parts. A `note` flags symbols whose pin names are just numbers.
- **`mounting_type`:** 1,034 SMD parts were `through_hole` or `not_sure` (through-hole patterns matched inside names like `VQFN-HR` and `SMBF`).
- **LEDs:** `addressable RGB LED` searched plain RGB LEDs, `WS2812B LED` found 1 of 19 parts, and `LED driver` searched indicator LEDs. A colour now covers its shades (`green LED` with `library_type="no_fee"` found nothing: the only Basic green LED is listed as Emerald Green), and two colours or `bicolor`/`tricolor` mean one multi-colour part (`Illumination Color = Red + Green`, also in `spec_filters`).
- **Audio jack sizes:** 2.5, 3.5, 4.4 and 6.35mm were read as pin pitch; they now filter `Connector Type`. Jacks sharing a footprint can number pads differently, so alternatives list pin roles as unchecked and the pinout note says so.
- **Cellular modules:** `4G module` returned ESP32 WiFi modules and `Cat-M1 module` nothing. Cellular words search 2G/3G/4G/5G Modules, a network word (Cat-M, NB-IoT, Cat.1, GSM, GPRS) must be in `Communication System`, and replies note that LCSC's band lists are often incomplete.
- **Any-word searches** rank parts matching more of the words first, not by stock alone.
- **Empty basic, preferred or no-fee replies** say how many parts match in the other tiers; a part number found only there no longer reads as out of stock.
- **Two range filters on one listed attribute** must hold for the same item (a dual supervisor listing `2.93V、4.55V` matched a 3.3-3.5V window).
- **Dual-rail outputs:** `Output Voltage = 12V` no longer matches ±12V modules; `±12V` does.
- **Battery charger alternatives** must cover the original's input range and interfaces (BQ25622E was offered IP2312U first).
- **Query values:** bare inductances (`10u`, `2R2`), the current in a slash-separated BOM line, sub-1Ω ferrite and choke values (DCR), and `jst 4 pin sh` matching `jst sh 4 pin`.
- **`jlc_search_help`:** a range's `max` was the highest low end; operating temperature is now numeric.
- **`parsed`:** `parsed.subcategory` names the given subcategory, and unsearched words beside a part number are listed in `parsed.detected.not_searched`.
- **`sensor_recommend` measures:** the BM25S2621 soil probe no longer lists `humidity`, nor the BMM150 magnetometer `sound`; the PMWCS3 soil probe measures `soil_moisture` and `conductivity` (it listed only `temperature`), and the CY8CMBR3102 also `touch`.
- **`get_design_rules` lookups:** only file names matched, so `lipo`, `type-c`, `pull-up`, `rs485`, `stm32g0` and `strapping pins` found nothing (16% of calls did). Common terms and part-number prefixes now find their file, and other topics return the files that discuss them most, with a `note`.
- **SMA in RF cables and antennas:** `SMA IPEX` in RF Cables searched the SMA diode package and found nothing, and `IPEX to SMA cable` searched coax connectors. In RF Cables and Antennas, SMA, IPEX and U.FL name the connector, and a cable or pigtail word with an RF connector searches RF Cables.
- **USB design rule:** the HRO TYPE-C-31-M-12 has 16 contacts on 12 pads, and the Rd and Rp tolerances now follow the spec (Rd ±10%; Rp 56k ±20%, 22k and 10k ±5%).
- **Reference boards:** 52 boards' `key_coverage` and 25 descriptions or key ICs named parts the boards don't have (the Olimex ESP32-EVB said MCP2562; it has a SIT1050T), and boards sharing a repo got the last one's coverage. Also a misread board outline, cut-off descriptions, a wrong tag, and sub-sheets in git submodules now parsed.

## 0.7.8 (2026-11-01)

### Added

- **Datasheet PDF in `jlc_get_part`:** `datasheet_pdf` links the datasheet as a PDF on JLCPCB's storage, with `datasheet_pdf_expires` (about 30 minutes after the call). `datasheet`, LCSC's link, opens a viewer page rather than the file, and some parts have none: GP2S+ (C3155018) listed an empty datasheet while JLCPCB has its Mini-Circuits datasheet. A part served from the hour-long cache is fetched again when its link has under five minutes left.
- **RF frequency coverage in `jlc_find_alternatives`:** RF parts have no compatibility rules and came back as similar parts ranked by stock, maker and price, from the original's maker only. For BP2G1+ (C7459223, 1.2-2 GHz), 3 of 10 were 5 MHz-1 GHz CATV splitters or a 2.8-3.7 GHz one. RF similar parts (splitters, baluns, couplers, LNAs and other amplifiers, attenuators, detectors, filters, transceivers) now come from every maker in the subcategory, ordered by how much of the original's frequency range they cover: `frequency_coverage` is `full`, `partial` (with `share`) or `unknown` (no range listed). Parts that don't overlap it are left out, and `summary.frequency_check` counts each. BP2G1+ now gets ten parts covering 1.2-2 GHz from three makers.
- **Numeric RF inductor and ESD filters:** `Frequency - Self Resonant` and `Q @ Frequency` (listed for about 90% of Inductors (SMD)) and `Junction Capacitance` (ESD/TVS) take `>=`, `<=` and ranges in `spec_filters`; `Junction Capacitance <= 0.5pF` was ignored as not numeric. A part listing two junction capacitances (`0.3pF、0.6pF`) is compared by the larger.

### Fixed

- **`preferred` in `jlc_search`:** it was true for every basic part, so C1671, C14663 and C8218 were `preferred: true` in a search and `preferred: false` in `jlc_get_part`. It now means JLCPCB's Preferred flag in both, as `library_type` already showed; `library_type` says whether a part has an assembly fee. **Reply change:** basic parts in search results now have `preferred: false`.
- **`lcsc_url` in `jlc_get_part`:** null for parts LCSC lists but JLCPCB's API leaves without a link (MPD1020W2D21, C52139901); it's built from the LCSC code now. An empty `datasheet` is null rather than an empty string.
- **ESD and TVS values in a query:** `0.2pF ESD` filtered on `Capacitance`, which no ESD part lists, so the value was dropped and SMB TVS diodes came first. A capacitance there is now `Junction Capacitance <=` the value (566 parts for 0.2pF), and a voltage after `esd` is the stand-off voltage (Vrwm), as it already was after `tvs`. With `subcategory_name` set to the ESD subcategory, a bare `0.2pF` or `5V` is read the same way.
- **SMA connectors read as diode packages:** `SMA edge mount connector` and `SMA female right angle through hole 50 ohm` with `subcategory_name="Coaxial Connectors (RF)"` searched the SMA (DO-214AC) diode package and found nothing. SMA, SMB and SMC are the coax series when the query has connector words (connector, jack, plug, female, male, edge mount and similar) and no diode words, or the given subcategory is a connector one; `SMA schottky diode` and `TVS SMA` keep the package. The series filter also matches parts listing several (`SMA、FAKRA`), and SMB, SMC, SMP and TNC are recognized.
- **Words that zero a search with your own subcategory or filters:** those words aren't left out automatically, so a search could return nothing with only a generic hint. The hint now names the words and says how many parts match without them (`"diode RF low capacitance"`: 2,178 ESD parts under 0.5pF).

- **Holtek (Best Modules) sensors in `sensor_recommend`:**
  - **Datasheet links:** all 85 modules linked the same file, Best Modules' module catalog. Each now links its own datasheet. BMCOM modules link the datasheet of the Best Modules sensor they're built on, or else their user's guide. A datasheet for a single part on the module comes last: the sound detector would have linked its op-amp's (LMV324) and the TDS module its probe's, and modules built on a VEML7700, VL53L1X, AMG8833, MPU-6050 or STK3337 link their user's guide, the module's own document.
  - **Temperature:** 24 modules listed `temperature` only because their pages give an operating temperature or mention temperature compensation. It's now listed only where the module reports a temperature reading, checked against the datasheets: 12 keep it, 12 lose it. The HT7M21xx and BM22S402x PIR modules, the BMA26M221, the BM62S2201 pressure sensor and the BM62S5601 oxygen/flow sensor keep it. Radar, CO2, smoke, proximity and the other PIR modules lose it. The BM25S4021 TDS sensor gains it, and the BM62S3202 water level sensor now measures `level` as well.
  - **Measures:** pages that named nothing the scraper knew were listed as measuring `gas`. The two air velocity modules now measure `wind` and `flow`, as the FS3000 does; the two 24-bit ADC modules measure `voltage`, the MPU-6050 shake detection module `vibration` and the AMG8833 IR array `ir_temperature`. The others aren't sensors and are gone: a radar demo board and a roller-shutter motor obstruction module (a servo and the "Development Tools" page were already kept out). Keywords now match whole words, so `light` no longer comes from "time of flight", "slightly" or "lighting control", nor `particulate` from "dustproof", and operating humidity, usage notes and related-product links no longer count. 15 modules lose a measure they don't take: `light`, `humidity`, `pressure`, `flow`, `particulate`, `motion`, `gas` on the BM42S2022 thermopile, and `distance` on the ultrasonic oxygen sensor. The BM42S2022 now measures `ir_temperature`, the pH module and the BME63M001 TDS module `temperature`, and the BM25S2621 soil probe `soil_moisture`.
  - **Interfaces:** they now come from a module's features list and summary, not the whole page, which also holds comparison tables, pin tables and wiring notes. 15 modules lose `analog`, which came from mentions of their internal ADC; the BMH23M001 loses `spi`, which is its sibling BMH23M002's; the BM25S2621 soil probe is RS485 only, and its adapter kit, the BME34K262A, UART only. Hand-entered interfaces that contradicted the pages and datasheets are gone: the BM42S3021 thermocouple and BME26M301 air velocity modules are I2C only, not UART; the BME34M101 soil moisture module is UART only, not I2C or SPI; the BME63M001 is UART only, not I2C. The BM25S2021, BME33M251 and BME33M251A list `one_wire` (the BME33M251 listed UART instead). 12 modules whose pages write I²C with a superscript weren't listed as I2C, 9 of them with `Interface: I2C (address: ...)`. The HT7M21xx modules now list I2C and GPIO, as their datasheet gives.
  - **Sensing type:** the three infrared thermometer modules are `thermopile`, not `pyroelectric`; the BM42S3021 is `thermocouple`, not `thermopile`; the 24-bit ADC modules are `adc`, not `semiconductor`. The BM32S2021 and BMS33M332 infrared proximity modules, the BM25S4221 turbidity module and the BMH83M101A oximeter are `photodiode` (they were `capacitive`, `pyroelectric`, `pyroelectric` and `optical`).
  - **Supply voltage:** the features lists of the BM25S4421, BM42P782-N1 and BME63M001 weren't read, and three oximeter modules had usage notes read in place of their features. All six now list a supply voltage. The BME63M001 showed 1.71-3.6V, from a table that took BME part numbers for Bosch sensors; it runs on 3.3-5.5V.
  - **Descriptions:** HTML codes no longer appear in descriptions (`50&mu;A` is now `50μA`), and formulas and units stay joined (`C2H5OH`, `μg/m3`). Descriptions no longer pick up packing lists, usage notes or the MCU and application-note links under a page's Resources.

## 0.7.7 (2026-11-01)

### Fixed

- **Sensors that drop out of one scrape:** a sensor missing from a source's latest scrape now stays in `sensor_recommend` until three scrapes in a row miss it; new sensors are still added at once. A rerun of the sensor scrape on 2026-11-01 lost Holtek's HT7M2126, HT7M2127, HT7M2136, HT7M2156 and HT7M2176 PIR modules, because the Best Modules listing left them out for that run while their product pages were still up. They're back. A source whose scrape finds nothing also keeps its last data now, instead of an empty list going out with the next deploy.

## 0.7.6 (2026-11-01)

### Fixed

- **Parts tied on stock or price:** parts with the same stock (or the same price, with `sort_by="price"`) came back in no fixed order. `USB C` and `USB-C connector` listed the same 3,587 connectors in a different order, and which tied parts made the `limit` could change from one spelling to the next. Ties are now ordered by LCSC code in `jlc_search`, in `jlc_get_part(mpn=...)` matches, and in the candidates `jlc_find_alternatives` checks.

## 0.7.5 (2026-11-01)

### Fixed

- **CircuitPython sensor refresh:** the monthly sensor scrape on 2026-11-01 couldn't read the CircuitPython driver list. docs.circuitpython.org answered GitHub's build server with a Cloudflare challenge, so that source kept October's data and the scrape's deploy was held back. The list now comes from the Adafruit bundle's `docs/drivers.rst` on GitHub, the file the docs page is built from, and gives the same 126 sensors. Sensors CircuitPython lists outside its sensor sections, such as MPR121 under IO Expansion and EMC2101 under Motor Helpers, are kept on purpose now; before, a parsing accident kept them.

## 0.7.4 (2026-10-30)

### Fixed

- **LCSC codes in a search:** `jlc_search(query="C2040")` returned RP2040 plus resistors whose LCSC codes start with C2040 (C20400 to C20409). A query of LCSC codes alone now matches those codes exactly. A part number that looks like a code still matches (`C1815` returns 2SC1815 transistors as well as the capacitor C1815), and a reference designator in a BOM line (`C1 100nF 0402`) searches as before.
- **Height on electrolytics:** `Height` filters also read `Height - Seated (Max)`, which some electrolytics list instead. `Height <= 5.4mm` on SMD electrolytics found 1,421 of the 1,429 parts, with a warning that few parts list Height; it now finds all of them without the warning.
- **Digital potentiometers and ideal diode controllers:** `digital potentiometer 10k I2C` returned mechanical trimpots, and `ideal diode controller 12V` returned 1N4148-type switching diodes. `digital potentiometer`, `digipot`, `ideal diode` and `ORing controller` now search Digital Potentiometers and ORing Controllers, and a digital potentiometer's resistance is matched.
- **Female headers:** `1x8 female header` ranked 1x4 and 1x6 headers first, because the layout was matched against the pin headers' Pin Structure. Female headers list it as Holes Structure, which `1x8` and `2x20` now filter.
- **Barrel jacks:** the plug size in `5.5x2.1mm barrel jack` was dropped without a word. JLCPCB lists a jack's contact diameters, not the plug it takes (a jack for a 5.5x2.1mm plug lists a 6.4mm outside contact and a 2mm pin), so the size can't be searched, and `parsed.detected.not_searched` now says so.
- **Comparison signs:** `10uF capacitor < 25V` searched Voltage Rating >= 25V, and `mosfet Vds < 30V` Vds >= 30V. A sign written before a value now keeps its direction when it points against the default, also before a value written with µ or Ω (`< 10µF`). That includes values matched exactly before: `zener < 5.1V` now means under 5.1V, not exactly 5.1V, and `resistor 10k < 1%` a tolerance under 1%. The sign also carries over when a value moves to the spec a part type lists: `high side switch < 4A` searched Maximum Continuous Current >= 4A. `>50V` still means >= 50V.
- **Microamps on a regulator:** `LDO 3.3V 1uA` and `LDO 3.3V < 1uA` searched Output Current >= 1µA, which every LDO passes, so AMS1117 came first. No LDO or DC-DC converter lists an output current under 1mA, so a current under 1mA in an LDO or DC-DC query now means quiescent current at most that value (`LDO 3.3V 1uA` returns XC6206-type parts). `LDO 3.3V 500mA` is still output current.
- **Milliohms on MOSFETs, load switches and inductors:** `mosfet 10mohm`, `load switch 50mohm` and `inductor 10uH 100mohm` left the value out, because these parts don't list Resistance. On a part type that lists RDS(on) or DCR instead, a resistance written with an ohm unit (`10mohm`, `10mΩ`, `0.1ohm`) now means RDS(on) or DCR at most that value, or the written comparison (`mosfet < 10mΩ`). Without the unit it's still left out: in an inductor query, `1m` may be 1mH and `1R0` 1.0µH. On ferrite beads and common mode filters, which list DCR too, a value of 1Ω or more is the impedance, as `ferrite bead 600ohm` already searched; that now also applies when the part type is passed as `subcategory_name`.
- **`jlc_stock_check(library_type="no_fee")` paging:** from page 2 on, about half the basic and half the preferred parts were never returned. Each page now continues both lists where the previous page stopped, and `total_pages` and `has_more` follow both lists. A page can be shorter than `limit` once one list runs out.
- A search whose database query failed returned a generic internal error instead of "Search failed: query too complex. Reduce the number of filters."

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
