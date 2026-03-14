# SPI Bus

> Series termination, CS timing, multi-device topologies, Quad SPI flash, level translation.

## Quick Reference

- **Series resistor: 22-33 ohm at the driver** on SCLK, MOSI, CS. MISO resistor goes at the slave (it drives MISO), not the master.
- **Pull-up on CS#: 4.7 kohm to VCC.** Keeps slave deselected during power-up and when controller pins float.
- **10% rise-time rule for impedance control:** if trace propagation delay < 10% of rise time, no impedance control needed. At 10 ns rise time on FR4 stripline (~150 mm/ns), threshold is 150 mm.
- **Quad SPI flash: QE bit must be set before quad I/O.** WP# and HOLD# become IO2/IO3 -- hardware write protection is lost.

## Design Rules

### Series Termination

- **22-33 ohm at the driver, within 6 mm (250 mil) of the output pin.** On short buses: damps ringing. On electrically long buses: also provides impedance matching (R_series = Z0 - Z_driver).
- **MISO resistor placement is at the slave.** The slave drives MISO. Placing the resistor at the master leaves the full trace unterminated -- ringing reflects off the master-side resistor instead of being absorbed at the source.
- **CMOS driver output impedance is typically 10-30 ohm.** For 50 ohm trace with ~20 ohm driver: use 33 ohm (nearest E24). Microchip CEC1702 reference: 25 ohm at MCU, 45 ohm at flash, 4.7 kohm pull-up on CS#.
- **FPGAs can have <1 ns rise times even at low SPI clock rates.** Series termination is mandatory regardless of clock frequency -- the rise time, not the data rate, determines signal integrity.

### When Impedance Control Matters

- **10% rise-time rule:** if one-way propagation delay < 10% of signal rise time, trace is electrically short. No impedance control needed.
- **FR4 stripline propagation: ~150 mm/ns. Microstrip: ~170 mm/ns.** At 10 ns rise time -> critical length = 150 mm (stripline). Most on-board SPI routes are well under this.
- **If impedance control is needed, use 50 ohm.** Microchip specifies 50 ohm +/-15% for SPI flash at 50 MHz. This also matches other controlled-impedance nets on the board, simplifying stackup.

### Timing Gotchas

- **Max readback frequency is limited by slave SDO valid time (t_SDO_valid).** Only half a clock period is available between slave output update and master sample edge. Formula: f_max = 1 / (2 * (t_SDO_valid + t_master_setup)).
- **Hold time violation with delayed SDO update.** Some slaves update SDO a few ns after the sampling edge. If master hold time >15 ns, data is invalid. Fix: insert a logic gate delay in the SDO path (HC gate = 9 ns, AHC = 4.4 ns, HCT = 11 ns).
- **CS as conversion trigger (ADCs):** some ADCs start conversion on CS falling edge. Hardware SPI CS timing is rarely precise enough. Fix: use GPIO for CS.
- **Hardware SPI CS auto-toggles between bytes.** Many MCU SPI peripherals deassert CS between each byte transfer. Flash reads and ADC conversions interpret this as abort. Fix: GPIO for CS, or configure multi-byte frame mode if available.
- **SDO/RDY dual-function pin (ADCs):** SDO goes Hi-Z when CS deasserted, pulls low when conversion completes. In daisy-chain configs, add pull-up on SDO to maintain defined state and preserve RDY functionality.

### Bus Topologies

- **Star (default):** separate CS per slave, shared SCLK/MOSI/MISO. Only the selected slave drives MISO -- others must tri-state.
- **Bus contention risk:** if a slave does not tri-state MISO when CS is deasserted, two drivers fight. Verify tri-state behavior in the datasheet; add series resistor on each slave's MISO as insurance.
- **Daisy-chain:** first word shifted out ends up at the last device. Software must reverse device order when constructing frames. Some parts ship in standalone mode and require register write or pin strap for daisy-chain.
- **Bifurcated transmission line (2-slave only):** series termination at source, then equal-length split to two slaves. Reflections cancel at the 2-way split. Does NOT work for 3+ loads or bidirectional signals (MISO). Also provides lowest clock jitter of any 2-receiver distribution topology.
- **>4 slaves: 74HC138 decoder** for CS generation from 3 address pins. Adds ~10 ns gate delay but saves GPIO.

### Quad/Dual SPI Flash

- **Pin reuse in Quad mode:** IO2 = WP#, IO3 = HOLD#. Both functions are disabled when quad mode is active. Manage flash protection in software only.
- **QE bit (bit 6, Status Register):** non-volatile, persists across power cycles. Sequence: WREN (06h) -> WRSR (01h) with 40h -> poll RDSR (05h) until bits 1:0 clear. Read-modify-write the status register to preserve other bits.
- **Macronix 73-series (MX25Lxx73) ship with QE=1.** Use for x86 boot flash -- PC chipsets query SFDP table and may immediately start in Quad mode. With 35-series (QE=0 default), the chipset can't communicate in quad mode to set QE -> chicken-and-egg.
- **QPI mode (4-4-4):** standard x1 SPI commands are NOT accessible. Exit via RSTQIO (F5h) or power cycle. Distinct from QE=1, which still allows 1-1-1 and 1-1-4 reads.
- **Dummy cycles between address and data** on fast read commands. Typically 4-8 cycles depending on mode and part. Check datasheet for the specific command.
- **Flash reset sequence (66h + 99h):** some ICs need this before accepting commands after power-on. Include in boot firmware.
- **Recommended families:** W25Q128JV (Winbond, 128 Mbit, 133 MHz, SOIC-8/WSON-8). Cost-sensitive: GD25Q64C (GigaDevice, 64 Mbit, 120 MHz). Wide temp (-40 to +105C): IS25LP064 (ISSI, 64 Mbit). All support standard JEDEC commands.
- **Programming header:** if flash is not socketed, break out SCLK, MOSI, MISO, CS, VCC, GND for external programming.

### Level Translation

- **MAX3372E-MAX3393E family:** 8 Mbps minimum guaranteed, up to 16 Mbps when |VCC - VL| < 0.8V. Internal 10 kohm pull-ups sufficient for bus capacitance <90 pF. For >90 pF or traces >30 cm: add external 2.2 kohm pull-ups in parallel.
- **ESD protection built into MAX3373E-series:** +/-15 kV on VCC-side data lines. Thermal shutdown at 150C puts translator in tri-state.
- **2N7001T (SC-70):** single-bit unidirectional level shifter, 100 Mbps, 1.65-3.6V range. Use for MISO direction; pair with SN74AXC4T245 (4-bit, bidirectional, auto-direction) for SCLK/MOSI/CS.

> WARNING: VCCA (low-voltage side) must power up before or simultaneously with VCCB (high-voltage side). If VCCB rises first, back-current through the translator's internal FETs can latch up or damage the unpowered low-voltage IC. Applies to MAX33xx, TXB-series, and similar auto-direction translators.

- **MOSFET-based translators fail below ~1.8V VL.** Finding FETs with sufficiently low Vgs threshold becomes impractical. Use dedicated ICs for VL <= 1.8V.
- General level-shifting topology selection -> `misc/level-shifting.md`.

### Layout

- **Prefer inner-layer routing (stripline) for SPI flash.** Better EMI than microstrip. Espressif recommends layer 3 on 4-layer boards.
- **Length-match data I/O traces to SCLK within 2.54 mm (100 mil).** Critical for Quad and Octal SPI modes.
- **Ground copper and vias around SCLK.** SPI clock is the primary emission source. Separate clock shielding from data traces.
- **Do not route SPI traces under or near crystal oscillators.** Clock harmonics couple into the crystal, degrading RF performance on wireless designs -- Espressif specifically calls this out as a root cause of poor RX sensitivity.
- **SCLK: >= 0.5 mm (20 mil) spacing from any signal above 1 GHz.**
- **No ground plane slots under SPI traces.** Slots force return current into large loops -> slot antennas -> `guides/pcb-layout.md`.

## Common Mistakes

- **MISO series resistor placed at the master -- diagnosing on an existing board.** Scope MISO at the slave pin: if you see clean edges there but ringing at the master, the resistor is on the wrong end. Move it within 6 mm of the slave MISO output.
- **Hardware SPI CS glitch invisible during debug.** Logic analyzer shows correct data, but flash returns 0xFF because CS deasserted between bytes. Scope CS at 10 ns/div to catch the glitch. Fix: GPIO for CS, or multi-byte frame mode.
- **No series termination on FPGA-driven SPI.** Sub-ns rise times cause severe ringing even at 1 MHz clock. The ringing can exceed VCC+0.3V and trigger input protection diodes or cause false clocking. Fix: 22-33 ohm at FPGA output pins.
- **Daisy-chain data order reversed in firmware.** First word shifted out ends up at the last physical device. Fix: construct SPI frame with last device's data first.

## Formulas

**Maximum readback frequency:**
**Rule of thumb:** 10-50 MHz for most SPI flash and sensors. Always check slave t_SDO_valid.
**Formula:** f_max = 1 / (2 * (t_SDO_valid + t_master_setup))
**Example:** t_SDO_valid = 36 ns, t_setup = 10 ns -> f_max = 1 / (2 * 46e-9) = 10.9 MHz.

**Electrically short bus threshold (10% rule):**
**Rule of thumb:** SPI routes <15 cm need no impedance control with typical 10 ns rise time.
**Formula:** L_critical = t_rise * v_prop * 0.1
  - v_prop: ~150 mm/ns (FR4 stripline), ~170 mm/ns (FR4 microstrip)
**Example:** t_rise = 5 ns, stripline -> L_critical = 5 * 150 * 0.1 = 75 mm. Routes under 75 mm are electrically short.

## Sources

### Related Rules

- `misc/level-shifting.md` -- level-shifting topology selection for SPI and other interfaces
- `guides/pcb-layout.md` -- ground plane slots and return current paths

### References

1. ADI AN-1248 -- SPI Interface Timing: https://www.analog.com/en/resources/app-notes/an-1248.html
2. TI SCAA082A -- High-Speed Layout Guidelines: https://www.ti.com/lit/an/scaa082a/scaa082a.pdf
3. Altium -- Is There an SPI Trace Impedance Requirement?: https://resources.altium.com/p/there-spi-trace-impedance-requirement
4. Practical EE -- SPI Bus: https://practicalee.com/spi/
5. Microchip AN2402 -- PCB Layout Guide (SPI Flash Section): https://ww1.microchip.com/downloads/en/AppNotes/00002402A.pdf
6. Macronix AN-0251 -- Serial Flash Multi-I/O Introduction: https://www.macronix.com/Lists/ApplicationNote/Attachments/1899/AN0251V1%20-%20Macronix%20Serial%20Flash%20Multi%20IO%20Introduction.pdf
7. ADI -- Level Translators for SPI and I2C Bus Signals: https://www.analog.com/en/resources/technical-articles/level-translators-for-spi8482-and-isup2c-bus-signals.html
8. Espressif ESP32-S3 HW Design Guidelines -- PCB Layout (SPI/Flash Section): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
