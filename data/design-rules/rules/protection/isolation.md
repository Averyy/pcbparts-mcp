# Isolation

> Digital isolator vs optocoupler selection, creepage/clearance for PCB design, stitching capacitance for EMI compliance, and isolated power.

## Quick Reference

- **For digital isolation, ISO6441 supports 150Mbps with CMOS inputs (maximum +/-10uA steady input current).** Its input current is not its supply current; aging is included in device specifications, not absent [2, pp.3, 7].
- **Check the exact package's certified creepage.** Skyworks AN583 lists 7.6mm for its standard WB SOIC-16 despite an 8mm nominal dimension; coating is a qualified insulation measure, not automatic extra spacing [7, pp.4, 8].
- **Check the PCB laminate CTI separately from the IC mold compound.** At 400V working voltage, PD2 reinforced insulation needs 4mm for Group I or 8mm for Group IIIa in the cited standards example [4, pp.7, 9-10].
- **Stitching capacitance is an EMI measure, not a universal value.** ADI's four-channel ADuM1402 board at 5V/1Mbps exceeded CISPR 22 Class B by 4dB; 150pF added enough reduction in that test [5, pp.10-11].
- **Vishay AN02's 10-year, -20 to +60 degrees C example budgets 20% CTR aging, not 50%.** Combined temperature, aging, and manufacturing factors reduce 100% typical CTR to 49.8% [9, p.1].

## Design Rules

### Digital Isolators vs Optocouplers

- **Digital isolator families:** ISO6441's 150Mbps supported rate is a device specification; SLLA526's 47.6Mbps for ISO6741 is an asynchronous timing estimate at 5V, not its rated maximum. ISO78xx is the 5.7kVRMS family; ISO77xx is listed at 5kVRMS, with package-specific safety ratings [2, pp.3-4; 1, §1, Table 1-2].
- **Integrated isolated functions:** ISOW77xx (digital isolation + DC-DC), ISO14xx/ISO1500 (isolated RS-485). ISO14xx: 5kVRMS transient isolation; Profibus signaling assumes 5V bus-side supply. The reference design reports 30kV HBM ESD, 16kV IEC ESD, and 4kV EFT; check the exact variant's test conditions [1, Table 1-2; 3, pp.1-2].
- **Isolated SPI for BMS daisy-chain:** ADI LTC6820 isoSPI -- bidirectional SPI over a single twisted pair through pulse transformers, up to 1Mbps, 2uA typical idle. Its 100m cable example requires the specified transformer, termination, drive current, and timing budget; 100m and 1Mbps are not independent guarantees [6, pp.1, 18-22].
- **Optocoupler use cases:** analog proportional output (linear optocouplers for feedback loops), specific certification mandates requiring optocouplers, legacy drop-in where board is already qualified.

### Creepage & Clearance

- **Use each insulation surface's documented material group.** Group I requires CTI >= 600V; Group IIIa is 175V <= CTI < 400V. FR4 and IC packages are not universally Group IIIa and Group I respectively; TI's 400VDC example assumes those groups and PD2 [4, pp.3, 9-10].
- **WB SOIC-16: count exposed lead-frame tabs in the shortest creepage path.** Skyworks AN583 gives 7.6mm for its standard package and describes covering the tabs with conformal coating to achieve the nominal 8mm path. Verify the exact package certification and the end standard's coating requirements; this is not a universal limit for all wide-body packages [7, pp.4-5, 8].
- **For the following IEC 60950-1 creepage table, reinforced insulation doubles the basic values.** This multiplier does not determine clearance or solid-insulation qualification [7, p.4].

**Creepage example: IEC 60950-1 MAINS table reproduced in AN583, PD2, basic insulation; working voltage is RMS AC or DC across the insulation [7, p.4]. For another end standard, use its own table.**

| Working V (RMS AC or DC) | Group I | Group IIIa/IIIb |
|------------------|---------|------------------|
| 100 | 0.7 mm | 1.4 mm |
| 150 | 0.8 mm | 1.6 mm |
| 250 | 1.3 mm | 2.5 mm |
| 400 | 2.0 mm | 4.0 mm |

- **Clearance example: IEC 62368-1 Table 10, PD2, overvoltage category II, <=2000m.** TI's telecom AC/DC example uses up to 265VAC line-to-neutral -> 2.5kV rated impulse -> 3.6mm reinforced clearance. Material group does not set this air-gap distance; creepage separately uses the 400VDC maximum working voltage [4, pp.9-10].
- **Altitude correction:** above 2000m, multiply clearance by the applicable altitude factor; IEC 60664-1 Table A.2 gives 1.48 at 5000m in TI's example. Required clearance is 3.6mm * 1.48 = 5.328mm -> round up to at least 5.33mm [4, p.10].
- **PCB grooves increase creepage without increasing clearance.** Measure the shortest surface path around the actual groove/slot; do not add a universal width-plus-two-depth correction. TI's IEC 60664-1 summary gives minimum slot widths of 0.25mm (PD1), 1.0mm (PD2), and 1.5mm (PD3) before the slot is credited [4, p.11, Table 7].
- **Inner layers are solid insulation, not surface creepage.** AN-1109's IEC 60950 discussion gives 0.4mm minimum through insulation or along a bonded surface for reinforced insulation in most cases, plus applicable construction/type-test requirements. Dielectric strength multiplied by thickness and the number of cemented joints alone do not certify reinforced insulation [5, p.10].
- **Do not substitute a generic hi-pot test for safety spacing.** TI gives 2 * working voltage + 1000V only as a general functional-isolation production-test example (265VAC -> 1530V), not a reinforced-insulation qualification or permission to round the test down to 1.5kV [4, pp.10-11].

### PCB Layout for Isolation Barrier

- **Keep primary and secondary conductors separated on every layer.** Surface keep-outs enforce creepage/clearance; intentional internal stitching structures require separately qualified solid insulation and via clearances [5, pp.10, 15-20].
- **AN-1109's plane-overlap EMI methods use a four-layer minimum stack-up.** Two-layer boards can use a discrete safety stitching capacitor; they are not categorically unsuitable for isolation [5, p.6].

**Stitching capacitance (primary EMI fix):**
- **Discrete safety stitching cap:** AN-1109's examples are effective up to about 200MHz; above that, pad/trace inductance limits the bypass. Its Y2 examples suit the insulation requirements assumed there; choose the safety class and ratings required by the actual barrier [5, p.6].
- **Overlapping ground planes:** extend primary/secondary reference planes into the gap on internal layers only when the dielectric construction qualifies. AN-1109's single-joint structure suits basic insulation and has lower inductance than discrete capacitors [5, pp.6-7].
- **Floating metal plane:** AN-1109's structure provides two cemented joints and two sequential dielectric paths, useful for reinforced insulation under some standards; it does not automatically qualify. Two equal coupling capacitors in series halve each capacitor's value [5, pp.7, 10].
- **Medical:** AN-1109 notes some applications allow only 10-20pF total isolation capacitance between isolated ground and earth. Derive the actual capacitance budget from the required leakage-current tests; a Y1 label alone does not establish compliance [5, pp.6, 14].

**Stitching results from ADI AN-1109 (four active ADuM1402 channels, four-layer test boards); measurements apply to those layouts [5, pp.10-11]:**

| Condition | CISPR 22 Class A | CISPR 22 Class B |
|-----------|-----------------|-----------------|
| No stitching, 5V, 1 Mbps | Pass by ~6 dB | FAIL by 4 dB |
| 150pF stitching, 5V, 1 Mbps | Pass | Pass |
| 300pF stitching, 5V, 1 Mbps | Pass by wide margin | Pass by wide margin |
| No stitching, 3.3V, 1 Mbps | Pass | Pass |
| No stitching, 5V, 10 Mbps | FAIL | FAIL by 24dB / 20dB in the two bands |
| 400pF stitching, 5V, 10 Mbps | Pass | Source extrapolates an extra 100pF beyond the 300pF measurements |

- **3.3V vs 5V:** the standard four-layer ADuM1402 test board passed CISPR 22 Class B at four channels * 1Mbps with 3.3V supplies and no stitching. At 10Mbps, the unmodified 3.3V board still needed 15-16dB reduction [5, pp.10-11].
- **Interplane capacitance:** ADI's 0.1mm GND-to-VDD spacing gave 0.03V p-p measured VDD noise on the four-layer board versus 0.17V p-p on the two-layer board. This is same-side bypassing, distinct from barrier stitching [5, pp.8-9].
- **Edge guard via fence:** ADI used 4mm via spacing and measured about 1-2dB additional emissions reduction with guard structures. These are board-specific EMI results, not insulation spacings [5, pp.8, 11-12].

- ESD on isolated interfaces -> `protection/esd.md`. Ground planes, stackup -> `guides/pcb-layout.md`. Isolated CAN -> `interfaces/can.md`.

### Isolated Power

- **SN6505B push-pull transformer driver:** up to 5W, external center-tapped transformer, secondary full-wave rectified with Schottky + LDO. SN6501: up to 1.5W in the reference design [3, p.2].
- **Integrated:** TI ISOW77xx -- digital isolation + DC-DC in single 16-SOIC. Limited power budget per variant [1, Table 1-2].

### Optocoupler Design

- **CTR derating for Vishay AN02's example:** CNY17x/SFH61xA/TCET110x/K817P phototransistor families, -20 to +60 degrees C, 10-year service assumption. The factors in Formulas are that example's budget, not a universal 50% aging loss [9, p.1].
- **Emitter config (Vishay's TTL example, >=100kbit/s):** VCC=5V, RL=390 ohm, assumed CTR_min=50%, IF about 12.3mA targets a 2.4V high with TTL high-state input current neglected; 390 ohm also keeps the low below 0.8V for 1.6mA TTL input current. This is not a guaranteed 0.4-2.4V output swing [9, pp.1-2].
- **Collector config (slower, up to 28 kbit/s):** output from collector with pull-up. Transistor saturates -> slow VCEsat recovery. Derate CTR further to 25% for saturation (VCEsat < 0.5V at IC < 5mA, CTR halved vs emitter config). RL=5.1K in Vishay's TTL example [9, p.2].
- **Reducing IF from 10mA to 5mA quadruples projected life only under Broadcom's N=2 model at unchanged temperature and duty cycle.** Use AF = (I_stress/I_use)^2 * exp[(Ea/k) * (1/T_use - 1/T_stress)], with Ea=0.43eV, k=8.62e-5 eV/K, and temperatures in kelvin; its 20mA/125 degrees C stress to 5mA/60 degrees C use example gives AF about 185, not a guarantee for every optocoupler [8, p.2].

## Common Mistakes

- **Treating coating as an automatic creepage extension.** AN583's lead-frame-tab treatment still requires the applicable supplementary-insulation requirements; validate the coating/process instead of treating nominal package dimensions as certified spacing [7, pp.4, 8].
- **Traces or vias crossing barrier on inner layers.** Gap looks clean on surface but is shorted internally. Define layer-specific keep-outs, including clearance around vias in intentional overlap structures [5, pp.19-20].
- **X-rated capacitor substituted across a safety barrier.** AN-1109 calls for safety capacitors rated for shock-protection applications; an X-only rating does not establish the required barrier insulation [5, p.6].

## Formulas

**Optocoupler CTR derating:**
**Rule of thumb:** Vishay AN02 budgets approximately 50% of typical CTR for its -20 to +60 degrees C, 10-year example [9, p.1].
**Formula:** CTR_min = CTR_typ * 0.83 (temp) * 0.80 (aging) * 0.75 (mfg tolerance)
**Example:** CTR_typ=100% at IF=10mA -> CTR_min = 100 * 0.83 * 0.80 * 0.75 = 49.8% -> design for ~50% for that example [9, p.1].

## Sources

### Related Rules

- `protection/esd.md` -- ESD protection on isolated interfaces
- `guides/pcb-layout.md` -- Ground planes, stackup, and return current management
- `interfaces/can.md` -- Isolated CAN bus design
- `power/switching.md` -- Flyback topology for isolated power

### References

1. TI SLLA284G (September 2023) -- Digital Isolator Design Guide: https://www.ti.com/document-viewer/lit/html/SLLA284
2. TI SLLA526D (November 2025) -- Improve Your System Performance by Replacing Optocouplers with Digital Isolators: https://www.ti.com/document-viewer/lit/html/SLLA526
3. TI SLLA453A (September 2022) -- Isolated RS-485 Transceiver Reference Design: https://www.ti.com/document-viewer/lit/html/SLLA453
4. TI SLUP419 (March 2024; summarizes IEC 60664-1:2020 and IEC 62368-1:2023) -- Demystifying Clearance and Creepage Distance: https://www.ti.com/document-viewer/lit/html/SLUP419
5. ADI AN-1109 (Rev 0, April 2011) -- Recommendations for Control of Radiated Emissions with iCoupler Devices: https://www.analog.com/en/resources/app-notes/an-1109.html
6. ADI LTC6820 Datasheet (Rev C, May 2019) -- isoSPI Isolated Communications Interface: https://www.analog.com/media/en/technical-documentation/data-sheets/LTC6820.pdf
7. Skyworks AN583 (Rev 0.3, December 2021) -- Safety Considerations and Layout Recommendations for Digital Isolators: https://www.skyworksinc.com/-/media/SkyWorks/SL/documents/public/application-notes/AN583.pdf
8. Broadcom AV02-3401EN (December 2022) -- Calculate Reliable LED Lifetime Performance in Optocouplers: https://docs.broadcom.com/doc/AV02-3401EN
9. Vishay AN02 (Rev 1.4, November 2011) -- Optocoupler Application Examples (CTR Derating and Interface Circuits): https://www.vishay.com/docs/83741/83741.pdf
