# LDO Regulators

> When to use an LDO, how to stabilize it, and how to avoid the thermal/noise/startup traps.

## Quick Reference

- **Thermal gate: use the selected device's board-dependent thermal resistance.** Package names alone do not set a safe wattage; include ground-current dissipation [11, Thermal Considerations].
- **PSRR headroom means Vin - Vout, not voltage above dropout.** AN-1120 recommends >= 1V generally; ADP151 performs well with 500mV under its stated load conditions [2, p.8].
- **Output capacitance is device-specific.** AP2112 uses 1uF; LT3045 requires >= 10uF effective output capacitance, ESR < 20mohm and ESL < 2nH [8, p.1; 11, p.13].
- **NR/SS charging determines startup as well as noise.** At VNR/SS=0V, TPS7A91 charging current is 4-9uA with SS_CTRL grounded or 65-150uA with SS_CTRL tied to VIN [6, Table 2-1].
- **Parts:** AP2112K-3.3 (general), TPS7A20 (low-noise), LP5907 (no external NR cap), TPS7A02 (25nA typical Iq), LT3045 (parallelable) [8-12].

## Design Rules

### Thermal and Package Selection

- **Use board-specific thermal data rather than a SOT-23/SOT-223/DFN power table.** LT3045's datasheet gives measured thermal resistance versus copper area; use that method with worst-case input, load and ambient, then verify the assembled board [11, Thermal Considerations].
- **Recommended LDOs by application:**
  - General 3.3V digital: AP2112K-3.3 (600mA, SOT25/SOT-23-5, 250mV typical and 400mV maximum dropout at 600mA, 25 degrees C; recommended input <= 6V) [8, pp.1,3,8].
  - Low-noise analog/RF: TPS7A20 (300mA; typical noise 10uVrms at 1mA or 7uVrms at 300mA, Vout=2.8V, 10Hz-100kHz; typical PSRR 92dB at 1kHz, 300mA, Vin=Vout+1V) [9, pp.6-7].
  - Ultra-low-noise: LP5907 (250mA; 6.5uVrms typical at 250mA, 10Hz-100kHz; 82dB typical PSRR at 1kHz and 20mA, with Vin=Vout+1V and 1uF input/output caps) [10, p.5].
  - Sub-uV noise (VCOs, PLLs, SERDES clocks): LT3045 (0.8uVrms typical, 10Hz-100kHz, 500mA, Vout=1.3-15V, CSET=4.7uF, COUT=10uF; parallelable for higher current). Its headline PSRR is 76dB at 1MHz [11, pp.1,3].
  - Nano-Iq battery IoT: TPS7A02 (200mA, 25nA typical no-load Iq) [12, pp.1,6].
  - 2-5A low-noise designs: ADI lists ADP7158/ADP7159, LT3073 and MAX38907 as candidates; check each part's individual current rating rather than assuming all support 5A [1, Compromises].

### Output Capacitor and Stability

- **Older ESR-dependent LDOs need a device-specific ESR window.** TPS76050's typical stability plot at 25 degrees C requires 0.1-20 ohm ESR with 2.2uF; TI demonstrates oscillation with a low-ESR ceramic and a stable response after adding 1 ohm in series with that capacitor [3, pp.2-5].
- **Stability diagnostic: use a MOSFET switch and function generator for a fast load step.** TI's heuristic is four rings or fewer for sufficient phase margin; it does not establish a numerical phase margin or a universal load-step edge time [3, pp.3-5].
- **Use X7R/X5R output caps; exclude Y5V/Z5U.** Keep the effective capacitance above the selected LDO's minimum across voltage and temperature [7, Minimum Input- and Output Capacitance].
- **Large Cout can trigger current limit during startup.** TPS7A20 specifies 0.47-200uF effective output capacitance for stability, using >= 1uF nominal ceramic and <= 100mohm ESR; stability within that range does not guarantee an unchanged startup ramp [9, p.5; 6, Section 2.1.4.8].
- Cap DC bias derating -> `guides/passives.md`. Per-IC placement -> `power/decoupling.md`.

### PSRR and Noise

- **Use PSRR curves at the switcher's frequency, load and headroom.** AN-1120's 60dB/3kHz/3MHz example is a simplified model that ignores output-capacitor and pass-element parasitics; it is not a frequency template for every LDO [2, p.6].
- **ADP151 loses over 20dB of DC loop gain between 100mA and 200mA.** AN-1120 recommends a current rating >= 1.5 times the expected load to preserve PSRR; this is a selection guideline, not a guarantee of a particular rejection [2, pp.7-8].
- **Headroom near dropout destroys rejection before it necessarily loses DC regulation.** ADP151's comparison uses a 2.8V output at 200mA with 500mV versus 1V input-output differential; check the corresponding curve rather than adding a universal 500mV to dropout [2, p.8].
- **A reference bypass cap and an error-amplifier noise-gain network are different remedies.** For the adjustable LDO circuit in AN-1120, the R1/R3/C1 network sets high-frequency noise gain to 1.5-2 and its zero to 10-100Hz. The measured improvement is approximately 3 times (10dB) over 20Hz-2kHz, converging above 20kHz; those figures do not describe every NR pin [2, pp.4-5].
- **Comparing noise specs: use the same bandwidth and load conditions.** ADP223 at 1.2V: 27.7uVrms (10Hz-100kHz) versus 26.2uVrms (100Hz-100kHz); the latter excludes 8.9uVrms in the 10-100Hz band. LDOs requiring external NR caps can be up to 100 times noisier without them [2, p.5].
- **Cascaded ADP151s improved PSRR by up to 30dB in AN-1120's comparison.** The comparison uses 200mA and 1V total headroom; allocate >= 500mV input-output differential to each stage. Do not add dropout a second time to that differential [2, p.9].
- **For switcher ripple, AN-1120 prefers an input LC filter over a post-LDO filter.** Its example uses 1uF and 1uH (approximately 160kHz corner), plus a 10uF/1ohm series damping branch, giving approximately 33dB attenuation at 1MHz. A postfilter adds inductor-DCR load-regulation error; rate the inductor for maximum load current [2, pp.8-9].

### Startup and Sequencing

- **Fast-charge behavior is architecture-specific.** TPS7A84A and TPS7A91 use a changeover at approximately 97% of Vref; TPS7A96's changeover is programmed with FB_PG resistors, so 97% is an example setting for that device [6, Sections 2.2.1-2.2.3].
- **With EN tied to a slowly ramping VIN, check startup in dropout for overshoot.** TI identifies overshoot as a possible outcome, not an inevitable one. Use controlled EN sequencing when the downstream rails require it; verify the actual ramp [6, Section 2.1.4.7; 7, LDOs for Digital Loads].
- **EN defaults differ by part.** TPS7A02 has a smart pulldown that holds it disabled with EN floating; connect EN to VIN for always-on operation as specified by its datasheet [12, pp.3,19-20].
- **A pre-biased output needs a reverse-current check.** A PMOS pass device's body diode conducts toward VIN when sufficiently forward biased; use a protected part or the protection circuit specified for the power-down path [4, Sections 4-5].

### Nano-Iq and Battery Applications

- **TPS7A02 versus TPS7A05: TI calculates 8.7 versus 5.0 years, not an unconditional battery-life gain.** Assumptions: 100mAh, 1%/year battery self-discharge, 10nA capacitor leakage, 1uA MCU standby, 1600uA active at 16MHz, and 10000:1 standby/active time. Iq is 25nA versus 1uA; these inputs reproduce the reported lifetimes [5, p.4, Table 1].
- **TPS7A02's example curve maintains >= 98% current efficiency above 10uA load.** Dynamic biasing increases bandwidth with instantaneous load; verify transient response as well as no-load Iq [5, p.3].

### Reverse Current Protection

- **For bipolar-pass LDOs, the reverse path is an unrated parasitic junction.** ROHM distinguishes a rapidly falling input or sustained externally driven output from an open input; protection requirements depend on that case and the pass device [4, Sections 4-5].
- **An input series diode isolates the upstream supply; include its actual VF in the headroom budget.** ROHM gives application-dependent diode selection rather than a universal 100-300mV Schottky drop [4, Sections 2-3].
- **A bypass Schottky goes from Vout to Vin, cathode at Vin; it diverts reverse current rather than blocking backfeed.** ROHM recommends low VF (approximately <= 0.7V) and IR <= 1uA. RB168VWM-30 is a PMDE 30V/1A part with IR <= 0.6uA at 30V in the app note's table; check leakage at the maximum operating temperature [4, pp.2-3, Table 4].
- Some LDOs include internal reverse current protection (ADP1740/ADP1741) -- check before adding external diodes [7, Reverse-Current Protection Feature].

## Common Mistakes

- **Paralleling ordinary voltage-reference LDOs without current sharing.** Output-voltage mismatch prevents equal sharing. LT3045 supports paralleling with tied SET and IN pins; its example uses 20mohm ballast per output for better than 20% sharing accuracy at full load, with the ballast sized for the required sharing accuracy [11, Paralleling Devices].
- **Relying on thermal shutdown for normal regulation.** Shutdown hysteresis produces repeated off/on operation under sustained overheating; it does not define a safe continuous load. Check operating junction limits, not only the shutdown threshold [7, Thermal Shutdown].
- **Ignoring output-cap leakage in nA-Iq battery systems.** TI includes capacitor leakage alongside battery self-discharge and MCU standby current, and recommends measuring the selected capacitor over operating conditions [5, p.4].

## Formulas

**LDO thermal calculation including ground current:**
**Rule of thumb:** Use the datasheet's ground current at the actual load, not its no-load Iq [11, Calculating Junction Temperature].
**Formula:** P = (Vin - Vout) * Iout + Vin * Ignd; T_J = T_A + P * theta_JA
**Example:** In LT3045's datasheet example, a 5.25V maximum input, 3.3V/500mA output and assumed 12.5mA ground current give P = 1.041W. With the example DFN board's approximately 35 degrees C/W, the rise is approximately 36 degrees C; add the design's maximum ambient and compare against its junction rating [11, p.22; recalculated without rounding P to 1W].

## Sources

### Related Rules

- `guides/passives.md` -- Cap DC bias derating, dielectric selection
- `power/decoupling.md` -- Per-IC cap placement and via design

### References

1. ADI -- A Comprehensive Guide to LDO Regulators: https://www.analog.com/en/resources/analog-dialogue/articles/a-comprehensive-guide-to-ldo-regulators.html
2. ADI AN-1120 (Rev. 0, June 2011) -- Noise Sources in Low Dropout (LDO) Regulators: https://www.analog.com/en/resources/app-notes/an-1120.html
3. TI SLVA115A (February 2020) -- ESR, Stability, and the LDO Regulator: https://www.ti.com/lit/an/slva115a/slva115a.pdf
4. ROHM 66AN115E (Rev.001, January 2024) -- How to Select Reverse Current Protection Diodes for LDO Regulators: https://fscdn.rohm.com/en/products/databook/applinote/common/how_to_choose_reverse_current_protection_diode_for_ldo_an-e.pdf
5. TI SBVA084 (June 2020) -- Increase Your Battery Life With Nano Quiescent Current LDO: https://www.ti.com/lit/pdf/sbva084
6. TI SLVAFX0B (March 2026) -- Demystifying LDO Turn-On (Start-Up) Time: https://www.ti.com/lit/pdf/slvafx0
7. ADI -- How to Successfully Apply Low-Dropout Regulators: https://www.analog.com/en/resources/analog-dialogue/articles/applying-low-dropout-regulators.html
8. Diodes AP2112 (DS39724 Rev.2-2, June 2017): https://www.diodes.com/assets/Datasheets/AP2112.pdf
9. TI TPS7A20 (SBVS338H, July 2024): https://www.ti.com/lit/gpn/tps7a20
10. TI LP5907 (SNVS798Q, July 2025): https://www.ti.com/lit/ds/symlink/lp5907.pdf
11. ADI LT3045 (Rev. D): https://www.analog.com/media/en/technical-documentation/data-sheets/3045fa.pdf
12. TI TPS7A02 (SBVS277C, September 2022): https://www.ti.com/lit/ds/symlink/tps7a02.pdf
