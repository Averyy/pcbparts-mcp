# Crystal Oscillators

> Load cap calculation, crystal selection, drive level, startup margin, and layout for MCU Pierce oscillator circuits.

## Quick Reference

- **Equal external load capacitors are not equal to crystal CL.** Use the MCU vendor's parasitic-capacitance model; do not count pin capacitance both explicitly and inside Cstray [1, Crystal Matching; 2, pp.11-13].
- **Lower CL can improve startup margin, but changes pulling sensitivity.** ECS's 12MHz, 100-ohm examples need gm_crit=1.421mA/V at CL=20pF versus 0.275mA/V at CL=8pF; these are two named crystals, not a universal ratio [1, The Part Played by Gm_crit].
- **Distinguish gm from Gm_crit_max.** For STM32 datasheets specifying oscillator gm, require gm/gm_crit > 5; when the datasheet specifies maximum allowable crystal transconductance, compare gm_crit directly with that limit [2, pp.13-14].
- **Ground copper under the crystal is vendor-dependent.** ST specifies a local ground shield; ECS recommends no ground pattern under the crystal. Follow the MCU/package guidance and include the resulting parasitics in CL [2, pp.45-47; 4, Crystal PCB Design Guidelines].
- **Use C0G/NP0 load capacitors.** Their capacitance stability matters to crystal frequency; select tolerance using the crystal's pulling sensitivity [2, pp.17-18; 6, pp.6-7].

## Design Rules

### Load Capacitance Matching

- **Account for both pin capacitances and PCB stray capacitance using one consistent model.** In ECS's model, CL1+Cin=CL2+Cout=2 * (CL-Cstray). ST instead lumps pin/PCB parasitics into Cs in CL=(CL1 * CL2)/(CL1+CL2)+Cs; do not subtract the pin capacitances a second time [1, Crystal Matching; 2, pp.11-13].
- **Use actual MCU pin data, not a universal 5pF estimate.** ECS's STM32H5 example uses Cin=Cout=5pF and estimates PCB Cstray=3pF within its stated typical 2-5pF range. Those numbers are example assumptions, not values for every board/layer count [1, Crystal Matching].
- **Low CL increases sensitivity to capacitance error.** ECS identifies CL>=6pF as a reasonable pulling compromise, not a guarantee that every 6-10pF crystal fits every oscillator [1, Frequency Pulling].
- **Verify frequency on the final PCB.** Compare to the crystal measured with a known load on separate apparatus before adjusting capacitors for board parasitics [5, Testing and Troubleshooting].

### Crystal Selection

- **HSE example:** ECS-120-8-33B-CHN-TR is 12MHz, CL=8pF, ESR=100 ohm, 3.2mm * 2.5mm; ECS reports gm_crit=0.275mA/V. Its STM32L1 example uses gm=3.5mA/V, giving margin about 12.7; verify the actual MCU variant's oscillator parameter [1, How Different CL Changes the Circuit, Crystal Matching].
- **RP2040/RP235x:** Abracon ABM8-272-T3 is approved for these MCU families: 12MHz, CL=10pF, ESR<=50 ohm, 3.2mm * 2.5mm, maximum drive 200uW. Series resistance still needs verification on the actual MCU/supply/board [8, p.2 of drawing].
- **32.768kHz examples:** AN2648 lists NDK NX1610SE at CL=6pF and ESR=50kohm, SII SC-32S at CL=7pF and ESR=70kohm, and Micro Crystal CC7V-T1A variants at CL=7/9/12.5pF and ESR=50/70kohm. Its recommendations are oscillator-module-specific; select the actual load/ESR variant rather than imposing ESR<=50kohm on every MCU [7, Crystal Recommendations].
- **RTC crystal ESR is in kohm, not ohm.** Do not substitute the ohm-range ESR used for MHz crystals into the startup check [7, Crystal Recommendations; 8, p.2 of drawing].
- **MEMS alternatives need a compatible external-clock input.** SiT8008B covers 1-110MHz; SiT1532 supplies 32.768kHz without external crystal load capacitors. SiT1532's 10ppm room-temperature tolerance is not its temperature stability: the industrial option specifies 100ppm over -40 to +85 degrees C at 1.5-3.63V [9, p.1; 10, p.1].

### Drive Level and Series Resistor

- **Drive level is Iqrms^2 * ESR in the source's crystal-current model.** Compare with the selected crystal's drive rating; there is no universal 100-200uW limit for all MHz crystals. Overdrive causes damage or shortened life [2, pp.14-16].
- **Use Rs approximately equal to Xc2 only as an initial estimate.** ST then adjusts it while checking actual drive level and recalculates margin with ESR+Rs. Do not treat TI's simplified '50% voltage drop' statement as an exact RC voltage-divider result [2, p.16; 3, p.13].
- **TI's discrete LVC1GU04 high-frequency example replaces Rs with a series capacitor near C2.** At 25MHz, a 5ns inverter delay contributes 45 degrees phase shift before Rs adds delay. This is not a universal '>20MHz' modification for integrated MCU oscillators; follow the MCU's oscillator circuit [3, pp.15-16].
- **Test both drive extremes.** AN2648 describes lowest temperature/highest VDD for high loop gain and highest temperature/lowest VDD for low loop gain; measure startup and drive over the specified operating range [7, Drive Strength].

### Discrete Oscillator (External Inverter)

- **Use an unbuffered inverter such as SN74LVC1GU04 for TI's Pierce circuit.** SZZA043 reports gain of roughly hundreds for unbuffered versus thousands for buffered devices. Buffered devices can oscillate with adjusted components, but are more sensitive to parameter changes [3, pp.6, 13].
- **Do not use a Schmitt-trigger input as the linear Pierce amplifier.** Its two thresholds prevent reliable linear-region biasing; a Schmitt buffer can instead isolate the oscillator output [3, p.16].
- **Feedback resistor Rf is frequency/circuit-dependent.** TI's discrete inverter guidance uses 1-10Mohm; NXP's MCU examples use about 10Mohm for 32kHz and 100K for 10-20MHz. Many STM32s already include Rf, so do not add it by habit [3, p.13; 5, Crystal Oscillator Theory; 2, pp.11-12].

### PCB Layout

- **Use the local oscillator ground arrangement specified by the MCU vendor.** ST shows an underneath local ground shield tied to the nearest MCU ground and a guard ring; ECS's crystal-footprint keepout recommendation differs. Do not turn either into an all-layer rule for every crystal [2, pp.45-47; 4, Crystal PCB Design Guidelines].
- **Keep oscillator return current out of shared noisy returns.** AN3208 recommends separate ground connections for each grounded oscillator component and a guard isolated from other return currents [6, pp.5-7].
- **AN3208 recommends no vias in oscillator signal routing.** Its 0-ohm bridges are an option for difficult crossings; ground vias remain allowed. This is not restricted to 32.768kHz circuits [6, pp.6-7].
- **Ground crystal package pins according to the exact package drawing.** ECS distinguishes electrically connected seam-sealed lids from isolated glass-sealed lids; ST's local oscillator-shield guidance also excludes connecting a metallic case to that shield. Sealing method alone does not establish another part's pinout [4, Pierce Oscillator Layout; 2, p.45].

## Common Mistakes

- **Counting pin capacitance twice.** Two 10pF external capacitors give an 8pF load only if the effective lumped Cs is 3pF; adding separate 5pF pin capacitors changes that result. State the parasitic model before comparing to crystal CL [1, Crystal Matching; 2, pp.11-13].
- **Probe loading during measurement.** AN1706 gives 8-15pF for conventional probes, equivalent to about 1.24kohm-663 ohm at 16MHz. AN2648 warns a probe can start or stop oscillation; output the clock on a buffered MCU pin for frequency measurement [5, Testing and Troubleshooting; 7, Measurement Methods].
- **Pairing a high-CL crystal with the wrong oscillator.** ECS's ECS-120-20-33-AEL-TR / STM32L1 example gives gm/gm_crit about 2.46, below 5, versus about 12.7 with its 8pF crystal. This checks startup margin, not drive-level compliance [1, Crystal Matching].
- **DC across a translated-ground Colpitts crystal.** AN3208's MC68HC12/HCS12 circuit uses a blocking capacitor about 100 * CL; this is specific to that topology, not an extra capacitor for an MCU Pierce oscillator [6, pp.2-3].
- **Mechanical/reflow damage mistaken for a capacitor error.** Follow the crystal's solder profile and handling limits. AN1706's vibration advice to adhere a can-type crystal does not authorize arbitrary adhesive on every SMD crystal [5, Potential Problem Areas; 2, p.51].

## Formulas

**Load capacitor sizing with explicit pin capacitance [1, Crystal Matching]:**
**Rule of thumb:** ECS's 8pF CL example uses 5.1pF external capacitors only with Cstray=3pF and Cin=Cout=5pF.
**Formula:** CL = ((CL1+Cin) * (CL2+Cout))/(CL1+Cin+CL2+Cout) + Cstray. For equal total legs: CL1=2 * (CL-Cstray)-Cin; CL2=2 * (CL-Cstray)-Cout.
**Example:** CL=8pF, Cstray=3pF, Cin=Cout=5pF -> CL1=CL2=5pF; fitting 5.1pF gives CL=8.05pF in this model, before tolerances.

**Drive-level measurement [2, p.16]:**
**Rule of thumb:** Measure at the amplifier input with a probe <=1pF; ST recommends 0.1pF for the especially sensitive LSE input.
**Formula:** DL=(2 * pi * f * Vrms * Ctot)^2 * ESR; Vrms=Vpp/(2 * sqrt(2)); Ctot=CL1+Cs/2+Cprobe in ST's lumped-parasitic model. Compare to the selected crystal's drive limit; the simplified voltage method assumes negligible amplifier input current.

**Oscillator margin [2, pp.13-16, 18-19]:**
**Rule of thumb:** Use gm/gm_crit > 5 only when the MCU specifies actual oscillator gm. For Gm_crit_max, compare directly; Gm_crit_max=gm/5 in ST's convention.
**Formula:** For equal load legs, gm_crit=4 * (ESR+Rs) * (2 * pi * f)^2 * (C0+CL)^2. The separate measured negative-resistance safety factor is Sf=|Rneg|/ESRmax; ST specifies >=5 for HSE and >=3 for LSE. Power-cycle at each added-resistance step; sustained oscillation alone does not demonstrate restart [2, pp.18-19].

## Sources

### Related Rules

- `mcus/stm32.md` -- STM32 oscillator requirements
- `mcus/esp32.md` -- ESP32 crystal and RF clock design
- `mcus/rp2040.md` -- RP2040/RP2350 crystal requirements

### References

1. ECS Inc. -- Impact of Load Capacitance on Crystal Designs (HTML, named sections): https://ecsxtal.com/news-resources/the-impact-of-load-capacitance-on-crystal-oscillator-designs/
2. ST AN2867 (Rev 25, October 2026) -- Guidelines for Oscillator Design on STM8AF/AL/S and STM32 MCUs/MPUs: https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8af-al-s-and-stm32-microcontrollers-stmicroelectronics.pdf
3. TI SZZA043 (February 2004) -- Use of the CMOS Unbuffered Inverter in Oscillator Circuits: https://www.ti.com/lit/pdf/szza043
4. ECS Inc. -- Crystal & Oscillator PCB Design Considerations (HTML): https://ecsxtal.com/crystal-and-oscillator-printed-circuit-board-design-considerations/
5. NXP AN1706 -- Microcontroller Oscillator Circuit Design Considerations: https://www.nxp.com/docs/en/application-note/AN1706.pdf
6. NXP AN3208 (Rev 0, January 2006) -- Crystal Oscillator Troubleshooting Guide: https://www.nxp.com/docs/en/application-note/AN3208.pdf
7. Microchip AN2648 (DS00002648D, May 2022, pp.6, 9-10, 15-16) -- Selecting and Testing 32.768kHz Crystal Oscillators (named sections): https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ApplicationNotes/ApplicationNotes/AN2648-Selecting_Testing-32KHz-Crystal-Osc-for-AVR-MCUs-00002648.pdf
8. Abracon ABM8-272-T3 (drawing 456603 Rev B, September 16, 2024, p.2): https://abracon.com/datasheets/ABM8-272-T3.pdf
9. SiTime SiT8008B datasheet (Rev 1.08): https://www.sitime.com/datasheet/SiT8008
10. SiTime SiT1532 datasheet (Rev 2.0): https://www.sitime.com/datasheet/SiT1532
