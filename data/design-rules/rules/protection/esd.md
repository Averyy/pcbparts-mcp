# ESD & Surge Protection

> TVS selection, clamping voltage analysis, and PCB placement for system-level ESD (IEC 61000-4-2).

## Quick Reference

- **V_RWM >= 1.2 * max signal voltage.** Leakage rises exponentially near V_RWM -- bidirectional only if signal swings negative.
- **V_CLAMP at IC = V_BR + R_DYN * I_SURGE + L_GND * dI/dt.** Must stay below IC absolute max at worst-case temperature.
- **Ground inductance dominates: 1nH adds ~30V at IEC Level 4 (30 A/ns).** 4+ vias on TVS ground pad.
- **Route connector -> TVS -> IC in series.** T-junction stubs bypass TVS entirely.
- **Capacitance budget:** USB 2.0 <= 1.5pF, USB 3.2 Gen 1 < 0.5pF, USB 3.2 Gen 2 < 0.3pF, HDMI 2.1/DP 2.0 <= 0.15pF.

## Design Rules

### TVS Selection

- **Unidirectional for always-positive signals** (VBUS, GPIO). Bidirectional for signals that swing negative (audio, RS-485, CAN, differential AC-coupled). Bidirectional has ~2x capacitance and worse negative clamping.
- **V_RWM is the selection parameter, not V_BR.** V_BR is breakdown at 1mA -- leakage increases exponentially between V_RWM and V_BR. Select V_RWM >= max signal voltage including tolerances.
- **Flat-clamp TVS when IC abs max is tight.** R_DYN as low as 60 mohm vs 500-900 mohm for standard Zener. At 24A surge: TVS3300 clamps to 39.4V vs SMAJ33A at 59.2V -- 20V difference that determines whether a 60V-rated IC survives.
- **Multi-channel arrays for differential pairs** (USB, HDMI): 0.2pF mismatch between D+/D- converts CM ESD into DM noise. Use arrays with < 0.05pF channel mismatch.
- **Analog signal distortion near V_RWM.** Leakage clips waveforms even without ESD event. Measurable above ~80% of V_RWM. Use V_RWM >= 1.5x peak signal for analog interfaces.

> WARNING: Never use snap-back TVS on DC supply lines. The supply sustains current above I_hold -> TVS latches permanently and is destroyed by EOS. Standard Zener TVS has negligible latch-up risk on DC rails.

**Capacitance limits by interface:**

| Interface | Max TVS Capacitance |
|-----------|-------------------|
| CAN 2.0 / RS-485 | < 15pF |
| CAN FD (> 2 Mbps) | < 12pF |
| USB 2.0 | <= 1.5pF |
| USB 3.2 Gen 1 (5 Gbps) | < 0.5pF |
| USB 3.2 Gen 2 (10 Gbps) | < 0.3pF |
| USB 3.2 Gen 2x2 (20 Gbps) | < 0.15pF |
| HDMI 2.1 / DP 2.0 | <= 0.15pF |
| LVDS / MIPI D-PHY | < 0.5pF |
| PCIe Gen 4+ | < 0.25pF |

### Part Recommendations

- **USB 2.0 D+/D-:** TPD2E2U06 (TI, dual, 1.5pF, SOT-23-3) or ESD122 (TI, dual, 0.2pF, DFN1006-3) for tighter budget. General purpose USB/UART: USBLC6-2SC6 (ST, dual, 1.2pF, SOT-23-6).
- **USB 3.2 Gen 1 TX/RX:** TPD4E02B04 (TI, 4-ch, 0.25pF, USON 2.5x1.0). Covers up to 10 Gbps per lane.
- **USB 3.2 Gen 2x2 / 20 Gbps:** TPD1E01B04 (TI, 1-ch, 0.18pF, DFN0603). Use 8x for full Type-C TX/RX.
- **General GPIO/signal:** ESD321 (TI, 1-ch, 0.9pF, DFN1006) for 3.6V lines. ESD441 (TI, 1-ch, 1pF, DFN0603) for 5.5V lines (CC, VBUS, SBU).
- **CAN:** ESD2CANFD24-Q1 (TI, 2-ch, 2.5pF, SOT-23). Standard ESD2CAN24-Q1 is 3pF -- check if CAN FD > 2 Mbps needs lower.
- **HDMI TMDS:** TPD4E05U06 (TI, 4-ch, 0.4pF, USON 2.5x1.0) -- two devices cover 8 TMDS lines plus clock.
- **USB-PD VBUS surge (5-48V):** TVS0500 (5V/9V clamp), TVS1400 (9V/18V), TVS2200 (20V/28V), TVS3300 (33V/38V). Flat-clamp family, 2x2mm DRV package.
- **Ethernet:** ESD protection goes on the line side (before magnetics). Magnetics provide ~1500V isolation. ESDS304 (TI, 4-ch, 2.3pF, SOT-23) for 10/100/1000BASE.

### Clamping Voltage Analysis

- **Datasheet V_CLAMP assumes zero PCB parasitics at 25C.** Real clamping adds L_GND * dI/dt and temperature shift. Always calculate total V at IC.
- **Temperature derating:** V_BR tempco ~1e-3/C. At 85C: V_CLAMP rises ~6%. SMAJ33A at 25C: 59.8V -> 63.4V at 85C. I_PP derates ~50% at 85C, ~80% at 125C.
- **Package size determines R_DYN.** SMAJ (SMA) R_DYN ~884 mohm. SMBJ (SMB) ~504 mohm. Flat-clamp (DRV 2x2mm) ~60 mohm. Larger package = lower clamping at same surge current.
- **Low-voltage TVS leakage.** 3.3V/3.6V TVS can reach 1uA at V_RWM -- check against battery/sleep current budget.

**Worked example -- 24V industrial input, 33V V_RWM, IEC 61000-4-5 at 24A:**

| Device | R_DYN | V_CLAMP at 24A | Verdict |
|--------|-------|----------------|---------|
| SMAJ33A | 884 mohm | 59.2V | At 85C: 63.4V. Exceeds 60V abs max -- fails. |
| SMBJ33A | 504 mohm | 50.1V | At 85C: 54.2V. 60V IC survives with margin. |
| TVS3300 | 60 mohm | 39.4V | Excellent. 32A rated at 85C, 4000 strikes at 125C. |

### PCB Layout

- **Route connector -> TVS -> IC in series.** Never T-junction: a stub to TVS off the main trace adds inductance and lets current bypass TVS entirely.
- **Ground inductance is the dominant failure mode.** At IEC Level 4 (30A, 0.8ns rise): 1nH adds ~30V. ST AN5686 measured: L_GND +600pH -> 72V peak, +1nH -> 89V, +5nH -> 238V. Design the ground path, not just the signal path.
- **4+ vias on TVS ground pad.** Each via ~0.5nH; 4 in parallel ~0.125nH. Largest drill feasible. Plated-over vias with non-conductive fill preferred (preserves inner surface area for skin-effect current).
- **No vias between connector and TVS** -- keep ESD path on same layer. Vias between TVS and IC are acceptable (added inductance steers current toward TVS).
- **Keep-out zone around ESD path.** High dI/dt between connector and TVS radiates EMI into adjacent unprotected traces. No unprotected signals adjacent to this region on any layer.
- **45-degree corners maximum** between connector and TVS. 90-degree corner at 8kV produces E-field > 7kV -- strong EMI source. Curved traces preferred.
- **TVS ground connects to same-layer ground plane** with nearby stitching vias to adjacent internal ground plane. Chassis screw ground near TVS + connector ground further reduces impedance.

### Snap-Back Latch-Up

- **DC supplies: never use snap-back TVS.** Supply easily provides hold current -> permanent latch-up -> EOS destruction.
- **USB 2.0 HS is inherently safe:** 500mV signal, 45 ohm termination. Max current through snap-back device is ~11mA -- far below any hold current.
- **USB 2.0 FS/LS: calculate.** I_max = (3.6V - V_snapback) / R_series. For FS with 28 ohm: (3.6 - 2.0) / 28 = 57mA. If TVS I_hold > 57mA, safe.
- **USB 3.x RX lines with AC coupling caps: latch-up impossible.** No DC path to sustain hold current. Place TVS at connector side of coupling caps.
- **HDMI TMDS:** V_bias_max = 3.63V, R_min = 45 ohm. I_latch_max = (3.63 - V_snapback) / 45. Active pull-up circuits in HDMI receivers detect shorts and remove bias -> releases latch. No known field failures.
- **High-frequency signals (> 5 MHz) need higher hold current** than DC I-V curves suggest. Pulsed hold current at 5 MHz was ~158mA vs DC hold current of ~22mA in Nexperia testing. This relaxes latch-up risk for high-speed data.

### SEED Co-Design

- **Z-R-Z structure:** series resistor between external TVS and IC shifts the external TVS I-V slope as seen at the IC. Delays IC internal protection triggering so both share surge current optimally.
- **Optimal co-design:** both internal and external protection reach failure at the same voltage. System ESD robustness = sum of both protections' robustness.
- **Without TLP curves in IC datasheet:** iterate series resistor experimentally (typically a few ohms) until system ESD robustness peaks. Resistor value must not degrade eye diagram.

- USB D+/D- routing, CC resistors -> `interfaces/usb.md`. CAN physical layer -> `interfaces/can.md`. ESD on isolated interfaces -> `protection/isolation.md`.

## Common Mistakes

- **Datasheet V_CLAMP used without ground inductance or temperature.** SMAJ33A: 59.8V datasheet + 30V from 1nH ground path + 6% at 85C = 95V+ at IC. Always calculate V_CLAMP(T) + L_GND * dI/dt.
- **Pass-through TVS package placed backwards.** TI pass-through packages (DFN, SOT-5X3) route signal through device. Reversed orientation breaks signal path or protects the wrong side. Verify pin 1 against footprint.
- **TVS on stub instead of in-line.** Stub inductance L2 means ESD current splits between TVS and IC. V at IC = V_CLAMP + L2 * dI/dt. Even 0.25nH adds 10V at Level 4.
- **90-degree corners on ESD traces.** E-field concentration at corner > 7kV at 8kV strike. Causes arcing for trace gaps < 2.6mm and radiates EMI into nearby traces.
- **Bidirectional TVS on always-positive DC rail.** Wastes 20-30% clamping headroom vs unidirectional. Negative clamping through V_F (~0.7V) on unidirectional is superior.
- **TVS capacitance destroys differential impedance.** 1pF TVS on 90-ohm USB 3.x pair degrades return loss. Verify S-parameter impact at target data rate.

## Formulas

**Clamping voltage at IC:**
**Rule of thumb:** V_CLAMP is 1.5-2x V_RWM for standard TVS at rated surge current.
**Formula:** V_IC = V_BR + R_DYN * I_SURGE + L_GND * dI/dt
**Example:** SMBJ33A, V_BR=38V, R_DYN=504 mohm, I_SURGE=24A, L_GND=1nH, dI/dt=30 A/ns -> V_IC = 38 + 12.1 + 30 = 80.1V

**Temperature-derated clamping:**
**Rule of thumb:** V_CLAMP rises ~6% from 25C to 85C for standard Zener TVS.
**Formula:** V_CLAMP(T) = V_CLAMP(25C) * (1 + 1e-3 * (TJ - 25))
**Example:** SMAJ33A at 25C: 59.8V. At 85C: 59.8 * 1.06 = 63.4V.

**Snap-back latch-up check:**
**Rule of thumb:** If V_driver < V_snapback, latch-up is impossible.
**Formula:** I_max = (V_driver - V_snapback) / R_series
**Example:** USB 2.0 FS, V_driver=3.6V, V_snapback=2.0V, R_series=28 ohm -> I_max=57mA. Safe if TVS I_hold > 57mA.

## Sources

### Related Rules

- `interfaces/usb.md` -- USB D+/D- routing, CC resistors, ESD placement for USB connectors
- `interfaces/can.md` -- CAN physical layer protection and TVS placement
- `protection/isolation.md` -- ESD protection on isolated interfaces

### References

1. TI SSZB130 -- System-Level ESD Protection Guide: https://www.ti.com/lit/pdf/sszb130
2. ST AN5241 -- ESD Protection Fundamentals: https://www.st.com/resource/en/application_note/an5241-esd-protection-fundamentals-stmicroelectronics.pdf
3. TI SLVAE37 -- How to Select a Surge Diode: https://www.ti.com/lit/pdf/slvae37
4. ROHM 66AN046E -- Selection Method and Usage of TVS Diodes: https://fscdn.rohm.com/en/products/databook/applinote/discrete/diodes/selection_method_and_usage_of_tvs_diodes_an-e.pdf
5. TI SLVA680A -- ESD Protection Layout Guide: https://www.ti.com/lit/pdf/slva680
6. ST AN5686 -- PCB Layout Tips for ESD Protection: https://www.st.com/resource/en/application_note/an5686-pcb-layout-tips-to-maximize-esd-protection-efficiency-stmicroelectronics.pdf
7. TI SLVAF82B -- ESD/Surge Protection for USB Interfaces: https://www.ti.com/lit/pdf/slvaf82
8. Nexperia AN90038 -- ESD for High-Speed Without Latch-Up: https://assets.nexperia.com/documents/application-note/AN90038.pdf
