# LDO Regulators

> When to use an LDO, how to stabilize it, and how to avoid the thermal/noise/startup traps.

## Quick Reference

- **Thermal gate: P = (Vin - Vout) * Iout.** SOT-23-5 limit ~0.25W, SOT-223 ~0.75W, DFN 3x3 ~1.5W.
- **PSRR headroom: >= 500mV above dropout.** Below ~200mV headroom, PSRR approaches 0dB.
- **Output cap: >= 1uF X7R ceramic for modern ceramic-stable LDOs.** No ESR concern.
- **NR/bypass pin: 10-100nF for ~10dB noise reduction.** Larger cap = slower startup (tau = R_NR * C_NR).
- **Parts:** AP2112K-3.3 (general), TPS7A20 (low-noise), LP5907 (ultra-low-noise 6.5uVrms), TPS7A02 (25nA Iq), LT3045 (0.8uVrms, parallelable).

## Design Rules

### Thermal and Package Selection

| Package | theta_JA (C/W) | Max P at 50C ambient |
|---------|----------------|----------------------|
| SOT-23-5 | ~285 | 0.26W |
| SOT-223 | ~100 | 0.75W |
| DFN 3x3 | ~50 | 1.5W |

- **12V-to-3.3V at 30mA already hits SOT-23 limit.** P = 8.7V * 0.03A = 0.26W. At 100mA: 0.87W -> SOT-23 junction reaches 273C. Use a buck or larger package.
- **Recommended LDOs by application:**
  - General 3.3V digital: AP2112K-3.3 (600mA, SOT-23-5, 250mV dropout)
  - Low-noise analog/RF: TPS7A20 (300mA, 10uVrms, 92dB PSRR at 1kHz)
  - Ultra-low-noise: LP5907 (250mA, 6.5uVrms, 82dB PSRR at 1kHz)
  - Sub-uV noise (VCOs, PLLs, SERDES clocks): LT3045 (0.8uVrms 10Hz-100kHz, 79dB PSRR at 1MHz) -- quieter than a Li-ion battery; parallelable for higher current
  - Nano-Iq battery IoT: TPS7A02 (200mA, 25nA Iq)
  - 2-5A loads: ADP7158/ADP7159, LT3073, MAX38907

### Output Capacitor and Stability

- **Older ESR-dependent LDOs (TPS760xx era) need the ESR zero for stability.** ESR must fall in a device-specific range -- e.g., TPS76050 requires 0.1-20 ohm with 2.2uF minimum. Ceramic caps (ESR < 10 mohm) on these parts cause oscillation. Fix: add 1 ohm series resistor, or replace with a ceramic-stable LDO.
- **Stability diagnostic: fast load step (0 to Imax in <1us).** Four or fewer rings = adequate phase margin (>= 45 deg). Sustained ringing = unstable. Use a MOSFET switch + function generator, not an electronic load -- electronic loads are too slow.
- **Y5V/Z5U caps: capacitance variation with temperature can cause oscillation at -20C even if stable at 25C.** X7R or X5R only.
- **Large Cout can trigger current limit during startup** (within 20-50us), dramatically slowing turn-on. TPS7A20 is stable from 0.47uF to 200uF but higher values hit current limit.
- Cap DC bias derating -> `guides/passives.md`. Per-IC placement -> `power/decoupling.md`.

### PSRR and Noise

- **PSRR at 1kHz vs switching frequency are different specs.** A typical LDO has 60-80dB PSRR at DC, rolls off at 20dB/decade from 3dB point (~1-10kHz), hits 0dB at unity-gain (~1-3MHz). Above unity-gain, only the output cap provides rejection. For post-switcher use: check PSRR at your switching frequency (500kHz-2MHz), not the 1kHz headline.
- **PSRR degrades 20+dB at heavy load.** ADP151 loses over 20dB between 100mA and 200mA because the pass element output impedance drops. Fix: choose an LDO rated >= 1.5x your expected load.
- **PSRR degrades sharply near dropout.** Pass device enters triode/linear region, loop gain collapses. At very low headroom, PSRR approaches 0dB. Budget >= 500mV above dropout.
- **NR/bypass pin filters reference noise only (not error amplifier noise).** ~3x (10dB) improvement in 20Hz-2kHz band. Above 20kHz the curves converge -- the error amplifier open-loop characteristic limits further reduction.
- **Adjustable LDOs: reduce error amplifier noise gain with a cap across the top feedback resistor.** Set the C * R3 zero between 10-100Hz to cut 1/f noise. Some LDOs are not unity-gain stable -- check phase margin.
- **Comparing noise specs: always use 10Hz-100kHz, same load conditions.** ADP223 at 1.2V: 27.7uVrms (10Hz-100kHz) vs 26.2uVrms (100Hz-100kHz) -- the second hides 8.9uVrms of 1/f noise. LDOs requiring external NR caps can be 100x noisier without them.
- **Cascading two LDOs adds ~30dB PSRR.** Each stage needs >= 500mV headroom. Total min input = Vout + 2 * (dropout + headroom).
- **Post-LDO LC filter for when PSRR at switching frequency is insufficient.** 1uF + 1uH gives fc ~160kHz and ~33dB attenuation at 1MHz. Add a 10uF damping cap with 1 ohm series resistor to suppress LC resonance peaking.

### Startup and Sequencing

- **Soft-start charging currents vary widely.** TPS7A91: 4-9uA (slow mode) vs 65-150uA (fast mode). This 16x range directly affects turn-on time and inrush calculations.
- **Fast-charge circuitry reduces NR filter startup penalty.** Modern LDOs (TPS7A84A, TPS7A91, TPS7A96) use a higher current source until ~97% of Vref, then switch to normal NR filter for steady-state noise performance.

> WARNING: EN pin tied to VIN with a slow ramp causes the LDO to operate in dropout during the entire ramp. When VIN exceeds Vout + dropout, the loop snaps from saturated to regulating, causing output overshoot. In multi-rail systems this overshoot can latch up downstream ICs. Use a dedicated EN signal with a sharp edge, or add RC delay on EN.

- **Never leave EN floating** -- may oscillate or pick up noise. Tie to VIN through a resistor divider if no sequencing controller is used.
- **Startup with pre-biased output** (charge from previous power cycle) can cause reverse current through the PMOS body diode or output overshoot. Verify anti-backfeed behavior in datasheet.

### Nano-Iq and Battery Applications

- **25nA Iq (TPS7A02) vs 1uA Iq (TPS7A05): battery life 8.7 years vs 5.0 years** in a duty-cycled system (10000:1 standby/active ratio, 100mAh battery, 1600uA active at 16MHz). The LDO Iq dominates total system current in standby.
- **TPS7A02 maintains >= 98% current efficiency above 10uA load.** Dynamic biasing increases bandwidth with load current, avoiding the slow-transient penalty of traditional low-Iq LDOs.
- **Ground current increases with load.** Bipolar-pass LDOs (LM317 era): 10-100x increase from no-load to full-load. CMOS-pass LDOs: 2-5x. Check Ignd vs Iload curve -- matters for efficiency at moderate loads.
- **Battery end-of-discharge check:** Li-ion at 3.0V with a 2.8V LDO at 200mV dropout works. At 3.3V output it does not -- you're in dropout with no PSRR, no load regulation.

### Reverse Current Protection

- **PMOS LDOs have a body diode from Vout to Vin.** When Vout > Vin (power-down sequencing), current dumps back into the input supply.
- **Multi-rail sequencing hazard:** if LDO A powers down before LDO B and they share downstream load, Vout_B > Vin_A forward-biases the body diode. Damages LDO and raises rail A above programmed level.
- **Bipolar-pass LDOs also have parasitic diodes** (pn junction in wafer structure) that conduct reverse current. Unlike MOSFET body diodes, these are not rated -- always use protection with bipolar types.
- **Series Schottky (prevention):** blocks reverse current entirely. Penalty: V_F adds to dropout (100-300mV).
- **Bypass Schottky (shunt):** diode from Vout to Vin (cathode to Vin). No dropout penalty but leakage current flows during normal operation. Select IR < 1uA at max operating temp -- Schottky leakage increases exponentially (tens of mA at 85C possible). ROHM RB168VWM-30 (PMDE, 30V/1A, IR = 0.6uA) has ultra-low leakage.
- Some LDOs include internal reverse current protection (ADP1740/ADP1741) -- check before adding external diodes.

## Common Mistakes

- **Post-regulator LDO makes switcher noise worse at resonance.** LDO output impedance peaks at its unity-gain bandwidth (typically 200kHz-1MHz). If the switcher fundamental or a harmonic lands on this peak, the LDO amplifies ripple instead of rejecting it -- measured 6-8dB gain on ADP151 at 800kHz with 100mA load. Fix: check LDO output impedance (Zout) curve at your switching frequency; if Zout peaks there, add a post-LDO LC filter or change the switcher frequency.
- **Ceramic output cap piezoelectric noise in audio circuits.** High-K MLCC dielectrics (X7R/X5R in 0805+) are piezoelectric -- LDO output ripple excites the cap mechanically, creating audible whine at the loop bandwidth frequency. Fix: C0G caps for noise-sensitive outputs, or smaller case sizes (0402/0603 have less piezoelectric coupling).
- **LDO oscillates only at cold temperature.** X7R ceramic output caps lose 15-30% capacitance at -20C, pushing effective ESR and capacitance outside the LDO's stable region. Board passes all bench tests at 25C but fails thermal chamber testing. Particularly common with older ESR-dependent LDOs where the stability range is narrow. Fix: simulate output cap effective values at temperature extremes using manufacturer tools (Murata SimSurfing); add 50% capacitance margin or switch to X7R with lower voltage rating (less derating).
- **Parallel LDOs for higher current without matching.** Two AP2112K-3.3 outputs tied together -- the one with slightly higher output voltage (within +/-1% tolerance) sources all the current until it thermally folds back, then the other takes over and also folds back. Oscillates between the two at 1-10Hz. Fix: only use LDOs explicitly designed for parallel operation (LT3045 SET pin daisy-chain with 5mohm ballast resistors) or use a single higher-current part.
- **LDO thermal shutdown cycles destroy downstream ICs.** SOT-23 LDO at thermal limit enters shutdown-cooldown-restart cycle at 0.5-2Hz. Each restart produces an uncontrolled voltage ramp that violates downstream power sequencing -- FPGA I/O latch-up observed at 1Hz thermal cycling. Fix: if thermal calculation shows Tj within 20C of shutdown threshold, move to a larger package rather than relying on thermal protection.
- **Ignoring output cap leakage in nA-Iq battery systems.** Ceramic cap leakage (V_rated / insulation_resistance) can rival the LDO's 25nA Iq. TPS7A02 can stabilize with very small ceramic caps to minimize this.

## Formulas

**Power dissipation and junction temperature:**
**Rule of thumb:** If P > 0.25W, SOT-23 is not viable.
**Formula:** P = (Vin - Vout) * Iout, T_J = T_A + P * theta_JA
**Example:** 5V->3.3V at 500mA, SOT-223 (100C/W), T_A = 50C -> P = 0.85W, T_J = 135C -> too hot, need DFN or buck

**Load transient output deviation:**
**Rule of thumb:** 22uF ceramic limits deviation to ~100mV for a 500mA step.
**Formula:** delta_V = delta_I * delta_t / C_out + delta_I * ESR
  - delta_t = LDO loop response time (~5us typical, rarely in datasheet -- measure with fast load step)
  - ESL term for fast edges: V_ESL = ESL * dI/dt (PCB trace adds ~4-6nH per cm (10-15nH per inch))
**Example:** 1A step in 2us, 100uF tantalum, 55 mohm ESR, 5us response -> 50mV (cap) + 55mV (ESR) = 105mV

**NR pin startup time:**
**Rule of thumb:** 10nF = fast startup, moderate noise. 100nF = slow startup, best noise.
**Formula:** tau_NR = R_NR * C_NR (R_NR is LDO internal NR resistance)
**Example:** R_NR = 250K, C_NR = 100nF -> tau_NR = 25ms. Startup to 90% ~= 2.2 * tau = 55ms. To regulation ~= 5 * tau = 125ms.

**Inrush current:**
**Formula:** I_inrush = I_load + C_out * dVout/dt
**Example:** TPS7A20, Vout = 1.8V, C_out = 1.4uF, tau = 117us -> dV/dt = 1.8V/117us = 15.4V/ms -> I_inrush = 0 + 1.4uF * 15.4kV/s = 21.5mA. Current limit engages at ~20-50us if C_out is much larger.

## Sources

### Related Rules

- `guides/passives.md` -- Cap DC bias derating, dielectric selection
- `power/decoupling.md` -- Per-IC cap placement and via design

### References

1. TI SLVA079 -- LDO Terms and Definitions: https://www.ti.com/lit/an/slva079/slva079.pdf
2. ADI -- Comprehensive Guide to LDO Regulators: https://www.analog.com/en/resources/analog-dialogue/articles/a-comprehensive-guide-to-ldo-regulators.html
3. ADI AN-1120 -- Noise Sources in LDO Regulators: https://www.analog.com/en/resources/app-notes/an-1120.html
4. TI SLVA115A -- ESR, Stability, and the LDO: https://www.ti.com/lit/an/slva115a/slva115a.pdf
5. ROHM -- Reverse Current Protection Diodes for LDOs: https://fscdn.rohm.com/en/products/databook/applinote/common/how_to_choose_reverse_current_protection_diode_for_ldo_an-e.pdf
6. Microchip AN6030 -- LDO Basics: Parameters and Measurements: https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ApplicationNotes/ApplicationNotes/AN6030-LDO-Basics-Parameter-Definitions-Measurements-and-Calculations-DS00006030.pdf
7. TI SLYT151 -- Understanding the Load-Transient Response of LDOs: https://www.ti.com/lit/an/slyt151/slyt151.pdf
8. TI SBVA084 -- Increase Battery Life With Nano Quiescent Current LDO: https://www.ti.com/lit/an/sbva084/sbva084.pdf
9. TI SLVAFX0 -- Demystifying LDO Turn-On (Startup) Time: https://www.ti.com/lit/wp/slvafx0/slvafx0.pdf
10. ADI -- How to Successfully Apply Low-Dropout Regulators: https://www.analog.com/en/resources/analog-dialogue/articles/applying-low-dropout-regulators.html
