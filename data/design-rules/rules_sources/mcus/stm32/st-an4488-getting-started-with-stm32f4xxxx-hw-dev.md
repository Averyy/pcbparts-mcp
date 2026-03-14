---
source: "ST AN4488 -- Getting Started with STM32F4xxxx HW Dev"
url: "https://www.st.com/resource/en/application_note/an4488-getting-started-with-stm32f4xxxx-mcu-hardware-development-stmicroelectronics.pdf"
format: "PDF 50pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 46926
---
# Getting started with STM32F4xxxx MCU hardware development

## Introduction
This application note is intended for system designers who require an overview of the
hardware implementation of the development board, with focus on features like
- power supply
- package selection
- clock management
- reset control
- boot mode settings
- debug management.
This document shows how to use the high-density high-performance microcontrollers listed
in Table 1, and describes the minimum hardware resources required to develop an
application based on those products.
Detailed reference design schematics are also contained in this document, together with
descriptions of the main components, interfaces and modes.

**Table 1. Applicable products**

Type Part numbers and Product lines
STM32F401xB / STM32F401xC
STM32F401xD / STM32F401xE
STM32F405/415 line
STM32F407/417 line
STM32F410x8 / STM32F410xB
STM32F411xC / STM32F411xE
Microcontrollers
STM32F412xE / STM32F412xG
STM32F413/423 line
STM32F427/437 line
STM32F429/439 line
STM32F446 line
STM32F469/479 line

## 1 Reference documents

The following documents are available on www.st.com.

**Table 2. Referenced documents**

Reference Title
AN2867 Oscillator design guide for ST microcontrollers
AN2606 STM32 microcontroller system memory boot mode
AN3364 Migration and compatibility guidelines for STM32 microcontroller applications
This document applies to Arm®(a)-based devices.
a. Arm is a registered trademark of Arm Limited (or its subsidiaries) in the US and/or elsewhere.

## 2 Power supplies

The operating voltage supply (V_DD) range is 1.8 V to 3.6 V, which can be reduced down to 1.7 V with some restrictions, as detailed in the product datasheets. An embedded regulator is used to supply the internal 1.2 V digital power.
The real-time clock (RTC), backup registers and backup registers can be powered from the
V_BAT voltage when the main V_DD supply is powered off.

### 2.1 Digital supply

#### 2.1.1 Voltage regulator

The voltage regulator is always enabled after reset. It works in three different modes
depending on the application modes.
- in Run mode, the regulator supplies full power to the 1.2 V domain (core, memories
and digital peripherals)
- in Stop mode, the regulator supplies low power to the 1.2 V domain, preserving the
contents of the registers and SRAM
- in Standby mode, the regulator is powered down. The contents of the registers and
SRAM are lost except for those concerned with the Standby circuitry and the Backup
domain.

> Note: Depending on the selected package, there are specific pins that should be connected either to V_SS or V_DD to activate or deactivate the voltage regulator. Refer to section “Voltage
regulator “ in datasheet for details.

#### 2.1.2 Regulator OFF mode

Refer to section “Voltage regulator” in datasheet for details.
- When BYPASS_REG = V_DD, the core power supply should be provided through V_CAP1
and V_CAP2 pins connected together.
  - The two V ceramic capacitors should be replaced by two 100 nF decoupling
capacitors.
  - Since the internal voltage scaling is not managed internally, the external voltage
value must be aligned with the targeted maximum frequency.
  - When the internal regulator is OFF, there is no more internal monitoring on V12.
An external power supply supervisor should be used to monitor the V12 of the
logic power domain (V_CAP).

PA0 pin should be used for this purpose, and act as power-on reset on V12 power
domain.
- In regulator OFF mode, the following features are no more supported:
  - PA0 cannot be used as a GPIO pin since it allows to reset a part of the V12 logic
power domain which is not reset by the NRST pin.
  - As long as PA0 is kept low, the debug mode cannot be used under power-on
reset. As a consequence, PA0 and NRST pins must be managed separately if the
debug connection under reset or pre-reset is required.
  - The over-drive and under-drive modes are not available.
  - The Standby mode is not available.

*[Figure 1. BYPASS_REG supervisor reset connection]*

1. V_CAP2 is not available on all packages. In that case, a single 100 nF decoupling capacitor is connected to V_CAP1
The following conditions must be respected:
- V_DD should always be higher than V_CAP to avoid current injection between power
domains.
- If the time for V_CAP to reach V12 minimum value is smaller than the time for V_DD to
reach 1.7 V, then PA0 should be kept low to cover both conditions: until V_CAP reaches
V12 minimum value and until V_DD reaches 1.7 V.
- Otherwise, if the time for V_CAP to reach V12 minimum value is smaller than the time for
V_DD to reach 1.7 V, then PA0 could be asserted low externally.
- If V_CAP goes below V12 minimum value and V_DD is higher than 1.7 V, then PA0 must
be asserted low externally.

### 2.2 Power supply schemes

The circuit is powered by a stabilized power supply, V_DD.

> **Caution: The V_DD voltage range is 1.8 V to 3.6 V (down to 1.7 V with some restrictions, see relative**

Datasheet for details).
- The V_DD pins must be connected to V_DD with external decoupling capacitors: one
single Tantalum or Ceramic capacitor (min. 4.7 µF typ.10 µF) for the package + one
100 nF Ceramic capacitor for each V_DD pin.
- The V_BAT pin can be connected to the external battery (1.65 V < V_BAT < 3.6 V). If no
external battery is used, it is recommended to connect this pin to V_DD with a 100 nF
external ceramic decoupling capacitor.
- The V_DDA pin must be connected to two external decoupling capacitors (100 nF
Ceramic + 1 µF Tantalum or Ceramic).
- The V_REF+ pin can be connected to the V_DDA external power supply. If a separate,
external reference voltage is applied on V_REF+, a 100 nF and a 1 µF capacitors must
be connected on this pin. In all cases, V_REF+ must be kept between (V_DDA -1.2 V) and
V_DDA with minimum of 1.7 V.
- Additional precautions can be taken to filter analog noise:
  - V_DDA can be connected to V_DD through a ferrite bead.
  - The V_REF+ pin can be connected to V_DDA through a resistor.
- For the voltage regulator configuration, there is specific BYPASS_REG pin (not
available on all packages) that should be connected either to V_SS or V_DD to activate or
deactivate the voltage regulator specific.
  - Refer to Section 2.1.2 and section "Voltage regulator" of the related device
datasheet for details.
- When the voltage regulator is enabled, V_CAP1 and V_CAP2 pins must be connected to
2*2.2 µF LowESR < 2Ω Ceramic capacitor (or 1*4.7 µF LowESR < 1Ω Ceramic capacitor if only V_CAP1 pin is provided on some packages).

*[Figure 2. Power supply scheme (excluding STM32F469xx/F479xx)]*

1. Optional. If a separate, external reference voltage is connected on V_REF+, the two capacitors (100 nF and
1 µF) must be connected.
2. V_CAP2 is not available on all packages. In that case, a single 4.7 µF (ESR < 1Ω) is connected to V_CAP1.
V_CAP2, V_CAP1
3. V is either connected to V or to V (depending on package).
V_REF+ or V_DDA
4. V is either connected to V or to V (depending on package).
V_REF- or V_SSA
5. N is the number of V_DD and V_SS inputs.
6. Refer to datasheet for BYPASS_REG and PDR_ON pins connection.
7. V_DDUSB is only available on STM32F446xx.
8. Backup RAM is not available on STM32F410xx, STM32F411xx, STM32F412xx, STM32F413xx, and
STM32F423xx.

*[Figure 3. Power supply scheme for STM32F469xx/F479xx]*

1. Optional. If a separate, external reference voltage is connected on V_REF+, the two capacitors (100 nF and
1 µF) must be connected.
2. V is either connected to V or to V (depending on package).
V_REF+ or V_DDA
3. V is either connected to V or to V (depending on package).
V_REF- or V_SSA
4. Refer to datasheet for BYPASS_REG and PDR_ON pins connection.

### 2.3 Analog Supply

To improve conversion accuracy, the ADC has an independent power supply that can be
filtered separately, and shielded from noise on the PCB.
- The ADC voltage supply input is available on V_DDA pin.
- An isolated supply ground connection is provided on the V_SSA pin.
In all cases, the VSSA pin should be externally connected to same supply ground than VSS.
To ensure a better accuracy on low-voltage inputs, the user can connect a separate external
reference voltage ADC input on VREF+. The voltage on VREF+ may range from (V - 1.2
V) to V_DDA with a minimum of 1.7 V.
When available (depending on package), V_REF- must be externally tied to V_SSA.
V_REF- to V_SSA

## 3 Reset and power supply supervisor

### 3.1 System reset

A system reset sets all registers to their reset values except for the reset flags in the clock
controller CSR register and the registers in the Backup domain (see Figure 2).
A system reset is generated when one of the following events occurs:
1. A low level on the NRST pin (external reset)
2. window watchdog end-of-count condition (WWDG reset)
3. Independent watchdog end-of-count condition (IWDG reset)
4. A software reset (SW reset)
5. Low-power management reset
The reset source can be identified by checking the reset flags in the Control/Status register,
RCC_CSR.
The products listed in Table 1 do not require an external reset circuit to power-up correctly.
Only a pull-down capacitor is recommended to improve EMS performance by protecting the
device against parasitic resets, as exemplified in Figure 4.
Charging and discharging a pull-down capacitor through an internal resistor increases the
device power consumption. The capacitor recommended value (100 nF) can be reduced to
10 nF to limit this power consumption.

*[Figure 4. Reset circuit]*

#### 3.1.1 NRST circuitry example

This example applies to STM32F410xx, STM32F411xx, STM32F412xx, STM32F413xx,
to permanently disable internal reset circuitry.
Restrictions:
- PDR_ON = 0 is mostly intended for V_DD supply between 1.7 V and 1.9V (i.e. 1.8V +/-
5% supply).
Supply ranges which never go below 1.8V minimum should be better managed by

internal circuitry (no additional component needed, thanks to fully embedded reset
controller).
- When the internal reset is OFF, the following integrated features are no longer
supported:
  - The integrated power-on reset (POR) / power-down reset (PDR) circuitry is
disabled.
  - The brownout reset (BOR) circuitry must be disabled.
  - The embedded programmable voltage detector (PVD) is disabled.
  - VBAT functionality is no more available and V_BAT pin should be connected to V_DD.

*[Figure 5. NRST circuitry example (only for STM32F410xx, STM32F411xx,]*

Even with PDR_ON=0, during power up, the NRST is driven low by internal Reset controller
during T in order to allow stabilization of internal analog circuitry. Refer to
STM32F4xxxx datasheets for actual timing value.

*[Figure 6. NRST circuitry timings example (not to scale, only for STM32F410xx,]*

Selection of NRST voltage supervisor
Voltage supervisor should have the following characteristics
- Reset output active-low open-drain (output driving low when voltage is below trip
point).
  - Supervisor trip point including tolerances and hysteresis should fit the expected
V range.
Notice that supervisor spec usually specify trip point for falling supply, so
hysteresis should be added to check the power on phase.

### 3.2 Power supply supervisor

#### 3.2.1 PDR_ON circuitry example

> Note: This example doesn’t apply to STM32F410xx, STM32F411xx, STM32F412xx,

PDR_ON can be connected to VSS to permanently disable internal reset circuitry (external
voltage supervisor required on NRST pin). Thanks to backward compatibility, circuitry built
for other STM32F4xxxx products will work for STM32F410xx, STM32F411xx,
STM32F479xx.

> Note: Please contact your local STMicroelectronics representative or visit www.st.com in case you

want to use circuitry different from the one described hereafter.
Restrictions:
- PDR_ON = 0 is mostly intended for V_DD supply between 1.7 V and 1.9V (i.e. 1.8V +/-
5% supply).
Supply ranges which never go below 1.8V minimum should be better managed with
internal circuitry (no additional component thanks to fully embedded reset controller).
- To ensure safe power down, the external voltage supervisor (or equivalent) is required
to drive PDR_ON=1 during power off sequence.
When the internal reset is OFF, the following integrated features are no longer supported:
- The integrated power-on reset (POR) / power-down reset (PDR) circuitry is disabled.
- The brownout reset (BOR) circuitry must be disabled.
- The embedded programmable voltage detector (PVD) is disabled.
- V_BAT functionality is no more available and V_BAT pin should be connected to V_DD.

*[Figure 7. PDR_ON simple circuitry example (not needed for STM32F410xx,]*

*[Figure 8. PDR_ON timings example (not to scale, (not needed for STM32F410xx,]*

Selection of PDR_ON voltage supervisor
Voltage supervisor should have the following characteristics
- Reset output active-high push-pull (output driving high when voltage is below trip
point)
- Supervisor trip point including tolerances and hysteresis should fit the expected V
range.
Notice that supervisor spec usually specify trip point for falling supply, so hysteresis
should be added to check the power on phase.
Example:
  - Voltage regulator 1.8V +/- 5% mean V_DD min 1.71V
  - Supervisor specified at 1.66V +/- 2.5% with an hysteresis of 0.5% mean
- rising trip max = 1.71V (1.66V + 2.5% + 0.5%)
- falling trip min = 1.62V (1.66V - 2.5%).

#### 3.2.2 Power on reset (POR) / power down reset (PDR)

The device has an integrated POR/PDR circuitry that allows proper operation starting from 1.8 V.

The device remains in the Reset mode as long as V_DD is below a specified threshold,
V_POR/PDR, without the need for an external reset circuit. For more details concerning the

power on/power down reset threshold, refer to the electrical characteristics in the product
datasheets.

*[Figure 9. Power-on reset/power-down reset waveform]*

1. t_RSTTEMPO is approximately 2.6 ms. V_POR/PDR rising edge is 1.74 V (typ.) and V_POR/PDR falling edge is

1.70 V (typ.). Refer to STM32F4xxxx datasheets for actual value.

The internal power-on reset (POR) / power-down reset (PDR) circuitry is disabled through
the PDR_ON pin. An external power supply supervisor should monitor V_DD and should maintain the device in reset mode as long as V_DD is below a specified threshold. PDR_ON
should be connected to this external power supply supervisor. See Section 3.2.1 for details.

#### 3.2.3 Programmable voltage detector (PVD)

You can use the PVD to monitor the V_DD power supply by comparing it to a threshold
selected by the PLS[2:0] bits in the Power control register (PWR_CR).
The PVD is enabled by setting the PVDE bit.
A PVDO flag is available, in the Power control/status register (PWR_CSR), to indicate
whether V_DD is higher or lower than the PVD threshold. This event is internally connected to
EXTI Line16 and can generate an interrupt if enabled through the EXTI registers. The PVD
output interrupt can be generated when V_DD drops below the PVD threshold and/or when
V_DD rises above the PVD threshold depending on the EXTI Line16 rising/falling edge
configuration. As an example the service routine can perform emergency shutdown tasks.

*[Figure 10. PVD thresholds]*

## 4 Package

### 4.1 Package Selection

Package should be selected by taking into account the constrains that are strongly
dependent upon the application.
The list below summarizes the more frequent ones:
  - Amount of interfaces required.
Some interfaces might not be available on some packages.
Some interfaces combinations could not be possible on some packages.
  - PCB technology constrains.
Small pitch and high ball density could require more PCB layers and higher class
PCB
  - Package height
  - PCB available area
  - Noise emission or signal integrity of high speed interfaces.
Smaller packages usually provide better signal integrity. This is further enhanced
as Small pitch and high ball density requires multilayer PCBs which allow better
supply/ground distribution.
  - Compatibility with other devices.
Table 3 summarizes the available packages for all STM32F4xxxx family.

**Table 3. Package summary**

STM32F401xB/C
X X X X X
STM32F401xD/E
STM32F405xx/407xx X X X X X X
STM32F410xx X X X
STM32F411xx X X X X X
STM32F412xx X X X X X X X
STM32F413xx/423xx X X X X X X X
STM32F415xx/417xx X X X X X X
STM32F427xx/429xx X X X X X X X X

**Table 3. Package summary (continued)**

### 4.2 Pinout Compatibility

#### 4.2.1 I/O speed

- When using the GPIO as I/O, design considerations have to be taken into account to
ensure that the operation is as intended.
- When the load capacitance becomes larger, the rise/fall time of the I/O pin increases.
This capacitance includes the effects of the board traces.
- I/O characteristics are available in the product’s datasheet.
- Table 4 illustrates the I/O AC characteristics of the STM32F469xx:

**Table 4. I/O AC characteristics(1)(2)**

OSPEEDR
y[1:0] bit Symbol Parameter Conditions Min Typ Max Unit
value(1)
C_L = 50 pF, V ≥ 2.7 V - - 4
C_L = 50 pF, V ≥ 1.7 V - - 2
f Maximum frequency C_L = 10 pF, V ≥ 2.7 V - - 8 MHz
max(IO)out L DD
00 C L = 10 pF, V DD ≥ 1.8 V - - 4
C_L = 10 pF, V ≥ 1.7 V - - 3
Output high to low level fall
t / C_L = 50 pF, V = 1.7 V
f(IO)out time and output low to high L DD - - 100 ns
t to 3.6 V
r(IO)out level rise time
C_L = 50 pF, V ≥ 2.7 V - - 25
C_L = 50 pF, V ≥ 1.8 V - - 12.5
C_L = 50 pF, V ≥ 1.7 V - - 10
f Maximum frequency(3) L DD MHz
max(IO)out
C_L = 10 pF, V ≥ 2.7 V - - 50
C_L = 10 pF, V ≥ 1.8 V - - 20
C_L = 10 pF, V ≥ 1.7 V - - 12.5
C_L = 50 pF, V ≥ 2.7 V - - 10
t f(IO)out / O tim u e tp a u n t d h ig o h u t t p o u l t o l w ow le t v o e h l i f g a h ll C L = 10 pF, V DD ≥ 2.7 V - - 6 ns
t r(IO)out level rise time C L = 50 pF, V DD ≥ 1.7 V - - 20
C_L = 10 pF, V ≥ 1.7 V - - 10

**Table 4. I/O AC characteristics(1)(2) (continued)**

OSPEEDR
y[1:0] bit Symbol Parameter Conditions Min Typ Max Unit
value(1)
C_L = 40 pF, V ≥ 2.7 V - - 50(3)
C_L = 10 pF, V ≥ 2.7 V - - 100(3)
f Maximum frequency(3) C_L = 40 pF, V ≥ 1.7 V - - 25 MHz
max(IO)out L DD
C_L = 10 pF, V ≥ 1.8 V - - 50
10 C_L = 10 pF, V ≥ 1.7 V - - 42.5
C_L = 40 pF, V ≥2.7 V - - 6
t f(IO)out / O tim u e tp a u n t d h ig o h u t t p o u l t o l w ow le t v o e h l i f g a h ll C L = 10 pF, V DD ≥ 2.7 V - - 4 ns
t r(IO)out level rise time C L = 40 pF, V DD ≥ 1.7 V - - 10
C_L = 10 pF, V ≥ 1.7 V - - 6
C_L = 30 pF, V ≥ 2.7 V - - 100(3)
C_L = 30 pF, V ≥ 1.8 V - - 50
C_L = 30 pF, V ≥ 1.7 V - - 42.5
f Maximum frequency(3) L DD MHz
max(IO)out C_L = 10 pF, V ≥ 2.7 V - - 180(3)
C_L = 10 pF, V ≥ 1.8 V - - 100
C_L = 10 pF, V ≥ 1.7 V - - 72.5
11
C_L = 30 pF, V ≥ 2.7 V - - 4
C_L = 30 pF, V ≥1.8 V - - 6
t f(IO)out / O tim u e tp a u n t d h ig o h u t t p o u l t o l w ow le t v o e h l i f g a h ll C L = 30 pF, V DD ≥1.7 V - - 7 ns
t r(IO)out level rise time C L = 10 pF, V DD ≥ 2.7 V - - 2.5
C_L = 10 pF, V ≥1.8 V - - 3.5
C_L = 10 pF, V ≥1.7 V - - 4
Pulse width of external
- t signals detected by the EXTI - 10 - - ns
EXTIpw
controller
1. Guaranteed by design.
2. The I/O speed is configured using the OSPEEDRy[1:0] bits. Refer to the STM32F4xx reference manual for a description of
the GPIOx_SPEEDR GPIO port output speed register.
3. To minimize impact of process variations, IO compensation cell can be activated to reduce the overshoot during rise/fall
transitions, for maximum frequencies above 50 MHz and V > 2.4 V.

### 4.3 Alternate Function

Each pin of the MCU can be configured to multiple functions. These functions are selected by software.
The full description of I/O alternate functions is described in the datasheet of the selected device and the register, which allow the
pin configuration, are described in the reference manual.

**Table 5. Alternate function**

AF0 AF1 AF2 AF3 AF4 AF5 AF6 AF7 AF8 AF9 AF10 AF11 AF12 AF13 AF14 AF15
USA CAN1/2 QUADS FMC/
Port SPI2/3/ DCMI/
TIM3/4 TIM8/9 I2C1/2/ SPI1/2/ SPI2/3/ RT6/ /TIM12/ PI/OTG SDIO/
SYS TIM1/2 USAR ETH DSI LCD SYS
/5 /10/11 3 3/4/5/6 SAI1 UAR 13/14/ 2_HS/O OTG2
T1/2/3 HOST
T4/5/ QUAD TG1_F _
TIM1_ TIM3_ TIM8_ OTG_HS_ ETH_MII_ LCD_ EVENT
CH2N CH3 CH2N ULPI_D1 RXD2 G1 OUT
ETH_MII_
DSI
TIM2_ I2C2_ USART3 OTG_HS TX_EN/ LCD_ EVENT
CH4 SDA _RX _ULPI_D4 ETH_RMII_ G5 OUT
_TE
TX_EN
ETH_MII_
SPI2_
TIM1_ I2C2_SM USART3 OTG_HS_ TXD0/ OTG_ EVENT
PB12 - - - NSS/ - - CAN2_RX - -
BKIN BA _CK ULPI_D5 ETH_RMII_ HS_ID OUT I2S2_WS
Port B TXD0
SPI2_ ETH_MII_
TIM1_ USART3 OTG_HS_ EVENT
PB13 - - - - SCK/ - - CAN2_TX TXD1/ETH_ - - -
CH1N _CTS ULPI_D6 OUT
I2S2_CK RMII_TXD1
TIM1_ TIM8_ SPI2_MIS I2S2ext_ USART3 TIM12_C OTG_ EVENT
CH2N CH2N O SD _RTS H1 HS_DM OUT
SPI2_
RTC_ TIM1_ TIM8_ TIM12_C OTG_H EVENT
REFIN CH3N CH3N H2 S_DP ‘OUT
I2S2_SD
In order to easily explore Peripheral Alternate Functions mapping to pins, it is recommended to use the STM32CubeMX tool
available on www.st.com.

*[Figure 11. STM32CubeMX example screen-shot]*

#### 4.3.1 Handling unused pins

All microcontrollers are designed for a variety of applications and often a particular
application does not use 100% of the MCU resources.
To increase EMC performance, unused clocks, counters or I/Os, should not be left free, e.g.
I/Os should be set to “0” or “1”(pull-up or pull-down to the unused I/O pins.) and unused
features should be “frozen” or disabled.

> Note: To reduce leakage it is advisable to configure the I/O as an analog input or to push-pull and

to set it to “0”.

### 4.4 Boot mode selection

#### 4.4.1 Boot mode selection

In the STM32F4xxxx, three different boot modes can be selected by means of the
BOOT[1:0] pins as shown in Table 6.

**Table 6. Boot modes**

BOOT mode selection pins
Boot mode Aliasing
BOOT1 BOOT0
x 0 Main Flash memory Main Flash memory is selected as boot space
0 1 System memory System memory is selected as boot space
1 1 Embedded SRAM Embedded SRAM is selected as boot space
The values on the BOOT pins are latched on the 4th rising edge of SYSCLK after a reset. It
is up to the user to set the BOOT1 and BOOT0 pins after reset to select the required boot
mode.
Boot from User Flash mode
The application code that runs after reset is located in user flash memory.
The user flash memory in this mode is aliased to start at address 0x00000000 in boot
memory space. Upon reset, the top-of-stack value is fetched from address 0x00000000,
and code then begins execution at address 0x00000004.
Boot from System Memory mode
The system memory (not the user flash) is now aliased to start at address 0x00000000. The
application code in this case must have already been loaded into system memory.
Boot from Embedded SRAM mode
The SRAM start at address 0x00000000. When this mode is selected, the device expects
the vector table to have been relocated using the NVIC exception table and offset register,
and execution begins at the start of embedded SRAM. The application code in this case
must have already been loaded into embedded SRAM.
This last mode is usually used for Debugging.

### 4.5 Boot pin connection

Figure 12 shows the external connection required to select the boot memory of the
STM32F4xxxx.

*[Figure 12. Boot mode selection implementation example]*

1. Resistor values are given only as a typical example.

### 4.6 Embedded boot loader mode

The embedded boot loader is located in the System memory and is programmed by ST
during production.
It is used to reprogram the Flash memory using one of the following serial interfaces.
The following table shows the supported communication peripherals by the system
bootloader.

**Table 7. STM32F4xxxx bootloader communication peripherals**

STM32F405/415
STM32F412xx/
Bootloader STM32F401xB/C STM32F407/417 STM32F411xC/ STM32F469xx/
STM32F410xx STM32F413xx/
peripherals STM32F401xD/E STM32F427/437 STM32F411xE STM32F479xx
STM32F423xx
STM32F429/439
USB OTG FS USB OTG FS USB OTG FS USB OTG FS USB OTG FS
DFU (PA11/12) (PA11/12) - (PA11/12) (PA11/12) (PA11/12)
in Device mode in Device mode in Device mode in Device mode in Device mode
USART1 PA9/PA10 PA9/PA10 PA9/PA10 PA9/PA10 PA9/PA10 PA9/PA10
USART2 PD5/PD6 - - PD5/PD6 PD5/PD6 -
PB10/PB11/ PB10/PB11,
USART3 - - - PB10/PB11
PC10/PC11 PC10/PC11
CAN - PB5/PB13 - - PB5/PB13 PB5/PB13
I2C1 PB6/PB7 - PB6/PB7 PB6/PB7 PB6/PB7 -
I2C2 PB3/PB10 - PB3/PB10 PB3/PB10 PF0/PF1 -
I2C3 PA8/PB4 - - PA8/PB4 PA8/PB4 -
I2C FMP1 - - - - PB14/PB15 -
PA4/PA5/ PA4/PA5/ PA4/PA5/ PA4/PA5/
SPI1 - -
PA6/PA7 PA6/PA7 PA6/PA7 PA6/PA7
PB12/PB13/ PB12/PB13/ PB12/PB13/
SPI2 - - -
PB14/PB15 PB14/PB15 PB14/PB15

**Table 7. STM32F4xxxx bootloader communication peripherals (continued)**

STM32F405/415
STM32F412xx/
Bootloader STM32F401xB/C STM32F407/417 STM32F411xC/ STM32F469xx/
STM32F410xx STM32F413xx/
peripherals STM32F401xD/E STM32F427/437 STM32F411xE STM32F479xx
STM32F423xx
STM32F429/439
PA15/PC10/ PA15/PC10/ PA15/PC10/
SPI3 - - -
PC11/PC12 PC11/PC12 PC11/PC12
PE11/PE12/
SPI4 - - - - -
PE13/PE14
For additional information, refer to AN2606 (Table 2).

## 5 Debug management

The Host/Target interface is the hardware equipment that connects the host to the
application board. This interface is made of three components: a hardware debug tool, a
JTAG or SW connector and a cable connecting the host to the debug tool.
Figure 13 shows the connection of the host to the evaluation board.

*[Figure 13. Host-to-board connection]*

### 5.1 SWJ debug port (serial wire and JTAG)

The STM32F4xxxx core integrates the serial wire / JTAG debug port (SWJ-DP). It is an
Arm® standard CoreSight™ debug port that combines a JTAG-DP (5-pin) interface and a
SW-DP (2-pin) interface.
- The JTAG debug port (JTAG-DP) provides a 5-pin standard JTAG interface to the AHP-
AP port
- The serial wire debug port (SW-DP) provides a 2-pin (clock + data) interface to the
AHP-AP port
In the SWJ-DP, the two JTAG pins of the SW-DP are multiplexed with some of the five JTAG
pins of the JTAG-DP.
For more details on the SWJ debug port refer to the reference manual of the product, SWJ
debug port section (serial wire and JTAG).

### 5.2 Pinout and debug port pins

The STM32F4xxxx MCU is offered in various packages with different numbers of available
pins. As a result, some functionality related to the pin availability may differ from one
package to another.

#### 5.2.1 SWJ debug port pins

Five pins are used as outputs for the SWJ-DP as alternate functions of general-purpose
I/Os (GPIOs). These pins, shown in Table 8, are available on all packages.

**Table 8. Debug port pin assignment**

JTAG debug port SW debug port Pin
SWJ-DP pin name assignmen
Type Description Type Debug assignment t
JTAG test mode Serial wire data
JTMS/SWDIO I I/O PA13
selection input/output
JTCK/SWCLK I JTAG test clock I Serial wire clock PA14
JTDI I JTAG test data input - - PA15
TRACESWO if async
JTDO/TRACESWO O JTAG test data output - PB3
trace is enabled
JNTRST I JTAG test nReset - - PB4

#### 5.2.2 Internal pull-up and pull-down resistors on JTAG pins

The JTAG input pins must not be floating since they are directly connected to flip-flops to
control the debug mode features. Special care must be taken with the SWCLK/TCK pin that
is directly connected to the clock of some of these flip-flops.
To avoid any uncontrolled I/O levels, the STM32F4xxxx embeds internal pull-up and pull-
down resistors on JTAG input pins:
- JNTRST: Internal pull-up
- JTDI: Internal pull-up
- JTMS/SWDIO: Internal pull-up
- TCK/SWCLK: Internal pull-down
Once a JTAG I/O is released by the user software, the GPIO controller takes control again.
The reset states of the GPIO control registers put the I/Os in the equivalent state:
- JNTRST: Input pull-up
- JTDI: Input pull-up
- JTMS/SWDIO: Input pull-up
- JTCK/SWCLK: Input pull-down
- JTDO: Input floating
The software can then use these I/Os as standard GPIOs.

> Note: The JTAG IEEE standard recommends to add pull-up resistors on TDI, TMS and nTRST but

there is no special recommendation for TCK. However, for the STM32F4xxxx, an integrated
pull-down resistor is used for JTCK.
Having embedded pull-up and pull-down resistors removes the need to add external
resistors.

#### 5.2.3 SWJ debug port connection with standard JTAG connector

Figure 14 shows the connection between the STM32F4xxxx and a standard JTAG
connector.

*[Figure 14. JTAG connector implementation]*

## 6 Clocks

Three different clock sources can be used to drive the system clock (SYSCLK):
- HSI oscillator clock (high-speed internal clock signal)
- HSE oscillator clock (high-speed external clock signal)
- PLL clock
The devices have two secondary clock sources:
- 32 kHz low-speed internal RC (LSI RC) that drives the independent watchdog and,
optionally, the RTC used for Auto-wakeup from the Stop/Standby modes.
- 32.768 kHz low-speed external crystal (LSE crystal) that optionally drives the real-time
clock (RTCCLK)
Each clock source can be switched on or off independently when it is not used, to optimize
the power consumption.
Refer to the reference manual for the description of the clock tree.

### 6.1 HSE OSC clock

The high-speed external clock signal (HSE) can be generated from two possible clock
sources:
- HSE user external clock (see Figure 15)
- HSE external crystal/ceramic resonator (see Figure 16)

*[Figure 15. HSE external clock Figure 16. HSE crystal/ceramic]*

resonators
1. The value of R_EXT depends on the crystal characteristics. Typical value is in the range of 5 to 6 R
(resonator series resistance).
Refer to the dedicated Application Note (AN2867 - Oscillator design guide for ST
microcontrollers) and electrical characteristics sections in the datasheet of your product for
more details.

### 6.2 LSE OSC clock

The low-speed external clock signal (LSE) can be generated from two possible clock
sources:
- LSE user external clock (see Figure 17)
- LSE external crystal/ceramic resonator (see Figure 18)

*[Figure 17. LSE external clock Figure 18. LSE crystal/ceramic]*

resonators
1. “LSE crystal/ceramic resonators” figure:
To avoid exceeding the maximum value of C_L1 and C_L2 (15 pF) it is strongly recommended to use a
resonator with a load capacitance C_L ≤ 7 pF. Never use a resonator with a load capacitance of 12.5 pF.
2. “LSE external clock” and “LSE crystal/ceramic resonators” figures:
OSC32_IN and OSC32_OUT pins can be used also as GPIO, but it is recommended not to use them as
both RTC and GPIO pins in the same application.
3. “LSE crystal/ceramic resonators” figure:
The value of R_EXT depends on the crystal characteristics. A 0 Ω resistor would work but would not be
optimal. To fine tune R_EXT value, refer to AN2867 - Oscillator design guide for ST microcontrollers (Table 2)
and electrical characteristics sections in the datasheet of your product for more details.

## 7 Reference design

*[Figure 19. Reference schematic]*

’L
X;S; ’R B S,,T>=U S’MEX

*[Figure 20. Bill of Material]*

Comment Description Designator Footprint Quantity
TD-0341 [RESET/Black] SE PUSHBUTTON B1 PB10 1
CR1220 holder Battery BT1 BAT_2SM_CR1220 1
C1, C2, C3, C4, C5, C6, C7,
C8, C9, C13, C14, C15, C16,
C17, C18, C19, C20, C21,
100nF Capacitor C22, C23, C25, C30 0402C 22
4.7uF Polarized Capacitor (Radial) C10, C11 TAN-A 2
1uF Polarized Capacitor (Radial) C12, C24 TAN-A 2
2.2uF Capacitor C26, C27 1206C 2
2.2uF[N/A] Capacitor C28 1206C 1
2.2uF Capacitor C29 0402C 1
100nF Capacitor C31 0603C 1
20pF Capacitor C32, C33 0603C 2
1.5pF Capacitor C34, C35 0603C 2
JTAG CN1 IDC20S 1
JP10 SIP3 1
BEAD(FCM1608KF-601T03) Inductor L1 0603L 1
10K Resistor R1, R2, R3, R4, R8, R9, R12 0603R 7

0 Resistor R5, R6, R7, R11 0603R 4

[N/A] Resistor R10 0603R 1
SPDT Subminiature Toggle
Switch, Right Angle
Mounting, Vertical

09.03290.01 Actuation SW1, SW2 SW1_3TH_2R54_10X2R5 2

STM32F469 U1 BGA216_0R8_13X13_SKT 1
25MHz(with socket) Crystal X1 XTAL_socket 1
NX3215SA-32.768KHZ-EXS00ACrystal X2 XTAL_2SM_3R2X1R5 1

### 8.1 PCB stack-up

In order to reduce the reflections on high speed signals, it is necessary to match the
impedance between the source, sink and transmission lines. The impedance of a signal
trace depends on its geometry and its position with respect to any reference planes.
The trace width and spacing between differential pairs for a specific impedance requirement
is dependent on the chosen PCB stack-up. As there are limitations in the minimum trace
width and spacing which depend on the type of PCB technology and cost requirements, a
PCB stack-up needs to be chosen which allows all the required impedances to be realized.
The minimum configuration that can be used is 4 or 6 layers stack-up. An 8 layers boards
may be required for a very dense PCBs that have multiple SDRAM/SRAM/NOR/LCD
components.
The following stack-ups are intended as examples which can be used as a starting point for
helping in a stack-up evaluation and selection. These stack-up configurations are using a
GND plane adjacent to the power plane to increase the capacitance and reduce the gap
between GND and power plane. So high speed signals on top layer will have a solid GND
reference plane which helps to reduce EMC emissions, as going up in number of layers and
having a GND reference for each PCB signal layer will improve further the radiated EMC
performance.

*[Figure 21. Four layer PCB stack-up example]*

*[Figure 22. Six layer PCB stack-up example]*

### 8.2 Crystal oscillator

Use the application note: Oscillator design guide for STM8S, STM8A and STM32
microcontrollers (AN2867), for further guidance on how to layout and route crystal oscillator
circuits.

### 8.3 Power supply decoupling

All power supply and ground pins must be properly connected to the power supplies. These
connections, including pads, tracks and vias should have as low impedance as possible.
This is typically achieved with thick track widths and, preferably, the use of dedicated power
supply planes in multilayer PCBs.
In addition, each power supply pair should be decoupled with filtering Ceramic capacitors
(100 nF) and one single Tantalum or Ceramic capacitor (min. 4.7 µF typ.10 µF) connected in
parallel. These capacitors need to be placed as close as possible to, or below, the
appropriate pins on the underside of the PCB. Typical values are 10 nF to 100 nF, but exact
values depend on the application needs. Figure 22 shows the typical layout of such a
VDD/VSS pair.

*[Figure 23. Typical layout for V /V pair]*

### 8.4 High speed signal layout

#### 8.4.1 SDMMC bus interface

Interface connectivity
The SD/SDIO MMC card host interface (SDMMC) provides an interface between the APB2
peripheral bus and Multi Media Cards (MMCs), SD memory cards and SDIO cards. The
SDMMC interface is a serial data bus interface, that consists of a clock (CK), command
signal (CMD) and 8 data lines (D [0:7]).
Interface signal layout guidelines:
- Reference the plane using GND or PWR (if PWR, add 10nf switching cap between
PWR and GND)
- Trace the impedance: 50Ω ± 10%
- The skew being introduced into the clock system by unequal trace lengths and loads,
minimize the board skew, keep the trace lengths equal between the data and clock.
- The maximum skew between data and clock should be below 250 ps @ 10mm
- The maximum trace length should be below 120mm. If the signal trace exceeds this
trace-length/speed criterion, then a termination should be used
- The trace capacitance should not exceed 20 pF at 3.3V and 15pF at 1.8V
- The maximum signal trace inductance should be less than 16nH
- Use the recommended pull-up resistance for CMD and data signals to prevent bus
floating.
- The mismatch within data bus, data and CK or CK and CMD should be below 10mm.
- Keep the same number of vias between the data signals

> Note: The total capacitance of the SD memory card bus is the sum of the bus master capacitance.

CHOST, the bus capacitance CBUS itself and the capacitance CCARD of each card
connected to this line. The total bus capacitance is CL= CHost + CBus + N*CCard where
Host is STM32F4xxxx, bus is all the signals and Card is SD card.

#### 8.4.2 Flexible memory controller (FMC) interface

Interface connectivity
The FMC controller and in particular SDRAM memory controller which has many signals,
most of them have a similar functionality and work together. The controller I/O signals could
be split in four groups as follow:
- An address group which consists of row/column address and bank address.
- A command group which includes the row address strobe (NRAS), the column address
strobe (NCAS), and the write enable (SDWE).
- A control group which includes a chip select bank1 and bank2 (SDNE0/1), a clock
enable bank1 and bank2 (SDCKE0/1), and an output byte mask for the write access
(DQM).
- A data group/lane which contains 8 signals (a): the eight D (D7–D0) and the data mask
(DQM).

> Note: It depends of the used memory: SDRAM with x8 bus widths have only one data group, while

x16 and x32 bus-width SDRAM have two and four lanes, respectively.
Interface signal layout guidelines:
- Reference the plane using GND or PWR (if PWR, add 10nf stitching cap between PWR
and GND
- Trace the impedance: 50Ω ± 10%
- The maximum trace length should be below 120mm. If the signal trace exceeds this
trace-length/speed criterion, then a termination should be used.
- Reduce the crosstalk, place data tracks on the different layers from the address and
control lanes, if possible. Ho wever, when the data and address/control tracks coexist
on the same layer they must be isolated from each other by at least 5 mm.
- Match the trace lengths for the data group within ± 10 mm of each other to diminish the
skew. Serpentine traces (back and forth traces in an “S” pattern to increase trace
length) can be used to match the lengths.
- Placing the clock (SDCLK) signal on an internal layer, minimizes the noise (EMI).
- Route the clock signal at least 3x of the trace away from others signals. Use as less
vias as possible to avoid impedance change and reflection. Avoid using serpentine
routing.
- Match the clock traces to the data /address group traces within ±10mm.
- Match the clock traces to each signal trace in the address and command groups to
within ±10mm (with maximum of <= 20mm).
- Trace the capacitances:
  - At 3.3 V keep the trace within 20 pF with overall capacitive loading (including Data,
Address, SDCLK and Control) no more than 30pF.
  - At 1.8 V keep the trace within 15 pF with overall capacitive loading (including Data,
Address, SDCLK and Control) no more than 20pF.

#### 8.4.3 Quadrature serial parallel interface (Quad SPI)

Interface connectivity
The QUADSPI is a specialized communication interface targeting single, dual or Quad SPI

FLASH memories. The QUAD SPI interface is a serial data bus interface, that consists of a
clock (SCLK), a chip select signal (nCS) and 4 data lines (IO[0:3]).
Interface signal layout guidelines
- Reference the plane using GND or PWR (if PWR, add 10nf stitching cap between PWR
and GND
- Trace the impedance: 50Ω ± 10%
- The maximum trace length should be below 120mm. If the signal trace exceeds this
trace-length/speed criterion, then a termination should be used
- Avoid using multiple signal layers for the data signal routing.
- Route the clock signal at least 3x of the trace away from other signals. Use as less vias
as possible to avoid the impedance change and reflection. Avoid using a serpentine
routing.
- Match the trace lengths for the data group within ± 10 mm of each other to diminish
skew. Serpentine traces (back and forth traces in an “S” pattern to increase trace
length) can be used to match the lengths.
Avoid using a serpentine routing for the clock signal and as less via(s) as possible for the
whole path. a via alter the impedance and add a reflection to the signal.

#### 8.4.4 Embedded trace macrocell (ETM)

Interface connectivity
The ETM enables the reconstruction of the program execution. The data are traced using
the data watchpoint and trace (DWT) component or the instruction trace macrocell (ITM)
whereas instructions are traced using the embedded trace macrocell (ETM). The ETM
interface is synchronous with the data bus of 4 lines D [0:3] and the clock signal CLK.
Interface signals layout guidelines
- Reference the plane using GND or PWR (if PWR, add 10nf stitching cap between PWR
and GND
- Trace the impedance: 50Ω ± 10%
- All the data trace should be as short as possible (<=25 mm),
- Trace the lines which should run on the same layer with a solid ground plane
underneath it without a via.
- Trace the clock which should have only point-to-point connection. Any stubs should be
avoided.
- It is strongly recommended also for other (data) lines to be point-to-point only. If any
stubs are needed, they should be as short as possible. If longer are required, there
should be a possibility to optionally disconnect them (e .g. by jumpers).

### 8.5 Package layout recommendation

#### 8.5.1 BGA 216 0.8 mm pitch design example

**Table 9. BGA 216 0.8 mm pitch package information**

Package information (mm) Design parameters (mm)
Ball pitch : 0.8 Via size : hole size ∅= 0.2, pad size: 0.45, plane clearance: 0.65
Ball size : 0.4 Trace width : 0.10/0.125
Number of rows/columns : 15x15 Trace/trace space : 0.10/0.125
Package solder Pad: SMD BGA land size (Ball pad): ∅= 0.4, solder mask: 0.5
With 0.8 mm pitch BGA balls, fan-out vias are needed to route the balls to other layers on
the PCB. Through-vias are used in this example, which cost less than blind, buried vias. For
four adjacent BGA land pads, it is possible to have only one via as showing in Figure 24 and

*[Figure 25. The traces are routed of two first row and two first colon without fan-out via. The]*

current pitch size allows to route only one trace between two adjacent BGA land pads.
Figure 26 shows an example of ideal SDRAM signals fan-out vias with power and gnd
signals. These signals can be optimized to achieve the routing and length matching in an
another layer before connecting to an SDRAM IC.

*[Figure 24. BGA 0.8mm pitch example of fan-out]*

*[Figure 25. Via fan-out]*

*[Figure 26. FMC signal fan-out routing example]*

#### 8.5.2 WLCSP143 0.4 mm pitch design example

**Table 10. Wafer level chip scale package information**

Package information (mm) Design parameters (mm)
Bump pitch : 0.4 Microvia size : hole size ∅= 0.1, via land: 0.2
Bump size : 0.25 Trace width/space : 0.07/0.05 or 0.07/0.07
Number of rows/columns : 13x11 Bump pad size ∅= 0.26 max – 0.22 recommended
Non-solder mask defined via underbump Solder mask opening bump ∅=0.3 min (for 0.26
allowed diameter pad)

A better way to route this package and the fan-out signals is to use a through microvia
technology. Microvia will route out internal bumps to a buried layers inside the PCB. To
achieve this, the WLCSP package pads have to be connected to this internal layer through
microvia. In case of four layers PCB, the first layer is WLCSP component, the second layer
will be used as a signal layer, the third layer as the power and ground and the bottom layer
for a signal layout. Figure 27 shows an example of the layout for four layers PCB.

*[Figure 27. 143-bumps WLCSP, 0.40 mm pitch routing example]*

## 9 FAQ

### 9.1 Identify the STM32F4xxxx

In order to identify the STM32F4 refer to section “Part numbering” in your product
datasheet.
To get the MCU’s ID you can use ST-LINK Utility, once connected, the tool identify the
target, and shows the ID, sub family, revision and flash size of the device as shown below.

*[Figure 28. STM32 ST-LINK Utility]*

### 9.2 Hardware tools available

ST provides three different development platforms:

#### 9.2.1 Nucleao Boards

These boards have a wide extension capabilities with specialized shields like Arduino™
Uno.
Nucleao boards can easily be expanded through a variety of add-on boards.

#### 9.2.2 Discovery kits

Discovery boards helps user to discover the high performance microcontrollers of the
STM32 F4 series and to develop applications easily.
Different discovery boards are available. For example the STM32F429I-DISCO includes
these features:
- SDRAM 64Mbits
- L3GD20, MEMS motion sensor, 3 axis digital output gyroscope
- USB OTG with micro AB connector…

#### 9.2.3 Evaluation boards

Evaluation boards are a complete demonstration and development platform for the STM32
F4 series.
The full range of hardware features on the board is provided to help you evaluate all
peripherals (USB OTG HS, USB OTG FS, Ethernet, motor control, CAN, MicroSD card,
smartcard, USART, Audio DAC, RS-232, IrDA, SRAM, MEMS, EEPROM… etc.) and
develop your own applications.

#### 9.2.4 Where to find IBIS models?

IBIS models describe the electrical characteristics of the digital inputs and outputs of the
STM32F4xxxx through I=f (V) and V=f (T) data.
For further information on IBIS models refer to AN4803 (High-speed SI simulations using
IBIS and board-level simulations using HyperLynx SI on STM32 32-bit Arm® Cortex®
MCUs)
IBIS models are available on ST’s website.

### 9.3 MCU does not work properly

The table below summarizes some possible root causes that prevents the MCU from
starting correctly. It presents also the most common suspects related to the possible root
cause that you may need to verify.

**Table 11. MCU does not work properly**

Possible root cause What you need to verify
- Power delivered to the device must be stable.
VDD and GND feeding the • Monitor power supplies.
device • Check if GND is properly supplied to device.
- Verify the GND coupling.
- Monitor OSC_OUT with oscillator to verify if it is working
properly.
OSC_OUT
- Refer to the AN2867: Oscillator design guide for ST
microcontrollers.
- Check if RESET pin is correctly driven.
RESET pin
- NRST connection includes a 100nF capacitor to ground.
- Monitor boot pins.
BOOT PINs • MCU may not work properly if BOOT0 and BOOT1 are
floating.
- VCAP1 and VCAP2 should be connected to 2x2.2 µF
LowESR < 2 Ω Ceramic capacitor
VCAPs
(or one 4.7 µF LowESR < 1 Ω Ceramic capacitor if only
VCAP1 pin is provided on some packages).
- When programming the MCU, verify PLS [2:0] option bits.
(you can use ST Link utility for that)
PVD
- An interruption is generated depending of the programmed
PVD threshold.
- Respect worst conditions of temperature guaranteed by ST
Temperature range
in the Datasheet.
- Care must be taken when PDR_ON pin =1, in such
configuration the PDR block is active, that means if VDD
System RESET
drops down to 1.74 Volts (Refer to STM32F4xxxx
datasheets for actual value) a system reset will occur.

## 10 Conclusion

This application note should be used as a starting reference for a new design with
STM32F4xxxx device.