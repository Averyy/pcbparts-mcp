# Changelog

Notable changes to PCB Parts MCP, newest first.

Versions follow semver. While the project is in beta (0.x), a minor release such as 0.7.0 can change replies; its **Breaking** section lists what to check. Patch releases don't change tool names, arguments or reply fields, except where noted. Entries before 0.6.0 are brief; the commit history has the details. From 0.8.21 each version is also a GitHub release, tagged `vX.Y.Z`, with its entry as the notes.

## 0.9.1 (2026-11-13)

Changed replies: `jlc_search` for part numbers that end in R, k or M. Self-hosters: a new `HTTP_HOST` setting.

- A part number that ends in a unit letter is searched as a part number. `jlc_search("9774025151R")` read the Würth spacer's number as a 9.77 GΩ resistance, searched chip resistors and found nothing; with `strict=true` it returned an error. A value now has at most 4 significant digits before a one-letter unit (`1000R`, `4R75` and `4k7` are unchanged, and spelled-out units such as `12345 ohm` are always a resistance). The search finds C7496631.
- The new `HTTP_HOST` setting chooses the address the server listens on: `127.0.0.1` or `::1` keeps it on this machine, `::` listens on every IPv6 interface, and a specific address listens only there. The default stays `0.0.0.0`, every IPv4 interface, which also lets other machines on the network connect to a server run from source. An empty value counts as unset. In Docker keep `0.0.0.0`: `docker-compose.yml` already publishes the port on 127.0.0.1 only. Contributed by @plaes in #23.

## 0.9.0 (2026-11-12)

Changed replies: `sensor_recommend` (every record re-checked: voltages against makers' datasheets, descriptions, identities, measures), `get_design_rules` (33 files audited, 5 new topics), `board_get` data on 295 boards, `board_search` ranking and tags, `jlc_get_pinout` on some multi-unit symbols, `jlc_find_alternatives` with `library_type` and `has_easyeda_footprint`, `cse_search` and `cse_get_kicad`, and holder searches. Snapshot prices in `jlc_search` and `jlc_get_part(mpn=...)` are refreshed weekly, given as `prices_as_of`. New tool: `jlc_stock_history`. `/mcp/stats` gains fields. Self-hosters building from source: the catalog moved to `data/catalog/`.

### Breaking

- The catalog snapshot's prices are refreshed weekly; stock stays daily. `jlc_search` results and `jlc_get_part(mpn=...)` matches show the 1-piece price from the latest weekly refresh, and their replies add `prices_as_of` next to `data_as_of`. A part listed since that refresh has the price it was first scraped with. Prices barely move day to day: of 340,172 price changes between the 2026-11-09 and 2026-11-10 scrapes, 261,362 were under 0.05%, and storing them cost the repository 2.3 MB a day. `jlc_get_part(lcsc=...)` and `jlc_stock_check` are still live.
- The committed catalog moved from `data/categories/*.jsonl.gz` to `data/catalog/`: one uncompressed file per subcategory with each part's fields except stock and price, sorted by LCSC code, plus `stock.tsv` and `prices.tsv` for every part. Git stores only the rows that change, so a daily data commit adds about 1 MB instead of about 25 MB (the repository had grown to 6.75 GB, 6.6 GB of it old catalog copies). The old copies stay in the history, so existing clones and forks keep pulling as before; the README now clones with `--depth 1`, about 80 MB instead of about 7 GB. `scripts/build_database.py` reads the new layout and builds the same database; anything else that read `data/categories/` needs updating.

- Calculated CO2 is no longer listed under `measure="co2"`: ENS160, SGP30, iAQ-Core and APC1 moved to `eco2`, because their makers say the value is estimated from VOC, hydrogen or ethanol signals. BME680 and BME688 note that Bosch's BSEC library calculates IAQ and CO2 equivalent on the host (the separate BSEC software records left the catalog, below). Real CO2 sensors stay, and SEN6x stays with a note that only SEN63C, SEN66 and SEN69C have a CO2 sensor.
- ENS160 is no longer listed under humidity, pressure or temperature: it only takes humidity and temperature as compensation inputs, and the pressure tag came from the BME280 on a SparkFun combo board.
- ENS160, ENS161 and the ScioSense ENS16x library record list `voltage` 1.71-1.98V, the chips' VDD. They listed 1.71-3.6V or 1.8-3.6V, which is the separate VDDIO range, so a 3.3V supply read from the old value would exceed the 1.98V maximum.
- 23 records that aren't sensors left `sensor_recommend`, each checked against its maker's or project's documentation: `number` (an ESPHome platform tagged with 13 measures), ESPHome software and appliance integrations, a USB PD controller, a stepper driver, I/O expanders, an analog mux, an RF transceiver, ion generators, and a `co2` record that merged several unrelated libraries.
- SM300D2 moved from `co2` to `eco2`: its parameter table says the CO2 and formaldehyde outputs are equivalent values of TVOC. Its maker is now Generic (it was credited to Amphenol, with no source) and its `voltage` 4.8-5.2V.
- iAQ-Core lists `voltage` 3.2-3.4V (ams datasheet: 3.3V ±0.1V); it listed 3.0-5.5V, so a 5V supply looked safe. MAX32664 lists VDD 1.71-3.63V (was 1.8-3.3V).
- ADCs stay in `sensor_recommend` but appear only under what they measure. General-purpose ADCs (AD7194, ADS122C04, MCP3427, TLA2021, ADC128D818, ADS1258) are listed under `voltage`. They are no longer under sound, weight or force, which came from library text saying "low noise", "Iowa Scaled Engineering" and "PGA/FSR". Load-cell, thermocouple, RTD and ECG front ends (HX711, NAU7802, MAX31855, MAX31865, ADS1292R) keep their measures.
- MAX32664 sensor hubs are no longer typed photodiode or listed under acceleration, and carry a `capability_note` naming the front end each version needs. MAX30001 and MAX30003 ECG front ends are typed `adc` instead of photodiode.
- Records for different parts are no longer merged. `sensor_recommend` merged 109 part names into another part's record, and 77 of those were in use, so a part showed another's datasheet, supply range or measures: MH-Z19 carried MH-Z14A's datasheet, MPU6500 had MPU6050's supply range, LSM9DS0 had LSM9DS1's 1.9V minimum (ST: 2.4V), six different ST IMUs (LSM6DS3, DSL, DSO, DSR, DSV16X, DSV16BX) were one LSM6DSOX record, DS18S20 was DS18B20, and MAX30105, a smoke-detection part, put particulate on MAX30101. Each is now its own record, with its own voltage from the maker's datasheet where one was checked and none otherwise; family records (SHT3x, SCD4x, BME68x) no longer absorb concrete models. 27 names that really are the same device (AM2302 for DHT22 and the like) stay merged; every decision and its evidence is in `data/sensors/ic_alias_evidence.json`.
- Every sensor record's supply voltage (all 1,701) was reviewed against its maker's datasheet or product page, and 782 of those 0.8.24 also had differ, including 171 that 0.8.24 left empty (BMA456, ICM-42688-P, ZED-F9P, TMF8806, LD2416 and others). 222 are empty, each with its reason recorded: 154 parts have no supply of their own (photoresistors, thermopiles, electrochemical cells, RTDs, load cells, heated gas elements whose heater and sensing-loop ratings aren't a supply) or the stored number wasn't a voltage (MRT511's 45 is a noise density, ME4-NO2's 10 a resistance), 62 have no maker or vendor source that states one, and 6 are families whose members differ (LSM6DS, MH-Z19). MH-Z19 no longer borrows a model's supply. AS7341 and AS7343 run on 1.7-2.0V and 1.7-1.98V (listed 1.7-3.6V), BMM350's VDD is 1.72-1.98V (1.62-3.6V), Acconeer A111 1.71-1.89V (1.8-3.6V), HLK AS201 2.2-5.5V (12V), Senseair K30 5.0-9V, its preferred range (4.5-14.0V, its absolute rating), ADS1293 2.7-5.5V (1.7-3.6V); minimums the catalog rounded to 1.7V are the makers' 1.71V. 39 parts sold in separate supply versions or with separate modes list each, e.g. AS5600 "3.0-3.6 or 4.5-5.5" and MLX90614 "2.6-3.6 or 4.5-5.5"; a record covering several chips gives the range all of them support (TMP11x 1.9-5.5V, which TMP116 needs). PZEM-004T lists the 5V its TTL interface needs, with a note that it runs from the 80-260VAC line it measures, and KY-040 lists 3.3 or 5V, because its outputs are pulled up to whatever powers it. Each checked value and its source is in `data/sensors/curated.json`.
- Sensor records missing their sensing technology, interfaces or maker were filled from makers' and module vendors' pages. `type` is now empty on 19 records (132 in 0.8.24), `protocols` on 4 (120) and `manufacturer` on 10 (59). What stays empty is a module combining several technologies (SEN54/SEN55, HW-290, body-composition modules), a part whose maker names no technology (HSCDTD008A), or a part no source attributes to a maker. The four without `protocols` are lidars with only an Ethernet port (Benewake Horn-RT, Horn-X2-Pro; the catalog has no Ethernet tag) or no documented interface (COIN-D4, Delta-2D). Types follow one rule per technology: silicon piezoresistive pressure dies are `mems`, silicon light and proximity detectors `photodiode`, GNSS receivers `rf`. Magnetic sensors and encoders typed Hall-effect without a source now carry their makers' technology: HMC5883L, HMC6343, HMC6352, QMC5883L/P, MMC56x3, MMC5983MA and BMM350 are `magnetoresistive` (AMR or TMR), RM3100 `magneto_inductive`, FG-3+ `fluxgate`, AMT25 `capacitive`, KY-040 a `mechanical` encoder and BM32S2031-1 an `optical` proximity module; Alps names no technology for HSCDTD008A, so it has none; AS201 is `mems` (it was `imu`, a device class), BMH05104 was credited to Holtek (it is Best Health's four-electrode BMH05104-2), the GROW fingerprint record now names R307, R503 and ZFM-20, and HWT901B's description was a Vietnamese library summary.
- The monthly sensor scrape would have dropped about 50 parts over its next three runs. 0.9.0 stopped reading "IMU", "6-axis" and "9-DoF" as accelerometer and gyroscope keywords, because they gave magnetometers a gyroscope. After that, libraries described only that way (LSM6DSV16X, ICM-42688, BMI088, ADIS1647x, QMI8658A and others) and general-purpose ADCs got no measures and were skipped as non-sensors. Their reviewed entries would then have failed the catalog build that gates the scrape. Such wording now still means an accelerometer and gyroscope when the text names no inertial or magnetic sensor, and a nine-axis part always has a gyroscope. Zephyr bindings whose trimmed description names no measure (ICM-42686, MAX32664C) and the ADCs have their measures set explicitly. A live scrape of all 14 sources finds every one of them again.
- LD2410 and LD2412 keep `light`. The Hi-Link modules have a photodiode whose reading ESPHome exposes, but ESPHome dropped the entity's device class on 6 November, and the scraper keyed on it, so the next scrape would have removed `light`. A part a scrape no longer finds is dropped at once when every one of its pages answers 404, instead of staying listed for three more scrapes: the MicroPython SN-GCJA5 driver's repository was deleted, so SN-GCJA5 stops claiming MicroPython support.
- Winsen products the scraper couldn't classify were listed as gas sensors, as in 0.8.24: its piezoelectric vibration sensors (WAP01, WAV01-WAV05, EA-134, WVV01, WVI01, WAI01), the ZH401 light sensor, conductivity probes, and residual-chlorine and aerosol monitors. They are now listed under what they measure, and Winsen's ion generators are skipped.
- Sensor descriptions use plain punctuation: full-width brackets, commas and tildes, invisible spaces and subscript digits from maker pages (mostly Winsen's) are stored as ASCII, so CH₄ reads CH4 (164 records).
- Descriptions changed on 698 records, most of them to describe the part rather than a software library ("Lightweight BMP58x driver for Arduino..."), Zephyr binding instructions or another board: ADS1115 had a pH-meter library's text, SCD40 was a "temperature sensor", QMC5883L an accelerometer and ICM-42688-P a three-chip module. Measures changed on 167 records (particulate sensors under gas, IMUs with a gyroscope or magnetometer they don't have, ADCs under what a library used them for), types on 174 (thermal-conductivity CO2 sensors labelled NDIR; laser, NDIR and photoacoustic types come from the makers), protocols on 331 and makers on 86 (AMS5812 is Analog Microelectronics, not ams-OSRAM).
- A second audit of 80 sensor records against makers' pages found a wrong or missing measure, interface, type or name on 36. The causes are fixed in the scrapers and build, and the rest corrected by hand with sources:
  - Winsen pages list some outputs in continuation rows of the spec table or in the Features list, and those were dropped; parts whose page names its outputs also got a guessed UART or I2C bus. Winsen interfaces differ from 0.8.24 on 134 records: the automotive modules are CAN or LIN (no UART), bare MOS gas chips are analog (GM-602B had I2C), water-quality probes RS-485 or 4-20 mA, MH-Z19 and ZH08 add PWM, MH-711A lists UART, I2C and analog.
  - Benewake interfaces come from each model's Interface row instead of a UART+I2C default: TF02-i and TFmini-i are CAN/RS-485 only, TF03 and TF350 add CAN, RS-232 and RS-485, and six models add their switching output (`gpio`).
  - Deneyap board libraries gave each chip the whole board's measures: MMC5603NJ, a magnetometer, was listed as an accelerometer and gyroscope, and SHT4x with pressure.
  - MaxBotix proximity sensors gain `proximity` (22), thermopile temperature sensors `ir_temperature` (TMP006, TMP007, AMG88, TSD305; not the RTGA71 NDIR gas detector), RGB light sensors `color` (APDS-9253, APDS-9950, APDS-9999, LTR-381RGB), and load cells lose `pressure`.
  - BNO086 is CEVA's (with a magnetometer and UART), BL0940 has SPI and UART, SMT100 RS-485 and analog outputs, MH-T5052B is NDIR, Winsen's FRn flow sensors thermal (not Hall-effect), and ESPHome component ids used as names read as the part (JSN_SR04T is JSN-SR04T, XIAOMI_LYWSD02MMC is LYWSD02MMC).
  - Descriptions cut to the length limit end at a sentence or word instead of mid-word (66 records).
- Identities: 34 duplicate records merged into their parts (vendor or library prefixes such as 7Semi, HLK, Microfire and MyLD2410 had become ids, and fxas210002c was a typo), 12 records that aren't parts left (Bosch BSEC and u-blox GNSS software, MaxBotix assortment kits, a Xiaomi scale, an LSM303 driver sub-device whose support now sits on LSM303AGR and LSM303DLHC; LSM9DS0/LSM9DS1 sub-device records merged into their chips), and 124 names were corrected (BMP085 showed as "BMP180MI", SHT30 as "ClosedCube SHT31D"; Winsen records named after their page address now carry the model, so MRTD-3011 is RTT-D7211-5.5). Old ids and names still find the record. The catalog has 1,701 records (1,669 in 0.8.24).
- `board_search` tags matched keywords inside other words: SDRAM made ULX3S, OrangeCrab and USB Armory `rf-sdr`, Grove, WROVER and "microvolt" made four boards `robotics`, VESC made three motor controllers `drone-uav`, and "smartcard" tagged `rtc`. Tags match whole words now (TMC2*, WS2812* and similar part-number stems are marked), every board's tags were checked against its parts, and 47 boards' tags changed.
- Three sensors built into a chip left the list, since they aren't parts you can buy: Bouffalo Lab TSEN, Silicon Labs EMU die temperature, and Raspberry Pi BCM283x SoC temperature. The Zephyr scraper now skips these and similar bindings.
- `get_design_rules`: 33 files were audited against makers' datasheets, app notes and specifications: power, protection, interfaces, MCUs, misc (including RF and antennas, which 0.8.12 had checked only in part), and the three guides 0.8.20 didn't cover (passives, power architecture, schematic practices). Wrong values were corrected, conditions added (which chip, family or test circuit a number belongs to), worked examples recalculated, and advice no primary source supports removed, so the 33 files are about 660 lines shorter in total and every claim carries a citation. All 41 files have now been checked against their sources. Corrections include:
  - Power and protection: a P-FET reverse-polarity circuit drawn backwards (drain goes to the battery), LTC3775 being a 38V part rather than 60V, and CSD17571Q2 being 24 mohm rather than 2.6 (also wrong in the MOSFET rules).
  - MCUs: RP2040's DVDD is the 1.1V core rail fed from VREG_VOUT, not 3.3V. Most F4 parts need an active-high supervisor on PDR_ON rather than tying it low. Every F4 group except F410 has a USB DFU bootloader on PA11/PA12, including F405-F439 (the file said F401/F411 only, then no DFU on F405/407). ESP32-C3 FH4 and FH4X GPIO counts were swapped. GPIO2 is not the C3's boot-message strap. iCE40 SPI_SS_B selects boot source the other way round from what the file said.
  - Interfaces: the ESP32 auto-reset circuit drives EN from RTS and GPIO0 from DTR (the file had them swapped). SN65HVD230 is a 3.3V CAN transceiver and ATA6561 needs 5V VCC plus a logic VIO (the file had them the other way round). MAX3485E is one unit load, not 1/8. MAX232 takes 1 uF capacitors. CH340N needs no crystal. TPS65987D is a single-port QFN part with external flash. A CAN terminator shorted to 24V dissipates 4.8W, so the blanket 0.5W/1W ratings were removed. The USB-C rule no longer says a sink reads disconnect below 0.276V; Type-C Table 4-36 puts the disconnect/connect threshold at 2.043V.
  - Parts and circuits: TPS22916 is 60 mohm in a WCSP-4 with no CT pin or thermal shutdown. UCC27511A is rated 4.5-18V, not 35V. MIC4606 is a full bridge. BSC019N04LS's 1.9 mohm is at 10V Vgs. ADR431 is the 2.5V part. MCP6V92 chops at 100 kHz. The 742792510 bead is a 6A 1812 part. A ferrite damping-resistor formula was missing its factors of 2. A WSLF2512 thermal example was off by ten. An op-amp bias pole and a stray-capacitance example were each ten times too high.
  - Level shifting: TXS translators support open-drain buses such as I2C; only TXB is unsuitable. BSS138's 3.5 ohm is specified at 10V Vgs.
  - RF: a guided-wavelength table whose 915 and 868 MHz rows didn't follow from its own assumption, an L-match example that didn't present 50 ohm, and the Johanson 2450AT18B100 chip antenna being a 1206 part rather than 0402.
  - From an independent review: TI's 6.46A inrush example pulled its 1.8V rail down to 320mV, an 82% drop (the rule read as a 320mV sag); Victron's current/3 cable shortcut is for 5m of total positive-plus-negative cable, not a 5m run; a 4.7 kohm I2C pull-up meets Standard mode's rise time at 250 pF only at its nominal value (about 239 pF with a +5% part); an EMC line's unsourced SPI capacitor value is gone; and the relay rule adds that an RC network across mains contacts sits across the supply when they are open (check its leakage, resistor dissipation and capacitor rating, per Littelfuse) and that mains-side copper needs creepage and clearance from the coil side on every layer.
  - Across files: the crystal rule now requires gain margin gm/gm_crit > 5, as ST's AN2867 states (it said >= 5; the STM32 rule was right). The PCB layout guide no longer prefers inner layers for crystal traces, which needs the vias NXP's AN3208 rules out, and no longer puts thermal relief on current-shunt and power-stage FET pads, which TI's motor-driver guide says need direct copper. The RF rule's GCPW impedance examples (from a 2-D field solve) are recomputed by a test with closed-form models.
  - From a second review: the CAN rule said Microchip's ATA6560/61 note gives no capacitor limit, but it says below 100 pF per bus line at 1 Mbit/s and at most 470 pF at 125 kbit/s; the CAN rate x length <= 50 rule is TI's rule of thumb for buses over 100 m (40 m at 1 Mbps below that). The PCB layout guide told readers to narrow a 20 mil, 50 ohm microstrip to 18 mil because the IPC equation reads 46 ohm (MT-094 says that geometry is about 50 ohm and the equation is the error), put 75 ohm at W/H 1:1 (it's about 0.83), dropped the "neglecting T" condition from the stripline B/W rule (with 1 oz copper, B/W 2-2.2 gives 42-44 ohm), said microstrip delay doesn't depend on width (only stripline's doesn't), and set an unsourced 10:1 via aspect-ratio limit that contradicted the DFM guide. ESP32-S3 octal flash, not only octal PSRAM, takes GPIO33-37. New: nRF52832 P0.09/P0.10 are NFC antenna pins until UICR NFCPINS is written, a common cause of dead GPIO.

### Fixed

- The stock history database stores each event once, in its primary key, without two unused indexes or the files' prices: 367 MB became 107 MB, `jlc_stock_history` replies are identical (checked on 5,003 parts over four windows) and lookups are about four times faster. History files are written one per day under `data/history/YYYY-MM/`, so git stores each day once; rewriting the month's file every day had stored 25 MB of history as 97 MB. The Docker image no longer includes the raw catalog and history files, only the databases built from them; with the smaller history database it went from 1.96 GB to 1.52 GB.
- Stock history was checked day by day against the daily catalog snapshots in git (all 263 days) and corrected. On 2026-04-02, 04-06 and 07-14 it listed 7,681, 31,045 and 55,664 parts as gone that were in that day's published catalog, and missed 60, 99 and 931 real events (2026-02-25 had 345 such events); those days now hold exactly the changes between the published catalogs, and lose their `suspect_scrape` notes. On the four scrape-gap days (03-03, 03-16, 03-18, 05-15), 42, 39, 8 and 5 subcategories went missing at once, 508,041 parts, and 97-100% of each were back the next day; their gone-then-new pairs were replaced as if the parts had been kept, which is what the scrape now does (below). 861,953 fewer events; every other day still matches its snapshots exactly, and the database is 75 MB. The first week of tracking (02-21 to 02-26, when the 10-unit floor and the scraper changed) is unchanged.
- The daily scrape no longer publishes a subcategory short when JLCPCB returns an empty page before the total it reports: the page is requested again, up to twice. When a scrape gap empties whole subcategories (three or more each missing at least 100 parts and 10%, or one missing 1,000 or more), their parts keep the previous scrape's rows for up to two days, listed in `manifest.json` under `carried_forward`, instead of disappearing from search and stock history for a day; the check before publication still judges the parts actually scraped. A single smaller loss is a delisting and leaves the same day: in the 263 days of snapshots none of those parts came back.
- `board_search` puts boards whose name or description matches the requested function phrase ahead of incidental mentions. Browsing a compound tag such as `led-driver` also favors boards describing that function, so dedicated LED drivers no longer fall behind keyboards and dev boards just because they have fewer parts. A board's name and the first clause of its description now outrank a passing mention: ESPresence, a presence sensor with a mains supply module, ranked 4th for "power supply" and is now 30th, and SparkFun's FemtoBuck leads a buck search.
- A `board_search` query with no searchable words (`the board`, `pcb design`, `a" OR "b`: stop words, single characters, quotes and OR, which isn't an operator) still browses the catalog, as documented, but the reply now adds a `note` saying so. It had listed all 303 boards by component count with nothing to tell them apart from matches.
- `cse_search` and `cse_get_kicad` no longer report a part as missing when CSE's first answer has a status other than `Success`. 4 of 10 fresh part numbers came back that way (GD32F103CBT6, MP2315GJ-Z), and every repeat said `Success`. We now ask once more and ignore the first answer, whose parts can be unrelated. If the second answer is no better the reply is an error rather than an empty result. A search that does find nothing is now remembered for a week, as intended, instead of being sent to CSE every time.
- `jlc_find_alternatives` with `library_type="no_fee"` and `has_easyeda_footprint` spent most of its footprint checks on extended parts that the no_fee filter then dropped, so basic and preferred alternatives further down were never checked. The filter now runs first: over 20 test parts, verified no_fee alternatives went from 30 to 40 (C8678 5 to 10, C1525 3 to 5) with fewer checks (166, was 300). Without `has_easyeda_footprint` candidate selection is unchanged; all alternatives replies gain `summary.stages`.
- `jlc_search`'s `why_empty` says `status: "budget_exhausted_or_busy"` when its checks run out of time. Such a check came back without a status, as if merely incomplete, and the server logged it as a failed search with a traceback.
- `sensor_recommend` with a query of only non-Latin text (`温度`) returned the whole catalog, and a query containing a NUL character failed with a generic tool error. The first now matches nothing, the second returns "Query contains invalid characters". A query with no searchable words (`é`, `-`, `sensor`) still leaves only the measure, type, protocol and platform filters, and the reply now adds a `note` saying so, as `board_search` does.
- `jlc_get_pinout` listed every pin twice for symbols that EasyEDA draws whole and again as units under other names: LM358 C328566 came back with 16 pins (OUT1 and OUTA, VEE and GND on pin 4). The whole drawing's pins are used now, units add only pins it lacks, and a unit's electrical type fills in the same pad (8 pins, outputs and supplies marked).
- `datasheet_pdf` links (`/mcp/datasheet/<lcsc>`): when JLCPCB doesn't answer, the 502 reply no longer passes its error text through.
- Sensor records corrected by hand are kept in `data/sensors/curated.json` with their evidence, and win over every scraper and build rule, so the monthly re-scrape can't undo them. The sensor scrape now builds the catalog before committing its data, and the scrapers no longer store an absolute maximum, an upper bound or one of several options as a supply voltage.
- `sensor_recommend` links: 44 of the 224 ESPHome links were dead. They pointed at esphome.io/components/sensor/<name>.html for components merged after the last ESPHome release, documented outside components/sensor/ (HLK-FM22x, the GROW fingerprint reader) or under a bus-suffixed name (honeywellabp2_i2c). Each now goes to the component's esphome.io page, to next.esphome.io when it is documented only for the coming release (28, including BQ27220, LIS3DH and VL53L1X), or to its source on GitHub when no page exists (4). 8 Tasmota links had the page's HTML stuck to the address (`...icp10125-driver><strong>InvenSense`), one also a doubled `https://`.
- `sensor_recommend` interfaces and measures: Xiaomi LYWSD02MMC and XMWSDJ04MMC thermometers list `ble` (they listed I2C, which nothing on them exposes), as do Aranet and ESPHome's other BLE devices. The Hydreon RG-9/RG-15 rain gauge is under `rain` (it was under distance and humidity, from its rainfall in mm and its 0-7 rain-intensity level), the SMT100 soil probe under `soil_moisture` (humidity, plus voltage from a readout of its own supply), and GY-39 is no longer under distance: its altitude is calculated from pressure. Winsen modules with an RS485 output list `rs485`, not `uart` (ZW-pH201, ZW-O201, ZW-ORP201, ZW-C1021, ZRT513-R1234YF, WPCW02 and others); ZW-C1021 gets its 9-36V supply from a "Power Supply" row the scraper skipped; ZW-TUR1021 lists its analog and UART outputs; and names lose a trailing "| Winsen". pH, ORP and dissolved-oxygen modules (Winsen ZW/MW series, DFRobot SEN0161) are under `ph`, `orp` and `dissolved_oxygen`, where they were only under `water_quality` or, for dissolved oxygen, under the `oxygen` gas measure; conductivity probes (DFR0300, EC10) are under `conductivity`; and ZW-NH101, ammonia nitrogen in water, is no longer listed as an ammonia gas sensor. HWT901B lists acceleration, gyroscope, magnetic field and tilt (it listed only gyroscope), and the Hydreon record is named "Hydreon RG-9/RG-15", so a search for RG-9 finds it.
- DS1821 lists `voltage` 2.7-5.5V (it listed 3.0-5.5V, a limit its datasheet doesn't give) with a note that its ±1 °C accuracy and 1-Wire timing are specified at 3.6-5.5V; S11059's maximum is the maker's 3.63V. An independent audit of 71 records found two more understated supplies: RV-3032 is 1.4-5.5V (1.3V is its timekeeping minimum; I2C needs 1.4V, or 2.0V at 400 kHz, now in a note) and MaxBotix MB1712 3.0-5V (it listed 3.0V, the minimum). Nine single-voltage parts read "5.0-5.0" and now read "5".
- 14 records new in this month's scrape were checked like the rest: ADIS16607-2 and -3 (3.1-3.6V, SPI and I2C), Goodix GT911 (2.8-3.3V), the GY-39 module (3-5V, I2C or UART), DFRobot's SEN0701 IR positioning module, Sensirion's SHT40I analog sensors (4.5-5.5V), SLF3S liquid flow (3.2-3.8V), STS35 (2.15-5.5V) and six Winsen water-quality modules (9-36V or 6-14V). TI's BQ25820 battery charger, which ESPHome added with its ADC readings as a sensor, is left out like other chargers.
- The monthly sensor scrape keeps more of each source. Winsen's category listings had 15 seconds each and 13 of 30 timed out in one run, leaving their products unscraped; listings now get 60 seconds, a second try, and a 15-minute cap. A rerun within 20 hours of the last scrape no longer counts as another missed month, and a record found under the id today's rules give it (hlkld2410 is ld2410) is no longer also carried under its old id. A reviewed part that leaves every source no longer stops the month's data from being committed; the check before deploying fails instead, until `curated.json` is updated. The supply parser no longer reads an output range in the same cell ("5V; 0.5-4.5V output"), a tolerance written on a range ("3.3~5V ±5%") or a ceiling such as "not higher than 5V" as the supply.
- Battery holder searches include Battery accessories listings that say "Battery base" (C5375990, C5375986), which 0.8.24 left out.
- Reference boards: inductors with a bare number no longer get a unit invented for them (TPA3255 L1-L5 read 10000mH; the source says only "10"). Coilcraft XFL, XEL and MSS codes decode in nanohenries (XFL4020-222 is 2.2uH, not 2.2mH). Capacitance and "0 ohm" values on L references stay as written, and so do bare numbers on C references (ANAVI's "0.1" read 100000uF). Murata BLM bead and LQW/LQP inductor codes and Nichicon UWT capacitor codes now read as values (Prusa Buddy Mini's 37 beads are 120 or 60 ohm, WM1302's RF inductors 1.2-47nH); EHM's DR73 inductors read 10uH and 22uH; SimpleFMCWRadar's C16/C24 read 1nF, not 1000000uF. USB Armory Mk II now comes from its main schematic: 194 parts and 156 nets, where it had the power sheet's 31 parts and no nets.
- Reference boards were re-parsed and checked against their source files: 8,176 part rows on 289 of the 303 boards changed, 427 were added and 132 removed (do-not-fit parts, fiducials, logos, tooling holes and heatsinks). `format` names the KiCad version each board's files were saved with: 61 boards had the wrong one, most of them labelled kicad7.
  - MPNs, makers and distributor codes the parser dropped are back: Eagle parts now take the library variant (technology) they were placed with and their own attributes, instead of a mix of every variant's (Sapog's C5 read 50V ±10% where its variant says 25V ±20%), and attribute names such as MANF#, "Manufacturer Part Number" and MicroType's value-in-`id` convention are read. 3,157 MPNs and 1,271 makers changed or were added.
  - Values: "1MEG" resistors, "1000 pF"-style capacitors that read as "pF", Taiyo Yuden MAKK inductors, ferrite impedances that overrides had replaced with "ferrite bead", and a Würth bead number read as 7.42793 Mohm. 232 values changed.
  - Where a part's value and its MPN or description disagree in the source, the value the designer placed is kept and the identity of another part dropped (217 rows), unless the source proves the MPN: YARD Stick One C27/C28/C32 are 47pF (Great Scott Gadgets' commit 25badce93e changed their part number and description but not the value field), and Tigard U4 is the 93LC56 its LCSC code orders.
  - Connectivity: Bus Pirate 5 was parsed from a subsheet and now has its 208 fitted parts and 183 nets (it had 38 and none). Ubertooth One, ENNOID BMS, HALPI2 RS-485, EEGFrontier, the HV flyback converter and the LED Matrix module also had no nets and now do; nets across all boards went from 21,084 to 21,777. A missing registered schematic now fails instead of falling back to another sheet.
  - A second check compared 15 boards with their sources, part by part and net by net, and the parser causes it found are fixed:
    - Fitted parts whose schematic value was "~" were dropped with their nets. PocketPD's RP2040 BOOT button and OpenAirScope's two RF-match capacitors are among 54 parts back on 19 boards.
    - Connectors keep their pitch and series: SparkFun's 1 mm Qwiic sockets read "1x4 header", a 1.27 mm SWD header "2x7 header", and XT60s "1x2 header".
    - IPC-7351 footprint names stay whole: SOT50P160X60-6N (a SOT-563) and SOT95P280X145-6N (a SOT-23-6) both read "SOT-6".
    - Parts whose ref contains a dot or starts with "+" (Olimex's +3.3V test pads, an Olimex 5.0V/3.3V jumper) had lost every pin. Power symbols are now recognised by their power flag.
    - Part numbers and ratings hidden by a decoded value are kept: dc-poe's F1 2920L110/60MR keeps its 60V rating, and crystals keep their load capacitance.
    - Do-not-fit parts are dropped however they're marked: DNP 47K, DNF, NM, nf, and Olimex's NA(...), which had listed 57 unassembled parts as fitted (47uF capacitors, a BME280, RCLAMP0524P arrays).
    - Solder jumpers say whether they're normally open or closed, and 164 LED series resistors are no longer called pull-ups.
    - Board descriptions: SimpleFMCWRadar's gain block has one amplifier, not three; Duet 2 WiFi v1.04 has no Ethernet PHY; and HEEV's power stage is a separate board.
  - Metadata: ADSBee RF, PrntrBoard V2 and USB Armory key ICs named parts the boards don't have, the MPPT CN3791 board claimed a varistor, and the ESP32-S3 Feather's file is the 8 MB, no-PSRAM version.

### Added

- `jlc_stock_history` shows recorded low-stock changes for one part, flags possible scrape gaps, and includes its stock in the current catalog snapshot. It returns up to 100 events over the latest 180 days by default (1-366 allowed), explains which changes are recorded, and never treats a missing scrape entry as a confirmed stockout. Future events also keep the previous snapshot stock; older history stays readable without it.
- `jlc_search(facets=true)` adds `facets`: how many of all the matching parts (not just this page) each manufacturer, package and library type has, top 15 of each, so an assistant can narrow a broad search (100nF 0402 capacitors: 246 parts, Murata 32, YAGEO 25...). Counting has its own limit of about 200 ms: when it runs out the facets say incomplete and the search results are unaffected. Without `facets` the reply is unchanged.
- `jlc_find_alternatives` replies have `summary.stages`: how many candidates each source returned (and whether it hit its limit or failed), how many passed or failed the spec checks and the library/package filter, how many footprints were checked, compatible, incompatible, unknown or skipped at the cap, and whether the list was cut. A failed catalog lookup now says so instead of looking like no candidates.
- `get_design_rules`: five sourced references for LEDs/addressable LEDs, relays/inductive loads, buttons/debounce, Nordic nRF52 and assembly/DFA (46 files total), with topic aliases and citation validation.
- ENS160, ENS161, SGP30, iAQ-Core, BME680, BME688, APC1, SEN6x, SM300D2, PZEM-004T, KY-040 and the MAX32664 hubs carry `capability_note`, and so do 49 parts that need a supply besides the listed `voltage`: a separate VDDIO or LED rail (BMI330, APDS-9930, MAX3010x), a GNSS module's backup supply (ZED-F9P, LC26G), the 12V emitter rail of Infineon's PAS CO2, or a negative rail for bipolar use (AD8495); ENS160 and SGP30 also carry `compensation_inputs` and cited `voltage_evidence`, as CCS811 does.
- `/mcp/stats` counts why calls found nothing or failed: `reasons`, one fixed label a call (which filter blocked a `jlc_search`, a part number not in stock, no ECAD model and so on), and `why_empty`, how the checks behind that reply went. DigiKey gains `retry_found` and `retry_missed` for the all-digit keyword retry. Still no IPs, queries or part numbers.

## 0.8.24 (2026-11-09)

Changed replies: `jlc_search` results for repeated `=` filters on range specs, battery holders and the words adjustable, variable and fixed; `digikey_get_part` misses on all-digit numbers.

### Breaking

- Repeated `=` filters on a range-listed spec now keep range matching: each value matches what it would alone, and the filters still mean any of the values. LDOs with `Output Voltage` = 3.3V and = 5V went from 4,793 parts to 6,281, because adjustable parts such as C75510 (1.2V~37V) were being left out. `Supply Voltage` and `Vin` still require a part to cover every value. The rule is now in the `spec_filters` description.
- "battery holder", "cell holder", "coin cell holder" and "button cell holder" are now a part type covering the five subcategories holders are filed under; in Battery accessories only listings that say "holder" match. `battery holder` went from 188 parts to about 660 and `coin cell holder` from none to about 400.
- In a holder search, AA, AAA, C, D, No. 1/2/5/7, 14500, 10440 and coin or button cell match the size in the part's text, as `Battery Size` in `filters_applied.spec_filters`. `AA` no longer returns AAA-only holders, 14500 finds AA holders, and D returns no parts because none is stocked.
- "adjustable", "variable" and "fixed" stay search words when the query names no part type or model. They used to add an `Output Type` filter, which turned `adjustable battery holder` into DC-DC converters.
- `digikey_get_part` retries an all-digit number its lookup misses with DigiKey's keyword search, which costs one more request and keeps exact manufacturer part numbers only, so Keystone 209 is found. Several makers' parts can come back. A number still not found adds `hint`.

### Fixed

- A single letter joined by a hyphen stays attached to its word: `BH-D` searched `BH` and returned 889 unrelated parts. It now matches that prefix only, and finds nothing because no part has it.

## 0.8.23 (2026-11-08)

### Breaking

- Inductor alternatives with unknown or differing Isat criteria, rating bases, or thermal-current conditions now appear in `unverified_alternatives`, with explicit unchecked requirements. They no longer drive a verified recommendation, savings comparison, or `compatibility_verified=true`. DCR comparisons require comparable published rating bases. Multi-diode forward-current comparisons also remain unverified when loading/thermal conditions aren't established.
- Part results can include `spec_evidence` (reviewed manufacturer values, conditions, document identity, printed page and source URL), `spec_discrepancies` (catalog versus document claims), and `no_datasheet_note` (the flag applies to JLCPCB only). Catalog specs and numeric search/sort values are preserved.
- Negative output-voltage queries/filters preserve polarity, including catalogs with unsigned values plus Negative configuration. Ferrite impedance filters with a frequency require that condition (including OR alternatives and natural-language requests). Negated part-number searches return an explicit unsupported-exclusion error instead of selecting the excluded identity.
- Empty searches can return `why_empty`: bounded local library/package/stock counterfactuals with retained constraints, exact/lower-bound counts, next calls and completeness. Original results remain empty. Diagnostic work uses a private read-only connection, at most three queries, a 200 ms deadline, two million SQLite steps and 5,000 post-filter rows. No automatic external calls.
- Local part results carry `data_source` with snapshot observation time; live lookup results retain their observation time through caching. MPN misses explicitly describe the local snapshot and offer an unexecuted `next_call` to `jlc_stock_check(min_stock=0)`; availability beyond the snapshot stays unknown. MPN hits also return `data_as_of`.
- Sensor data excludes generic MCU/platform identities such as RP2040. CCS811 exposes `eco2` instead of `co2`; humidity/temperature are compensation inputs, not its direct measurements. It includes capability/voltage evidence and the 1.8–3.3 V operating range (3.6 V is a stress limit). Description merging prioritizes device/integration sources over breakout prose, preventing SCD4X from inheriting an all-in-one board's capabilities. Other families still need individual capability audits.
- Alternatives savings preserve the legacy $3 numeric basis but explicitly label it a rounded Economic loading-fee estimate: `is_estimate`, `assembly_service_assumption`, `loading_fee_per_extended_type_estimate_usd` and `fee_basis`. It is not a current quote or a Standard assembly fee calculation.

### Fixed

- C53308978's catalog DCR is 20 mΩ, but SOREDE SRD-WI-22770 Rev A (2024-06-14), printed p.2/8, specifies 27 mΩ maximum. The discrepancy is annotated at runtime, independently of daily catalog rebuilds. Its 8.5 A typical Isat at 30% inductance drop cannot verify equivalence to C913245's 8.5 A at 20% drop. Reviewed evidence accompanies both parts.
- C2500 (Nexperia BAV99,215) now explains multi-diode loading conditions and carries the manufacturer's 215 mA single-loaded and 125 mA per-diode both-loaded limiting values (BAV99 v.9, Table 5). Multi-diode listings warn about loading and thermal conditions; single-diode listings do not receive that warning. `If >= 150mA` still filters the catalog's 125 mA value.
- Isat and diode-current sorting explain the missing comparison conditions. Missing-datasheet flags explicitly refer to JLCPCB's listing, even when LCSC has a copy. The response builder also enforces the unverified-candidate boundary, and confidence reports unchecked requirements from those candidates.
- Component scrapes finish retries in a private staging directory before history generation or category publication. Incomplete/tripped runs fail without replacing published data; progress remains resumable. Publication I/O errors roll back completed replacements and retain staged output. Final checks reject remaining failed subcategories, inconsistent counts, >5% total drops and >30% drops in previously 1,000+ part categories. The existing explicit manual drop override applies to count thresholds only.
- The component workflow reuses the same manifest validation before commit/deploy. No workflow was executed as part of local verification.
- Fixed a deprecated class-scoped test fixture. Removed completed and duplicate planning documents; remaining deferred work stays in a local, uncommitted backlog.

## 0.8.22 (2026-11-07)

Changed replies: `get_design_rules` text for voltage supervisors.

### Fixed

- **Voltage-supervisor rules that had open-drain RESET backwards** (from a design-session report, checked against the TLV803, TPS3808 and MAX803/809 datasheets). The rule said to pull RESET up to a rail that's up before the monitored rail, never to the monitored rail; TI's TLV803 application and Maxim's MAX803 datasheet pull up to the monitored rail, and Maxim warns that a pull-up to another rail drives RESET high while the supervisor is below 1 V. It said an open-drain output can't discharge a capacitor on RESET; an asserted output is a low-impedance sink, and the real limits are its current rating (5 mA on TLV803 and TPS3808) and the RC release delay. TPS3808 and MAX809 were said to hold RESET low below 0.6 V; they're valid down to 0.8 V and 1 V. The 100 kohm pull-down fix applies to push-pull outputs such as MAX809; beside an open-drain pull-up it only forms a divider. The 4.7 kohm default is now the datasheet's range (10 kohm-1 Mohm on TLV803 and TPS3808).

## 0.8.21 (2026-11-06)

Changed replies: `get_design_rules` text for EMC, DFM, I2C and USB.

### Fixed

- **Design rules that were still wrong** (from a follow-up review of 0.8.20, each checked against its source). The EMC guide put Murata NFE61P filters on MIPI camera lanes and called them 0603 pi filters; NFE61P is a 6.8 x 1.6 mm single-circuit T filter made for DC power lines, and Murata's MIPI D-PHY note recommends DLM common-mode filters, which keep both the differential and single-ended signals intact. TDK MAF is an audio-line filter, not a USB/HDMI part. DLW21HN was called a > 5 Gbps choke, but DLW21HN900SQ2 is Murata's USB 2.0 part; signal-line chokes are now chosen by cutoff frequency from Murata's charts, with sizes in mm (Murata's codes mix inch 0805 with metric 1210/0806/0605; inch 1210 is a 3.2 x 2.5 mm footprint). TDK ACM2012H's commercial version was discontinued in 2019. The I2C rule "2.2 kohm for 400 kHz or > 200 pF" gives a 373 ns rise at 200 pF, over the 300 ns limit; 400 kHz at 200 pF needs 967 ohm-1.77 kohm (3.3 V), and the worked example's "use 1.8 kohm" was over its own 1.77 kohm maximum. The 5 V minimum was 1.5 kohm, under the 1.53 kohm limit. JLCPCB Economic reflow is 255 +/- 5 C, so up to 260 C, and Standard is 240 +/- 5 C. TI's MCU-pin resistor note now also says TI ranks fast parallel ports, such as external-memory buses, high for filtering.

### Changed

- A new test recomputes the I2C pull-up worked examples in the rule files.
- Each version is now published as a GitHub release, tagged `vX.Y.Z`, with its changelog entry as the notes. Self-hosters can watch the repository's releases to hear about new versions.

## 0.8.20 (2026-11-06)

Changed replies: `get_design_rules` text for EMC, PCB layout, signal integrity, thermal, DFM, connectors, checklist and test/debug.

### Fixed

- **Design rules that were wrong** (each checked against its source). Microstrip and stripline delay were 10x off ("136 ps/in (5.4 ns/100mm)"; it's 5.4 ps/mm). IPC-2221's internal clearance above 500 V was 10x off (0.025 mm/V; IPC says 0.0025 mm/V added to the 500 V spacing). TI's 1000 pF MCU-pin cap applies to edges of 100 ns or slower, not faster. Double-sided reflow put heavy parts on the wrong side. The series-termination explanation had the receiver wait two trips (it sees full voltage on the first). The duty-cycle Zth formula underestimated peak Tj about fourfold. CDCV304's 50 ps is output skew, not jitter (56-63 fs RMS); DS125BR820 is a redriver, not a retimer; GCT USB4085 is through-hole, not mid-mount. Henry Ott proposed the split-ground-plane test; he didn't report one. The nearest E24 value to 25 ohm is 24; a 0.3 Dk error moves 50 ohm by ~2 ohm, not 4.
- **Rules stated as universal that hold only where their source measured them** (from the design-session report in `todo-bug-design-rule-accuracy-and-applicability.md`): series resistors and 1000 pF caps on simple MCU I/O only; grounding unused pins (ESP32 boot pins fight it); 47 pF USB data caps (Full-Speed only; High-Speed allows ~4 pF); ESD, fuse, TVS and ferrite on every line or rail; the 20-25 ohm "normal" rail resistance; mandatory teardrops; ground-plane splits (the exceptions are now listed); the 2-layer EMC cutoff; IPC-2152 current capacity; ADI's Kelvin-shunt results; thermal metrics (datasheet theta-JA vs board theta-JA vs psi-JT); fab limits now name their fab and service; DFA spacing and tombstoning guidance name their source. Numbers with no source are cut or marked "no source found".

### Changed

- **Design rules style guide:** rules keep the conditions and uncertainty their source states, say whether a number is a requirement, fab limit, recommendation or one design's example, cite short [n] IDs, and give a calculation instead of a default where the design decides. "Most conservative value" is gone: a bigger cap or smaller pull-up isn't always safer. A new test checks every paired unit (mm/mil, ps/in) in the rule files.

## 0.8.19 (2026-11-06)

### Fixed

- **`Iq` in `spec_filters` was ignored:** `Iq` worked in query text (`LDO Iq < 100nA`) and as a `sort_spec`, but a `spec_filters` entry named `Iq` came back in `ignored_filters` as "isn't numeric" and the search ran without it. `Iq` (any case) now filters the same as `Quiescent Current`: 1,154 3.3V LDOs under 10µA either way. The `spec_filters` description lists it among the short names.
- **`jlc_get_pinout` description:** it said `unverified=true`, but the reply holds the string "Symbol not verified by LCSC", as it always has. The description now names the string.
- **`cse_search` and `cse_get_kicad` descriptions** said "up to 45 s", but no limit caps a call: timeouts apply to each request phase, and `cse_get_kicad` searches, then downloads. An uncached search took about 15 s (four measured), and prod's daily average ran from 3 to 26 s. The descriptions now give the typical time and say answers are kept.

### Changed

- **Docs rewritten:** the README is now an overview, down from 5,600 words to about 1,150. `landing/llms.txt` lists the facts an AI client needs (each tool's arguments, defaults, limits and reply fields, how queries are read, quotas) without the per-release notes it had copied from the README. The query rules, spec filters, packages, sorting and alternatives rules moved to `docs/search-guide.md`. Corrections made on the way: `cse_get_kicad` needs `CSEARCH_USER` and `CSEARCH_PASS` when self-hosting, and `docker-compose.yml` needs the external `web` network created first.

## 0.8.18 (2026-11-05)

Changed replies: `jlc_get_pinout` has a `note` for polarized two-pin parts.

### Added

- **`jlc_get_pinout` warns that diode and LED pin numbers aren't standard:** BAS316's EasyEDA symbol (C109218) has the anode on pin 1 and the cathode on pin 2, the reverse of Nexperia's datasheet, and the reply gave no hint. EasyEDA numbers these parts both ways: of 7 well-stocked diodes and LEDs, 3 symbols put the anode on pin 1 and 4 the cathode. Each footprint's polarity mark sat on the pad its symbol names K, so EasyEDA's symbol and footprint agree; mixing their numbers with a datasheet's or another library's footprint puts the part in backwards. A two-pin symbol whose pins are named for the anode and cathode (A/K, A/C, +/-) now gets a `note` saying the numbers match EasyEDA's footprint pads but not necessarily other sources, so connect the part by pin name.

## 0.8.17 (2026-11-05)

### Fixed

- **Tool descriptions left out their reply notes:** MCP clients get a tool description's first section and its argument notes, not the docstring's Returns or Examples sections, so about 9,000 characters across 12 tools never reached them. The guidance in them is now in the part clients get: `pcba_type` `standard_only` moves the whole order to Standard assembly, `no_datasheet`, `total` before `limit`, spec-sort `sort_value`/`sort` (`jlc_search`); JLCPCB matching only whole part numbers and their starts (`jlc_stock_check`); MPN lookups searching the daily snapshot (`jlc_get_part`) and where alternatives' stock comes from; pin numbers matching footprint pads and when `electrical`, `unverified` and `note` appear (`jlc_get_pinout`); Mouser's `not_found`; result order and `matched_by`, consensus counts and `tag_consensus` (`board_search`); board part numbers and `did_you_mean` (`board_get`); sensor order; design rules' `note`. Field lists the replies already show and the examples were dropped. A test checks that every word of each tool's docstring reaches clients.

## 0.8.16 (2026-11-05)

### Fixed

- **`mouser_get_part` and `digikey_get_part` descriptions:** 0.8.15's note on Mouser's `lifecycle` (null where Mouser states none; DigiKey's status and the maker's site for NRND) and 0.8.14's note on DigiKey's packaging fields (`packaging`, `other_packaging`) were in the part of the description that MCP clients don't receive. Both are now in the part they do.

## 0.8.15 (2026-11-04)

New reply fields: `data_as_of` in `jlc_search`, and `prices` in `jlc_stock_check` for one LCSC code. Changed replies: `jlc_stock_check` with one LCSC code returns only that part; `mouser_get_part`'s `lifecycle` is null instead of `Active` when Mouser states no status; package names that had Chinese words in them are in English.

### Added

- **Price tiers in `jlc_stock_check`:** a query of one LCSC code returns the part's price tiers (`prices`, as in `jlc_get_part`) from the same live reply as its stock, so a BOM line takes one call instead of two. Text searches stay without them.

### Fixed

- **`mouser_get_part` said Active when Mouser says nothing:** `lifecycle` was `Active` for every part Mouser gave no status and didn't mark discontinued. AP2553W6-7 came back Active though Diodes' datasheet is stamped NOT RECOMMENDED FOR NEW DESIGN and DigiKey lists it NRND; Mouser states no status for it. `lifecycle` is now Mouser's own status where it states one (Not Recommended for New Designs, End of Life, Obsolete, Discontinued) and null otherwise, which is most parts. The descriptions point to `digikey_get_part`'s `lifecycle` and the maker's site for NRND.
- **`jlc_search` and `jlc_get_part` gave different stock and prices for the same part:** C14663 read 38,555,997 at $0.0083 in search and 37,538,619 at $0.0072 in `jlc_get_part`. Both are the 1-piece price; search uses the daily catalog snapshot, and JLCPCB had changed the price since. Search replies now give the snapshot's scrape time as `data_as_of`, and the descriptions say which tools are live (`jlc_get_part`, held up to an hour, and `jlc_stock_check`).
- **`jlc_stock_check` with an LCSC code listed other parts:** JLCPCB's search also matches the code's digits inside part numbers, so `C5947` returned four TLC5947 drivers after the 74HC595D, and `C1622` 16.2k resistors and a 74LVC162245 after the 47 nF capacitor. One LCSC code now returns only that part, and says so when it has less stock than `min_stock` or doesn't match the filters given.
- **Package names in Chinese:** 2,975 parts read `插件,12.6x4.4mm` (through-hole) next to `Plugin` on others, so a BOM's package column and package filters saw two spellings. They now use the English listings' own words in every tool: `插件` is `Plugin`, `弯插` (right-angle through-hole, 1,187 parts) is `Plugin` with `,Right Angle`, `交错脚` is `(Staggered pins)`, and `卧贴`/`立贴` are `Right Angle`/`Vertical`. The full-width comma in `Surface Mount，Right Angle` (17,370 connectors) is a comma, and `SOТ23-6` (C5371028), spelled with a Cyrillic Т, now matches SOT23-6 filters. Package filters take either spelling: `jlc_stock_check` also sends JLCPCB's own (its live search still uses `插件,12.6x4.4mm`), and `jlc_search` reads the old one.
- **`jlc_search` description:** `filters_applied` lists every filter that ran, given as an argument or read from the query; `parsed` shows only what the query text gave. A `Voltage >= 25V` filter given as an argument was missing from `parsed`, so it looked as if it hadn't run.

## 0.8.14 (2026-11-04)

New `digikey_get_part` reply fields, all optional. For a manufacturer part number whose first DigiKey listing is a reel, `part_number`, `price_breaks` and `min_qty` change to the cut tape's.

### Fixed

- **`digikey_get_part` mixed two packagings:** TPS62130RGTR came back as 296-37682-2-ND, the 3000-piece reel, with price breaks from 3000 at $1.00 and `min_qty` 3000, next to `price` $1.99, the cut tape's single-unit price. The part number, breaks and minimum came from whichever packaging DigiKey listed first, and `price` from the product as a whole. All four now describe one packaging: the DigiKey number you asked for, or else the smallest order (cut tape before a reel, DigiKey's own stock before Marketplace, no Digi-Reel fee). `packaging` names it, and `other_packaging` lists the others with their part number, minimum order and price (a Digi-Reel adds `reel_fee`, a Marketplace listing `marketplace`).

## 0.8.13 (2026-11-04)

### Added

- **Eight guitar-pedal reference boards:** GuitarML's Classic Boost (2N5088) and TS/RAT combo (TL072 Tube Screamer-style overdrive, LM301 RAT-style distortion, 2N5458 JFET buffer), and six boards from torvalds/1590A: the Buffered base (LT3462A inverting converter for -V, AP2202 LDO, DMC3071LVT MOSFET bypass switching), the Daisy Seed base (LS844 JFET input buffer), and the Boost, Compressor, Fuzz and Octaver effect boards (MMBF5103, MMBFJ201, LS844, DMMT5551). `BOARDS.md` listed them as two rows of several boards each, which the parser couldn't read, so neither had ever been searchable. All are tagged `audio`. torvalds' STM32 effect board is left out: its PCM3060 codec's I2S pins connect to nothing, so it isn't a working reference.

### Fixed

- **`nc_pins` listed pins that are connected:** a pin wired only to a part the board parser drops (a test point, a solder jumper, a pedal's wiring pad) has no net in the board data, so 0.8.11 listed it as NC. The SIM7080G's USB_BOOT pin on the Absmach S0 goes to solder jumper JP1, for one. Pins are now checked against every pad in the design file: 1,082 pins on 316 parts are no longer listed as NC.
- **Adafruit MAX31865 board:** its library misspells one ground pin `ANGD@1`; the fix meant to rename it never matched, so it's now `AGND@1` in the netlist.

## 0.8.12 (2026-11-04)

### Fixed

- **RF antenna design rule:** its "ADI table" said 1.5 mm FR4 with a 2.8 mm trace and 0.2 mm gap gives 50 ohm GCPW. That's the plain-microstrip 50 ohm width; with ground 0.2 mm away it's about 35 ohm (2-D field solve), and ADI's article has no such row. The rule's own 2-layer line (1.2 mm trace, 0.25 mm gap) is right at 50 ohm and now says solder mask takes about 3 ohm off. Checking the same sources fixed three more lines: ADI gives about -45 dB as the practical isolation limit between RF lines, not a minimum; ADI's 0402 SRFs (100 pF: 800 MHz, 20 pF: 2.5 GHz) replace figures that had 100 pF bypassing at 2.4 GHz; and the ESP32 line follows Espressif (a 15 mil, 100 ohm stub trace, not a 5.6 nH inductor; all layers clear under an IPEX connector, not a 1 mm ring).
- **`jlc_get_pinout` footprint hint:** a client that loaded the tool list before 0.8.4 has no `footprint` argument, so the note pointing to `footprint=true` left it stuck. The note now says to reconnect to load it.

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
