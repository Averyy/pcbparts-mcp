# Power Architecture

> Multi-rail planning: topology selection, hybrid strategies, power budgeting, sequencing, inrush, PMIC vs discrete.

## Quick Reference

- **LDO only when dropout < 1V and Iout < 300mA.** At 12V-to-3.3V an LDO is 27.5% efficient -- use a buck (93% sync) or buck-then-LDO hybrid.
- **Power budget every rail before selecting parts.** A 500mA/3.3V buck feeding a 1.1A-rated LDO cannot deliver the LDO's max 2.75W -- works at low speed, fails under full processor load.
- **Sequence core -> auxiliary -> I/O.** Reversed sequence causes latch-up (immediate) or ESD stress on unpowered I/O (cumulative degradation).
- **Design traces and vias for peak inrush, not steady-state.** 100uF on 1.8V without slew control: 6.5A inrush, 82% rail sag.
- **4-switch buck-boost for Li-ion to 3.3V.** Battery spans 3.0-4.2V across Vout -- neither buck nor boost works alone. Up to 98% efficiency.

## Design Rules

### Topology Selection

- **If LDO efficiency < 50%, switch to a buck.** 12V-to-3.3V LDO = 27.5% efficient. 3.3V-to-2.5V = 75.8%. Threshold is clear -- anything above 1.5x dropout-to-Vout ratio needs a switcher.
- **Buck 12V to 3.3V synchronous at 10A: ~93% efficiency.** Diode (non-sync) buck loses ~3.6W in the freewheeling diode alone at 10A; sync buck replaces it with a 10mohm FET losing 0.73W. Always use sync buck above 1A.
- **SIMO (single-inductor multiple-output) for ultra-compact multi-rail.** MAX17270: 3 regulated outputs from one inductor. Best for wearables/IoT where board area is critical and per-rail current is low. Not suitable for high transient loads -- shared inductor limits per-channel response.
- **LDO for noise-sensitive rails.** 2.5V CMOS VIL = 0.7V, 1.8V CMOS VIL = 0.63V. After -10% supply tolerance: 0.63V and 0.57V margins. Switching noise (tens to hundreds of mV) can violate these thresholds. Buck-then-LDO hybrid solves both efficiency and noise.
  - Low-noise analog/PLL: LT3045/LT3042 (ADI, ultralow noise with VIOC to minimize LDO headroom).
  - General 3.3V from 5V: ADP125 (ADI, 500mA, SOT-23-5) or ADP1740 (ADI, 2A).

### Hybrid Topologies

- **Buck then LDO: maximize efficiency, minimize noise.** Buck handles the large voltage step at >90% efficiency. LDO cleans ripple with minimal dropout.
- **VIOC (voltage input-to-output control) eliminates wasted LDO headroom.** LT3070-1 regulates the upstream buck output to maintain only 85mV dropout. At 3A: 255mW dissipation vs 1.2W for a typical 400mV-dropout LDO -- nearly 5x reduction.
- **Silent Switcher bucks may eliminate the post-LDO entirely.** LT8650S, LTC3310S: low EMI, small footprint. Evaluate output ripple vs load VIL requirements before adding an LDO stage.
- **Quad-buck single-chip for FPGA/processor rails.** ADP5054: 17A total in 7mm * 7mm. Full solution ~41mm * 20mm. Replaces 4 discrete regulators plus sequencing glue.
- **Power modules for extreme density.** LTM4700 uModule: up to 100A from 15mm * 22mm. Higher BOM cost but drastically reduced design effort and risk.

### Power Budgeting

- **Work backward from every load.** Enumerate all loads per rail including pull-ups, LEDs, and dividers. Ten 4.7kohm pull-ups on 3.3V = 7mA. Twenty LEDs at 5mA = 100mA. These push marginal regulators into overcurrent.
- **Multiply efficiencies at each cascaded stage.** A buck (90%) feeding an LDO (76%) for 3.3V to 2.5V: overall 68.4%. See Formulas section for calculation.
- **Verify no cascaded stage exceeds upstream capacity.** ADP5304 buck at 500mA/3.3V = 1.65W max output. Downstream LT1965 LDO rated 1.1A at 2.5V = 2.75W demand. System works at light load, fails under full processor load when PSU1 current-limits or shuts down.
- **Sleep current budget for battery systems.** Discrete design with 5 regulators at 10uA Iq each = 50uA total. PMIC with shared bias: lower total Iq. Matters when sleep target is < 10uA.
- **Use LTpowerPlanner to visualize rail hierarchy.** Catches cascading capacity violations before component selection. Free tool, generates power tree diagram.

### Sequencing

- **Typical FPGA/processor: VCCINT -> VCCAUX -> VCCO.** Always check device datasheet -- sequence varies by family. Xilinx Spartan-3A has internal POR but still benefits from staggered inrush.
- **Passive RC delay on enable pins: X5R varies +/-15% over temperature plus +/-10% DC bias.** A sequence that works at 25C can swap order at -20C or +85C, causing latch-up.
- **Precision enable (ADP5134): +/-3% threshold accuracy.** Internal 0.97V reference, 80mV hysteresis. Connect attenuated output of regulator N to enable pin of regulator N+1 via resistor divider. Only 2 external resistors per channel.
- **Dedicated sequencer ICs (ADM1184): +/-0.8% accuracy.** Use when >2-3 rails need coordinated sequencing, or when regulators lack precision enable pins. ADM1186 adds programmable timing.

### Inrush Current Management

- **Uncontrolled inrush damages traces, blows vias, collapses rails.** 100uF on 1.8V: 6.5A peak, rail drops from 1.8V to 320mV (82% sag). Other modules on that rail will reset.
- **Load switches for hot-plugged or high-capacitance loads.** Slew-rate-controlled TPS229xx family. Multiple load switches can individually gate capacitive loads on a single rail -- cheaper than multiple regulators.
- **Load switch rise time suffixes (TI TPS229xx):** A = fastest (<10us), B = ~100us, C = ~800us, D = ~9ms. Adjustable CT pin on TPS22965 allows custom rise time via external capacitor.
- **Discrete inrush limiter: minimum 4 components** (2 MOSFETs, 2 resistors). R_SR in Mohm range to control slew. Prefer integrated load switches when current rating allows.

### PMIC vs Discrete

- **Discrete advantage: flexibility.** Need a 5th rail? Add one regulator. Need 3A instead of 2A? Swap one IC. But each rail needs: 2 feedback resistors, soft-start cap, EN/PGOOD pull-up/down, compensation network, sequencing glue.
- **PMIC advantage: integration.** Automatic sequencing, single PGOOD/nPOR, fault handling, DVS via I2C -- all without external glue. Lower total Iq from shared bias.

| PMIC Type | Configuration | Best For |
|-----------|--------------|----------|
| Externally configurable | Resistor-set voltages | Simple multi-rail without MCU |
| Software configurable (I2C) | Volatile -- reprogram every startup | Systems with MCU already present |
| Factory-programmed | Pre-set for specific processor | Matched processor (e.g., TPS65218D0 for AM335x) |
| User-programmable (EEPROM/OTP) | Program once, retains settings | Flexible multi-processor (TPS6521815 for i.MX, Xilinx, Intel) |

- **DVS (dynamic voltage scaling) via PMIC:** centralized I2C control of rail voltages. Discrete DVS requires additional transistors + resistors per rail to switch feedback dividers.
- **Hybrid PMIC + discrete is valid.** Use PMIC for core rails with sequencing, add a discrete buck for a 5th rail or higher-current demand. LP8732-Q1 (quad PMIC) + single external buck is common.

## Common Mistakes

- **LDO in SOT-23 for large voltage drop.** 12V to 3.3V at 100mA = 870mW. SOT-23 max ~260mW. Package fails thermally before hitting current limit -- no overcurrent protection triggers. Fix: buck converter, or buck-then-LDO hybrid.
- **Via stitching undersized for power.** Standard via handles ~1A. A single via connecting regulator output to power plane acts as a fuse at inrush current. Failure is invisible -- via opens under a component, hard to see or probe. Fix: 3 vias minimum for 2A with margin.
- **No PGOOD monitoring on critical rails.** System boots into undefined state if a rail fails to reach target. MCU starts executing with core powered but I/O rail still ramping -- undefined GPIO states can latch up external devices. Fix: tie PGOOD to processor reset, or use PMIC with integrated sequencing.
- **Power budget ignores cascaded efficiency.** A 10W buck fed from an 85%-efficient upstream converter needs 11.8W input -- but the upstream stage was sized for 10W because the designer only budgeted the final stage. System works at 80% load, brownouts at 100% when the upstream hits its current limit. Fix: multiply each stage's input power = P_out / eta, working backward from load to source. A 3-stage chain at 90%/85%/92% delivers only 70.4% wall-to-load.
- **Switching noise false-triggers 1.8V CMOS logic.** 1.8V CMOS VIL = 0.63V. After -10% tolerance = 0.57V. Switching noise of 200-400mV puts signals into indeterminate region. Fix: buck-then-LDO for 1.8V and 2.5V rails, or use Silent Switcher bucks.

## Formulas

**Inrush current:**
**Rule of thumb:** 100uF at 3.3V with fast turn-on: >3A inrush. Load switch reduces by 4-7x.
**Formula:** I_inrush = C_load * dV / dt
**Example:** 22uF, 3.3V, target max 600mA -> dt = 22uF * 3.3V / 600mA = 121us minimum rise time. Select TPS22902B (146us typ) or TPS22924C (800us).

**Cascaded efficiency:**
**Rule of thumb:** Two 90%-efficient stages = 81% overall. Three = 72.9%.
**Formula:** eta_total = eta_1 * eta_2 * ... * eta_n
**Example:** 12V wall -> buck (90%) -> LDO (76%) for 3.3V to 2.5V. Overall = 68.4%. Input power for 500mA at 2.5V: 1.25W / 0.684 = 1.83W from wall.

## Sources

### Related Rules

- `power/ldo.md` -- LDO regulator design, noise performance, stability requirements
- `power/switching.md` -- Buck/boost topology selection, inductor sizing, compensation
- `guides/thermal.md` -- Thermal verification for LDO and regulator packages

### References

1. ADI -- Multirail Power Supply Design Part 1: Strategy: https://www.analog.com/en/resources/analog-dialogue/articles/multirail-power-supply-design-for-successful-application-boards-part1.html
2. ADI AN-140 -- Linear vs Switching Regulators: https://www.analog.com/en/resources/app-notes/an-140.html
3. ADI -- Multirail Power Supply Design Part 2: Power Budgeting + Layout: https://www.analog.com/en/resources/analog-dialogue/articles/multirail-power-supply-design-for-successful-application-boards-part2.html
4. ADI AN-1311 -- Power Supply Sequencing: https://www.analog.com/en/resources/app-notes/an-1311.html
5. TI SLDA039B -- PMIC Power Management Design Guide: https://www.ti.com/lit/sg/slda039b/slda039b.pdf
6. ADI -- Supply Topology Selection for Processors/MCUs: https://www.analog.com/en/resources/technical-articles/supply-topology-high-power.html
7. TI SLVA670A -- Managing Inrush Current: https://www.ti.com/lit/an/slva670a/slva670a.pdf
