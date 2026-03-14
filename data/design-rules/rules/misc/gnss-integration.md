# GNSS Module Integration

> When integrating a GNSS module -- antenna selection, ground plane sizing, RF path, LNA power, backup battery, PPS routing.

## Quick Reference

- **Ground plane: minimum 50x50mm for a 25x25mm patch.** Below 40x40mm, performance degrades significantly. 70x70mm gives optimal patch gain.
- **Active antenna for any cable > 10cm.** Cable loss at L1 (1575 MHz): RG174 ~0.5dB/m, RG316 ~0.8dB/m, RG178 ~1.1dB/m. Active LNA gain: 15-26dB for u-blox receivers; above 35dB with short cable, receiver overloads.
- **Backup battery on V_BCKP enables hot/warm start.** Without it, every power cycle is cold start (~30s TTFF vs ~1s hot). CR2032 or ML2032 rechargeable.
- **Keep-out zone: no components within 10mm of patch antenna edges.** Tall components (h > 3mm) must be >= 10mm away. Enclosure/cover >= 5mm clearance.
- **Recommended modules:** u-blox SAM-M8Q (integrated patch, 15.5x15.5mm), u-blox NEO-M9N (multi-band), Quectel L76-L (low power, 10.1x9.7mm), Quectel LC29H (RTK-capable).

## Design Rules

### Antenna Selection

| Antenna Type | Gain (dBic) | Ground Plane Req | Best For |
|-------------|-------------|-----------------|----------|
| 25x25mm ceramic patch | 4-5 | 70x70mm optimal, 50x50mm min | Roof/dashboard mount, best performance |
| 18x18mm ceramic patch | 2-3 | 50x50mm min | Space-constrained with decent GP |
| Chip antenna (3.2x1.6mm) | -1 to +1 | 80x40mm min, highly GP-dependent | Consumer electronics, non-critical nav |
| Quadrifilar helix | 2-4 | Less GP-dependent | Multi-orientation, vehicle tracking |

- **Patches < 17x17mm show moderate navigation performance.** Smaller aperture = less signal energy. Amplifying after the antenna does not improve SNR.
- **Chip antennas have 3dB loss vs patch/helix** due to linear polarization (GNSS signals are RHCP). Average C/N0 on 80x40mm PCB: 43.4 dBHz. On 24x15mm PCB: only 34.7 dBHz -- marginal for navigation. Not recommended where positioning is essential.
- **Ceramic patch resonant frequency depends on dielectric and ground plane.** Conformal coating or potting shifts resonant frequency and voids antenna module warranty (SAM-M8Q).

### Ground Plane Design

- **SAM-M8Q: optimized for 50x50mm ground plane center mount.** Below 40x40mm, performance decreases significantly. Use at least one full copper layer for ground.
- **For external patch: 70x70mm ground plane gives peak gain** from a 25x25mm patch. Undersized planes tilt the radiation pattern and reduce gain toward zenith.
- **Route signal traces away from the module on the top layer.** Layer swaps (top to bottom) > 20mm from the module edge.

### Active Antenna Power (Bias-Tee)

- **DC supply via coax center conductor.** RF choke (100nH, Murata LQG15HS) blocks RF from DC supply path. Decoupling cap (1nF) at LNA Vcc pin filters residual RF.
- **LNA BOM: NXP BGU7004/BGU7008.** NF = 0.85-0.9dB, gain = 16.5-18.5dB, 1.5-2.85V optimized at 1.8V, 4.5-4.8mA. Input matching: one external inductor (5.6nH, Murata LQW15A). Integrated input/output DC blocking -- no external blocking caps needed.
- **Active antenna current draw: 3-20mA typical.** u-blox modules with integrated bias-tee (MAX-M8Q, NEO series) limit supply current and detect antenna short/open.
- **Antenna supervisor for fault detection.** u-blox AADET_N pin monitors supply current (open = 0mA, normal = 5-15mA, shorted = >50mA). Quectel L76 uses 10 ohm series resistor on VDD_RF for short protection.
- **ESD on antenna port:** NXP PESD5V0F1BL TVS increases system ESD from 2kV to 10kV HBM.
- **SAW filter before LNA when cellular transmitter co-located.** Epcos B9444 or B7839, Murata. GSM transmits up to +33dBm peak -- can exceed GNSS module RF_IN absolute max.

### Module Integration

- **VCC supply: low impedance, < 0.2 ohm.** No series resistors, no ferrite beads, no inductors in VCC line. Peak current during backup-to-normal transition exceeds steady-state operating current.
- **V_BCKP:** maintains RTC and BBR for hot/warm start. Connect to VCC_IO if no backup battery. Avoid high resistance on V_BCKP line -- current spike during supply switchover causes voltage drop and malfunction.
- **VCC_IO sets I/O logic level.** Without VCC_IO, module stays in reset. Connect to VCC for single-supply designs.
- **RESET_N: do not add capacitance to GND** (causes false reset at startup). Leave open if unused. Do not drive high -- input only.
- **I/O lines > 3mm act as antennas at L-band.** Add ferrite beads (Murata BLM15HD102SN1) or series resistors (> 20 ohm) on UART, I2C lines close to the module pin. Prevents in-band interference from digital switching coupling into the GNSS antenna.

### PPS (Pulse Per Second) Signal

- **Accuracy (u-blox LEA-6T): 30 ns RMS without compensation, 15 ns with quantization error compensation** (UBX-TIM-TP message provides nanosecond quantization error for each pulse).
- **Time pulse derived from 48 MHz internal clock.** Integer divisors (e.g., 8 MHz = 48/6) avoid quantization jitter. Non-integer divisors (e.g., 10 MHz) add edge jitter from clock rounding.
- **For improved phase noise: add external PLL.** Lock external TCXO or OCXO to PPS for holdover and clean spectrum. The 48MHz-derived pulse is not designed for low phase noise.
- **Cable delay compensation:** RG174: 5.26 ns/m; RG316: 5.05 ns/m. A 10 m RG174 cable = 52.6 ns offset. Configure in UBX-CFG-TP5 user delay field. Calibrate against reference PPS if sub-50 ns accuracy needed.

### Interference Management

- **In-band interference (near 1575MHz):** display harmonics (e.g., 315 MHz * 5 = 1575 MHz), MCU clocks (e.g., 26 MHz * 60.6), SDRAM bus switching.
- **>= 20dB isolation between GNSS and cellular antennas.** If insufficient, add SAW filter on GNSS RF input.
- **Shield the GNSS module** if co-located with wireless transmitters. Feed-through capacitors (Murata NFL18SP157X1A3, 34pF) on I/O lines penetrating the shield.

## Common Mistakes

- **Ground plane too small for chip antenna.** A chip antenna on 24x15mm PCB averages 34.7 dBHz C/N0 -- below 44 dBHz minimum for reliable navigation. Same chip on 80x40mm: 43.4 dBHz. Either use larger PCB or switch to patch/helix with adequate ground plane.
- **Conformal coating or potting over patch antenna.** Changes dielectric environment, shifts resonant frequency. Module manufacturer explicitly voids warranty. Leave antenna area exposed or use window in coating.
- **No backup battery -- every power cycle is cold start.** Cold start TTFF ~26-30s. Hot start with valid ephemeris: ~1s. For frequent power cycles (vehicle tracking, wearables), backup battery pays for itself in user experience.
- **Ultrasonic cleaning after soldering.** Permanently damages quartz oscillators inside the GNSS module. Use no-clean solder paste and skip cleaning. Do not apply ultrasonic welding near the module.
- **Digital signal traces routed under or near the module.** SPI clock, I2C, UART lines under the module radiate directly into the antenna. Even 3mm of unshielded trace acts as antenna at L-band. Route all signals away on top layer, use inner layers only > 20mm from module edge.

## Formulas

**GNSS link budget (simplified):**
**Rule of thumb:** Minimum C/N0 for navigation: 44 dBHz. Typical GPS L1 signal at ground: -130 dBm.
**Formula:** C/N0 = P_rx + G_ant - NF + 174 (dBHz)
**Example:** P_rx = -130 dBm, G_ant = 3 dBi (patch), NF = 1.5 dB (SAW+LNA) -> C/N0 = -130 + 3 - 1.5 + 174 = 45.5 dBHz. Margin: 1.5 dB above minimum -- tight, add LNA gain or improve antenna.

## Sources

### Related Rules

- `misc/rf-antenna.md` -- General RF antenna design, impedance matching, keep-out zones

### References

1. u-blox GNSS Antennas Application Note UBX-15030289: https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_%28UBX-15030289%29.pdf
2. u-blox SAM-M8Q Hardware Integration Manual UBX-16018358: https://content.u-blox.com/sites/default/files/SAM-M8Q_HardwareIntegrationManual_%28UBX-16018358%29.pdf
3. Quectel L76 Hardware Design V3.3: https://centerclick.com/ntp/docs/Quectel_L76L76-L_Hardware_Design_V3.3.pdf
4. SparkFun GPS-RTK2 Hookup Guide: https://learn.sparkfun.com/tutorials/gps-rtk2-hookup-guide/all
5. ArduSimple -- Understanding GPS Timepulse or PPS: https://www.ardusimple.com/understanding-gps-timepulse-or-pps/
6. LXAntenna -- How to Power an Active GPS Antenna: https://lxantenna.com/how-to-power-an-active-gps-antenna/
7. NXP AN11420 -- GPS LNA Voltage Supply via Coax Cable: https://www.nxp.com/docs/en/application-note/AN11420.pdf
8. Wurth ANR017 -- GNSS Antenna Selection Guide: https://www.we-online.com/components/media/o171079v410%20ANR017_GNSS_Antenna.pdf
9. u-blox GPS-based Timing Application Note GPS.G6-X-11007: https://content.u-blox.com/sites/default/files/products/documents/Timing_AppNote_%28GPS.G6-X-11007%29.pdf
