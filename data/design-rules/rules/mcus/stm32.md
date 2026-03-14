# STM32

> Boot configuration, reset circuit, power supply (VCAP, VDDA, BYPASS_REG, PDR_ON), HSE crystal, GPIO speed, ADC accuracy, USB power.

## Quick Reference

- **VCAP capacitors: F4 = 2x 2.2 uF low ESR (< 2 ohm). H7 = 2.2 uF low ESR (< 100 mohm).** Wrong ESR causes regulator instability. Single VCAP packages (no VCAP2): use 1x 4.7 uF (ESR < 1 ohm).
- **NRST: 100 nF pull-down cap for EMS protection.** F4 does not require external reset circuit for power-up. G0 NRST is configurable as reset I/O, reset input only, or GPIO (PF2).
- **Boot: F4 uses BOOT0/BOOT1 pins. H7 uses BOOT pin + option bytes. G0 uses BOOT0 pin + option bytes.** Default: boot from main flash. 10 kohm pull-down on BOOT0 for normal operation.
- **VDDA: 100 nF + 1 uF decoupling. Connect to VDD through ferrite bead.** VREF+ to VDDA through 47 ohm resistor (H7). VDDA minimum depends on which analog peripherals are used.
- **HSE: 25 MHz for H7 (required for Ethernet/USB), 8 MHz typical for G0 (4-48 MHz range).** Crystal accuracy and load cap calculation -> `misc/crystal.md`.

## Design Rules

### Power Supply

- **F4 VDD range: 1.8-3.6V (down to 1.7V with restrictions).** Decoupling: one 4.7 uF (min) bulk tantalum or ceramic per package + 100 nF ceramic per VDD pin. Place caps as close as possible to pins, preferably underneath on opposite PCB layer.
- **H7 VDD range: 1.71-3.6V (down to 1.62V with external power supervisor on PDR_ON).** Decoupling: 4.7 uF min per package + 100 nF per VDD pin. Below 1.71V requires external reset controller on NRST.
- **G0 VDD range: 1.7-3.6V.** Decoupling: 4.7 uF + 100 nF ceramic per VDD/VSS pair.
- **VCAP pins (F4): 2x 2.2 uF low ESR < 2 ohm ceramic.** Single VCAP packages: 1x 4.7 uF ESR < 1 ohm. These supply the internal 1.2V core regulator output. Wrong capacitor ESR causes regulator oscillation.
- **VCAP pins (H7): 2.2 uF low ESR < 100 mohm ceramic on VCAP1/VCAP2.** Much tighter ESR requirement than F4. VDDLDO pins connected together with 4.7 uF cap.
- **VDDA: 100 nF ceramic + 1 uF.** Connect VDDA to VDD through ferrite bead for noise isolation. VSSA must be externally connected to same ground as VSS.
- **VDDA minimum voltage by peripheral (H7):** No analog: 0V. ADC/comparator: 1.62V. DAC: 1.8V. OPAMP: 2.0V. VREFBUF: depends on selected output level. Design for the most demanding peripheral used.
- **VREF+: connect to VDDA unless separate reference needed.** If separate: 100 nF + 1 uF decoupling. H7: VREF+ to VDDA through 47 ohm resistor. Must be <= VDDA, minimum 1.7V (F4) or 2V when VDDA > 2V (H7).
- **VBAT: connect to VDD with 100 nF if no battery used.** Range: 1.65-3.6V (F4), 1.2-3.6V (H7), 1.55-3.6V (G0). H7: if VDD > VBAT + 0.6V during startup, current injects into VBAT through internal diode -- add external low-drop diode if battery cannot handle this.

### H7 SMPS and Voltage Scaling

- **H7 SMPS step-down converter (available on some packages): enables power optimization.** Enabled via SDEN bit in PWR_CR3. Internal supply mode: VCORE follows system operating modes with VOS/SVOS bits. External supply mode: outputs 2.5V or 1.8V (SDLEVEL bits).
- **SMPS external components: 2.2 uH inductor + 220 pF cap on VLXSMPS, 10 uF (ESR < 20 mohm) on VFBSMPS, 4.7 uF (ESR < 100 mohm) on VDDSMPS.** VDDSMPS must equal VDD level.
- **Voltage scaling: VOS0 through VOS3 (run mode), SVOS3/SVOS4/SVOS5 (stop mode).** Higher VOS level = higher max frequency but higher power. Default after reset is VOS3 (lowest performance). Must configure VOS before increasing clock frequency.

### F4 BYPASS_REG and PDR_ON

- **BYPASS_REG = VDD: internal regulator bypassed.** Core power supplied externally through VCAP pins (connected together). Replace 2.2 uF VCAP caps with 100 nF decoupling. External voltage must match targeted max frequency. Requires external power supervisor on PA0 to monitor V12 domain.
- **When BYPASS_REG active: PA0 reserved for V12 reset (not usable as GPIO), over-drive/under-drive unavailable, standby mode unavailable, debug under reset requires separate PA0/NRST management.**
- **PDR_ON = VSS: disables internal POR/PDR.** Intended for 1.8V +/-5% supply. When internal reset OFF: BOR must be disabled, PVD unavailable, VBAT must connect to VDD. Requires external voltage supervisor on NRST or PDR_ON.
- **PDR_ON voltage supervisor selection: active-high push-pull output.** Trip point example for 1.8V supply: supervisor at 1.66V +/-2.5% with 0.5% hysteresis gives rising trip max = 1.71V, falling trip min = 1.62V.

### Reset

- **F4: 100 nF pull-down cap on NRST for EMS protection.** No external reset circuit required for normal power-up. Internal POR/PDR handles reset from 1.8V. Can reduce to 10 nF to limit power consumption from charging through internal pull-up.
- **G0 NRST: configurable via option bytes as reset I/O (default), reset input only, or GPIO (PF2).** Default: bidirectional -- internal resets drive pin low, external low signal triggers reset. 20 us minimum reset pulse width. Internal reset holder option (in option bytes) ensures pin stays low until VIL threshold is met.
- **H7 NRST: active-low with internal filter.** Minimum 20 us reset pulse. BOOT0 pin with 10 kohm pull-down for default flash boot.
- **VBAT domain reset: only occurs when both VDD and VBAT have been powered off.** Setting BDRST bit in RCC_BDCR triggers software RTC domain reset.

### Boot Configuration

- **F4: BOOT0 + BOOT1 pins, latched on 4th rising edge of SYSCLK after reset.**

| BOOT1 | BOOT0 | Boot space |
|-------|-------|-----------|
| x | 0 | Main flash (default) |
| 0 | 1 | System memory (bootloader) |
| 1 | 1 | Embedded SRAM |

- **H7: single BOOT pin + option bytes (BOOT_ADD0/BOOT_ADD1).** BOOT=0 uses BOOT_ADD0 (default: flash at 0x08000000). BOOT=1 uses BOOT_ADD1 (default: system memory at 0x1FF00000). Option bytes allow any boot address from 0x00000000 to 0x3FFF0000. Flash level 2 protection forces flash-only boot.
- **G0: BOOT0 pin + option bytes (nBOOT1, BOOT_SEL, nBOOT0).** BOOT_LOCK bit in FLASH_SECR forces main flash boot regardless of other settings. Boot latched on 4th rising edge of SYSCLK. Bootloader supports USART (PA2/3, PA9/10), I2C (PB6/7), SPI (PA4-7).
- **F4 bootloader peripherals vary by sub-family.** F405/407/415/417/427-439: USB OTG FS (PA11/12) + USART1 (PA9/10) + I2C + SPI + CAN. F401/411: USART + I2C + SPI only (no CAN). Check AN2606 for exact peripheral/pin mapping per device -- USB bootloader availability varies by sub-family and revision.
- **BOOT0: 10 kohm pull-down to VSS for normal flash boot.** Applying VDD permanently to BOOT0 generates extra current consumption through internal circuits.

### HSE Crystal

- **H7: 25 MHz recommended for accurate Ethernet, USB OTG HS, I2S, and SAI clocking.** Range: 4-48 MHz. Load caps: 5-25 pF typical, ~10 pF estimated pin + board stray capacitance.
- **G0: 8 MHz typical (range 4-48 MHz).** HSI48 available on G0B1/G0C1 for crystal-less USB via clock recovery system (CRS) synchronized to USB SOF.
- **LSE: 32.768 kHz with configurable drive strength via LSEDRV[1:0] in RCC_BDCR.** Four levels: Low, Medium-Low, Medium-High, High. Higher drive = more robust startup but higher power. LSE frequency must exceed 30 kHz to avoid false CSS detections.
- **Clock security system (CSS): switches to HSI on HSE failure, sends break to TIM1/TIM8/TIM15-17, generates NMI.** LSE CSS must be enabled only after LSE and LSI are ready and RTC clock source is selected.
- **HSE gain margin must exceed 5x for reliable startup across temperature.** LSE gain margin must exceed 3x. Gain margin = g_m_crit / g_m_min where g_m_crit depends on crystal ESR, load caps, and frequency. Verify with negative resistance measurement -- crystal must start within spec'd time at coldest operating temperature.
- Crystal selection and load cap calculation details -> `misc/crystal.md`.

### USB

- **F4/G0 USB FS: internal PHY, no external series resistors needed on D+/D-.** Matching impedance is embedded. ESD protection: USBLC6-2SC6 (low cost) or USBLC6-2P6 (low area), placed close to connector.
- **H7 USB: VDD50USB (4.0-5.5V from VBUS) regulates to VDD33USB (3.0-3.6V).** If both pins available, connect together. Decoupling: VDD50USB 4.7 uF, VDD33USB 100 nF + 1 uF. When VDD33USB separate from VDD: must be last applied / first removed, VDD33USB < VDD + 300 mV.
- **USB FS requires precise 48 MHz clock.** From main PLL (needs HSE crystal), or HSI48 with CRS (device mode only, not accurate enough for host). AHB frequency must be > 14.2 MHz for OTG_FS, > 30 MHz for OTG_HS.
- **G0B1/G0C1 crystal-less USB via HSI48+CRS.** HSI48 free-run accuracy is ~3%, but CRS locks to USB SOF packets in device mode for sufficient accuracy. Enables USB DFU bootloader without external crystal. Clock sources for G0 USB: HSE, HSI48, or PLLQCLK. HSI48 is auto-enabled when selected as USB clock source.
- **VBUS sensing on PA9: voltage divider required.** PA9 is 5V-tolerant but must not see 5V VBUS when MCU unpowered (violates abs max). Divider values: 82 kohm to GND + 33 kohm to VBUS for 3.0-3.6V VDD range. 68 kohm to GND + 82 kohm to VBUS for 1.65-2.0V VDD range.
- **Self-powered USB device: only start PHY/controller on VBUS detection.** D+ 1.5 kohm pull-up (embedded on some STM32s) must connect only when VBUS present. GPIO drives pull-up enable after VBUS detection.
- USB ESD and layout details -> `protection/esd.md`, `interfaces/usb.md`.

### GPIO

- **Unused pins: configure as analog input (lowest power -- Schmitt trigger disabled) or push-pull output driven low.** Floating inputs cause Schmitt trigger to toggle randomly, increasing consumption.
- **GPIO speed (OSPEEDR): higher speed = faster edges but more EMI and SSO noise.** F4 at OSPEEDR=11 (very high): 100 MHz max at 30 pF load (VDD >= 2.7V), 180 MHz at 10 pF. Use lowest speed setting that meets timing requirements. IO compensation cell can be activated above 50 MHz (VDD > 2.4V) to reduce overshoot.
- **Five-volt tolerant (FT) pins: tolerant to VDD + 3.6V (max 5.5V) in input mode only.** When analog function enabled (ADC), FT tolerance is lost -- pin limited to min(VDDA, VREF+) + 0.3V. When VDD = 0V, max input on FT pins drops to 3.6V.

> WARNING: Not all GPIO pins are 5V-tolerant. STM32 datasheets mark each pin as FT (five-volt tolerant), TT (three-volt tolerant), or TC (three-volt capable). TC pins are limited to VDD + 0.3V max -- connecting 5V signals to a TC pin damages the device. Check the pinout table in the datasheet for every pin that interfaces with 5V logic. Common trap: assuming all pins on a 3.3V STM32 tolerate 5V because "some pins are FT."

- **Debug pins (PA13/SWDIO, PA14/SWCLK): have internal pull-up/pull-down by default.** PA13 pull-up, PA14 pull-down. If reused as GPIO, avoid forcing opposite level (causes extra consumption through internal pull resistors).
- **VBAT-domain GPIO (H7): limited to 3 mA drive strength** through integrated power switch. Do not use for high-current loads even when VDD is valid.
- **G0 multi-bonding on small packages (STM32G03x/G04x): multiple die pads connected to single package pin.** No internal protection against pad conflicts -- configure each pad carefully. Can increase drive strength by configuring multiple pads as same output level.

### ADC Accuracy

- **F2/F4 (F405/407/415/417): configure ART with data cache ON + instruction cache ON + prefetch OFF for best ADC accuracy.** Prefetch causes extra flash access noise: raw dispersion drops from 21 LSB (prefetch ON) to 18 LSB (prefetch OFF) at 12-bit resolution, 1.65V input.
- **F42x/F43x: additional ADC accuracy options (ADCDC1 in PWR_CR, ADCxDC2 in SYSCFG_PMC).** Option 1 (ADCDC1): requires prefetch OFF, VDD >= 2.4V. Option 2 (ADCxDC2): requires fADC >= 30 MHz, 12-bit resolution. Both reduce dispersion to ~6 LSB (vs 21 LSB baseline on F42x/F43x with default ART settings -- not directly comparable to F405/407 numbers above due to different silicon revisions).
- **Do not toggle I/Os on the same port as ADC input during conversion.** Switching noise couples into analog inputs. Avoid starting communication peripheral TX just before conversion.
- **Averaging by 4 with optimal ART config: 0% of samples exceed +/-5 LSB from mode at 0.6 Msps (12-bit).** Total dispersion range ~7-8 LSB. Averaging by 8 narrows to +/-4 LSB.

## Common Mistakes

- **Wrong VCAP ESR causes regulator oscillation.** F4 requires ESR < 2 ohm, H7 requires ESR < 100 mohm. Using a generic bulk ceramic (ESR near 0) on F4 can also cause instability -- the regulator needs some ESR for stability. Check the specific ESR range in the datasheet.
- **Leaving BOOT0 pulled to VDD permanently.** Generates continuous extra current consumption through internal boot selection circuits. Fix: 10 kohm pull-down to VSS, use pushbutton or jumper only when bootloader access needed.
- **Connecting 5V VBUS directly to PA9 without voltage divider.** When MCU is unpowered, 5V on PA9 exceeds absolute maximum ratings and damages the pin. Fix: resistor divider (82k/33k) or MOSFET detector (2N7002).
- **ADC prefetch causing 21 LSB dispersion on F2/F4.** Flash prefetch generates noise that corrupts ADC readings. Most developers leave ART at default (all ON) without realizing the impact. Fix: disable prefetch during ADC conversions, re-enable after.
- **G0 NRST permanently grounded as "enable" pin.** Holds device in startup phase indefinitely -- NRST is not a chip enable. Fix: use low-power standby/shutdown modes instead. NRST has ~40 kohm internal pull-up; grounding it wastes current continuously.
- **H7 VBAT current injection during startup.** If VDD > VBAT + 0.6V, current flows through internal diode into VBAT. Can damage coin cell batteries. Fix: add external low-drop diode in series with battery on VBAT pin.

## Formulas

**STM32 ADC effective resolution with averaging:**
**Rule of thumb:** Averaging by N adds log2(N)/2 effective bits. 4x averaging adds 1 ENOB.
**Formula:** ENOB = log2(2^N / sigma_rms), where sigma_rms = dispersion_LSB / (2 * sqrt(2))
**Example:** F4 with prefetch OFF: 18 LSB dispersion at 12-bit. sigma_rms ~ 6.4 LSB. ENOB = log2(4096/6.4) = 9.3 bits. With 4x averaging: ~10.3 ENOB.

## Sources

### Related Rules

- `misc/crystal.md` -- Crystal selection, load cap calculation, and HSE/LSE design
- `protection/esd.md` -- USB ESD protection placement and TVS selection
- `interfaces/usb.md` -- USB layout, impedance control, and connector wiring

### References

1. ST AN4488 -- Getting Started with STM32F4xxxx HW Dev: https://www.st.com/resource/en/application_note/an4488-getting-started-with-stm32f4xxxx-mcu-hardware-development-stmicroelectronics.pdf
2. ST AN2867 -- Oscillator Design Guide for STM8/STM32: https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8af-al-s-and-stm32-microcontrollers-stmicroelectronics.pdf
3. ST AN5096 -- Getting Started with STM32G0 HW Dev: https://www.st.com/resource/en/application_note/an5096-getting-started-with-stm32g0-mcus-hardware-development-stmicroelectronics.pdf
4. ST AN4938 -- Getting Started with STM32H7 HW Dev: https://www.st.com/resource/en/application_note/an4938-getting-started-with-stm32h74xig-and-stm32h75xig-mcu-hardware-development-stmicroelectronics.pdf
5. ST AN4899 -- STM32 GPIO HW Settings & Low-Power: https://www.st.com/resource/en/application_note/an4899-stm32-microcontroller-gpio-hardware-settings-and-lowpower-consumption-stmicroelectronics.pdf
6. ST AN4879 -- USB Hardware/PCB Guidelines for STM32: https://www.st.com/resource/en/application_note/an4879-introduction-to-usb-hardware-and-pcb-guidelines-using-stm32-mcus-stmicroelectronics.pdf
7. ST AN4073 -- Improving ADC Accuracy (STM32F2/F4): https://www.st.com/resource/en/application_note/an4073-how-to-improve-adc-accuracy-when-using-stm32f2xx-and-stm32f4xx-microcontrollers-stmicroelectronics.pdf
