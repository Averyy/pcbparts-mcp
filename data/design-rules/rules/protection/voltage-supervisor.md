# Voltage Supervisor & Watchdog

> Reset threshold budgeting, output topology selection, hysteresis design, and watchdog timer configuration.

## Quick Reference

- **VTH(nom) = (Vss(min) + Vcpu(min)) / 2.** Total VTH accuracy window must fit entirely between Vcpu(min) and Vss(min) -- overlap means false resets or missed brown-outs [4, pp.3-4].
- **TPS3808G01 has 6mV typical hysteresis on its 0.4V sense threshold** -- about 27mV when divided from a 1.8V trip point. External hysteresis is needed when load-induced battery rebound exceeds that margin [5, pp.2-4; 9, §6.5].
- **Open-drain RESET: pull up to the monitored rail by default; wire-OR outputs for multiple rails** [8, 11]. Resistor: the datasheet's range, 10K-1M on TLV803 and TPS3808 [8, 9].
- **A windowed watchdog still accepts a periodic ISR while the main loop is stuck.** Arrange watchdog service to depend on completed application work; window checking only rejects service outside its timing window [6, Windowed Watchdogs; 7, pp.1-2].
- **TCAN1146-Q1 Q&A: TI recommends window times >64ms.** Send three ordered answers in response window 1 and the fourth in window 2; reading the question is an additional SPI transaction unless already known [7, p.3].

## Design Rules

### Threshold Selection

- **Fixed-threshold ICs avoid divider tolerance.** MAX16140: +/-1.5% threshold accuracy, 1.7-4.85V factory thresholds, 1.7-5.5V operating supply, 370nA typical quiescent current with RESET unasserted and VCC=1.1 * VTH (specified current limits at -40 to +85 degrees C). ADM809/810: SOT-23/SC70; use the threshold min/max for the selected suffix and temperature, not a universal +/-1.5% [11, pp.1, 3; 14, pp.1, 3].
- **Adjustable-threshold ICs:** TPS386000 (four channels + watchdog, 0.4V sense threshold +/-1%, 1.8-6.5V supply). ADM8612 has factory thresholds from 0.5V to 1.9V and supports an external divider, but is not a +/-0.5% reference: accuracy ranges from +/-1.3% to +/-2.2% by threshold option, with 2-5.5V supply and 92nA typical quiescent current with RESET deasserted at 25 degrees C [12, pp.1, 6-7; 13, pp.1, 3, 12].
- **Sense pin leakage drives divider resistance limit.** TPS386000's +/-25nA limit contributes +/-12.5mV with R1=500K or +/-6.25mV with R1=250K, before resistor tolerance. SLVA521's printed threshold example has inconsistent arithmetic; recompute the complete tolerance corners instead of using its claimed pass/fail results [4, pp.4-6; 12, p.7].
- **Evaluate reference, both divider resistors, and sense leakage together.** For R1 from rail to SENSE and R2 to ground, use VTH = Vref * (1 + R1/R2) + I_sense * R1 with current defined positive into SENSE. Sweep min/max reference, resistor values, and signed leakage; two 1% resistors do not imply only 1% threshold error [4, p.4].

> WARNING: Keep the entire threshold tolerance window above Vcpu(min) and below Vss(min). Otherwise reset can arrive after the CPU has left its operating range or assert during valid supply operation [4, pp.3-4].
- **VPOR limits depend on load and ramp rate.** TPS3808: 0.8V maximum at 15uA RESET current, VOL <=0.2V, VDD rise time >=15us/V. MAX803/809 guarantee valid reset down to 1V under their output-current conditions; TLV803 specifies 1.1V with 50uA load, VOL <0.2V, and VDD slew <=66.7V/ms [8, §7.5; 9, §6.5; 10, pp.1, 3].

### Output Type

- **Open-drain:** wired-OR -- any supervisor pulling low holds reset [8, §9.1.1].
- **Push-pull:** only ONE per reset line -- multiple push-pull outputs cause bus contention [3, Push-Pull Output].
- **Bi-directional uP reset + push-pull:** add the series resistor shown in the supervisor's application circuit; verify the low level and contention current for both drivers instead of assuming 1K works for every pair [3, Figure 3].
- **Bi-directional + wired-OR (MAX6316 series):** internal 4.7K pull-up plus an approximately 2us active pull-up pulse. ADI notes that some uP reset pins sink only 1.6mA; size any external pull-up to that pin's actual rating [3, Bi-Directional Output].

| Scenario | Output Type |
|----------|-------------|
| Multiple supervisors on one bus | Open-drain |
| Single supervisor, no pull-up desired | Push-pull |
| Bi-directional reset + single supervisor | Push-pull with series resistance verified for both drivers |
| Bi-directional reset + multiple supervisors | Bi-directional (MAX6316) |
| Reset voltage != supervisor supply | Open-drain |

### Pull-Up Sizing

- **Pull-up rail: the monitored rail (the supervisor's VDD) by default** [8, §9.2.2; 10]. On TLV803, RESET follows the pull-up below 1.1V [8, §8.3.2]; on another rail it can read high while the monitored supply is invalid [10]. Use another rail only to match the reset input's logic level [8, §9.1.2], and only if it can't come up before the monitored rail.
- **Value: inside the datasheet's range.** TLV803 and TPS3808: 10K-1M [8, 9]; ADI's nominal for Maxim parts is 4.7K [3]. R_max = (V_pullup - V_IH(min)) / I_leakage(max). R_min = (V_pullup - V_OL(max)) / I_OL(test).
- **Use maximum leakage at the required temperature.** TPS3808 specifies 300nA maximum RESET leakage over its stated operating range; add receiver leakage and leakage from all wired-OR devices [9, §6.5; 3, Open-Drain Output].
- **Check every device that must pull RESET low.** ADI's 1.6mA example is a limit of some uP reset drivers, not a universal supervisor limit; a stronger supervisor does not compensate for a weaker bidirectional MCU pin [3, Bi-Directional Output].

### Hysteresis & Noise Filtering

- **TPS3808G01 internal hysteresis is 1.5% typical, 3% maximum of its 0.4V threshold.** SLVA360 uses Vs-=0.400V and Vs+=0.406V as nominal values, not guaranteed threshold corners; the external-hysteresis design still needs a tolerance analysis [5, p.3; 9, §6.5].
- **External hysteresis circuit:** Rh from RESET to SENSE adds positive feedback. SLVA360 uses an independent V2=1.8V pull-up, Rh=1M, Rp=100K, R1=102K, R2=26.7K for nominal 1.8V falling / 2.0V rising thresholds; V2 is part of the threshold calculation [5, pp.2-5].
- **Choose reset timeout from the required supply settling and processor reset timing.** The minimum specified timeout must cover that interval; TLV803's 200ms typical value is not a universal SMPS default or a guaranteed minimum [2, Reset Timeout Period; 8, §3].
- **Overdrive vs duration is a tradeoff, not immunity to every short high-amplitude glitch.** Larger threshold overdrive generally needs a shorter pulse to assert reset; compare the actual transient to the selected part's rejection curve [2, Threshold Overdrive; 14, p.7, Figure 11].
- **Manual-reset debounce is separate from reset timeout.** MAX16140's level-trigger MR debounce is 20ms typical for 10ms-2s timeout options, versus 0.6ms for its 310us option; select the exact configuration rather than applying a 100-300ms default [11, p.3].

### Multi-Rail Sequencing

- **Wired-OR:** multiple open-drain supervisors on shared RESET. Pull-up R must handle cumulative leakage from all devices [3, Open-Drain Output].
- **Daisy-chain with EN gating:** delays accumulate through the chain, including regulator ramp and each supervisor's maximum release delay. Adding three nominal 200ms delays does not establish a 600ms worst-case boot time [1, Figure 10; 8, §3].
- **Multi-voltage ICs:** TPS386000 provides four adjustable supervisors and a watchdog, with open-drain outputs and a 1.8-6.5V supply; its SENSE inputs must remain within their specified limits [12, pp.1, 6-7].
- **FPGA sequencing:** use the FPGA vendor's rail order and timing rather than a universal core-before-I/O rule -> `mcus/fpga.md` [1, Application Use Case Examples].
- LDO EN pin sequencing, PGOOD -> `power/ldo.md`.

### Watchdog Timers

- **Timeout watchdogs do not detect valid-looking service from faulty code.** Windowed watchdogs additionally reject early service, but periodic faulty service inside the open window still passes [7, pp.1-2].
- **Windowed (MAX20478/MAX20480):** service during CLOSED or after OPEN is a fault. Extended startup windows, fault counters, and RESET latch behavior depend on configuration; after power-up ADI's latch example needs two consecutive valid services, with a separate first-power-up exception [6, Extended Windows and RESETx Latch Feature].
- **Q&A algorithms are device-specific.** ADI's watchdog article uses x^8 + x^6 + x^5 + x^4 + 1 over I2C; TCAN1146 has configurable question generation, polynomial, and seed and requires four ordered answer writes per cycle. Do not transfer one device's polynomial or service sequence to another [6, Challenge/Response Watchdog; 7, pp.2-3].
- **Account for both clocks and scheduling jitter.** Service must occur after the latest possible CLOSED-window end and before the earliest possible watchdog expiration; an OPEN-window width alone does not define a valid schedule [6, Windowed Watchdogs].
- **Debug disable is device-specific.** ADM8613/ADM8614 have a WD_DIS input; verify the selected device's disable behavior before connecting the debug control [13, p.1].

## Common Mistakes

- **Capacitor on RESET without checking current and delay.** An asserted open-drain output sinks and discharges it [8, 10]. Check the discharge peak against the pin rating (5mA on TLV803 and TPS3808 [8, 9]) and the release delay as the pull-up recharges it (initial voltage 0V, leakage neglected): t = R_pu * C * ln(V_pu / (V_pu - V_IH)). A series resistor limits the peak but lifts the asserted low by R_series * pull-up current: check V_IL.
- **Watchdog error counters differ.** TCAN1146 decrements its counter on each successful cycle; ADI's double-fault windowed example needs two consecutive valid services to clear a single recorded fault. Configure the threshold and action for the exact part [7, p.3, §7.1; 6, Single/Consecutive WD Fault Counter].
- **Power-on glitch read as a release.** Below VPOR, do not rely on a valid reset state: TLV803 becomes high impedance below 1.1V, and MAX809 stops sinking below 1V [8, §8.3.2; 10, p.5]. A pull-up rail that comes up first, or logic with a low V_IH (a low-voltage FPGA or SRAM), sees a release while the supply is below threshold. Pull up to the monitored rail (the glitch then stays under VPOR), bring the monitored rail up first, or pick a lower-VPOR part. Push-pull (MAX809): 100K from RESET to ground holds it low down to 0V [10]; beside an open-drain pull-up it only divides (10K up, 100K down leaves 91%).
- **A 2x OPEN-window rule does not prove valid servicing.** An edge inside CLOSED is still a fault even if OPEN is very long; verify earliest/latest service against both window boundaries [6, Windowed Watchdogs].

## Formulas

**External hysteresis (TPS3808, nominal model) [5, pp.2-4]:**
**Rule of thumb:** SLVA360's Rh=1M, Rp=100K example provides about 200mV hysteresis only with its stated divider and V2=1.8V pull-up.
**Formula:** V1+ = Vs+ * (1 + R1/R2 + R1/Rh); V1- = Vs- * (1 + R1/R2 + R1/(Rh+Rp)) - V2 * R1/(Rh+Rp). Assume RESET=0V when asserted; include actual VOL, leakage, and tolerances for limits.
**Example:** Vs+=0.406V, Vs-=0.400V, R1=102K, R2=26.7K, Rh=1M, Rp=100K, V2=1.8V -> V1+=1.9984V, V1-=1.7983V, hysteresis=200.2mV. The falling-threshold expression must include Vs- * R1/(Rh+Rp).

## Sources

### Related Rules

- `mcus/fpga.md` -- FPGA power sequencing with voltage supervisors, vendor-specific rail-order requirements
- `power/ldo.md` -- LDO EN pin sequencing, PGOOD signal usage

### References

1. ADI -- High Performance Voltage Supervisors Explained, Part 1: https://www.analog.com/en/resources/analog-dialogue/articles/high-perf-volt-supervisors-explained-part-1.html
2. ADI -- How Voltage Supervisors Address Power Supply Noise and Glitches: https://www.analog.com/en/resources/analog-dialogue/articles/voltage-supervisors-address-power-supply-noise-and-glitches.html
3. ADI -- Choosing Supervisor Outputs (Open-Drain vs Push-Pull): https://www.analog.com/en/resources/technical-articles/choosing-supervisor-outputs.html
4. TI SLVA521 (March 2013) -- Setting the SVS Voltage Monitor Threshold: https://www.ti.com/lit/an/slva521/slva521.pdf
5. TI SLVA360 (August 2009) -- Adding Hysteresis to Supply Voltage Supervisor: https://www.ti.com/lit/pdf/slva360
6. ADI -- The Basics of Windowed Watchdogs (MAX20478/MAX20480): https://www.analog.com/en/resources/technical-articles/the-basics-of-windowed-watchdogs.html
7. TI SLLA546 (June 2021) -- Q&A Watchdog Overview and Configuration: https://www.ti.com/lit/pdf/slla546
8. TI TLV803 datasheet (SBVS157E): https://www.ti.com/lit/gpn/tlv803
9. TI TPS3808 datasheet (SBVS050N): https://www.ti.com/lit/gpn/tps3808
10. Analog Devices (Maxim) MAX803/MAX809/MAX810 datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/MAX803-MAX810Z.pdf
11. ADI MAX16140 family datasheet (19-100095 Rev 6, November 2019): https://www.analog.com/media/en/technical-documentation/data-sheets/MAX16140-MAX16142.pdf
12. TI TPS386000/TPS386040 datasheet (SBVS105F, October 2018): https://www.ti.com/lit/gpn/tps386000
13. ADI ADM8611-ADM8615 datasheet (Rev G, May 2021): https://www.analog.com/media/en/technical-documentation/data-sheets/adm8611_8612_8613_8614_8615.pdf
14. ADI ADM803/ADM809/ADM810 datasheet (Rev I, October 2014): https://www.analog.com/media/en/technical-documentation/data-sheets/ADM803_809_810.pdf
