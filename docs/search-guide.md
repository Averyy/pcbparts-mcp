# Search guide

How `jlc_search` reads a query, the spec filter syntax, package matching, sorting and the rules `jlc_find_alternatives` checks. AI clients get the parts they need from the tool descriptions; this page is for people who want the details. [CHANGELOG.md](../CHANGELOG.md) has the reason behind each rule.

## How a query is read

A query like `100nF 25V X7R 0402` becomes filters: the capacitance, a voltage rating of at least 25V, the dielectric and the package. Words that aren't values or package names search the part text.

**Values and units.** `u`, `µ` and `μ` all mean micro, and `Ω` is optional: `2.2µF`, `10 kΩ`, `4u7` (4.7uF, or 4.7uH in an inductor query), `6V3` (6.3V). Resistance prefixes keep their case: `10M` and `10Meg` are megaohms, `10m` and `10 milliohm` are milliohms. Package `1005` is metric for imperial `0402`.

**Comparisons in the text.** `Iq < 10uA`, `Vf < 0.3V` and `quiescent current < 10µA` keep their quantity and operator. A sign before a bare value applies to the part's main rating: `10uF capacitor < 25V` means a voltage rating under 25V.

**Values go to the spec the part type lists.**

- `5V relay` is the coil voltage; `3.3V LDO` the exact output; `12V buck converter` an output range covering 12V; `3.3V level shifter` a supply range covering 3.3V.
- `24V input 3.3V output` and `12V to 5V` set both sides of a regulator, and `Vin 24V` or `from 24V` set only the input.
- A current under 1mA in an LDO or DC-DC query is the quiescent current (`LDO 3.3V 1uA`). "Low Iq" sets no limit, so give a number.
- A resistance with an ohm unit on MOSFETs, load switches or inductors is a maximum RDS(on) or DCR (`mosfet 10mohm`). On ferrite beads and common mode filters, 1Ω or more is the impedance.
- In a MOSFET query, a voltage next to `logic level`, `GPIO` or `MCU` (up to 5V) or `gate`/`Vgs` (up to 20V) is the gate drive. Parts that list RDS(on) at or below that drive rank first. `logic level mosfet 30V` still means Vds >= 30V.
- `0.2pF ESD` is a junction capacitance of at most 0.2pF, and `5V ESD diode` a stand-off voltage of at least 5V.
- One-time fuses match the exact current rating and at least the voltage asked for. `PTC`, `polyfuse` or `resettable` (or a package only resettable fuses come in: 1812, 1210, 2920) selects resettable fuses, matched on hold current.
- Memory sizes are minimums: `ESP32-S3 module 16MB flash 8MB PSRAM` reads the module's N/R ordering code, and `microcontroller 128KB flash` the program storage size.

**Connectors** filter on pin count and pitch where the connector type lists them: every result for `JST PH 2 pin` has 2 pins at 2.0mm. Where a type rarely lists them, the value is left out and `parsed.adjusted_filters` says so. `qwiic`, `STEMMA QT` and `easyC` mean a 4-pin 1.0mm JST SH connector, `Grove` a 4-pin 2.0mm one, and footprint names like `JST_SH4_RA` give the series, pitch and count. A series name (PH, SH, XH) ranks matching parts first instead of filtering, because many connectors don't list one. Female headers take a hole layout such as `2x20`. `SMA`, `SMB` and `SMC` are coax connectors next to connector words, and diode packages otherwise.

**Colours** filter LED colour: `green` includes Emerald Green and Yellow Green, `warm white` is one shade, and `red green LED` means one part with both colours. `bicolor` alone means any two-colour part.

**Library and price words.** `basic`, `preferred` and `no fee` set the library filter; `cheapest` sorts by price. Arguments you pass (`library_type`, `sort_by`) win over query words.

**BOM wording.** `USB C`, `USBC` and `Type C` mean Type-C connectors; LED wins over diode (`red LED 0603 diode` searches LEDs); `respack` means a resistor network. CAD footprint names such as `R_0603_1608Metric` aren't part numbers: if they leave a search empty, it's retried without them.

## When part of a query can't be used

The reply always says what happened:

- `filters_applied` lists every filter that ran, and `parsed` what was read from the query text.
- `parsed.adjusted_filters` lists values moved to another spec or left out because the part type doesn't list that spec.
- `relaxed` names query words left out because nothing matched them together with the rest of the query. `relaxed.dropped_filters` lists parsed spec filters dropped when a part number was retried. With `subcategory_name` or `spec_filters` given, those words aren't left out: the reply is empty and `hint` names them and how many parts match without them.
- `ignored_filters` lists filters that couldn't be applied, or that few of these parts list.
- `unlisted` counts parts a range filter dropped only because they list no value for it (AO3401A lists no operating temperature, so a `-40°C` filter drops it).

`strict=true` turns relaxing off: every word and parsed requirement stays, and an unsupported constraint returns an error with no results.

## Spec filters

`spec_filters` takes a list of `{"name", "op", "value"}`:

```json
[{"name": "Vgs(th)", "op": "<", "value": "2V"}, {"name": "Id", "op": ">=", "value": "5A"}]
```

Operators are `=`, `>=`, `<=`, `>` and `<`. Names ignore case. A value without a unit uses the spec's base unit (V, A, ohms, F, H, Hz, W, mm or bytes). `jlc_search_help(subcategory="MOSFETs")` lists every spec a subcategory can filter or sort on, with real values. A malformed filter returns an error with `valid_values` instead of being dropped.

Short names:

| Part type | Names |
|-----------|-------|
| MOSFETs | `Vgs(th)`, `Vds`, `Id`, `Rds(on)` |
| Diodes | `Vr`, `If`, `Vf` |
| BJTs | `Vceo`, `Ic` |
| Regulators | `Vout`, `Iout`, `Quiescent Current` (`Iq`, `standby current`, `Supply Current (Iq)`) |
| ICs | `Supply Voltage` (also a level shifter's VCCA/VCCB) |
| Isolated parts | `Isolation Voltage` |
| Passives | `Capacitance`, `Resistance`, `Inductance`, `Voltage`, `Tolerance`, `Power`, `DCR`, `Isat` |
| Crystals, oscillators | `Frequency`, `Load Capacitance` |
| RF inductors | `Frequency - Self Resonant`, `Q @ Frequency` |
| ESD/TVS | `Junction Capacitance`, `Reverse Stand-Off Voltage (Vrwm)` |
| Any part | `Operating Temperature` (°C) |

**Ranges.** Supply and output voltages are often listed as ranges ("2.7V~5.5V"): `=` matches a range that includes the value, `>=` one that reaches it, `<=` one that goes down to it. Operating temperature works the same way: `<= -40` means rated down to -40°C, `>= 85` up to 85°C, and `= "-40~85"` covers both ends. In a query, `-40°C` means rated down to it and `105C` up to it. A dual-rail output (`±12V`) matches only a `±12V` filter.

**Dropout at a load.** `{"name": "Dropout", "op": "<=", "value": "0.3V@500mA"}` compares each LDO's dropout at or above 500mA (scaling a lower test current's figure up) and shows the figure used in `dropout_at_load`.

## Part types

600+ plain names map to JLCPCB subcategories, among them:

| Category | Names |
|----------|-------|
| Capacitors | `mlcc`, `ceramic capacitor`, `electrolytic`, `tantalum`, `polymer capacitor` |
| Resistors | `resistor`, `current sense resistor`, `resistor network`, `respack` |
| Inductors | `inductor`, `ferrite bead` |
| Diodes | `diode`, `schottky`, `zener`, `tvs`, `esd diode`, `rectifier` |
| MOSFETs | `mosfet`, `n-channel mosfet`, `p-channel mosfet`, `nmos`, `pmos` |
| Regulators | `ldo`, `buck`, `boost`, `buck-boost`, `dc-dc` |
| Crystals | `crystal`, `oscillator`, `tcxo` |
| Connectors | `usb-c`, `pin header`, `jst`, `terminal block`, `qwiic`, `3.5mm jack` |
| LEDs | `led`, `rgb led`, `ws2812`, `neopixel` |
| Cellular modules | `4g module`, `lte modem`, `nb-iot module`, `cat-m module` |
| Interface ICs | `level shifter`, `rs485 transceiver`, `can transceiver` |
| Drivers | `gate driver`, `motor driver`, `h-bridge`, `stepper driver`, `bldc driver` |
| Other | `mcu`, `relay`, `usb pd`, `efuse`, `fuel gauge`, `mems microphone`, `schmitt trigger` |

`inductor`, `relay`, `diode` and `motor driver` each search several subcategories. Supercapacitors aren't in JLCPCB's catalog; that search points to Mouser and DigiKey.

## Packages

A package filter includes its other spellings:

- `SOT-23` includes `SOT-23-3`, `SOT-23-3L` and `SOT-23(TO-236)`; `0603` includes metric `1608`.
- A bare family covers every body size and maker spelling: `QFN-32` also matches VQFN, WQFN, UQFN and HVQFN, `TQFP-44` matches LQFP, and `SOIC-8` matches SOP-8 and SO-8.
- A full package such as `QFN-24-EP(4x4)` keeps its body size and exposed pad across those spellings. If no catalog package has that body, the bare family is matched and `parsed.adjusted_filters` says so (not with `strict=true`).
- `packages=["0402", "0603"]`, or `in 0402 or 0603` in the query, matches either.

## Sorting and paging

`sort_by` is `stock` or `price`, or sort by a spec with `sort_spec` and `sort_order` (`asc` by default): `jlc_search(query="n-channel mosfet SOT-23", sort_spec="RDS(on)@4.5V")`. RDS(on), dropout and Vf are listed at different test conditions, so they sort at one (`RDS(on)@4.5V`, `Dropout@500mA`, `Vf@1A`) or at the condition the search already gives; without one, `sort.note` says the figures were compared as listed. `sort_order` works only with `sort_spec`. Parts that don't list the spec come last. Each row's `sort_value` is the figure it sorted on. Query words work too: `lowest Iq`, `highest Isat`, `smallest DCR`, `most flash`. Isat rankings compare catalog numbers across potentially different inductance-drop criteria and rating bases; multi-diode current rankings can mix loading conditions. A mistyped catalog figure sorts to the top, so check the datasheets of the parts you pick.

`limit` is 20 by default and up to 100; `offset` pages through the same search (`offset=20` with `limit=20` is page 2). `total` counts every match. Counts come from at most 50,000 candidates, and `counts_complete=false` says when that cap was hit.

## Alternatives

`jlc_find_alternatives(lcsc=...)` takes an LCSC code; for a manufacturer part number, look it up with `jlc_get_part(mpn=...)` first. `summary.found` counts only parts that pass the compatibility rules. Candidates missing a required match are listed separately in `unverified_alternatives` for manual comparison, and part types without rules return `similar_parts`.

The rules, for 120+ subcategories:

1. The primary value (resistance, capacitance, ...) and the required specs match. A spec that's missing or can't be read keeps the part out of `alternatives`.
2. Physical and functional identity: connector contacts, orientation and series; transistor polarity and count; battery IC function; module chip. ESP32 modules need at least the original's flash and PSRAM.
3. Ratings are the same or better, at the same test condition where one is listed (dropout, Vf, RDS(on)). A rating that's missing or can't be read doesn't disqualify a part: it goes in `specs_unparseable` for you to check.
4. Inductor Isat needs comparable inductance-drop criteria and rating bases; thermal current needs comparable temperature-rise, ambient and rating bases; DCR needs comparable published bases. Missing or differing conditions put candidates in `unverified_alternatives`. Multi-diode current comparisons need loading/thermal evidence too. Reviewed `spec_evidence` keeps document values and citations separate from catalog specs; `spec_discrepancies` flags known conflicts without changing numeric search/sort values.
5. Regulators must cover the original's input and output ranges. A single input rating proves only the maximum, so the minimum input stays unchecked. Their pinout and external parts always need checking, so their confidence is never high.
6. Basic and preferred parts rank first, then passives and crystals in the original's package. `same_package=true` keeps only that package. Each list is 10 parts by default, up to 50.

RF parts (splitters, LNAs, filters, transceivers) have no rules: `similar_parts` are ordered by how much of the original's frequency range each covers (`frequency_coverage`). Modules and other part types without rules list parts in the original's package and part family first, marked `likely_drop_in`.

A passing check means the catalog listings are compatible. It doesn't guarantee a drop-in: compare datasheets, pinouts and `package_warning`. `board_quantity` and `placements_per_board` turn `comparison.savings` into an order total, using the rounded legacy $3 Economic loading-fee estimate for each extended type added or removed; the result is not a current order quote.

## Empty searches and source scope

`why_empty` tests only supplied library/package/stock restrictions on the normalized plan, retaining the other constraints. `blocking` contains useful single changes and next calls; `tested` records counts as exact or at least. `diagnostics_complete=false` means the private diagnostic connection reached its time/work/row budget or a count was incomplete. No suggestion proves suitability; several requirements can interact. Original results stay empty and no live requests are triggered.

Snapshot rows carry `data_source` and their observation time. Live lookups preserve their observed timestamp while cached. A local MPN miss is not proof the part is absent from JLCPCB: its `next_call` describes a live check with `min_stock=0`, which runs only if the caller executes it.

Negative Vout requirements compare signed outputs, including unsigned catalog magnitudes labelled Negative. `Impedance @ Frequency` with `@` requires the listed frequency too; numeric comparisons apply to impedance at that condition. Unsupported part-number exclusions return an error instead of a positive match.

Savings retain the rounded legacy $3 Economic loading-fee estimate with explicit machine-readable assumptions; they are not current order quotes and do not calculate Standard-service fees.
