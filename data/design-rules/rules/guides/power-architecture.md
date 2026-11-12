# Power Architecture

> Multi-rail planning: topology selection, hybrid strategies, power budgeting, sequencing, inrush, PMIC vs discrete.

## Quick Reference

- **Choose an LDO from loss, dropout and transient budgets, not a fixed current cutoff.** 12V-to-3.3V gives at most 27.5% efficiency before quiescent current; use a buck or hybrid when that loss exceeds the thermal budget [2, pp.2-3].
- **Power budget every rail before selecting parts.** ADI's 500mA/3.3V ADP5304 cannot supply a 1.1A load through the LT1965; subtract other 3.3V loads and LDO ground current from that 500mA first [3, Power Budgeting].
- **Use the processor's specified power-up and power-down sequence.** Core -> auxiliary -> I/O is AN-1311's Spartan-3A example, not a universal FPGA/processor requirement [4, p.1].
- **Validate inrush with the actual source and output capacitance.** TI measured 6.46A and 82% sag when switching 100uF onto its already-powered 1.8V buck rail with 66uF output capacitance [7, pp.10-11].
- **Use buck-boost when the required input range crosses the output voltage.** ADI's LTC3114-1 example regulates 3.3V; choose from efficiency curves at the actual input and load [6, Figure 6].

## Design Rules

### Topology Selection

- **Small input-output headroom can favor an LDO, including at light load.** At 3.3V-to-2.5V, efficiency approaches 75.8% when ground current is negligible; compare with the switcher's efficiency at the same load, then verify worst-case dropout and heat -> `power/ldo.md` [2, pp.2-3].
- **AN-140's 12V-to-3.3V/10A synchronous example reaches about 93% at 200-500kHz.** Its loss model assumes 10mohm FETs and 2mohm inductor DCR: replacing a 0.5V freewheel diode reduces that conduction term from 3.625W to 0.725W, ignoring ripple. This is an example, not a guaranteed efficiency or a universal 1A topology boundary [2, pp.5-7].
- **SIMO for compact multi-rail supplies:** MAX17270 provides three outputs from one inductor. Verify simultaneous load and transient requirements because outputs share that inductor; shared inductance alone does not rule out all high-transient applications [6, Figure 4 and Table 4].
- **Size post-regulation from the load's supply-noise specification and the LDO's PSRR at the ripple frequency.** A logic input VIL limit is not an allowable supply-ripple specification; it depends on the receiver, driver VOL and ground noise [1, Switching Noise and Multirail PSU Caveats and Tips; 8, p.18].
  - Low-noise analog/PLL: LT3045/LT3042; verify headroom and noise rejection for the operating point -> `power/ldo.md` [1, Multirail PSU Caveats and Tips].
  - General 3.3V from 5V: ADP125 (500mA, 8-lead exposed-pad MSOP or LFCSP), not a SOT-23 footprint [9, p.1].

### Hybrid Topologies

- **Buck then LDO: budget headroom for rejection and transient response as well as dropout.** A stage barely above dropout need not deliver its advertised PSRR; LT3070-1 uses greater VIOC headroom for these reasons [8, p.18].
- **LT3070-1 VIOC maintains 300mV typical input-output headroom (250-350mV specified).** Its 85mV typical dropout is specified at 5A, VOUT=1V, VBIAS=2.5V and 25 degrees C, not the VIOC target. At 3A, 300mV contributes 0.9W pass-element loss, excluding ground and bias supply power; compensate the coupled buck/LDO loop [8, pp.3-4, 18].
- **Silent Switcher bucks can avoid a post-LDO when they meet the load's supply-noise budget.** LT8650S and LTC3310S are examples; evaluate ripple and transients at the load rather than comparing supply ripple directly with VIL [1, footnote 2].
- **Quad-buck single-chip for FPGA/processor rails.** ADI's ADP5054 example supplies 17A total in 7mm * 7mm, with a full solution about 41mm * 20mm. The total is shared across channels, not available from each output [1, Package, Power, Cost, Efficiency, and Performance Trade-Offs].
- **Power module example:** LTM4700 supplies up to 100A from 15mm * 22mm; check the module's operating-condition and thermal limits rather than treating package area as a power guarantee [1, Package, Power, Cost, Efficiency, and Performance Trade-Offs].

### Power Budgeting

- **Work backward from every load.** Include pull-ups, LEDs and dividers, and use their maximum active current; a pull-up's full V/R current is drawn when its line is held low, not continuously in every logic state [3, Power Budgeting].
- **Verify current as well as power at cascaded stages.** ADI's ADP5304 at 500mA/3.3V provides 1.65W shared by its direct loads and the LT1965 input. An LDO passes approximately its load current, so a 1.1A/2.5V load (2.75W) cannot be supported even before considering the LDO's loss [3, Figure 2].
- **Check PMIC quiescent current in the actual operating mode.** Shared bias can reduce duplicated circuitry, but the integrated and discrete solutions must be compared with the same enabled rails and sleep requirements [5, pp.2-3].
- **Use LTpowerPlanner to visualize rail hierarchy.** Include direct and downstream loads on each source rail before selecting regulators [3, Power Budgeting, Figure 3].

### Sequencing

- **Check the exact processor's sequencing requirements and attached I/O circuits.** AN-1311's Spartan-3A example uses VCCINT -> VCCAUX -> VCCO to limit inrush and meet connected-circuit requirements despite internal POR; other devices require different orders -> `mcus/fpga.md` [4, p.1].
- **Passive RC delays require worst-case capacitor and enable-threshold analysis.** X5R specifies +/-15% temperature change over -55 to +85 degrees C, not a +/-10% bias limit. Include the exact capacitor's bias curve and regulator EN threshold corners; RC delay is not rail-good feedback [4, p.3; 10, Table 1 and Choosing the Right Capacitor].
- **Precision enable (ADP5134): +/-3% over input voltage and temperature.** Its threshold is 0.97V typical with 80mV typical hysteresis. Connect attenuated output of regulator N to enable pin of regulator N+1 via two resistors per channel; keep these tolerances in the release-voltage budget [4, pp.4-5].
- **Dedicated sequencer ICs:** ADM1184 offers +/-0.8% monitoring accuracy over voltage and temperature; ADM1186 adds programmable timing. Use them when the timing/monitoring requirements exceed the regulators' enable capabilities, without a universal rail-count cutoff [4, p.6].

### Inrush Current Management

- **Size slew control with the source's transient response.** TI's 6.46A peak, which pulled the 1.8V rail down to 320mV (an 82% drop), belongs to its 1.8V buck/66uF source and switched 100uF load; a different source impedance or switch gives different peak current and sag [7, pp.10-11].
- **Load switches for hot-plugged or high-capacitance loads:** TPS22965 has an adjustable CT pin; individual switches can gate capacitive loads on a shared rail [7, pp.6, 8-9].
- **Rise-time suffixes are device-specific.** TI's TPS22924 example has B/C/D rise times of 96us/800us/9ms. TPS22902B is 146us typical at 3.3V, so the letter B does not establish a family-wide timing value; check minimum timing and the actual output ramp [7, pp.7-8].
- **TI's Figure 5 discrete limiter uses two MOSFETs and two resistors.** Its R_SR is in the Mohm range; an added capacitor reduces the required resistor. This is one implementation, not a minimum component count for every limiter [7, p.5].

### PMIC vs Discrete

- **Compare the actual external components and sequencer functions.** TI's LP8732-Q1 comparison integrates four rails and sequencing; discrete regulator designs do not all need external compensation, soft-start capacitors or feedback resistors [5, pp.2-3].
- **PMIC integration depends on the selected part and programming.** Verify sequencing, reset, fault response and DVS functions rather than assuming all PMICs provide them without external logic [5, pp.4-8].

| PMIC Type | Configuration | Best For |
|-----------|--------------|----------|
| Externally configurable | Resistor-set voltages | Simple multi-rail without MCU |
| Software configurable (I2C) | TI's configurable examples store changes in volatile registers; reapply after power loss | A controller is available for startup configuration [5, p.6] |
| Factory-programmed | Pre-set for a specific processor | TPS65218D0 for AM335x/AM437x [5, p.7] |
| User-programmable (EEPROM/OTP) | Nonvolatile configuration; rewrite capability depends on EEPROM vs OTP | TPS6521815 for supported i.MX, FPGA and SoC power trees [5, p.7] |

- **DVS:** TI's discrete example switches feedback-divider resistors with transistors; its PMIC example changes voltages through registers. These are implementation examples, not requirements for every discrete regulator [5, pp.4-5].
- **Hybrid PMIC + discrete is valid.** TI illustrates LP8732-Q1 plus an external converter for a fifth rail, avoiding a larger PMIC selected solely for that extra output [5, p.4, Figure 4].

## Common Mistakes

- **Assuming a SOT-23 package has a universal 260mW limit.** LDO dissipation depends on the selected part, local ambient and the assembled board's thermal path; thermal shutdown also differs from current limiting. Check the package/board model -> `guides/thermal.md` [2, Linear Regulator Power Loss; 3, Avoid Overheating].
- **Treating a via as a universal 1A conductor.** ADI's two-via minimum (three preferred) assumes vias already rated for 1A in that board; plating, hole size, layer and allowed temperature rise change capacity -> `guides/pcb-layout.md` [3, Vias and Stitching].
- **A timed enable chain releases the processor even if a rail never starts.** Use monitored rail-good signals or a sequencer/reset circuit that remains asserted on a failed supply; distinguish a delay from verified regulation -> `protection/voltage-supervisor.md` [4, pp.3, 6; 5, p.5].
- **Budgeting upstream output power without downstream conversion loss.** Refer each downstream load to the upstream output using that downstream stage's efficiency; apply the upstream efficiency only when calculating its own input demand. Include shared direct loads [3, Power Budgeting].

## Formulas

**Inrush current:**
**Rule of thumb:** Budget capacitor charging plus the load's startup current; use maximum effective capacitance and the fastest actual ramp, not just typical 10%-90% rise time [7, pp.2, 7-9; 11, p.19, Figure 8-1].
**Formula:** I_switch(t) = C_load * dV_out/dt + I_load(t); for a linear full-swing ramp, dt_min = C_load * delta_V / (I_limit - I_load).
**Example:** TI's 22uF/3.3V example with zero load current and a 600mA charging budget needs a linear full-swing dt >= 121us. TPS22902B's 146us is typical 10%-90% timing, not a guaranteed minimum full-swing ramp; verify the minimum timing, capacitor tolerance, ramp shape and startup load [7, p.7; 11, p.19, Figure 8-1].

## Sources

### Related Rules

- `power/ldo.md` -- LDO regulator design, noise performance, stability requirements
- `power/switching.md` -- Buck/boost topology selection, inductor sizing, compensation
- `guides/thermal.md` -- Thermal verification for LDO and regulator packages

### References

1. ADI -- Multirail Power Supply Design Part 1: Strategy: https://www.analog.com/en/resources/analog-dialogue/articles/multirail-power-supply-design-for-successful-application-boards-part1.html
2. ADI AN-140 -- Basic Concepts of Linear Regulator and Switching Mode Power Supplies (Rev.C, October 2013): https://www.analog.com/media/en/technical-documentation/app-notes/an140.pdf
3. ADI -- Multirail Power Supply Design Part 2: Power Budgeting + Layout: https://www.analog.com/en/resources/analog-dialogue/articles/multirail-power-supply-design-for-successful-application-boards-part2.html
4. ADI AN-1311 -- Complex Power Supply Sequencing Made Easy (Rev.0, August 2014): https://www.analog.com/media/en/technical-documentation/app-notes/an-1311.pdf
5. TI SLDA039B -- How to Design Flexible Processor Power Systems Using PMICs (revised January 2020): https://www.ti.com/lit/sg/slda039b/slda039b.pdf
6. ADI -- Supply Topology Selection for Processors/MCUs: https://www.analog.com/en/resources/technical-articles/supply-topology-high-power.html
7. TI SLVA670A -- Managing Inrush Current (revised May 2015): https://www.ti.com/lit/an/slva670a/slva670a.pdf
8. ADI -- LT3070-1 datasheet (Rev.0): https://www.analog.com/media/en/technical-documentation/data-sheets/lt3070-1.pdf
9. ADI -- ADP124/ADP125 datasheet (Rev.D, December 2014): https://www.analog.com/media/en/technical-documentation/data-sheets/adp124_125.pdf
10. ADI Tutorial 5527 -- Temperature and Voltage Variation of Ceramic Capacitors (2012-12-04): https://www.analog.com/en/resources/technical-articles/temperature-and-voltage-variation-ceramic-capacitor.html
11. TI -- TPS22901/TPS22902/TPS22902B datasheet (SLVS803E, September 2020): https://www.ti.com/lit/ds/symlink/tps22902.pdf
