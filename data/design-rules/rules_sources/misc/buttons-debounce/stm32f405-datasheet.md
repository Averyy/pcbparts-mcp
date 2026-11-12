Source: https://www.st.com/resource/en/datasheet/stm32f405rg.pdf
Retrieved: 2026-11-09

[PDF: 206 pages.]

# **STM32F405xx STM32F407xx**

#### Arm [®] Cortex [®] -M4 32b MCU+FPU, 210DMIPS, up to 1MB flash/192+4KB RAM, USB OTG HS/FS, Ethernet, 17 TIMs, 3 ADCs, 15 comm. interfaces, and camera

**Datasheet**                                      - **production data**

#### **Features**


- **Includes ST state-of-the-art patented**
**technology**


- Core: Arm [®] 32-bit Cortex [®] -M4 CPU with FPU,
Adaptive real-time accelerator (ART
Accelerator) allowing 0-wait state execution
from flash memory, frequency up to 168 MHz,
memory protection unit, 210 DMIPS/
1.25 DMIPS/MHz (Dhrystone 2.1), and DSP
instructions

- Memories

  - Up to 1 Mbyte of flash memory

  - Up to 192+4 Kbytes of SRAM including 64Kbyte of CCM (core coupled memory) data
RAM

  - 512 bytes of OTP memory

  - Flexible static memory controller
supporting CompactFlash™, SRAM,
PSRAM, NOR and NAND memories

- LCD parallel interface, 8080/6800 modes

- Clock, reset, and supply management

  - 1.8 V to 3.6 V application supply and I/Os

  - POR, PDR, PVD and BOR

  - 4-to-26 MHz crystal oscillator

  - Internal 16 MHz factory-trimmed RC (1%
accuracy)

  - 32 kHz oscillator for RTC with calibration

  - Internal 32 kHz RC with calibration

- Low-power operation

  - Sleep, Stop, and Standby modes

  - VBAT supply for RTC, 20×32-bit backup
registers + optional 4 KB backup SRAM

- 3×12-bit, 2.4 MSPS A/D converters: up to 24
channels and 7.2 MSPS in triple interleaved
mode

- 2×12-bit D/A converters

- General-purpose DMA: 16-stream DMA
controller with FIFOs and burst support


WLCSP90
(4.223x3.969 mm)


LQFP64 (10 × 10 mm)
LQFP100 (14 × 14 mm)
LQFP144 (20 × 20 mm)

LQFP176 (24 × 24 mm)


UFBGA176
(10 × 10 mm)


- Up to 17 timers: up to twelve 16-bit and two 32bit timers up to 168 MHz, each with up to 4
IC/OC/PWM or pulse counter and quadrature
(incremental) encoder input

- Debug mode

  - Serial wire debug (SWD) & JTAG
interfaces

  - Cortex-M4 Embedded Trace Macrocell™

- Up to 140 I/O ports with interrupt capability

  - Up to 136 fast I/Os up to 84 MHz

  - Up to 138 5 V-tolerant I/Os

- Up to 15 communication interfaces

  - Up to 3 × I [2] C interfaces (SMBus/PMBus)

  - Up to 4 USARTs/2 UARTs (10.5 Mbit/s, ISO
7816 interface, LIN, IrDA, modem control)

  - Up to 3 SPIs (42 Mbits/s), 2 with muxed
full-duplex I [2] S to achieve audio class
accuracy via internal audio PLL or external
clock

  - 2 × CAN interfaces (2.0B Active)

  - SDIO interface

- Advanced connectivity

  - USB 2.0 full-speed device/host/OTG
controller with on-chip PHY

  - USB 2.0 high-speed/full-speed
device/host/OTG controller with dedicated
DMA, on-chip full-speed PHY and ULPI

  - 10/100 Ethernet MAC with dedicated DMA:
supports IEEE 1588v2 hardware, MII/RMII


March 2026 DS8626 Rev 12 1/206


This is information on a product in full production.


_[www.st.com](http://www.st.com)_


- 8- to 14-bit parallel camera interface up to
54 Mbytes/s

- True random number generator

- CRC calculation unit


**STM32F405xx, STM32F407xx**


- 96-bit unique ID

- RTC: subsecond accuracy, hardware calendar

- All packages are ECOPACK2 compliant


**Table 1. Device summary**


**Reference** **Part number**


STM32F405xx STM32F405RG, STM32F405VG, STM32F405ZG, STM32F405OG, STM32F405OE


STM32F407VG, STM32F407IG, STM32F407ZG, STM32F407VE, STM32F407ZE,
STM32F407xx
STM32F407IE


2/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Contents**

## **Contents**


**1** **Introduction ... 13**


**2** **Description ... 14**


2.1 Full compatibility throughout the family ... 17


**3** **Functional overview ... 20**

3.1 Arm [®] Cortex [®] -M4 core with FPU and embedded flash and SRAM ... 21


3.2 Adaptive real-time memory accelerator (ART Accelerator) ... 21


3.3 Memory protection unit ... 21


3.4 Embedded flash memory ... 22


3.5 CRC (cyclic redundancy check) calculation unit ... 22


3.6 Embedded SRAM ... 22


3.7 Multi-AHB bus matrix ... 22


3.8 DMA controller (DMA) ... 23


3.9 Flexible static memory controller (FSMC) ... 24


3.9.1 LCD parallel interface ... 24


3.10 Nested vectored interrupt controller (NVIC) ... 24


3.11 External interrupt/event controller (EXTI) ... 25


3.12 Clocks and startup ... 25


3.13 Boot modes ... 25


3.14 Power supply schemes ... 25


3.15 Power supply supervisor ... 26


3.15.1 Internal reset ON ... 26


3.15.2 Internal reset OFF ... 26


3.16 Voltage regulator ... 28


3.16.1 Regulator ON ... 28


3.16.2 Regulator OFF ... 29


3.17 Regulator ON/OFF and internal reset ON/OFF availability ... 31


3.18 Real-time clock (RTC), backup SRAM and backup registers ... 31


3.19 Low-power modes ... 32

3.20 VBAT operation ... 33

3.21 Timers and watchdogs ... 33


DS8626 Rev 12 3/206



**Contents** **STM32F405xx, STM32F407xx**


3.21.1 Advanced-control timers (TIM1, TIM8) ... 34


3.21.2 General-purpose timers (TIMx) ... 35


3.21.3 Basic timers TIM6 and TIM7 ... 35


3.22 Inter-integrated circuit interface (I²C) ... 36


3.23 Universal synchronous/asynchronous receiver transmitters (USART) . . 36


3.24 Serial peripheral interface (SPI) ... 37


3.25 Inter-integrated sound (I2S) ... 37


3.26 Audio PLL (PLLI2S) ... 38


3.27 Secure digital input/output interface (SDIO) ... 38


3.28 Ethernet MAC interface with dedicated DMA and IEEE 1588 support ... 38


3.29 Controller area network (bxCAN) ... 39


3.30 Universal serial bus on-the-go full-speed (OTG_FS) ... 39


3.31 Universal serial bus on-the-go high-speed (OTG_HS) ... 40


3.32 Digital camera interface (DCMI) ... 40


3.33 True random number generator (RNG) ... 40


3.34 General-purpose input/outputs (GPIOs) ... 41


3.35 Analog-to-digital converters (ADCs) ... 41


3.36 Temperature sensor ... 41


3.37 Digital-to-analog converter (DAC) ... 41


3.38 Serial wire JTAG debug port (SWJ-DP) ... 42


3.39 Embedded Trace Macrocell™ ... 42


**4** **Pinouts and pin description ... 43**


**5** **Memory mapping ... 73**


**6** **Electrical characteristics ... 78**


6.1 Parameter conditions ... 78


6.1.1 Minimum and maximum values ... 78


6.1.2 Typical values ... 78


6.1.3 Typical curves ... 78


6.1.4 Loading capacitor ... 78


6.1.5 Pin input voltage ... 78


6.1.6 Power supply scheme ... 79


6.1.7 Current consumption measurement ... 80


4/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Contents**


6.2 Absolute maximum ratings ... 80


6.3 Operating conditions ... 81


6.3.1 General operating conditions ... 81


6.3.2 VCAP_1/VCAP_2 external capacitor ... 84


6.3.3 Operating conditions at power-up / power-down (regulator ON) ... 84


6.3.4 Operating conditions at power-up / power-down (regulator OFF) ... 84


6.3.5 Embedded reset and power control block characteristics ... 85


6.3.6 Supply current characteristics ... 86


6.3.7 Wakeup time from low-power mode ... 100


6.3.8 External clock source characteristics ... 101


6.3.9 Internal clock source characteristics ... 105


6.3.10 PLL characteristics ... 106


6.3.11 PLL spread spectrum clock generation (SSCG) characteristics ... 108


6.3.12 Memory characteristics ... 110


6.3.13 EMC characteristics ... 112


6.3.14 Absolute maximum ratings (electrical sensitivity) ... 114


6.3.15 I/O current injection characteristics ... 115


6.3.16 I/O port characteristics ... 116


6.3.17 NRST pin characteristics ... 121


6.3.18 TIM timer characteristics ... 121


6.3.19 Communications interfaces ... 123


6.3.20 CAN (controller area network) interface ... 135


6.3.21 12-bit ADC characteristics ... 135


6.3.22 Temperature sensor characteristics ... 140

6.3.23 VBAT monitoring characteristics ... 141

6.3.24 Embedded reference voltage ... 141


6.3.25 DAC electrical characteristics ... 141


6.3.26 FSMC characteristics ... 144


6.3.27 Camera interface (DCMI) timing specifications ... 162


6.3.28 SD/SDIO MMC card host interface (SDIO) characteristics ... 163


6.3.29 RTC characteristics ... 164


**7** **Package information ... 165**


7.1 Device marking ... 165


7.2 WLCSP90 package information ... 166


7.3 LQFP64 package information (5W) ... 169


DS8626 Rev 12 5/206



**Contents** **STM32F405xx, STM32F407xx**


7.4 LQFP100 package information (1L) ... 172


7.5 LQFP144 package information (1A) ... 175


7.6 UFBGA(176+25) package information (A0E7) ... 179


7.7 LQFP176 package information (1T) ... 181


7.8 Thermal characteristics ... 185


**8** **Ordering information ... 186**


**Appendix A** **Application block diagrams ... 187**


A.1 USB OTG full speed (FS) interface solutions ... 187


A.2 USB OTG high speed (HS) interface solutions ... 189


A.3 Ethernet interface solutions... 190


**9** **Important security notice ... 192**


**10** **Revision history ... 193**


6/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **List of tables**

## **List of tables**


Table 1. Device summary ... 2
Table 2. STM32F405xx and STM32F407xx: features and peripheral counts... 15
Table 3. Regulator ON/OFF and internal reset ON/OFF availability... 31
Table 4. Timer feature comparison... 33
Table 5. USART feature comparison ... 37
Table 6. Legend/abbreviations used in the pinout table ... 48
Table 7. STM32F40xxx pin and ball definitions ... 49
Table 8. FSMC pin definition ... 61
Table 9. Alternate function mapping ... 64
Table 10. Register boundary addresses... 74
Table 11. Voltage characteristics ... 80
Table 12. Current characteristics ... 81
Table 13. Thermal characteristics... 81
Table 14. General operating conditions ... 81
Table 15. Limitations depending on the operating power supply range ... 83
Table 16. VCAP_1/VCAP_2 operating conditions ... 84
Table 17. Operating conditions at power-up / power-down (regulator ON) ... 84
Table 18. Operating conditions at power-up / power-down (regulator OFF)... 84
Table 19. Embedded reset and power control block characteristics... 85
Table 20. Typical and maximum current consumption in Run mode, code with data processing
running from flash memory (ART accelerator enabled) or RAM ... 87
Table 21. Typical and maximum current consumption in Run mode, code with data processing
running from flash memory (ART accelerator disabled) ... 88
Table 22. Typical and maximum current consumption in Sleep mode ... 91
Table 23. Typical and maximum current consumptions in Stop mode ... 92
Table 24. Typical and maximum current consumptions in Standby mode ... 92
Table 25. Typical and maximum current consumptions in VBAT mode... 93
Table 26. Typical current consumption in Run mode, code with data processing
running from flash memory, regulator ON (ART accelerator enabled
except prefetch), VDD = 1.8 V... 95
Table 27. Switching output I/O current consumption ... 97
Table 28. Peripheral current consumption ... 98
Table 29. Low-power mode wakeup timings ... 101
Table 30. High-speed external user clock characteristics... 101
Table 31. Low-speed external user clock characteristics ... 102
Table 32. HSE 4-26 MHz oscillator characteristics ... 103
Table 33. LSE oscillator characteristics (fLSE = 32.768 kHz) ... 104
Table 34. HSI oscillator characteristics ... 105
Table 35. LSI oscillator characteristics ... 105
Table 36. Main PLL characteristics... 106
Table 37. PLLI2S (audio PLL) characteristics ... 107
Table 38. SSCG parameters constraint ... 108
Table 39. Flash memory characteristics ... 110
Table 40. Flash memory programming... 110
Table 41. Flash memory programming with VPP ... 112
Table 42. Flash memory endurance and data retention ... 112
Table 43. EMS characteristics ... 113
Table 44. EMI characteristics for fHSE = 25 MH and fCPU = 168 MHz ... 114


DS8626 Rev 12 7/206



**List of tables** **STM32F405xx, STM32F407xx**


Table 45. ESD absolute maximum ratings ... 114
Table 46. Electrical sensitivities ... 115
Table 47. I/O current injection susceptibility ... 116
Table 48. I/O static characteristics ... 116
Table 49. Output voltage characteristics ... 118
Table 50. I/O AC characteristics ... 119
Table 51. NRST pin characteristics ... 121
Table 52. Characteristics of TIMx connected to the APB1 domain ... 122
Table 53. Characteristics of TIMx connected to the APB2 domain ... 123
Table 54. I2C analog filter characteristics... 123
Table 55. SPI dynamic characteristics ... 124
Table 56. I2S dynamic characteristics ... 128
Table 57. USB OTG FS startup time ... 130
Table 58. USB OTG FS DC electrical characteristics... 130
Table 59. USB OTG FS electrical characteristics... 131
Table 60. USB HS DC electrical characteristics ... 131
Table 61. USB HS clock timing parameters ... 131
Table 62. ULPI timing ... 132
Table 63. Ethernet DC electrical characteristics... 133
Table 64. Dynamic characteristics: Ethernet MAC signals for SMI... 133
Table 65. Dynamic characteristics: Ethernet MAC signals for RMII ... 134
Table 66. Dynamic characteristics: Ethernet MAC signals for MII ... 135
Table 67. ADC characteristics ... 135
Table 68. ADC accuracy at fADC = 30 MHz ... 137
Table 69. Temperature sensor characteristics ... 140
Table 70. Temperature sensor calibration values... 140
Table 71. VBAT monitoring characteristics ... 141
Table 72. Embedded internal reference voltage... 141
Table 73. Internal reference voltage calibration values ... 141
Table 74. DAC characteristics ... 141
Table 75. Asynchronous non-multiplexed SRAM/PSRAM/NOR read timings ... 145
Table 76. Asynchronous non-multiplexed SRAM/PSRAM/NOR write timings ... 146
Table 77. Asynchronous multiplexed PSRAM/NOR read timings... 147
Table 78. Asynchronous multiplexed PSRAM/NOR write timings ... 148
Table 79. Synchronous multiplexed NOR/PSRAM read timings ... 150
Table 80. Synchronous multiplexed PSRAM write timings... 151
Table 81. Synchronous non-multiplexed NOR/PSRAM read timings ... 153
Table 82. Synchronous non-multiplexed PSRAM write timings ... 154
Table 83. Switching characteristics for PC Card/CF read and write cycles
in attribute/common space... 159
Table 84. Switching characteristics for PC Card/CF read and write cycles
in I/O space ... 160
Table 85. Switching characteristics for NAND flash read cycles ... 161
Table 86. Switching characteristics for NAND flash write cycles ... 162
Table 87. DCMI characteristics... 162
Table 88. Dynamic characteristics: SD/MMC characteristics ... 164
Table 89. RTC characteristics ... 164
Table 90. WLCSP90 - 4.223 x 3.969 mm, 0.400 mm pitch wafer level chip scale
package mechanical data ... 167
Table 91. WLCSP90 recommended PCB design rules ... 168
Table 92. LQFP64 - Mechanical data ... 170
Table 93. LQFP100 - Mechanical data ... 173


8/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **List of tables**


Table 94. LQFP144 - Mechanical data ... 176
Table 95. UFBGA(176+25) - Mechanical data ... 179
Table 96. UFBGA(176+25) - Example of PCB design rules (0.65 mm pitch BGA) ... 180
Table 97. LQFP176 - Mechanical data ... 182
Table 98. Package thermal characteristics... 185
Table 99. Document revision history ... 193


DS8626 Rev 12 9/206



**List of figures** **STM32F405xx, STM32F407xx**

## **List of figures**


Figure 1. Compatible board design between STM32F10xx/STM32F40xxx for LQFP64 ... 17
Figure 2. Compatible board design STM32F10xx/STM32F2/STM32F40xxx
for LQFP100 package... 18
Figure 3. Compatible board design between STM32F10xx/STM32F2/STM32F40xxx
for LQFP144 package... 18
Figure 4. Compatible board design between STM32F2 and STM32F40xxx
for LQFP176 and BGA176 packages ... 19
Figure 5. STM32F40xxx block diagram ... 20
Figure 6. Multi-AHB matrix... 23
Figure 7. Power supply supervisor interconnection with internal reset OFF ... 27
Figure 8. PDR_ON and NRST control with internal reset OFF ... 28
Figure 9. Regulator OFF ... 29
Figure 10. Startup in regulator OFF mode: slow VDD slope

- power-down reset risen after VCAP_1/VCAP_2 stabilization ... 30
Figure 11. Startup in regulator OFF mode: fast VDD slope

- power-down reset risen before VCAP_1/VCAP_2 stabilization ... 31
Figure 12. STM32F40xxx LQFP64 pinout ... 43
Figure 13. STM32F40xxx LQFP100 pinout ... 44
Figure 14. STM32F40xxx LQFP144 pinout ... 45
Figure 15. STM32F40xxx LQFP176 pinout ... 46
Figure 16. STM32F40xxx UFBGA176 ballout ... 47
Figure 17. STM32F40xxx WLCSP90 ballout ... 48
Figure 18. STM32F40xxx memory map... 73
Figure 19. Pin loading conditions... 78
Figure 20. Pin input voltage ... 78
Figure 21. Power supply scheme ... 79
Figure 22. Current consumption measurement scheme ... 80
Figure 23. External capacitor CEXT ... 84
Figure 24. Typical current consumption versus temperature, Run mode, code with data
processing running from flash (ART accelerator ON) or RAM, and peripherals OFF... 89
Figure 25. Typical current consumption versus temperature, Run mode, code with data
processing running from flash (ART accelerator ON) or RAM, and peripherals ON... 89
Figure 26. Typical current consumption versus temperature, Run mode, code with data
processing running from flash (ART accelerator OFF) or RAM, and peripherals OFF... 90
Figure 27. Typical current consumption versus temperature, Run mode, code with data
processing running from flash (ART accelerator OFF) or RAM, and peripherals ON... 90
Figure 28. Typical VBAT current consumption (LSE and RTC ON/backup RAM OFF) ... 93
Figure 29. Typical VBAT current consumption (LSE and RTC ON/backup RAM ON) ... 94
Figure 30. High-speed external clock source AC timing diagram ... 102
Figure 31. Low-speed external clock source AC timing diagram... 103
Figure 32. Typical application with an 8 MHz crystal ... 104
Figure 33. Typical application with a 32.768 kHz crystal ... 105
Figure 34. ACCLSI versus temperature ... 106
Figure 35. PLL output clock waveforms in center spread mode ... 109
Figure 36. PLL output clock waveforms in down spread mode ... 110
Figure 37. I/O AC characteristics definition ... 120
Figure 38. Recommended NRST pin protection ... 121
Figure 39. SPI timing diagram - slave mode and CPHA = 0 ... 126


10/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **List of figures**


Figure 40. SPI timing diagram - slave mode and CPHA = 1 ... 126
Figure 41. SPI timing diagram - master mode ... 127
Figure 42. I2S slave timing diagram (Philips protocol) ... 129
Figure 43. I2S master timing diagram (Philips protocol) [(1)] ... 129
Figure 44. USB OTG FS timings: definition of data signal rise and fall time ... 131
Figure 45. ULPI timing diagram ... 132
Figure 46. Ethernet SMI timing diagram ... 133
Figure 47. Ethernet RMII timing diagram ... 134
Figure 48. Ethernet MII timing diagram ... 134
Figure 49. ADC accuracy characteristics... 137
Figure 50. Typical connection diagram when using the ADC with FT/TT pins featuring
analog switch function ... 138
Figure 51. Power supply and reference decoupling (VREF+ not connected to VDDA)... 139
Figure 52. Power supply and reference decoupling (VREF+ connected to VDDA)... 140
Figure 53. 12-bit buffered /non-buffered DAC ... 144
Figure 54. Asynchronous non-multiplexed SRAM/PSRAM/NOR read waveforms ... 145
Figure 55. Asynchronous non-multiplexed SRAM/PSRAM/NOR write waveforms ... 146
Figure 56. Asynchronous multiplexed PSRAM/NOR read waveforms... 147
Figure 57. Asynchronous multiplexed PSRAM/NOR write waveforms ... 148
Figure 58. Synchronous multiplexed NOR/PSRAM read timings ... 149
Figure 59. Synchronous multiplexed PSRAM write timings... 151
Figure 60. Synchronous non-multiplexed NOR/PSRAM read timings ... 152
Figure 61. Synchronous non-multiplexed PSRAM write timings ... 154
Figure 62. PC Card/CompactFlash controller waveforms for common memory read access ... 155
Figure 63. PC Card/CompactFlash controller waveforms for common memory write access... 156
Figure 64. PC Card/CompactFlash controller waveforms for attribute memory read
access... 157
Figure 65. PC Card/CompactFlash controller waveforms for attribute memory write
access... 158
Figure 66. PC Card/CompactFlash controller waveforms for I/O space read access ... 158
Figure 67. PC Card/CompactFlash controller waveforms for I/O space write access ... 159
Figure 68. NAND controller waveforms for read access ... 161
Figure 69. NAND controller waveforms for write access ... 161
Figure 70. DCMI timing diagram ... 162
Figure 71. SDIO high-speed mode ... 163
Figure 72. SD default mode ... 164
Figure 73. WLCSP90 - 4.223 x 3.969 mm, 0.400 mm pitch wafer level chip scale
package outline... 166
Figure 74. WLCSP90 - 4.223 x 3.969 mm, 0.400 mm pitch wafer level chip scale
package recommended footprint ... 167
Figure 75. WLCSP90 marking example (package top view) ... 168
Figure 76. LQFP64 - Outline [(15)] ... 169
Figure 77. LQFP100 - Outline [(15)] ... 172
Figure 78. LQFP100 - Footprint example ... 174
Figure 79. LQFP144 - Outline [(15)] ... 175
Figure 80. LQFP144 - Footprint example ... 178
Figure 81. UFBGA(176+25) - Outline ... 179
Figure 82. UFBGA(176+25) - Footprint example... 180
Figure 83. LQFP176 - Outline [(15)] ... 181
Figure 84. LQFP176 - Footprint example ... 184
Figure 85. USB controller configured as peripheral-only and used
in Full speed mode ... 187


DS8626 Rev 12 11/206



**List of figures** **STM32F405xx, STM32F407xx**


Figure 86. USB controller configured as host-only and used in full speed mode... 187
Figure 87. USB controller configured in dual mode and used in full speed mode ... 188
Figure 88. USB controller configured as peripheral, host, or dual-mode
and used in high speed mode... 189
Figure 89. MII mode using a 25 MHz crystal ... 190
Figure 90. RMII with a 50 MHz oscillator ... 190
Figure 91. RMII with a 25 MHz crystal and PHY with PLL... 191


12/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Introduction**

### **1 Introduction**


This datasheet provides the description of the STM32F405xx and STM32F407xx lines of
microcontrollers. For more details on the whole STMicroelectronics STM32™ family, refer to
_Section 2.1: Full compatibility throughout the family_ .


The STM32F405xx and STM32F407xx datasheet should be read in conjunction with the
STM32F4xx reference manual which is available from the STMicroelectronics website
_www.st.com_ .


For information on the device errata with respect to the datasheet and reference manual,
refer to the STM32F405xx and STM32F407xx errata sheet (ES0182), which is available
from the STMicroelectronics website _www.st.com_ .

For information on the Arm [® ] Cortex [®] -M4 core, refer to the Cortex [®] -M4 programming
manual (PM0214) available from _www.st.com_ .


_Note:_ _Arm and Cortex are registered trademarks of Arm Limited (or its subsidiaries or affiliates) in_
_the US and/or elsewhere._

_The Arm word and logo are trademarks of Arm Limited (or its subsidiaries) in the US and/or_
_elsewhere. All rights reserved._


DS8626 Rev 12 13/206



**Description** **STM32F405xx, STM32F407xx**

### **2 Description**


The STM32F405xx and STM32F407xx family is based on the high-performance Arm [®]
Cortex [®] -M4 32-bit RISC core operating at a frequency of up to 168 MHz. The Cortex [®] -M4
core features a floating-point unit (FPU) single precision which supports all Arm singleprecision data-processing instructions and data types. It also implements a full set of DSP
instructions and a memory protection unit (MPU) which enhances application security.


The STM32F405xx and STM32F407xx family incorporates high-speed embedded
memories (flash memory up to 1 Mbyte, up to 192 Kbytes of SRAM), up to 4 Kbytes of
backup SRAM, and an extensive range of enhanced I/Os and peripherals connected to two
APB buses, three AHB buses and a 32-bit multi-AHB bus matrix.


All devices offer three 12-bit ADCs, two DACs, a low-power RTC, 12 general-purpose 16-bit
timers including two PWM timers for motor control, two general-purpose 32-bit timers. a true
random number generator (RNG). They also feature standard and advanced
communication interfaces.

- Up to three I [2] Cs

- Three SPIs, two I [2] Ss full duplex. To achieve audio class accuracy, the I2S peripherals
can be clocked via a dedicated internal audio PLL or via an external clock to allow
synchronization

- Four USARTs plus two UARTs

- A USB OTG full speed and a USB OTG high speed with full-speed capability (with the
ULPI)

- Two CANs

- An SDIO/MMC interface

- Ethernet and the camera interface available on STM32F407xx devices only


New advanced peripherals include an SDIO, an enhanced flexible static memory control
(FSMC) interface (for devices offered in packages of 100 pins and more), a camera
interface for CMOS sensors. Refer to _Table 2: STM32F405xx and STM32F407xx: features_
_and peripheral counts_ for the list of peripherals available on each part number.


The STM32F405xx and STM32F407xx family operates in the –40 to +105 °C temperature
range from a 1.8 to 3.6 V power supply. The supply voltage can drop to 1.7 V when the
device operates in the 0 to 70 °C temperature range using an external power supply
supervisor: refer to _Section 3.15.2: Internal reset OFF_ . A comprehensive set of powersaving mode allows the design of low-power applications.


The STM32F405xx and STM32F407xx family offers devices in various packages ranging
from 64 pins to 176 pins. The set of included peripherals changes with the device chosen.


These features make the STM32F405xx and STM32F407xx microcontroller family suitable
for a wide range of applications:

- Motor drive and application control

- Medical equipment

- Industrial applications: PLC, inverters, circuit breakers

- Printers, and scanners

- Alarm systems, video intercom, and HVAC

- Home audio appliances


14/206 DS8626 Rev 12


_Figure 5_ shows the general block diagram of the device family.


**Table 2. STM32F405xx and STM32F407xx: features and peripheral counts**


**Peripherals** **STM32F405RG** **STM32F405OG** **STM32F405VG** **STM32F405ZG** **STM32F405OE** **STM32F407Vx** **STM32F407Zx** **STM32F407Ix**


Flash memory in
1024 512 512 1024 512 1024 512 1024
Kbytes


SRAM in
Kbytes


System 192(112+16+64)


Backup 4


FSMC memory
No Yes [(1)]
controller


Ethernet No Yes


General10
purpose


Advanced
2
-control


Timers


Basic 2


IWDG Yes


WWDG Yes


RTC Yes


True random number
Yes
generator


**Table 2. STM32F405xx and STM32F407xx: features and peripheral counts (continued)**


**Peripherals** **STM32F405RG** **STM32F405OG** **STM32F405VG** **STM32F405ZG** **STM32F405OE** **STM32F407Vx** **STM32F407Zx** **STM32F407Ix**


SPI / I2S 3/2 (full duplex) [(2)]

I [2] C 3


USART/
4/2
UART


Communi
cation
interfaces


USB
Yes
OTG FS


USB
Yes
OTG HS


CAN 2


SDIO Yes


Camera interface No Yes


GPIOs 51 72 82 114 72 82 114 140


12-bit ADC
Number of channels



16 13 16 24 13 16 24 24


12-bit DAC Yes
Number of channels 2


Maximum CPU
168 MHz
frequency

Operating voltage 1.8 to 3.6 V [(3)]


Operating
temperatures


Ambient temperatures: –40 to +85 °C /–40 to +105 °C


Junction temperature: –40 to + 125 °C


UFBGA176
Package LQFP64 WLCSP90 LQFP100 LQFP144 WLCSP90 LQFP100 LQFP144
LQFP176


1. For the LQFP100 and WLCSP90 packages, only FSMC Bank1 or Bank2 are available. Bank1 can only support a multiplexed NOR/PSRAM memory using the NE1 Chip
Select. Bank2 can only support a 16- or 8-bit NAND flash memory using the NCE2 Chip Select. The interrupt line cannot be used since Port G is not available in this
package.

2. The SPI2 and SPI3 interfaces give the flexibility to work in an exclusive way in either the SPI mode or the I [2] S audio mode.

3. VDD/VDDA minimum value of 1.7 V is obtained when the device operates in reduced temperature range, and with the use of an external power supply supervisor (refer to
_Section 3.15.2: Internal reset OFF_ ).


**STM32F405xx, STM32F407xx** **Description**

#### **2.1 Full compatibility throughout the family**


The STM32F405xx and STM32F407xx are part of the STM32F4 family. They are fully pinto-pin, software and feature compatible with the STM32F2xx devices, allowing the user to
try different memory densities, peripherals, and performances (FPU, higher frequency) for a
greater degree of freedom during the development cycle.


The STM32F405xx and STM32F407xx devices maintain a close compatibility with the
whole STM32F10xxx family. All functional pins are pin-to-pin compatible. The
STM32F405xx and STM32F407xx, however, are not drop-in replacements for the
STM32F10xxx devices: the two families do not have the same power scheme, and so their
power pins are different. Nonetheless, transition from the STM32F10xxx to the
STM32F40xxx family remains simple as only a few pins are impacted.


_Figure 4_, _Figure 3_, _Figure 2_, and _Figure 1_ give compatible board designs between the
STM32F40xxx, STM32F2, and STM32F10xxx families.


**Figure 1. Compatible board design between STM32F10xx/STM32F40xxx for LQFP64**


VSS


VSS


48 33

47 32


49 47


VSS


VSS


0 Ω resistor or soldering bridge
present for the STM32F10xx
configuration, not present in the
STM32F4xx configuration




1 16



ai18489


DS8626 Rev 12 17/206



**Description** **STM32F405xx, STM32F407xx**


**Figure 2. Compatible board design STM32F10xx/STM32F2/STM32F40xxx**
**for LQFP100 package**


VSS


75 51

73 50


76 73



VSS


VSS



��������������������������������
�������������������32F10xxx
99 (VSS) ���������������������������������

19 20 26 �������������������������


19 20 26

1 25




VSS

���������������������������������
-�����������������������
-����������������������
-����������������������������


VDD


VSS


VSS


������������������
�����������������


ai18488d


**Figure 3. Compatible board design between STM32F10xx/STM32F2/STM32F40xxx**
**for LQFP144 package**


��������������������������������
�������������������32F10xx

VSS 73 ����������������������������������

106 �������������������������


VSS


108 SS 73


���������������������32F10xx





VSS


VSS

�����������������������
����������������������
���������������


������������
���������������
�������
����������




VDD VSS


������������




1 36


VSS


���������������������������������

- V- VSSSS ������������������, VDD ����������������������� VDD VSS VVSS DD

- VDD �����������������������������������������������������������������


VDD VSS


VSS ��������������
VDD �������������


ai18487d


18/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Description**


**Figure 4. Compatible board design between STM32F2 and STM32F40xxx**
**for LQFP176 and BGA176 packages**


132 89


������������


1 44


���������������������
�������������
��������o�






VDDVSS


������������������������������������

- VSS, VDD �����������������������

- VDD ���������������������������������������������o�������������������


MS19919V3


DS8626 Rev 12 19/206



**Functional overview** **STM32F405xx, STM32F407xx**

### **3 Functional overview**


**Figure 5. STM32F40xxx block diagram**


RNG


Camera
interface


USB

OTG FS


CCM data RAM 64 KB


NJTRST, JTDI,


JTCK/SWCLK


JTDO/SWD, JTDO


TRACECLK


TRACED[3:0]


MII or RMII as AF


MDIO as AF


DP, DM


ULPI:CK, D[7:0], DIR, STP, NXT


ID, VBUS, SOF


PA[15:0]


PB[15:0]


PC[15:0]


PD[15:0]


PE[15:0]


PF[15:0]


PG[15:0]


PH[15:0]


PI[11:0]


140 AF


DMA2 8 StreamsFIFO


DMA1 8 StreamsFIFO


GPIO PORT A


GPIO PORT B


GPIO PORT C


GPIO PORT D


GPIO PORT E


GPIO PORT F


GPIO PORT G


GPIO PORT H


GPIO PORT I


EXT IT. WKUP


External memory
controller (FSMC)

SRAM, PSRAM, NOR Flash,
PC Card (ATA), NAND Flash


Flash

up to


1 MB


SRAM 112 KB


SRAM 16 KB


JTAG & SW


MPU


AHB3


ETM NVIC


D-BUS


Arm Cortex-M4
168 MHz

FPU


Ethernet MAC

10/100


USB

OTG HS


I-BUS


S-BUS


DMA/


FIFO


DMA/


FIFO


DMA2


AHB/APB2 AHB/APB1


WWDG


TIM6


TIM7


@VDDA


DAC1


DAC2


DMA1


16b


16b


ITF


AHB2 168 MHz


AHB1 168 MHz


Reset &


M ANclockA G T

control


XTAL OSC
4- 16MHz


IWDG


PWR
interface


@VBAT


XTAL 32 kHz


RTC

AWU


VDD Power managmt


Voltage
regulator
3.3 to 1.2 V


@VDDA @VDD


Supply
supervision


POR/PDR
BOR


PVD


RC HS


RC L S


P L L1&2


POR
reset


Int


@VDDA


@VDD


CLK, NE [3:0], A[23:0],


D[31:0], OEN, WEN,


NBL[3:0], NL, NREG,


NWAIT/IORDY, CD


NIORD, IOWR, INT[2:3]


INTN, NIIS16 as AF


HSYNC, VSYNC


PUIXCLK, D[13:0]


DP


DM


ID, VBUS, SOF


VDD = 1.8 to 3.6 V


VSS


VCAP1, VCPA2


VDDA, VSSA


NRST


OSC_IN


OSC_OUT


VBAT = 1.65 to 3.6 V


OSC32_IN


OSC32_OUT


RTC_AF1


Backup register RTC_AF1


4 KB BKPSRAM


4 channels, ETR as AF


4 channels, ETR as AF


4 channels, ETR as AF


4 channels


2 channels as AF


1 channel as AF


1 channel as AF


RX, TX as AF
CTS, RTS as AF


RX, TX as AF
CTS, RTS as AF


RX, TX as AF


RX, TX as AF


MOSI/SD, MISO/SD_ext, SCK/CK
NSS/WS, MCK as AF


MOSI/SD, MISO/SD_ext, SCK/CK
NSS/WS, MCK as AF


SCL, SDA, SMBA as AF


SCL, SDA, SMBA as AF


SCL, SDA, SMBA as AF


TX, RX


TX, RX


MS19920V5


I2C1/SMBUS


I2C2/SMBUS


I2C3/SMBUS


bxCAN1


bxCAN2


TIM2


TIM3


TIM4


TIM5


TIM12


TIM13


TIM14


USART2


USART3


UART4


UART5


SP2/I2S2


SP3/I2S3


32b


16b


16b


32b


16b


16b


16b


smcard
irDA


smcard
irDA


CMD, CK as AFD[7:0] SDIO / MMC


4 compl. channels (TIM1_CH1[1:4]N,
4 channels (TIM1_CH1[1:4]ETR, TIM1 / PWM
BKIN as AF


16b


4 compl. channels (TIM1_CH1[1:4]N,
4 channels (TIM1_CH1[1:4]ETR, TIM8 / PWM 16b
BKIN as AF


2 channels as AF


1 channel as AF


1 channel as AF


RX, TX, CK,
CTS, RTS as AF


RX, TX, CK,
CTS, RTS as AF


MOSI, MISO,
SCK, NSS as AF


VDDREF_ADC


8 analog inputs common
to the 3 ADCs


8 analog inputs common
to the ADC1 & 2


8 analog inputs for ADC3


TIM9 16b


TIM10 16b


TIM11 16b


irDAsmcard USART1

smcardirDA USART6


SPI1


@VDDA


Temperature sensor


ADC1


ADC2


ADC3


IF


DAC1_OUT


as AF


DAC2_OUT


as AF


1. The camera interface and ethernet are available only on STM32F407xx devices.


20/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**

#### 3.1 Arm [®] Cortex [®] -M4 core with FPU and embedded flash and **SRAM**


The Arm Cortex-M4 processor with FPU is the latest generation of Arm processors for
embedded systems. It was developed to provide a low-cost platform that meets the needs of
MCU implementation, with a reduced pin count and low-power consumption, while
delivering outstanding computational performance and an advanced response to interrupts.


The Arm Cortex-M4 32-bit RISC processor with FPU features exceptional code-efficiency,
delivering the high-performance expected from an Arm core in the memory size usually
associated with 8- and 16-bit devices.


The processor supports a set of DSP instructions which allow efficient signal processing and
complex algorithm execution.


Its single precision FPU (floating point unit) speeds up software development by using
metalanguage development tools, while avoiding saturation.


The STM32F405xx and STM32F407xx family is compatible with all Arm tools and software.


_Figure 5_ shows the general block diagram of the STM32F40xxx family.


_Note:_ _Cortex-M4 with FPU is binary compatible with Cortex-M3._

#### **3.2 Adaptive real-time memory accelerator (ART Accelerator)**


The ART Accelerator is a memory accelerator which is optimized for STM32 industrystandard Arm [®] Cortex [®] -M4 with FPU processors. It balances the inherent performance
advantage of the Arm Cortex-M4 with FPU over flash memory technologies, which normally
requires the processor to wait for the flash memory at higher frequencies.


To release the processor full 210 DMIPS performance at this frequency, the accelerator
implements an instruction prefetch queue and branch cache, which increases program
execution speed from the 128-bit flash memory. Based on CoreMark benchmark, the
performance achieved thanks to the ART accelerator is equivalent to 0 wait state program
execution from flash memory at a CPU frequency up to 168 MHz.

#### **3.3 Memory protection unit**


The memory protection unit (MPU) is used to manage the CPU accesses to memory to
prevent one task to accidentally corrupt the memory or resources used by any other active
task. This memory area is organized into up to 8 protected areas that can in turn be divided
up into 8 subareas. The protection area sizes are between 32 bytes and the whole 4
gigabytes of addressable memory.


The MPU is especially helpful for applications where some critical or certified code has to be
protected against the misbehavior of other tasks. It is usually managed by an RTOS (realtime operating system). If a program accesses a memory location that is prohibited by the
MPU, the RTOS can detect it and take action. In an RTOS environment, the kernel can
dynamically update the MPU area setting, based on the process to be executed.


The MPU is optional and can be bypassed for applications that do not need it.


DS8626 Rev 12 21/206



**Functional overview** **STM32F405xx, STM32F407xx**

#### **3.4 Embedded flash memory**


The STM32F40xxx devices embed a flash memory of 512 Kbytes or 1 Mbytes available for
storing programs and data, plus 512 bytes of OTP memory.

#### **3.5 CRC (cyclic redundancy check) calculation unit**


The CRC (cyclic redundancy check) calculation unit is used to get a CRC code from a 32-bit
data word and a fixed generator polynomial.


Among other applications, CRC-based techniques are used to verify data transmission or
storage integrity. In the scope of the EN/IEC 60335-1 standard, they offer a means of
verifying the flash memory integrity. The CRC calculation unit helps compute a software
signature during runtime, to be compared with a reference signature generated at link-time
and stored at a given memory location.

#### **3.6 Embedded SRAM**


All STM32F40xxx products embed:

- Up to 192 Kbytes of system SRAM including 64 Kbytes of CCM (core coupled memory)
data RAM

RAM memory is accessed (read/write) at CPU clock speed with 0 wait states.

- 4 Kbytes of backup SRAM

This area is accessible only from the CPU. Its content is protected against possible
unwanted write accesses, and is retained in Standby or VBAT mode.

#### **3.7 Multi-AHB bus matrix**


The 32-bit multi-AHB bus matrix interconnects all the masters (CPU, DMAs, Ethernet, USB
HS) and the slaves (flash memory, RAM, FSMC, AHB, and APB peripherals) and ensures a
seamless and efficient operation even when several high-speed peripherals work
simultaneously.


22/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**


**Figure 6. Multi-AHB matrix**


64-Kbyte
CCM data RAM


ARM GP GP MAC USB OTG
Cortex-M4 DMA1 DMA2 Ethernet HS


ICODE


DCODE


Flash
memory


SRAM1
112 Kbyte


SRAM2
16 Kbyte

AHB1
peripherals

AHB2


APB1


Bus matrix-S

#### **3.8 DMA controller (DMA)**


peripherals
APB2

FSMC
Static MemCtl


ai18490e


The devices feature two general-purpose dual-port DMAs (DMA1 and DMA2) with 8
streams each. They are able to manage memory-to-memory, peripheral-to-memory and
memory-to-peripheral transfers. They feature dedicated FIFOs for APB/AHB peripherals,
support burst transfer and are designed to provide the maximum peripheral bandwidth
(AHB/APB).


The two DMA controllers support circular buffer management, so that no specific code is
needed when the controller reaches the end of the buffer. The two DMA controllers also
have a double buffering feature, which automates the use and switching of two memory
buffers without requiring any special code.


Each stream is connected to dedicated hardware DMA requests, with support for software
trigger on each stream. Configuration is made by software and transfer sizes between
source and destination are independent.


DS8626 Rev 12 23/206



**Functional overview** **STM32F405xx, STM32F407xx**


The DMA can be used with the main peripherals:

- SPI and I [2] S

- I [2] C

- USART

- General-purpose, basic and advanced-control timers TIMx

- DAC

- SDIO

- Camera interface (DCMI)

- ADC.

#### **3.9 Flexible static memory controller (FSMC)**


The FSMC is embedded in the STM32F405xx and STM32F407xx family. It has four Chip
Select outputs supporting the following modes: PCCard/CompactFlash, SRAM, PSRAM,
NOR flash and NAND flash.


Functionality overview:

- Write FIFO

- Maximum FSMC_CLK frequency for synchronous accesses is 60 MHz.


**3.9.1** **LCD parallel interface**


The FSMC can be configured to interface seamlessly with most graphic LCD controllers. It
supports the Intel 8080 and Motorola 6800 modes, and is flexible enough to adapt to
specific LCD interfaces. This LCD parallel interface capability makes it easy to build costeffective graphic applications using LCD modules with embedded controllers or high
performance solutions using external controllers with dedicated acceleration.

#### **3.10 Nested vectored interrupt controller (NVIC)**


The STM32F405xx and STM32F407xx embed a nested vectored interrupt controller able to
manage 16 priority levels, and handle up to 82 maskable interrupt channels plus the 16
interrupt lines of the Cortex [®] -M4 with FPU core.

- Closely coupled NVIC gives low-latency interrupt processing

- Interrupt entry vector table address passed directly to the core

- Allows early processing of interrupts

- Processing of late arriving, higher-priority interrupts

- Support tail chaining

- Processor state automatically saved

- Interrupt entry restored on interrupt exit with no instruction overhead


This hardware block provides flexible interrupt management features with minimum interrupt
latency.


24/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**

#### **3.11 External interrupt/event controller (EXTI)**


The external interrupt/event controller consists of 23 edge-detector lines used to generate
interrupt/event requests. Each line can be independently configured to select the trigger
event (rising edge, falling edge, both) and can be masked independently. A pending register
maintains the status of the interrupt requests. The EXTI can detect an external line with a
pulse width shorter than the Internal APB2 clock period. Up to 140 GPIOs can be connected
to the 16 external interrupt lines.

#### **3.12 Clocks and startup**


On reset the 16 MHz internal RC oscillator is selected as the default CPU clock. The
16 MHz internal RC oscillator is factory-trimmed to offer 1% accuracy over the full
temperature range. The application can then select as system clock either the RC oscillator
or an external 4-26 MHz clock source. This clock can be monitored for failure. If a failure is
detected, the system automatically switches back to the internal RC oscillator and a
software interrupt is generated (if enabled). This clock source is input to a PLL thus allowing
to increase the frequency up to 168 MHz. Similarly, full interrupt management of the PLL
clock entry is available when necessary (for example if an indirectly used external oscillator
fails).


Several prescalers allow the configuration of the three AHB buses, the high-speed APB
(APB2) and the low-speed APB (APB1) domains. The maximum frequency of the three AHB
buses is 168 MHz while the maximum frequency of the high-speed APB domains is
84 MHz. The maximum allowed frequency of the low-speed APB domain is 42 MHz.


The devices embed a dedicated PLL (PLLI2S) which allows to achieve audio class
performance. In this case, the I [2] S master clock can generate all standard sampling
frequencies from 8 kHz to 192 kHz.

#### **3.13 Boot modes**


At startup, boot pins are used to select one out of three boot options:

- Boot from user flash

- Boot from system memory

- Boot from embedded SRAM


The boot loader is located in system memory. It is used to reprogram the flash memory by
using USART1 (PA9/PA10), USART3 (PC10/PC11 or PB10/PB11), CAN2 (PB5/PB13), USB
OTG FS in Device mode (PA11/PA12) through DFU (device firmware upgrade).

#### **3.14 Power supply schemes**


- VDD = 1.8 to 3.6 V: external power supply for I/Os and the internal regulator (when
enabled), provided externally through VDD pins.

- VSSA, VDDA = 1.8 to 3.6 V: external analog power supplies for ADC, DAC, Reset
blocks, RCs and PLL. VDDA and VSSA must be connected to VDD and VSS, respectively.

- VBAT = 1.65 to 3.6 V: power supply for RTC, external clock 32 kHz oscillator and
backup registers (through power switch) when VDD is not present.


DS8626 Rev 12 25/206



**Functional overview** **STM32F405xx, STM32F407xx**


Refer to _Figure 21: Power supply scheme_ for more details.


_Note:_ _VDD/VDDA minimum value of 1.7 V is obtained when the device operates in reduced_
_temperature range, and with the use of an external power supply supervisor (refer to_
_Section 3.15.2: Internal reset OFF)._

_Refer to Table 2 in order to identify the packages supporting this option._

#### **3.15 Power supply supervisor**


**3.15.1** **Internal reset ON**


On packages embedding the PDR_ON pin, the power supply supervisor is enabled by
holding PDR_ON high. On all other packages, the power supply supervisor is always
enabled.


The device has an integrated power-on reset (POR) / power-down reset (PDR) circuitry
coupled with a Brownout reset (BOR) circuitry. At power-on, POR/PDR is always active and
ensures proper operation starting from 1.8 V. After the 1.8 V POR threshold level is
reached, the option byte loading process starts, either to confirm or modify default BOR
threshold levels, or to disable BOR permanently. Three BOR thresholds are available
through option bytes. The device remains in reset mode when VDD is below a specified
threshold, VPOR/PDR or VBOR, without the need for an external reset circuit.

The device also features an embedded programmable voltage detector (PVD) that monitors
the VDD/VDDA power supply and compares it to the VPVD threshold. An interrupt can be
generated when VDD/VDDA drops below the VPVD threshold and/or when VDD/VDDA is
higher than the VPVD threshold. The interrupt service routine can then generate a warning
message and/or put the MCU into a safe state. The PVD is enabled by software.


**3.15.2** **Internal reset OFF**


This feature is available only on packages featuring the PDR_ON pin. The internal power-on
reset (POR) / power-down reset (PDR) circuitry is disabled with the PDR_ON pin.


An external power supply supervisor should monitor VDD and should maintain the device in
reset mode as long as VDD is below a specified threshold. PDR_ON should be connected to
this external power supply supervisor. Refer to _Figure 7: Power supply supervisor_
_interconnection with internal reset OFF_ .


26/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**


**Figure 7. Power supply supervisor interconnection with internal reset OFF**


VDD


**External VDD power supply supervisor**


Ext. reset controller active when


VDD < 1.7 V


Application reset
signal


VSS


VDD


NRST


PDR_ON


MS31383V4


1. PDR = 1.7 V for reduce temperature range; PDR = 1.8 V for all temperature range.

The VDD specified threshold, below which the device must be maintained under reset, is
1.8 V (see _Figure 7_ ). This supply voltage can drop to 1.7 V when the device operates in the
0 to 70 °C temperature range.


A comprehensive set of power-saving mode allows to design low-power applications.


When the internal reset is OFF, the following integrated features are no more supported:

- The integrated power-on reset (POR) / power-down reset (PDR) circuitry is disabled

- The brownout reset (BOR) circuitry is disabled

- The embedded programmable voltage detector (PVD) is disabled

- VBAT functionality is no more available and VBAT pin should be connected to VDD

All packages, except for the LQFP64 and LQFP100, allow to disable the internal reset
through the PDR_ON signal.


DS8626 Rev 12 27/206



**Functional overview** **STM32F405xx, STM32F407xx**


**Figure 8. PDR_ON and NRST control with internal reset OFF**


VDD


PDR = 1.7 V


time


Reset by a source different from
power supply supervisor


NRST


PDR_ON PDR_ON


time


MS19009V8


1. PDR = 1.7 V for reduce temperature range; PDR = 1.8 V for all temperature range.

#### **3.16 Voltage regulator**


The regulator has four operating modes:

- Regulator ON

- Main regulator mode (MR)

- Low-power regulator (LPR)

- Power-down

- Regulator OFF


**3.16.1** **Regulator ON**


On packages embedding the BYPASS_REG pin, the regulator is enabled by holding
BYPASS_REG low. On all other packages, the regulator is always enabled.


There are three power modes configured by software when regulator is ON:

- MR is used in the nominal regulation mode (With different voltage scaling in Run)

In Main regulator mode (MR mode), different voltage scaling are provided to reach the
best compromise between maximum frequency and dynamic power consumption.
Refer to _Table 14: General operating conditions_ .

- LPR is used in the Stop modes

The LP regulator mode is configured by software when entering Stop mode.

- Power-down is used in Standby mode.

The Power-down mode is activated only when entering in Standby mode. The regulator
output is in high impedance and the kernel circuitry is powered down, inducing zero
consumption. The contents of the registers and SRAM are lost)


28/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**


Two external ceramic capacitors should be connected on VCAP_1 & VCAP_2 pin. Refer to
_Figure 21: Power supply scheme_ and _Figure 16: VCAP_1/VCAP_2 operating conditions_ .


All packages have regulator ON feature.


**3.16.2** **Regulator OFF**


This feature is available only on packages featuring the BYPASS_REG pin. The regulator is
disabled by holding BYPASS_REG high. The regulator OFF mode allows to supply
externally a V12 voltage source through VCAP_1 and VCAP_2 pins.

Since the internal voltage scaling is not manage internally, the external voltage value must
be aligned with the targeted maximum frequency. Refer to _Table 14: General operating_
_conditions_ .


The two 2.2 µF ceramic capacitors should be replaced by two 100 nF decoupling
capacitors.


Refer to _Figure 21: Power supply scheme_


When the regulator is OFF, there is no more internal monitoring on V12. An external power
supply supervisor should be used to monitor the V12 of the logic power domain. PA0 pin
should be used for this purpose, and act as power-on reset on V12 power domain.

In regulator OFF mode the following features are no more supported:

- PA0 cannot be used as a GPIO pin since it allows to reset a part of the V12 logic power
domain which is not reset by the NRST pin.

- As long as PA0 is kept low, the debug mode cannot be used under power-on reset. As
a consequence, PA0 and NRST pins must be managed separately if the debug
connection under reset or pre-reset is required.

- The standby mode is not available


**Figure 9. Regulator OFF**


V12


External VCAP_1/2 power
supply supervisor
Ext. reset controller active
when VCAP_1/2 < Min V12


PA0


BYPASS_REG


Application reset
signal (optional)


NRST


ai18498V5


(note 1)
(1 x 100 nF)
2 x 100 nF

V DD


N × 100 nF
+ 1 × 4.7 μF


V12


V DD
1/2/...N


V CAP1
V CAP2


VSS
1/2/...N


DS8626 Rev 12 29/206



**Functional overview** **STM32F405xx, STM32F407xx**


The following conditions must be respected:

- VDD should always be higher than VCAP_1 and VCAP_2 to avoid current injection
between power domains.

- If the time for VCAP_1 and VCAP_2 to reach V12 minimum value is faster than the time for
VDD to reach 1.8 V, then PA0 should be kept low to cover both conditions: until VCAP_1
and VCAP_2 reach V12 minimum value and until VDD reaches 1.8 V (see _Figure 10_ ).

- Otherwise, if the time for VCAP_1 and VCAP_2 to reach V12 minimum value is slower
than the time for VDD to reach 1.8 V, then PA0 could be asserted low externally (see
_Figure 11_ ).

- If VCAP_1 and VCAP_2 go below V12 minimum value and VDD is higher than 1.8 V, then
a reset must be asserted on PA0 pin.


_Note:_ _The minimum value of_ V12 _depends on the maximum frequency targeted in the application_
_(see Table 14: General operating conditions)._


**Figure 10. Startup in regulator OFF mode: slow VDD slope**

**- power-down reset risen after VCAP_1/VCAP_2 stabilization**


VDD


PDR = 1.7 V or 1.8 V [(2)]

VCAP_1/VCAP_2
V12

Min V12


NRST


1. This figure is valid both whatever the internal reset mode (ON or OFF).

2. PDR = 1.7 V for reduced temperature range; PDR = 1.8 V for all temperature ranges.


30/206 DS8626 Rev 12


time


time


ai18491e


**STM32F405xx, STM32F407xx** **Functional overview**


**Figure 11. Startup in regulator OFF mode: fast VDD slope**

**- power-down reset risen before VCAP_1/VCAP_2 stabilization**


VDD


PDR = 1.7 V or 1.8 V [(2)]


VCAP_1/VCAP_2
V12

Min V12


time

NRST


PA0 asserted externally


time ai18492d


1. This figure is valid both whatever the internal reset mode (ON or OFF).

2. PDR = 1.7 V for a reduced temperature range; PDR = 1.8 V for all temperature ranges.

#### **3.17 Regulator ON/OFF and internal reset ON/OFF availability**


**Table 3. Regulator ON/OFF and internal reset ON/OFF availability**


**Internal reset**
**Regulator ON** **Regulator OFF** **Internal reset ON**
**OFF**


LQFP64
Yes No
LQFP100 Yes No


LQFP144
Yes

WLCSP90 Yes Yes

PDR_ON set to

UFBGA176 BYPASS_REG set BYPASS_REG set VDD


Yes
PDR_ON
connected to an
external power
supply supervisor


WLCSP90
UFBGA176
LQFP176


Yes
BYPASS_REG set
to VSS


Yes
BYPASS_REG set
to VDD


#### **3.18 Real-time clock (RTC), backup SRAM and backup registers**

The backup domain of the STM32F405xx and STM32F407xx includes:

- The real-time clock (RTC)

- 4 Kbytes of backup SRAM

- 20 backup registers


The real-time clock (RTC) is an independent BCD timer/counter. Dedicated registers contain
the second, minute, hour (in 12/24 hour), week day, date, month, year, in BCD (binarycoded decimal) format. Correction for 28, 29 (leap year), 30, and 31 day of the month are
performed automatically. The RTC provides a programmable alarm and programmable
periodic interrupts with wakeup from Stop and Standby modes. The sub-seconds value is
also available in binary format.


It is clocked by a 32.768 kHz external crystal, resonator or oscillator, the internal low-power
RC oscillator or the high-speed external clock divided by 2 to 31. The internal low-speed RC


DS8626 Rev 12 31/206



**Functional overview** **STM32F405xx, STM32F407xx**


has a typical frequency of 32 kHz. The RTC can be calibrated using an external 512 Hz
output to compensate for any natural quartz deviation.


Two alarm registers are used to generate an alarm at a specific time and calendar fields can
be independently masked for alarm comparison. To generate a periodic interrupt, a 16-bit
programmable binary auto-reload downcounter with programmable resolution is available
and allows automatic wakeup and periodic alarms from every 120 µs to every 36 hours.


A 20-bit prescaler is used for the time base clock. It is by default configured to generate a
time base of 1 second from a clock at 32.768 kHz.


The 4-Kbyte backup SRAM is an EEPROM-like memory area. It can be used to store data
which need to be retained in VBAT and standby mode. This memory area is disabled by
default to minimize power consumption (see _Section 3.19: Low-power modes_ ). It can be
enabled by software.


The backup registers are 32-bit registers used to store 80 bytes of user application data
when VDD power is not present. Backup registers are not reset by a system, a power reset,
or when the device wakes up from the Standby mode (see _Section 3.19: Low-power_
_modes_ ).


Additional 32-bit registers contain the programmable alarm subseconds, seconds, minutes,
hours, day, and date.


Like backup SRAM, the RTC and backup registers are supplied through a switch that is
powered either from the VDD supply when present or from the VBAT pin.

#### **3.19 Low-power modes**


The STM32F405xx and STM32F407xx support three low-power modes to achieve the best
compromise between low-power consumption, short startup time and available wakeup
sources:

- **Sleep mode**

In Sleep mode, only the CPU is stopped. All peripherals continue to operate and can
wake up the CPU when an interrupt/event occurs.

- **Stop mode**

The Stop mode achieves the lowest power consumption while retaining the contents of
SRAM and registers. All clocks in the V12 domain are stopped, the PLL, the HSI RC
and the HSE crystal oscillators are disabled. The voltage regulator can also be put
either in normal or in low-power mode.

The device can be woken up from the Stop mode by any of the EXTI line (the EXTI line
source can be one of the 16 external lines, the PVD output, the RTC alarm / wakeup /
tamper / time stamp events, the USB OTG FS/HS wakeup or the Ethernet wakeup).

- **Standby mode**

The Standby mode is used to achieve the lowest power consumption. The internal
voltage regulator is switched off so that the entire V12 domain is powered off. The PLL,
the HSI RC and the HSE crystal oscillators are also switched off. After entering


32/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**


Standby mode, the SRAM and register contents are lost except for registers in the
backup domain and the backup SRAM when selected.

The device exits the Standby mode when an external reset (NRST pin), an IWDG reset,
a rising edge on the WKUP pin, or an RTC alarm / wakeup / tamper /time stamp event
occurs.

The standby mode is not supported when the embedded voltage regulator is bypassed
and the V12 domain is controlled by an external power.

#### **3.20 VBAT operation**

The VBAT pin allows to power the device VBAT domain from an external battery, an external
supercapacitor, or from VDD when no external battery and an external supercapacitor are
present.


VBAT operation is activated when VDD is not present.

The VBAT pin supplies the RTC, the backup registers and the backup SRAM.

_Note:_ _When the microcontroller is supplied from VBAT, external interrupts and RTC alarm/events_
_do not exit it from VBAT operation._

_When PDR_ON pin is not connected to VDD (internal reset OFF), the VBAT functionality is no_
_more available and VBAT pin should be connected to VDD._

#### **3.21 Timers and watchdogs**


The STM32F405xx and STM32F407xx devices include two advanced-control timers, eight
general-purpose timers, two basic timers and two watchdog timers.


All timer counters can be frozen in debug mode.


_Table 4_ compares the features of the advanced-control, general-purpose and basic timers.


**Table 4. Timer feature comparison**


**Max**
**timer**
**clock**
**(MHz)**


**Capture/**
**compare**
**channels**


**Timer** **Counter** **Counter** **Prescaler**
**Timer**
**type** **resolution** **type** **factor**


**DMA**
**request**
**generation**


**Complemen-**
**tary output**


**Max**
**interface**
**clock**
**(MHz)**


Up,
Advanced TIM1,
16-bit Down,
-control TIM8
Up/down


Any integer
between 1 Yes 4 Yes 84 168
and 65536


DS8626 Rev 12 33/206



**Functional overview** **STM32F405xx, STM32F407xx**


**Table 4. Timer feature comparison (continued)**


**Max**
**timer**
**clock**
**(MHz)**


**Capture/**
**compare**
**channels**


**Timer** **Counter** **Counter** **Prescaler**
**Timer**
**type** **resolution** **type** **factor**


**DMA**
**request**
**generation**


**Complemen-**
**tary output**


**Max**
**interface**
**clock**
**(MHz)**


Up,
TIM2,
32-bit Down,
TIM5
Up/down


Up,
TIM3,
16-bit Down,
TIM4
Up/down


Any integer
between 1 Yes 4 No 42 84
and 65536


Any integer
between 1 Yes 4 No 42 84
and 65536


General
purpose


Any integer
TIM9 16-bit Up between 1 No 2 No 84 168
and 65536


TIM10 Any integer
, 16-bit Up between 1 No 1 No 84 168
TIM11 and 65536


Any integer
TIM12 16-bit Up between 1 No 2 No 42 84
and 65536


TIM13 Any integer
, 16-bit Up between 1 No 1 No 42 84
TIM14 and 65536


Any integer
TIM6,
Basic 16-bit Up between 1 Yes 0 No 42 84
TIM7
and 65536


**3.21.1** **Advanced-control timers (TIM1, TIM8)**


The advanced-control timers (TIM1, TIM8) can be seen as three-phase PWM generators
multiplexed on 6 channels. They have complementary PWM outputs with programmable
inserted dead times. They can also be considered as complete general-purpose timers.
Their 4 independent channels can be used for:

- Input capture

- Output compare

- PWM generation (edge- or center-aligned modes)

- One-pulse mode output


If configured as standard 16-bit timers, they have the same features as the general-purpose
TIMx timers. If configured as 16-bit PWM generators, they have full modulation capability (0100%).


The advanced-control timer can work together with the TIMx timers via the Timer Link
feature for synchronization or event chaining.


TIM1 and TIM8 support independent DMA request generation.


34/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**


**3.21.2** **General-purpose timers (TIMx)**


There are ten synchronizable general-purpose timers embedded in the STM32F40xxx
devices (see _Table 4_ for differences).

- **TIM2, TIM3, TIM4, TIM5**

The STM32F40xxx include 4 full-featured general-purpose timers: TIM2, TIM5, TIM3,
and TIM4.The TIM2 and TIM5 timers are based on a 32-bit auto-reload
up/downcounter and a 16-bit prescaler. The TIM3 and TIM4 timers are based on a 16bit auto-reload up/downcounter and a 16-bit prescaler. They all feature 4 independent
channels for input capture/output compare, PWM or one-pulse mode output. This gives
up to 16 input capture/output compare/PWMs on the largest packages.

The TIM2, TIM3, TIM4, TIM5 general-purpose timers can work together, or with the
other general-purpose timers and the advanced-control timers TIM1 and TIM8 via the
Timer Link feature for synchronization or event chaining.

Any of these general-purpose timers can be used to generate PWM outputs.

TIM2, TIM3, TIM4, TIM5 all have independent DMA request generation. They are
capable of handling quadrature (incremental) encoder signals and the digital outputs
from 1 to 4 hall-effect sensors.

- **TIM9, TIM10, TIM11, TIM12, TIM13, and TIM14**

These timers are based on a 16-bit auto-reload upcounter and a 16-bit prescaler.
TIM10, TIM11, TIM13, and TIM14 feature one independent channel, whereas TIM9
and TIM12 have two independent channels for input capture/output compare, PWM or
one-pulse mode output. They can be synchronized with the TIM2, TIM3, TIM4, TIM5
full-featured general-purpose timers. They can also be used as simple time bases.


**3.21.3** **Basic timers TIM6 and TIM7**


These timers are mainly used for DAC trigger and waveform generation. They can also be
used as a generic 16-bit time base.


TIM6 and TIM7 support independent DMA request generation.


**Independent watchdog**


The independent watchdog is based on a 12-bit downcounter and 8-bit prescaler. It is
clocked from an independent 32 kHz internal RC and as it operates independently from the
main clock, it can operate in Stop and Standby modes. It can be used either as a watchdog
to reset the device when a problem occurs, or as a free-running timer for application timeout
management. It is hardware- or software-configurable through the option bytes.


**Window watchdog**


The window watchdog is based on a 7-bit downcounter that can be set as free-running. It
can be used as a watchdog to reset the device when a problem occurs. It is clocked from
the main clock. It has an early warning interrupt capability and the counter can be frozen in
debug mode.


DS8626 Rev 12 35/206



**Functional overview** **STM32F405xx, STM32F407xx**


**SysTick timer**


This timer is dedicated to real-time operating systems, but could also be used as a standard
downcounter. It features:

- A 24-bit downcounter

- Autoreload capability

- Maskable system interrupt generation when the counter reaches 0

- Programmable clock source.

#### **3.22 Inter-integrated circuit interface (I²C)**


Up to three I²C bus interfaces can operate in multimaster and slave modes. They can
support the Standard-mode (up to 100 kHz) and Fast-mode (up to 400 kHz). They support
the 7/10-bit addressing mode and the 7-bit dual addressing mode (as slave). A hardware
CRC generation/verification is embedded.


They can be served by DMA and they support SMBus 2.0/PMBus.

#### **3.23 Universal synchronous/asynchronous receiver transmitters** **(USART)**


The STM32F405xx and STM32F407xx embed four universal synchronous/asynchronous
receiver transmitters (USART1, USART2, USART3 and USART6) and two universal
asynchronous receiver transmitters (UART4 and UART5).


These six interfaces provide asynchronous communication, IrDA SIR ENDEC support,
multiprocessor communication mode, single-wire half-duplex communication mode and
have LIN Master/Slave capability. The USART1 and USART6 interfaces are able to
communicate at speeds of up to 10.5 Mbit/s. The other available interfaces communicate at
up to 5.25 Mbit/s.


USART1, USART2, USART3 and USART6 also provide hardware management of the CTS
and RTS signals, Smart Card mode (ISO 7816 compliant) and SPI-like communication
capability. All interfaces can be served by the DMA controller.


36/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**


**Table 5. USART feature comparison**


**Max. baud rate**
**in Mbit/s**
**(oversampling**
**by 8)**


**Max. baud rate**
**in Mbit/s**
**(oversampling**
**by 16)**


**USART** **Standard**
**name** **features**


**Modem**
**SPI** **Smartcard**
**(RTS/** **LIN** **irDA**
**master** **(ISO 7816)**
**CTS)**


**APB**
**mapping**


APB2
USART1 X X X X X X 5.25 10.5 (max.
84 MHz)


APB1
USART2 X X X X X X 2.62 5.25 (max.
42 MHz)


APB1
USART3 X X X X X X 2.62 5.25 (max.
42 MHz)


APB1
UART4 X - X - X - 2.62 5.25 (max.
42 MHz)


APB1
UART5 X - X - X - 2.62 5.25 (max.
42 MHz)


APB2
USART6 X X X X X X 5.25 10.5 (max.
84 MHz)

#### **3.24 Serial peripheral interface (SPI)**


The STM32F40xxx feature up to three SPIs in slave and master modes in full-duplex and
simplex communication modes. SPI1 can communicate at up to 42 Mbits/s, SPI2 and SPI3
can communicate at up to 21 Mbit/s. The 3-bit prescaler gives 8 master mode frequencies
and the frame is configurable to 8 bits or 16 bits. The hardware CRC generation/verification
supports basic SD Card/MMC modes. All SPIs can be served by the DMA controller.


The SPI interface can be configured to operate in TI mode for communications in master
mode and slave mode.

#### **3.25 Inter-integrated sound (I [2] S)**

Two standard I [2] S interfaces (multiplexed with SPI2 and SPI3) are available. They can be
operated in master or slave mode, in full duplex and half-duplex communication modes, and
can be configured to operate with a 16-/32-bit resolution as an input or output channel.
Audio sampling frequencies from 8 kHz up to 192 kHz are supported. When either or both of
the I [2] S interfaces is/are configured in master mode, the master clock can be output to the
external DAC/CODEC at 256 times the sampling frequency.

All I [2] Sx can be served by the DMA controller.


DS8626 Rev 12 37/206



**Functional overview** **STM32F405xx, STM32F407xx**

#### **3.26 Audio PLL (PLLI2S)**

The devices feature an additional dedicated PLL for audio I [2] S application. It allows to
achieve error-free I [2] S sampling clock accuracy without compromising on the CPU
performance, while using USB peripherals.

The PLLI2S configuration can be modified to manage an I [2] S sample rate change without
disabling the main PLL (PLL) used for CPU, USB and Ethernet interfaces.


The audio PLL can be programmed with very low error to obtain sampling rates ranging
from 8 KHz to 192 KHz.

In addition to the audio PLL, a master clock input pin can be used to synchronize the I [2] S
flow with an external PLL (or Codec output).

#### **3.27 Secure digital input/output interface (SDIO)**


An SD/SDIO/MMC host interface is available, that supports MultiMediaCard System
Specification Version 4.2 in three different databus modes: 1-bit (default), 4-bit and 8-bit.


The interface allows data transfer at up to 48 MHz, and is compliant with the SD Memory
Card Specification Version 2.0.


The SDIO Card Specification Version 2.0 is also supported with two different databus
modes: 1-bit (default) and 4-bit.


The current version supports only one SD/SDIO/MMC4.2 card at any one time and a stack
of MMC4.1 or previous.


In addition to SD/SDIO/MMC, this interface is fully compliant with the CE-ATA digital
protocol Rev1.1.

#### **3.28 Ethernet MAC interface with dedicated DMA and IEEE 1588** **support**


Peripheral available only on the STM32F407xx devices.


The STM32F407xx devices provide an IEEE-802.3-2002-compliant media access controller
(MAC) for ethernet LAN communications through an industry-standard mediumindependent interface (MII) or a reduced medium-independent interface (RMII). The
STM32F407xx requires an external physical interface device (PHY) to connect to the
physical LAN bus (twisted-pair, fiber, etc.). the PHY is connected to the STM32F407xx MII
port using 17 signals for MII or 9 signals for RMII, and can be clocked using the 25 MHz
(MII) from the STM32F407xx.


38/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**


The STM32F407xx includes the following features:

- Supports 10 and 100 Mbit/s rates

- Dedicated DMA controller allowing high-speed transfers between the dedicated SRAM
and the descriptors (see the STM32F40xxx/41xxx reference manual for details)

- Tagged MAC frame support (VLAN support)

- Half-duplex (CSMA/CD) and full-duplex operation

- MAC control sublayer (control frames) support

- 32-bit CRC generation and removal

- Several address filtering modes for physical and multicast address (multicast and
group addresses)

- 32-bit status code for each transmitted or received frame

- Internal FIFOs to buffer transmit and receive frames. The transmit FIFO and the
receive FIFO are both 2 Kbytes.

- Supports hardware PTP (precision time protocol) in accordance with IEEE 1588 2008
(PTP V2) with the time stamp comparator connected to the TIM2 input

- Triggers interrupt when system time becomes greater than target time

#### **3.29 Controller area network (bxCAN)**


The two CANs are compliant with the 2.0A and B (active) specifications with a bitrate up to 1
Mbit/s. They can receive and transmit standard frames with 11-bit identifiers as well as
extended frames with 29-bit identifiers. Each CAN has three transmit mailboxes, two receive
FIFOS with 3 stages and 28 shared scalable filter banks (all of them can be used even if one
CAN is used). 256 bytes of SRAM are allocated for each CAN.

#### **3.30 Universal serial bus on-the-go full-speed (OTG_FS)**


The STM32F405xx and STM32F407xx embed an USB OTG full-speed device/host/OTG
peripheral with integrated transceivers. The USB OTG FS peripheral is compliant with the
USB 2.0 specification and with the OTG 1.0 specification. It has software-configurable
endpoint setting and supports suspend/resume. The USB OTG full-speed controller
requires a dedicated 48 MHz clock that is generated by a PLL connected to the HSE
oscillator. The major features are:

- Combined Rx and Tx FIFO size of 320 × 35 bits with dynamic FIFO sizing

- Supports the session request protocol (SRP) and host negotiation protocol (HNP)

- 4 bidirectional endpoints

- 8 host channels with periodic OUT support

- HNP/SNP/IP inside (no need for any external resistor)

- For OTG/Host modes, a power switch is needed in case bus-powered devices are
connected


DS8626 Rev 12 39/206



**Functional overview** **STM32F405xx, STM32F407xx**

#### **3.31 Universal serial bus on-the-go high-speed (OTG_HS)**


The STM32F405xx and STM32F407xx devices embed a USB OTG high-speed (up to
480 Mb/s) device/host/OTG peripheral. The USB OTG HS supports both full-speed and
high-speed operations. It integrates the transceivers for full-speed operation (12 MB/s) and
features a UTMI low-pin interface (ULPI) for high-speed operation (480 MB/s). When using
the USB OTG HS in HS mode, an external PHY device connected to the ULPI is required.


The USB OTG HS peripheral is compliant with the USB 2.0 specification and with the OTG
1.0 specification. It has software-configurable endpoint setting and supports
suspend/resume. The USB OTG full-speed controller requires a dedicated 48 MHz clock
that is generated by a PLL connected to the HSE oscillator.


The major features are:

- Combined Rx and Tx FIFO size of 1 Kbit × 35 with dynamic FIFO sizing

- Supports the session request protocol (SRP) and host negotiation protocol (HNP)

- 6 bidirectional endpoints

- 12 host channels with periodic OUT support

- Internal FS OTG PHY support

- External HS or HS OTG operation supporting ULPI in SDR mode. The OTG PHY is
connected to the microcontroller ULPI port through 12 signals. It can be clocked using
the 60 MHz output.

- Internal USB DMA

- HNP/SNP/IP inside (no need for any external resistor)

- for OTG/Host modes, a power switch is needed in case bus-powered devices are
connected

#### **3.32 Digital camera interface (DCMI)**


The camera interface is _not_ available in STM32F405xx devices.


STM32F407xx products embed a camera interface that can connect with camera modules
and CMOS sensors through an 8-bit to 14-bit parallel interface, to receive video data. The
camera interface can sustain a data transfer rate up to 54 Mbyte/s at 54 MHz. It features:

- Programmable polarity for the input pixel clock and synchronization signals

- Parallel data communication can be 8-, 10-, 12- or 14-bit

- Supports 8-bit progressive video monochrome or raw bayer format, YCbCr 4:2:2
progressive video, RGB 565 progressive video or compressed data (like JPEG)

- Supports continuous mode or snapshot (a single frame) mode

- Capability to automatically crop the image

#### **3.33 True random number generator (RNG)**


All STM32F405xx and STM32F407xx products embed a true random number generator
(RNG) that provides full entropy outputs to the application as 32-bit samples. It is composed
of a live entropy source (analog) and an internal conditioning component.


40/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Functional overview**

#### **3.34 General-purpose input/outputs (GPIOs)**


Each of the GPIO pins can be configured by software as output (push-pull or open-drain,
with or without pull-up or pull-down), as input (floating, with or without pull-up or pull-down)
or as peripheral alternate function. Most of the GPIO pins are shared with digital or analog
alternate functions. All GPIOs are high-current-capable and have speed selection to better
manage internal noise, power consumption and electromagnetic emission.


The I/O configuration can be locked if needed by following a specific sequence in order to
avoid spurious writing to the I/Os registers.


Fast I/O handling allowing maximum I/O toggling up to 84 MHz.

#### **3.35 Analog-to-digital converters (ADCs)**


Three 12-bit analog-to-digital converters are embedded and each ADC shares up to 16
external channels, performing conversions in the single-shot or scan mode. In scan mode,
automatic conversion is performed on a selected group of analog inputs.


Additional logic functions embedded in the ADC interface allow:

- Simultaneous sample and hold

- Interleaved sample and hold


The ADC can be served by the DMA controller. An analog watchdog feature allows very
precise monitoring of the converted voltage of one, some or all selected channels. An
interrupt is generated when the converted voltage is outside the programmed thresholds.


To synchronize A/D conversion and timers, the ADCs could be triggered by any of TIM1,
TIM2, TIM3, TIM4, TIM5, or TIM8 timer.

#### **3.36 Temperature sensor**


The temperature sensor has to generate a voltage that varies linearly with temperature. The
conversion range is between 1.8 V and 3.6 V. The temperature sensor is internally
connected to the ADC1_IN16 input channel which is used to convert the sensor output
voltage into a digital value.


As the offset of the temperature sensor varies from chip to chip due to process variation, the
internal temperature sensor is mainly suitable for applications that detect temperature
changes instead of absolute temperatures. If an accurate temperature reading is needed,
then an external temperature sensor part should be used.

#### **3.37 Digital-to-analog converter (DAC)**


The two 12-bit buffered DAC channels can be used to convert two digital signals into two
analog voltage signal outputs.


DS8626 Rev 12 41/206



**Functional overview** **STM32F405xx, STM32F407xx**


This dual digital Interface supports the following features:

- two DAC converters: one for each output channel

- 8-bit or 12-bit monotonic output

- left or right data alignment in 12-bit mode

- synchronized update capability

- noise-wave generation

- triangular-wave generation

- dual DAC channel independent or simultaneous conversions

- DMA capability for each channel

- external triggers for conversion

- input voltage reference VREF+

Eight DAC trigger inputs are used in the device. The DAC channels are triggered through
the timer update outputs that are also connected to different DMA streams.

#### **3.38 Serial wire JTAG debug port (SWJ-DP)**


The Arm SWJ-DP interface is embedded, and is a combined JTAG and serial wire debug
port that enables either a serial wire debug or a JTAG probe to be connected to the target.


Debug is performed using 2 pins only instead of 5 required by the JTAG (JTAG pins could
be re-use as GPIO with alternate function): the JTAG TMS and TCK pins are shared with
SWDIO and SWCLK, respectively, and a specific sequence on the TMS pin is used to
switch between JTAG-DP and SW-DP.

#### **3.39 Embedded Trace Macrocell™**


The Arm Embedded Trace Macrocell provides a greater visibility of the instruction and data
flow inside the CPU core by streaming compressed data at a very high rate from the
STM32F40xxx through a small number of ETM pins to an external hardware trace port
analyser (TPA) device. The TPA is connected to a host computer using USB, Ethernet, or
any other high-speed channel. Real-time instruction and data flow activity can be recorded
and then formatted for display on the host computer that runs the debugger software. TPA
hardware is commercially available from common development tool vendors.


The Embedded Trace Macrocell operates with third party debugger software tools.


42/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**

### **4 Pinouts and pin description**


**Figure 12. STM32F40xxx LQFP64 pinout**


VBAT

PC13

PC14
PC15

PH0
PH1

NRST
PC0
PC1
PC2
PC3
VSSA
VDDA
PA0_WKUP
PA1
PA2


2

4

6

8

10

12

14

16


64 63 62 61 60 59 58 57 56 55 54 53 52 51 50 49
48

46

44

42

LQFP64 40


38

36

34

33
17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32


LQFP64


VDD
VCAP_2
PA13
PA12
PA11
PA10
PA9
PA8
PC9
PC8
PC7
PC6
PB15
PB14
PB13
PB12


ai18493b


1. The above figure shows the package top view.


DS8626 Rev 12 43/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Figure 13. STM32F40xxx LQFP100 pinout**


PE2
PE3
PE4
PE5
PE6
VBAT

PC13

PC14
PC15
VSS
VDD
PH0

PH1

NRST
PC0
PC1
PC2
PC3
VDD
VSSA
VREF+
VDDA
PA0
PA1
PA2


~~1~~
~~2~~
~~3~~
~~4~~
~~5~~
~~6~~
~~7~~
~~8~~
~~9~~
~~1~~ 0
~~1~~ 1
~~1~~ 2
~~1~~ 3
~~1~~ 4
~~1~~ 5
~~1~~ 6
~~1~~ 7
~~1~~ 8
~~1~~ 9
~~2~~ 0
21
22
~~2~~ 3
~~2~~ 4
~~2~~ 5


VDD
VSS
VCAP_2
PA13
PA12
PA 11
PA10
PA9
PA8
PC9
PC8
PC7
PC6
PD15
PD14
PD13
PD12
PD11
PD10
PD9
PD8
PB15
PB14
PB13
PB12


ai18495c


LQFP100


7 ~~5~~
7 ~~4~~
7 ~~3~~
7 ~~2~~
71
7 ~~0~~
6 ~~9~~
6 ~~8~~
6 ~~7~~
6 ~~6~~
6 ~~5~~
6 ~~4~~
6 ~~3~~
6 ~~2~~
6 ~~1~~
6 ~~0~~
5 ~~9~~
5 ~~8~~
5 ~~7~~
5 ~~6~~
5 ~~5~~
5 ~~4~~
5 ~~3~~
5 ~~2~~
5 ~~1~~


1. The above figure shows the package top view.


44/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Figure 14. STM32F40xxx LQFP144 pinout**


PE2 ~~1~~ 10 ~~8~~ VDD
PE3 ~~2~~ 10 ~~7~~ VSS
PE4 ~~3~~ 10 ~~6~~ V
PE5 ~~4~~ 10 ~~5~~ PA13
PE6 ~~5~~ 104 PA12
VBAT ~~6~~ 103 PA11
PC13 ~~7~~ 102 PA10
PC14 ~~8~~ 10 ~~1~~ PA9
PC15 ~~9~~ 10 ~~0~~ PA8
PF0 ~~1~~ 0 9 ~~9~~ PC9
PF1 ~~1~~ 1 9 ~~8~~ PC8
PF2 ~~1~~ 2 9 ~~7~~ PC7
PF3 ~~1~~ 3 9 ~~6~~ PC6
PF4 ~~1~~ 4 9 ~~5~~ VDD
PF5 ~~1~~ 5 9 ~~4~~ VSS
VSS ~~1~~ 6 9 ~~3~~ PG8
VDD ~~1~~ 7 9 ~~2~~ PG7
PF6 ~~1~~ 8 9 ~~1~~ PG6
PF7 ~~1~~ 9 LQFP144 9 ~~0~~ PG5
PF8 ~~2~~ 0 8 ~~9~~ PG4
PF9 21 8 ~~8~~ PG3
PF10 22 8 ~~7~~ PG2
PH0 ~~2~~ 3 8 ~~6~~ PD15
PH1 ~~2~~ 4 8 ~~5~~ PD14
NRST ~~2~~ 5 8 ~~4~~ VDD
PC0 26 83 VSS
PC1 27 82 PD13
PC2 28 81 PD12
PC3 29 80 PD11

VDD 30 79 PD10
VSSA 31 78 PD9
VREF+ 32 77 PD8
VDDA 33 76 PB15
PA0 34 75 PB14
PA1 35 74 PB13
PA2 36 73 PB12


~~1~~
~~2~~
~~3~~
~~4~~
~~5~~
~~6~~
~~7~~
~~8~~
~~9~~
~~1~~ 0
~~1~~ 1
~~1~~ 2
~~1~~ 3
~~1~~ 4
~~1~~ 5
~~1~~ 6
~~1~~ 7
~~1~~ 8
~~1~~ 9
~~2~~ 0
21
22
~~2~~ 3
~~2~~ 4
~~2~~ 5

26
27
28
29
30
31
32
33
34
35
36


83
82
81
80
79
78
77
76
75
74
73


VCAP_2


LQFP144


10 ~~8~~
10 ~~7~~
10 ~~6~~
10 ~~5~~
104
103
102
10 ~~1~~
10 ~~0~~
9 ~~9~~
9 ~~8~~
9 ~~7~~
9 ~~6~~
9 ~~5~~
9 ~~4~~
9 ~~3~~
9 ~~2~~
9 ~~1~~
9 ~~0~~
8 ~~9~~
8 ~~8~~
8 ~~7~~
8 ~~6~~
8 ~~5~~
8 ~~4~~


1. The above figure shows the package top view.


ai18496b


DS8626 Rev 12 45/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Figure 15. STM32F40xxx LQFP176 pinout**


PE2
PE3
PE4
PE5

PE6

VBAT

PI8

PC13

PC14

PC15

PI9
PI10
PI11
VSS


PI1
PI0
PH15
PH14
PH13

VDD
VSS
VCAP_2

PA13

PA12

PA11

PA10

PA9

PA8


VDD


DD 118 PC9

PF0 16 117 PC8

PF1 17 116 PC7

PF2 18 115 PC6

PF3 19 114 VDD

PF4 20 113 VSS
PF5 21 112 PG8

VSS 22 LQFP176 111 PG7


VDD
VSS


132
131
130
129
128
127
126
125
124
123
122
121
120
119
118
117
116
115
114
113
112
111
110
109
108


107
106
105
104
103V
102V
101
100
99
98


VSS
VDD


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25

26
27
28
29
30
31
32
33
34
35
36


LQFP176


DD 110 PG6

PF6 24 109 PG5

PF7 25 108 PG4

PF8 26 107 PG3

PF9 27


106 PG2

PF10 28


105 PD15

PH0 29 104 PD14

PH1 30


103V

NRST 31


102V

PC0 32


VDD
VSS


101 PD13

PC1 33 100 PD12

PC2 34 99 PD11

PC3 35 98 PD10

VDD 36 PD9


VDD
VSSA


SSA 96 PD8

VREF+ 38 PB15


PH12


MS19916V4


VDDA


DDA 94 PB14

PA0 40 93 PB13

PA1 41 92 PB12

PA2 42


PH2
PH3


97
37

38

39

40

41

42

43

44


96
95
94
93
92
91
90


VDD
VSS


1. The above figure shows the package top view.


46/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Figure 16. STM32F40xxx UFBGA176 ballout**


1 2 **3** 4 5 6 7 8 9 10 11 12 13 14 15


A PE3 PE2 PE1 PE0 PB8 PB5 PG14 PG13 PB4 PB3 PD7 PC12 PA15 PA14 PA13


B PE4 PE5 PE6 PB9 PB7 PB6 PG15 PG12 PG11 PG10 PD6 PD0 PC11 PC10 PA12


C VBAT PI7 PI6 PI5 VDD PDR_ON VDD VDD VDD PG9 PD5 PD1 PI3 PI2 PA11


D PC13 PI8 PI9 PI4 VSS BOOT0 VSS VSS VSS PD4 PD3 PD2 PH15 PI1 PA10


E PC14 PF0 PI10 PI11 PH13 PH14 PI0 PA9


F PC15 VSS VDD PH2 VSS VSS VSS VSS VSS VSS VCAP_2 PC9 PA8


G PH0 VSS VDD PH3 VSS VSS VSS VSS VSS VSS VDD PC8 PC7


H PH1 PF2 PF1 PH4 VSS VSS VSS VSS VSS VSS VDD PG8 PC6


J NRST PF3 PF4 PH5 VSS VSS VSS VSS VSS VDD VDD PG7 PG6


K PF7 PF6 PF5 VDD VSS VSS VSS VSS VSS PH12 PG5 PG4 PG3


L PF10 PF9 PF8 BYPASS_ PH11 PH10 PD15 PG2
REG


M VSSA PC0 PC1 PC2 PC3 PB2 PG1 VSS VSS VCAP_1 PH6 PH8 PH9 PD14 PD13


N VREF- PA1 PA0 PA4 PC4 PF13 PG0 VDD VDD VDD PE13 PH7 PD12 PD11 PD10


P VREF+ PA2 PA6 PA5 PC5 PF12 PF15 PE8 PE9 PE11 PE14 PB12 PB13 PD9 PD8


R VDDA PA3 PA7 PB1 PB0 PF11 PF14 PE7 PE10 PE12 PE15 PB10 PB11 PB14 PB15


ai18497b


1. This figure shows the package top view.


DS8626 Rev 12 47/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Figure 17. STM32F40xxx WLCSP90 ballout**


10 9 8 7 6 5 4 3 2



VDD


A VBAT PC13 PDR_ON BOOT0 PB4 PD7 PD4 PC12


PA14


PC14 PC15 VDD PB7 PB3 PD6 PD2 PA15 PI1 VCAP_2


B PC15 VDD PB7 PB3 PD6 PD2 PA15


PI1


C PA0 VSS PB9 PB6 PD5 PD1 PC11 PI0


PA12


PA11


BYPASS_
REG


D PC2 PB8 PB5 PD0 PC10 PA13


PB5 PD0 PC10 PA13 PA10 PA9 PA8


PA10 PA9


E PC0 PC3 VSS


VSS VDD VSS VDD PC9 PC8 PC7


PC0 PC3 VSS VSS VDD VSS VDD PC9 PC8


F PH0 PH1 PA1


VDD PE10 PE14 VCAP_1 PC6 PD14 PD15


G NRST


H VSSA


VDDA PA5 PB0 PE7


PE13 PE15 PD10 PD12 PD11


PA3 PA6 PB1 PE8 PE12 PB10 PD9 PD8 PB15


PE8 PE12


PD9 PD8


J PA2 PA4 PA7 PB2 PE9 PE11 PB11 PB12 PB14


PB13


MS30402V1


1. This figure shows the package bump view.


**Table 6. Legend/abbreviations used in the pinout table**


**Name** **Abbreviation** **Definition**


Unless otherwise specified in brackets below the pin name, the pin function during and after
Pin name
reset is the same as the actual pin name


S Supply pin


Pin type


I/O structure


I Input only pin


I/O Input / output pin


FT 5 V tolerant I/O


TTa 3.3 V tolerant I/O directly connected to ADC


B Dedicated BOOT0 pin


RST Bidirectional reset pin with embedded weak pull-up resistor


Notes Unless otherwise specified by a note, all I/Os are set as floating inputs during and after reset


Alternate
Functions selected through GPIOx_AFR registers
functions


Additional
Functions directly selected/enabled through peripheral registers
functions


48/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


**Additional**
**Alternate functions**
**functions**


TRACECLK/ FSMC_A23 /

- - 1 1 A2 1 PE2 I/O FT - ETH_MII_TXD3 / EVENTOUT


TRACED0/FSMC_A19 /

- - 2 2 A1 2 PE3 I/O FT - EVENTOUT


TRACED1/FSMC_A20 /

- - 3 3 B1 3 PE4 I/O FT - DCMI_D4/ EVENTOUT


TRACED2 / FSMC_A21 /

- - 4 4 B2 4 PE5 I/O FT - TIM9_CH1 / DCMI_D6 / EVENTOUT


TRACED3 / FSMC_A22 /

- - 5 5 B3 5 PE6 I/O FT - TIM9_CH2 / DCMI_D7 / EVENTOUT


1 A10 6 6 C1 6 VBAT S - - - 
(3)( RTC_TAMP1,

- - - - D2 7 PI8 I/O FT 4) - RTC_TAMP2,

RTC_TS


(3) RTC_OUT,
2 A9 7 7 D1 8 PC13 I/O FT (4) - RTC_TAMP1,

RTC_TS


PC14/OSC32_IN (3)(
3 B10 8 8 E1 9 (PC14) I/O FT 4) - OSC32_IN [(5)]


PC15/ (3)(
4 B9 9 9 F1 10 OSC32_OUT I/O FT 4) - OSC32_OUT [(5)]
(PC15)


- - - - D3 11 PI9 I/O FT - CAN1_RX / EVENTOUT 

ETH_MII_RX_ER /

- - - - E3 12 PI10 I/O FT - EVENTOUT


OTG_HS_ULPI_DIR /

- - - - E4 13 PI11 I/O FT - EVENTOUT


- - - - F2 14 VSS S - - - 
- - - - F3 15 VDD S - - - 

FSMC_A0 / I2C2_SDA /

- - - 10 E2 16 PF0 I/O FT - EVENTOUT


DS8626 Rev 12 49/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


**Additional**
**Alternate functions**
**functions**


FSMC_A1 / I2C2_SCL /

- - - 11 H3 17 PF1 I/O FT - EVENTOUT


FSMC_A2 / I2C2_SMBA /

- - - 12 H2 18 PF2 I/O FT - EVENTOUT

- - - 13 J2 19 PF3 I/O FT (5) FSMC_A3/EVENTOUT ADC3_IN9

- - - 14 J3 20 PF4 I/O FT (5) FSMC_A4/EVENTOUT ADC3_IN14

- - - 15 K3 21 PF5 I/O FT (5) FSMC_A5/EVENTOUT ADC3_IN15


- C9 10 16 G2 22 VSS S - - - 
- B8 11 17 G3 23 VDD S - - - 

TIM10_CH1 /

- - - 18 K2 24 PF6 I/O FT (5) FSMC_NIORD/ ADC3_IN4
EVENTOUT

- - - 19 K1 25 PF7 I/O FT (5) TIM11_CH1/FSMC_NREG/ ADC3_IN5
EVENTOUT


TIM13_CH1 /

- - - 20 L3 26 PF8 I/O FT (5) FSMC_NIOWR/ ADC3_IN6
EVENTOUT

- - - 21 L2 27 PF9 I/O FT (5) TIM14_CH1 / FSMC_CD/ ADC3_IN7
EVENTOUT

- - - 22 L1 28 PF10 I/O FT (5) FSMC_INTR/ EVENTOUT ADC3_IN8


PH0/OSC_IN
5 F10 12 23 G1 29 I/O FT - EVENTOUT OSC_IN [(5)]
(PH0)


PH1/OSC_OUT
6 F9 13 24 H1 30 I/O FT - EVENTOUT OSC_OUT [(5)]
(PH1)


7 G10 14 25 J1 31 NRST I/O RST - - 
8 E10 15 26 M2 32 PC0 I/O FT (5) OTG_HS_ULPI_STP/ ADC123_IN10
EVENTOUT

9 - 16 27 M3 33 PC1 I/O FT (5) ETH_MDC/ EVENTOUT ADC123_IN11


SPI2_MISO /
10 D10 17 28 M4 34 PC2 I/O FT (5) OTG_HS_ULPI_DIR /
ETH_MII_TXD2
/I2S2ext_SD/ EVENTOUT


50/206 DS8626 Rev 12


ADC123_IN12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


**Additional**
**Alternate functions**
**functions**


SPI2_MOSI / I2S2_SD /
11 E9 18 29 M5 35 PC3 I/O FT (5) OTG_HS_ULPI_NXT /
ETH_MII_TX_CLK **/**
EVENTOUT


ADC123_IN13


 -  - 19 30  - 36 VDD S  -  -  -  
12 H10 20 31 M1 37 VSSA S - - - 
 -  -  -  - N1  - VREF– S  -  -  -  
 -  - 21 32 P1 38 VREF+ S  -  -  -  
13 G9 22 33 R1 39 VDDA S - - - 


14 C10 23 34 N3 40 PA0/WKUP I/O FT (6)
(PA0)


15 F8 24 35 N2 41 PA1 I/O FT (5)


USART2_CTS/
UART4_TX/
ETH_MII_CRS /
TIM2_CH1_ETR/
TIM5_CH1 / TIM8_ETR/
EVENTOUT


USART2_RTS /
UART4_RX/
ETH_RMII_REF_CLK /
ETH_MII_RX_CLK /
TIM5_CH2 / TIM2_CH2/
EVENTOUT


ADC123_IN0/WK
UP [(5)]


ADC123_IN1


USART2_TX/TIM5_CH3 /
16 J10 25 36 P2 42 PA2 I/O FT (5) TIM9_CH1 / TIM2_CH3 / ADC123_IN2
ETH_MDIO/ EVENTOUT


 -  -  -  - F4 43 PH2 I/O FT  - ETH_MII_CRS/EVENTOUT  

 -  -  -  - G4 44 PH3 I/O FT  - ETH_MII_COL/EVENTOUT  

I2C2_SCL /

 -  -  -  - H4 45 PH4 I/O FT  - OTG_HS_ULPI_NXT/  EVENTOUT


 -  -  -  - J4 46 PH5 I/O FT  - I2C2_SDA/ EVENTOUT  


17 H9 26 37 R2 47 PA3 I/O FT (5)


USART2_RX/TIM5_CH4 /
TIM9_CH2 / TIM2_CH4 /
OTG_HS_ULPI_D0 /
ETH_MII_COL/
EVENTOUT


ADC123_IN3


18 E5 27 38 - - VSS S - - - 

DS8626 Rev 12 51/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


**Additional**
**Alternate functions**
**functions**


 - D9  -  - L4 48 BYPASS_REG I FT  -  -  

19 E4 28 39 K4 49 VDD S - - - 


20 J9 29 40 N4 50 PA4 I/O TTa (5)


SPI1_NSS / SPI3_NSS /
USART2_CK /
DCMI_HSYNC /
OTG_HS_SOF/ I2S3_WS/
EVENTOUT


SPI1_SCK/
21 G8 30 41 P4 51 PA5 I/O TTa (5) OTG_HS_ULPI_CK /
TIM2_CH1_ETR/
TIM8_CH1N/ EVENTOUT


SPI1_MISO /
22 H8 31 42 P3 52 PA6 I/O FT (5) TIM8_BKIN/TIM13_CH1 /
DCMI_PIXCLK / TIM3_CH1
/ TIM1_BKIN **/** EVENTOUT


ADC12_IN4
/DAC_OUT1


ADC12_IN5/DAC
_OUT2


ADC12_IN6


ADC12_IN7


23 J8 32 43 R3 53 PA7 I/O FT (5)


SPI1_MOSI/ TIM8_CH1N /
TIM14_CH1/TIM3_CH2/
ETH_MII_RX_DV /
TIM1_CH1N /
ETH_RMII_CRS_DV/
EVENTOUT


ETH_RMII_RX_D0 /
24 - 33 44 N5 54 PC4 I/O FT (5) ETH_MII_RX_D0/ ADC12_IN14
EVENTOUT


ETH_RMII_RX_D1 /
25 - 34 45 P5 55 PC5 I/O FT (5) ETH_MII_RX_D1/ ADC12_IN15
EVENTOUT


TIM3_CH3 / TIM8_CH2N/
26 G7 35 46 R5 56 PB0 I/O FT (5) OTG_HS_ULPI_D1/
ETH_MII_RXD2 /
TIM1_CH2N/ EVENTOUT


TIM3_CH4 / TIM8_CH3N/
27 H7 36 47 R4 57 PB1 I/O FT (5) OTG_HS_ULPI_D2/
ETH_MII_RXD3 /
TIM1_CH3N/ EVENTOUT


ADC12_IN8


ADC12_IN9


PB2/BOOT1
28 J7 37 48 M6 58 I/O FT - EVENTOUT (PB2)


52/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


**Additional**
**Alternate functions**
**functions**


- - - 49 R6 59 PF11 I/O FT - DCMI_D12/ EVENTOUT 

- - - 50 P6 60 PF12 I/O FT - FSMC_A6/ EVENTOUT 

- - - 51 M8 61 VSS S - - - 
- - - 52 N8 62 VDD S - - - 

- - - 53 N6 63 PF13 I/O FT - FSMC_A7/ EVENTOUT 

- - - 54 R7 64 PF14 I/O FT - FSMC_A8/ EVENTOUT 

- - - 55 P7 65 PF15 I/O FT - FSMC_A9/ EVENTOUT 

- - - 56 N7 66 PG0 I/O FT - FSMC_A10/ EVENTOUT 

- - - 57 M7 67 PG1 I/O FT - FSMC_A11/ EVENTOUT 

FSMC_D4/TIM1_ETR/

- G6 38 58 R8 68 PE7 I/O FT - EVENTOUT


FSMC_D5/ TIM1_CH1N/

- H6 39 59 P8 69 PE8 I/O FT - EVENTOUT


FSMC_D6/TIM1_CH1/

- J6 40 60 P9 70 PE9 I/O FT - EVENTOUT


- - - 61 M9 71 VSS S - - - 
- - - 62 N9 72 VDD S - - - 

FSMC_D7/TIM1_CH2N/

- F6 41 63 R9 73 PE10 I/O FT - EVENTOUT


FSMC_D8/TIM1_CH2/

- J5 42 64 P10 74 PE11 I/O FT - EVENTOUT


FSMC_D9/TIM1_CH3N/

- H5 43 65 R10 75 PE12 I/O FT - EVENTOUT


FSMC_D10/TIM1_CH3/

- G5 44 66 N11 76 PE13 I/O FT - EVENTOUT


FSMC_D11/TIM1_CH4/

- F5 45 67 P11 77 PE14 I/O FT - EVENTOUT


FSMC_D12/TIM1_BKIN/

- G4 46 68 R11 78 PE15 I/O FT - EVENTOUT


DS8626 Rev 12 53/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


29 H4 47 69 R12 79 PB10 I/O FT 

30 J4 48 70 R13 80 PB11 I/O FT 


SPI2_SCK / I2S2_CK /
I2C2_SCL/ USART3_TX /
OTG_HS_ULPI_D3 /
ETH_MII_RX_ER /
TIM2_CH3/ EVENTOUT


I2C2_SDA/USART3_RX/
OTG_HS_ULPI_D4 /
ETH_RMII_TX_EN/
ETH_MII_TX_EN /
TIM2_CH4/ EVENTOUT


**Additional**
**Alternate functions**
**functions**


31 F4 49 71 M10 81 VCAP_1 S - - - 
32 - 50 72 N10 82 VDD S - - - 

I2C2_SMBA / TIM12_CH1 /

 -  -  -  - M11 83 PH6 I/O FT  - ETH_MII_RXD2/  EVENTOUT


I2C3_SCL /

 -  -  -  - N12 84 PH7 I/O FT  - ETH_MII_RXD3/  EVENTOUT


I2C3_SDA /

 -  -  -  - M12 85 PH8 I/O FT  - DCMI_HSYNC/  EVENTOUT


I2C3_SMBA / TIM12_CH2/

 -  -  -  - M13 86 PH9 I/O FT  -  DCMI_D0/ EVENTOUT


TIM5_CH1 / DCMI_D1/

 -  -  -  - L13 87 PH10 I/O FT  -  EVENTOUT


TIM5_CH2 / DCMI_D2/

 -  -  -  - L12 88 PH11 I/O FT  -  EVENTOUT


TIM5_CH3 / DCMI_D3/

 -  -  -  - K12 89 PH12 I/O FT  -  EVENTOUT


 -  -  -  - H12 90 VSS S  -  -  -  
 -  -  -  - J12 91 VDD S  -  -  -  

54/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


33 J3 51 73 P12 92 PB12 I/O FT 

34 J1 52 74 P13 93 PB13 I/O FT 

35 J2 53 75 R14 94 PB14 I/O FT 

36 H1 54 76 R15 95 PB15 I/O FT 


SPI2_NSS / I2S2_WS /
I2C2_SMBA/
USART3_CK/ TIM1_BKIN /
CAN2_RX /
OTG_HS_ULPI_D5/
ETH_RMII_TXD0 /
ETH_MII_TXD0/
OTG_HS_ID/ EVENTOUT


SPI2_SCK / I2S2_CK /
USART3_CTS/
TIM1_CH1N /CAN2_TX /
OTG_HS_ULPI_D6 /
ETH_RMII_TXD1 /
ETH_MII_TXD1/
EVENTOUT


SPI2_MISO/ TIM1_CH2N /
TIM12_CH1 /
OTG_HS_DM/
USART3_RTS /
TIM8_CH2N/I2S2ext_SD/
EVENTOUT


SPI2_MOSI / I2S2_SD/
TIM1_CH3N / TIM8_CH3N
/ TIM12_CH2 /
OTG_HS_DP/ EVENTOUT


      

OTG_HS_VBUS


      

RTC_REFIN


**Additional**
**Alternate functions**
**functions**


FSMC_D13 / USART3_TX/

- H2 55 77 P15 96 PD8 I/O FT - EVENTOUT


FSMC_D14 / USART3_RX/

- H3 56 78 P14 97 PD9 I/O FT - EVENTOUT


FSMC_D15 / USART3_CK/

- G3 57 79 N15 98 PD10 I/O FT - EVENTOUT


FSMC_CLE /

- G1 58 80 N14 99 PD11 I/O FT - FSMC_A16/USART3_CTS/ EVENTOUT


- G2 59 81 N13 100 PD12 I/O FT 


FSMC_ALE/
FSMC_A17/TIM4_CH1 /
USART3_RTS/
EVENTOUT


DS8626 Rev 12 55/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


**Additional**
**Alternate functions**
**functions**


FSMC_A18/TIM4_CH2/

- - 60 82 M15 101 PD13 I/O FT - EVENTOUT


- - - 83 - 102 VSS S - - - 
- - - 84 J13 103 VDD S - - - 

FSMC_D0/TIM4_CH3/

- F2 61 85 M14 104 PD14 I/O FT - EVENTOUT/ EVENTOUT


FSMC_D1/TIM4_CH4/

- F1 62 86 L14 105 PD15 I/O FT - EVENTOUT


- - - 87 L15 106 PG2 I/O FT - FSMC_A12/ EVENTOUT 

- - - 88 K15 107 PG3 I/O FT - FSMC_A13/ EVENTOUT 

- - - 89 K14 108 PG4 I/O FT - FSMC_A14/ EVENTOUT 

- - - 90 K13 109 PG5 I/O FT - FSMC_A15/ EVENTOUT 

- - - 91 J15 110 PG6 I/O FT - FSMC_INT2/ EVENTOUT 

FSMC_INT3 /USART6_CK/

- - - 92 J14 111 PG7 I/O FT - EVENTOUT


USART6_RTS /

- - - 93 H14 112 PG8 I/O FT - ETH_PPS_OUT/ EVENTOUT


- - - 94 G12 113 VSS S - - 
- - - 95 H13 114 VDD S - - 


37 F3 63 96 H15 115 PC6 I/O FT 

38 E1 64 97 G15 116 PC7 I/O FT 


I2S2_MCK /
TIM8_CH1/SDIO_D6 /
USART6_TX /
DCMI_D0/TIM3_CH1/
EVENTOUT


I2S3_MCK /
TIM8_CH2/SDIO_D7 /
USART6_RX /
DCMI_D1/TIM3_CH2/
EVENTOUT


TIM8_CH3/SDIO_D0
39 E2 65 98 G14 117 PC8 I/O FT - /TIM3_CH3/ USART6_CK / DCMI_D2/ EVENTOUT


56/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


40 E3 66 99 F14 118 PC9 I/O FT 

41 D1 67 100 F15 119 PA8 I/O FT 


I2S_CKIN/ MCO2 /
TIM8_CH4/SDIO_D1 /
/I2C3_SDA / DCMI_D3 /
TIM3_CH4/ EVENTOUT


MCO1 / USART1_CK/
TIM1_CH1/ I2C3_SCL/
OTG_FS_SOF/
EVENTOUT


**Additional**
**Alternate functions**
**functions**


USART1_TX/ TIM1_CH2 /
42 D2 68 101 E15 120 PA9 I/O FT - I2C3_SMBA / DCMI_D0/ OTG_FS_VBUS
EVENTOUT


USART1_RX/ TIM1_CH3/
43 D3 69 102 D15 121 PA10 I/O FT - OTG_FS_ID/DCMI_D1/ EVENTOUT


USART1_CTS / CAN1_RX
44 C1 70 103 C15 122 PA11 I/O FT - / TIM1_CH4 / OTG_FS_DM/ EVENTOUT


USART1_RTS / CAN1_TX/
45 C2 71 104 B15 123 PA12 I/O FT - TIM1_ETR/ OTG_FS_DP/ EVENTOUT


PA13
46 D4 72 105 A15 124 I/O FT - JTMS-SWDIO/ EVENTOUT (JTMS-SWDIO)


47 B1 73 106 F13 125 VCAP_2 S - - - 
 - E7 74 107 F12 126 VSS S  -  -  -  
48 E6 75 108 G13 127 VDD S - - - 

TIM8_CH1N / CAN1_TX/

 -  -  -  - E12 128 PH13 I/O FT  -  EVENTOUT


TIM8_CH2N / DCMI_D4/

 -  -  -  - E13 129 PH14 I/O FT  -  EVENTOUT


TIM8_CH3N / DCMI_D11/

 -  -  -  - D13 130 PH15 I/O FT  -  EVENTOUT


TIM5_CH4 / SPI2_NSS /

 - C3  -  - E14 131 PI0 I/O FT  - I2S2_WS / DCMI_D13/  EVENTOUT


SPI2_SCK / I2S2_CK /

 - B2  -  - D14 132 PI1 I/O FT  -  DCMI_D8/ EVENTOUT


DS8626 Rev 12 57/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


**Additional**
**Alternate functions**
**functions**


TIM8_CH4 /SPI2_MISO /

 -  -  -  - C14 133 PI2 I/O FT  - DCMI_D9 / I2S2ext_SD/  EVENTOUT


TIM8_ETR / SPI2_MOSI /

 -  -  -  - C13 134 PI3 I/O FT  - I2S2_SD / DCMI_D10/  EVENTOUT


 -  -  -  - D9 135 VSS S  -  -  -  
 -  -  -  - C9 136 VDD S  -  -  -  

PA14
49 A2 76 109 A14 137 I/O FT - JTCK-SWCLK/ EVENTOUT (JTCK/SWCLK)


JTDI/ SPI3_NSS/
PA15
50 B3 77 110 A13 138 I/O FT - I2S3_WS/TIM2_CH1_ETR (JTDI)
/ SPI1_NSS / EVENTOUT


51 D5 78 111 B14 139 PC10 I/O FT 

52 C4 79 112 B13 140 PC11 I/O FT 

53 A3 80 113 A12 141 PC12 I/O FT 


SPI3_SCK / I2S3_CK/
UART4_TX/SDIO_D2 /
DCMI_D8 / USART3_TX/
EVENTOUT


UART4_RX/ SPI3_MISO /
SDIO_D3 /
DCMI_D4/USART3_RX /
I2S3ext_SD/ EVENTOUT


UART5_TX/SDIO_CK /
DCMI_D9 / SPI3_MOSI
/I2S3_SD / USART3_CK/
EVENTOUT


FSMC_D2/CAN1_RX/

 - D6 81 114 B12 142 PD0 I/O FT  -  EVENTOUT


FSMC_D3 / CAN1_TX/

 - C5 82 115 C12 143 PD1 I/O FT  -  EVENTOUT


TIM3_ETR/UART5_RX/
54 B4 83 116 D12 144 PD2 I/O FT - SDIO_CMD / DCMI_D11/ EVENTOUT


FSMC_CLK/

 -  - 84 117 D11 145 PD3 I/O FT  - USART2_CTS/  EVENTOUT


58/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


**Additional**
**Alternate functions**
**functions**


FSMC_NOE/

- A4 85 118 D10 146 PD4 I/O FT - USART2_RTS/ EVENTOUT


FSMC_NWE/USART2_TX/

- C6 86 119 C11 147 PD5 I/O FT - EVENTOUT


- - - 120 D8 148 VSS S - - - 
- - - 121 C8 149 VDD S - - - 

FSMC_NWAIT/

- B5 87 122 B11 150 PD6 I/O FT - USART2_RX/ EVENTOUT


USART2_CK/FSMC_NE1/

- A5 88 123 A11 151 PD7 I/O FT - FSMC_NCE2/ EVENTOUT


USART6_RX /

- - - 124 C10 152 PG9 I/O FT - FSMC_NE2/FSMC_NCE3/ EVENTOUT


FSMC_NCE4_1/

- - - 125 B10 153 PG10 I/O FT - FSMC_NE3/ EVENTOUT


- - - 126 B9 154 PG11 I/O FT 


FSMC_NCE4_2 /
ETH_MII_TX_EN/
ETH _RMII_TX_EN/
EVENTOUT


FSMC_NE4 /

- - - 127 B8 155 PG12 I/O FT - USART6_RTS/ EVENTOUT


- - - 128 A8 156 PG13 I/O FT 

- - - 129 A7 157 PG14 I/O FT 


FSMC_A24 /
USART6_CTS
/ETH_MII_TXD0/
ETH_RMII_TXD0/
EVENTOUT


FSMC_A25 / USART6_TX
/ETH_MII_TXD1/
ETH_RMII_TXD1/
EVENTOUT


- E8 - 130 D7 158 VSS S - - - 
- F7 - 131 C7 159 VDD S - - - 

USART6_CTS /

- - - 132 B7 160 PG15 I/O FT - DCMI_D13/ EVENTOUT


DS8626 Rev 12 59/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


PB3
55 B6 89 133 A10 161 (JTDO/ I/O FT TRACESWO)


JTDO/ TRACESWO/
SPI3_SCK / I2S3_CK /
TIM2_CH2 / SPI1_SCK/
EVENTOUT


**Additional**
**Alternate functions**
**functions**


NJTRST/ SPI3_MISO /
PB4
56 A6 90 134 A9 162 I/O FT - TIM3_CH1 / SPI1_MISO / (NJTRST)
I2S3ext_SD/ EVENTOUT


57 D7 91 135 A6 163 PB5 I/O FT 

58 C7 92 136 B6 164 PB6 I/O FT 

59 B7 93 137 B5 165 PB7 I/O FT 


I2C1_SMBA/ CAN2_RX /
OTG_HS_ULPI_D7 /
ETH_PPS_OUT/TIM3_CH2
/ SPI1_MOSI/ SPI3_MOSI /
DCMI_D10 / I2S3_SD/
EVENTOUT


I2C1_SCL/ TIM4_CH1 /
CAN2_TX /
DCMI_D5/USART1_TX/
EVENTOUT


I2C1_SDA / FSMC_NL /
DCMI_VSYNC /
USART1_RX/ TIM4_CH2/
EVENTOUT


60 A7 94 138 D6 166 BOOT0 I B - - VPP


61 D8 95 139 A5 167 PB8 I/O FT 

62 C8 96 140 B4 168 PB9 I/O FT 


TIM4_CH3/SDIO_D4/
TIM10_CH1 / DCMI_D6 /
ETH_MII_TXD3 /
I2C1_SCL/ CAN1_RX/
EVENTOUT


SPI2_NSS/ I2S2_WS /
TIM4_CH4/ TIM11_CH1/
SDIO_D5 / DCMI_D7 /
I2C1_SDA / CAN1_TX/
EVENTOUT


TIM4_ETR / FSMC_NBL0 /

 -  - 97 141 A4 169 PE0 I/O FT  -  DCMI_D2/ EVENTOUT


FSMC_NBL1 / DCMI_D3/

 -  - 98 142 A3 170 PE1 I/O FT  -  EVENTOUT


63 - 99 - D5 - VSS S - - - 

60/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Table 7. STM32F40xxx pin and ball definitions** **[(1)]** **(continued)**


**Pin number**


**Pin name**

**(function after**
**reset)** **[(2)]**


**Additional**
**Alternate functions**
**functions**


 - A8  - 143 C6 171 PDR_ON I FT  -  -  

10
64 A1 0 144 C5 172 VDD S - - - 

TIM8_BKIN / DCMI_D5/

 -  -  -  - D4 173 PI4 I/O FT  -  EVENTOUT


TIM8_CH1 /

 -  -  -  - C4 174 PI5 I/O FT  - DCMI_VSYNC/  EVENTOUT


TIM8_CH2 / DCMI_D6/

 -  -  -  - C3 175 PI6 I/O FT  -  EVENTOUT


TIM8_CH3 / DCMI_D7/

 -  -  -  - C2 176 PI7 I/O FT  -  EVENTOUT


1. UFBGA176 F6, F7, F8, F9, F10, G6, G7, G8, G9, G10, H6, H7, H8, H9, H10, J6, J7, J8, J9, J10, K6, K7, K8, K9 and K10
balls are connected to VSS for heat dissipation and package mechanical stability.

2. Function availability depends on the chosen device.


3. PC13, PC14, PC15 and PI8 are supplied through the power switch. Since the switch only sinks a limited amount of current
(3 mA), the use of GPIOs PC13 to PC15 and PI8 in output mode is limited:

  - The speed should not exceed 2 MHz with a maximum load of 30 pF.

  - These I/Os must not be used as a current source (e.g. to drive an LED).


4. Main function after the first backup domain power-up. Later on, it depends on the contents of the RTC registers even after
reset (because these registers are not reset by the main reset). For details on how to manage these I/Os, refer to the RTC
register description sections in the STM32F4xx reference manual, available from the STMicroelectronics website:
_www.st.com_ .


5. FT = 5 V tolerant except when in analog mode or oscillator mode (for PC14, PC15, PH0 and PH1).


6. If the device is delivered in an UFBGA176 or WLCSP90 and the BYPASS_REG pin is set to VDD (Regulator off/internal
reset ON mode), then PA0 is used as an internal Reset (active low).


**Table 8. FSMC pin definition**


**FSMC**

**WLCSP90**

**Pins** **[(1)]** **NOR/PSRAM/** **LQFP100** **[(2)]** **(2)**

**CF** **NOR/PSRAM Mux** **NAND 16 bit**
**SRAM**


PE2       - A23 A23       - Yes       

PE3       - A19 A19       - Yes       

PE4       - A20 A20       - Yes       

PE5       - A21 A21       - Yes       

PE6       - A22 A22       - Yes       

DS8626 Rev 12 61/206



**Pinouts and pin description** **STM32F405xx, STM32F407xx**


**Table 8. FSMC pin definition (continued)**


**FSMC**

**WLCSP90**

**Pins** **[(1)]** **NOR/PSRAM/** **LQFP100** **[(2)]** **(2)**

**CF** **NOR/PSRAM Mux** **NAND 16 bit**
**SRAM**


PF0 A0 A0       -       -       -       

PF1 A1 A1       -       -       -       

PF2 A2 A2       -       -       -       

PF3 A3 A3       -       -       -       

PF4 A4 A4       -       -       -       

PF5 A5 A5       -       -       -       

PF6 NIORD       -       -       -       -       

PF7 NREG       -       -       -       -       

PF8 NIOWR       -       -       -       -       

PF9 CD       -       -       -       -       

PF10 INTR       -       -       -       -       

PF12 A6 A6       -       -       -       

PF13 A7 A7       -       -       -       

PF14 A8 A8       -       -       -       

PF15 A9 A9       -       -       -       

PG0 A10 A10       -       -       -       

PG1       - A11       -       -       -       

PE7 D4 D4 DA4 D4 Yes Yes


PE8 D5 D5 DA5 D5 Yes Yes


PE9 D6 D6 DA6 D6 Yes Yes


PE10 D7 D7 DA7 D7 Yes Yes


PE11 D8 D8 DA8 D8 Yes Yes


PE12 D9 D9 DA9 D9 Yes Yes


PE13 D10 D10 DA10 D10 Yes Yes


PE14 D11 D11 DA11 D11 Yes Yes


PE15 D12 D12 DA12 D12 Yes Yes


PD8 D13 D13 DA13 D13 Yes Yes


PD9 D14 D14 DA14 D14 Yes Yes


PD10 D15 D15 DA15 D15 Yes Yes


PD11       - A16 A16 CLE Yes Yes


PD12       - A17 A17 ALE Yes Yes


PD13       - A18 A18       - Yes       

PD14 D0 D0 DA0 D0 Yes Yes


62/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Pinouts and pin description**


**Table 8. FSMC pin definition (continued)**


**FSMC**

**WLCSP90**

**Pins** **[(1)]** **NOR/PSRAM/** **LQFP100** **[(2)]** **(2)**

**CF** **NOR/PSRAM Mux** **NAND 16 bit**
**SRAM**


PD15 D1 D1 DA1 D1 Yes Yes


PG2       - A12       -       -       -       

PG3       - A13       -       -       -       

PG4       - A14       -       -       -       

PG5       - A15       -       -       -       

PG6       -       -       - INT2       -       

PG7       -       -       - INT3       -       

PD0 D2 D2 DA2 D2 Yes Yes


PD1 D3 D3 DA3 D3 Yes Yes


PD3       - CLK CLK       - Yes       

PD4 NOE NOE NOE NOE Yes Yes


PD5 NWE NWE NWE NWE Yes Yes


PD6 NWAIT NWAIT NWAIT NWAIT Yes Yes


PD7       - NE1 NE1 NCE2 Yes Yes


PG9       - NE2 NE2 NCE3       -       

PG10 NCE4_1 NE3 NE3       -       -       

PG11 NCE4_2       -       -       -       -       

PG12       - NE4 NE4       -       -       

PG13       - A24 A24       -       -       

PG14       - A25 A25       -       -       

PB7       - NADV NADV       - Yes Yes


PE0       - NBL0 NBL0       - Yes       

PE1       - NBL1 NBL1       - Yes       

1. Full FSMC features are available on LQFP144, LQFP176, and UFBGA176. The features available on
smaller packages are given in the dedicated package column.


2. Ports F and G are not available in devices delivered in 100-pin packages.


DS8626 Rev 12 63/206



**Table 9. Alternate function mapping**


**AF0** **AF1** **AF2** **AF3** **AF4** **AF5** **AF6** **AF7** **AF8** **AF9** **AF10** **AF11** **AF12** **AF13**


**Port**


**SPI1/SPI2/** **CAN1/2** **AF14** **AF15**
**TIM8/9/10** **SPI3/I2Sext** **USART1/2/3/** **UART4/5/** **OTG_FS/** **FSMC/SDIO**
**SYS** **TIM1/2** **TIM3/4/5** **/11** **I2C1/2/3** **I2S2/I2S2e** **/I2S3** **I2S3ext** **USART6** **TIM12/13/** **OTG_HS** **ETH** **/OTG_FS** **DCMI**
**xt** **14**


**SPI3/I2Sext** **USART1/2/3/** **UART4/5/**
**/I2S3** **I2S3ext** **USART6**


**CAN1/2**
**TIM12/13/**
**14**


**OTG_FS/** **FSMC/SDIO**
**ETH** **DCMI**
**OTG_HS** **/OTG_FS**


PA0 - TIM2_CH1_ETR TIM 5_CH1 TIM8_ETR - - - USART2_CTS UART4_TX - - ETH_MII_CRS - - - EVENTOUT


PA1 - TIM2_CH2 TIM5_CH2 - - - - USART2_RTS UART4_RX - 


ETH_MII
_RX_CLK
ETH_RMII__REF
_CLK


- - - EVENTOUT


Port A


PA2 - TIM2_CH3 TIM5_CH3 TIM9_CH1 - - - USART2_TX - - - ETH_MDIO - - - EVENTOUT


PA3 - TIM2_CH4 TIM5_CH4 TIM9_CH2 - - - USART2_RX - - OTG_HS_ULPI_D0 ETH _MII_COL - - - EVENTOUT


PA4 - - - - - SPI1_NSS SPI3_NSS I2S3_WS USART2_CK - - - - OTG_HS_SOF HSYNC DCMI_ - EVENTOUT


PA5 - TIM2_CH1_ETR - TIM8_CH1N - SPI1_SCK - - - - OTG_HS_ULPI_CK - - - - EVENTOUT


PA6 - TIM1_BKIN TIM3_CH1 TIM8_BKIN - SPI1_MISO - - - TIM13_CH1 - - - PIXCLK DCMI_ - EVENTOUT


ETH_MII _RX_DV
PA7 - TIM1_CH1N TIM3_CH2 TIM8_CH1N - SPI1_MOSI - - - TIM14_CH1 - ETH_RMII - - - EVENTOUT
_CRS_DV


PA8 MCO1 TIM1_CH1 - - I2C3_SCL - - USART1_CK - - OTG_FS_SOF - - - - EVENTOUT


PA9 - TIM1_CH2 - - SMBAI2C3_ - - USART1_TX - - - - - DCMI_D0 - EVENTOUT


PA10 - TIM1_CH3 - - - - - USART1_RX - - OTG_FS_ID - - DCMI_D1 - EVENTOUT


PA11 - TIM1_CH4 - - - - - USART1_CTS - CAN1_RX OTG_FS_DM - - - - EVENTOUT


PA12 - TIM1_ETR - - - - - USART1_RTS - CAN1_TX OTG_FS_DP - - - - EVENTOUT


PA13 SWDIO JTMS- - - - - - - - - - - - - - - EVENTOUT


PA14 SWCLK JTCK- - - - - - - - - - - - - - - EVENTOUT


PA15 JTDI TIM 2_CH1 TIM 2_ETR - - - SPI1_NSS SPI3_NSS/I2S3_WS - - - - - - - - EVENTOUT


**Table 9. Alternate function mapping (continued)**


**AF0** **AF1** **AF2** **AF3** **AF4** **AF5** **AF6** **AF7** **AF8** **AF9** **AF10** **AF11** **AF12** **AF13**


**Port**


**SPI1/SPI2/** **CAN1/2** **AF14** **AF15**
**TIM8/9/10** **SPI3/I2Sext** **USART1/2/3/** **UART4/5/** **OTG_FS/** **FSMC/SDIO**
**SYS** **TIM1/2** **TIM3/4/5** **/11** **I2C1/2/3** **I2S2/I2S2e** **/I2S3** **I2S3ext** **USART6** **TIM12/13/** **OTG_HS** **ETH** **/OTG_FS** **DCMI**
**xt** **14**


**SPI3/I2Sext** **USART1/2/3/** **UART4/5/**
**/I2S3** **I2S3ext** **USART6**


**CAN1/2**
**TIM12/13/**
**14**


**OTG_FS/** **FSMC/SDIO**
**ETH** **DCMI**
**OTG_HS** **/OTG_FS**


Port B


PB0 - TIM1_CH2N TIM3_CH3 TIM8_CH2N - - - - - - OTG_HS_ULPI_D1 ETH _MII_RXD2 - - - EVENTOUT


PB1 - TIM1_CH3N TIM3_CH4 TIM8_CH3N - - - - - OTG_HS_ULPI_D2 ETH _MII_RXD3 - - - EVENTOUT


PB2 - - - - - - - - - - - - - - - EVENTOUT

PB3 TRACESJTDO/WO TIM2_CH2 - - - SPI1_SCK SPI3_SCK I2S3_CK - - - - - - - - EVENTOUT


PB4 NJTRST - TIM3_CH1 - SPI1_MISO SPI3_MISO I2S3ext_SD - - - - - - - EVENTOUT


PB5 - - TIM3_CH2 I2C1_SMBA SPI1_MOSI SPI3_MOSI I2S3_SD - - CAN2_RX OTG_HS_ULPI_D7 ETH _PPS_OUT - DCMI_D10 - EVENTOUT


PB6 - - TIM4_CH1 I2C1_SCL - - USART1_TX - CAN2_TX - - - DCMI_D5 - EVENTOUT


PB7 - - TIM4_CH2 I2C1_SDA - - USART1_RX - - - - FSMC_NL DCMI_VSYNC - EVENTOUT


PB8 - - TIM4_CH3 TIM10_CH1 I2C1_SCL - - - - CAN1_RX - ETH _MII_TXD3 SDIO_D4 DCMI_D6 - EVENTOUT


SPI2_NSS
PB9 - - TIM4_CH4 TIM11_CH1 I2C1_SDA - - - CAN1_TX - - SDIO_D5 DCMI_D7 - EVENTOUT
I2S2_WS


PB10 - TIM2_CH3 - - I2C2_SCL SPI2_SCK I2S2_CK - USART3_TX - - OTG_HS_ULPI_D3 ETH_ MII_RX_ER - - - EVENTOUT


PB11 - TIM2_CH4 - - I2C2_SDA - - USART3_RX - - OTG_HS_ULPI_D4


ETH _MII_TX_EN
ETH   -   -   - EVENTOUT
_RMII_TX_EN


PB12 - TIM1_BKIN - - SMBAI2C2_ SPI2_NSS I2S2_WS - USART3_CK - CAN2_RX OTG_HS_ULPI_D5 ETH _RMII_TXD0ETH _MII_TXD0 OTG_HS_ID - - EVENTOUT


PB13 - TIM1_CH1N - - - SPI2_SCK I2S2_CK - USART3_CTS - CAN2_TX OTG_HS_ULPI_D6 ETH _RMII_TXD1ETH _MII_TXD1 - - - EVENTOUT


PB14 - TIM1_CH2N - TIM8_CH2N - SPI2_MISO I2S2ext_SD USART3_RTS - TIM12_CH1 - - OTG_HS_DM - - EVENTOUT


PB15 REFINRTC_ TIM1_CH3N - TIM8_CH3N - SPI2_MOSI I2S2_SD - - - TIM12_CH2 - - OTG_HS_DP - - EVENTOUT


**Table 9. Alternate function mapping (continued)**


**AF0** **AF1** **AF2** **AF3** **AF4** **AF5** **AF6** **AF7** **AF8** **AF9** **AF10** **AF11** **AF12** **AF13**


**Port**


**SPI1/SPI2/** **CAN1/2** **AF14** **AF15**
**TIM8/9/10** **SPI3/I2Sext** **USART1/2/3/** **UART4/5/** **OTG_FS/** **FSMC/SDIO**
**SYS** **TIM1/2** **TIM3/4/5** **/11** **I2C1/2/3** **I2S2/I2S2e** **/I2S3** **I2S3ext** **USART6** **TIM12/13/** **OTG_HS** **ETH** **/OTG_FS** **DCMI**
**xt** **14**


**SPI3/I2Sext** **USART1/2/3/** **UART4/5/**
**/I2S3** **I2S3ext** **USART6**


**CAN1/2**
**TIM12/13/**
**14**


**OTG_FS/** **FSMC/SDIO**
**ETH** **DCMI**
**OTG_HS** **/OTG_FS**


Port C


PC0 - - - - - - - - - - OTG_HS_ULPI_STP - - - - EVENTOUT


PC1 - - - - - - - - - - - ETH_MDC - - - EVENTOUT


PC2 - - - - - SPI2_MISO I2S2ext_SD - - - OTG_HS_ULPI_DIR ETH _MII_TXD2 - - - EVENTOUT


PC3 - - - - - SPI2_MOSII2S2_SD - - - - OTG_HS_ULPI_NXT _MII_TX_CLKETH - - - EVENTOUT


PC4 - - - - - - - - - - - ETH_RMII_RXD0ETH_MII_RXD0 - - - EVENTOUT


PC5 - - - - - - - - - - - ETH _RMII_RXD1ETH _MII_RXD1 - - - EVENTOUT


PC6 - - TIM3_CH1 TIM8_CH1 I2S2_MCK - USART6_TX - - - SDIO_D6 DCMI_D0 - EVENTOUT


PC7 - - TIM3_CH2 TIM8_CH2 - - I2S3_MCK - USART6_RX - - - SDIO_D7 DCMI_D1 - EVENTOUT


PC8 - - TIM3_CH3 TIM8_CH3 - - - - USART6_CK - - - SDIO_D0 DCMI_D2 - EVENTOUT


PC9 MCO2 - TIM3_CH4 TIM8_CH4 I2C3_SDA I2S_CKIN - - - - - - SDIO_D1 DCMI_D3 - EVENTOUT


PC10 - - - - - - SPI3_SCK/I2S3_CK USART3_TX/ UART4_TX - - - SDIO_D2 DCMI_D8 - EVENTOUT


PC11 - - - - - I2S3ext_SD SPI3_MISO/ USART3_RX UART4_RX - - - SDIO_D3 DCMI_D4 - EVENTOUT


PC12 - - - - - - SPI3_MOSI I2S3_SD USART3_CK UART5_TX - - - SDIO_CK DCMI_D9 - EVENTOUT


PC13 - - - - - - - - - - - - - - - 

PC14 - - - - - - - - - - - - - - - 

PC15 - - - - - - - - - - - - - - - 

**Table 9. Alternate function mapping (continued)**


**AF0** **AF1** **AF2** **AF3** **AF4** **AF5** **AF6** **AF7** **AF8** **AF9** **AF10** **AF11** **AF12** **AF13**


**Port**


**SPI1/SPI2/** **CAN1/2** **AF14** **AF15**
**TIM8/9/10** **SPI3/I2Sext** **USART1/2/3/** **UART4/5/** **OTG_FS/** **FSMC/SDIO**
**SYS** **TIM1/2** **TIM3/4/5** **/11** **I2C1/2/3** **I2S2/I2S2e** **/I2S3** **I2S3ext** **USART6** **TIM12/13/** **OTG_HS** **ETH** **/OTG_FS** **DCMI**
**xt** **14**


**SPI3/I2Sext** **USART1/2/3/** **UART4/5/**
**/I2S3** **I2S3ext** **USART6**


**CAN1/2**
**TIM12/13/**
**14**


**OTG_FS/** **FSMC/SDIO**
**ETH** **DCMI**
**OTG_HS** **/OTG_FS**


Port D


PD0 - - - - - - - - - CAN1_RX - - FSMC_D2 - - EVENTOUT


PD1 - - - - - - - - - CAN1_TX - - FSMC_D3 - - EVENTOUT


PD2 - - TIM3_ETR - - - - - UART5_RX - - - SDIO_CMD DCMI_D11 - EVENTOUT


PD3 - - - - - - - USART2_CTS - - - - FSMC_CLK - - EVENTOUT


PD4 - - - - - - - USART2_RTS - - - - FSMC_NOE - - EVENTOUT


PD5 - - - - - - - USART2_TX - - - - FSMC_NWE - - EVENTOUT


PD6 - - - - - - - USART2_RX - - - - FSMC_NWAIT - - EVENTOUT


PD7 - - - - - - - USART2_CK - - - - FSMC_NCE2 FSMC_NE1/ - - EVENTOUT


PD8 - - - - - - - USART3_TX - - - - FSMC_D13 - - EVENTOUT


PD9 - - - - - - - USART3_RX - - - - FSMC_D14 - - EVENTOUT


PD10 - - - - - - - USART3_CK - - - - FSMC_D15 - - EVENTOUT


PD11 - - - - - - - USART3_CTS - - - - FSMC_A16 - - EVENTOUT


PD12 - - TIM4_CH1 - - - - USART3_RTS - - - - FSMC_A17 - - EVENTOUT


PD13 - - TIM4_CH2 - - - - - - - - - FSMC_A18 - - EVENTOUT


PD14 - - TIM4_CH3 - - - - - - - - - FSMC_D0 - - EVENTOUT


PD15 - - TIM4_CH4 - - - - - - - - - FSMC_D1 - - EVENTOUT


**Table 9. Alternate function mapping (continued)**


**AF0** **AF1** **AF2** **AF3** **AF4** **AF5** **AF6** **AF7** **AF8** **AF9** **AF10** **AF11** **AF12** **AF13**


**Port**


**SPI1/SPI2/** **CAN1/2** **AF14** **AF15**
**TIM8/9/10** **SPI3/I2Sext** **USART1/2/3/** **UART4/5/** **OTG_FS/** **FSMC/SDIO**
**SYS** **TIM1/2** **TIM3/4/5** **/11** **I2C1/2/3** **I2S2/I2S2e** **/I2S3** **I2S3ext** **USART6** **TIM12/13/** **OTG_HS** **ETH** **/OTG_FS** **DCMI**
**xt** **14**


**SPI3/I2Sext** **USART1/2/3/** **UART4/5/**
**/I2S3** **I2S3ext** **USART6**


**CAN1/2**
**TIM12/13/**
**14**


**OTG_FS/** **FSMC/SDIO**
**ETH** **DCMI**
**OTG_HS** **/OTG_FS**


Port E


PE0 - - TIM4_ETR - - - - - - - - - FSMC_NBL0 DCMI_D2 - EVENTOUT


PE1 - - - - - - - - - - - - FSMC_NBL1 DCMI_D3 - EVENTOUT


PE2 TRACECLK - - - - - - - - - - ETH _MII_TXD3 FSMC_A23 - - EVENTOUT


PE3 TRACED0 - - - - - - - - - - - FSMC_A19 - - EVENTOUT


PE4 TRACED1 - - - - - - - - - - - FSMC_A20 DCMI_D4 - EVENTOUT


PE5 TRACED2 - - TIM9_CH1 - - - - - - - - FSMC_A21 DCMI_D6 - EVENTOUT


PE6 TRACED3 - - TIM9_CH2 - - - - - - - - FSMC_A22 DCMI_D7 - EVENTOUT


PE7 - TIM1_ETR - - - - - - - - - - FSMC_D4 - - EVENTOUT


PE8 - TIM1_CH1N - - - - - - - - - - FSMC_D5 - - EVENTOUT


PE9 - TIM1_CH1 - - - - - - - - - - FSMC_D6 - - EVENTOUT


PE10 - TIM1_CH2N - - - - - - - - - - FSMC_D7 - - EVENTOUT


PE11 - TIM1_CH2 - - - - - - - - - - FSMC_D8 - - EVENTOUT


PE12 - TIM1_CH3N - - - - - - - - - - FSMC_D9 - - EVENTOUT


PE13 - TIM1_CH3 - - - - - - - - - - FSMC_D10 - - EVENTOUT


PE14 - TIM1_CH4 - - - - - - - - - - FSMC_D11 - - EVENTOUT


PE15 - TIM1_BKIN - - - - - - - - - - FSMC_D12 - - EVENTOUT


**Table 9. Alternate function mapping (continued)**


**AF0** **AF1** **AF2** **AF3** **AF4** **AF5** **AF6** **AF7** **AF8** **AF9** **AF10** **AF11** **AF12** **AF13**


**Port**


**SPI1/SPI2/** **CAN1/2** **AF14** **AF15**
**TIM8/9/10** **SPI3/I2Sext** **USART1/2/3/** **UART4/5/** **OTG_FS/** **FSMC/SDIO**
**SYS** **TIM1/2** **TIM3/4/5** **/11** **I2C1/2/3** **I2S2/I2S2e** **/I2S3** **I2S3ext** **USART6** **TIM12/13/** **OTG_HS** **ETH** **/OTG_FS** **DCMI**
**xt** **14**


**SPI3/I2Sext** **USART1/2/3/** **UART4/5/**
**/I2S3** **I2S3ext** **USART6**


**CAN1/2**
**TIM12/13/**
**14**


**OTG_FS/** **FSMC/SDIO**
**ETH** **DCMI**
**OTG_HS** **/OTG_FS**


Port F


PF0 - - - - I2C2_SDA - - - - - - - FSMC_A0 - - EVENTOUT


PF1 - - - - I2C2_SCL - - - - - - - FSMC_A1 - - EVENTOUT


PF2 - - - - SMBAI2C2_ - - - - - - - FSMC_A2 - - EVENTOUT


PF3 - - - - - - - - - - - - FSMC_A3 - - EVENTOUT


PF4 - - - - - - - - - - - - FSMC_A4 - - EVENTOUT


PF5 - - - - - - - - - - - - FSMC_A5 - - EVENTOUT


PF6 - - - TIM10_CH1 - - - - - - - - FSMC_NIORD - - EVENTOUT


PF7 - - - TIM11_CH1 - - - - - - - - FSMC_NREG - - EVENTOUT


PF8 - - - - - - - - - TIM13_CH1 - - NIOWR FSMC_ - - EVENTOUT


PF9 - - - - - - - - - TIM14_CH1 - - FSMC_CD - - EVENTOUT


PF10 - - - - - - - - - - - - FSMC_INTR - - EVENTOUT


PF11 - - - - - - - - - - - - DCMI_D12 - EVENTOUT


PF12 - - - - - - - - - - - - FSMC_A6 - - EVENTOUT


PF13 - - - - - - - - - - - - FSMC_A7 - - EVENTOUT


PF14 - - - - - - - - - - - - FSMC_A8 - - EVENTOUT


PF15 - - - - - - - - - - - - FSMC_A9 - - EVENTOUT


**Table 9. Alternate function mapping (continued)**


**AF0** **AF1** **AF2** **AF3** **AF4** **AF5** **AF6** **AF7** **AF8** **AF9** **AF10** **AF11** **AF12** **AF13**


**Port**


**SPI1/SPI2/** **CAN1/2** **AF14** **AF15**
**TIM8/9/10** **SPI3/I2Sext** **USART1/2/3/** **UART4/5/** **OTG_FS/** **FSMC/SDIO**
**SYS** **TIM1/2** **TIM3/4/5** **/11** **I2C1/2/3** **I2S2/I2S2e** **/I2S3** **I2S3ext** **USART6** **TIM12/13/** **OTG_HS** **ETH** **/OTG_FS** **DCMI**
**xt** **14**


**SPI3/I2Sext** **USART1/2/3/** **UART4/5/**
**/I2S3** **I2S3ext** **USART6**


**CAN1/2**
**TIM12/13/**
**14**


**OTG_FS/** **FSMC/SDIO**
**ETH** **DCMI**
**OTG_HS** **/OTG_FS**


Port G


PG0 - - - - - - - - - - - - FSMC_A10 - - EVENTOUT


PG1 - - - - - - - - - - - - FSMC_A11 - - EVENTOUT


PG2 - - - - - - - - - - - - FSMC_A12 - - EVENTOUT


PG3 - - - - - - - - - - - - FSMC_A13 - - EVENTOUT


PG4 - - - - - - - - - - - - FSMC_A14 - - EVENTOUT


PG5 - - - - - - - - - - - - FSMC_A15 - - EVENTOUT


PG6 - - - - - - - - - - - - FSMC_INT2 - - EVENTOUT


PG7 - - - - - - - - USART6_CK - - - FSMC_INT3 - - EVENTOUT


PG8 - - - - - - - - USART6_RTS - - ETH _PPS_OUT - - - EVENTOUT


PG9 - - - - - - - - USART6_RX - - - FSMC_NCE3 FSMC_NE2/ - - EVENTOUT


FSMC_
PG10 - - - - - - - - - - - - NCE4_1/ - - EVENTOUT
FSMC_NE3


ETH _MII_TX_EN
PG11 - - - - - - - - - - - ETH _RMII_
TX_EN


FSMC_NCE4_2 - - EVENTOUT


PG12 - - - - - - - - USART6_RTS - - - FSMC_NE4 - - EVENTOUT


ETH _MII_TXD0
PG13 - - - - - - - - UART6_CTS - - FSMC_A24 - - EVENTOUT
ETH _RMII_TXD0


PG14 - - - - - - - - USART6_TX - - ETH _RMII_TXD1 ETH _MII_TXD1 FSMC_A25 - - EVENTOUT


PG15 - - - - - - - - USART6_CTS - - - - DCMI_D13 - EVENTOUT


**Table 9. Alternate function mapping (continued)**


**AF0** **AF1** **AF2** **AF3** **AF4** **AF5** **AF6** **AF7** **AF8** **AF9** **AF10** **AF11** **AF12** **AF13**


**Port**


**SPI1/SPI2/** **CAN1/2** **AF14** **AF15**
**TIM8/9/10** **SPI3/I2Sext** **USART1/2/3/** **UART4/5/** **OTG_FS/** **FSMC/SDIO**
**SYS** **TIM1/2** **TIM3/4/5** **/11** **I2C1/2/3** **I2S2/I2S2e** **/I2S3** **I2S3ext** **USART6** **TIM12/13/** **OTG_HS** **ETH** **/OTG_FS** **DCMI**
**xt** **14**


**SPI3/I2Sext** **USART1/2/3/** **UART4/5/**
**/I2S3** **I2S3ext** **USART6**


**CAN1/2**
**TIM12/13/**
**14**


**OTG_FS/** **FSMC/SDIO**
**ETH** **DCMI**
**OTG_HS** **/OTG_FS**


Port H


PH0 - - - - - - - - - - - - - - - EVENTOUT


PH1 - - - - - - - - - - - - - - - EVENTOUT


PH2 - - - - - - - - - - - ETH _MII_CRS - - - EVENTOUT


PH3 - - - - - - - - - - - ETH _MII_COL - - - EVENTOUT


PH4 - - - - I2C2_SCL - - - - - OTG_HS_ULPI_NXT - - - - EVENTOUT


PH5 - - - - I2C2_SDA - - - - - - - - - - EVENTOUT


PH6 - - - - SMBAI2C2_ - - - - TIM12_CH1 - ETH _MII_RXD2 - - - EVENTOUT


PH7 - - - - I2C3_SCL - - - - - - ETH _MII_RXD3 - - - EVENTOUT


PH8 - - - - I2C3_SDA - - - - - - - - HSYNC DCMI_ - EVENTOUT


PH9 - - - - SMBAI2C3_ - - - - TIM12_CH2 - - - DCMI_D0 - EVENTOUT


PH10 - - TIM5_CH1 - - - - - - - - - - DCMI_D1 - EVENTOUT


PH11 - - TIM5_CH2 - - - - - - - - - - DCMI_D2 - EVENTOUT


PH12 - - TIM5_CH3 - - - - - - - - - - DCMI_D3 - EVENTOUT


PH13 - - - TIM8_CH1N - - - - - CAN1_TX - - - - - EVENTOUT


PH14 - - - TIM8_CH2N - - - - - - - - - DCMI_D4 - EVENTOUT


PH15 - - - TIM8_CH3N - - - - - - - - - DCMI_D11 - EVENTOUT


**Table 9. Alternate function mapping (continued)**


**AF0** **AF1** **AF2** **AF3** **AF4** **AF5** **AF6** **AF7** **AF8** **AF9** **AF10** **AF11** **AF12** **AF13**


**Port**


Port I


**SPI1/SPI2/** **CAN1/2** **AF14** **AF15**
**TIM8/9/10** **SPI3/I2Sext** **USART1/2/3/** **UART4/5/** **OTG_FS/** **FSMC/SDIO**
**SYS** **TIM1/2** **TIM3/4/5** **/11** **I2C1/2/3** **I2S2/I2S2e** **/I2S3** **I2S3ext** **USART6** **TIM12/13/** **OTG_HS** **ETH** **/OTG_FS** **DCMI**
**xt** **14**


**SPI3/I2Sext** **USART1/2/3/** **UART4/5/**
**/I2S3** **I2S3ext** **USART6**


**CAN1/2**
**TIM12/13/**
**14**


**OTG_FS/** **FSMC/SDIO**
**ETH** **DCMI**
**OTG_HS** **/OTG_FS**


PI0 - - TIM5_CH4 - - SPI2_NSS I2S2_WS - - - - - - - DCMI_D13 - EVENTOUT


PI1 - - - - - SPI2_SCK I2S2_CK - - - - - - - DCMI_D8 - EVENTOUT


PI2 - - - TIM8_CH4 - SPI2_MISO I2S2ext_SD - - - - - - DCMI_D9 - EVENTOUT


PI3 - - - TIM8_ETR - SPI2_MOSI I2S2_SD - - - - - - - DCMI_D10 - EVENTOUT


PI4 - - - TIM8_BKIN - - - - - - - - - DCMI_D5 - EVENTOUT


PI5 - - - TIM8_CH1 - - - - - - - - - VSYNC DCMI_ - EVENTOUT


PI6 - - - TIM8_CH2 - - - - - - - - - DCMI_D6 - EVENTOUT


PI7 - - - TIM8_CH3 - - - - - - - - - DCMI_D7 - EVENTOUT


PI8 - - - - - - - - - - - - - - - 

PI9 - - - - - - - - - CAN1_RX - - - - - EVENTOUT


PI10 - - - - - - - - - - - ETH _MII_RX_ER - - - EVENTOUT


PI11 - - - - - - - - - - OTG_HS_ULPI_DIR - - - - EVENTOUT


**STM32F405xx, STM32F407xx** **Memory mapping**

### **5 Memory mapping**


The memory map is shown in _Figure 18_ .


**Figure 18. STM32F40xxx memory map**


Reserved 0xE010 0000 - 0xFFFF FFFF


CORTEX-M4 internal peripherals 0xE000 0000 - 0xE00F FFFF


0xFFFF FFFF


0xE000 0000
0xDFFF FFFF


0xC000 0000
0xBFFF FFFF


0xA000 0000
0x9FFF FFFF


0x8000 0000
0x7FFF FFFF


0x6000 0000
0x5FFF FFFF


0x4000 0000
0x3FFF FFFF


0x2000 0000
0x1FFF FFFF


0x0000 0000


Reserved 0x1FFF C008 - 0x1FFF FFFF


512-Mbyte
block 7
Cortex-M4's
internal
peripherals


512-Mbyte
block 6
Not used


512-Mbyte
block 5
FSMC registers


512-Mbyte
block 4
FSMC bank 3
& bank4


512-Mbyte
block 3
FSMC bank1
& bank2


512-Mbyte
block 2
Peripherals


512-Mbyte
block 1
SRAM


512-Mbyte
block 0
Code


Reserved


SRAM (16 KB aliased
by bit-banding)


SRAM (112 KB aliased
by bit-banding)


0x2002 0000 - 0x3FFF FFFF


0x2001 C000 - 0x2001 FFFF


0x2000 0000 - 0x2001 BFFF


Option Bytes


0x1FFF C000 - 0x1FFF C007


Reserved 0x1FFF 7A10 - 0x1FFF 7FFF


System memory + OTP


0x1FFF 0000 - 0x1FFF 7A0F


Reserved 0x1001 0000 - 0x1FFE FFFF


CCM data RAM
0x1000 0000 - 0x1000 FFFF
(64 KB data SRAM)


Reserved


0x0810 0000 - 0x0FFF FFFF

Flash 0x0800 0000 - 0x080F FFFF


Reserved 0xA000 1000 - 0xDFFF FFFF

0xA000 0FFF
AHB3
0x6000 0000
Reserved 0x5006 0C00 - 0x5FFF FFFF


0x5006 0BFF


AHB2


0x5000 0000
Reserved 0x4008 0000 - 0x4FFF FFFF

0x4007 FFFF


AHB1


0x4002 0000


Reserved 0x4001 5800 - 0x4001 FFFF


0x4001 57FF


APB2


0x4001 0000

Reserved 0x4000 7800 - 0x4000 FFFF

0x4000 7FFF


APB1


0x4000 0000


ai18513g


Reserved
Aliased to Flash, system
memory or SRAM depending
on the BOOT pins


0x0800 0000 - 0x080F FFFF

0x0010 0000 - 0x07FF FFFF


0x0000 0000 - 0x000F FFFF


DS8626 Rev 12 73/206



**Memory mapping** **STM32F405xx, STM32F407xx**


**Table 10. Register boundary addresses**


**Bus** **Boundary address** **Peripheral**


0xE00F FFFF - 0xFFFF FFFF Reserved


Cortex-M4 0xE000 0000 - 0xE00F FFFF Cortex-M4 internal peripherals


0xA000 1000 - 0xDFFF FFFF Reserved


0xA000 0000 - 0xA000 0FFF FSMC control register


0x9000 0000 - 0x9FFF FFFF FSMC bank 4


AHB3


AHB2


0x8000 0000 - 0x8FFF FFFF FSMC bank 3


0x7000 0000 - 0x7FFF FFFF FSMC bank 2


0x6000 0000 - 0x6FFF FFFF FSMC bank 1


0x5006 0C00- 0x5FFF FFFF Reserved


0x5006 0800 - 0x5006 0BFF RNG


0x5005 0400 - 0x5006 07FF Reserved


0x5005 0000 - 0x5005 03FF DCMI


0x5004 0000- 0x5004 FFFF Reserved


0x5000 0000 - 0x5003 FFFF USB OTG FS


0x4008 0000- 0x4FFF FFFF Reserved


74/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Memory mapping**


**Table 10. Register boundary addresses (continued)**


**Bus** **Boundary address** **Peripheral**


0x4004 0000 - 0x4007 FFFF USB OTG HS


0x4002 9400 - 0x4003 FFFF Reserved


0x4002 9000 - 0x4002 93FF


0x4002 8C00 - 0x4002 8FFF


0x4002 8800 - 0x4002 8BFF


0x4002 8400 - 0x4002 87FF


0x4002 8000 - 0x4002 83FF


ETHERNET MAC


AHB1


0x4002 6800 - 0x4002 7FFF Reserved


0x4002 6400 - 0x4002 67FF DMA2


0x4002 6000 - 0x4002 63FF DMA1


0x4002 5000 - 0x4002 5FFF Reserved


0x4002 4000 - 0x4002 4FFF BKPSRAM


0x4002 3C00 - 0x4002 3FFF Flash interface register


0x4002 3800 - 0x4002 3BFF RCC


0x4002 3400 - 0x4002 37FF Reserved


0x4002 3000 - 0x4002 33FF CRC


0x4002 2400 - 0x4002 2FFF Reserved


0x4002 2000 - 0x4002 23FF GPIOI


0x4002 1C00 - 0x4002 1FFF GPIOH


0x4002 1800 - 0x4002 1BFF GPIOG


0x4002 1400 - 0x4002 17FF GPIOF


0x4002 1000 - 0x4002 13FF GPIOE


0x4002 0C00 - 0x4002 0FFF GPIOD


0x4002 0800 - 0x4002 0BFF GPIOC


0x4002 0400 - 0x4002 07FF GPIOB


0x4002 0000 - 0x4002 03FF GPIOA


0x4001 5800- 0x4001 FFFF Reserved


DS8626 Rev 12 75/206



**Memory mapping** **STM32F405xx, STM32F407xx**


**Table 10. Register boundary addresses (continued)**


**Bus** **Boundary address** **Peripheral**


0x4001 4C00 - 0x4001 57FF Reserved


0x4001 4800 - 0x4001 4BFF TIM11


0x4001 4400 - 0x4001 47FF TIM10


0x4001 4000 - 0x4001 43FF TIM9


0x4001 3C00 - 0x4001 3FFF EXTI


0x4001 3800 - 0x4001 3BFF SYSCFG


0x4001 3400 - 0x4001 37FF Reserved


0x4001 3000 - 0x4001 33FF SPI1


APB2


0x4001 2C00 - 0x4001 2FFF SDIO


0x4001 2400 - 0x4001 2BFF Reserved


0x4001 2000 - 0x4001 23FF ADC1 - ADC2 - ADC3


0x4001 1800 - 0x4001 1FFF Reserved


0x4001 1400 - 0x4001 17FF USART6


0x4001 1000 - 0x4001 13FF USART1


0x4001 0800 - 0x4001 0FFF Reserved


0x4001 0400 - 0x4001 07FF TIM8


0x4001 0000 - 0x4001 03FF TIM1


0x4000 7800- 0x4000 FFFF Reserved


76/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Memory mapping**


**Table 10. Register boundary addresses (continued)**


**Bus** **Boundary address** **Peripheral**


0x4000 7800 - 0x4000 7FFF Reserved


0x4000 7400 - 0x4000 77FF DAC


0x4000 7000 - 0x4000 73FF PWR


0x4000 6C00 - 0x4000 6FFF Reserved


0x4000 6800 - 0x4000 6BFF CAN2


0x4000 6400 - 0x4000 67FF CAN1


0x4000 6000 - 0x4000 63FF Reserved


0x4000 5C00 - 0x4000 5FFF I2C3


0x4000 5800 - 0x4000 5BFF I2C2


0x4000 5400 - 0x4000 57FF I2C1


0x4000 5000 - 0x4000 53FF UART5


0x4000 4C00 - 0x4000 4FFF UART4


0x4000 4800 - 0x4000 4BFF USART3


0x4000 4400 - 0x4000 47FF USART2


0x4000 4000 - 0x4000 43FF I2S3ext


APB1


0x4000 3C00 - 0x4000 3FFF SPI3 / I2S3


0x4000 3800 - 0x4000 3BFF SPI2 / I2S2


0x4000 3400 - 0x4000 37FF I2S2ext


0x4000 3000 - 0x4000 33FF IWDG


0x4000 2C00 - 0x4000 2FFF WWDG


0x4000 2800 - 0x4000 2BFF RTC & BKP Registers


0x4000 2400 - 0x4000 27FF Reserved


0x4000 2000 - 0x4000 23FF TIM14


0x4000 1C00 - 0x4000 1FFF TIM13


0x4000 1800 - 0x4000 1BFF TIM12


0x4000 1400 - 0x4000 17FF TIM7


0x4000 1000 - 0x4000 13FF TIM6


0x4000 0C00 - 0x4000 0FFF TIM5


0x4000 0800 - 0x4000 0BFF TIM4


0x4000 0400 - 0x4000 07FF TIM3


0x4000 0000 - 0x4000 03FF TIM2


DS8626 Rev 12 77/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**

### **6 Electrical characteristics**

#### **6.1 Parameter conditions**


Unless otherwise specified, all voltages are referenced to VSS.


**6.1.1** **Minimum and maximum values**


Unless otherwise specified the minimum and maximum values are evaluated in the worst
conditions of ambient temperature, supply voltage, and frequencies by tests in production
on 100% of the devices with an ambient temperature at TA = 25 °C and TA = TAmax (given
by the selected temperature range).


Data based on characterization results, design simulation and/or technology characteristics
are indicated in the table footnotes and are not tested in production. Based on
characterization, the minimum and maximum values refer to sample tests and represent the
mean value plus or minus three times the standard deviation (mean±3Σ).


**6.1.2** **Typical values**


Unless otherwise specified, typical data are based on TA = 25 °C, VDD = 3.3 V (for the
1.8 V ≤ VDD ≤ 3.6 V voltage range). They are given only as design guidelines and are not
tested.


Typical ADC accuracy values are determined by characterization of a batch of samples from
a standard diffusion lot over the full temperature range, where 95% of the devices have an
error less than or equal to the value indicated (mean±2Σ).


**6.1.3** **Typical curves**


Unless otherwise specified, all typical curves are given only as design guidelines and are
not tested.


**6.1.4** **Loading capacitor**


The loading conditions used for pin parameter measurement are shown in _Figure 19_ .


**6.1.5** **Pin input voltage**


The input voltage measurement on a pin of the device is described in _Figure 20_ .


**Figure 19. Pin loading conditions** **Figure 20. Pin input voltage**


MCU pin


C = 50 pF


MS19011V2


78/206 DS8626 Rev 12


MCU pin


VIN


MS19010V2


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**6.1.6** **Power supply scheme**


**Figure 21. Power supply scheme**


VBAT


VBAT =
1.65 to 3.6V


GPIOs


VCAP_1
2 × 2.2 μF VCAP_2


Power
switch


OUT


IN


Voltage
regulator


Reset
controller


ADC


Backup circuitry
(OSC32K,RTC,
Wakeup logic
Backup registers,
backup RAM)


IO
Logic


Kernel logic
(CPU, digital
& RAM)


Flash memory


Analog:
RCs,
PLL,..


VDD


VDD
1/2/...14/15


VSS
1/2/...14/15


BYPASS_REG


PDR_ON


VDDA


15 × 100 nF
+ 1 × 4.7 μF


VDD


100 nF
+ 1 μF


VREF


100 nF
+ 1 μF


VREF+


VREF

VSSA


MS19911V3


1. Each power supply pair must be decoupled with filtering ceramic capacitors as shown above. These capacitors must be
placed as close as possible to, or below, the appropriate pins on the underside of the PCB to ensure the good functionality
of the device.

2. To connect BYPASS_REG and PDR_ON pins, refer to _Section 3.16: Voltage regulator_ and _Table 3.15: Power supply_
_supervisor_ .

3. The two 2.2 µF ceramic capacitors should be replaced by two 100 nF decoupling capacitors when the voltage regulator is
OFF.

4. The 4.7 µF ceramic capacitor must be connected to one of the VDD pin.

5. VDDA=VDD and VSSA=VSS.


DS8626 Rev 12 79/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**6.1.7** **Current consumption measurement**


**Figure 22. Current consumption measurement scheme**


IDD_VBAT

VBAT


IDD

VDD


VDDA

#### **6.2 Absolute maximum ratings**


ai14126


Stresses above the absolute maximum ratings listed in _Table 11: Voltage characteristics_,
_Table 12: Current characteristics_, and _Table 13: Thermal characteristics_ may cause
permanent damage to the device. These are stress ratings only and functional operation of
the device at these conditions is not implied. Exposure to maximum rating conditions for
extended periods may affect device reliability. Device mission profile (application conditions)
is compliant with JEDEC JESD47 Qualification Standard, extended mission profiles are
available on demand.


**Table 11. Voltage characteristics**


**Symbol** **Ratings** **Min** **Max** **Unit**


VDD–VSS External main supply voltage (including VDDA, VDD) [(1)]


–0.3 4.0


Input voltage on five-volt tolerant pin [(2)] VSS–0.3 VDD+4 V
VIN


VSS–0.3 VDD+4


Input voltage on any other pin VSS–0.3 4.0


| Δ VDDx| Variations between different VDD power pins   - 50

mV
Variations between all the different ground pins
|VSSX - VSS| including VREF - - 50


VESD(HBM) Electrostatic discharge voltage (human body model)


see _Section 6.3.14:_
_Absolute maximum_
_ratings (electrical_
_sensitivity)_


1. All main power (VDD, VDDA) and ground (VSS, VSSA) pins must always be connected to the external power
supply, in the permitted range.

2. VIN maximum value must always be respected. Refer to _Table 12_ for the values of the maximum allowed
injected current.


80/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 12. Current characteristics**


**Symbol** **Ratings** **Max.** **Unit**


IVDD Total current into VDD power lines (source) [(1)]



IVSS Total current out of VSS ground lines (sink) [(1)] 240


Output current sunk by any I/O and control pin 25
IIO

Output current source by any I/Os and control pin 25


mA


IINJ(PIN) (2)


Injected current on five-volt tolerant I/O [(3)]

Injected current on any other pin [(4)]


Σ IINJ(PIN)(4) Total injected current (sum of all I/O and control pins) [(5)]


–5/+0


±5


±25


1. All main power (VDD, VDDA) and ground (VSS, VSSA) pins must always be connected to the external power
supply, in the permitted range.


2. Negative injection disturbs the analog performance of the device. See note in _Section 6.3.21: 12-bit ADC_
_characteristics_ .

3. Positive injection is not possible on these I/Os. A negative injection is induced by VIN<VSS. IINJ(PIN) must
never be exceeded. Refer to _Table 11_ for the values of the maximum allowed input voltage.

4. A positive injection is induced by VIN>VDD while a negative injection is induced by VIN<VSS. IINJ(PIN) must
never be exceeded. Refer to _Table 11_ for the values of the maximum allowed input voltage.

5. When several inputs are submitted to a current injection, the maximum ΣIINJ(PIN) is the absolute sum of the
positive and negative injected currents (instantaneous values).


**Table 13. Thermal characteristics**


**Symbol** **Ratings** **Value** **Unit**


TSTG Storage temperature range –65 to +150 °C

TJ Maximum junction temperature 125 °C

#### **6.3 Operating conditions**


**6.3.1** **General operating conditions**


**Table 14. General operating conditions**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


VOS bit in PWR_CR register = 0 [(1)] 0                     - 144
fHCLK Internal AHB clock frequency


VOS bit in PWR_CR register= 1 0 - 168
MHz


fPCLK1 Internal APB1 clock frequency - 0 - 42


fPCLK2 Internal APB2 clock frequency - 0 - 84

VDD Standard operating voltage - 1.8 [(2)] - 3.6 V


1.8 [(2)] - 2.4


VDDA(3)(4)


Analog operating voltage
(ADC limited to 1.2 M samples) Must be the same potential as

Analog operating voltage VDD(5)


Analog operating voltage VDD(5) V
2.4                                   - 3.6
(ADC limited to 1.4 M samples)


VBAT Backup operating voltage - 1.65 - 3.6 V


DS8626 Rev 12 81/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 14. General operating conditions (continued)**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


VOS bit in PWR_CR register = 0 [(1)]

1.08 1.14 1.20 V
Max frequency 144MHz


VOS bit in PWR_CR register= 1
1.20 1.26 1.32 V
Max frequency 168MHz


Max frequency 144MHz 1.10 1.14 1.20 V


Max frequency 168MHz 1.20 1.26 1.30 V


V12


VIN


Regulator ON:
1.2 V internal voltage on
VCAP_1/VCAP_2 pins


Regulator OFF:
1.2 V external voltage must be
supplied from external regulator
on VCAP_1/VCAP_2 pins


Input voltage on RST and FT 2 V ≤ VDD ≤ 3.6 V –0.3 - 5.5
pins [(6)] VDD ≤ 2 V –0.3 - 5.2

Input voltage on TTa pins - –0.3 - VDDA+
0.3


Input voltage on B pin - - - 5.5


LQFP64             -             - 435


LQFP100             -             - 465


V


mW


Power dissipation at TA = 85 °C
PD for suffix 6 or TA = 105 °C for
suffix 7 [(7)]


Ambient temperature for 6 suffix
version

TA

Ambient temperature for 7 suffix
version


Maximum power dissipation –40 - 85
°C
Low-power dissipation [(8)] –40 - 105


Maximum power dissipation –40 - 105
°C
Low-power dissipation [(8)] –40 - 125


LQFP144 - - 500


LQFP176 - - 526


UFBGA176 - - 513


WLCSP90 - - 543


6 suffix version –40                          - 105
TJ Junction temperature range °C
7 suffix version –40                          - 125


1. The average expected gain in power consumption when VOS = 0 compared to VOS = 1 is around 10% for the whole
temperature range, when the system clock frequency is between 30 and 144 MHz.

2. VDD/VDDA minimum value of 1.7 V is obtained when the device operates in reduced temperature range, and with the use of
an external power supply supervisor (refer to _Section 3.15.2: Internal reset OFF_ ).


3. When the ADC is used, refer to _Table 67: ADC characteristics_ .

4. If VREF+ pin is present, it must respect the following condition: VDDA-VREF+ < 1.2 V.

5. It is recommended to power VDD and VDDA from the same source. A maximum difference of 300 mV between VDD and
VDDA can be tolerated during power-up and power-down operation.

6. To sustain a voltage higher than VDD+0.3, the internal pull-up and pull-down resistors must be disabled.

7. If TA is lower, higher PD values are allowed as long as TJ does not exceed TJmax.

8. In low-power dissipation state, TA can be extended to this range as long as TJ does not exceed TJmax.


82/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 15. Limitations depending on the operating power supply range**


**Possible**
**flash**
**memory**
**operations**


8-bit erase
and program
operations
only


**Operating**
**power**
**supply**
**range**


**ADC**
**operation**


**Maximum**
**flash memory**
**access**
**frequency**
**with no wait**
**state**
**(fFlashmax)**


**Maximum flash**
**memory access**
**frequency** **Clock output**
**with wait** **I/O operation** **Frequency on**
**states** **[(1)]** **[(2)]** **I/O pins**


- up to
60 MHz
when VDD =
3.0 to 3.6 V

- up to
48 MHz
when VDD =
2.7 to 3.0 V


Conversion
VDD =1.8 to time up to 20 MHz [(4)] 160 MHz with 7
2.1 V [(3)] wait states
1.2 Msps


up to 30 MHz


- Degraded
speed
performance

- No I/O
compensation


- Degraded
speed
performance

- No I/O
compensation


- Degraded
speed
performance

- I/O
compensation
works


- Full-speed
operation

- I/O
compensation
works


16-bit erase
up to 30 MHz and program
operations


16-bit erase
up to 48 MHz and program
operations


VDD = 2.1 to
2.4 V


VDD = 2.4 to
2.7 V


Conversion
168 MHz with 7
time up to 22 MHz
wait states
1.2 Msps


Conversion
168 MHz with 6
time up to 24 MHz
wait states
2.4 Msps


Conversion
VDD = 2.7 to time up to 30 MHz 168 MHz with 5
3.6 V [(5)] wait states
2.4 Msps


32-bit erase
and program
operations


1. It applies only when code executed from flash memory access, when code executed from RAM, no wait state is required.


2. Thanks to the ART accelerator and the 128-bit flash memory, the number of wait states given here does not impact the
execution speed from flash memory since the ART accelerator allows to achieve a performance equivalent to 0 wait state
program execution.

3. VDD/VDDA minimum value of 1.7 V is obtained when the device operates in reduced temperature range, and with the use
of an external power supply supervisor (refer to _Section 3.15.2: Internal reset OFF_ ).


4. Prefetch is not available. Refer to AN3430 application note for details on how to adjust performance and power.


5. The voltage range for OTG USB FS can drop down to 2.7 V. However it is degraded between 2.7 and 3 V.


DS8626 Rev 12 83/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**6.3.2** **VCAP_1/VCAP_2 external capacitor**


Stabilization for the main regulator is achieved by connecting an external capacitor CEXT to
the VCAP_1/VCAP_2 pins. CEXT is specified in _Table 16_ .


**Figure 23. External capacitor CEXT**


C


ESR


R Leak

MS19044V2


1. Legend: ESR is the equivalent series resistance.


**Table 16. VCAP_1/VCAP_2 operating conditions** **[(1)]**

**Symbol** **Parameter** **Conditions**


CEXT Capacitance of external capacitor 2.2 µF


ESR ESR of external capacitor < 2 Ω


1. When bypassing the voltage regulator, the two 2.2 µF VCAP capacitors are not required and should be
replaced by two 100 nF decoupling capacitors.


**6.3.3** **Operating conditions at power-up / power-down (regulator ON)**


Subject to general operating conditions for TA.


**Table 17. Operating conditions at power-up / power-down (regulator ON)**


**Symbol** **Parameter** **Min** **Max** **Unit**


VDD rise time rate 20 ∞
tVDD µs/V
VDD fall time rate 20 ∞


**6.3.4** **Operating conditions at power-up / power-down (regulator OFF)**


Subject to general operating conditions for TA.


**Table 18. Operating conditions at power-up / power-down (regulator OFF)** **[(1)]**


**Symbol** **Parameter** **Conditions** **Min** **Max** **Unit**


VDD rise time rate Power-up 20 ∞
tVDD

VDD fall time rate Power-down 20 ∞


µs/V


tVCAP


VCAP_1 and VCAP_2 rise time Power-up 20 ∞
rate

VCAP_1 and VCAP_2 fall time Power-down 20 ∞
rate


1. To reset the internal logic at power-down, a reset must be applied on pin PA0 when VDD reach below
minimum value of V12.


84/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**6.3.5** **Embedded reset and power control block characteristics**


The parameters given in _Table 19_ are derived from tests performed under ambient
temperature and VDD supply voltage conditions summarized in _Table 14_ .


**Table 19. Embedded reset and power control block characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


PLS[2:0]=000 (rising
2.09 2.14 2.19 V
edge)


PLS[2:0]=000 (falling
1.98 2.04 2.08 V
edge)


PLS[2:0]=001 (rising
2.23 2.30 2.37 V
edge)


PLS[2:0]=001 (falling
2.13 2.19 2.25 V
edge)


PLS[2:0]=010 (rising
2.39 2.45 2.51 V
edge)


PLS[2:0]=010 (falling
2.29 2.35 2.39 V
edge)


PLS[2:0]=011 (rising edge) 2.54 2.60 2.65 V


Programmable voltage
VPVD detector level selection


PLS[2:0]=011 (falling
2.44 2.51 2.56 V
edge)


PLS[2:0]=100 (rising
2.70 2.76 2.82 V
edge)


PLS[2:0]=100 (falling
2.59 2.66 2.71 V
edge)


PLS[2:0]=101 (rising
2.86 2.93 2.99 V
edge)


PLS[2:0]=101 (falling
2.75 2.84 2.92 V
edge)


PLS[2:0]=110 (rising edge) 2.96 3.03 3.10 V


PLS[2:0]=110 (falling
2.85 2.93 2.99 V
edge)


PLS[2:0]=111 (rising edge) 3.07 3.14 3.21 V


PLS[2:0]=111 (falling
2.95 3.03 3.09 V
edge)


VPVDhyst(1) PVD hysteresis - - 100 - mV


Power-on/power-down
VPOR/PDR reset threshold


Falling edge 1.60 1.68 1.76 V


Rising edge 1.64 1.72 1.80 V


VPDRhyst(1) PDR hysteresis - - 40 - mV


Brownout level 1
VBOR1 threshold


Falling edge 2.13 2.19 2.24 V


Rising edge 2.23 2.29 2.33 V


DS8626 Rev 12 85/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 19. Embedded reset and power control block characteristics (continued)**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


Brownout level 2
VBOR2 threshold


Brownout level 3
VBOR3 threshold


Falling edge 2.44 2.50 2.56 V


Rising edge 2.53 2.59 2.63 V


Falling edge 2.75 2.83 2.88 V


Rising edge 2.85 2.92 2.97 V


VBORhyst(1) BOR hysteresis  -  - 100  - mV

TRSTTEMPO(1)(2) Reset temporization - 0.5 1.5 3.0 ms


InRush current on
IRUSH(1) voltage regulator power-on (POR or
wakeup from Standby)


InRush energy on
ERUSH(1) voltage regulator power-on (POR or
wakeup from Standby)


1. Specified by design.


-         - 160 200 mA


VDD = 1.8 V, TA = 105 °C, - - 5.4 µC
IRUSH = 171 mA for 31 µs


2. The reset temporization is measured from the power-on (POR reset or wakeup from VBAT) to the instant
when first instruction is read by the user application code.


**6.3.6** **Supply current characteristics**


The current consumption is a function of several parameters and factors such as the
operating voltage, ambient temperature, I/O pin loading, device software configuration,
operating frequencies, I/O pin switching rate, program location in memory and executed
binary code.
The current consumption is measured as described in _Figure 22: Current consumption_
_measurement scheme_ .


All Run mode current consumption measurements given in this section are performed using
a CoreMark-compliant code.


**Typical and maximum current consumption**


The MCU is placed under the following conditions:

- At startup, all I/O pins are configured as analog inputs by firmware.

- All peripherals are disabled except if it is explicitly mentioned.

- The flash memory access time is adjusted to fHCLK frequency (0 wait state from 0 to
30 MHz, 1 wait state from 30 to 60 MHz, 2 wait states from 60 to 90 MHz, 3 wait states
from 90 to 120 MHz, 4 wait states from 120 to 150 MHz, and 5 wait states from 150 to
168 MHz).

- When the peripherals are enabled HCLK is the system clock, fPCLK1 = fHCLK/4, and
fPCLK2 = fHCLK/2, except is explicitly mentioned.

- The maximum values are obtained for VDD = 3.6 V and maximum ambient temperature
(TA), and the typical values for TA= 25 °C and VDD = 3.3 V unless otherwise specified.


86/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 20. Typical and maximum current consumption in Run mode, code with data processing**
**running from flash memory (ART accelerator enabled) or RAM** **[(1)]**

**Typ** **Max** **[(2)]**


**Symbol** **Parameter** **Conditions** **fHCLK**


**Unit**
**TA =** **TA =** **TA =**
**25 °C** **85 °C** **105 °C**


168 MHz 87 102 109


144 MHz 67 80 86


120 MHz 56 69 75


90 MHz 44 56 62


60 MHz 30 42 49


30 MHz 16 28 35


25 MHz 12 24 31

16 MHz [(6)] 9 20 28


8 MHz 5 17 24


4 MHz 3 15 22


2 MHz 2 14 21


168 MHz 40 54 61


144 MHz 31 43 50


120 MHz 26 38 45


90 MHz 20 32 39


60 MHz 14 26 33


30 MHz 8 20 27


25 MHz 6 18 25

16 MHz [(6)] 5 16 24


8 MHz 3 15 22


4 MHz 2 14 21


2 MHz 2 14 21


Supply current in
IDD Run mode


External clock [(3)], all
peripherals enabled [(4)(5)]


External clock [(3)], all
peripherals disabled [(4)(5)]


mA


1. Code and data processing running from SRAM1 using boot pins.

2. Evaluated by characterization, tested in production at VDD max and fHCLK max with peripherals enabled.

3. External clock is 4 MHz and PLL is on when fHCLK > 25 MHz.

4. When the ADC is ON (ADON bit set in the ADC_CR2 register), add an additional power consumption of 1.6 mA per ADC for
the analog part.


5. When analog peripheral blocks such as ADCs, DACs, HSE, LSE, HSI, or LSI are ON, an additional power consumption
should be considered.


6. In this case HCLK = system clock/2.


DS8626 Rev 12 87/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 21. Typical and maximum current consumption in Run mode, code with data processing**
**running from flash memory (ART accelerator disabled)**

**Typ** **Max** **[(1)]**
**Symbol** **Parameter** **Conditions** **fHCLK** **Unit**

**TA = 25 °C** **TA = 85 °C** **TA = 105 °C**


168 MHz 93 109 117


144 MHz 76 89 96


120 MHz 67 79 86


90 MHz 53 65 73


60 MHz 37 49 56


30 MHz 20 32 39


25 MHz 16 27 35


16 MHz 11 23 30


8 MHz 6 18 25


4 MHz 4 16 23


2 MHz 3 15 22


168 MHz 46 61 69


144 MHz 40 52 60


120 MHz 37 48 56


90 MHz 30 42 50


60 MHz 22 33 41


30 MHz 12 24 31


25 MHz 10 21 29


16 MHz 7 19 26


8 MHz 4 16 23


4 MHz 3 15 22


2 MHz 2 14 21


Supply current
IDD in Run mode


External clock [(2)],
all peripherals
enabled [(3)(4)]


External clock [(2)],
all peripherals
disabled [(3)(4)]


mA


1. Evaluated by characterization, tested in production at VDD max and fHCLK max with peripherals enabled.

2. External clock is 4 MHz and PLL is on when fHCLK > 25 MHz.

3. When analog peripheral blocks such as (ADCs, DACs, HSE, LSE, HSI,LSI) are on, an additional power consumption
should be considered.


4. When the ADC is ON (ADON bit set in the ADC_CR2 register), add an additional power consumption of 1.6 mA per ADC
for the analog part.


88/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 24. Typical current consumption versus temperature, Run mode, code with data**
**processing running from flash (ART accelerator ON) or RAM, and peripherals OFF**













0 20 40 60 80 100 120 140 160 180


CPU Frequency (MHz


-45 °C


0 °C


25 °C


55 °C


85 °C


105 °C


MS19974V1


**Figure 25. Typical current consumption versus temperature, Run mode, code with data**
**processing running from flash (ART accelerator ON) or RAM, and peripherals ON**













0 20 40 60 80 100 120 140 160 180


CPU Frequency (MHz


-45°C


0°C


25°C


55°C


85°C


105°C


MS19975V1


DS8626 Rev 12 89/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 26. Typical current consumption versus temperature, Run mode, code with data**
**processing running from flash (ART accelerator OFF) or RAM, and peripherals OFF**









0 20 40 60 80 100 120 140 160 180


CPU Frequency (MHz


-45°C


0°C


25°C


55°C


85°C


105°C


MS19976V1


**Figure 27. Typical current consumption versus temperature, Run mode, code with data**
**processing running from flash (ART accelerator OFF) or RAM, and peripherals ON**








0 20 40 60 80 100 120 140 160 180


CPU Frequency (MHz


90/206 DS8626 Rev 12


-45°C


0°C


25°C


55°C


85°C


105°C


MS19977V1


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 22. Typical and maximum current consumption in Sleep mode**

**Typ** **Max** **[(1)]**


**Symbol** **Parameter** **Conditions** **fHCLK**


**Unit**
**TA =** **TA =** **TA =**
**25 °C** **85 °C** **105 °C**


168 MHz 59 77 84


144 MHz 46 61 67


120 MHz 38 53 60


90 MHz 30 44 51


60 MHz 20 34 41


30 MHz 11 24 31


25 MHz 8 21 28


16 MHz 6 18 25


8 MHz 3 16 23


4 MHz 2 15 22


2 MHz 2 14 21


168 MHz 12 27 35


144 MHz 9 22 29


120 MHz 8 20 28


90 MHz 7 19 26


60 MHz 5 17 24


30 MHz 3 16 23


25 MHz 2 15 22


16 MHz 2 14 21


8 MHz 1 14 21


4 MHz 1 13 21


2 MHz 1 13 21


Supply current in
IDD Sleep mode


External clock [(2)],
all peripherals enabled [(3)]


External clock [(2)], all
peripherals disabled


mA


1. Evaluated by characterization, tested in production at VDD max and fHCLK max with peripherals enabled.

2. External clock is 4 MHz and PLL is on when fHCLK > 25 MHz.

3. Add an additional power consumption of 1.6 mA per ADC for the analog part. In applications, this consumption occurs only
while the ADC is ON (ADON bit is set in the ADC_CR2 register).


DS8626 Rev 12 91/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 23. Typical and maximum current consumptions in Stop mode**


**Typ** **Max**


**Symbol** **Parameter** **Conditions**


**Unit**
**TA =** **TA =** **TA =** **TA =**
**25 °C** **25 °C** **85 °C** **105 °C**


Flash in Stop mode, low-speed and highspeed internal RC oscillators and high-speed 0.45 1.5 11.00 20.00
oscillator OFF (no independent watchdog)


Flash in Deep power-down mode, low-speed
and high-speed internal RC oscillators and
high-speed oscillator OFF (no independent
watchdog)


0.40 1.5 11.00 20.00


IDD_STOP


Supply
current in
Stop mode
with main
regulator in
Run mode


Supply
current in
Stop mode
with main
regulator in
Low-power
mode


Flash in Deep power-down mode, low-speed
and high-speed internal RC oscillators and
high-speed oscillator OFF (no independent
watchdog)


Flash in Stop mode, low-speed and highspeed internal RC oscillators and high-speed 0.31 1.1 8.00 15.00
oscillator OFF (no independent watchdog)


mA


0.28 1.1 8.00 15.00


**Table 24. Typical and maximum current consumptions in Standby mode**

**Typ** **Max** **[(1)]**


**Symbol** **Parameter** **Conditions**


**TA = 25 °C** **85 °CTA =** **105 °CTA =** **Unit**


**V1.8 VDD =** **V2.4 VDD=** **V3.3 VDD =** **VDD = 3.6 V**


Supply current
IDD_STBY in Standby
mode


Backup SRAM ON, low3.0 3.4 4.0 20 36
speed oscillator and RTC ON


Backup SRAM OFF, low2.4 2.7 3.3 16 32
speed oscillator and RTC ON


Backup SRAM ON, RTC
2.4 2.6 3.0 12.5 24.8
OFF


Backup SRAM OFF, RTC
1.7 1.9 2.2 9.8 19.2
OFF


µA


1. Evaluated by characterization - not tested in production.


92/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 25. Typical and maximum current consumptions in VBAT mode**

**Typ** **Max** **[(1)]**


**Symbol** **Parameter** **Conditions**


**TA = 25 °C** **85 °CTA =** **105 °CTA =**
**Unit**


**VBAT**
**=**
**1.8 V**


**VBAT=**
**2.4 V**


**VBAT**
**=** **VBAT = 3.6 V**
**3.3 V**


Backup SRAM ON, low-speed
1.29 1.42 1.68 6 11
oscillator and RTC ON


Backup SRAM OFF, low-speed
oscillator and RTC ON 0.62 0.73 0.96 3 5 µA


Backup SRAM ON, RTC OFF 0.79 0.81 0.86 5 10


Backup SRAM OFF, RTC OFF 0.10 0.10 0.10 2 4


IDD_VBA

T


Backup
domain
supply
current


1. Evaluated by characterization - not tested in production.


**Figure 28. Typical VBAT current consumption (LSE and RTC ON/backup RAM OFF)**


3.5



2.5



1.5



0.5



1.65V


1.8V


2V


2.4V


2.7V


3V


3.3V


3.6V


0 10 20 30 40 50 60 70 80 90 100


**Temperature in (°C)**


MS19990V1


DS8626 Rev 12 93/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 29. Typical VBAT current consumption (LSE and RTC ON/backup RAM ON)**









1.65V


1.8V


2V


2.4V


2.7V


3V


3.3V


3.6V


0 10 20 30 40 50 60 70 80 90 100


**Temperature in (°C)**


MS19991V1


**Additional current consumption**


The MCU is placed under the following conditions:

- All I/O pins are configured in analog mode.

- The flash memory access time is adjusted to fHCLK frequency.

- The voltage scaling is adjusted to fHCLK frequency as follows:

- Scale 2 for fHCLK ≤ 144 MHz

- Scale 1 for 144 MHz < fHCLK ≤ 168 MHz.

- The system clock is HCLK, fPCLK1 = fHCLK/4, and fPCLK2 = fHCLK/2.

- The HSE crystal clock frequency is 25 MHz.

- TA= 25 °C.


94/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 26. Typical current consumption in Run mode, code with data processing**
**running from flash memory, regulator ON (ART accelerator enabled**
**except prefetch), VDD = 1.8 V** **[(1)]**

**Symbol** **Parameter** **Conditions** **fHCLK (MHz)** **Typ. at T25 °CA =** **Unit**


160 36.2


144 29.3


120 24.7


Supply current in All peripheral
IDD
Run mode disabled


90 19.3


60 13.4


30 7.7


25 6.0


mA


1. When peripherals are enabled, the power consumption corresponding to the analog part of the peripherals
(such as ADC or DAC) is not included.


**I/O system current consumption**


The current consumption of the I/O system has two components: static and dynamic.


I/O static current consumption


All the I/Os used as input with pull-up or pull-down generate current consumption when the
pin is externally held to the opposite level. The value of this current consumption can be
simply computed by using the pull-up/pull-down resistors values given in _Table 48: I/O static_
_characteristics_ .


For the output pins, any internal or external pull-up or pull-down and external load must also
be considered to estimate the current consumption.


Additional I/O current consumption is due to I/Os configured as inputs if an intermediate
voltage level is externally applied. This current consumption is caused by the input Schmitt
trigger circuits used to discriminate the input value. Unless this specific configuration is
required by the application, this supply current consumption can be avoided by configuring
these I/Os in analog mode. This is notably the case of ADC input pins which should be
configured as analog inputs.


**Caution:** Any floating input pin can also settle to an intermediate voltage level or switch inadvertently,
as a result of external electromagnetic noise. To avoid current consumption related to
floating pins, they must either be configured in analog mode, or forced internally to a definite
digital value. This can be done either by using pull-up/down resistors or by configuring the
pins in output mode.


I/O dynamic current consumption


In addition to the internal peripheral current consumption measured previously (see
_Table 28: Peripheral current consumption_ ), the I/Os used by an application also contribute
to the current consumption. When an I/O pin switches, it uses the current from the MCU
supply voltage to supply the I/O pin circuitry and to charge/discharge the capacitive load
internal and external connected to the pin:


ISW = VDD × fSW × C


DS8626 Rev 12 95/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


where

ISW is the current sunk by a switching I/O to charge/discharge the capacitive load

VDD is the MCU supply voltage

fSW is the I/O switching frequency

C is the total capacitance seen by the I/O pin: C = CINT+ CEXT

The test pin is configured in push-pull output mode and is toggled by software at a fixed
frequency.


96/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 27. Switching output I/O current consumption**


**I/O toggling**
**Symbol** **Parameter** **Conditions** **[(1)]** **Typ** **Unit**
**frequency (fSW)**


2 MHz 0.02


8 MHz 0.14


25 MHz 0.51


50 MHz 0.86


60 MHz 1.30


2 MHz 0.10


8 MHz 0.38


25 MHz 1.18


50 MHz 2.47


60 MHz 2.86


2 MHz 0.17


8 MHz 0.66


25 MHz 1.70


50 MHz 2.65


60 MHz 3.48


2 MHz 0.23


8 MHz 0.95


25 MHz 3.20


50 MHz 4.69


60 MHz 8.06


2 MHz 0.30


8 MHz 1.22


25 MHz 3.90


50 MHz 8.82

60 MHz - [(3)]


I/O switching
IDDIO current


VDD = 3.3 V [(2)]

C = CINT


VDD = 3.3 V
CEXT = 0 pF
C = CINT + CEXT+ CS


VDD = 3.3 V
CEXT = 10 pF
C = CINT + CEXT+ CS


VDD = 3.3 V
CEXT = 22 pF
C = CINT + CEXT+ CS


VDD = 3.3 V
CEXT = 33 pF
C = CINT + CEXT+ CS


mA


1. CS is the PCB board capacitance including the pad pin. CS = 7 pF (estimated value).

2. This test is performed by cutting the LQFP package pin (pad removal).


3. At 60 MHz, C maximum load is specified 30 pF.


DS8626 Rev 12 97/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**On-chip peripheral current consumption**


The current consumption of the on-chip peripherals is given in _Table 28_ . The MCU is placed
under the following conditions:

- At startup, all I/O pins are configured as analog pins by firmware.

- All peripherals are disabled unless otherwise mentioned

- The code is running from flash memory and the flash memory access time is equal to 5
wait states at 168 MHz.

- The code is running from flash memory and the flash memory access time is equal to 4
wait states at 144 MHz, and the power scale mode is set to 2.

- The ART accelerator is ON.

- The given value is calculated by measuring the difference of current consumption

- with all peripherals clocked off

- with one peripheral clocked on (with only the clock applied)

- When the peripherals are enabled: HCLK is the system clock, fPCLK1 = fHCLK/4, and
fPCLK2 = fHCLK/2.

- The typical values are obtained for VDD = 3.3 V and TA= 25 °C, unless otherwise
specified.


**Table 28. Peripheral current consumption**

**IDD(Typ)** **[(1)]**


**Peripheral**


**Unit**
**Scale1** **Scale2**


**(up t 168 MHz)**


**(up to 144 MHz)**


AHB1
(up to 168 MHz)


GPIOA 2.70 2.40


GPIOB 2.50 2.22


GPIOC 2.54 2.28


GPIOD 2.55 2.28


GPIOE 2.68 2.40


GPIOF 2.53 2.28


GPIOG 2.51 2.22


GPIOH 2.51 2.22


GPIOI 2.50 2.22


OTG_HS+ULPI 28.33 25.38


CRC 0.41 0.40


BKPSRAM 0.63 0.58


DMA1 37.44 33.58


DMA2 37.69 33.93


µA/MHz


ETH_MAC
ETH_MAC_TX
ETH_MAC_RX
ETH_MAC_PTP


98/206 DS8626 Rev 12


20.43 18.39


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 28. Peripheral current consumption (continued)**

**IDD(Typ)** **[(1)]**


**Peripheral**


AHB2
(up to 168 MHz)


OTG_FS 26.45 26.67


DCMI 5.87 5.35 µA/MHz


RNG 1.50 1.67


**Unit**
**Scale1** **Scale2**


**(up t 168 MHz)**


**(up to 144 MHz)**


AHB3
FSMC 12.46 11.31 µA/MHz
(up to 168 MHz)


Bus matrix [(2)] 13.10 11.81 µA/MHz


TIM2 16.71 16.50


TIM3 12.33 11.94


TIM4 13.45 12.92


TIM5 17.14 16.58


TIM6 2.43 3.06


TIM7 2.43 2.22


TIM12 6.62 6.83


TIM13 5.05 5.47


TIM14 5.26 5.61


PWR 1.00 0.56


USART2 2.69 2.78


USART3 2.74 2.78


APB1
(up to 42 MHz)


UART4 3.24 3.33


UART5 2.69 2.78


I2C1 2.67 2.50


I2C2 2.83 2.78


I2C3 2.81 2.78


SPI2 2.43 2.22


SPI3 2.43 2.22

I2S2 [(3)] 2.43 2.22

I2S3 [(3)] 2.26 2.22


CAN1 5.12 5.56


CAN2 4.81 5.28

DAC [(4)] 1.67 1.67


WWDG 1.00 0.83


µA/MHz


DS8626 Rev 12 99/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 28. Peripheral current consumption (continued)**

**IDD(Typ)** **[(1)]**


**Peripheral**


APB2
(up to 84 MHz)


SDIO 7.08 7.92


TIM1 16.79 15.51


TIM8 17.88 16.53


TIM9 7.64 7.28


TIM10 4.89 4.82


TIM11 5.19 4.82

ADC1 [(5)] 4.67 4.58

ADC2 [(5)] 4.67 4.58

ADC3 [(5)] 4.43 4.44


SPI1 1.32 1.39


USART1 3.51 3.72


USART6 3.55 3.75


SYSCFG 0.74 0.56


**Unit**
**Scale1** **Scale2**


**(up t 168 MHz)**


**(up to 144 MHz)**


µA/MHz


1. When the I/O compensation cell is ON, IDD typical value increases by 0.22 mA.

2. The BusMatrix is automatically active when at least one master is ON.


3. To enable an I2S peripheral, first set the I2SMOD bit and then the I2SE bit in the SPI_I2SCFGR register.


4. When the DAC is ON and EN1/2 bits are set in DAC_CR register, add an additional power consumption of
0.8 mA per DAC channel for the analog part.


5. When the ADC is ON (ADON bit set in the ADC_CR2 register), add an additional power consumption of
1.6 mA per ADC for the analog part.


**6.3.7** **Wakeup time from low-power mode**


The wakeup times given in _Table 29_ is measured on a wakeup phase with a 16 MHz HSI
RC oscillator. The clock source used to wake up the device depends from the current
operating mode:

- Stop or Standby mode: the clock source is the RC oscillator

- Sleep mode: the clock source is the clock that was set before entering Sleep mode.


All timings are derived from tests performed under ambient temperature and VDD supply
voltage conditions summarized in _Table 14_ .


100/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 29. Low-power mode wakeup timings**

**Symbol** **Parameter** **Min** **[(1)]** **Typ** **[(1)]** **Max** **[(1)]** **Unit**


CPU
tWUSLEEP(2) Wakeup from Sleep mode   - 5   - clock
cycle


Wakeup from Stop mode (regulator in Run mode and

- 13                                                        flash memory in Stop mode)


tWUSTOP(2)


Wakeup from Stop mode (regulator in low-power mode

- 17 40
and flash memory in Stop mode)


Wakeup from Stop mode (regulator in Run mode and

- 105                                          flash memory in Deep power-down mode)


Wakeup from Stop mode (regulator in low-power mode

- 110                                          and flash memory in Deep power-down mode)


µs


tWUSTDBY(2)(3) Wakeup from Standby mode 260 375 480 µs


1. Evaluated by characterization - not tested in production.


2. The wakeup times are measured from the wakeup event to the point in which the application code reads the first instruction.

3. tWUSTDBY minimum and maximum values are given at 105 °C and –45 °C, respectively.


**6.3.8** **External clock source characteristics**


**High-speed external user clock generated from an external source**


The characteristics given in _Table 30_ result from tests performed using an high-speed
external clock source, and under ambient temperature and supply voltage conditions
summarized in _Table 14_ .


**Table 30. High-speed external user clock characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


External user clock source
fHSE_ext frequency [(1)]


1 - 50 MHz


VHSEH OSC_IN input pin high level voltage 0.7VDD - VDD
V
VHSEL OSC_IN input pin low level voltage - VSS - 0.3VDD


tw(HSE) OSC_IN high or low time [(1)]
tw(HSE)


5 - 


ns
tr(HSE) OSC_IN rise or fall time [(1)] - - 10
tf(HSE)


Cin(HSE) OSC_IN input capacitance [(1)]  -  - 5  - pF

DuCy(HSE) Duty cycle - 45 - 55 %

IL OSC_IN Input leakage current VSS ≤ VIN ≤ VDD    -    - ±1 µA


1. Specified by design.


DS8626 Rev 12 101/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Low-speed external user clock generated from an external source**


The characteristics given in _Table 31_ result from tests performed using an low-speed
external clock source, and under ambient temperature and supply voltage conditions
summarized in _Table 14_ .


**Table 31. Low-speed external user clock characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


User External clock source
fLSE_ext frequency [(1)]


- 32.768 1000 kHz


OSC32_IN input pin high level
VLSEH voltage 0.7VDD  - VDD V

VLSEL OSC32_IN input pin low level voltage  - VSS  - 0.3VDD

tw(LSE) OSC32_IN high or low time [(1)] 450   -   tf(LSE)

ns
tr(LSE) OSC32_IN rise or fall time [(1)]   -   - 50
tf(LSE)

Cin(LSE) OSC32_IN input capacitance [(1)]  -  - 5  - pF

DuCy(LSE) Duty cycle  - 30  - 70 %

IL OSC32_IN Input leakage current VSS ≤ VIN ≤ VDD     -     - ±1 µA


1. Specified by design.


**Figure 30. High-speed external clock source AC timing diagram**


VHSEH

90%

10 %

VHSEL


tr(HSE) tf(HSE) tW(HSE) tW(HSE) t

~~T~~ HS ~~E~~


fHSE_ext


IL


External

clock source OSC_IN


clock source


STM32F


ai17528


102/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 31. Low-speed external clock source AC timing diagram**


VLSEH

90%


VLSEL


10%


tr(LSE) tf(LSE) tW(LSE) tW(LSE) t

TLSE


fLSE_ext


IL


External
OSC32_IN


clock source


STM32F


**High-speed external clock generated from a crystal/ceramic resonator**


ai17529


The high-speed external (HSE) clock can be supplied with a 4 to 26 MHz crystal/ceramic
resonator oscillator. All the information given in this paragraph are based on
characterization results obtained with typical external components specified in _Table 32_ . In
the application, the resonator and the load capacitors have to be placed as close as
possible to the oscillator pins in order to minimize output distortion and startup stabilization
time. Refer to the crystal resonator manufacturer for more details on the resonator
characteristics (frequency, package, accuracy).


**Table 32. HSE 4-26 MHz oscillator characteristics** **[(1)]**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


fOSC_IN Oscillator frequency  - 4  - 26 MHz

RF Feedback resistor   -   - 200   - k Ω

Gm Oscillator transconductance 5  -  Startup mA/V
Gmcritmax Maximum critical crystal Gm  -  - 1


tSU(HSE)(2)


Startup time VDD is stabilized - 2 - ms


1. Specified by design.

2. Evaluated by characterization - not tested in production. tSU(HSE) is the startup time measured from the
moment it is enabled (by software) to a stabilized 8 MHz oscillation is reached. This value is measured for
a standard crystal resonator and can vary significantly with the crystal manufacturer


For CL1 and CL2, it is recommended to use high-quality external ceramic capacitors in the
5 pF to 25 pF range (typ.), designed for high-frequency applications, and selected to match
the requirements of the crystal or resonator (see _Figure 32_ ). CL1 and CL2 are usually the
same size. The crystal manufacturer typically specifies a load capacitance which is the
series combination of CL1 and CL2. PCB and MCU pin capacitance must be included (10 pF
can be used as a rough estimate of the combined pin and board capacitance) when sizing
CL1 and CL2.


DS8626 Rev 12 103/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


_Note:_ _For information on electing the crystal, refer to the application note AN2867 “Oscillator_
_design guide for ST microcontrollers” available from the ST website www.st.com._


**Figure 32. Typical application with an 8 MHz crystal**


Resonator with
integrated capacitors

~~C~~ L1
OSC_IN fHSE


8 MHz
resonator


CL2 REXT [(1)]


ai17530


RF


OSC_OUT


Bias
controlled
gain


STM32F


1. REXT value depends on the crystal characteristics.


**Low-speed external clock generated from a crystal/ceramic resonator**


The low-speed external (LSE) clock can be supplied with a 32.768 kHz crystal/ceramic
resonator oscillator. All the information given in this paragraph are based on
characterization results obtained with typical external components specified in _Table 33_ . In
the application, the resonator and the load capacitors have to be placed as close as
possible to the oscillator pins in order to minimize output distortion and startup stabilization
time. Refer to the crystal resonator manufacturer for more details on the resonator
characteristics (frequency, package, accuracy).


**Table 33. LSE oscillator characteristics (fLSE = 32.768 kHz)** **[(1)]**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


fOSC_IN Oscillator frequency  -  - 32.768  - kHz

RF Feedback resistor   -   - 18.4   - M Ω

IDD LSE current consumption   -   -   - 1 µA

Gm Oscillator transconductance 2.8  -  Startup µA/V
Gmcritmax Maximum critical crystal Gm  -  - 0.56


tSU(LSE)(2)


Startup time VDD is stabilized - 2 - s


1. Specified by design.

2. Evaluated by characterization - not tested in production. tSU(LSE) is the startup time measured from the
moment it is enabled (by software) to a stabilized 32.768 kHz oscillation is reached. This value is
measured for a standard crystal resonator and it can vary significantly with the crystal manufacturer


_Note:_ _For information on electing the crystal, refer to the application note AN2867 “Oscillator_
_design guide for ST microcontrollers” available from the ST website www.st.com._


104/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 33. Typical application with a 32.768 kHz crystal**


Resonator with
integrated capacitors

~~C~~ L1
OSC32_IN fLSE


32.768 kHz
resonator


RF


OSC32_OUT


Bias
controlled
gain


STM32F


CL2


ai17531


**6.3.9** **Internal clock source characteristics**


The parameters given in _Table 34_ and _Table 35_ are derived from tests performed under
ambient temperature and VDD supply voltage conditions summarized in _Table 14_ .


**High-speed internal (HSI) RC oscillator**


**Table 34. HSI oscillator characteristics** **[(1)]**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


fHSI Frequency           -           - 16           - MHz


TA = –10 to 85 °C [(3)] –4 - 4 %


- - - 1 %


ACCHSI


HSI user trimming step [(2)]


Accuracy of the HSI oscillator


TA = –40 to 105 °C [(3)]


–8 - 4.5 %


TA = 25 °C [(4)]


–1 - 1 %


tsu(HSI)(2) HSI oscillator startup time  -  - 2.2 4 µs

IDD(HSI)(2) HSI oscillator power consumption  -  - 60 80 µA


1. VDD = 3.3 V, PLL OFF, TA = –40 to 125 °C unless otherwise specified.

2. Specified by design.


3. Evaluated by characterization - not tested in production.


4. Factory calibrated, parts not soldered.


**Low-speed internal (LSI) RC oscillator**


**Table 35. LSI oscillator characteristics** **[(1)]**


**Symbol** **Parameter** **Min** **Typ** **Max** **Unit**


fLSI(2)

tsu(LSI)(3)


Frequency 17 32 47 kHz


LSI oscillator startup time - 15 40 µs


IDD(LSI)(3) LSI oscillator power consumption   - 0.4 0.6 µA


1. VDD = 3 V, TA = –40 to 105 °C unless otherwise specified.

2. Evaluated by characterization - not tested in production.


3. Specified by design.


DS8626 Rev 12 105/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 34. ACCLSI versus temperature**



max







-10


-20


-30


-40


-45 -35 -25 -15 -5 5 15 25 35 45 55 65 75 85 95 105

Temperature (°C)


**6.3.10** **PLL characteristics**


avg


min


MS19013V1


The parameters given in _Table 36_ and _Table 37_ are derived from tests performed under
temperature and VDD supply voltage conditions summarized in _Table 14_ .


**Table 36. Main PLL characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


fPLL_IN PLL input clock [(1)] - 0.95 [(2)] 1 2.10 MHz

fPLL_OUT PLL multiplier output clock - 24 - 168 MHz


48 MHz PLL multiplier output
fPLL48_OUT clock - - 48 75 MHz


fVCO_OUT PLL VCO output - 100 - 432 MHz


VCO freq = 100 MHz 75                       - 200
tLOCK PLL lock time µs
VCO freq = 432 MHz 100                       - 300


106/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 36. Main PLL characteristics (continued)**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


RMS                      - 25                      


Cycle-to-cycle jitter


Period Jitter


System clock
120 MHz


peak
to - ± 150 peak


RMS - 15 

peak
to - ± 200 peak


Jitter [(3)]


ps


Main clock output (MCO) for Cycle to cycle at 50 MHz

- 32                                                       RMII Ethernet on 1000 samples


Main clock output (MCO) for MII Cycle to cycle at 25 MHz

- 40                                                       Ethernet on 1000 samples


Cycle to cycle at 1 MHz
Bit Time CAN jitter         - 330         on 1000 samples

IDD(PLL)(4) PLL power consumption on VDD VCO freq = 100 MHzVCO freq = 432 MHz 0.150.45  - 0.400.75 mA

IDDA(PLL)(4) PLL power consumption on VDDA VCO freq = 100 MHzVCO freq = 432 MHz 0.300.55  - 0.400.85 mA


1. Take care of using the appropriate division factor M to obtain the specified PLL input clock values. The M factor is shared
between PLL and PLLI2S.


2. Specified by design.


3. The use of 2 PLLs in parallel could degraded the Jitter up to +30%.


4. Evaluated by characterization - not tested in production.


**Table 37. PLLI2S (audio PLL) characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


fPLLI2S_IN PLLI2S input clock [(1)] - 0.95 [(2)] 1 2.10 MHz

fPLLI2S_OUT PLLI2S multiplier output clock - - - 216 MHz

fVCO_OUT PLLI2S VCO output - 100 - 432 MHz


VCO freq = 100 MHz 75                      - 200
tLOCK PLLI2S lock time µs
VCO freq = 432 MHz 100                      - 300


RMS - 90 

peak
to  - ± 280  - ps
peak


Master I [2] S clock jitter
Jitter [(3)]


Cycle to cycle at
12.288 MHz on
48KHz period,
N=432, R=5


Average frequency of
12.288 MHz
N = 432, R = 5
on 1000 samples


- 90 - ps


Cycle to cycle at 48 KHz
WS I [2] S clock jitter - 400 - ps
on 1000 samples


DS8626 Rev 12 107/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 37. PLLI2S (audio PLL) characteristics (continued)**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


IDD(PLLI2S)(4) PLLI2S power consumption on VDD


(4) [PLLI2S power consumption on ]
IDDA(PLLI2S) VDDA


VCO freq = 100 MHz 0.15 0.40

- mA
VCO freq = 432 MHz 0.45 0.75


VCO freq = 100 MHz 0.30 0.40

- mA
VCO freq = 432 MHz 0.55 0.85


1. Take care of using the appropriate division factor M to have the specified PLL input clock values.


2. Specified by design.


3. Value given with main PLL running.


4. Evaluated by characterization - not tested in production.


**6.3.11** **PLL spread spectrum clock generation (SSCG) characteristics**


The spread spectrum clock generation (SSCG) feature allows to reduce electromagnetic
interferences (see _Table 44: EMI characteristics for fHSE = 25 MH and fCPU = 168 MHz_ ). It
is available only on the main PLL.


**Table 38. SSCG parameters constraint**

**Symbol** **Parameter** **Min** **Typ** **Max** **[(1)]** **Unit**


fMod Modulation frequency       -       - 10 KHz


md Peak modulation depth 0.25     - 2 %

MODEPER * INCSTEP  -  -  - 2 [15]  - 1  

1. Specified by design.


Equation 1


The frequency modulation period (MODEPER) is given by the equation below:


MODEPER = round [ fPLL_IN ⁄ ( 4 × fMod )]


fPLL_IN and fMod must be expressed in Hz.

As an example:


If fPLL_IN = 1 MHz, and fMOD = 1 kHz, the modulation depth (MODEPER) is given by
equation 1:


MODEPER = round [ 10 [6] ⁄ ( 4 × 10 [3] )] = 250


Equation 2


Equation 2 allows to calculate the increment step (INCSTEP):

INCSTEP = round [(( 2 [15]          - 1 ) × md × PLLN ) ⁄ ( 100 × 5 × MODEPER )]


fVCO_OUT must be expressed in MHz.


108/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


With a modulation depth (md) = ±2 % (4 % peak to peak), and PLLN = 240 (in MHz):


INCSTEP = round [(( 2 [15]       - 1 ) × 2 × 240 ) ⁄ ( 100 × 5 × 250 )] = 126md(quantitazed)%


An amplitude quantization error may be generated because the linear modulation profile is
obtained by taking the quantized values (rounded to the nearest integer) of MODPER and
INCSTEP. As a result, the achieved modulation depth is quantized. The percentage
quantized modulation depth is given by the following formula:

mdquantized% = ( MODEPER × INCSTEP × 100 × 5 ) ⁄ (( 2 [15]            - 1 ) × PLLN )


As a result:

mdquantized% = ( 250 × 126 × 100 × 5 ) ⁄ (( 2 [15]            - 1 ) × 240 ) = 2.002%(peak)


_Figure 35_ and _Figure 36_ show the main PLL output clock waveforms in center spread and
down spread modes, where:

F0 is fPLL_OUT nominal.

Tmode is the modulation period.

md is the modulation depth.


**Figure 35. PLL output clock waveforms in center spread mode**


Frequency (PLL_OUT)


md


F0


md


tmode 2xtmode


Time


ai17291


DS8626 Rev 12 109/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 36. PLL output clock waveforms in down spread mode**


Frequency (PLL_OUT)


F0


2xmd


tmode 2xtmode


Time


ai17292b


**6.3.12** **Memory characteristics**


**Flash memory**


The characteristics are given at TA = –40 to 105 °C unless otherwise specified.

The devices are shipped to customers with the flash memory erased.


**Table 39. Flash memory characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


Write / Erase 8-bit mode, VDD = 1.8 V                    - 5                    


IDD Supply current


Write / Erase 16-bit mode, VDD = 2.1 V - 8 - mA

Write / Erase 32-bit mode, VDD = 3.3 V - 12 

**Table 40. Flash memory programming**


**Symbol** **Parameter** **Conditions** **Min** **[(1)]** **Typ** **Max** **[(1)]** **Unit**


Program/erase parallelism
tprog Word programming time (PSIZE) = x 8/16/32  - 16 100 [(2)] µs


Program/erase parallelism

- 400 800
(PSIZE) = x 8


tERASE16KB Sector (16 KB) erase time


tERASE64KB Sector (64 KB) erase time


Program/erase parallelism

- 300 600 ms
(PSIZE) = x 16


Program/erase parallelism

- 250 500
(PSIZE) = x 32


Program/erase parallelism

- 1200 2400
(PSIZE) = x 8


Program/erase parallelism

- 700 1400 ms
(PSIZE) = x 16


Program/erase parallelism

- 550 1100
(PSIZE) = x 32


110/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 40. Flash memory programming (continued)**

**Symbol** **Parameter** **Conditions** **Min** **[(1)]** **Typ** **Max** **[(1)]** **Unit**


Program/erase parallelism

- 2 4
(PSIZE) = x 8


tERASE128KB Sector (128 KB) erase time


tME Mass erase time


Vprog Programming voltage


Program/erase parallelism

- 1.3 2.6 s
(PSIZE) = x 16


Program/erase parallelism

- 1 2
(PSIZE) = x 32


Program/erase parallelism

- 16 32
(PSIZE) = x 8


Program/erase parallelism

- 11 22 s
(PSIZE) = x 16


Program/erase parallelism

- 8 16
(PSIZE) = x 32


32-bit program operation 2.7 - 3.6 V


16-bit program operation 2.1 - 3.6 V


8-bit program operation 1.8 - 3.6 V


1. Evaluated by characterization - not tested in production.


2. The maximum programming time is measured after 100K erase operations.


DS8626 Rev 12 111/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 41. Flash memory programming with VPP**


**Symbol** **Parameter** **Conditions** **Min** **[(1)]** **Typ** **Max** **[(1)]**


**Unit**


µs


tprog Double word programming


- 16 100 [(2)]


tERASE16KB Sector (16 KB) erase time - 230 


TA = 0 to +40 °C
VDD = 3.3 V
VPP = 8.5 V


tERASE64KB Sector (64 KB) erase time VDD = 3.3 V - 490 - ms


tERASE128KB Sector (128 KB) erase time PP - 875 


tME Mass erase time - 6.9 - s

Vprog Programming voltage - 2.7 - 3.6 V

VPP VPP voltage range - 7 - 9 V


Minimum current sunk on
IPP the VPP pin  - 10  -  - mA


tVPP(3)


Cumulative time during

-                    -                    - 1 hour
which VPP is applied


1. Specified by design.


2. The maximum programming time is measured after 100K erase operations.

3. VPP should only be connected during programming/erasing.


**Table 42. Flash memory endurance and data retention**


**Value**
**Symbol** **Parameter** **Conditions** **Unit**
**Min** **[(1)]**

NEND Endurance TTAA = –40 to +85 °C (6 suffix versions) = –40 to +105 °C (7 suffix versions) 10 kcycles


1 kcycle [(2)] at TA = 85 °C



tRET Data retention


1 kcycle [(2)] at TA = 105 °C 10 Years

10 kcycles [(2)] at TA = 55 °C 20


1. Evaluated by characterization - not tested in production.


2. Cycling performed over the whole temperature range.


**6.3.13** **EMC characteristics**


Susceptibility tests are performed on a sample basis during device characterization.


**Functional EMS (electromagnetic susceptibility)**


While a simple application is executed on the device (toggling 2 LEDs through I/O ports).
the device is stressed by two electromagnetic events until a failure occurs. The failure is
indicated by the LEDs:

- **Electrostatic discharge (ESD)** (positive and negative) is applied to all device pins until
a functional disturbance occurs. This test is compliant with the IEC 61000-4-2 standard.

- **FTB** : A burst of fast transient voltage (positive and negative) is applied to VDD and VSS
through a 100 pF capacitor, until a functional disturbance occurs. This test is compliant
with the IEC 61000-4-4 standard.


112/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


A device reset allows normal operations to be resumed.


The test results are given in _Table 43_ . They are based on the EMS levels and classes
defined in application note AN1709.


**Table 43. EMS characteristics**


**Level/**
**Symbol** **Parameter** **Conditions**
**Class**


Voltage limits to be applied on any I/O pin to
VFESD induce a functional disturbance


Fast transient voltage burst limits to be
VEFTB applied through 100 pF on VDD and VSS
pins to induce a functional disturbance


VDD = 3.3 V, LQFP176, TA = +25 °C,
fHCLK = 168 MHz, conforms to 2B
IEC 61000-4-2


VDD = 3.3 V, LQFP176, TA = +25 °C,
fHCLK = 168 MHz, conforms to 4A
IEC 61000-4-2


**Designing hardened software to avoid noise problems**


EMC characterization and optimization are performed at component level with a typical
application environment and simplified MCU software. It should be noted that good EMC
performance is highly dependent on the user application and the software in particular.


Therefore it is recommended that the user applies EMC software optimization and
prequalification tests in relation with the EMC level requested for his application.


Software recommendations


The software flowchart must include the management of runaway conditions such as:

- Corrupted program counter

- Unexpected reset

- Critical Data corruption (control registers...)


Prequalification trials


Most of the common failures (unexpected reset and program counter corruption) can be
reproduced by manually forcing a low state on the NRST pin or the Oscillator pins for 1
second.


To complete these trials, ESD stress can be applied directly on the device, over the range of
specification values. When unexpected behavior is detected, the software can be hardened
to prevent unrecoverable errors occurring (see application note AN1015).


DS8626 Rev 12 113/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Electromagnetic Interference (EMI)**


The electromagnetic field emitted by the device are monitored while a simple application,
executing EEMBC code, is running. This emission test is compliant with SAE IEC61967-2
standard which specifies the test board and the pin loading.


**Table 44. EMI characteristics for fHSE = 25 MH and fCPU = 168 MHz**


**Monitored**
**Symbol** **Parameter** **Conditions** **Value** **Unit**
**frequency band**


VDD = 3.3 V, TA = 25 °C, LQFP176
Peak [(1)] package, conforming to SAE J1752/3
EEMBC, code running from flash
memory with ART accelerator enabled


0.1 to 30 MHz 32


30 to 130 MHz 25 dBµV


130 MHz to 1GHz 29


SEMI


Level [(2)] 0.1 MHz to 2 GHz 4 


VDD = 3.3 V, TA = 25 °C, LQFP176
Peak [(1)] package, conforming to SAE J1752/3
EEMBC, code running from flash
memory with ART accelerator and PLL

[(2)] spread spectrum enabled


0.1 to 30 MHz 19


30 to 130 MHz 16 dBµV


130 MHz to 1GHz 18


spread spectrum enabled

Level [(2)] 0.1 MHz to 2 GHz 3.5 


1. Refer to AN1709 "EMI radiated test" chapter.


2. Refer to AN1709 "EMI level classification" chapter.


**6.3.14** **Absolute maximum ratings (electrical sensitivity)**


Stresses above the absolute maximum ratings listed in _Table 11: Voltage characteristics_,
_Table 12: Current characteristics_, and _Table 13: Thermal characteristics_ may cause
permanent damage to the device. These are stress ratings only and the functional operation
of the device at these conditions is not implied. Exposure to maximum rating conditions for
extended periods may affect device reliability. Device mission profile (application conditions)
is compliant with JEDEC JESD47 Qualification Standard, extended mission profiles are
available on demand.


**Electrostatic discharge (ESD)**


Electrostatic discharges (a positive then a negative pulse separated by 1 second) are
applied to the pins of each sample according to each pin combination. The sample size
depends on the number of supply pins in the device (3 parts × (n+1) supply pins). This test
conforms to the JESD22-A114/C101 standard.


**Table 45. ESD absolute maximum ratings**


**Maximum**
**Symbol** **Ratings** **Conditions** **Class** **Unit**
**value** **[(1)]**


Electrostatic discharge
VESD(HBM) voltage (human body TA = +25 °C conforming to JESD22-A114 2 2000 [(2)]
model)


V


Electrostatic discharge
VESD(CDM) voltage (charge device
model)


TA = +25 °C conforming to II 250
ANSI/ESDA/JEDEC JS-002


1. Evaluated by characterization - not tested in production.


114/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


2. On VBAT pin, VESD(HBM) is limited to 1000 V.


**Static latchup**


Two complementary static tests are required on six parts to assess the latchup
performance:

- A supply overvoltage is applied to each power supply pin

- A current injection is applied to each input, output and configurable I/O pin


These tests are compliant with EIA/JESD 78A IC latchup standard.


**Table 46. Electrical sensitivities**


**Symbol** **Parameter** **Conditions** **Class**


LU Static latch-up class TA = +105 °C conforming to JESD78A II level A


**6.3.15** **I/O current injection characteristics**


As a general rule, current injection to the I/O pins, due to external voltage below VSS or
above VDD (for standard, 3 V-capable I/O pins) should be avoided during normal product
operation. However, in order to give an indication of the robustness of the microcontroller in
cases when abnormal injection accidentally happens, susceptibility tests are performed on a
sample basis during device characterization.


**Functional susceptibilty to I/O current injection**


While a simple application is executed on the device, the device is stressed by injecting
current into the I/O pins programmed in floating input mode. While current is injected into
the I/O pin, one at a time, the device is checked for functional failures.


The failure is indicated by an out of range parameter: ADC error above a certain limit (>5
LSB TUE), out of conventional limits of induced leakage current on adjacent pins (out of
5 μA/+0 μA range), or other functional failure (for example reset, oscillator frequency
deviation).


Negative induced leakage current is caused by negative injection and positive induced
leakage current by positive injection.


The test results are given in _Table 47_ .


DS8626 Rev 12 115/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 47. I/O current injection susceptibility**


**Functional susceptibility**


**Symbol** **Description**


**Unit**
**Negative** **Positive**
**injection** **injection**


Injected current on BOOT0 pin - 0 NA

Injected current on NRST pin - 0 NA


IINJ(1)


Injected current on PE2, PE3, PE4, PE5, PE6,
PI8, PC13, PC14, PC15, PI9, PI10, PI11, PF0,
PF1, PF2, PF3, PF4, PF5, PF10, PH0/OSC_IN,
PH1/OSC_OUT, PC0, PC1, PC2, PC3, PB6,
PB7, PB8, PB9, PE0, PE1, PI4, PI5, PI6, PI7,
PDR_ON, BYPASS_REG


- 0 NA


mA


Injected current on all FT pins          - 5 NA

Injected current on any other pin          - 5 +5


1. It is recommended to add a Schottky diode (pin to ground) to analog pins which may potentially inject negative currents.


**6.3.16** **I/O port characteristics**


**General input/output characteristics**


Unless otherwise specified, the parameters given in _Table 48_ are derived from tests
performed under the conditions summarized in _Table 14_ . All I/Os are CMOS and TTL
compliant.


_Note:_ _For information on GPIO configuration, refer to application note AN4899 “STM32 GPIO_
_configuration for hardware settings and low-power consumption” available from the ST_
_website www.st.com._


**Table 48. I/O static characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**

FT, TTa and NRST I/O input low     -     - 0.3VDD-0.04 [(1)]
level voltage 1.7 V ≤ VDD ≤ 3.6 V      -      - 0.3VDD(2)


V


VIL


VIH


BOOT0 I/O input low level
voltage


BOOT0 I/O input low level
voltage


1.75 V ≤ VDD ≤ 3.6 V - -40 °C ≤ TA ≤ 105 °C

0.1VDD-+0.1 [(1)]
1.7 V ≤ VDD ≤ 3.6 V - 0 °C ≤ TA ≤ 105 °C


FT, TTa and NRST I/O input low 0.45VDD+0.3 [(1)] - level voltage 1.7 V ≤ VDD ≤ 3.6 V 0.7VDD(2) - 


1.75 V ≤ VDD ≤ 3.6 V - -40 °C ≤ TA ≤ 105 °C
0.17VDD+0.7 [(1)]

1.7 V ≤ VDD ≤ 3.6 V - 0 °C ≤ TA ≤ 105 °C


116/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 48. I/O static characteristics (continued)**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


FT, TTa and NRST I/O input (3)
hysteresis 1.7 V ≤ VDD ≤ 3.6 V 10%VDD      -      


VHYS


V


BOOT0 I/O input hysteresis


1.75 V ≤ VDD ≤ 3.6 V
-40 °C ≤ TA ≤ 105 °C
0.1              -              1.7 V ≤ VDD ≤ 3.6 V
0 °C ≤ TA ≤ 105 °C


I/O input leakage current [(4)] VSS ≤ VIN ≤ VDD     -     - ± 1
Ilkg µA
I/O FT input leakage current [(5)] VIN = 5 V     -     - 3


Weak pull-up
RPU equivalent
resistor [(6)]


Weak pull-down
RPD equivalent
resistor [(7)]


All pins
except for
PA10 and
PB12
(OTG_FS_ID,
OTG_HS_ID)


PA10 and
PB12
(OTG_FS_ID,
OTG_HS_ID)


All pins
except for
PA10 and
PB12


PA10 and

- 7 10 14
PB12


VIN = VSS 30 40 50


   - 7 10 14


VIN = VDD 30 40 50


k Ω


CIO(8) I/O pin capacitance  -  -  - 5  - pF


1. Specified by design.


2. Tested in production.


3. With a minimum of 200 mV.


4. Leakage could be higher than the maximum value, if negative current is injected on adjacent pins.Refer to _Table 47: I/O_
_current injection susceptibility_

5. To sustain a voltage higher than VDD + 0.3 V, the internal pull-up/pull-down resistors must be disabled. Leakage could be
higher than the maximum value, if negative current is injected on adjacent pins. Refer to _Table 47: I/O current injection_
_susceptibility_ .


6. Pull-up and pull-down resistors are designed with a true resistance in series with a switchable PMOS. This PMOS
contribution to the series resistance is minimum (~10% order).

7. Pull-up and pull-down resistors are designed with a true resistance in series with a switchable NMOS. This NMOS
contribution to the series resistance is minimum (~10% order).

8. Hysteresis voltage between Schmitt trigger switching levels. Evaluated by characterization - not tested in production.


All I/Os are CMOS and TTL compliant (no software configuration required). Their
characteristics cover more than the strict CMOS-technology or TTL parameters.


DS8626 Rev 12 117/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Output driving current**


The GPIOs (general purpose input/outputs) can sink or source up to ± 8 mA, and sink or
source up to ± 20 mA (with a relaxed VOL/VOH) except PC13, PC14 and PC15 which can
sink or source up to ± 3mA. When using the PC13 to PC15 GPIOs in output mode, the speed
should not exceed 2 MHz with a maximum load of 30 pF.


In the user application, the number of I/O pins which can drive current must be limited to
respect the absolute maximum rating specified in _Section 6.2_ . In particular:

- The sum of the currents sourced by all the I/Os on VDD, plus the maximum Run
consumption of the MCU sourced on VDD, cannot exceed the absolute maximum rating
IVDD (see _Table 12_ ).

- The sum of the currents sunk by all the I/Os on VSS plus the maximum Run
consumption of the MCU sunk on VSS cannot exceed the absolute maximum rating
IVSS (see _Table 12_ ).


**Output voltage levels**


Unless otherwise specified, the parameters given in _Table 49_ are derived from tests
performed under ambient temperature and VDD supply voltage conditions summarized in
_Table 14_ . All I/Os are CMOS and TTL compliant.


**Table 49. Output voltage characteristics** **[(1)]**


**Symbol** **Parameter** **Conditions** **Min** **Max** **Unit**


VOL(2)


Output low level voltage CMOS port
IIO = +8 mA

Output high level voltage

2.7 V < VDD < 3.6 V


VOL Output low level voltage CMOS port - 0.4

VOH(3) Output high level voltage IIO = +8 mA VDD–0.4 - V


Output high level voltage VDD–0.4 


VOL (2) Output low level voltage TTL port - 0.4

VOH (3) Output high level voltage 2.7 V < VIIO =+ 8mADD < 3.6 V 2.4 - V


VOL(2)(4)


Output low level voltage IIO = +20 mA

Output high level voltage 2.7 V < VDD < 3.6 V


VOL Output low level voltage IIO = +20 mA - 1.3 V

VOH(3)(4) Output high level voltage 2.7 V < VDD < 3.6 V VDD–1.3 
VOL(2)(4) Output low level voltage IIO = +6 mA - 0.4 V

VOH(3)(4) Output high level voltage 2 V < VDD < 2.7 V VDD–0.4 


VOL(2)(4) Output low level voltage IIO = +6 mA

V (3)(4) Output high level voltage 2 V < VDD < 2.7 V


1. PC13, PC14, PC15 and PI8 are supplied through the power switch. Since the switch only sinks a limited
amount of current (3 mA), the use of GPIOs PC13 to PC15 and PI8 in output mode is limited: the speed
should not exceed 2 MHz with a maximum load of 30 pF and these I/Os must not be used as a current
source (e.g. to drive an LED).

2. The IIO current sunk by the device must always respect the absolute maximum rating specified in _Table 12_
and the sum of IIO (I/O ports and control pins) must not exceed IVSS.

3. The IIO current sourced by the device must always respect the absolute maximum rating specified in
_Table 12_ and the sum of IIO (I/O ports and control pins) must not exceed IVDD.

4. Evaluated by characterization - not tested in production.


118/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Input/output AC characteristics**


The definition and values of input/output AC characteristics are given in _Figure 37_ and
_Table 50_, respectively.


Unless otherwise specified, the parameters given in _Table 50_ are derived from tests
performed under the ambient temperature and VDD supply voltage conditions summarized
in _Table 14_ .


**Table 50. I/O AC characteristics** **[(1)(2)]**


**OSPEEDRy**

**[1:0] bit** **Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**
**value** **[(1)]**


CL = 50 pF, VDD > 2.70 V                           -                           - 4


fmax(IO)out Maximum frequency [(3)]





tf(IO)out/
tr(IO)out


Output high to low level fall
time and output low to high
level rise time


fmax(IO)out Maximum frequency [(3)]


tf(IO)out/
tr(IO)out


Output high to low level fall
time and output low to high
level rise time


fmax(IO)out Maximum frequency [(3)]


CL = 50 pF, VDD > 1.8 V - - 2
MHz

CL = 10 pF, VDD > 2.70 V - - 8

CL = 10 pF, VDD > 1.8 V - - 4


CL = 50 pF, VDD = 1.8 V to - - 100 ns
3.6 V


CL = 50 pF, VDD > 2.70 V - - 25

CL = 50 pF, VDD > 1.8 V - - 12.5
MHz

CL = 10 pF, VDD > 2.70 V - - 50 [(4)]

CL = 10 pF, VDD > 1.8 V - - 20

CL = 50 pF, VDD >2.7 V - - 10

CL = 50 pF, VDD > 1.8 V - - 20
ns

CL = 10 pF, VDD > 2.70 V - - 6

CL = 10 pF, VDD > 1.8 V - - 10

CL = 40 pF, VDD > 2.70 V - - 50 [(4)]

CL = 40 pF, VDD > 1.8 V - - 25
MHz

CL = 10 pF, VDD > 2.70 V - - 100 [(4)]

CL = 10 pF, VDD > 1.8 V - - 50 [(4)]

CL = 40 pF, VDD > 2.70 V - - 6

CL = 40 pF, VDD > 1.8 V - - 10
ns

CL = 10 pF, VDD > 2.70 V - - 4

CL = 10 pF, VDD > 1.8 V - - 6


tf(IO)out/
tr(IO)out


Output high to low level fall
time and output low to high
level rise time


DS8626 Rev 12 119/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 50. I/O AC characteristics** **[(1)(2)]** **(continued)**


**OSPEEDRy**

**[1:0] bit** **Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**
**value** **[(1)]**


CL = 30 pF, VDD > 2.70 V                           -                           - 100 [(4)]


Fmax(IO)out Maximum frequency [(3)]



CL = 30 pF, VDD > 1.8 V - - 50 [(4)]
MHz

CL = 10 pF, VDD > 2.70 V - - 180 [(4)]

CL = 10 pF, VDD > 1.8 V - - 100 [(4)]

CL = 30 pF, VDD > 2.70 V - - 4

CL = 30 pF, VDD > 1.8 V - - 6
ns

CL = 10 pF, VDD > 2.70 V - - 2.5

CL = 10 pF, VDD > 1.8 V - - 4


tf(IO)out/
tr(IO)out


Output high to low level fall
time and output low to high
level rise time


Pulse width of external signals

- tEXTIpw detected by the EXTI     - 10     -     - ns
controller


1. Evaluated by characterization - not tested in production.


2. The I/O speed is configured using the OSPEEDRy[1:0] bits. Refer to the STM32F4xx reference manual for a description of
the GPIOx_SPEEDR GPIO port output speed register.


3. The maximum frequency is defined in _Figure 37_ .


4. For maximum frequencies above 50 MHz, the compensation cell should be used.


**Figure 37. I/O AC characteristics definition**


90%


10%


50%

90%


tf(IO)out


T


50%


10%


EXTERNAL tr(IO)out
OUTPUT

ON CL


Maximum frequency is achieved with a duty cycle at
45-55% when loaded by the specified capacitance


120/206 DS8626 Rev 12


MSv75936V1


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**6.3.17** **NRST pin characteristics**


The NRST pin input driver uses CMOS technology. It is connected to a permanent pull-up
resistor, RPU (see _Table 48_ ).

Unless otherwise specified, the parameters given in _Table 51_ are derived from tests
performed under the ambient temperature and VDD supply voltage conditions summarized
in _Table 14_ .


**Table 51. NRST pin characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


VIL(NRST)(1)


NRST Input low level voltage TTL ports

NRST Input high level voltage 2.7 V ≤ VDD ≤ 3.6 V


- - 0.8


VIH(NRST)(1) NRST Input high level voltage 2.7 V ≤ VDD ≤ 3.6 V 2 - V


VIL(NRST)(1) NRST Input low level voltage CMOS ports

V (1) NRST Input high level voltage 1.8 V ≤ VDD ≤ 3.6 V


- - 0.3VDD


VIH(NRST)(1) NRST Input high level voltage 1.8 V ≤ VDD ≤ 3.6 V 0.7VDD - 


NRST Schmitt trigger voltage
Vhys(NRST) hysteresis - - 200 - mV


RPU Weak pull-up equivalent resistor [(2)]


VIN = VSS 30 40 50 k Ω


VF(NRST)(1) NRST Input filtered pulse  -  -  - 100 ns

VNF(NRST)(1) NRST Input not filtered pulse VDD > 2.7 V 300 - - ns


Internal reset
TNRST_OUT Generated reset pulse duration source 20 - - µs


1. Specified by design.


2. The pull-up is designed with a true resistance in series with a switchable PMOS. This PMOS contribution to
the series resistance must be minimum (~10% order).


**Figure 38. Recommended NRST pin protection**


External
reset circuit [(1)]


0.1 μF


VDD


RPU
NRST [(2)]


~~Filter~~


Internal Reset


STM32F


ai14132c


1. The reset network protects the device against parasitic resets.

2. The user must ensure that the level on the NRST pin can go below the VIL(NRST) max level specified in
_Table 51_ . Otherwise the reset is not taken into account by the device.


**6.3.18** **TIM timer characteristics**


The parameters given in _Table 52_ and _Table 53_ are specified by design.


Refer to _Section 6.3.16: I/O port characteristics_ for details on the input/output alternate
function characteristics (output compare, input capture, external clock, PWM output).


DS8626 Rev 12 121/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 52. Characteristics of TIMx connected to the APB1 domain** **[(1)]**


**Symbol** **Parameter** **Conditions** **Min** **Max** **Unit**


1 - tTIMxCLK


11.9 - ns


1 - tTIMxCLK


23.8 - ns


0 fTIMxCLK/2 MHz


0 42 MHz


tres(TIM) Timer resolution time


Timer external clock
fEXT frequency on CH1 to CH4


AHB/APB1
prescaler distinct
from 1, fTIMxCLK =
84 MHz


AHB/APB1
prescaler = 1,
fTIMxCLK = 42 MHz


ResTIM Timer resolution - 16/32 bit


1 65536 tTIMxCLK


0.0119 780 µs


1  - tTIMxCLK


0.0119 51130563 µs


tCOUNTER


16-bit counter clock
period when internal clock
is selected


32-bit counter clock
period when internal clock
is selected


fTIMxCLK = 84 MHz
APB1= 42 MHz


- 65536 × 65536 tTIMxCLK
tMAX_COUNT Maximum possible count

- 51.1 s


1. TIMx is used as a general term to refer to the TIM2, TIM3, TIM4, TIM5, TIM6, TIM7, and TIM12 timers.


122/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 53. Characteristics of TIMx connected to the APB2 domain** **[(1)]**


**Symbol** **Parameter** **Conditions** **Min** **Max** **Unit**


1 - tTIMxCLK


5.95 - ns


1 - tTIMxCLK


11.9 - ns


0 fTIMxCLK/2 MHz


0 84 MHz


tres(TIM) Timer resolution time


AHB/APB2
prescaler distinct
from 1, fTIMxCLK =
168 MHz


AHB/APB2
prescaler = 1,
fTIMxCLK = 84 MHz


Timer external clock
fEXT frequency on CH1 to
CH4

TIM Timer resolution fTIMxCLK =

168 MHz

16-bit counter clock

APB2 = 84 MHz


ResTIM Timer resolution TIMxCLK - 16 bit


16-bit counter clock

APB2 = 84 MHz

tCOUNTER period when internal 1 65536 tTIMxCLK
clock is selected


tMAX_COUNT Maximum possible count       - 32768 tTIMxCLK


1. TIMx is used as a general term to refer to the TIM1, TIM8, TIM9, TIM10, and TIM11 timers.


**6.3.19** **Communications interfaces**

**I** **[2]** **C interface characteristics**

The I [2] C interface meets the timings requirements of the I [2] C-bus specification and user
manual rev. 03 for:

- Standard-mode (Sm): with a bit rate up to 100 kbit/s

- Fast-mode (Fm): with a bit rate up to 400 kbit/s.

The I [2] C timings requirements are specified by design when the I2C peripheral is properly
configured (refer to RM0090 reference manual).


The SDA and SCL I/O requirements are met with the following restrictions: the SDA and
SCL I/O pins are not “true” open-drain. When configured as open-drain, the PMOS
connected between the I/O pin and VDD is disabled, but is still present. Refer to
_Section 6.3.16: I/O port characteristics_ for more details on the I [2] C I/O characteristics.

All I [2] C SDA and SCL I/Os embed an analog filter. Refer to the table below for the analog
filter characteristics:


**Table 54. I2C analog filter characteristics** **[(1)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


Maximum pulse width of spikes
tAF that are suppressed by the analog 50 [(2)]
filter


1. Specified by design.

2. Spikes with widths below tAF(min) are filtered.

3. Spikes with widths above tAF(max) are not filtered


260 [(3)]


ns


DS8626 Rev 12 123/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**SPI interface characteristics**


Unless otherwise specified, the parameters given in _Table 55_ for SPI are derived from tests
performed under the ambient temperature, fPCLKx frequency and VDD supply voltage
conditions summarized in _Table 14_ with the following configuration:

- Output speed is set to OSPEEDRy[1:0] = 10

- Capacitive load C = 30 pF

- Measurement points are done at CMOS levels: 0.5 VDD

Refer to _Section 6.3.16: I/O port characteristics_ for more details on the input/output alternate
function characteristics (NSS, SCK, MOSI, MISO).


**Table 55. SPI dynamic characteristics** **[(1)]**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**



fSCK


1/tc(SCK)


Master mode, SPI1,
2.7V < VDD < 3.6V

-                           


Slave mode, SPI1/2/3,
21
1.7V < VDD < 3.6V


MHz


SPI clock frequency


Slave mode, SPI1,
42
2.7V < VDD < 3.6V


Master mode, SPI1/2/3,
1.7V < VDD < 3.6V

-                           



Duty(SCK) [Duty cycle of SPI clock ] Slave mode 30 50 70 %
frequency


124/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 55. SPI dynamic characteristics** **[(1)]** **(continued)**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


tw(SCKH)
SCK high and low time


Master mode, SPI presc = 2,
2.7V < VDD < 3.6V TPCLK-0.5 TPCLK TPCLK+0.5


Master mode, SPI presc = 2,
tw(SCKL) 1.7V < VDD < 3.6V TPCLK-2 TPCLK TPCLK+2


tsu(NSS) NSS setup time Slave mode, SPI presc = 2 4 x TPCLK

-                                                              th(NSS) NSS hold time Slave mode, SPI presc = 2 2 x TPCLK

tsu(MI) Master mode 6.5 - Data input setup time

tsu(SI) Slave mode 2.5 - 
th(MI) Master mode 2.5 - Data input hold time

th(SI) Slave mode 4 - 
ta(SO)(2) Data output access time Slave mode, SPI presc = 2 0 - 4 x TPCLK


tdis(SO)(3) Data output disable time


tv(SO)

Data output valid/hold time

th(SO)


tv(MO) Data output valid time


Slave mode, SPI1,
0                - 7.5
2.7V < VDD < 3.6V


Slave mode, SPI1/2/3
0                - 16.5
1.7V < VDD < 3.6V


Slave mode (after enable edge),

- 11 13
SPI1, 2.7V < VDD < 3.6V


Slave mode (after enable edge),

- 12 16.5
SPI2/3, 2.7V < VDD < 3.6V


Slave mode (after enable edge),

- 15.5 19
SPI1, 1.7V < VDD < 3.6V


Slave mode (after enable edge),

- 18 20.5
SPI2/3, 1.7V < VDD < 3.6V


Master mode (after enable edge),

-                           - 2.5
SPI1, 2.7V < VDD < 3.6V


Master mode (after enable edge),

-                           - 4.5
SPI1/2/3, 1.7V < VDD < 3.6V


ns


th(MO) Data output hold time Master mode (after enable edge) 0 - 

1. Evaluated by characterization - not tested in production.


2. Min time is for the minimum time to drive the output and the max time is for the maximum time to validate the data.


3. Min time is for the minimum time to invalidate the output and the max time is for the maximum time to put the data in Hi-Z.


DS8626 Rev 12 125/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 39. SPI timing diagram - slave mode and CPHA = 0**


NSS input


~~t~~ c(SCK) th(NSS)


~~t~~ su(NSS)


~~t~~ w(SCKH)


CPHA=0
CPOL=0


CPHA=0
CPOL=1


MISO output


MOSI input


NSS input


CPHA=1
CPOL=0


CPHA=1
CPOL=1


~~t~~ a(SO) ~~t~~ v(SO)


First bit OUT Next bits OUT

~~t~~ w(SCKL)


~~t~~ h(SO)


~~t~~ dis(SO)


MSv41658V2


~~t~~ su(SI) ~~t~~ h(SI)


First bit IN


Next bits IN


Last bit OUT


Last bit IN


**Figure 40. SPI timing diagram - slave mode and CPHA = 1**


tsu(NSS)


~~t~~ w(SCKH)
~~t~~ c(SCK)


ta(SO) ~~t~~ w(SCKL) tv(SO)


~~t~~ h(SO)


~~t~~ h(NSS)


tdis(SO)


MISO output


MOSI input


~~t~~ su(SI)


First bit OUT Next bits OUT Last bit OUT


~~t~~ h(SI)


First bit IN Next bits IN Last bit IN


MSv41659V2


126/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 41. SPI timing diagram - master mode**


High


NSS input


CPHA=0
CPOL=0


CPHA=0
CPOL=1


CPHA=1
CPOL=0


CPHA=1
CPOL=1


MISO input


MOSI output


tsu(MI)


~~t~~ h(MI)


First bit IN Next bits IN Last bit IN


First bit OUT Next bits OUT Last bit OUT


tv(MO) th(MO)


MSv72626V1


DS8626 Rev 12 127/206

~~t~~ c(SCK)
tw(SCKH)


tw(SCKL)



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**I** **[2]** **S interface characteristics**

Unless otherwise specified, the parameters given in _Table 56_ for the i [2] S interface are
derived from tests performed under the ambient temperature, fPCLKx frequency and VDD
supply voltage conditions summarized in _Table 14_, with the following configuration:

- Output speed is set to OSPEEDRy[1:0] = 10

- Capacitive load C = 30 pF

- Measurement points are done at CMOS levels: 0.5 VDD

Refer to _Section 6.3.16: I/O port characteristics_ for more details on the input/output alternate


function characteristics (CK, SD, WS).


**Table 56. I** **[2]** **S dynamic characteristics** **[(1)]**


**Symbol** **Parameter** **Conditions** **Min** **Max** **Unit**

fMCK I [2] S main clock output - 256 x 8K 256 x FS(2) MHz


Master data: 32 bits                       - 64 x FS
fCK I [2] S clock frequency MHz
Slave data: 32 bits                        - 64 x FS

DCK I [2] S clock frequency duty cycle Slave receiver 30 70 %

tv(WS) WS valid time Master mode 0 6

th(WS) WS hold time Master mode 0 
tsu(WS) WS setup time Slave mode 1 
th(WS) WS hold time Slave mode 0 


tsu(SD_MR) Master receiver 7.5 Data input setup time

tsu(SD_SR) Slave receiver 2 


ns


th(SD_MR) Master receiver 0 Data input hold time

th(SD_SR) Slave receiver 0 
tv(SD_ST) Slave transmitter (after enable edge) - 27
th(SD_ST) Data output valid time

tv(SD_MT) Master transmitter (after enable edge) - 20

th(SD_MT) Data output hold time Master transmitter (after enable edge) 2.5 

1. Evaluated by characterization - not tested in production.

2. The maximum value of 256 x FS is 42 MHz (APB1 maximum frequency).


_Note:_ _Refer to the I_ _[2]_ _S section of RM0090 reference manual for more details on the sampling_
_frequency (FS). fMCK, fCK, and DCK values reflect only the digital peripheral behavior. The_
_value of these parameters might be slightly impacted by the source clock accuracy. DCK_
_depends mainly on the value of ODD bit. The digital contribution leads to a minimum value_
_of I2SDIV / (2 x I2SDIV + ODD) and a maximum value of (I2SDIV + ODD) / (2 x I2SDIV +_
_ODD). FS maximum value is supported for each mode/condition._


128/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 42. I** **[2]** **S slave timing diagram (Philips protocol)**


1. LSB transmit/receive of the previously transmitted byte. No LSB transmit/receive is sent before the first
byte.


**Figure 43. I** **[2]** **S master timing diagram (Philips protocol)** **[(1)]**


1. Evaluated by characterization - not tested in production.

2. LSB transmit/receive of the previously transmitted byte. No LSB transmit/receive is sent before the first
byte.


DS8626 Rev 12 129/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**USB OTG FS characteristics**


This interface is present in both the USB OTG HS and USB OTG FS controllers.


**Table 57. USB OTG FS startup time**


**Symbol** **Parameter** **Max** **Unit**


tSTARTUP(1)


1. Specified by design.


USB OTG FS transceiver startup time 1 µs


**Table 58. USB OTG FS DC electrical characteristics**


**Symbol** **Parameter** **Conditions** **Min.** **[(1)]**


USB OTG FS operating
VDD voltage   - 3.0 [(2)]


**Typ.** **Max.** **[(1)]** **Unit**


 - 3.6 V


I(USB_FS_DP/DM,
Differential input sensitivity 0.2 - USB_HS_DP/DM)


Input
levels


Output
levels


VDI(3)


(3) [Differential common mode ]
VCM range Includes VDI range 0.8 - 2.5 V

VSE(3) Single ended receiver threshold - 1.3 - 2.0

VOL Static output level low RL of 1.5 k Ω to 3.6 V [(4)] - - 0.3

V
VOH Static output level high RL of 15 k Ω to VSS(4) 2.8 - 3.6


17 21 24


RPD


RPU


PA11, PA12, PB14, PB15
(USB_FS_DP/DM,
USB_HS_DP/DM)
VIN = VDD


PA9, PB13
(OTG_FS_VBUS, 0.65 1.1 2.0
OTG_HS_VBUS)


PA12, PB15 (USB_FS_DP,
USB_HS_DP) VIN = VSS 1.5 1.8 2.1


PA9, PB13
(OTG_FS_VBUS, VIN = VSS 0.25 0.37 0.55
OTG_HS_VBUS)


k Ω


1. All the voltages are measured from the local ground potential.


2. The STM32F405xx and STM32F407xx USB OTG FS functionality is ensured down to 2.7 V but not the full
USB OTG FS electrical characteristics which are degraded in the 2.7-to-3.0 V VDD voltage range.

3. Specified by design.

4. RL is the load connected on the USB OTG FS drivers


130/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 44. USB OTG FS timings: definition of data signal rise and fall time**


Cross over
points
Differential
data lines


VCRS


VSS


tf tr


ai14137b


**Table 59. USB OTG FS electrical characteristics** **[(1)]**


**Driver characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Max** **Unit**


tr Rise time [(2)]


CL = 50 pF 4 20 ns


tf Fall time [(2)] CL = 50 pF 4 20 ns

trfm Rise/ fall time matching tr/tf 90 110 %

VCRS Output signal crossover voltage  - 1.3 2.0 V


1. Specified by design.

2. Measured from 10% to 90% of the data signal. For more detailed informations, please refer to USB
Specification - Chapter 7 (version 2.0).


**USB HS characteristics**


Unless otherwise specified, the parameters given in _Table 62_ for ULPI are derived from
tests performed under the ambient temperature, fHCLK frequency summarized in _Table 61_
and VDD supply voltage conditions summarized in _Table 60_, with the following configuration:

- Output speed is set to OSPEEDRy[1:0] = 10

- Capacitive load C = 30 pF

- Measurement points are done at CMOS levels: 0.5VDD.

Refer to Section _Section 6.3.16: I/O port characteristics_ for more details on the input/output
characteristics.


**Table 60. USB HS DC electrical characteristics**


**Symbol** **Parameter** **Min.** **[(1)]**


**Max.** **[(1)]** **Unit**


Input level VDD USB OTG HS operating voltage 2.7 3.6 V


1. All the voltages are measured from the local ground potential.


**Table 61. USB HS clock timing parameters** **[(1)]**


**Parameter** **Symbol** **Min** **Nominal** **Max** **Unit**


fHCLK value to guarantee proper operation of - 30 - - MHz
USB HS interface


Frequency (first transition) 8-bit ±10% FSTART_8BIT 54 60 66 MHz


DS8626 Rev 12 131/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 61. USB HS clock timing parameters** **[(1)]**


**Parameter** **Symbol** **Min** **Nominal** **Max** **Unit**


Frequency (steady state) ±500 ppm FSTEADY 59.97 60 60.03 MHz

Duty cycle (first transition) 8-bit ±10% DSTART_8BIT 40 50 60 %

Duty cycle (steady state) ±500 ppm DSTEADY 49.975 50 50.025 %


Time to reach the steady state frequency and
duty cycle after the first transition TSTEADY         -         - 1.4 ms


Clock startup time after the
de-assertion of SuspendM


Peripheral TSTART_DEV - - 5.6
ms
Host TSTART_HOST - - 


PHY preparation time after the first transition
of the input clock TPREP - - - µs


1. Specified by design.


**Table 62. ULPI timing**

**Value** **[(1)]**
**Parameter** **Symbol** **Unit**

**Min.** **Max.**


Control in (ULPI_DIR) setup time - 2.0
tSC

Control in (ULPI_NXT) setup time - 1.5


Control in (ULPI_DIR, ULPI_NXT) hold time tHC 0 
Data in setup time tSD - 2.0

Data in hold time tHD 0 
Control out (ULPI_STP) setup time and hold time tDC - 9.2

Data out available from clock rising edge tDD - 10.7


1. VDD = 2.7 V to 3.6 V and TA = –40 to 85 °C.


**Figure 45. ULPI timing diagram**


Clock


ns


ai17361c


Control In
(ULPI_DIR,
ULPI_NXT)


data In
(8-bit)


Control out
(ULPI_STP)


data out
(8-bit)


tSC tHC


tS ~~D~~ tHD


tDC


tDC


tD ~~D~~


132/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Ethernet characteristics**


Unless otherwise specified, the parameters given in _Table 64_, _Table 65_ and _Table 66_ for
SMI, RMII and MII are derived from tests performed under the ambient temperature, fHCLK
frequency summarized in _Table 14_ and VDD supply voltage conditions summarized in
_Table 63_, with the following configuration:

- Output speed is set to OSPEEDRy[1:0] = 10

- Capacitive load C = 30 pF

- Measurement points are done at CMOS levels: 0.5VDD.

Refer to _Section 6.3.16: I/O port characteristics_ for more details on the input/output
characteristics.


**Table 63. Ethernet DC electrical characteristics**


**Symbol** **Parameter** **Min.** **[(1)]**


**Max.** **[(1)]** **Unit**


Input level VDD Ethernet operating voltage 2.7 3.6 V


1. All the voltages are measured from the local ground potential.


_Table 64_ gives the list of Ethernet MAC signals for the SMI (station management interface)
and _Figure 46_ shows the corresponding timing diagram.


**Figure 46. Ethernet SMI timing diagram**


tMDC


ETH_MDC


td(MDIO)


ETH_MDIO(O)


tsu(MDIO) th(MDIO)


ETH_MDIO(I)


MS31384V1


**Table 64. Dynamic characteristics: Ethernet MAC signals for SMI** **[(1)]**


**Symbol** **Parameter** **Min** **Typ** **Max** **Unit**


tMDC MDC cycle time(2.38 MHz) 411 420 425

Td(MDIO) Write data valid time 6 10 13
ns

tsu(MDIO) Read data setup time 12 - 
th(MDIO) Read data hold time 0 - 

1. Evaluated by characterization - not tested in production.


_Table 65_ gives the list of Ethernet MAC signals for the RMII and _Figure 47_ shows the
corresponding timing diagram.


DS8626 Rev 12 133/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 47. Ethernet RMII timing diagram**


RMII_REF_CLK


td(TXEN)
td(TXD)


RMII_TX_EN
RMII_TXD[1:0]


tsu(RXD) tih(RXD)
tsu(CRS) tih(CRS)


RMII_RXD[1:0]
RMII_CRS_DV


ai15667


**Table 65. Dynamic characteristics: Ethernet MAC signals for RMII**


**Symbol** **Rating** **Min** **Typ** **Max** **Unit**


tsu(RXD) Receive data setup time 2           -           - ns

tih(RXD) Receive data hold time 1            -            - ns

tsu(CRS) Carrier sense set-up time 0.5           -           - ns

tih(CRS) Carrier sense hold time 2            -            - ns

td(TXEN) Transmit enable valid delay time 8 9.5 11 ns

td(TXD) Transmit data valid delay time 8.5 10 11.5 ns


_Table 66_ gives the list of Ethernet MAC signals for MII and _Figure 47_ shows the
corresponding timing diagram.


**Figure 48. Ethernet MII timing diagram**


134/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 66. Dynamic characteristics: Ethernet MAC signals for MII** **[(1)]**


**Symbol** **Parameter** **Min** **Typ** **Max** **Unit**


tsu(RXD) Receive data setup time 9         -         
tih(RXD) Receive data hold time 10         -         
tsu(DV) Data valid setup time 9         -         


tih(DV) Data valid hold time 8          -          
tsu(ER) Error setup time 6         -         
tih(ER) Error hold time 8          -          
td(TXEN) Transmit enable valid delay time 0 10 14

td(TXD) Transmit data valid delay time 0 10 15


1. Evaluated by characterization - not tested in production.


**6.3.20** **CAN (controller area network) interface**


ns


Refer to _Section 6.3.16: I/O port characteristics_ for more details on the input/output alternate
function characteristics (CANTX and CANRX).


**6.3.21** **12-bit ADC characteristics**


Unless otherwise specified, the parameters given in _Table 67_ are derived from tests
performed under the ambient temperature, fPCLK2 frequency and VDDA supply voltage
conditions summarized in _Table 14_ .


**Table 67. ADC characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**

VDDA Power supply  - 1.8 [(1)]  - 3.6

VREF+ Positive reference voltage  - 1.8 [(1)(2)(3)]  - VDDA V

VREF  - Negative reference voltage  -  - 0  


fADC ADC clock frequency


fTRIG(4) External trigger frequency


VDDA = 1.8 [(1)(3)] to 0.6 15 18 MHz
2.4 V

VDDA = 2.4 to 3.6 V [(3)] 0.6 30 36 MHz

fADC = 30 MHz,  -  - 1764 kHz
12-bit resolution


-        -        - 17 1/fADC


VAIN Conversion voltage range [(5)]  - 0 (Vtied to ground)SSA or VREF-  - VREF+ V

RAIN(4) External input impedance See _Equation 1_ details for  -  - 50 κΩ

RADC(4)(6) Sampling switch resistance - - - 6 κΩ

CADC(4) Internal sample and hold capacitor - - 4 - pF


DS8626 Rev 12 135/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 67. ADC characteristics (continued)**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


tlat(4) Injection trigger conversion latency


tlatr(4) Regular trigger conversion latency


fADC = 30 MHz - - 0.100 µs

-                    - 3 [(7)] 1/fADC

fADC = 30 MHz - - 0.067 µs

-                    - 2 [(7)] 1/fADC


tS(4) Sampling time fADC = 30 MHz 0.100 - 16 µs

- 3                                    - 480 1/fADC


tSTAB(4) Power-up time - - 2 3 µs

fADC = 30 MHz 0.50                      - 16.40 µs
12-bit resolution

fADC = 30 MHz 0.43                      - 16.34 µs
10-bit resolution


tCONV(4) Total conversion time (including sampling time)


Sampling rate
fS(4) (fADC = 30 MHz, and
tS = 3 ADC cycles)


fADC = 30 MHz 0.37   - 16.27 µs
8-bit resolution

fADC = 30 MHz 0.30   - 16.20 µs
6-bit resolution

9 to 492 (tapproximation)S for sampling +n-bit resolution for successive 1/fADC


12-bit resolution

-                       - 2 Msps
Single ADC


12-bit resolution
Interleave Dual ADC - - 3.75 Msps
mode


12-bit resolution
Interleave Triple ADC - - 6 Msps
mode


ADC VREF DC current
IVREF+(4) consumption in conversion - - 300 500 µA
mode


ADC VDDA DC current
IVDDA(4) consumption in conversion - - 1.6 1.8 mA
mode


1. VDD/VDDA minimum value of 1.7 V is obtained when the device operates in reduced temperature range, and with the use of
an external power supply supervisor (refer to _Section 3.15.2: Internal reset OFF_ ).

2. It is recommended to maintain the voltage difference between VREF+ and VDDA below 1.8 V.

3. VDDA -VREF+ < 1.2 V.

4. Evaluated by characterization - not tested in production.

5. VREF+ is internally connected to VDDA and VREF- is internally connected to VSSA.

6. RADC maximum value is given for VDD=1.8 V, and minimum value for VDD=3.3 V.

7. For external triggers, a delay of 1/fPCLK2 must be added to the latency specified in _Table 67_ .


136/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Equation 1: RAIN max formula**

( k                               - 0.5 )
RAIN = ----------------------------------------------------------------                  - RADC

N + 2
fADC × CADC × ln ( 2 )


The formula above ( _Equation 1_ ) is used to determine the maximum external impedance
allowed for an error below 1/4 of LSB. N = 12 (from 12-bit resolution) and k is the number of
sampling periods defined in the ADC_SMPR1 register.


a


**Table 68. ADC accuracy at fADC = 30 MHz**


**Symbol** **Parameter** **Test conditions** **Typ** **Max** **[(1)]**


**Unit**


LSB


ET Total unadjusted error


±2 ±5


EO Offset error ±1.5 ±2.5


fPCLK2 = 60 MHz,
fADC = 30 MHz, RAIN < 10 k Ω,
VDDA = 1.8 [(2)] to 3.6 V


EG Gain error fADC = 30 MHz, RAIN < 10 k Ω, ±1.5 ±3

ED Differential linearity error VDDA = 1.8 [(2)] to 3.6 V ±1 ±2


EL Integral linearity error ±1.5 ±3


1. Evaluated by characterization - not tested in production.

2. VDD/VDDA minimum value of 1.7 V is obtained when the device operates in reduced temperature range,
and with the use of an external power supply supervisor (refer to _Section 3.15.2: Internal reset OFF_ ).


_Note:_ _ADC accuracy vs. negative injection current: injecting a negative current on any analog_
_input pins should be avoided as this significantly reduces the accuracy of the conversion_
_being performed on another analog input. It is recommended to add a Schottky diode (pin to_
_ground) to analog pins which may potentially inject negative currents._
_Any positive injection current within the limits specified for IINJ(PIN) and SIINJ(PIN) in_
_Section 6.3.16 does not affect the ADC accuracy._


**Figure 49. ADC accuracy characteristics**


VREF+ VDDA

[1LSB = (or )]


VREF+


2 [n]


Output code


2 [n] -1

2 [n] -2
2 [n] -3


2 [n]


EG


(3)


(1) Example of an actual transfer curve
(2) Ideal transfer curve
(3) End-point correlation line


n = ADC resolution
ET = total unadjusted error: maximum deviation
between the actual and ideal transfer curves
EO = offset error: maximum deviation between the first
actual transition and the first ideal one
EG = gain error: deviation between the last ideal
transition and the last actual one
ED = differential linearity error: maximum deviation
between actual steps and the ideal one
EL = integral linearity error: maximum deviation between
any actual transition and the end point correlation line


VREF+ (VDDA)


MSv19880V6


6

4

2
1


VSSA


(1)


EO


(2)


E ~~T~~


EL


ED


1 LSB ideal


DS8626 Rev 12 137/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 50. Typical connection diagram when using the ADC with FT/TT pins featuring**
**analog switch function**


VREF+(4)


Sample-and-hold ADC converter


RADC

Converter


(4)


RAIN(1)


VDDA


I/O
analog
switch


Sampling
switch with
multiplexing


VAIN


Cparasitic(2) Ilkg


(3) CADC


VSS VSS


1. Refer to _Table 67: ADC characteristics_ for the values of RAIN, RADC and CADC.


VSSA


MSv67871V3


2. Cparasitic represents the capacitance of the PCB (dependent on soldering and PCB layout quality) plus the
pad capacitance (refer to _Table 48: I/O static characteristics_ ) A high Cparasitic value downgrades conversion
accuracy. To remedy this, fADC should be reduced.

3. Refer to _Table 48: I/O static characteristics_ .

4. Refer to _Figure 21: Power supply scheme_ .


138/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**General PCB design guidelines**


Power supply decoupling should be performed as shown in _Figure 51_ or _Figure 52_,
depending on whether VREF+ is connected to VDDA or not. The 10 nF capacitors should be
ceramic (good quality). They should be placed them as close as possible to the chip.


**Figure 51. Power supply and reference decoupling (VREF+ not connected to VDDA)**


STM32F


[(1)]
VREF+


1 μF // 10 nF


VDDA


1 μF // 10 nF


[(1)]
VSSA/VREF

ai17535b


1. VREF+ and VREF– inputs are both available on UFBGA176. VREF+ is also available on LQFP100, LQFP144,
and LQFP176. When VREF+ and VREF– are not available, they are internally connected to VDDA and VSSA.


DS8626 Rev 12 139/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 52. Power supply and reference decoupling** **(VREF+ connected to VDDA)**


STM32F


VREF+/VDDA


(1)


1 μF // 10 nF


VREF-/VSSA [(1)]


ai17536c


1. VREF+ and VREF– inputs are both available on UFBGA176. VREF+ is also available on LQFP100, LQFP144,
and LQFP176. When VREF+ and VREF– are not available, they are internally connected to VDDA and VSSA.


**6.3.22** **Temperature sensor characteristics**


**Table 69. Temperature sensor characteristics**


**Symbol** **Parameter** **Min** **Typ** **Max** **Unit**

TL(1) VSENSE linearity with temperature    - ± 1 ± 2 °C

Avg_Slope [(1)] Average slope - 2.5 - mV/°C

V25(1) Voltage at 25 °C   - 0.76   - V

tSTART(2) Startup time   - 6 10 µs

TS_temp(2) ADC sampling time when reading the temperature (1 °C accuracy) 10  -  - µs


1. Evaluated by characterization - not tested in production.


2. Specified by design.


**Table 70. Temperature sensor calibration values**


**Symbol** **Parameter** **Memory address**


TS_CAL1 TS ADC raw data acquired at temperature of 30 °C, VDDA=3.3 V 0x1FFF 7A2C - 0x1FFF 7A2D

TS_CAL2 TS ADC raw data acquired at temperature of 110 °C, VDDA=3.3 V 0x1FFF 7A2E - 0x1FFF 7A2F


140/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**6.3.23** **VBAT monitoring characteristics**


**Table 71. VBAT monitoring characteristics**


**Symbol** **Parameter** **Min** **Typ** **Max** **Unit**


R Resistor bridge for VBAT   - 50   - K Ω

Q Ratio on VBAT measurement   - 2   -   
Er [(1)] Error on Q –1    - +1 %

TS_vbat(2)(2) ADC sampling time when reading the V1 mV accuracy BAT 5   -   - µs


1. Specified by design.


2. Shortest sampling time can be determined in the application by multiple iterations.


**6.3.24** **Embedded reference voltage**


The parameters given in _Table 72_ are derived from tests performed under ambient
temperature and VDD supply voltage conditions summarized in _Table 14_ .


**Table 72. Embedded internal reference voltage**


**Symbol** **Parameter** **Conditions** **Min** **Typ** **Max** **Unit**


VREFINT Internal reference voltage –40 °C < TA < +105 °C 1.18 1.21 1.24 V

TS_vrefint(1) ADC sampling time when reading the internal reference voltage  - 10  -  - µs

VRERINT_s(2) Internal reference voltage spread over the temperature range VDD = 3 V - 3 5 mV

TCoeff(2) Temperature coefficient   -   - 30 50 ppm/°C

tSTART(2) Startup time  -  - 6 10 µs


1. Shortest sampling time can be determined in the application by multiple iterations.


2. Specified by design.


**Table 73. Internal reference voltage calibration values**


**Symbol** **Parameter** **Memory address**


VREFIN_CAL Raw data acquired at temperature of 30 °C, VDDA=3.3 V 0x1FFF 7A2A - 0x1FFF 7A2B


**6.3.25** **DAC electrical characteristics**


**Table 74. DAC characteristics**


**Symbol** **Parameter** **Min** **Typ** **Max** **Unit** **Comments**


VDDA Analog supply voltage 1.8 [(1)]  - 3.6 V  
VREF+ Reference supply voltage 1.8 [(1)]  - 3.6 V VREF+ ≤ VDDA

VSSA Ground 0  - 0 V  

DS8626 Rev 12 141/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 74. DAC characteristics (continued)**


**Symbol** **Parameter** **Min** **Typ** **Max** **Unit** **Comments**

RLOAD(2) Resistive load with buffer ON 5  -  - k Ω  


RO(2) Impedance output with buffer OFF - - 15 k Ω


When the buffer is OFF, the
Minimum resistive load between
DAC_OUT and VSS to have a 1%
accuracy is 1.5 M Ω


Maximum capacitive load at
CLOAD(2) Capacitive load - - 50 pF DAC_OUT pin (when the buffer is
ON).


It gives the maximum output
DAC_OUT Lower DAC_OUT voltage
0.2                        -                        - V excursion of the DAC.
min [(2)] with buffer ON
It corresponds to 12-bit input code
(0x0E0) to (0xF1C) at VREF+ =
DAC_OUT Higher DAC_OUT voltage 3.6 V and (0x1C7) to (0xE38) at
max [(2)] with buffer ON  -  - VDDA – 0.2 V VREF+ = 1.8 V


DAC_OUT Lower DAC_OUT voltage

- 0.5                               - mV
min [(2)] with buffer OFF It gives the maximum output
DAC_OUT Higher DAC_OUT voltage excursion of the DAC.
max [(2)] with buffer OFF  -  - VREF+ – 1LSB V


DAC DC VREF current
IVREF+(4) consumption in quiescent
mode (Standby mode)


DAC DC VDDA current
IDDA(4) consumption in quiescent
mode [(3)]


Differential non linearity
DNL [(4)] Difference between two
consecutive code-1LSB)


- 170 240


µA


With no load, worst code (0x800)
at VREF+ = 3.6 V in terms of DC
consumption on the inputs


With no load, worst code (0xF1C)

- 50 75 at VREF+ = 3.6 V in terms of DC
consumption on the inputs


With no load, middle code (0x800)

- 280 380 µA
on the inputs


With no load, worst code (0xF1C)

- 475 625 µA at VREF+ = 3.6 V in terms of DC
consumption on the inputs


Given for the DAC in 10-bit

- - ±0.5 LSB
configuration.


Given for the DAC in 12-bit

- - ±2 LSB
configuration.


Given for the DAC in 10-bit

- - ±1 LSB
configuration.


Given for the DAC in 12-bit

- - ±4 LSB
configuration.


INL [(4)]


Integral non linearity
(difference between
measured value at Code i
and the value at Code i on a
line drawn between Code 0
and last Code 1023)


142/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 74. DAC characteristics (continued)**


**Symbol** **Parameter** **Min** **Typ** **Max** **Unit** **Comments**


Given for the DAC in 12-bit

- - ±10 mV
configuration


Given for the DAC in 10-bit at

- - ±3 LSB
VREF+ = 3.6 V


Given for the DAC in 12-bit at

- - ±12 LSB
VREF+ = 3.6 V


Offset [(4)]


Offset error
(difference between
measured value at Code
(0x800) and the ideal value
= VREF+/2)


Gain Given for the DAC in 12-bit
Gain error      -      - ±0.5 %
error [(4)] configuration


tSETTLING(4)


Settling time (full scale: for a
10-bit input code transition
between the lowest and the
highest input codes when
DAC_OUT reaches final
value ±4LSB


- 3 6 µs CLOAD ≤ 50 pF,
RLOAD ≥ 5 k Ω


THD [(4)] Total Harmonic Distortion - - - dB CLOAD ≤ 50 pF,
Buffer ON RLOAD ≥ 5 k Ω


Update
rate [(2)]


Max frequency for a correct
DAC_OUT change when
small variation in the input
code (from code i to i+1LSB)


[≤] [ 50 pF,]

- - 1 MS/s [C][LOAD]
RLOAD ≥ 5 k Ω


Wakeup time from off state CLOAD ≤ 50 pF, RLOAD ≥ 5 k Ω
tWAKEUP(4) (Setting the ENx bit in the - 6.5 10 µs input code between lowest and
DAC Control register) highest possible ones.


Power supply rejection ratio
PSRR+ [(2)] (to VDDA) (static DC - –67 –40 dB No RLOAD, CLOAD = 50 pF
measurement)


1. VDD/VDDA minimum value of 1.7 V is obtained when the device operates in reduced temperature range, and with the use of
an external power supply supervisor (refer to _Section 3.15.2: Internal reset OFF_ ).


2. Specified by design.


3. The quiescent mode corresponds to a state where the DAC maintains a stable output level to ensure that no dynamic
consumption occurs.


4. Evaluated by characterization - not tested in production.


DS8626 Rev 12 143/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 53. 12-bit buffered /non-buffered DAC**


Buffered/Non-buffered DAC


Buffer(1)


R L


12-bit
digital to
analog
converter


DAC_OUTx


C
L


ai17157V3


1. The DAC integrates an output buffer that can be used to reduce the output impedance and to drive external
loads directly without the use of an external operational amplifier. The buffer can be bypassed by
configuring the BOFFx bit in the DAC_CR register.


**6.3.26** **FSMC characteristics**


Unless otherwise specified, the parameters given in _Table 75_ to _Table 86_ for the FSMC
interface are derived from tests performed under the ambient temperature, fHCLK frequency
and VDD supply voltage conditions summarized in _Table 14_, with the following configuration:

- Output speed is set to OSPEEDRy[1:0] = 10

- Capacitive load C = 30 pF

- Measurement points are done at CMOS levels: 0.5VDD

Refer to Section _Section 6.3.16: I/O port characteristics_ for more details on the input/output
characteristics.


**Asynchronous waveforms and timings**


_Figure 54_ through _Figure 57_ represent asynchronous waveforms and _Table 75_ through
_Table 78_ provide the corresponding timings. The results shown in these tables are obtained
with the following FSMC configuration:

- AddressSetupTime = 1

- AddressHoldTime = 0x1

- DataSetupTime = 0x1

- BusTurnAroundDuration = 0x0


In all timing tables, the THCLK is the HCLK clock period.


144/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 54. Asynchronous non-multiplexed SRAM/PSRAM/NOR read waveforms**


tw(NE)


FSMC_NE


tv(NOE_NE) t w(NOE) t h(NE_NOE)


FSMC_NOE


FSMC_NWE


tv(A_NE)


FSMC_A[25:0]
Address


tv(BL_NE)


FSMC_NBL[1:0]


FSMC_D[15:0]


t v(NADV_NE)


tw(NADV)


FSMC_NADV [(1)]


1. Mode 2/B, C and D only. In Mode 1, FSMC_NADV is not used.


t h(A_NOE)


t h(BL_NOE)


tsu(Data_NOE)


tsu(Data_NE)


Data


t h(Data_NE)


th(Data_NOE)


ai14991c


**Table 75. Asynchronous non-multiplexed SRAM/PSRAM/NOR read timings** **[(1)(2)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(NE) FSMC_NE low time 2THCLK–0.5 2 THCLK+1 ns

tv(NOE_NE) FSMC_NEx low to FSMC_NOE low 0.5 3 ns

tw(NOE) FSMC_NOE low time 2THCLK–2 2THCLK+ 2 ns

th(NE_NOE) FSMC_NOE high to FSMC_NE high hold time 0  - ns

tv(A_NE) FSMC_NEx low to FSMC_A valid   - 4.5 ns

th(A_NOE) Address hold time after FSMC_NOE high 4  - ns

tv(BL_NE) FSMC_NEx low to FSMC_BL valid  - 1.5 ns

th(BL_NOE) FSMC_BL hold time after FSMC_NOE high 0  - ns

tsu(Data_NE) Data to FSMC_NEx high setup time THCLK+4  - ns

tsu(Data_NOE) Data to FSMC_NOEx high setup time THCLK+4 - ns

th(Data_NOE) Data hold time after FSMC_NOE high 0 - ns

th(Data_NE) Data hold time after FSMC_NEx high 0  - ns

tv(NADV_NE) FSMC_NEx low to FSMC_NADV low - 2 ns

tw(NADV) FSMC_NADV low time  - THCLK ns


1. CL = 30 pF.

2. Evaluated by characterization - not tested in production.


DS8626 Rev 12 145/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 55. Asynchronous non-multiplexed SRAM/PSRAM/NOR write waveforms**


tw(NE)


FSMC_NEx


FSMC_NOE


tv(NWE_NE ~~)~~ tw(NWE ~~)~~ th(NE_NWE)


FSMC_NWE


tv(A_NE)


FSMC_A[25:0] Address


th(A_NWE)


FSMC_NBL[1:0]


FSMC_D[15:0]


FSMC_NADV [(1)]


tv(BL_NE)


tv(Data_NE ~~)~~


tv(NADV_NE)


tw(NAD ~~V)~~


th(BL_NWE)


NBL


th(Data_NWE)


Data


ai14990


1. Mode 2/B, C and D only. In Mode 1, FSMC_NADV is not used.


**Table 76. Asynchronous non-multiplexed SRAM/PSRAM/NOR write timings** **[(1)(2)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(NE) FSMC_NE low time 3THCLK 3THCLK+ 4 ns

tv(NWE_NE) FSMC_NEx low to FSMC_NWE low THCLK–0.5 THCLK+0.5 ns

tw(NWE) FSMC_NWE low time THCLK–1 THCLK+2 ns

th(NE_NWE) FSMC_NWE high to FSMC_NE high hold time THCLK–1         - ns

tv(A_NE) FSMC_NEx low to FSMC_A valid           - 0 ns

th(A_NWE) Address hold time after FSMC_NWE high THCLK– 2          - ns

tv(BL_NE) FSMC_NEx low to FSMC_BL valid           - 1.5 ns

th(BL_NWE) FSMC_BL hold time after FSMC_NWE high THCLK– 1         - ns

tv(Data_NE) Data to FSMC_NEx low to Data valid           - THCLK+3 ns

th(Data_NWE) Data hold time after FSMC_NWE high THCLK–1         - ns

tv(NADV_NE) FSMC_NEx low to FSMC_NADV low         - 2 ns

tw(NADV) FSMC_NADV low time          - THCLK+0.5 ns


1. CL = 30 pF.

2. Evaluated by characterization - not tested in production.


146/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 56. Asynchronous multiplexed PSRAM/NOR read waveforms**


tw(NE)


FSMC_NE


tv(NOE_NE) t h(NE_NOE)


FSMC_NOE


t w(NOE)


FSMC_NWE


tv(A_NE)


FSMC_A[25:16]
Address


tv(BL_NE)


FSMC_NBL[1:0]


FSMC_AD[15:0]


FSMC_NADV


NBL


th(A_NOE)


th(BL_NOE)


tsu(Data_NE)


th(Data_NE)


t v(A_NE)


Address


t v(NADV_NE)


tw(NADV)


tsu(Data_NOE) th(Data_NOE)


Data


th(AD_NADV)


ai14892b


**Table 77. Asynchronous multiplexed PSRAM/NOR read timings** **[(1)(2)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(NE) FSMC_NE low time 3THCLK–1 3THCLK+1 ns

tv(NOE_NE) FSMC_NEx low to FSMC_NOE low 2THCLK–0.5 2THCLK+0.5 ns

tw(NOE) FSMC_NOE low time THCLK–1 THCLK+1 ns

th(NE_NOE) FSMC_NOE high to FSMC_NE high hold time 0  - ns

tv(A_NE) FSMC_NEx low to FSMC_A valid   - 3 ns

tv(NADV_NE) FSMC_NEx low to FSMC_NADV low 1 2 ns

tw(NADV) FSMC_NADV low time THCLK– 2 THCLK+1 ns

th(AD_NADV) FSMC_AD(adress) valid hold time after FSMC_NADV high) THCLK  - ns

th(A_NOE) Address hold time after FSMC_NOE high THCLK–1  - ns

th(BL_NOE) FSMC_BL time after FSMC_NOE high 0  - ns

tv(BL_NE) FSMC_NEx low to FSMC_BL valid  - 2 ns

tsu(Data_NE) Data to FSMC_NEx high setup time THCLK+4  - ns

tsu(Data_NOE) Data to FSMC_NOE high setup time THCLK+4 - ns

th(Data_NE) Data hold time after FSMC_NEx high 0  - ns

th(Data_NOE) Data hold time after FSMC_NOE high 0  - ns


1. CL = 30 pF.

2. Evaluated by characterization - not tested in production.


DS8626 Rev 12 147/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 57. Asynchronous multiplexed PSRAM/NOR write waveforms**


tw(NE)


FSMC_NEx


FSMC_NOE


tv(NWE_ ~~NE)~~ tw(NWE ~~)~~ th(NE_NWE)


FSMC_NWE


tv(A_NE)


FSMC_A[25:16]
Address


th(A_NWE)


th(Data_NWE)


ai14891B


FSMC_NBL[1:0]


FSMC_AD[15:0]


FSMC_NADV


tv(BL_NE)


tv(A_NE)


Address


tv(NADV_N ~~E)~~


tw(NAD ~~V)~~


th(BL_NWE)


NBL


tv(Data_NADV)


Data


th(AD_NADV)


**Table 78. Asynchronous multiplexed PSRAM/NOR write timings** **[(1)(2)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(NE) FSMC_NE low time 4THCLK–0.5 4THCLK+3 ns

tv(NWE_NE) FSMC_NEx low to FSMC_NWE low THCLK–0.5 THCLK -0.5 ns

tw(NWE) FSMC_NWE low tim e 2THCLK–0.5 2THCLK+3 ns

th(NE_NWE) FSMC_NWE high to FSMC_NE high hold time THCLK         - ns

tv(A_NE) FSMC_NEx low to FSMC_A valid           - 0 ns

tv(NADV_NE) FSMC_NEx low to FSMC_NADV low 1 2 ns

tw(NADV) FSMC_NADV low time THCLK– 2 THCLK+ 1 ns


FSMC_AD(address) valid hold time after
th(AD_NADV) FSMC_NADV high) THCLK–2         - ns


th(A_NWE) Address hold time after FSMC_NWE high THCLK          - ns

th(BL_NWE) FSMC_BL hold time after FSMC_NWE high THCLK–2         - ns

tv(BL_NE) FSMC_NEx low to FSMC_BL valid           - 1.5 ns

tv(Data_NADV) FSMC_NADV high to Data valid         - THCLK–0.5 ns

th(Data_NWE) Data hold time after FSMC_NWE high THCLK         - ns


1. CL = 30 pF.


148/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


2. Evaluated by characterization - not tested in production.


**Synchronous waveforms and timings**


_Figure 58_ through _Figure 61_ represent synchronous waveforms and _Table 80_ through
_Table 82_ provide the corresponding timings. The results shown in these tables are obtained
with the following FSMC configuration:

- BurstAccessMode = FSMC_BurstAccessMode_Enable;

- MemoryType = FSMC_MemoryType_CRAM;

- WriteBurst = FSMC_WriteBurst_Enable;

- CLKDivision = 1; (0 is not supported, see the STM32F40xxx/41xxx reference manual)

- DataLatency = 1 for NOR flash; DataLatency = 0 for PSRAM


In all timing tables, the THCLK is the HCLK clock period (with maximum
FSMC_CLK = 60 MHz).


**Figure 58. Synchronous multiplexed NOR/PSRAM read timings**


BUSTURN = 0


FSMC_CLK


FSMC_NEx


tw(CLK) tw(CLK)


Data latency = 0


td(CLKL-NADVL)


FSMC_NADV


FSMC_A[25:16]


FSMC_NOE


td(CLKL-ADV)


td(CLKL-NExL) td(CLKL-NExH)


td(CLKL-NADVH)


td(CLKL-AV)


td(CLKL-ADIV)


td(CLKL-AIV)


td(CLKL-NOEL) td(CLKL-NOEH)


tsu(ADV-CLKH)


~~t~~ h(CLKH-ADV)
tsu(ADV-CLKH) th(CLKH-ADV)


FSMC_AD[15:0] AD[15:0] D1 D2


tsu(NWAITV-CLKH) th(CLKH-NWAITV)


FSMC_NWAIT


(WAITCFG = 1b, WAITPOL + 0b)


FSMC_NWAIT


(WAITCFG = 0b, WAITPOL + 0b)


tsu(NWAITV-CLKH) th(CLKH-NWAITV)


tsu(NWAITV-CLKH) th(CLKH-NWAITV)


ai14893g


DS8626 Rev 12 149/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 79. Synchronous multiplexed NOR/PSRAM read timings** **[(1)(2)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(CLK) FSMC_CLK period 2THCLK           - ns

td(CLKL-NExL) FSMC_CLK low to FSMC_NEx low (x=0..2)          - 0 ns

td(CLKL-NExH) FSMC_CLK low to FSMC_NEx high (x= 0…2) 2         - ns

td(CLKL-NADVL) FSMC_CLK low to FSMC_NADV low         - 2 ns

td(CLKL-NADVH) FSMC_CLK low to FSMC_NADV high 2        - ns

td(CLKL-AV) FSMC_CLK low to FSMC_Ax valid (x=16…25)          - 0 ns

td(CLKL-AIV) FSMC_CLK low to FSMC_Ax invalid (x=16…25) 0          - ns

td(CLKL-NOEL) FSMC_CLK low to FSMC_NOE low         - 0 ns

td(CLKL-NOEH) FSMC_CLK low to FSMC_NOE high 2         - ns

td(CLKL-ADV) FSMC_CLK low to FSMC_AD[15:0] valid          - 4.5 ns

td(CLKL-ADIV) FSMC_CLK low to FSMC_AD[15:0] invalid 0          - ns

tsu(ADV-CLKH) FSMC_A/D[15:0] valid data before FSMC_CLK high 6         - ns

th(CLKH-ADV) FSMC_A/D[15:0] valid data after FSMC_CLK high 0         - ns

tsu(NWAIT-CLKH) FSMC_NWAIT valid before FSMC_CLK high 4         - ns

th(CLKH-NWAIT) FSMC_NWAIT valid after FSMC_CLK high 0         - ns


1. CL = 30 pF.

2. Evaluated by characterization - not tested in production.


150/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 59. Synchronous multiplexed PSRAM write timings**


BUSTURN = 0


FSMC_CLK


FSMC_NEx


tw(CLK) tw(CLK)


Data latency = 0


td(CLKL-NADVL)


FSMC_NADV


FSMC_A[25:16]


FSMC_NWE


td(CLKL-ADV)


td(CLKL-NExL) td(CLKL-NExH)


td(CLKL-NADVH)


td(CLKL-AV)


td(CLKL-AIV)


td(CLKL-NWEL) td(CLKL-NWEH)


td(CLKL-ADIV) td(CLKL-Data)


td(CLKL-Data ~~)~~


FSMC_AD[15:0] AD[15:0] D1 D2


FSMC_NWAIT


(WAITCFG = 0b, WAITPOL + 0b)


FSMC_NBL


tsu(NWAITV-CLKH) th(CLKH-NWAITV)


td(CLKL-NBLH)


ai14992g


**Table 80. Synchronous multiplexed PSRAM write timings** **[(1)(2)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(CLK) FSMC_CLK period 2THCLK   - ns

td(CLKL-NExL) FSMC_CLK low to FSMC_NEx low (x=0..2) - 1 ns

td(CLKL-NExH) FSMC_CLK low to FSMC_NEx high (x= 0…2) 1 - ns

td(CLKL-NADVL) FSMC_CLK low to FSMC_NADV low - 0 ns

td(CLKL- FSMC_CLK low to FSMC_NADV high 0   - ns

NADVH)

td(CLKL-AV) FSMC_CLK low to FSMC_Ax valid (x=16…25)  - 0 ns

td(CLKL-AIV) FSMC_CLK low to FSMC_Ax invalid (x=16…25) 8  - ns

td(CLKL-NWEL) FSMC_CLK low to FSMC_NWE low - 0.5 ns

td(CLKL-NWEH) FSMC_CLK low to FSMC_NWE high 0 - ns

td(CLKL-ADIV) FSMC_CLK low to FSMC_AD[15:0] invalid 0 - ns


FSMC_A/D[15:0] valid data after FSMC_CLK
td(CLKL-DATA) low - 3 ns


DS8626 Rev 12 151/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 80. Synchronous multiplexed PSRAM write timings** **[(1)(2)]** **(continued)**


**Symbol** **Parameter** **Min** **Max** **Unit**


td(CLKL-NBLH) FSMC_CLK low to FSMC_NBL high 0         - ns

tsu(NWAIT- FSMC_NWAIT valid before FSMC_CLK high 4          - ns

CLKH)

th(CLKH-NWAIT) FSMC_NWAIT valid after FSMC_CLK high 0        - ns


1. CL = 30 pF.

2. Evaluated by characterization - not tested in production.


**Figure 60. Synchronous non-multiplexed NOR/PSRAM read timings**


tw(CLK) tw(CLK)


BUSTURN = 0


FSMC_CLK


td(CLKL-NExL) td(CLKL-NExH)

Data latency = 0

FSMC_NEx


td(CLKL-NADVL ~~)~~ td(CLKL-NADVH)


FSMC_NADV


td(CLKL-AV) td(CLKL-AIV)


FSMC_A[25:0]


td(CLKL-NOEL) td(CLKL-NOEH)


FSMC_NOE


tsu(DV-CLKH) ~~t~~ h(CLKH-DV)


tsu(DV-CLKH) th(CLKH-DV)


FSMC_D[15:0] D1 D2


tsu(NWAITV-CLKH) th(CLKH-NWAITV)


FSMC_NWAIT


(WAITCFG = 1b, WAITPOL + 0b)


FSMC_NWAIT


(WAITCFG = 0b, WAITPOL + 0b)


tsu(NWAITV-CLKH) t h(CLKH-NWAITV)


tsu(NWAITV-CLKH) th(CLKH-NWAITV)


ai14894f


152/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 81. Synchronous non-multiplexed NOR/PSRAM read timings** **[(1)(2)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(CLK) FSMC_CLK period 2THCLK –0.5         - ns

td(CLKL-NExL) FSMC_CLK low to FSMC_NEx low (x=0..2)         - 0.5 ns

td(CLKL-NExH) FSMC_CLK low to FSMC_NEx high (x= 0…2) 0        - ns

td(CLKL-NADVL) FSMC_CLK low to FSMC_NADV low        - 2 ns

td(CLKL-NADVH) FSMC_CLK low to FSMC_NADV high 3        - ns

td(CLKL-AV) FSMC_CLK low to FSMC_Ax valid (x=16…25)         - 0 ns

td(CLKL-AIV) FSMC_CLK low to FSMC_Ax invalid (x=16…25) 2         - ns

td(CLKL-NOEL) FSMC_CLK low to FSMC_NOE low        - 0.5 ns

td(CLKL-NOEH) FSMC_CLK low to FSMC_NOE high 1.5        - ns

tsu(DV-CLKH) FSMC_D[15:0] valid data before FSMC_CLK high 6         - ns

th(CLKH-DV) FSMC_D[15:0] valid data after FSMC_CLK high 3        - ns

tsu(NWAIT-CLKH) FSMC_NWAIT valid before FSMC_CLK high 4        - ns

th(CLKH-NWAIT) FSMC_NWAIT valid after FSMC_CLK high 0        - ns


1. CL = 30 pF.

2. Evaluated by characterization - not tested in production.


DS8626 Rev 12 153/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 61. Synchronous non-multiplexed PSRAM write timings**


tw(CLK) tw(CLK)


BUSTURN = 0


FSMC_CLK


td(CLKL-NExL) td(CLKL-NExH)

Data latency = 0

FSMC_NEx


td(CLKL-NADVL ~~)~~ td(CLKL-NADVH)


FSMC_NADV


td(CLKL-AV) td(CLKL-AIV)


FSMC_A[25:0]


td(CLKL-NWEL) td(CLKL-NWEH)


FSMC_NWE


td(CLKL-Data)


td(CLKL-Data)


FSMC_D[15:0] D1 D2


FSMC_NWAIT


(WAITCFG = 0b, WAITPOL + 0b)


FSMC_NBL


tsu(NWAITV-CLKH)


td(CLKL-NBLH)


th(CLKH-NWAITV)


ai14993g


**Table 82. Synchronous non-multiplexed PSRAM write timings** **[(1)(2)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(CLK) FSMC_CLK period 2THCLK            - ns

t [d(CLKL-NExL)] FSMC_CLK low to FSMC_NEx low (x=0..2)               - 1 ns


td(CLKL-NExH) FSMC_CLK low to FSMC_NEx high (x= 0…2) 1          - ns

td(CLKL-NADVL) FSMC_CLK low to FSMC_NADV low         - 7 ns

td(CLKL-NADVH) FSMC_CLK low to FSMC_NADV high 6         - ns

td(CLKL-AV) FSMC_CLK low to FSMC_Ax valid (x=16…25)           - 0 ns

td(CLKL-AIV) FSMC_CLK low to FSMC_Ax invalid (x=16…25) 6           - ns

td(CLKL-NWEL) FSMC_CLK low to FSMC_NWE low         - 1 ns

td(CLKL-NWEH) FSMC_CLK low to FSMC_NWE high 2         - ns

td(CLKL-Data) FSMC_D[15:0] valid data after FSMC_CLK low           - 3 ns

td(CLKL-NBLH) FSMC_CLK low to FSMC_NBL high 3          - ns

tsu(NWAIT-CLKH) FSMC_NWAIT valid before FSMC_CLK high 4         - ns

th(CLKH-NWAIT) FSMC_NWAIT valid after FSMC_CLK high 0         - ns


1. CL = 30 pF.

2. Evaluated by characterization - not tested in production.


154/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**PC Card/CompactFlash controller waveforms and timings**


_Figure 62_ through _Figure 67_ represent synchronous waveforms, and _Table 83_ and _Table 84_
provide the corresponding timings. The results shown in this table are obtained with the
following FSMC configuration:

- COM.FSMC_SetupTime = 0x04;

- COM.FSMC_WaitSetupTime = 0x07;

- COM.FSMC_HoldSetupTime = 0x04;

- COM.FSMC_HiZSetupTime = 0x00;

- ATT.FSMC_SetupTime = 0x04;

- ATT.FSMC_WaitSetupTime = 0x07;

- ATT.FSMC_HoldSetupTime = 0x04;

- ATT.FSMC_HiZSetupTime = 0x00;

- IO.FSMC_SetupTime = 0x04;

- IO.FSMC_WaitSetupTime = 0x07;

- IO.FSMC_HoldSetupTime = 0x04;

- IO.FSMC_HiZSetupTime = 0x00;

- TCLRSetupTime = 0;

- TARSetupTime = 0.


In all timing tables, the THCLK is the HCLK clock period.


**Figure 62. PC Card/CompactFlash controller waveforms for common memory read**
**access**


FSMC_NCE4_2 [(1)]


FSMC_NCE4_1


th(NCEx-AI)


th(NCEx-NREG)
th(NCEx-NIORD)
th(NCEx-NIOWR)


FSMC_A[10:0]


FSMC_NREG
FSMC_NIOWR
FSMC_NIORD


FSMC_NWE


tv(NCEx-A)


td(NREG-NCEx)
td(NIORD-NCEx)


td(NCE4_1-NOE) tw(NOE)

FSMC_NOE


tsu(D-NOE ~~)~~ th(NOE-D)


FSMC_D[15:0]


1. FSMC_NCE4_2 remains high (inactive during 8-bit access.


ai14895b


DS8626 Rev 12 155/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 63. PC Card/CompactFlash controller waveforms for common memory write**
**access**


FSMC_NCE4_1


FSMC_NCE4_2 High


FSMC_A[10:0]


FSMC_NREG
FSMC_NIOWR
FSMC_NIORD


tv(NCE4_1-A)


td(NREG-NCE4_1)
td(NIORD-NCE4_1)


td(NCE4_1-NWE) tw(NWE)


FSMC_NWE


FSMC_NOE


MEMxHIZ =1


td(D-NWE)


tv(NWE-D)


th(NCE4_1-AI)


th(NCE4_1-NREG)
th(NCE4_1-NIORD)
th(NCE4_1-NIOWR)


td(NWE-NCE4_1)


th(NWE-D)


FSMC_D[15:0]


156/206 DS8626 Rev 12


ai14896


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 64. PC Card/CompactFlash controller waveforms for attribute memory read**
**access**


FSMC_NCE4_1


tv(NCE4_1-A) th(NCE4_1-AI)


FSMC_NCE4_2


FSMC_A[10:0]


FSMC_NIOWR
FSMC_NIORD


FSMC_NREG


FSMC_NWE


High


td(NREG-NCE4_1) th(NCE4_1-NREG)


td(NCE4_1-NO ~~E)~~ tw(NOE)


FSMC_NOE


tsu(D-NOE ~~)~~ th(NOE-D)


FSMC_D[15:0] [(1)]


1. Only data bits 0...7 are read (bits 8...15 are disregarded).


td(NOE-NCE4_1)


ai14897b


DS8626 Rev 12 157/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 65. PC Card/CompactFlash controller waveforms for attribute memory write**
**access**


FSMC_NCE4_1


FSMC_NCE4_2


FSMC_A[10:0]


FSMC_NIOWR
FSMC_NIORD


FSMC_NREG


High


th(NCE4_1-AI)


th(NCE4_1-NREG)


td(NCE4_1-NWE)


FSMC_NWE


FSMC_NOE


FSMC_D[7:0](1)


tv(NCE4_1-A)


td(NREG-NCE4_1)


tw(NWE)


td(NWE-NCE4_1 ~~)~~


tv(NWE-D)


ai14898b


1. Only data bits 0...7 are driven (bits 8...15 remains Hi-Z).


**Figure 66. PC Card/CompactFlash controller waveforms for I/O space read access**


FSMC_NCE4_1

FSMC_NCE4_2

tv(NCEx-A) th(NCE4_1-AI)


FSMC_A[10:0]


FSMC_NREG

FSMC_NWE
FSMC_NOE


FSMC_NIOWR


td(NIORD-NCE4_1) tw(NIORD)


FSMC_NIORD


tsu(D-NIORD) td(NIORD-D)


FSMC_D[15:0]


ai14899B


158/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 67. PC Card/CompactFlash controller waveforms for I/O space write access**


FSMC_NCE4_1
FSMC_NCE4_2


tv(NCEx-A) th(NCE4_1-AI)


FSMC_A[10:0]


FSMC_NREG

FSMC_NWE

FSMC_NOE


FSMC_NIORD


td(NCE4_1-NIOWR ~~)~~ tw(NIOWR)


FSMC_NIOWR


ATTxHIZ =1


tv(NIOWR-D)


th(NIOWR-D)


FSMC_D[15:0]


**Table 83. Switching characteristics for PC Card/CF read and write cycles**
**in attribute/common space** **[(1)(2)]**


ai14900c


**Symbol** **Parameter** **Min** **Max** **Unit**


tv(NCEx-A) FSMC_Ncex low to FSMC_Ay valid   - 0 ns

th(NCEx_AI) FSMC_NCEx high to FSMC_Ax invalid 4   - ns

td(NREG-NCEx) FSMC_NCEx low to FSMC_NREG valid  - 3.5 ns

th(NCEx-NREG) FSMC_NCEx high to FSMC_NREG invalid THCLK+4  - ns

td(NCEx-NWE) FSMC_NCEx low to FSMC_NWE low  - 5THCLK+0.5 ns

td(NCEx-NOE) FSMC_NCEx low to FSMC_NOE low  - 5THCLK +0.5 ns

tw(NOE) FSMC_NOE low width 8THCLK–1 8THCLK+1 ns

td(NOE_NCEx) FSMC_NOE high to FSMC_NCEx high 5THCLK+2.5  - ns

tsu (D-NOE) FSMC_D[15:0] valid data before FSMC_NOE high 4.5   - ns

th(N0E-D) FSMC_N0E high to FSMC_D[15:0] invalid 3   - ns

tw(NWE) FSMC_NWE low width 8THCLK–0.5 8THCLK+ 3 ns


td(NWE_NCEx) FSMC_NWE high to FSMC_NCEx high 5THCLK–1  - ns

td(NCEx-NWE) FSMC_NCEx low to FSMC_NWE low  - 5THCLK+ 1 ns

tv(NWE-D) FSMC_NWE low to FSMC_D[15:0] valid   - 0 ns

th (NWE-D) FSMC_NWE high to FSMC_D[15:0] invalid 8THCLK –1  - ns

td (D-NWE) FSMC_D[15:0] valid before FSMC_NWE high 13THCLK –1  - ns


1. CL = 30 pF.

2. Evaluated by characterization - not tested in production.


DS8626 Rev 12 159/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 84. Switching characteristics for PC Card/CF read and write cycles**
**in I/O space** **[(1)(2)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(NIOWR) FSMC_NIOWR low width 8THCLK –1   - ns

tv(NIOWR-D) FSMC_NIOWR low to FSMC_D[15:0] valid   - 5THCLK– 1 ns

th(NIOWR-D) FSMC_NIOWR high to FSMC_D[15:0] invalid 8THCLK– 2   - ns

td(NCE4_1-NIOWR) FSMC_NCE4_1 low to FSMC_NIOWR valid - 5THCLK+ 2.5 ns

th(NCEx-NIOWR) FSMC_NCEx high to FSMC_NIOWR invalid 5THCLK–1.5  - ns

td(NIORD-NCEx) FSMC_NCEx low to FSMC_NIORD valid  - 5THCLK+ 2 ns

th(NCEx-NIORD) FSMC_NCEx high to FSMC_NIORD) valid 5THCLK– 1.5  - ns

tw(NIORD) FSMC_NIORD low width 8THCLK–0.5   - ns

tsu(D-NIORD) FSMC_D[15:0] valid before FSMC_NIORD high 9   - ns

td(NIORD-D) FSMC_D[15:0] valid after FSMC_NIORD high 0   - ns


1. CL = 30 pF.

2. Evaluated by characterization - not tested in production.


**NAND controller waveforms and timings**


_Figure 68_ and _Figure 69_ represent synchronous waveforms, and _Table 85_ and _Table 86_
provide the corresponding timings. The results shown in this table are obtained with the
following FSMC configuration:

- COM.FSMC_SetupTime = 0x01;

- COM.FSMC_WaitSetupTime = 0x03;

- COM.FSMC_HoldSetupTime = 0x02;

- COM.FSMC_HiZSetupTime = 0x01;

- ATT.FSMC_SetupTime = 0x01;

- ATT.FSMC_WaitSetupTime = 0x03;

- ATT.FSMC_HoldSetupTime = 0x02;

- ATT.FSMC_HiZSetupTime = 0x01;

- Bank = FSMC_Bank_NAND;

- MemoryDataWidth = FSMC_MemoryDataWidth_16b;

- ECC = FSMC_ECC_Enable;

- ECCPageSize = FSMC_ECCPageSize_512Bytes;

- TCLRSetupTime = 0;

- TARSetupTime = 0.


In all timing tables, the THCLK is the HCLK clock period.


160/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Figure 68. NAND controller waveforms for read access**


FMC_NCEx


ALE (FMC_A17)
CLE (FMC_A16)

td(ALE-NOE) th(NOE-ALE)


FMC_NWE


tw(NOE)


FMC_NOE (NRE)


tsu(D-NOE) th(NOE-D)


FMC_D[y:0]


MSv73150V1


1. y = 7 or 15 depending on the NAND flash memory interface.


**Figure 69. NAND controller waveforms for write access**


FMC_NCEx


ALE (FMC_A17)
CLE (FMC_A16)


FMC_NWE


FMC_NOE (NRE)


FMC_D[y:0]


td(ALE-NWE) tw(NWE) th(NWE-ALE)


td(D-NWE)


tv(NWE-D) th(NWE-D)


MSv73151V1


1. y = 7 or 15 depending on the NAND flash memory interface.


**Table 85. Switching characteristics for NAND flash read cycles** **[(1)]**


**Symbol** **Parameter** **Min** **Max** **Unit**

tw(N0E) FSMC_NOE low width 4THCLK0.5   - 4THCLK+ 3 ns


tsu(D-NOE) FSMC_D[15-0] valid data before FSMC_NOE high 10  - ns

th(NOE-D) FSMC_D[15-0] valid data after FSMC_NOE high 0  - ns

td(ALE-NOE) FSMC_ALE valid before FSMC_NOE low  - 3THCLK ns

th(NOE-ALE) FSMC_NWE high to FSMC_ALE invalid 3THCLK– 2  - ns


1. CL = 30 pF.


DS8626 Rev 12 161/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Table 86. Switching characteristics for NAND flash write cycles** **[(1)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


tw(NWE) FSMC_NWE low width 4THCLK–1 4THCLK+ 3 ns

tv(NWE-D) FSMC_NWE low to FSMC_D[15-0] valid          - 0 ns

th(NWE-D) FSMC_NWE high to FSMC_D[15-0] invalid 3THCLK –2          - ns

td(D-NWE) FSMC_D[15-0] valid before FSMC_NWE high 5THCLK–3          - ns

td(ALE-NWE) FSMC_ALE valid before FSMC_NWE low          - 3THCLK ns

th(NWE-ALE) FSMC_NWE high to FSMC_ALE invalid 3THCLK–2          - ns


1. CL = 30 pF.


**6.3.27** **Camera interface (DCMI) timing specifications**


Unless otherwise specified, the parameters given in _Table 87_ for DCMI are derived from
tests performed under the ambient temperature, fHCLK frequency and VDD supply voltage
summarized in _Table 13_, with the following configuration:

- PCK polarity: falling

- VSYNC and HSYNC polarity: high

- Data format: 14 bits


**Figure 70. DCMI timing diagram**


1/DCMI_PIXCLK


DCMI_PIXCLK


th(HSYNC)


th(HSYNC)


DCMI_HSYNC


DCMI_VSYNC


DATA[0:13]


tsu(HSYNC)


tsu(VSYNC)


tsu(DATA) th(DATA)


MS32414V2


**Table 87. DCMI characteristics** **[(1)]**


**Symbol** **Parameter** **Min** **Max** **Unit**


- Frequency ratio DCMI_PIXCLK/fHCLK                 - 0.4                 

DCMI_PIXCLK Pixel clock input      - 54 MHz


Dpixel Pixel clock input duty cycle 30 70 %


162/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Electrical characteristics**


**Table 87. DCMI characteristics** **[(1)]** **(continued)**


**Symbol** **Parameter** **Min** **Max** **Unit**


tsu(DATA) Data input setup time 2.5         

th(DATA) Data hold time 1         


tsu(HSYNC), HSYNC/VSYNC input setup time 2        tsu(VSYNC)


th(HSYNC), HSYNC/VSYNC input hold time 0.5        th(VSYNC)


1. Evaluated by characterization - not tested in production.


**6.3.28** **SD/SDIO MMC card host interface (SDIO) characteristics**


ns


Unless otherwise specified, the parameters given in _Table 88_ are derived from tests
performed under ambient temperature, fPCLKx frequency and VDD supply voltage conditions
summarized in _Table 14_ with the following configuration:

- Output speed is set to OSPEEDRy[1:0] = 10

- Capacitive load C = 30 pF

- Measurement points are done at CMOS levels: 0.5VDD

Refer to _Section 6.3.16: I/O port characteristics_ for more details on the input/output
characteristics.


**Figure 71. SDIO high-speed mode**


DS8626 Rev 12 163/206



**Electrical characteristics** **STM32F405xx, STM32F407xx**


**Figure 72. SD default mode**


CK


tOVD tOHD


D, CMD
(output)


ai14888


**Table 88. Dynamic characteristics: SD/MMC characteristics** **[(1)]**


**Symbol** **Parameter** **Conditions** Min Typ Max Unit


fPP Clock frequency in data transfer mode - 0 - 48 MHz

SDIO_CK/fPCLK2 frequency ratio        -        -        - 8/3        
tW(CKL) Clock low time fPP = 48 MHz 8.5 9 ns
tW(CKH) Clock high time fPP = 48 MHz 8.3 10 

CMD, D inputs (referenced to CK) in MMC and SD HS mode


tISU Input setup time HS fPP = 48 MHz 3 - ns
tIH Input hold time HS fPP = 48 MHz 0 - 

CMD, D outputs (referenced to CK) in MMC and SD HS mode


tOV Output valid time HS fPP = 48 MHz - 4.5 6
ns
tOH Output hold time HS fPP = 48 MHz 1 - 

CMD, D inputs (referenced to CK) in SD default mode


tISUD Input setup time SD fPP = 24 MHz 1.5 - ns
tIHD Input hold time SD fPP = 24 MHz 0.5 - 

CMD, D outputs (referenced to CK) in SD default mode


tOVD Output valid default time SD fPP = 24 MHz - 4.5 7
ns
tOHD Output hold default time SD fPP = 24 MHz 0.5 - 

1. Evaluated by characterization - not tested in production.


**6.3.29** **RTC characteristics**


**Table 89. RTC characteristics**


**Symbol** **Parameter** **Conditions** **Min** **Max**


Any read/write operation

- fPCLK1/RTCCLK frequency ratio from/to an RTC register 4              

164/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Package information**

### **7 Package information**


In order to meet environmental requirements, ST offers these devices in different grades of
ECOPACK packages, depending on their level of environmental compliance. ECOPACK
specifications, grade definitions and product status are available at: _www.st.com_ .
ECOPACK is an ST trademark.

#### **7.1 Device marking**


Refer to technical note “Reference device marking schematics for STM32 microcontrollers
and microprocessors” (TN1433), available on _www.st.com_, for the location of pin 1 / ball A1
as well as the location and orientation of the marking areas versus pin 1 / ball A1.


Parts marked as “ES”, “E”, or accompanied by an engineering sample notification letter, are
not yet qualified and therefore not approved for use in production. ST is not responsible for
any consequences resulting from such use. In no event will ST be liable for the customer
using any of these engineering samples in production. ST’s Quality department must be
contacted prior to any decision to use these engineering samples to run a qualification
activity.


A WLCSP simplified marking example (if any) is provided in the corresponding package
information subsection.


DS8626 Rev 12 165/206



**Package information** **STM32F405xx, STM32F407xx**

#### **7.2 WLCSP90 package information**


**Figure 73. WLCSP90 - 4.223 x 3.969 mm, 0.400 mm pitch wafer level chip scale**
**package outline**


A


J


e1


e

10 1


BOTTOM VIEW
BUMP SIDE


FRONT VIEW


D


A1 orientation
reference


TOP VIEW
WAFER BACK SIDE


A1 ball location


e


e2


G


F


Bump


eee


E


aaa
(4X)


b


ccc Z X Y

ddd Z


bbb Z


Detail A


A3


A2


A


SIDE VIEW


A1


Seating plane


Detail A
(Rotated 90°)


Z


A0JW_ME_V4


1. Drawing is not to scale.


166/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Package information**


**Table 90. WLCSP90 - 4.223 x 3.969 mm, 0.400 mm pitch wafer level chip scale**
**package mechanical data**

**millimeters** **inches** **[(1)]**
**Symbol**

**Min** **Typ** **Max** **Min** **Typ** **Max**


A 0.540 0.570 0.600 0.0213 0.0224 0.0236


A1        - 0.190        -        - 0.0075        

A2        - 0.380        -        - 0.0150        


A3 [(2)]

b [(3)]


  - 0.025  -  - 0.0010  

0.240 0.270 0.300 0.0094 0.0106 0.0118


D 4.188 4.223 4.258 0.1649 0.1663 0.1676


E 3.934 3.969 4.004 0.1549 0.1563 0.1576


e   - 0.400   -   - 0.0157   

e1   - 3.600   -   - 0.1417   

e2   - 3.200   -   - 0.1260   

F   - 0.3115   -   - 0.0123   

G   - 0.3845   -   - 0.0151   

aaa   - 0.100   -   - 0.0039   

bbb   - 0.100   -   - 0.0039   

ccc   - 0.100   -   - 0.0039   

ddd   - 0.050   -   - 0.0020   

eee   - 0.050   -   - 0.0020   

1. Values in inches are converted from mm and rounded to 4 decimal digits.


2. Back side coating.


3. Dimension is measured at the maximum bump diameter parallel to primary datum Z.


**Figure 74. WLCSP90 - 4.223 x 3.969 mm, 0.400 mm pitch wafer level chip scale**
**package recommended footprint**


Dpad


Dsm MS18965V2


DS8626 Rev 12 167/206



**Package information** **STM32F405xx, STM32F407xx**


**Table 91. WLCSP90 recommended PCB design rules**


**Dimension** **Recommended values**


Pitch 0.4 mm


260 µm max. (circular)
Dpad
220 µm recommended


Dsm 300 µm min. (for 260 µm diameter pad)


PCB pad design Non-solder mask defined via underbump allowed


**Device marking for WLCSP90**


The following figure gives an example of topside marking and ball A1 position identifier
location.


The printed markings may differ depending on the supply chain.
Other optional marking or inset/upset marks, which depend on supply chain operations, are
not indicated below.


**Figure 75. WLCSP90 marking example (package top view)**


Product identification(1)

### F405OEB


Ball A1
indentifer


Revision code
Date code
### Y WW R


MSv36120V1


1. Parts marked as “ES”, “E” or accompanied by an Engineering Sample notification letter, are not yet
qualified and therefore not yet ready to be used in production and any consequences deriving from such
usage will not be at ST charge. In no event, ST will be liable for any customer usage of these engineering
samples in production. ST Quality has to be contacted prior to any decision to use these Engineering
Samples to run qualification activity.


168/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Package information**

#### **7.3 LQFP64 package information (5W)**


This LQFP is 64-pin, 10 x 10 mm low-profile quad flat package.


**Figure 76. LQFP64 - Outline** **[(15)]**


BOTTOM VIEW


(2)



~~(~~ L1)


R1


R2


B


B

L


H




D 1/4


4x N/4 TIPS

aaa C A-B D


(13) (N – 4)x e


A


(6)


E 1/4


S


(1) (11)


GAUGE PLANE


WITH PLATING


bbb H A-B D 4x


C


0.05


A2 A1 [(12)] b ddd C A-B D ccc


C


(11) (11)


c c1


(4)


(5) (2)


(10) N


1
2
3


D


D1


E 1/4


D (3)


(4)


SECTION A-A


(9)(11)

b


(3) A D 1/4 (6) B (3) (2)(5)

E1 E


b1


D 1/4


(6)


(11)


A A
(Section A-A)


SECTION B-B


BASE METAL


5W_LQFP64_ME_V1


TOP VIEW


DS8626 Rev 12 169/206



**Package information** **STM32F405xx, STM32F407xx**


**Table 92. LQFP64 - Mechanical data**

**millimeters** **inches** **[(14)]**
**Symbol**

**Min** **Typ** **Max** **Min** **Typ** **Max**


A        -        - 1.60        -        - 0.0630

A1 [(12)] 0.05        - 0.15 0.0020        - 0.0059

A2 1.35 1.40 1.45 0.0531 0.0551 0.0570

b [(9)(11)] 0.17 0.22 0.27 0.0067 0.0087 0.0106

b1 [(11)] 0.17 0.20 0.23 0.0067 0.0079 0.0091

c [(11)] 0.09          - 0.20 0.0035          - 0.0079

c1 [(11)] 0.09         - 0.16 0.0035         - 0.0063

D [(4)] 12.00 BSC 0.4724 BSC

D1 [(2)(5)] 10.00 BSC 0.3937 BSC

E [(4)] 12.00 BSC 0.4724 BSC

E1 [(2)(5)] 10.00 BSC 0.3937 BSC

e 0.50 BSC 0.1970 BSC

L 0.45 0.60 0.75 0.0177 0.0236 0.0295

L1 1.00 REF 0.0394 REF

N [(13)] 64


θ 0° 3.5° 7° 0° 3.5° 7°


θ1 0°         -         - 0°         -         

θ2 10° 12° 14° 10° 12° 14°


θ3 10° 12° 14° 10° 12° 14°


R1 0.08        -        - 0.0031        -        
R2 0.08        - 0.20 0.0031        - 0.0079

S 0.20        -        - 0.0079        -        
aaa [(1)] 0.20 0.0079

bbb [(1)] 0.20 0.0079

ccc [(1)] 0.08 0.0031

ddd [(1)] 0.08 0.0031


170/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Package information**


**Notes:**


1. Dimensioning and tolerancing schemes conform to ASME Y14.5M-1994.

2. The Top package body size may be smaller than the bottom package size by as much
as 0.15 mm.

3. Datums A-B and D to be determined at datum plane H.

4. To be determined at seating datum plane C.

5. Dimensions D1 and E1 do not include mold flash or protrusions. Allowable mold flash
or protrusions is “0.25 mm” per side. D1 and E1 are Maximum plastic body size
dimensions including mold mismatch.

6. Details of pin 1 identifier are optional but must be located within the zone indicated.

7. All Dimensions are in millimeters.

8. No intrusion allowed inwards the leads.

9. Dimension “b” does not include dambar protrusion. Allowable dambar protrusion shall
not cause the lead width to exceed the maximum “b” dimension by more than 0.08 mm.
Dambar cannot be located on the lower radius or the foot. Minimum space between
protrusion and an adjacent lead is 0.07 mm for 0.4 mm and 0.5 mm pitch packages.

10. Exact shape of each corner is optional.

11. These dimensions apply to the flat section of the lead between 0.10 mm and 0.25 mm
from the lead tip.

12. A1 is defined as the distance from the seating plane to the lowest point on the package
body.

13. “N” is the number of terminal positions for the specified body size.

14. Values in inches are converted from mm and rounded to 4 decimal digits.

15. Drawing is not to scale.


DS8626 Rev 12 171/206



**Package information** **STM32F405xx, STM32F407xx**

#### **7.4 LQFP100 package information (1L)**


This LQFP is a 100-pin, 14 x 14 mm low-profile quad flat package.


_Note:_ _See list of notes in the notes section._


**Figure 77. LQFP100 - Outline** **[(15)]**


�2 ��


(2)


R1


R2


B


GAUGE PLANE


H


B          
�� L


L


D1/4


(6)


E1/4


S


B


4x N/4 TIPS


4x


aaaC A-BD
bbb H A-B D


(1) (11)


BOTTOM VIEW


(N-4) x e


(13)


A


C


0.05
A2 A1 b aaa C A-BD ccc C

(12)


SIDE VIEW


D (4)

(2) (5) D1


~~(~~ L1)


SECTION A-A


(9) (11)

b


WITH PLATING


(11)


(11)


c c1


~~b~~ 1

(11)


SECTION B-B


(10)


A


BASE METAL


1L_LQFP100_ME_V3


1
2
3


D
N


E1/4


D1/4


(6)


TOP VIEW


(3)


SECTION A-A


B


(4)


(2)


(5)


E1 E


A A


172/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Package information**


**Table 93. LQFP100 - Mechanical data**

**millimeters** **inches** **[(14)]**
**Symbol**

**Min** **Typ** **Max** **Min** **Typ** **Max**


A        - 1.50 1.60        - 0.0590 0.0630

A1 [(12)] 0.05        - 0.15 0.0019        - 0.0059


A2 1.35 1.40 1.45 0.0531 0.0551 0.0570

b [(9)(11)] 0.17 0.22 0.27 0.0067 0.0087 0.0106

b1 [(11)] 0.17 0.20 0.23 0.0067 0.0079 0.0090

c [(11)] 0.09          - 0.20 0.0035          - 0.0079

c1 [(11)] 0.09         - 0.16 0.0035         - 0.0063

D [(4)] 16.00 BSC 0.6299 BSC

D1 [(2)(5)] 14.00 BSC 0.5512 BSC

E [(4)] 16.00 BSC 0.6299 BSC

E1 [(2)(5)] 14.00 BSC 0.5512 BSC


e 0.50 BSC 0.0197 BSC


L 0.45 0.60 0.75 0.177 0.0236 0.0295

L1 [(1)(11)] 1.00        - 0.0394        
N [(13)] 100


θ 0° 3.5° 7° 0° 3.5° 7°


θ1 0°         -         - 0°         -         

θ2 10° 12° 14° 10° 12° 14°


θ3 10° 12° 14° 10° 12° 14°


R1 0.08        -        - 0.0031        -        

R2 0.08        - 0.20 0.0031        - 0.0079


S 0.20        -        - 0.0079        -        
aaa [(1)] 0.20 0.0079

bbb [(1)] 0.20 0.0079

ccc [(1)] 0.08 0.0031

ddd [(1)] 0.08 0.0031


DS8626 Rev 12 173/206



**Package information** **STM32F405xx, STM32F407xx**


**Notes:**


1. Dimensioning and tolerancing schemes conform to ASME Y14.5M-1994.

2. The top package body size may be smaller than the bottom package size by as much
as 0.15 mm.

3. Datums A-B and D to be determined at datum plane H.

4. To be determined at the seating datum plane C.

5. Dimensions D1 and E1 do not include mold flash or protrusions. Allowable mold flash
or protrusions is 0.25 mm per side. D1 and E1 are maximum plastic body size
dimensions including mold mismatch.

6. Details of pin 1 identifier are optional but must be located within the zone indicated.

7. All dimensions are in millimeters.

8. No intrusion is allowed inwards the leads.

9. Dimension b does not include a dambar protrusion. Allowable dambar protrusion shall
not cause the lead width to exceed the maximum b dimension by more than 0.08 mm.
The dambar cannot be located on the lower radius or the foot. The minimum space
between the protrusion and an adjacent lead is 0.07 mm for 0.4 mm and 0.5 mm pitch
packages.

10. The exact shape of each corner is optional.

11. These dimensions apply to the flat section of the lead that is between 0.10 mm and
0.25 mm from the lead tip.

12. A1 is defined as the distance from the seating plane to the lowest point on the package
body.

13. N is the number of terminal positions for the specified body size.

14. Values in inches are converted from mm and rounded to four decimal digits.

15. Drawing is not to scale.


**Figure 78. LQFP100 - Footprint example**


75 51


76 50
0.5


0.3


16.7 14.3


100 26


1.2



1. Dimensions are expressed in millimeters.


174/206 DS8626 Rev 12



12.3


16.7


1L_LQFP100_FP_V1


**STM32F405xx, STM32F407xx** **Package information**

#### **7.5 LQFP144 package information (1A)**


This LQFP is a 144-pin, 20 x 20 mm low-profile quad flat package.


_Note:_ _See list of notes in the notes section._


**Figure 79. LQFP144 - Outline** **[(15)]**


BOTTOM VIEW



(2)


R1


B


B

L


H




R2


(6)
D 1/4


GAUGE PLANE


S


E 1/4


(L1)


(1)


(1) (11)

4x N/4 TIPS


bbb H A-B D 4x


C


ccc C


(4)


(2)(5)


WITH PLATING


A


aaa C A-B D


(N-4)x e


0.05 A2 A1(12) b ddd C A-B D


(4)


(10)


D


SECTION A-A


(9)(11)

b


2
3


D
D1

(3)
N


E 1/4


(11)c c1(11)


D 1/4


(6)


(3) A B (3) (2)(5)


E1 E


b1


(11)


SECTION B-B


BASE METAL


1A_LQFP144_ME_V2


A A
(Section A-A)


TOP VIEW


DS8626 Rev 12 175/206



**Package information** **STM32F405xx, STM32F407xx**


**Table 94. LQFP144 - Mechanical data**

**millimeters** **inches** **[(14)]**
**Symbol**

**Min** **Typ** **Max** **Min** **Typ** **Max**


A       -       - 1.60       -       - 0.0630

A1 [(12)] 0.05       - 0.15 0.0020       - 0.0059


A2 1.35 1.40 1.45 0.0531 0.0551 0.0571

b [(9)(11)] 0.17 0.22 0.27 0.0067 0.0087 0.0106

b1 [(11)] 0.17 0.20 0.23 0.0067 0.0079 0.0090

c [(11)] 0.09         - 0.20 0.0035         - 0.0079

c1 [(11)] 0.09        - 0.16 0.0035        - 0.0063

D [(4)] 22.00 BSC 0.8661 BSC

D1 [(2)(5)] 20.00 BSC 0.7874 BSC

E [(4)] 22.00 BSC 0.8661 BSC

E1 [(2)(5)] 20.00 BSC 0.7874 BSC


e 0.50 BSC 0.0197 BSC


L 0.45 0.60 0.75 0.0177 0.0236 0.0295


L1 1.00 REF 0.0394 REF

N [(13)] 144


θ 0° 3.5° 7° 0° 3.5° 7°


θ1 0°        -        - 0°        -        

θ2 10° 12° 14° 10° 12° 14°


θ3 10° 12° 14° 10° 12° 14°


R1 0.08        -        - 0.0031        -        

R2 0.08        - 0.20 0.0031        - 0.0079


S 0.20       -       - 0.0079       -       

aaa 0.20 0.0079


bbb 0.20 0.0079


ccc 0.08 0.0031


ddd 0.08 0.0031


176/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Package information**


**Notes:**


1. Dimensioning and tolerancing schemes conform to ASME Y14.5M-1994.

2. The top package body size may be smaller than the bottom package size by as much
as 0.15 mm.

3. Datums A-B and D to be determined at datum plane H.

4. To be determined at the seating datum plane C.

5. Dimensions D1 and E1 do not include mold flash or protrusions. Allowable mold flash
or protrusions is 0.25 mm per side. D1 and E1 are maximum plastic body size
dimensions including mold mismatch.

6. Details of pin 1 identifier are optional but must be located within the zone indicated.

7. All dimensions are in millimeters.

8. No intrusion is allowed inwards the leads.

9. Dimension b does not include a dambar protrusion. Allowable dambar protrusion shall
not cause the lead width to exceed the maximum b dimension by more than 0.08 mm.
The dambar cannot be located on the lower radius or the foot. The minimum space
between the protrusion and an adjacent lead is 0.07 mm for 0.4 mm and 0.5 mm pitch
packages.

10. The exact shape of each corner is optional.

11. These dimensions apply to the flat section of the lead that is between 0.10 mm and
0.25 mm from the lead tip.

12. A1 is defined as the distance from the seating plane to the lowest point on the package
body.

13. N is the number of terminal positions for the specified body size.

14. Values in inches are converted from mm and rounded to four decimal digits.

15. Drawing is not to scale.


DS8626 Rev 12 177/206



**Package information** **STM32F405xx, STM32F407xx**


**Figure 80. LQFP144 - Footprint example**


108 73


1.35




0.35


0.50



19.90 17.85



22.60


1 36


19.90


~~2~~ 2.60


1. Dimensions are expressed in millimeters.


178/206 DS8626 Rev 12


1A_LQFP144_FP


**STM32F405xx, STM32F407xx** **Package information**

#### **7.6 UFBGA(176+25) package information (A0E7)**


This UFBGA is a 176+25-ball, 10 x 10 mm, 0.65 mm pitch, ultra fine pitch ball grid array
package.


**Figure 81. UFBGA(176+25) - Outline**


Seating plane


C


A1 ball
index
area


D


B


A2


A4


A3


A


R


b


E1

e F


ddd C


A1 [A]


A1 ball
identifier


F


D1


e


A


E


15 1


BOTTOM VIEW


1. Drawing is not to scale.


Øb (176 + 25 balls)
TOP VIEW


Ø eee M C A B
Ø fff M C


C
C


A


A0E7_ME_V10


**Table 95. UFBGA(176+25) - Mechanical data**

**millimeters** **inches** **[(1)]**
**Symbol**

**Min.** **Typ.** **Max.** **Min.** **Typ.** **Max.**


A  -  - 0.600  -  - 0.0236


A1 0.050 0.080 0.110 0.0020 0.0031 0.0043


A2  - 0.450  -  - 0.0177  

A3  - 0.130  -  - 0.0051  

A4  - 0.320  -  - 0.0126  

b 0.240 0.290 0.340 0.0094 0.0114 0.0134


D 9.850 10.000 10.150 0.3878 0.3937 0.3996


D1  - 9.100  -  - 0.3583  

E 9.850 10.000 10.150 0.3878 0.3937 0.3996


E1  - 9.100  -  - 0.3583  

e   - 0.650   -   - 0.0256   

F  - 0.450  -  - 0.0177  

ddd  -  - 0.080  -  - 0.0031


DS8626 Rev 12 179/206



**Package information** **STM32F405xx, STM32F407xx**


**Table 95. UFBGA(176+25) - Mechanical data (continued)**

**millimeters** **inches** **[(1)]**
**Symbol**

**Min.** **Typ.** **Max.** **Min.** **Typ.** **Max.**


eee          -          - 0.150          -          - 0.0059


fff                  -                  - 0.050                  -                  - 0.0020


1. Values in inches are converted from mm and rounded to 4 decimal digits.


**Figure 82. UFBGA(176+25) - Footprint example**


Dpad


Dsm

BGA_WLCSP_FT_V1


**Table 96. UFBGA(176+25) - Example of PCB design rules (0.65 mm pitch BGA)**


**Dimension** **Values**


Pitch 0.65 mm


Dpad 0.300 mm


0.400 mm typ. (depends on the soldermask
Dsm
registration tolerance)


Stencil opening 0.300 mm


Stencil thickness Between 0.100 mm and 0.125 mm


Pad trace width 0.100 mm


180/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Package information**

#### **7.7 LQFP176 package information (1T)**


This LQFP is a 176-pin, 24 x 24 mm, 0.5 mm pitch, low profile quad flat package.


_Note:_ _See list of notes in the notes section._


**Figure 83. LQFP176 - Outline** **[(15)]**


�2 �1


(2)


R1


R2


B(See SECTION B-B)

GAUGE PLANE


0.25


H


D1/4


(6)


E1/4
4x
bbb H A-B D


~~S~~


��


B  L


(1) (11)


4x N/4 TIPS


aaaC A-BD


A2 0.05


BOTTOM VIEW SECTION A-A


(N-4) x e ����


(L1)


C
A


A1


(2) (5)


(10)


D
D1

N D


E1/4


(12)


b ddd C A-BD ccc C


SIDE VIEW


(4)


���


(4)


(9) (11)

b WITH PLATING


c1


(5)

(2)


E1 E


~~D~~ 1/4


(6)
���


(11) c c1 (11)


c


b1 BASE METAL

(11)


A B


SECTION A-A


A A


SECTION B-B


TOP VIEW


1T_LQFP176_ME_V2


DS8626 Rev 12 181/206



**Package information** **STM32F405xx, STM32F407xx**


**Table 97. LQFP176 - Mechanical data**

**millimeters** **inches** **[(14)]**
**Symbol**

**Min** **Typ** **Max** **Min** **Typ** **Max**


A        -        - 1.600        -        - 0.0630

A1 [(12)] 0.050        - 0.150 0.0020        - 0.0059

A2 1.350 1.400 1.450 0.0531 0.0551 0.0571

b [(9)(11)] 0.170 0.220 0.270 0.0067 0.0087 0.0106

b1 [(11)] 0.170 0.200 0.230 0.0067 0.0079 0.0091

c [(11)] 0.090          - 0.200 0.0035          - 0.0079

c1 [(11)] 0.090         - 0.160 0.0035         - 0.063

D [(4)] 26.000 1.0236

D1 [(2)(5)] 24.000 0.9449

E [(4)] 26.000 0.0197

E1 [(2)(5)] 24.000 0.9449

e 0.500 0.1970

L 0.450 0.600 0.750 0.0177 0.0236 0.0295

L1 [(1)(11)] 1 0.0394 REF

N [(13)] 176


θ 0° 3.5° 7° 0° 3.5° 7°


θ1 0°         -         - 0°         -         

θ2 10° 12° 14° 10° 12° 14°


θ3 10° 12° 14° 10° 12° 14°


R1 0.080        -        - 0.0031        -        
R2 0.080        - 0.200 0.0031        - 0.0079

S 0.200        -        - 0.0079        -        
aaa [(1)] 0.200 0.0079

bbb [(1)] 0.200 0.0079

ccc [(1)] 0.080 0.0031

ddd [(1)] 0.080 0.0031


182/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Package information**


**Notes:**


1. Dimensioning and tolerancing schemes conform to ASME Y14.5M-1994.

2. The top package body size may be smaller than the bottom package size by as much
as 0.15 mm.

3. Datums A-B and D to be determined at datum plane H.

4. To be determined at the seating datum plane C.

5. Dimensions D1 and E1 do not include mold flash or protrusions. Allowable mold flash
or protrusions is 0.25 mm per side. D1 and E1 are maximum plastic body size
dimensions including mold mismatch.

6. Details of pin 1 identifier are optional but must be located within the zone indicated.

7. All dimensions are in millimeters.

8. No intrusion is allowed inwards the leads.

9. Dimension b does not include a dambar protrusion. Allowable dambar protrusion shall
not cause the lead width to exceed the maximum b dimension by more than 0.08 mm.
The dambar cannot be located on the lower radius or the foot. The minimum space
between the protrusion and an adjacent lead is 0.07 mm for 0.4 mm and 0.5 mm pitch
packages.

10. The exact shape of each corner is optional.

11. These dimensions apply to the flat section of the lead that is between 0.10 mm and
0.25 mm from the lead tip.

12. A1 is defined as the distance from the seating plane to the lowest point on the package
body.

13. N is the number of terminal positions for the specified body size.

14. Values in inches are converted from mm and rounded to four decimal digits.

15. Drawing is not to scale.


DS8626 Rev 12 183/206



**Package information** **STM32F405xx, STM32F407xx**


**Figure 84. LQFP176 - Footprint example**


1.2


1 [176]


44
45


21.8


26.7


1. Dimensions are expressed in millimeters.


184/206 DS8626 Rev 12


0.5


0.3


133
132


89
88
1.2


1T_FP_V1


**STM32F405xx, STM32F407xx** **Package information**

#### **7.8 Thermal characteristics**


The maximum chip-junction temperature, TJ max, in degrees Celsius, may be calculated
using the following equation:


TJ max = TA max + (PD max x Θ JA)

Where:

- TA max is the maximum ambient temperature in ° C,

- Θ JA is the package junction-to-ambient thermal resistance, in ° C/W,

- PD max is the sum of PINT max and PI/O max (PD max = PINT max + PI/Omax),

- PINT max is the product of IDD and VDD, expressed in Watts. This is the maximum chip
internal power.


PI/O max represents the maximum power dissipation on output pins where:

PI/O max = Σ (VOL × IOL) + Σ ((VDD – VOH) × IOH),

taking into account the actual VOL / IOL and VOH / IOH of the I/Os at low and high level in the
application.


**Table 98. Package thermal characteristics**


**Symbol** **Parameter** **Value** **Unit**


**Thermal resistance junction-ambient**
46
LQFP64 - 10 × 10 mm / 0.5 mm pitch


**Thermal resistance junction-ambient**
43
LQFP100 - 14 × 14 mm / 0.5 mm pitch


Θ JA


**Thermal resistance junction-ambient**
40
LQFP144 - 20 × 20 mm / 0.5 mm pitch


**Thermal resistance junction-ambient**
38
LQFP176 - 24 × 24 mm / 0.5 mm pitch


**Thermal resistance junction-ambient**
39
UFBGA176 - 10× 10 mm / 0.65 mm pitch


**Thermal resistance junction-ambient**
38.1
WLCSP90 - 0.400 mm pitch


°C/W


**Reference document**


JESD51-2 Integrated Circuits Thermal Test Method Environment Conditions - Natural
Convection (Still Air). Available from www.jedec.org.


DS8626 Rev 12 185/206



**Ordering information** **STM32F405xx, STM32F407xx**

### **8 Ordering information**


Example: STM32 F 405 R E T 6 xxx


**Device family**

STM32 = Arm-based 32-bit microcontroller


**Product type**

F = general-purpose


**Device subfamily**

405 = STM32F40xxx, connectivity

407= STM32F40xxx, connectivity, camera interface, Ethernet


**Pin count**

R = 64 pins

O = 90 pins

V = 100 pins

Z = 144 pins

I = 176 pins


**Flash memory size**

E = 512 Kbytes of flash memory

G = 1024 Kbytes of flash memory


**Package**

T = LQFP

H = UFBGA

Y = WLCSP


**Temperature range**

6 = Industrial temperature range, –40 to 85 °C.

7 = Industrial temperature range, –40 to 105 °C.


**Options**

xxx = programmed parts

TR = tape and reel


For a list of available options (speed, package, etc.) or for further information on any aspect
of this device, please contact your nearest ST sales office.


186/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Application block diagrams**

### **Appendix A Application block diagrams**

#### **A.1 USB OTG full speed (FS) interface solutions**


**Figure 85. USB controller configured as peripheral-only and used**
**in Full speed mode**


VDD

5V to VDD
Volatge regulator [(1)]


STM32F4xx


VBUS


DM


DP


OSC_IN


OSC_OUT


PA11//PB14


PA12/PB15

VSS


MS19000V5


1. External voltage regulator only needed when building a VBUS powered device.

2. The same application can be developed using the OTG HS in FS mode to achieve enhanced performance
thanks to the large Rx/Tx FIFO and to a dedicated DMA controller.


**Figure 86. USB controller configured as host-only and used in full speed mode**


VDD


EN
GPIO


5 V Pwr


Current limiter
power switch [(1)]


Overcurrent


VBUS


DM


DP


VSS


STM32F4xx


OSC_IN


OSC_OUT


GPIO+IRQ


PA11//PB14


PA12/PB15


MS19001V4


1. The current limiter is required only if the application has to support a VBUS powered device. A basic power
switch can be used if 5 V are available on the application board.

2. The same application can be developed using the OTG HS in FS mode to achieve enhanced performance
thanks to the large Rx/Tx FIFO and to a dedicated DMA controller.


DS8626 Rev 12 187/206



**Application block diagrams** **STM32F405xx, STM32F407xx**


**Figure 87. USB controller configured in dual mode and used in full speed mode**


VDD


5 V to VDD
voltage regulator [(1)]


VDD


EN
GPIO


5 V Pwr


Current limiter
power switch [(2)]


Overcurrent


STM32F4xx


OSC_IN


OSC_OUT


GPIO+IRQ


PA9/PB13


PA11/PB14


PA12/PB15


ID [(3)]
PA10/PB12


VSS


VBUS


DM


DP


MS19002V3


1. External voltage regulator only needed when building a VBUS powered device.

2. The current limiter is required only if the application has to support a VBUS powered device. A basic power
switch can be used if 5 V are available on the application board.

3. The ID pin is required in dual role only.

4. The same application can be developed using the OTG HS in FS mode to achieve enhanced performance
thanks to the large Rx/Tx FIFO and to a dedicated DMA controller.


188/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Application block diagrams**

#### **A.2 USB OTG high speed (HS) interface solutions**


**Figure 88. USB controller configured as peripheral, host, or dual-mode**
**and used in high speed mode**


STM32F4xx


DP


DM


ULPI_CLK


ULPI_D[7:0]


ULPI_DIR


ULPI_STP


ULPI_NXT


VBUS


VSS


USB HS

OTG Ctrl


FS PHY


ULPI


not connected


DP


DM

ID [(2)] USB


connector


MS19005V2


High speed
OTG PHY


XT1

PLL
24 or 26 MHz XT [(1)]


MCO1 or MCO2


XI


1. It is possible to use MCO1 or MCO2 to save a crystal. It is however not mandatory to clock the
STM32F40xxx with a 24 or 26 MHz crystal when using USB HS. The above figure only shows an example
of a possible connection.

2. The ID pin is required in dual role only.


DS8626 Rev 12 189/206



**Application block diagrams** **STM32F405xx, STM32F407xx**

#### **A.3 Ethernet interface solutions**


**Figure 89. MII mode using a 25 MHz crystal**


STM32


MII_TX_CLK
MII_TX_EN
MII_TXD[3:0]
MII_CRS
MII_COL


MII
= 15 pins


MCU
Ethernet MII_TX_EN Ethernet

MII_TXD[3:0]

MAC 10/100 PHY 10/100


HCLK [(1] ~~[)]~~


MII + MDC
= 17 pins


MS19968V1


Ethernet
PHY 10/100


Timer
input
trigger


IEEE1588 PTP


trigger Timestamp

TIM2
comparator


MII_RX_CLK
MII_RXD[3:0]
MII_RX_DV
MII_RX_ER


MDIO
MDC


PPS_OUT [(2)]


PHY_CLK 25 MHz
XT1


XTAL
25 MHz


OSC


PLL HCLK


MCO1/MCO2


1. fHCLK must be greater than 25 MHz.

2. Pulse per second when using IEEE1588 PTP optional signal.


**Figure 90. RMII with a 50 MHz oscillator**


STM32


MCU
Ethernet
MAC 10/100


HCLK [(1] ~~[)]~~


RMII_TX_EN


RMII_TXD[1:0]


RMII_RXD[1:0]


RMII_CRX_DV

RMII_REF_CLK


MDIO


MDC


RMII
= 7 pins

RMII + MDC
= 9 pins


Timer
input
trigger


IEEE1588 PTP


trigger Timestamp

TIM2
comparator


OSC
50 MHz


/2 or /20
2.5 or 25 MHz synchronous 50 MHz


PLL HCLK


PHY_CLK  50 MHz XT1


50 MHz


MS19969V1


1. fHCLK must be greater than 25 MHz.


190/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Application block diagrams**


**Figure 91. RMII with a 25 MHz crystal and PHY with PLL**


STM32F


MCU
Ethernet
MAC 10/100


HCLK [(1] ~~[)]~~


Ethernet
PHY 10/100


RMII
= 7 pins


REF_CLK


RMII_TX_EN


RMII_TXD[1:0]


RMII_RXD[1:0]


RMII_CRX_DV

RMII_REF_CLK


MDIO


MDC


Timer
input
trigger


IEEE1588 PTP


trigger Timestamp

TIM2
comparator


/2 or /20
2.5 or 25 MHz synchronous 50 MHz


RMII + MDC
= 9 pins


MS19970V1


PLL


XTAL
25 MHz OSC


PLL HCLK

MCO1/MCO2 PHY_CLK  25 MHz XT1


1. fHCLK must be greater than 25 MHz.

2. The 25 MHz (PHY_CLK) must be derived directly from the HSE oscillator, before the PLL block.


DS8626 Rev 12 191/206



**Important security notice** **STM32F405xx, STM32F407xx**

### **9 Important security notice**


The STMicroelectronics group of companies (ST) places a high value on product security,
which is why the ST product(s) identified in this documentation may be certified by various
security certification bodies and/or may implement our own security measures as set forth
herein. However, no level of security certification and/or built-in security measures can
guarantee that ST products are resistant to all forms of attacks. As such, it is the
responsibility of each of ST's customers to determine if the level of security provided in an
ST product meets the customer needs both in relation to the ST product alone, as well as
when combined with other components and/or software for the customer end product or
application. In particular, take note that:

- ST products may have been certified by one or more security certification bodies, such
as Platform Security Architecture (www.psacertified.org) and/or Security Evaluation
standard for IoT Platforms (www.trustcb.com). For details concerning whether the ST
product(s) referenced herein have received security certification along with the level
and current status of such certification, either visit the relevant certification standards
website or go to the relevant product page on www.st.com for the most up to date
information. As the status and/or level of security certification for an ST product can
change from time to time, customers should re-check security certification status/level
as needed. If an ST product is not shown to be certified under a particular security
standard, customers should not assume it is certified.

- Certification bodies have the right to evaluate, grant and revoke security certification in
relation to ST products. These certification bodies are therefore independently
responsible for granting or revoking security certification for an ST product, and ST
does not take any responsibility for mistakes, evaluations, assessments, testing, or
other activity carried out by the certification body with respect to any ST product.

- Industry-based cryptographic algorithms (such as AES, DES, or MD5) and other open
standard technologies which may be used in conjunction with an ST product are based
on standards which were not developed by ST. ST does not take responsibility for any
flaws in such cryptographic algorithms or open technologies or for any methods which
have been or may be developed to bypass, decrypt or crack such algorithms or
technologies.

- While robust security testing may be done, no level of certification can absolutely
guarantee protections against all attacks, including, for example, against advanced
attacks which have not been tested for, against new or unidentified forms of attack, or
against any form of attack when using an ST product outside of its specification or
intended use, or in conjunction with other components or software which are used by
customer to create their end product or application. ST is not responsible for resistance
against such attacks. As such, regardless of the incorporated security features and/or
any information or support that may be provided by ST, each customer is solely
responsible for determining if the level of attacks tested for meets their needs, both in
relation to the ST product alone and when incorporated into a customer end product or
application.

- All security features of ST products (inclusive of any hardware, software,
documentation, and the like), including but not limited to any enhanced security
features added by ST, are provided on an "AS IS" BASIS. AS SUCH, TO THE EXTENT
PERMITTED BY APPLICABLE LAW, ST DISCLAIMS ALL WARRANTIES, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, unless the
applicable written and signed contract terms specifically provide otherwise.


192/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Revision history**

### **10 Revision history**


**Table 99. Document revision history**


**Date** **Revision** **Changes**


15-Sep-2011 1 Initial release.


24-Jan-2012 2


Added WLCSP90 package on cover page.
Renamed USART4 and USART5 into UART4 and UART5,
respectively.
Updated number of USB OTG HS and FS in Table 3: STM32F405xx
and STM32F407xx: features and peripheral counts.
Updated Figure 3: Compatible board design between
STM32F10xx/STM32F2/STM32F40xxx for LQFP144 package and
Figure 4: Compatible board design between STM32F2 and
STM32F40xxx for LQFP176 and BGA176 packages, and removed
note 1 and 2.
Updated Section 3.0.9: Flexible static memory controller (FSMC).
Modified I/Os used to reprogram the flash memory for CAN2 and USB
OTG FS in Section 3.0.13: Boot modes.
Updated note in Section 3.0.14: Power supply schemes.
PDR_ON no more available on LQFP100 package. Updated Section
3.0.16: Voltage regulator. Updated condition to obtain a minimum
supply voltage of 1.7 V in the whole document.
Renamed USART4/5 to UART4/5 and added LIN and IrDA feature for
UART4 and UART5 in Table 6: USART feature comparison.
Removed support of I2C for OTG PHY in Section 3.0.30: Universal
serial bus on-the-go full-speed (OTG_FS).
Added Table 7: Legend/abbreviations used in the pinout table.
Table 8: STM32F40xxx pin and ball definitions: replaced VSS_3,
VSS_4, and VSS_8 by VSS; reformatted Table 8: STM32F40xxx pin
and ball definitions to better highlight I/O structure, and alternate
functions versus additional functions; signal corresponding to
LQFP100 pin 99 changed from PDR_ON to VSS; EVENTOUT added
in the list of alternate functions for all I/Os; ADC3_IN8 added as
alternate function for PF10; FSMC_CLE and FSMC_ALE added as
alternate functions for PD11 and PD12, respectively; PH10 alternate
function TIM15_CH1_ETR renamed TIM5_CH1; updated PA4 and PA5
I/O structure to TTa.
Removed OTG_HS_SCL, OTG_HS_SDA, OTG_FS_INTN in Table 8:
STM32F40xxx pin and ball definitions and Table 10: Alternate function
mapping.
Changed TCM data RAM to CCM data RAM in Figure 18:
STM32F40xxx memory map.
Added IVDD and IVSS maximum values in Table 14: Current
characteristics.
Added Note 1 related to fHCLK, updated Note 2 in Table 16: General
operating conditions, and added maximum power dissipation values.
Updated Table 17: Limitations depending on the operating power
supply range.


DS8626 Rev 12 193/206



**Revision history** **STM32F405xx, STM32F407xx**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


2
24-Jan-2012
(continued)


Added V12 in Table 21: Embedded reset and power control block
characteristics.
Updated Table 23: Typical and maximum current consumption in Run
mode, code with data processing  running from flash memory (ART
accelerator disabled) and Table 22: Typical and maximum current
consumption in Run mode, code with data processing  running from
flash memory (ART accelerator enabled) or RAM. Added Figure,
Figure 25, Figure 26, and Figure 27.
Updated Table 24: Typical and maximum current consumption in Sleep
mode and removed Note 1.
Updated Table 25: Typical and maximum current consumptions in Stop
mode and Table 26: Typical and maximum current consumptions in
Standby mode, Table 27: Typical and maximum current consumptions
in VBAT mode, and Table 29: Switching output I/O current
consumption.
Section : On-chip peripheral current consumption: modified conditions,
and updated Table 30: Peripheral current consumption and Note 2.
Changed fHSE_ext to 50 MHz and tr(HSE)/tf(HSE) maximum value in
Table 32: High-speed external user clock characteristics.
Added Cin(LSE) in Table 33: Low-speed external user clock
characteristics.
Updated maximum PLL input clock frequency, removed related note,
and deleted jitter for MCO for RMII Ethernet typical value in Table 38:
Main PLL characteristics. Updated maximum PLLI2S input clock
frequency and removed related note in Table 39: PLLI2S (audio PLL)
characteristics.
Updated Section : Flash memory to specify that the devices are
shipped to customers with the flash memory erased. Updated Table 41:
Flash memory characteristics, and added tME in Table 42: Flash
memory programming.
Updated Table 45: EMS characteristics, and Table 46: EMI
characteristics.
Updated Table 58: I2S dynamic characteristics
Updated Figure 45: ULPI timing diagram and Table 64: ULPI timing.
Added tCOUNTER and tMAX_COUNT in Table 54: Characteristics of
TIMx connected to the APB1 domain and Table 55: Characteristics of
TIMx connected to the APB2 domain. Updated Table 67: Dynamic
characteristics: Ethernet MAC signals for RMII.
Removed USB-IF certification in Section : USB OTG FS
characteristics.


194/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Revision history**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


2
24-Jan-2012
(continued)


Updated Table 63: USB HS clock timing parameters
Updated Table 69: ADC characteristics.
Updated Table 70: ADC accuracy at fADC = 30 MHz.
Updated Note 1 in Table 76: DAC characteristics.
Section 6.3.26: FSMC characteristics: updated Table 77 toTable 88,
changed CL value to 30 pF, and modified FSMC configuration for
asynchronous timings and waveforms. Updated Figure 59:
Synchronous multiplexed PSRAM write timings.
Updated Table 100: Package thermal characteristics.
Appendix A.1: USB OTG full speed (FS) interface solutions: modified
Figure 93: USB controller configured as peripheral-only and used in
Full speed mode added Note 2, updated Figure 94: USB controller
configured as host-only and used in full speed mode and added Note
2, changed Figure 95: USB controller configured in dual mode and
used in full speed mode and added Note 3.
Appendix A.2: USB OTG high speed (HS) interface solutions: removed
figures USB OTG HS device-only connection in FS mode and USB
OTG HS host-only connection in FS mode, and updated Figure 96:
USB controller configured as peripheral, host, or dual-mode and used
in high speed mode and added Note 2.
Added Appendix A.3: Ethernet interface solutions.


DS8626 Rev 12 195/206



**Revision history** **STM32F405xx, STM32F407xx**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


31-May-2012 3


Updated Figure 5: STM32F40xxx block diagram and Figure 7: Power
supply supervisor interconnection with internal reset OFF
Added SDIO, added notes related to FSMC and SPI/I2S in Table 3:
STM32F405xx and STM32F407xx: features and peripheral counts.
Starting from Silicon revision Z, USB OTG full-speed interface is now
available for all STM32F405xx devices.
Added full information on WLCSP90 package together with
corresponding part numbers.
Changed number of AHB buses to 3.
Modified available flash memory sizes in Section 3.0.4: Embedded
flash memory.
Modified number of maskable interrupt channels in Section 3.0.10:
Nested vectored interrupt controller (NVIC).
Updated case of Regulator ON/internal reset ON, Regulator
ON/internal reset OFF, and Regulator OFF/internal reset ON in Section
3.0.16: Voltage regulator.
Updated standby mode description in Section 3.0.19: Low-power
modes.
Added Note 1 below Figure 16: STM32F40xxx UFBGA176 ballout.
Added Note 1 below Figure 17: STM32F40xxx WLCSP90 ballout.
Updated Table 8: STM32F40xxx pin and ball definitions.
Added Table 9: FSMC pin definition.
Removed OTG_HS_INTN alternate function in Table 8: STM32F40xxx
pin and ball definitions and Table 10: Alternate function mapping.
Removed I2S2_WS on PB6/AF5 in Table 10: Alternate function
mapping.
Replaced JTRST by NJTRST, removed ETH_RMII _TX_CLK, and
modified I2S3ext_SD on PC11 in Table 10: Alternate function
mapping.
Added Table 12: register boundary addresses.
Updated Figure 18: STM32F40xxx memory map.
Updated VDDA and VREF+ decoupling capacitor in Figure 21: Power
supply scheme.
Added power dissipation maximum value for WLCSP90 in Table 16:
General operating conditions.
Updated VPOR/PDR in Table 21: Embedded reset and power control
block characteristics.
Updated notes in Table 23: Typical and maximum current consumption
in Run mode, code with data processing  running from flash memory
(ART accelerator disabled), Table 22: Typical and maximum current
consumption in Run mode, code with data processing  running from
flash memory (ART accelerator enabled) or RAM, and Table 24:
Typical and maximum current consumption in Sleep mode.
Updated maximum current consumption at TA = 25 °n Table 25:
Typical and maximum current consumptions in Stop mode.


196/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Revision history**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


3
31-May-2012
(continued)


Removed fHSE_ext typical value in Table 32: High-speed external user
clock characteristics. Updated Table 34: HSE 4-26 MHz oscillator
characteristics and Table 35: LSE oscillator characteristics (fLSE =
32.768 kHz).
Added fPLL48_OUT maximum value in Table 38: Main PLL
characteristics.
Modified equation 1 and 2 in Section 6.3.11: PLL spread spectrum
clock generation (SSCG) characteristics.
Updated Table 41: Flash memory characteristics, Table 42: Flash
memory programming, and Table 43: Flash memory programming with
VPP.
Updated Section : Output driving current.
Table 56: I2C characteristics: Note 4 updated and applied to th(SDA) in
Fast mode, and removed note 4 related to th(SDA) minimum value.
Updated Table 69: ADC characteristics. Updated note concerning ADC
accuracy vs. negative injection current below Table 70: ADC accuracy
at fADC = 30 MHz.
Added WLCSP90 thermal resistance in Table 100: Package thermal
characteristics.
Updated Table 92: WLCSP90 - 4.223 x 3.969 mm, 0.400 mm pitch
wafer level chip scale package mechanical data.
Updated Figure 87: UFBGA176+25 ball, 10 x 10 mm, 0.65 mm pitch,
ultra fine pitch ball grid array package outline and Table 97:
UFBGA176+25 ball, 10 × 10 × 0.65 mm pitch, ultra thin fine pitch ball
grid array mechanical data.
Added Figure 91: LQFP176 - 176-pin, 24 x 24 mm low profile quad flat
recommended footprint.
Removed 256 and 768 Kbyte flash memory density from Table : .


DS8626 Rev 12 197/206



**Revision history** **STM32F405xx, STM32F407xx**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


04-Jun-2013 4


Modified Note 1 below Table 3: STM32F405xx and STM32F407xx:
features and peripheral counts.
Updated Figure 4 title.
Updated Note 3 below Figure 21: Power supply scheme.
Changed simplex mode into half-duplex mode in Section 3.0.25: Interintegrated sound (I2S).
Replaced DAC1_OUT and DAC2_OUT by DAC_OUT1 and
DAC_OUT2, respectively.
Updated pin 36 signal in Figure 15: STM32F40xxx LQFP176 pinout.
Changed pin number from F8 to D4 for PA13 pin in Table 8:
STM32F40xxx pin and ball definitions.
Replaced TIM2_CH1/TIM2_ETR by TIM2_CH1_ETR for PA0 and PA5
pins in Table 10: Alternate function mapping.
Changed system memory into System memory + OTP in Figure 18:
STM32F40xxx memory map.
Added Note 1 below Table 18: VCAP_1/VCAP_2 operating conditions.
Updated IDDA description in Table 76: DAC characteristics.
Removed PA9/PB13 connection to VBUS in Figure 93: USB controller
configured as peripheral-only and used in Full speed mode and Figure
94: USB controller configured as host-only and used in full speed
mode.
Updated SPI throughput on front page and Section 3.0.24: Serial
peripheral interface (SPI)
Updated operating voltages in Table 3: STM32F405xx and
STM32F407xx: features and peripheral counts.
Updated note in Section 3.0.14: Power supply schemes
Updated Section 3.0.15: Power supply supervisor
Updated “Regulator ON” paragraph in Section 3.0.16: Voltage
regulator
Removed note in Section 3.0.19: Low-power modes
Corrected wrong reference manual in Section 3.0.28: Ethernet MAC
interface with dedicated DMA and IEEE 1588 support
Updated Table 17: Limitations depending on the operating power
supply range
Updated Table 26: Typical and maximum current consumptions in
Standby mode
Updated Table 27: Typical and maximum current consumptions in
VBAT mode
Updated Table 39: PLLI2S (audio PLL) characteristics
Updated Table 46: EMI characteristics
Updated Table 51: Output voltage characteristics
Updated Table 53: NRST pin characteristics
Updated Table 57: SPI dynamic characteristics
Updated Table 58: I2S dynamic characteristics
Deleted Table 59
Updated Table 64: ULPI timing
Updated Figure 46: Ethernet SMI timing diagram


198/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Revision history**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


4
04-Jun-2013
(continued)


Updated Figure 87: UFBGA176+25 ball, 10 x 10 mm, 0.65 mm pitch,
ultra fine pitch ball grid array package outline
Updated Table 97: UFBGA176+25 ball, 10 × 10 × 0.65 mm pitch, ultra
thin fine pitch ball grid array mechanical data
Updated Figure 5: STM32F40xxx block diagram
Updated Section 2: Description
Updated footnote (3) in Table 3: STM32F405xx and STM32F407xx:
features and peripheral counts.
Updated Figure 3: Compatible board design between
STM32F10xx/STM32F2/STM32F40xxx for LQFP144 package
Updated Figure 4: Compatible board design between STM32F2 and
STM32F40xxx for LQFP176 and BGA176 packages
Updated Section 3.0.14: Power supply schemes
Updated Section 3.0.15: Power supply supervisor
Updated Section 3.0.16: Voltage regulator, including figures.
Updated Table 16: General operating conditions, including footnote (2).
Updated Table 17: Limitations depending on the operating power
supply range, including footnote (3).
Updated footnote (1) in Table 69: ADC characteristics.
Updated footnote (2) in Table 70: ADC accuracy at fADC = 30 MHz.
Updated footnote (1) in Table 76: DAC characteristics.
Updated Figure 9: Regulator OFF.
Updated Figure 7: Power supply supervisor interconnection with
internal reset OFF.
Added Section 3.0.17: Regulator ON/OFF and internal reset ON/OFF
availability.
Updated footnote (2) of Figure 21: Power supply scheme.
Replaced respectively “I2S3S_WS" by "I2S3_WS”, “I2S3S_CK” by
“I2S3_CK” and “FSMC_BLN1” by “FSMC_NBL1” in Table 10: Alternate
function mapping.
Added “EVENTOUT” as alternate function “AF15” for pin PC13, PC14,
PC15, PH0, PH1, PI8 in Table 10: Alternate function mapping
Replaced “DCMI_12” by “DCMI_D12” in Table 8: STM32F40xxx pin
and ball definitions.


Removed the following sentence from Section : I2C interface
characteristics: ”Unless otherwise specified, the parameters
given in Table 56 are derived from tests performed under the
ambient temperature, fPCLK1 frequency and VDD supply
voltage conditions summarized in Table 16.”.
In _Table 8: STM32F40xxx pin and ball definitions on page 53_ :

- For pin PC13, replaced “RTC_AF1” by “RTC_OUT, RTC_TAMP1,
RTC_TS”

- for pin PI8, replaced “RTC_AF2” by “RTC_TAMP1, RTC_TAMP2,
RTC_TS”.

- for pin PB15, added RTC_REFIN in Alternate functions column.


In _Table 10: Alternate function mapping on page 70_, for port
PB15, replaced “RTC_50Hz” by “RTC_REFIN”.


DS8626 Rev 12 199/206



**Revision history** **STM32F405xx, STM32F407xx**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


4
04-Jun-2013
(continued)


Updated Figure 6: Multi-AHB matrix.
Updated Figure 7: Power supply supervisor interconnection with
internal reset OFF
Changed 1.2 V to V12 in Section : Regulator OFF
Updated LQFP176 pin 48.
Updated Section 1: Introduction.
Updated Section 2: Description.
Updated operating voltage in Table 3: STM32F405xx and
STM32F407xx: features and peripheral counts.
Updated Note 1.
Updated Section 3.0.15: Power supply supervisor.
Updated Section 3.0.16: Voltage regulator.
Updated Figure 9: Regulator OFF.
Updated Table 4: Regulator ON/OFF and internal reset ON/OFF
availability.
Updated Section 3.0.19: Low-power modes.
Updated Section 3.0.20: VBAT operation.
Updated Section 3.0.22: Inter-integrated circuit interface (I²C) .
Updated pin 48 in Figure 15: STM32F40xxx LQFP176 pinout.
Updated Table 7: Legend/abbreviations used in the pinout table.
Updated Table 8: STM32F40xxx pin and ball definitions.
Updated Table 16: General operating conditions.
Updated Table 17: Limitations depending on the operating power
supply range.
Updated Section 6.3.7: Wakeup time from low-power mode.
Updated Table 36: HSI oscillator characteristics.
Updated Section 6.3.15: I/O current injection characteristics.
Updated Table 50: I/O static characteristics.
Updated Table 53: NRST pin characteristics.
Updated Table 56: I2C characteristics.
Updated Figure 39: I2C bus AC waveforms and measurement circuit.
Updated Section 6.3.19: Communications interfaces.
Updated Table 69: ADC characteristics.
Added Table 72: Temperature sensor calibration values.
Added Table 75: Internal reference voltage calibration values.
Updated Section 6.3.26: FSMC characteristics.
Updated Section 6.3.28: SD/SDIO MMC card host interface (SDIO)
characteristics.
Updated Table 25: Typical and maximum current consumptions in Stop
mode.
Updated Section : SPI interface characteristics included Table 57.
Updated Section : I2S interface characteristics included Table 58.
Updated Table 66: Dynamic characteristics: Ethernet MAC signals for
SMI.
Updated Table 68: Dynamic characteristics: Ethernet MAC signals for
MII.


200/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Revision history**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


4
04-Jun-2013
(continued)


Updated Table 66: Dynamic characteristics: Ethernet MAC signals for
SMI.
Updated Table 68: Dynamic characteristics: Ethernet MAC signals for
MII.
Updated Table 81: Synchronous multiplexed NOR/PSRAM read
timings.
Updated Table 82: Synchronous multiplexed PSRAM write timings.
Updated Table 83: Synchronous non-multiplexed NOR/PSRAM read
timings.
Updated Table 84: Synchronous non-multiplexed PSRAM write
timings.
Updated Section 6.3.27: Camera interface (DCMI) timing specifications
including Table 89: DCMI characteristics and addition of Figure 72:
DCMI timing diagram.
Updated Section 6.3.28: SD/SDIO MMC card host interface (SDIO)
characteristics including Table 90.
Updated Chapter Figure 9.


DS8626 Rev 12 201/206



**Revision history** **STM32F405xx, STM32F407xx**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


06-Mar-2015 5


Replace Cortex-M4F by Cortex-M4 with FPU throughout the
document.
Updated Section : Regulator OFF and Table 4: Regulator ON/OFF and
internal reset ON/OFF availability for LQFP176.
Updated Figure 15: STM32F40xxx LQFP176 pinout and Table 8:
STM32F40xxx pin and ball definitions.
Updated Figure 6: Multi-AHB matrix.
Added note 1 below Figure 12: STM32F40xxx LQFP64 pinout, Figure
13: STM32F40xxx LQFP100 pinout, Figure 14: STM32F40xxx
LQFP144 pinout and Figure 15: STM32F40xxx LQFP176 pinout.
Updated IVDD and IVSS in Table 14: Current characteristics.
Updated PLS[2:0]=101 (falling edge) configuration in Table 21:
Embedded reset and power control block characteristics.
Added Section : Additional current consumption. Updated Section :
On-chip peripheral current consumption.
Updated Table 31: Low-power mode wakeup timings.
Updated Table 34: HSE 4-26 MHz oscillator characteristics and Table
35: LSE oscillator characteristics (fLSE = 32.768 kHz).
Changed condition related to VESD(CDM) in Table 47: ESD absolute
maximum ratings.
Updated Table 49: I/O current injection susceptibility, Table 50: I/O
static characteristics, Table 51: Output voltage characteristics
conditions, Table 52: I/O AC characteristics and Figure 37: I/O AC
characteristics definition.
Updated Section : I2C interface characteristics.
Remove note 3 in Table 71: Temperature sensor characteristics.
Updated Figure 72: DCMI timing diagram.
Modified Figure 75: WLCSP90 - 4.223 x 3.969 mm, 0.400 mm pitch
wafer level chip scale package outline and Table 92: WLCSP90 - 4.223
x 3.969 mm, 0.400 mm pitch wafer level chip scale package
mechanical data. Added Figure 76: WLCSP90 - 4.223 x 3.969 mm,
0.400 mm pitch wafer level chip scale recommended footprint and
Table 93: WLCSP90 recommended PCB design rules. /
Modified Figure 78: LQFP64 – 64-pin, 10 x 10 mm low-profile quad flat
package outline and Table 94: LQFP64 – 64-pin 10 x 10 mm low-profile
quad flat package mechanical data.
Updated Figure 87: UFBGA176+25 ball, 10 x 10 mm, 0.65 mm pitch,
ultra fine pitch ball grid array package outline and Table 97:
UFBGA176+25 ball, 10 × 10 × 0.65 mm pitch, ultra thin fine pitch ball
grid array mechanical data. Added Figure 88: UFBGA176+25 - 201ball, 10 x 10 mm, 0.65 mm pitch, ultra fine pitch ball grid array
recommended footprint and Table 98: UFBGA176+25 recommended
PCB design rules (0.65 mm pitch BGA).
Updated Figure 90: LQFP176 - 176-pin, 24 x 24 mm low profile quad
flat package outline.
Added Section : Device marking for WLCSP90, Section : Device
marking for LQFP64, Section : Device marking for LFP100, Section :
Device marking for LQFP144, Section : Device marking for
UFBGA176+25 and Section : Device marking for LQFP176.


202/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Revision history**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


22-Oct-2015 6


16-Mar-2016 7


09-Sep-2016 8


In the whole document, updated notes related to values specified by
design or by characterization.
Updated Table 36: HSI oscillator characteristics.
Changed fVCO_OUT minimum value and VCO freq to 100 MHz in
Table 38: Main PLL characteristics and Table 39: PLLI2S (audio PLL)
characteristics.
Updated Figure 39: SPI timing diagram - slave mode and CPHA = 0.
Updated Figure 53: 12-bit buffered /non-buffered DAC.
Removed note 1 related to better performance using a restricted VDD
range in Table 70: ADC accuracy at fADC = 30 MHz.
Upated Figure 84: LQFP144 - 144-pin, 20 x 20 mm low-profile quad flat
package outline.
Updated Figure 87: UFBGA176+25 ball, 10 x 10 mm, 0.65 mm pitch,
ultra fine pitch ball grid array package outline and Table 97:
UFBGA176+25 ball, 10 × 10 × 0.65 mm pitch, ultra thin fine pitch ball
grid array mechanical data.


Updated Figure 2: Compatible board design
STM32F10xx/STM32F2/STM32F40xxx for LQFP100 package.
Updated |VSSX- VSS| in Table 13: Voltage characteristics to add
VREF-.
Added VREF- in Table 69: ADC characteristics.
Updated Table 92: WLCSP90 - 4.223 x 3.969 mm, 0.400 mm pitch
wafer level chip scale package mechanical data.


Removed note 1 below Figure 5: STM32F40xxx block diagram.
Updated definition of stresses above maximum ratings in Section 6.2:
Absolute maximum ratings.
Updated th(NSS) in Figure 39: SPI timing diagram - slave mode and
CPHA = 0 and Figure 40: SPI timing diagram - slave mode and CPHA
= 1.
Added note related to optional marking and inset/upset marks in all
package marking sections.
Updated Figure 87: UFBGA176+25 ball, 10 x 10 mm, 0.65 mm pitch,
ultra fine pitch ball grid array package outline and Table 97:
UFBGA176+25 ball, 10 × 10 × 0.65 mm pitch, ultra thin fine pitch ball
grid array mechanical data.


DS8626 Rev 12 203/206



**Revision history** **STM32F405xx, STM32F407xx**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


14-Aug-2020 9


Renamed Section 3 and Section 8 into Functional overview and
Ordering information, respectively.
Added Arm logo and legal notice in Section 1: Introduction and
updated Arm wordmark in the whole document. Removed USB
certified logos.
Updated camera interfaces for STM32F405OE in Table 3:
STM32F405xx and STM32F407xx: features and peripheral counts.
Added OTP memory in Features and Section 3.0.4: Embedded flash
memory.
Changed random number generator to true random number generator
in the whole document and updated Section 3.0.34: True random
number generator (RNG).
Added Note 1 related to UFBGA176 in Table 8: STM32F40xxx pin and
ball definitions.
Updated Section 6.2: Absolute maximum ratings introduction.
Updated VPVD minimum value for PLS[2:0]=101 (falling edge) in Table
21: Embedded reset and power control block characteristics.
Updated Note 1 in Table 36: HSI oscillator characteristics.
Added reference to application note AN4899 in Section 6.3.16: I/O port
characteristics.
Replaced DCMI_PIXCK by DCMI_PIXCLK in Table 10: Alternate
function mapping.
Renamed Section 8 into Ordering information.
Updated D1 in Figure 87: UFBGA176+25 ball, 10 x 10 mm, 0.65 mm
pitch, ultra fine pitch ball grid array package outline.


204/206 DS8626 Rev 12


**STM32F405xx, STM32F407xx** **Revision history**


**Table 99. Document revision history (continued)**


**Date** **Revision** **Changes**


08-Nov-2024 10


04-Feb-2026 11


Updated:

- Cover page

- _Section 1: Introduction_

- _Figure 5: STM32F40xxx block diagram_

- _Section 3.18: Real-time clock (RTC), backup SRAM and backup_
_registers_

- _Table 7: STM32F40xxx pin and ball definitions_

- _Table 9: Alternate function mapping_

- _I/O system current consumption_

- _Note 1_ in _Table 34: HSI oscillator characteristics_ .

- _Table 33: LSE oscillator characteristics (fLSE = 32.768 kHz)_

- _Figure 37: I/O AC characteristics definition_

- _Figure 39: SPI timing diagram - slave mode and CPHA = 0_,

_Figure 40: SPI timing diagram - slave mode and CPHA = 1_, and
_Figure 41: SPI timing diagram - master mode_

- _Table 44: EMI characteristics for fHSE = 25 MH and fCPU =_
_168 MHz_

- _Figure 49: ADC accuracy characteristics_ and _Figure 50: Typical_
_connection diagram when using the ADC with FT/TT pins featuring_
_analog switch function_

- _Figure 68: NAND controller waveforms for read access_ and

_Figure 69: NAND controller waveforms for write access_

- _Table 96: UFBGA(176+25) - Example of PCB design rules (0.65 mm_
_pitch BGA)_ title

- _Section 7: Package information_
Added _Section 9: Important security notice_


Updated _Figure 7: Power supply supervisor interconnection with_
_internal reset OFF_ .
Updated _Figure 8: PDR_ON and NRST control with internal reset OFF_ .
Updated _Figure 9: Regulator OFF_ .
Updated _Figure 18: STM32F40xxx memory map_ .
Updated _Figure 20: Pin input voltage_ .
Updated _Table 45: ESD absolute maximum ratings_ .
Updated _Section 7.3: LQFP64 package information (5W)_ .


18-Mar-2026 12 Re-numbering of _Section 3: Functional overview_ sub-sections.


DS8626 Rev 12 205/206



**STM32F405xx, STM32F407xx**


**IMPORTANT NOTICE – READ CAREFULLY**


STMicroelectronics NV and its subsidiaries (“ST”) reserve the right to make changes, corrections, enhancements, modifications, and
improvements to ST products and/or to this document at any time without notice.


In the event of any conflict between the provisions of this document and the provisions of any contractual arrangement in force between the
purchasers and ST, the provisions of such contractual arrangement shall prevail.


The purchasers should obtain the latest relevant information on ST products before placing orders. ST products are sold pursuant to ST’s
terms and conditions of sale in place at the time of order acknowledgment.


The purchasers are solely responsible for the choice, selection, and use of ST products and ST assumes no liability for application
assistance or the design of the purchasers’ products.


No license, express or implied, to any intellectual property right is granted by ST herein.


Resale of ST products with provisions different from the information set forth herein shall void any warranty granted by ST for such product.


If the purchasers identify an ST product that meets their functional and performance requirements but that is not designated for the
purchasers' market segment, the purchasers shall contact ST for more information.


ST and the ST logo are trademarks of ST. For additional information about ST trademarks, refer to www.st.com/trademarks. All other product
or service names are the property of their respective owners.


Information in this document supersedes and replaces information previously supplied in any prior versions of this document.


© 2026 STMicroelectronics – All rights reserved


206/206 DS8626 Rev 12

