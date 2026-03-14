# Reverse Polarity Protection

> Topology selection, MOSFET sizing, and controller choice for input reverse voltage blocking.

## Quick Reference

- **Topology by current:** Series Schottky < 3A. P-FET self-bias 1-5A. N-FET + ideal diode controller > 5A. eFuse when OCP/OVP also needed.
- **MOSFET VDS: 40V for 12V systems, 60V for 24V.** Covers ISO 7637 transients.
- **RDS(ON) derates 1.85 * at 175C.** Always calculate P_loss = I^2 * RDS(ON) * K_temp at max TJ.
- **Body diode conducts at startup.** At 10A: 7W. Gate must activate in milliseconds or TJ exceeds abs max.
- **N-FET is ~1/3 die area of P-FET for same RDS(ON).** Lower cost, but requires charge pump or controller.

## Design Rules

### Topology Selection

| Topology | Forward Drop | Current Range | Key Limitation |
|----------|-------------|---------------|----------------|
| Series Schottky / SBR | 0.3-0.5V | < 3A | Leakage doubles per 10C; thermal runaway above 85C ambient |
| P-FET self-bias | I^2 * RDS(ON) | 1-5A | No reverse current blocking; ~2-3x die area vs N-FET |
| N-FET + controller | 20-30mV regulated | 5-50A+ | Requires controller IC + charge pump cap |
| eFuse (TPS25942, TPS2660) | I^2 * RDS(ON) | 0.6-15A | IC cost; limited voltage range per family |

- **Schottky thermal runaway:** leakage doubles every 10C. At 85C+, self-heating can exceed dissipation capacity. Super Barrier Rectifiers (Diodes Inc SBRT series) reduce power loss ~20% vs Schottky at same current, lower leakage at temp, but same fundamental thermal runaway mechanism. Use MOSFET above 85C ambient or above 3A.
- **eFuse integrates OCP/OVP/inrush/reverse in one IC.** TPS25942: programmable inrush via dV/dT cap, fast-trip < 200ns at 1.6x I_LIM, +/-8% current limit accuracy, 0.6-5.3A range. TPS2660: +/-70V transient abs max, 20V/us slew rate tolerance, reverse blocking in ~1us, suits 60V DC SELV industrial. Saves > 100mm^2 vs discrete.

> WARNING: Never use a diode-to-ground to clamp reverse polarity. It clamps to -0.7V (PN) or -0.3V (Schottky), exceeding -0.3V absolute max of most CMOS ICs. DC supply will drive sustained current through the clamp diode -- requires precise fuse/PTC sizing to avoid fire.

### P-FET Circuit

- **Source to battery+, drain to load.** Body diode blocks when input is reversed. No controller needed.
- **Gate pull-down: 100K to load-side ground.** VGS = -VIN -> fully ON. Logic-level VGS(th) < 2.5V required for 3.3-5V self-bias.
- **Zener clamp gate-to-source** when VIN > VGS(max) (typically 20V). 12-15V Zener, cathode to source, anode to gate. Series gate resistor 10-100 ohm limits dV/dt coupling through CGD.
- **Does NOT block reverse current.** Motor back-EMF or cap discharge flows through the enhanced channel back to input. Output caps discharge during input shorts. Bidirectional blocking requires back-to-back FETs -> `power/power-path.md`.
- **P-FET parts:** Si2301CDS (SOT-23, -20V, 3A, 110mohm) for < 2A. DMP2035U (SOT-23, -20V, 3.6A, 30mohm at 2.5V VGS) for 2-5A. DMP6023LFGQ (PowerDI3333, -60V, 25mohm) for higher current.

### N-FET + Ideal Diode Controller

- **Source to input, drain to load.** Controller drives gate above source via internal charge pump (~11.4V typical). Regulates VDS to 20-30mV forward drop.
- **Linear regulation** (LM74700-Q1, LTC4359): actively adjusts gate drive for constant forward drop -- better transient response, no oscillation at light loads. **Hysteretic** (LM74610-Q1): ON/OFF switching -- simpler but can oscillate.
- **Reverse blocking < 500ns.** Fast pull-down detects VDS < -10mV to -30mV and discharges gate. If controller loses power, body diode still conducts forward (fail-safe).
- **Reverse current blocking vs reverse polarity protection are different features.** P-FET self-bias provides reverse polarity protection only. Ideal diode controllers provide both -- critical for holdup capacitor applications where input shorts must not discharge output caps.

**Controller selection:**

| Controller | VIN Range | IQ | Reverse V Rating | Key Feature |
|-----------|-----------|-----|-----------------|-------------|
| LM74700-Q1 | 3.2-65V | 26uA | -65V | Lowest cost, automotive Q1, linear regulation |
| LTC4359 | 4-80V | 155uA | -40V | Cold-crank to 4V, /SHDN for load switch + 14uA sleep |
| LTC4357 | 9-80V | 650uA | -80V | 48V telecom/server ORing |
| NCV68061 | 3.3-40V | -- | -40V | onsemi, 11.4V gate drive, 140mV turn-on threshold |
| AP74700AQ | 3.5-40V | 35uA | -40V | LM74700 alternative (Diodes Inc), regulates to 20mV |

- **Charge pump cap: 100nF-1uF ceramic, rated >= VIN + 15V.** X5R/X7R, within 5mm of CBOOT/CP pin.
- **Cold-crank survival:** 12V automotive dips to 3-4V for seconds during cold start. LM74700-Q1 operates down to 3.2V. LTC4359 to 4V. Verify controller min VIN vs cold-crank profile.
- **Back-to-back FETs for load switch + RVP:** LTC4359 /SHDN drives two N-FETs -- Q2 blocks forward, Q1 blocks reverse. Body diodes oppose -> full bidirectional blocking. Inrush limited via gate capacitor slew control.
- **Extended reverse (ISO 7637 Pulse 1: -150V at 12V, -600V at 24V):** pulse-rated resistor in anode path + avalanche-rated TVS. LTC4359 protects to -40V; for higher, add R2 in anode path to extend to -100V.
- **ORing multiple supplies:** 20-30mV forward drop instead of Schottky 400-500mV. Each controller independently isolates failed supply in < 500ns. Full ORing -> `power/power-path.md`.

### Automotive Transients (ISO 7637-2)

- **Pulse 1 (reverse):** -150V at 12V, -600V at 24V. N-FET + controller blocks within ~0.75us.
- **Pulse 3b (switching noise):** +75V to +150V (12V) burst. VDS rating must exceed TVS-clamped level.
- **Load dump (Pulse 5b):** +80V for 400ms (12V) or +200V (24V). TVS clamping mandatory.
- **Avalanche-rated MOSFETs** (EAS specified) absorb single-pulse energy if TVS fails. Non-avalanche parts fail destructively. Select for avalanche if no external TVS.

### MOSFET Selection

- **VDS: 40V for 12V, 60V for 24V.** Never use 20V on 12V -- no transient headroom.
- **RDS(ON) target:** size so P_loss = I^2 * RDS(ON) * K_temp < 500mW at max TJ for standard packages.

**Temperature derating (typical Si MOSFET):**

| TJ (C) | K_temp (RDS(ON) multiplier) |
|---------|----------------------------|
| 25 | 1.0x |
| 85 | 1.3x |
| 125 | 1.5x |
| 175 | 1.85x |

- **Logic-level gate (VGS(th) < 2.5V) for P-FET self-bias** from 3.3-5V rails. Standard-level fine for N-FET with controller (11V charge pump).
- **QG drives turn-on speed.** At QG=50nC, I_gate=25mA: t_on=2us. During this time body diode carries full load at ~0.7V.
- **Package thermal resistance:** LFPAK33 (3x3mm) ~51C/W. SO-8FL (5x6mm) ~43C/W. LFPAK56 (5x6mm) ~43C/W. Use 5x6 packages above 8A. Exposed pads require thermal vias for rated RthJA.
- **dV/dt-induced turn-on:** fast VDS transients couple through CGD to gate. If induced VGS > VGS(th), FET momentarily conducts -- defeats protection. Fix: low-CGD FET, gate pull-down <= 10K, or active gate clamp.
- **Hot-plug SOA:** connecting to live supply puts FET in linear mode (full VDS while ramping ID). Check 1ms and 10ms SOA curves, not just DC ratings.

### PCB Layout

- **Place RVP FET at power entry, before bulk decoupling.** Copper pours for > 5A, not traces.
- **Controller within 10mm of FET gate.** Charge pump cap, gate resistor, controller in tight cluster.
- **Kelvin-sense connections:** anode/cathode sense pins direct to MOSFET drain/source pads. Route as differential pair, not through power copper upstream.
- Thermal vias, exposed pad -> `guides/thermal.md`. MOSFET gate drive -> `misc/mosfet-circuits.md`. Battery protection -> `power/battery.md`.

## Common Mistakes

- **P-FET body diode allows reverse current from motors/caps.** Single P-FET blocks reverse polarity but NOT reverse current. Output caps discharge through enhanced FET channel during input shorts -- system loses holdup time. Ideal diode controller senses -10mV VDS and disconnects in < 500ns.
- **Body diode startup thermal ignored.** At 10A through body diode: P = 0.7V * 10A = 7W. At RthJA = 43C/W: steady-state delta-TJ = 301C -- exceeds abs max within seconds. Nexperia measured 24.5A through N-FET body diode reaching TJ = 175C during 30s charge pump startup. Use low-QG FETs to minimize body diode conduction time.
- **Schottky thermal runaway in high-temp automotive.** Reverse leakage doubles every 10C. 60V Schottky at 150C: 100mA leakage = 6W dissipation at -60V. Self-heating accelerates leakage -> thermal runaway -> diode failure -> reverse current damages load.
- **dV/dt turn-on during ISO 7637 pulses.** >100V/us slew couples through CGD. If induced VGS > VGS(th), FET passes reverse voltage to load. Measure CGD/CGS ratio -- lower is better.
- **eFuse current limit set too low for inrush.** Motor startup, cap charging, hot-plug exceed steady-state. Set I_LIM >= 2x steady-state. Use eFuse inrush timer (dV/dT control) -- TPS25942 ramps output at programmed rate.
- **Forgetting reverse leakage in sleep mode.** 3.3V TVS at V_RWM: ~100nA typical. But low-voltage Schottky at 85C can leak > 1mA. Battery-powered systems: account for all leakage paths in power-down current budget.

## Formulas

**MOSFET conduction loss:**
**Rule of thumb:** Target < 500mW at max TJ for 3x3mm and 5x6mm packages.
**Formula:** P_loss = I_load^2 * RDS(ON) * K_temp
**Example:** 6A, 14mohm, TJ=175C -> P = 36 * 0.014 * 1.85 = 932mW. At RthJA=51C/W: delta-TJ=47.5C, max T_ambient = 175 - 47.5 = 127.5C.

**Body diode startup power:**
**Rule of thumb:** At > 5A, body diode startup dominates thermal design.
**Formula:** P_diode = V_F * I_load (V_F ~ 0.7V for body diode)
**Example:** 10A -> P = 7W. At RthJA=43C/W: delta-TJ = 301C in steady state. Gate must activate within milliseconds.

**Gate turn-on time:**
**Rule of thumb:** Lower QG = faster turn-on = shorter body diode stress.
**Formula:** t_on = QG / I_gate
**Example:** QG=50nC, I_gate=25mA -> t_on=2us. Body diode dissipates 7W for 2us at 10A -- negligible. But charge pump startup is milliseconds, not microseconds.

## Sources

### Related Rules

- `power/power-path.md` -- Bidirectional blocking with back-to-back FETs, supply ORing
- `guides/thermal.md` -- Thermal vias, exposed pad thermal management
- `misc/mosfet-circuits.md` -- MOSFET gate drive circuits and switching design
- `power/battery.md` -- Battery protection and charging circuits

### References

1. TI SLVAE57B -- Basics of Ideal Diodes: https://www.ti.com/lit/pdf/slvae57
2. ADI -- Low IQ Ideal Diode Controller (LTC4357/LTC4359): https://www.analog.com/en/resources/technical-articles/low-iq-ideal-diode-controller-with-reverse-input-protection.html
3. EDN -- Protecting Against Reverse Polarity (Part 1): https://www.edn.com/protecting-against-reverse-polarity-methods-examined-part-1/
4. EDN -- Protecting Against Reverse Polarity (Part 2): https://www.edn.com/protecting-against-reverse-polarity-methods-examined-part-2/
5. onsemi AND90146 -- MOSFET Selection for RVP: https://www.onsemi.com/download/application-notes/pdf/and90146-d.pdf
6. Diodes Inc AN1192 -- Understanding RVP Approaches: https://www.diodes.com/assets/App-Note-Files/AN1192_App-Note_Automotive-RVP.pdf?v=9
7. TI SLVA862A -- Basics of eFuses: https://www.ti.com/lit/pdf/slva862
8. Nexperia AN50001 -- Reverse Battery Protection: https://assets.nexperia.com/documents/application-note/AN50001.pdf
