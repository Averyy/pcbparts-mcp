# Power Path Management

> Routing power from multiple sources (USB, battery, solar) to the system load -- source priority, ideal diodes, DPM/DPPM, and ship mode.

## Quick Reference

- **DPPM over DPM for unknown adapters.** DPM limits current but cannot detect adapter voltage collapse. DPPM monitors output voltage and reduces charge current before system crashes.
- **Ship mode leakage: bq25120A 2nA, TPS22915B 500nA.** 500nA on 100mAh = 19+ years shelf life.
- **Switchover voltage dip: V_dip = t_sw * (Iout / Cout).** 500mA with 22uF and 100us dead time = 2.3V dip -- resets a 3.3V system.
- **Back-to-back MOSFETs required for full reverse blocking.** Single MOSFET body diode conducts when channel is off.
- **Set solar IIN limit >= panel Isc.** Lower limit fights MPPT and prevents reaching true MPP.

## Design Rules

### Source Architecture

- **Direct connection: simplest but dead battery clamps system bus.** Only viable when system tolerates full battery voltage range (3.0-4.2V) and load < 2A average. If load exceeds precharge current (~10% of fast-charge), safety timer expires with no recovery.
- **Direct connection topology choice:** system load after sense resistor gives DPM (charge current adjusts with system load but termination affected by parasitic load). System load before sense resistor gives clean termination but no DPM -- total current limited only by IC peak protection.
- **Path selection (DPPM): system boots from adapter regardless of battery state.** Primary advantage over direct connection. bq2407x family: internal ~300mohm input FET + external battery FET (30-50mohm). Battery FET Rds_on sets supplement-mode voltage drop.
- **Diode-OR: LTC4412 (2.5-28V, 11uA Iq).** Each controller independently blocks reverse in < 500ns. 20mV forward drop via linear servo regulation -- eliminates oscillation and DC reverse leakage that comparator-based designs suffer from.
- **Prioritizer: LTC4417 (2.5-36V, 3 inputs).** 1.5% UV/OV accuracy. 256ms validation delay prevents false switching. Priority by pin assignment, not voltage level -- battery (14.8V) gets lower priority than wall adapter (12V).
- **If peak current > 2.5A:** use path selection topology. Direct connection triggers cycle-by-cycle current limit in bqSWITCHER ICs.

### Ideal Diode Design

- **MOSFET orientation is backwards from intuition.** Source connects to input side -- body diode anode at input allows initial current flow (~0.7V drop) until controller activates channel (~20mV). Drain-to-source body diode blocks reverse when channel is off.
- **N-channel above ~5A:** lower Rds_on but needs charge pump for gate drive. 10A through 5mohm: 50mV drop, 500mW (vs Schottky 5W at 0.5V Vf).
- **P-channel simpler, practical to ~5A.** No charge pump needed. Higher Rds_on at equivalent die size.
- **ADI linear servo: 15-20mV forward drop.** Servo amplifier regulates VDS to reference voltage as load changes. Comparator-based designs either allow DC reverse leakage or oscillate at light load.
- **Reverse current response: < 1us.** Detects VDS < -10mV and discharges gate in 0.5-1us.

### Power MUX and Switchover

- **Break-before-make: prevents reverse current, causes voltage dip.** Incoming FET carries inrush + load simultaneously during switchover -- size SOA for combined peak current.
- **Make-before-break (diode mode): minimal dip, brief reverse current.** Body diode of outgoing FET conducts during overlap. eFuse/ideal-diode controllers limit reverse current magnitude.
- **Integrated MUX: TPS2120 (2.8-22V, 3A).** Automatic priority with manual override. Controlled linear slew rate -- discrete RC gate delay cannot match.
- **Semi-integrated MUX: 2x TPS25942 eFuses** or 2x TPS2660. Provide controlled slew, OCP, thermal shutdown per input. TPS259470x for 2.7-23V, 5.5A.
- **Adapter hot-plug: cable inductance + input cap resonance -> >50% voltage overshoot.** Size input capacitance to limit pulse below converter max ratings. TVS on input for worst-case plug-in transient.

### DPM and DPPM

- **DPPM monitors output voltage, not input.** If Vsys drops below threshold, charge current reduces. At zero charge, battery enters supplement mode. Handles weak adapters and AC brownouts that DPM misses.
- **DPPM thresholds vary by IC and directly affect voltage-sensitive systems:** bq24072: VOUT = VBAT + 225mV, DPPM = VOUT - 100mV (smallest mode transition, ~225mV). bq24073/4: VOUT = 4.4V, DPPM = 4.3V. bq24075: VOUT = 5.5V, DPPM = 4.3V (up to 2V transition -- worst for voltage-sensitive loads).
- **VINDPM for unknown adapters: bq25120A default ~4.6V, programmable 4.2-4.9V via I2C.** Headroom: VIN >= VBAT + VDO + Rds_on * I_chg. Higher input FET Rds_on requires higher starting VIN.
- **Battery FET delay with missing battery: up to 10x longer switchover** when input drops within 125mV of expected battery voltage. Size holdover capacitance for battery-absent worst case: 100uF delivers 100mA for 100us with 100mV droop.
- **Termination disabled during DPM/DPPM.** Charger cannot distinguish "battery full" from "current reduced by path management." Safety timer runs at half speed (2x timer).
- **Battery-supplement mode: output drops below VBAT, battery FET turns on.** Battery supplements input current to system. Input FET limits to 100mA during output short; battery FET hiccup-checks every ~64ms.

### Solar and MPPT

- **FOCV: V_mpp = K * Voc.** K = 0.75-0.85 for crystalline silicon. Panel briefly disconnected to sample Voc.
- **Buck charger (panel > battery): BQ24650 (28V input, 10A).** MPPSET pin sets input regulation via resistor divider to 1.2V reference. Standalone, RC-settable.
- **Boost charger (panel < battery): BQ25504/05/70.** Handle down to ~100mV startup, 3-5V sustained. OCV sampled every 16 seconds with selectable 80% K-factor via VOC_SAMP divider.
- **Buck-boost (most flexible): BQ25798 (24V input, 5A, I2C).** Programmable K-factor adapts to temperature-induced Voc shifts without fixed divider. Best for variable-temperature environments.
- **LTC4015 dither MPPT:** dithers VIN_UVCL_SETTING ~1x/second. If charge current drops >= 1% in single step, reverses direction after 7ms. >= 25% change triggers full global search (normally every ~15 min, min interval 5 min).
- **LTC4015 low-power fallback:** below ~5% of full-scale, disable dithering but maintain active MPPT. Below ~1%, ADC noise makes dithering unreliable -- controller reverts to fixed 70% Voc. Below charger minimum operating current (5-20mA), battery may actually drain at ~10mA. Suspend charger and retry every ~60 seconds.

### Battery-Fed Topology (Solar)

- **Standard diode-OR: system load can collapse panel to battery voltage.** Both ideal diode controllers turn on, panel operates far below MPP.
- **Battery-fed topology (LTC4015): move system load after battery.** Charger output feeds battery, battery feeds load. LTC4015 maximizes total output power (battery + load current combined). Panel never collapsed by load.
- **Battery-fed trade-offs:** coulomb counter impaired (cannot distinguish battery vs load current). C/x termination triggers on combined current. System cannot boot until battery charges above minimum system voltage. Battery must supply full load during MPPT global search (charger briefly disabled). If load exceeds precharge current and battery is below precharge threshold, battery drains even with input present.
- **Use battery-fed when:** panel MPP voltage far from battery voltage, load transients large relative to panel current, or maximum energy harvest critical.

### Ship Mode

- **bq25120A: 2nA ship mode (monitors button + adapter only).** Entry via EN_SHIPMODE I2C command. Device waits until VIN disconnected before entering ship mode.
- **TPS22915B load switch: 500nA, 1.05-5.5V, 2A.** 0.76mm x 0.76mm CSP. PMOS passes battery to ON pin on button press; VOUT latches ON pin high via pullup. Same button exits ship mode and registers presses afterward.
- **/MR (master reset) wakeup on bq25120A:** internally pulled to VBAT with deglitch -- no external cap needed. TVS if user-exposed. N-channel level shifter if /MR at VBAT (4.2V) but MCU GPIO is 1.8V/3.3V.
- **Production line gotcha: adapter bounce on jig removal wakes device.** Fix: set EN_SHIPMODE while VIN present, raise /CD after adapter removal to complete ship mode entry.
- **Power on/off button:** configure MRREC register on bq25120A for hold duration. Same button wakes (short press) and powers down (long hold). Single I2C register write to re-enter ship mode from low-battery wake.

## Common Mistakes

- **Battery never reaches full charge under sustained load.** DPPM continuously reduces charge current, never hitting termination threshold. Safety timer runs at half speed. Charger cycles between charging and terminating indefinitely in direct-connection topology when system load causes voltage to dip below recharge threshold.
- **Ship mode entered with adapter still connected -- device never sleeps.** bq25120A waits for VIN removal before completing ship mode entry. If EN_SHIPMODE is sent via I2C but the USB cable stays plugged in, device remains active at full quiescent current. On the production line, test jig removal bounce can also wake the device immediately after ship mode is set. Fix: send EN_SHIPMODE, physically remove adapter, then raise /CD to confirm entry. Verify ship mode current with ammeter before boxing units.
- **Ideal diode oscillates at light load due to comparator hysteresis.** Discrete ideal diode circuits using a comparator (LM393) to sense VDS have ~5mV hysteresis. At loads below 50mA through a 10mohm FET, VDS is only 0.5mV -- well below the comparator threshold. The FET toggles on/off at the comparator's response speed (10-50kHz), creating conducted EMI and audible noise. Fix: use a linear servo controller (LTC4412) that regulates VDS to a fixed ~20mV, or add 100mV of intentional hysteresis and accept the higher dropout.
- **Single MOSFET without back-to-back in path selection.** Body diode conducts reverse current when channel off, causing battery current ringing at power-up. Fix: back-to-back FETs or use soft-start cap (10nF on gate).
- **FOCV K-factor wrong for panel type or temperature.** Thin-film K = 0.70-0.80 (not 0.75-0.85). Temperature shifts Voc by ~-0.3%/C. Fix: I2C-programmable K (BQ25798) or dither MPPT (LTC4015).

## Formulas

**Switchover voltage dip:**
**Rule of thumb:** 100uF with 500mA dips ~250mV during 50us switchover.
**Formula:** V_dip = t_sw * (Iout / Cout)
**Example:** t_sw = 50us, Iout = 500mA, Cout = 100uF -> V_dip = 250mV

**Ship mode battery life:**
**Rule of thumb:** 500nA on 100mAh = 19+ years shelf life.
**Formula:** days = (capacity_mAh / leakage_mA) / 24 * 0.85
**Example:** 100mAh, 500nA -> (100 / 0.0005) / 24 * 0.85 = 7,083 days (19.4 years)

**Ideal diode power loss:**
**Rule of thumb:** 3A through 5mohm = 45mW vs Schottky 1.5W.
**Formula:** P = I_load^2 * Rds_on (vs Schottky: P = I_load * Vf)
**Example:** 3A, 5mohm -> 45mW. Schottky (Vf=0.5V) -> 1.5W.

**Break-before-make timing (discrete path selection):**
**Formula:** R1 * (C1 + Cgs_Q3) > Rsys * Csys_min
**Example:** Ensures battery FET Q3 turns off before input FET turns on at VIN removal.

## Sources

### Related Rules

- `power/battery.md` -- Battery charging, DPM/DPPM charger integration, fuel gauging
- `protection/reverse-polarity.md` -- Reverse polarity MOSFET selection for input protection
- `misc/mosfet-circuits.md` -- MOSFET selection fundamentals, gate drive for ideal diodes

### References

1. ADI -- PowerPath Controllers/Ideal Diodes Primer: https://www.analog.com/en/resources/technical-articles/primer-on-powerpath-controllers-ideal-diodes-prioritizers.html
2. TI SLUA400A -- Dynamic Power-Path Management and DPM: https://www.ti.com/lit/an/slua400a/slua400a.pdf
3. TI SLVAE51A -- Basics of Power MUX: https://www.ti.com/lit/an/slvae51a/slvae51a.pdf
4. TI SLYT333 -- Linear Li-Ion Charger with Power-Path Control: https://www.ti.com/lit/an/slyt333/slyt333.pdf
5. ADI -- LTC4015 MPPT for Solar Panels: https://www.analog.com/en/resources/technical-articles/multi-chemistry-battery-charger-supports-maximum-power-point-tracking.html
6. TI SLUAAP0 -- Solar Battery Charger Selection: https://www.ti.com/lit/an/sluaap0/sluaap0.pdf
7. TI SLUA376 -- Battery Charger Power-Path Management: https://www.ti.com/lit/an/slua376/slua376.pdf
8. ADI -- LTC4412 Ideal Diode Controller: https://www.analog.com/en/resources/technical-articles/ideal-diode-controller-eliminates-energy-wasting-diodes-in-power-or-ing-applications.html
9. TI SLVA821 -- Implementing Ship Mode Using TPS22915B Load Switch: https://www.ti.com/lit/an/slva821/slva821.pdf
10. TI SSZT534 -- How to Implement Ship Mode in Li-ion Battery Design: https://www.ti.com/lit/ta/sszt534/sszt534.pdf
