# Motor Control

> BLDC gate driver selection, 3-phase layout, bootstrap circuits, current sensing, dead time, stepper drivers (TMC2209, A4988). MOSFET selection fundamentals -> `misc/mosfet-circuits.md`. General thermal estimation -> `guides/thermal.md`.

## Quick Reference

- **BLDC driver architecture: integrated FET for < 70W, gate driver + external FETs for > 70W.** Integrated FET: limited by package thermal. Gate driver: up to 3.5A/4.5A source/sink gate current.
- **Bootstrap cap >= 10x gate capacitance of high-side FET.** Accounts for DC bias shift, temperature drift, and skipped cycles during load transients.
- **Smart Gate Drive (DRV832x): adjustable IDRIVE eliminates external gate resistors.** Slew rate = Qgd / IDRIVE. Trade EMI vs thermal without board redesign.
- **Current sense shunt: 1-10 mohm, <= 100ppm/C.** Kelvin-connect sense traces as differential pair. Triple-shunt gives simultaneous 3-phase measurement; dual-shunt saves cost but cannot measure one phase during 100% duty cycle sectors.
- **TMC2209 stepper: SpreadCycle for torque, StealthChop for silence.** StallGuard4 sensorless stall detection via SGTHRS register (0-255). CoolStep reduces current by up to 75%.

## Design Rules

### BLDC Gate Driver Selection

- **DRV8316: integrated 3-phase MOSFET driver, 4.5-35V, up to 8A peak.** FOC/sinusoidal control with 200V/us adjustable slew rate. Internal dead time 500ns typical with VGS handshaking -- prevents shoot-through without MCU dead time insertion.
- **DRV8323: 3-phase Smart Gate Driver, 6-60V, external FETs.** Integrates optional 3x current sense amplifiers, optional buck regulator. SPI or hardware interface variants.
- **Rate motor driver voltage at 1.5-2x maximum battery voltage** for high-power motors and battery systems. 1.2x sufficient for well-regulated supplies and low-power motors.
- **Gate driver current determines slew rate and EMI/thermal tradeoff.** Too high IDRIVE: VDS overshoot, SW node ringing, EMI failure. Too low IDRIVE: excessive switching loss, FET heating. DRV832x Smart Gate lets you tune IDRIVE via register without changing external components.
- **IDRIVE slew rate calculation:** t_slew = Qgd / IDRIVE. Example: CSD18532Q5B (Qgd=6.9nC) at IDRIVE=25mA -> t_slew = 276ns. At IDRIVE=150mA -> t_rise = 46ns.
- **Average gate drive current: I_avg = Qg * num_FETs * f_sw.** Example: 44nC * 6 FETs * 45kHz = 11.88mA. Verify gate driver supply can source this continuously.

### Bootstrap Circuit

- **Minimum bootstrap cap (detailed):** C_boot >= Q_total / delta_V_HB, where Q_total = Q_G + (I_HBS * D_max / f_sw) + (I_HB / f_sw). Below minimum -> UVLO trips, high-side FET turns off prematurely.
- **VDD bypass cap >= 10x bootstrap cap.** Replenishes bootstrap cap charge without excessive ripple. 10x ratio limits VDD ripple to 10% worst case.
- **Bootstrap diode: fast recovery or Schottky, low Vf, low junction capacitance.** Slow recovery diode causes large over/undershoot on HB-HS pin that can trigger driver UVLO. Voltage rating must exceed DC-link voltage with margin.
- **Bootstrap resistor (2.2 ohm typical): limits peak inrush current at startup.** 0 ohm causes fast dv/dt on HB-HS that couples into LO/HO outputs (verified on UCC27710). Time constant = R_boot * C_boot / duty_cycle -- too high extends startup time.
- **Use X7R or C0G MLCC for bootstrap cap.** Low ESR/ESL, voltage rating >= 2x VDD. Place bootstrap cap and VDD bypass cap as close as possible to driver supply pins.

> WARNING: At D > 50%, low-side on-time may be insufficient to fully recharge bootstrap cap. Verify bootstrap voltage at worst-case duty cycle. ICs with integrated charge pump (e.g., DRV8316) avoid this issue entirely.

### Dead Time and Shoot-Through

- **DRV8316 internal dead time: 500ns typical at 200V/us slew rate.** Dead time varies with current direction: when body diode conducts in same direction as next FET, dead time shortens (VGS handshaking detects safe turn-on). When current reverses, dead time extends to datasheet typical/max.
- **MCU dead time insertion: only needed if MCU dead time > driver dead time.** If MCU dead time < driver dead time, driver compensates automatically. Adding unnecessary MCU dead time increases duty cycle distortion.
- **DRV831x/MCx831x Delay Compensation feature** auto-corrects asymmetric propagation delays between current-in and current-out phases, reducing duty cycle distortion in sinusoidal commutation. Recommended target: tpd + tdead.

### Current Sensing

- **Triple-shunt (one shunt per phase leg): most accurate.** Measures all 3 phase currents simultaneously in middle of PWM period (center-aligned SVM). Requires 3 ADC channels but provides redundancy -- if one fails, operates as dual-shunt.
- **Dual-shunt: lower cost, measures 2 phases and calculates third** via i_a + i_b + i_c = 0. Cannot measure phase at 100% duty cycle (low-side FET off entire period). Full DC bus utilization still possible since at least 2 phases always measurable in each SVM sector.
- **ADC sampling must be synchronized to PWM center.** Sample during low-side FET on-time only. Low-side on-time must exceed ADC conversion time + settling time to avoid transient artifacts from switching.
- **Sense shunt placement for DRV832x:** connect between low-side FET source and PGND. Kelvin-connect SN and SP pins as differential pair directly to shunt pads. Place 100pF-1nF filter cap at amplifier input pins, not at shunt.
- **Shielding on split-supply systems:** if DRV832x sense amplifier reference (AGND) is separated from power ground, route analog ground plane between sense amplifier and power stage to prevent switching noise coupling.

### 3-Phase Layout

- **Star-point grounding: all ground returns to single point under driver IC.** Digital, analog, and power grounds partitioned on board but joined at star point. Prevents power stage switching current from flowing through analog ground.
- **DRV832x: common ground plane acceptable for most designs.** Split ground plane only needed when sense amplifier noise floor must be < 1 LSB. For split plane, join analog and power ground at single point near driver thermal pad.
- **Half-bridge hot loop: input cap -> high-side FET drain -> high-side FET source/low-side FET drain -> low-side FET source -> sense resistor -> input cap ground.** Minimize this loop area. Place bypass cap directly adjacent to FET drain/source connections.
- **Thermal pad: direct-connect vias (no thermal relief), 0.5mm (20mil) diameter, 0.2mm (8mil) hole.** Each via ~5.7C/W through 1.56mm FR-4. Array of vias under thermal pad for minimum thermal resistance. Do not solder-mask thermal vias -- causes excessive voiding.
- **2-oz copper halves thermal resistance** vs 1-oz for same plane dimensions. Critical for motor drivers where thermal pad is primary heat path.
- **SW node copper: keep minimal.** Large copper area on switch node acts as antenna -- radiates EMI at switching frequency and harmonics.
- **Via current capacity per IPC-2152 (10C rise, 1-oz):** 0.15mm (6mil) = 0.2A, 0.2mm (8mil) = 0.55A, 0.25mm (10mil) = 0.81A, 0.4mm (16mil) = 1.1A. Use multi-via arrays for high-current connections.

### Motor Drive EMC

- **ST AN4694: ground grid improvements on 2-layer boards** provide near-ground-plane performance. Convert single-ended ground traces to grid by adding short connections and moving vias to create multiple parallel return paths.

### Stepper Drivers

- **TMC2209: 2A RMS, 256 microstep, UART interface.** SpreadCycle for max torque, StealthChop2 for silent operation (voltage-mode chopper). Integrated StallGuard4 + CoolStep for sensorless stall detection and load-adaptive current.
- **A4988: 2A peak (1.4A RMS without heatsink), simple step/dir interface.** 16 microstep max. Fixed-frequency PWM chopper. No sensorless stall detection. Budget option for non-critical applications.
- **SpreadCycle chopper tuning (Trinamic AN-001):** Start with TBL=1 (1-2us blank time), TOFF=5-20us range, HEND=10. Reduce hysteresis to 0, increase HEND until vibration stops improving, add 1-2 increments for margin. Measure fast-decay duration with scope -- should slightly exceed blank time. Distorted sine wave at low velocity with correct supply voltage -> increase TBL by one (too-low blank time is the cause).
- **Supply voltage window:** R_coil * I_coil << Vs < 25 * R_coil * I_coil. Below minimum: motor cannot follow sine wave (back-EMF + resistive drop exceeds supply). Above maximum: excessive power dissipation and chopper frequency.
- **StallGuard2 parameterization (Trinamic AN-002):** Optimize SGT in range -10 to +10. Set SGMIN=0 (disable CoolStep) during calibration. Run motor at medium velocity, adjust SGT until SG=0 at mechanical load close to stall. SGT outside -10 to +10 indicates suboptimal motor/speed/voltage combination. SFILT=1 averages over 4 full steps for noise reduction; SFILT=0 for fastest response.
- **StallGuard velocity range is limited.** At zero/low velocity: resistive losses dominate, StallGuard cannot distinguish load from I^2R heating. At high velocity: driver cannot deliver full current. Only works in mid-velocity range. Motor coil resistance increases with temperature (copper tempco) -- calibrate at operating temperature extremes.
- **CoolStep: load-adaptive current reduces power by up to 75%.** Automatically increases current when load increases (via StallGuard feedback). Set minimum current (SGMIN) high enough to prevent stall at maximum expected load transient.
- **Motor selection for StallGuard accuracy:** lower coil resistance -> lower resistive loss offset -> more precise SG reading. Operating at 80% of nominal current reduces resistive losses to 64% while retaining 80% torque, improving StallGuard signal quality.

## Common Mistakes

- **Skipping bootstrap resistor causes false gate driver faults at startup.** 0 ohm bootstrap resistor allows fast dv/dt on HB-HS that couples into gate outputs. 2.2 ohm eliminates the issue with negligible impact on steady-state operation.
- **Thermal relief on driver thermal pad vias.** Constricts heat path from die to bottom ground plane. Motor drivers dissipate significant power -- direct-connect vias are mandatory, not optional.
- **Via clusters splitting ground plane under signal traces.** Creates gap forcing return current to detour around via field, forming large loop antenna. Stagger vias and route signal traces around via clusters.
- **Ground plane discontinuity between power stage and sense amplifier.** Switching current return path detours through analog ground, injecting noise into current sense. Maintain continuous ground plane or use controlled split with single join point.
- **StallGuard calibrated at room temperature only.** Coil resistance increases with temperature (copper tempco 0.393%/C), changing the SG reading. Calibrate at operating temperature extremes and add safety margin.
- **Solder-masking thermal vias under driver pad.** Causes excessive voiding during reflow. Leave thermal vias exposed for direct solder connection.

## Formulas

**Bootstrap capacitor (rule of thumb):**
**Rule of thumb:** C_boot >= 10 * C_gate. For 58nC Qg FET at 10V gate drive: C_gate = 58nC/10V = 5.8nF -> C_boot >= 58nF, use 100nF X7R.
**Formula:** C_boot >= Q_total / delta_V_HB, where Q_total = Q_G + (I_HBS * D_max / f_sw) + (I_HB / f_sw), delta_V_HB = VDD - V_diode - V_UVLO
**Example:** Q_G=58nC, I_HBS=100uA, D_max=0.95, f_sw=20kHz, I_HB=3mA, VDD=12V, V_diode=0.5V, V_UVLO=8V -> Q_total = 58nC + 4.75nC + 150nC = 212.75nC. delta_V_HB = 3.5V. C_boot >= 60.8nF -> use 100nF.

Contactor coil drive formulas -> `misc/ev-power-systems.md`.

## Sources

### Related Rules

- `misc/mosfet-circuits.md` -- MOSFET selection fundamentals, gate drive, SOA
- `guides/thermal.md` -- General thermal estimation for power dissipation
- `misc/ev-power-systems.md` -- Contactor coil drive formulas

### References

1. TI SLVAES1A -- Brushless-DC Motor Driver Considerations and Selection Guide: https://www.ti.com/document-viewer/lit/html/SLVAES1A
2. TI SLVA959B -- Best Practices for Board Layout of Motor Drivers: https://www.ti.com/document-viewer/lit/html/SLVA959B
3. TI SLUA887 -- Bootstrap Circuitry Selection for Half-Bridge Configurations: https://www.ti.com/document-viewer/lit/html/SLUA887
4. TI SLVA714D -- Understanding Smart Gate Drive: https://www.ti.com/lit/an/slva714d/slva714d.pdf
5. NXP AN14164 -- Current Sensing Techniques in Motor Control Applications: https://www.nxp.com/docs/en/application-note/AN14164.pdf
6. ST AN4694 -- EMC Design Guides for Motor Control Applications: https://www.st.com/resource/en/application_note/an4694-emc-design-guides-for-motor-control-applications-stmicroelectronics.pdf
7. TI SLVA951 -- Layout Guide for the DRV832x Family of Three-Phase Smart Gate Drivers: https://www.ti.com/lit/pdf/slva951
8. TI SLVAF84 -- Delay and Dead Time in Integrated MOSFET Drivers: https://www.ti.com/document-viewer/lit/html/SLVAF84
9. ADI (Trinamic) AN-001 -- Parameterization of spreadCycle: https://www.analog.com/en/resources/app-notes/an-001.html
10. ADI (Trinamic) AN-002 -- Parameterization of StallGuard2 & CoolStep: https://www.analog.com/en/resources/app-notes/an-002.html
11. Allegro -- A4988 DMOS Microstepping Driver Datasheet: https://www.allegromicro.com/-/media/files/datasheets/a4988-datasheet.pdf
