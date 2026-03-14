# ESP32 (S3, C3, C6)

> Strapping pins, power supply, RF matching, USB-JTAG, crystal, flash/PSRAM -- per-chip variant differences.

## Quick Reference

- **Strapping pins differ per chip. S3: GPIO0 + GPIO46. C3: GPIO2 + GPIO8 + GPIO9. C6: GPIO8 + GPIO9.** Getting these wrong causes boot into download mode or invalid state. Strapping values are latched 3 ms after CHIP_PU goes high.
- **Power supply: 3.3V, >= 500 mA. 10 uF on VDD3P3 (analog), LC filter on analog rail.** All power rails must rise together -- VDD3P3_RTC cannot be used as standalone backup supply.
- **Reset: RC circuit on CHIP_PU (S3/C6) or CHIP_EN (C3). R = 10 kohm, C = 1 uF.** CHIP_PU/CHIP_EN must not float. For battery or unstable supply: add external reset IC with ~3.0V threshold.
- **RF matching: CLC for S3/C3, CLCCL bandpass for C6.** 0201 packages, placed close to chip. Matching network target: conjugate match to chip impedance (~35+j0 ohm). Tuned S11 < -10 dB (VSWR < 2:1) at 2.4 GHz. S21 < -35 dB at 4.8 GHz and 7.2 GHz.
- **USB pins: S3 = GPIO19/20, C3 = GPIO18/19, C6 = GPIO12/13.** 22-33 ohm series resistors close to chip. Reserve cap-to-ground footprint on each line.

## Design Rules

### Chip and Package Selection

- **C3 for new cost-sensitive designs: ESP32-C3FH4 (QFN32, 5x5mm) or ESP32-C3FH4X (QFN32, 5x5mm).** Both have internal 4 MB flash. FH4 exposes 16 GPIO, FH4X exposes 22 GPIO. RISC-V single core at 160 MHz, Wi-Fi + BLE 5.0.
- **S3 for higher performance: ESP32-S3FN8 (QFN56, 7x7mm, 8 MB flash) or ESP32-S3FH4R2 (QFN56, 7x7mm, 4 MB flash + 2 MB PSRAM).** Xtensa dual-core at 240 MHz, Wi-Fi + BLE 5.0, USB OTG.
- **C6 for Thread/Zigbee + Wi-Fi: QFN40 (5x5mm, external flash required) or QFN32 (5x5mm, in-package flash).** RISC-V single core at 160 MHz, Wi-Fi 6 + BLE 5.0 + 802.15.4.
- **S3 variants with octal PSRAM (R8/R8V) occupy GPIO33-37.** These pins are unavailable for other functions when octal PSRAM is present. Plan pin budget before selecting variant.

### Power Supply

- **Digital power: 100 nF close to each VDD pin (VDD3P3_CPU on S3/C3, VDDPST1/VDDPST2 on C6).** S3 additionally has VDD3P3_RTC (pin 20) needing 100 nF.
- **Analog power (VDD3P3/VDDA): 10 uF + LC filter to suppress RF TX current spikes.** Inductor rated current >= 500 mA. During TX, current draw increases abruptly -- without 10 uF, rail collapses and causes brownout.
- **VDD_SPI: powers flash/PSRAM at 3.3V (default) via internal resistor from VDD3P3_RTC (S3) or VDD3P3_CPU (C3) or VDDPST2 (C6).** Add 100 nF + 1 uF close to VDD_SPI pin. Voltage drop through internal RSPI means VDD3P3_RTC/CPU must be >= 3.0V for flash to operate reliably.
- **S3 VDD_SPI voltage selection: controlled by GPIO45 (default low = 3.3V, high = 1.8V internal LDO, 40 mA max).** Can be overridden by EFUSE_VDD_SPI_FORCE + EFUSE_VDD_SPI_TIEH. When using in-package flash with eFuse-locked voltage, GPIO45 strapping is ignored and R1 pull-down is optional.
- **10 uF + 100 nF decoupling within 5 mm of each VDD pin.** Field failure case: 68% failure rate on ESP32+LoRa board traced to 420 mV ground bounce from split ground plane during 120 mA TX burst -- dropped 3.3V below 2.97V brownout threshold.
- **ESD protection diode recommended at power entrance** (before bulk 10 uF cap).

### Reset Circuit

- **RC delay: R = 10 kohm, C = 1 uF on CHIP_PU (S3/C6) or CHIP_EN (C3).** Ensures 50 us minimum stabilization time (tSTBL) before chip enable. Reset requires CHIP_PU/EN held below 0.25 * VDD for >= 50 us (tRST).
- **For slow/unstable power sources (battery charging, solar): add external reset IC** with threshold ~3.0V (e.g., voltage supervisor). RC circuit alone may not provide monotonic, clean enable signal.
- **Auto-reset for programming: DTR -> boot pin, RTS -> EN.** S3: DTR -> GPIO0, RTS -> CHIP_PU. C3/C6: DTR -> GPIO9, RTS -> CHIP_EN/CHIP_PU. Two-transistor circuit prevents simultaneous DTR+RTS assertion from holding chip in reset. Requires 1 uF cap on EN pin for reliable auto-reset -- boards without this cap fail intermittently on Windows.

### Strapping Pins

- **S3 boot mode: GPIO0 (45 kohm internal pull-up) + GPIO46 (internal pull-down).** GPIO0 low + GPIO46 low/floating = download boot. GPIO0 high = SPI boot (normal). GPIO46 high while GPIO0 low = invalid mode. GPIO45 controls VDD_SPI voltage (see power section). GPIO3 controls JTAG signal source.
- **C3 boot mode: GPIO9 (45 kohm internal pull-up) + GPIO8.** GPIO9 low + GPIO8 high = download boot. GPIO9 high = SPI boot (normal). GPIO8 low + GPIO9 low = invalid combination (undefined behavior). **GPIO2 is a strapping pin** that controls boot message printing (high = print, low = suppress) -- not boot mode selection, but must be accounted for in pin planning. Pull-up recommended to avoid power-up glitches.
- **C6 boot mode: GPIO9 (internal pull-up) + GPIO8.** GPIO9 low + GPIO8 high = download boot. GPIO9 high = SPI boot (normal). GPIO8 low + GPIO9 low = invalid. Additional strapping: GPIO15, MTMS, MTDI.
- **Do not add high-value capacitors on boot pins (GPIO0 on S3, GPIO9 on C3/C6).** Slow rise time from large cap causes chip to sample wrong value and enter download mode unexpectedly.
- **Pull-up resistor on boot pin: use 10 kohm (strong enough to override 45 kohm internal pull-up noise).** Boot button pulls to GND through 10 kohm.
- **Strapping pin hold time: 3 ms after CHIP_PU/EN goes high.** External circuits connected to strapping pins must not change state during this window.

### Crystal

- **40 MHz crystal, +/-10 ppm, required on all variants.** Firmware does not support other frequencies. Recommended: Seiko Epson TSX-3225 (3.2x2.5mm, 10pF load, +/-10ppm) or Abracon ABM8-40.000MHZ-B2-T (3.2x2.5mm). Match CL to crystal spec using C_load = (C1*C2)/(C1+C2) + C_stray.
- **24 nH series inductor on XTAL_P trace** to suppress high-frequency harmonics that degrade RF performance. Adjust value after RF testing.
- **Crystal amplitude must exceed 500 mV.** Defective crystals with low amplitude or >10 ppm offset cause Wi-Fi/Bluetooth connection failures. Verify frequency offset within +/-10 ppm using spectrum analyzer at 2.4 GHz TX tone.
- **32.768 kHz RTC crystal (optional): parallel bias resistor 5-10 Mohm** (usually DNP). If not used, XTAL_32K pins available as GPIO.
- Crystal selection and load cap calculation details -> `misc/crystal.md`.

### Flash and PSRAM

- **C3 with in-package flash (FH4/FH4X): flash SPI pins not bonded out, cannot be used for other functions.** No external flash circuit needed.
- **S3 off-package flash: add zero-ohm resistor footprints in series on SPI lines.** Provides flexibility for drive strength tuning, RF interference mitigation, and timing correction.
- **S3 octal PSRAM (R8/R8V): occupies GPIO33-37 plus SPICLK_P/SPICLK_N.** These pins share VDD_SPI power domain -- if octal 1.8V flash/PSRAM is used, SPICLK_P and SPICLK_N also operate at 1.8V.
- **C6 QFN32 variant has in-package flash; QFN40 requires external flash.** Flash pins on QFN32 are not bonded out.

### RF and Antenna

- **RF trace: 50 ohm impedance control.** On 0.8 mm FR-4 core: ~0.254 mm trace width. Use rounded tracks (not right angles) for 2.4 GHz RF output.
- **Chip matching circuit (close to chip): S3/C3 use CLC structure, C6 uses CLCCL bandpass.** CLCCL suppresses both high-frequency harmonics and low-frequency noise. Component values: C = 1.2-1.8 pF (Murata GRM0335C1H1RXBA01D), L = 2.4-3.0 nH (Murata LQP03TN2NXB02D). Use 0201 packages.
- **Add stub on first capacitor at chip end of matching circuit.** Enables impedance measurement without desoldering.
- **Module matching values cannot be reused for custom PCBs** -- board parasitics change impedance. Always re-tune with network analyzer.
- **Use 0603 (not 0402) for matching network prototypes.** Easier to rework during RF tuning. Production can switch to 0201/0402 after values are locked.
- **Via fence around RF section: 0.3 mm vias, <= 10 mm pitch.** Isolates RF from digital noise. Copper fill must maintain >= 3*w clearance from 50 ohm trace (w = trace width) or impedance shifts (38 ohm observed in field with 0.3 mm encroachment).
- **Do not route RF trace under crystal oscillator.** Causes injection locking during TX bursts -- 22 dBc spurs at LoRa center frequencies observed in field.

### USB

- **S3 USB pins: GPIO19 (D-) / GPIO20 (D+). C3: GPIO18 (D-) / GPIO19 (D+). C6: GPIO12 (D-) / GPIO13 (D+).** S3 has USB OTG (full-speed); C3/C6 have USB Serial/JTAG controller only.
- **22-33 ohm series resistors between chip USB pins and connector, placed close to chip.** Reserve cap-to-ground footprint on each trace for EMC tuning.
- **USB differential pair: 90 ohm impedance.**
- **USB D+ fluctuates between high and low on power-up.** If stable initial state is needed, add external pull-up on D+ for consistent high level at startup.
- **S3 USB-OTG download boot mode: drives MTMS, MTDI, MTDO, MTCK, GPIO21, GPIO38 after init.** If USB-OTG download boot is not needed, disable via eFuse bit EFUSE_DIS_USB_OTG_DOWNLOAD_MODE to prevent unexpected IO state changes.

### GPIO

- **S3 power-up glitches: GPIO1-14, GPIO17-20, XTAL_32K_P/N output low-level glitches (~60 us).** GPIO18/19 also show high-level glitches. GPIO20 has pull-down + high-level glitch. Do not connect latching circuits or safety-critical loads to these pins without external pull resistors.
- **C3 power-up glitches: MTCK, MTDO, GPIO10, U0RXD have ~5 ns low-level glitch. GPIO18 has ~50 us high-level glitch.**
- **S3 deep-sleep: only GPIO0-21 (VDD3P3_RTC domain) remain controllable.** GPIO33-48 (VDD3P3_CPU / VDD_SPI domains) float in deep sleep -- do not connect latching or safety-critical loads to these pins. C6: only VDDPST1 domain GPIOs controllable in deep-sleep (XTAL_32K_P/N, GPIO2-3, MTMS, MTDI, MTCK, MTDO).
- **UART0 TX (U0TXD): add 499 ohm series resistor to suppress harmonics.** Applies to all variants.
- **ADC: use ADC1, not ADC2.** C3 ADC2 is not factory-calibrated and some chip revisions have non-functional ADC2. S3 ADC1 recommended for best accuracy. Add 100 nF filter cap between ADC pin and ground.
- **Unused pins: set to analog input mode or push-pull low for lowest leakage.** Floating high-impedance pins increase power consumption.
- Crystal, RF matching, and power formulas -> `misc/crystal.md`, `misc/rf-antenna.md`, `power/decoupling.md`.

## Common Mistakes

- **Ground plane split symptoms mimic software bugs.** Brownout-induced resets during Wi-Fi/BLE TX look like firmware crashes -- engineers spend weeks debugging code when the root cause is a 0.3 mm ground trace creating inductive return current paths. Fix: always check VREG_OUT with oscilloscope during max TX burst before suspecting firmware. Stitching vias at 1.5 mm pitch around ESP32 eliminate the issue.
- **RF performance degrades silently over production batches.** Solder paste thickness variation shifts parasitic capacitance near the RF trace, detuning impedance by 5-10 ohm across a production run. Boards pass functional test but range drops 30-50%. Fix: add TDR verification to incoming QA on RF-critical products, or widen copper clearance to >= 3*w to reduce sensitivity to manufacturing variation.
- **Wi-Fi channel 13/14 fails while channels 1-11 work.** Higher channels are closer to the 2nd harmonic of common 1.2 GHz DDR clocks and the 3rd harmonic of 802.15.4 (868 MHz). Engineers test on channel 6 only and miss the interference. Fix: test all channels during validation, especially 12-14. Route RF feedline away from crystal and high-speed digital.
- **C3 GPIO8 left floating during download boot.** GPIO8 must be high for valid download mode -- GPIO8 low + GPIO9 low is an invalid strapping combination that triggers undefined behavior. Fix: pull GPIO8 high with 10 kohm when using download boot.
- **Auto-reset circuit without EN capacitor.** Third-party boards that connect DTR/RTS to boot pin/EN without the 1 uF cap on EN pin get unreliable auto-reset, especially on Windows. Fix: always include >= 1 uF between EN/CHIP_PU and GND.
- **Matching network tuned on eval board applied unchanged to custom PCB.** Board parasitics (trace length, ground plane geometry, connector transition) shift impedance -- a CLC network tuned to S11 < -15 dB on the DevKitC measured -6 dB on a 4-layer custom board with different stackup. Fix: treat eval board values as starting point only; always re-measure S11/S21 with VNA on each new layout and iterate component values.

## Sources

### Related Rules

- `misc/crystal.md` -- Crystal selection and load cap calculation
- `misc/rf-antenna.md` -- RF matching, antenna design, and impedance tuning
- `power/decoupling.md` -- Per-IC decoupling strategy and capacitor placement

### References

1. Espressif ESP32-S3 HW Design Guidelines -- Schematic Checklist: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html
2. Espressif ESP32-C3 HW Design Guidelines -- Schematic Checklist: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html
3. Espressif ESP32-C6 HW Design Guidelines -- Schematic Checklist: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c6/schematic-checklist.html
4. esptool -- Boot Mode Selection (ESP32-S3): https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html
5. esptool -- Boot Mode Selection (ESP32-C3): https://docs.espressif.com/projects/esptool/en/latest/esp32c3/advanced-topics/boot-mode-selection.html
6. Deep Blue Embedded -- ESP32 PCB Design in KiCAD (ESP32-C3 + Chip Antenna Hardware Design): https://deepbluembedded.com/esp32-pcb-design-in-kicad-esp32-c3-chip-antenna-hardware-design/
7. PCBCool -- ESP32 PCB Failure Case Study on Power and RF Layout Design: https://pcbcool.com/case-studies/esp32-pcb-failure-case-study-on-power-and-rf-layout/

