# Test and Debug

> Test point sizing and placement, debug connectors, current shunt Kelvin sensing, DFT guidelines, board bring-up procedure.

## Quick Reference

- **Bed-of-nails test pads: >= 0.8 mm, 1.0 mm preferred, no solder mask, no paste** [7]. Match the size to the probes; flying-probe and ICT can use smaller [4]. All test points on one side of the board.
- **ARM 10-pin Cortex debug connector (1.27 mm pitch)** is the standard for SWD. Tag-Connect TC2030-IDC saves board space (pogo pads, zero height).
- **Current shunt without Kelvin sensing: 22.8% error** in ADI's 0.5 mohm, 20 A test; its best Kelvin layouts measured 0.6-1%, others up to 5% [3]. Details and conditions below.
- **Board bring-up: scope on rails, not DMM.** DMM averages out oscillation and noise. Before first power, compare rail-to-GND readings with the expected load or a known-good board, and current-limit the first power-up [2, 10].
- **2.54 mm (100 mil) test grid spacing** for ICT. 1.27 mm (50 mil) costs 4x and reduces probe reliability.

## Design Rules

### Test Point Design

- **No solder paste on test pads** -- paste residue degrades probe contact after reflow (pad size: Quick Reference).
- **Spacing: 2.54 mm (100 mil) grid preferred.** 1.91 mm (75 mil) acceptable. 1.27 mm (50 mil) costs 4x and reduces probe durability.
- **Single-sided probing** (fewer-component side). Reduces fixture cost by half or more.
- **Route unused MCU pins to test pads** for firmware debug and greenwire patches.
- **Untented vias as emergency test points.** Leave test-critical vias without solder mask for probing when dedicated test pads are impractical.
- **Keystone 5018 SMT test points** for prototypes. Ring allows secure clip mounting. Mark as DNP for production -- pad remains as ICT contact.

### Flying Probe Test (FPT)

- **FPT minimum pad: 0.5 mm (20 mil) recommended, 0.15 mm (6 mil) absolute minimum.**
- **Probe-to-sensor gap: 2.8 mm** for SEICA single-sided horizontal flying probe; vertical and double-sided testers differ [4].
- **Board support every 150 mm** to prevent flex during probing -- unsupported areas cause false failures on large boards.
- FPT needs no custom fixture -- ideal for prototypes and low volume. ICT is faster for volume > ~500 boards.

### In-Circuit Test (ICT)

- **Pad diameter by board size:** boards < 300 mm: 0.7 mm recommended (0.6 mm min). Boards > 300 mm: 0.9 mm recommended (0.7 mm min).

| Grid | Nail Pitch | Min Interaxis | Relative Cost |
|------|-----------|---------------|---------------|
| P100 | 2.54 mm (100 mil) | 2.1 mm | 1 (baseline) |
| P75 | 1.91 mm (75 mil) | 1.7 mm | 2 |
| P50 | 1.27 mm (50 mil) | 1.25 mm | 4 |

- **No test points under BGAs.** Nail pressure damages solder joints. Leave >= 5.08 mm (200 mil) gap on all BGA sides.
- **Locating holes:** 2.7 mm +/-0.05 mm diameter, non-metalized, >= 3 mm from board edge. Solder mask clearance: 0.3 mm around locating holes.
- **Component clearance to test point:** 0.7 mm for parts < 2 mm tall, 1.91 mm for parts > 4 mm tall.

### Debug Connectors

**ARM Cortex 10-pin (1.27 mm pitch, SWD + JTAG):**

| Pin | Signal | Pin | Signal |
|-----|--------|-----|--------|
| 1 | VCC | 2 | SWDIO / TMS |
| 3 | GND | 4 | SWDCLK / TCK |
| 5 | GND | 6 | SWO / TDO |
| 7 | KEY (no pin) | 8 | NC / TDI |
| 9 | GNDDetect | 10 | nRESET |

- **10-pin is the default** for Cortex-M. Pin 7 is keying (no physical pin). SWD uses 2 pins (SWDIO + SWCLK); add SWO for printf-style trace. Connector: Samtec FTSH-105-01-L-DV-K (shrouded) or FTSH-105-01-L-DV (unshrouded).
- **20-pin adds ETM trace** (TRACECLK + TRACEDATA[0:3]) for cycle-accurate profiling or code coverage.
- **Tag-Connect TC2030-IDC:** 6-pin pogo-pad footprint, zero board-side height. No-legs variant for production (exposed pads only). May need a custom adapter board to your debug probe.
- **SWJ-DP defaults to JTAG on reset.** Debug probes send a 50-bit switching sequence to enter SWD mode. If firmware reconfigures SWD pins as GPIO before the probe connects, the switching sequence never reaches the DAP -- debugger is locked out. Fix: preserve SWD on reset, or add a physical boot-mode jumper that holds the chip in reset until the probe attaches.
- **Debug probe selection:** If open-source + driver-free: CMSIS-DAP/DAPLink (USB HID, works everywhere). If widest device support or commercial project needing vendor support: J-Link (proprietary, fastest flash programming). If STM32-only and cost matters: ST-Link (bundled with Nucleo/Discovery boards).
- **GDB server selection:** If Cortex-M only + need scriptable target introspection (register dumps, RTOS-aware threading): pyOCD (Python, ARM-maintained). If multi-arch (RISC-V, MIPS) or unusual/mixed probe setups: OpenOCD (17+ adapter types). If using J-Link hardware: J-Link GDB Server (most reliable with J-Link probes, but opaque when it fails).

### Current Shunt Kelvin Sensing

- **ADI's test: Welwyn ULRG3-2512-0M50-FLFSLT (0.5 mohm 2512), 20 A, 25 C, sampled within 1 s.** Without Kelvin it read 12.28 mV for 10 mV ideal (22.8%; about 0.11 mohm of solder and copper in series) [3].
- **Sense vias at the outer edge of each pad worked best for that resistor.** ADI Table 1: layout C (outer edge, separate sense layer) measured 1%, D 0.6%; C tolerates placement better [3]. ADI says results depend on resistor composition and size: check the shunt maker's recommended footprint.
- **Route sense traces on a different layer** from the power path. Vias at pad edges reach the sense layer without cutting main current-carrying copper.

**Parallel shunts (from TI SDAA115):**
- **Individual Kelvin sense from each shunt is mandatory.** Sensing from only one shunt (Layout 1) gives 56.5 mV offset. From center shunt (Layout 2) gives 51.2 mV offset. From all shunts (Layout 3): 1.7 mV offset on 397 mV expected.
- **Parallel shunts: series resistors in each Kelvin loop >= 100 * R_shunt** (TI's INA190 example). Without them, hundreds of mA circulate between sense loops. Check the amplifier's input-bias error with the chosen value [8, sec.2].
- **Match trace length and width to every shunt** for even current sharing. Diagonal current paths (TL-BR or TR-BL) give best results -- avoid same-side paths (TR-BR, TL-BL) which create asymmetric drops.

### Board Bring-Up Procedure

1. **Visual inspection** (both sides). Check pin 1 orientation, solder bridges, tombstoned passives, blown packages, bad barrel fill on THT.
2. **Power rail resistance (board OFF).** Each rail to GND. Normal depends on the load: 20-25 ohm needn't alarm; about 5 ohm or less, investigate a short [2]. Compare with a known-good board.
3. **Apply power with current-limited supply.** Start low, increase while monitoring. Touch components for excessive heat.
4. **Measure rails with oscilloscope** (not multimeter). Scope reveals oscillation and noise that a DMM averages out.
5. **Check reset signal.** If stuck, trace what holds it asserted (supervisor, watchdog, external pull-down).
6. **Connect debug probe.** Verify processor ID and SWD/JTAG communication.
7. **Enable peripherals one at a time** (UART, SPI, I2C, USB). Test individually before enabling all simultaneously.
8. **Monitor thermal behavior under load** -> `guides/thermal.md`.

### Prototype Design-for-Debug

- **Sub-system isolation:** zero-ohm resistors or jumpers between subsystems. Allows testing sections independently and bypassing failed supplies with lab power. Place on power rails, not signal paths.
- **Swaperoo resistors:** zero-ohm on UART TX/RX for easy swap if lines are crossed.
- **Indicator LEDs on power rails** through a jumper so LEDs can be disconnected for accurate current measurement.
- **Board version ID readable in firmware.** ADC resistive divider on a spare GPIO pin -- different resistor values per revision. Enables software to detect board version and adapt pinout/behavior. Cheaper and more reliable than GPIO straps for > 4 versions.

## Common Mistakes

- **ICT fixture probe hits component body instead of pad.** Tall components near test points shadow the probe at approach angle. Fix: maintain >= 1.91 mm clearance from test pads to any component > 4 mm tall.
- **Copying ADI's outer-edge pickup to a different shunt.** ADI's results are for one 2512 metal shunt; composition and size change them. Fix: use the shunt maker's Kelvin footprint [3].
- **Parallel shunt array sensed from only one resistor.** TI SDAA115 shows sensing from nearest shunt (Layout 1) adds 56.5 mV offset to a 397 mV expected output. Sensing from center shunt (Layout 2) still adds 51.2 mV. Fix: individual Kelvin from each shunt with >= 100x series limiting resistors.
- **Solder paste on test point pads.** Residue from reflow degrades probe contact reliability over production life. Fix: exclude test points from paste layer.

## Formulas

**FPT probe clearance from tall component:**
**Rule of thumb:** 1 mm for < 2 mm tall parts. 2 mm for 4 mm tall. Scales linearly.
**Formula:** L = (0.29 * H) + 0.7, where H = component height (mm), L = clearance (mm)
**Example:** 6 mm electrolytic cap -> L = (0.29 * 6) + 0.7 = 2.44 mm clearance from pad edge.

**Parallel shunt Kelvin current-limiting resistor:**
**Rule of thumb:** R_limit >= 100 * R_shunt (TI's INA190 example) [8, sec.2].
**Example:** Three parallel 300 uohm shunts -> R_limit >= 30 mohm; add margin only within the amplifier's input-bias error budget.

## Sources

### Related Rules

- `guides/thermal.md` -- Monitoring thermal behavior under load during bring-up

### References

1. MacroFab -- Improve Your Next PCB Prototype: Better Debugging, Testing, and Reliability: https://www.macrofab.com/blog/improve-pcb-prototype/
2. Practical EE -- Bringup: https://practicalee.com/bringup/
3. ADI -- Optimize High-Current Sensing Accuracy by Improving Pad Layout of Low-Value Shunt Resistors: https://www.analog.com/en/resources/analog-dialogue/articles/optimize-high-current-sensing-accuracy.html
4. Sierra Circuits -- Design for Testing (DFT) Guidelines for PCB Manufacturing: https://www.protoexpress.com/blog/design-for-testing-guidelines-pcb-manufacturing/
5. ARM -- Cortex-M Debug Connectors (10-pin and 20-pin pinouts): https://documentation-service.arm.com/static/5fce6c49e167456a35b36af1
6. Memfault -- A Deep Dive into ARM Cortex-M Debug Interfaces: https://interrupt.memfault.com/blog/a-deep-dive-into-arm-cortex-m-debug-interfaces
7. FixturFab -- Basic PCBA Design for Test (DFT) Guide: https://www.fixturfab.com/articles/basic-pcba-design-test-dft-guide
8. TI SDAA115 -- Optimal Layout Practices for Low-Ohmic Current Sense Resistors in Parallel: https://www.ti.com/lit/an/sdaa115/sdaa115.pdf
9. Altium -- Checklist for Systematically Testing PCB Prototypes: https://resources.altium.com/p/checklist-systematically-testing-pcb-prototypes
10. grosdode/PCB-design -- Prototyping & Bring-up Checklist: https://raw.githubusercontent.com/grosdode/PCB-design/main/PCB_Checklist/pcb_checklist.md
