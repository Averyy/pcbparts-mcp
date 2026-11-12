# Switching Regulators

> Topology selection, component sizing, loop compensation, and SMPS-specific layout for buck, boost, buck-boost, and flyback converters.

## Quick Reference

- **Default inductor ripple: 30% within TI's 20-40% estimate when no datasheet range is given.** For externally sensed current-mode designs, AN-149 recommends at least 10-15mVpp AC signal at the sense pins [3, Section 3; 6, Current Sensing Signal and Noise].
- **Single-phase buck input-cap ripple rating:** I_rms ~= Iout * sqrt(D * (1-D)), neglecting inductor ripple; worst case is Iout/2 at D=0.5. Check capacitor RMS rating at operating temperature [7, p.4; 9, p.2].
- **CCM boost RHPZ limits bandwidth.** Set crossover < 1/10 of worst-case RHPZ frequency (min Vin, max load); use the transfer function for the actual topology [6, Small Signal Model of the Boost Step-Up Converter].
- **Internally compensated ICs: follow the datasheet's allowed L and C combinations.** Preserve L*C only when that datasheet permits the substitution; the product alone does not establish stability [5, Section 7].
- **LMR33630 and LTC3775 are unsuitable for 48V input.** Their operating maxima are 36V and 38V respectively [13, p.1; 14, p.1].

## Design Rules

### Topology Selection

- **Boost switch-current limit is not output-current capability.** For the CCM peak-current-limited boost in SLVA372, Iout_max = (I_lim_min - delta_IL/2) * (1-D); evaluate at minimum Vin with D = 1 - Vin_min * eta / Vout and the datasheet's minimum current limit [4, pp.2-3].
- **For the CCM boost model, f_RHPZ = R_load * (1-D)^2 / (2*pi*L).** Evaluate at minimum Vin and maximum load; do not reuse this equation unchanged for every buck-boost topology [6, pp.6-7, Equation 6].
- **Four-switch buck-boost: check both modes.** When no datasheet inductor range is specified, calculate buck and boost inductance and use the larger; verify switch peak currents in both modes as well [5, Sections 3-4].
- **Conventional boost stages retain an input-to-output path through the inductor and rectifier.** Shutdown isolation requires an explicit disconnect function; TPS61021A and TPS63020 specify load disconnect, so the conventional topology's path is not universal [4, Figure 1-1; 15, p.1; 16, p.1].
- LDO thermal and noise selection -> `power/ldo.md`.

### Pre-Bias Startup

- **Use an explicitly specified pre-bias startup mode when another rail can charge Cout.** TPS54302 holds both MOSFETs off until its soft-start reference exceeds FB, preventing low-side discharge of the pre-biased output; TPS562201 also specifies startup from a pre-biased output. Pulse-skipping support alone is not a reverse-blocking specification [10, Section 6.3.6; 11, p.1].
- **DDR VTT is a separate sink/source requirement.** TPS51200 provides tracking and sink/source termination regulation; that capability alone does not establish pre-bias behavior for every DDR regulator [23, p.1].

### Minimum On-Time and Pulse Skipping

- **Check t_on_required = Vout / (Vin_max * f_sw) against the controller's minimum on-time for a CCM buck.** LTC3775 specifies < 30ns on its front page, with application behavior discussed under Minimum On-Time Considerations. This does not extend its 38V input rating [14, pp.1,17-18].
- **If the required on-time is too short, reduce f_sw, use two stages, or select another controller.** LTC3775 drops cycles in pulse-skipping mode at this limit, increasing ripple; forced-continuous behavior differs. Do not assign a universal ripple multiplier [14, pp.17-18].

### Spread Spectrum Clocking

- **TPS54302 has built-in +/-6% switching-frequency spread.** Its datasheet specifies EMI reduction, not a universal 10-15dB improvement; use the actual modulation spectrum when checking a noise-sensitive load [10, Section 6.3.12].

### Recommended ICs

| Use Case | IC | Key Specs | Package |
|----------|----|-----------|---------|
| Buck 5-12V, 1-3A | TPS54302 | Sync, 4.5-28V input, 3A, spread spectrum [10, p.1] | SOT-23-6 |
| Buck 5-12V, 2A | TPS562201 | Sync, 4.5-17V input, 2A [11, p.1] | SOT-23-6 |
| Buck <1A ultra-small | TLV62568 | Sync, 2.5-5.5V input, 1A, 1.5MHz [12, p.1] | SOT-23-5 option |
| Buck 12-24V, 3A | LMR33630 | Sync, 3.8-36V input, 3A [13, p.1] | HSOIC-8 |
| High step-down, <= 38V input | LTC3775 | Voltage mode, < 30ns minimum on-time, 4.5-38V input [14, p.1] | MSOP-16 or 3x3mm QFN |
| Boost low-voltage battery to 3.3V | TPS61021A | 0.5-4.4V input (>= 0.9V to start), 1.8-4.0V output; 3A switch rating is not 3A output [15, p.1] | 2x2mm WSON |
| 4-switch buck-boost | TPS63020 | 1.8-5.5V input, 1.2-5.5V output, 4A typical switch-current limit; 2A output at Vin > 2.5V, Vout=3.3V [16, p.1] | 3x4mm VSON-14 |
| Flyback offline, 10W adapter example | TNY278GN | Integrated MOSFET; 700V drain absolute maximum, 10W at 85-265VAC in a typical non-ventilated enclosed adapter at 50 degrees C ambient [17, pp.1,12] | SMD-8C |
| SEPIC 3-6V->12V | LT3757 | 2.9-40V input, boost/SEPIC/flyback controller [18, p.1] | MSOP-10 option |

### Inductors

- **Compare RMS current to the thermal rating and peak current to Isat separately.** Wurth's typical nominal-current criterion is +40 degrees C self-heating; a 10% inductance drop is one saturation criterion, not a manufacturer-independent standard [8, Design Tip 3].
- **Soft-saturating powder cores trade a gradual inductance drop for higher core loss than ferrite in AN-140's comparison.** Do not select solely by the shape of the saturation curve; check loss at the chosen switching frequency [1, Power Losses in a Switching Regulator].
- **Recommended low-DCR families: Wurth WE-HCI/WE-PDF flat-wire inductors.** Use maximum rather than typical DCR for worst-case loss when both are specified [8, Design Tip 4].

### MOSFET Selection

- **For a buck high-side FET, compare switching charge as well as Rds_on.** The low-side FET's switching overlap loss is small when it turns on after its body diode conducts and turns off before diode conduction; conduction loss, reverse recovery and capacitance losses still matter [1, Power Losses in a Switching Regulator].

> WARNING: Low-side body-diode reverse recovery increases high-side switching loss and SW-node ringing. Check Qrr and the controller's dead-time requirements; longer dead time also increases body-diode loss [1, Power Losses in a Switching Regulator; 7, pp.2-3].

**MOSFET candidates; resistance and gate charge require their stated drive conditions:**

| Application | Part | Key Specs |
|-------------|------|-----------|
| 12V buck high-side | BSZ0909NS | 34V, Rds_on <= 12mohm at Vgs=10V, Id=20A, 25 degrees C; Qg 13nC typical at Vgs=10V, Vds=15V, Id=30A; TSDSON-8 [19, pp.1-3] |
| 12V buck low-side | BSC010N04LS | 40V, Rds_on <= 1mohm at Vgs=10V, Id=50A, 25 degrees C; Qg 95nC typical at Vgs=10V, Vds=20V, Id=50A; SuperSO8 [20, pp.1,4,6] |
| 24-48V buck | IRFH5015 | 150V, Rds_on <= 31mohm at Vgs=10V, Id=34A, 25 degrees C; Qg 36nC typical at Vgs=10V, Vds=75V, Id=34A; 5x6mm PQFN [21, pp.1-2] |
| 5V buck/boost | CSD17571Q2 | 30V, 24mohm typical at Vgs=4.5V (20mohm at 10V), Id=5A, 25 degrees C; Qg 2.4nC typical at Vgs=4.5V, Vds=15V, Id=5A; SON-2x2mm [22, pp.1,3] |

### Efficiency and Loss Breakdown

- **Do not treat a single loss ranking as universal.** ROHM's calculated 12V->5V/3A, 1MHz, 4.7uH example uses 80mohm inductor DCR and 100/70mohm high-/low-side FETs: total loss 1.82W (approximately 89% efficiency), including 723mW inductor loss and 376/369mW FET conduction loss. Its non-synchronous comparison totals 2.23W (approximately 87%), with 875mW diode conduction [7, pp.6-10].
- **At low load, loss profile flips:** switching, output-capacitance, gate-charge and IC operating losses dominate; at high load, FET and inductor conduction losses dominate [7, p.11].

### Input and Output Capacitors

- **Use input ceramics for the local HF current loop, with bulk capacitance as required.** A ceramic-only rule does not replace checking the RMS ripple-current ratings of the complete input network [9, Sections 1.1-1.3].
- **For a CCM boost, C_out >= Iout * D / (f_sw * delta_Vout) covers only the capacitive ripple term.** Add ESR ripple and transient requirements; internally compensated devices still require their permitted C range [4, Section 7].
- **Cold ESR must stay inside the selected regulator's stability range.** SNVA559C's example warns that aluminum-electrolytic ESR can increase 40 times from 25 to -40 degrees C. It recommends a flatter-ESR parallel capacitor, such as tantalum or film, rather than an automatic ceramic substitution [2, Capacitor ESR and Loop Stability].
- Ceramic DC bias derating, ripple formula, transient sizing -> `power/decoupling.md`.

### Loop Compensation

- **For the current-mode buck designs in AN-149, Type II uses two capacitors and one resistor.** Target crossover below approximately 1/10-1/6 of f_sw, >= 45 degrees phase margin (60 preferred), and >= 8dB loop-gain attenuation at f_sw/2; the sampling effect adds double poles there [6, Loop Compensation Design of a Current Mode Converter].
- **Peak current mode at D > 50% needs slope compensation.** Verify the selected controller's implementation; constant-on-time valley current control is a different case [6, Current Mode Control].
- **For LTC3851/LTC3833 current-mode debug, try 0.1uF from ITH to IC ground.** Stabilizing the supply points toward compensation; continued instability calls for current-sense and PCB-noise checks. AN-149 places the diagnostic capacitor between amplifier output and FB for voltage-mode supplies, not universally to ground [6, Identifying the Problem].

### Feedback Network

- **Divider current >= 100 times FB bias current is TI's guideline for < 1% bias-current error.** Set the lower resistor from VFB / Idivider and the total from Vout / Idivider; a universal 500K total limit does not follow without Vout [5, Section 5].
- **A feedforward capacitor introduces a pole as well as a zero.** AN-149 centers the phase boost around crossover and checks the resulting HF gain; Cff = 1 / (2*pi*f_crossover*R_top) alone does not optimize the network [6, Design of the Feedback Divider Network].
- **Kelvin sense for current-mode control.** Route SENSE+/SENSE- together directly to the sense element; put filter components at the IC pins. Keep a SENSE- via isolated from other VOUT planes [6, Current Sensing Signal and Noise].
- General SMPS placement, feedback isolation and power-trace sizing -> `guides/pcb-layout.md`; capacitor connection inductance -> `power/decoupling.md`.

## Common Mistakes

- **Measuring ripple with a long scope ground clip.** The loop picks up switching noise; ANP039's probe-sheath removal and tip/barrel ground connection avoid this artifact. Keep the probe ground connection as short as the measurement setup permits [8, Design Tip 8].
- **Trusting nominal 22uF/6.3V capacitance at 3.3V.** SLVA535B's specific Murata GRM188R60J226MEA0 X5R output capacitor is derated to 8.2uF in its TPS63802 example. That value does not apply to every 22uF/6.3V part [5, p.9].
- **Adding an ordinary load switch as guaranteed boost isolation.** TPS22918 is a single N-channel switch, without a specified reverse-blocking function; do not use it where specified reverse-current blocking is required. Use the boost's documented disconnect function or verify the complete external FET/diode path [24, pp.1,12; 15, p.1].

## Formulas

**Four-switch buck-boost inductor (CCM estimate, when no device-specific range is given):**
**Rule of thumb:** Calculate buck and boost requirements, use the larger, and then check peak switch current at minimum switching frequency [5, Sections 3-4].
**Buck mode:** L >= Vout * (Vin_max - Vout) / (Kind * f_sw * Vin_max * Iout)
**Boost mode:** L >= Vin_min^2 * (Vout - Vin_min) / (Kind * f_sw * Iout * Vout^2)
  - Kind = 0.2-0.4 estimate; 0.3 used below. These are power-stage estimates, not permission to exceed a compensated IC's L/C range [5, Section 3].
**Example:** 2.6-5.0V input, 3.3V/2A, 2MHz -> buck L = 0.94uH, boost L = 0.36uH -> 1.0uH candidate before tolerance and peak-current checks [5, Equations 3-4; calculated for the stated 2MHz].

## Sources

### Related Rules

- `power/ldo.md` -- LDO thermal and noise selection
- `power/decoupling.md` -- Ceramic DC bias derating, ripple formula, transient sizing, regulator I/O caps
- `guides/pcb-layout.md` -- Power traces, feedback isolation and SMPS placement

### References

1. ADI AN-140 -- Basic Concepts of Linear Regulator and Switching Mode Power Supplies: https://www.analog.com/en/resources/app-notes/an-140.html
2. TI SNVA559C -- Switching Regulator Fundamentals: https://www.ti.com/lit/an/snva559c/snva559c.pdf
3. TI SLVA477B -- Basic Calculation of a Buck Converter's Power Stage: https://www.ti.com/lit/an/slva477b/slva477b.pdf
4. TI SLVA372D (November 2022) -- Basic Calculation of a Boost Converter's Power Stage: https://www.ti.com/lit/an/slva372c/slva372c.pdf
5. TI SLVA535B (July 2018) -- Basic Calculations of a 4-Switch Buck-Boost Power Stage: https://www.ti.com/lit/an/slva535b/slva535b.pdf
6. ADI AN-149 (Rev. A, January 2015) -- Modeling and Loop Compensation Design of Switching Mode Power Supplies: https://www.analog.com/en/resources/app-notes/an-149.html
7. ROHM 64AN035E (Rev.004, November 2022) -- Efficiency of Buck Converter: https://fscdn.rohm.com/en/products/databook/applinote/ic/power/switching_regulator/buck_converter_efficiency_app-e.pdf
8. Wurth ANP039 -- Power Inductors: 8 Design Tips: https://www.we-online.com/components/media/o109038v410%20AppNotes_ANP039_PowerInductors8DesignTipps_EN.pdf
9. TI SLTA055 (February 2006) -- Input and Output Capacitor Selection: https://www.ti.com/lit/an/slta055/slta055.pdf
10. TI TPS54302 (SLVSDG6C, March 2026): https://www.ti.com/lit/gpn/tps54302
11. TI TPS562201 (SLVSD91D, September 2024): https://www.ti.com/lit/ds/symlink/tps562201.pdf
12. TI TLV62568 (SLVSD89B, November 2017): https://www.ti.com/lit/gpn/tlv62568
13. TI LMR33630 (SNVSAN3F, November 2020): https://www.ti.com/lit/ds/symlink/lmr33630.pdf
14. ADI LTC3775 (Rev. A): https://www.analog.com/media/en/technical-documentation/data-sheets/3775fa.pdf
15. TI TPS61021A (SLVSDM0, June 2016): https://www.ti.com/lit/ds/symlink/tps61021a.pdf
16. TI TPS63020 (SLVS916I, October 2019): https://www.ti.com/lit/gpn/tps63020
17. Power Integrations TinySwitch-III (December 2021): https://www.power.com/sites/default/files/documents/tinyswitch-iii_family_datasheet.pdf
18. ADI LT3757/LT3757A (Rev. H): https://www.analog.com/media/en/technical-documentation/data-sheets/LT3757-3757A.pdf
19. Infineon BSZ0909NS (Rev.2.0, May 2013): https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsz0909ns-ds-en.pdf
20. Infineon BSC010N04LS (Rev.2.5, May 2024): https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsc010n04ls-datasheet-en.pdf
21. Infineon IRFH5015PbF: https://www.infineon.com/assets/row/public/documents/24/49/infineon-irfh5015-datasheet-en.pdf
22. TI CSD17571Q2 (SLPS393A, January 2015): https://www.ti.com/lit/gpn/csd17571q2
23. TI TPS51200 (SLUS812E, September 2025): https://www.ti.com/lit/gpn/tps51200
24. TI TPS22918 (SLVSD76C, July 2017): https://www.ti.com/lit/gpn/tps22918
