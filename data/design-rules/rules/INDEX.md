# Design Rules Index

## Rule Files

### Guides — read before designing

| File | What It Covers |
|------|----------------|
| `guides/passives.md` | Selecting R, C, L — voltage derating, tolerance, dielectrics, packages |
| `guides/connectors.md` | Connector family selection — JST SH/PH/XH, USB, terminal blocks, current ratings |
| `guides/power-architecture.md` | Multi-rail planning, LDO vs buck decision, sequencing, inrush, PMIC vs discrete |
| `guides/thermal.md` | Thermal estimation (theta-JA vs psi-JT), package limits, heatsink sizing, transient thermal (Zth) |
| `guides/schematic-practices.md` | Schematic readability, net naming, hierarchical design, sheet organization |
| `guides/checklist.md` | Pre-build review — catches common omissions |
| `guides/pcb-layout.md` | Ground planes, return paths, stackup, trace width, vias, thermal relief |
| `guides/signal-integrity.md` | Transmission lines, reflections, termination, crosstalk, differential pairs |
| `guides/emc.md` | EMC/EMI fundamentals, filtering, shielding, SMPS hot loops |
| `guides/dfm.md` | Manufacturing constraints, fab tolerances, DFA, IPC classes, panelization |
| `guides/test-debug.md` | Test points, debug headers (SWD/JTAG), current shunts, ICT/flying probe, board bring-up |

### Interfaces

| File | What It Covers |
|------|----------------|
| `interfaces/i2c.md` | Pull-up calculation, bus capacitance, speed modes |
| `interfaces/spi.md` | Clock modes, CS timing, multi-device buses |
| `interfaces/uart.md` | Level matching, flow control, RS-232/TTL |
| `interfaces/usb.md` | USB 2.0 D+/D- routing, USB-C CC resistors, power delivery, VBUS power path |
| `interfaces/can.md` | CAN 2.0/FD physical layer, transceiver selection, termination, PCB layout, ESD |
| `interfaces/ethernet.md` | Ethernet PHY layout, magnetics, Bob Smith termination, PoE PD, EMC |

### Power

| File | What It Covers |
|------|----------------|
| `power/decoupling.md` | Per-IC ceramics, bulk caps, ESL by package, via inductance, BGA strategy, anti-resonance |
| `power/ldo.md` | Dropout, ESR stability, PSRR, noise (NR pin), thermal limits, nano-Iq battery |
| `power/switching.md` | Buck/boost/buck-boost/flyback topology, inductor sizing, MOSFET selection, loop compensation, layout |
| `power/battery-chemistry.md` | LiPo/Li-ion/LiFePO4/NiMH comparison, voltage curves, C-rates, aging, safety, form factors, primary cells |
| `power/battery.md` | CC/CV charging ICs, NTC thermistor, protection (DW01/8205A), BMS AFE, fuel gauge (coulomb counting, Impedance Track), cell balancing |
| `power/power-path.md` | USB + battery coexistence, ideal diodes, ship mode, solar MPPT, charger IC selection, load switching |

### Protection

| File | What It Covers |
|------|----------------|
| `protection/esd.md` | TVS selection (unidirectional vs bidirectional), clamp voltage calculation, trace routing, IEC 61000-4-2 |
| `protection/reverse-polarity.md` | P-FET vs Schottky vs ideal diode controller |
| `protection/voltage-supervisor.md` | Reset ICs, brown-out detection, threshold hysteresis, watchdog (timeout/windowed/Q&A) |
| `protection/isolation.md` | Digital isolators vs optocouplers (CTR aging), creepage/clearance, stitching capacitance, isolated power |

### MCUs

| File | What It Covers |
|------|----------------|
| `mcus/esp32.md` | Strapping pins, power, RF, USB-JTAG (per-chip: C3, S3, C6) |
| `mcus/stm32.md` | Boot config, reset circuit, HSE crystal |
| `mcus/rp2040.md` | External flash, USB boot, 1.1V core power |
| `mcus/fpga.md` | FPGA power sequencing, BGA decoupling, configuration flash, IO banking, SERDES, clock distribution |

### Misc

| File | What It Covers |
|------|----------------|
| `misc/crystal.md` | Load cap calculation, stray capacitance, drive level |
| `misc/level-shifting.md` | Voltage translation topologies, speed vs method |
| `misc/mosfet-circuits.md` | MOSFET selection, gate drive, load switches, relay coil suppression, TEC/Peltier drivers, paralleling |
| `misc/rf-antenna.md` | Keep-out zones, matching networks, module placement, sub-GHz LoRa/ISM, GNSS antennas, 24 GHz mmWave, ADS-B 1090 MHz |
| `misc/op-amp-basics.md` | Selection, common circuits, single-supply biasing, sensor conditioning |
| `misc/adc-dac.md` | Signal conditioning, anti-aliasing filters, sampling theory, mixed-signal layout |
| `misc/gnss-integration.md` | GNSS module integration, active/passive antennas, ground plane sizing, LNA bias-tee power, PPS signal routing |
| `misc/ev-power-systems.md` | High-voltage DC (48-800V), precharge, contactor drivers (pickup/hold profiles), wire sizing, fusing, insulation monitoring |
| `misc/motor-control.md` | BLDC gate drivers (DRV83xx), 3-phase layout, bootstrap, current sensing, stepper drivers (TMC2209 StallGuard4/CoolStep, A4988) |
| `misc/audio.md` | I2S interface, audio codec integration, Class D amplifier layout, MEMS microphones, DAC output stage |
