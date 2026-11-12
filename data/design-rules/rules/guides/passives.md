# Passives

> Selecting R, C, L, and ferrite beads -- voltage derating, tolerance, packages, specific part recommendations.

## Quick Reference

- **Ceramic cap DC bias depends on the exact part.** ADI's 4.7uF, 16V X7R example at 12V retains about 1.5uF in 0805 versus 3.4uF in 1206; these are example curves, not package guarantees [1, Not All X7Rs Are Created Equal].
- **Ferrite bead current rating is a thermal limit, not a filtering guarantee.** ADI recommends about 20% of rated current as a starting point; verify impedance at actual bias [5, pp.4-5].
- **Check both inductor current limits.** Isat uses a specified inductance drop (often 10%, 20%, or 30%); Irms uses the vendor's specified temperature rise, commonly +40 degrees C, and usually excludes AC losses [3, pp.1-2; 4, Design Tip 3].
- **Ferrite bead + downstream cap needs a resonance check at light load.** ADI measured 10dB peaking near 2.5MHz with MPZ1608S101A and a 10nF ceramic at microampere load [5, pp.6-7].

## Design Rules

### Ceramic Capacitors

- **Do not select MLCCs by voltage-rating ratio alone.** In ADI's sampled 4.7uF Murata curves, a higher rating within the same package and dielectric often did not improve bias retention; compare exact MPN curves rather than assuming a universal package or voltage relationship [1, Figure 1].
- **X7R type designation says nothing about voltage coefficient.** Its +/-15% capacitance change over -55 to +125 degrees C is a temperature characteristic, not initial capacitance tolerance or a DC-bias limit. Specify exact MPN and verify with vendor simulation tools [1, Table 1 and Choosing the Right Capacitor].
- **Use the selected dielectric's aging rate.** Johanson quotes 2.5% capacitance loss per decade hour for its X7R/X5R and 7% for Y5V; C0G/NP0 does not age. These are not universal vendor limits; de-aging depends on both temperature and time, and soldering does not guarantee a full reset [2, The Effect of Time and Reversing the Aging Effect].
- **Check combined voltage and temperature data instead of adding independent percentage losses.** In ADI's unnamed 4.7uF, 6.3V, 0603 Y5V example, 5V bias leaves 0.33uF at room temperature but 0.39uF at +85 degrees C; temperature and bias do not combine as independent factors [1, Choosing the Right Capacitor].

> WARNING: A nominal capacitance is insufficient for regulator stability checks. ADI's Y5V example loses 92.9% at 5V bias; its separate 68.14% temperature loss at +85 degrees C is measured at zero bias. Use the combined operating-point data to check the regulator's minimum effective capacitance [1, Choosing the Right Capacitor].

- **Microphonic noise:** Class II ceramics exhibit piezoelectric effects; use C0G/NP0 where capacitance requirements permit avoiding that mechanism [1, Background on Some Basic Ceramic Capacitors Types].
- **MLCC examples:** 100nF: Murata GRM155R71C104KA88D (0402 X7R 16V, +/-10%), used in TI's PMP20490A BOM. 10uF: Murata GRM188R61A106KE69D (0603 X5R 10V, +/-10%); X5R's +/-15% temperature change over -55 to +85 degrees C does not specify bias retention [9, p.1; 10, p.1].
- Decoupling-specific rules (per-pin ceramics, bulk caps, placement) -> `power/decoupling.md`.

### Resistors

- **Divider current of 100 times maximum input leakage is only a starting point.** Calculate threshold corners with resistor and reference tolerances as well as leakage; the appropriate divider resistance depends on that budget -> `protection/voltage-supervisor.md` [11, pp.2-7].
- **Current-sense resistor thermal resistance depends on resistance value as well as package.** Vishay WSLF2512's 6.7 degrees C/W element-to-terminal value applies to 0.5mohm, not 5mohm; its element TCR is also different from the complete component TCR including copper terminals [6, pp.2-3; 8, p.2].
- **SMD resistors transfer as much as 90% of heat through the PCB.** Check the selected part's ambient/terminal derating conditions and PCB heat spreading; neither package size nor nominal wattage alone defines allowable dissipation [6, pp.1-3].
- **Working-voltage limits are family-specific.** Vishay CRCW-HP e3: 0402 50V, 0603 75V, 0805 150V, 1206 200V; also satisfy the power limit at the selected resistance and board temperature [7, pp.1, 4].
- **Pulse handling requires the exact pulse curve, resistance and waveform.** CRCW-HP e3 is a pulse-proof thick-film family, not a 0.1%/25ppm precision family: it specifies +/-0.5%, +/-1% or +/-5% and +/-100 or +/-200ppm/K. Check single-pulse and repetitive-pulse curves separately rather than assigning an energy limit by film technology [7, pp.1-2, 5-7].
- Thermal design for power resistors -> `guides/thermal.md`.

### Inductors

- **Ferrite core vs composite:** ferrite typically has a sharp saturation knee; powdered-iron/composite cores have softer saturation. Compare loss curves at the actual switching frequency rather than applying a universal 100kHz material boundary [3, p.2; 4, Design Tip 1].
- **Ferrite TCL reaches 700ppm/degrees C or higher.** Coilcraft notes that inductance typically decreases as temperature decreases, so room-temperature tolerance alone does not bound the cold value; use the selected part's temperature curve [3, p.1].
- **Buck inductor sizing:** Wurth's rough sizing uses 30% peak-to-peak ripple (20-40% range) and maximum coil current of 1.5 * I_out. Its boost shortcut is 2 * I_in, not 2 * I_out, with I_in approximated as (V_out / V_in) * I_out before losses; verify actual peak and RMS currents, efficiency and the converter's current limit [4, Design Tips 2-3].
- **Inductance measurement frequency matters.** Apparent inductance changes near self-resonance; check the specified test frequency and operating-frequency loss data rather than assuming a fixed percentage change [3, pp.1-2].
- **For EMC-critical converters, Wurth recommends shielded WE-PD, WE-TPC, WE-DD or WE-HCI.** Its Design Tip 5 also excludes tracks underneath and circuit boards directly above the inductor because shielding leaves an air gap; shielding alone does not establish compliance [4, Design Tip 5].
- Full switching converter design -> `power/switching.md`.

### Ferrite Beads

- **DC bias impact is severe and device-specific.** ADI's 100MHz curves show TDK MPZ1608S101A (100 ohm, 3A, 0603) dropping to 10 ohm at 1.5A, and Wurth 742792510 (70 ohm, 6A, 1812) to 15 ohm at 3A. The latter's 6A rating allows +40 degrees C rise; its +20 degrees C rating is 5A [5, p.5; 12, p.1].
- **Bias also shifts the complete filter response.** In ADI's ADP2120 FPWM test with MPZ1608S101A and 1uF, moving from no load to 250mA shifts cutoff from about 180kHz to 370kHz and reduces attenuation at 1.2MHz from 30dB to 18dB [5, pp.5-6, Figures 11-13].
- **Check R_DC against the rail tolerance at maximum load.** An assumed 0.7 ohm bead at 400mA drops 280mV, or 25.5% of a 1.1V rail; this is a calculation example, not a specification of the beads listed here [5, p.8, source-resistance discussion].
- **Selection order:** pick target impedance at noise frequency, verify it at actual DC bias, check R_DC voltage drop, then check damping at the lightest load [5, pp.4-10].

- **Damping (Method C):** add a series R_damp/C_damp branch across the load, alongside the existing decoupling. Use the resistance window below and retain a tunable resistor on prototypes; 16 times the total downstream decoupling is the minimum capacitance ratio for that window, not a guarantee with arbitrary resistor values [5, pp.9-10].
- **Use 742792510 for high-current power filtering.** It is 1812, 70 ohm at 100MHz, 6A at +40 degrees C rise and 0.03 ohm maximum DCR; these ratings do not establish suitability for USB signal lines [12, p.1].

## Common Mistakes

- **Capacitance measured after desoldering appears correct but fails in circuit.** Removing DC bias hides the loss; heating also changes aging state. Re-check capacitance under operating bias after the post-reflow stabilization interval specified by the manufacturer [1, Introduction; 2, Testing After Assembly].
- **Undamped ferrite bead filter amplifies switching noise.** In ADI's ADP5071 test (9V input, 16V output, 5mA load), the bead/10nF filter adds 10dB at 2.4MHz. A 1uF/2 ohm series damping branch changes this to 5dB attenuation; the result belongs to that circuit [5, pp.7, 10, Figures 17-18, 29].

## Formulas

**Ferrite bead damping resistor (Method C):**
**Rule of thumb:** C_damp >= 16 * C_decoup; use effective capacitances and include external trace inductance in L_bead [5, p.10].
**Formula:** 2 * sqrt(L_bead / C_damp) <= R_damp <= 0.5 * sqrt(L_bead / C_decoup) [5, p.10, Equations 3-4].
**Example:** Assume L_bead = 1uH, C_decoup = 100nF, C_damp = 1.6uF: both bounds are 1.58 ohm. Increase C_damp above 16 * C_decoup to allow component tolerance and a practical resistor range.

## Sources

### Related Rules
- `power/decoupling.md` -- per-IC ceramics, bulk caps, ESL by package, BGA strategy
- `power/switching.md` -- full switching converter design (inductor selection in context)
- `guides/thermal.md` -- thermal design for power resistors, junction temp calculation

### References
1. ADI Tutorial 5527 -- Temperature and Voltage Variation of Ceramic Capacitors (2012-12-04, HTML section names cited): https://www.analog.com/en/resources/technical-articles/temperature-and-voltage-variation-ceramic-capacitor.html
2. Johanson Dielectrics -- Ceramic Capacitor Aging Made Simple (undated HTML, local snapshot extracted 2026-02-09): https://www.johansondielectrics.com/tech-notes/ceramic-capacitor-aging-made-simple/
3. Coilcraft Doc 1287 -- Introduction to Inductor Specifications (revised 2020-07-15): https://www.coilcraft.com/getmedia/ac56eabb-8678-4ca2-9604-c609886d68c1/doc1287_inductor_specifications.pdf
4. Wurth ANP039 -- Power Inductors 8 Design Tips (6-page edition, no revision/date printed): https://www.we-online.com/components/media/o109038v410%20AppNotes_ANP039_PowerInductors8DesignTipps_EN.pdf
5. ADI AN-1368 -- Ferrite Bead Demystified (Rev.0, August 2015): https://www.analog.com/media/en/technical-documentation/app-notes/an-1368.pdf
6. Vishay 30380 -- Thermal Management for Surface-Mount Devices (revision 2018-03-19): https://www.vishay.com/docs/30380/terminalderating.pdf
7. Vishay 20043 -- CRCW-HP e3, Pulse Proof, High Power Thick Film Chip Resistors (revision 2026-03-17): https://www.vishay.com/docs/20043/crcwhpe3.pdf
8. Vishay 30193 -- WSLF Power Metal Strip Resistors (revision 2026-10-14): https://www.vishay.com/docs/30193/wslf.pdf
9. TI -- PMP20490A BOM, variant 001 (updated 2016-12-23): https://www.ti.com/lit/pdf/tidrpm3
10. Murata -- GRM188R61A106KE69# specifications (updated 2015-08-17, manufacturer PDF mirrored by Octopart): https://datasheet.octopart.com/GRM188R61A106KE69D-Murata-datasheet-46741888.pdf
11. TI SLVA450B -- IQ vs Accuracy Tradeoff in Designing Resistor Divider Input to a Voltage Supervisor (revised April 2021): https://www.ti.com/lit/pdf/slva450
12. Wurth -- 742792510 WE-CBF datasheet (revision 006.000, 2021-10-13): https://www.we-online.com/components/products/datasheet/742792510.pdf
