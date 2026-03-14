# Crystal Oscillators

> Load cap calculation, crystal selection, drive level, startup margin, and layout for MCU Pierce oscillator circuits.

## Quick Reference

- **Load cap formula: CL1 = CL2 = 2 * (CL - Cstray) - Cin.** CL1/CL2 are NOT equal to CL. With CL = 10 pF, Cstray = 3 pF, Cin = 5 pF: caps = 9 pF, not 10 pF.
- **Use 8 pF CL crystals for modern low-power MCUs.** 20 pF CL requires 5x higher gm_crit (1.42 vs 0.28 mA/V at 12 MHz) -- many modern MCUs cannot drive it.
- **Oscillator margin >= 5.** gm / gm_crit >= 5. Below 3 is not recommended. Test at max temperature + min VDD (worst case for startup failure).
- **No ground plane under crystal on any layer.** Adds parasitic capacitance that shifts frequency. No signal or power routing under crystal.
- **Use C0G/NP0 caps for CL1 and CL2.** X7R temperature drift pulls frequency.

## Design Rules

### Load Capacitance Matching

- **CL1 and CL2 must account for Cin, Cout, and Cstray.** Formula: CL1 = 2 * (CL - Cstray) - Cin, CL2 = 2 * (CL - Cstray) - Cout. STM32H5: Cin = Cout = 5 pF. If MCU datasheet omits Cin/Cout, estimate 5 pF each.
- **Stray capacitance varies widely by board type.** A 1 cm trace, 0.1 cm wide, over FR4 ground plane at 0.031 cm spacing = ~1 pF. Typical: 2 pF (4-layer, short traces) to 5 pF (2-layer, long traces). Hybrid PCBs with thin dielectric: 15-50 pF -- catastrophic if not accounted for.
- **Below 6 pF CL, pulling ratio becomes very steep.** Small Cstray errors cause large frequency shifts. 6-10 pF CL is the practical sweet spot.
- **Verify frequency on final PCB.** Measure crystal frequency on separate apparatus with known CL, compare to PCB frequency. If they disagree, Cstray is wrong and caps need adjustment.

### Crystal Selection

- **HSE (MHz) recommendations:**
  - General MCU (8-16 MHz): ECS-120-8-33B-CHN-TR (12 MHz, 8 pF CL, 100 ohm ESR, 3.2x2.5 mm). gm_crit = 0.275 mA/V -- works with low-gm MCUs like STM32L1 (3.5 mA/V, margin = 12.7).
  - RP2040/RP2350: Abracon ABM8-272-T3 (12 MHz, 10 pF CL, 50 ohm ESR max, 3.2x2.5 mm). Tested with 1 kohm Rs at 3.3V IOVDD across temperature.
  - High frequency (16-25 MHz): 8 pF CL variant. Above 20 MHz, Rs adds phase delay that can prevent oscillation -- replace Rs with series capacitor approximately equal to C2.
- **32.768 kHz RTC crystal recommendations:** NDK NX1610SE (6 pF CL, 50 kohm ESR, 1.6x1.0 mm), SII SC-32S (7 pF CL, 70 kohm ESR), Microcrystal CC7V-T1A (7 pF CL, 50 kohm ESR). Choose ESR <= 50 kohm for wider MCU compatibility -- high ESR crystals (>70 kohm) may not start on ultra-low-power oscillator modules.
- **32.768 kHz ESR is in kohm, not ohm.** Typical range 35-90 kohm. Confusing this with MHz crystal ESR (ohm range) is a common unit error.
- **MEMS oscillator modules eliminate crystal design.** SiT8008 (1-110 MHz, +/-50 ppm) or SiT1532 (32.768 kHz, +/-20 ppm) -- no load caps, no layout sensitivity, no drive level concerns. Cost premium ~$0.30-0.50. Use when startup reliability is critical or PCB iteration budget is zero.

### Drive Level and Series Resistor

- **Drive level = Iqrms^2 * ESR.** Max drive: 1 uW for small 32 kHz tuning forks, 100-200 uW for MHz SMD crystals, up to 5 mW for large AT-cut. Exceeding max drive causes aging, frequency drift, mechanical failure.
- **Rs approximately equal to Xc2 gives ~50% voltage attenuation.** At 25 MHz with 30 pF: Xc2 = 200 ohm, Rs = 200 ohm. At 100 kHz with 30 pF: Xc2 = 48 kohm.
- **Above 20 MHz, Rs phase shift can prevent oscillation.** Replace Rs with a series capacitor approximately equal to C2. TI measured this at 25 MHz -- the additional phase delay from Rs combined with the inverter's own propagation delay (5 ns = 45 degrees at 25 MHz) exceeds budget.
- **Test drive level at min temperature + max VDD.** This is worst case for overdrive (loop gain peaks). Max temperature + min VDD is worst case for startup failure.

### Discrete Oscillator (External Inverter)

- **Use unbuffered inverter (74LVC1GU04), NOT buffered (74HC04).** Buffered inverters have gain in thousands -- too sensitive to parameter changes, less stable. Unbuffered gain ~100 is correct.
- **Do NOT use Schmitt-trigger inverter (74HC14).** Two different thresholds (VT+/VT-) cannot be properly biased in the linear region by feedback resistor. Oscillation is unreliable or fails. Schmitt-trigger inverters are fine as output buffers after the oscillator -- not as the oscillator amplifier.
- **Feedback resistor Rf = 1-10 Mohm.** Lower for >10 MHz (100 kohm - 1 Mohm range), higher for 32 kHz (10 Mohm). Rf biases the inverter at VDD/2. Too low loads the circuit; too high gives insufficient feedback.

### PCB Layout

- **Remove copper pour under crystal footprint on all layers.** Ground copper adds parasitic capacitance. This applies to both MHz and kHz crystals.
- **Separate ground connections for each load cap.** Individual vias to ground plane for C1, C2, and crystal ground pins. Don't daisy-chain.
- **Guard ring around crystal circuit.** Grounded copper ring must carry zero current -- it shields only if it's not part of any return path.
- **For 32.768 kHz, avoid vias in signal path.** Use 0-ohm resistor bridges instead. Vias to ground plane for cap connections are acceptable.
- **Ground seam-sealed crystal cases; do NOT ground glass-sealed cases.** Seam-sealed: metal lid connects to ground pins, grounding reduces EMI. Glass-sealed: lid is isolated from ground pins, grounding has no benefit.

## Common Mistakes

- **Assuming CL1 = CL2 = CL.** Most common error. If crystal specifies CL = 10 pF and you use 10 pF caps, actual load = (10*10)/(10+10) + Cstray = 8 pF -- 20% low, pulling frequency sharp.
- **Probe loading during measurement.** Standard 10x probe adds 8-15 pF. At 16 MHz: 663-1240 ohm impedance. Circuit may oscillate WITH probe but fail without (probe provides extra capacitance that lowers loop impedance). Use firmware to output clock to buffered I/O pin for measurement.
- **Pairing 20 pF CL crystal with low-gm MCU.** ECS-120-20 paired with STM32L1 (3.5 mA/V) gives margin of only 2.46 -- below minimum 5. May start on the bench but fail across temperature. Switch to 8 pF CL crystal: margin jumps to 12.7.
- **Colpitts configuration DC voltage across crystal.** Some MCU architectures (MC68HC12) place DC across crystal, accelerating aging. Add DC-blocking capacitor ~100x CL (~1 nF) in series if using Colpitts.
- **Crystal fails after reflow.** Excessive reflow temperature or dwell time cracks hermetic seal, allowing moisture ingress. Adhere SMD crystals to PCB in vibration-prone applications.

## Formulas

**Load capacitor sizing:**
**Rule of thumb:** For 8 pF CL crystal with 3 pF Cstray and 5 pF Cin/Cout, use 5.1 pF caps.
**Formula:** CL1 = 2 * (CL - Cstray) - Cin, CL2 = 2 * (CL - Cstray) - Cout
**Example:** CL = 8 pF, Cstray = 3 pF, Cin = Cout = 5 pF -> CL1 = 2 * (8 - 3) - 5 = 5 pF. Use 5.1 pF (E96).

**Drive level estimation:**
**Rule of thumb:** If Vpp at CL1 > 1.5V and ESR > 50 ohm, add or increase Rs.
**Formula:** DL = (2 * pi * f * Vrms * Ctot)^2 * ESR
  - Vrms = Vpp / (2 * sqrt(2)), Ctot = CL1 + Cstray/2 + Cprobe
**Example:** 12 MHz, Vpp = 1.5V, CL1 = 5.1 pF, Cstray = 3 pF, Cprobe = 1 pF, ESR = 100 ohm -> Vrms = 0.53V, Ctot = 7.6 pF, Iqrms = 2*pi*12e6*0.53*7.6e-12 = 304 uA, DL = (304e-6)^2 * 100 = 9.2 uW. Under 200 uW max -- safe.

**Oscillator margin:**
**Rule of thumb:** gm/gm_crit >= 5 for production. >= 10 preferred for wide-temperature.
**Formula:** margin = gm / gm_crit
**Example:** STM32L1 gm = 3.5 mA/V, ECS-120-8-33B gm_crit = 0.275 mA/V -> margin = 12.7.

## Sources

### Related Rules

- `mcus/stm32.md` -- STM32-specific oscillator requirements (ST AN2867 gm tables)
- `mcus/esp32.md` -- ESP32 crystal and RF clock design
- `mcus/rp2040.md` -- RP2040/RP2350 crystal requirements

### References

1. ECS Inc. -- Impact of Load Capacitance on Crystal Designs: https://ecsxtal.com/news-resources/the-impact-of-load-capacitance-on-crystal-oscillator-designs/
2. ST AN2867 -- Oscillator Design Guide (STM8/STM32): https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8af-al-s-and-stm32-microcontrollers-stmicroelectronics.pdf
3. TI SZZA043 -- CMOS Unbuffered Inverter in Oscillator Circuits: https://www.ti.com/lit/pdf/szza043
4. ECS Inc. -- Crystal & Oscillator PCB Design Considerations: https://ecsxtal.com/crystal-and-oscillator-printed-circuit-board-design-considerations/
5. NXP AN1706 -- Microcontroller Oscillator Circuit Design: https://www.nxp.com/docs/en/application-note/AN1706.pdf
6. NXP AN3208 -- Crystal Oscillator Troubleshooting Guide: https://www.nxp.com/docs/en/application-note/AN3208.pdf
7. Microchip AN2648 -- Selecting and Testing 32.768 kHz Crystal Oscillators: https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ApplicationNotes/ApplicationNotes/AN2648-Selecting_Testing-32KHz-Crystal-Osc-for-AVR-MCUs-00002648.pdf
8. Espressif ESP32-S3 HW Design Guidelines -- PCB Layout (Crystal Section): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
9. Espressif ESP32-S3 HW Design Guidelines -- Schematic (Clock Source Section): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html
