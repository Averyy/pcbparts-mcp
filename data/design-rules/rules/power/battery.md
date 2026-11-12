# Battery Charging, Protection, and Monitoring

> CC/CV charging, NTC monitoring, protection ICs, charger IC selection, fuel gauge, and multi-cell BMS. Chemistry selection -> `power/battery-chemistry.md`. Power path, ship mode, DPM/DPPM -> `power/power-path.md`.

## Quick Reference

- **Set charge voltage, current and temperature limits from the exact cell specification.** Panasonic NCR18650BF specifies 0.5CA standard charge and 10-45 degrees C; a generic 0-45 degrees C window is insufficient for that cell [6, p.1].
- **MCP73831 has no charge safety timer or cell-temperature input.** Its thermal regulation monitors the IC, not the cell; add independent supervision or use a charger with those functions, such as MCP73841 [1, pp.10-12; 7, pp.1-2, 13-16].
- **Fortune DW01A fault thresholds: 4.30V +/-50mV overcharge, 2.40V +/-100mV overdischarge at 25 degrees C.** These are not charging targets or normal load cutoffs [8, pp.6-7].
- **Size overcurrent protection from both FET resistances.** DW01A senses 150mV typical, 120-180mV at 25 degrees C; an unspecified 8205A does not establish a fixed 3A trip [8, pp.7, 9].
- **Gauge accuracy figures are test results, not algorithm guarantees.** TI's room-temperature 4S2P robot-vacuum comparison measured about 20% peak error for voltage correlation, 6% for coulomb counting and 1% for Impedance Track in one test [4, section 7.2].

## Design Rules

### CC/CV Charging

- **Use current termination plus an independent elapsed-charge safety limit.** AN947 recommends 0.07-0.1C primary termination for its conventional 4.2V Li-ion discussion and an elapsed timer as secondary protection. Do not append an arbitrary 30-minute charge after the charger's termination signal [1, pp.5-7].
- **0.5C versus 1C is a cell-and-charger-specific trade-off.** In AN947's 1000mAh MCP73841 example, halving fast-charge current also halves termination current from 0.07C to 0.035C: charge time increases 36% and final capacity increases about 2%. This does not establish a universal cycle-life gain [1, pp.10, 13].
- **Chemistry-specific voltages must name the cell.** Lithium Werks ANR26650M1B recommends 3.6V with taper to 125mA; a 4.2V Li-ion charger is unsuitable. Do not treat 3.65V for all LFP or 2.85V for all LTO as safe defaults -> `power/battery-chemistry.md` [10, p.2].
- **Parasitic load distorts CV termination.** A load on the battery-current measurement path can keep measured current above the termination threshold; use a charger with a separate system power path or disconnect the load during charging -> `power/power-path.md` [1, p.7; 3, section IV.C].
- **Budget reverse leakage from its worst-case specification.** AN947 recommends below a few microamps, ideally below 1uA; MCP73831 specifies up to 2uA with VDD floating. Integrated reverse blocking does not imply zero battery drain [1, p.8; 7, pp.4, 18].

### NTC Temperature Monitoring

- **Use the thermistor's exact R/T curve and tolerance.** Vishay NTCLE203E3103FB0 is a 10kohm, 1% part with B25/85 = 3977K +/-0.75%; the 5% version widens thresholds in Vishay's BQ2005 NiMH example, not by a universal +/-5 degrees C [2, pp.2-4].
- **Beta is a part specification, not a package rule.** Vishay's listed NTCS0805E3103xMT, NTCS0603E3103xMT and NTCS0402E3103xLT families have B25/85 of 3570K, 3610K and 3490K respectively. Recalculate bias resistors when substituting the thermistor [2, p.4].
- **AN947's MCP73841 NTC network is a specific 0-45 degrees C example.** It uses a cell-mounted 10kohm/B3982 thermistor with 33.56kohm at 0 degrees C and 4.52kohm at 45 degrees C. Its 10.5kohm/15kohm bias pair is not transferable to another charger's thresholds [1, p.12; calculation below].

### Protection ICs

- **DW01A uses two external N-channel FETs for separate charge/discharge interruption.** Calculate its overcurrent threshold using the sum of their on-resistances at the actual gate voltage and temperature; the manufacturer's 3A example assumes 25mohm per FET [8, pp.5, 9].
- **Use the protector's voltage thresholds and delay specifications.** At VCC = 3.6V and 25 degrees C, DW01A short-circuit sensing is 1.35V typical with 50us maximum short-circuit delay; it is not a fixed 9A trip with a 10-30ms delay [8, p.7].
- **Si6926ADQ is TI's bq275xx reference-design FET example.** SLUA456 lists a dual 20V device, 4.1A and 33mohm at VGS = 3V. Those figures do not establish a drop-in current upgrade for every 8205A board; check package, pinout and thermal limits [5, pp.1-2].
- **FS312F-G has a higher cutoff than DW01A, but not 3.0V typical.** At 25 degrees C, Fortune specifies 2.90V +/-80mV overdischarge and 4.250V +/-25mV overcharge. Select both thresholds against the cell limits, including tolerance; do not substitute by marking alone [9, pp.4, 7].
- **Fault recovery is protector-specific.** DW01A overcharge releases below 4.10V typical, or with load attached once voltage falls below its overcharge threshold. Overdischarge recovery depends on charger detection and battery voltage; it is not universally charger-only recovery [8, pp.7-8].
- **SLUA456 uses two series 0.1uF ceramic capacitors across PACK+/PACK-.** Each capacitor must withstand the full pack voltage if the other shorts; short, wide connections reduce ESD-path inductance [5, pp.2-3].
- **Reverse cell polarity violates DW01A's VCC minimum of GND - 0.3V.** Add reverse-polarity protection rather than relying on the pack protector -> `protection/reverse-polarity.md` [8, p.6].

> WARNING: DW01A fault-delay circuits are not charge-duration timers. TP4056 and MCP73831 provide no elapsed-charge safety timer; use independent timing supervision or a charger with a timer, such as MCP73841 [1, p.12; 7, pp.13-16; 8, pp.7-9; 11, pp.1-3].

### Charger IC Selection

- **Linear charger selection depends on thermal dissipation, not a universal 1A boundary.** Check maximum input voltage, battery voltage at entry to fast charge, maximum regulated current and board thermal resistance [1, p.11; 7, section 6.1.1.3].
  - **TP4056:** the NanJing Top Power datasheet gives 1.2kohm for 1A and 10kohm for 130mA; C/10 termination follows CV taper. PROG monitors charging current, and CE disables charging when low. Thermal feedback reduces current when dissipation is excessive; no universal SOP-8 wattage limit is specified [11, pp.1-3].
  - **MCP73831:** 15-500mA programmable charge current, with voltage and termination variants selected by ordering code. The 4.20V option lists 4.168-4.232V at VDD = 5.2V, IOUT = 10mA and -5 to 55 degrees C; include line/load regulation outside that test condition. There is no safety timer or cell NTC input [7, pp.1-4, 13-16, 25].
  - **MCP73841:** external PMOS pass transistor and capacitor-programmed precharge/fast-charge/elapsed timers. AN947's 110mohm, 1% resistor gives 1A typical, 1.091A maximum; its PMOS dissipation calculates to 2.49W using the stated rounded inputs, not a package rating [1, pp.10-12].
- **Synchronous buck chargers need reverse-current control.** A low-side FET can discharge the battery to ground if inductor current reverses; a nonsynchronous freewheel diode removes that path, but does not block battery-to-input current through the high-side body diode [3, sections II.C, IV.B].
- **Bootstrap collapse is a near-dropout problem.** When adapter voltage is too close to battery voltage, an NMOS high-side bootstrap cannot sustain continuous 100% duty cycle. Use the charger's specified charge-pump or periodic-refresh behavior, or a PMOS high-side topology; CV taper alone does not force 100% duty cycle [3, sections II.C, IV.A].
- **Adapter hot-plug can exceed 50% overshoot with small input capacitors.** Check cable/input-capacitor resonance against the converter input limit; MCP73831 explicitly calls for input transient protection on hot-pluggable supplies [3, section V.A; 7, section 6.1.1.2].

### Fuel Gauge / State-of-Charge

- **Use SLUAAR3's error figures only for its measured load and pack.** The room-temperature 4S2P robot-vacuum tests do not establish universal error bounds for voltage correlation, coulomb counting, CEDV or Impedance Track [4, section 7.2].
- **MAX17048 is a battery-model gauge, not a simple rested-voltage lookup.** ModelGauge tracks load variation without a current-sense resistor or learning cycle; temperature compensation requires host input and the cell model must fit the chosen battery [12, pp.1, 8-10].
- **Impedance Track learning requirements depend on the gauge.** SLUAAR3 describes OCV updates below dV/dt = 4uV/s, >37% charge change for Qmax updates and >=90% for the first update. Use the chosen gauge's learning procedure rather than applying those thresholds to all bq27xxx parts [4, section 6].
- **SLUA456's bq275xx shunt example is 10mohm with <=100ppm/degrees C temperature coefficient.** Keep peak sense voltage within the selected gauge's range (the note gives 125mV); trade low-current offset against shunt dissipation and calibrate current gain [5, pp.2-3].
- **Kelvin-connect both cell-voltage sense leads and the current shunt.** SLUA456 also takes the low-current ground connection at the shunt; current-carrying copper must not become part of the measured resistance [5, pp.2-3].
- **Use the bq275xx reference differential low-pass filter at the sense inputs.** Its shunt capacitor suppresses mismatch-induced common-mode noise, so 5% filter components suffice in that circuit. Without filtering, the amplifier can rectify RF into a DC current offset [5, p.3].

### Multi-Cell / BMS

- **Monitor and protect each cell against its own voltage limit.** BQ76920 supports 3-5 series cells, per-cell OV/UV detection and host-controlled passive balancing; pack voltage alone cannot identify an overcharged cell [13, sections 1, 8.3.1.3, 8.3.1.4].
- **BQ76920 internal balancing is limited to 50mA per cell.** Select input resistors and balancing duty cycle accordingly; use its external-FET balancing topology for higher current. The host must not balance adjacent cells simultaneously and must respect package dissipation; series-cell count alone does not require active energy-transfer balancing [13, section 8.3.1.3.3].

## Common Mistakes

- **Compare system-load current with the charger's termination threshold.** The relevant comparison is load current against the actual termination setting: 20mA alone cannot hold a charger above a 70mA threshold. Separating system and battery-current paths prevents load current from being mistaken for battery current [1, p.7].
- **Extending precharge time to mask a fault.** Use the charger and cell qualification procedure; AN947's approximately one-hour precharge discussion is not a universal test that every cell must exceed 2.8V within an hour [1, pp.5, 12].
- **Assuming a 1% shunt guarantees 1% SoC accuracy.** Gauge gain calibration, offset, temperature drift and Kelvin routing also matter; resistor tolerance alone is not an SoC error floor [5, pp.2-3].
- **Connecting a 68ohm balance path directly across a 4.2V cell with BQ76920 internal balancing.** The ideal resistor current is 61.8mA and dissipation 259mW before internal-path drops, exceeding the IC's 50mA balancing capability. Use its resistor-selection procedure or external balancing FETs [13, section 8.3.1.3.3].
- **Using a generic cold-charge threshold instead of the cell specification.** A 0 degrees C cutoff still permits charging NCR18650BF below its specified 10 degrees C minimum; set the NTC network and worst-case tolerances for the selected cell [6, p.1].
- **Treating TP4056 PROG as valid only during CC.** The manufacturer's monitor relationship applies in all charging modes, including CV taper; charge current alone is not a battery state-of-charge measurement [11, p.2].

## Formulas

**MCP73841 NTC bias resistors (AN947's 0-45 degrees C example):**
**Rule of thumb:** 10.5kohm + 15kohm applies to the illustrated MCP73841 network and 10kohm/B3982 thermistor, not another charger or cell temperature window [1, p.12].
**Formula:** R_T1 = (2 * R_COLD * R_HOT) / (R_COLD - R_HOT); R_T2 = (2 * R_COLD * R_HOT) / (R_COLD - 3 * R_HOT)
**Example:** R_COLD = 33.56kohm, R_HOT = 4.52kohm -> R_T1 = 10.45kohm (use 10.5kohm), R_T2 = 15.17kohm (use 15kohm). AN947 reports the nominal window within 1 degree C of target; include component and comparator tolerances separately.

**MCP73841 external PMOS worst-case dissipation:**
**Formula:** P_Q1 = (VDD_max - (V_precharge_transition_min + V_sense_max)) * I_charge_max. With AN947's stated rounded inputs, (5.25V - (2.85V + 0.120V)) * 1.091A = 2.48748W (2.49W); the note prints 2.48W. Include the sense-resistor drop and maximum current rather than nominal 1A [1, p.11].

## Sources

### Related Rules

- `power/battery-chemistry.md` -- Chemistry selection and cell-specific voltage/current limits
- `power/power-path.md` -- DPM/DPPM topology, ship mode, parasitic load and CV termination
- `protection/reverse-polarity.md` -- Reverse battery connection protection

### References

1. Microchip AN947, DS00947A (2004) -- Power Management in Portable Applications: Charging Lithium-Ion/Lithium-Polymer Batteries: https://ww1.microchip.com/downloads/en/AppNotes/00947a.pdf
2. Vishay 29089 (revision 16-Sep-2014) -- Fast Charging Control with NTC Temperature Sensing: https://www.vishay.com/docs/29089/fastappl.pdf
3. TI SLYP089 -- Design Trade-offs for Switch-Mode Battery Chargers: https://www.ti.com/lit/ml/slyp089/slyp089.pdf
4. TI SLUAAR3 (December 2023) -- Battery Gauging Algorithm Comparison: https://www.ti.com/lit/SLUAAR3
5. TI SLUA456 (March 2008) -- Single Cell Gas Gauge Circuit Design: https://www.ti.com/lit/pdf/slua456
6. Panasonic -- Specifications for NCR18650BF (four-page sheet, no revision stated): https://api.pim.na.industrial.panasonic.com/file_stream/main/fileversion/3446
7. Microchip MCP73831/2 datasheet, DS20001984H (2020): https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf
8. Fortune DW01A datasheet, Rev. 1.1 (June 2010): https://www.ic-fortune.com/upload/Download/DW01A-DS-11_EN.pdf
9. Fortune FS312F-G datasheet, Rev. 1.2 (May 2014): https://www.ic-fortune.com/upload/Download/FS312F-G-DS-12_EN.pdf
10. Lithium Werks -- 26650 Lithium Ion Power Cell, ANR26650M1B (January 2019), manufacturer sheet hosted by distributor: https://a123batteries.com/product_images/uploaded_images/26650.pdf
11. NanJing Top Power -- TP4056-42-SOP8-PP datasheet (three-page sheet, no revision stated), manufacturer sheet hosted by distributor: https://dlnmh9ip6v2uc.cloudfront.net/datasheets/Prototyping/TP4056.pdf
12. ADI/Maxim MAX17048/MAX17049 datasheet, 19-6171 Rev. 7 (November 2016): https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17048-MAX17049.pdf
13. TI BQ769x0 datasheet, SLUSBK2I (March 2022): https://www.ti.com/lit/ds/symlink/bq76920.pdf
