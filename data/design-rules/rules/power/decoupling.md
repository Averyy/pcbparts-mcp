# Decoupling

> Capacitor selection, placement, and via design for per-IC power integrity.

## Quick Reference

- **BGA processor default: 100nF per 2 power balls, 0402 or smaller.** Follow the device's decoupling requirements when they differ [1, pp.2-3].
- **Use one HF capacitor value for the BGA default, 100-200nF.** Mixed values need PDN impedance analysis because of anti-resonance [1, p.2].
- **ESL measurements, not package guarantees:** AVX measured 0603 ~870pH, 0805 ~1050pH, 1206 ~1200pH, 1210 ~980pH; reverse-geometry 0612 ~610pH and 0508 ~600pH [6, Tables 1-2].
- **BGA bulk default: >= 15uF per approximately 10 power balls.** Check startup sequencing and the regulator's capacitance limits [1, pp.2,5].

## Design Rules

### Placement and Via Design

- **For closely spaced power/ground planes (<= 0.5mm), prioritize cap-to-plane connection inductance.** Put vias adjacent to pads and mount caps on the face nearest the planes; four vias instead of two can nearly halve connection inductance when via diameter is small relative to pad width. Do not share cap vias with active devices in this configuration [5, closely spaced planes].
- **For a ferrite pi-filter, arrange caps at 90 degrees to the bead.** Wurth ANP098a's 50-ohm test board used ferrite 742863122 with two 100nF X7R caps; three GND vias around each pad, <= 0.3mm from its edge, gave the best result. Its via-position simulation showed up to 4dB improvement for the 90-degree arrangement over clustered vias [4, Sections 2-6].
- **Blind-via height matters more than drill diameter.** TI's estimate for one 0.15mm-diameter, 0.15mm-high blind via is 0.072nH versus 1.1nH for a 0.4mm through-via in a 1.5mm board; use L(nH) ~= (h/5) * (1 + ln(4*h/d)), with h and d in mm, as a via estimate rather than a complete decoupling-loop model [2, Via Inductance].
- **With widely spaced planes (> 0.5mm), place local caps near pins connected to the most distant plane.** For components above L1 with L2=GND and L3=PWR, that means the power pins. Same-side cap/device via sharing is allowed in this configuration only when the cap fits directly at the via without a trace stub; opposite-side sharing is excluded [5, widely spaced planes].

### BGA Strategy

- **For fine-pitch BGAs, share a via between at most two same-net power or ground balls to fit caps under the footprint.** TI's method skips every other via row, fitting 0402 caps inside a 0.8mm-pitch footprint or rotated 0201 caps. This is preferable to moving all caps outside the footprint; route BGA balls and caps directly to their planes rather than daisy-chaining balls through capacitor traces [1, pp.2-3].

### Stackup for Decoupling

- **Interplane capacitance needs close spacing, not merely a four-layer stackup.** LearnEMC gives approximately 16pF/cm^2 for FR4 planes spaced 0.25mm apart. TI recommends power/ground separation <= 0.25mm (10mil) for its high-speed BGA guidance; its approximate 250MHz transition to planar/on-die decoupling is not a universal cutoff [5, closely spaced planes; 1, pp.1,3,5].

### Regulator I/O Caps

- **For TI PTH modules, 75mVpp input ripple is a guideline for limiting bulk-capacitor heating.** SLTA055's calculated example with a 35mohm bulk capacitor reduces its RMS ripple current from 2.9A to 628mA and dissipation from 294mW to 13.8mW after adding input ceramics; these are example results, not universal targets [3, pp.2-4].
- **TI PTH output-capacitor impedance limits: > 4mohm below 20kHz and > 2mohm from 20-200kHz.** These apply to the PTH family discussed in SLTA055, not all regulators. Below those limits, that module's transient response loses damping [3, pp.7-8].
- LDO output-capacitor ESR requirements -> `power/ldo.md`; dielectric and DC-bias selection -> `guides/passives.md`.

> WARNING: Excess bulk capacitance can change power sequencing or trip startup OCP. Most PTH products in SLTA055 ramp at approximately 1V/ms, drawing an additional 1A per 1000uF; use the selected regulator's specified slew rate and maximum capacitance [1, p.2; 3, Section 2.5].

### Analog Supply Filtering

- **Ferrite bead pi-filter for PLL/analog supplies: keep the IC-side capacitor.** If space permits only one cap, omit the input-side cap. Without downstream storage, the bead's HF impedance blocks the load's peak current [1, p.4].
- **Default for BGA processor core power: omit the series bead.** TI discourages it because it isolates planar capacitance and forces transient current through the downstream capacitor connections; exceptions require a designed PDN, rather than a bead added for EMI after the fact [1, pp.4-5].

> WARNING: An undamped bead/cap filter can amplify ripple. AN-1368 gives typical LC resonances of 0.1-10MHz and approximately 10-15dB peaking when resonance lies in the bead's inductive region; its ADP5071 example at 5mA load has 10dB gain at 2.4MHz. Damping guidance -> `guides/passives.md` [9, pp.6-8].

### DC Bias Aging

- **DC bias aging is additional to the immediate DC-bias capacitance loss.** In Vishay's room-temperature study of 0603 X7R 100nF/50V parts, competing samples at 20V lost > 20% of their already-biased capacitance after 1000 hours, averaging > 7% per decade hour. These results describe the tested parts, not every X7R [7, pp.3-4].
- **The same study found faster drift at 50V bias.** After bias removal and with terminals shorted, competing samples took 50-1000 hours or more to recover to approximately 95%; all tested samples recovered to 100% after 150 degrees C for one hour [7, pp.4-5].
- **Johanson's normal aging rates: X7R/X5R -2.5% per decade hour, Y5V -7%.** Its manufacturing tolerance is referenced to 1000 hours; this does not mean aging stops then. Measurements in the first 10 hours after soldering can be erratic or high because soldering partially de-ages the dielectric [8, The Effect of Time; Testing After Assembly].

## Common Mistakes

- **Applying an RF capacitor's isolated resonance to a routed connection.** SLOA069's nominal 30pF example uses 27.77pF effective capacitance and 0.23nH ESL; adding 1.5cm of trace at an assumed 6nH/cm shifts the calculated resonance from 1.99GHz to 314MHz. This is an RF example, not the resonance of the 100nF BGA default [2, pp.10-11; recalculated from the stated capacitance and ESL].
- **Treating a measured filter improvement as a package-only result.** ANP098a's poor 0805 layout shared a GND via, added stubs and put caps parallel to the ferrite; it lost > 40dB of insertion loss relative to the next-best channel at some frequencies. Differences among the properly arranged filters were at most 10dB; 1-2mm stubs added approximately 0.5nH in that layout [4, Sections 3,5].
- **Treating X7R as universally better than C0G for RF bypassing.** ANP098a's mixed 100pF/1nF/4.7nF capacitor bank had stronger resonances with C0G than X7R; it does not prohibit C0G for a selected RF frequency. TI's SLOA069 instead recommends C0G for high-speed op-amp bypassing: choose for the circuit's frequency and check the assembled network [4, Sections 3,5-6; 2, Capacitor Dielectric Types].

## Formulas

**Input bulk capacitance behind a supply-path inductor (TI POL approximation):**
**Rule of thumb:** Use the reflected *input* load-current step, not the output step; this is not an output-capacitor sizing equation [3, pp.5-6].
**Formula:** C_bulk >= 1.21 * I_transient_in^2 * L_input / delta_V_in^2; I_transient_in = sum(Vout / (Vin * eta) * delta_Iout)
  - L_input: actual input filter inductance; SLTA055 uses <= 560nH, or assumes 50nH for the host path when no filter is fitted.
  - The result is an approximate minimum; verify the host supply response and LC damping experimentally [3, pp.5-6].
**Example:** 2.8A total reflected input step, 560nH, 100mV input dip limit -> 1.21 * 2.8^2 * 560e-9 / 0.1^2 = 531uF minimum, before ESR and host-supply validation [3, Section 1.6; recalculated with rounded current].

## Sources

### Related Rules

- `power/ldo.md` -- Output cap ESR stability requirements for LDOs fed by decoupled rails
- `guides/passives.md` -- Ferrite bead damping guidance, cap DC bias derating, dielectric selection

### References

1. TI SPRABV2 (February 2019) -- General Hardware Design/BGA PCB Design/BGA Decoupling: https://www.ti.com/lit/an/sprabv2/sprabv2.pdf
2. TI SLOA069 (September 2001) -- How (Not) to Decouple High-Speed Operational Amplifiers: https://www.ti.com/lit/an/sloa069/sloa069.pdf
3. TI SLTA055 (February 2006) -- Input and Output Capacitor Selection: https://www.ti.com/lit/an/slta055/slta055.pdf
4. Wurth ANP098a (16-May-2022) -- Effect of Layout, Vias and Design on the Blocking Quality of Filter Capacitors: https://www.we-online.com/components/media/o695199v410%20ANP098a%20EN.pdf
5. LearnEMC -- PCB Decoupling Guidelines (undated; closely/widely spaced plane guidance): https://learnemc.com/circuit-board-decoupling-information
6. Kyocera AVX -- Parasitic Inductance of Multilayer Ceramic Capacitors (undated): https://kyocera-avx.com/docs/techinfo/CeramicCapacitors/parasitc.pdf
7. Vishay 45263 (14-Dec-2021) -- Time-Dependent Capacitance Drift of X7R MLCCs Under Exposure to a Constant DC Bias Voltage: https://www.vishay.com/docs/45263/timedepcapdrix7rmlccexptoconstdcbiasvolt.pdf
8. Johanson Dielectrics -- Ceramic Capacitor Aging Made Simple (undated): https://www.johansondielectrics.com/tech-notes/ceramic-capacitor-aging-made-simple/
9. ADI AN-1368 (Rev. 0, August 2015) -- Ferrite Bead Demystified: https://www.analog.com/en/resources/app-notes/an-1368.html
