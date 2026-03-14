# MOSFET Circuits

> Selection criteria, gate drive, load switches, inductive load driving, TEC/Peltier control, paralleling.

## Quick Reference

- **VDS sizing: 2x Vin_max, no more.** Higher voltage = higher Rds(on) for same die area. 30V Si ~10mohm, 60V ~25mohm, 100V ~80mohm. A 60V FET on a 12V rail has 2-3x the Rds(on) of a 25V part.
- **Check Rds(on) at your actual Vgs, not 10V.** Rds(on) at 4.5V can be 2-3x higher than at 10V. For 3.3V drive, verify at Vgs=3.3V or select FETs specified for 2.5V drive (Infineon OptiMOS 2.5V family).
- **Spirito effect: SOA shrinks at high temperature.** Linear-mode hotspot thermal runaway at Tj>100C. 25C SOA curves are dangerously optimistic. Always use highest-temperature SOA curve.
- **Relay coil flyback: Zener + Schottky in series, not Schottky alone.** Schottky-only delays release 5-50x. 12V Zener: clamps at 12.3V, release drops from ~50ms to ~2ms.
- **Integrated load switches beat discrete below 5A.** TPS22916, RT9742: built-in inrush control, thermal shutdown, reverse current blocking, <1uA shutdown.

## Design Rules

### MOSFET Selection

- **Datasheet ID_max is a package limit, not silicon limit.** Bond wires cap current below what Rds(on)/Rth would allow. Infineon IPP029N06N: calculates to 169A from Rds(on)/Rth, bond wires cap at 100A. Compare FETs by Rds(on) at your operating Vgs, not by ID_max.
- **Rds(on) temperature coefficient: alpha ~0.4%/C for Si MOSFETs.** Rds(on)(Tj) = Rds(on)_25C * 1.004^(Tj - 25). At 125C: 1.49x. At 150C: 1.65x. Always use hot Rds(on) for thermal calculations.
- **Logic-level gate (Vgs(th) < 2.5V) required for direct MCU drive.** Standard-level needs 10V gate drive. Logic-level FETs have higher Qg than standard-level at same Rds(on)/VDS -- and lower Vgs(th) makes them susceptible to dVDS/dt-induced turn-on in half-bridge. Standard-level preferred for high-frequency switching.
- **FOM = Rds(on) * Qg for switching apps; Rds(on) alone for DC loads.** Gate charge, not Rds(on), limits switching speed. At Qg=50nC, Ig=25mA: ton=2us.
- **SOA is the binding constraint for any linear-mode operation.** Hot-plug, soft-start, current limiting, active clamping all put the FET in linear mode. Not Rds(on) or Id_max.

> WARNING: Spirito effect (electro-thermal instability) causes localized hotspot runaway in MOSFETs in linear mode at high Tj. Modern trench FETs have worse linear-mode SOA than older planar. For hot-swap/active clamp: select parts with guaranteed SOA at 125C (not 25C). Infineon OptiMOS linear FETs and IXYS linear-mode parts are designed for this.

**Recommended MOSFETs:**

| Application | Part | Key Specs |
|-------------|------|-----------|
| 5V N-ch load switch | CSD17571Q2 | 30V, 2.6mohm@4.5V, Qg 3.1nC, SON-2x2 |
| 12V N-ch switching | BSC019N04LS | 40V, 1.9mohm@4.5V, Qg 41nC, TDSON-8 |
| 12V P-ch load switch | DMP2035U | -20V, 30mohm@Vgs=-2.5V, SOT-23 |
| Linear mode / hot-swap | IPD90P03P4L-04 | -30V P-ch, guaranteed SOA at 175C |
| High-side P-ch <2A | Si2301CDS | -20V, 110mohm, SOT-23 |

- Reverse polarity MOSFET selection -> `protection/reverse-polarity.md`. Thermal design -> `guides/thermal.md`.

### Gate Drive

- **Gate resistor sizing: Rg = (Vdrive - Vplateau) / Ig_peak.** Start with 10 ohm. Too low -> EMI from fast dV/dt, ringing from gate loop inductance. Too high -> slow switching, high loss.
- **Separate turn-on and turn-off resistors.** Diode in parallel with Rg_on bypasses during turn-off. Faster turn-off reduces body diode conduction in half-bridge dead time. This is the standard gate drive network for hard-switching half-bridges.
- **Gate loop inductance: every 1nH causes ~1V gate overshoot at fast di/dt.** Keep gate driver, Rg, and FET gate pin in <5mm loop. Route on same layer, no vias in gate path.
- **Miller plateau determines dV/dt.** dV/dt = Ig / Cgd. Cgd (Crss) varies 5-10x with VDS -- use value at operating VDS, not 0V.
- **QGD/QGS ratio matters for half-bridge.** QGD/QGS of 0.5-0.8 and QGD/QGS(TH) < 1.0 recommended for hard switching. Higher ratios increase dVDS/dt-induced turn-on risk (shoot-through).
- **Bootstrap cap >= 10x Qg of high-side FET.** Fast recovery diode (<50ns trr), low Vf. Minimum low-side on-time to recharge cap limits max duty cycle to ~99%. For 100% duty cycle or always-on high-side: use charge pump (LTC4440, LM5109).

**Recommended gate drivers:**

| Application | Part | Key Specs |
|-------------|------|-----------|
| Single low-side | UCC27511A | 4A peak, 4.5-35V, SOT-23-5 |
| Half-bridge integrated | UCC21520 | 4A/6A, isolated, SOIC-16 |
| Low-voltage half-bridge | MIC4606 | 1A, 5.5-16V, bootstrap, TSSOP-10 |
| Configurable 3-phase | MOTIX 6EDL7141 | 10mA-1.5A prog, SPI config, charge pump for 100% duty |

### Load Switches

- **Integrated load switches below 5A:** TPS22916 (5.5V, 2A, 24mohm, SOT-23-5) -- controlled rise time via CT pin, <1uA off-state, quick output discharge. RT9742 (5.5V, 2A, 22mohm) similar, lower cost.
- **Discrete P-ch load switch:** source to supply, drain to load. Gate pull-up to source via 100K (off by default). Drive gate low through N-ch level shifter (BSS138) when supply > MCU VDD. Add 10-15V Zener gate-to-source clamp when Vin > Vgs(max).
- **Discrete N-ch high-side: requires charge pump or bootstrap.** Better Rds(on) than P-ch but more complex. Prefer integrated (TPS22916 family) unless current > 5A.
- **Inrush current limiting: target 1-10ms rise time for capacitive loads.** Integrated switches use CT pin (external cap sets dV/dt). Discrete: series gate resistor + gate capacitor sets RC ramp.

> WARNING: Hot-plugging into discharged capacitive load puts FET in linear mode (full VDS, rising ID). A 100uF cap at 5V: 5V * 0.5A = 2.5W instantaneous. At 10,000uF on 12V, peak power reaches hundreds of watts for milliseconds. Check SOA at actual hot-plug pulse duration.

- **Reverse current blocking:** most integrated load switches block reverse current by design. Discrete P-ch does NOT -- body diode conducts. Back-to-back FETs needed -> `power/power-path.md`.

### Inductive Load Driving (Relays, Solenoids)

- **Schottky diode across coil: simplest but slowest release.** Clamps flyback to ~0.3V above rail. Relay stays energized 5-50x longer than unclamped. SS14 (1A/40V SMA) or B5819W (1A/40V SOD-123) for coils up to 1A.
- **Zener + Schottky in series: fast release with controlled clamp.** Zener voltage <= (VDS_max - Vcoil) / 2 for margin. 12V relay with 30V FET: 12V Zener clamps at 12.3V, VDS peak = 24.3V. Release drops from ~50ms to ~2ms.
- **TVS across FET (drain-to-source): best for high-energy solenoids.** Bidirectional TVS, Vbr > Vcoil, Vc < VDS_max. Verify single-pulse energy rating (Eppk) >= 0.5*L*I^2.
- **RC snubber across coil for EMC.** R = sqrt(L/C_parasitic), C = 10x C_parasitic. Typical: 100 ohm + 10nF for small relays. Use with diode clamp.
- **ULN2003A / ULN2803A for multiple low-current coils.** 7/8 Darlington drivers, 50V/500mA per channel, integrated clamp diodes to COM pin (connect to V+). Vce(sat) ~1V at 300mA. Use MOSFET for >500mA or when 1V drop matters (5V relay on 5V supply).
- **Coil suppression tradeoff: release speed vs contact life.** Faster flyback decay = more arc at contacts = better self-cleaning but more erosion. Slower = less arcing but risk of contact welding. Signal relays: fast clamp. Power relays: balance.

### TEC/Peltier Driver Circuits

- **DC drive is significantly more efficient than PWM.** TI measured 39% less input power for equivalent cooling at one operating point (1A avg, 50% duty, 20 kHz). PWM I^2*R losses from RMS current exceeding DC equivalent. Five months continuous testing showed no aging difference between PWM and DC drive.
- **H-bridge for heating AND cooling.** DRV8871 (single-chip, 3.6A, PWM input) or discrete bridge with gate drivers. Buck-boost alternative (TPS63020): TEC between input and output, single inductor, polarity set by output voltage relative to input.
- **Current control, not voltage control.** TEC resistance varies with temperature (positive tempco). Voltage drive causes current runaway. Delta T remains constant across temperature range with current drive but not voltage drive.
- **Operate at 50-70% of Imax for best COP.** Exceeding Imax causes Joule heating > Peltier cooling -- TEC gets hotter, not colder.
- **PWM frequency if used: >10 kHz minimum.** Below 10 kHz, thermal cycling fatigues TEC solder joints. LC filter on PWM output converts to quasi-DC -- preferred over raw PWM. For laser diode / photodiode TECs: use DC only -- even kHz-range current ripple can frequency-modulate the laser.
- **Thermal runaway protection mandatory.** NTC on hot side, firmware shutdown. Without protection, heatsink failure + TEC = fire risk.
- **PID compensation: TEC module is ~two-pole system (20mHz + 1Hz).** Integrator zero at 70mHz, derivative zero at crossover/5 for phase margin. Loop crossover at ~2Hz. Use ultra-low-leakage op-amp for integrator (MAX4475, 150pA max). C0G or polystyrene for integrator cap -- no electrolytic or tantalum (leakage causes gain errors).

**Recommended TEC driver ICs:**

| IC | Topology | Max Current | Key Feature |
|----|----------|-------------|-------------|
| DRV8871 | H-bridge | 3.6A | PWM input, current limiting, HTSSOP-16 |
| MAX1968 | PWM H-bridge | 3A | Integrated 4 switches, analog control, TSSOP-EP-28 |
| ADN8834 | Half-linear H-bridge | 1.5A | Single inductor, ultracompact |
| LTC1923 | PWM H-bridge | External FETs | Full TEC controller, SSOP-24 |

### Paralleling MOSFETs

- **Positive Rds(on) tempco self-balances DC current.** Hotter FET -> higher Rds(on) -> less current. Inherent to Si MOSFETs, makes DC paralleling straightforward.
- **Dynamic current sharing requires matched Vgs(th).** FET with lower Vgs(th) turns on first, carries transient overcurrent. Use same part from same lot. Typical lot spread: +/-100mV.
- **Individual gate resistors: 1-10 ohm per FET.** Prevents parasitic oscillation at 50-200MHz from gate loop coupling. Without them, parallel FETs oscillate.
- **Kelvin source connection for gate drive.** Separate source sense trace from each FET source pad to driver ground. Common source inductance (even 1nH) causes negative feedback that slows switching and current imbalance during transitions.

## Common Mistakes

- **Ignoring Miller plateau in thermal calculation.** Switching loss occurs primarily during Miller plateau. P_sw = 0.5 * Vds * Id * (t_rise + t_fall) * f_sw. At 100kHz with 50ns transitions: switching loss can exceed conduction loss. Omitting this underestimates total dissipation by 30-50%.
- **Zener clamp voltage selected without checking hot VDS margin.** At 125C, Zener voltage rises ~5-8% (positive tempco). A 12V Zener at 125C clamps at ~12.9V, pushing VDS_peak from 24.3V to 25.2V. On a 30V FET derated to 80% at temperature, max VDS = 24V -- now exceeded. Select Zener for hot conditions: V_zener(125C) + V_coil + margin < VDS_max.
- **SOA derating at temperature.** Linear derating: IDS(TC) = IDS(25C) * (TJ_max - TC) / (TJ_max - 25C). At 100C case with 150C TJ_max: only 40% of 25C SOA current. Designers often use 25C SOA at elevated temperature -- guaranteed failure in hot-swap.
- **Bootstrap cap too small.** Must supply Qg plus driver quiescent current for entire high-side on-time. If Cboot < 10x Qg, gate voltage droops -> Rds(on) increases -> FET overheats. At 100% duty cycle, bootstrap cannot recharge -- use charge pump.
- **Driving gate from open-drain without adequate pull-up.** Slow pull-up means slow dV/dt, extended time in linear region, high switching loss. Size pull-up for Ig = (Vdrive - Vplateau) / Rpullup >= Qg / t_sw_target. Or use totem-pole gate driver.

## Formulas

**Rds(on) at temperature:**
**Rule of thumb:** Rds(on) at 125C ~ 1.5x the 25C value. At 150C ~ 1.65x.
**Formula:** Rds(on)(Tj) = Rds(on)_25C * 1.004^(Tj - 25)
**Example:** 10mohm at 25C, Tj=125C -> 10m * 1.004^100 = 10m * 1.49 = 14.9mohm

**MOSFET switching loss:**
**Rule of thumb:** At f_sw > 100kHz, switching loss often exceeds conduction loss.
**Formula:** P_sw = 0.5 * Vds * Id * (t_rise + t_fall) * f_sw
  - t_rise ~ Qgd / Ig_on, t_fall ~ Qgd / Ig_off
**Example:** Vds=12V, Id=5A, Qgd=8nC, Ig=0.5A -> t_rise=16ns, P_sw = 0.5 * 12 * 5 * 32e-9 * 500e3 = 0.48W

**Inductive clamp Zener voltage:**
**Rule of thumb:** V_zener = (VDS_max - Vcoil) / 2 for 50% margin.
**Formula:** VDS_peak = Vcoil + V_zener + V_schottky. Select V_zener <= VDS_max - Vcoil - V_margin.
**Example:** 12V relay, 30V FET, 6V margin -> V_zener <= 30 - 12 - 6 = 12V. VDS_peak = 12 + 12.3 = 24.3V.

**SOA temperature derating:**
**Rule of thumb:** At TC = 100C with TJ_max = 150C, SOA current drops to 40% of 25C value.
**Formula:** IDS(TC) = IDS(25C) * (TJ_max - TC) / (TJ_max - 25C)
**Example:** IDS(25C) = 7.3A at 12V/10ms, TC = 100C, TJ_max = 150C -> IDS = 7.3 * (150-100)/(150-25) = 2.9A

## Sources

### Related Rules

- `protection/reverse-polarity.md` -- Reverse polarity MOSFET selection
- `guides/thermal.md` -- Thermal design for power MOSFETs
- `power/power-path.md` -- Back-to-back FETs for reverse current blocking

### References

1. Infineon AN_2112 -- Designing with Power MOSFETs: https://www.infineon.com/assets/row/public/documents/24/42/infineon-designing-with-power-mosfets-applicationnotes-en.pdf
2. Infineon -- OptiMOS Datasheet Explanation: https://www.infineon.com/assets/row/public/documents/24/42/infineon-mosfet-optimos-datasheet-explanation-an-en.pdf
3. onsemi AND9093 -- Using MOSFETs in Load Switch Applications: https://www.onsemi.com/pub/collateral/and9093-d.pdf
4. Infineon AN_2203 -- Gate Drive for Power MOSFETs: https://www.infineon.com/dgdl/Infineon-Gate_drive_for_power_MOSFETs_in_switchtin_applications-ApplicationNotes-v01_00-EN.pdf?fileId=8ac78c8c80027ecd0180467c871b3622
5. TI SLUAAO2 -- Using MOSFET SOA Curves in Your Design: https://www.ti.com/lit/an/sluaao2/sluaao2.pdf
6. onsemi AND90146 -- MOSFET Selection for Reverse Polarity Protection: https://www.onsemi.com/download/application-notes/pdf/and90146-d.pdf
7. TI SLVA652A -- Basics of Load Switches: https://www.ti.com/lit/an/slva652a/slva652a.pdf
8. ADI -- Switching Inductive Loads with Safe Demagnetization: https://www.analog.com/en/resources/technical-articles/switching-inductive-loads-with-safe-demagnetization.html
9. ADI HFAN-08.2.0 -- How to Control and Compensate a TEC: https://www.analog.com/en/resources/technical-articles/hfan0820-how-to-control-and-compensate-a-thermoelectric-cooler-tec.html
10. TI SLUA202A -- Closed Loop Temperature Regulation Using UC3638 H-Bridge: https://www.ti.com/lit/an/slua202a/slua202a.pdf
11. TI SLUA979A -- Driving a Peltier Element (TEC): Efficiency and Aging: https://www.ti.com/lit/an/slua979a/slua979a.pdf
12. EDN -- Low-Cost Driver for Thermoelectric Coolers (TECs): https://www.edn.com/low-cost-driver-for-thermoelectric-coolers-tecs/
