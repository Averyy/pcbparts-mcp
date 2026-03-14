# Isolation

> Digital isolator vs optocoupler selection, creepage/clearance for PCB design, stitching capacitance for EMI compliance, and isolated power.

## Quick Reference

- **Digital isolator is the default.** SiO2 ~500 V/um vs mold compound ~100 V/um. TDDB lifetime ~100x longer. No aging, CMOS input (+/-10uA vs 2-16mA LED drive). Optocoupler only for analog proportional isolation or legacy cert.
- **WB SOIC-16 actual creepage = 7.6mm, not 8mm.** JEDEC metal tabs reduce effective distance per IEC 60112. Conformal coating restores 8mm.
- **PCB creepage uses FR4 material group (IIIa), not IC material group (I).** IC package may meet 4mm (Group I), but FR4 traces need 8mm (Group IIIa) for 400V reinforced.
- **300pF stitching capacitance is the primary EMI fix.** Without it at 5V/1 Mbps, standard 4-layer board fails CISPR 22 Class B by 4dB. With 300pF: passes Class A and B by wide margin.
- **Optocoupler CTR degrades ~50% over 10 years.** Design for end-of-life: CTR_min = CTR_typ * 0.83 (temp) * 0.80 (aging) * 0.75 (mfg).

## Design Rules

### Digital Isolators vs Optocouplers

| Parameter | Gen-Purpose Opto | High-Speed Opto | Digital Isolator (ISO6741) |
|-----------|-----------------|-----------------|---------------------------|
| Rise/fall | 2-35 us | 15 ns | 4.5 ns |
| Prop delay | 3-40 us | 27-40 ns | 11 ns |
| Max data rate | 0.1 Mbps | 12.5 Mbps | 47.6 Mbps |
| CMTI (min) | N/A | +/-20 kV/us | +/-150 kV/us |
| Input drive | 2-16 mA | 6-14 mA | +/-10 uA (CMOS) |
| Input capacitance | ~60 pF | ~60 pF | ~1.5 pF |
| Aging | CTR -50%/10yr | CTR -50%/10yr | None |

- **Digital isolator families:** TI ISO67xx (47.6 Mbps, 5 kVRMS, 150 kV/us CMTI). ISO77xx/ISO78xx (100 Mbps, 5.7 kVRMS, 12.8 kV surge, supply down to 2.25V). ISO6441 (150 Mbps, highest single-chip data rate). Skyworks Si86xx/Si87xx. ADI ADuM series.
- **Integrated isolated functions:** ISOW77xx (digital isolation + DC-DC), ISO14xx/ISO1500 (isolated RS-485). ISO14xx: 5 kVRMS, Profibus-compliant, 30 kV HBM ESD, 16 kV IEC ESD, 4 kV EFT built-in.
- **Isolated SPI for BMS daisy-chain:** ADI LTC6820 isoSPI -- bidirectional SPI over single twisted pair through pulse transformer, 1 Mbps, up to 100m cable, 2uA idle. No software changes needed vs standard SPI.
- **Optocoupler use cases:** analog proportional output (linear optocouplers for feedback loops), specific certification mandates requiring optocouplers, legacy drop-in where board is already qualified.

### Creepage & Clearance

- **IC package vs PCB -- PCB is usually the bottleneck.** IC mold compound is Material Group I (CTI >= 600V, halves creepage). FR4 is Group IIIa (CTI 175-400V). A TI isolator needing 4mm creepage (Group I) sits on FR4 needing 8mm (Group IIIa) for the same voltage.
- **WB SOIC-16: actual 7.6mm, not 8mm.** Metal tabs from JEDEC standard manufacturing reduce creepage per IEC 60112. All isolation vendors using standard JEDEC WB SOIC-16 have this limitation. At 400V reinforced (Group IIIa needs 8.0mm), 7.6mm fails. Conformal coating restores 8mm.
- **Reinforced insulation: double all basic creepage values.**

**Creepage (IEC 62368-1/IEC 60664-1, PD2, basic insulation):**

| Working V (VRMS) | Group I | Group IIIa (FR4) |
|------------------|---------|------------------|
| 100 | 0.7 mm | 1.4 mm |
| 150 | 0.8 mm | 1.6 mm |
| 250 | 1.3 mm | 2.5 mm |
| 400 | 2.0 mm | 4.0 mm |

**Clearance (IEC 62368-1, OV Cat II):**

| Line-Neutral VRMS | Impulse | Basic | Reinforced |
|-------------------|---------|-------|------------|
| <=150 (US 120V) | 1500V | 0.76 mm | 1.8 mm |
| <=300 (EU 230V) | 2500V | 1.8 mm | 3.6 mm |
| <=600 (industrial) | 4000V | 3.8 mm | 7.9 mm |

- **Altitude correction:** above 2000m, multiply clearance by correction factor from IEC 60664-1 Table A.2. 5000m: 1.48x. Example: 230V reinforced clearance 3.6mm * 1.48 = 5.33mm.
- **PCB grooves increase creepage:** effective = existing + groove width + 2x groove depth. Minimum groove width: PD1=0.25mm, PD2=1.0mm, PD3=1.5mm.
- **Inner layer spacing for reinforced:** >= 0.4mm FR4 between copper structures (dielectric strength 40 kV/mm -> 16 kV at 0.4mm). Two cemented joints through 0.4mm FR4 qualifies as reinforced under IEC 60950.
- **Hi-pot test:** 2 * working voltage + 1000V. 265 VAC working -> 1530V test -> commonly 1.5 kV.

### PCB Layout for Isolation Barrier

- **No traces, vias, fills, or pads across barrier on ANY layer.** Gap must be clear through entire stack-up. Inner-layer short = safety failure.
- **4-layer minimum.** Stack: top signal, ground, power, bottom signal. Ground plane adjacent to signal layer gives controlled impedance and low-inductance return paths. 2-layer boards cannot manage return current paths or stitching effectively.

**Stitching capacitance (primary EMI fix):**

- **Y2 safety cap:** effective to ~200 MHz. Single stitching point. Simple to add/replace. Place within 10mm of isolator IC -- board edge adds inductance that negates HF bypass. Parasitic inductance from pads/traces localizes the bypass.
- **Overlapping ground planes:** extend primary/secondary reference planes into gap on internal layers. One cemented joint = basic insulation only. Very low inductance, distributed over large area -- effective above 200 MHz where discrete caps roll off. Most area-efficient: capacitance per unit area is 2x that of floating plane method.
- **Floating metal plane:** copper on internal layer spans full gap with dielectric both sides. Two cemented joints = reinforced insulation. Net capacitance halved (series). Better for reinforced insulation requirements but less area-efficient.
- **Medical:** total stitching <= 10-20pF to limit patient leakage current. Single small Y1 cap instead of plane overlap.

**Stitching budget from ADI AN-1109 anechoic chamber data (ADuM1402, 4-layer board):**

| Condition | CISPR 22 Class A | CISPR 22 Class B |
|-----------|-----------------|-----------------|
| No stitching, 5V, 1 Mbps | Pass by ~6 dB | FAIL by 4 dB |
| 150pF stitching, 5V, 1 Mbps | Pass | Pass |
| 300pF stitching, 5V, 1 Mbps | Pass by wide margin | Pass by wide margin |
| No stitching, 3.3V, 1 Mbps | Pass | Pass |
| No stitching, 5V, 10 Mbps | FAIL | FAIL by 15-24 dB |
| ~400pF stitching, 5V, 10 Mbps | Pass | Pass (need all techniques) |

- **3.3V vs 5V:** 3.3V reduces emissions enough for CISPR 22 Class B at 1 Mbps without stitching on standard 4-layer. Prefer 3.3V when possible.
- **Interplane capacitance:** 0.1mm core between GND and VDD planes reduces VDD noise from 0.17V p-p to 0.03V p-p. Supplements stitching at 300 MHz-1 GHz.
- **Edge guard via fence:** 4mm via spacing, tying ground fills to reference plane every 10mm. Provides ~1-2dB additional reduction. Remove thin copper fill fingers (act as patch antennas).

- ESD on isolated interfaces -> `protection/esd.md`. Ground planes, stackup -> `guides/pcb-layout.md`. Isolated CAN -> `interfaces/can.md`.

### Isolated Power

- **SN6505B push-pull transformer driver:** up to 5W, external center-tapped transformer, secondary full-wave rectified with Schottky + LDO. SN6501: up to 1.5W, simpler.
- **Integrated:** TI ISOW77xx -- digital isolation + DC-DC in single 16-SOIC. Limited power budget per variant.
- **>5W -> flyback** -> `power/switching.md`.

### Optocoupler Design

- **CTR derating for 10-year life:** design for ~50% of typical CTR (see Formulas section for derating factors). Always calculate IF at end-of-life CTR, not typical.
- **Emitter config (faster, up to 100 kbit/s):** output from emitter with pull-down resistor. No saturation -> faster recovery. VCC=5V, RL=390 ohm, CTR_min=50%, IF=12.3mA -> output swings 0.4-2.4V with 20% noise margin to TTL thresholds.
- **Collector config (slower, up to 28 kbit/s):** output from collector with pull-up. Transistor saturates -> slow VCEsat recovery. Derate CTR further to 25% for saturation (VCEsat < 0.5V at IC < 5mA, CTR halved vs emitter config). RL=5.1K typical.
- **Reducing IF from 10mA to 5mA quadruples projected LED lifetime.** Black Model: AF = (I_stress/I_use)^2 * exp(0.43eV/K * (1/T_use - 1/T_stress)). At IF=5mA, TA=60C: AF~185x from HTOL data (20mA/125C) -> >20 years with <10% CTR loss.
- **Input resistor:** RV = (VCC - VF - VOL) / IF. VF ~ 1.2V for IR LED. Calculate at end-of-life CTR to ensure sufficient IF.

## Common Mistakes

- **Conformal coating applied after assembly bridges isolation gap.** Silicone coating wicks along component leads and between pads, creating conductive path when contaminated. Use solder dam or masking tape to keep coating 1-2mm back from barrier edge, or specify selective coating in assembly drawing.
- **Secondary-side LDO ground return routed under isolation gap.** Low-frequency power return on inner layer creates a loop that couples 50/60 Hz mains noise into secondary circuits. Route all secondary power/ground on secondary side only; verify with cross-section view in EDA.
- **Traces or vias crossing barrier on inner layers.** Gap looks clean on surface but is shorted internally. Define keep-out zone spanning ALL layers in EDA tool.
- **Optocoupler collector config used at >50 kbit/s without speed-up capacitor.** VCEsat recovery time in collector config limits bandwidth to ~28 kbit/s. Adding 10-22pF across the collector resistor creates a differentiated edge that cuts propagation delay 3-5x, but overshoot must be verified against downstream logic thresholds.
- **Isolated DC-DC transformer not derated for altitude.** Transformer insulation breakdown voltage drops above 2000m (same IEC 60664-1 altitude correction as clearance). A transformer rated 4 kVRMS at sea level may only provide 2.7 kV at 5000m after 1.48x derating -- below the 3 kV reinforced requirement.
- **Y-cap replaced with standard X-cap during rework.** X-caps are not rated for line-to-ground and lack the reinforced insulation and fail-open behavior of Y-caps. A shorted X-cap across the barrier creates a direct mains-to-secondary fault. Mark Y-cap positions on silkscreen with safety symbol.

## Formulas

**Creepage/clearance lookup:**
**Rule of thumb:** 230V mains reinforced: ~6.4mm creepage (Group IIIa), ~3.6mm clearance. At 5000m altitude: clearance 5.33mm.
**Procedure:** Working voltage -> IEC 62368-1 Table 17 (creepage by material group) and Table 10 (clearance by impulse voltage). Reinforced: double creepage, use IEC 62368-1 reinforced column for clearance. Altitude > 2000m: multiply clearance by IEC 60664-1 Table A.2 factor.
**Example:** 230V telecom, PD2, reinforced -> creepage: Group I 4mm, Group IIIa 8mm. Impulse 2.5kV -> clearance 3.6mm. At 5000m: 3.6 * 1.48 = 5.33mm.

**Stitching capacitance (overlapping planes):**
**Rule of thumb:** 300pF for single-channel 5V/1 Mbps. ~400pF for multi-channel 10 Mbps.
**Formula:** C = epsilon_0 * epsilon_r * A / d = (8.854e-12 * 4.5 * A) / d
**Example:** 8mm * 100mm overlap, 0.1mm FR4 core -> C = (8.854e-12 * 4.5 * 800e-6) / 0.1e-3 = 318pF. Floating plane: halve result (two caps in series).

**Optocoupler CTR derating:**
**Rule of thumb:** Design for 50% of typical CTR for 10-year life at <=60C.
**Formula:** CTR_min = CTR_typ * 0.83 (temp) * 0.80 (aging) * 0.75 (mfg tolerance)
**Example:** CTR_typ=100% at IF=10mA -> CTR_min = 100 * 0.83 * 0.80 * 0.75 = 49.8% -> design for ~50%.

## Sources

### Related Rules

- `protection/esd.md` -- ESD protection on isolated interfaces
- `guides/pcb-layout.md` -- Ground planes, stackup, and return current management
- `interfaces/can.md` -- Isolated CAN bus design
- `power/switching.md` -- Flyback topology for isolated power > 5W

### References

1. TI SLLA284 -- Digital Isolator Design Guide: https://www.ti.com/document-viewer/lit/html/SLLA284
2. TI SLLA526 -- Improve Your System Performance by Replacing Optocouplers with Digital Isolators: https://www.ti.com/document-viewer/lit/html/SLLA526
3. TI SLLA453 -- Isolated RS-485 Transceiver Reference Design: https://www.ti.com/document-viewer/lit/html/SLLA453
4. TI SLUP419 -- Demystifying Clearance and Creepage Distance: https://www.ti.com/document-viewer/lit/html/SLUP419
5. ADI AN-1109 -- Recommendations for Control of Radiated Emissions with iCoupler Devices: https://www.analog.com/en/resources/app-notes/an-1109.html
6. ADI LTC6820 Datasheet -- isoSPI Isolated Communications Interface: https://www.analog.com/media/en/technical-documentation/data-sheets/LTC6820.pdf
7. Skyworks AN583 -- Safety Considerations and Layout Recommendations for Digital Isolators: https://www.skyworksinc.com/-/media/SkyWorks/SL/documents/public/application-notes/AN583.pdf
8. Broadcom AV02-3401EN -- Calculate Reliable LED Lifetime Performance in Optocouplers: https://docs.broadcom.com/doc/AV02-3401EN
9. Vishay AN02 -- Optocoupler Application Examples (CTR Derating and Interface Circuits): https://www.vishay.com/docs/83741/83741.pdf
