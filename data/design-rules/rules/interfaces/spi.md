# SPI Bus

> Series termination, CS timing, multi-device topologies, Quad SPI flash, level translation.

## Quick Reference

- **CEC1702 flash reference: 25 ohm at the MCU, 45 ohm at the flash I/O.** Final series values require electrical analysis; a MISO source resistor belongs at the slave [3, p.12; 2, §1.3.2].
- **Pull-up on CS#: 4.7 kohm to the flash supply in the CEC1702 reference.** Keeps the flash deselected when controller pins float; use the same rail as the flash [3, pp.12-13].
- **Readback timing includes the slave's maximum SDO-valid delay and the master's setup time.** The half-period budget applies only when launch and capture are opposite edges [1, When Is the Bus Data Updated?].
- **QE register location and power-up state are flash-specific.** Macronix MX25xxxx35 uses status bit 6; MX25Lxx73 has QE permanently set [4, pp.8-9].

## Design Rules

### Series Termination

- **Source termination must account for driver impedance.** Use R_series + Z_driver = Z0, then verify receiver timing and overshoot/undershoot; neither a fixed resistor value nor the SPI clock rate alone establishes a match [2, §1.3.2; 3, p.12].
- **MISO resistor placement is at the slave.** The slave drives MISO; a master-side resistor is not source termination for that direction. Quad data I/O changes direction, so CEC1702's reference provides resistors at both endpoints [2, §1.3.2; 3, pp.11-12].

### When Impedance Control Matters

- **CEC1702 SPI flash: 50 ohm +/-15% at 50MHz is Microchip's board recommendation.** It is not a universal SPI impedance requirement; match data I/O to SCLK within 2.54mm (100mil) for this interface [3, p.13].

### Timing Gotchas

- **Some slaves update SDO after the sampling edge rather than on the opposite edge.** Check the actual timing diagram against the configured CPOL/CPHA; the half-period readback formula below does not apply to same-edge delayed updates [1, Which Transmission Mode Is Used by the Slave?, When Is the Bus Data Updated?].
- **A same-edge delayed SDO update can violate the master's hold time.** AN-1248 flags masters needing > 15ns hold and lists typical NOR delays: HC 9ns, AHC 4.4ns, HCT 11ns. A delay gate is a fix only if its minimum delay closes hold and its maximum delay still closes setup over voltage, temperature and load [1, Table 2].
- **CS as conversion trigger (ADCs): check both CS-to-SCLK limits and the conversion clock requirement.** AN-1248 distinguishes ADCs needing continuous SCLK from internally clocked ADCs needing quiet SCLK during conversion; use GPIO CS when hardware SPI cannot meet that sequence [1, CS as Start Conversion Signal].
- **SDO/RDY behavior is ADC-specific.** For AN-1248's daisy-chain case, add an SDO pull-up to preserve RDY functionality; do not assume a deselected slave can drive a shared MISO ready indication [1, SDO as Conversion Ready Pin, Daisy-Chain Topology].

### Bus Topologies

- **Shared MISO: verify SDO disable timing and operating mode.** AN-1248 warns that SDO need not disable with CS in daisy-chain mode; disconnect it from the shared bus or disable SDO explicitly. A series resistor limits contention but does not make incompatible outputs shareable [1, Parallel Configuration].
- **Daisy-chain:** first word shifted out ends up at the last device. Some parts power up in standalone mode with SDO high impedance: put such a part first, enable its chain mode, and bias its SDO so the next device does not receive a floating input [1, Daisy-Chain Topology].

### Quad/Dual SPI Flash

- **Macronix MX25xxxx35: QE repurposes WP# and HOLD#/RESET# as I/O, where those functions exist.** Hardware protection/reset through those pins is unavailable with QE set; software protection must preserve the other status bits [4, pp.8-9].
- **MX25xxxx35 QE is nonvolatile status bit 6.** Sequence: WREN (06h) -> WRSR (01h), read-modify-writing bit 6 -> poll RDSR (05h) until bits 1:0 clear. This is Macronix's sequence, not a generic procedure for Winbond/GigaDevice/ISSI [4, pp.8-9].
- **Macronix MX25Lxx73 has QE permanently set, not merely a default QE=1.** AN-0251 recommends it for PC chipsets that inspect SFDP and immediately use Quad; check the selected chipset's boot protocol [4, p.9].
- **QPI (4-4-4) sends commands on four data lines.** QE-enabled SPI can still accept single-line commands; use the selected flash's documented QPI exit/reset sequence rather than assuming F5h works across vendors [4, pp.3,7,9].
- **Dummy cycles are command-specific.** AN-0251's examples use 8 for 6Bh Quad Output and 6 for EBh Quad I/O; match the exact part's command and frequency setting [4, pp.6-7].
- **CEC1702 flash needs external programming provisions when not socketed.** The programming connector and controller isolation must suit the chosen programmer and flash supply [3, p.13].

### Level Translation

- **MAX3373E: ADI's example gives 8Mbps guaranteed, up to 16Mbps for |VCC - VL| < 0.8V.** Its 10 kohm / 90pF and external 2.2 kohm pull-up discussion is for standard-mode I2C, not an SPI loading guarantee; check the selected translator's load/timing specifications [5, Dedicated Level Translators, Typical Applications].
- **2N7001T (SC-70 or X2SON):** single-bit unidirectional level shifter, 1.65-3.6V supplies, up to 100Mbps. TI pairs it with direction-controlled SN74AXC4T245 for the opposite SPI direction [7, pp.2,4].
- **SN74AXC4T245 is direction-controlled, 0.65-3.6V on each supply.** It is not auto-directional or 5V tolerant. Its supplies can sequence in either order; use its OE pull-ups for high impedance during power transitions instead of applying a blanket low-rail-first rule [8, §§1,3].
- General level-shifting topology selection -> `misc/level-shifting.md`.

### Layout

- **ESP32-S3 flash/PSRAM: reserve zero-ohm series footprints close to the MCU.** Espressif recommends inner-layer routing (e.g. layer 3), separately grounded clock/data shielding, and matched Octal SPI lengths [6, Flash and PSRAM].
- **CEC1702 SPI_CLK: >= 0.508mm (20mil) from signals above 1GHz** [3, p.13]. Return-plane continuity -> `guides/pcb-layout.md`.

## Common Mistakes

- **Adding a hold-fix gate using only its typical delay.** The extra delay also consumes readback setup margin; reducing SCLK helps setup but does not fix a same-edge hold violation [1, When Is the Bus Data Updated?].

## Formulas

**Maximum readback frequency:**
**Rule of thumb:** Use the half-cycle budget only for opposite-edge SDO launch/capture and a 50% duty-cycle clock [1, When Is the Bus Data Updated?].
**Formula:** f_max = 1 / (2 * (t_SDO_valid(max) + t_master_setup)) for the idealized direct connection. Clock/data flight time, translation delay, duty-cycle distortion and skew consume additional margin; check hold separately.
**Example:** AN-1248's 36ns SDO-valid and assumed 10ns master setup give 1 / (2 * 46ns) = 10.87MHz before those extra delays; its practical recommendation is 10MHz [1].

## Sources

### Related Rules

- `misc/level-shifting.md` -- level-shifting topology selection for SPI and other interfaces
- `guides/pcb-layout.md` -- ground plane slots and return current paths

### References

1. ADI AN-1248 -- SPI Interface Timing (HTML, no revision stated; local snapshot February 2026): https://www.analog.com/en/resources/app-notes/an-1248.html
2. TI SCAA082A (August 2017) -- High-Speed Layout Guidelines: https://www.ti.com/lit/an/scaa082a/scaa082a.pdf
3. Microchip AN2402 (DS00002402A, March 2017), pp.11-13 -- PCB Layout Guide for CEC1702: https://ww1.microchip.com/downloads/en/AppNotes/00002402A.pdf
4. Macronix AN-0251 (Ver.01, August 2013), pp.3,6-9 -- Serial Flash Multi-I/O Introduction: https://www.macronix.com/Lists/ApplicationNote/Attachments/1899/AN0251V1%20-%20Macronix%20Serial%20Flash%20Multi%20IO%20Introduction.pdf
5. ADI -- Level Translators for SPI and I2C Bus Signals (HTML, no revision stated; local snapshot February 2026): https://www.analog.com/en/resources/technical-articles/level-translators-for-spi8482-and-isup2c-bus-signals.html
6. Espressif ESP32-S3 HW Design Guidelines -- PCB Layout, Flash and PSRAM (HTML, local snapshot February 2026): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
7. TI SCEA064A (March 2021), pp.2,4 -- Voltage Level Translation for SPI, UART, and JTAG Interfaces With Focus On 2N7001T: https://www.ti.com/lit/pdf/scea064
8. TI SN74AXC4T245 datasheet (SCES877B, April 2024), sections 1,3: https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf
