# Battery Charging, Protection, and Monitoring

> CC/CV charging, NTC monitoring, protection ICs, charger IC selection, fuel gauge, and multi-cell BMS. Chemistry selection -> `power/battery-chemistry.md`. Power path, ship mode, DPM/DPPM -> `power/power-path.md`.

## Quick Reference

- **CC/CV: charge at 0.5-1C to 4.20V +/-1%, terminate at 0.07-0.1C.** 65% of charge in CC phase. ~165 min total.
- **Charge temperature: 0-45C.** Below 0C causes permanent lithium plating -- no safe charge rate. Even brief charging at -5C causes measurable plating.
- **Voltage accuracy: +/-1% (= +/-42mV on 4.2V).** Undercharge by 42mV (~1%) loses ~8-10% capacity. Overcharge above 4.30V = plating, gas, CID rupture.
- **Protection: DW01 + 8205A standard single-cell.** Overdischarge 2.5V, overcurrent via Rds_on sensing. No safety timer.
- **Fuel gauge: voltage correlation ~20% error, coulomb counting ~6%, Impedance Track ~1%.**

## Design Rules

### CC/CV Charging

- **Three stages:** (1) preconditioning at 0.1C below ~2.8V with ~1hr safety timer, (2) fast charge CC at 0.5-1C, (3) CV at 4.2V +/-1%.
- **Termination: current < 0.07-0.1C AND safety timer.** Both required. Never rely on current alone. Recommended: continue charging 30 min after end-of-charge signal, then shutdown. No trickle charge for Li-ion -- causes lithium plating.
- **0.5C vs 1C: 36% longer charge, ~2% more capacity, reduced thermal stress.** MCP73841 at 0.5C: termination current scales to 0.035C, increasing final capacity from ~98% to ~100%. Free longevity win when charge time is not critical.
- **After termination, OCV settles to 3.70-3.90V** (not 4.20V). 4.20V is surface voltage under charge. Relaxation drops 300-500mV. Chargers in standby mode may recharge at 4.00V to 4.05V instead of full 4.20V -- reduces voltage stress and prolongs life.
- **Chemistry-specific voltages:** LFP 3.65V, LTO 2.85V. Charger ICs NOT interchangeable between chemistries. A 3.6V Li-ion in LFP charger gets insufficient charge; LFP in standard charger gets overcharged.
- **Parasitic load distorts CV termination.** Device load prevents current from dropping below threshold. Charger thinks battery is not full and continues charging. Use DPM/DPPM or charge with device off -> `power/power-path.md`.
- **Reverse leakage when input absent: must be < 1uA.** Even 1uA drains 8.8mAh/year. Flyback topology with rectifier diode naturally prevents backfeed; linear chargers need explicit blocking.

### NTC Temperature Monitoring

- **Standard: 10kohm NTC at 25C, beta ~3977-3982K.** 1% tolerance for accurate windows: Vishay NTCLE203E3103FB0 (B25/85 = 3977K +/-0.75%). 5% tolerance NTC gives +/-5C error on threshold boundaries.
- **SMD NTC beta varies by package and affects bias resistors:** 0805 (B~3570K), 0603 (B~3610K), 0402 (B~3490K). Each package needs different R_T1/R_T2 values. Do not swap packages without recalculating.
- **NTC must have close thermal contact with cell.** Remote placement makes all threshold tolerance calculations meaningless.
- **Bias resistor calculation (Microchip AN947, 0-45C window with 10kohm/B3982 NTC):**
  - R_COLD(0C) = 33.56kohm, R_HOT(45C) = 4.52kohm
  - R_T1 = (2 * R_COLD * R_HOT) / (R_COLD - R_HOT) = 10.44kohm -> use 10.5kohm
  - R_T2 = (2 * R_COLD * R_HOT) / (R_COLD - 3 * R_HOT) = 15.17kohm -> use 15kohm
  - Window accuracy within 1C of target.

### Protection ICs

- **DW01 + 8205A: standard single-cell.** DW01 monitors voltage/current. 8205A is dual N-FET (charge + discharge). Low-side switching for cheaper, lower Rds_on.
- **No external sense resistor** -- uses FET Rds_on for overcurrent. 8205A trips at ~3A overcurrent. Short-circuit: trips at ~9A, 10-30ms response.
- **Higher current: Si6926ADQ (dual 4.1A, 20V, 33mohm at Vgs=3V)** as 8205A upgrade. Used in TI bq275xx reference designs.
- **Overdischarge: DW01 at 2.5V.** FS312 pin-compatible with 3.0V cutoff -- better for cell longevity. Below 0V: anode copper dissolves, permanent shunts form.
- **Over-voltage: 4.35V triggers charge FET disable.** ~50ms delay for noise rejection. Recovery requires opposing condition: under-voltage needs charger connected; over-voltage needs load.
- **Two 0.1uF ceramic caps in series across PACK+/PACK-.** If one shorts from ESD, circuit still operates. Copper trace to caps must be as short and wide as possible for effective ESD clamping.
- **DW01 + 8205A power-up behavior is nondeterministic.** 50/50 chance circuit powers up when battery inserted. Connecting charger or shorting OUT-/B- momentarily enables output. Annoying but normal.
- **Dies on reverse battery connection** (no recovery). Reverse polarity -> `protection/reverse-polarity.md`.

> WARNING: DW01 + 8205A have no safety timer. A failed cell stuck at 4.19V will charge indefinitely. Always pair with a charger IC that has its own safety timer (TP4056 also has NO safety timer -- use MCP73831 or add external timer).

### Charger IC Selection

- **Linear (TP4056, MCP73831): simple, < 10 components.** Practical limit ~1A. Efficiency = Vbat/Vin. Worst-case power: P = (Vin_max - Vbat_min) * I_charge.
  - **TP4056:** R_prog sets current (1.2kohm = 1A, 10kohm = 130mA). NO safety timer. PROG pin ADC-readable for charge current monitoring. CE pin can be lifted for MCU charge enable/disable. SOP-8 thermal limit ~1.2W -- at 5V/3.0V depleted battery: P = 2.0W (thermal foldback). Reverse cell connection kills IC and protection circuit permanently.
  - **MCP73831:** Internal safety timer. 4.20V +/-0.75% accuracy. Safer default choice.
  - **MCP73841:** External PMOS pass transistor. Programmable precharge/fast-charge/termination timers via cap. Sense resistor: 110mohm/1% for 1A (worst-case 2.48W in PMOS at 5.25V input, depleted battery).
- **Switching charger above 3-4A or tight thermal budget.** Buck charger: synchronous preferred for efficiency but needs reverse-current protection (battery can source current through low-side FET). Nonsynchronous simpler -- free-wheeling diode intrinsically blocks reverse current.
  - **USB-PD: BQ25895 (I2C, 5A, NVDC, VINDPM).**
  - **Bootstrap collapse in buck charger:** during CV taper, duty cycle approaches 100%, no low-side interval to recharge BOOT cap. Fix: IC with internal charge pump, PMOS high-side, or periodic recharge pulse (99.9x% duty cycle).
- **Adapter hot-plug:** cable inductance + input cap resonance -> >50% voltage overshoot. Size input capacitance to limit below converter absolute max. Adapter insertion/removal detection must not be affected by converter.

### Fuel Gauge / State-of-Charge

| Algorithm | Peak error | Key limitation |
|-----------|-----------|----------------|
| Voltage correlation | ~20% | Only works after long rest (OCV stabilization) |
| Voltage + IR correction | ~10% | Worse with aged cells (IR underestimated) and cold |
| Coulomb counting | ~6% | Needs full charge to initialize. 25C-to-0C = 51% capacity delta |
| CEDV | ~6% | 15-25% error on aged cells. Abrupt SoC drop at low temp/high discharge |
| Impedance Track (bq27xxx) | ~1% | Needs learning cycle |

- **Voltage correlation: MAX17048** (I2C, no sense resistor, ModelGauge). Adequate for low-current IoT with long sleep. Unreliable for LFP (flat discharge curve) -> `power/battery-chemistry.md`.
- **Impedance Track (bq27xxx):** takes OCV when dV/dt < 4uV/s. Needs >37% delta charge for Qmax update (90% for first cycle). Ra table updates during discharge. Plan one complete charge-discharge in production testing. Self-discharge compensated by periodic OCV readings -- maintains accuracy during long idle.
- **Coulomb counting temperature trap:** charged at 25C = 2250mAh capacity. Used at 0C = 1100mAh actual. Coulomb counter reports 51% more charge than available. Must recalibrate at operating temperature.
- **Sense resistor: 10mohm typical.** Temp coeff <= 100ppm/C (metal foil/strip). Tolerance 1% or better -- 5% resistor = 5% SoC error floor. Max sense voltage 125mV. Power: 10mohm at 3A = 90mW.
- **Kelvin connections critical.** Separate sense leads from high-current paths. Route as differential pair. Common-mode cap at IC pins. Single-point ground connection at sense resistor for low-current return.
- **Differential low-pass filter before sense inputs.** Even 5% component tolerance adequate because shunt cap (C6) reduces AC common-mode from mismatch. Without filter, differential amplifier may rectify RF and create DC offset error.

### Multi-Cell / BMS

- **Per-cell voltage monitoring mandatory.** Single pack voltage cannot detect imbalanced cells. 3-5S: BQ76920 (I2C, passive balancing, integrated AFE).
- **If ANY cell exceeds 4.2V, terminate immediately.** Never average cell voltages for termination decisions.
- **Passive balancing: adequate for 2S-4S** with well-matched cells. Simple, wastes energy as heat.
- **Active balancing: required above 4S** or high-capacity cells where passive balancing time is excessive. 85-95% transfer efficiency.
- **Cell matching at assembly:** within 20mAh and 5mohm IR for best pack life.

## Common Mistakes

- **Parasitic load prevents CV termination, charger runs indefinitely.** A 20mA system load on a direct-connection topology keeps charge current above the 70mA termination threshold (for a 1A charger at 0.07C). Battery floats at 4.20V under continuous charge for days. Accelerated calendar aging at 100% SoC + elevated temperature from charger dissipation degrades 15-20% capacity in months. Fix: use DPPM topology, charge with load disconnected, or set termination threshold above expected parasitic load.
- **Precharge timer too short/too long.** Standard 1-hour precharge timer adequate. If cell cannot reach 2.8V within timer, it is faulty -- do not extend timer. Extending timer risks damage to shorted or deeply degraded cells.
- **5% sense resistor with Impedance Track -> 5% SoC error floor.** Fix: 1% for coulomb counting, 0.5% for bq27xxx. Kelvin connections on sense resistor are equally critical -- current-carrying trace resistance adds to effective sense value.
- **Passive balancing resistors undersized for high-capacity cells.** A 68 ohm balancing resistor on a BQ76920 passes ~62mA at 4.2V. For 3Ah cells with 50mAh imbalance, balancing takes 48 minutes -- acceptable. For 10Ah cells with 200mAh imbalance, balancing takes 3.2 hours and the resistor dissipates 260mW continuously. On a 4S pack, that is 1W of heat on a small PCB area. Fix: size balancing resistors for worst-case imbalance at max cell capacity; above 5Ah cells, evaluate active balancing (BQ34Z100-G1 + external FETs) to avoid thermal issues.
- **Charging below 0C "because it seems to work."** Lithium plating is invisible -- cell passes capacity test immediately after but develops internal shorts weeks later. Plated lithium is mechanically fragile: vibration or thermal cycling causes dendrite contact with cathode. NTC threshold must hard-disable charging below 0C with no override path.
- **TP4056 PROG pin ADC reading misinterpreted as charge current.** PROG pin voltage is proportional to charge current only during CC phase. During CV phase, the pin voltage reflects the internal regulation loop state, not actual battery current. Engineers reading PROG via ADC report "battery is still drawing 800mA" when actual current has tapered to 100mA, leading to incorrect SoC estimates and premature load reconnection. Fix: PROG pin is only valid for current measurement during CC; during CV, use a series sense resistor or fuel gauge IC.

## Formulas

**NTC bias resistors (0-45C charge window):**
**Rule of thumb:** 10.5kohm + 15kohm for standard 10kohm/B3982 NTC.
**Formula:** R_T1 = (2 * R_COLD * R_HOT) / (R_COLD - R_HOT); R_T2 = (2 * R_COLD * R_HOT) / (R_COLD - 3*R_HOT)
**Example:** R_COLD(0C) = 33.56kohm, R_HOT(45C) = 4.52kohm -> R_T1 = 10.44kohm (use 10.5kohm), R_T2 = 15.17kohm (use 15kohm). Window accuracy within 1C.

**Linear charger thermal dissipation:**
**Rule of thumb:** At 5V USB, linear charger wastes ~1W per amp at 3.7V battery.
**Formula:** P = (Vin - Vbat) * I_charge
**Example:** Vin = 5.0V, Vbat = 3.0V (depleted), I = 1A -> P = 2.0W worst case. TP4056 SOP-8 limit ~1.2W. MCP73841 with external PMOS: 2.48W at 5.25V input (size PMOS thermal pad for this).

**Sense resistor power and voltage:**
**Rule of thumb:** 10mohm at 3A = 90mW, 30mV. Choose lowest value giving adequate ADC resolution.
**Formula:** P = I^2 * R_sense; V_sense = I * R_sense (must be < 125mV)
**Example:** 3A, 10mohm -> P = 90mW, V = 30mV. At 10A, 5mohm -> P = 500mW, V = 50mV.

## Sources

### Related Rules

- `power/battery-chemistry.md` -- Chemistry selection, voltage curves, cycle life, LFP flat discharge curve
- `power/power-path.md` -- DPM/DPPM topology, ship mode, parasitic load and CV termination
- `protection/reverse-polarity.md` -- Reverse battery connection protection

### References

1. Microchip AN947 -- Li-Ion Charging Fundamentals: https://ww1.microchip.com/downloads/en/AppNotes/00947a.pdf
2. Battery University BU-409 -- Charging Lithium-ion: https://www.batteryuniversity.com/article/bu-409-charging-lithium-ion/
3. Battery University BU-410 -- Charging at High and Low Temperatures: https://www.batteryuniversity.com/article/bu-410-charging-at-high-and-low-temperatures/
4. Hackaday -- Lithium-Ion Battery Circuitry Is Simple: https://hackaday.com/2022/10/10/lithium-ion-battery-circuitry-is-simple/
5. ADI -- Practical Design Techniques: Battery Chargers: https://www.analog.com/media/en/training-seminars/design-handbooks/Practical-Design-Techniques-Power-Thermal/Section5.pdf
6. Vishay -- Fast Charging Control with NTC Temperature Sensing: https://www.vishay.com/docs/29089/fastappl.pdf
7. TI SLYP089 -- Design Trade-offs for Switch-Mode Battery Chargers: https://www.ti.com/lit/ml/slyp089/slyp089.pdf
8. TI SLUAAR3 -- Battery Gauging Algorithm Comparison: https://www.ti.com/lit/SLUAAR3
9. TI SLUA456 -- Single Cell Gas Gauge Circuit Design: https://www.ti.com/lit/pdf/slua456
10. OrionBMS Wiring & Installation Manual: https://www.orionbms.com/manuals/pdf/wiring.pdf
