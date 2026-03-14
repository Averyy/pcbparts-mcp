# Switching Regulators

> Topology selection, component sizing, loop compensation, and SMPS-specific layout for buck, boost, buck-boost, and flyback converters.

## Quick Reference

- **Target 30% inductor ripple current.** Below 20%, inductance increases exponentially for marginal gain. Below 10-15mV peak-to-peak on the sense node, current-mode control loses regulation.
- **Input cap RMS current is the binding constraint:** I_rms = Iout * sqrt(D*(1-D)). Caps must handle this RMS, not just capacitance. Ceramics only.
- **VDS rating: don't oversize.** 60V FET on a 12V rail has 2-3x higher Rds_on than a 25V FET of equal die size. Use >= 2x Vin_max, no more.
- **Boost/buck-boost RHPZ limits bandwidth.** Set crossover < 1/10 of worst-case RHPZ frequency (min Vin, max load).
- **Internally compensated ICs: follow datasheet L and C range exactly.** Output cap is part of the loop. Changing L or C changes loop response. Maintain the L*C product.

## Design Rules

### Topology Selection

| Topology | When | Key Gotcha |
|----------|------|------------|
| Buck | Vout < Vin | Min on-time limits max Vin/Vout ratio |
| Boost | Vout > Vin | RHPZ limits transient response; output shorted to input through inductor at startup |
| 4-switch buck-boost | Vin spans Vout | Size inductor for worst case of both modes -- calculate L for buck and boost separately, use the larger |
| Flyback | Isolated or multi-output | Unregulated outputs: 5-10% load regulation; post-regulate with LDO ~1V above target |
| SEPIC | Non-inverting boost alt | Less efficient than 4-switch; coupled inductor leakage spikes VDS |

- **Boost max output current = (I_lim - dIL/2) * (1-D).** Verify at worst case: lowest Vin, highest D. Miss this and you hit current limit at full load.
- LDO vs buck decision criteria -> `power/ldo.md`.

### Pre-Bias Startup

- **Most integrated buck ICs do NOT support pre-bias.** They start with the low-side FET on to charge the bootstrap cap, discharging any pre-existing output voltage. This sinks current through the body diode -- potentially latching up the load or violating sequencing specs in FPGA/DDR systems.
- **ICs with pre-bias support:** TPS54302 (starts in skip mode), LTC3775 (guaranteed monotonic startup), LMR33630 (monotonic, won't sink current), TPS62913 (0.75-6V, pre-bias compatible).
- **DDR termination regulators are inherently pre-bias safe** -- they sink/source. TPS51200 is purpose-built for DDR VTT with tracking.

### Minimum On-Time and Pulse Skipping

- **D_min = t_on_min * f_sw.** If required D < D_min, the converter skips pulses -> 3-5x output ripple increase, audible noise, jittery waveform.
- **48V->3.3V at 500kHz with 100ns min on-time:** D_min = 0.05, D_required = 3.3/(48*0.9) = 0.076. Marginal at nominal, fails at high Vin. At 600kHz: fails outright.
- **LTC3775: 30ns minimum on-time** -- designed for high step-down (48V->1V at 300kHz). Most integrated converters: 80-150ns.
- **Fix options:** reduce f_sw (increases L and C), two-stage conversion (48V->12V->3.3V), or IC with lower t_on_min.

### Spread Spectrum Clocking

- **Spread spectrum reduces peak conducted EMI by 10-15dB** by spreading switching energy across a band. Does not reduce total radiated power -- just peak spectral density.
- **Do not use on clock-sensitive loads** (ADC references, PLL VCOs, RF synthesizers). Frequency modulation creates sidebands that alias into the signal band.
- **ICs with built-in spread spectrum:** LMR33630 (+/-6%), LMQ61460 (+/-10%), TPS568230 (+/-6%).

### Recommended ICs

| Use Case | IC | Key Specs | Package |
|----------|----|-----------|---------|
| Buck 5-12V, 1-3A | TPS54302 | Sync, 4.5-28V, 3A, 97% peak | SOT-23-6 |
| Buck 5-12V, 2A | TPS562201 | Sync, 4.5-17V, 2A | SOT-23-6 |
| Buck <1A ultra-small | TLV62568 | Sync, 2.5-5.5V, 1A, 1MHz | SOT-23-5 |
| Buck 12-48V, 3-5A | LMR33630 | Sync, 3.8-36V, 3A, spread spectrum | HSOIC-8 |
| High step-down 48V | LTC3775 | Voltage mode, 30ns t_on_min, 4.5-60V | TSSOP-16 |
| Boost 3.3V->5V | TPS61021A | 0.5-5.5V in, 3A switch | 2x2mm QFN |
| 4-switch buck-boost | TPS63020 | 1.8-5.5V I/O, 4A | 3x3mm QFN |
| Flyback <10W offline | TNY278GN | Integrated 725V MOSFET | SMD-8C |
| SEPIC 3-6V->12V | LT3757 | 2.9-40V, boost/SEPIC/flyback | MSOP-10 |

### Inductors

- **"Nominal current" vs "saturation current" NOT standardized across manufacturers.** One is thermal (+40C rise), other is inductance drop (often 10%, but varies). Design to the LOWER of the two ratings.
- **Ferrite saturation worsens at high temperature.** Verify Isat at operating temperature, not just 25C. Wurth REDEXPERT can simulate temperature-dependent saturation.
- **Soft-saturation cores (powder/composite):** inductance drops gradually vs hard knee of gapped ferrite. Better for PoL converters handling large load steps -- a hard-saturating inductor can cause a sharp current spike that trips overcurrent protection.
- **Inductor tolerance of -15% can push actual inductance below current-mode sense threshold.** Account for tolerance + temperature drift when sizing.
- **Ripple current below 20%: inductance increases exponentially for negligible benefit.** The relationship is strongly nonlinear -- going from 30% to 20% ripple roughly doubles the inductance requirement.
- **Recommended families:** Wurth WE-HCI/WE-PDF (flat wire, low DCR). Coilcraft XAL (high Isat, small footprint). TDK CLF (general purpose). Murata DFE (ultra-compact).

### MOSFET Selection

- **High-side (buck): optimize for low QG.** Sees both conduction and switching loss. Switching loss = 0.5 * Vin * Iout * (tr+tf) * f_sw.
- **Low-side sync: optimize for low Rds_on.** Switches at near-zero VDS (body diode already conducting), so switching loss is negligible.
- **Qg vs Rds_on tradeoff is fundamental:** small die = low Qg but high Rds_on; large die = opposite. High-side wants small die, low-side wants large die.

> WARNING: MOSFET body diode reverse recovery in the low-side FET increases high-side switching loss and causes SW node ringing -- a major EMI source. Select FETs with low Qrr and ensure adequate dead time.

**Recommended MOSFETs:**

| Application | Part | Key Specs |
|-------------|------|-----------|
| 12V buck high-side | BSZ0909NS | 30V, 12mohm, 13nC Qg, TSDSON-8 |
| 12V buck low-side | BSC010N04LS | 40V, 1mohm, 95nC Qg, SuperSO8 5x6 |
| 24-48V buck | IRFH5015 | 150V, 44mohm, 22nC Qg, PQFN |
| 5V buck/boost | CSD17571Q2 | 30V, 2.6mohm, 5.5nC Qg, SON-2x2 |
| Schottky (non-sync) | SS34 | 40V, 3A, 0.5V Vf, SMA |

### Efficiency and Loss Breakdown

- **9 loss mechanisms in sync buck (ranked at heavy load):**
  1. Inductor DCR: Iout^2 * DCR (often the single largest loss)
  2. High-side conduction: Iout^2 * Rds_on * D
  3. Low-side conduction: Iout^2 * Rds_on * (1-D)
  4. High-side switching: 0.5 * Vin * Iout * (tr+tf) * f_sw
  5. Gate charge: (Qg_high + Qg_low) * Vgs * f_sw
  6. Dead time body diode: Vd * Iout * t_dead * f_sw
  7. Reverse recovery: 0.5 * Vin * Irr * trr * f_sw
  8. COSS discharge: 0.5 * Coss * Vin^2 * f_sw
  9. IC quiescent current
- **Reference: 12V->5V/3A sync buck at 1MHz, 4.7uH.** Total ~1.82W (~89% eff). Breakdown: inductor DCR 723mW, MOSFET conduction 745mW (376+369), switching 180mW. Non-sync equivalent: 2.23W (~87% eff) -- diode conduction alone is 875mW vs 369mW for sync low-side FET.
- **At low load, loss profile flips:** switching loss, Coss, gate charge, and Iq dominate. Using a smaller MOSFET at low load reduces capacitive losses but limits current capability -- a fundamental tradeoff.

### Input and Output Capacitors

- **Input cap RMS current is the binding constraint -- exceed it and the cap overheats and fails.** Peaks at D=0.5. See Formulas section for sizing calculation. Ceramics only -- aluminum electrolytic cannot handle the ripple current density.
- **Boost output cap supplies load during entire switch on-time** -- significantly larger than buck for same power. Rule of thumb: 2-3x larger than buck equivalent.
- **Aluminum electrolytic ESR increases up to 40x from 25C to -40C.** Below 0C, parallel with ceramic. Below -40C, avoid aluminum entirely -- use tantalum or polymer.
- **Recommended input caps:** Murata GRM X5R (0805: 10uF/25V, 1210: 22uF/25V). Bulk: Panasonic EEH-ZC hybrid polymer (low ESR, handles ripple). Verify RMS rating at operating temp.
- Ceramic DC bias derating, ripple formula, transient sizing -> `power/decoupling.md`.

### Loop Compensation

- **Current mode: Type II (3 passives).** Crossover 1/10 to 1/6 of f_sw. The current loop makes the inductor a controlled current source, reducing the power stage to a quasi-first-order system. Much easier to compensate than voltage mode.
- **Voltage mode: Type III (6 passives).** Double-zeros must be placed around the L-C resonant frequency to compensate the -180 deg phase delay. More sensitive to output cap ESR changes.
- **Stability targets: phase margin >= 45 deg (60 preferred), gain margin >= 10dB.** At least 8dB attenuation at f_sw/2 -- the current-loop sampling effect creates double poles there.
- **Peak current mode at D > 50% needs slope compensation.** Most modern ICs include it internally -- verify in datasheet.
- **Quick debug: 0.1uF on COMP/ITH to ground.** If supply stabilizes, problem is loop compensation. If still unstable, it's current sensing noise or layout -- check Kelvin sense routing.

### Feedback Network

- **Divider current >= 100x IC feedback input bias current.** If IFB = 50nA, divider >= 5uA (max ~500K total resistance). High-Z dividers pick up SW node noise.
- **1% resistors for feedback.** 5% on top leg -> +/-165mV on 3.3V output.
- **Feedforward cap across top resistor:** Cff = 1 / (2 * pi * f_crossover * R_top). Oversizing creates a double zero that pushes gain above unity at f_sw/2.
- **Route FB trace on opposite side from SW node** with ground plane between. 0.1pF coupling at 100V/ns = 10mA noise into the high-Z node.

### SMPS Layout

- **Input ceramic as close as possible to VIN/PGND.** This cap carries the full pulsating input current.
- **Route VIN/GND traces THROUGH filter cap pads, not around them.** A stub adds inductance that defeats HF bypassing.
- **BOOT cap within 3mm of IC** with short traces to BOOT and SW pins. Long path -> erratic gate drive.
- **SW node copper: minimal.** Keep just large enough for current. Do not flood-fill -- it radiates.
- **Compensation components close to IC, not near inductor.** COMP/ITH is high-impedance and extremely sensitive to capacitive coupling from the SW node.
- **Kelvin sense for current-mode control.** Route SENSE+/SENSE- as differential pair directly to sense element. Filter cap at IC pins, not at sense element. If a via is used in the SENSE- net, make sure it does not contact other VOUT planes.
- **Arrange components so current loops curl the same direction in both half-cycles** -- prevents magnetic field reversal and reduces radiated EMI.
- **Shielded inductors for EMC.** Do not route signal traces under power inductors -- even shielded types have residual fringing flux.
- **Power traces: 0.38mm (15mil) per amp minimum.** One via per 200mA when transitioning between layers.

## Common Mistakes

- **Measuring ripple with long scope ground clip.** Ground clip loop picks up radiated SW noise, showing 10x worse ripple than actual. Fix: tip-and-barrel technique with ground loop under 10mm. Wurth ANP039 details the probe-sheath removal method.
- **Inductor DCR thermal runaway in enclosed products.** At 50C ambient, a 100mohm DCR inductor dissipating 0.9W at 3A raises core temp to 90C+. Ferrite permeability drops, ripple increases, losses climb further. In fanless enclosures this positive feedback loop can thermally destroy the inductor within minutes of sustained full load. Fix: derate DCR losses at max ambient, verify with thermal camera under worst-case load.
- **Boost converter backfeeds load during fault/shutdown.** Engineers add an output disconnect FET but forget that the body diode of most load switches conducts Vin to Vout through the inductor when the converter is disabled. A 3.3V-to-5V boost with a P-FET load switch still passes 3.3V to the "off" 5V rail. Fix: back-to-back FETs or a load switch with reverse-blocking (e.g., TPS22918 with <1uA reverse leakage).
- **Output capacitor pre-charge from parallel supply rail causes reverse inductor current.** In multi-rail FPGA boards, a 1.8V rail can backfeed into a disabled 1.2V rail through ESD clamp diodes, pre-charging Cout to ~1.4V. When the 1.2V converter enables, the control loop sees "output too high" and pulls current backwards through the inductor -- tripping OCP or damaging the low-side FET. Fix: verify all inter-rail coupling paths and use ICs with anti-backflow (e.g., TPS54302 skip mode).
- **Feedforward cap creates audio-frequency oscillation during soft-start.** During startup, output voltage ramps slowly and the FB node voltage is near zero. Cff differentiates the ramp, injecting current that overrides the divider ratio and fools the error amplifier into premature regulation. Result: 1-10kHz motorboating until output reaches ~80% of target. Fix: size Cff for steady-state crossover only and verify startup waveform on scope -- some ICs need Cff removed entirely if soft-start is slow.
- **Using 22uF/6.3V X5R cap at 3.3V and trusting the nominal value.** DC bias derating can drop it to 8.2uF actual. Verify derated capacitance with manufacturer tools (Murata SimSurfing, TDK SEAT) before committing. This is especially dangerous on boost output caps where C_out is already borderline.

## Formulas

**Buck inductor:**
**Rule of thumb:** L = Vout * (Vin - Vout) / (0.3 * f_sw * Vin * Iout)
**Formula:** L = Vout * (Vin - Vout) / (Kind * f_sw * Vin * Iout), Kind = 0.2 to 0.4
**Example:** 12V to 3.3V at 3A, 500kHz, 30% ripple -> L = 3.3 * 8.7 / (0.3 * 500e3 * 12 * 3) = 5.3uH -> use 4.7uH standard

**Boost duty cycle (include efficiency):**
**Formula:** D = 1 - (Vin_min * eta) / Vout
**Example:** 3.3V to 5V, eta=0.8 -> D = 1 - (3.3*0.8)/5 = 0.472. Using 90% instead of 80% gives D=0.406 -- the 10% efficiency difference shifts duty cycle enough to change inductor sizing.

**Right-half-plane zero (boost/buck-boost):**
**Rule of thumb:** Set crossover < 1/10 of worst-case f_RHPZ.
**Formula:** f_RHPZ = R_load * (1-D)^2 / (2 * pi * L)
**Example:** 5V/1A (R=5 ohm), D=0.44, L=4.7uH -> f_RHPZ = 5 * 0.56^2 / (6.28 * 4.7e-6) = 53kHz. Crossover < 5.3kHz.

**Input cap RMS current (buck):**
**Rule of thumb:** RMS peaks at D=0.5 (I_rms = 0.5 * Iout).
**Formula:** I_rms = Iout * sqrt(D * (1 - D))
**Example:** 3A, D=0.306 -> I_rms = 3 * sqrt(0.306 * 0.694) = 1.38A. Select input caps rated for >= 1.38A RMS at operating temp.

**Boost output capacitor:**
**Rule of thumb:** Boost output caps 2-3x larger than buck for same power.
**Formula:** C_out = Iout * D / (f_sw * dVout)
**Example:** 5V/1A, D=0.44, f_sw=500kHz, 50mV ripple -> C_out = 1 * 0.44 / (500e3 * 0.05) = 17.6uF minimum (before DC bias derating).

**4-switch buck-boost inductor:**
**Rule of thumb:** Calculate L for buck and boost modes; use the larger.
**Buck mode:** L >= Vout * (Vin_max - Vout) / (0.3 * f_sw * Vin_max * Iout)
**Boost mode:** L >= Vin_min^2 * (Vout - Vin_min) / (0.3 * f_sw * Iout * Vout^2)
**Example:** 2.6-5.0V in, 3.3V/2A, 2MHz -> Buck L = 0.94uH, Boost L = 0.36uH -> use 1.0uH.

**Non-sync vs sync diode loss comparison:**
**Formula (non-sync):** P_diode = Iout * Vf * (1 - D)
**Formula (sync):** P_lowside = Iout^2 * Rds_on * (1 - D)
**Example:** 12V->5V/3A. Non-sync (Vf=0.5V): 875mW. Sync (Rds_on=70mohm): 369mW. Sync saves 506mW -- the crossover where sync wins is roughly Iout > Vf/Rds_on*(1-D), which for typical parts is ~1A.

## Sources

### Related Rules

- `power/ldo.md` -- LDO vs buck decision criteria
- `power/decoupling.md` -- Ceramic DC bias derating, ripple formula, transient sizing, regulator I/O caps

### References

1. ADI AN-140 -- Linear Reg & SMPS Basics: https://www.analog.com/en/resources/app-notes/an-140.html
2. TI SNVA559C -- Switching Regulator Fundamentals: https://www.ti.com/lit/an/snva559c/snva559c.pdf
3. TI SLVA477B -- Buck Converter Power Stage Design: https://www.ti.com/lit/an/slva477b/slva477b.pdf
4. TI SLVA372C -- Boost Converter Power Stage Design: https://www.ti.com/lit/an/slva372c/slva372c.pdf
5. TI SLVA535B -- 4-Switch Buck-Boost Power Stage: https://www.ti.com/lit/an/slva535b/slva535b.pdf
6. ADI AN-149 -- Loop Compensation Design: https://www.analog.com/en/resources/app-notes/an-149.html
7. Rohm -- Efficiency of Buck Converter (9 Loss Mechanisms): https://fscdn.rohm.com/en/products/databook/applinote/ic/power/switching_regulator/buck_converter_efficiency_app-e.pdf
8. Wurth ANP039 -- Power Inductors 8 Design Tips: https://www.we-online.com/components/media/o109038v410%20AppNotes_ANP039_PowerInductors8DesignTipps_EN.pdf
9. TI SLTA055 -- I/O Capacitor Selection: https://www.ti.com/lit/an/slta055/slta055.pdf
10. Wurth DC/DC Handbook Extract -- SMPS from EMC POV: https://www.we-online.com/components/media/o784081v410%20Extract-DCDC_Converter-1.0.pdf
11. TI SNVA021C -- SMPS Layout Guidelines: https://www.ti.com/lit/an/snva021c/snva021c.pdf
