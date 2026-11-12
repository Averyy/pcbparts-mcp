# STM32

> Boot configuration, reset circuit, power supply (VCAP, VDDA, BYPASS_REG, PDR_ON), HSE crystal, GPIO speed, ADC accuracy, USB power.

## Quick Reference

- **VCAP with internal regulator enabled: F4 = 2x 2.2 uF, ESR < 2 ohm; STM32H74x/H75x = 2.2 uF on each of VCAP1/VCAP2, ESR < 100 mohm.** F4 packages with only VCAP1: 1x 4.7 uF, ESR < 1 ohm [1, p.9; 4, p.12].
- **NRST: 100 nF to ground for F4 EMS protection.** Internal POR/PDR handles normal power-up; G0 option bytes can disable the external reset function by selecting PF2 GPIO mode [1, p.13; 3, p.8].
- **Boot selection is device-specific: F405/407 use BOOT0 + PB2/BOOT1; STM32H74x/H75x use BOOT + address option bytes; G0 can ignore the BOOT0 pin.** Check the programmed option bytes before relying on a boot strap [8, p.52; 4, p.25; 3, p.21].
- **F4 and STM32H74x/H75x VDDA: 100 nF + 1 uF.** Ferrite filtering from VDD is optional; the H7 47 ohm VREF+ filter is an option for an externally supplied reference, not a connection for a VREFBUF output [1, p.9; 4, pp.7, 12-13].
- **STM32H74x/H75x and G0 HSE crystal range: 4-48 MHz.** H7 25 MHz is a reference-design choice, not a universal Ethernet/USB requirement; select load capacitors for the crystal and actual stray capacitance [4, pp.21-22; 3, p.13; 2, pp.12-14].

## Design Rules

### Power Supply

- **F4 VDD range: 1.8-3.6V (down to 1.7V with device-specific restrictions).** Decoupling: one 4.7 uF minimum bulk tantalum or ceramic per package + 100 nF ceramic per VDD pin [1, pp.7, 9].
- **STM32H74x/H75x VDD range: 1.71-3.6V; 1.62V requires an external supervisor on NRST and PDR_ON tied to VSS.** This lower limit is available only on packages exposing PDR_ON. Decoupling: 4.7 uF minimum per package + 100 nF per VDD pin [4, pp.7, 12, 17-18].
- **G0 VDD range: 1.7-3.6V for startup.** Decoupling: 4.7 uF + 100 nF ceramic at the VDD/VDDA supply pair; operating below the startup threshold is subject to the device's PDR limits [3, pp.2-4].
- **VCAP pins (F4): 2x 2.2 uF low ESR < 2 ohm ceramic.** Single VCAP packages: 1x 4.7 uF ESR < 1 ohm. These stabilize the internal core regulator; the F405/407 specification gives an ESR upper limit, not a minimum ESR requirement [1, p.9; 8, p.84].
- **VCAP pins (STM32H74x/H75x, LDO enabled): 2.2 uF low ESR < 100 mohm ceramic on each of VCAP1/VCAP2.** AN4938 connects the VCAP pins together; if VCAP3 exists, connect it to the others without an additional capacitor. VDDLDO pins connect together with 4.7 uF decoupling [4, p.12].
- **F4 and STM32H74x/H75x VDDA: 100 nF ceramic + 1 uF.** A ferrite bead between VDD and VDDA is an optional noise filter. VSSA must be externally connected to the same ground as VSS [1, pp.9, 12; 4, pp.12-13].
- **VDDA minimum voltage by peripheral (STM32H74x/H75x):** No analog: 0V. ADC/comparator: 1.62V. DAC: 1.8V. OPAMP: 2.0V. VREFBUF: depends on selected output level. Design for the most demanding peripheral used [4, pp.7-8].
- **VREF+ with an external reference: F4 requires max(1.7V, VDDA - 1.2V) <= VREF+ <= VDDA.** STM32H74x/H75x: minimum 2V when VDDA > 2V and the ADC is used, otherwise 1.62V; do not exceed VDDA. Use 100 nF + 1 uF for a separate reference. AN4938's optional 47 ohm filter connects VDDA to an externally supplied VREF+; leave that connection out when VREFBUF drives the pin [1, p.9; 4, pp.7, 12-13].
- **VBAT: connect to VDD and decouple to ground with 100 nF if no battery is used.** Range: 1.65-3.6V (F4), 1.2-3.6V (STM32H74x/H75x), 1.55-3.6V (G0) [1, p.9; 4, pp.10, 12; 3, p.2].

### STM32H74x/H75x SMPS and Voltage Scaling

- **STM32H7x5/H7x7 SMPS: select internal or external supply mode before choosing the output network.** Enable through SDEN in PWR_CR3. Direct internal supply tracks VOS/SVOS; external supply mode provides 1.8V or 2.5V through SDLEVEL [4, pp.11, 14].
- **AN4938 SMPS component network: 2.2 uH inductor at VLXSMPS with 220 pF, 10 uF at VFBSMPS, and 4.7 uF at VDDSMPS.** The note lists nominal ESR values of 20 mohm and 100 mohm respectively; use the selected device datasheet for component limits and supply-mode connections. Wire VDDSMPS to VDD [4, pp.9, 13].
- **STM32H74x/H75x voltage scaling: VOS0 through VOS3 in Run, SVOS3/SVOS4/SVOS5 in Stop.** Reset selects VOS3. Select the voltage scale allowed for the target clock before increasing frequency; the scale number is not an increasing-performance index [4, pp.10-11].

### F4 BYPASS_REG and PDR_ON

- **On F4 packages exposing BYPASS_REG, BYPASS_REG = VDD bypasses the internal regulator.** Supply the core externally through VCAP pins connected together; replace the two 2.2 uF capacitors with two 100 nF decoupling capacitors. External voltage must match the target frequency, and an external supervisor must monitor the core domain through PA0 [1, pp.7-8; 8, pp.28-29, 84].
- **When BYPASS_REG active: PA0 is reserved for core-domain reset, over-drive/under-drive and Standby are unavailable.** Manage PA0 and NRST separately for debug connection under reset [1, p.8].
- **F4 external reset supervision has two different connections.** F410/411/412/413/423/446/469/479 packages with PDR_ON can tie it to VSS and use an active-low open-drain supervisor on NRST. For the other F4 products covered by AN4488, use its active-high push-pull supervisor on PDR_ON, including asserting PDR_ON high during power-down; do not simply tie it low [1, pp.13-17]. With internal reset disabled, disable BOR, PVD is unavailable, and tie VBAT to VDD [1, pp.14, 16].
- **Budget the supervisor trip point including hysteresis.** AN4488's example uses a 1.8V +/-5% supply and a 1.66V +/-2.5% supervisor with 0.5% hysteresis: recomputed rising maximum = 1.7098V, falling minimum = 1.6185V. These are rounded to 1.71V and 1.62V in the note, not guaranteed margins for every F4 device [1, p.17].

### Reset

- **F4: 100 nF pull-down cap on NRST for EMS protection.** No external reset circuit is required for normal power-up with internal POR/PDR enabled. AN4488 permits reducing the capacitor to 10 nF to limit charging/discharging consumption [1, p.13].
- **G0 NRST: configurable via option bytes as reset I/O (default), reset input only, or GPIO (PF2).** The 20 us minimum is the pulse generated for internal resets in bidirectional mode, not an external-input pulse-width requirement. The optional internal reset holder keeps driving until the pin reaches VIL [3, p.8].
- **STM32H74x/H75x reset pulse generator: minimum 20 us output pulse.** Use the selected device datasheet for external NRST input timing [4, pp.16-17].

### Boot Configuration

- **F405/407: BOOT0 + PB2/BOOT1 pins, latched on the 4th rising edge of SYSCLK after reset.** The table applies to these devices; other F4 boot controls must be checked against their own reference manual [1, pp.25-26; 8, p.52].

| BOOT1 | BOOT0 | Boot space |
|-------|-------|-----------|
| x | 0 | Main flash (default) |
| 0 | 1 | System memory (bootloader) |
| 1 | 1 | Embedded SRAM |
- **STM32H74x/H75x: BOOT pin selects BOOT_ADD0 or BOOT_ADD1.** Factory defaults are flash at 0x08000000 and system memory at 0x1FF00000 respectively. Option bytes select mapped boot addresses from 0x00000000 to 0x3FFF0000; level 2 readout protection forces flash boot. Secure access mode changes this behavior [4, p.25].
- **G0: nBOOT_SEL=0 selects the BOOT0 pin; nBOOT_SEL=1 selects the inverse of nBOOT0.** With BOOT_LOCK=0, effective BOOT0=0 boots flash; effective BOOT0=1 selects system memory when nBOOT1=1, SRAM when nBOOT1=0. BOOT_LOCK=1 forces main flash. Settings latch on the 4th SYSCLK rising edge and are sampled again on Standby exit [3, p.21].
- **F4 bootloader peripherals vary by sub-family; every F4 group except F410 has USB OTG FS DFU on PA11/PA12.** AN4488 lists DFU for F401, F405/407/415/417/427/437/429/439, F411, F412/413/423 and F469/479, and USART1 on PA9/PA10 for all groups. The F405-F439 group adds USART3 and CAN (PB5/PB13) but has no I2C/SPI bootloader interface. Check AN2606 for the exact device and bootloader revision before allocating recovery pins [1, pp.27-28].
- **BOOT0: a 10 kohm pull-down is the STM32H753 reference-design example, not a substitute for checking boot option bytes.** Applying VDD permanently to BOOT0 generates extra consumption [4, p.34; 5, p.28].

### HSE Crystal

- **STM32H74x/H75x: 25 MHz is an HSE choice recommended for Ethernet, USB OTG HS, I2S, and SAI clocking; the crystal range is 4-48 MHz.** AN4938's 5-25 pF load capacitors and estimated 10 pF pin/board capacitance are illustrative; calculate for the chosen crystal and board [4, pp.21-22; 2, pp.12-14].
- **G0 HSE crystal range: 4-48 MHz.** HSI48 is available on G0B1/G0C1 for crystal-less USB using CRS synchronized to USB SOF [3, pp.13-14].
- **LSE: 32.768 kHz with drive strength selected through LSEDRV[1:0].** On G0, with LSE clock security enabled, frequency must exceed 30 kHz to avoid false detections [3, pp.15-16; 4, p.23].
- **STM32H74x/H75x HSE CSS: on HSE failure, HSI replaces an HSE-derived system clock, TIM1/TIM8/TIM15-17 receive a break event, and an NMI is generated.** Enable LSE CSS only after LSE is ready and the RTC clock source is selected [4, p.24].
- **Oscillator compatibility: when the datasheet specifies oscillator transconductance gm, require gain margin gm / gmcrit > 5 for HSE or LSE.** For equal load capacitors, gmcrit = 4 * ESR * (2 * pi * f)^2 * (C0 + CL)^2. If the datasheet instead specifies Gm_crit_max (sometimes named Gm), compare gmcrit directly against that limit; its factor-of-five margin is already included [2, pp.13-14].
- Crystal selection and load cap calculation details -> `misc/crystal.md`.

### USB

- **F4/G0 USB FS: internal PHY, no external series resistors needed on D+/D-.** Matching impedance is embedded. For bus-powered USB FS, AN4879 lists USBLC6-2SC6 (low cost) or USBLC6-2P6 (low area); use the separate self-powered protection recommendations when applicable [6, pp.9-10, 14].
- **STM32H74x/H75x USB supply: choose either 5V-input regulation or direct 3.3V supply.** With VDD50USB at 4.0-5.5V, use 4.7 uF on that input and 1 uF (ESR <= 600 mohm) on the regulated VDD33USB output; do not short the two pins. With direct 3.0-3.6V on VDD33USB, tie VDD50USB to it if present and decouple with 100 nF + 1 uF [4, pp.8, 12]. For an independent VDD33USB supply, apply it last and remove it first; its VDD + 300 mV restriction applies during power-on/down while VDD is below its minimum. Check VDD50USB sequencing separately against the selected device datasheet [4, pp.8-9].
- **USB FS requires a precise 48 MHz clock.** Use an HSE-derived PLL clock (crystal or HSE bypass), or a supported HSI48/CRS device-mode clock. For OTG peripherals, AHB must be > 14.2 MHz for OTG_FS and > 30 MHz for OTG_HS [6, pp.10-11, 24].
- **G0B1/G0C1 crystal-less USB via HSI48+CRS.** The ~3% free-run accuracy is a factory calibration at 25 degrees C; CRS can lock to USB SOF in device mode. USB clock choices are HSE, HSI48, or PLLQCLK; HSI48 is auto-enabled when selected while USB is enabled [3, pp.11, 14].
- **VBUS sensing through a resistor divider uses a regular GPIO input; disable the embedded PA9 VBUS-sensing function.** AN4879 specifies 82 kohm to GND + 33 kohm to VBUS for VDD=3.0-3.6V, or 68 kohm to GND + 82 kohm to VBUS for VDD=1.65-2.0V, with 1% resistors. Check worst-case divider voltage against the selected GPIO operating limits at every supply state, including unpowered; the 82/33 kohm divider can exceed 3.6V at the pin. If those limits are exceeded, use its 2N7002 detector [6, pp.11-13; 5, pp.19-20].
- **Self-powered USB device: only start PHY/controller on VBUS detection.** Connect the D+ 1.5 kohm pull-up (embedded on some STM32s) only while VBUS is present [6, pp.14-15].
- USB ESD and layout details -> `protection/esd.md`, `interfaces/usb.md`.

### GPIO

- **Unused pins: configure as analog input or push-pull output driven low.** Analog mode disables the input Schmitt trigger [1, p.25; 5, p.29].
- **STM32F469 GPIO speed example, OSPEEDR=11: 100 MHz at 30 pF or 180 MHz at 10 pF, both with VDD >= 2.7V.** These are not family-wide F4 limits. The I/O compensation recommendation applies above 50 MHz with VDD > 2.4V [1, pp.22-23].
- **FT pin voltage tolerance depends on every supply connected to that pad.** AN4899 describes VIN <= min(relevant supplies) + 3.6V, capped at 5.5V, in input mode without an enabled analog function; at zero supply the bound falls to 3.6V. With an analog function enabled, the limit is min(VDDA, VREF+) + 0.3V. Use the selected device's operating limits, not its absolute maximum rating, for the actual pad [5, pp.19-20].

> WARNING: Check the datasheet I/O structure for every 5V interface. TC pins lack the FT protection structure; applying 5V to an ordinary VDD-powered TC pin can exceed its VDD + 0.3V limit and damage it [5, pp.11, 19].
- **Debug pins (PA13/SWDIO, PA14/SWCLK): internal pull-up/pull-down by default.** PA13 pull-up, PA14 pull-down. If reused as GPIO, avoid forcing the opposite level [1, pp.30-31; 5, p.28].
- **VBAT-domain GPIO: limited to 3 mA through the integrated power switch.** Do not use for high-current loads even when VDD is valid [5, p.28].
- **G0 multi-bonding on small packages (STM32G03x/G04x): multiple die pads connect to one package pin.** No internal protection against pad conflicts; configure each pad consistently. Same-level outputs can increase drive strength [3, p.25].

### ADC Accuracy

- **F2/F405/407/415/417: data cache ON + instruction cache ON + prefetch OFF improves ADC dispersion in AN4073's test.** On STM32F407ZGT6 at 25 degrees C, VDD=VDDA=VREF+=3.3V, fADC=36 MHz, fCPU=144 MHz, 12-bit resolution, 3-cycle sampling, and 1.65V input, raw dispersion fell from 21 to 18 LSB. These are lab histogram widths, not guaranteed accuracy limits [7, pp.10-15].
- **F42x/F43x ADC accuracy options are mutually exclusive: ADCDC1 in PWR_CR or ADCxDC2 in SYSCFG_PMC.** ADCDC1 requires prefetch OFF and VDD=2.4-3.6V. ADCxDC2 requires fADC >= 30 MHz and 12-bit resolution; enable multiple ADCxDC2 bits only under the simultaneous-sampling/interleaving conditions in AN4073 Table 6. In its 1.65V test with caches ON/prefetch OFF, default dispersion was 8 LSB and either option gave 6 LSB, not a 21-LSB F42x/F43x baseline [7, pp.18-22].
- **Do not toggle I/Os on the same port as an ADC input during conversion.** Avoid starting communication TX just before conversion [7, p.9].
- **AN4073 lab result: averaging by 4 with caches ON/prefetch OFF gave no samples outside +/-5 LSB of the histogram mode at 0.6 Msps.** Under the STM32F407 conditions above, total dispersion was 7-8 LSB; averaging by 8 gave 4-5 LSB total dispersion. This is not a guaranteed ENOB improvement [7, pp.15-17].

## Common Mistakes

- **G0 still booting the loader after first programming.** The flash-empty flag updates during option-byte loading; reload option bytes, power-reset, or clear EMPTY as documented before expecting user-flash boot after a system reset [3, p.21].
- **NRST permanently grounded as an enable wastes current and holds startup indefinitely.** The internal pull-up is approximately 40 kohm; use a low-power mode after releasing reset [5, p.28].
- **STM32H74x/H75x VBAT injection during a fast VDD startup.** If VDD rises within tRSTTEMPO and exceeds VBAT + 0.6V, the internal diode can inject current into the battery. Add a low-drop series diode when the battery cannot accept that current [4, p.10].

## Sources

### Related Rules

- `misc/crystal.md` -- Crystal selection, load cap calculation, and HSE/LSE design
- `protection/esd.md` -- USB ESD protection placement and TVS selection
- `interfaces/usb.md` -- USB layout, impedance control, and connector wiring

### References

1. ST AN4488 (Rev 7, October 2018) -- Getting Started with STM32F4xxxx HW Dev: https://www.st.com/resource/en/application_note/an4488-getting-started-with-stm32f4xxxx-mcu-hardware-development-stmicroelectronics.pdf
2. ST AN2867 (Rev 25) -- Oscillator Design Guide for STM8/STM32: https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8af-al-s-and-stm32-microcontrollers-stmicroelectronics.pdf
3. ST AN5096 (Rev 4) -- Getting Started with STM32G0 HW Dev: https://www.st.com/resource/en/application_note/an5096-getting-started-with-stm32g0-mcus-hardware-development-stmicroelectronics.pdf
4. ST AN4938 (Rev 7, October 2024) -- Getting Started with STM32H7 HW Dev: https://www.st.com/resource/en/application_note/an4938-getting-started-with-stm32h74xig-and-stm32h75xig-mcu-hardware-development-stmicroelectronics.pdf
5. ST AN4899 (Rev 4, May 2026) -- STM32 GPIO HW Settings & Low-Power: https://www.st.com/resource/en/application_note/an4899-stm32-microcontroller-gpio-hardware-settings-and-lowpower-consumption-stmicroelectronics.pdf
6. ST AN4879 (Rev 13) -- USB Hardware/PCB Guidelines for STM32: https://www.st.com/resource/en/application_note/an4879-introduction-to-usb-hardware-and-pcb-guidelines-using-stm32-mcus-stmicroelectronics.pdf
7. ST AN4073 (DocID022945 Rev 5) -- Improving ADC Accuracy (STM32F2/F4): https://www.st.com/resource/en/application_note/an4073-how-to-improve-adc-accuracy-when-using-stm32f2xx-and-stm32f4xx-microcontrollers-stmicroelectronics.pdf
8. ST DS8626 (Rev 12, March 2026) -- STM32F405xx/STM32F407xx datasheet: https://www.st.com/resource/en/datasheet/stm32f405rg.pdf
