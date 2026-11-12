# ESD & Surge Protection

> TVS selection, clamping voltage analysis, and PCB placement for system-level ESD (IEC 61000-4-2).

## Quick Reference

- **V_RWM >= max signal voltage including tolerances.** Check leakage at that voltage and operating temperature; no universal 20% margin [2, §2.1].
- **Include TVS-path and ground inductance in V_CLAMP at the IC.** Use clamping data for the applied waveform and current, including temperature limits; keep the resulting voltage below the protected circuit's rated tolerance [2, §2.4; 4, p.7].
- **Ground inductance dominates: 1nH adds ~30V at IEC Level 4 (30 A/ns typical).** Use multiple ground vias at the TVS [4, pp.3-4, 8-10].
- **Route connector -> TVS -> IC through the TVS pad.** A stub adds inductive overshoot at the IC [3, §2.1].
- **TI USB capacitance recommendations:** < 4pF for USB 2.0; < 0.5pF at 5Gbps/lane, < 0.3pF at 10Gbps/lane [5, pp.5, 7, 9].

## Design Rules

### TVS Selection

- **Unidirectional for always-positive signals** (VBUS, GPIO). Bidirectional for signals whose voltage relative to ground swings negative (audio, RS-485, CAN); differential signaling alone does not require bidirectional protection [2, §2.5].
- **V_RWM is the selection parameter, not V_BR.** V_BR is typically specified at 1mA, but use the device's stated test current; nominal voltage below V_BR does not assure low leakage [2, §2.2].
- **Flat-clamp TVS when IC abs max is tight.** TI's 24A, 8/20us example gives 59.8V nominal for SMAJ33A versus about 39V for TVS3300; the SMAJ estimate rises to 63.4V at 85 degrees C [2, §3.3].
- **Multi-channel arrays for differential pairs** (USB, HDMI): compare line-to-ground capacitance and channel matching at the same bias. USBLC6-2 specifies 0.015pF line-to-ground matching; its 1.2pF line-to-line capacitance is not its load to ground [8, p.2].
- **Analog signal loading:** use the leakage and capacitance specifications at the actual bias; low-voltage surge TVS leakage can exceed 1mA, invalidating a low-current budget [2, §2.6, §3.6].

> WARNING: A snap-back TVS on a DC rail latches if the supply load line sustains the on-state above the hold current. Select a hold voltage above the rail or prove the available current cannot sustain latch-up [6, §3].

### Part Recommendations

- **USB 2.0 D+/D-:** TPD2E2U06 (TI, dual, 1.5pF typical at 2.5V bias, 1MHz and 25 degrees C; SC70-3 DCK or 5-pin DRL) or ESD122 (TI, dual, 0.2pF, DFN1006-3). USBLC6-2SC6 (ST, dual, SOT23-6L) has 2.5pF typical / 3.5pF maximum line-to-ground capacitance at 1.65V bias and 25 degrees C [7, pp.1, 4; 5, p.5; 8, p.2].
- **USB 3.2 Gen 1 TX/RX:** TPD4E02B04 (TI, 4-ch, 0.25pF, USON 2.5mm * 1.0mm). Covers up to 10Gbps per lane [5, pp.7-10].
- **USB 3.2 Gen 2x2 / 20Gbps:** TPD1E01B04 (TI, 1-ch, 0.18pF, DFN0603 or DFN1006). Use eight for full Type-C TX/RX as in TI's example [5, pp.9, 12].
- **General GPIO/signal:** ESD321 (TI, 1-ch, 0.9pF, DFN1006 or SOD523) for 3.6V lines. ESD441 (1pF, DFN0603) for 5.5V lines; ESD341 (0.66pF) for 3.6V SBU. For CC/SBU short-to-VBUS tolerance, TI lists ESD752 (24V working voltage, not a 24V clamp); match the DC fault voltage as well as ESD clamping -> `interfaces/usb.md` [5, pp.3, 14, 17].
- **CAN:** ESD2CANFD24-Q1 (TI, 2-ch, 2.5pF typical, SOT-23); ESD2CAN24-Q1 is 3pF typical. Both are listed for CAN FD; capacitance alone does not impose a 2Mbps cutoff [9, §1-3, §5.7].
- **HDMI TMDS:** TPD4E05U06 (TI, 4-ch, 0.5pF, USON 2.5mm * 1.0mm); two devices cover the eight conductors of three data pairs plus one clock pair [5, p.3; 6, §5.2.1].
- **USB-PD VBUS surge:** TI lists TVS0500 for 5V VBUS (~9V clamp), TVS1400 for 9V (~18V), TVS2200 for 20V (~28V), and TVS3300 for 28V (~38V), in 2mm * 2mm DRV. These selections do not cover 48V VBUS; the figures are the application note's recommendations, not waveform-independent clamps [5, p.16].
- **Ethernet:** ESDS304 (TI, 4-ch, 2.3pF typical, SOT-23-5) supports 10/100/1000BASE; TI's application places it between the magnetics and PHY. Keep its ground on the PHY side; line-side protection requires an isolation-compatible topology [10, §3, §7.2].

### Clamping Voltage Analysis

- **Datasheet V_CLAMP is tied to a current, waveform, and temperature.** Do not extrapolate surge dynamic resistance to an ESD pulse; include PCB inductance separately [2, §2.4; 4, p.7].
- **Temperature derating is device-specific.** TI's SMAJ33A example uses a 0.001/degree C coefficient and a 50% pulse-power derating at 85 degrees C; use the selected manufacturer's curves, not those factors for every TVS [2, §3.3-3.4].
- **Compare R_DYN for the same waveform.** TI's 8/20us example uses 884 mohm (SMAJ33A), 504 mohm (SMBJ33A), and 60 mohm maximum (TVS3300); these are device examples, not package specifications [2, §3.3].

**TI example -- 24V industrial input allowing 33V DC, 24A 8/20us surge; estimates exclude PCB parasitics [2, §3.3-3.4]:**

| Device | V_CLAMP nominal | V_CLAMP at 85 degrees C | Limitation |
|--------|-----------------|-------------------------|------------|
| SMAJ33A | 59.8V | 63.4V estimated | Exceeds a 60V input rating; pulse-power budget also fails. |
| SMBJ33A | 51.1V | 54.2V estimated | Verify the selected vendor's waveform and temperature ratings. |
| TVS3300 | About 39V | Flat-clamp example | TI reports 32A capability at 85 degrees C and 4000 strikes at 30A, 125 degrees C. |

### PCB Layout

- **Route connector -> TVS -> IC through the TVS pad.** A stub adds TVS-path inductance, increasing the voltage at the IC [4, pp.7-9].
- **Ground inductance is the dominant failure mode.** For an 8kV contact discharge, ST uses 30 A/ns typical: 1nH adds ~30V. Its test board measured 56V peak with ~1nH baseline; adding 0.6nH, 1nH, and 5nH raised peaks to 72V, 89V, and 238V [4, pp.3-5].
- **Use multiple TVS ground vias; four is TI's illustrated layout, not a universal inductance guarantee.** TI recommends large pad/drill diameters and nonconductive-filled, plated-over ground vias; do not assume four mutually coupled vias give one-quarter the single-via inductance [3, §2.4].
- **No vias between connector and TVS** -- keep ESD path on same layer. Vias between TVS and IC are acceptable (added inductance steers current toward TVS) [3, §2.3].
- **Keep-out zone around ESD path.** High dI/dt between connector and TVS radiates EMI into adjacent unprotected traces. No unprotected signals adjacent to this region on any layer [3, §2.2].
- **45-degree corners maximum** between connector and TVS; curved traces preferred. TI's corner-field illustration does not establish a universal safe trace gap [3, §2.2].
- **TVS ground connects to same-layer ground plane** with nearby stitching vias to adjacent internal ground plane. Chassis screw ground near TVS + connector ground further reduces impedance [3, §2.4].

### Snap-Back Latch-Up

- **DC supplies: reject snap-back TVS when the supply can sustain its hold current below the operating voltage.** Check both hold voltage and current; otherwise the TVS stays conducting after the pulse [6, §3].
- **USB 2.0 HS:** Nexperia's worst-case high-state voltage is about 0.5V; snap-back voltage above 0.5V prevents sustained latch-up in HS mode. Check LS/FS operation separately [6, §5.1.1].
- **USB 2.0 FS/LS: calculate using the correct driver resistance.** Nexperia uses 28 ohm minimum for legacy LS/FS without USB 2.0 capability, but 40.5 ohm minimum for a USB 2.0-capable driver; see Formulas [6, §5.1.1].
- **USB 3.x:** connector-side protection outside the PHY coupling capacitors has no sustaining DC path in Nexperia's topology, absent a VBUS short. PHY-side TX protection requires a separate latch-up check [6, §5.1.2].
- **HDMI TMDS:** V_bias_max = 3.63V, R_min = 45 ohm. Require I_hold > (3.63V - V_snapback) / 45 ohm unless V_hold exceeds the bias; do not assume every receiver removes its pull-up during a short [6, §5.2.1].
- **Nexperia's pulsed hold-current result is conditional:** its 5MHz, 50% duty-cycle, 50-ohm test with ground-level low state required more hold current than DC. Do not apply this relaxation to a biased waveform or a different TVS without testing [6, §4].

### SEED Co-Design

- **Z-R-Z structure:** series resistor between external TVS and IC shifts the external TVS I-V slope as seen at the IC. Delays IC internal protection triggering so both share surge current optimally [1, §5.2].
- **Optimal co-design:** internal and external protection reaching failure at the same voltage gives a maximum shared current equal to the sum of their individual failure currents in the TLP model [1, §5.2].
- **Without TLP curves in IC datasheet:** iterate series resistor experimentally until system ESD robustness peaks. Resistor value must not degrade eye diagram [1, §5.2].

- USB D+/D- routing, CC resistors -> `interfaces/usb.md`. CAN physical layer -> `interfaces/can.md`. ESD on isolated interfaces -> `protection/isolation.md`.

## Common Mistakes

- **A room-temperature surge calculation misses the hot limit.** TI's SMAJ33A example rises from 59.8V to 63.4V at 85 degrees C before any PCB overshoot is added [2, §3.3].
- **TVS on stub instead of in-line.** Stub inductance adds to the TVS-ground path; at ST's typical 30 A/ns, 0.25nH adds 7.5V [3, §2.1; 4, pp.3-5].
- **Bidirectional TVS on an always-positive DC rail clamps negative pulses in avalanche.** A unidirectional TVS instead conducts forward for negative pulses; compare the specified negative clamps, not a fixed 0.7V forward-drop assumption [2, §2.5].
- **TVS capacitance alone does not qualify a high-speed link.** Verify the protected link's eye diagram and S-parameters at the target data rate [1, §3].

## Formulas

**Snap-back latch-up check [6, §5.1.1]:**
**Rule of thumb:** If the maximum driver voltage is below the TVS hold voltage, the DC load line cannot sustain latch-up; otherwise compare available current to I_hold.
**Formula:** I_max = (V_driver - V_snapback) / R_series
**Example:** Legacy USB LS/FS without USB 2.0 capability, V_driver=3.6V, V_snapback=2.0V, R_series=28 ohm -> I_max=57.1mA. Require TVS I_hold > 57.1mA.

## Sources

### Related Rules

- `interfaces/usb.md` -- USB D+/D- routing, CC resistors, ESD placement for USB connectors
- `interfaces/can.md` -- CAN physical layer protection and TVS placement
- `protection/isolation.md` -- ESD protection on isolated interfaces

### References

1. ST AN5241 (Rev 2, October 2023) -- ESD Protection Fundamentals: https://www.st.com/resource/en/application_note/an5241-esd-protection-fundamentals-stmicroelectronics.pdf
2. TI SLVAE37 (January 2019) -- How to Select a Surge Diode: https://www.ti.com/lit/pdf/slvae37
3. TI SLVA680A (April 2022) -- ESD Protection Layout Guide: https://www.ti.com/lit/pdf/slva680
4. ST AN5686 (Rev 1, July 2021) -- PCB Layout Tips for ESD Protection: https://www.st.com/resource/en/application_note/an5686-pcb-layout-tips-to-maximize-esd-protection-efficiency-stmicroelectronics.pdf
5. TI SLVAF82B (January 2024) -- ESD/Surge Protection for USB Interfaces: https://www.ti.com/lit/pdf/slvaf82
6. Nexperia AN90038 (Rev 3, July 2023) -- ESD for High-Speed Without Latch-Up: https://assets.nexperia.com/documents/application-note/AN90038.pdf
7. TI TPD2E2U06 datasheet (SLLSEG9C, December 2019): https://www.ti.com/lit/gpn/tpd2e2u06
8. ST USBLC6-2 datasheet (DS4260 Rev 7, December 2021): https://www.st.com/resource/en/datasheet/usblc6-2.pdf
9. TI ESD2CANxx24-Q1 datasheet (SLVSFW5): https://www.ti.com/lit/gpn/esd2canfd24-q1
10. TI ESDS30x datasheet (SLVSEG8B, January 2024): https://www.ti.com/lit/gpn/esds304
