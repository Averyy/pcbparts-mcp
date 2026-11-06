# Thermal Design

> Junction temperature estimation, theta-JA vs psi-JT, exposed pad soldering, thermal vias, PCB copper as heatsink, MOSFET thermal design, heatsink selection.

## Quick Reference

- **Datasheet theta-JA compares packages on a JEDEC board; it isn't your board's value** (varies up to 100% with copper area). Before layout, model the board's effective theta-JA; on the built board, Tj = T_top + psi-JT * P with measured T_top and no top heatsink [2, secs.1.8, 3].
- **Exposed pad solder coverage:** in TI's FEA, 50% centered coverage cost +4% theta-JA and 10% cost +19%; the critical coverage depends on package and board [4, sec.5.2].
- **More copper layers and thermal vias roughly double power capacity** (Nexperia LFPAK56: 5.05W on 1 layer -> 9.6W on 4; conditions below) [9, sec.4].
- **The 1W example:** board Rth 50 K/W, FR4 limit 130C, Ta 80C -> 1W per device without heatsink or airflow; board size and copper change it [9, sec.2.3.3].
- **Ambient is the air next to the part at the worst case,** not the room: TI cites 50-60C inside typical enclosures [7]. Model it before layout and measure it in the powered enclosure; no fixed enclosure offset is sourced [2, sec.7].

## Design Rules

### Thermal Metrics -- What to Use When

- **theta-JA:** measured on a JEDEC board in still air, where 70-95% of the power leaves through the PCB. Use the datasheet value only to compare packages; predict Tj with an effective theta-JA modeled or measured for your board, neighbouring loads included [2, secs.1.1, 1.8].
- **theta-JC (top):** valid when a heatsink on the package top takes most of the heat (theta-JC << board-path theta-JA). Without one, it gives a falsely high Tj because most heat goes through the board [2, sec.2.2].
- **psi-JT (Tj on the built board):** Tj = T_top + psi-JT * P, using the device's psi-JT (TI: typically 0.5-2 C/W for plastic packages) and a measured T_top, with no top heatsink. It moves less than theta-JA between boards, but board and airflow still change it [2, secs.3, 3.2].
- **psi-JB:** Tj = T_board + psi-JB * P, with T_board measured at the center package lead or nearest BGA breakout with a fine-wire sensor [2, secs.4.1, 5].
- **Factors affecting theta-JA (rule of thumb):** PCB design 100%, chip/pad size 50%, internal package geometry 35%, altitude 18%, ambient temperature 7%, power dissipation 3%.
- **Altitude derating:** 3000 ft = 1.1x, 5000 ft = 1.14x, 7000 ft = 1.17x, 9000 ft = 1.2x.

### Junction Temperature Measurement

- **Thermocouple at package center:** 36-40 AWG wire, < 2x2mm thermally conductive epoxy bead. Dress wire along package diagonal, down to PCB surface, 25mm along surface before lifting. Heavy-gauge wire causes 5-50% error by sinking heat away from the measurement point.
- **IR camera:** set emissivity to 0.95 for solder mask, 0.85 for black anodized, 0.1-0.2 for bare copper/aluminum. Polished metal at default emissivity reads 30-50C too low. Apply Kapton tape for accurate bare-metal readings.
- **Reliability example:** with Ea = 0.9 eV, 125C -> 115C roughly doubles MTBF (Arrhenius); the factor depends on the failure mechanism, and TI notes many applications need no derating [1, sec.7.3].

### Transient Thermal Impedance (Zth)

- **Steady-state theta-JA is insufficient for pulsed loads.** Use the datasheet Zth(j-c) curve, which needs the case temperature Tc(t), not ambient [10, sec.2.1].
- **Short pulses exploit thermal mass of the die.** Read Zth at the pulse width from the exact device's curve; its fraction of steady-state Rth depends on the device's RC time constants [10, sec.2.1]. Die shrinks reduce thermal capacitance -- re-check Zth after a die revision.
- **Repeated pulses:** use the datasheet's Zth curve for your duty cycle, or convolve the loss waveform with dZth/dt [10, sec.2.1]. A single-pulse Zth at the pulse width ignores heat left from earlier pulses and underestimates peak Tj.
- **Foster model** (datasheet Zth curves): node temperatures have no physical meaning, and it can't be cascaded accurately between module and heatsink [10, sec.2.3].
- **Module + heatsink with overlapping time constants:** model or measure the whole path. A Cauer network converted from Foster data doesn't guarantee physical nodes or accurate cascading [10, sec.2.3].
- **Infineon characterizes IGBT-module Zth with a water-cooled bar,** which gave higher Rth(j-c) than the air-cooled setup it compared [10, sec.2.3.2]. Check how your device's vendor measured before assuming the datasheet is conservative.

### Exposed Pad & PowerPAD Design

- **PowerPAD improvement (TI model, Tj 150C, Ta 80C; standard package on a low-k board vs soldered PowerPAD on TI's board):** 20-pin SSOP 0.75W -> 3.25W (4.3x). 24-pin TSSOP 0.55W -> 2.32W [3, App.A].

> WARNING: Solder the exposed pad down. TI warns an unsoldered pad degrades both thermal performance and mechanical integrity;
> its reduced-coverage FEA below already shows +19-34% theta-JA at 5-10% coverage [3, sec.2.1; 4, sec.5.2].

**Solder coverage impact on theta-JA (TI FEA, centered solder) [4, sec.5.2]:**

| Solder Coverage | theta-JA Increase |
|----------------|-------------------|
| 100% (baseline) | 0% |
| 50% | +4% |
| 20% | +13% |
| 10% | +19% (critical inflection) |
| 5% | +34% |

- **Via diameter matters for small pads:** 0.33mm preferred over 0.2mm -- 15-25% lower theta-JA for pads with <= 4 vias. Difference < 10% for >= 9 vias. For 1-2 vias, via diameter is the dominant thermal variable.
- **TI recommended:** 0.3mm via diameter, 1.5mm pitch, distributed across exposed pad. For packages with small exposed pads, place vias near the periphery of the pad if maximum count is not feasible.
- **Solder resist on surrounding copper reduces theta-JA by ~5%** due to higher emissivity (0.9 vs 0.5 for bare copper). Leave exposed pad unmasked for soldering, mask surrounding copper.
- General via design rules -> `guides/pcb-layout.md`.

### PCB Copper as Heatsink

- **Diminishing returns above ~30-40mm copper side length.** 20x20mm to 40x40mm: theta-JA drops ~30%. 40x40mm to 80x80mm: only ~15% more. Cross-hatched copper at 50% fill: only +3% vs solid copper.
- **Layer count impact (TI LM2652, 28-lead e-TSSOP, 2W):** 2-layer 1oz/1oz = 43.4 C/W, 4-layer 2/1/1/2 oz = 25 C/W (42% lower); plane geometry and copper changed too. Copper coverage 100% vs 50%: only 3% difference. Ground plane connection to the DAP landing pattern on the top layer is the key factor [4, Table 2].
- **Copper weight:** 2oz outer layers vs 1oz reduces theta-JA by ~10-15%. Improvement is largest for small packages. Inner layer copper weight matters less -- 1oz is sufficient.
- **Airflow:** 200 LFM reduces theta-JA ~24%. 400 LFM ~30%. Above 400 LFM diminishing returns.

### MOSFET Thermal Design

- **MOSFET proximity (Nexperia simulation, single top copper layer, 0.5W each):** two LFPAK33 closer than 20 mm ran up to 20C hotter; separate copper areas 2 mm apart (LFPAK56D halves) passed almost no heat across the FR4 [9, sec.3.3].
- **Split copper pours:** 40x40mm split area (drain + source separate) = 60x60mm solid pour thermally. Two individual LFPAK56 run ~10C cooler than one dual LFPAK56D at same total power.
- **Thermal runaway check:** at max ambient, calculate P_loss(Tj) = I^2 * RDS(ON)(Tj) plus switching loss. Stable only if dP_loss/dTj < 1/theta-JA(effective) at the operating point [2, sec.1.8; 9, sec.2]. At fixed current a positive RDS(ON) tempco raises the loss as it heats; it helps current sharing between paralleled FETs, not single-device stability.
- **RDS(on) temperature derating:** ~1.5x at 125C, ~1.85x at 175C vs 25C. Always calculate power at max operating temperature, not 25C lab conditions.

**Package power, Nexperia simulation** (100x100x1.6 mm FR4, 2 oz per layer, natural convection, Ta 20C, Tj 175C, PCB temperature limit not applied) [9, sec.4]: LFPAK56 5.05W on 1 layer, 9.6W on 4 layers with vias; LFPAK88 5.9W and 10.65W. Other packages need the device's own data and a board model; no generic package table is sourced.

- **SOT-23 thermal wall:** at an assumed board theta-JA of 200 C/W, 0.5W raises Tj by 100C. Pick the package and copper from the actual ambient, Tj limit and board model [2, sec.1.8].
- **Margin:** set it from the device's limits and the product's reliability target, calculated on the actual board; no fixed percentage is sourced [1, sec.7.3].
- MOSFET RDS(on) temperature derating -> `protection/reverse-polarity.md`.

### Heatsink Selection

- **Heatsink width scales linearly; length follows sqrt.** 2x width = 2x dissipation. 2x length = only 1.4x. If board space allows, always increase width (perpendicular to airflow) rather than length.
- **Paint or anodize heatsink surfaces.** Radiation is ~25% of natural convection transfer. Polished aluminum emissivity ~0.05; black anodized ~0.85.
- **Fan selection:** size from the heatsink's thermal resistance vs airflow curve at the system's real airflow [7]. Fan-law estimate (no source in References): sound power ~ speed^5, so 20% slower is ~5 dB quieter.

**Volumetric heatsink resistance (theta-SA * volume):**

| Airflow | Volumetric Resistance (cm3 * C/W) |
|---------|----------------------------------|
| Natural convection | 500-800 |
| 200 LFM | 150-250 |
| 500 LFM | 80-150 |

- **Heatsink families:** Same Sky BGA-STD for BGA/QFN (board-level, clip-on/adhesive). TO-220: Same Sky HSxx or Aavid/Boyd 530xxx. SOT-223/DPAK: PCB copper pour is primary heatsink -- board-level heatsinks rarely outperform 4-layer copper with thermal vias.
- **TIM selection:** Prototyping: thermal grease (k = 0.7-5 W/(m*K)), removable. Production: thermal pads (Bergquist Gap Pad, Henkel Gap Filler), lower k (1-5 W/(m*K)) but consistent bond line. High-reliability: phase-change TIMs (k = 3-5 W/(m*K)) prevent grease pump-out.

## Common Mistakes

- **Using 25C lab ambient for thermal calculations.** Products run in enclosures (TI: 50-60C typical) or automotive (85-125C). Fix: use the application's maximum local ambient, measured where the part is [7; 2, sec.7].
- **LDO sized without thermal check.** 5V to 1.8V at 100mA = 320mW. At 70C with an assumed 200 C/W board theta-JA (SOT-23): Tj = 70 + 0.32 * 200 = 134C, above a 125C limit. Fix: always verify Tj at max ambient -> `power/ldo.md`.
- **Thermal design validated only at steady-state.** A motor driver's pulses can exceed Tj_max during each pulse while the average is fine. Fix: calculate peak Tj from the losses, pulse width, period and case temperature with the Zth curve [10, sec.2.1].
- **Reading bare metal with IR camera at default emissivity.** Polished copper/aluminum emissivity ~0.05. Camera set to 0.95 reads 30-50C too low. Fix: apply Kapton tape or set emissivity to match surface.
- **Heavy-gauge thermocouple on package top.** 30+ AWG thermocouple wire sinks heat, reading 5-50% lower delta between ambient and surface temperature. Fix: use 36-40 AWG with thermally conductive epoxy bead < 2x2mm, dressed 25mm along PCB before lifting.

## Formulas

**Heatsink thermal budget:**
**Condition:** the series budget assumes most of the heat goes into the heatsink [2, sec.2.2].
**Formula:** theta-SA = (Tj_max - Ta) / P - theta-JC - theta-CS
**Example:** TO-220, 2.78W, Ta = 50C, Tj_max = 125C, theta-JC = 0.5 C/W, theta-CS = 0.45 C/W -> theta-SA = 75/2.78 - 0.5 - 0.45 = 26.03 C/W max. Selected heatsink: 19.1 C/W -> Tj = 50 + 2.78 * (0.5 + 0.45 + 19.1) = 105.7C, 19C margin [12].

**TIM thermal impedance:**
**Rule of thumb:** theta-CS for thermal grease is 0.2-1 C/W for TO-220 size. Thermal pads are 2-5x higher.
**Formula:** theta-CS = thickness / (k_TIM * area)
**Example:** 0.04mm grease (k = 0.79 W/(m*K)), TO-220 tab (112mm2): theta-CS = 0.04e-3 / (0.79 * 112e-6) = 0.45 C/W.

**Pulsed power peak Tj:**
**Rule of thumb:** a single pulse starting at Tj = Tc, with Tc fixed; for pulse trains see Transient Thermal Impedance above [10, sec.2.1].
**Formula:** Tj_peak = Tc + P_peak * Zth(j-c)(t_pulse)  (Zth in C/W: multiply a normalized curve by Rth first)
**Example:** isolated 1ms pulse, Zth(j-c) = 0.3 C/W (steady-state 2 C/W), P_peak = 50W, Tc = 80C -> Tj_peak = 95C. Steady-state would predict 180C.

**Thermal via array resistance:**
**Rule of thumb:** use the actual barrel plating and the depth to the plane that takes the heat [9, Eq.2].
**Formula:** Rth_via = h / (k_cu * pi * d * t * N) where h = board thickness, d = via diameter, t = plating thickness, N = number of vias
**Example:** 1.6mm board, 0.3mm drill, 25um plating, 4 vias -> Rth_via = 0.0016 / (385 * 3.14 * 0.3e-3 * 25e-6 * 4) = 44 C/W (thin-wall barrels). To an inner plane, use its depth for h; spreading in the copper adds resistance in series [9, Eq.2].

## Sources

### Related Rules

- `guides/pcb-layout.md` -- Via design rules, copper pour, stackup selection
- `protection/reverse-polarity.md` -- MOSFET RDS(on) temperature derating
- `power/ldo.md` -- LDO thermal verification, dropout and power dissipation

### References

1. TI SLVA118A -- LDO Regulator Design Guide: https://www.ti.com/lit/an/slva118a/slva118a.pdf
2. TI SPRA953C -- Semiconductor/IC Package Thermal Metrics: https://www.ti.com/lit/an/spra953c/spra953c.pdf
3. TI SLMA002H -- PowerPAD Thermally Enhanced Package: https://www.ti.com/lit/pdf/slma002
4. TI SNVA183B -- Board Layout for Best Thermal Resistance: https://www.ti.com/lit/an/snva183b/snva183b.pdf
5. ADI -- Maximize Power Capability in Thermal Design Part 1: https://www.analog.com/en/resources/analog-dialogue/articles/maximize-power-capability-in-thermal-design-part-1.html
6. ADI AN-140 -- Linear vs Switching Regulators: https://www.analog.com/en/resources/app-notes/an-140.html
7. TI SLVA462 -- Heatsink Design and Selection: https://www.ti.com/lit/an/slva462/slva462.pdf
8. TI SLUP239A -- Understanding LDO Regulators: https://www.ti.com/lit/ml/slup239/slup239.pdf
9. Nexperia AN90003 -- LFPAK MOSFET Thermal Design Guide: https://assets.nexperia.com/documents/application-note/AN90003.pdf
10. Infineon AN2015-10 -- Transient Thermal Measurements and Thermal Equivalent Circuit Models: https://www.infineon.com/dgdl/Infineon-AN2015_10_Thermal_equivalent_circuit_models-AN-v01_00-EN.pdf?fileId=db3a30431a5c32f2011aa65358394dd2
11. ROHM 65AN114E -- theta-JA and psi-JT: https://fscdn.rohm.com/en/products/databook/applinote/common/theta_ja_and_psi_jt_an-e.pdf
12. Same Sky -- How to Select a Heat Sink: https://www.sameskydevices.com/blog/how-to-select-a-heat-sink
