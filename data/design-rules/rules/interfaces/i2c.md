# I2C Bus

> Pull-up sizing, bus capacitance budget, level shifting, bus recovery, off-board protection.

## Quick Reference

- **Pull-ups: 4.7 kohm default (100 kHz, <200 pF).** Use 2.2 kohm for 400 kHz or >200 pF. Calculate from formulas below when bus capacitance is known.
- **Max bus capacitance: 400 pF** (Standard/Fast). Budget ~10 pF/device + 0.5 pF/cm trace + 80 pF/m cable.
- **Level shift: BSS138 N-MOSFET** (SOT-23). Gate to lower VDD, source to low side, drain to high side. Pull-ups on both sides. Standard/Fast mode only.
- **Hung bus: 9 clock pulses on SCL** before every I2C peripheral init on boot.
- **Off-board protection: Wurth 742792693 ferrite + 824012823 TVS** per line. Ferrite impedance below 10 MHz is negligible vs kohm pull-ups -- no effect on rise time (verified by simulation and measurement).

## Design Rules

### Pull-Up Resistor Selection

- **Minimum Rp (sink current limit):** Rp_min = (VCC - 0.4V) / IOL. Standard/Fast IOL = 3 mA: at 3.3V -> 967 ohm, at 5V -> 1.53 kohm. Fast Plus IOL = 20 mA: at 3.3V -> 145 ohm. Going below Rp_min prevents the output from pulling SDA/SCL below VOL_max.
- **Maximum Rp (rise time limit):** Rp_max = tr / (0.8473 * Cb). The 0.8473 comes from RC charging between 0.3*VCC and 0.7*VCC.
- **If Rp_max < Rp_min, the bus cannot meet timing.** Reduce capacitance (fewer devices, shorter traces, add a buffer) or lower the clock frequency.
- **Speed vs power trade-off:** within the valid range, lower Rp = faster edges but more power; higher Rp = lower power but slower edges. Pick based on whether your design is power-constrained or speed-constrained.

> WARNING: If calculated Rp_max < Rp_min, the bus is overloaded. No pull-up value will work -- you must reduce bus capacitance or lower clock speed.

### Bus Buffering and Multiplexing

- **Buffers (PCA9515, TCA9517):** isolate capacitance. Each side gets independent 400 pF budget. Also provide level translation.
- **Multiplexers (PCA9544, 4-ch):** solve address conflicts by enabling one downstream channel at a time. Only one channel active at once.
- **Switches (PCA9548, 8-ch):** can enable multiple channels simultaneously but do NOT isolate capacitance. All active channels sum into total bus load.
- **Do not cascade TCA9517 in A-B B-A topology.** B-side static voltage offset prevents proper logic-low recognition on the second device. PCA9518 hub solves this with inter-device signaling.

### Level Shifting

- **BSS138 MOSFET level shifter works for Standard and Fast mode (up to 400 kHz).** Not suitable for High-Speed mode (3.4 MHz) -- FET switching is too slow.
- **VDD2 must equal or exceed VDD1 in normal operation.** VDD2 < VDD1 is only acceptable during power sequencing transitions.
- **IC translators:** PCA9306, TCA9406 for level-only. PCA9548 also provides translation between sides.
- General level-shifting topology selection -> `misc/level-shifting.md`.

### Hung Bus Recovery

- **Root cause:** master reset during a read. Slave holds SDA low waiting to clock out the next bit. I2C peripheral register writes cannot clear this.
- **Software fix: master pulses SCL up to 9 times.** After each pulse, check SDA. When SDA releases, issue STOP. No adverse effect on other slaves -- they are not being addressed.
- **Hardware fix: ADG749 analog switch** (SC70, break-before-make, 3.5 ohm Ron at 5V) between VDD and slave power pin. 15 us reset pulse discharges 1 uF decoupling + 2 slaves to <0.1V. Slave I2C state machine resets on power-up.
- **Run 9-clock recovery on every boot** before initializing the I2C peripheral. Costs nothing, prevents the most common I2C failure mode.

### Off-Board Protection

- **Ferrite + TVS on each line for off-board I2C.** Ferrite: Wurth 742792693 (WE-CBF, Z = 2.2 kohm at 100 MHz, 0603). TVS: Wurth 824012823 (WE-TVS SuperSpeed, 0.18 pF, DFN1210, 3.3V).
- **Ferrite does not degrade signal quality.** Simulation and measurement at 400 kHz with 400 pF bus show identical rise times with and without the 742792693. The ferrite's sub-10 MHz impedance is negligible compared to kohm pull-ups.
- **During ESD events, >10 A flows briefly** through TVS protection diodes, leaving ~10V residual. All ICs on the bus must withstand this -- requires low-impedance ground (large copper pour on inner layer) to avoid further voltage rise.
- **Bus length limited by capacitance.** At ~80 pF/m, 400 pF budget gives ~5 m max. For longer: P82B715 (50 m at 85 kHz over 50 ohm coax/twisted pair), P82B96 (100 m at 71 kHz, 1 km at 31 kHz).
- ESD protection placement and design -> `protection/esd.md`.

### Hot Insertion

- **I2C was not designed for live insertion.** Plugging a device into an active bus pulls SDA/SCL low momentarily through the device's input protection diodes.
- **Hot-swap buffers (PCA9511/12/13/14):** start in Hi-Z, monitor bus for STOP or idle, connect only when bus is idle. Required for backplane and modular designs. PCA9511 has ENABLE + READY pins; PCA9512 is pin-compatible without ENABLE.

### Address Conflicts

- **Hardware strap pins first.** Many devices offer 1-3 address pins (2-8 addresses). Some (BME280: 0x76/0x77 only) have insufficient options.
- **PCA9548 switch or PCA9544 mux** when strap pins are exhausted. PCA9548 can enable multiple channels -- verify no address overlap across enabled channels.

### SMBus Interop

- **SMBus 35 ms timeout resets all devices if communication stalls.** Firmware must complete transactions within this window. Prevents permanent hung-bus but adds a real-time constraint.
- **SMBus fixed thresholds (0.8V / 2.1V) are only safe for I2C interop when VCC >= 3.0V.** Below 3.0V, VIH may not be met -- use I2C-native thresholds (0.3*VCC / 0.7*VCC) instead.

### Layout

- **Pull-ups close to the master** (or central bus point). Pull-ups at the far end add unnecessary RC delay.
- **No series resistors on I2C lines.** Open-drain with pull-ups means series resistors create voltage dividers and corrupt logic levels.
- **ESD components close to the connector,** not near the IC -> `protection/esd.md`.

## Common Mistakes

- **Oscilloscope probe pushes bus over capacitance limit.** A 10x passive probe adds ~10 pF per channel. On a bus near 400 pF, probing SDA+SCL adds 20 pF -- circuit works with probe, fails without (or vice versa). Fix: use active probes (<1 pF) for marginal buses, or budget probe capacitance during debug.
- **Pull-ups on both sides of BSS138 level shifter too strong.** At 1 kohm pull-up on 5V side with SDA low, ~5 mA flows through the FET continuously. Within abs max but shifts VOL upward, possibly exceeding 0.4V threshold. Fix: calculate Rp_min for each side independently using that side's VCC and IOL.
- **Mixed-speed devices on same bus segment.** A 100 kHz-only device cannot handle 400 kHz transactions -- it may interpret bus activity as valid data and corrupt its internal state. Fix: PCA9515 buffer to isolate fast and slow segments.

## Formulas

**Minimum pull-up resistance:**
**Rule of thumb:** 1 kohm at 3.3V, 1.5 kohm at 5V.
**Formula:** Rp_min = (VCC - VOL) / IOL
  - VOL: 0.4V (VCC > 2V), 0.2*VCC (VCC <= 2V)
  - IOL: 3 mA (Standard/Fast), 20 mA (Fast Plus)
**Example:** VCC = 3.3V, Fast mode -> (3.3 - 0.4) / 0.003 = 967 ohm -> use 1 kohm minimum.

**Maximum pull-up resistance:**
**Rule of thumb:** 4.7 kohm for Standard mode, 2.2 kohm for Fast mode.
**Formula:** Rp_max = tr / (0.8473 * Cb)
  - tr: 1000 ns (Standard), 300 ns (Fast), 120 ns (Fast Plus)
**Example:** Fast mode, Cb = 200 pF -> 300e-9 / (0.8473 * 200e-12) = 1.77 kohm -> use 1.8 kohm.

**Bus capacitance estimate:**
**Rule of thumb:** 10 pF/device + 0.5 pF/cm trace + 80 pF/m cable.
**Formula:** Cb = N * C_device + L_trace_cm * 0.5 + L_cable_m * 80 (all in pF)
**Example:** 8 devices, 20 cm trace, no cable -> 80 + 10 + 0 = 90 pF. Well within 400 pF.

## Sources

### Related Rules

- `misc/level-shifting.md` -- level-shifting topology selection for I2C and other interfaces
- `protection/esd.md` -- ESD protection placement and design for off-board connections

### References

1. TI SLVA689 -- I2C Bus Pullup Resistor Calculation: https://www.ti.com/lit/pdf/slva689
2. SparkFun -- I2C Tutorial: https://learn.sparkfun.com/tutorials/i2c
3. NXP AN10216 -- I2C Manual: https://www.nxp.com/docs/en/application-note/AN10216.pdf
4. Nexperia AN10441 -- Level Shifting Techniques in I2C-bus Design: https://assets.nexperia.com/documents/application-note/AN10441.pdf
5. TI SLVA787 -- Choosing the Correct I2C Device: https://www.ti.com/lit/an/slva787/slva787.pdf
6. Wurth ANP121 -- Filter and Surge Protection for I2C Bus: https://www.we-online.com/components/media/o734709v410%20ANP121a%20%20Filter%20and%20surge%20protection%20for%20I2C%20Bus%20EN.pdf
7. ADI AN-686 -- Implementing an I2C Reset: https://www.analog.com/media/en/technical-documentation/application-notes/54305147357414AN686_0.pdf
