# Motor Control

> BLDC gate driver selection, 3-phase layout, bootstrap circuits, current sensing, dead time, stepper drivers (TMC2209, A4988). MOSFET selection fundamentals -> `misc/mosfet-circuits.md`. General thermal estimation -> `guides/thermal.md`.

## Quick Reference

- **TI's 70W architecture boundary is typical guidance, not a rating.** Integrated-FET devices suit low/mid power and external-FET gate drivers higher power; actual winding current, hot Rds(on), PCB cooling and switching loss set the boundary [1, Section 2.1].
- **Bootstrap capacitance must cover Qg and driver consumption at allowable droop.** The 10 * C_gate shortcut alone does not verify maximum on-time or MLCC bias loss [3, pp.3-4].
- **DRV832x IDRIVE controls gate current, not dV/dt directly.** Qgd / IDRIVE estimates transition time; tune against the measured waveform [4, Sections 1.4, 2.1].
- **Dual low-side shunts limit DC-bus utilization.** Triple-shunt sensing can select the two measurable phases near 100% peak duty; two fixed shunts cannot do that in every SVM sector [5, pp.4-5].
- **TMC2209 StallGuard4 operates with StealthChop.** Its SGTHRS is unsigned 0-255; StallGuard2's signed SGT tuning procedure does not transfer to it [11, pp.29,58-59].

## Design Rules

### BLDC Gate Driver Selection

- **DRV8316: integrated 3-phase MOSFET driver, 4.5-35V, up to 8A peak.** It supports externally controlled FOC/sinusoidal commutation; the peak current is not a continuous thermal rating [12, pp.1,68-70].
- **DRV8323: 6-60V external-FET Smart Gate Driver with three current-sense amplifiers.** The R suffix adds a 600mA buck regulator; S/H variants select SPI/hardware interfaces. Peak source/sink gate drive is 1A/2A [13, pp.1,5].
- **TI recommends voltage-rating headroom of 1.2x maximum supply for well-regulated low-power motors, or 1.5-2x for high-power/battery systems.** Check regeneration and switching transients against the actual ratings; these are selection guidelines, not surge clamps [1, Section 2.1; 13, Section 10.1].
- **Gate drive current determines the EMI/thermal tradeoff.** Excessive IDRIVE increases VDS overshoot, ringing and induced turn-on; insufficient IDRIVE increases switching loss. DRV832x provides adjustable current without external gate resistors [4, Section 2.1; 13, Section 8.3.1].
- **IDRIVE estimates the voltage-transition duration: t_slew = Qgd / IDRIVE.** TI's CSD18532Q5B example uses Qgd=6.9nC (typical at VDS=30V, ID=25A); 25mA gives 276ns calculated versus approximately 312ns measured with DRV8701 at a 24V bus. This is a first-order constant-current approximation [4, pp.3,6].
- **Budget average gate charge for every FET that switches.** I_avg = Qg * num_FETs * f_sw; TI's 44nC, six-FET, 45kHz example gives 11.88mA for gate charging alone. Add driver quiescent current and check the actual gate-voltage/bus-voltage charge data [4, p.7].

### Bootstrap Circuit

- **For bootstrap-only drivers such as UCC27710, calculate charge and allowable droop.** C_boot >= Q_total / delta_V_HB; include gate charge, floating-supply quiescent current and leakage for the longest high-side on-time. The falling UVLO threshold is only a lower bound: the remaining voltage must also fully enhance the FET [3, p.3; 13, Section 9.2.1.2].
- **VDD bypass cap >= 10x bootstrap cap is TI's starting recommendation.** Its charge-sharing model limits VDD-capacitor ripple to approximately 10%; verify effective capacitance and supply impedance [3, p.4].
- **Bootstrap diode: fast recovery or Schottky, low Vf, low junction capacitance.** Rate reverse voltage above the maximum DC-link voltage with margin and check startup peak current; diode recovery causes HB-HS overshoot/undershoot and UVLO trips in TI's test [3, pp.4-5].
- **2.2 ohm is the UCC27710 startup example, not a universal bootstrap resistor.** It removes the unwanted output excursions seen with 0 ohm in that test. Check peak charging current and sufficient recharge during the actual high-side off-time; increasing R_boot delays startup [3, pp.6-7].
- **Bootstrap MLCC rating: TI recommends 2x VDD with low ESR/ESL.** Use effective capacitance after voltage bias, temperature and tolerance; oversized capacitors also increase startup charge and diode stress [3, pp.3-4].

> WARNING: Bootstrap recharge depends on the switch-node-low interval and charging impedance, not a universal 50% duty-cycle threshold. DRV8316 and DRV832x use charge-pump high-side supplies; apply their capacitor and gate-charge requirements instead of a generic bootstrap network [3, pp.2-3; 12, Section 8.3.1; 13, Section 9.2.1.2].

### Dead Time and Shoot-Through

- **DRV8316's 500ns dead time is typical for the 200V/us setting and specified commutation direction.** When current flows out of OUTx, low-side-to-high-side commutation gives the typical delay; high-side-to-low-side commutation is shorter. Reverse current reverses those cases. VGS handshaking prevents overlap, so 500ns is not a fixed minimum [7, Section 2].
- **Additional MCU dead time changes DRV8x output timing according to both current direction and input edges.** In the typical-delay cases, dead time follows the larger MCU/driver value; same-direction diode/FET conduction shortens it. Use SLVAF84's table rather than treating MCU dead time as required only above a threshold; this behavior does not establish safe dead time for unrelated external-FET drivers [7, Sections 3-4].
- **Some DRV831x/MCx831x devices provide Delay Compensation** to reduce duty-cycle distortion from unequal delays. TI recommends a target of tpd + tdead; do not add this target as an extra physical shoot-through dead time [7, Section 5].

### Current Sensing

- **Triple low-side shunts permit phase selection at high modulation.** With center-aligned SVM, measure two valid currents simultaneously and reconstruct the third when a phase reaches 100% duty. Two simultaneous ADC modules suffice; retaining a failed-sensor backup requires sacrificing full bus utilization [5, pp.3-4].
- **Dual-shunt: measure two fixed phases and reconstruct the third.** Limit peak duty so each measured phase has a valid low-side conduction window. NXP's center-sampled symmetrical PWM requires minimum low-side on-time >= 2 * ADC conversion time, with settling and dead time added [5, p.5].
- **Sense shunt placement for DRV8323/DRV8323R:** connect between low-side FET source and PGND. Kelvin-connect SPx and SNx directly to the shunt terminals; check amplifier settling and stability before adding an input filter [6, Sections 7.4, 8].
- **In split-ground DRV832x layouts, shield SPx/SNx with power ground.** These inputs belong to the power-stage domain; VREF and SOx use the logic-ground domain. AGND is not a replacement for the amplifier's VREF input [6, Section 8].

### 3-Phase Layout

- **DRV832x normally uses a common ground plane.** Connect ground pins directly to the thermal pad and plane. If noise isolation requires a split, connect domains near the driver and place the thermal pad over power ground; there is no specified 1-LSB trigger for splitting [6, Section 2].
- **DRV832x shunt and low-side FET pads need direct copper connections.** Thermal relief on the shunt adds parasitic inductance and voltage spikes; the driver thermal pad also needs direct connections [6, Sections 2, 7.2, 7.4]. General via sizing and exposed-pad assembly -> `guides/pcb-layout.md`, `guides/thermal.md`.
- **Doubling copper thickness halves the lateral copper-path resistance in TI's fixed-geometry model.** It does not halve total junction-to-ambient thermal resistance [2, Section 2.3].

### Motor Drive EMC

- **TI SLVA959B's two-layer ground-grid example** connects previously single-ended ground paths with added traces and moved vias, approaching ground-plane behavior. This example is not an ST AN4694 measurement [2, Section 1.2].

### Stepper Drivers

- **TMC2209: up to 2A RMS / 2.8A peak with adequate cooling.** UART configures microstepping up to 256; MicroPlyer interpolates pin-selected steps. StallGuard4 and CoolStep use StealthChop; switching to SpreadCycle changes the available load-detection behavior [11, pp.1,14,58-60].
- **A4988: up to 35V and +/-2A output rating, STEP/DIR, up to 1/16 microstep.** It uses fixed-off-time current regulation, not fixed-frequency PWM. Continuous current depends on PCB cooling; there is no guaranteed 1.4A RMS without a heatsink [10, pp.1-2,5,7].
- **SpreadCycle tuning values depend on the IC clock and register encoding.** AN-001 starts with 1-2us blanking at 16MHz and 5-20us off-time; those are times, not raw TOFF register values. Its HEND encoding has a -3 offset, so a hysteresis-end value of 10 is encoded as 13. Check the selected driver's register table [8, Parameterization of spreadCycle].
- **AN-001's supply guideline is R_coil * I_coil << Vs < 25 * R_coil * I_coil.** It describes the chopper/motor operating window, not permission to exceed the driver's voltage rating [8, Prerequisites].
- **StallGuard2 parameterization applies to StallGuard2 devices, not TMC2209.** AN-002 recommends tuning SGT near -10 to +10, SEMIN=0 to disable CoolStep during calibration, and SFILT=0 for fastest stall response; SFILT=1 averages over four full steps [9, StallGuard2 Parameterization].
- **TMC2209 StallGuard4 calibration:** at the operating speed/current, increase load and use half the lowest pre-stall SG_RESULT as the starting SGTHRS; then test across motors and temperature. SEMIN=0 disables CoolStep; SEMIN is a StallGuard-result threshold, not the minimum motor-current setting [11, pp.29-30,58-62].
- **CoolStep's up-to-75% figure is an energy-saving claim, not a guaranteed current reduction.** Maintain torque margin for load transients and the actual speed range [11, pp.1,59-62].

## Common Mistakes

- **Calibrating StallGuard only at room temperature.** Coil resistance and motor losses change the reading; AN-002 requires tests with different motors, electronics and motor temperatures to establish a reliable threshold margin [9, Detecting a Stall].
- **Assigning a via a universal current or thermal rating.** TI's 20mil pad/8mil hole example depends on its geometry; the quoted thermal calculation does not establish a plated-barrel rating. Use the actual barrel copper and board stackup -> `guides/thermal.md`, `guides/pcb-layout.md` [2, Section 2.5].

## Formulas

**Bootstrap sizing for UCC27710-style floating supplies [3, p.3]:**
**Rule of thumb:** C_boot >= 10 * C_gate, with C_gate = Qg / (VDD - V_diode), is only a starting check. Also satisfy charge/droop, minimum gate voltage and recharge timing using effective capacitance.
**Formula:** C_boot >= Q_total / delta_V_HB; Q_total = Q_G + I_HBS * D_max / f_sw + I_HB / f_sw; delta_V_HB = VDD - V_diode - V_UVLO. I_HBS is HB-to-VSS leakage; I_HB is floating-supply quiescent current. Use worst-case device values and add any external leakage and longer skipped-cycle on-time.
**Example:** Illustrative inputs Q_G=58nC, I_HBS=100uA, D_max=0.95, f_sw=20kHz, I_HB=3mA, VDD=12V, V_diode=0.5V, V_UVLO=8V give Q_total=212.75nC and delta_V_HB=3.5V, hence 60.8nF minimum. A nominal 100nF is acceptable only if its effective value exceeds that minimum and its resulting gate voltage satisfies the FET's drive requirement.

Contactor coil drive formulas -> `misc/ev-power-systems.md`.

## Sources

### Related Rules

- `misc/mosfet-circuits.md` -- MOSFET selection fundamentals, gate drive, SOA
- `guides/thermal.md` -- General thermal estimation for power dissipation
- `misc/ev-power-systems.md` -- Contactor coil drive formulas

### References

1. TI SLVAES1A -- Brushless-DC Motor Driver Considerations and Selection Guide: https://www.ti.com/document-viewer/lit/html/SLVAES1A
2. TI SLVA959B -- Best Practices for Board Layout of Motor Drivers: https://www.ti.com/document-viewer/lit/html/SLVA959B
3. TI SLUA887A (September 2023) -- Bootstrap Circuitry Selection for Half-Bridge Configurations: https://www.ti.com/document-viewer/lit/html/SLUA887
4. TI SLVA714D (March 2021) -- Understanding Smart Gate Drive: https://www.ti.com/lit/an/slva714d/slva714d.pdf
5. NXP AN14164 (Rev.1.0, February 2024) -- Current Sensing Techniques in Motor Control Applications: https://www.nxp.com/docs/en/application-note/AN14164.pdf
6. TI SLVA951 (March 2018) -- Layout Guide for the DRV832x Family of Three-Phase Smart Gate Drivers: https://www.ti.com/lit/pdf/slva951
7. TI SLVAF84 (September 2021) -- Delay and Dead Time in Integrated MOSFET Drivers: https://www.ti.com/document-viewer/lit/html/SLVAF84
8. ADI (Trinamic) AN-001 -- Parameterization of spreadCycle: https://www.analog.com/en/resources/app-notes/an-001.html
9. ADI (Trinamic) AN-002 -- Parameterization of StallGuard2 & CoolStep: https://www.analog.com/en/resources/app-notes/an-002.html
10. Allegro A4988 (Rev.8) -- DMOS Microstepping Driver Datasheet: https://www.allegromicro.com/-/media/files/datasheets/a4988-datasheet.pdf
11. ADI TMC2209 (Rev.1.09, February 2023): https://www.analog.com/media/en/technical-documentation/data-sheets/TMC2209_datasheet_rev1.09.pdf
12. TI DRV8316 (SLVSF16B, April 2022): https://www.ti.com/lit/ds/symlink/drv8316.pdf
13. TI DRV832x (SLVSDJ3D, March 2022): https://www.ti.com/lit/ds/symlink/drv8323.pdf
