---
source: "ST AN4938 -- Getting Started with STM32H7 HW Dev"
url: "https://www.st.com/resource/en/application_note/an4938-getting-started-with-stm32h74xig-and-stm32h75xig-mcu-hardware-development-stmicroelectronics.pdf"
format: "PDF 46pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 14442
---
# Getting started with STM32H74xI/G and STM32H75xI/G MCU hardware development

## Introduction

This application note is intended for system designers who develop applications based on the STM32H750 Value line, STM32H742, STM32H743/753, STM32H745/755, and STM32H747/757 lines, and who need an implementation overview of power supply, package selection, clock management, reset control, boot mode settings, and debug management.

## 1 General information

This document applies to STM32H74xI/G and STM32H75xI/G Arm Cortex-based devices.

## 2 Power supplies

### 2.1 Introduction

STM32H74xI/G and STM32H75xI/G devices require 1.71 to 3.6 V operating voltage supply (VDD), reducible to 1.62 V by using an external power supervisor with PDR_ON pin connected to VSS.

Digital power can be supplied by internal system voltage regulator or directly by external supply voltage. Digital power voltage can be dynamically set at different values for maximum performance.

RTC, RTC backup registers, and backup SRAM can be powered from VBAT (1.2 to 3.6 V) when VDD is off.

#### 2.1.1 Independent analog supply and reference voltage

Independent power supply for analog peripherals (VDDA pin, VSSA ground). Internal voltage reference buffer supports four voltages (VREFBUF_CSR register).

VDDA minimum depends on peripheral used:
- No analog peripheral: 0 V
- ADC or comparator: 1.62 V
- DAC: 1.8 V
- OPAMP: 2.0 V
- VREFBUF_OUT: depends on required level

#### 2.1.2 USB transceiver independent power supply

- **VDD50USB available:** Receives 4.0-5.5 V (typically from VBUS). Regulated output (3.0-3.6 V) on VDD33USB. Condition: VDD50USB < VDD + 300 mV.
- **VDD33USB available:** Receives 3.0-3.6 V. If VDD50USB also available, connect together. When separate from VDD: must be last applied/first removed, VDD33USB < VDD + 300 mV during power-on/down.
- **Neither available:** VDD must be 3.0-3.6 V for USB transceiver use.

*[Figure 1. VDD33USB connected to VDD power supply]*

*[Figure 2. VDD33USB/VDD50USB connected to external power supply]*

#### 2.1.3 Battery backup domain

VBAT pin connected to optional 1.2-3.6 V battery. Otherwise connect to VDD. During VBAT mode: PC14/PC15 as LSE pins only, PC13 as TAMP1, PI8 as TAMP2, PC1 as TAMP3.

During startup, if VDD > VBAT + 0.6 V, current may be injected into VBAT through internal diode. If battery cannot support this, add external low-drop diode.

**Battery charging:** When VDD present, battery can be charged through internal 5 kohm or 1.5 kohm resistor (software configurable). Automatically disabled in VBAT mode.

#### 2.1.4 LDO voltage regulator

Always enabled after reset (default VOS3). Three modes: Run (full power), Stop (low power, preserves registers/SRAM), Standby (powered down, contents lost except standby/backup domain).

Supports dynamic voltage scaling: VOS0, VOS1, VOS2, VOS3, SVOS3, SVOS4, SVOS5. Requires capacitor on VCAP pins.

#### 2.1.5 SMPS step-down converter

Available on some devices for power optimization. Enabled via SDEN bit in PWR_CR3.

**Internal supply mode (Direct):** VCORE domain follows system operating modes with voltage scaling via VOS/SVOS bits. Can also supply LDO in normal or high-performance mode.

**External supply mode:** Supplies external circuits in MR mode with output voltage of 2.5 V or 1.8 V (SDLEVEL bits).

### 2.2 Power supply scheme

- **VDD = 1.62-3.6 V:** External power for I/Os, flash, system analog. Requires single 4.7 uF min capacitor per package + 100 nF per VDD pin. Below 1.71 V requires external reset controller.
- **VDDA = 1.62-3.6 V:** Analog power for ADC, DAC, OPAMP. 100 nF ceramic + 1 uF capacitor.
- **VDD33USB / VDD50USB:** USB transceiver power. VDD50USB: 4.7 uF capacitor. VDD33USB: 100 nF + 1 uF capacitors.
- **VBAT = 1.2-3.6 V:** RTC, 32 kHz oscillator, backup registers. Connect to VDD with 100 nF if no battery.
- **VREF+:** Connect to VDDA or separate reference (100 nF + 1 uF). Must be <= VDDA, minimum 2 V when VDDA > 2 V with ADC, otherwise 1.62 V.
- **VDDLDO = 1.62-3.6 V:** Regulator supply. VCAP1/VCAP2: 2.2 uF low ESR (< 100 mohm). VDDLDOx pins connected together with 4.7 uF capacitor.

**SMPS-equipped devices additional supplies:**
- **VDDSMPS = 1.62-3.6 V:** Must equal VDD level. 4.7 uF capacitor (ESR 100 mohm).
- **VLXSMPS:** 2.2 uH inductor with 220 pF capacitor.
- **VFBSMPS = VCORE = 1.8 or 2.5 V:** 10 uF capacitor (ESR 20 mohm).

**DSI-equipped devices (STM32H7x7I/G):**
- **VDDDSI = 1.8-3.6 V:** DSI regulator supply.
- **VDD12DSI = 1.15-1.3 V:** Optional supply for DSI PHY.
- **VCAPDSI:** 2.2 uF capacitor for regulator dynamic performance.

Additional filtering: VDDA via ferrite bead to VDD. VREF+ via 47 ohm resistor to VDDA.

*[Figure 3. Power supply overview]*

### 2.3 Reset and power supply supervisor

#### 2.3.1 Power-on reset (POR) / power-down reset (PDR)

Integrated POR/PDR allows proper operation from 1.71 V. Device remains in reset when VDD below threshold. tRSTTEMPO ~2.6 ms. VPOR/PDR rising: 1.66 V typ, falling: 1.62 V typ.

On packages with PDR_ON pin: supervisor enabled by holding PDR_ON high.

*[Figure 4. Power on reset/power down reset waveform]*

#### 2.3.2 Programmable voltage detector (PVD)

Monitors VDD via PLS[2:0] bits in PWR_CR1. PVDO flag in PWR_CSR1 indicates VDD vs threshold. Connected to EXTI line16 for interrupt generation.

#### 2.3.3 Analog voltage detector (AVD)

Monitors VDDA via ALS[1:0] in PWR_CR1. Threshold: 1.7, 2.1, 2.5, or 2.8 V. Enabled via AVDEN bit.

#### 2.3.4 System reset

Generated by: NRST pin low, brownout reset, VDD below threshold, IWDG, WWDG, low-power mode reset, Cortex-M7 SFTRESET.

*[Figure 6. Reset circuit]*

Pulse generator produces minimum 20 us reset pulse.

#### 2.3.5 Internal power supervisor ON

On packages with PDR_ON: enabled by holding PDR_ON high. Otherwise always enabled.

#### 2.3.6 Internal power supervisor OFF

Available on packages with PDR_ON pin. Connect PDR_ON to VSS. Requires external power supply supervisor on VDD and NRST.

When internal reset is OFF: POR/PDR disabled, BOR must be disabled, PVD disabled, VBAT functionality unavailable (connect VBAT to VDD).

*[Figure 7. Power supply supervisor interconnection with internal power supervisor OFF]*

*[Figure 8. NRST circuitry timing example]*

#### 2.3.7 Bypass mode

Power management unit can be bypassed (software configurable). Core power supplied through VCAPx pins (connected together). External voltage must be consistent with targeted maximum frequency. In Standby mode, external source switched off.

External voltage must be present before or at same time as VDDLDO. Keep above 1.15 V until LDO disabled by software.

## 3 Alternate function mapping to pins

Use STM32CubeMX tool for peripheral alternate function mapping exploration.

## 4 Clocks

Four system clock sources: HSI, CSI, HSE, Main PLL.

Two secondary clock sources:
- 32 kHz LSI RC (drives IWDG, optionally RTC)
- 32.768 kHz LSE crystal (optionally drives RTC)

### 4.1 HSE oscillator clock

Two sources: external user clock or external crystal/ceramic resonator.

Resonator and load capacitors placed as close as possible to oscillator pins.

**External crystal (HSE crystal):** 4-48 MHz. 25 MHz is good choice for accurate Ethernet, USB OTG HS, I2S, and SAI. CL1/CL2: 5-25 pF range (typical). ~10 pF estimated for combined pin and board capacitance.

**External clock (HSE bypass):** Square, sinus, or triangle with ~50% duty cycle driving OSC_IN pin.

### 4.2 LSE oscillator clock

**External crystal (LSE crystal):** 32.768 kHz. Provides low-power, highly accurate RTC clock. Drive strength configurable via LSEDRV[1:0] in RCC_BDCR: Low (00), Medium-low (10), Medium-high (01), High (11).

**External clock (LSE bypass):** Up to 1 MHz driving OSC32_IN pin.

> OSC32_IN and OSC32_OUT can be used as GPIO, but not recommended for both RTC and GPIO in same application.

### 4.3 Clock security system (CSS)

Two CSS: one for HSE, one for LSE.

**HSE CSS:** If HSE failure detected, system clock switches to HSI, clock failure event sent to TIM1/TIM8/TIM15/TIM16/TIM17 break inputs, NMI generated. If HSE was PLL source, PLL also disabled.

**LSE CSS:** Must be enabled only when LSE is enabled/ready and after RTC clock selected via RTCSRC[1:0]. Wakes from all low-power modes except VBAT on failure.

## 5 Boot configuration

### 5.1 Boot mode selection

| BOOT pin | Boot address option bytes | Boot space |
|---|---|---|
| 0 | BOOT_ADD0[15:0] | Default: User Flash at 0x0800 0000 |
| 1 | BOOT_ADD1[15:0] | Default: System Flash at 0x1FF0 0000 |

BOOT_ADD0/BOOT_ADD1 allow programming any boot address from 0x0000 0000 to 0x3FFF 0000 (all flash, all RAM, system memory bootloader).

When Flash level 2 protection enabled, only boot from flash is available.

### 5.2 Boot pin connection

*[Figure 14. Boot mode selection implementation example]*

### 5.3 System bootloader mode

The bootloader is programmed by ST during production and supports communication peripherals for reprogramming.

## 6 Debug management

### 6.1 Introduction

The host/target interface includes: hardware debug tool, SWJ connector, and cable.

*[Figure 15. Host to board connection]*

### 6.2 SWJ debug port (serial wire and JTAG)

STM32H7 core integrates Serial Wire / JTAG debug port (SWJ-DP).

#### 6.2.1 TPIU trace port

Available for trace data output.

#### 6.2.2 External debug trigger

External trigger pins available for debug.

### 6.3 Pinout and debug port pins

#### 6.3.1 SWJ debug port pins

| SWJ pin name | JTAG debug port | SW debug port | Type | Pin assignment |
|---|---|---|---|---|
| JTMS/SWDIO | JTMS | SWDIO | I/O | PA13 |
| JTCK/SWCLK | JTCK | SWCLK | I | PA14 |
| JTDI | JTDI | -- | I | PA15 |
| JTDO/TRACESWO | JTDO | SWO | O | PB3 |
| NJTRST | NJTRST | -- | I | PB4 |

#### 6.3.2 Flexible SWJ-DP pin assignment

After reset, all five SWJ-DP pins assigned as dedicated debug pins. MCU offers possibility to disable individual pins for GPIO usage.

#### 6.3.3 Internal pull-up and pull-down on JTAG pins

JTMS/SWDIO: pull-up, JTCK/SWCLK: pull-down, JTDI: pull-up, JTDO: floating, NJTRST: pull-up. Embedded resistors remove need for external resistors.

*[Figure 16. JTAG connector implementation]*

## 7 Recommendations

### 7.1 Printed circuit board

Multilayer PCB with separate ground and VDD layers recommended for good decoupling and shielding.

### 7.2 Component position

Separate: high-current, low-voltage, digital, and EMI-contributing circuits to reduce cross-coupling.

### 7.3 Ground and power supply (VSS, VDD)

Ground each block individually with returns to single point. Minimize loop areas. Decoupling capacitors as close as possible to device. Power supply close to ground line to minimize supply loop area.

### 7.4 Decoupling

All power supply and ground pins properly connected with low impedance. Power supply pair decoupled with 100 nF ceramic + ~4.7 uF, placed as close as possible to or below appropriate pins.

*[Figure 17. Typical layout for VDD/VSS pair]*

### 7.5 Other signals

Study: signals where disturbance affects process permanently (interrupts, handshaking), digital signals (maximize electrical margin, slow Schmitt triggers), noisy signals (clock), sensitive signals (high-Z).

### 7.6 Unused I/Os and features

Unused I/Os: connect to fixed logic level via external or internal pull-up/pull-down, or configure as output. Unused features: freeze or disable (default value).

## 8 Reference design

### 8.1 Description

STM32H753XI reference design with 176-pin LQFP package.

*[Figure 18. STM32H753XI reference schematic]*

#### 8.1.1 Clocks
- HSE: 25 MHz crystal
- LSE: 32.768 kHz crystal for RTC

#### 8.1.2 Reset
Active-low reset with reset button and debug connector.

#### 8.1.3 Boot mode
BOOT0 pin with 10 kohm pull-down resistor (default boot from Flash).

#### 8.1.4 SWJ interface
Standard JTAG connector connection.

#### 8.1.5 Power supply
See power supply scheme section.

### 8.2 Component references

**Mandatory components:**

| Component | Reference | Value | Qty | Comments |
|---|---|---|---|---|
| Microcontroller | U1 | STM32H753XI | 1 | 176-pin LQFP |
| Capacitor | C1..CN | 100 nF | N | Ceramic decoupling per VDD pin |
| Capacitor | C_bulk | 4.7 uF | 1 | Package bulk |
| Capacitor | CVDDA | 100 nF + 1 uF | 2 | VDDA decoupling |
| Capacitor | CVCAP | 2.2 uF (low ESR) | 2 | VCAP1/VCAP2 |

**Optional components:**

| Component | Value | Comments |
|---|---|---|
| HSE crystal (X1) | 25 MHz | With load capacitors |
| LSE crystal (X2) | 32.768 kHz | With load capacitors |
| Battery | 3 V | VBAT, or connect VBAT to VDD |
| Reset button | -- | External reset |
| JTAG connector | 20-pin | Program/debug |

## 9 Recommended PCB routing guidelines

### 9.1 PCB stack-up

**Four-layer example:** Signal - Ground - Power - Signal

**Six-layer example:** Signal - Ground - Signal - Signal - Power - Signal

*[Figure 19. Four layer PCB stack-up example]*

*[Figure 20. Six layer PCB stack-up example]*

### 9.2 Crystal oscillator

Place crystal and load capacitors as close as possible to oscillator pins. Route crystal traces on same layer, short and symmetric. Ground guard ring around crystal recommended. Avoid routing other signals near crystal traces.

### 9.3 Power supply decoupling

Place decoupling capacitors as close as possible to power pins, preferably underneath the device on the opposite PCB layer. Minimize via inductance with short, wide traces.

*[Figure 21. Decoupling capacitor placement depending on package type]*

*[Figure 22. Example of decoupling capacitor placed underneath the STM32H74xI/G and STM32H75xI/G]*

### 9.4 High-speed signal layout

#### 9.4.1 SDMMC bus interface

Match trace lengths for data and clock signals. Keep traces as short as possible. Use ground plane reference.

#### 9.4.2 Flexible memory controller (FMC) interface

Match trace lengths for address, data, and control signals. Minimize stubs.

#### 9.4.3 Quad serial parallel interface (QUADSPI)

Match trace lengths for all QUADSPI signals. Keep traces short with controlled impedance.

#### 9.4.4 Embedded trace macrocell (ETM)

Match trace lengths for ETM signals. Keep traces short.
