# Reverse Polarity Protection

> Topology selection, MOSFET sizing, and controller choice for input reverse voltage blocking.

## Quick Reference

- **Topology by current (examples, not hard limits):** AN50001 uses Schottky near 3A, P-FET near 5.7A, and N-FET near 25A; select by forward loss and thermal limits. Use an eFuse with explicit reverse-input protection when OCP/OVP is also needed [6, Table 1; 5, §3.8].
- **40V for 12V and 60V for 24V are onsemi's preferred MOSFET starting ratings, not ISO 7637 immunity.** Verify worst-case clamped input-to-output voltage, including a charged output during a negative input pulse [3, p.4; 7, pp.17-19].
- **RDS(ON) temperature multiplier is part-specific.** onsemi uses 1.85 at 175 degrees C for NVTFS5C478NLWFTAG; calculate loss using the chosen FET's curve [3, p.10].
- **Body diode conducts at startup.** Check the controller's charge-pump startup and the FET's transient thermal impedance; there is no universal millisecond survival limit [6, §5; 7, p.13].
- **N-FET is ~1/3 die area of P-FET for same RDS(ON).** Lower cost, but requires charge pump or controller [4, p.5].

## Design Rules

### Topology Selection

| Topology | Forward Drop | Current Range | Key Limitation |
|----------|-------------|---------------|----------------|
| Series Schottky / SBR | Device-specific V_F | ~3A example | Reverse leakage rises at high junction temperature [6, §3]. |
| P-FET self-bias | I * RDS(ON) | ~5.7A example | No reverse current blocking [4, pp.4-5; 6, §4]. |
| N-FET + controller | 20-30mV while regulation is possible | FET/thermal limited | Fully enhanced drop becomes I * RDS(ON) [2; 4, p.4]. |
| eFuse | I * RDS(ON) | Device-specific | TPS2660 includes reverse-input protection; do not infer it from the eFuse label [5, §3.8]. |

- **Schottky thermal runaway depends on leakage, reverse voltage, and thermal resistance.** Diodes' 12V/10A example shows about 20% less dissipation for SBRT20U50SLPQ than the compared Schottky; this is not a universal 85 degrees C cutoff or 20% benefit [4, pp.2-3].
- **Check reverse-input protection separately from reverse-current blocking.** TPS25942 has +/-8% current-limit accuracy over 0.6-5.3A and <200ns fast trip at 1.6 * I_LIM in TI's example. TPS2660 explicitly integrates reverse-input protection and has +/-70V transient absolute maxima and 20V/us surge slew tolerance; absolute maxima are not operating limits [5, §3.3-3.4, §3.8-3.9].

> WARNING: A shunt diode/TVS plus fuse is a fuse-clearing protection circuit, not an indefinitely sustainable reverse-voltage clamp. Verify fuse clearing and diode pulse survival for the available fault current [5, §3.8, Figure 14(c)].

### P-FET Circuit

- **Drain to battery+, source to load for the high-side self-biased P-FET.** Its body diode conducts from input to load during startup and blocks reversed input when the gate is off [3, p.3, Figure 4].
- **Select P-FET RDS(ON) at the actual negative VGS available from the rail.** VGS(th) is specified at a small drain current and is not a fully-on gate voltage; DMP2035U specifies resistance at -1.8V, -2.5V, and -4.5V [9, p.2].
- **Clamp gate-to-source when the rail can exceed the selected FET's VGS rating.** Cathode to source, anode to gate; size the gate-to-ground resistor to limit sustained Zener current while maintaining the required gate drive. DMP2035U has only +/-10V VGS maximum, not the common +/-20V rating [3, pp.2-3; 9, p.2].
- **Does NOT block reverse current.** Motor back-EMF or cap discharge flows through the enhanced channel back to input. Output caps discharge during input shorts. Bidirectional blocking requires back-to-back FETs -> `power/power-path.md` [4, p.4].
- **P-FET parts:** DMP2035U (SOT23, -20V) has 30mohm typical / 45mohm maximum at VGS=-2.5V, ID=-4A, 25 degrees C; its headline current rating is not a board-level 5A guarantee. DMP6023LFGQ (PowerDI3333-8, -60V) specifies 25mohm maximum at VGS=-10V, ID=-5A, 25 degrees C [9, p.2; 10, pp.1-2].

### N-FET + Ideal Diode Controller

- **Source to input, drain to load.** LTC4359 regulates forward drop to 30mV while sufficient gate-drive headroom remains; NCV68061 provides 11.4V typical gate-to-source drive. These values are controller-specific [2; 3, p.4].
- **Linear regulation** (LM74700-Q1, LTC4359): actively adjusts gate drive for constant forward drop, minimizing reverse current. Light-to-heavy load steps still need fast gate charging to avoid output droop. **Hysteretic** (LM74610-Q1): ON/OFF switching -- check its charge-pump cycling behavior [1, §6.1, §6.5; 2].
- **Reverse blocking time depends on the controller and gate charge.** LTC4359 responds to more than 30mV reverse drop with <500ns gate pull-down in ADI's example; LM74700-Q1 has 0.75us maximum comparator delay plus FET discharge time [2; 1, §6.3].
- **Reverse current blocking vs reverse polarity protection are different features.** P-FET self-bias provides reverse polarity protection only. LTC4359 provides both; LTC4357 needs additional reverse-input protection components [2; 8, pp.2, 10].

**Controller selection:**

| Controller | VIN / IQ | Reverse-input capability | Condition |
|-----------|----------|--------------------------|-----------|
| LM74700-Q1 | 4-60V in electrical table; 80uA typical | -65V headline rating | Datasheet headline is 3.2-65V with 3.9V startup; check electrical limits for the use case [7, §1, §6.5]. |
| LTC4359 | 4-80V; 155uA typical | -40V with reference protection circuit | /SHDN: 14uA typical; single FET body diode still conducts forward [2]. |
| LTC4357 | 9-80V; 650uA typical | Not inherently -80V tolerant | IN absolute minimum is -1V; add the datasheet's reverse-input circuit [2; 8, pp.1-3, 10]. |
| NCV68061 | See device datasheet | Mode-dependent | Drain tied to load gives ideal-diode mode; drain tied to ground gives RVP-only mode [3, pp.4-5]. |
| AP74700AQ | 3.2-65V; 80uA typical | -65V | 3.9V startup; 20mV regulation [11, p.1]. |

- **Charge pump capacitor is controller-specific.** LM74700-Q1 uses at least 100nF between VCAP and ANODE, not to ground. Size its voltage rating for that differential and its capacitance for gate charge/startup; do not apply a universal VIN + 15V rating or assume LTC4359 needs the same external capacitor [7, §6.3, p.13; 2].
- **Cold-crank survival requires both operating and startup limits.** LM74700-Q1 advertises 3.2V operation but 3.9V startup; a rail that dips while already running is different from powering up into the dip. LTC4359 operates from 4V [7, §1; 2].
- **Back-to-back FETs for load switch + RVP:** LTC4359 /SHDN drives two N-FETs -- Q2 blocks forward, Q1 blocks reverse. Body diodes oppose -> full bidirectional blocking. Inrush limited via gate capacitor slew control [2, Figure 5].
- **Extended reverse input protection:** ADI's LTC4359 Figure 7 adds R2 to extend VIN-VOUT protection to -100VDC, with a 10mV reduction in forward regulation, a 250V FET, and pulse-rated components. This is a complete reference circuit, not just a resistor added to any -40V design [2, Figure 7].
- **ORing multiple supplies:** LTC4359's 30mV regulation applies while the FET has sufficient gate-drive margin; its forward drop rises with I * RDS(ON) once fully enhanced. Full ORing -> `power/power-path.md` [2].

### Automotive Transients (ISO 7637-2)

- **Pulse 1 example:** TI describes -150V with 10-ohm generator impedance for 2ms on a 12V system, and -600V with 50 ohm for 1ms on a 24V system. Controller/FET survival requires the specified TVS clamping, not the raw pulse voltage across a 40V/60V FET [1, §7.3].
- **Pulse 3b (switching noise):** +75V to +150V (12V) burst. VDS must withstand input-to-output stress after TVS clamping, including held-up output voltage [3, p.1; 7, pp.17-19].
- **Load dump is a separate energy requirement.** Use the specified suppressed/unsuppressed load-dump profile and the controller reference design's TVS or active clamp; a reverse-blocking rating alone does not establish survival [1, §6.6].
- **Avalanche rating is not a substitute for a TVS-failure analysis.** ADI's LTC4359 design selects a FET for its avalanche current and energy; its extended-range circuit adds a TVS when reverse current can exceed that rating [2, Figures 4, 7].

### MOSFET Selection

- **VDS must exceed the worst differential across the off FET.** A held-up output adds to the magnitude of a negative input transient; onsemi's 40V/60V starting choices still require a coordinated clamp [3, p.4; 7, pp.17-19].
- **RDS(ON) target is thermal-design dependent.** onsemi's tested 6-10A parts dissipate 706-933mW at 175 degrees C, so 500mW is not a universal package limit [3, p.10, Table 5].
- **Use the resistance guaranteed at the available gate drive.** onsemi evaluates NCV68061-driven FETs at VGS=10V because its gate drive is 11.4V typical; use a low-voltage RDS(ON) specification for self-biased low-voltage P-FETs [3, p.4; 9, p.2].
- **QG alone does not determine startup time.** Include the controller's charge-pump undervoltage delay before gate charging starts [7, p.13].
- **Thermal resistance belongs to a device and board, not just a package.** onsemi's optimized four-layer test uses 51 degrees C/W for NVTFS5C478NLWFTAG (3.3mm * 3.3mm micro8FL) and 43 degrees C/W for NVMFS5C468NLAFT1G (5mm * 6mm SO-8FL), not generic LFPAK33/LFPAK56 values [3, pp.8-10, Tables 4-5].
- **Hot-plug/inrush SOA:** an LTC4359 back-to-back load switch controls slew through the gate capacitor; verify the selected FET's SOA for that actual ramp and load, not just its DC current rating [2, Figure 5].

### PCB Layout

- **Place RVP FET before the bulk hold-up capacitor.** In ideal-diode mode the output capacitor must remain on the protected side; otherwise input faults discharge it [3, p.4, Figure 6].
- **Kelvin-sense connections:** connect ANODE/CATHODE sense paths directly to the FET terminals; a shared high-current trace drop corrupts millivolt forward/reverse detection [7, p.23].
- Thermal vias, exposed pad -> `guides/thermal.md`. MOSFET gate drive -> `misc/mosfet-circuits.md`. Battery protection -> `power/battery.md`.

## Common Mistakes

- **P-FET reverse conduction is through the enhanced channel.** A single self-biased P-FET stays on during a positive-polarity output-to-input backfeed condition; the body diode is not the reverse-current mechanism [4, p.4].
- **Reading AN50001's startup plot as a measured charge-pump delay.** Nexperia deliberately delayed enhancement by 30s in a 24.5A electrothermal simulation; the body diode dissipated about 15W and TJ reached about 175 degrees C. This is not an actual controller's startup timing [6, §5].
- **Setting eFuse I_LIM to twice steady current without an inrush calculation.** TPS25942 uses a dV/dT capacitor to control startup current; size the ramp for load capacitance and available current instead of a universal multiplier [5, §3.2-3.4].

## Formulas

**MOSFET conduction loss at temperature [3, p.10]:**
**Rule of thumb:** Use the selected FET's RDS(ON)-versus-temperature curve and board-specific thermal resistance.
**Formula:** P_loss = I_load^2 * RDS(ON,25 degrees C) * K_temp
**Example:** onsemi NVTFS5C478NLWFTAG at VGS=10V: 6A, 14mohm at 25 degrees C, K_temp=1.85 at 175 degrees C -> P = 36 * 0.014 * 1.85 = 932.4mW. With the example board's 51 degrees C/W, delta-TJ=47.55 degrees C and maximum ambient about 127.45 degrees C. This is a calculation at the junction limit, not a recommended operating margin.

## Sources

### Related Rules

- `power/power-path.md` -- Bidirectional blocking with back-to-back FETs, supply ORing
- `guides/thermal.md` -- Thermal vias, exposed pad thermal management
- `misc/mosfet-circuits.md` -- MOSFET gate drive circuits and switching design
- `power/battery.md` -- Battery protection and charging circuits

### References

1. TI SLVAE57B (October 2021) -- Basics of Ideal Diodes: https://www.ti.com/lit/pdf/slvae57
2. ADI -- Low IQ Ideal Diode Controller (LTC4357/LTC4359): https://www.analog.com/en/resources/technical-articles/low-iq-ideal-diode-controller-with-reverse-input-protection.html
3. onsemi AND90146/D (Rev 1, July 2023) -- MOSFET Selection for RVP: https://www.onsemi.com/download/application-notes/pdf/and90146-d.pdf
4. Diodes Inc AN1192 (Rev 1, February 2025) -- Understanding RVP Approaches: https://www.diodes.com/assets/App-Note-Files/AN1192_App-Note_Automotive-RVP.pdf?v=9
5. TI SLVA862A -- Basics of eFuses: https://www.ti.com/lit/pdf/slva862
6. Nexperia AN50001 (Rev 1.0, January 2021) -- Reverse Battery Protection: https://assets.nexperia.com/documents/application-note/AN50001.pdf
7. TI LM74700-Q1 datasheet (SNOSD17G, December 2020): https://www.ti.com/lit/gpn/lm74700-q1
8. ADI LTC4357 datasheet (Rev D, September 2010): https://www.analog.com/media/en/technical-documentation/data-sheets/4357fd.pdf
9. Diodes Inc DMP2035U datasheet (DS31830 Rev 11-2, June 2025): https://www.diodes.com/assets/Datasheets/DMP2035U.pdf
10. Diodes Inc DMP6023LFGQ datasheet (DS38647 Rev 5-2, September 2026): https://www.diodes.com/assets/Datasheets/DMP6023LFGQ.pdf
11. Diodes Inc AP74700AQ datasheet (DS46953 Rev 3-2): https://www.diodes.com/assets/Datasheets/AP74700AQ.pdf
