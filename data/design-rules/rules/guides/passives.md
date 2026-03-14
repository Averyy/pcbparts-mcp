# Passives

> Selecting R, C, L, and ferrite beads -- voltage derating, tolerance stacking, packages, specific part recommendations.

## Quick Reference

- **Ceramic cap DC bias depends on package, not just voltage ratio.** 4.7uF X7R 0805 at 12V: 32% remaining. Same cap in 1206: 73%. Always check Murata SimSurfing / TDK SEAT at operating voltage.
- **Ferrite bead impedance drops up to 90% at 50% rated current.** Load at <= 20% rated current for effective filtering, or select rated >= 5x load current.
- **Inductor Isat vs Irms are different specs.** Isat = inductance drop (10%, 20%, or 30% -- no standard). Irms = +40C thermal rise. Either can be the binding constraint.
- **1% resistors cost the same as 5%.** No reason to specify 5% in new designs at JLCPCB/LCSC/Digikey volume.
- **Ferrite bead + downstream cap = LC resonance.** If resonance falls in the bead's inductive region (0.1-10 MHz), expect 10-15 dB gain at your switching frequency instead of attenuation.

## Design Rules

### Ceramic Capacitors

- **DC bias derating scales inversely with package size.** Going from 0805 to 1206 can double retained capacitance under bias. For Class II caps in power paths, use the largest package that fits. Higher voltage rating in the same package does NOT improve DC bias performance -- a 25V 4.7uF X7R 1206 at 12V performs no better than a 16V 4.7uF X7R 1206.
- **X7R type designation says nothing about voltage coefficient.** Any material meeting +/-15% over -55C to +125C can be called X7R. Two vendors' "4.7uF X7R 0805" caps have wildly different DC bias curves. Always specify exact MPN and verify with vendor simulation tools.
- **Aging: X7R/X5R lose 2.5% per decade hour** (1hr, 10hr, 100hr, 1000hr). Y5V loses 7%. C0G/NP0 does not age. Aging is reversible above Curie point (~125C) -- soldering partially de-ages but not reliably.
- **DC bias + aging + temperature stack.** 4.7uF X7R at 40% rated voltage: ~20% bias loss + 10% aging + 15% temperature = only ~55% of nominal remaining. Check all three at your operating point.

> WARNING: Y5V loses up to 93% capacitance under DC bias (4.7uF/6.3V at 5V = 0.33uF) and ~68% over temperature at +85C. Never use Y5V for decoupling or filtering.

- **C0G/NP0 under 1000pF:** zero aging, zero DC bias derating, linear TCR. No cost premium for +/-5% tolerance. 50V and 100V ratings are essentially free -- use for timing, filtering, and reference circuits.
- **Microphonic noise:** Class II ceramics generate audible noise (1-4kHz) under AC voltage from piezoelectric effect. C0G/NP0 does not. Mitigation: two caps in series (cancel mechanical motion), or polymer for audio-path coupling.
- **Electrolytic ESR doubles at -20C, triples at -40C.** Polymer aluminum caps maintain low ESR to -40C but typically <= 25V. Use polymer types for bulk capacitance at cold temperatures.
- **Flex-term (soft termination) for 1206+ caps** in thermal-cycling applications (-40C to +85C). CTE mismatch between ceramic body and PCB cracks standard terminations. Risk increases with package size.
- **Recommended general-purpose MLCCs:** 100nF decoupling: Murata GRM155R71C104KA88 (0402 X7R 16V), Samsung CL05B104KO5NNNC (0402 X7R 16V). 10uF bulk: Murata GRM188R61A106KE69 (0603 X5R 10V), TDK C1608X5R1A106M (0603 X5R 10V).
- Decoupling-specific rules (per-pin ceramics, bulk caps, placement) -> `power/decoupling.md`.

### Resistors

- **TCR adds drift on top of tolerance.** 100ppm/C resistor drifts +/-0.5% over 50C range. For precision circuits (voltage references, gain setting), use 25ppm/C or better.
- **Voltage divider current: >= 100x downstream comparator/reference input leakage current.** Use 10K-100K total resistance for most feedback and threshold dividers. With 1% resistors and 2% reference, worst-case threshold accuracy is 4-5% -- budget for this in threshold designs.
- **Current-sense resistors: each value has a different thermal resistance** unlike standard thick-film. Use metal foil or metal strip types for precision (TCR <= 50ppm/C). Kelvin connections (4-wire) mandatory above 100mA to avoid pad/trace IR drop.
- **SMD resistors dissipate 90% of heat through the board, not air.** Power rating is meaningless without PCB copper context. Terminal derating (not ambient derating) is the correct model for SMD.
- **Max working voltage by package:** 0402: 50V. 0603: 75V. 0805: 150V. 1206: 200V.
- **Pulse handling:** thick-film handles ~0.1J at 1ms; thin-film handles ~0.01J (10x less). A "33 ohm series resistor" for ESD protection fails on first surge if thin-film. Use thick-film for surge-exposed paths.
- **Recommended resistor families:** General-purpose (1%/100ppm): Yageo RC-series, Panasonic ERJ-series. Precision feedback (0.1%/25ppm): Susumu RG-series, Vishay CRCW-HP. Current sense (1%/50ppm, Kelvin): Vishay WSL-series, Bourns CSS-series.
- Thermal design for power resistors -> `guides/thermal.md`.

### Inductors

- **Ferrite core vs composite:** ferrite has flat inductance with sharp knee at saturation. Composite/powdered-iron has gradual soft saturation -- more forgiving but harder to predict. Ferrite preferred above 100kHz; iron powder below 100kHz.
- **Ferrite TCL up to 700 ppm/C.** At -40C, some ferrite materials show 5-10% inductance increase, shifting converter operating point. Check inductance vs temperature for designs operating below 0C.
- **Buck inductor sizing:** target 30% peak-to-peak ripple current (range 20-40%). Select Isat >= 1.5x I_out. Boost converter: input current = (V_out/V_in) * I_out, select Isat >= 2x I_out.
- **Inductance measurement frequency matters.** Ferrite-core inductors show 10-20% lower inductance at 1MHz vs 100kHz. Verify measurement frequency matches your switching frequency.
- **Recommended inductor families:** Buck converters (shielded, 1-22uH): Wurth WE-MAPI, Coilcraft XAL-series (molded, high Isat). EMI filtering (CMC): Wurth WE-CMB. Small signal/LC filters: Murata LQH-series.
- **DO:** Use shielded inductors for any EMC-compliant design. Do not route traces under power inductors.
- **DON'T:** Stack PCBs directly above power inductors -- magnetic coupling through the air gap.
- Full switching converter design -> `power/switching.md`.

### Ferrite Beads

- **DC bias impact is severe and underspecified.** TDK MPZ1608S101A (100 ohm at 100MHz, 3A rated) drops to 10 ohm at 50% rated current (1.5A). Wurth 742 792 510 (70 ohm, 6A, 1812) drops to 15 ohm at 3A. Bead + 1uF cap at 250mA bias: cutoff moves from 180kHz to 370kHz, attenuation drops from 30dB to 18dB at 1.2MHz.
- **R_DC voltage drop on low-voltage rails:** a 0.7 ohm bead on a 1.1V/400mA rail drops 280mV (25% of the rail). Always check R_DC impact on 1.0V and 1.2V core supplies. Inrush current spike at start-up can cause undervoltage sequencing failures.
- **Selection order:** (1) Pick target impedance at noise frequency. (2) Verify impedance holds at actual DC bias from vendor curves. (3) Check R_DC voltage drop. (4) Add damping network for LC resonance.

> WARNING: Ferrite bead + downstream decoupling cap = LC resonant circuit. If resonance falls in the bead's inductive region (0.1-10 MHz), you get 10-15 dB of gain instead of attenuation -- often right at the switching regulator frequency. Worst at light load (microamp to 1mA), which includes sleep/standby modes.

- **Damping (Method C -- preferred):** C_damp >= 16x total downstream decoupling, in series with R_damp (1-10 ohm). Kills resonance without degrading HF bypassing. Always include a placeholder damping resistor in the schematic for prototype tuning.

> WARNING: Never use a ferrite bead without a downstream decoupling cap. A ferrite bead alone is inductive -- without a cap to form a low-pass filter, it provides zero attenuation and can ring with parasitic capacitance at unpredictable frequencies.

- **Recommended ferrite beads:** Analog/PLL (600 ohm/100MHz): Murata BLM18PG601SN1 (0603, 500mA). High-current power (120 ohm/100MHz): TDK MPZ1608S121A (0603, 3A). USB/high-speed signal: Wurth 742792510 (0402, 120 ohm, 200mA, low capacitance).

### Tolerance Analysis

- **1% resistors from different batches may be centered at different points** within the 1% window. Do not assume Gaussian centered at nominal.
- **RSS tolerance stacking** is acceptable for 4+ independent random sources in non-critical circuits. For power and safety thresholds, use worst-case analysis.

## Common Mistakes

- **Specifying "10uF X7R" without a specific part number.** X7R is only a temperature coefficient spec -- voltage coefficient varies wildly between vendors and packages. Fix: specify exact MPN and verify with vendor simulation tools.
- **Ferrite bead R_DC causes brown-out on low-voltage rails.** 0.7 ohm on 1.1V/400mA = 280mV drop (25% of rail), pushing supply below IC minimum VCC. Intermittent -- only appears during heavy computational load. Fix: check R_DC * I_load against rail voltage tolerance.
- **Undamped ferrite bead filter amplifies switching noise.** LC resonance of bead inductance + 10nF ceramic at ~2.5MHz produces 10dB gain instead of attenuation -- right at a typical switcher frequency. Fix: add Method C damping (C_damp >= 16x C_decoup, R_damp 1-10 ohm).
- **Resistor pulse rating ignored on ESD/surge paths.** Thin-film handles 10x less pulse energy than thick-film at the same package size. Fix: verify single-pulse energy rating; use thick-film for surge-exposed resistors.

## Formulas

**Inductor ripple current (buck converter):**
**Rule of thumb:** Target 30% of I_out peak-to-peak ripple.
**Formula:** L = (V_in - V_out) * V_out / (V_in * delta_I * f_sw)
**Example:** 12V to 3.3V, 1A, 500kHz, 30% ripple -> L = (12 - 3.3) * 3.3 / (12 * 0.3 * 500e3) = 15.9uH -> use 15uH or 22uH

**Ferrite bead damping resistor (Method C):**
**Rule of thumb:** C_damp >= 16x total downstream decoupling. R_damp: 1-10 ohm.
**Formula:** sqrt(L_bead / C_damp) <= R_damp <= sqrt(L_bead / C_decoup)
**Example:** L_bead = 1uH, C_decoup = 100nF, C_damp = 1.6uF -> R_damp: 0.79 to 3.16 ohm -> use 2.2 ohm

**Voltage divider accuracy with leakage current:**
**Rule of thumb:** Divider current >= 100x comparator input leakage.
**Formula:** %ACC = (R2 * I_S * (V_IT/V_REF - 1)) / V_IT * 100%
**Example:** TPS3808 (I_S = 25nA), V_IT = 2.97V, V_REF = 0.405V, R2 = 187K -> %ACC = 1%. Total accuracy with 1% resistors + 2% reference = 4.73%.

**Current-sense resistor power dissipation:**
**Rule of thumb:** 10mohm at 3A = 90mW. Side-terminated packages run cooler at same dissipation.
**Formula:** P = I^2 * R_sense. Element rise = P * R_TH (thermal resistance per value/size).
**Example:** 10A through 5mohm WSLF2512 (R_TH = 6.7 C/W) -> P = 500mW, element rises 3.35C above terminal.

## Sources

### Related Rules
- `power/decoupling.md` -- per-IC ceramics, bulk caps, ESL by package, BGA strategy
- `power/switching.md` -- full switching converter design (inductor selection in context)
- `guides/thermal.md` -- thermal design for power resistors, junction temp calculation

### References
1. Murata -- DC Bias Voltage Characteristics: https://article.murata.com/en-us/article/voltage-characteristics-of-electrostatic-capacitance
2. Murata -- Temperature Characteristics of MLCCs: https://article.murata.com/en-us/article/temperature-characteristics-electrostatic-capacitance
3. ADI Tutorial 5527 -- Why Your 4.7uF Becomes 0.33uF: https://www.analog.com/en/resources/technical-articles/temperature-and-voltage-variation-ceramic-capacitor.html
4. Coilcraft Doc 1287 -- Introduction to Inductor Specifications: https://www.coilcraft.com/getmedia/ac56eabb-8678-4ca2-9604-c609886d68c1/doc1287_inductor_specifications.pdf
5. Wurth ANP039 -- Power Inductors 8 Design Tips: https://www.we-online.com/components/media/o109038v410%20AppNotes_ANP039_PowerInductors8DesignTipps_EN.pdf
6. TI SLVA450B -- Voltage Divider Resistor Selection: https://www.ti.com/lit/pdf/slva450
7. Vishay -- Thermal Management for SMD Resistors: https://www.vishay.com/docs/30380/terminalderating.pdf
8. SparkFun -- Resistors: Example Applications (LED Current Limiting): https://learn.sparkfun.com/tutorials/resistors/example-applications
9. ADI AN-1368 -- Ferrite Bead Demystified: https://www.analog.com/en/resources/app-notes/an-1368.html
10. Abracon -- Ferrite Beads: Basic Operations and Key Parameters: https://abracon.com/uploads/resources/Ferrite-Beads-White-Paper.pdf
11. AllAboutCircuits -- Choosing and Using Ferrite Beads: https://www.allaboutcircuits.com/technical-articles/choosing-and-using-ferrite-beads/
12. EmbeddedRelated -- Tolerance Analysis (Jason Sachs): https://www.embeddedrelated.com/showarticle/1353.php
13. Johanson Dielectrics -- Ceramic Capacitor Aging Made Simple: https://www.johansondielectrics.com/tech-notes/ceramic-capacitor-aging-made-simple/
