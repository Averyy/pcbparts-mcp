# MOSFET Circuits

> Selection criteria, gate drive, load switches, inductive load driving, TEC/Peltier control, paralleling.

## Quick Reference

- **Size VDS for the worst-case bus and switching overshoot.** Infineon recommends at least 20% margin above maximum steady-state voltage; twice the bus voltage is a motor-inverter example, not a ceiling [1, Section 3.4].
- **Check guaranteed Rds(on) at the available gate voltage.** CSD17571Q2 has Vgs(th)=1.3-2V at only 250uA; its Rds(on) is specified at 4.5V and 10V, so that threshold does not qualify it for 3.3V power switching [10, p.3].
- **Linear-mode SOA depends on case temperature and pulse duration.** Use the device's SOA and its manufacturer's temperature-derating method, not a universal 100 degrees C instability threshold [1, Section 6; 5, Sections 4-7].
- **For fast relay release, use a series diode/Zener suppression path.** Check the Zener's clamping voltage at coil current against MOSFET VDS; a plain freewheel diode extends current decay [7, Figures 3-4].
- **TPS22916 reverse blocking is a specified feature, not a property of every load switch.** Its timing and output-discharge options depend on the suffix [11, Sections 3, 8.3].

## Design Rules

### MOSFET Selection

- **ID_max can be package-limited or thermally limited.** Infineon's IPP029N06N example calculates 169A with Tj(max)=175 degrees C, Tc=25 degrees C, RthJC=0.8 degrees C/W and hot Rds(on)=6.6mohm, but caps the rating at 100A because of package/assembly constraints. Compare Rds(on) at the operating Vgs and thermal conditions rather than ID_max alone [2, Section 2.2].
- **Infineon's alpha=0.4%/degree C is an OptiMOS approximation.** Rds(on)(Tj) = Rds(on)_25C * 1.004^(Tj - 25), giving 1.49 times at 125 degrees C and 1.65 times at 150 degrees C. Use the selected device's temperature curve when available [2, Section 2.9].
- **A logic-level label does not establish MCU-drive suitability.** Standard-level devices in AN_2203 are typically driven at 10-15V; logic-level devices typically at 5V. The latter's lower threshold increases susceptibility to dVDS/dt-induced turn-on in half-bridges [4, Sections 2.1-2.2].
- **SOA is the binding constraint for linear-mode operation.** Hot-plug, soft-start, current limiting, and active clamping require checks at simultaneous VDS and ID for the actual pulse waveform, rather than relying on Rds(on) or ID_max [5, Sections 3-7].

> WARNING: Electrothermal instability causes localized current crowding below the device's zero-temperature-coefficient operating point. A low-Rds(on) trench MOSFET is not automatically suitable for hot-swap or active clamping; check the thermal-stability boundary as well as the constant-power boundary [1, Sections 6.3-6.4].

**MOSFET selection checks (resistances at 25 degrees C):**

| Application | Part | Key Specs |
|-------------|------|-----------|
| 5V N-ch load switch | CSD17571Q2 | 30V, 24mohm typical / 29mohm max at Vgs=4.5V, ID=5A; Qg=2.4nC typical / 3.1nC max at 4.5V, VDS=15V, ID=5A; SON 2mm * 2mm [10, pp.1,3] |
| 12V N-ch switching | BSC019N04LS | 40V, 2.7mohm max at Vgs=4.5V, ID=50A; 1.9mohm max at 10V; PG-TDSON-8 [12, pp.1,5] |
| P-ch load switch | DMP2035U | -20V, 45mohm max at Vgs=-2.5V, ID=-4A; SOT-23; Vgs absolute maximum +/-10V rules out pulling its gate directly to ground on a 12V rail [13, p.2] |
| Low-voltage P-ch | Si2301CDS | -20V, 112mohm max at Vgs=-4.5V, ID=-2.8A; 142mohm max at -2.5V, -2A; SOT-23; Vgs absolute maximum +/-8V [14, pp.1-2] |

- Reverse polarity MOSFET selection -> `protection/reverse-polarity.md`. Thermal design -> `guides/thermal.md`.

### Gate Drive

- **Gate resistance includes driver output impedance and the FET's internal gate resistance.** During the plateau, Ig_on is approximately (Vdrive - Vplateau) / (Rdriver_source + Rg_external + Rg_internal). Select external resistance from the required gate current and verify ringing and switching loss; there is no universal 10 ohm starting value in this calculation [4, Sections 4.1, 4.3].
- **Separate turn-on and turn-off resistors when the half-bridge needs stronger turn-off.** A diode/resistor network allows independent switching speeds; stronger pull-down reduces induced turn-on, while turn-off overshoot still requires checking [1, Sections 3.4, 7.1].
- **Use gate charge over the actual switching excursion.** Crss varies with VDS, so a single capacitance measured at one voltage does not predict the whole transition. Gate-loop/source inductance also alters the effective drive voltage [2, Sections 2.11, 2.15; 4, Section 3.2].
- **QGD/QGS of 0.5-0.8 and QGD/QGS(TH) < 1 are Infineon's hard-switching selection guidance.** Higher charge ratios increase dVDS/dt-induced turn-on risk; check the driver pull-down and actual gate waveform too [1, Section 7.1].
- **Bootstrap sizing uses charge divided by allowable droop, not capacitance compared directly with Qg.** Include driver consumption and maximum high-side on-time; bootstrap-only supplies need a recharge interval. MOTIX 6EDL7141 uses charge pumps for operation up to 100% duty cycle [4, Sections 6.2, 6.6]; calculation -> `misc/motor-control.md`.

**Gate drivers:**

| Application | Part | Key Specs |
|-------------|------|-----------|
| Single low-side | UCC27511A | 4A source / 8A sink peak, 4.5-18V supply, SOT-23-6; split outputs set turn-on/off resistances independently [15, pp.1-2] |
| Isolated dual-channel | UCC21520 | 4A source / 6A sink peak, SOIC-16; each output needs bias referenced to its own source [16, Sections 3, 6.3] |
| Full-bridge | MIC4606 | 85V bridge, 1A peak drive, 5.5-16V gate supply, bootstrap; QFN-16 or TSSOP-16 [17, pp.1,4] |
| Configurable 3-phase | MOTIX 6EDL7141 | 10mA-1.5A programmable source/sink, SPI, charge pumps for 100% duty cycle [4, Section 6.6] |

### Load Switches

- **TPS22916: 1-5.5V, 2A maximum continuous switch current, WCSP-4.** RON is 60mohm typical / 80mohm max at VIN=5V, IOUT=200mA, 25 degrees C, rising to 100mohm max over -40 to +85 degrees C. B/C suffixes select fixed fast/slow timing; there is no CT pin or thermal shutdown [11, Sections 3, 5, 6.5, 9.4].
- **Discrete P-ch load switch:** source to supply, drain to load. Pull the gate up to source for default-off and use a small-signal N-ch level shifter when the control cannot reach the source voltage; AND9093's example uses 1K-10K, selected to limit pull-up current to milliamps or less. Constrain Vgs to the selected FET's rating with a current-limited drive/clamp network [3, pp.1-3; 13, p.2; 14, p.1].
- **Discrete N-ch high-side: drain to supply, source to load.** The gate supply must rise above the output by the Vgs needed for specified Rds(on); a bootstrap-only driver cannot sustain an always-on output [3, pp.1-3; 4, Section 6.2].
- **Set inrush from load capacitance and the permissible supply current.** A gate RC does not establish a universal 1-10ms safe ramp; validate the resulting VDS/ID waveform against SOA at startup temperature [3, Turn-on Considerations; 5, Section 7].
- **A single discrete load-switch FET does not block output-to-input backfeed.** With the P-ch source at VIN or N-ch drain at VIN, the body diode conducts from output toward input. Use a device with specified reverse blocking or back-to-back FETs -> `power/power-path.md` [3, Figures 2-3; 6, Reverse Current Blocking].

### Inductive Load Driving (Relays, Solenoids)

- **Low-side coil flyback diode: cathode to coil supply, anode to the switched coil terminal.** Size it for initial turn-off current and reverse voltage. COM on ULN2003A is the common cathode of its clamp diodes and connects to the coil supply [18, Sections 4, 7.2, 8.2]; a plain diode slows release [7, Figure 3].
- **Series Zener plus forward diode across the coil gives faster release.** The suppression path must block during energization and conduct through Zener breakdown at turn-off. For a low-side switch, check VDS_peak = Vcoil + VZ(clamp at coil current) + VF + switching overshoot; do not use nominal Zener voltage or a fixed 0.3V diode drop as a guaranteed clamp [7, Figure 4; 1, Section 3.4].
- **ULN2003A for multiple low-current coils:** seven Darlington outputs, 50V and 500mA single-output rating. At 350mA collector / 500uA input current, Vce(sat) is 1.2V typical / 1.6V max; package thermal limits prevent treating all seven channels as independently continuous 500mA loads [18, Sections 3, 5.6, 5.8, 9.3].

### TEC/Peltier Driver Circuits

- **TI's unfiltered-PWM TEC test measured temperature lift, not 39% less input power for equal cooling.** On ET-063-10-13 with a heatsink, 1A DC produced 8.1 degrees C more ambient-to-cold-side difference than 0A/2A, 50% duty, 20kHz PWM. TPS54201-Q1 provided filtered current and DRV8873-Q1 the unfiltered bridge drive. The five-month, 1.4A aging comparison found no measurable module degradation under those test conditions [9, pp.2-5].
- **For reversible TEC drive:** DRV8871 provides a 6.5-45V H-bridge with 3.6A peak capability and internal current regulation, in HSOP-8; continuous capability requires a thermal calculation. TI also identifies TPS63020 as a constant-current buck-boost alternative [19, pp.1,13-14; 9, p.3].
- **Current drive avoids the temperature-dependent impedance error of open-loop voltage drive.** TI's test uses constant-current regulation; its result does not establish that voltage drive universally causes current runaway [9, p.2].
- **PID compensation values describe a laser-diode TEC model, not every Peltier assembly.** HFAN-08.2.0 assumes poles at 20mHz and 1Hz; its example places an integrator zero at 70mHz, a derivative zero at 0.4Hz and crossover at 2Hz. Characterize the actual TEC/thermistor response, including heating mode [8, Using a Control Loop; Compensating the Loop].
- **High-impedance TEC integrators need leakage control.** HFAN-08.2.0 specifies MAX4475ASA (150pA maximum input leakage), a guard ring, and low-leakage capacitors; polystyrene is preferred, large ceramic values require leakage checks, and electrolytic/tantalum capacitors are excluded [8, Selecting Components].

**TEC driver ICs:**

| IC | Topology | Key Specs |
|----|----------|-----------|
| MAX1968 | PWM H-bridge | +/-3A, integrated switches, TSSOP-EP-28 [20, p.1] |
| ADN8834 | Linear/PWM H-bridge | 1.5A, single inductor [21, p.1] |
| LTC1923 | PWM H-bridge controller | External FETs, SSOP-28 or QFN-32 [22, pp.1-2] |

### Paralleling MOSFETs

- **Positive Rds(on) tempco helps sharing only in fully enhanced operation.** Dynamic sharing also depends on Vgs(th), transconductance, capacitances and diode recovery; same part/lot does not guarantee a particular threshold spread [1, Section 10; 2, Section 2.7].
- **Give each parallel FET its own gate network.** Individual series resistors or ferrite beads decouple gates; choose values for the actual devices and parasitics rather than a universal 1-10 ohm range or oscillation frequency [1, Section 10].
- **Keep source and gate-drive impedances matched.** Common-source inductance feeds back against gate drive during current transitions; a separate source return prevents power-path inductance from becoming part of the drive loop [1, Section 10; 4, Section 3.2].

## Common Mistakes

- **Using nominal Zener voltage as the hot flyback clamp.** The suppression diode's operating-current voltage, temperature behavior and tolerance determine peak VDS. The gate clamp must also respect the selected part's Vgs maximum: the listed DMP2035U and Si2301CDS allow only +/-10V and +/-8V respectively [7, Figure 4; 13, p.2; 14, p.1].
- **Treating a ramped hot-plug waveform as a full-duration square pulse.** TI's equivalent-square method retains peak power and equal energy; apply temperature and repetition corrections separately. A peak instantaneous power alone does not establish safe operation [5, pp.6-7].

## Formulas

**SOA temperature derating, TI CSD17570Q5B example [5, p.4]:**
**Rule of thumb:** At Tc=100 degrees C and Tj(max)=150 degrees C, TI's linear derating factor is 0.4.
**Formula:** IDS(Tc) = IDS(25 degrees C) * (Tj_max - Tc) / (Tj_max - 25 degrees C)
**Example:** For the 12V, 10ms single-pulse SOA point, 7.3A * (150 - 100)/(150 - 25) = 2.92A. Check case temperature, pulse shape and repetition separately; this is not an ambient-temperature rating.

## Sources

### Related Rules

- `protection/reverse-polarity.md` -- Reverse polarity MOSFET selection
- `guides/thermal.md` -- Thermal design for power MOSFETs
- `power/power-path.md` -- Back-to-back FETs for reverse current blocking

### References

1. Infineon AN_2112_PL18_2112_024619 (V1.1, February 2022) -- Designing with Power MOSFETs: https://www.infineon.com/assets/row/public/documents/24/42/infineon-designing-with-power-mosfets-applicationnotes-en.pdf
2. Infineon AN 2012-03 (V1.1, March 2012) -- OptiMOS Power MOSFET Datasheet Explanation: https://www.infineon.com/assets/row/public/documents/24/42/infineon-mosfet-optimos-datasheet-explanation-an-en.pdf
3. onsemi AND9093/D (Rev.1, February 2014) -- Using MOSFETs in Load Switch Applications: https://www.onsemi.com/pub/collateral/and9093-d.pdf
4. Infineon AN_2203_PL18_2204_004502 (V1.0, April 2022) -- Gate Drive for Power MOSFETs in Switching Applications: https://www.infineon.com/dgdl/Infineon-Gate_drive_for_power_MOSFETs_in_switchtin_applications-ApplicationNotes-v01_00-EN.pdf?fileId=8ac78c8c80027ecd0180467c871b3622
5. TI SLUAAO2 (March 2023) -- Using MOSFET Safe Operating Area Curves in Your Design: https://www.ti.com/lit/an/sluaao2/sluaao2.pdf
6. TI SLVA652A -- Basics of Load Switches: https://www.ti.com/lit/an/slva652a/slva652a.pdf
7. ADI -- Switching Inductive Loads with Safe Demagnetization: https://www.analog.com/en/resources/technical-articles/switching-inductive-loads-with-safe-demagnetization.html
8. ADI HFAN-08.2.0 -- How to Control and Compensate a Thermoelectric Cooler: https://www.analog.com/en/resources/technical-articles/hfan0820-how-to-control-and-compensate-a-thermoelectric-cooler-tec.html
9. TI SLUA979A (January 2020) -- Driving a Peltier Element (TEC): Efficiency and Aging: https://www.ti.com/lit/an/slua979a/slua979a.pdf
10. TI CSD17571Q2 (SLPS393A, January 2015): https://www.ti.com/lit/ds/symlink/csd17571q2.pdf
11. TI TPS22916 (SLVSDO5F, December 2021): https://www.ti.com/lit/ds/symlink/tps22916.pdf
12. Infineon BSC019N04LS (Rev.2.4, May 2024): https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsc019n04ls-datasheet-en.pdf
13. Diodes DMP2035U (DS31830 Rev.11-2, June 2025): https://www.diodes.com/assets/Datasheets/DMP2035U.pdf
14. Vishay Si2301CDS (68741 Rev.C, October 2010): https://www.vishay.com/docs/68741/si2301cd.pdf
15. TI UCC27511A (SLUSD95A, January 2024): https://www.ti.com/lit/ds/symlink/ucc27511a.pdf
16. TI UCC21520 (SLUSCJ9F): https://www.ti.com/lit/ds/symlink/ucc21520.pdf
17. Microchip MIC4606 (DS20005604D): https://www.microchip.com/content/dam/mchp/documents/APID/ProductDocuments/DataSheets/MIC4606-Data-Sheet-DS20005604D.pdf
18. TI ULN200x/ULQ200x (SLRS027T): https://www.ti.com/lit/ds/symlink/uln2003a.pdf
19. TI DRV8871 (SLVSCY9B, July 2016): https://www.ti.com/lit/ds/symlink/drv8871.pdf
20. ADI MAX1968/MAX1969 (Rev.3, June 2015): https://www.analog.com/media/en/technical-documentation/data-sheets/MAX1968-MAX1969.pdf
21. ADI ADN8834 (Rev.C): https://www.analog.com/media/en/technical-documentation/data-sheets/ADN8834.pdf
22. ADI LTC1923 (1923f): https://www.analog.com/media/en/technical-documentation/data-sheets/1923f.pdf
