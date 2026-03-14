---
source: "ST AN5096 -- Getting Started with STM32G0 HW Dev"
url: "https://www.st.com/resource/en/application_note/an5096-getting-started-with-stm32g0-mcus-hardware-development-stmicroelectronics.pdf"
format: "PDF 35pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 28938
---
# Getting started with STM32G0 MCUs hardware development

## Introduction

This application note is intended for system designers who require a hardware implementation overview of the development board features such as the power supply, clock management, reset control, boot mode settings, and debug management. It shows how to use STM32G0 Series devices and describes the minimum hardware resources required to develop an application.

This document also includes detailed reference design schematics with the description of the main components, interfaces and modes.

## 1 Power supplies and reset sources on STM32G0 Series

This section describes the power supply schemes and the reset and power supply supervisor on STM32G0 Series devices.

STM32G0 Series are Arm Cortex-M0+ based devices.

### 1.1 Power supplies on STM32G0 Series

The STM32G0 Series devices require a 1.7 V to 3.6 V operating supply voltage (VDD). Several different power supplies are provided to specific peripherals:

- **VDD = 1.7 V (1.60 V) to 3.6 V** -- External power supply for the internal regulator and the system analog such as reset, power management and internal clocks. Provided externally through VDD/VDDA pin. The minimum voltage of 1.7 V corresponds to power-on reset release threshold VPOR(MAX). Once this threshold is crossed and power-on reset is released, the functionality is guaranteed down to power-down reset threshold VPDR(MIN).

- **VDDA = 1.62 V (ADC and COMP) / 1.8 V (DAC) / 2.4 V (VREFBUF) to 3.6 V** -- Analog power supply for the A/D converter, D/A converters, voltage reference buffer and comparators. VDDA voltage level is identical to VDD voltage as it is provided externally through VDD/VDDA pin.

- **VDDIO1 = VDD** -- Power supply for the I/Os. VDDIO1 voltage level is identical to VDD voltage as it is provided externally through VDD/VDDA pin.

- **VDDIO2 = 1.6 to 3.6 V** -- Power supply from VDDIO2 pin for selected I/Os. Although VDDIO2 is independent of VDD or VDDA, it must not be applied without valid VDD. Available in some STM32G0Bxxx and STM32G0Cxxx devices. Refer to the product datasheet for detailed information.

- **VBAT = 1.55 V to 3.6 V** -- Power supply (through a power switch) for RTC, TAMP, low-speed external 32.768 kHz oscillator and backup registers when VDD is not present. Provided externally through VBAT pin. When this pin is not available on the package, it is internally bonded to VDD/VDDA.

- **VREF+** -- Input reference voltage for the ADC and DAC, or the output of the internal voltage reference buffer (when enabled). When VDDA < 2V, VREF+ must be equal to VDDA. When VDDA >= 2 V, VREF+ must be between 2 V and VDDA. It can be grounded when the ADC and DAC are not active. The internal voltage reference buffer supports two output voltages configured with VRS bit of VREFBUF_CSR register:
  - VREF+ around 2.048 V (requiring VDDA equal to or higher than 2.4 V)
  - VREF+ around 2.5 V (requiring VDDA equal to or higher than 2.8 V)
  VREF+ is delivered through VREF+ pin. On packages without VREF+ pin, VREF+ is internally connected with VDD, and the internal voltage reference buffer must be kept disabled.

- **VCORE** -- An embedded linear voltage regulator supplies the VCORE internal digital power. VCORE is the power supply for digital peripherals, SRAM and Flash memory. The Flash memory is also supplied by VDD.

| Power supply | STM32G0 Series |
|---|---|
| VDD | 1.7 to 3.6 V |
| VDDIO2 | 1.6 to 3.6 V |
| VREF+ | When VDDA < 2 V, VREF+ must be equal to VDDA. When VDDA >= 2 V, VREF+ must be between 2 V and VDDA |
| VBAT | 1.55 to 3.6 V |

*[Figure 1. STM32G0 Series power supply]*

> Power supply pin pair (VDD/VDDA and VSS/VSSA) must be decoupled with filtering ceramic capacitors as shown above. These capacitors must be placed as close as possible to, or below, the appropriate pins on the underside of the PCB to ensure the good functionality of the device.

*[Figure 2. STM32G0 Series power supply for devices supporting VDDIO2]*

> Power supply pin pair (VDD/VDDA/VDDIO2 and VSS/VSSA) must be decoupled with filtering ceramic capacitors as shown above. These capacitors must be placed as close as possible to, or below, the appropriate pins on the underside of the PCB to ensure the good functionality of the device.

#### 1.1.1 Battery backup

To retain the content of the Backup registers when VDD is turned off, the VBAT pin can be connected to an optional standby voltage supplied by a battery or another source.

The VBAT pin also powers the RTC unit, allowing the RTC to operate even when the main digital supply (VDD) is turned off.

The switch to the VBAT supply is controlled by the POR/PDR circuitry embedded in the reset block.

If no external battery is used in the application, it is recommended to connect VBAT externally to VDD.

#### 1.1.2 Voltage regulator

The voltage regulator, when available on the device, is always enabled after reset. It works under two different modes:

- **Main (MR)** is used in normal operating mode (Run).
- **Low power (LPR)** can be used in Stop mode where the power demand is reduced.

In Standby mode the regulator is in power-down mode. In this mode, the regulator output is in high impedance and the kernel circuitry is powered down, inducing zero consumption and the loss of the register and SRAM contents. However, the following features are available if configured:

- **Independent watchdog (IWDG):** started by writing to its key register or by a hardware option. Once started it cannot be stopped except by a reset.
- **Real-time clock (RTC):** configured by the RTCEN bit in RCC_BDCR.
- **Internal low-speed oscillator (LSI):** configured by the LSION bit in RCC_CSR.
- **External 32.768 kHz oscillator (LSE):** configured by the LSEON bit in RCC_BDCR.

### 1.2 Power supply supervisor on STM32G0 Series

#### 1.2.1 Power-on reset (POR) / power-down reset (PDR) / brown-out reset (BOR)

The devices feature an integrated POR/PDR, coupled with a BOR circuitry. The POR/PDR is active in all power modes. The BOR can be enabled or disabled only through option bytes. It is not available in Shutdown mode.

When the BOR is enabled, four BOR levels can be selected through option bytes, with independent configuration for rising and falling thresholds. During power-on, the BOR keeps the device under reset until the VDD supply voltage reaches the specified BOR rising threshold (VBORRx). At this point, the device reset is released and the system can start.

During power-down, when VDD drops below the selected BOR falling threshold (VBORFx), the device is put under reset again.

> It is not allowed to configure BOR falling threshold (VBORFx) to a value higher than BOR rising threshold (VBORRx).

*[Figure 3. POR, PDR, and BOR thresholds]*

> The reset temporization tRSTTEMPO starts when VDD crosses VPOR threshold, indifferently from the configuration of the BOR option bits. For more details on the brown-out reset thresholds, refer to the electrical characteristics section in the corresponding datasheet.

#### 1.2.2 Programmable voltage detector (PVD)

The PVD can be used to monitor the VDD power supply by comparing it to the thresholds selected through PVDRT[2:0] bits (rising thresholds) and PVDFT[2:0] bits (falling thresholds) in PWR_CR2. VPVDFx should always be set to a lower voltage level than VPVDRx.

The PVD is enabled by setting the PVDE bit.

A PVDO flag is available in PWR_SR2. It indicates if VDD is higher or lower than the PVD threshold. This event is internally connected to EXTI line16 and can generate an interrupt if enabled through the EXTI registers. The PVD output interrupt can be generated when VDD drops below the PVD threshold and/or when VDD rises above the PVD threshold depending on EXTI line16 rising/falling edge configuration.

*[Figure 4. PVD thresholds]*

### 1.3 Reset on STM32G0 Series

#### 1.3.1 Power reset

A power reset is generated when one of the following events occurs:

- Power-on reset (POR) or brown-out reset (BOR)
- Exit from Standby mode
- Exit from Shutdown mode

Power and brown-out reset set all registers to their reset values except the registers of the RTC domain. When exiting Standby mode, all registers in the VCORE domain are set to their reset value. Registers outside the VCORE domain (RTC, WKUP, IWDG, and Standby/Shutdown mode control) are not impacted.

When exiting Shutdown mode, the brown-out reset is generated, resetting all registers except those in the RTC domain.

#### 1.3.2 System reset

System reset sets all registers to their reset values except the reset flags in RCC_CSR and the registers in the RTC domain.

System reset is generated when one of the following events occurs:

- Low level on the NRST pin (external reset)
- Window watchdog event (WWDG reset)
- Independent watchdog event (IWDG reset)
- Software reset (SW reset)
- Low-power mode security reset
- Option byte loader reset
- Power-on reset

The reset source can be identified by checking the reset flags in the RCC_CSR register.

**NRST pin (external reset)**

Through specific option bits, the NRST pin is configurable for operating as:

- **Reset input/output** (default at device delivery) -- Valid reset signal on the pin is propagated to the internal logic, and each internal reset source is led to a pulse generator the output of which drives this pin. The GPIO functionality (PF2) is not available. The pulse generator guarantees a minimum reset pulse duration of 20 us for each internal reset source to be output on the NRST pin. An internal reset holder option can be used, if enabled in the option bytes, to ensure that the pin is pulled low until its voltage meets VIL threshold.
- **Reset input** -- Any valid reset signal on the NRST pin is propagated to device internal logic, but resets generated internally by the device are not visible on the pin. GPIO functionality (PF2) is not available.
- **GPIO** -- The pin can be used as PF2 standard GPIO. The reset function of the pin is not available. Reset is only possible from device internal reset sources and it is not propagated to the pin.

*[Figure 5. Simplified diagram of the reset circuit]*

> Upon power reset or wakeup from shutdown mode, the NRST pin is configured as Reset input/output and driven low by the system until it is reconfigured to the expected mode when the option bytes are loaded, in the fourth clock cycle after the end of tRSTTEMPO.

**Software reset**

The SYSRESETREQ bit in Cortex-M0+ application interrupt and reset control register must be set to force a software reset on the device (refer to PM0223).

**Low-power mode security reset**

To prevent that critical applications mistakenly enter a low-power mode, three low-power mode security resets are available. If enabled in option bytes, the resets are generated in the following conditions:

- **Entering Standby mode:** enabled by resetting nRST_STDBY bit in user option bytes.
- **Entering Stop mode:** enabled by resetting nRST_STOP bit in user option bytes.
- **Entering Shutdown mode:** enabled by resetting nRST_SHDW bit in user option bytes.

**Option byte loader reset**

Generated when the OBL_LAUNCH bit (bit 27) is set in the FLASH_CR register. This bit is used to launch the option byte loading by software.

#### 1.3.3 RTC domain reset

An RTC domain reset is generated when one of the following events occurs:

- Software reset, triggered by setting the BDRST bit in RCC_BDCR.
- VDD or VBAT power on, if both supplies have previously been powered off.

An RTC domain reset only affects the LSE oscillator, the RTC, the backup registers and the RCC RTC domain control register.

## 2 Clocks

STM32G0 Series provide the following clock sources producing primary clocks:

- **HSI16 RC** -- high-speed fully-integrated RC oscillator producing HSI16 clock (about 16 MHz)
- **HSI48 RC** -- high-speed fully-integrated RC oscillator producing HSI48 clock for USB (about 48 MHz)
- **HSE OSC** -- high-speed oscillator with external crystal/ceramic resonator or external clock source, producing HSE clock (4 to 48 MHz)
- **LSI RC** -- low-speed fully-integrated RC oscillator producing LSI clock (about 32 kHz)
- **LSE OSC** -- low-speed oscillator with external crystal/ceramic resonator or external clock source, producing LSE clock (accurate 32.768 kHz or external clock up to 1 MHz)
- **I2S_CKIN** -- pin for direct clock input for I2S1 peripheral

Each oscillator can be switched on or off independently when it is not used, to optimize power consumption.

The device produces secondary clocks by dividing or multiplying the primary clocks:

- **HSISYS** -- clock derived from HSI16 through division by a factor programmable from 1 to 128
- **PLLPCLK, PLLQCLK and PLLRCLK** -- clocks output from the PLL block
- **SYSCLK** -- clock obtained through selecting one of LSE, LSI, HSE, PLLRCLK, and HSISYS clocks
- **HCLK** -- clock derived from SYSCLK through division by a factor programmable from 1 to 512
- **HCLK8** -- clock derived from HCLK through division by eight
- **PCLK** -- clock derived from HCLK through division by a factor programmable from 1 to 16
- **TIMPCLK** -- clock derived from PCLK, running at PCLK frequency if APB prescaler division factor is 1, or at twice the PCLK frequency otherwise

HSISYS is used as system clock source after startup from reset, with the division by 1 (producing HSI16 frequency). HCLK and PCLK maximum allowed frequency is 64 MHz.

Peripheral clock sources (selected from bus they are attached to except):

- **TIMx:** TIMPCLK (all timers), PLLQCLK (TIM1 and TIM15)
- **LPTIMx:** LSI, LSE, HSI16, PCLK, LPTIMx_IN. Wakeup from Stop only with LSI or LSE.
- **UCPD:** always clocked with HSI16
- **ADC:** SYSCLK, HSI16, PLLPCLK
- **USARTx / LPUART1:** SYSCLK, HSI16, LSE, PCLK. Wakeup from Stop only with HSI16 or LSE.
- **I2Cx:** SYSCLK, HSI16, PCLK. Wakeup from Stop only with HSI16.
- **I2S1:** SYSCLK, HSI16, PLLPCLK, I2S_CKIN pin
- **RNG:** SYSCLK, HSI16/8, PLLQCLK. RNG clock can additionally be divided by 2, 4, or 8.
- **CEC:** HSI16/488, LSE
- **RTC:** LSE, LSI, HSE/32. Wakeup from Stop only with LSI or LSE.
- **IWDG:** always clocked with LSI
- **USB:** HSE, HSI48, PLLQCLK
- **FDCAN:** HSE, PCLK, PLLQCLK
- **SysTick:** HCLK, HCLK/8

*[Figure 6. Clock tree]*

### 2.1 HSE clock

The high speed external clock signal (HSE) can be generated from two possible clock sources:

- HSE external crystal/ceramic resonator
- HSE user external clock

The resonator and the load capacitors have to be placed as close as possible to the oscillator pins in order to minimize output distortion and startup stabilization time. The loading capacitance values must be adjusted according to the selected oscillator.

*[Figure 7. HSE/LSE clock sources]*

**External crystal/ceramic resonator (HSE crystal)**

The 4 to 48 MHz external oscillator has the advantage of producing a very accurate rate on the main clock. The HSERDY flag in RCC_CR indicates if the HSE oscillator is stable or not. At startup, the clock is not released until this bit is set by hardware.

**External source (HSE bypass)**

In this mode, an external clock source must be provided with a frequency of up to 48 MHz. Selected by setting the HSEBYP and HSEON bits in RCC_CR. The external clock signal (square, sinus or triangle) with ~40-60% duty cycle depending on the frequency must drive the OSC_IN pin. The OSC_OUT pin can be used as a GPIO or configured as OSC_EN alternate function to provide an enable signal to external clock synthesizer.

### 2.2 HSI16 clock

The HSI16 clock signal is generated from an internal 16 MHz RC oscillator. It provides a clock source at low cost (no external components) with faster startup time than the HSE crystal oscillator, but less accurate even after calibration.

**Calibration:** Each device is factory calibrated to 1% accuracy at TA=25C. After reset, the factory calibration value is loaded in HSICAL[7:0] bits in RCC_ICSCR. Voltage or temperature variations can be trimmed using HSITRIM[6:0] bits in RCC_ICSCR.

### 2.3 HSI48 clock

Available on STM32G0B1xx and STM32G0C1xx devices. Provides a high-precision clock to the USB peripheral thanks to the clock recovery system (CRS). CRS uses the USB SOF signal, LSE clock or an external signal as timing reference to precisely adjust the HSI48 RC oscillator frequency.

HSI48 is disabled in Stop or Standby mode. Free-run frequency accuracy is ~3% at TA=25C. It is automatically enabled when selected as clock source for the USB peripheral.

### 2.4 PLL

The internal PLL multiplies the frequency of HSI16- or HSE-based clock. The allowed input frequency range is from 2.66 to 16 MHz. A dedicated divider PLLM with division factor programmable from 1 to 8 allows setting frequency within the valid PLL input range.

PLL configuration must be done before enabling the PLL. To modify:
1. Disable the PLL by setting PLLON to 0 in RCC_CR
2. Wait until PLLRDY is cleared
3. Change the desired parameter
4. Enable the PLL by setting PLLON to 1
5. Enable desired PLL outputs by configuring PLLPEN, PLLQEN, and PLLREN in RCC_PLLCFGR

### 2.5 LSE clock

The LSE crystal is a 32.768 kHz low speed external crystal or ceramic resonator. It provides a low-power but highly accurate clock source to the RTC peripheral.

The crystal oscillator driving strength can be changed at runtime using LSEDRV[1:0] bits in RCC_BDCR to obtain the best compromise between robustness/short start-up time and low-power consumption.

**External source (LSE bypass):** frequency up to 1 MHz. Selected by setting LSEBYP and LSEON bits. External clock signal drives OSC32_IN pin.

### 2.6 LSI clock

The LSI RC acts as a low-power clock source (32 kHz) that can be kept running in Stop and Standby mode for IWDG and RTC.

### 2.7 System clock (SYSCLK) selection

One of the following clocks can be selected as SYSCLK: LSI, LSE, HSISYS, HSE, PLLRCLK.

System clock maximum frequency is 64 MHz. Upon system reset, HSISYS clock derived from HSI16 is selected. When a clock source is used directly or through the PLL as system clock, it is not possible to stop it.

### 2.8 Clock source frequency versus voltage scaling

| Clock | Range 1 Max (MHz) | Range 2 Max (MHz) |
|---|---|---|
| HSI16 | 16 | 16 |
| HSE | 48 | 16 |
| PLLPCLK | 122 (VCO max 344 MHz) | 40 (VCO max 128 MHz) |
| PLLQCLK | 128 (VCO max 344 MHz) | 32 (VCO max 128 MHz) |
| PLLRCLK | 64 (VCO max 344 MHz) | 16 (VCO max 128 MHz) |

### 2.9 Clock security system (CSS)

If a failure is detected on the HSE clock:
- The HSE oscillator is automatically disabled
- A clock failure event is sent to the break input of TIM1, TIM15, TIM16 and TIM17
- CSSI (clock security system interrupt) is generated, linked to Cortex-M0+ NMI

If HSE is selected directly or indirectly as system clock and a failure is detected, the system clock switches automatically to HSISYS.

### 2.10 Clock security system for LSE clock (LSECSS)

LSECSSON must be written after LSE and LSI are enabled and ready, and after selecting the RTC clock by RTCSEL. Works in all modes except VBAT. If LSE clock fails and is used as system clock, it switches automatically to LSI.

The frequency of the LSE oscillator must exceed 30 kHz to avoid false positive detections.

### 2.11 ADC clock

Derived from system clock or PLLPCLK output. Can reach 122 MHz and can be divided by prescalers: 1, 2, 4, 6, 8, 10, 12, 16, 32, 64, 128 or 256 (ADC1_CCR register). Alternatively, derived from AHB clock divided by 1, 2, or 4 (CKMODE bit fields in ADC1_CCR). If programmed factor is 1, the AHB prescaler must be set to 1.

### 2.12 RTC clock

RTCCLK source can be HSE/32, LSE or LSI, selected by RTCSEL[1:0] in RCC_BDCR. Selection cannot be modified without resetting the RTC domain. PCLK frequency must be >= RTCCLK frequency.

- **LSE selected:** RTC continues even if VDD is off, provided VBAT is maintained.
- **LSI selected:** RTC state not guaranteed if VDD is off.
- **HSE/32 selected:** RTC state not guaranteed if VDD or VCORE is off.

### 2.13 Timer clock

TIMPCLK is derived from PCLK: equals PCLK if APB prescaler is 1, otherwise twice PCLK. For TIM1 and TIM15, PLLQCLK can also be selected (max 128 MHz).

### 2.14 Watchdog clock

If the IWDG is started by hardware option or software access, the LSI oscillator is forced ON and cannot be disabled.

### 2.15 Clock-out capability

**MCO:** One of LSI, LSE, SYSCLK, HSI16, HSE, PLLRCLK can be output. On STM32G0B1xx/C1xx, two clock outputs (MCO and MCO2) are available with additional sources: HSI48, PLLPCLK, PLLQCLK, RTCCLK, RTC WAKEUP.

**LSCO:** LSI or LSE can be output. Selection controlled by LSCOSEL in RCC_BDCR. Available in Stop 0, Stop 1 and Standby modes.

### 2.16 Internal/external clock measurement with TIM14/TIM16/TIM17

**TIM14** channel 1 input capture sources: GPIO, RTCCLK, HSE/32, MCO.

**TIM16** channel 1 input capture sources: GPIO, LSI, LSE, RTC wakeup interrupt.

**TIM17** channel 1 input capture sources: GPIO, HSE/32, MCO.

**Calibration of the HSI16 oscillator:** Counting HSISYS clock pulses between consecutive edges of the LSE clock allows measuring HSI16 frequency with nearly the same accuracy as the 32.768 kHz quartz crystal.

Measures to improve measurement accuracy:
- Set HSISYS divider to 1
- Average results of multiple consecutive measurements
- Use input capture prescaler (1 capture every up to 8 periods)
- Use LSE clock for RTC and RTC wakeup interrupt signal as time reference

## 3 Boot configuration

Three different boot modes can be selected through the BOOT0 pin, BOOT_LOCK bit in FLASH_SECR register, and boot configuration bits nBOOT1, BOOT_SEL and nBOOT0 in the user option byte:

| BOOT_LOCK | nBOOT1 | BOOT0 pin | nBOOT_SEL | nBOOT0 | Selected boot area |
|---|---|---|---|---|---|
| 0 | X | 0 | 0 | X | Main Flash memory |
| 0 | 1 | 1 | 0 | X | System memory |
| 0 | 0 | 1 | 0 | X | Embedded SRAM |
| 0 | X | X | 1 | 1 | Main Flash memory |
| 0 | 1 | X | 1 | 0 | System memory |
| 0 | 0 | X | 1 | 0 | Embedded SRAM |
| 1 | X | X | X | X | Main Flash memory forced |

The boot mode configuration is latched on the 4th rising edge of SYSCLK after a reset. Also re-sampled when exiting from Standby mode.

After startup delay, the CPU fetches the top-of-stack value from address 0x0000 0000, then starts code execution from the boot memory at 0x0000 0004.

- **Boot from main Flash memory:** aliased at 0x0000 0000, original at 0x0800 0000.
- **Boot from system memory:** aliased at 0x0000 0000, original at 0x1FFF0000.
- **Boot from embedded SRAM:** aliased at 0x0000 0000, original at 0x2000 0000.

**BOOT_LOCK:** Forces unique entry point in main Flash memory regardless of other boot mode bits.

**Empty check:** EMPTY bit of FLASH_ACR allows easy programming of virgin devices by boot loader. When set, System memory (boot loader) is selected instead of Main Flash. Updated only during Option bytes loading.

**Physical remap:** Application software can modify the memory accessible in the code area via MEM_MODE bits in SYSCFG_CFGR1.

**Embedded boot loader:** Located in System memory, used to reprogram Flash via:
- USART on pins PA2/PA3, PA9/PA10 or PC10/PC11
- I2C on pins PB6/PB7 or PB10/PB11
- SPI on pins PA4/PA5/PA6/PA7 or PB12/PB13/PB14/PB15

## 4 Debug management

### 4.1 Introduction

The host/target interface connects the host to the application board via a hardware debug tool, an SWD connector and a cable.

*[Figure 11. Host-to-board connection]*

### 4.2 SWD port (serial wire debug)

The STM32G0 Series core integrates the serial wire debug port (SW-DP), an ARM standard CoreSight debug port with a 2-pin (clock + data) interface.

### 4.3 Pinout and debug port pins

#### 4.3.1 Serial wire debug (SWD) pin assignment

| SWD pin name | Type | Debug assignment |
|---|---|---|
| SWDIO | I/O | Serial wire data input/output -- PA13 |
| SWCLK | I | Serial wire clock -- PA14 |

After reset, the SWD pins are assigned as dedicated pins immediately usable by the debugger host. The MCU offers the possibility to disable SWD, releasing pins for GPIO usage.

#### 4.3.2 Internal pull-up and pull-down on SWD pins

Reset states: SWDIO = alternate function pull-up, SWCLK = alternate function pull-down. Embedded pull-up and pull-down resistors remove the need for external resistors.

*[Figure 12. SWD port connection]*

#### 4.3.3 Multi bonding on STM32G03xxx and STM32G04xxx small packages

A multi-bonding approach is used on small packages to offer maximum alternate functions and analog inputs. Multiple die pads are connected internally to a single package pin. Each alternate function is accessible if configured at I/O port level.

Configuration of each device pad must be done carefully as there are no design protections to avoid interferences between pads. By default, all GPIOs (except PA14) are configured in analog input.

Multi bonding offers extended drive strength. By configuring multiple pads in output mode (same output level), the transistor drive resistance is decreased.

## 5 Recommendations

### 5.1 Printed circuit board

Use a multilayer PCB with separate ground and VDD layers for good decoupling and shielding. If not feasible, ensure good structure for ground and power supply.

### 5.2 Component position

Separate: high-current circuits, low-voltage circuits, digital component circuits, circuits by EMI contribution to reduce cross-coupling.

### 5.3 Ground and power supply (VDD, VDDIO2)

Every block should be grounded individually with all ground returns to a single point. Loops must be avoided or have minimum area. Decoupling capacitors must be placed as close as possible to the device.

Power supply should be close to ground line to minimize supply loop area (acts as antenna for EMI). All component-free PCB areas should be filled with additional grounding.

### 5.4 Decoupling

All power supply and ground pins must be properly connected with low impedance (thick tracks, dedicated power planes).

A power supply pair should be decoupled with 100 nF filtering ceramic capacitor and a chemical capacitor of about 4.7 uF. These capacitors need to be placed as close as possible to, or below, the appropriate pins on the underside of the PCB. Typical values are 10 nF to 100 nF.

*[Figure 14. Typical layout for VDD/VSS pair]*

### 5.5 Other signals

EMC performance can be improved by studying: signals where temporary disturbance affects running process permanently (interrupts, handshaking strobes), digital signals (best electrical margin, slow Schmitt triggers), noisy signals (clock), sensitive signals (high-Z).

### 5.6 Unused I/O and features

Unused I/Os should be connected to a fixed logic level of 0 or 1 by external or internal pull-up or pull-down, or configured as output mode using software. Unused features should be frozen or disabled.

## 6 Reference design

### 6.1 Description

The reference design introduces the STM32G081, running at 64 MHz, combining the Cortex-M0+ 32-bit RISC CPU core with 128 Kbytes Flash and 36 Kbytes SRAM.

*[Figure 15. STM32G0 Series reference schematic]*

> If no external battery is used in the application, it is recommended to connect VBAT externally to VDD.

#### 6.1.1 Clock
- HSE: X1 -- 8 MHz crystal
- LSE: X2 -- 32.768 kHz crystal for embedded RTC

#### 6.1.2 Reset
Reset signal is active low. Sources: reset button (B1), debugging tools via CN1.

> By default the reset holder is activated. Any internal reset results in pulling down NRST pin until it reaches its VIL threshold.

#### 6.1.3 Boot mode
Boot option configured by default through option bytes. BOOT0 pin can be used for physical control on boot entry point.

#### 6.1.4 SWD interface
Standard SWD connector connection. It is recommended to connect the reset pin to be able to reset from the tool.

### 6.2 Component references

**Mandatory components:**

| Component | Reference | Value | Qty | Comments |
|---|---|---|---|---|
| Microcontroller | U1 | STM32G081RBT6 | 1 | 64-pin package |
| Capacitor | C1 | 100 nF | 1 | Ceramic decoupling |
| Capacitor | C6 | 4.7 uF | 1 | Used for VDD |

**Optional components:**

| Component | Reference | Value | Qty | Comments |
|---|---|---|---|---|
| Resistor | R1 | 390 ohm | 1 | Used for HSE (typical example) |
| Capacitor | C4 | 100 nF | 1 | Ceramic for RESET button |
| Capacitor | C5 | 100 nF | 1 | Ceramic decoupling |
| Capacitor | C7/C8 | 10 pF | 2 | Used for LSE |
| Capacitor | C9/C10 | 20 pF | 2 | Used for HSE |
| Quartz | X1 | 8 MHz | 1 | Used for HSE |
| Quartz | X2 | 32 kHz | 1 | Used for LSE |
| Battery | BT1 | 3 V | 1 | If no battery, connect VBAT to VDD |
| Push-button | B1 | - | 1 | Reset button |
| SWD connector | CN1 | FTSH-105-01-L-DV | 1 | Program/debug |
