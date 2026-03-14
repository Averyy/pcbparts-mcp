# Verified Design Rule Sources

382 sources across 41 topic files. 352 after cleanup (Mar 2026), then +30 gap-fill sources across 9 topics (audio, test-debug, fpga, can, isolation, adc-dac, thermal, ethernet, esp32) = 382. Every source is free, no paywall.

## How to Use This File

Each design rule file has a curated list of sources ranked by priority. When writing a rule file, start with Source 1 and work down. Sources are chosen for:

1. **Trustworthiness** -- manufacturer app notes, official specs, established educational sites
2. **Extractability** -- **strongly prefer HTML sources**. PDFs are acceptable only when no HTML alternative exists. HTML extracts cleanly and preserves tables/structure. TI PDFs that resolve via `ti.com/document-viewer/lit/html/{DOCID}` count as HTML.
3. **Educational value** -- teaches the "why", not just the "what"

### Platform Extractability Guide

| Platform | Method | Quality |
|----------|--------|---------|
| TI App Notes (HTML) | HTML via `ti.com/document-viewer/lit/html/{DOCID}` | EXCELLENT -- ~36% of docs, structured tables/sections. **Preferred** — extractor auto-probes HTML first. |
| TI App Notes (PDF) | PDF via `ti.com/lit/an/{docid}/{docid}.pdf` | HIGH -- predictable URL pattern, fallback only when HTML unavailable |
| ADI App Notes | HTML via `analog.com/en/resources/app-notes/an-{N}.html` | EXCELLENT -- structured HTML, best for LLMs |
| ADI Technical Articles | HTML via `analog.com/en/resources/technical-articles/{slug}.html` | EXCELLENT |
| Espressif HW Guidelines | HTML via `docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/{chip}/` | EXCELLENT -- Sphinx/RST, 10 chip variants, 4 pages each (schematic-checklist, pcb-layout-design, download-guidelines, resources). Old ReadTheDocs site renders clean HTML; new CDP site is a JS SPA (unusable for extraction). |
| Espressif ESP-IDF Docs | HTML via `docs.espressif.com/projects/esp-idf/en/latest/{chip}/...` | EXCELLENT -- peripheral HW notes, SD pull-up requirements |
| Espressif Chip Errata | HTML via `docs.espressif.com/projects/esp-chip-errata/en/latest/{chip}/` | HIGH -- known silicon bugs + workarounds |
| Raspberry Pi Docs | PDF via `datasheets.raspberrypi.com/{chip}/{doc}.pdf` | HIGH |
| SparkFun Learn | HTML via `learn.sparkfun.com/tutorials/{slug}` | EXCELLENT -- CC BY-SA 4.0 |
| All About Circuits | HTML via `allaboutcircuits.com/technical-articles/{slug}/` | EXCELLENT |
| Nexperia App Notes | HTML interactive notes or PDF via `assets.nexperia.com/...` | MIXED |
| ST App Notes | PDF via `st.com/resource/en/application_note/{filename}.pdf` | GOOD -- website is JS-heavy, direct PDF only |
| Murata Articles | HTML via `article.murata.com/en-us/article/{slug}` | HIGH |
| Infineon App Notes | PDF via `infineon.com/assets/row/public/documents/...` | MEDIUM-HIGH |
| Altium Resources | HTML via `resources.altium.com/p/{slug}` | EXCELLENT -- well-structured articles, many by Lee Ritchey and Zachariah Peterson |
| LearnEMC | HTML via `learnemc.com/{topic}` | EXCELLENT -- Dr. Todd Hubing, gold standard for free EMC education |
| Henry Ott Consultants | HTML via `hott.shielddigitaldesign.com/techtips/{slug}.html` | EXCELLENT -- lightweight HTML, the EMC authority |
| Sierra Circuits | HTML via `protoexpress.com/blog/{slug}` or `/kb/{slug}` | EXCELLENT -- manufacturer perspective with concrete numbers |

> **Format policy:** Strongly prefer HTML sources over PDFs. PDF extraction via pdfplumber is adequate but loses table structure and figure context. HTML extracts cleanly with no artifacts. When adding new sources, always check if an HTML version exists before falling back to PDF.

---

## guides/passives.md

Covers: ceramic cap voltage derating, dielectric selection (C0G/X5R/X7R), resistor power by package, inductor Isat vs Irms, tolerance stacking, package selection, LED current limiting, ferrite bead selection and filtering.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Murata -- DC Bias Voltage Characteristics | HTML | `https://article.murata.com/en-us/article/voltage-characteristics-of-electrostatic-capacitance` |
| 2 | Murata -- Temperature Characteristics of MLCCs | HTML | `https://article.murata.com/en-us/article/temperature-characteristics-electrostatic-capacitance` |
| 3 | ADI Tutorial 5527 -- Why Your 4.7uF Becomes 0.33uF | HTML | `https://www.analog.com/en/resources/technical-articles/temperature-and-voltage-variation-ceramic-capacitor.html` |
| 4 | Coilcraft Doc 1287 -- Introduction to Inductor Specifications | PDF 2pp | `https://www.coilcraft.com/getmedia/ac56eabb-8678-4ca2-9604-c609886d68c1/doc1287_inductor_specifications.pdf` |
| 5 | Wurth ANP039 -- Power Inductors 8 Design Tips | PDF 6pp | `https://www.we-online.com/components/media/o109038v410%20AppNotes_ANP039_PowerInductors8DesignTipps_EN.pdf` |
| 6 | TI SLVA450B -- Voltage Divider Resistor Selection | PDF 10pp | `https://www.ti.com/lit/pdf/slva450` |
| 7 | Vishay -- Thermal Management for SMD Resistors | PDF 4pp | `https://www.vishay.com/docs/30380/terminalderating.pdf` |
| 8 | SparkFun -- Resistors: Example Applications (LED Current Limiting) | HTML | `https://learn.sparkfun.com/tutorials/resistors/example-applications` |
| 9 | ADI AN-1368 -- Ferrite Bead Demystified | HTML | `https://www.analog.com/en/resources/app-notes/an-1368.html` |
| 10 | Abracon -- Ferrite Beads: Basic Operations and Key Parameters | PDF 9pp | `https://abracon.com/uploads/resources/Ferrite-Beads-White-Paper.pdf` |
| 11 | AllAboutCircuits -- Choosing and Using Ferrite Beads | HTML | `https://www.allaboutcircuits.com/technical-articles/choosing-and-using-ferrite-beads/` |
| 12 | EmbeddedRelated -- Tolerance Analysis (Jason Sachs) | HTML | `https://www.embeddedrelated.com/showarticle/1353.php` |
| 13 | Johanson Dielectrics -- Ceramic Capacitor Aging Made Simple | HTML | `https://www.johansondielectrics.com/tech-notes/ceramic-capacitor-aging-made-simple/` |

---

## guides/connectors.md

Covers: JST SH/PH/XH selection, USB connector types, terminal blocks vs headers vs barrel jacks, FPC/FFC, current ratings, mechanical considerations, connector family disambiguation.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | SparkFun -- Connector Basics Tutorial | HTML | `https://learn.sparkfun.com/tutorials/connector-basics` |
| 2 | AllAboutCircuits -- How to Select DC Power Connectors | HTML | `https://www.allaboutcircuits.com/industry-articles/how-to-select-dc-power-connectors-the-basics/` |
| 3 | TE Connectivity -- Terminal Blocks Selection Guide | PDF 12pp | `https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=1654690_TBlocks_Selection_Guide&DocType=DS&DocLang=English` |
| 4 | Eaton -- How to Select a Terminal Block | PDF 6pp | `https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/brochure/eaton-how-to-select-terminal-block-white-paper.pdf` |
| 5 | Hackaday -- Friendly Flexible Circuits: The Cables | HTML | `https://hackaday.com/2024/02/07/friendly-flexible-circuits-the-cables/` |
| 6 | Hackaday -- JST Is Not A Connector | HTML | `https://hackaday.com/2017/12/27/jst-is-not-a-connector/` |

---

## guides/power-architecture.md

Covers: multi-rail planning, LDO vs buck decision tree, power budget, enable/power-good sequencing, inrush current.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ADI -- Multirail Power Supply Design Part 1: Strategy | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/multirail-power-supply-design-for-successful-application-boards-part1.html` |
| 2 | ADI AN-140 -- Linear vs Switching Regulators | HTML | `https://www.analog.com/en/resources/app-notes/an-140.html` |
| 3 | ADI -- Multirail Power Supply Design Part 2: Power Budgeting + Layout | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/multirail-power-supply-design-for-successful-application-boards-part2.html` |
| 4 | ADI AN-1311 -- Power Supply Sequencing | HTML | `https://www.analog.com/en/resources/app-notes/an-1311.html` |
| 5 | TI SLDA039B -- PMIC Power Management Design Guide | PDF 11pp | `https://www.ti.com/lit/sg/slda039b/slda039b.pdf` |
| 6 | ADI -- Supply Topology Selection for Processors/MCUs | HTML | `https://www.analog.com/en/resources/technical-articles/supply-topology-high-power.html` |
| 7 | TI SLVA670A -- Managing Inrush Current | PDF 13pp | `https://www.ti.com/lit/an/slva670a/slva670a.pdf` |

---

## guides/thermal.md

Covers: LDO thermal estimation, junction temp calculation, theta-JA vs theta-JC vs psi-JT (and why theta-JA is misused), thermal pad design, thermal via sizing, PCB copper as heatsink, Cauer vs Foster thermal models, heatsink selection with worked example.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SLVA118A -- LDO Regulator Design Guide | PDF 25pp | `https://www.ti.com/lit/an/slva118a/slva118a.pdf` |
| 2 | TI SPRA953C -- Semiconductor/IC Package Thermal Metrics | PDF 15pp | `https://www.ti.com/lit/an/spra953c/spra953c.pdf` |
| 3 | TI SLMA002H -- PowerPAD Thermally Enhanced Package | PDF 31pp | `https://www.ti.com/lit/pdf/slma002` |
| 4 | TI SNVA183B -- Board Layout for Best Thermal Resistance | PDF 15pp | `https://www.ti.com/lit/an/snva183b/snva183b.pdf` |
| 5 | ADI -- Maximize Power Capability in Thermal Design Part 1 | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/maximize-power-capability-in-thermal-design-part-1.html` |
| 6 | ADI AN-140 -- Linear vs Switching Regulators | HTML | `https://www.analog.com/en/resources/app-notes/an-140.html` |
| 7 | TI SLVA462 -- Heatsink Design and Selection | PDF 4pp | `https://www.ti.com/lit/an/slva462/slva462.pdf` |
| 8 | TI SLUP239A -- Understanding LDO Regulators | PDF 9pp | `https://www.ti.com/lit/ml/slup239/slup239.pdf` |
| 9 | Nexperia AN90003 -- LFPAK MOSFET Thermal Design Guide | PDF 53pp | `https://assets.nexperia.com/documents/application-note/AN90003.pdf` |
| 10 | Infineon AN2015-10 -- Transient Thermal Measurements and Thermal Equivalent Circuit Models | PDF 11pp | `https://www.infineon.com/dgdl/Infineon-AN2015_10_Thermal_equivalent_circuit_models-AN-v01_00-EN.pdf?fileId=db3a30431a5c32f2011aa65358394dd2` |
| 11 | ROHM 65AN114E -- theta-JA and psi-JT (Thermal Characterization Parameters) | PDF 7pp | `https://fscdn.rohm.com/en/products/databook/applinote/common/theta_ja_and_psi_jt_an-e.pdf` |
| 12 | Same Sky -- How to Select a Heat Sink (Worked Example) | HTML | `https://www.sameskydevices.com/blog/how-to-select-a-heat-sink` |

**Cross-ref:** ADI AN-140 also cited in `guides/power-architecture.md` #2 and `power/switching.md` #1.

---

## guides/schematic-practices.md

Covers: schematic readability (signal flow, power symbol orientation), net naming conventions, hierarchical design, off-sheet connectors (ports vs net labels), sheet organization, title blocks, annotation, component/footprint naming standards.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Altium -- Easy Schematics Creation for Elegance and Readability | HTML | `https://resources.altium.com/p/creating-elegant-and-readable-schematics` |
| 2 | Altium -- The Anatomy of Your Schematic Netlist, Ports, and Net Names | HTML | `https://resources.altium.com/p/anatomy-your-schematic-netlist-ports-and-net-names` |
| 3 | Altium -- Hierarchical Block Diagrams and Schematic Designs | HTML | `https://resources.altium.com/p/how-hierarchical-schematic-design-can-help-your-next-pcb-schematic-layout` |
| 4 | Sierra Circuits -- How to Draw and Design a PCB Schematic | HTML | `https://www.protoexpress.com/blog/how-to-draw-design-pcb-schematic/` |
| 5 | Cadence -- Best Practices for Capturing Circuit Board Schematics | HTML | `https://resources.pcb.cadence.com/blog/2021-best-practices-for-capturing-circuit-board-schematics` |
| 6 | SparkFun -- How to Read a Schematic | HTML | `https://learn.sparkfun.com/tutorials/how-to-read-a-schematic/all` |
| 7 | Altium -- Naming Convention and PCB Data Management | HTML | `https://resources.altium.com/p/naming-convention-and-pcb-data-management` |

**Key teaching points:** #1 is the best single article on schematic readability (signal flow left-to-right, power up/GND down, uppercase net names). #2 explains when to use net labels vs ports for off-sheet connections. #3 covers hierarchical design for repeated blocks and team design. #4 is the most comprehensive single guide (20+ guidelines including alphabetical page naming, IEEE ref designators, title blocks). #5 covers the capture workflow (tool setup, library management, DRC, layout handoff). #6 is the best symbol literacy tutorial. #7 covers IPC-7351 naming conventions.

---

## guides/checklist.md

Covers: pre-build schematic review checklist, PCB layout checklist, DFM rules, IPC standards.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | pcbchecklist.com (Henrik Hansen) -- Most exhaustive | HTML + GitHub | `https://pcbchecklist.com/` |
| 2 | azonenberg/pcb-checklist -- Schematic checklist | Markdown | `https://raw.githubusercontent.com/azonenberg/pcb-checklist/master/schematic-checklist.md` |
| 3 | azonenberg/pcb-checklist -- Layout checklist | Markdown | `https://raw.githubusercontent.com/azonenberg/pcb-checklist/master/layout-checklist.md` |
| 4 | Altium -- Schematic Design Review Checklist | HTML | `https://resources.altium.com/p/schematic-review-checklist` |
| 5 | grosdode/PCB-design -- Prototyping & Bring-up Checklist | Markdown | `https://raw.githubusercontent.com/grosdode/PCB-design/main/PCB_Checklist/pcb_checklist.md` |
| 6 | Sierra Circuits -- IPC-2221 Standards Reference | HTML | `https://www.protoexpress.com/blog/ipc-2221-circuit-board-design/` |
| 7 | Sierra Circuits -- DFM Rules | HTML | `https://www.protoexpress.com/kb/dfm-rules/` |
| 8 | Espressif ESP32-S3 HW Design Guidelines -- Schematic Checklist | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html` |
| 9 | Espressif ESP32-S3 HW Design Guidelines -- PCB Layout Design | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html` |

**Note on #8-9:** Best-in-class real-world checklist examples. The schematic checklist covers power supply, decoupling, crystal, RF matching, strapping, GPIO default states, ADC calibration, USB routing -- all with specific component values. The PCB layout page covers 4-layer stackup, trace width minimums, impedance targets (50 ohm single-ended, 90 ohm USB diff), crystal/RF keep-out zones, via stitching, and a troubleshooting section. General PCB design knowledge despite being ESP32-specific.

---

## guides/pcb-layout.md

Covers: ground planes and return paths, PCB stackup design (2/4/6/8-layer), layer assignment, microstrip vs stripline, trace width and current capacity (IPC-2152), via types and current capacity, stitching vias, annular ring, thermal relief. **This is the foundational PCB design file.**

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | LearnEMC -- Identifying Current Paths | HTML | `https://learnemc.com/identifying-current-paths` |
| 2 | LearnEMC -- Some of the Worst EMC Design Guidelines | HTML | `https://learnemc.com/some-of-the-worst-emc-design-guidelines` |
| 3 | Henry Ott -- Grounding of Mixed Signal PCBs | HTML | `https://hott.shielddigitaldesign.com/techtips/split-gnd-plane.html` |
| 4 | Henry Ott -- PCB Stack-Up Part 1: Introduction | HTML | `https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-1.html` |
| 5 | Henry Ott -- PCB Stack-Up Part 2: Four-Layer Boards | HTML | `https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-2.html` |
| 6 | Altium -- How to Design the Best 4-Layer PCB Stackup | HTML | `https://resources.altium.com/p/4-layer-pcb-stackup` |
| 7 | ADI MT-094 -- Microstrip and Stripline Design | PDF 7pp | `https://www.analog.com/media/en/training-seminars/tutorials/mt-094.pdf` |
| 8 | Altium -- Stripline vs Microstrip: Differences and Routing Guidelines | HTML | `https://resources.altium.com/p/stripline-vs-microstrip-understanding-their-differences-and-their-pcb-routing-guidelines` |
| 9 | SMPS.us -- IPC-2152 Trace Width Calculator and Equations | HTML | `https://www.smps.us/pcb-calculator.html` |
| 10 | Sierra Circuits -- How to Design a Via with Current Carrying Capacity | HTML | `https://www.protoexpress.com/blog/how-to-design-via-with-current-carrying-capacity/` |
| 11 | San Francisco Circuits -- PCB Via Types Guide (8 Types) | HTML | `https://www.sfcircuits.com/pcb-school/pcb-via-types` |
| 12 | Altium -- Everything You Need to Know About Stitching Vias | HTML | `https://resources.altium.com/p/everything-you-need-know-about-stitching-vias` |
| 13 | Sierra Circuits -- Annular Ring Explained by a PCB Manufacturer | HTML | `https://www.protoexpress.com/blog/dont-let-annular-rings-drive-you-crazy/` |
| 14 | Altium -- Thermal Relief Design Guide | HTML | `https://resources.altium.com/p/thermal-relief-design` |

**Key teaching points:** #1 is THE foundation (return current behavior at DC vs HF). #2-3 are essential anti-patterns (why ground plane splits are almost always wrong). #4-6 cover stackup from theory to practice. #7-8 are impedance formulas. #9-14 are physical design rules with hard numbers.

---

## guides/signal-integrity.md

Covers: when a trace becomes a transmission line, characteristic impedance, reflections and termination strategies (series, parallel, AC, Thevenin), crosstalk (NEXT/FEXT), differential pairs, rise time and bandwidth, practical "when to care" rules.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Altium -- The Ultimate Introduction to High-Speed Signal Integrity | HTML | `https://resources.altium.com/p/introduction-to-high-speed-signal-integrity-for-pcb-designers` |
| 2 | Altium -- Why is There a Transmission Line Critical Length? | HTML | `https://resources.altium.com/p/why-there-transmission-line-critical-length` |
| 3 | Altium/Lee Ritchey -- Transmission Line Termination Techniques | HTML | `https://resources.altium.com/p/transmission-lines-and-terminations-in-high-speed-design` |
| 4 | Altium/Phil's Lab -- High-Speed PCB Design Tips and Guidelines | HTML | `https://resources.altium.com/p/high-speed-pcb-design-tips` |
| 5 | Altium/Lee Ritchey -- Crosstalk or Coupling in High-Speed Design | HTML | `https://resources.altium.com/p/crosstalk-or-coupling` |
| 6 | Sierra Circuits -- Differential Pairs in PCB Transmission Lines | HTML | `https://www.protoexpress.com/blog/differential-pairs-in-pcb-transmission-lines/` |
| 7 | Sierra Circuits -- Handling Crosstalk in High-Speed PCB Designs | HTML | `https://www.protoexpress.com/blog/crosstalk-high-speed-pcb-design/` |
| 8 | Intel -- Basic Principles of Signal Integrity | PDF 4pp | `https://cdrdv2-public.intel.com/650327/wp_sgnlntgry.pdf` |
| 9 | ADI -- A Short Course in PCB Layout for High-Speed ADCs | HTML | `https://www.analog.com/en/resources/technical-articles/a-short-course-in-pcb-layout-for-high-speed-adcs.html` |

**Key teaching points:** #1 is the best single-page SI overview. #2 debunks the 1/4 rise time myth. #3 covers all 5 termination types. #4 has the f_knee = 0.35/t_rise formula and 3h spacing rule. #5 debunks guard traces. #8 covers ground bounce in just 4 pages.

---

## guides/emc.md

Covers: EMC basics (source-path-receptor), conducted vs radiated emissions, common-mode vs differential-mode noise, filtering (pi filters, CM chokes, X/Y caps), shielding, PCB layout for EMC, SMPS hot loops, slot antennas, compliance awareness (CE/FCC).

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | LearnEMC -- Introduction to Printed Circuit Board Layout for EMC | HTML | `https://learnemc.com/pcb-layout` |
| 2 | LearnEMC -- Introduction to Electromagnetic Compatibility | HTML | `https://learnemc.com/introduction-to-emc` |
| 3 | LearnEMC -- An Introduction to Grounding for EMC | HTML | `https://learnemc.com/grounding` |
| 4 | LearnEMC -- Introduction to Common-Mode Filtering | HTML | `https://learnemc.com/cm-filtering` |
| 5 | LearnEMC -- Plane-Wave Shielding Theory | HTML | `https://learnemc.com/shielding-theory` |
| 6 | LearnEMC -- Practical Electromagnetic Shielding | HTML | `https://learnemc.com/practical-em-shielding` |
| 7 | TI SZZA009 -- PCB Design Guidelines for Reduced EMI | PDF 23pp | `https://www.ti.com/lit/an/szza009/szza009.pdf` |
| 8 | ADI AN-139 -- Power Supply Layout and EMI | HTML | `https://www.analog.com/en/resources/app-notes/an-139.html` |

**Key teaching points:** #1 is the single best free EMC PCB layout resource (10-step review checklist). #3 teaches "ground is NOT a current return path." #4 covers CM vs DM filtering systematically. #5-6 cover shielding math + practice. #7 is uniquely practical for 2-layer boards (ground gridding). #8 shows SMPS hot loops for buck/boost/SEPIC/flyback.

---

## guides/dfm.md

Covers: PCB manufacturing constraints (trace/space, drill, annular ring, solder mask), assembly rules (component spacing, orientation, tombstoning), IPC class 2 vs 3, panelization, fiducials, fab house capabilities (JLCPCB, PCBWay, OSHPark).

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | JLCPCB -- PCB Design Rules and Guidelines: Complete Best Practices | HTML | `https://jlcpcb.com/blog/pcb-design-rules-best-practices` |
| 2 | PCBWay -- PCB Manufacturing Tolerances | HTML | `https://www.pcbway.com/pcb_prototype/PCB_Manufacturing_Tolerances.html` |
| 3 | OSH Park -- Fabrication Services and Design Rules | HTML | `https://docs.oshpark.com/services/` |
| 4 | Sierra Circuits -- DFA Rules | HTML | `https://www.protoexpress.com/kb/dfa-rules/` |
| 5 | Sierra Circuits -- IPC Class 2 vs Class 3: Different Design Rules | HTML | `https://www.protoexpress.com/blog/ipc-class-2-vs-class-3-different-design-rules/` |
| 6 | Eurocircuits -- Tombstoning: PCB Assembly Guidelines | HTML | `https://www.eurocircuits.com/technical-guidelines/pcb-assembly-guidelines/tombstoning/` |
| 7 | Altium -- Complete Guide to DFM Analysis | HTML | `https://resources.altium.com/p/complete-guide-dfm-analysis` |
| 8 | Sierra Circuits -- Panel Requirements for PCB Assembly | HTML | `https://www.protoexpress.com/kb/panel-requirements-for-pcb-assembly/` |

**Key teaching points:** #1-3 are the actual design rules for the three most common fab houses. #4 has an 8x8 component spacing matrix. #5 has IPC class comparison with concrete tables. #6 covers tombstoning root causes -- rare practical knowledge. #7 teaches the DFM workflow (when to check during design). #8 covers panelization, fiducials, and tooling holes.

**Cross-ref:** Sierra Circuits DFM Rules also listed in `guides/checklist.md` #7.

---

## guides/test-debug.md

Covers: DFT guidelines for PCB manufacturing, board bring-up procedure, current shunt pad layout, ARM Cortex-M debug connectors (SWD/JTAG), test point sizing and placement, ICT/DFT bed-of-nails design, PCB prototype testing checklist.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | MacroFab -- Improve Your Next PCB Prototype: Better Debugging, Testing, and Reliability | HTML | `https://www.macrofab.com/blog/improve-pcb-prototype/` |
| 2 | Practical EE -- Bringup | HTML | `https://practicalee.com/bringup/` |
| 3 | ADI -- Optimize High-Current Sensing Accuracy by Improving Pad Layout of Low-Value Shunt Resistors | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/optimize-high-current-sensing-accuracy.html` |
| 4 | Sierra Circuits -- Design for Testing (DFT) Guidelines for PCB Manufacturing | HTML | `https://www.protoexpress.com/blog/design-for-testing-guidelines-pcb-manufacturing/` |
| 5 | ARM -- Cortex-M Debug Connectors (10-pin and 20-pin pinouts) | PDF 5pp | `https://documentation-service.arm.com/static/5fce6c49e167456a35b36af1` |
| 6 | Memfault -- A Deep Dive into ARM Cortex-M Debug Interfaces | HTML | `https://interrupt.memfault.com/blog/a-deep-dive-into-arm-cortex-m-debug-interfaces` |
| 7 | FixturFab -- Basic PCBA Design for Test (DFT) Guide | HTML | `https://www.fixturfab.com/articles/basic-pcba-design-test-dft-guide` |
| 8 | TI SDAA115 -- Optimal Layout Practices for Low-Ohmic Current Sense Resistors in Parallel | PDF 11pp | `https://www.ti.com/lit/an/sdaa115/sdaa115.pdf` |
| 9 | Altium -- Checklist for Systematically Testing PCB Prototypes | HTML | `https://resources.altium.com/p/checklist-systematically-testing-pcb-prototypes` |

**Key teaching points:** #1 is the best single source (debug headers, LEDs, test pads, power jumpers, board partitioning). #2 is a step-by-step bring-up procedure with photos of real defects. #3 shows 5 Kelvin-sense pad layouts with measured accuracy data. #4 covers test point sizing (6mil min, 20mil recommended) from a manufacturer's perspective. #5 is the official ARM pinout reference for 10-pin and 20-pin Cortex debug connectors. #6 explains SWD vs JTAG at the protocol level with practical implementation details. #7 covers bed-of-nails ICT fixture design and DFT pad placement rules. #8 details optimal PCB pad layout for paralleled low-ohmic current sense resistors. #9 is a systematic checklist for testing PCB prototypes from power-on through functional verification.

---

## interfaces/i2c.md

Covers: pull-up calculation, bus capacitance, speed modes, address conflicts, multi-device loading, level shifting, bus buffering, ESD protection, hung bus recovery.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SLVA689 -- I2C Bus Pullup Resistor Calculation | PDF 5pp | `https://www.ti.com/lit/pdf/slva689` |
| 2 | SparkFun -- I2C Tutorial | HTML | `https://learn.sparkfun.com/tutorials/i2c` |
| 3 | NXP AN10216 -- I2C Manual | PDF 51pp | `https://www.nxp.com/docs/en/application-note/AN10216.pdf` |
| 4 | Nexperia AN10441 -- Level Shifting Techniques in I2C-bus Design | PDF 5pp | `https://assets.nexperia.com/documents/application-note/AN10441.pdf` |
| 5 | TI SLVA787 -- Choosing the Correct I2C Device | PDF 12pp | `https://www.ti.com/lit/an/slva787/slva787.pdf` |
| 6 | Wurth ANP121 -- Filter and Surge Protection for I2C Bus | PDF 7pp | `https://www.we-online.com/components/media/o734709v410%20ANP121a%20%20Filter%20and%20surge%20protection%20for%20I2C%20Bus%20EN.pdf` |
| 7 | ADI AN-686 -- Implementing an I2C Reset | PDF 2pp | `https://www.analog.com/media/en/technical-documentation/application-notes/54305147357414AN686_0.pdf` |

---

## interfaces/spi.md

Covers: SPI modes (CPOL/CPHA), CS timing, multi-device buses, clock speed limits, series termination, signal integrity, SPI flash layout.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ADI AN-1248 -- SPI Interface Timing | HTML | `https://www.analog.com/en/resources/app-notes/an-1248.html` |
| 2 | TI SCAA082A -- High-Speed Layout Guidelines | PDF 21pp | `https://www.ti.com/lit/an/scaa082a/scaa082a.pdf` |
| 3 | Altium -- Is There an SPI Trace Impedance Requirement? | HTML | `https://resources.altium.com/p/there-spi-trace-impedance-requirement` |
| 4 | Practical EE -- SPI Bus | HTML | `https://practicalee.com/spi/` |
| 5 | Microchip AN2402 -- PCB Layout Guide (SPI Flash Section) | PDF 21pp | `https://ww1.microchip.com/downloads/en/AppNotes/00002402A.pdf` |
| 6 | Macronix AN-0251 -- Serial Flash Multi-I/O Introduction | PDF 12pp | `https://www.macronix.com/Lists/ApplicationNote/Attachments/1899/AN0251V1%20-%20Macronix%20Serial%20Flash%20Multi%20IO%20Introduction.pdf` |
| 7 | ADI -- Level Translators for SPI and I2C Bus Signals | HTML | `https://www.analog.com/en/resources/technical-articles/level-translators-for-spi8482-and-isup2c-bus-signals.html` |
| 8 | Espressif ESP32-S3 HW Design Guidelines -- PCB Layout (SPI/Flash Section) | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html` |

**Note on #9:** Espressif PCB layout SPI section covers general SPI flash layout best practices: route SPI traces on inner layers, octal SPI length matching, series resistor/ferrite bead + cap to ground on SPI_CLK for EMC, decoupling cap placement near flash IC.

---

## interfaces/uart.md

Covers: UART protocol, RS-232/RS-485 voltage levels, level shifting, flow control, baud rate tolerance, USB-to-UART bridge IC selection (CH340, FT232, CP2102), auto-reset circuits.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ADI -- Fundamentals of RS-232 Serial Communications | HTML | `https://www.analog.com/en/resources/technical-articles/fundamentals-of-rs232-serial-communications.html` |
| 2 | Silicon Labs AN0059 -- UART Flow Control | PDF 11pp | `https://www.silabs.com/documents/public/application-notes/an0059.0-uart-flow-control.pdf` |
| 3 | TI SLLA544 -- RS-232 FAQ | PDF 5pp | `https://www.ti.com/lit/an/slla544/slla544.pdf` |
| 4 | SparkFun -- Serial Communication Tutorial | HTML | `https://learn.sparkfun.com/tutorials/serial-communication` |
| 5 | TI SCEA064A -- Level Translation for SPI, UART, JTAG | PDF 9pp | `https://www.ti.com/lit/pdf/scea064` |
| 6 | ADI AN-960 -- RS-485/RS-422 Circuit Implementation Guide | HTML | `https://www.analog.com/en/resources/app-notes/an-960.html` |
| 7 | TI SLLA272 -- The RS-485 Design Guide | PDF 9pp | `https://www.ti.com/lit/pdf/slla272` |
| 8 | ADI -- Clock Accuracy Requirements for UART | HTML | `https://www.analog.com/en/resources/technical-articles/determining-clock-accuracy-requirements-for-uart-communications.html` |
| 9 | FTDI AN_146 -- USB Hardware Design Guidelines for FTDI ICs | PDF 15pp | `https://ftdichip.com/wp-content/uploads/2020/08/AN_146_USB_Hardware_Design_Guidelines_for_FTDI_ICs.pdf` |
| 10 | Kazulog -- ESP32 Auto Bootloader Mechanism and Truth Table | HTML | `https://kazulog.fun/en/dev-en/esp32-auto-bootloader/` |

---

## interfaces/usb.md

Covers: USB 2.0 data line routing (90 ohm differential impedance, D+/D- length matching, series resistors, DP pull-up), USB-C CC resistors and PD negotiation, VBUS power path and protection, ESD on data lines, connector footprint guidelines.

### USB 2.0 Data Routing

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Embedded Hardware Design -- USB 2.0 PCB Layout Guidelines | HTML | `https://embeddedhardwaredesign.com/usb2-0-pcb-layout-guidelines/` |
| 2 | Silicon Labs AN0046 -- USB Hardware Design Guidelines | PDF 21pp | `https://www.silabs.com/documents/public/application-notes/an0046-efm32-usb-hardware-design-guidelines.pdf` |
| 3 | TI SPRABT8A -- AM335x USB Layout Guidelines | PDF 13pp | `https://www.ti.com/lit/an/sprabt8a/sprabt8a.pdf` |
| 4 | TI SWCA124 -- TUSB121x USB 2.0 Board Guidelines | PDF 4pp | `https://www.ti.com/lit/pdf/swca124` |
| 5 | FTDI AN_146 -- USB Hardware Design Guidelines for FTDI ICs | PDF 15pp | `https://ftdichip.com/wp-content/uploads/2020/08/AN_146_USB_Hardware_Design_Guidelines_for_FTDI_ICs.pdf` |

**Key teaching points:** #1 is the best single source (vendor-independent, eye diagrams showing degradation from bad routing, complete checklist). #2 has the best physics explanation (critical length, skew budget calculation, DP pull-up for device mode). #3 has unique 3W/5W spacing rules and image plane guidance. #4 is a dense 20-rule cheat sheet with exact numbers (5cm optimal trace, 150mil max mismatch, 4pF max external cap, 20*h edge clearance). #5 covers series resistor purpose (edge rate control) and is dual-cited from `interfaces/uart.md`.

### USB Type-C and Power Delivery

| # | Source | Format | URL |
|---|--------|--------|-----|
| 6 | Espressif -- USB Type-C Hardware Design Guide | HTML | `https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_typec_hardware_guide.html` |
| 7 | TI SLYY109 -- USB Type-C Primer | PDF 14pp | `https://www.ti.com/lit/pdf/slyy109` |
| 8 | Benson Leung -- How to Design a Proper USB-C Power Sink | HTML | `https://medium.com/@leung.benson/how-to-design-a-proper-usb-c-power-sink-hint-not-the-way-raspberry-pi-4-did-it-f470d7a5910` |
| 9 | Dubious Creations -- Designing with USB-C: Lessons Learned | HTML | `https://dubiouscreations.com/2021/04/06/designing-with-usb-c-lessons-learned/` |
| 10 | Hackaday -- All About USB-C: Resistors and Emarkers | HTML | `https://hackaday.com/2023/01/04/all-about-usb-c-resistors-and-emarkers/` |
| 11 | Hackaday -- All About USB-C: Example Circuits | HTML | `https://hackaday.com/2023/08/07/all-about-usb-c-example-circuits/` |
| 12 | onsemi AN-5086 -- USB Type-C CC Pin Design Considerations | PDF 5pp | `https://www.onsemi.com/pub/Collateral/AN-5086-D.PDF` |
| 13 | TI SLYY145 -- USB Type-C and USB PD Power Path Design Considerations | PDF 8pp | `https://www.ti.com/lit/slyy145` |
| 14 | TI SLVA994 -- USB PD Power Path Performance and Protection | PDF 23pp | `https://www.ti.com/lit/an/slva994/slva994.pdf` |
| 15 | Wurth ANE009 -- Production Guide USB 3.1 Type C (Connector Footprint) | PDF 17pp | `https://www.we-online.com/components/media/o563289v410%20ANE009a_EN.pdf` |
| 16 | TI SLVAE65 -- Dead Battery Application (TPS6598x) | PDF 6pp | `https://www.ti.com/lit/an/slvae65/slvae65.pdf` |

---

## interfaces/can.md

Covers: CAN 2.0/FD physical layer, transceiver selection and comparison, termination (standard and split), PCB layout, ESD protection, EMC performance, CAN FD hardware design.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SLLA337 -- Overview of 3.3V CAN Transceivers | HTML | `https://www.ti.com/document-viewer/lit/html/SLLA337` |
| 2 | TI SSZTAM0 -- How Termination CAN Improve EMC Performance | HTML | `https://www.ti.com/document-viewer/lit/html/SSZTAM0` |
| 3 | TI SLVAFC1 -- CAN Bus ESD Protection | HTML | `https://www.ti.com/document-viewer/lit/html/SLVAFC1` |
| 4 | TI SLLA270 -- Controller Area Network Physical Layer Requirements | PDF 15pp | `https://www.ti.com/lit/pdf/SLLA270` |
| 5 | TI SLLA271 -- Common-Mode Chokes in CAN Networks: Source of Unexpected Transients | PDF 7pp | `https://www.ti.com/lit/pdf/SLLA271` |
| 6 | TI SLLA486 -- Top Design Questions About Isolated CAN Bus Design | HTML | `https://www.ti.com/document-viewer/lit/html/SLLA486` |
| 7 | Microchip AN228 -- A CAN Physical Layer Discussion | PDF 12pp | `https://ww1.microchip.com/downloads/en/appnotes/00228a.pdf` |
| 8 | Altium -- Designing CAN-Bus Circuitry: CAN-Bus PCB Layout Guidelines | HTML | `https://resources.altium.com/p/can-bus-designing-can-bus-circuitry` |
| 9 | Microchip ATAN0103 -- ATA6560/ATA6561 CAN FD Transceiver Application Note | PDF 17pp | `https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ApplicationNotes/ApplicationNotes/Atmel-9310-ATA6560-EK-ATA6561-EK_Application-Note.pdf` |

**Cross-ref:** ST AN5878 (How to Design a Robust Automotive CAN System) already cited in `misc/ev-power-systems.md` #10 — covers automotive CAN bus termination, transceiver selection, and EMC/ESD from an EV systems perspective. For ESD protection fundamentals → see `protection/esd.md`. For isolated CAN in BMS applications → see `protection/isolation.md` #1 (SLLA284).

**Key teaching points:** #1 explains 3.3V/5V transceiver interoperability and split termination with scope captures. #2 is the deep-dive on split termination EMC benefits (2x CM noise reduction with measurements). #3 covers ESD diode selection criteria (working voltage, IEC 61000-4-2, capacitance budget). #4 is the definitive physical layer reference (bus length vs rate, cables, connectors, stubs, chokes, isolation). #5 is a critical "gotcha" — CMC inductive flyback can generate 65V+ transients; covers protector placement and choke selection. #6 addresses isolated CAN nodes (when to isolate, software-controlled termination).

---

## interfaces/ethernet.md

Covers: Ethernet PHY layout, magnetics selection (Bob Smith termination, CMRR, impedance), Gigabit Ethernet front-end design, PoE PD and PSE design, EMC optimization, schematic review guidelines.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SNLA387 -- Ethernet PHY Design Checklist | HTML | `https://www.ti.com/document-viewer/lit/html/SNLA387` |
| 2 | TI SNLA079 (AN-1469) -- PHYTER Design and Layout Guide | PDF 16pp | `https://www.ti.com/lit/pdf/snla079` |
| 3 | Microchip -- LAN8720A QFN Schematic Checklist | PDF 18pp | `https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/SupportingCollateral/LAN8720AQFNRevDSchematicChecklist.pdf` |
| 4 | Microchip -- LAN8720 QFN Routing Checklist | PDF 15pp | `https://ww1.microchip.com/downloads/en/DeviceDoc/LAN8720_QFN_Rev_A_Routing_Checklist.pdf` |
| 5 | WIZnet -- W5500 Hardware Design Guide | HTML | `https://docs.wiznet.io/Design-Guide/hardware_design_guide` |
| 6 | TI SLVAF59 -- PoE PD Schematic Review Guidelines | HTML | `https://www.ti.com/document-viewer/lit/html/SLVAF59` |
| 7 | TI SNLA466 -- Optimizing EMC Performance in Industrial Ethernet Applications | HTML | `https://www.ti.com/document-viewer/lit/html/SNLA466` |
| 8 | Embedded Hardware Design -- Selecting the Right Ethernet Magnetics | HTML | `https://embeddedhardwaredesign.com/selecting-the-right-ethernet-magnetics/` |
| 9 | Wurth Elektronik RD016 -- Gigabit-Ethernet Front End Reference Design | PDF 11pp | `https://www.we-online.com/components/media/o721295v410%20RD016a%20EN.pdf` |
| 10 | Microchip AN3580 -- Designing 1-port PoE System Using PD69201 (PSE) | PDF 18pp | `https://ww1.microchip.com/downloads/aemDocuments/documents/POE/ApplicationNotes/ApplicationNotes/AN3580-Designing_1-port_PoE_System_Using_PD69201.pdf` |

**Cross-ref:** For general differential pair routing theory → see `guides/signal-integrity.md`. For ESD protection on Ethernet ports → see `protection/esd.md`. For PCB stackup and impedance control → see `guides/pcb-layout.md`.

**Key teaching points:** #1 is the universal Ethernet PHY design checklist (decoupling, MDI routing, magnetics keep-out, ground/earth isolation). #2 has the best impedance calculation formulas (microstrip/stripline) and the canonical Bob Smith termination explanation (75 ohm + 2kV cap). #3-4 are the gold standard LAN8720A references (pin-level schematic + routing, 49.9 ohm 1% TX/RX pull-ups, ferrite bead + 470pF + 1uF power filtering, 4-layer minimum stackup). #5 covers W5500 SPI-Ethernet with specific dimensions (<25mm transformer-to-RJ45, >=80mil chassis GND gap). #6 is a step-by-step PoE PD walkthrough (bridge selection for 13W/25W/51W/71W, 120nF max input cap for IEEE detection, TVS, DC-DC). #7 covers systematic EMC debug (CISPR 32 Class A/B, emission source isolation, CMC placement).

---

## power/decoupling.md

Covers: per-IC ceramic caps, bulk caps, same-value strategy, voltage derating, placement, via stitching, EMC considerations, MLCC parasitic inductance by package, self-resonant frequency, Class II aging.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SPRABV2 -- BGA Decoupling Best Practices | PDF 6pp | `https://www.ti.com/lit/an/sprabv2/sprabv2.pdf` |
| 2 | TI SLOA069 -- How (Not) to Decouple High-Speed Op Amps | PDF 14pp | `https://www.ti.com/lit/an/sloa069/sloa069.pdf` |
| 3 | Murata -- Voltage Characteristics of Ceramic Caps | HTML | `https://article.murata.com/en-us/article/voltage-characteristics-of-electrostatic-capacitance` |
| 4 | TI SLTA055 -- I/O Capacitor Selection for Regulators | PDF 11pp | `https://www.ti.com/lit/an/slta055/slta055.pdf` |
| 5 | ADI MT-101 -- Decoupling Techniques | PDF 14pp | `https://www.analog.com/media/en/training-seminars/tutorials/MT-101.pdf` |
| 6 | Wurth ANP098 -- Layout/Via Effects on Filter Capacitors | PDF 7pp | `https://www.we-online.com/components/media/o695199v410%20ANP098a%20EN.pdf` |
| 7 | LearnEMC -- PCB Decoupling Guidelines | HTML | `https://learnemc.com/circuit-board-decoupling-information` |
| 8 | Kyocera AVX -- Parasitic Inductance of Multilayer Ceramic Capacitors | PDF 5pp | `https://kyocera-avx.com/docs/techinfo/CeramicCapacitors/parasitc.pdf` |
| 9 | Vishay -- Time-Dependent Capacitance Drift of X7R MLCCs Under DC Bias | PDF 6pp | `https://www.vishay.com/docs/45263/timedepcapdrix7rmlccexptoconstdcbiasvolt.pdf` |
| 10 | Johanson Dielectrics -- Ceramic Capacitor Aging Made Simple | HTML | `https://www.johansondielectrics.com/tech-notes/ceramic-capacitor-aging-made-simple/` |
| 11 | Espressif ESP32-S3 HW Design Guidelines -- PCB Layout (Power Section) | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html` |

**Note on #13:** Espressif PCB layout power section is a concise, practical general reference: min trace widths (25mil main, 20mil secondary, 10mil branch), star topology, decoupling cap placement near pins, 0201 component sizing for filter circuits, ESD diode placement. Applicable beyond ESP32.

---

## power/ldo.md

Covers: dropout voltage, ESR stability, ceramic vs electrolytic, thermal limits, I/O cap requirements, PSRR, noise, reverse current protection, transient/load-step response, quiescent current, startup/soft-start, enable pin sequencing.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SLVA079 -- LDO Terms and Definitions | PDF 13pp | `https://www.ti.com/lit/an/slva079/slva079.pdf` |
| 2 | ADI -- Comprehensive Guide to LDO Regulators | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/a-comprehensive-guide-to-ldo-regulators.html` |
| 3 | ADI AN-1120 -- Noise Sources in LDO Regulators | HTML | `https://www.analog.com/en/resources/app-notes/an-1120.html` |
| 4 | TI SLVA115A -- ESR, Stability, and the LDO | PDF 7pp | `https://www.ti.com/lit/an/slva115a/slva115a.pdf` |
| 5 | ROHM -- Reverse Current Protection Diodes for LDOs | PDF 6pp | `https://fscdn.rohm.com/en/products/databook/applinote/common/how_to_choose_reverse_current_protection_diode_for_ldo_an-e.pdf` |
| 6 | Microchip AN6030 -- LDO Basics: Parameters and Measurements | PDF 18pp | `https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ApplicationNotes/ApplicationNotes/AN6030-LDO-Basics-Parameter-Definitions-Measurements-and-Calculations-DS00006030.pdf` |
| 7 | TI SLYT151 -- Understanding the Load-Transient Response of LDOs | PDF 6pp | `https://www.ti.com/lit/an/slyt151/slyt151.pdf` |
| 8 | TI SBVA084 -- Increase Battery Life With Nano Quiescent Current LDO | PDF 6pp | `https://www.ti.com/lit/an/sbva084/sbva084.pdf` |
| 9 | TI SLVAFX0 -- Demystifying LDO Turn-On (Startup) Time | PDF 17pp | `https://www.ti.com/lit/wp/slvafx0/slvafx0.pdf` |
| 10 | ADI -- How to Successfully Apply Low-Dropout Regulators | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/applying-low-dropout-regulators.html` |

---

## power/switching.md

Covers: buck/boost/buck-boost topology, inductor selection, I/O cap selection, loop compensation, efficiency/losses, EMC layout.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ADI AN-140 -- Linear Reg & SMPS Basics | HTML | `https://www.analog.com/en/resources/app-notes/an-140.html` |
| 2 | TI SNVA559C -- Switching Regulator Fundamentals | PDF 29pp | `https://www.ti.com/lit/an/snva559c/snva559c.pdf` |
| 3 | TI SLVA477B -- Buck Converter Power Stage Design | PDF 8pp | `https://www.ti.com/lit/an/slva477b/slva477b.pdf` |
| 4 | TI SLVA372C -- Boost Converter Power Stage Design | PDF 10pp | `https://www.ti.com/lit/an/slva372c/slva372c.pdf` |
| 5 | TI SLVA535B -- 4-Switch Buck-Boost Power Stage | PDF 13pp | `https://www.ti.com/lit/an/slva535b/slva535b.pdf` |
| 6 | ADI AN-149 -- Loop Compensation Design | HTML | `https://www.analog.com/en/resources/app-notes/an-149.html` |
| 7 | Rohm -- Efficiency of Buck Converter (9 Loss Mechanisms) | PDF 16pp | `https://fscdn.rohm.com/en/products/databook/applinote/ic/power/switching_regulator/buck_converter_efficiency_app-e.pdf` |
| 8 | Wurth ANP039 -- Power Inductors 8 Design Tips | PDF 6pp | `https://www.we-online.com/components/media/o109038v410%20AppNotes_ANP039_PowerInductors8DesignTipps_EN.pdf` |
| 9 | TI SLTA055 -- I/O Capacitor Selection | PDF 11pp | `https://www.ti.com/lit/an/slta055/slta055.pdf` |
| 10 | Wurth DC/DC Handbook Extract -- SMPS from EMC POV | PDF 10pp | `https://www.we-online.com/components/media/o784081v410%20Extract-DCDC_Converter-1.0.pdf` |
| 11 | TI SNVA021C -- SMPS Layout Guidelines | PDF 5pp | `https://www.ti.com/lit/an/snva021c/snva021c.pdf` |

---

## power/battery-chemistry.md

Covers: Battery chemistry comparison (LiPo, Li-ion NMC/NCA/LCO, LiFePO4, NiMH, alkaline), voltage ranges and discharge curves, C-rate capabilities, cycle life and calendar aging, thermal runaway and safety, cell form factors (pouch, cylindrical, prismatic, coin), primary cells (Li-SOCl2, Li-MnO2, CR2032), chemistry selection criteria for embedded/IoT designs.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Battery University BU-205 -- Types of Lithium-ion | HTML | `https://www.batteryuniversity.com/article/bu-205-types-of-lithium-ion/` |
| 2 | Battery University -- What's the Best Battery? | HTML | `https://www.batteryuniversity.com/article/whats-the-best-battery/` |
| 3 | Battery University BU-501a -- Discharge Characteristics of Li-ion | HTML | `https://www.batteryuniversity.com/article/bu-501a-discharge-characteristics-of-li-ion/` |
| 4 | Battery University BU-808 -- How to Prolong Lithium-based Batteries | HTML | `https://www.batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries` |
| 5 | Battery University BU-301a -- Types of Battery Cells | HTML | `https://www.batteryuniversity.com/article/bu-301a-types-of-battery-cells/` |
| 6 | Battery University BU-106a -- Choices of Primary Batteries | HTML | `https://www.batteryuniversity.com/article/bu-106a-choices-of-primary-batteries/` |
| 7 | ADI -- Match the Battery to the Application | HTML | `https://www.analog.com/en/resources/technical-articles/match-the-battery-to-the-application-to-avoid-disappointment.html` |
| 8 | TI SWRA349 -- Coin Cells and Peak Current Draw | PDF 14pp | `https://www.ti.com/lit/an/swra349/swra349.pdf` |

---

## power/battery.md

Covers: Li-ion/LiPo CC/CV charging, charge current selection, NTC monitoring, battery protection ICs, switching charger topologies, temperature safety, fuel gauge ICs, state-of-charge estimation.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Microchip AN947 -- Li-Ion Charging Fundamentals | PDF 16pp | `https://ww1.microchip.com/downloads/en/AppNotes/00947a.pdf` |
| 2 | Battery University BU-409 -- Charging Lithium-ion | HTML | `https://www.batteryuniversity.com/article/bu-409-charging-lithium-ion/` |
| 3 | Battery University BU-410 -- Charging at High and Low Temperatures | HTML | `https://www.batteryuniversity.com/article/bu-410-charging-at-high-and-low-temperatures/` |
| 4 | Hackaday -- Lithium-Ion Battery Circuitry Is Simple | HTML | `https://hackaday.com/2022/10/10/lithium-ion-battery-circuitry-is-simple/` |
| 5 | ADI -- Practical Design Techniques: Battery Chargers | PDF 25pp | `https://www.analog.com/media/en/training-seminars/design-handbooks/Practical-Design-Techniques-Power-Thermal/Section5.pdf` |
| 6 | Vishay -- Fast Charging Control with NTC Temperature Sensing | PDF 4pp | `https://www.vishay.com/docs/29089/fastappl.pdf` |
| 7 | TI SLYP089 -- Design Trade-offs for Switch-Mode Battery Chargers | PDF 17pp | `https://www.ti.com/lit/ml/slyp089/slyp089.pdf` |
| 8 | TI SLUAAR3 -- Battery Gauging Algorithm Comparison | PDF 11pp | `https://www.ti.com/lit/SLUAAR3` |
| 9 | TI SLUA456 -- Single Cell Gas Gauge Circuit Design | PDF 6pp | `https://www.ti.com/lit/pdf/slua456` |
| 10 | OrionBMS Wiring & Installation Manual | PDF 57pp | `https://www.orionbms.com/manuals/pdf/wiring.pdf` |

**Cross-ref:** Precharge circuits for high-capacity packs → see `misc/ev-power-systems.md` #1-3. BMS cell tap wiring and sense line filtering → see `misc/ev-power-systems.md` #10.

**Key teaching points:** #10 addresses cell tap connector safety, wire routing away from high-current conductors, and verification procedures before connecting to BMS.

---

## power/power-path.md

Covers: USB + battery coexistence, ideal diode ORing, load disconnect, solar charging, DPM/DPPM, power MUX, MPPT.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ADI -- PowerPath Controllers/Ideal Diodes Primer | HTML | `https://www.analog.com/en/resources/technical-articles/primer-on-powerpath-controllers-ideal-diodes-prioritizers.html` |
| 2 | TI SLUA400A -- Dynamic Power-Path Management and DPM | PDF 8pp | `https://www.ti.com/lit/an/slua400a/slua400a.pdf` |
| 3 | TI SLVAE51A -- Basics of Power MUX | PDF 13pp | `https://www.ti.com/lit/an/slvae51a/slvae51a.pdf` |
| 4 | TI SLYT333 -- Linear Li-Ion Charger with Power-Path Control | PDF 9pp | `https://www.ti.com/lit/an/slyt333/slyt333.pdf` |
| 5 | ADI -- LTC4015 MPPT for Solar Panels | HTML | `https://www.analog.com/en/resources/technical-articles/multi-chemistry-battery-charger-supports-maximum-power-point-tracking.html` |
| 6 | TI SLUAAP0 -- Solar Battery Charger Selection | PDF 6pp | `https://www.ti.com/lit/an/sluaap0/sluaap0.pdf` |
| 7 | TI SLUA376 -- Battery Charger Power-Path Management | PDF 14pp | `https://www.ti.com/lit/an/slua376/slua376.pdf` |
| 8 | ADI -- LTC4412 Ideal Diode Controller | HTML | `https://www.analog.com/en/resources/technical-articles/ideal-diode-controller-eliminates-energy-wasting-diodes-in-power-or-ing-applications.html` |
| 9 | TI SLVA821 -- Implementing Ship Mode Using TPS22915B Load Switch | PDF 7pp | `https://www.ti.com/lit/an/slva821/slva821.pdf` |
| 10 | TI SSZT534 -- How to Implement Ship Mode in Li-ion Battery Design | PDF 5pp | `https://www.ti.com/lit/ta/sszt534/sszt534.pdf` |

---

## protection/esd.md

Covers: TVS selection, working voltage vs signal voltage, clamp voltage vs IC abs max, placement, PCB layout for ESD, USB-specific protection, latch-up.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SSZB130 -- System-Level ESD Protection Guide | PDF 25pp | `https://www.ti.com/lit/pdf/sszb130` |
| 2 | ST AN5241 -- ESD Protection Fundamentals | PDF 19pp | `https://www.st.com/resource/en/application_note/an5241-esd-protection-fundamentals-stmicroelectronics.pdf` |
| 3 | TI SLVAE37 -- How to Select a Surge Diode | PDF 9pp | `https://www.ti.com/lit/pdf/slvae37` |
| 4 | ROHM 66AN046E -- Selection Method and Usage of TVS Diodes | PDF 15pp | `https://fscdn.rohm.com/en/products/databook/applinote/discrete/diodes/selection_method_and_usage_of_tvs_diodes_an-e.pdf` |
| 5 | TI SLVA680A -- ESD Protection Layout Guide | PDF 11pp | `https://www.ti.com/lit/pdf/slva680` |
| 6 | ST AN5686 -- PCB Layout Tips for ESD Protection | PDF 17pp | `https://www.st.com/resource/en/application_note/an5686-pcb-layout-tips-to-maximize-esd-protection-efficiency-stmicroelectronics.pdf` |
| 7 | TI SLVAF82B -- ESD/Surge Protection for USB Interfaces | PDF 19pp | `https://www.ti.com/lit/pdf/slvaf82` |
| 8 | Nexperia AN90038 -- ESD for High-Speed Without Latch-Up | PDF 24pp | `https://assets.nexperia.com/documents/application-note/AN90038.pdf` |

---

## protection/reverse-polarity.md

Covers: P-FET vs Schottky vs ideal diode controller, selection criteria, eFuses, thermal analysis.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SLVAE57B -- Basics of Ideal Diodes | PDF 25pp | `https://www.ti.com/lit/pdf/slvae57` |
| 2 | ADI -- Low IQ Ideal Diode Controller (LTC4357/LTC4359) | HTML | `https://www.analog.com/en/resources/technical-articles/low-iq-ideal-diode-controller-with-reverse-input-protection.html` |
| 3 | EDN -- Protecting Against Reverse Polarity (Part 1) | HTML | `https://www.edn.com/protecting-against-reverse-polarity-methods-examined-part-1/` |
| 4 | EDN -- Protecting Against Reverse Polarity (Part 2) | HTML | `https://www.edn.com/protecting-against-reverse-polarity-methods-examined-part-2/` |
| 5 | onsemi AND90146 -- MOSFET Selection for RVP | PDF 11pp | `https://www.onsemi.com/download/application-notes/pdf/and90146-d.pdf` |
| 6 | Diodes Inc AN1192 -- Understanding RVP Approaches | PDF 8pp | `https://www.diodes.com/assets/App-Note-Files/AN1192_App-Note_Automotive-RVP.pdf?v=9` |
| 7 | TI SLVA862A -- Basics of eFuses | PDF 14pp | `https://www.ti.com/lit/pdf/slva862` |
| 8 | Nexperia AN50001 -- Reverse Battery Protection | PDF 18pp | `https://assets.nexperia.com/documents/application-note/AN50001.pdf` |

---

## protection/voltage-supervisor.md

Covers: voltage supervisor IC selection, reset circuit design, power-on reset timing, glitch filtering, open-drain vs push-pull outputs, watchdog timers, threshold setting.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ADI -- High Performance Voltage Supervisors Explained, Part 1 | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/high-perf-volt-supervisors-explained-part-1.html` |
| 2 | ADI -- How Voltage Supervisors Address Power Supply Noise and Glitches | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/voltage-supervisors-address-power-supply-noise-and-glitches.html` |
| 3 | ADI -- Choosing Supervisor Outputs (Open-Drain vs Push-Pull) | HTML | `https://www.analog.com/en/resources/technical-articles/choosing-supervisor-outputs.html` |
| 4 | TI SLVA521 -- Setting the SVS Voltage Monitor Threshold | PDF 7pp | `https://www.ti.com/lit/an/slva521/slva521.pdf` |
| 5 | TI SLVA360 -- Adding Hysteresis to Supply Voltage Supervisor | PDF 6pp | `https://www.ti.com/lit/pdf/slva360` |
| 6 | TI SLVA485 -- Pull-up/Pull-down Resistor for Open Drain Outputs | PDF 9pp | `https://www.ti.com/lit/an/slva485/slva485.pdf` |
| 7 | ADI -- The Basics of Windowed Watchdogs (MAX20478/MAX20480) | HTML | `https://www.analog.com/en/resources/technical-articles/the-basics-of-windowed-watchdogs.html` |
| 8 | TI SLLA546 -- Q&A Watchdog Overview and Configuration | PDF 6pp | `https://www.ti.com/lit/pdf/slla546` |

---

## protection/isolation.md

Covers: Digital isolators vs optocouplers, isolated power, creepage/clearance with worked examples, PCB layout for isolation, optocoupler CTR degradation prediction, optocoupler interface circuit design.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SLLA284 -- Digital Isolator Design Guide | HTML | `https://www.ti.com/document-viewer/lit/html/SLLA284` |
| 2 | TI SLLA526 -- Improve Your System Performance by Replacing Optocouplers with Digital Isolators | HTML | `https://www.ti.com/document-viewer/lit/html/SLLA526` |
| 3 | TI SLLA453 -- Isolated RS-485 Transceiver Reference Design | HTML | `https://www.ti.com/document-viewer/lit/html/SLLA453` |
| 4 | TI SLUP419 -- Demystifying Clearance and Creepage Distance | HTML | `https://www.ti.com/document-viewer/lit/html/SLUP419` |
| 5 | ADI AN-1109 -- Recommendations for Control of Radiated Emissions with iCoupler Devices | HTML | `https://www.analog.com/en/resources/app-notes/an-1109.html` |
| 6 | ADI LTC6820 Datasheet -- isoSPI Isolated Communications Interface | PDF 30pp | `https://www.analog.com/media/en/technical-documentation/data-sheets/LTC6820.pdf` |
| 7 | Skyworks AN583 -- Safety Considerations and Layout Recommendations for Digital Isolators | PDF 11pp | `https://www.skyworksinc.com/-/media/SkyWorks/SL/documents/public/application-notes/AN583.pdf` |
| 8 | Broadcom AV02-3401EN -- Calculate Reliable LED Lifetime Performance in Optocouplers | PDF 7pp | `https://docs.broadcom.com/doc/AV02-3401EN` |
| 9 | Vishay AN02 -- Optocoupler Application Examples (CTR Derating and Interface Circuits) | PDF 6pp | `https://www.vishay.com/docs/83741/83741.pdf` |

**Cross-ref:** ADI AN-960 (RS-485/RS-422 Circuit Implementation Guide) already cited in `interfaces/uart.md` #6 — covers non-isolated RS-485 fundamentals. TI SLLA272 (RS-485 Design Guide) already cited in `interfaces/uart.md` #7. For CAN bus isolation specifically → see `interfaces/can.md` #7 (SLLA486). For ESD protection on isolated interfaces → see `protection/esd.md`.

**Key teaching points:** #1 is the comprehensive digital isolator design guide (edge-based vs OOK architectures, isolated SPI/I2C/UART applications, EMC-optimized PCB layout with split ground planes). #2 is the definitive optocoupler-vs-digital-isolator comparison (switching speed, TDDB lifetime, power consumption, integration level). #3 provides complete isolated RS-485 reference designs with SN6505B transformer driver for isolated power — the best single source for "how to build an isolated RS-485 node." #4 is the gold standard for creepage/clearance (IEC 60664 flowcharts, material groups/CTI, pollution degrees, overvoltage categories, worked examples). #5 is essential for isolation barrier PCB layout (split ground planes, stitching capacitance, edge guarding, CISPR 22 Class A/B measurements). #6 is the isoSPI reference for BMS applications (LTC6820 + pulse transformer, daisy-chain topology, twisted pair up to 100m).

---

## mcus/esp32.md

Covers: Strapping pins, power supply design, RF layout and antenna matching, USB-JTAG, third-party PCB design retrospectives with failure analysis (per-chip: C3, S3, C6).

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Espressif ESP32-S3 HW Design Guidelines -- Schematic Checklist | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html` |
| 2 | Espressif ESP32-C3 HW Design Guidelines -- Schematic Checklist | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html` |
| 3 | Espressif ESP32-C6 HW Design Guidelines -- Schematic Checklist | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c6/schematic-checklist.html` |
| 4 | esptool -- Boot Mode Selection (ESP32-S3) | HTML | `https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html` |
| 5 | esptool -- Boot Mode Selection (ESP32-C3) | HTML | `https://docs.espressif.com/projects/esptool/en/latest/esp32c3/advanced-topics/boot-mode-selection.html` |
| 6 | Deep Blue Embedded -- ESP32 PCB Design in KiCAD (ESP32-C3 + Chip Antenna Hardware Design) | HTML | `https://deepbluembedded.com/esp32-pcb-design-in-kicad-esp32-c3-chip-antenna-hardware-design/` |
| 7 | PCBCool -- ESP32 PCB Failure Case Study on Power and RF Layout Design | HTML | `https://pcbcool.com/case-studies/esp32-pcb-failure-case-study-on-power-and-rf-layout/` |

**Note:** All URLs use the old ReadTheDocs site (`docs.espressif.com`), clean Sphinx HTML. The new CDP site (`documentation.espressif.com`) is a Vue.js SPA unusable for extraction. Other chip variants follow the same URL pattern (`{chip}` = esp32, esp32s2, esp32c2, esp32c5, esp32c61, esp32h2, esp32p4).

---

## mcus/stm32.md

Covers: boot configuration (BOOT0/BOOT1), reset circuit, HSE crystal requirements, decoupling, SWD/JTAG debug, GPIO configuration, ADC reference voltage, USB hardware design.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ST AN4488 -- Getting Started with STM32F4xxxx HW Dev | PDF 50pp | `https://www.st.com/resource/en/application_note/an4488-getting-started-with-stm32f4xxxx-mcu-hardware-development-stmicroelectronics.pdf` |
| 2 | ST AN2867 -- Oscillator Design Guide for STM8/STM32 | PDF 59pp | `https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8af-al-s-and-stm32-microcontrollers-stmicroelectronics.pdf` |
| 3 | ST AN5096 -- Getting Started with STM32G0 HW Dev | PDF 35pp | `https://www.st.com/resource/en/application_note/an5096-getting-started-with-stm32g0-mcus-hardware-development-stmicroelectronics.pdf` |
| 4 | ST AN4938 -- Getting Started with STM32H7 HW Dev | PDF 46pp | `https://www.st.com/resource/en/application_note/an4938-getting-started-with-stm32h74xig-and-stm32h75xig-mcu-hardware-development-stmicroelectronics.pdf` |
| 5 | ST AN4899 -- STM32 GPIO HW Settings & Low-Power | PDF 31pp | `https://www.st.com/resource/en/application_note/an4899-stm32-microcontroller-gpio-hardware-settings-and-lowpower-consumption-stmicroelectronics.pdf` |
| 6 | ST AN4879 -- USB Hardware/PCB Guidelines for STM32 | PDF 31pp | `https://www.st.com/resource/en/application_note/an4879-introduction-to-usb-hardware-and-pcb-guidelines-using-stm32-mcus-stmicroelectronics.pdf` |
| 7 | ST AN4073 -- Improving ADC Accuracy (STM32F2/F4) | PDF 32pp | `https://www.st.com/resource/en/application_note/an4073-how-to-improve-adc-accuracy-when-using-stm32f2xx-and-stm32f4xx-microcontrollers-stmicroelectronics.pdf` |

---

## mcus/rp2040.md

Covers: external flash selection, USB boot mode (27 ohm resistors), power (3.3V IO + 1.1V core), minimal circuit, RP2350 migration, battery/low-power design.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | RPi -- Hardware Design with RP2040 | PDF 37pp | `https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf` |
| 2 | RPi Pico Datasheet (reference implementation) | PDF 33pp | `https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf` |
| 3 | RPi -- Hardware Design with RP2350 | PDF 22pp | `https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf` |
| 4 | RPi -- Pico 2 Datasheet (RP2350 reference impl.) | PDF 27pp | `https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf` |
| 5 | RPi -- Power Switching RP2040 App Note | PDF 11pp | `https://pip.raspberrypi.com/documents/RP-004339-WP-Power-switching-RP2040-for-low-standby-current-applications.pdf` |

---

## mcus/fpga.md

Covers: FPGA power sequencing, BGA decoupling, configuration flash, IO banking, SERDES, clock distribution, Intel/Altera design guidelines, DDR3/DDR4 memory interface routing.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Lattice FPGA-TN-02038 -- ECP5 and ECP5-5G Hardware Checklist | PDF 36pp | `https://0x04.net/~mwk/doc/lattice/ecp5/FPGA-TN-02038-2-0-ECP5-and-ECP5-5G-Hardware-Checklist.pdf` |
| 2 | Lattice FPGA-TN-02006 -- iCE40 Hardware Checklist | PDF 24pp | `https://0x04.net/~mwk/sbdocs/ice40/FPGA-TN-02006-2-3-iCE40-Hardware-Checklist.pdf` |
| 3 | Lattice TN1114 -- Electrical Recommendations for Lattice SERDES | PDF 22pp | `https://www.latticesemi.com/~/media/3E4AA60747DC46FC9EC26A9FD2F35894.ashx` |
| 4 | TI SLYT598 -- Power Supply Sequencing for FPGAs | PDF 5pp | `https://www.ti.com/lit/pdf/slyt598` |
| 5 | Altium -- How to Start an FPGA PCB Layout For Your Embedded System | HTML | `https://resources.altium.com/p/how-start-fpga-pcb-layout-your-embedded-system` |
| 6 | Intel/Altera AN-662 -- Arria V and Cyclone V Design Guidelines | PDF 44pp | `https://cdrdv2-public.intel.com/654271/an662.pdf` |
| 7 | Altium -- Fly-by Topology for DDR3 and DDR4 Memory: Routing Guidelines | HTML | `https://resources.altium.com/p/fly-topology-routing-ddr3-and-ddr4-memory` |
| 8 | Micron TN-40-40 -- DDR4 Point-to-Point Design Guide | PDF 34pp | `https://www.mouser.com/pdfDocs/Micron_DDR4_Design_Guide.pdf` |

**Cross-ref:** PCB stackup design (2/4/6/8-layer) → see `guides/pcb-layout.md`. Transmission lines, termination, and differential pairs → see `guides/signal-integrity.md`. Per-IC decoupling capacitor selection → see `power/decoupling.md`. SPI flash interface protocol → see `interfaces/spi.md`. Oscillator PCB layout → see `misc/crystal.md`.

**Note on Lattice URLs (#1, #2):** The official Lattice `view_document?document_id=` endpoint is broken as of Feb 2026 (returns wrong documents or redirects to product pages). These are the official Lattice technical notes hosted at a community mirror (0x04.net/~mwk) maintained by open-source FPGA toolchain developers. Source #3 uses the Lattice CDN hash URL which still works.

**Key teaching points:** #1 is THE primary ECP5 hardware reference (used in ULX3S, OrangeCrab, Glasgow, Cynthion): power sequencing (VCCIO before/with VCC and VCCAUX), decoupling per rail (100 nF per pin + bulk), SPI flash configuration pins, sysIO banking rules, SERDES rail filtering, JTAG, unused pin handling. #2 is the iCE40 equivalent (iCEBreaker): PLL analog supply isolation, SPI flash 0x0B Fast Read requirement. #3 covers SERDES analog design: CML buffer architecture, quiet supply with ferrite bead + cascaded caps, AC coupling cap values (20 nF min for 8b10b). #4 covers 4 sequencing techniques: RC time constant, PGOOD cascading, analog sequencer (LM3880), digital PMBus monitor (UCD90120A). #5 is the practical BGA layout starting point: stackup formula (signal layers = BGA rows / 4), NSMD vs SMD pads, dogbone vs via-in-pad by pitch, decoupling on BGA backside.

---

## misc/crystal.md

Covers: load cap formula, stray capacitance estimation, drive level, negative resistance margin, PCB layout for crystals, troubleshooting.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ECS Inc. -- Impact of Load Capacitance on Crystal Designs | HTML | `https://ecsxtal.com/news-resources/the-impact-of-load-capacitance-on-crystal-oscillator-designs/` |
| 2 | ST AN2867 -- Oscillator Design Guide (STM8/STM32) | PDF 59pp | `https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8af-al-s-and-stm32-microcontrollers-stmicroelectronics.pdf` |
| 3 | TI SZZA043 -- CMOS Unbuffered Inverter in Oscillator Circuits | PDF 25pp | `https://www.ti.com/lit/pdf/szza043` |
| 4 | ECS Inc. -- Crystal & Oscillator PCB Design Considerations | HTML | `https://ecsxtal.com/crystal-and-oscillator-printed-circuit-board-design-considerations/` |
| 5 | NXP AN1706 -- Microcontroller Oscillator Circuit Design | PDF 12pp | `https://www.nxp.com/docs/en/application-note/AN1706.pdf` |
| 6 | NXP AN3208 -- Crystal Oscillator Troubleshooting Guide | PDF 10pp | `https://www.nxp.com/docs/en/application-note/AN3208.pdf` |
| 7 | Microchip AN2648 -- Selecting and Testing 32.768 kHz Crystal Oscillators | PDF 28pp | `https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ApplicationNotes/ApplicationNotes/AN2648-Selecting_Testing-32KHz-Crystal-Osc-for-AVR-MCUs-00002648.pdf` |
| 8 | Espressif ESP32-S3 HW Design Guidelines -- PCB Layout (Crystal Section) | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html` |
| 9 | Espressif ESP32-S3 HW Design Guidelines -- Schematic (Clock Source Section) | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html` |

**Note on #9-10:** The crystal sections of the Espressif HW Design Guidelines are excellent general references: load cap formula (CL = C1*C4/(C1+C4) + Cstray), series inductor on XTAL_P, 2mm min gap from clock pin, no vias on clock traces, ground via stitching, keep-out area rules, 32.768 kHz RTC crystal ESR limits. Applies to any MCU crystal design.

---

## misc/level-shifting.md

Covers: voltage translation topologies (resistor divider, BSS138, TXB0108, LSF), bidirectional vs unidirectional, speed limits, pull-up sizing, addressable LED data line shifting.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SCEA035A -- Selecting the Right Level-Translation Solution | PDF 23pp | `https://www.ti.com/lit/pdf/scea035` |
| 2 | TI SCEA135 -- Do's and Don'ts for TXB/TXS Level-Shifters | PDF 10pp | `https://www.ti.com/lit/pdf/scea135` |
| 3 | Nexperia AN10441 Rev.2 -- Level Shifting in I2C-Bus Design | PDF 5pp | `https://assets.nexperia.com/documents/application-note/AN10441.pdf` |
| 4 | NXP (originally Philips) AN97055 -- Bidirectional Level Shifter for I2C-Bus | PDF 16pp | `https://cdn-shop.adafruit.com/datasheets/an97055.pdf` |
| 5 | NXP AN11127 -- Bidirectional Voltage Translators NVT20xx/PCA9306 | PDF 25pp | `https://www.nxp.com/docs/en/application-note/AN11127.pdf` |
| 6 | Nexperia AN90033 -- LSF010x Auto-Sense Applications | PDF 13pp | `https://assets.nexperia.com/documents/application-note/AN90033.pdf` |
| 7 | Big Mess o' Wires -- Tale of Three Level Shifters | HTML | `https://www.bigmessowires.com/2023/08/22/a-tale-of-three-bidirectional-level-shifters/` |

---

## misc/mosfet-circuits.md

Covers: MOSFET selection (Vgs(th), Rds(on)), P-ch vs N-ch, load switches, reverse polarity, gate drive, reading datasheets, SOA curves, relay coil drive, flyback protection.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Infineon AN_2112 -- Designing with Power MOSFETs | PDF 27pp | `https://www.infineon.com/assets/row/public/documents/24/42/infineon-designing-with-power-mosfets-applicationnotes-en.pdf` |
| 2 | Infineon -- OptiMOS Datasheet Explanation | PDF 30pp | `https://www.infineon.com/assets/row/public/documents/24/42/infineon-mosfet-optimos-datasheet-explanation-an-en.pdf` |
| 3 | onsemi AND9093 -- Using MOSFETs in Load Switch Applications | PDF 8pp | `https://www.onsemi.com/pub/collateral/and9093-d.pdf` |
| 4 | Infineon AN_2203 -- Gate Drive for Power MOSFETs | PDF 36pp | `https://www.infineon.com/dgdl/Infineon-Gate_drive_for_power_MOSFETs_in_switchtin_applications-ApplicationNotes-v01_00-EN.pdf?fileId=8ac78c8c80027ecd0180467c871b3622` |
| 5 | TI SLUAAO2 -- Using MOSFET SOA Curves in Your Design | PDF 9pp | `https://www.ti.com/lit/an/sluaao2/sluaao2.pdf` |
| 6 | onsemi AND90146 -- MOSFET Selection for Reverse Polarity Protection | PDF 11pp | `https://www.onsemi.com/download/application-notes/pdf/and90146-d.pdf` |
| 7 | TI SLVA652A -- Basics of Load Switches | PDF 14pp | `https://www.ti.com/lit/an/slva652a/slva652a.pdf` |
| 8 | ADI -- Switching Inductive Loads with Safe Demagnetization | HTML | `https://www.analog.com/en/resources/technical-articles/switching-inductive-loads-with-safe-demagnetization.html` |
| 9 | ADI HFAN-08.2.0 -- How to Control and Compensate a TEC | HTML | `https://www.analog.com/en/resources/technical-articles/hfan0820-how-to-control-and-compensate-a-thermoelectric-cooler-tec.html` |
| 10 | TI SLUA202A -- Closed Loop Temperature Regulation Using UC3638 H-Bridge | PDF 6pp | `https://www.ti.com/lit/an/slua202a/slua202a.pdf` |
| 11 | TI SLUA979A -- Driving a Peltier Element (TEC): Efficiency and Aging | PDF 7pp | `https://www.ti.com/lit/an/slua979a/slua979a.pdf` |
| 12 | EDN -- Low-Cost Driver for Thermoelectric Coolers (TECs) | HTML | `https://www.edn.com/low-cost-driver-for-thermoelectric-coolers-tecs/` |

**Cross-ref:** HV contactor driver circuits → see `misc/ev-power-systems.md` #4-5.

**Key teaching points:** #9-11,12 cover Peltier/TEC driver circuits using H-bridge topology for bidirectional current (heating/cooling modes), current limiting, and PWM vs DC drive tradeoffs (DC is 39% more efficient).

---

## misc/rf-antenna.md

Covers: antenna keep-out zones, PCB trace vs chip vs external antenna, RF matching networks, module placement, 50 ohm impedance, IFA/MIFA design, RF PCB layout, sub-GHz (868/915 MHz) LoRa/ISM band design.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Infineon/Cypress AN91445 -- Antenna Design and RF Layout Guidelines | PDF 60pp | `https://www.infineon.com/dgdl/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf?fileId=8ac78c8c7cdc391c017d073e054f6227` |
| 2 | ADI -- PCBs Layout Guidelines for RF & Mixed-Signal | HTML | `https://www.analog.com/en/resources/technical-articles/pcbs-layout-guidelines-for-rf--mixedsignal.html` |
| 3 | Nordic -- General PCB Design Guidelines for nRF52 Series | HTML | `https://devzone.nordicsemi.com/guides/hardware-design-test-and-measuring/b/nrf5x/posts/general-pcb-design-guidelines-for-nrf52-series` |
| 4 | Espressif ESP32 HW Design Guidelines -- PCB Layout | HTML | `https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html` |

**Cross-ref:** Espressif HW Design Guidelines have chip-specific RF matching and antenna layout guidance. See `mcus/esp32.md` sources. Key RF difference: S3/C3 use CLC matching; C6 uses CLCCL (bandpass, better for AC-DC/lighting). PCB layout pages cover 50 ohm impedance, CLC component placement, stub design, and keep-out zones.
| 5 | Johanson -- Chip Antenna Layout for BLE/802.11/Zigbee | HTML | `https://www.johansontechnology.com/tech-notes/chip-antenna-layout-considerations-for-ble-80211-and-24g-zigbee/` |
| 6 | Johanson -- Understanding Chip Antennas Handbook | PDF 27pp | `https://www.johansontechnology.com/docs/4469/johanson-understanding-chip-antennas-handbook.pdf` |
| 7 | Silicon Labs AN1088 -- Designing with Inverted-F 2.4 GHz PCB Antenna | PDF 15pp | `https://www.silabs.com/documents/public/application-notes/an1088-designing-with-pcb-antenna.pdf` |
| 8 | Abracon -- PCB Trace vs. Chip Antenna Design Considerations | PDF 8pp | `https://abracon.com/downloads/PCB-Trace-vs-Chip-Antenna-PCB-Design-Considerations.pdf` |
| 9 | Silicon Labs AN629 -- RF IC Layout Design Guide | PDF 32pp | `https://www.silabs.com/documents/public/application-notes/AN629.pdf` |
| 10 | TI SWRA640H -- CC13xx/CC26xx HW Config and PCB Design | PDF 44pp | `https://www.ti.com/lit/an/swra640h/swra640h.pdf` |
| 11 | Microchip/Atmel AT09567 -- ISM Band PCB Antenna Reference Design | PDF 10pp | `https://ww1.microchip.com/downloads/en/Appnotes/Atmel-42332-ISM-Band-Antenna-Reference-Design_Application-Note_AT09567.pdf` |
| 12 | Semtech AN1200.40 -- SX1261/SX1262 Reference Design Explanation | PDF 25pp | `https://cdn-reichelt.de/documents/datenblatt/A200/SX1262REFERENCE.pdf` |
| 13 | TI SWRA416 -- Miniature Helical PCB Antenna for 868/915 MHz | PDF 25pp | `https://www.ti.com/lit/an/swra416/swra416.pdf` |
| 14 | ADI -- How to Build a 24 GHz FMCW Radar System | HTML | `https://www.analog.com/en/resources/technical-articles/how-to-build-a-24-ghz-fmcw-radar-system.html` |

**Cross-ref:** GNSS antenna ground plane sizing and RF path design → see `misc/gnss-integration.md` #1,8. ADS-B 1090 MHz front-end (SAW + LNA) is covered by reference board schematics (ADSBee, Reid-n0rc ADS-B LNA) — no standalone design rule source yet.

**Key teaching points:** #14 covers 24 GHz FMCW radar system design (VCO, mixer, IF amplifier, Wilkinson divider, antenna feed).

---

## misc/op-amp-basics.md

Covers: op-amp selection (rail-to-rail, GBW, offset), common circuits (buffer, gain, difference), single-supply biasing, feedback stability, sensor signal conditioning, common mistakes.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ADI MT-035 -- Op Amp Inputs, Outputs, Single-Supply, Rail-to-Rail | PDF 12pp | `https://www.analog.com/media/en/training-seminars/tutorials/MT-035.pdf` |
| 2 | ADI AN-581 -- Biasing and Decoupling Op Amps in Single Supply | HTML | `https://www.analog.com/en/resources/app-notes/an-581.html` |
| 3 | ADI AN-937 -- Designing Amplifier Circuits: How to Avoid Common Problems | HTML | `https://www.analog.com/en/resources/app-notes/an-937.html` |
| 4 | TI SBOA067 -- Op Amps and Comparators: Don't Confuse Them | PDF 13pp | `https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/14/op-amp-vs-comparators.pdf` |
| 5 | Microchip AN682 -- Using Single Supply Op Amps in Embedded Systems | PDF 10pp | `https://ww1.microchip.com/downloads/en/AppNotes/00682c.pdf` |
| 6 | Microchip AN990 -- Analog Sensor Conditioning Circuits Overview | PDF 16pp | `https://ww1.microchip.com/downloads/en/appnotes/00990a.pdf` |
| 7 | TI SLOA020A -- Stability Analysis of VFB Op Amps Including Compensation | PDF 30pp | `https://www.ti.com/lit/an/sloa020a/sloa020a.pdf` |
| 8 | ADI MT-033 -- Voltage Feedback Op Amp Gain and Bandwidth | PDF 8pp | `https://www.analog.com/media/en/training-seminars/tutorials/MT-033.pdf` |
| 9 | ADI -- Op Amps Driving Capacitive Loads (Ask the Applications Engineer-25) | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/ask-the-applications-engineer-25.html` |

---

## misc/adc-dac.md

Covers: Signal conditioning, anti-aliasing filter design, sampling theory, mixed-signal PCB layout for ADCs, precision ADC routing and grounding, DAC frequency response equalization.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | ADI -- Seven Steps to Successful Analog-to-Digital Signal Conversion | HTML | `https://www.analog.com/en/resources/technical-articles/seven-steps-to-successful-analog-to-digital-signal-conversion.html` |
| 2 | ADI -- Practical Filter Design Challenges for Precision ADCs | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/practical-filter-design-precision-adcs.html` |
| 3 | ADI -- Filter Basics: Anti-Aliasing | HTML | `https://www.analog.com/en/resources/technical-articles/guide-to-antialiasing-filter-basics.html` |
| 4 | ADI -- Equalizing Techniques Flatten DAC Frequency Response | HTML | `https://www.analog.com/en/resources/technical-articles/equalizing-techniques-flatten-dac-frequency-response.html` |
| 5 | ADI -- Basic Guidelines for Layout Design of Mixed-Signal PCBs | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/what-are-the-basic-guidelines-for-layout-design-of-mixed-signal-pcbs.html` |
| 6 | Altium -- How to Properly Ground ADCs | HTML | `https://resources.altium.com/p/how-properly-ground-adcs` |
| 7 | TI SLYP167 -- PCB Layout Tips for High Resolution (Precision Analog Seminar) | PDF 22pp | `https://www.ti.com/lit/ml/slyp167/slyp167.pdf` |
| 8 | TI SLYT626 -- Designing an Anti-Aliasing Filter for ADCs in the Frequency Domain | PDF 5pp | `https://www.ti.com/lit/an/slyt626/slyt626.pdf` |

**Key teaching points:** #1 is the complete sensor→ADC signal chain methodology. #2-3 cover anti-aliasing from practical (SAR/sigma-delta tradeoffs) to theoretical (Butterworth vs Bessel). #4 covers DAC sinc rolloff and all 4 compensation methods. #5-6 address the perennial "should I split my ground plane?" question for mixed-signal.

---

## misc/gnss-integration.md

Covers: GNSS module integration (u-blox, Quectel), antenna types (active vs passive, chip vs patch), ground plane sizing, RF trace routing, LNA bias-tee power supply, backup battery for hot start, PPS (pulse-per-second) signal routing and decoupling, TCXO vs crystal oscillator selection.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | u-blox GNSS Antennas Application Note UBX-15030289 | PDF 36pp | `https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_%28UBX-15030289%29.pdf` |
| 2 | u-blox SAM-M8Q Hardware Integration Manual UBX-16018358 | PDF 23pp | `https://content.u-blox.com/sites/default/files/SAM-M8Q_HardwareIntegrationManual_%28UBX-16018358%29.pdf` |
| 3 | Quectel L76 Hardware Design V3.3 | PDF 59pp | `https://centerclick.com/ntp/docs/Quectel_L76L76-L_Hardware_Design_V3.3.pdf` |
| 4 | SparkFun GPS-RTK2 Hookup Guide | HTML | `https://learn.sparkfun.com/tutorials/gps-rtk2-hookup-guide/all` |
| 5 | ArduSimple -- Understanding GPS Timepulse or PPS | HTML | `https://www.ardusimple.com/understanding-gps-timepulse-or-pps/` |
| 6 | LXAntenna -- How to Power an Active GPS Antenna | HTML | `https://lxantenna.com/how-to-power-an-active-gps-antenna/` |
| 7 | NXP AN11420 -- GPS LNA Voltage Supply via Coax Cable | PDF 11pp | `https://www.nxp.com/docs/en/application-note/AN11420.pdf` |
| 8 | Wurth ANR017 -- GNSS Antenna Selection Guide | PDF 44pp | `https://www.we-online.com/components/media/o171079v410%20ANR017_GNSS_Antenna.pdf` |
| 9 | u-blox GPS-based Timing Application Note GPS.G6-X-11007 | PDF 14pp | `https://content.u-blox.com/sites/default/files/products/documents/Timing_AppNote_%28GPS.G6-X-11007%29.pdf` |

**Key teaching points:** #1 is the definitive u-blox antenna guide (footprint, ground plane 5mm isolation, active antenna power 3-20mA, LNA bias-tee). #2-3 cover hardware integration (RF trace routing, backup battery circuits, TCXO selection, reference schematics). #8 explains antenna selection (ground plane sizing 60x60mm min for 25x25mm patch, radiation patterns, ceramic chip vs patch). #4 is the best hookup tutorial for RTK high-precision GNSS. #5,9 explain PPS signal (1Hz-10MHz pulse synchronized to UTC, 50-ohm routing above 1MHz, cable delay compensation). #6-7 cover active antenna power delivery via bias-tee (DC on RF coax, 27nH + 10ohm + 100nF filtering).

---

## misc/ev-power-systems.md

Covers: High-voltage DC systems (48V-120V), battery pack precharge circuits (resistor + contactor sequencing to limit inrush current to motor controller caps), high-side contactor drivers, BMS integration (CAN bus communication, cell tap wiring, sense wire filtering), high-current fusing and wire sizing (Anderson Powerpole, XT90 connectors, ampacity derating), series battery string balancing (14S+).

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | Sensata -- How to Design Precharge Circuits for EVs White Paper | PDF 10pp | `https://www.sensata.com/sites/default/files/a/sensata-how-to-design-precharge-circuits-evs-whitepaper.pdf` |
| 2 | TI TIDUF73 -- High-Voltage Passive Precharge Reference Design | PDF 14pp | `https://www.ti.com/lit/pdf/tiduf73` |
| 3 | Battery Design Net -- Pre-Charge Resistor | HTML | `https://www.batterydesign.net/pre-charge-resistor/` |
| 4 | TI SLVAF35 -- Driving High-Voltage Contactors in EV and HEVs | PDF 8pp | `https://www.ti.com/lit/pdf/slvaf35` |
| 5 | ST AN5940 -- Contactor Driver using VNH7100BAS | PDF 21pp | `https://www.st.com/resource/en/application_note/an5940-contactor-driver-using-the-vnh7100bas-stmicroelectronics.pdf` |
| 6 | Anderson Power -- Technical Reference (Amperage Ratings) | PDF 5pp | `https://www.andersonpower.com/content/dam/app/site/resources/techreference/ppmptecref.pdf` |
| 7 | Bourns -- Automotive Grade Fuses for 48V Systems White Paper | PDF 9pp | `https://www.bourns.com/docs/technical-documents/technical-library/singlfuse/bourns-automotive-grade-fuses-provide-overcurrent-protection-in-harsh-environment-applications-white-paper.pdf` |
| 8 | Eaton -- EV Fuse Selection Guide ELX1527 | PDF 4pp | `https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/technical/eaton-ev-fuse-selection-guide-elx1527-en.pdf` |
| 9 | Victron Energy -- DC Wiring (Cable Thickness Guide) | HTML | `https://www.victronenergy.com/media/pg/The_Wiring_Unlimited_book/en/dc-wiring.html` |
| 10 | ST AN5878 -- How to Design a Robust Automotive CAN System | PDF 21pp | `https://www.st.com/resource/en/application_note/an5878-how-to-design-a-robust-automotive-can-system-stmicroelectronics.pdf` |

**Key teaching points:** #1-3 are the gold standard precharge references (RC time constant, why precharge before closing main contactors, resistor power dissipation, sequencing: close negative → precharge → wait 90-95% → close positive → open precharge). #4-5 cover contactor driver circuits (high-side + low-side switching, coil drive requirements, single-coil vs dual-coil). #6,9 address wire sizing and connectors (Anderson Powerpole ratings, AWG ampacity derating, voltage drop calculations). #7-8 cover fuse selection methodology (rated voltage must exceed max battery SOC, derating factors for ambient temperature/enclosure/altitude). #10 covers CAN bus hardware design for EV systems (bus termination, transceiver selection, EMC, ESD protection).

---

## misc/motor-control.md

Covers: BLDC/FOC gate driver selection (DRV8302/8316/8323), 3-phase H-bridge layout (hot loop minimization, star-point grounding), bootstrap circuit design, current sensing methods (low-side shunt, inline, Hall-effect), dead time and shoot-through protection (Smart Gate Drive), motor drive EMC, stepper driver design (TMC2209 SpreadCycle/StallGuard tuning, A4988), microstepping current regulation.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | TI SLVAES1A -- Brushless-DC Motor Driver Considerations and Selection Guide | HTML | `https://www.ti.com/document-viewer/lit/html/SLVAES1A` |
| 2 | TI SLVA959B -- Best Practices for Board Layout of Motor Drivers | HTML | `https://www.ti.com/document-viewer/lit/html/SLVA959B` |
| 3 | TI SLUA887 -- Bootstrap Circuitry Selection for Half-Bridge Configurations | HTML | `https://www.ti.com/document-viewer/lit/html/SLUA887` |
| 4 | TI SLVA714D -- Understanding Smart Gate Drive | PDF 24pp | `https://www.ti.com/lit/an/slva714d/slva714d.pdf` |
| 5 | NXP AN14164 -- Current Sensing Techniques in Motor Control Applications | PDF 20pp | `https://www.nxp.com/docs/en/application-note/AN14164.pdf` |
| 6 | ST AN4694 -- EMC Design Guides for Motor Control Applications | PDF 51pp | `https://www.st.com/resource/en/application_note/an4694-emc-design-guides-for-motor-control-applications-stmicroelectronics.pdf` |
| 7 | TI SLVA951 -- Layout Guide for the DRV832x Family of Three-Phase Smart Gate Drivers | PDF 14pp | `https://www.ti.com/lit/pdf/slva951` |
| 8 | TI SLVAF84 -- Delay and Dead Time in Integrated MOSFET Drivers | HTML | `https://www.ti.com/document-viewer/lit/html/SLVAF84` |
| 9 | ADI (Trinamic) AN-001 -- Parameterization of spreadCycle | HTML | `https://www.analog.com/en/resources/app-notes/an-001.html` |
| 10 | ADI (Trinamic) AN-002 -- Parameterization of StallGuard2 & CoolStep | HTML | `https://www.analog.com/en/resources/app-notes/an-002.html` |
| 11 | Allegro -- A4988 DMOS Microstepping Driver Datasheet | PDF 20pp | `https://www.allegromicro.com/-/media/files/datasheets/a4988-datasheet.pdf` |

**Cross-ref:** MOSFET selection (Vgs(th), Rds(on), SOA curves) and gate drive fundamentals → see `misc/mosfet-circuits.md` #1 (Infineon "Designing with Power MOSFETs"), #4 (Infineon "Gate Drive for Power MOSFETs"). General thermal estimation → see `guides/thermal.md`. General EMC fundamentals → see `guides/emc.md`. PCB ground planes and return paths → see `guides/pcb-layout.md`.

**Key teaching points:** #1 is THE starting point — covers the entire BLDC design decision tree: gate driver vs integrated FET (threshold ~70W), current sensing architectures (1x/2x/3x CSA, low-side vs inline), PWM modes (trapezoidal 6-step vs sinusoidal/FOC), and Smart Gate Drive features. #2 covers motor driver PCB layout: hot loop minimization, star-ground partitioning, Kelvin connections for sense resistors, decoupling and bulk cap placement. #3-4 are the essential bootstrap + dead time pair: bootstrap cap sizing (minimum 10x total gate charge, detailed equation in #3), and Smart Gate Drive handshaking-based closed-loop dead time (#4). #5 covers current sensing for FOC: triple/dual/single DC-bus shunt configurations with PWM/ADC synchronization timing diagrams. #6 is the gold standard motor control EMC guide with 6 real-world case studies showing measured before/after emissions. #7 is the DRV832x-specific layout guide (directly applicable to VESC and moteus designs). #9-10 are the Trinamic chopper tuning bibles: SpreadCycle parameter optimization (#9), and sensorless stall detection via back-EMF with CoolStep for up to 75% energy reduction (#10). #11 is the primary design reference for the classic STEP/DIR stepper driver (35V/2A, mixed/slow decay auto-selection).

---

## misc/audio.md

Covers: I2S interface, audio codec integration and clocking, Class D amplifier PCB layout, mixed-signal grounding for audio, MEMS microphone interface (analog/PDM), click/pop suppression, headphone driver design.

| # | Source | Format | URL |
|---|--------|--------|-----|
| 1 | AllAboutCircuits -- Introduction to the I2S Interface | HTML | `https://www.allaboutcircuits.com/technical-articles/introduction-to-the-i2s-interface/` |
| 2 | SparkFun -- Audio Codec Breakout WM8960 Hookup Guide | HTML | `https://learn.sparkfun.com/tutorials/audio-codec-breakout---wm8960-hookup-guide/all` |
| 3 | SparkFun -- I2S Audio Breakout Hookup Guide (MAX98357A) | HTML | `https://learn.sparkfun.com/tutorials/i2s-audio-breakout-hookup-guide` |
| 4 | TDK InvenSense -- AN-1003: Recommendations for Mounting and Connecting MEMS Microphones | PDF 11pp | `https://invensense.tdk.com/wp-content/uploads/2015/02/Recommendations-for-Mounting-and-Connecting-InvenSense-MEMS-Microphones.pdf` |
| 5 | ADI -- AN-1429: Design Considerations for Headphone Drivers in Mobile Phones | PDF 8pp | `https://www.analog.com/media/en/technical-documentation/application-notes/AN-1429.pdf` |
| 6 | TI SLAA896 -- PCB Layout Guidelines for TAS2xxx Class-D Boosted Audio Amplifier | PDF 10pp | `https://www.ti.com/lit/an/slaa896/slaa896.pdf` |
| 7 | TI SLAA404C -- Design and Configuration Guide for TLV320AIC3204/AIC3254 Audio Codecs | PDF 29pp | `https://www.ti.com/lit/an/slaa404c/slaa404c.pdf` |
| 8 | ADI -- Staying Well Grounded (Hank Zumbahlen, Analog Dialogue) | HTML | `https://www.analog.com/en/resources/analog-dialogue/articles/staying-well-grounded.html` |
| 9 | TI SLYT499 -- Grounding in Mixed-Signal Systems Demystified, Part 1 | PDF 6pp | `https://www.ti.com/lit/an/slyt499/slyt499.pdf` |
| 10 | TDK InvenSense -- Analog and Digital MEMS Microphone Design Considerations | PDF 7pp | `https://invensense.tdk.com/wp-content/uploads/2015/02/Analog-and-Digital-MEMS-Microphone-Design-Considerations.pdf` |
| 11 | TI SLAAED0 -- Introduction to Click and Pop Noise Measurement in Class-D Audio Amplifiers | PDF 18pp | `https://www.ti.com/lit/pdf/slaaed0` |

**Cross-ref:** Audio PCB grounding and mixed-signal layout → see `misc/adc-dac.md` #5 (ADI -- Basic Guidelines for Layout Design of Mixed-Signal PCBs).

**Key teaching points:** #1 is the best I2S protocol introduction (signal descriptions from the original Philips/NXP spec, master/slave configurations). #2 covers full codec signal chain (microphone ADC → I2S → DAC → speaker/headphone) with WM8960 MICBIAS, ALC, PGA config. #3 explains filterless Class D (speaker inductance averages 300 kHz PWM), no MCLK needed, gain/channel selection via resistor dividers. #4 is the definitive MEMS microphone hardware guide: sound hole sizing (0.5-1mm), Helmholtz resonance avoidance, PDM wire length limits (6" max without termination), pseudo-differential analog MEMS technique (200 ohm series resistor). #5 covers the complete DAC-to-headphone chain: I-to-V conversion with feedback capacitor, Butterworth reconstruction filter, headphone impedance/sensitivity table (8-600 ohm).

---

## Source Count Summary

| Category | Files | Sources |
|----------|-------|---------|
| Guides | 11 | 94 |
| Interfaces | 6 | 54 |
| Power | 6 | 60 |
| Protection | 4 | 30 |
| MCUs | 4 | 22 |
| Misc | 10 | 92 |
| **Total** | **41** | **352** |

(checklist.md sources are reference checklists, not design-rule content sources -- listed separately above)
