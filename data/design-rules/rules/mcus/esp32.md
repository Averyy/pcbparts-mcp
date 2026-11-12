# ESP32 (S3, C3, C6)

> Strapping pins, power supply, RF matching, USB-JTAG, crystal, flash/PSRAM -- per-chip variant differences.

## Quick Reference

- **Boot-mode straps: S3 GPIO0/GPIO46; C3 GPIO2/GPIO8/GPIO9; C6 GPIO8/GPIO9.** These are not the complete S3/C6 strap sets; keep strap levels stable for at least 3 ms after enable rises [8, pp.32-35; 9, pp.30-32; 10, pp.33-36].
- **S3/C3/C6 single-supply recommendation: 3.3V, >= 500 mA supply capability, not a peak-current specification.** Main supply rails operate at 3.0-3.6V; add 10 uF on S3/C3 VDD3P3 or C6 VDDA3P3 and the chip-specific LC filter [1-3, Power Supply; 8-10, Table 5-2].
- **Reset default: 10 kohm + 1 uF on CHIP_PU (S3/C6) or CHIP_EN (C3).** Validate against the actual supply waveform; slow/unstable supplies or frequent power cycling need additional reset circuitry, such as a supervisor with around 3.0V threshold [1-3, Chip Power-up and Reset Timing].
- **RF matching: CLC preferred for S3/C3, CLCCL preferred for C6.** Use 0201 matching components close to the chip; tune toward the chip conjugate point 35+j0 ohm and S21 < -35 dB at 4.8 GHz and 7.2 GHz [1-3, RF Tuning].
- **USB pins: S3 = GPIO19/20, C3 = GPIO18/19, C6 = GPIO12/13.** Espressif recommends populating 22/33 ohm series resistors and reserving cap-to-ground footprints close to the chip [1-3, USB].

## Design Rules

### Chip and Package Selection

- **C3 for new cost-sensitive designs: ESP32-C3FH4 (QFN32, 5x5mm) or ESP32-C3FH4X (QFN32, 5x5mm).** Both have in-package 4 MB flash. The datasheet lists 22 GPIO for FH4 and 16 for FH4X; flash-connected pins remain reserved even when bonded out. RISC-V single core up to 160 MHz, Wi-Fi + Bluetooth LE 5 [9, pp.3-4, 12-15, 29].
- **S3 for higher performance: ESP32-S3FN8 (QFN56, 7x7mm, 8 MB flash) or ESP32-S3FH4R2 (QFN56, 7x7mm, 4 MB flash + 2 MB PSRAM).** Xtensa dual-core up to 240 MHz, Wi-Fi + Bluetooth LE 5, USB OTG [8, pp.3-4, 13, 77-78].
- **C6 for Thread/Zigbee + Wi-Fi: QFN40 (5x5mm, external flash required) or QFN32 (5x5mm, in-package flash).** RISC-V single core at 160 MHz, Wi-Fi 6 + Bluetooth LE 5.3 + 802.15.4 [10, pp.3-5, 13, 78].

### Power Supply

- **Digital/RTC decoupling: 100 nF close to S3/C3 VDD3P3_CPU and VDD3P3_RTC, and C6 VDDPST1/VDDPST2.** S3 VDD3P3_RTC is pin 20; C3 also needs RTC-rail decoupling. S3/C3 VDD3P3_RTC is not a standalone backup supply [1-3, Power Supply].
- **Analog TX rail: 10 uF plus LC filter on S3/C3 VDD3P3 or C6 VDDA3P3.** Espressif recommends an inductor rated >= 500 mA; the power-entrance 10 uF and TX-rail 10 uF can be merged when the entrance is close to that rail [1-3, Analog Power Supply].
- **VDD_SPI at 3.3V is fed through RSPI from S3 VDD3P3_RTC, C3 VDD3P3_CPU, or C6 VDDPST2.** Add 100 nF + 1 uF at S3/C6 VDD_SPI; C3 guidance specifies 1 uF. C6 external VDD_SPI decoupling applies to QFN40; QFN32 flash pins are not bonded out. Check source voltage > VDD_flash_min + I_flash_max * RSPI; merely meeting the 3.0V rail minimum does not budget the resistor drop [1-3, Digital Power Supply; 8-10, Table 5-3].
- **S3 VDD_SPI voltage selection: controlled by GPIO45 (default low = 3.3V, high = 1.8V internal LDO, 40 mA typical).** Can be overridden by EFUSE_VDD_SPI_FORCE + EFUSE_VDD_SPI_TIEH. When EFUSE_VDD_SPI_FORCE=1, GPIO45 is ignored and EFUSE_VDD_SPI_TIEH selects 0=1.8V or 1=3.3V; use the memory voltage specified for the exact chip variant [8, pp.13, 34, 65].
- **Espressif recommends an ESD protection diode and at least 10 uF at the power entrance** [1-3, Power Supply].
- **Burn eFuses (secure boot, flash encryption, MAC or user data) with the eFuse supply at <= 3.3 V: VDD3P3_CPU on S3/C3, VDDPST2 on C6.** The burn circuits are sensitive to higher voltage even though normal operation permits up to 3.6 V [8, p.64; 9, p.54; 10, p.64].

### Reset Circuit

- **CHIP_PU/EN must not float; tSTBL and tRST are each >= 50 us.** The datasheet timing diagrams mark the supply crossing at 2.8V; reset requires enable below 0.25 * its supply-domain voltage. The nominal 10 kohm/1 uF RC is a starting point, not a guaranteed ramp limit; the ideal-ramp estimate below excludes leakage, capacitor tolerance and incomplete discharge [1-3, Chip Power-up and Reset Timing; 8, pp.30, 65; 9, pp.27-28, 55; 10, pp.30-31, 65].
- **Espressif's DevKits fit exactly 10 kohm + 1 uF on CHIP_PU in S3-DevKitC-1 v1.1 and C6-DevKitC-1 v1.4.** These are reference implementations, not validation of a different regulator's ramp [11-12, sheet 2].
- **For slow/unstable power sources (battery charging, solar): add external reset IC** with threshold ~3.0V (e.g., voltage supervisor). Espressif also identifies frequent power cycling as a case where RC alone can fail [1-3, Chip Power-up and Reset Timing].
- **Auto-reset for programming: DTR -> boot pin, RTS -> EN.** S3: DTR -> GPIO0, RTS -> CHIP_PU. C3/C6: DTR -> GPIO9, RTS -> CHIP_EN/CHIP_PU. Two-transistor circuit prevents simultaneous DTR+RTS assertion from holding chip in reset. For this two-transistor circuit, esptool specifies 1-10 uF from EN to GND for reliable auto-reset [4-5, Automatic Bootloader; 11, sheet 2].

### Strapping Pins

- **S3 boot mode: GPIO0 (45 kohm typical internal pull-up) + GPIO46 (internal pull-down).** GPIO0 low + GPIO46 low/floating = download boot. GPIO0 high = SPI boot (normal). GPIO46 high while GPIO0 low = invalid mode. GPIO45 controls VDD_SPI voltage (see power section). GPIO3 controls JTAG signal source only when the corresponding eFuse configuration enables strapping selection [8, pp.32-35, 65].
- **C3 boot mode: GPIO9 (45 kohm typical internal pull-up) + GPIO8.** GPIO9 low + GPIO8 high = download boot. GPIO9 high = SPI boot (normal). GPIO8 low + GPIO9 low = invalid combination (undefined behavior). **GPIO2 is a boot strapping pin; pull it high as recommended because of glitches.** Its level does not actually determine SPI versus joint download boot. GPIO8, together with EFUSE_UART_PRINT_CONTROL, controls UART ROM printing [9, pp.30-32, 55].
- **C6 boot mode: GPIO9 (internal pull-up) + GPIO8.** GPIO9 low + GPIO8 high = download boot. GPIO9 high = SPI boot (normal). GPIO8 low + GPIO9 low = invalid. Additional straps: GPIO15 selects JTAG under eFuse control; MTMS/MTDI select SDIO clock edges [10, pp.33-36].
- **Do not add high-value capacitors on boot pins (GPIO0 on S3, GPIO9 on C3/C6).** Slow rise time causes the wrong boot state to be sampled [1-3, Strapping Pins].
- **Boot pin: 10 kohm external pull-up as fitted on the cited DevKits, boot button straight to GND.** Espressif recommends the pull-up (the internal one is a weak ~45 kohm). A button through 10 kohm against the 10 kohm pull-up gives VDD/2 (1.65 V) ignoring the internal pull-up, above VIL max 0.25 * VDD (0.825 V), so it does not guarantee a valid low [8, p.65; 9, p.55; 10, p.65; 11-12, sheet 2].
- **Strapping pin hold time: at least 3 ms after CHIP_PU/EN goes high.** This is a minimum hold interval, not an exact latch instant [8, p.33; 9, p.31; 10, p.34].

### Crystal

- **S3/C3/C6 firmware supports a 40 MHz crystal; Espressif recommends accuracy within +/-10 ppm.** Choose load capacitors from the exact crystal specification and PCB parasitics, then tune with the RF TX-tone test [1-3, External Crystal Clock Source].
- **24 nH series inductor on XTAL_P trace** to suppress high-frequency harmonics that degrade RF performance. This is Espressif's initial value for S3/C3/C6; adjust after RF testing [1-3, External Crystal Clock Source].
- **Espressif recommends crystal amplitude > 500 mV on S3/C3/C6.** Defective crystals with low amplitude or >10 ppm offset cause Wi-Fi/Bluetooth connection failures. Verify frequency offset within +/-10 ppm using spectrum analyzer at the 2.4 GHz TX tone [1-3, External Crystal Clock Source].
- **32.768 kHz RTC crystal (optional): parallel bias resistor > 5 Mohm and <= 10 Mohm** (usually DNP). If not used, XTAL_32K pins are available as GPIO [1-3, RTC Clock Source].
- Crystal selection and load cap calculation details -> `misc/crystal.md`.

### Flash and PSRAM

- **C3FH4X does not bond out its flash SPI pins; C3FH4 does, but they remain reserved for in-package flash.** Neither needs an external flash circuit [9, pp.12-15, 29].
- **S3 off-package flash: add zero-ohm resistor footprints in series on SPI lines.** Provides flexibility for drive strength tuning, RF interference mitigation, and timing correction [1, Flash].
- **S3 octal flash or octal PSRAM, in-package or external, reserves GPIO33-37 in addition to the SPI bus pins.** SPICLK_P/N share the memory voltage domain but are not listed as PSRAM signals in Table 2-14. On ESP32-S3-WROOM-1/1U modules with octal PSRAM, exposed IO35-37 are unavailable; with ESP32-S3R16V, exposed GPIO47/48 also operate at 1.8V [8, p.31; 1, GPIO; 13, p.12].
- **C6 QFN32 variant has in-package flash; QFN40 requires external flash.** Flash pins on QFN32 are not bonded out [10, pp.13, 32].

### RF and Antenna

- **RF trace: 50 ohm impedance control.** Derive geometry from the actual board stackup -> `misc/rf-antenna.md` [1-3, RF Circuit].
- **Chip matching circuit (close to chip): S3/C3 use CLC structure, C6 uses CLCCL bandpass.** CLCCL suppresses both high-frequency harmonics and low-frequency noise. For layouts that strictly follow Espressif's chip layout, its tuning ranges are C = 1.2-1.8 pF (GRM0335C1H1RXBA01D family) and L = 2.4-3.0 nH (LQP03TN2NXB02D family); these are not fixed BOM values for arbitrary boards [1-3, RF Tuning].
- **Add stub on first capacitor at chip end of matching circuit.** Espressif specifies the stub and 0201 packages for these networks [1-3, RF Tuning].
- **Module matching values cannot be reused for custom PCBs** -- board parasitics change impedance. Re-tune with a network analyzer [1-3, RF Tuning].

### USB

- **S3 USB pins: GPIO19 (D-) / GPIO20 (D+). C3: GPIO18 (D-) / GPIO19 (D+). C6: GPIO12 (D-) / GPIO13 (D+).** S3 has USB OTG and USB Serial/JTAG (both full-speed); C3/C6 have USB Serial/JTAG only [1-3, USB].
- **Populate 22/33 ohm series resistors on S3/C3/C6 USB D+/D-, close to the chip.** Espressif recommends fitting them, and reserving a cap-to-ground footprint on each data trace for tuning; the checklists give no default capacitor value [1-3, USB].
- USB routing details -> `interfaces/usb.md`.
- **Espressif's own DevKits put one LESD5D5.0CT1G (LRC, 5 V, 15 pF) on each of VBUS, D- and D+ on the cited S3/C6 reference boards.** The 15 pF is typical at 25 degrees C, not a capacitance limit. C6-DevKitC-1 v1.4 has two USB-C ports, 5.1 kohm on each CC pin, and Schottky-ORed VBUS inputs; S3-DevKitC-1 v1.1 uses micro-USB (board_get: espressif-esp32-s3-devkitc-1). Treat these as board examples, not a universal ESD choice [6, p.2; 11-12, sheet 2].
- **USB D+ fluctuates between high and low on power-up.** If stable initial state is needed, add external pull-up on D+ for consistent high level at startup [1-3, USB].
- **S3 USB-OTG download boot initializes external-PHY pads: MTDO output high, MTCK/GPIO38 output low; MTMS/MTDI/GPIO21 inputs.** If this download mode is not needed, Espressif suggests EFUSE_DIS_USB_OTG_DOWNLOAD_MODE to avoid those pad-state changes [1, USB].

### GPIO

- **S3 power-up glitches: GPIO1-14, GPIO17-19, XTAL_32K_P/N output low-level glitches (60 us typical).** GPIO18/19 also show high-level glitches. GPIO20 has pull-down + high-level glitch. Do not connect latching circuits or safety-critical loads to these pins without external circuitry that establishes the required safe state [8, p.18].
- **C3 power-up glitches: MTCK, MTDO, GPIO10, U0RXD have 5 ns typical low-level glitches; GPIO18 has a 50 us typical high-level glitch** [9, p.18].
- **Deep-sleep control is limited to S3 GPIO0-21 (VDD3P3_RTC) or C6 VDDPST1 pins (GPIO0-7).** Do not assume non-RTC pins remain software-controllable; select pins and any retention configuration for the exact chip [1, GPIO; 3, GPIO].
- **UART0 TX (U0TXD): add 499 ohm series resistor to suppress harmonics.** Espressif recommends this on S3/C3/C6 [1-3, UART].
- **ADC: prefer ADC1 on C3/S3.** C3 ADC2 is not factory-calibrated and some chip revisions have non-functional ADC2. S3 ADC2 also shares hardware with Wi-Fi; ESP-IDF v5.4.2 arbitrates oneshot reads and returns ESP_ERR_TIMEOUT when the ADC is busy. C3 ADC2 oneshot is unsupported by default because results are unstable [7, Hardware Limitations]. Add 100 nF from the ADC pin to ground on S3/C3/C6 [1-3, ADC].
- **Configure unused pins from each chip's reset/power-domain table.** Espressif recommends pulls for high-impedance pins; do not apply a universal analog-input or drive-low policy to boot straps or memory pins [1-3, GPIO].
- Crystal, RF matching, and power formulas -> `misc/crystal.md`, `misc/rf-antenna.md`, `power/decoupling.md`.

## Common Mistakes

- **A peripheral on C3/C6 GPIO8 can prevent programming even with the boot button pressed.** Ensure it permits GPIO8 high while GPIO9 is low during joint download boot [9, p.31; 10, p.34].
- **Serial-port opening can assert DTR and RTS together.** With RTS directly wired to EN this holds reset; use the cited two-transistor truth table and check terminal hardware-flow-control settings [4-5, Automatic Bootloader].

## Formulas

**Rule of thumb:** ideal linear-ramp estimate only: at 3.3V, tau = R * C >= 1.4 * T_ramp + 0.1 ms. The nominal 10 kohm/1 uF estimate is about 7 ms; it is not a guaranteed supply-ramp limit [8, p.30; 9, pp.27-28; 10, pp.30-31].
**Formula:** tau >= 1.65 * ((2.8 V / V_final) * T_ramp + 50 us)
  - Derived ideal RC model: all rails share a linear ramp from 0 to V_final, EN starts fully discharged, and EN leakage is neglected. During the ramp, V_EN / VDD = 1 - (tau / t) * (1 - e^(-t / tau)), reaching 0.25 at t = 0.606 * tau. The coefficients are rounded; the formula applies only when (2.8 V / V_final) * T_ramp + 50 us <= T_ramp; validate the actual waveform and discharge between power cycles.
  - Use the slowest soft-start time in the regulator's datasheet, and the capacitor's effective value at 3.3 V and its tolerance.
**Example:** 8.7 ms soft start to 3.3 V -> tau >= 1.65 * (0.848 * 8.7 ms + 0.05 ms) = 12.3 ms -> 10 kohm with 2.2 uF (22 ms nominal; if the selected part retains 60% after DC bias and tolerance, 13.2 ms effective exceeds the calculated 12.3 ms).

## Sources

### Related Rules

- `misc/crystal.md` -- Crystal selection and load cap calculation
- `misc/rf-antenna.md` -- RF matching, antenna design, and impedance tuning
- `power/decoupling.md` -- Per-IC decoupling strategy and capacitor placement

### References

1. Espressif ESP32-S3 HW Design Guidelines -- Schematic Checklist, HTML snapshot extracted 2026-02-09 (no numbered revision): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html
2. Espressif ESP32-C3 HW Design Guidelines -- Schematic Checklist, HTML snapshot extracted 2026-02-09 (no numbered revision): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html
3. Espressif ESP32-C6 HW Design Guidelines -- Schematic Checklist, HTML snapshot extracted 2026-02-09 (no numbered revision): https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c6/schematic-checklist.html
4. Espressif esptool -- Boot Mode Selection (ESP32-S3), latest HTML retrieved 2026-11-09 (no numbered revision): https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html
5. Espressif esptool -- Boot Mode Selection (ESP32-C3), latest HTML retrieved 2026-11-09 (no numbered revision): https://docs.espressif.com/projects/esptool/en/latest/esp32c3/advanced-topics/boot-mode-selection.html
6. LRC -- LESD5D5.0CT1G datasheet Rev.O, manufacturer document mirrored by AllDatasheet: https://www.alldatasheet.com/html-pdf/769823/LRC/LESD5D5.0CT1G/126/2/LESD5D5.0CT1G.html
7. Espressif -- ESP-IDF v5.4.2 ADC Oneshot Mode Driver, Hardware Limitations: https://github.com/espressif/esp-idf/blob/v5.4.2/docs/en/api-reference/peripherals/adc_oneshot.rst
8. Espressif -- ESP32-S3 Series Datasheet v2.2 (Table 2-13 power-up timing, Table 5-2 note 3 eFuse supply): https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf
9. Espressif -- ESP32-C3 Series Datasheet v2.4 (Table 2-11 power-up timing, Table 5-2 note 2 eFuse supply): https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf
10. Espressif -- ESP32-C6 Series Datasheet v1.5 (Table 2-15 power-up timing, Table 5-2 note 3 eFuse supply on VDDPST2): https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf
11. Espressif -- ESP32-C6-DevKitC-1 v1.4 schematic (USB-C ports, ESD, CHIP_PU RC): https://dl.espressif.com/dl/schematics/esp32-c6-devkitc-1-schematics_v1.4.pdf
12. Espressif -- ESP32-S3-DevKitC-1 v1.1 schematic: https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-DevKitC-1_V1.1_20221130.pdf
13. Espressif -- ESP32-S3-WROOM-1/ESP32-S3-WROOM-1U Datasheet v1.8: https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
