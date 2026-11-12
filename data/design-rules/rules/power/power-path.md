# Power Path Management

> Routing power from multiple sources (USB, battery, solar) to the system load -- source priority, ideal diodes, DPM/DPPM, and ship mode.

## Quick Reference

- **For unknown adapters, use VINDPM or DPPM.** Input-current limiting alone cannot detect voltage collapse; VINDPM monitors input voltage and DPPM monitors system voltage [2, pp.1-4].
- **Ship mode current: bq25120A 2nA typical, TPS22915B 500nA typical.** Include cell self-discharge and all other pack leakage in shelf-life estimates [8, 9].
- **Switchover voltage dip: V_dip = t_sw * (Iout / Cout).** With constant 500mA load, 22uF effective capacitance and 100us without source current, calculated dip is 2.27V before ESR effects [3, section 4.3].
- **Use back-to-back MOSFETs when disabled paths must block both directions.** A single correctly oriented ideal-diode FET blocks reverse current but still passes forward current through its body diode [1].
- **LTC4015 solar input-current limit >= panel maximum Isc.** This prevents input-current regulation from interfering with MPPT; it is not a universal charger setting [5, Input Current Limit Setting].

## Design Rules

### Source Architecture

- **Direct connection: dead battery clamps system bus.** For the bq2410x/11x/12x circuits in SLUA376, TI excludes average system loads above 2A and discourages peaks above 2.5A because of thermal and cycle-by-cycle limits. Below the precharge threshold, only about 10% of fast-charge current is available; system load can prevent recovery and expire the precharge timer [7, pp.3-5].
- **Direct connection topology choice (bq2410x/11x/12x):** system load after sense resistor gives DPM (charge current adjusts with system load but termination is affected by parasitic load). System load before sense resistor gives clean termination but no DPM -- total current is limited by IC peak-current and thermal protection [7, pp.4-9].
- **Path selection: system can boot from an adequate adapter with a depleted battery.** The bq2407x input and battery FETs are both internal; use its battery-supplement voltage-drop specifications rather than an assumed external FET resistance [11, pp.18-22].
- **Diode-OR: LTC4412 (2.5-28V battery supply, 11uA typical Iq).** Its linear servo targets 20mV typical forward drop while it has gate-drive headroom; at higher load the drop becomes I_load * Rds_on [10, pp.1, 3, 7].
- **Prioritizer: LTC4417 (2.5-36V, 3 inputs).** 1.5% UV/OV accuracy and 256ms input validation. Priority is by pin assignment, not voltage level -- a 14.8V battery can have lower priority than a 12V adapter [1, Prioritizers].

### Ideal Diode Design

- **Orient the body diode from input to output.** An N-channel ideal-diode FET has source at input and drain at output; the P-channel FET used by LTC4412 has drain at input and source at output. Reversing either permits body-diode backfeed even with the gate off [1, figure 2; 10, figure 1].
- **Above 5A, ADI recommends evaluating N-channel controllers.** They require a gate supply above the input (usually an internal charge pump). This is a topology recommendation, not a P-channel current rating [1, MOSFET Types and Configurations].
- **Check reverse turn-off with the actual gate load.** At 25 degrees C, LTC4412 specifies 13us typical, 22us maximum to reach VGS > -1.5V with 1nF gate capacitance and SENSE stepped from 11.8V to 12.2V at VIN = 12V; its reverse threshold is 20mV typical, 10-32mV [10, pp.3-4].

### Power MUX and Switchover

- **Break-before-make trades reverse-current isolation for output droop.** Incoming switch current includes both load and capacitor recharge current; check its current limit and SOA for the combined transient [3, sections 4.1-4.4].
- **Diode-mode overlap requires a reverse-blocking element on each path.** A diode blocks reverse current; an active controller admits a transient until it detects reversal and turns off its FET. Overlap alone does not limit reverse current [3, section 4.1].
- **Integrated MUX: TPS2120 (2.8-22V, adjustable 1-3A current limit).** Automatic priority with manual selection and controlled output slew [13, p.1].
- **Semi-integrated MUX: two TPS25942 eFuses or two TPS2660.** Follow the specific MUX interconnection for priority, reverse blocking and controlled slew; SLVAE51A also shows a two-TPS259470x implementation [3, figures 2-2, 3-4, 4-3].
- **Small input capacitors can permit hot-plug overshoot above 50% of adapter voltage.** Check cable/input-capacitor resonance against the converter's absolute maximum; capacitance is not selected from DC ripple alone [14, section V.A].

### DPM and DPPM

- **DPPM reduces charge current when Vsys drops below its threshold.** Once charge current is zero, a usable battery can supplement the input if the system drops below the battery-supplement threshold. With no usable battery, system load alone must remain within adapter capability [2, p.4].
- **DPPM thresholds vary by IC (nominal values):** bq24072: VOUT = VBAT + 225mV, DPPM = VOUT - 100mV. bq24073/4: VOUT = 4.4V, DPPM = 4.3V. bq24075: VOUT target = 5.5V, DPPM = 4.3V; below 5.5V input it passes the available input voltage. Further droop into supplement mode depends on VBAT and load, not a fixed 2V bound [11, p.6; 4].
- **bq25120A VINDPM: default 4.6V, programmable 4.2-4.9V via I2C.** Budget VIN >= VBAT + VDO(IN-PMID) + Rds_on(BAT-FET) * I_chg; the input-path dropout and battery-FET drop are separate terms [2, pp.6-7].
- **Battery-absent switchover needs hold-up capacitance.** SLUA400A's general discussion gives up to 10 times longer delay after the lost input reaches within 125mV of battery voltage; its hold-up example is 100uF supplying 100mA for 100us with 100mV droop. This is not a specified bq25120A or other MUX timing limit [2, p.5].
- **bq25120A disables termination during DPM/DPPM.** Its safety timer runs at half speed during VINDPM only if the 2X timer is enabled [2, pp.6-7].
- **bq2407x supplement current is unregulated until short-circuit protection acts.** Its current datasheet gives a 60ms typical short-circuit recovery interval; use the specified detection/deglitch thresholds, not a normal load-current limit [11, pp.12, 22].

### Solar and MPPT

- **FOCV: V_mpp = K * Voc.** TI gives K = 0.75-0.85 as typical under normal sunlight, not a guaranteed value for a panel technology. Sample unloaded Voc and select K for the panel [6, section 2].
- **Buck charger (panel > battery): BQ24650 (28V maximum input, up to 10A with external power stage).** MPPSET uses a resistor divider to a 1.2V reference; this fixes the input regulation voltage rather than periodically sampling Voc [6, section 2.1, table 3-1].
- **Boost energy harvester (panel < storage voltage): BQ25570.** Cold start requires 600mV typical (700mV maximum for 0 < TA < 85 degrees C, VBAT below undervoltage and VSTOR initially 0V); after cold start, input operation extends down to 100mV. Input maximum is 5.1V and must remain below storage voltage for boost operation; Voc is sampled every 16 seconds typical, with 80% selectable by tying VOC_SAMP to VSTOR or a divider for another fraction [12, pp.5-7, 13-15].
- **Buck-boost: BQ25798 (24V maximum input, 5A, I2C).** FOCV and an I2C-programmable K-factor allow the input target to follow sampled Voc as panel temperature changes [6, section 2.3, table 3-1].
- **LTC4015 dither MPPT:** dithers VIN_UVCL_SETTING approximately once per second. If charge current falls by >= 1% in one step, direction reverses after 7ms. A change greater than +/-25% triggers a global search (normally about every 15 minutes, limited to once per 5 minutes) [5, MPPT Special Considerations].
- **LTC4015 low-power fallback:** below about 5% of full-scale charge current, holds the global-search result without dithering; below about 1%, uses 70% of sampled Voc. With only about 5-20mA input available (application-dependent), charger operation can discharge the battery, generally by less than 10mA. If that loss matters, suspend charging below 1% of full-scale and retry periodically; ADI's example is every 60 seconds [5, Low Available Power; MPPT And Low Input Power].

### Battery-Fed Topology (Solar)

- **LTC4015 diode-OR: load exceeding panel capability collapses the panel to battery voltage.** The loss of harvested power depends on how far that voltage is from the panel's MPP [5, Potential Issues With Diode-OR Topology].
- **Battery-fed topology (LTC4015): connect the load at the battery side of the sense resistor as in ADI's figure 4.** The switching charger then controls all panel current and maximizes combined battery and load power [5, Battery Fed Topology].
- **Battery-fed trade-offs:** coulomb counter cannot distinguish battery from load current; C/x termination sees combined current; startup waits for battery voltage to exceed the system minimum. The battery must support the full load whenever MPPT or battery-series-resistance measurement disables the charger; below the precharge threshold, load exceeding precharge current drains the battery even with input present [5, Battery Fed Topology].

### Ship Mode

- **bq25120A ship-mode entry waits for VIN removal after EN_SHIPMODE.** It monitors /MR and adapter insertion while asleep [9].
- **TPS22915B load switch: 1.05-5.5V, 2A, 0.76mm * 0.76mm CSP.** In TI's circuit, a PMOS passes battery voltage to ON during the button press and VOUT latches ON high afterward. Level-shift the button signal if battery voltage exceeds the MCU GPIO rating [8, pp.2-3, 6].
- **/MR wakeup on bq25120A:** internally pulled to VBAT and deglitched -- no external debounce capacitor needed. Use an N-channel FET to emulate a press from a lower-voltage MCU; add TVS protection if the switch is user-exposed [9].
- **Power on/off button:** configure bq25120A MRREC and hold duration for long-press power-off; another press wakes it. A single I2C register write can return a low-battery wake to ship mode [9].

## Common Mistakes

- **Direct-connected system load causes repeated recharge cycles.** Load-induced battery IR drop can cross the recharge threshold immediately after termination; SLUA376 documents this for bq2410x/11x/12x topologies [7, p.5].
- **Production jig bounce wakes a device just put into ship mode.** For bq25120A, send EN_SHIPMODE with VIN present, remove the adapter, then raise /CD to complete entry after removal bounce [9].
- **Comparator-based ideal diodes oscillate at light load or permit DC reverse current.** Use a linear-servo controller such as LTC4412; adding arbitrary comparator hysteresis does not establish safe switchover behavior [1, The Ideal Diode in Actual Practice].
- **Removing Q2 from SLUA376's input path bypasses controlled turn-on.** Q1's forward body diode conducts immediately at power-up and produces battery-current ringing. Retain the back-to-back pair; the illustrated 10nF soft-start capacitor controls Q2 turn-on, not the diode path after Q2 is removed [7, pp.10-11].

## Formulas

**Switchover voltage dip:**
**Rule of thumb:** Use effective capacitance and worst-case switchover time; this model assumes constant load current and no source contribution during the gap [3, section 4.3].
**Formula:** V_dip = t_sw * (Iout / Cout); add capacitor ESR and other path drops separately.
**Example:** t_sw = 50us, Iout = 500mA, Cout = 100uF -> V_dip = 250mV

**Break-before-make timing (SLUA376 figure 13 only):**
**Formula:** R1 * (C1 + Cgs_Q3) > R_sys_light * Csys, where R_sys_light is the equivalent system resistance at the lightest load. This delays battery-FET Q3 turn-on at VIN removal while the system bus decays; it is not a general MUX timing equation [7, p.12].

## Sources

### Related Rules

- `power/battery.md` -- Battery charging, DPM/DPPM charger integration, fuel gauging
- `protection/reverse-polarity.md` -- Reverse polarity MOSFET selection for input protection
- `misc/mosfet-circuits.md` -- MOSFET selection fundamentals, gate drive for ideal diodes

### References

1. ADI -- PowerPath Controllers/Ideal Diodes Primer: https://www.analog.com/en/resources/technical-articles/primer-on-powerpath-controllers-ideal-diodes-prioritizers.html
2. TI SLUA400A (May 2018) -- Dynamic Power-Path Management and DPM: https://www.ti.com/lit/an/slua400a/slua400a.pdf
3. TI SLVAE51A (October 2020) -- Basics of Power MUX: https://www.ti.com/lit/an/slvae51a/slvae51a.pdf
4. TI SLYT333 -- Linear Li-Ion Charger with Power-Path Control: https://www.ti.com/lit/an/slyt333/slyt333.pdf
5. ADI -- LTC4015 MPPT for Solar Panels: https://www.analog.com/en/resources/technical-articles/multi-chemistry-battery-charger-supports-maximum-power-point-tracking.html
6. TI SLUAAP0 (June 2023) -- Solar Battery Charger Selection: https://www.ti.com/lit/an/sluaap0/sluaap0.pdf
7. TI SLUA376 (June 2006) -- Battery Charger Power-Path Management: https://www.ti.com/lit/an/slua376/slua376.pdf
8. TI SLVA821 -- Implementing Ship Mode Using TPS22915B Load Switch: https://www.ti.com/lit/an/slva821/slva821.pdf
9. TI SSZT534 -- How to Implement Ship Mode in Li-ion Battery Design: https://www.ti.com/lit/ta/sszt534/sszt534.pdf
10. ADI LTC4412 datasheet, Rev. B (4412fb) -- Low Loss PowerPath Controller: https://www.analog.com/media/en/technical-documentation/data-sheets/4412fb.pdf
11. TI BQ2407x datasheet, SLUS810N (October 2021): https://www.ti.com/lit/ds/symlink/bq24074.pdf
12. TI BQ25570 datasheet, SLUSBH2G (March 2019): https://www.ti.com/lit/ds/symlink/bq25570.pdf
13. TI TPS212x datasheet, SLVSEA3F (August 2020): https://www.ti.com/lit/ds/symlink/tps2120.pdf
14. TI SLYP089 -- Design Trade-offs for Switch-Mode Battery Chargers: https://www.ti.com/lit/ml/slyp089/slyp089.pdf
