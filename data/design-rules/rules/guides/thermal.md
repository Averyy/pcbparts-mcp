# Thermal Design

> Junction temperature estimation, theta-JA vs psi-JT, exposed pad soldering, thermal vias, PCB copper as heatsink, MOSFET thermal design, heatsink selection.

## Quick Reference

- **theta-JA is for package comparison ONLY.** Varies up to 100% with PCB copper area. Use psi-JT instead: Tj = psi-JT * P + T_top (psi-JT typically 0.5-2 C/W).
- **Exposed pad solder coverage < 10% increases theta-JA by 19%+.** Keep above 50% for < 5% penalty.
- **4-layer PCB with thermal vias nearly doubles power capacity** vs 2-layer (e.g., LFPAK56: 5W -> 9.6W at 20C ambient; e-TSSOP: theta-JA drops from 43-48 to 25-28 C/W).
- **The 1W Rule:** FR4 thermal resistance ~ 50-60 K/W. At 80C ambient, max ~1W per device without heatsink or forced air.
- **Sealed enclosure:** internal air rises 15-25C above external ambient in typical plastic. Use Ta = external_ambient + 20C. Metal enclosures with good thermal contact: 5-10C.

## Design Rules

### Thermal Metrics -- What to Use When

- **theta-JA:** Measured on JEDEC board in sealed still-air enclosure. 70-95% of power dissipates through the PCB, not the package. Never use to predict Tj in a real application -- only for comparing packages against each other.
- **theta-JC (top):** Only valid when a heatsink is attached to the package top and RthJC << RthJA. For plastic packages without heatsinks, gives erroneously high Tj because most heat goes through the board, not the case top.
- **psi-JT (recommended for Tj estimation):** Tj = psi-JT * P + T_top. Typical: 0.5-2 C/W. Small and stable across different PCB designs because heat flow partition between top and board stays roughly constant. For plastic SMD packages, this is the correct metric for in-system temperature estimation.
- **psi-JB:** Tj = psi-JB * P + T_board. Close to theta-JB because 75-95% of heat flows through the board. Use when a board thermocouple is more practical than a package-top thermocouple.
- **Factors affecting theta-JA (rule of thumb):** PCB design 100%, chip/pad size 50%, internal package geometry 35%, altitude 18%, ambient temperature 7%, power dissipation 3%.
- **Altitude derating:** 3000 ft = 1.1x, 5000 ft = 1.14x, 7000 ft = 1.17x, 9000 ft = 1.2x.

### Junction Temperature Measurement

- **Thermocouple at package center:** 36-40 AWG wire, < 2x2mm thermally conductive epoxy bead. Dress wire along package diagonal, down to PCB surface, 25mm along surface before lifting. Heavy-gauge wire causes 5-50% error by sinking heat away from the measurement point.
- **IR camera:** set emissivity to 0.95 for solder mask, 0.85 for black anodized, 0.1-0.2 for bare copper/aluminum. Polished metal at default emissivity reads 30-50C too low. Apply Kapton tape for accurate bare-metal readings.
- **Reliability:** reducing Tj by 10C approximately doubles MTBF (Arrhenius, Ea ~ 0.9 eV). Common derating: target Tj_max - 10C.

### Transient Thermal Impedance (Zth)

- **Steady-state theta-JA is insufficient for pulsed loads.** Use the Zth(j-c) curve from the datasheet for switching regulators, motor drivers, PWM-driven FETs.
- **Short pulses exploit thermal mass of the die.** 100us pulse: Zth ~ 10-20% of steady-state Rth. 10ms pulse: ~50-70%. Die shrinks reduce thermal capacitance -- re-check Zth after die revision.
- **Duty cycle scaling:** effective Zth = Zth(t_on) * D + Zth(T) * (1-D). At D < 0.1, effective Rth is 3-10x lower than steady-state.
- **Foster model** (datasheet Zth curves): node temperatures have no physical meaning. Cannot be cascaded accurately between module and heatsink. For periodic pulses, use the Foster Zth curve directly -- it gives correct transient Tj.
- **Cauer model:** RC elements map to physical layers. Can be cascaded. Required for water-cooled or tightly-coupled systems where heatsink tau overlaps package tau.
- **Datasheet Zth is measured with water-cooled heatsink** (Infineon, most IGBT/MOSFET vendors). Air-cooled heatsinks allow wider heat spreading, producing lower actual Zth(j-c). Datasheet value is conservative.

### Exposed Pad & PowerPAD Design

- **PowerPAD improvement:** 20-pin SSOP standard = 0.75W, PowerPAD = 3.25W (4.3x). 24-pin TSSOP standard = 0.55W, PowerPAD = 2.32W.

> WARNING: Unsoldered or poorly-soldered exposed pad increases theta-JA by 19-34%. Can push Tj above absolute maximum under normal operating conditions.

**Solder coverage impact on theta-JA:**

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
- **Layer count impact** (28-lead e-TSSOP, 2oz/1oz/1oz/2oz): 2-layer = 43-48 C/W, optimized 4-layer = 25-28 C/W (42% reduction). Copper coverage 100% vs 50%: only 3% difference. Ground plane connection to DAP landing pattern on the top layer is the key factor.
- **Copper weight:** 2oz outer layers vs 1oz reduces theta-JA by ~10-15%. Improvement is largest for small packages. Inner layer copper weight matters less -- 1oz is sufficient.
- **Airflow:** 200 LFM reduces theta-JA ~24%. 400 LFM ~30%. Above 400 LFM diminishing returns.

### MOSFET Thermal Design

- **MOSFET proximity:** two MOSFETs within 20mm start heating each other (+20C for LFPAK33). Below 2mm gap on FR4, virtually zero heat transfer between separate copper islands.
- **Split copper pours:** 40x40mm split area (drain + source separate) = 60x60mm solid pour thermally. Two individual LFPAK56 run ~10C cooler than one dual LFPAK56D at same total power.
- **Thermal runaway check:** at max ambient, calculate P_loss(Tj) = I^2 * RDS(ON)(Tj). If dP/dTj > 1/RthJA, thermally unstable. Positive RDS(ON) tempco makes MOSFETs stable for conduction loss, but switching losses (lower threshold at high temp) can destabilize at high frequency.
- **RDS(on) temperature derating:** ~1.5x at 125C, ~1.85x at 175C vs 25C. Always calculate power at max operating temperature, not 25C lab conditions.

**Package power dissipation (natural convection, 20C ambient):**

| Package | theta-JA typical (C/W) | Max P, 1-layer | Max P, 4-layer |
|---------|----------------------|----------------|----------------|
| SOT-23 | 200-300 | 0.3-0.5W | 0.5-0.8W |
| SOT-223 | 50-80 | 1-1.5W | 2-3W |
| DPAK (TO-252) | 40-60 | 2-3W | 4-5W |
| D2PAK (TO-263) | 25-40 | 3-4W | 5-8W |
| LFPAK56 (5x6mm) | 30-50 | 5W | 9.6W |
| LFPAK88 (8x8mm) | 25-40 | 5.9W | 10.7W |
| QFN exposed pad | 20-40 | varies | varies |

- **SOT-23 thermal wall:** at 200 C/W, even 0.5W raises Tj by 100C. Any linear regulator or MOSFET > 300mW needs a larger package. SOT-223 minimum for 0.5-1.5W. DPAK or exposed-pad QFN for > 2W.
- **When to upgrade:** if P_diss > 50% of package max at your ambient, move up one package size. 50% margin covers PCB layout variation, manufacturing tolerance, thermal aging.
- MOSFET RDS(on) temperature derating -> `protection/reverse-polarity.md`.

### Heatsink Selection

- **Heatsink width scales linearly; length follows sqrt.** 2x width = 2x dissipation. 2x length = only 1.4x. If board space allows, always increase width (perpendicular to airflow) rather than length.
- **Paint or anodize heatsink surfaces.** Radiation is ~25% of natural convection transfer. Polished aluminum emissivity ~0.05; black anodized ~0.85.
- **Fan selection:** target 200-400 LFM for 2-3x improvement over natural convection. Fan noise scales as speed^5 -- 20% speed reduction cuts noise nearly in half.

**Volumetric heatsink resistance (theta-SA * volume):**

| Airflow | Volumetric Resistance (cm3 * C/W) |
|---------|----------------------------------|
| Natural convection | 500-800 |
| 200 LFM | 150-250 |
| 500 LFM | 80-150 |

- **Heatsink families:** Same Sky BGA-STD for BGA/QFN (board-level, clip-on/adhesive). TO-220: Same Sky HSxx or Aavid/Boyd 530xxx. SOT-223/DPAK: PCB copper pour is primary heatsink -- board-level heatsinks rarely outperform 4-layer copper with thermal vias.
- **TIM selection:** Prototyping: thermal grease (k = 0.7-5 W/(m*K)), removable. Production: thermal pads (Bergquist Gap Pad, Henkel Gap Filler), lower k (1-5 W/(m*K)) but consistent bond line. High-reliability: phase-change TIMs (k = 3-5 W/(m*K)) prevent grease pump-out.

## Common Mistakes

- **Using theta-JA * P + Ta to predict Tj.** theta-JA varies up to 100% with PCB copper area. A 40 C/W datasheet value could be 25 C/W or 50 C/W on your board. Fix: use psi-JT with measured package temperature.
- **theta-JC used for plastic packages without heatsink.** Assumes all heat goes through the case top. In reality, 70-95% goes through the board. Result: calculated Tj is much higher than actual, potentially causing over-design or wrong package choice. Fix: use psi-JT or psi-JB.
- **Using 25C lab ambient for thermal calculations.** Products operate in enclosures (50-60C internal) or automotive (85-125C). Fix: use external Ta + 20C for sealed plastic enclosures, or application-specified max ambient.
- **LDO sized without thermal check.** 5V to 1.8V at 100mA = 320mW. SOT-23 at 70C: Tj = 70 + 0.32 * 200 = 134C -- exceeds 125C limit. Fix: always verify Tj at max ambient -> `power/ldo.md`.
- **Thermal design validated only at steady-state.** Motor drivers with 10A pulses at 10% duty cycle may exceed Tj_max during each pulse even though average is fine. Fix: check Zth curve for pulse width.
- **Reading bare metal with IR camera at default emissivity.** Polished copper/aluminum emissivity ~0.05. Camera set to 0.95 reads 30-50C too low. Fix: apply Kapton tape or set emissivity to match surface.
- **Heavy-gauge thermocouple on package top.** 30+ AWG thermocouple wire sinks heat, reading 5-50% lower delta between ambient and surface temperature. Fix: use 36-40 AWG with thermally conductive epoxy bead < 2x2mm, dressed 25mm along PCB before lifting.

## Formulas

**Junction temperature (psi-JT method):**
**Rule of thumb:** psi-JT is typically 0.5-2 C/W. Much smaller and more stable than theta-JA.
**Formula:** Tj = psi-JT * P + T_top
**Example:** psi-JT = 1.5 C/W, P = 2W, T_top measured = 65C -> Tj = 1.5 * 2 + 65 = 68C.

**Heatsink thermal budget:**
**Rule of thumb:** Budget 20% margin on theta-SA for manufacturing variation and aging.
**Formula:** theta-SA = (Tj_max - Ta) / P - theta-JC - theta-CS
**Example:** TO-220, 2.78W, Ta = 50C, Tj_max = 125C, theta-JC = 0.5 C/W, theta-CS = 0.45 C/W -> theta-SA = 75/2.78 - 0.5 - 0.45 = 26.05 C/W max. Selected heatsink: 19.1 C/W -> Tj = 50 + 2.78 * (0.5 + 0.45 + 19.1) = 105.7C, 19C margin.

**TIM thermal impedance:**
**Rule of thumb:** theta-CS for thermal grease is 0.2-1 C/W for TO-220 size. Thermal pads are 2-5x higher.
**Formula:** theta-CS = thickness / (k_TIM * area)
**Example:** 0.04mm grease (k = 0.79 W/(m*K)), TO-220 tab (112mm2): theta-CS = 0.04e-3 / (0.79 * 112e-6) = 0.45 C/W.

**Pulsed power peak Tj:**
**Rule of thumb:** Pulses < 1ms: Zth ~ 10-20% of steady-state. 10ms pulses: ~50-70%.
**Formula:** Tj_peak = Zth(j-c)(t_pulse) * P_peak + Tc
**Example:** Zth(j-c) at 1ms = 0.3 C/W (steady-state = 2 C/W). P_peak = 50W, Tc = 80C -> Tj_peak = 0.3 * 50 + 80 = 95C. Steady-state would predict 180C (too pessimistic).

**Thermal via array resistance:**
**Rule of thumb:** 4 vias (0.3mm drill, 1oz plating) in a 3x3mm exposed pad contribute ~15-20 C/W to the pad-to-plane path.
**Formula:** Rth_via = h / (k_cu * pi * d * t * N) where h = board thickness, d = via diameter, t = plating thickness, N = number of vias
**Example:** 1.6mm board, 0.3mm drill, 25um plating, 4 vias -> Rth_via = 0.0016 / (385 * 3.14 * 0.3e-3 * 25e-6 * 4) = 44 C/W (via barrel only). Total pad-to-plane Rth is lower (~15-20 C/W) because copper spreading in inner planes dominates.

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
