Source: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf
Retrieved: 2026-11-09

[PDF: 78 pages.]

# ESP32 Series
## Datasheet Version 5.3

2.4 GHz Wi-Fi + Bluetooth [®] + Bluetooth LE SoC

###### Including:


ESP32-D0WD-V3


ESP32-U4WDH


[ESP32-S0WD – Not Recommended for New Designs (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd)


[ESP32-D0WD – Not Recommended for New Designs (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd)


[ESP32-D0WDQ6 – Not Recommended for New Designs (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd)


[ESP32-D0WDQ6-V3 – Not Recommended for New Designs (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd)


[ESP32-D0WDR2-V3 – End of Life (EOL), upgraded to ESP32-D0WDRH2-V3](https://www.espressif.com/en/products/socs)


www.espressif.com


##### Product Overview

ESP32 is a single 2.4 GHz Wi-Fi-and-Bluetooth combo chip designed with the TSMC low-power 40 nm


technology. It is designed to achieve the best power and RF performance, showing robustness, versatility and


reliability in a wide variety of applications and power scenarios.


For details on part numbers and ordering information, please refer to Section 1 ESP32 Series Comparison. For


details on chip revisions, please refer to _[ESP32 Chip Revision v3.0 User Guide](https://www.espressif.com/sites/default/files/documentation/ESP32_ECO_V3_User_Guide__EN.pdf)_ and


_[ESP32 Series SoC Errata](https://www.espressif.com/sites/default/files/documentation/eco_and_workarounds_for_bugs_in_esp32_en.pdf)_ .


The functional block diagram of the SoC is shown below.


In-Package
Flash or PSRAM


SPI


I2C


I2S


SDIO


UART

TWAI®


ETH


RMT


PWM


Touch sensor


DAC


ADC


Timers


Bluetooth

link
controller


Bluetooth
baseband


RF
receive


Clock
generator


RF
transmit


Cryptographic hardware

acceleration


SHA RSA


Wi-Fi
Wi-Fi MAC
baseband


Core and memory


2 (or 1) x Xtensa® 32-bit

LX6 Microprocessors


ROM


SRAM AES RNG


RTC


ULP
coprocessor


Recovery


PMU

coprocessor memory


ESP32 Functional Block Diagram


Espressif Systems 2
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


###### Features

Wi-Fi


_•_ 802.11b/g/n


_•_ 802.11n (2.4 GHz), up to 150 Mbps


_•_ WMM


_•_ TX/RX A-MPDU, RX A-MSDU


_•_ Immediate Block ACK


_•_ Defragmentation


_•_ Automatic Beacon monitoring (hardware TSF)


_•_ Four virtual Wi-Fi interfaces


_•_ Simultaneous support for Infrastructure Station, SoftAP, and Promiscuous modes


Note that when ESP32 is in Station mode, performing a scan, the SoftAP channel will be changed.


_•_ Antenna diversity


Bluetooth [®]


_•_ Compliant with Bluetooth v4.2 BR/EDR and Bluetooth LE specifications


_•_ Class-1, class-2 and class-3 transmitter without external power amplifier


_•_ Enhanced Power Control


_•_ +9 dBm transmitting power


_•_ NZIF receiver with –94 dBm Bluetooth LE sensitivity


_•_ Adaptive Frequency Hopping (AFH)


_•_ Standard HCI based on SDIO/SPI/UART


_•_ High-speed UART HCI, up to 4 Mbps


_•_ Bluetooth 4.2 BR/EDR and Bluetooth LE dual mode controller


_•_ Synchronous Connection-Oriented/Extended (SCO/eSCO)


_•_ CVSD and SBC for audio codec


_•_ Bluetooth Piconet and Scatternet


_•_ Multi-connections in Classic Bluetooth and Bluetooth LE


_•_ Simultaneous advertising and scanning


CPU and Memory


_•_ Xtensa [®] single-/dual-core 32-bit LX6 microprocessor(s)


_•_ CoreMark [®] score:


- 1 core at 240 MHz: 539.98 CoreMark; 2.25 CoreMark/MHz


Espressif Systems 3
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


- 2 cores at 240 MHz: 1079.96 CoreMark; 4.50 CoreMark/MHz


_•_ 448 KB ROM


_•_ 520 KB SRAM


_•_ 16 KB SRAM in RTC


_•_ QSPI supports multiple flash/SRAM chips


Clocks and Timers


_•_ Internal 8 MHz oscillator with calibration


_•_ Internal RC oscillator with calibration


_•_ External 2 MHz ~ 60 MHz crystal oscillator (40 MHz only for Wi-Fi/Bluetooth functionality)


_•_ External 32 kHz crystal oscillator for RTC with calibration


_•_ Two timer groups, including 2 × 64-bit timers and 1 × main watchdog in each group


_•_ One RTC timer


_•_ RTC watchdog


Advanced Peripheral Interfaces


_•_ 34 programmable GPIOs


- Five strapping GPIOs


- Six input-only GPIOs


- Six GPIOs needed for in-package flash (ESP32-U4WDH) and in-package PSRAM


(ESP32-D0WDRH2-V3)


_•_ 12-bit SAR ADC up to 18 channels


_•_ Two 8-bit DAC


_•_ 10 touch sensors


_•_ Four SPI interfaces


_•_ Two I2S interfaces


_•_ Two I2C interfaces


_•_ Three UART interfaces


_•_ One host (SD/eMMC/SDIO)


_•_ One slave (SDIO/SPI)


_•_ Pulse count controller


_•_ Ethernet MAC interface with dedicated DMA and IEEE 1588 support


_•_ TWAI [®], compatible with ISO 11898-1 (CAN Specification 2.0)


_•_ RMT (TX/RX)


Espressif Systems 4
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


_•_ Motor PWM


_•_ LED PWM up to 16 channels


Power Management


_•_ Fine-resolution power control through a selection of clock frequency, duty cycle, Wi-Fi operating modes,


and individual power control of internal components


_•_ Five power modes designed for typical scenarios: Active, Modem-sleep, Light-sleep, Deep-sleep,


Hibernation


_•_ Power consumption in Deep-sleep mode is 10 _µ_ A


_•_ Ultra-Low-Power (ULP) coprocessors


_•_ RTC memory remains powered on in Deep-sleep mode


Security


_•_ Secure boot


_•_ Flash encryption


_•_ 1024-bit OTP, up to 768-bit for customers


_•_ Cryptographic hardware acceleration:


- AES


- Hash (SHA-2)


- RSA


- Random Number Generator (RNG)

###### Applications


With low power consumption, ESP32 is an ideal choice for IoT devices in the following areas:


_•_ Smart Home


_•_ Industrial Automation


_•_ Health Care


_•_ Consumer Electronics


_•_ Smart Agriculture


_•_ POS Machines


_•_ Service Robot


_•_ Audio Devices


_•_ Generic Low-power IoT Sensor Hubs


_•_ Generic Low-power IoT Data Loggers


_•_ Cameras for Video Streaming


_•_ Speech Recognition


_•_ Image Recognition


_•_ SDIO Wi-Fi + Bluetooth Networking Card


Espressif Systems 5
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Contents


Note:


Check the link or the QR code to make sure that you use the latest version of this document:


[https://www.espressif.com/documentation/esp32_datasheet_en.pdf](https://www.espressif.com/documentation/esp32_datasheet_en.pdf)

##### Contents Product Overview 2

Features 3


Applications 5

##### 1 ESP32 Series Comparison 11

1.1 Nomenclature 11


1.2 Comparison 11

##### 2 Pins 12

2.1 Pin Layout 12


2.2 Pin Overview 14


2.3 IO Pins 17


2.3.1 Restrictions for GPIOs and RTC_GPIOs 17


2.4 Analog Pins 17


2.5 Power Supply 17


2.5.1 Power Pins 17


2.5.2 Power Scheme 18


2.5.3 Chip Power-up and Reset 19


2.6 Pin Mapping Between Chip and Flash/PSRAM 20

##### 3 Boot Configurations 22

3.1 Chip Boot Mode Control 23


3.2 Internal LDO (VDD_SDIO) Voltage Control 24


3.3 U0TXD Printing Control 25


3.4 Timing Control of SDIO Slave 25


3.5 JTAG Signal Source Control 25

##### 4 Functional Description 26

4.1 CPU and Memory 26


4.1.1 CPU 26


4.1.2 Internal Memory 26


4.1.3 External Flash and RAM 27


4.1.4 Address Mapping Structure 27


4.1.5 Cache 29


4.2 System Clocks 29


4.2.1 CPU Clock 29


Espressif Systems 6
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Contents


4.2.2 RTC Clock 29


4.2.3 Audio PLL Clock 30


4.3 RTC and Low-power Management 30


4.3.1 Power Management Unit (PMU) 30


4.3.2 Ultra-Low-Power Coprocessor 31


4.4 Timers and Watchdogs 31


4.4.1 General Purpose Timers 31


4.4.2 Watchdog Timers 31


4.5 Cryptographic Hardware Accelerators 32


4.6 Radio and Wi-Fi 32


4.6.1 2.4 GHz Receiver 32


4.6.2 2.4 GHz Transmitter 33


4.6.3 Clock Generator 33


4.6.4 Wi-Fi Radio and Baseband 33


4.6.5 Wi-Fi MAC 34


4.7 Bluetooth 34


4.7.1 Bluetooth Radio and Baseband 34


4.7.2 Bluetooth Interface 34


4.7.3 Bluetooth Stack 35


4.7.4 Bluetooth Link Controller 35


4.8 Digital Peripherals 36


4.8.1 General Purpose Input / Output Interface (GPIO) 36


4.8.2 Serial Peripheral Interface (SPI) 36


4.8.3 Universal Asynchronous Receiver Transmitter (UART) 36


4.8.4 I2C Interface 37


4.8.5 I2S Interface 38


4.8.6 Remote Control Peripheral 38


4.8.7 Pulse Counter Controller (PCNT) 38


4.8.8 LED PWM Controller 39


4.8.9 Motor Control PWM 39


4.8.10 SD/SDIO/MMC Host Controller 40


4.8.11 SDIO/SPI Slave Controller 41

4.8.12 TWAI [®] Controller 42


4.8.13 Ethernet MAC Interface 42


4.9 Analog Peripherals 43


4.9.1 Analog-to-Digital Converter (ADC) 43


4.9.2 Digital-to-Analog Converter (DAC) 44


4.9.3 Touch Sensor 44


4.10 Peripheral Pin Configurations 46

##### 5 Electrical Characteristics 51

5.1 Absolute Maximum Ratings 51


5.2 Recommended Power Supply Characteristics 51


5.3 DC Characteristics (3.3 V, 25 °C) 52


5.4 RF Current Consumption in Active Mode 52


5.5 Reliability 53


Espressif Systems 7
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Contents


5.6 Wi-Fi Radio 53


5.7 Bluetooth Radio 54

5.7.1 Receiver –Basic Data Rate 54

5.7.2 Transmitter –Basic Data Rate 54

5.7.3 Receiver –Enhanced Data Rate 55

5.7.4 Transmitter –Enhanced Data Rate 55


5.8 Bluetooth LE Radio 56


5.8.1 Receiver 56


5.8.2 Transmitter 58

##### 6 Packaging 59 Related Documentation and Resources 60 Appendix A – ESP32 Pin Lists 61

A.1. Notes on ESP32 Pin Lists 61


A.2. GPIO_Matrix 63


A.3. Ethernet_MAC 68


A.4. IO_MUX 68

##### Revision History 70


Espressif Systems 8
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


List of Tables

##### List of Tables


1-1 ESP32 Series Comparison 11


2-1 Pin Overview 14


2-2 Analog Pins 17


2-3 Power Pins 18


2-4 Description of Timing Parameters for Power-up and Reset 19


2-5 Pin-to-Pin Mapping Between Chip and In-Package Flash/PSRAM 20


2-6 Pin-to-Pin Mapping Between Chip and Off-Package Flash/PSRAM 20


3-1 Default Configuration of Strapping Pins 22


3-2 Description of Timing Parameters for the Strapping Pins 23


3-3 Chip Boot Mode Control 23


3-4 U0TXD Printing Control 25


3-5 Timing Control of SDIO Slave 25


4-1 Memory and Peripheral Mapping 28


4-2 Power Consumption by Power Modes 30


4-3 ADC Characteristics 43


4-4 ADC Calibration Results 44


4-5 Capacitive-Sensing GPIOs Available on ESP32 45


4-6 Peripheral Pin Configurations 46


5-1 Absolute Maximum Ratings 51


5-2 Recommended Power Supply Characteristics 51


5-3 DC Characteristics (3.3 V, 25 °C) 52


5-4 Current Consumption Depending on RF Modes 52


5-5 Reliability Qualifications 53


5-6 Wi-Fi Radio Characteristics 53

5-7 Receiver Characteristics –Basic Data Rate 54

5-8 Transmitter Characteristics –Basic Data Rate 54

5-9 Receiver Characteristics –Enhanced Data Rate 55

5-10 Transmitter Characteristics –Enhanced Data Rate 56

5-11 Receiver Characteristics –Bluetooth LE 56

5-12 Transmitter Characteristics –Bluetooth LE 58


6-1 Notes on ESP32 Pin Lists 61


6-2 GPIO_Matrix 63


6-3 Ethernet_MAC 68


Espressif Systems 9
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


List of Figures

##### List of Figures


1-1 ESP32 Series Nomenclature 11


2-1 ESP32 Pin Layout (QFN 6*6, Top View) 12


2-2 ESP32 Pin Layout (QFN 5*5, Top View) 13


2-3 ESP32 Power Scheme 18


2-4 Visualization of Timing Parameters for Power-up and Reset 19


3-1 Visualization of Timing Parameters for the Strapping Pins 23


3-2 Chip Boot Flow 24


4-1 Address Mapping Structure 27


6-1 QFN48 (6×6 mm) Package 59


6-2 QFN48 (5×5 mm) Package 59


Espressif Systems 10
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


1 ESP32 Series Comparison

##### 1 ESP32 Series Comparison

###### 1.1 Nomenclature


ESP32 D 0 WD


R2 H


Q6


V3


**Chip revision v3.0 or newer**

**Package**
Q6: QFN 6*6
N/A: QFN 5*5

**High temperature**


**In-package PSRAM**
R2: 2 MB PSRAM

**Connection**
WD: Wi-Fi b/g/n + Bluetooth/Bluetooth LE dual mode

**In-package flash**
0: No in-package flash
2: 2 MB flash
4: 4 MB flash

**Core**
D/U: Dual core
S: Single core


**Chip Series**


###### 1.2 Comparison


Figure 1-1. ESP32 Series Nomenclature


Table 1-1. ESP32 Series Comparison


In-Package


Part Number [1] Core Chip Revision [2]


Flash/PSRAM Package


VDD_SDIO


Voltage


ESP32-D0WD-V3 Dual core v3.0/v3.1 [4] - QFN 5*5 1.8 V/3.3 V


ESP32-D0WDR2-V3 (EOL)

Dual core v3.0/v3.1 [4] 2 MB PSRAM QFN 5*5 3.3 V
Upgraded to ESP32-D0WDRH2-V3 [7]

ESP32-U4WDH Dual core [3] v3.0/v3.1 [4] 4 MB fash [6] QFN 5*5 3.3 V

[ESP32-D0WDQ6-V3 (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd) Dual core v3.0/v3.1 [4] - QFN 6*6 1.8 V/3.3 V

[ESP32-D0WD (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd) Dual core v1.0/v1.1 [5] - QFN 5*5 1.8 V/3.3 V

[ESP32-D0WDQ6 (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd) Dual core v1.0/v1.1 [5] - QFN 6*6 1.8 V/3.3 V

[ESP32-S0WD (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd) Single core v1.0/v1.1 [5] - QFN 5*5 1.8 V/3.3 V


1 All above chips support Wi-Fi b/g/n + Bluetooth/Bluetooth LE Dual Mode connection. For details on chip marking and


packing, see Section 6 Packaging.
2 Differences between ESP32 chip revisions and how to distinguish them are described in _[ESP32 Series SoC Errata](https://www.espressif.com/sites/default/files/documentation/eco_and_workarounds_for_bugs_in_esp32_en.pdf)_ .
3 ESP32-U4WDH will be produced as dual-core instead of single core. [See PCN-2021-021](https://www.espressif.com/sites/default/files/pcn_downloads/PCN-2021-021%20ESP32-U4WDH%20%E5%8D%87%E7%BA%A7%E4%B8%BA%E5%8F%8C%E6%A0%B8%E5%A4%84%E7%90%86%E5%99%A8%E4%BA%A7%E5%93%81.pdf) for details.
4 The chips will be produced with chip revision v3.1 inside. [See PCN20220901](https://www.espressif.com/sites/default/files/pcn_downloads/PCN20220901%20Upgrade%20Chip%20Revision%20of%20ESP32%20Series%20Products.pdf) for details.
5 The chips will be produced with chip revision v1.1 inside. [See PCN20220901](https://www.espressif.com/sites/default/files/pcn_downloads/PCN20220901%20Upgrade%20Chip%20Revision%20of%20ESP32%20Series%20Products.pdf) for details.
6 The in-package flash supports:


 - More than 100,000 program/erase cycles


 - More than 20 years data retention time
7 ESP32-D0WDR2-V3 is end of life and upgraded to ESP32-D0WDRH2-V3. [See PCN20251001](https://documentation.espressif.com/en/PCN20251001_ESP32-S3R2_ESP32-D0WDR2-V3_%E5%8D%87%E7%BA%A7.html) for details.


Espressif Systems 11
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


2 Pins

##### 2 Pins

###### 2.1 Pin Layout


VDDA


LNA_IN


VDD3P3


VDD3P3


SENSOR_VP


SENSOR_CAPP


SENSOR_CAPN


SENSOR_VN


CHIP_PU


VDET_1












GPIO23


GPIO18


GPIO5


SD_DATA_1


SD_DATA_0


SD_CLK


SD_CMD


SD_DATA_3


SD_DATA_2


GPIO17


VDD_SDIO


GPIO16


ESP32
49 GND


VDET_2 11


32K_XP 12


Figure 2-1. ESP32 Pin Layout (QFN 6*6, Top View)


Espressif Systems 12
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)














ESP32 Series Datasheet v5.3


2 Pins


VDDA


LNA_IN


VDD3P3


VDD3P3


SENSOR_VP


SENSOR_CAPP


SENSOR_CAPN


SENSOR_VN


CHIP_PU


VDET_1


VDET_2


GPIO19


VDD3P3_CPU


GPIO23


GPIO18


GPIO5


SD_DATA_1


SD_DATA_0


SD_CLK


SD_CMD


SD_DATA_3


SD_DATA_2


VDD_SDIO


GPIO16


ESP32
49 GND
















32K_XP 12 27 GPIO17


32K_XN


GPIO25
















Figure 2-2. ESP32 Pin Layout (QFN 5*5, Top View)


Espressif Systems 13
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


###### 2.2 Pin Overview

Name No. Type Function


Table 2-1. Pin Overview


Analog


VDDA 1 P Analog power supply (2.3 V _∼_ 3.6 V)


LNA_IN 2 I/O RF input and output


VDD3P3 3 P Analog power supply (2.3 V _∼_ 3.6 V)


VDD3P3 4 P Analog power supply (2.3 V _∼_ 3.6 V)


VDD3P3_RTC


SENSOR_VP 5 I GPIO36, ADC1_CH0, RTC_GPIO0


SENSOR_CAPP 6 I GPIO37, ADC1_CH1, RTC_GPIO1


SENSOR_CAPN 7 I GPIO38, ADC1_CH2, RTC_GPIO2


SENSOR_VN 8 I GPIO39, ADC1_CH3, RTC_GPIO3


High: On; enables the chip


CHIP_PU 9 I


Low: Off; the chip shuts down


Note: Do not leave the CHIP_PU pin foating.


VDET_1 10 I GPIO34, ADC1_CH6, RTC_GPIO4


VDET_2 11 I GPIO35, ADC1_CH7, RTC_GPIO5


32K_XP 12 I/O GPIO32, ADC1_CH4, RTC_GPIO9, TOUCH9, 32K_XP (32.768 kHz crystal oscillator input)


32K_XN 13 I/O GPIO33, ADC1_CH5, RTC_GPIO8, TOUCH8, 32K_XN (32.768 kHz crystal oscillator output)


GPIO25 14 I/O GPIO25, ADC2_CH8, RTC_GPIO6, DAC_1, EMAC_RXD0


GPIO26 15 I/O GPIO26, ADC2_CH9, RTC_GPIO7, DAC_2, EMAC_RXD1


GPIO27 16 I/O GPIO27, ADC2_CH7, RTC_GPIO17, TOUCH7, EMAC_RX_DV


MTMS 17 I/O GPIO14, ADC2_CH6, RTC_GPIO16, TOUCH6, EMAC_TXD2, HSPICLK, HS2_CLK, SD_CLK, MTMS


MTDI 18 I/O GPIO12, ADC2_CH5, RTC_GPIO15, TOUCH5, EMAC_TXD3, HSPIQ, HS2_DATA2, SD_DATA2, MTDI


VDD3P3_RTC 19 P Input power supply for RTC IO (2.3 V _∼_ 3.6 V)


MTCK 20 I/O GPIO13, ADC2_CH4, RTC_GPIO14, TOUCH4, EMAC_RX_ER, HSPID, HS2_DATA3, SD_DATA3, MTCK


MTDO 21 I/O GPIO15, ADC2_CH3, RTC_GPIO13, TOUCH3, EMAC_RXD3, HSPICS0, HS2_CMD, SD_CMD, MTDO


Name No. Type Function


GPIO2 22 I/O GPIO2, ADC2_CH2, RTC_GPIO12, TOUCH2, HSPIWP, HS2_DATA0, SD_DATA0


GPIO0 23 I/O GPIO0, ADC2_CH1, RTC_GPIO11, TOUCH1, EMAC_TX_CLK, CLK_OUT1,


GPIO4 24 I/O GPIO4, ADC2_CH0, RTC_GPIO10, TOUCH0, EMAC_TX_ER, HSPIHD, HS2_DATA1, SD_DATA1


VDD_SDIO


GPIO16 25 I/O GPIO16, HS1_DATA4, U2RXD, EMAC_CLK_OUT


VDD_SDIO 26 P Output power supply: 1.8 V or the same voltage as VDD3P3_RTC


GPIO17 27 I/O GPIO17, HS1_DATA5, U2TXD, EMAC_CLK_OUT_180


SD_DATA_2 28 I/O GPIO9, HS1_DATA2, U1RXD, SD_DATA2, SPIHD


SD_DATA_3 29 I/O GPIO10, HS1_DATA3, U1TXD, SD_DATA3, SPIWP


SD_CMD 30 I/O GPIO11, HS1_CMD, U1RTS, SD_CMD, SPICS0


SD_CLK 31 I/O GPIO6, HS1_CLK, U1CTS, SD_CLK, SPICLK


SD_DATA_0 32 I/O GPIO7, HS1_DATA0, U2RTS, SD_DATA0, SPIQ


SD_DATA_1 33 I/O GPIO8, HS1_DATA1, U2CTS, SD_DATA1, SPID


VDD3P3_CPU


GPIO5 34 I/O GPIO5, HS1_DATA6, VSPICS0, EMAC_RX_CLK


GPIO18 35 I/O GPIO18, HS1_DATA7, VSPICLK


GPIO23 36 I/O GPIO23, HS1_STROBE, VSPID


VDD3P3_CPU 37 P Input power supply for CPU IO (1.8 V _∼_ 3.6 V)


GPIO19 38 I/O GPIO19, U0CTS, VSPIQ, EMAC_TXD0


GPIO22 39 I/O GPIO22, U0RTS, VSPIWP, EMAC_TXD1


U0RXD 40 I/O GPIO3, U0RXD, CLK_OUT2


U0TXD 41 I/O GPIO1, U0TXD, CLK_OUT3, EMAC_RXD2


GPIO21 42 I/O GPIO21, VSPIHD, EMAC_TX_EN


Analog


VDDA 43 P Analog power supply (2.3 V _∼_ 3.6 V)


XTAL_N 44 O External crystal output


XTAL_P 45 I External crystal input


VDDA 46 P Analog power supply (2.3 V _∼_ 3.6 V)


CAP2 47 I Connects to a 3.3 nF (10%) capacitor and 20 kΩ resistor in parallel to CAP1


Name No. Type Function


CAP1 48 I Connects to a 10 nF series capacitor to ground


GND 49 P Ground


Notes for Table 2-1 Pin Overview:


1. Function names:


CLK_OUT… clock output


SPICLK


HSPICLK


VSPICLK






SPI clock signal



HS…_CLK SDIO Master clock signal


SD_CLK SDIO Slave clock signal

}


EMAC_TX_CLK


EMAC_RX_CLK


U…_RTS


U…_CTS


U…_RXD


U…_TXD


MTMS


MTDI


MTCK


MTDO


}


}








EMAC clock signal


UART0/1/2 hardware flow control signals


UART0/1/2 receive/transmit signals


JTAG interface signals


GPIO… General-purpose input/output with signals routed via the GPIO matrix. For


more details on the GPIO matrix, see _ESP32 Technical Reference Manual_                
Chapter _IO MUX and GPIO Matrix_ 。


2. Regarding highlighted cells, see Section 2.3.1 Restrictions for GPIOs and RTC_GPIOs.


3. For a quick reference guide to using the IO_MUX, Ethernet MAC, and GPIO Matrix pins of ESP32, please refer to Appendix ESP32 Pin Lists.


2 Pins

###### 2.3 IO Pins


2.3.1 Restrictions for GPIOs and RTC_GPIOs


All IO pins of the ESP32 have GPIO and some have RTC_GPIO pin functions. However, these IO pins are


multifunctional and can be configured for different purposes based on the requirements. Some IOs have


restrictions for usage. It is essential to consider their multiplexed nature and the limitations when using these


IO pins.


In Table 2-1 Pin Overview some pin functions are highlighted, specically:


_•_ GPIO  - Input only pins, output is not supported due to lack of pull-up/pull-down resistors.


_•_ GPIO  - allocated for communication with in-package flash/PSRAM and NOT recommended for other


uses. For details, see Section 2.6 Pin Mapping Between Chip and Flash/PSRAM.


_•_ GPIO  - have one of the following important functions:


- Strapping pins – need to be at certain logic levels at startup. See Section 3 _Boot Configurations_ .


- JTAG interface – often used for debugging.


- UART interface – often used for debugging.


See also Appendix A.1 – Notes on ESP32 Pin Lists.

###### 2.4 Analog Pins


Table 2-2. Analog Pins


Pin Pin Pin Pin


No. Name Type Function


2 LNA_IN I/O Low Noise Amplifer (LNA) input signal, Power Amplifer (PA) output signal


9 CHIP_PU I


High: on, enables the chip (Powered up).
Low: off, the chip powers off (powered down).
Note: Do not leave the CHIP_PU pin foating.


44 XTAL_N  - External clock input/output connected to chip’s crystal or oscillator.


45 XTAL_P  - P/N means differential clock positive/negative.

###### 2.5 Power Supply


2.5.1 Power Pins


ESP32’s digital pins are divided into three different power domains:


_•_ VDD3P3_RTC


_•_ VDD3P3_CPU


_•_ VDD_SDIO


Espressif Systems 17
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


2 Pins


Table 2-3. Power Pins


Pin Pin Power Supply


No. Name Direction Power Domain / Other IO Pins


1 VDDA Input Analog power domain


3 VDD3P3 Input Analog power domain


4 VDD3P3 Input Analog power domain

19 VDD3P3_RTC [1] Input RTC and part of Digital power domains RTC IO

26 VDD3P3_SDIO [2] Input/Output Analog power domain

37 VDD3P3_CPU [3] Input Digital power domain Digital IO


43 VDDA Input Analog power domain


46 VDDA Input Analog power domain


49 GND     - External ground connection


1 VDD3P3_RTC is also the input power supply for RTC and CPU.
2 VDD_SDIO connects to the output of an internal LDO whose input is VDD3P3_RTC. When


VDD_SDIO is connected to the same PCB net together with VDD3P3_RTC, the internal


LDO is disabled automatically.
3 VDD3P3_CPU is also the input power supply for CPU.


2.5.2 Power Scheme


The power scheme is shown in Figure 2-3 ESP32 Power Scheme.


VDD3P3_RTC VDD3P3_CPU


R = 6 Ω

1.8 V LDO LDO 1.1 V LDO 1.1 V


VDD_SDIO


3.3 V/1.8 V


SDIO


Domain


RTC


Domain


Figure 2-3. ESP32 Power Scheme


Espressif Systems 18
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


CPU


Domain


ESP32 Series Datasheet v5.3


2 Pins


The internal LDO can be configured as having 1.8 V, or the same voltage as VDD3P3_RTC. It can be powered


off via software to minimize the current of flash/SRAM during the Deep-sleep mode.


2.5.3 Chip Power-up and Reset


Once the power is supplied to the chip, its power rails need a short time to stabilize. After that, CHIP_PU – the


pin used for power-up and reset – is pulled high to activate the chip. For information on CHIP_PU as well as


power-up and reset timing, see Figure 2-4 and Table 2-4.


t _ST BL_ t _RST_


VDD3P3_RTC Min


VDD


V _IL_nRST_

CHIP_PU


Figure 2-4. Visualization of Timing Parameters for Power-up and Reset


Table 2-4. Description of Timing Parameters for Power-up and Reset


Parameter Description Min ( _µ_ s)


t _ST BL_


t _RST_


Time reserved for the 3.3 V rails to stabilize before the CHIP_PU

50
pin is pulled high to activate the chip


Time reserved for CHIP_PU to stay below V _IL_ _ _nRST_ to reset the

50
chip (see Table 5-3)


_•_ In scenarios where ESP32 is powered up and down repeatedly by switching the power rails, while there


is a large capacitor on the VDD33 rail and CHIP_PU and VDD33 are connected, simply switching off the


CHIP_PU power rail and immediately switching it back on may cause an incomplete power discharge


cycle and failure to reset the chip adequately.


An additional discharge circuit may be required to accelerate the discharge of the large capacitor on rail


VDD33, which will ensure proper power-on-reset when the ESP32 is powered up again.


_•_ When a battery is used as the power supply for the ESP32 series of chips and modules, a supply voltage


supervisor is recommended, so that a boot failure due to low voltage is avoided. Users are


recommended to pull CHIP_PU low if the power supply for ESP32 is below 2.3 V.


Notes on power supply:


_•_ The operating voltage of ESP32 ranges from 2.3 V to 3.6 V. When using a single-power supply, the


recommended voltage of the power supply is 3.3 V, and its recommended output current is 500 mA or


more.


_•_ PSRAM and flash both are powered by VDD_SDIO. If the chip has an in-package flash, the voltage of


VDD_SDIO is determined by the operating voltage of the in-package flash. If the chip also connects to


an external PSRAM, the operating voltage of external PSRAM must match that of the in-package flash.


This also applies if the chip has an in-package PSRAM but also connects to an external flash.


Espressif Systems 19
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


2 Pins


_•_ When VDD_SDIO 1.8 V is used as the power supply for external flash/PSRAM, a 2 kΩ grounding resistor


should be added to VDD_SDIO. For the circuit design, please refer to


_[ESP32 Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html?#fig-esp32-1v8-vddsdio)_ .


_•_ When the three digital power supplies are used to drive peripherals, e.g., 3.3 V flash, they should comply


with the peripherals’ specifications.

###### 2.6 Pin Mapping Between Chip and Flash/PSRAM


Table 2-5 lists the pin-to-pin mapping between the chip and the in-package flash/PSRAM. The chip pins listed


here are not recommended for other usage.


For the data port connection between ESP32 and off-package flash/PSRAM please refer to Table 2-6.


Table 2-5. Pin-to-Pin Mapping Between Chip and In-Package Flash/PSRAM


ESP32-U4WDH In-Package Flash (4 MB)


SD_DATA_1 IO0/DI


GPIO17 IO1/DO


SD_DATA_0 IO2/WP#


SD_CMD IO3/HOLD#


SD_CLK CLK


GPIO16 CS#


GND VSS

VDD_SDIO [1] VDD


ESP32-D0WDRH2-V3 In-Package PSRAM (2 MB)


SD_DATA_1 SIO0/SI


SD_DATA_0 SIO1/SO


SD_DATA_3 SIO2


SD_DATA_2 SIO3


SD_CLK SCLK

GPIO16 [2] CE#


GND VSS

VDD_SDIO [1] VDD


Table 2-6. Pin-to-Pin Mapping Between Chip and Off-Package Flash/PSRAM


Chip Pin Off-Package Flash


SD_DATA_1/SPID IO0/DI


SD_DATA_0/SPIQ IO1/DO


SD_DATA_3/SPIWP IO2/WP#


SD_DATA_2/SPIHD IO3/HOLD#


SD_CLK CLK


SD_CMD CS#


GND VSS


VDD_SDIO VDD


Cont’d on next page


Espressif Systems 20
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


2 Pins


Note:


Table 2-6 – cont’d from previous page


Chip Pin Off-Package PSRAM


Chip Pin Off-Package PSRAM


SD_DATA_1 SIO0/SI


SD_DATA_0 SIO1/SO


SD_DATA_3 SIO2


SD_DATA_2 SIO3

SD_CLK/GPIO17 [3] SCLK

GPIO16 [2] CE#


GND VSS


VDD_SDIO VDD


1. As the in-package flash (ESP32-U4WDH) and the in-package PSRAM (ESP32-D0WDRH2-V3) operate at 3.3 V,


VDD_SDIO must be powered by VDD3P3_RTC via a 6 Ω resistor. See Figure 2-3 ESP32 Power Scheme.


2. If GPIO16 is used to connect to PSRAM’s CE# signal, please add a pull-up resistor at the GPIO16 pin. See


_[ESP32-WROVER-E Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf)_  - Figure _Schematics of ESP32-WROVER-E_ .


3. SD_CLK and GPIO17 pins are available to connect to the SCLK signal of external PSRAM.


_•_ If SD_CLK pin is selected, one GPIO (i.e., GPIO17) will be saved. The saved GPIO can be used for other


purposes. This connection has passed internal tests, but relevant certification has not been completed.


_•_ Or GPIO17 pin is used to connect to the SCLK signal. This connection has passed relevant certification,


[see certifcates for ESP32-WROVER-E.](https://www.espressif.com/en/support/documents/certificates?keys=ESP32-WROVER-E)


Please select the proper pin for your specific applications.


Espressif Systems 21
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


3 Boot Confgurations

##### 3 Boot Configurations


The chip allows for configuring the following boot parameters through strapping pins and eFuse bits at


power-up or a hardware reset, without microcontroller interaction.


_•_ Chip boot mode


- Strapping pin: GPIO0 and GPIO2


_•_ Internal LDO (VDD_SDIO) Voltage


- Strapping pin: MTDI


- eFuse bit: EFUSE_SDIO_FORCE and EFUSE_SDIO_TIEH


_•_ U0TXD printing


- Strapping pin: MTDO


_•_ Timing of SDIO Slave


- Strapping pin: MTDO and GPIO5


_•_ JTAG signal source


- eFuse bit: EFUSE_DISABLE_JTAG


The default values of all the above eFuse bits are 0, which means that they are not burnt. Given that eFuse is


one-time programmable, once an eFuse bit is programmed to 1, it can never be reverted to 0. For how to


program eFuse bits, please refer to _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#efuse)_ - Chapter _eFuse Controller_ .


The default values of the strapping pins, namely the logic levels, are determined by pins’internal weak


pull-up/pull-down resistors at reset if the pins are not connected to any circuit, or connected to an external


high-impedance circuit.


Table 3-1. Default Configuration of Strapping Pins


Strapping Pin Default Confguration Bit Value


GPIO0 Pull-up 1


GPIO2 Pull-down 0


MTDI Pull-down 0


MTDO Pull-up 1


GPIO5 Pull-up 1


To change the bit values, the strapping pins should be connected to external pull-down/pull-up resistances. If


the ESP32 is used as a device by a host MCU, the strapping pin voltage levels can also be controlled by the


host MCU.


All strapping pins have latches. At system reset, the latches sample the bit values of their respective strapping


pins and store them until the chip is powered down or shut down. The states of latches cannot be changed in


any other way. It makes the strapping pin values available during the entire chip operation, and the pins are


freed up to be used as regular IO pins after reset.


The timing of signals connected to the strapping pins should adhere to the _setup time_ and _hold time_


specifications in Table 3-2 and Figure 3-1.


Espressif Systems 22
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


3 Boot Confgurations


Table 3-2. Description of Timing Parameters for the Strapping Pins


Parameter Description Min (ms)


t _SU_


t _H_


pin values after CHIP_PU is already high and before these pins


start operating as regular IO pins.


t _SU_ t _H_


V _IH_nRST_


CHIP_PU


V _IH_


Strapping pin


Figure 3-1. Visualization of Timing Parameters for the Strapping Pins


_Setup time_ is the time reserved for the power rails to stabilize be
0
fore the CHIP_PU pin is pulled high to activate the chip.


_Hold_ _time_ is the time reserved for the chip to read the strapping



###### 3.1 Chip Boot Mode Control

GPIO0 and GPIO2 control the boot mode after the reset is released. See Table 3-3 _Chip Boot Mode_


_Control_ .


Table 3-3. Chip Boot Mode Control


Boot Mode GPIO0 GPIO2


SPI Boot Mode 1 Any value

Joint Download Boot Mode [2] 0 0


1 Bold marks the default value and configuration.
2 Joint Download Boot mode supports the following


download methods:

_•_ SDIO Download Boot

_•_ UART Download Boot


In Joint Download Boot mode, the detailed boot flow of the chip is put below 3-2.


Espressif Systems 23
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


3 Boot Confgurations


Figure 3-2. Chip Boot Flow


uart_download_dis controls boot mode behaviors:


It permanently disables Download Boot mode when uart_download_dis is set to 1 (valid only for ESP32 chip


revisions v3.0 and higher).

###### 3.2 Internal LDO (VDD_SDIO) Voltage Control


The required VDD_SPI voltage for the chips of the ESP32 Series can be found in Table 1-1 _Comparison_ .


MTDI is used to select the VDD_SDIO power supply voltage at reset:


_•_ MTDI = 0 (by default), VDD_SDIO pin is powered directly from VDD3P3_RTC. Typically this voltage is 3.3


V. For more information, see Section 2.5.2 _Power Scheme_ .


_•_ MTDI = 1, VDD_SDIO pin is powered from internal 1.8 V LDO.


This functionality can be overridden by setting EFUSE_SDIO_FORCE to 1, in which case the EFUSE_SDIO_TIEH


determines the VDD_SDIO voltage:


_•_ EFUSE_SDIO_TIEH = 0, VDD_SDIO connects to 1.8 V LDO.


_•_ EFUSE_SDIO_TIEH = 1, VDD_SDIO connects to VDD3P3_RTC.


Espressif Systems 24
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


3 Boot Confgurations

###### 3.3 U0TXD Printing Control


During booting, the strapping pin MTDO can be used to control the U0TXD Printing, as Table 3-4 shows.


Table 3-4. U0TXD Printing Control


U0TXD Printing Control MTDO

Enabled [1] 1


Disabled 0


1 Bold marks the default value and


configuration.

###### 3.4 Timing Control of SDIO Slave


The strapping pin MTDO and GPIO5 can be used to control the timing of SDIO slave, see Table 3-5 _Timing_


_Control of SDIO Slave_ .


Table 3-5. Timing Control of SDIO Slave


Edge behavior MTDO GPIO5


Falling edge sampling, falling edge output 0 0


Falling edge sampling, rising edge output 0 1


Rising edge sampling, falling edge output 1 0


Rising edge sampling, rising edge output 1 1


1 Bold marks the default value and configuration.

###### 3.5 JTAG Signal Source Control


If EFUSE_DISABLE_JTAG is set to 1, the source of JTAG signals can be disabled.


Espressif Systems 25
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description

##### 4 Functional Description

###### 4.1 CPU and Memory


4.1.1 CPU


ESP32 contains one or two low-power Xtensa [®] 32-bit LX6 microprocessor(s) with the following


features:


_•_ [7-stage pipeline to support the clock frequency of up to 240 MHz (160 MHz for ESP32-S0WD (NRND))](https://www.espressif.com/en/products/longevity-commitment?id=nrnd)


_•_ 16/24-bit Instruction Set provides high code-density


_•_ Support for Floating Point Unit


_•_ Support for DSP instructions, such as a 32-bit multiplier, a 32-bit divider, and a 40-bit MAC


_•_ Support for 32 interrupt vectors from about 70 interrupt sources


The single-/dual-CPU interfaces include:


_•_ Xtensa RAM/ROM Interface for instructions and data


_•_ Xtensa Local Memory Interface for fast peripheral register access


_•_ External and internal interrupt sources


_•_ JTAG for debugging


For information about the Xtensa [®] Instruction Set Architecture, please refer to

_Xtensa_ [®] _[Instruction Set Architecture (ISA) Summary](https://www.cadence.com/content/dam/cadence-www/global/en_US/documents/tools/silicon-solutions/compute-ip/isa-summary.pdf)_ .


4.1.2 Internal Memory


ESP32’s internal memory includes:


_•_ 448 KB of ROM for booting and core functions


_•_ 520 KB of on-chip SRAM for data and instructions


_•_ 8 KB of SRAM in RTC, which is called RTC FAST Memory and can be used for data storage; it is accessed


by the main CPU during RTC Boot from the Deep-sleep mode.


_•_ 8 KB of SRAM in RTC, which is called RTC SLOW Memory and can be accessed by the ULP coprocessor


during the Deep-sleep mode.


_•_ 1 Kbit of eFuse: 256 bits are used for the system (MAC address and chip configuration) and the


remaining 768 bits are reserved for customer applications, including flash-encryption and chip-ID.


_•_ In-package flash or PSRAM


Note:


Products in the ESP32 series differ from each other, in terms of their support for in-package flash or PSRAM and the


size of them. For details, please refer to Section 1 ESP32 Series Comparison.


Espressif Systems 26
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


4.1.3 External Flash and RAM


ESP32 supports multiple external QSPI flash and external RAM (SRAM) chips. More details can be found in


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#spi)_ - Chapter _SPI Controller_ . ESP32 also supports hardware


encryption/decryption based on AES to protect developers’ programs and data in flash.


ESP32 can access the external QSPI flash and SRAM through high-speed caches.


_•_ Up to 16 MB of external flash can be mapped into CPU instruction memory space and read-only memory


space simultaneously.


- When external flash is mapped into CPU instruction memory space, up to 11 MB + 248 KB can be


mapped at a time. Note that if more than 3 MB + 248 KB are mapped, cache performance will be


reduced due to speculative reads by the CPU.


- When external flash is mapped into read-only data memory space, up to 4 MB can be mapped at a


time. 8-bit, 16-bit and 32-bit reads are supported.


_•_ External RAM can be mapped into CPU data memory space. SRAM up to 8 MB is supported and up to 4


MB can be mapped at a time. 8-bit, 16-bit and 32-bit reads and writes are supported.


Note:


After ESP32 is initialized, firmware can customize the mapping of external RAM or flash into the CPU address space.


4.1.4 Address Mapping Structure


The structure of address mapping is shown in Figure 4-1. The memory and peripheral mapping is shown in


Table 4-1.


Figure 4-1. Address Mapping Structure


Espressif Systems 27
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Table 4-1. Memory and Peripheral Mapping


Category Target Start Address End Address Size


Internal ROM 0 0×4000_0000 0×4005_FFFF 384 KB


Internal ROM 1 0×3FF9_0000 0×3FF9_FFFF 64 KB


Internal SRAM 0 0×4007_0000 0×4009_FFFF 192 KB


Embedded


Memory


External


Memory


Peripheral


0×3FFE_0000 0×3FFF_FFFF
Internal SRAM 1 128 KB
0×400A_0000 0×400B_FFFF


Internal SRAM 2 0×3FFA_E000 0×3FFD_FFFF 200 KB


0×3FF8_0000 0×3FF8_1FFF
RTC FAST Memory 8 KB
0×400C_0000 0×400C_1FFF


RTC SLOW Memory 0×5000_0000 0×5000_1FFF 8 KB


0×3F40_0000 0×3F7F_FFFF 4 MB
External Flash

0×400C_2000 0×40BF_FFFF 11 MB+248 KB


External RAM 0×3F80_0000 0×3FBF_FFFF 4 MB


DPort Register 0×3FF0_0000 0×3FF0_0FFF 4 KB


AES Accelerator 0×3FF0_1000 0×3FF0_1FFF 4 KB


RSA Accelerator 0×3FF0_2000 0×3FF0_2FFF 4 KB


SHA Accelerator 0×3FF0_3000 0×3FF0_3FFF 4 KB


Secure Boot 0×3FF0_4000 0×3FF0_4FFF 4 KB


Cache MMU Table 0×3FF1_0000 0×3FF1_3FFF 16 KB


PID Controller 0×3FF1_F000 0×3FF1_FFFF 4 KB


UART0 0×3FF4_0000 0×3FF4_0FFF 4 KB


SPI1 0×3FF4_2000 0×3FF4_2FFF 4 KB


SPI0 0×3FF4_3000 0×3FF4_3FFF 4 KB


GPIO 0×3FF4_4000 0×3FF4_4FFF 4 KB


RTC 0×3FF4_8000 0×3FF4_8FFF 4 KB


IO MUX 0×3FF4_9000 0×3FF4_9FFF 4 KB


SDIO Slave 0×3FF4_B000 0×3FF4_BFFF 4 KB


UDMA1 0×3FF4_C000 0×3FF4_CFFF 4 KB


I2S0 0×3FF4_F000 0×3FF4_FFFF 4 KB


UART1 0×3FF5_0000 0×3FF5_0FFF 4 KB


I2C0 0×3FF5_3000 0×3FF5_3FFF 4 KB


UDMA0 0×3FF5_4000 0×3FF5_4FFF 4 KB


SDIO Slave 0×3FF5_5000 0×3FF5_5FFF 4 KB


RMT 0×3FF5_6000 0×3FF5_6FFF 4 KB


PCNT 0×3FF5_7000 0×3FF5_7FFF 4 KB


SDIO Slave 0×3FF5_8000 0×3FF5_8FFF 4 KB


LED PWM 0×3FF5_9000 0×3FF5_9FFF 4 KB


eFuse Controller 0×3FF5_A000 0×3FF5_AFFF 4 KB


Flash Encryption 0×3FF5_B000 0×3FF5_BFFF 4 KB


PWM0 0×3FF5_E000 0×3FF5_EFFF 4 KB


TIMG0 0×3FF5_F000 0×3FF5_FFFF 4 KB


TIMG1 0×3FF6_0000 0×3FF6_0FFF 4 KB


SPI2 0×3FF6_4000 0×3FF6_4FFF 4 KB


SPI3 0×3FF6_5000 0×3FF6_5FFF 4 KB


Espressif Systems 28
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Category Target Start Address End Address Size


SYSCON 0×3FF6_6000 0×3FF6_6FFF 4 KB


I2C1 0×3FF6_7000 0×3FF6_7FFF 4 KB


SDMMC 0×3FF6_8000 0×3FF6_8FFF 4 KB


EMAC 0×3FF6_9000 0×3FF6_AFFF 8 KB


Peripheral


4.1.5 Cache


TWAI 0×3FF6_B000 0×3FF6_BFFF 4 KB


PWM1 0×3FF6_C000 0×3FF6_CFFF 4 KB


I2S1 0×3FF6_D000 0×3FF6_DFFF 4 KB


UART2 0×3FF6_E000 0×3FF6_EFFF 4 KB


PWM2 0×3FF6_F000 0×3FF6_FFFF 4 KB


PWM3 0×3FF7_0000 0×3FF7_0FFF 4 KB


RNG 0×3FF7_5000 0×3FF7_5FFF 4 KB


ESP32 uses a two-way set-associative cache. Each of the two CPUs has 32 KB of cache featuring a block


size of 32 bytes for accessing external storage.


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#sysmem)_ - Chapter _System and Memory_ - Section _Cache_ .

###### 4.2 System Clocks


4.2.1 CPU Clock


Upon reset, an external crystal clock source is selected as the default CPU clock. The external crystal clock


source also connects to a PLL to generate a high-frequency clock (typically 160 MHz).


In addition, ESP32 has an internal 8 MHz oscillator. The application can select the clock source from the


external crystal clock source, the PLL clock or the internal 8 MHz oscillator. The selected clock source drives


the CPU clock directly, or after division, depending on the application.


4.2.2 RTC Clock


The RTC clock has five possible sources:


_•_ External low-speed (32 kHz) crystal clock


_•_ External crystal clock divided by 4


_•_ Internal RC oscillator (typically about 150 kHz, and adjustable)


_•_ Internal 8 MHz oscillator


_•_ Internal 31.25 kHz clock (derived from the internal 8 MHz oscillator divided by 256)


When the chip is in the normal power mode and needs faster CPU accessing, the application can choose the


external high-speed crystal clock divided by 4 or the internal 8 MHz oscillator. When the chip operates in the


low-power mode, the application chooses the external low-speed (32 kHz) crystal clock, the internal RC clock


or the internal 31.25 kHz clock.


Espressif Systems 29
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


4.2.3 Audio PLL Clock


The audio clock is generated by the ultra-low-noise fractional-N PLL.


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#resclk)_ - Chapter _Reset and Clock_ .

###### 4.3 RTC and Low-power Management


4.3.1 Power Management Unit (PMU)


With the use of advanced power-management technologies, ESP32 can switch between different power


modes.


_•_ Power modes


- Active mode: The chip radio is powered up. The chip can receive, transmit, or listen.


- Modem-sleep mode: The CPU is operational and the clock is configurable. The Wi-Fi/Bluetooth


baseband and radio are disabled.


- Light-sleep mode: The CPU is paused. The RTC memory and RTC peripherals, as well as the ULP


coprocessor are running. Any wake-up events (MAC, SDIO host, RTC timer, or external interrupts)


will wake up the chip.


- Deep-sleep mode: Only the RTC memory and RTC peripherals are powered up. Wi-Fi and Bluetooth


connection data are stored in the RTC memory. The ULP coprocessor is functional.


- Hibernation mode: The internal 8 MHz oscillator and ULP coprocessor are disabled. The RTC


recovery memory is powered down. Only one RTC timer on the slow clock and certain RTC GPIOs


are active. The RTC timer or the RTC GPIOs can wake up the chip from the Hibernation mode.


Table 4-2. Power Consumption by Power Modes


Power mode Description Power Consumption


Active (RF working)


The CPU is
Modem-sleep

powered up.


160 MHz [*] Dual-core chip(s) 27 mA ~ 44 mA

Single-core chip(s) 27 mA ~ 34 mA


Wi-Fi/BT Tx packet
Table 5-4 for details.


Wi-Fi Tx packet
Please refer to


Wi-Fi/BT Rx and listening


240 MHz [*] Dual-core chip(s) 30 mA ~ 68 mA

Single-core chip(s) N/A


Dual-core chip(s) 20 mA ~ 31 mA
Normal speed: 80 MHz

Single-core chip(s) 20 mA ~ 25 mA


Light-sleep - 0.8 mA


The ULP coprocessor is powered up. 150 _µ_ A


Deep-sleep


ULP sensor-monitored pattern 100 _µ_ A @1% duty


RTC timer + RTC memory 10 _µ_ A


Hibernation RTC timer only 5 _µ_ A


Power off CHIP_PU is set to low level, the chip is powered down. 1 _µ_ A


_•_  - Among the ESP32 series of SoCs, ESP32-D0WD-V3, ESP32-D0WDRH2-V3, ESP32-U4WDH, ESP32-D0WD


[(NRND), ESP32-D0WDQ6 (NRND), and ESP32-D0WDQ6-V3 (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd) have a maximum CPU frequency of 240 MHz,


Espressif Systems 30
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


[ESP32-S0WD (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd) has a maximum CPU frequency of 160 MHz.


_•_ When Wi-Fi is enabled, the chip switches between Active and Modem-sleep modes. Therefore, power consumption


changes accordingly.


_•_ In Modem-sleep mode, the CPU frequency changes automatically. The frequency depends on the CPU load and


the peripherals used.


_•_ During Deep-sleep, when the ULP coprocessor is powered on, peripherals such as GPIO and RTC I2C are able to


operate.


_•_ When the system works in the ULP sensor-monitored pattern, the ULP coprocessor works with the ULP sensor


periodically and the ADC works with a duty cycle of 1%, so the power consumption is 100 _µ_ A.


4.3.2 Ultra-Low-Power Coprocessor


The ULP coprocessor and RTC memory remain powered on during the Deep-sleep mode. Hence, the


developer can store a program for the ULP coprocessor in the RTC slow memory to access the peripheral


devices, internal timers and internal sensors during the Deep-sleep mode. This is useful for designing


applications where the CPU needs to be woken up by an external event, or a timer, or a combination of the


two, while maintaining minimal power consumption.


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#ulp)_ - Chapter _ULP Coprocessor_ .

###### 4.4 Timers and Watchdogs


4.4.1 General Purpose Timers


There are four general-purpose timers embedded in the chip. They are all 64-bit generic timers which are


based on 16-bit prescalers and 64-bit auto-reload-capable up/down-timers.


The timers feature:


_•_ A 16-bit clock prescaler, from 2 to 65536


_•_ A 64-bit timer


_•_ Configurable up/down timer: incrementing or decrementing


_•_ Halt and resume of time-base counter


_•_ Auto-reload at alarming


_•_ Software-controlled instant reload


_•_ Level and edge interrupt generation


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#timg)_ - Chapter _Timer Group_ .


4.4.2 Watchdog Timers


The chip has three watchdog timers: one in each of the two timer modules (called the Main Watchdog Timer,


or MWDT) and one in the RTC module (called the RTC Watchdog Timer, or RWDT). These watchdog timers are


intended to recover from an unforeseen fault causing the application program to abandon its normal


sequence. A watchdog timer has four stages. Each stage may trigger one of three or four possible actions


upon the expiry of its programmed time period, unless the watchdog is fed or disabled. The actions are:


Espressif Systems 31
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


interrupt, CPU reset, core reset, and system reset. Only the RWDT can trigger the system reset, and is able to


reset the entire chip, including the RTC itself. A timeout value can be set for each stage individually.


During flash boot the RWDT and the first MWDT start automatically in order to detect, and recover from,


booting problems.


The watchdogs have the following features:


_•_ Four stages, each of which can be configured or disabled separately


_•_ A programmable time period for each stage


_•_ One of three or four possible actions (interrupt, CPU reset, core reset, and system reset) upon the expiry


of each stage


_•_ 32-bit expiry counter


_•_ Write protection that prevents the RWDT and MWDT configuration from being inadvertently altered


_•_ SPI flash boot protection


If the boot process from an SPI flash does not complete within a predetermined time period, the


watchdog will reboot the entire system.


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#wdt)_ - Chapter _Watchdog Timers_ .

###### 4.5 Cryptographic Hardware Accelerators


ESP32 is equipped with hardware accelerators of general algorithms, such as AES (FIPS PUB 197), SHA (FIPS


PUB 180-4), and RSA. The chip also supports independent arithmetic, such as large-number modular


multiplication and large-number multiplication. The maximum operation length for RSA, large-number modular


multiplication, and large-number multiplication is 4096 bits.


The hardware accelerators greatly improve operation speed and reduce software complexity. They also


support code encryption and dynamic decryption, which ensures that code in the flash will not be


hacked.

###### 4.6 Radio and Wi-Fi


The radio module consists of the following blocks:


_•_ 2.4 GHz receiver


_•_ 2.4 GHz transmitter


_•_ Bias and regulators


_•_ Balun and transmit-receive switch


_•_ Clock generator


4.6.1 2.4 GHz Receiver


The 2.4 GHz receiver demodulates the 2.4 GHz RF signal to quadrature baseband signals and converts them


to the digital domain with two high-resolution, high-speed ADCs. To adapt to varying signal channel


conditions, RF filters, Automatic Gain Control (AGC), DC offset cancelation circuits and baseband filters are


integrated in the chip.


Espressif Systems 32
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


4.6.2 2.4 GHz Transmitter


The 2.4 GHz transmitter modulates the quadrature baseband signals to the 2.4 GHz RF signal, and drives the


antenna with a high-powered Complementary Metal Oxide Semiconductor (CMOS) power amplifier. The use of


digital calibration further improves the linearity of the power amplifier, enabling state-of-the-art performance in


delivering up to +20.5 dBm of power for an 802.11b transmission and +18 dBm for an 802.11n transmission.


Additional calibrations are integrated to cancel any radio imperfections, such as:


_•_ Carrier leakage


_•_ I/Q phase matching


_•_ Baseband nonlinearities


_•_ RF nonlinearities


_•_ Antenna matching


These built-in calibration routines reduce the amount of time required for product testing, and render the


testing equipment unnecessary.


4.6.3 Clock Generator


The clock generator produces quadrature clock signals of 2.4 GHz for both the receiver and the transmitter. All


components of the clock generator are integrated into the chip, including all inductors, varactors, filters,


regulators and dividers.


The clock generator has built-in calibration and self-test circuits. Quadrature clock phases and phase noise


are optimized on-chip with patented calibration algorithms which ensure the best performance of the receiver


and the transmitter.


4.6.4 Wi-Fi Radio and Baseband


ESP32 implements a TCP/IP and full 802.11 b/g/n Wi-Fi MAC protocol. It supports the Basic Service Set (BSS)


STA and SoftAP operations under the Distributed Control Function (DCF). Power management is handled with


minimal host interaction to minimize the active-duty period.


The ESP32 Wi-Fi Radio and Baseband support the following features:


_•_ 802.11b/g/n


_•_ 802.11n MCS0-7 in both 20 MHz and 40 MHz bandwidth


_•_ 802.11n MCS32 (RX)


_•_ 802.11n 0.4 _µ_ s guard-interval


_•_ up to 150 Mbps of data rate


_•_ Receiving STBC 2×1


_•_ Up to 20.5 dBm of transmitting power


_•_ Adjustable transmitting power


_•_ Antenna diversity


ESP32 supports antenna diversity with an external RF switch. One or more GPIOs control the RF switch


and selects the best antenna to minimize the effects of channel fading.


Espressif Systems 33
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


4.6.5 Wi-Fi MAC


The ESP32 Wi-Fi MAC applies low-level protocol functions automatically. They are as follows:


_•_ Four virtual Wi-Fi interfaces


_•_ Simultaneous Infrastructure BSS Station mode/SoftAP mode/Promiscuous mode


_•_ RTS protection, CTS protection, Immediate Block ACK


_•_ Defragmentation


_•_ TX/RX A-MPDU, RX A-MSDU


_•_ TXOP


_•_ WMM


_•_ CCMP (CBC-MAC, counter mode), TKIP (MIC, RC4), WAPI (SMS4), WEP (RC4) and CRC


_•_ Automatic beacon monitoring (hardware TSF)

###### 4.7 Bluetooth


The chip integrates a Bluetooth link controller and Bluetooth baseband, which carry out the baseband


protocols and other low-level link routines, such as modulation/demodulation, packet processing, bit stream


processing, frequency hopping, etc.


4.7.1 Bluetooth Radio and Baseband


The Bluetooth Radio and Baseband support the following features:


_•_ Class-1, class-2 and class-3 transmit output powers, and a dynamic control range of up to 21 dB


_•_ _π_ /4 DQPSK and 8 DPSK modulation


_•_ High performance in NZIF receiver sensitivity with a minimum sensitivity of -94 dBm


_•_ Class-1 operation without external PA


_•_ Internal SRAM allows full-speed data-transfer, mixed voice and data, and full piconet operation


_•_ Logic for forward error correction, header error control, access code correlation, CRC, demodulation,


encryption bit stream generation, whitening and transmit pulse shaping


_•_ ACL, SCO, eSCO, and AFH


_•_ A-law, _µ_ -law, and CVSD digital audio CODEC in PCM interface


_•_ SBC audio CODEC


_•_ Power management for low-power applications


_•_ SMP with 128-bit AES


4.7.2 Bluetooth Interface


_•_ Provides UART HCI interface, up to 4 Mbps


_•_ Provides SDIO/SPI HCI interface


_•_ Provides PCM/I2S audio interface


Espressif Systems 34
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


4.7.3 Bluetooth Stack


The Bluetooth stack of the chip is compliant with the Bluetooth v4.2 BR/EDR and Bluetooth LE specifications.


4.7.4 Bluetooth Link Controller


The link controller operates in three major states: standby, connection and sniff. It enables multiple


connections, and other operations, such as inquiry, page, and secure simple-pairing, and therefore enables


Piconet and Scatternet. Below are the features:


_•_ Classic Bluetooth


   - Device Discovery (inquiry, and inquiry scan)


   - Connection establishment (page, and page scan)


   - Multi-connections


   - Asynchronous data reception and transmission


   - Synchronous links (SCO/eSCO)


   - Master/Slave Switch


   - Adaptive Frequency Hopping and Channel assessment


   - Broadcast encryption


   - Authentication and encryption


   - Secure Simple-Pairing


   - Multi-point and scatternet management


   - Sniff mode


   - Connectionless Slave Broadcast (transmitter and receiver)


   - Enhanced Power Control


   - Ping


_•_ Bluetooth Low Energy


   - Advertising


   - Scanning


   - Simultaneous advertising and scanning


   - Multiple connections


   - Asynchronous data reception and transmission


   - Adaptive Frequency Hopping and Channel assessment


   - Connection parameter update


   - Data Length Extension


   - Link Layer Encryption


   - LE Ping


Espressif Systems 35
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description

###### 4.8 Digital Peripherals


4.8.1 General Purpose Input / Output Interface (GPIO)


ESP32 has 34 GPIO pins which can be assigned various functions by programming the appropriate registers.


There are several kinds of GPIOs: digital-only, analog-enabled, capacitive-touch-enabled, etc. Analog-enabled


GPIOs and Capacitive-touch-enabled GPIOs can be configured as digital GPIOs.


Most of the digital GPIOs can be configured as internal pull-up or pull-down, or set to high impedance. When


configured as an input, the input value can be read through the register. The input can also be set to


edge-trigger or level-trigger to generate CPU interrupts. Most of the digital IO pins are bi-directional,


non-inverting and tristate, including input and output buffers with tristate control. These pins can be


multiplexed with other functions, such as the SDIO, UART, SPI, etc. (More details can be found in the


Appendix, Table IO_MUX. ) For low-power operations, the GPIOs can be set to hold their states.


For details, see Section 4.10 _Peripheral Pin Configurations_, Appendix A –ESP32 Pin Lists and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.2 Serial Peripheral Interface (SPI)


ESP32 integrates four SPI controllers which can be used to communicate with external devices that use the


SPI protocol. Controller SPI0 is used as a buffer for accessing external memory. Controller SPI1 can be used


as a master. Controllers SPI2 and SPI3 can be configured as either a master or a slave.


SPI1, SPI2, and SPI3 use signal buses prefixed with SPI, HSPI, and VSPI, respectively.


Features of General Purpose SPI (GP-SPI)


_•_ Programmable data transfer length, in multiples of 1 byte


_•_ Four-line full-duplex/half-duplex communication and three-line half-duplex communication support


_•_ Master mode and slave mode


_•_ Programmable CPOL and CPHA


_•_ Programmable clock


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#spi)_ - Chapter _SPI Controller_ .


Pin Assignment


For SPI, the pins are multiplexed with GPIO6 ~ GPIO11 via the IO MUX. For HSPI, the pins are multiplexed with


GPIO2, GPIO4, GPIO12 ~ GPIO15 via the IO MUX. For VSPI, the pins are multiplexed with GPIO5, GPIO18 ~


GPIO19, GPIO21 ~ GPIO23 via the IO MUX.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.3 Universal Asynchronous Receiver Transmitter (UART)


ESP32 has three UART interfaces that facilitate the transmission and reception of asynchronous serial data


between the chip and external UART devices.


Espressif Systems 36
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Feature List


_•_ Programmable baud rates up to 5 MBaud


_•_ RAM shared by TX FIFOs and RX FIFOs


_•_ Supports input baud rate self-check


_•_ Support for various lengths of data bits and stop bits


_•_ Parity bit support


_•_ Asynchronous communication (RS232 and RS485) and IrDA support


_•_ Supports DMA to communicate data in high speed


_•_ Supports UART wake-up


_•_ Supports both software and hardware flow control


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#uart)_ - Chapter _UART Controller_ .


Pin Assignment


The pins for UART can be chosen from any GPIOs via the GPIO Matrix.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.4 I2C Interface


ESP32 has two I2C bus interfaces which can serve as I2C master or slave, depending on the user’s


configuration.


Feature List


_•_ Standard mode (100 Kbit/s)


_•_ Fast mode (400 Kbit/s)


_•_ Up to 5 MHz, yet constrained by SDA pull-up strength


_•_ Support for 7-bit and 10-bit addressing, as well as dual address mode


_•_ Supports continuous data transmission with disabled Serial Clock Line (SCL)


_•_ Supports programmable digital noise filter


Users can program command registers to control I2C interfaces, so that they have more flexibility.


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#i2c)_ - Chapter _I2C Controller_ .


Pin Assignment


For regular I2C, the pins used can be chosen from any GPIOs via the GPIO Matrix.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


Espressif Systems 37
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


4.8.5 I2S Interface


The I2S Controller in the ESP32 chip provides a flexible communication interface for streaming digital data in


multimedia applications, particularly digital audio applications.


Feature List


_•_ Master mode and slave mode


_•_ Full-duplex and half-duplex communications


_•_ A variety of audio standards supported


_•_ Configurable high-precision output clock


_•_ Supports PDM signal input and output


_•_ Configurable data transmit and receive modes


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#i2s)_ - Chapter _I2S Controller_ .


Pin Assignment


The pins for the I2S Controller can be chosen from any GPIOs via the GPIO Matrix.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.6 Remote Control Peripheral


The Remote Control Peripheral (RMT) controls the transmission and reception of infrared remote control


signals.


Feature List


_•_ Eight channels for sending and receiving infrared remote control signals


_•_ Independent transmission and reception capabilities for each channel


_•_ Clock divider counter, state machine, and receiver for each RX channel


_•_ Supports various infrared protocols


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#rmt)_ - Chapter _Remote Control Peripheral_ .


Pin Assignment


The pins for the Remote Control Peripheral can be chosen from any GPIOs via the GPIO Matrix.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.7 Pulse Counter Controller (PCNT)


The pulse counter controller (PCNT) is designed to count input pulses by tracking rising and falling edges of


the input pulse signal.


Espressif Systems 38
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Feature List


_•_ Eight independent pulse counter units


_•_ Each pulse counter unit has a 16-bit signed counter register and two channels


_•_ Counter modes: increment, decrement, or disable


_•_ Glitch filtering for input pulse signals and control signals


_•_ Selection between counting on rising or falling edges of the input pulse signal


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#pcnt)_ - Chapter _Pulse Count Controller_ .


Pin Assignment


The pins for the Pulse Count Controller can be chosen from any GPIOs via the GPIO Matrix.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.8 LED PWM Controller


The LED PWM Controller (LEDC) is designed to generate PWM signals for LED control.


Feature List


_•_ Sixteen independent PWM generators


_•_ Maximum PWM duty cycle resolution of 20 bits


_•_ Eight independent timers with 20-bit counters, configurable fractional clock dividers and counter


overflow values


_•_ Adjustable phase of PWM signal output


_•_ PWM duty cycle dithering


_•_ Automatic duty cycle fading


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#ledpwm)_ - Chapter _LED PWM Controller_ .


Pin Assignment


The pins for the LED PWM Controller can be chosen from any GPIOs via the GPIO Matrix.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.9 Motor Control PWM


The Pulse Width Modulation (PWM) controller can be used for driving digital motors and smart lights. The


controller consists of PWM timers, the PWM operator and a dedicated capture sub-module. Each timer


provides timing in synchronous or independent form, and each PWM operator generates a waveform for one


PWM channel. The dedicated capture sub-module can accurately capture events with external timing.


Espressif Systems 39
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Feature List


_•_ Three PWM timers for precise timing and frequency control


   - Every PWM timer has a dedicated 8-bit clock prescaler


   - The 16-bit counter in the PWM timer can work in count-up mode, count-down mode, or


count-up-down mode


   - A hardware sync can trigger a reload on the PWM timer with a phase register. It will also trigger the

prescaler’restart, so that the timer’s clock can also be synced, with selectable hardware


synchronization source


_•_ Three PWM operators for generating waveform pairs


   - Six PWM outputs to operate in several topologies


   - Configurable dead time on rising and falling edges; each set up independently


   - Modulating of PWM output by high-frequency carrier signals, useful when gate drivers are insulated


with a transformer


_•_ Fault Detection module


   - Programmable fault handling in both cycle-by-cycle mode and one-shot mode


   - A fault condition can force the PWM output to either high or low logic levels


_•_ Capture module for hardware-based signal processing


   - Speed measurement of rotating machinery


   - Measurement of elapsed time between position sensor pulses


   - Period and duty cycle measurement of pulse train signals


   - Decoding current or voltage amplitude derived from duty-cycle-encoded signals of current/voltage


sensors


   - Three individual capture channels, each of which with a 32-bit time-stamp register


   - Selection of edge polarity and prescaling of input capture signals


   - The capture timer can sync with a PWM timer or external signals


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#mcpwm)_ - Chapter _Motor Control PWM_ .


Pin Assignment


The pins for the Motor Control PWM can be chosen from any GPIOs via the GPIO Matrix.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.10 SD/SDIO/MMC Host Controller


An SD/SDIO/MMC host controller is available on ESP32.


Espressif Systems 40
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Feature List


_•_ Supports two external cards


_•_ Supports SD Memory Card standard: version 3.0 and version 3.01)


_•_ Supports SDIO Version 3.0


_•_ Supports Consumer Electronics Advanced Transport Architecture (CE-ATA Version 1.1)


_•_ Supports Multimedia Cards (MMC version 4.41, eMMC version 4.5 and version 4.51)


The controller allows up to 80 MHz clock output in three different data-bus modes: 1-bit, 4-bit, and 8-bit


modes. It supports two SD/SDIO/MMC4.41 cards in a 4-bit data-bus mode. It also supports one SD card


operating at 1.8 V.


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#sdhost)_ - Chapter _SD/MMC Host Controller_ .


Pin Assignment


The pins for SD/SDIO/MMC Host Controller are multiplexed with GPIO2, GPIO4, GPIO6 ~ GPIO15 via IO


MUX.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.11 SDIO/SPI Slave Controller


ESP32 integrates an SD device interface that conforms to the industry-standard SDIO Card Specification


Version 2.0, and allows a host controller to access the SoC, using the SDIO bus interface and protocol. ESP32


acts as the slave on the SDIO bus. The host can access the SDIO-interface registers directly and can access


shared memory via a DMA engine, thus maximizing performance without engaging the processor cores.


Feature List


The SDIO/SPI slave controller supports the following features:


_•_ SPI, 1-bit SDIO, and 4-bit SDIO transfer modes over the full clock range from 0 to 50 MHz


_•_ Configurable sampling and driving clock edge


_•_ Special registers for direct access by host


_•_ Interrupts to host for initiating data transfer


_•_ Automatic loading of SDIO bus data and automatic discarding of padding data


_•_ Block size of up to 512 bytes


_•_ Interrupt vectors between the host and the slave, allowing both to interrupt each other


_•_ Supports DMA for data transfer


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#sdioslave)_ - Chapter _SDIO Slave Controller_ .


Espressif Systems 41
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Pin Assignment


The pins for SDIO/SPI Slave Controller are multiplexed with GPIO2, GPIO4, GPIO6 ~ GPIO15 via IO MUX.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.12 TWAI [®] Controller


The Two-wire Automotive Interface (TWAI [®] ) is a multi-master, multi-cast communication protocol designed for


automotive applications. The TWAI controller facilitates the communication based on this protocol.


Feature List


_•_ Compatible with ISO 11898-1 protocol (CAN Specification 2.0)


_•_ Standard frame format (11-bit ID) and extended frame format (29-bit ID)


_•_ Bit rates:


   - From 25 Kbit/s to 1 Mbit/s in chip revision v0.0/v1.0/v1.1


   - From 12.5 Kbit/s to 1 Mbit/s in chip revision v3.0/v3.1


_•_ Multiple modes of operation: Normal, Listen Only, and Self-Test


_•_ 64-byte receive FIFO


_•_ Special transmissions: single-shot transmissions and self reception


_•_ Acceptance filter (single and dual filter modes)


_•_ Error detection and handling: error counters, configurable error interrupt threshold, error code capture,


arbitration lost capture


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#twai)_ - Chapter _Two-wire Automotive Interface (TWAI)_ .


Pin Assignment


The pins for the Two-wire Automotive Interface can be chosen from any GPIOs via the GPIO Matrix.


For more information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.8.13 Ethernet MAC Interface


An IEEE-802.3-2008-compliant Media Access Controller (MAC) is provided for Ethernet LAN communications.


ESP32 requires an external physical interface device (PHY) to connect to the physical LAN bus (twisted-pair,


fiber, etc.). The PHY is connected to ESP32 through 17 signals of MII or nine signals of RMII.


Feature List


_•_ 10 Mbps and 100 Mbps rates


_•_ Dedicated DMA controller allowing high-speed transfer between the dedicated SRAM and Ethernet MAC


_•_ Tagged MAC frame (VLAN support)


Espressif Systems 42
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


_•_ Half-duplex (CSMA/CD) and full-duplex operation


_•_ MAC control sublayer (control frames)


_•_ 32-bit CRC generation and removal


_•_ Several address-filtering modes for physical and multicast address (multicast and group addresses)


_•_ 32-bit status code for each transmitted or received frame


_•_ Internal FIFOs to buffer transmit and receive frames. The transmit FIFO and the receive FIFO are both 512


words (32-bit)


_•_ Hardware PTP (Precision Time Protocol) in accordance with IEEE 1588 2008 (PTP V2)


_•_ 25 MHz/50 MHz clock output


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#ethernetmac)_ - Chapter _Ethernet Media Access Controller (MAC)_ .


Pin Assignment


For information about the pin assignment of Ethernet MAC Interface, see Section 4.10 _Peripheral Pin_


_Configurations_ and _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .

###### 4.9 Analog Peripherals


4.9.1 Analog-to-Digital Converter (ADC)


ESP32 integrates two 12-bit SAR ADCs and supports measurements on 18 channels (analog-enabled pins).


The ULP coprocessor in ESP32 is also designed to measure voltage, while operating in the sleep mode, which


enables low-power consumption. The CPU can be woken up by a threshold setting and/or via other


triggers.


Table 4-3 describes the ADC characteristics.


Table 4-3. ADC Characteristics


Parameter Description Min Max Unit


RTC controller; ADC connected to an
DNL (Differential nonlinearity) –7 7 LSB
external 100 nF capacitor; DC signal input;


ambient temperature at 25 °C;
INL (Integral nonlinearity) –12 12 LSB
Wi-Fi&Bluetooth off


RTC controller                    - 200 ksps
Sampling rate

DIG controller                     - 2 Msps


Notes:


_•_ When atten = 3 and the measurement result is above 3000 (voltage at approx. 2450 mV), the ADC


accuracy will be worse than described in the table above.


_•_ To get better DNL results, users can take multiple sampling tests with a filter, or calculate the average


value.


Espressif Systems 43
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


_•_ The input voltage range of GPIO pins within VDD3P3_RTC domain should strictly follow the DC


characteristics provided in Table 5-3. Otherwise, measurement errors may be introduced, and chip


performance may be affected.


By default, there are ±6% differences in measured results between chips. ESP-IDF provides couple of


[calibration methods](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/adc_calibration.html) for ADC1. Results after calibration using eFuse Vref value are shown in Table 4-4. For


higher accuracy, users may apply other calibration methods provided in ESP-IDF, or implement their


own.


Table 4-4. ADC Calibration Results


Parameter Description Min Max Unit


Atten = 0, effective measurement range of 100 _∼_ 950 mV –23 23 mV


Total error


Atten = 1, effective measurement range of 100 _∼_ 1250 mV –30 30 mV

Atten = 2, effective measurement range of 150 _∼_ 1750 mV –40 40 mV

Atten = 3, effective measurement range of 150 _∼_ 2450 mV –60 60 mV


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#sensor)_ - Chapter _On-Chip Sensors and Analog Signal_


_Processing_ .


Pin Assignment


With appropriate settings, the ADCs can be configured to measure voltage on 18 pins maximum. For detailed


information about the pin assignment, see Section 4.10 _Peripheral Pin Configurations_ and


_[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and GPIO Matrix_ .


4.9.2 Digital-to-Analog Converter (DAC)


Two 8-bit DAC channels can be used to convert two digital signals into two analog voltage signal outputs. The


design structure is composed of integrated resistor strings and a buffer. This dual DAC supports power supply


as input voltage reference. The two DAC channels can also support independent conversions.


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#sensor)_ - Chapter _On-Chip Sensors and Analog Signal_


_Processing_ .


Pin Assignment


The DAC can be configured by GPIO 25 and GPIO 26. For detailed information about the pin assignment, see


Section 4.10 _Peripheral Pin Configurations_ and _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ - Chapter _IO_MUX and_


_GPIO Matrix_ .


4.9.3 Touch Sensor


ESP32 has 10 capacitive-sensing GPIOs, which detect variations induced by touching or approaching the


GPIOs with a finger or other objects. The low-noise nature of the design and the high sensitivity of the circuit


allow relatively small pads to be used. Arrays of pads can also be used, so that a larger area or more points


can be detected.


Espressif Systems 44
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Pin Assignment


The 10 capacitive-sensing GPIOs are listed in Table 4-5.


Table 4-5. Capacitive-Sensing GPIOs Available on ESP32


Capacitive-Sensing Signal Name Pin Name


T0 GPIO4


T1 GPIO0


T2 GPIO2


T3 MTDO


T4 MTCK


T5 MTDI


T6 MTMS


T7 GPIO27


T8 32K_XN


T9 32K_XP


For details, see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#sensor)_ - Chapter _On-Chip Sensors and Analog Signal_


_Processing_ .


Note:


ESP32 Touch Sensor has not passed the Conducted Susceptibility (CS) test for now, and thus has limited application


scenarios.


Espressif Systems 45
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description

###### 4.10 Peripheral Pin Configurations


Table 4-6. Peripheral Pin Configurations


Interface Signal Pin Function


ADC1_CH0 SENSOR_VP


ADC1_CH1 SENSOR_CAPP


ADC1_CH2 SENSOR_CAPN


ADC1_CH3 SENSOR_VN


ADC1_CH4 32K_XP


ADC1_CH5 32K_XN


ADC1_CH6 VDET_1


ADC1_CH7 VDET_2


ADC


ADC2_CH0 GPIO4


ADC2_CH1 GPIO0


ADC2_CH2 GPIO2


ADC2_CH3 MTDO


ADC2_CH4 MTCK


ADC2_CH5 MTDI


ADC2_CH6 MTMS


ADC2_CH7 GPIO27


ADC2_CH8 GPIO25


ADC2_CH9 GPIO26


Two 12-bit SAR ADCs


DAC_1 GPIO25
DAC Two 8-bit DACs
DAC_2 GPIO26


TOUCH0 GPIO4


TOUCH1 GPIO0


TOUCH2 GPIO2


TOUCH3 MTDO


Touch Sensor


JTAG


TOUCH4 MTCK


TOUCH5 MTDI


TOUCH6 MTMS


TOUCH7 GPIO27


TOUCH8 32K_XN


TOUCH9 32K_XP


MTDI MTDI


MTCK MTCK
JTAG for software debugging

MTMS MTMS


Capacitive touch sensors


MTDO MTDO


Espressif Systems 46
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Interface Signal Pin Function


HS2_CLK MTMS


HS2_CMD MTDO


SD/SDIO/MMC Host


Controller


Motor PWM


SDIO/SPI Slave


Controller


UART


I2C


HS2_DATA0 GPIO2


HS2_DATA1 GPIO4


HS2_DATA2 MTDI


HS2_DATA3 MTCK


PWM0_OUT0~2


PWM1_OUT_IN0~2


PWM0_FLT_IN0~2


U1RXD_in


U1CTS_in


U1TXD_out


U1RTS_out


U2RXD_in


U2CTS_in


U2TXD_out


U2RTS_out


I2CEXT0_SCL_in


I2CEXT0_SDA_in


I2CEXT1_SCL_in


I2CEXT1_SDA_in


I2CEXT0_SCL_out


I2CEXT0_SDA_out


I2CEXT1_SCL_out


I2CEXT1_SDA_out


PWM1_FLT_IN0~2


PWM0_CAP_IN0~2


PWM1_CAP_IN0~2


PWM0_SYNC_IN0~2


PWM1_SYNC_IN0~2


Any GPIO Pins


Supports SD memory card V3.01 standard


Three channels of 16-bit timers generate


PWM waveforms. Each channel has a pair


of output signals, three fault detection


signals, three event-capture signals, and


three sync signals.


SDIO interface that conforms to the


industry standard SDIO 2.0 card


specification


SD_CLK MTMS


SD_CMD MTDO


SD_DATA0 GPIO2


SD_DATA1 GPIO4


SD_DATA2 MTDI


SD_DATA3 MTCK


U0RXD_in


U0CTS_in


U0DSR_in


U0TXD_out


U0RTS_out


U0DTR_out


Three UART devices with hardware
Any GPIO Pins

flow-control and DMA


Any GPIO Pins Two I2C devices in slave or master mode


Espressif Systems 47
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Interface Signal Pin Function


LED PWM


I2S


ledc_hs_sig_out0~7 16 independent channels @80 MHz
Any GPIO Pins

ledc_ls_sig_out0~7 clock/RTC CLK. Duty accuracy: 16 bits.


I2S0I_DATA_in0~15


I2S0O_BCK_in


I2S0O_WS_in


I2S0I_BCK_in


I2S0I_WS_in


I2S0I_H_SYNC


I2S0I_V_SYNC


I2S0I_H_ENABLE


I2S0O_BCK_out


I2S0I_WS_out


I2S0O_DATA_out0~23


I2S1I_DATA_in0~15


Any GPIO Pins


I2S0O_WS_out
Stereo input and output from/to the audio


I2S0I_BCK_out


codec; parallel LCD data output; parallel


camera data input.


I2S1O_BCK_in Note: I2S0_CLK and I2S1_CLK can only


I2S1O_WS_in


I2S1I_BCK_in


I2S1I_WS_in


I2S1I_H_SYNC


I2S1I_V_SYNC


I2S1I_H_ENABLE


I2S1O_BCK_out


I2S1O_WS_out


I2S1I_BCK_out


I2S1I_WS_out


I2S1O_DATA_out0~23


I2S0_CLK GPIO0, U0RXD,


I2S1_CLK or U0TXD


be mapped to GPIO0, U0RXD (GPIO3), or


U0TXD (GPIO1) via IO MUX by selecting


GPIO functions CLK_OUT1, CLK_OUT2,


and CLK_OUT3. For more information,


see _[ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf#iomuxgpio)_ 

Chapter _IO_MUX and GPIO Matrix_ - Table


_IO MUX Pad Summary_ .


RMT_SIG_IN0~7 Eight channels for an IR transmitter and
RMT Any GPIO Pins

RMT_SIG_OUT0~7 receiver of various waveforms


General Purpose


SPI


HSPIQ_in/_out


HSPID_in/_out


HSPICLK_in/_out


HSPI_CS0_in/_out


HSPI_CS1_out


HSPI_CS2_out


VSPIQ_in/_out


VSPID_in/_out


VSPICLK_in/_out


VSPI_CS0_in/_out


VSPI_CS1_out


VSPI_CS2_out


Any GPIO Pins


Standard SPI consists of clock,


chip-select, MOSI and MISO. These SPIs


can be connected to LCD and other


external devices. They support the


following features:

_•_ Both master and slave modes;

_•_ Four sub-modes of the SPI transfer


format;

_•_ Configurable SPI frequency;

_•_ Up to 64 bytes of FIFO and DMA.


Espressif Systems 48
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Interface Signal Pin Function


SPIHD SD_DATA_2


SPIWP SD_DATA_3


SPICS0 SD_CMD


SPICLK SD_CLK


SPIQ SD_DATA_0


SPID SD_DATA_1


HSPICLK MTMS


Parallel QSPI


EMAC


HSPICS0 MTDO


HSPIQ MTDI


HSPID MTCK


HSPIHD GPIO4


HSPIWP GPIO2


VSPICLK GPIO18


VSPICS0 GPIO5


VSPIQ GPIO19


VSPID GPIO23


VSPIHD GPIO21


VSPIWP GPIO22


EMAC_TX_CLK GPIO0


EMAC_RX_CLK GPIO5


EMAC_TX_EN GPIO21


EMAC_TXD0 GPIO19


EMAC_TXD1 GPIO22


EMAC_TXD2 MTMS


EMAC_TXD3 MTDI


EMAC_RX_ER MTCK


EMAC_RX_DV GPIO27


EMAC_RXD0 GPIO25


EMAC_RXD1 GPIO26


EMAC_RXD2 U0TXD


EMAC_RXD3 MTDO


EMAC_CLK_OUT GPIO16


EMAC_CLK_OUT_180 GPIO17


EMAC_TX_ER GPIO4


EMAC_MDC_out Any GPIO Pins


EMAC_MDI_in Any GPIO Pins


EMAC_MDO_out Any GPIO Pins


EMAC_CRS_out Any GPIO Pins


EMAC_COL_out Any GPIO Pins


Supports Standard SPI, Dual SPI, and


Quad SPI that can be connected to the


external flash and SRAM


Ethernet MAC with MII/RMII interface


Espressif Systems 49
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


4 Functional Description


Interface Signal Pin Function


pcnt_sig_ch0_in0


pcnt_sig_ch1_in0


pcnt_ctrl_ch0_in0


pcnt_ctrl_ch1_in0


pcnt_sig_ch0_in1


pcnt_sig_ch1_in1


pcnt_ctrl_ch0_in1


pcnt_ctrl_ch1_in1


pcnt_sig_ch0_in2


pcnt_sig_ch1_in2


pcnt_ctrl_ch0_in2


pcnt_ctrl_ch1_in2


pcnt_sig_ch0_in3


pcnt_sig_ch1_in3


Operating in seven different modes, the


pulse counter captures pulse and counts


pulse edges.


Pulse Counter


TWAI


pcnt_ctrl_ch0_in3


pcnt_ctrl_ch1_in3


pcnt_sig_ch0_in4


pcnt_sig_ch1_in4


pcnt_ctrl_ch0_in4


pcnt_ctrl_ch1_in4


pcnt_sig_ch0_in5


pcnt_sig_ch1_in5


pcnt_ctrl_ch0_in5


pcnt_ctrl_ch1_in5


pcnt_sig_ch0_in6


pcnt_sig_ch1_in6


pcnt_ctrl_ch0_in6


pcnt_ctrl_ch1_in6


pcnt_sig_ch0_in7


pcnt_sig_ch1_in7


pcnt_ctrl_ch0_in7


pcnt_ctrl_ch1_in7


twai_rx


twai_tx


twai_bus_off_on


twai_clkout


Any GPIO Pins


Compatible with ISO 11898-1 protocol
Any GPIO Pins

(CAN Specification 2.0)


Espressif Systems 50
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


5 Electrical Characteristics

##### 5 Electrical Characteristics

###### 5.1 Absolute Maximum Ratings


Stresses above those listed in Table 5-1 _Absolute Maximum Ratings_ may cause permanent damage to the


device. These are stress ratings only and normal operation of the device at these or any other conditions


beyond those indicated in Section 5.2 Recommended Power Supply Characteristics is not implied. Exposure


to absolute-maximum-rated conditions for extended periods may affect device reliability.


Table 5-1. Absolute Maximum Ratings


Parameter Description Min Max Unit


VDDA, VDD3P3, VDD3P3_RTC,

Allowed input voltage –0.3 3.6 V
VDD3P3_CPU, VDD_SDIO

I _output_ [1] Cumulative IO output current      - 1200 mA

T _ST ORE_ Storage temperature –40 150 °C

1 The product proved to be fully functional after all its IO pins were pulled high while being connected


to ground for 24 consecutive hours at ambient temperature of 25 °C.

###### 5.2 Recommended Power Supply Characteristics


Table 5-2. Recommended Power Supply Characteristics


Parameter Description Min Typ Max Unit


VDDA, VDD3P3_RTC, VDD3P3,

VDD_SDIO (3.3 V mode) _[note 1]_


Voltage applied to power supply

2.3/3.0 _[note 2]_ 3.3 3.6 V
pins per power domain


VDD3P3_CPU Voltage applied to power supply pin 1.8 3.3 3.6 V


I _V DD_


Current delivered by external power

0.5                       -                       - A
supply


T _[note 3]_ Operating temperature –40 - 125 °C


1. _•_ VDD_SDIO works as the power supply for the related IO, and also for an external device. Please refer to the


Appendix IO_MUX of this datasheet for more details.


_•_ VDD_SDIO can be sourced internally by the ESP32 from the VDD3P3_RTC power domain:


- When VDD_SDIO operates at 3.3 V, it is driven directly by VDD3P3_RTC through a 6 Ω resistor, therefore,


there will be some voltage drop from VDD3P3_RTC.


- When VDD_SDIO operates at 1.8 V, it can be generated from ESP32’s internal LDO. The maximum current


this LDO can offer is 40 mA, and the output voltage range is 1.65 V ~ 2.0 V.


_•_ VDD_SDIO can also be driven by an external power supply.


_•_ Please refer to Section 2.5.2 Power Scheme, for more information.


2. _•_ Chips with a 3.3 V flash or PSRAM in-package: this minimum voltage is 3.0 V;


_•_ Chips with no flash or PSRAM in-package: this minimum voltage is 2.3 V;


_•_ For more information, see Section 1 ESP32 Series Comparison.


3. The operating temperature of ESP32-U4WDH and ESP32-D0WDRH2-V3 ranges from –40 °C to 85 °C, due to the


in-package flash or PSRAM. For other chips that have no in-package flash or PSRAM, their operating temperature is


–40 °C ~ 125 °C.


Espressif Systems 51
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


5 Electrical Characteristics

###### 5.3 DC Characteristics (3.3 V, 25 °C)


Table 5-3. DC Characteristics (3.3 V, 25 °C)


Parameter Description Min Typ Max Unit


C _IN_ Pin capacitance  - 2  - pF

V _IH_ High-level input voltage 0.75 × VDD [1]  - VDD [1] + 0.3 V

V _IL_ Low-level input voltage –0.3  - 0.25 × VDD [1] V


I _IH_ High-level input current    -    - 50 nA


I _IL_ Low-level input current    -    - 50 nA

V _OH_ High-level output voltage 0.8 × VDD [1]  -  - V

V _OL_ Low-level output voltage  -  - 0.1 × VDD [1] V


VDD3P3_CPU

- 40         - mA
power domain [1] _[,]_ [2]


VDD3P3_RTC

- 40         - mA
power domain [1] _[,]_ [2]


VDD_SDIO power

- 20         - mA
domain [1] _[,]_ [3]


I _OH_


I _OL_


High-level source current

(VDD [1] = 3.3 V,


V _OH_ >= 2.64 V,


output drive strength set


to the maximum)


Low-level sink current


(VDD [1] = 3.3 V, V _OL_ = 0.495 V,


output drive strength set to the maximum)


- 28 - mA


R _P U_ Resistance of internal pull-up resistor - 45 - kΩ


R _P D_ Resistance of internal pull-down resistor - 45 - kΩ


V _IH_ _ _nRST_


V _IL_ _ _nRST_


Chip reset release voltage (CHIP_PU voltage


is within the specifed range)


Low-level input voltage of CHIP_PU


to shut down the chip


0.75 × VDD [1] - VDD [1] + 0.3 V


   -    - 0.6 V


1. Please see Table IO_MUX for IO’s power domain. VDD is the I/O voltage for a particular power domain of pins.


2. For VDD3P3_CPU and VDD3P3_RTC power domain, per-pin current sourced in the same domain is gradually


reduced from around 40 mA to around 29 mA, V _OH_ >=2.64 V, as the number of current-source pins increases.


3. For VDD_SDIO power domain, per-pin current sourced in the same domain is gradually reduced from around 30 mA


to around 10 mA, V _OH_ >=2.64 V, as the number of current-source pins increases.

###### 5.4 RF Current Consumption in Active Mode


The current consumption measurements are taken with a 3.3 V supply at 25 °C of ambient temperature at the


RF port. All transmitters’ measurements are based on a 50% duty cycle.


Table 5-4. Current Consumption Depending on RF Modes


Work Mode Min Typ Max Unit


Transmit 802.11b, DSSS 1 Mbps, POUT = +19.5 dBm    - 240    - mA


Transmit 802.11g, OFDM 54 Mbps, POUT = +16 dBm    - 190    - mA


Transmit 802.11n, OFDM MCS7, POUT = +14 dBm    - 180    - mA


Receive 802.11b/g/n    - 95 ~ 100    - mA


Espressif Systems 52
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


5 Electrical Characteristics


Work Mode Min Typ Max Unit


Transmit BT/BLE, POUT = 0 dBm    - 130    - mA


Receive BT/BLE    - 95 ~ 100    - mA

###### 5.5 Reliability


Table 5-5. Reliability Qualifications


Test Item Test Conditions Test Standard


HTOL (High Temperature

125 °C, 1000 hours JESD22-A108
Operating Life)


ESD (Electro-Static


Discharge Sensitivity)


HBM (Human Body Mode) [1] ± 2000 V JS-001

CDM (Charge Device Mode) [2] ± 500 V JS-002


Current trigger ± 200 mA
Latch up JESD78
Voltage trigger 1.5 × VDD _max_


J-STD-020,


JESD47,


JESD22-A113


Preconditioning


Bake 24 hours @125 °C


Moisture soak (level 3: 192 hours @30 °C, 60% RH)


IR reflow solder: 260 + 0 °C, 20 seconds, three


times


TCT (Temperature Cycling

–65 °C / 150 °C, 500 cycles JESD22-A104
Test)


Autoclave Test 121 °C, 100% RH, 96 hours JESD22-A102


uHAST (Highly Accel

erated Stress Test,


unbiased)


130 °C, 85% RH, 96 hours JESD22-A118


HTSL (High Temperature

150 °C, 1000 hours JESD22-A103
Storage Life)


1. JEDEC document JEP155 states that 500 V HBM allows safe manufacturing with a standard ESD control process.


2. JEDEC document JEP157 states that 250 V CDM allows safe manufacturing with a standard ESD control process.

###### 5.6 Wi-Fi Radio


Table 5-6. Wi-Fi Radio Characteristics


Parameter Description Min Typ Max Unit

Operating frequency range _[note]_ [1]    - 2412    - 2484 MHz

Output impedance _[note]_ [2]   -   - _note 2_   - Ω


11n, MCS7 12 13 14 dBm
TX power _[note]_ [3]

11b mode 18.5 19.5 20.5 dBm


11b, 1 Mbps                     - –98                     - dBm

11b, 11 Mbps                     - –88                     - dBm

11g, 6 Mbps                    - –93                    - dBm


Sensitivity


11g, 54 Mbps - –75 - dBm


Espressif Systems 53
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


5 Electrical Characteristics


Parameter Description Min Typ Max Unit

11n, HT20, MCS0                   - –93                   - dBm

11n, HT20, MCS7                   - –73                   - dBm

11n, HT40, MCS0                   - –90                   - dBm

11n, HT40, MCS7                   - –70                   - dBm


11g, 6 Mbps                    - 27                    - dB


Adjacent channel rejection


11g, 54 Mbps - 13 - dB


11n, HT20, MCS0 - 27 - dB


11n, HT20, MCS7 - 12 - dB


1. Device should operate in the frequency range allocated by regional regulatory authorities. Target operating


frequency range is configurable by software.


2. The typical value of the Wi-Fi radio output impedance is different between chips in different QFN packages. For


chips in a QFN 6×6 package, the value is 30+j10 Ω. For chips in a QFN 5×5 package, the value is 35+j10 Ω.


3. Target TX power is configurable based on device or certification requirements.

###### 5.7 Bluetooth Radio


5.7.1 Receiver **–** Basic Data Rate


Table 5-7. Receiver Characteristics **–** Basic Data Rate


Parameter Description Min Typ Max Unit


Sensitivity @0.1% BER    - –90 –89 –88 dBm


Maximum received signal @0.1% BER    - 0    -    - dBm


Co-channel C/I    -    - +7    - dB


F = F0 + 1 MHz                        -                        - –6 dB

F = F0 –1 MHz                       -                       - –6 dB


Adjacent channel selectivity C/I


Out-of-band blocking performance


F = F0 + 2 MHz - - –25 dB

F = F0 –2 MHz - - –33 dB

F = F0 + 3 MHz - - –25 dB

F = F0 –3 MHz - - –45 dB


30 MHz ~ 2000 MHz –10 - - dBm

2000 MHz ~ 2400 MHz –27 - - dBm

2500 MHz ~ 3000 MHz –27 - - dBm

3000 MHz ~ 12.5 GHz –10 - - dBm


Intermodulation    - –36    -    - dBm


5.7.2 Transmitter **–** Basic Data Rate


Table 5-8. Transmitter Characteristics **–** Basic Data Rate


Parameter Description Min Typ Max Unit

RF transmit power _[note]_ [1]  -  - 0  - dBm


Gain control step  -  - 3  - dB


Espressif Systems 54
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


5 Electrical Characteristics


Parameter Description Min Typ Max Unit


RF power control range  - –12  - +9 dBm


+20 dB bandwidth  -  - 0.9  - MHz


F = F0 ± 2 MHz                       - –47                       - dBm


Adjacent channel transmit power


F = F0 ± 3 MHz - –55 - dBm

F = F0 ± > 3 MHz - –60 - dBm


∆ _f_ 1avg  -  -  - 155 kHz

∆ _f_ 2max  - 133.7  -  - kHz

∆ _f_ 2avg/∆ _f_ 1avg  -  - 0.92  -  
ICFT  -  - –7  - kHz


Drift rate   -   - 0.7   - kHz/50 _µ_ s


Drift (DH1)  -  - 6  - kHz


Drift (DH5)  -  - 6  - kHz


1. There are in total eight power levels from level 0 to level 7, with transmit power ranging from –12 dBm to 9 dBm.


When the power level rises by 1, the transmit power increases by 3 dB. Power level 4 is used by default and the


corresponding transmit power is 0 dBm.


5.7.3 Receiver **–** Enhanced Data Rate


Table 5-9. Receiver Characteristics **–** Enhanced Data Rate


Parameter Description Min Typ Max Unit


_π_ /4 DQPSK


Sensitivity @0.01% BER    - –90 –89 –88 dBm


Maximum received signal @0.01% BER    -    - 0    - dBm


Co-channel C/I    -    - 11    - dB


F = F0 + 1 MHz                           - –7                           - dB

F = F0 –1 MHz                          - –7                          - dB


Adjacent channel selectivity C/I


F = F0 + 2 MHz   - –25   - dB

F = F0 –2 MHz   - –35   - dB

F = F0 + 3 MHz   - –25   - dB

F = F0 –3 MHz   - –45   - dB


8DPSK


Sensitivity @0.01% BER - –84 –83 –82 dBm


Maximum received signal @0.01% BER - - –5 - dBm


C/I c-channel - - 18 - dB


F = F0 + 1 MHz                       - 2                       - dB

F = F0 –1 MHz                       - 2                       - dB


Adjacent channel selectivity C/I


5.7.4 Transmitter **–** Enhanced Data Rate


F = F0 + 2 MHz - –25 - dB

F = F0 –2 MHz - –25 - dB

F = F0 + 3 MHz - –25 - dB

F = F0 –3 MHz - –38 - dB


Espressif Systems 55
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


5 Electrical Characteristics


Table 5-10. Transmitter Characteristics **–** Enhanced Data Rate


Parameter Description Min Typ Max Unit


RF transmit power (see note under Table 5-10)    -    - 0    - dBm


Gain control step    -    - 3    - dB


RF power control range    - –12    - +9 dBm


_π_ /4 DQPSK max w0   -   - –0.72   - kHz


_π_ /4 DQPSK max wi   -   - –6   - kHz


_π_ /4 DQPSK max |wi + w0|   -   - –7.42   - kHz


8DPSK max w0   -   - 0.7   - kHz


8DPSK max wi    -    - –9.6    - kHz


8DPSK max |wi + w0|    -    - –10    - kHz


RMS DEVM                    - 4.28                    - %


_π_ /4 DQPSK modulation accuracy


8 DPSK modulation accuracy


In-band spurious emissions


99% DEVM - 100 - %


Peak DEVM - 13.3 - %


RMS DEVM - 5.8 - %


99% DEVM - 100 - %


Peak DEVM - 14 - %


F = F0 ± 1 MHz - –46 - dBm

F = F0 ± 2 MHz - –40 - dBm

F = F0 ± 3 MHz - –46 - dBm

F = F0 +/–> 3 MHz - - –53 dBm


EDR differential phase coding    -    - 100    - %

###### 5.8 Bluetooth LE Radio


5.8.1 Receiver


Table 5-11. Receiver Characteristics **–** Bluetooth LE


Parameter Description Min Typ Max Unit


Sensitivity @30.8% PER   - –94 –93 –92 dBm


Maximum received signal @30.8% PER   - 0   -   - dBm


Co-channel C/I   -   - +10   - dB


F = F0 + 1 MHz                          - –5                          - dB

F = F0 –1 MHz                          - –5                          - dB


Adjacent channel selectivity C/I


Out-of-band blocking performance


F = F0 + 2 MHz - –25 - dB

F = F0 –2 MHz - –35 - dB

F = F0 + 3 MHz - –25 - dB

F = F0 –3 MHz - –45 - dB


30 MHz ~ 2000 MHz –10 - - dBm


2000 MHz ~ 2400


MHz


2500 MHz ~ 3000


MHz


–27 - - dBm


–27 - - dBm


ESP32 Series Datasheet v5.3


Espressif Systems 56
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


5 Electrical Characteristics


Parameter Description Min Typ Max Unit

3000 MHz ~ 12.5 GHz –10                        -                        - dBm


Intermodulation    - –36    -    - dBm


Espressif Systems 57
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


5 Electrical Characteristics


5.8.2 Transmitter


Table 5-12. Transmitter Characteristics **–** Bluetooth LE


Parameter Description Min Typ Max Unit


RF transmit power (see note under Table 5-8)   -   - 0   - dBm


Gain control step   -   - 3   - dB


RF power control range   - –12   - +9 dBm


F = F0 ± 2 MHz                        - –52                        - dBm


Adjacent channel transmit power


F = F0 ± 3 MHz - –58 - dBm

F = F0 ± > 3 MHz - –60 - dBm


∆ _f_ 1avg - - - 265 kHz

∆ _f_ 2max - 247 - - kHz

∆ _f_ 2avg/∆ _f_ 1avg - - 0.92 - 
ICFT - - –10 - kHz


Drift rate - - 0.7 - kHz/50 _µ_ s


Drift - - 2 - kHz


Espressif Systems 58
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


6 Packaging

##### 6 Packaging


_•_ For information about tape, reel, and chip marking, please refer to _[ESP32 Chip Packaging Information](https://docs.espressif.com/projects/esp-packaging/en/latest/esp32/00-index/index_chip.html)_ .


_•_ The pins of the chip are numbered in anti-clockwise order starting from Pin 1 in the top view. For pin


numbers and pin names, see also pin layout figures in Section 2.1 Pin Layout.


**Pin 1**
**Pin 2**
**Pin 3**


**Pin 1**
**Pin 2**
**Pin 3**


Figure 6-1. ~~Q~~ FN48 (6×6 mm ~~)~~ ~~P~~ ackage


D


**PIN #1 DDT**
**BY MARKING** L


D2


**PIN #1 ID**
**C0.350**


REF.
A
A1
A3
D
E
02
E2
b
b1
L
e


**in 1**
**Pn 2**


**0 a.a.a. C**


**0 aaa C**


~~**1//lccclCI**~~


L

L
48L SLP E
(5x5r1r1) **e_f**


TOP VIEw


SIDE VIEw


**CCC** 0.10
ddd 0.05
eee 0.08
fff 0.10


**PIN #1 ID** Dimensional Ref.
**C0.350** REF. Min. Norn. Max.

A 0.800 0.850 0.900
A1 0.000 **--** 0.050
A3 0.203 Ref.
D 4.950 5.000 5.050

E2 E 4.950 5.000 5.050
### + 02 3.650 3.700 3.750

E2 3.650 3.700 3.750
b 0.130 0.180 0.230
b1 0.070 0.120 0.170
L 0.300 0.350 0.400

**48X bl** e 0.350 BSC

Tol. of Form&Position
aaa 0.10
BOTTOM VIEw bbb 0.10


### +


E2


**bl**
**48X**


Notes

**1.** **All DIMENSIONS ARE IN MILLIMETERS,**
**2, DIMENSIONING AND T**  - **LERANCING PER JEDEC M**  - **[-]** **220,**


Figure 6-2. QFN48 (5×5 mm) Package


Espressif Systems 59
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


_Related Documentation and Resources_

##### Related Documentation and Resources

###### Related Documentation


_•_ [ESP32 Technical Reference Manual](https://espressif.com/documentation/esp32_technical_reference_manual_en.pdf)  - Detailed information on how to use the ESP32 memory and peripherals.

_•_ [ESP32 Hardware Design Guidelines](https://espressif.com/documentation/esp32_hardware_design_guidelines_en.pdf)  - Guidelines on how to integrate the ESP32 into your hardware product.

_•_ [ESP32 ECO and Workarounds for Bugs](https://espressif.com/documentation/eco_and_workarounds_for_bugs_in_esp32_en.pdf)  - Correction of ESP32 design errors.

_•_ [ESP32 Series SoC Errata](https://espressif.com/sites/default/files/documentation/esp32_errata_en.pdf)  - Descriptions of known errors in ESP32 series of SoCs.

_•_ _Certificates_


[https://espressif.com/en/support/documents/certifcates](https://espressif.com/en/support/documents/certificates?keys=&field_product_value%5B%5D=ESP32)

_•_ _ESP32 Product/Process Change Notifications (PCN)_


[https://espressif.com/en/support/documents/pcns](https://espressif.com/en/support/documents/pcns)

_•_ _ESP32 Advisories_  - Information on security, bugs, compatibility, component reliability.


[https://espressif.com/en/support/documents/advisories](https://espressif.com/en/support/documents/advisories)

_•_ _Documentation Updates and Update Notification Subscription_


[https://espressif.com/en/support/download/documents](https://espressif.com/en/support/download/documents)

###### Developer Zone


_•_ [ESP-IDF Programming Guide for ESP32](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html)  - Extensive documentation for the ESP-IDF development framework.

_•_ _ESP-IDF_ and other development frameworks on GitHub.


[https://github.com/espressif](https://github.com/espressif)

_•_ _ESP32 BBS Forum_  - Engineer-to-Engineer (E2E) Community for Espressif products where you can post questions,


share knowledge, explore ideas, and help solve problems with fellow engineers.


[https://esp32.com/](https://esp32.com/)

_•_ _The ESP Journal_  - Best Practices, Articles, and Notes from Espressif folks.


[https://blog.espressif.com/](https://blog.espressif.com/)

_•_ See the tabs _SDKs and Demos_, _Apps_, _Tools_, _AT Firmware_ .


[https://espressif.com/en/support/download/sdks-demos](https://espressif.com/en/support/download/sdks-demos)

###### Products


_•_ _ESP32 Series SoCs_  - Browse through all ESP32 SoCs.


[https://espressif.com/en/products/socs?id=ESP32](https://espressif.com/en/products/socs?id=ESP32)

_•_ _ESP32 Series Modules_  - Browse through all ESP32-based modules.


[https://espressif.com/en/products/modules?id=ESP32](https://espressif.com/en/products/modules?id=ESP32)

_•_ _ESP32 Series DevKits_  - Browse through all ESP32-based devkits.


[https://espressif.com/en/products/devkits?id=ESP32](https://espressif.com/en/products/devkits?id=ESP32)

_•_ _ESP Product Selector_  - Find an Espressif hardware product suitable for your needs by comparing or applying filters.


[https://products.espressif.com/#/product-selector?language=en](https://products.espressif.com/#/product-selector?language=en)

###### Contact Us


_•_ See the tabs _Sales Questions_, _Technical Enquiries_, _Circuit Schematic & PCB Design Review_, _Get Samples_


(Online stores), _Become Our Supplier_, _Comments & Suggestions_ .


[https://espressif.com/en/contact-us/sales-questions](https://espressif.com/en/contact-us/sales-questions)


Espressif Systems 60
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Appendix A

##### Appendix A – ESP32 Pin Lists

###### A.1. Notes on ESP32 Pin Lists


Table 6-1. Notes on ESP32 Pin Lists


No. Description


In Table IO_MUX, the boxes highlighted in yellow indicate the GPIO pins that are input-only.
1

Please see the following note for further details.


GPIO pins 34-39 are input-only. These pins do not feature an output driver or internal pull





up/pull-down circuitry. The pin names are: SENSOR_VP (GPIO36), SENSOR_CAPP (GPIO37),


SENSOR_CAPN (GPIO38), SENSOR_VN (GPIO39), VDET_1 (GPIO34), VDET_2 (GPIO35).


The pins are grouped into four power domains: VDDA (analog power supply), VDD3P3_RTC


(RTC power supply), VDD3P3_CPU (power supply of digital IOs and CPU cores), VDD_SDIO


(power supply of SDIO IOs). VDD_SDIO is the output of the internal SDIO-LDO. The voltage of


SDIO-LDO can be configured at 1.8 V or be the same as that of VDD3P3_RTC. The strapping


pin and eFuse bits determine the default voltage of the SDIO-LDO. Software can change


the voltage of the SDIO-LDO by configuring register bits. For details, please see the column

“Power Domain”in Table IO_MUX.


The functional pins in the VDD3P3_RTC domain are those with analog functions, including


the 32 kHz crystal oscillator, ADC, DAC, and the capacitive touch sensor. Please see columns

“Analog Function 0 ~ 2” in Table IO_MUX.


These VDD3P3_RTC pins support the RTC function, and can work during Deep-sleep. For
5

example, an RTC-GPIO can be used for waking up the chip from Deep-sleep.



The GPIO pins support up to six digital functions, as shown in columns “Function 0 ~ 5” In

Table IO_MUX. The function selection registers will be set as “ _N_ ”, where _N_ is the function


number. Below are some definitions:

_•_ SD_* is for signals of the SDIO slave.

_•_ HS1_* is for Port 1 signals of the SDIO host.

_•_ HS2_* is for Port 2 signals of the SDIO host.

_•_ MT* is for signals of the JTAG.

_•_ U0* is for signals of the UART0 module.

_•_ U1* is for signals of the UART1 module.

_•_ U2* is for signals of the UART2 module.

_•_ SPI* is for signals of the SPI01 module.

_•_ HSPI* is for signals of the SPI2 module.

_•_ VSPI* is for signals of the SPI3 module.


Espressif Systems 61
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Appendix A


No. Description


Each column about digital “Function” is accompanied by a column about “Type”. Please

see the following explanations for the meanings of “type” with respect to each “function”

they are associated with. For each “Function- _N_ ”, “type” signifies:

_•_ I: input only. If a function other than “Function- _N_ ” is assigned, the input signal of

“Function- _N_ ” is still from this pin.

_•_ I1: input only. If a function other than “Function- _N_ ” is assigned, the input signal of

“Function- _N_ ” is always “1”.

_•_ I0: input only. If a function other than “Function- _N_ ” is assigned, the input signal of








“Function- _N_ ” is always “0”.

_•_ O: output only.

_•_ T: high-impedance.

_•_ I/O/T: combinations of input, output, and high-impedance according to the function


signal.

_•_ I1/O/T: combinations of input, output, and high-impedance, according to the function

signal. If a function is not selected, the input signal of the function is “1”.

For example, pin 30 can function as HS1_CMD or SD_CMD, where HS1_CMD is of an“I1/O/T”


type. If pin 30 is selected as HS1_CMD, this pin’s input and output are controlled by the SDIO

host. If pin 30 is not selected as HS1_CMD, the input signal of the SDIO host is always “1”.


Each digital output pin is associated with its configurable drive strength. Column “Drive


Strength” in Table IO_MUX lists the default values. The drive strength of the digital output


pins can be configured into one of the following four options:

_•_ 0: ~5 mA

_•_ 1: ~10 mA

_•_ 2: ~20 mA

_•_ 3: ~40 mA


The default value is 2.


The drive strength of the internal pull-up (wpu) and pull-down (wpd) is ~75 _µ_ A.


Column“At Reset” in Table IO_MUX lists the status of each pin during reset, including input

enable (ie=1), internal pull-up (wpu) and internal pull-down (wpd). During reset, all pins are


output-disabled.


Column “After Reset” in Table IO_MUX lists the status of each pin immediately after reset,


including input-enable (ie=1), internal pull-up (wpu) and internal pull-down (wpd). After reset,

each pin is set to “Function 0”. The output-enable is controlled by digital Function 0.


Table Ethernet_MAC is about the signal mapping inside Ethernet MAC. The Ethernet MAC


supports MII and RMII interfaces, and supports both the internal PLL clock and the external


clock source. For the MII interface, the Ethernet MAC is with/without the TX_ERR signal.


MDC, MDIO, CRS and COL are slow signals, and can be mapped onto any GPIO pin through


the GPIO-Matrix.


Table GPIO Matrix is for the GPIO-Matrix. The signals of the on-chip functional modules can


be mapped onto any GPIO pin. Some signals can be mapped onto a pin by both IO-MUX

and GPIO-Matrix, as shown in the column tagged as“Same input signal from IO_MUX core”


in Table GPIO Matrix.


Espressif Systems 62
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Appendix A


No. Description


*In Table GPIO_Matrix，the column “Default Value if unassigned”records the default value



of the an input signal if no GPIO is assigned to it. The actual value is determined by register


GPIO_FUNC _m_ _IN_INV_SEL and GPIO_FUNC _m_ _IN_SEL. (The value of _m_ ranges from 1 to


255.)


###### A.2. GPIO_Matrix

Signal

Default
No. Input Signals

Value If


Unassigned*


Table 6-2. GPIO_Matrix


Same Input Signal


from IO_MUX Core Output Signals


Output Enable


Output Signal


0 SPICLK_in 0 yes SPICLK_out SPICLK_oe


1 SPIQ_in 0 yes SPIQ_out SPIQ_oe


2 SPID_in 0 yes SPID_out SPID_oe


3 SPIHD_in 0 yes SPIHD_out SPIHD_oe


4 SPIWP_in 0 yes SPIWP_out SPIWP_oe


5 SPICS0_in 0 yes SPICS0_out SPICS0_oe


6 SPICS1_in 0 no SPICS1_out SPICS1_oe


7 SPICS2_in 0 no SPICS2_out SPICS2_oe


8 HSPICLK_in 0 yes HSPICLK_out HSPICLK_oe


9 HSPIQ_in 0 yes HSPIQ_out HSPIQ_oe


10 HSPID_in 0 yes HSPID_out HSPID_oe


11 HSPICS0_in 0 yes HSPICS0_out HSPICS0_oe


12 HSPIHD_in 0 yes HSPIHD_out HSPIHD_oe


13 HSPIWP_in 0 yes HSPIWP_out HSPIWP_oe


14 U0RXD_in 0 yes U0TXD_out 1’d1


15 U0CTS_in 0 yes U0RTS_out 1’d1


16 U0DSR_in 0 no U0DTR_out 1’d1


17 U1RXD_in 0 yes U1TXD_out 1’d1


18 U1CTS_in 0 yes U1RTS_out 1’d1


23 I2S0O_BCK_in 0 no I2S0O_BCK_out 1’d1


24 I2S1O_BCK_in 0 no I2S1O_BCK_out 1’d1


25 I2S0O_WS_in 0 no I2S0O_WS_out 1’d1


26 I2S1O_WS_in 0 no I2S1O_WS_out 1’d1


27 I2S0I_BCK_in 0 no I2S0I_BCK_out 1’d1


28 I2S0I_WS_in 0 no I2S0I_WS_out 1’d1


29 I2CEXT0_SCL_in 1 no I2CEXT0_SCL_out 1’d1


30 I2CEXT0_SDA_in 1 no I2CEXT0_SDA_out 1’d1


31 pwm0_sync0_in 0 no sdio_tohost_int_out 1’d1


32 pwm0_sync1_in 0 no pwm0_out0a 1’d1


33 pwm0_sync2_in 0 no pwm0_out0b 1’d1


Espressif Systems 63
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Appendix A


Signal

Default
No. Input Signals

Value If


Unassigned*


Same Input Signal


from IO_MUX Core Output Signals


Output Enable


Output Signal


34 pwm0_f0_in 0 no pwm0_out1a 1’d1


35 pwm0_f1_in 0 no pwm0_out1b 1’d1


36 pwm0_f2_in 0 no pwm0_out2a 1’d1


37 - 0 no pwm0_out2b 1’d1


39 pcnt_sig_ch0_in0 0 no - 1’d1


40 pcnt_sig_ch1_in0 0 no - 1’d1


41 pcnt_ctrl_ch0_in0 0 no - 1’d1


42 pcnt_ctrl_ch1_in0 0 no - 1’d1


43 pcnt_sig_ch0_in1 0 no - 1’d1


44 pcnt_sig_ch1_in1 0 no - 1’d1


45 pcnt_ctrl_ch0_in1 0 no - 1’d1


46 pcnt_ctrl_ch1_in1 0 no - 1’d1


47 pcnt_sig_ch0_in2 0 no - 1’d1


48 pcnt_sig_ch1_in2 0 no - 1’d1


49 pcnt_ctrl_ch0_in2 0 no - 1’d1


50 pcnt_ctrl_ch1_in2 0 no - 1’d1


51 pcnt_sig_ch0_in3 0 no - 1’d1


52 pcnt_sig_ch1_in3 0 no - 1’d1


53 pcnt_ctrl_ch0_in3 0 no - 1’d1


54 pcnt_ctrl_ch1_in3 0 no - 1’d1


55 pcnt_sig_ch0_in4 0 no - 1’d1


56 pcnt_sig_ch1_in4 0 no - 1’d1


57 pcnt_ctrl_ch0_in4 0 no - 1’d1


58 pcnt_ctrl_ch1_in4 0 no - 1’d1


61 HSPICS1_in 0 no HSPICS1_out HSPICS1_oe


62 HSPICS2_in 0 no HSPICS2_out HSPICS2_oe


63 VSPICLK_in 0 yes VSPICLK_out_mux VSPICLK_oe


64 VSPIQ_in 0 yes VSPIQ_out VSPIQ_oe


65 VSPID_in 0 yes VSPID_out VSPID_oe


66 VSPIHD_in 0 yes VSPIHD_out VSPIHD_oe


67 VSPIWP_in 0 yes VSPIWP_out VSPIWP_oe


68 VSPICS0_in 0 yes VSPICS0_out VSPICS0_oe


69 VSPICS1_in 0 no VSPICS1_out VSPICS1_oe


70 VSPICS2_in 0 no VSPICS2_out VSPICS2_oe


71 pcnt_sig_ch0_in5 0 no ledc_hs_sig_out0 1’d1


72 pcnt_sig_ch1_in5 0 no ledc_hs_sig_out1 1’d1


73 pcnt_ctrl_ch0_in5 0 no ledc_hs_sig_out2 1’d1


74 pcnt_ctrl_ch1_in5 0 no ledc_hs_sig_out3 1’d1


75 pcnt_sig_ch0_in6 0 no ledc_hs_sig_out4 1’d1


76 pcnt_sig_ch1_in6 0 no ledc_hs_sig_out5 1’d1


Espressif Systems 64
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Appendix A


Signal

Default
No. Input Signals

Value If


Unassigned*


Same Input Signal


from IO_MUX Core Output Signals


Output Enable


Output Signal


77 pcnt_ctrl_ch0_in6 0 no ledc_hs_sig_out6 1’d1


78 pcnt_ctrl_ch1_in6 0 no ledc_hs_sig_out7 1’d1


79 pcnt_sig_ch0_in7 0 no ledc_ls_sig_out0 1’d1


80 pcnt_sig_ch1_in7 0 no ledc_ls_sig_out1 1’d1


81 pcnt_ctrl_ch0_in7 0 no ledc_ls_sig_out2 1’d1


82 pcnt_ctrl_ch1_in7 0 no ledc_ls_sig_out3 1’d1


83 rmt_sig_in0 0 no ledc_ls_sig_out4 1’d1


84 rmt_sig_in1 0 no ledc_ls_sig_out5 1’d1


85 rmt_sig_in2 0 no ledc_ls_sig_out6 1’d1


86 rmt_sig_in3 0 no ledc_ls_sig_out7 1’d1


87 rmt_sig_in4 0 no rmt_sig_out0 1’d1


88 rmt_sig_in5 0 no rmt_sig_out1 1’d1


89 rmt_sig_in6 0 no rmt_sig_out2 1’d1


90 rmt_sig_in7 0 no rmt_sig_out3 1’d1


91 - - - rmt_sig_out4 1’d1


92 - - - rmt_sig_out6 1’d1


94 twai_rx 1 no rmt_sig_out7 1’d1


95 I2CEXT1_SCL_in 1 no I2CEXT1_SCL_out 1’d1


96 I2CEXT1_SDA_in 1 no I2CEXT1_SDA_out 1’d1


97 host_card_detect_n_1 0 no host_ccmd_od_pullup_en_n 1’d1


98 host_card_detect_n_2 0 no host_rst_n_1 1’d1


99 host_card_write_prt_1 0 no host_rst_n_2 1’d1


100 host_card_write_prt_2 0 no gpio_sd0_out 1’d1


101 host_card_int_n_1 0 no gpio_sd1_out 1’d1


102 host_card_int_n_2 0 no gpio_sd2_out 1’d1


103 pwm1_sync0_in 0 no gpio_sd3_out 1’d1


104 pwm1_sync1_in 0 no gpio_sd4_out 1’d1


105 pwm1_sync2_in 0 no gpio_sd5_out 1’d1


106 pwm1_f0_in 0 no gpio_sd6_out 1’d1


107 pwm1_f1_in 0 no gpio_sd7_out 1’d1


108 pwm1_f2_in 0 no pwm1_out0a 1’d1


109 pwm0_cap0_in 0 no pwm1_out0b 1’d1


110 pwm0_cap1_in 0 no pwm1_out1a 1’d1


111 pwm0_cap2_in 0 no pwm1_out1b 1’d1


112 pwm1_cap0_in 0 no pwm1_out2a 1’d1


113 pwm1_cap1_in 0 no pwm1_out2b 1’d1


114 pwm1_cap2_in 0 no pwm2_out1h 1’d1


115 pwm2_fta 1 no pwm2_out1l 1’d1


116 pwm2_ftb 1 no pwm2_out2h 1’d1


117 pwm2_cap1_in 0 no pwm2_out2l 1’d1


Espressif Systems 65
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Appendix A


Signal

Default
No. Input Signals

Value If


Unassigned*


Same Input Signal


from IO_MUX Core Output Signals


Output Enable


Output Signal


118 pwm2_cap2_in 0 no pwm2_out3h 1’d1


119 pwm2_cap3_in 0 no pwm2_out3l 1’d1


120 pwm3_fta 1 no pwm2_out4h 1’d1


121 pwm3_ftb 1 no pwm2_out4l 1’d1


122 pwm3_cap1_in 0 no - 1’d1


123 pwm3_cap2_in 0 no twai_tx 1’d1


124 pwm3_cap3_in 0 no twai_bus_off_on 1’d1


125 - - - twai_clkout 1’d1


140 I2S0I_DATA_in0 0 no I2S0O_DATA_out0 1’d1


141 I2S0I_DATA_in1 0 no I2S0O_DATA_out1 1’d1


142 I2S0I_DATA_in2 0 no I2S0O_DATA_out2 1’d1


143 I2S0I_DATA_in3 0 no I2S0O_DATA_out3 1’d1


144 I2S0I_DATA_in4 0 no I2S0O_DATA_out4 1’d1


145 I2S0I_DATA_in5 0 no I2S0O_DATA_out5 1’d1


146 I2S0I_DATA_in6 0 no I2S0O_DATA_out6 1’d1


147 I2S0I_DATA_in7 0 no I2S0O_DATA_out7 1’d1


148 I2S0I_DATA_in8 0 no I2S0O_DATA_out8 1’d1


149 I2S0I_DATA_in9 0 no I2S0O_DATA_out9 1’d1


150 I2S0I_DATA_in10 0 no I2S0O_DATA_out10 1’d1


151 I2S0I_DATA_in11 0 no I2S0O_DATA_out11 1’d1


152 I2S0I_DATA_in12 0 no I2S0O_DATA_out12 1’d1


153 I2S0I_DATA_in13 0 no I2S0O_DATA_out13 1’d1


154 I2S0I_DATA_in14 0 no I2S0O_DATA_out14 1’d1


155 I2S0I_DATA_in15 0 no I2S0O_DATA_out15 1’d1


156 - - - I2S0O_DATA_out16 1’d1


157 - - - I2S0O_DATA_out17 1’d1


158 - - - I2S0O_DATA_out18 1’d1


159 - - - I2S0O_DATA_out19 1’d1


160 - - - I2S0O_DATA_out20 1’d1


161 - - - I2S0O_DATA_out21 1’d1


162 - - - I2S0O_DATA_out22 1’d1


163 - - - I2S0O_DATA_out23 1’d1


164 I2S1I_BCK_in 0 no I2S1I_BCK_out 1’d1


165 I2S1I_WS_in 0 no I2S1I_WS_out 1’d1


166 I2S1I_DATA_in0 0 no I2S1O_DATA_out0 1’d1


167 I2S1I_DATA_in1 0 no I2S1O_DATA_out1 1’d1


168 I2S1I_DATA_in2 0 no I2S1O_DATA_out2 1’d1


169 I2S1I_DATA_in3 0 no I2S1O_DATA_out3 1’d1


170 I2S1I_DATA_in4 0 no I2S1O_DATA_out4 1’d1


171 I2S1I_DATA_in5 0 no I2S1O_DATA_out5 1’d1


Espressif Systems 66
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Appendix A


Signal

Default
No. Input Signals

Value If


Unassigned*


Same Input Signal


from IO_MUX Core Output Signals


Output Enable


Output Signal


172 I2S1I_DATA_in6 0 no I2S1O_DATA_out6 1’d1


173 I2S1I_DATA_in7 0 no I2S1O_DATA_out7 1’d1


174 I2S1I_DATA_in8 0 no I2S1O_DATA_out8 1’d1


175 I2S1I_DATA_in9 0 no I2S1O_DATA_out9 1’d1


176 I2S1I_DATA_in10 0 no I2S1O_DATA_out10 1’d1


177 I2S1I_DATA_in11 0 no I2S1O_DATA_out11 1’d1


178 I2S1I_DATA_in12 0 no I2S1O_DATA_out12 1’d1


179 I2S1I_DATA_in13 0 no I2S1O_DATA_out13 1’d1


180 I2S1I_DATA_in14 0 no I2S1O_DATA_out14 1’d1


181 I2S1I_DATA_in15 0 no I2S1O_DATA_out15 1’d1


182 - - - I2S1O_DATA_out16 1’d1


183 - - - I2S1O_DATA_out17 1’d1


184 - - - I2S1O_DATA_out18 1’d1


185 - - - I2S1O_DATA_out19 1’d1


186 - - - I2S1O_DATA_out20 1’d1


187 - - - I2S1O_DATA_out21 1’d1


188 - - - I2S1O_DATA_out22 1’d1


189 - - - I2S1O_DATA_out23 1’d1


190 I2S0I_H_SYNC 0 no pwm3_out1h 1’d1


191 I2S0I_V_SYNC 0 no pwm3_out1l 1’d1


192 I2S0I_H_ENABLE 0 no pwm3_out2h 1’d1


193 I2S1I_H_SYNC 0 no pwm3_out2l 1’d1


194 I2S1I_V_SYNC 0 no pwm3_out3h 1’d1


195 I2S1I_H_ENABLE 0 no pwm3_out3l 1’d1


196 - - - pwm3_out4h 1’d1


197 - - - pwm3_out4l 1’d1


198 U2RXD_in 0 yes U2TXD_out 1’d1


199 U2CTS_in 0 yes U2RTS_out 1’d1


200 emac_mdc_i 0 no emac_mdc_o emac_mdc_o


201 emac_mdi_i 0 no emac_mdo_o emac_mdo_o


202 emac_crs_i 0 no emac_crs_o emac_crs_oe


203 emac_col_i 0 no emac_col_o emac_col_oe


204 pcmfsync_in 0 no bt_audio0_irq 1’d1


205 pcmclk_in 0 no bt_audio1_irq 1’d1


206 pcmdin 0 no bt_audio2_irq 1’d1


207 - - - ble_audio0_irq 1’d1


208 - - - ble_audio1_irq 1’d1


209 - - - ble_audio2_irq 1’d1


210 - - - pcmfsync_out pcmfsync_en


211 - - - pcmclk_out pcmclk_en


Espressif Systems 67
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Appendix A


Signal

Default
No. Input Signals

Value If


Unassigned*


Same Input Signal


from IO_MUX Core Output Signals


Output Enable


Output Signal


212 - - - pcmdout pcmdout_en


213 - - - ble_audio_sync0_p 1’d1


214 - - - ble_audio_sync1_p 1’d1


215 - - - ble_audio_sync2_p 1’d1


224 - - - sig_in_func224 1’d1


225 - - - sig_in_func225 1’d1


226 - - - sig_in_func226 1’d1


227 - - - sig_in_func227 1’d1


228 - - - sig_in_func228 1’d1

###### A.3. Ethernet_MAC


Table 6-3. Ethernet_MAC


Pin Name Function6 MII (int_osc) MII (ext_osc) RMII (int_osc) RMII (ext_osc)


GPIO0 EMAC_TX_CLK TX_CLK (I) TX_CLK (I) CLK_OUT(O) EXT_OSC_CLK(I)


GPIO5 EMAC_RX_CLK RX_CLK (I) RX_CLK (I) - 

GPIO21 EMAC_TX_EN TX_EN(O) TX_EN(O) TX_EN(O) TX_EN(O)


GPIO19 EMAC_TXD0 TXD[0](O) TXD[0](O) TXD[0](O) TXD[0](O)


GPIO22 EMAC_TXD1 TXD[1](O) TXD[1](O) TXD[1](O) TXD[1](O)


MTMS EMAC_TXD2 TXD[2](O) TXD[2](O) - 

MTDI EMAC_TXD3 TXD[3](O) TXD[3](O) - 

MTCK EMAC_RX_ER RX_ER(I) RX_ER(I) - 

GPIO27 EMAC_RX_DV RX_DV(I) RX_DV(I) CRS_DV(I) CRS_DV(I)


GPIO25 EMAC_RXD0 RXD[0](I) RXD[0](I) RXD[0](I) RXD[0](I)


GPIO26 EMAC_RXD1 RXD[1](I) RXD[1](I) RXD[1](I) RXD[1](I)


U0TXD EMAC_RXD2 RXD[2](I) RXD[2](I) - 

MTDO EMAC_RXD3 RXD[3](I) RXD[3](I) - 

GPIO16 EMAC_CLK_OUT CLK_OUT(O) - CLK_OUT(O) 

GPIO17 EMAC_CLK_OUT_180 CLK_OUT_180(O) - CLK_OUT_180(O) 

GPIO4 EMAC_TX_ER TX_ERR(O)* TX_ERR(O)* - 

In GPIO Matrix* - MDC(O) MDC(O) MDC(O) MDC(O)


In GPIO Matrix* - MDIO(IO) MDIO(IO) MDIO(IO) MDIO(IO)


In GPIO Matrix* - CRS(I) CRS(I) - 

In GPIO Matrix* - COL(I) COL(I) - 

*Notes: 1. The GPIO Matrix can be any GPIO. 2. The TX_ERR (O) is optional.

###### A.4. IO_MUX


For the list of IO_MUX pins, please see the next page.


Espressif Systems 68
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


**Pin No.** **Power Supply Pin** **Analog Pin** **Digital Pin** **Power Domain** **Analog Function0**

**1** VDDA VDDA supply in

**2** LNA_IN VDD3P3

**3** VDD3P3 VDD3P3 supply in

**4** VDD3P3 VDD3P3 supply in


**Analog**
**Function1**


**Analog**
**Function2**


**RTC**
**Function0**


**IO_MUX**


**RTC Function1** **Function0** **Type** **Function1** **Type** **Function2** **Type** **Function3** **Type** **Function4** **Type** **Function5** **Type** **Drive Strength (2’d2: 20 mA)** **At Reset** **After Reset**


**5** SENSOR_VP VDD3P3_RTC ADC1_CH0 RTC_GPIO0 GPIO36 I GPIO36 I oe=0, ie=0 oe=0, ie=0

**6** SENSOR_CAPP VDD3P3_RTC ADC1_CH1 RTC_GPIO1 GPIO37 I GPIO37 I oe=0, ie=0 oe=0, ie=0

**7** SENSOR_CAPN VDD3P3_RTC ADC1_CH2 RTC_GPIO2 GPIO38 I GPIO38 I oe=0, ie=0 oe=0, ie=0

**8** SENSOR_VN VDD3P3_RTC ADC1_CH3 RTC_GPIO3 GPIO39 I GPIO39 I oe=0, ie=0 oe=0, ie=0

**9** CHIP_PU VDD3P3_RTC

**10** VDET_1 VDD3P3_RTC ADC1_CH6 RTC_GPIO4 GPIO34 I GPIO34 I oe=0, ie=0 oe=0, ie=0

**11** VDET_2 VDD3P3_RTC ADC1_CH7 RTC_GPIO5 GPIO35 I GPIO35 I oe=0, ie=0 oe=0, ie=0

**12** 32K_XP VDD3P3_RTC XTAL_32K_P ADC1_CH4 TOUCH9 RTC_GPIO9 GPIO32 I/O/T GPIO32 I/O/T 2'd2 oe=0, ie=0 oe=0, ie=0


**13** 32K_XN VDD3P3_RTC XTAL_32K_N ADC1_CH5 TOUCH8 RTC_GPIO8 GPIO33 I/O/T GPIO33 I/O/T 2'd2 oe=0, ie=0 oe=0, ie=0

**14** GPIO25 VDD3P3_RTC DAC_1 ADC2_CH8 RTC_GPIO6 GPIO25 I/O/T GPIO25 I/O/T EMAC_RXD0 I 2'd2 oe=0, ie=0 oe=0, ie=0

**15** GPIO26 VDD3P3_RTC DAC_2 ADC2_CH9 RTC_GPIO7 GPIO26 I/O/T GPIO26 I/O/T EMAC_RXD1 I 2'd2 oe=0, ie=0 oe=0, ie=0

**16** GPIO27 VDD3P3_RTC ADC2_CH7 TOUCH7 RTC_GPIO17 GPIO27 I/O/T GPIO27 I/O/T EMAC_RX_DV I 2'd2 oe=0, ie=0 oe=0, ie=0

**17** MTMS VDD3P3_RTC ADC2_CH6 TOUCH6 RTC_GPIO16 MTMS I0 HSPICLK I/O/T GPIO14 I/O/T HS2_CLK O SD_CLK I0 EMAC_TXD2 O 2'd2 oe=0, ie=0 oe=0, ie=1, wpu

**18** MTDI VDD3P3_RTC ADC2_CH5 TOUCH5 RTC_GPIO15 MTDI I1 HSPIQ I/O/T GPIO12 I/O/T HS2_DATA2 I1/O/T SD_DATA2 I1/O/T EMAC_TXD3 O 2'd2 oe=0, ie=1, wpd oe=0, ie=1, wpd

**19** VDD3P3_RTC VDD3P3_RTC supply in

**20** MTCK VDD3P3_RTC ADC2_CH4 TOUCH4 RTC_GPIO14 MTCK I1 HSPID I/O/T GPIO13 I/O/T HS2_DATA3 I1/O/T SD_DATA3 I1/O/T EMAC_RX_ER I 2'd2 oe=0, ie=0 oe=0, ie=1, wpd

**21** MTDO VDD3P3_RTC ADC2_CH3 TOUCH3 RTC_GPIO13 I2C_SDA MTDO O/T HSPICS0 I/O/T GPIO15 I/O/T HS2_CMD I1/O/T SD_CMD I1/O/T EMAC_RXD3 I 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**22** GPIO2 VDD3P3_RTC ADC2_CH2 TOUCH2 RTC_GPIO12 I2C_SCL GPIO2 I/O/T HSPIWP I/O/T GPIO2 I/O/T HS2_DATA0 I1/O/T SD_DATA0 I1/O/T 2'd2 oe=0, ie=1, wpd oe=0, ie=1, wpd

**23** GPIO0 VDD3P3_RTC ADC2_CH1 TOUCH1 RTC_GPIO11 I2C_SDA GPIO0 I/O/T CLK_OUT1 O GPIO0 I/O/T EMAC_TX_CLK I 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**24** GPIO4 VDD3P3_RTC ADC2_CH0 TOUCH0 RTC_GPIO10 I2C_SCL GPIO4 I/O/T HSPIHD I/O/T GPIO4 I/O/T HS2_DATA1 I1/O/T SD_DATA1 I1/O/T EMAC_TX_ER O 2'd2 oe=0, ie=1, wpd oe=0, ie=1, wpd


**25** GPIO16 VDD_SDIO GPIO16 I/O/T GPIO16 I/O/T HS1_DATA4 I1/O/T U2RXD I1 EMAC_CLK_OUT O 2'd2 oe=0, ie=0 oe=0, ie=1

**26** VDD_SDIO VDD_SDIO supply out/in

**27** GPIO17 VDD_SDIO GPIO17 I/O/T GPIO17 I/O/T HS1_DATA5 I1/O/T U2TXD O EMAC_CLK_OUT_180 O 2'd2 oe=0, ie=0 oe=0, ie=1

**28** SD_DATA_2 VDD_SDIO SD_DATA2 I1/O/T SPIHD I/O/T GPIO9 I/O/T HS1_DATA2 I1/O/T U1RXD I1 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**29** SD_DATA_3 VDD_SDIO SD_DATA3 I0/O/T SPIWP I/O/T GPIO10 I/O/T HS1_DATA3 I1/O/T U1TXD O 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**30** SD_CMD VDD_SDIO SD_CMD I1/O/T SPICS0 I/O/T GPIO11 I/O/T HS1_CMD I1/O/T U1RTS O 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**31** SD_CLK VDD_SDIO SD_CLK I0 SPICLK I/O/T GPIO6 I/O/T HS1_CLK O U1CTS I1 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**32** SD_DATA_0 VDD_SDIO SD_DATA0 I1/O/T SPIQ I/O/T GPIO7 I/O/T HS1_DATA0 I1/O/T U2RTS O 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**33** SD_DATA_1 VDD_SDIO SD_DATA1 I1/O/T SPID I/O/T GPIO8 I/O/T HS1_DATA1 I1/O/T U2CTS I1 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**34** GPIO5 VDD3P3_CPU GPIO5 I/O/T VSPICS0 I/O/T GPIO5 I/O/T HS1_DATA6 I1/O/T EMAC_RX_CLK I 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**35** GPIO18 VDD3P3_CPU GPIO18 I/O/T VSPICLK I/O/T GPIO18 I/O/T HS1_DATA7 I1/O/T 2'd2 oe=0, ie=0 oe=0, ie=1

**36** GPIO23 VDD3P3_CPU GPIO23 I/O/T VSPID I/O/T GPIO23 I/O/T HS1_STROBE I0 2'd2 oe=0, ie=0 oe=0, ie=1


**37** VDD3P3_CPU VDD3P3_CPU supply in

**38** GPIO19 VDD3P3_CPU GPIO19 I/O/T VSPIQ I/O/T GPIO19 I/O/T U0CTS I1 EMAC_TXD0 O 2'd2 oe=0, ie=0 oe=0, ie=1

**39** GPIO22 VDD3P3_CPU GPIO22 I/O/T VSPIWP I/O/T GPIO22 I/O/T U0RTS O EMAC_TXD1 O 2'd2 oe=0, ie=0 oe=0, ie=1

**40** U0RXD VDD3P3_CPU U0RXD I1 CLK_OUT2 O GPIO3 I/O/T 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**41** U0TXD VDD3P3_CPU U0TXD O CLK_OUT3 O GPIO1 I/O/T EMAC_RXD2 I 2'd2 oe=0, ie=1, wpu oe=0, ie=1, wpu

**42** GPIO21 VDD3P3_CPU GPIO21 I/O/T VSPIHD I/O/T GPIO21 I/O/T EMAC_TX_EN O 2'd2 oe=0, ie=0 oe=0, ie=1

**43** VDDA VDDA supply in

**44** XTAL_N VDDA

**45** XTAL_P VDDA

**46** VDDA VDDA supply in

**47** CAP2 VDDA

**48** CAP1 VDDA

**Total Number** 8 14 26

**Notes:**

 - wpu: weak pull-up;

 - wpd: weak pull-down;

 - ie: input enable;

 - oe: output enable;

 - Please see _Table: Notes on ESP32 Pin Lists_ for more information.（请参考表：管脚清单说明。）


_Revision History_

##### Revision History


Date Version Release notes


Section 4.8.3 Universal Asynchronous Receiver Transmitter (UART) and 4.8.4
2026.07 v5.3

I2C Interface: Fixed typos


_•_ ESP32-D0WDR2-V3 is end of life and upgraded to ESP32-D0WDRH2-V3
2025.11 v5.2

_•_ Table 1-1 Comparison: Updated ”Ordering Code” to ”Part Number”


_•_ Section 4.8.3 Universal Asynchronous Receiver Transmitter (UART): Added


description ”Programmable baud rates up to 5 MBaud”


2025.10 v5.1


2025.08 v5.0


2025.04 v4.9


2025.01 v4.8


2024.09 v4.7


_•_ Section 3 Boot Configurations: Fixed the typo about Internal LDO (VDD_SDIO)


Voltage Control

_•_ Fixed other typos


_•_ Table 2-3 Power Pins: Added power pin 1 VDDA

_•_ Updated Figure 3-1 Visualization of Timing Parameters for the Strapping Pins

_•_ Table 5-3 DC Characteristics (3.3 V, 25 °C): Added V _IH_ _ _nRST_


_•_ Section CPU and Memory: Improved CoreMark scores

_•_ Section 3.1 Chip Boot Mode Control: Modified the description from ”valid only


for ESP32 ECO V3” to ”valid only for ESP32 chip revisions v3.0 and higher”

_•_ Section 4.8.2 Serial Peripheral Interface (SPI): Added information about SPI

_•_ Table 2-2 Analog Pins: Fixed typos about pin numbers


_•_ Section 3 Boot Configurations: Fixed the typo about JTAG signal source


control

_•_ Section 2.2 Pin Overview: Added a note about JTAG interface signals

_•_ Table 2-5 Pin Mapping Between Chip and Flash/PSRAM: Modified a note


about VDD_SDIO


_•_ Table 5-2 Recommended Power Supply Characteristics: Deleted a note about


VDD3P3_RTC limitation

_•_ Section 4.1.1 CPU: Fixed the link to Cadence Xtensa ISA Summary

_•_ Section 4.8.7 Pulse Counter Controller (PCNT): Fixed the typo in the Feature


List


Cont’d on next page


Espressif Systems 70
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


_Revision History_


Date Version Release notes


Cont’d from previous page


2024.08 v4.6


Improved the formatting, structure, and wording in the following sections:

_•_ Section 2 Pins

_•_ Section 3 Boot Configurations (used to be named as ”Strapping Pins”)

_•_ Section 4 Functional Description


Section 2.5.3 Chip Power-up and Reset: Updated the link to the VDD_SDIO 1.8 V
2024.02 v4.5

circuit design to ESP32 Hardware Design Guidelines


2023.12 v4.4 Table 1-1 Comparison: Added information about fash under the table


_•_ Updated formatting throughout the document


2023.07 v4.3


2023.01 v4.2


2022.12 v4.1


2022.10 v4.0


_•_ Updated wording in some sections

_•_ Added a new section 2.3.1 Restrictions for GPIOs and RTC_GPIOs

_•_ Added a new section 4.1.5 Cache


_•_ [Removed contents about hall sensor according to PCN20221202](https://www.espressif.com/sites/default/files/pcn_downloads/PCN20221202%20Remove%20Hall%20Sensor%20from%20ESP32%20Series%20of%20Documentation.pdf)

_•_ Section 4.9.3 Touch Sensor: Added a note about limited applications of touch


sensor


_•_ Section 4.1.1 CPU: Added link to

Xtensa [®] Instruction Set Architecture (ISA) Summary

_•_ Table 1-1 Comparison: Updated the description about chip revision upgrade


_•_ Section Product Overview: Updated the description

_•_ Table 2-6 Pin Mapping Between Chip and Flash/PSRAM: Added two notes


below the table

_•_ Section 2.5.2 Power Scheme: Added a new item to “Notes on power supply”

_•_ Updated Figure 1-1 ESP32 Series Nomenclature

_•_ Table 1-1 Comparison: Added a new column “VDD_SDIO Voltage”

_•_ Section 4.8.12 TWAI [®] Controller: Updated the bit rates

_•_ [Added Not Recommended for New Designs (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd) label to ESP32-S0WD


Cont’d on next page


Espressif Systems 71
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


_Revision History_


Date Version Release notes


Cont’d from previous page


2022.03 v3.9


2021.10 v3.8


2021.07 v3.7


2021.03 V3.6


_•_ Added a new chip variant ESP32-D0WDR2-V3

_•_ Added Table 2-5 Pin Mapping Between Chip and Flash/PSRAM and Table 2-6


Pin Mapping Between Chip and Flash/PSRAM

_•_ Updated Figure 6-2 QFN48 (5×5 mm) Package

_•_ Updated Appendix IO_MUX

_•_ Updated Table 4-6 Peripheral Pin Configurations

_•_ Section 3.1 Chip Boot Mode Control: Added links to _ESP32 Technical_


_Reference Manual_


_•_ Upgraded ESP32-U4WDH variant from single-core to dual-core, see


[PCN-2021-021.](https://www.espressif.com/sites/default/files/pcn_downloads/PCN-2021-021%20ESP32-U4WDH%20%E5%8D%87%E7%BA%A7%E4%B8%BA%E5%8F%8C%E6%A0%B8%E5%A4%84%E7%90%86%E5%99%A8%E4%BA%A7%E5%93%81.pdf) The single-core version coexists with the new dual-core


version around December 2, 2021. The physical product is subject to batch


tracking.

_•_ Section CPU and Memory: Added CoreMark [®] score

_•_ Section 4.8.12 TWAI [®] Controller: Updated the description

_•_ [Added Not Recommended for New Designs (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd) label to the


ESP32-D0WDQ6-V3 variant

_•_ Section 6 Packaging: Provided a link to _[Espressif Chip Package Information](https://www.espressif.com/sites/default/files/documentation/Espressif%27s_Chip-Packing_Information__EN.pdf)_

_•_ Updated Section Bluetooth


_•_ Removed ESP32-D2WD variant

_•_ Section 4.7.1 Bluetooth Radio and Baseband: Updated wording

_•_ Updated pin function numbers starting from Function0

_•_ [Added Not Recommended for New Designs (NRND)](https://www.espressif.com/en/products/longevity-commitment?id=nrnd) label to ESP32-D0WD and


ESP32-D0WDQ6 variants


_•_ Updated Figure Block Diagram

_•_ Updated Table 5-5 Reliability

_•_ Updated Figure 2-3 ESP32 Power Scheme

_•_ Updated Table 5-2 Recommended Power Supply Characteristics

_•_ Updated the notes below Table 2-4 Description of Timing Parameters for


Power-up and Reset

_•_ Table 4-1, 4-6, Section 4.8.12 TWAI [®] Controller: Added more information about


TWAI®


Cont’d on next page


Espressif Systems 72
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


_Revision History_


Date Version Release notes


Cont’d from previous page


2021.01 V3.5


2020.04 V3.4


_•_ Table 2-1 Pin Overview: Updated the description for CAP2 from 3 nF to 3.3 nF

_•_ Section Advanced Peripheral Interfaces: Added TWAI [®]

_•_ Updated Figure Block Diagram

_•_ Appendix IO_MUX: Updated the reset values for MTCK, MTMS, GPIO27


_•_ Added one chip variant: ESP32-U4WDH

_•_ Updated some figures in Table 4-2, 5-6, 5-7, 5-9, 5-11, 5-12

_•_ Table 5-7 Receiver –Basic Data Rate: Added a note under the table


_•_ Added two chip variants: ESP32-D0WD-V3 and ESP32-D0WDQ6-V3.
2020.01 V3.3

_•_ Added a note under Table 4-3 Analog-to-Digital Converter (ADC)


2019.10 V3.2 _•_ Updated Figure 2-4 Visualization of Timing Parameters for Power-up and Reset


_•_ Table 2-1 Pin Overview: Added pin-pin mapping between ESP32-D2WD and


2019.07 V3.1


the in-package flash under the table

_•_ Updated Figure 1-1 ESP32 Series Nomenclature


_•_ Section 3 Boot Configurations (used to be named as ”Strapping Pins”): Added
2019.04 V3.0

information about the setup and hold times for the strapping pins


2019.02 V2.9


2019.01 V2.8


_•_ Table 2-1 Pin Overview: Applied new formatting

_•_ Table 4-6 Peripheral Pin Configurations: Fixed typos with respect to the ADC1


channel mappings


_•_ Changed the RF power control range in Table 5-7, 5-10, and 5-12 from –12 ~

+12 to –12 ~ +9 dBm;

_•_ Small text changes


_•_ Updated Section Applications
2018.11 V2.7

_•_ Table IO_MUX: Updated pin statuses at reset and after reset


Espressif Systems 73
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


Cont’d on next page


ESP32 Series Datasheet v5.3


_Revision History_


Date Version Release notes


Cont’d from previous page


2018.10 V2.6 _•_ Section 6 Packaging: Updated QFN package drawings


_•_ Table 5-1 Absolute Maximum Ratings: Added ”Cumulative IO output current”


2018.08 V2.5


2018.07 V2.4


_•_ Table 5-3 DC Characteristics (3.3 V, 25 °C): Added more parameters

_•_ Appendix IO_MUX: Changed the power domain names to be consistent with


the pin names


_•_ Deleted information on Packet Traffic Arbitration (PTA);

_•_ Added Figure 2-4 Visualization of Timing Parameters for Power-up and Reset

_•_ Table 4-2 Power Management Unit (PMU): Added the current consumption


figures for dual-core SoCs

_•_ Updated Section 4.9.1 Analog-to-Digital Converter (ADC)


_•_ Table 4-2 Power Management Unit (PMU): Added the current consumption
2018.06 V2.3

figures at CPU frequency of 160 MHz


2018.05 V2.2


_•_ Table 2-1 Pin Overview: Changed the voltage range of VDD3P3_RTC from


1.8-3.6 V to 2.3-3.6 V

_•_ Updated Section 2.5.2 Power Scheme

_•_ Updated Section 4.1.3 External Flash and RAM

_•_ Updated Table 4-2 Power Management Unit (PMU)

_•_ Removed content about temperature sensor;


Changes to electrical characteristics:

_•_ Updated Table 5-1 Absolute Maximum Ratings

_•_ Added Table 5-2 Recommended Power Supply Characteristics

_•_ Added Table 5-3 DC Characteristics (3.3 V, 25 °C)

_•_ Added Table 5-5 Reliability

_•_ Table 5-7 Receiver –Basic Data Rate: Updated the values of ”Gain control step”


and ”Adjacent channel transmit power”

_•_ Table 5-10 Transmitter –Enhanced Data Rate: Updated the values of ”Gain


control step”, ” _π_ /4 DQPSK modulation accuracy”, ”8 DPSK modulation


accuracy”, and ”In-band spurious emissions”

_•_ Table 5-12 Transmitter: Updated the values of ”Gain control step” and


”Adjacent channel transmit power”


Cont’d on next page


Espressif Systems 74
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


_Revision History_


Date Version Release notes


Cont’d from previous page


2018.01 V2.1


_•_ Deleted software-specific features;

_•_ Deleted information on LNA pre-amplifier;

_•_ Specified the CPU speed and flash speed of ESP32-D2WD;

_•_ Section 2.5.2 Power Scheme: Added notes


2017.12 V2.0 _•_ Section 6 Packaging: Added a note on the sequence of pin number


_•_ Table 2-1 Pin Overview: Updated the description of pin CHIP_PU

_•_ Section 2.5.2 Power Scheme: Added a note

_•_ Section 3 Boot Configurations (used to be named as ”Strapping Pins”):


2017.10 V1.9


Updated the description of the chip’s system reset

_•_ Section 4.6.4 Wi-Fi Radio and Baseband: Added a description of antenna


diversity and selection

_•_ Table 4-2 Power Management Unit (PMU): Deleted ”Association sleep pattern”,


added notes to Active sleep and Modem-sleep


_•_ Added Table 4-6 Peripheral Pin Configurations
2017.08 V1.8

_•_ Figure Block Diagram: Corrected a typo


Espressif Systems 75
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


Cont’d on next page


ESP32 Series Datasheet v5.3


_Revision History_


Date Version Release notes


Cont’d from previous page


2017.08 V1.7


2017.06 V1.6


2017.06 V1.5


_•_ Section Bluetooth: Changed the transmitting power to +12 dBm; the sensitivity

of NZIF receiver to –97 dBm

_•_ Table 2-1 Pin Overview: Added a note

_•_ section 4.1.1 CPU: Added 160 MHz clock frequency

_•_ Section 4.6.4 Wi-Fi Radio and Baseband: Changed the transmitting power


from 21 dBm to 20.5 dBm

_•_ Section 4.7.1 Bluetooth Radio and Baseband: Changed the dynamic control


range of class-1, class-2 and class-3 transmit output powers to ”up to 24


dBm”; changed the dynamic range of NZIF receiver sensitivity to ”over 97 dB”

_•_ Table 4-2 Power Management Unit (PMU): Added two notes

_•_ Updated Section 4.8.1 General Purpose Input / Output Interface (GPIO)

_•_ Updated Section 4.8.11 SDIO/SPI Slave Controller

_•_ Updated Table 5-1 Absolute Maximum Ratings

_•_ Table 5.4 RF Current Consumption in Active Mode: Changed the duty cycle on

which the transmitters’measurements are based to 50%.

_•_ Table 5-6 Wi-Fi Radio: Added a note on “Output impedance”

_•_ Table 5-7, 5-9, 5-11: Updated parameter ”Sensitivity”

_•_ Table 5-7, 5-10, 5-12: Updated parameters ”RF transmit power” and ”RF power


control range”; added parameter ”Gain control step”

_•_ Deleted Chapters: ”Touch Sensor” and ”Code Examples”;

_•_ [Added a link to certifcation download.](http://espressif.com/en/certificates)


_•_ Section Complete Integration Solution: Changed the number of external


components to 20

_•_ Section 4.8.1 General Purpose Input / Output Interface (GPIO): Changed the


number of GPIO pins to 34


_•_ Section CPU and Memory: Changed the power supply range

_•_ Section 2.5.2 Power Scheme: Updated the note

_•_ Updated Table 5-1 Absolute Maximum Ratings

_•_ Table Notes on ESP32 Pin Lists: Changed the drive strength values of the


digital output pins in Note 8

_•_ Added the option to subscribe for notifications of documentation changes


Cont’d on next page


Espressif Systems 76
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


_Revision History_


Date Version Release notes


Cont’d from previous page


2017.05 V1.4


2017.04 V1.3


_•_ Section Clocks and Timers: Added a note to the frequency of the external


crystal oscillator

_•_ Section 3 Boot Configurations (used to be named as ”Strapping Pins”): Added


a note

_•_ Updated Section 4.3 RTC and Low-power Management

_•_ Table 5-1 Absolute Maximum Ratings: Changed the maximum driving capability


from 12 mA to 80 mA

_•_ Table 5-6 Wi-Fi Radio: Changed the input impedance value of 50Ω to output


impedance value of 30+j10 Ω

_•_ Table Notes on ESP32 Pin Lists: Added a note to No.8

_•_ Table IO_MUX: Deleted GPIO20


_•_ Added Appendix Notes on ESP32 Pin Lists

_•_ Updated Table 5-6 Wi-Fi Radio

_•_ Updated Figure 2-2 ESP32 Pin Layout (QFN 5*5, Top View)


_•_ Table 2-1 Pin Overview: Added a note
2017.03 V1.2

_•_ Section 4.1.2 Internal Memory: Updated the note


2017.02 V1.1


_•_ Added Section 1 ESP32 Series Comparison

_•_ Updated Section MCU and Advanced Features

_•_ Updated Section Block Diagram

_•_ Updated Section 2 Pins

_•_ Updated Section CPU and Memory

_•_ Updated Section 4.2.3 Audio PLL Clock

_•_ Updated Section 5.1 Absolute Maximum Ratings

_•_ Updated Section 6 Packaging

_•_ Updated Section Related Documentation and Resources


2016.08 V1.0 First release.


Espressif Systems 77
[Submit Documentation Feedback](https://www.espressif.com/en/company/documents/documentation_feedback?docId=4033&sections=&version=5.3)


ESP32 Series Datasheet v5.3


Disclaimer and Copyright Notice


Information in this document, including URL references, is subject to change without notice.


ALL THIRD PARTY’S INFORMATION IN THIS DOCUMENT IS PROVIDED AS IS WITH NO WARRANTIES TO ITS AUTHENTICITY AND
ACCURACY.


NO WARRANTY IS PROVIDED TO THIS DOCUMENT FOR ITS MERCHANTABILITY, NON-INFRINGEMENT, FITNESS FOR ANY PARTICULAR
PURPOSE, NOR DOES ANY WARRANTY OTHERWISE ARISING OUT OF ANY PROPOSAL, SPECIFICATION OR SAMPLE.


All liability, including liability for infringement of any proprietary rights, relating to use of information in this document is disclaimed. No
licenses express or implied, by estoppel or otherwise, to any intellectual property rights are granted herein.


The Wi-Fi Alliance Member logo is a trademark of the Wi-Fi Alliance. The Bluetooth logo is a registered trademark of Bluetooth SIG.


All trade names, trademarks and registered trademarks mentioned in this document are property of their respective owners, and are
hereby acknowledged.


Copyright © 2026 Espressif Systems (Shanghai) Co., Ltd. All rights reserved.


[w.espressif.com](https://www.espressif.com/)

