# Voltage Supervisor & Watchdog

> Reset threshold budgeting, output topology selection, hysteresis design, and watchdog timer configuration.

## Quick Reference

- **VTH(nom) = (Vss(min) + Vcpu(min)) / 2.** Total VTH accuracy window must fit entirely between Vcpu(min) and Vss(min) -- overlap means false resets or missed brown-outs.
- **TPS3808 has only 6mV hysteresis on sense pin** -- reflects to 27mV on 1.8V through divider. Battery systems need external hysteresis (Rh=1M, Rp=100K -> ~200mV).
- **Open-drain RESET: pull up to the monitored rail by default; wire-OR outputs for multiple rails** [9, 11]. Resistor: the datasheet's range, 10K-1M on TLV803 and TPS3808 [9, 10].
- **Watchdog from main loop, NEVER from timer ISR.** ISR-serviced watchdog hides main-loop lockups. Windowed watchdog catches this; simple timeout does not.
- **Q&A watchdog window > 64ms.** SPI overhead for reading question and writing 4 responses requires significant time per TCAN1146 reference.

## Design Rules

### Threshold Selection

- **Fixed-threshold ICs preferred.** MAX16140: +/-0.5%, 0.7-6.0V, 1.1uA. ADM809/810: +/-1.5%, 1.0-5.5V, 50uA, SOT-23/SC70 (cheapest).
- **Adjustable-threshold ICs:** TPS38600 (+/-1% ref, 2.5-18V, quad channel + watchdog), ADM8612 (+/-0.5% ref, 1.2-5.5V, 0.5uA). Use 1% resistors minimum.
- **Sense pin leakage drives divider resistance limit.** 25nA * 500K = 12.5mV error. At 250K: 6.25mV. TI SLVA521 example: R1=500K caused VTH_min (1.708V) < Vcpu_min (1.71V) -- FAIL. Reducing R1 to 250K fixed it (VTH_min=1.712V).
- **Error budget terms stack:** reference accuracy (+/-0.5-1% over temp) + divider tolerance (~1% with 1% resistors, ~0.1% with 0.1%) + sense pin leakage (I_sense * R1). Use spreadsheet -- hand calculation misses interactions.

> WARNING: VTH accuracy window MUST NOT overlap supply accuracy window. Example: +/-2.5% total budget on 3.0V nominal -> VTH range 2.925-3.075V. If Vcpu(min)=2.97V, VTH_min (2.925V) < Vcpu(min) -> supervisor may not assert before CPU browns out.

- **VPOR (power-on reset voltage): the lowest supply at which RESET is valid.** TPS3808: 0.8V max; MAX803/809: 1V; TLV803: 1.1V [9, 10, 11].

### Output Type

- **Open-drain:** wired-OR -- any supervisor pulling low holds reset [9, §9.1.1].
- **Push-pull:** only ONE per reset line -- multiple push-pull outputs cause bus contention.
- **Bi-directional uP reset + push-pull:** add 1K series resistor so uP can override supervisor.
- **Bi-directional + wired-OR (MAX6316):** open-drain with internal 4.7K pull-up + ~2us active pull-up for fast rise time. uP reset pins typically sink only 1.6mA -- reducing external pull-up below ~2K to speed rise time may prevent uP from pulling low enough to register as logic low.

| Scenario | Output Type |
|----------|-------------|
| Multiple supervisors on one bus | Open-drain |
| Single supervisor, no pull-up desired | Push-pull |
| Bi-directional reset + single supervisor | Push-pull with 1K series |
| Bi-directional reset + multiple supervisors | Bi-directional (MAX6316) |
| Reset voltage != supervisor supply | Open-drain |

### Pull-Up Sizing

- **Pull-up rail: the monitored rail (the supervisor's VDD) by default** [9, §9.2.2; 11]. Below VPOR, RESET follows the pull-up [9, §8.3.2]; on another rail it reads high then [11]. Use another rail only to match the reset input's logic level [9, §9.1.2], and only if it can't come up before the monitored rail.
- **Value: inside the datasheet's range.** TLV803 and TPS3808: 10K-1M [9, 10]; ADI's nominal for Maxim parts is 4.7K [3]. R_max = (V_pullup - V_IH(min)) / I_leakage(max). R_min = (V_pullup - V_OL(max)) / I_OL(test).
- **Leakage doubles every 10-15C.** At 125C, 10nA (25C) spec may reach 100-300nA. Verify R_max at max operating temperature.
- **Large pull-up (>100K):** high-impedance net picks up noise from nearby digital traces. Long open-drain traces with large R are especially vulnerable.
- **Small pull-up (<2K):** power consumption when RESET asserted (3.3V/2K = 1.65mA), and uP reset sink current limit (~1.6mA) may prevent valid logic low.

### Hysteresis & Noise Filtering

- **TPS3808 internal hysteresis: 6mV on sense pin (Vs+ = 0.406V, Vs- = 0.400V).** Through R1/R2 divider to 1.8V input: only 27mV. Battery with gradual discharge slope will oscillate around VTH.
- **External hysteresis circuit:** feedback resistor Rh from RESET to sense divider node. When RESET is low, Rh pulls sense node down -> higher input voltage needed to release. Rh=1M, Rp=100K, R1=102K, R2=26.7K -> 200mV hysteresis on 1.8V rail (fall at 1.8V, rise at 2.0V).
- **Reset timeout (tRP) >= 2x supply settling time.** Masks overshoot and ringing after supply recovery. Typical 100-200ms for SMPS. Too short: MCU starts while supply is ringing.
- **Overdrive vs duration:** short glitches with large magnitude do NOT trigger reset; longer, smaller overdrives do. Check overdrive-vs-duration curve in datasheet to verify immunity to SMPS switching transients.
- **Manual reset debounce (tMR): 100-300ms.** Some supervisors have internal deglitch on MR pin (MAX6444 has long tMR specifically for accidental-press immunity). Others need external RC (10K + 100nF = 1ms).

### Multi-Rail Sequencing

- **Wired-OR:** multiple open-drain supervisors on shared RESET. Pull-up R must handle cumulative leakage from all devices.
- **Daisy-chain with EN gating:** each supervisor RESET gates next regulator EN. 3-rail chain with tRP=200ms each -> 600ms worst-case boot delay.
- **Multi-voltage ICs:** TPS386000 (quad supervisor + watchdog, 2.5-18V, +/-1% ref, open-drain x4). Single IC for 2-4 rail systems.
- **FPGA sequencing is critical:** violating core-before-I/O (or vice versa per vendor) causes I/O bank latch-up with destructive current -> `mcus/fpga.md`.
- LDO EN pin sequencing, PGOOD -> `power/ldo.md`.

### Watchdog Timers

- **Timeout (simple):** catches hard lockups only. Does NOT catch loop-lock -- stuck loop can still toggle WDI via timer ISR.
- **Windowed:** CLOSED + OPEN windows. Service during CLOSED = fault. Catches loop-lock. Extended all-OPEN window at power-on for boot. RESET latch mode holds reset continuously until two consecutive valid services (useful for disabling CAN during fault).
- **Q&A (challenge/response):** MCU reads question register (I2C/SPI), computes LFSR answer (x^8 + x^6 + x^5 + x^4 + 1), responds within timing window. MAX20478/MAX20480 for ASIL-D. TCAN1146: 4 SPI transactions per window -- window > 64ms recommended.
- **Watchdog clock: internal RC oscillator, +/-10-20% typical.** Size OPEN window to accommodate drift on both watchdog and MCU sides.
- **Selection:** non-critical -> timeout. Industrial/automotive -> windowed. Safety-critical (ASIL-C/D) -> Q&A.
- **MCU BOD vs external supervisor:** MCU BOD +/-5% typical vs external +/-0.5-2%. Use external when accuracy matters, multiple rails need monitoring, or safety standards require independent monitoring.
- **Timeout sizing:** 200ms for simple control loops, 1-2s for networked systems. Too short = nuisance trips. Too long = extended uncontrolled output (dangerous for motor/heater/actuator).
- **Disable during debug:** WD_DIS pin or register bit. Tie to test point or debug header.

## Common Mistakes

- **Capacitor on RESET without checking current and delay.** An asserted open-drain output sinks and discharges it [9, 10]. Check the discharge peak against the pin rating (5mA on TLV803 and TPS3808 [9, 10]) and the release delay as the pull-up recharges it: t = R_pu * C * ln(V_pu / (V_pu - V_IH)). A series resistor limits the peak but lifts the asserted low by R_series * pull-up current: check V_IL.
- **Watchdog error counter ignored.** TCAN1146 and MAX20478 have configurable error counters -- a single missed service increments counter but doesn't immediately assert RESET. Two consecutive valid services needed to decrement counter back. Fail to configure threshold and nuisance resets occur, or genuine faults are masked.
- **Power-on glitch read as a release.** Below VPOR the supervisor can't sink: an open-drain RESET sits at its pull-up rail, a push-pull one floats [1, 11]. A pull-up rail that comes up first, or logic with a low V_IH (1.2V FPGA core, 1.8V SRAM), sees a release while the supply is below threshold. Pull up to the monitored rail (the glitch then stays under VPOR), bring the monitored rail up first, or pick a lower-VPOR part. Push-pull (MAX809): 100K from RESET to ground holds it low down to 0V [11]; beside an open-drain pull-up it only divides (10K up, 100K down leaves 91%).
- **Windowed watchdog CLOSED window sized without clock drift.** +/-20% watchdog RC oscillator + +/-1% MCU crystal = service pulse may land in CLOSED window under worst-case drift. Size OPEN window >= 2x nominal service period.

## Formulas

**Threshold error budget:**
**Rule of thumb:** Fixed-threshold: +/-0.5% (TPS3808) to +/-1.5% (ADM809). Adjustable: add ~1% for 1% divider resistors.
**Formula:** VTH_max = VTH_nom * (1 + e_ref + e_div + I_sense*R1/VTH_nom). VTH_min = VTH_nom * (1 - e_ref - e_div - I_sense*R1/VTH_nom).
**Example:** 1.8V rail, VTH_nom=1.737V, 1% ref, 1% dividers (R1=500K), 25nA leakage -> VTH range 1.708-1.766V. CPU min=1.71V. VTH_min (1.708V) < Vcpu_min (1.71V) -> FAIL. Reduce R1 to 250K -> VTH range 1.712-1.763V -> PASS.

**Pull-up resistor range:**
**Rule of thumb:** the datasheet's range (10K-1M on TLV803 and TPS3808 [9, 10]); ADI's nominal is 4.7K [3].
**Formula:** R_max = (V_pullup - V_IH(min)) / (I_leak_OD + I_leak_input). R_min = (V_pullup - V_OL(max)) / I_OL(test), and never below the datasheet's minimum.
**Example:** V_pullup=1.8V, V_IH=1.0V, I_leak=1.1uA -> R_max=727K. V_OL=0.3V, I_OL=1mA -> R_min=1.5K. 10K (the TPS3808 minimum) is within range.

**External hysteresis (TPS3808):**
**Rule of thumb:** Rh=1M, Rp=100K -> ~200mV on 1.8V rail.
**Formula:** Solve simultaneously: V1+ = Vs+ * (1 + R1/R2 + R1/Rh) and V1- = Vs- * (1 + R1/R2) - V2*R1/(Rh+Rp) where Vs+=0.406V, Vs-=0.400V.
**Example:** V1-=1.8V, V1+=2.0V, V2=1.8V, Rp=100K, Rh=1M -> R1=102K, R2=26.7K.

**Watchdog window sizing:**
**Rule of thumb:** OPEN window >= 2x nominal service period.
**Formula:** T_OPEN_min = T_service * (1 + drift_WD) / (1 - drift_MCU)
**Example:** 100ms service, WD +/-15%, MCU +/-1% -> T_OPEN_min = 100 * 1.15 / 0.99 = 116ms

## Sources

### Related Rules

- `mcus/fpga.md` -- FPGA power sequencing with voltage supervisors, core-before-I/O latch-up risk
- `power/ldo.md` -- LDO EN pin sequencing, PGOOD signal usage

### References

1. ADI -- High Performance Voltage Supervisors Explained, Part 1: https://www.analog.com/en/resources/analog-dialogue/articles/high-perf-volt-supervisors-explained-part-1.html
2. ADI -- How Voltage Supervisors Address Power Supply Noise and Glitches: https://www.analog.com/en/resources/analog-dialogue/articles/voltage-supervisors-address-power-supply-noise-and-glitches.html
3. ADI -- Choosing Supervisor Outputs (Open-Drain vs Push-Pull): https://www.analog.com/en/resources/technical-articles/choosing-supervisor-outputs.html
4. TI SLVA521 -- Setting the SVS Voltage Monitor Threshold: https://www.ti.com/lit/an/slva521/slva521.pdf
5. TI SLVA360 -- Adding Hysteresis to Supply Voltage Supervisor: https://www.ti.com/lit/pdf/slva360
6. TI SLVA485 -- Pull-up/Pull-down Resistor for Open Drain Outputs: https://www.ti.com/lit/an/slva485/slva485.pdf
7. ADI -- The Basics of Windowed Watchdogs (MAX20478/MAX20480): https://www.analog.com/en/resources/technical-articles/the-basics-of-windowed-watchdogs.html
8. TI SLLA546 -- Q&A Watchdog Overview and Configuration: https://www.ti.com/lit/pdf/slla546
9. TI TLV803 datasheet (SBVS157E): https://www.ti.com/lit/gpn/tlv803
10. TI TPS3808 datasheet (SBVS050N): https://www.ti.com/lit/gpn/tps3808
11. Analog Devices (Maxim) MAX803/MAX809/MAX810 datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/MAX803-MAX810Z.pdf
