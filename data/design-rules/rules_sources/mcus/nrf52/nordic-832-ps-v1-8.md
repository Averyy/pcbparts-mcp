Source: https://www.mouser.com/datasheet/2/297/nRF52832_PS_v1_8-2942485.pdf
Retrieved: 2026-11-09

[PDF: 560 pages.]

# **nRF52832 Product Specification v1.8**

**Key features** **Applications**

- 2.4 GHz transceiver - Internet of Things (IoT)


  - -96 dBm sensitivity in _Bluetooth_ _[®]_ low energy mode

  - Supported data rates: 1 Mbps, 2 Mbps _Bluetooth_ ® low energy mode

  - -20 to +4 dBm TX power, configurable in 4 dB steps

  - On-chip balun (single-ended RF)

  - 5.3 mA peak current in TX (0 dBm)

  - 5.4 mA peak current in RX

  - RSSI (1 dB resolution)

- Arm [®] Cortex [®] -M4 32-bit processor with FPU, 64 MHz

  - 215 EEMBC CoreMark [®] score running from flash memory

  - 58 μA/MHz running from flash memory

  - 51.6 μA/MHz running from RAM

  - Data watchpoint and trace (DWT), embedded trace macrocell (ETM), and
instrumentation trace macrocell (ITM)

  - Serial wire debug (SWD)

  - Trace port

- Flexible power management

  - 1.7 V–3.6 V supply voltage range

  - Fully automatic LDO and DC/DC regulator system

  - Fast wake-up using 64 MHz internal oscillator

  - 0.3 μA at 3 V in System OFF mode

  - 0.7 μA at 3 V in System OFF mode with full 64 kB RAM retention

  - 1.9 μA at 3 V in System ON mode, no RAM retention, wake on RTC

- Memory

  - 512 kB flash/64 kB RAM

  - 256 kB flash/32 kB RAM

- Nordic SoftDevice ready

- Support for concurrent multi-protocol

- Type 2 near field communication (NFC-A) tag with wakeup-on-field and touchto-pair capabilities

- 12-bit, 200 ksps ADC - 8 configurable channels with programmable gain

- 64 level comparator

- 15 level low power comparator with wakeup from System OFF mode

- Temperature sensor

- 32 general purpose I/O pins

- 3x 4-channel pulse width modulator (PWM) unit with EasyDMA

- Digital microphone interface (PDM)

- 5x 32-bit timer with counter mode

- Up to 3x SPI master/slave with EasyDMA

- Up to 2x I2C compatible 2-wire master/slave

- I2S with EasyDMA

- UART (CTS/RTS) with EasyDMA

- Programmable peripheral interconnect (PPI)

- Quadrature decoder (QDEC)

- AES HW encryption with EasyDMA

- Autonomous peripheral operation without CPU intervention using PPI and
EasyDMA

- 3x real-time counter (RTC)

- Single crystal operation

- Package variants

  - QFN48 package, 6 × 6 mm

  - WLCSP package, 3.0 × 3.2 mm


- Home automation

- Sensor networks

- Building automation

- Industrial

- Retail

Personal area networks

- Health/fitness sensor and monitor devices

- Medical devices

- Key fobs and wrist watches

Interactive entertainment devices

- Remote controls

- Gaming controllers

Beacons

A4WP wireless chargers and devices

Remote control toys

Computer peripherals and I/O devices

- Mouse

- Keyboard

- Multi-touch trackpad

- Gaming


All rights reserved.
Reproduction in whole or in part is prohibited without the prior written permission of the copyright holder.
2021-11-01


Contents

## **Contents**

###### **1 Revision history... 9**

**2 About this document... 11**
2.1 Document naming and status...11
2.2 Peripheral naming and abbreviations... 11
2.3 Register tables... 11
2.4 Registers... 12
**3 Block diagram...13**
**4 Pin assignments... 14**
4.1 QFN48 pin assignments... 14
4.2 WLCSP ball assignments... 16
4.3 GPIO usage restrictions...18
**5 Absolute maximum ratings... 20**
**6 Recommended operating conditions... 21**
6.1 WLCSP light sensitivity...21
**7 CPU... 22**
7.1 Floating point interrupt... 22
7.2 Electrical specification...22
7.3 CPU and support module configuration...23
**8 Memory... 24**
8.1 RAM - Random access memory...24
8.2 Flash - Non-volatile memory...25
8.3 Memory map... 25
8.4 Instantiation... 25
**9 AHB multilayer...27**
9.1 AHB multilayer priorities...27
**10 EasyDMA... 28**
10.1 EasyDMA array list... 29
**11 NVMC — Non-volatile memory controller...30**
11.1 Writing to Flash...30
11.2 Erasing a page in Flash... 30
11.3 Writing to user information configuration registers (UICR)... 30
11.4 Erasing user information configuration registers (UICR)... 30
11.5 Erase all... 31
11.6 Cache... 31
11.7 Registers... 31
11.8 Electrical specification...34
**12 BPROT — Block protection...35**
12.1 Registers... 35
**13 FICR — Factory information configuration registers...44**
13.1 Registers... 44
**14 UICR — User information configuration registers... 55**
14.1 Registers... 55
**15 Peripheral interface... 69**
15.1 Peripheral ID... 69
15.2 Peripherals with shared ID...69
15.3 Peripheral registers... 70
15.4 Bit set and clear...70
15.5 Tasks...70
15.6 Events...71


**Page 2**


Contents


15.7 Shortcuts... 71
15.8 Interrupts... 71
**16 Debug and trace... 73**
16.1 DAP - Debug access port...73
16.2 Access port protection... 73
16.3 CTRL-AP - Control access port...76
16.4 Debug Interface mode... 77
16.5 Real-time debug...78
16.6 Trace... 78
**17 Power and clock management...79**
17.1 Current consumption scenarios... 79
**18 POWER — Power supply...81**
18.1 Regulators... 81
18.2 System OFF mode...82
18.3 System ON mode... 83
18.4 Power supply supervisor...83
18.5 RAM sections...85
18.6 Reset... 85
18.7 Retained registers... 86
18.8 Reset behavior... 86
18.9 Registers... 86
18.10 Electrical specification...102
**19 CLOCK — Clock control...104**
19.1 HFCLK clock controller... 104
19.2 LFCLK clock controller...106
19.3 Registers... 108
19.4 Electrical specification...112
**20 GPIO — General purpose input/output... 114**
20.1 Pin configuration... 114
20.2 GPIO located near the RADIO... 116
20.3 Registers... 116
20.4 Electrical specification...157
**21 GPIOTE — GPIO tasks and events...161**
21.1 Pin events and tasks... 161
21.2 Port event...162
21.3 Tasks and events pin configuration... 162
21.4 Registers... 162
21.5 Electrical specification...171
**22 PPI — Programmable peripheral interconnect...172**
22.1 Pre-programmed channels...173
22.2 Registers... 173
**23 RADIO — 2.4 GHz Radio... 209**
23.1 EasyDMA...209
23.2 Packet configuration...210
23.3 Maximum packet length...211
23.4 Address configuration...211
23.5 Data whitening... 211
23.6 CRC...212
23.7 Radio states... 213
23.8 Transmit sequence...213
23.9 Receive sequence...215
23.10 Received Signal Strength Indicator (RSSI)...216
23.11 Interframe spacing...216
23.12 Device address match... 217
23.13 Bit counter...217
23.14 Registers... 218
23.15 Electrical specification...234


**Page 3**


Contents


**24 TIMER — Timer/counter...238**
24.1 Capture...239
24.2 Compare...239
24.3 Task delays...239
24.4 Task priority...239
24.5 Registers... 239
24.6 Electrical specification...245
**25 RTC — Real-time counter...246**
25.1 Clock source... 246
25.2 Resolution versus overflow and the PRESCALER... 246
25.3 COUNTER register...247
25.4 Overflow features... 247
25.5 TICK event... 247
25.6 Event control feature...248
25.7 Compare feature... 248
25.8 TASK and EVENT jitter/delay...250
25.9 Reading the COUNTER register...252
25.10 Registers... 252
25.11 Electrical specification...258
**26 RNG — Random number generator... 259**
26.1 Bias correction... 259
26.2 Speed... 259
26.3 Registers... 259
26.4 Electrical specification...261
**27 TEMP — Temperature sensor... 262**
27.1 Registers... 262
27.2 Electrical specification...267
**28 ECB — AES electronic codebook mode encryption...268**
28.1 Shared resources...268
28.2 EasyDMA...268
28.3 ECB data structure...268
28.4 Registers... 269
28.5 Electrical specification...270
**29 CCM — AES CCM mode encryption...271**
29.1 Shared resources...272
29.2 Encryption...272
29.3 Decryption... 272
29.4 AES CCM and RADIO concurrent operation...273
29.5 Encrypting packets on-the-fly in radio transmit mode...273
29.6 Decrypting packets on-the-fly in radio receive mode...274
29.7 CCM data structure...275
29.8 EasyDMA and ERROR event...276
29.9 Registers... 276
**30 AAR — Accelerated address resolver...280**
30.1 Shared resources...280
30.2 EasyDMA...280
30.3 Resolving a resolvable address...280
30.4 Use case example for chaining RADIO packet reception with address resolution using
AAR...281
30.5 IRK data structure...281
30.6 Registers... 282
30.7 Electrical specification...284
**31 SPIM — Serial peripheral interface master with EasyDMA...285**
31.1 Shared resources...285
31.2 EasyDMA...286
31.3 SPI master transaction sequence...287
31.4 Low power...288


**Page 4**


Contents


31.5 Master mode pin configuration... 288
31.6 Registers... 289
31.7 Electrical specification...294
**32 SPIS — Serial peripheral interface slave with EasyDMA...296**
32.1 Shared resources...296
32.2 EasyDMA...296
32.3 SPI slave operation...297
32.4 Pin configuration... 298
32.5 Registers... 299
32.6 Electrical specification...307
**33 TWIM — I** **[2]** **C compatible two-wire interface master with EasyDMA...309**
33.1 Shared resources...310
33.2 EasyDMA...310
33.3 Master write sequence...311
33.4 Master read sequence... 312
33.5 Master repeated start sequence... 313
33.6 Low power...314
33.7 Master mode pin configuration... 314
33.8 Registers... 314
33.9 Electrical specification...321
**34 TWIS — I** **[2]** **C compatible two-wire interface slave with EasyDMA...323**
34.1 Shared resources...325
34.2 EasyDMA...325
34.3 TWI slave responding to a read command...325
34.4 TWI slave responding to a write command... 326
34.5 Master repeated start sequence... 327
34.6 Terminating an ongoing TWI transaction...328
34.7 Low power...328
34.8 Slave mode pin configuration... 328
34.9 Registers... 329
34.10 Electrical specification...335
**35 UARTE — Universal asynchronous receiver/transmitter with EasyDMA... 337**
35.1 Shared resources...337
35.2 EasyDMA...337
35.3 Transmission... 338
35.4 Reception... 338
35.5 Error conditions... 340
35.6 Using the UARTE without flow control... 340
35.7 Parity configuration...340
35.8 Low power...340
35.9 Pin configuration... 341
35.10 Registers... 341
35.11 Electrical specification...349
**36 QDEC — Quadrature decoder...351**
36.1 Sampling and decoding... 351
36.2 LED output... 352
36.3 Debounce filters... 352
36.4 Accumulators...353
36.5 Output/input pins... 353
36.6 Pin configuration... 353
36.7 Registers... 354
36.8 Electrical specification...360
**37 SAADC — Successive approximation analog-to-digital converter...361**
37.1 Shared resources...361
37.2 Overview...361
37.3 Digital output... 362
37.4 Analog inputs and channels...363


**Page 5**


Contents


37.5 Operation modes...363
37.6 EasyDMA...365
37.7 Resistor ladder... 366
37.8 Reference...367
37.9 Acquisition time... 367
37.10 Limits event monitoring...368
37.11 Registers... 369
37.12 Electrical specification...393
37.13 Performance factors...395
**38 COMP — Comparator...396**
38.1 Differential mode... 397
38.2 Single-ended mode... 398
38.3 Registers... 400
38.4 Electrical specification...405
**39 LPCOMP — Low power comparator...406**
39.1 Shared resources...407
39.2 Pin configuration... 407
39.3 Registers... 408
39.4 Electrical specification...412
**40 WDT — Watchdog timer... 413**
40.1 Reload criteria... 413
40.2 Temporarily pausing the watchdog...413
40.3 Watchdog reset... 413
40.4 Registers... 414
40.5 Electrical specification...418
**41 SWI — Software interrupts...419**
41.1 Registers... 419
**42 NFCT — Near field communication tag...420**
42.1 Overview...420
42.2 Pin configuration... 422
42.3 EasyDMA...422
42.4 Collision resolution... 423
42.5 Frame timing controller... 424
42.6 Frame assembler... 425
42.7 Frame disassembler...426
42.8 Antenna interface... 427
42.9 NFCT antenna recommendations...427
42.10 Battery protection... 427
42.11 References... 428
42.12 Registers... 428
42.13 Electrical specification...439
**43 PDM — Pulse density modulation interface... 440**
43.1 Master clock generator... 440
43.2 Module operation... 440
43.3 Decimation filter... 441
43.4 EasyDMA...441
43.5 Hardware example... 442
43.6 Pin configuration... 442
43.7 Registers... 443
43.8 Electrical specification...447
**44 I** **[2]** **S — Inter-IC sound interface... 449**
44.1 Mode...449
44.2 Transmitting and receiving...449
44.3 Left right clock (LRCK)... 450
44.4 Serial clock (SCK)...450
44.5 Master clock (MCK)... 451
44.6 Width, alignment and format...451


**Page 6**


Contents


44.7 EasyDMA...453
44.8 Module operation... 455
44.9 Pin configuration... 456
44.10 Registers... 457
44.11 Electrical specification...464
**45 MWU — Memory watch unit...465**
45.1 Registers... 465
**46 EGU — Event generator unit...492**
46.1 Registers... 492
46.2 Electrical specification...498
**47 PWM — Pulse width modulation... 499**
47.1 Wave counter... 499
47.2 Decoder with EasyDMA...502
47.3 Limitations... 507
47.4 Pin configuration... 507
47.5 Registers... 508
47.6 Electrical specification...516
**48 SPI — Serial peripheral interface master...517**
48.1 Functional description... 517
48.2 Registers... 520
48.3 Electrical specification...523
**49 TWI — I** **[2]** **C compatible two-wire interface... 525**
49.1 Functional description... 525
49.2 Master mode pin configuration... 525
49.3 Shared resources...526
49.4 Master write sequence...526
49.5 Master read sequence... 527
49.6 Master repeated start sequence... 528
49.7 Low power...529
49.8 Registers... 529
49.9 Electrical specification...533
**50 UART — Universal asynchronous receiver/transmitter...535**
50.1 Functional description... 535
50.2 Pin configuration... 535
50.3 Shared resources...536
50.4 Transmission... 536
50.5 Reception... 536
50.6 Suspending the UART... 537
50.7 Error conditions... 537
50.8 Using the UART without flow control...538
50.9 Parity configuration...538
50.10 Registers... 538
50.11 Electrical specification...543
**51 Mechanical specifications... 544**
51.1 QFN48 6 x 6 mm package... 544
51.2 WLCSP package...545
**52 Ordering information...546**
52.1 IC marking...546
52.2 Box labels...546
52.3 Order code... 547
52.4 Code ranges and values...547
52.5 Product options... 548
**53 Reference circuitry... 550**
53.1 Schematic QFAA and QFAB QFN48 with internal LDO setup... 550
53.2 Schematic QFAA and QFAB QFN48 with DC/DC regulator setup... 551
53.3 Schematic QFAA and QFAB QFN48 with DC/DC regulator and NFC setup... 552
53.4 Schematic CIAA WLCSP with internal LDO setup... 553


**Page 7**


Contents


53.5 Schematic CIAA WLCSP with DC/DC regulator setup...554
53.6 Schematic CIAA WLCSP with DC/DC regulator and NFC setup...555
53.7 PCB guidelines...555
53.8 PCB layout example... 556
**54 Legal notices...558**


**Page 8**


1 Revision history

#### **1 Revision history**


**Date** **Version** **Description**
November 2021 1.8 The following content has been added or updated:

- _Ordering information_ on page 546 - Build codes
Fxx not recommended for new designs.
August 2021 1.7 The following content has been added or updated:

- _Pin assignments_ on page 14 - Added
description of standard drive and low frequency I/
O

- _FICR — Factory information configuration registers_
on page 44 - Updated INFO.VARIANT register
April 2021 1.6 The following content has been added or updated:

- _Debug and trace_ on page 73 - Updated
disabling access port protection description.

- _FICR — Factory information configuration registers_
on page 44 - Updated INFO.VARIANT register.

- _GPIO — General purpose input/output_ on page
114 - Updated electrical specification.

- _SPIS — Serial peripheral interface slave with_
_EasyDMA_ on page 296 - Updated SPIS electrical
parameters tSPIS,VSO, tSPIS,HSO, tSPIS,SUSI, and tSPIS,HSI.
March 2021 1.5 The following content has been added or updated:

- _Absolute maximum ratings_ on page 20 Increased Flash memory retention to 10 years at
85 °C.

- _UICR — User information configuration registers_
on page 55 - Added value HwDisabled to
APPROTECT register.

- _Debug and trace_ on page 73 - Added
description of APPROTECT functionality for devices
where APPROTECT is controlled by hardware
and software. Added peripheral APPROTECT
with necessary registers to control APPROTECT
for devices where APPROTECT is controlled by
hardware and software.

- _Ordering information_ on page 546 - Added new
product options.
October 2017 1.4 The following content has been added or updated:

- _Recommended operating conditions_ on page
21 - Added WLCSP light sensitivity information.

- _FICR — Factory information configuration registers_
on page 44 - Added registers PARTNO,
HWREVISION and PRODUCTIONREVISION.

- _UICR — User information configuration registers_
on page 55 - Changed width of PSELRESETn
port fields.

- _SPIM_                                               - Polarity in SPI mode table corrected.

- _COMP — Comparator_ on page 396 Documentation structure improvements/changes.

- Liability disclaimer updated - Directive 2011/65/
EU (RoHS 2).
February 2017 1.3 The following content has been added or updated:

- _RADIO — 2.4 GHz Radio_ on page 209 Introduced 2 Mbps Bluetooth [®] low energy mode.

- _FICR — Factory information configuration registers_
on page 44 - Updated INFO.PACKAGE register
(new package added).

- _UARTE_                                               - Corrected the pin configuration table.

- _PPI — Programmable peripheral interconnect_ on
page 172 - Timing information corrected.

- Updated the liability disclaimer.
September 2016 1.2 Updated the following:

- Power and clock management, _Current_
_consumption: Ultra-low power_ on page 80.

- Power, _Current consumption, sleep_ on page
102
July 2016 1.1 Added documentation for nRF52832 CIAA WLCSP.

Added or updated the following content:

- Cover - Added _Key features_ .


**Page 9**


1 Revision history


**Date** **Version** **Description**

- _Pin assignments_ on page 14 - Added _WLCSP_
_ball assignments_ . Moved _GPIO usage restrictions_
here from _GPIO/Notes on usage and restrictions_ .

- _Absolute maximum ratings_ on page 20 - Added
environmental information for WLCSP to the
table.

- _Memory_ on page 24 - Added QFAB and CIAA
information to the table.

- _FICR — Factory information configuration registers_
on page 44 - Updated INFO.PACKAGE register.

- _UICR — User information configuration registers_
on page 55 - Updated APPROTECT register.

- _Debug and trace_ on page 73 - Updated _DAP -_
_Debug access port_ .

- _POWER — Power supply_ on page 81 - Updated
_Pin reset_ .

- _CLOCK — Clock control_ on page 104 - Updated
information on external 32 kHz clock support.

- _GPIO — General purpose input/output_ on page
114 - Added _GPIO located near the RADIO_ .

- _RADIO — 2.4 GHz Radio_ on page 209 - Updated
Figure 29 and _Interframe spacing_ .

- _CCM_                                               - Updated SCRATCHPTR register.

- _SPIM_                                               - Updated _Master mode pin configuration_ .

- _UARTE_                                               - Added RXDRDY and TXDRDY events.

- _NFCT_                                               - Updated _Electrical specifications_ .

- _PWM — Pulse width modulation_ on page 499 Updated SEQ[1].REFRESH register.

- _Mechanical specifications_ on page 544 - Added
_WLCSP package_ .

- _Ordering information_ on page 546 - Updated
with CIAA and QFAB information.

- _Reference circuitry_ on page 550 - QFAB
information added. CIAA WLCSP schematics
added.
February 2016 1.0 First release.


**Page 10**


2 About this document

#### **2 About this document**


This product specification is organized into chapters based on the modules and peripherals that are available
in this IC.

The peripheral descriptions are divided into separate sections that include the following information:

- A detailed functional description of the peripheral

- Register configuration for the peripheral

- Electrical specification tables, containing performance data which apply for the operating conditions
described in _Recommended operating conditions_ on page 21.

###### **2.1 Document naming and status**

Nordic uses three distinct names for this document, which are reflecting the maturity and the status of the
document and its content.


**Table 1: Defined document names**


**Document name** **Description**
Objective Product Specification (OPS) Applies to document versions up to 0.7.

This product specification contains target specifications for product development.
Preliminary Product Specification (PPS) Applies to document versions 0.7 and up to 1.0.

This product specification contains preliminary data. Supplementary data may be
published from Nordic Semiconductor ASA later.
Product Specification (PS) Applies to document versions 1.0 and higher.

This product specification contains final product specifications. Nordic
Semiconductor ASA reserves the right to make changes at any time without notice
in order to improve design and supply the best possible product.

###### **2.2 Peripheral naming and abbreviations**

Every peripheral has a unique capitalized name or an abbreviation of its name, e.g. TIMER, used for
identification and reference. This name is used in chapter headings and references, and it will appear in the
ARM [®] Cortex [®] Microcontroller Software Interface Standard (CMSIS) hardware abstraction layer to identify
the peripheral.

The peripheral instance name, which is different from the peripheral name, is constructed using the
peripheral name followed by a numbered postfix, starting with 0, for example, TIMER0. A postfix is normally
only used if a peripheral can be instantiated more than once. The peripheral instance name is also used in
the CMSIS to identify the peripheral instance.

###### **2.3 Register tables**

Individual registers are described using register tables. These tables are built up of two sections. The first
three colored rows describe the position and size of the different fields in the register. The following rows
describe the fields in more detail.


**2.3.1 Fields and values**
The **Id (Field Id)** row specifies the bits that belong to the different fields in the register. If a field has
enumerated values, then every value will be identified with a unique value id in the **Value Id** column.

A blank space means that the field is reserved and read as undefined, and it also must be written as `0` to
secure forward compatibility. If a register is divided into more than one field, a unique field name is specified
for each field in the **Field** column. The **Value Id** may be omitted in the single-bit bit fields when values can be
substituted with a Boolean type enumerator range, e.g. true/false, disable(d)/enable(d), on/off, and so on.


**Page 11**


2 About this document


Values are usually provided as decimal or hexadecimal. Hexadecimal values have a `0x` prefix, decimal
values have no prefix.

The **Value** column can be populated in the following ways:

- Individual enumerated values, for example 1, 3, 9.

- Range of values, e.g. [0..4], indicating all values from and including 0 and 4.

- Implicit values. If no values are indicated in the **Value** column, all bit combinations are supported, or
alternatively the field's translation and limitations are described in the text instead.

If two or more fields are closely related, the **Value Id**, **Value**, and **Description** may be omitted for all but the
first field. Subsequent fields will indicate inheritance with '..'.

A feature marked **Deprecated** should not be used for new designs.

###### **2.4 Registers**


**Table 2: Register Overview**


**Register** **Offset** **Description**

_DUMMY_ 0x514 Example of a register controlling a dummy feature


**2.4.1 DUMMY**

Address offset: 0x514

Example of a register controlling a dummy feature


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D D D D C C C B A A

**Reset 0x00050002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW FIELD_A Example of a field with several enumerated values

Disabled 0 The example feature is disabled

NormalMode 1 The example feature is enabled in normal mode

ExtendedMode 2 The example feature is enabled along with extra functionality

B RW FIELD_B Example of a deprecated field Deprecated

Disabled 0 The override feature is disabled

Enabled 1 The override feature is enabled

C RW FIELD_C Example of a field with a valid range of values

ValidRange [2..7] Example of allowed values for this field

D RW FIELD_D Example of a field with no restriction on the values


**Page 12**


3 Block diagram

#### **3 Block diagram**


This block diagram illustrates the overall system. Arrows with white heads indicate signals that share
physical pins with other signals.


nRF52832


RAM0 RAM1 RAM2


RAM3


RAM4 RAM5 RAM6 RAM7


TP TPIU


SWCLK

SWDIO


SW-DP


CTRL-AP


AHB-AP


ETM


CPU


AHB TO APB

BRIDGE


FICR


AHB
Multi-Layer


master


master


UICR


NVMC


RNG


RTC [0..2]


TIMER [0..4]


TEMP


ECB


EasyDMA


CCM


EasyDMA


GPIO P0
(P0.0 – P0.31)


I-Cache


Flash


SCK

MOSI

MISO


SCL

SDA


SCL

SDA


RTS

CTS

TXD

RXD


CSN


ARM
CORTEX-M4


NVIC


SysTick


nRESE ~~T~~ POWER


WDT


PPI


XC1


XC2

XL1

XL2


ANT2

ANT1


CLOCK


RADIO


EasyDMA master


AAR


master EasyDMA


SPIM [0..2]


NFC2

NFCT
NFC1


master


master


EasyDMA


TWIS [0..1]


EasyDMA


TWIM [0..1]


AIN0 – AIN7


EasyDMA master


GPIOTE


COMP


LPCOMP


SAADC


EasyDMA master master EasyDMA


master


master


LED


A QDEC
B
UARTE [0]


QDEC


OUT0 – OUT3 PWM[0..3]


EasyDMA master


MCK
LRCK


EasyDMA


SCL
SDOUT

SDIN


I2S


EasyDMA master


master


master


MISO

SPIS [0..2]
MOSI

SCK


EasyDMA


CLK

DIN PDM


**Figure 1: Block diagram**


EasyDMA master


**Page 13**


4 Pin assignments


#### **4 Pin assignments**

Here we cover the pin assignments for each variant of the chip.

###### **4.1 QFN48 pin assignments**


DEC1

P0.00/XL1

P0.01/XL2

P0.02/AIN0
P0.03/AIN1

P0.04/AIN2


nRF5102N52832


N52832


VDD

XC2
XC1

DEC3
DEC2
VSS
ANT

P0.24

P0.23
P0.22

SWDIO

SWDCLK


P0.05/AIN3 7 QFN48QFN48


P0.06


2

4

6

8

10

12


QFN48


P0.07

P0.08

NFC1/P0.09

NFC2/P0.10


exposed die pad


35

33

31

29

27

25


**Figure 2: QFN48 pin assignments, top view**


**Table 3: QFN48 pin assignments**


**Pin** **Name** **Type** **Description**

**Left Side of chip**

1 DEC1 Power 0.9 V regulator digital supply decoupling


2 P0.00


XL1

3 P0.01


XL2

4 P0.02


AIN0

5 P0.03


AIN1

6 P0.04


AIN2

7 P0.05


AIN3


Digital I/O


Analog input

Digital I/O


Analog input

Digital I/O


Analog input

Digital I/O


Analog input

Digital I/O


Analog input

Digital I/O


Analog input


General purpose I/O


Connection for 32.768 kHz crystal (LFXO)

General purpose I/O


Connection for 32.768 kHz crystal (LFXO)

General purpose I/O


SAADC/COMP/LPCOMP input

General purpose I/O


SAADC/COMP/LPCOMP input

General purpose I/O


SAADC/COMP/LPCOMP input

General purpose I/O


SAADC/COMP/LPCOMP input


8 P0.06 Digital I/O General purpose I/O

9 P0.07 Digital I/O General purpose I/O


**Page 14**


4 Pin assignments


**Pin** **Name** **Type** **Description**

10 P0.08 Digital I/O General purpose I/O


11 NFC1


P0.09

12 NFC2


P0.10

**Bottom side of chip**


NFC input


Digital I/O

NFC input


Digital I/O


NFC antenna connection


General purpose I/O [1]

NFC antenna connection


General purpose I/O [1]


13 VDD Power Power supply

14 P0.11 Digital I/O General purpose I/O

15 P0.12 Digital I/O General purpose I/O

16 P0.13 Digital I/O General purpose I/O


17 P0.14


TRACEDATA[3]

18 P0.15


TRACEDATA[2]

19 P0.16


TRACEDATA[1]


Digital I/O General purpose I/O


Trace port output

Digital I/O General purpose I/O


Trace port output

Digital I/O General purpose I/O


Trace port output


20 P0.17 Digital I/O General purpose I/O


21 P0.18


TRACEDATA[0] / SWO


Digital I/O General purpose I/O


Single wire output


Trace port output


22 P0.19 Digital I/O General purpose I/O


23 P0.20


TRACECLK

24 P0.21


nRESET

**Right Side of chip**


Digital I/O General purpose I/O


Trace port clock output

Digital I/O General purpose I/O


Configurable as pin reset


25 SWDCLK Digital input Serial wire debug clock input for debug

and programming

26 SWDIO Digital I/O Serial wire debug I/O for debug and

programming

27 P0.22 Digital I/O General purpose I/O [2]

28 P0.23 Digital I/O General purpose I/O [2]

29 P0.24 Digital I/O General purpose I/O [2]

30 ANT RF Single-ended radio antenna connection

31 VSS Power Ground (Radio supply)

32 DEC2 Power 1.3 V regulator supply decoupling (Radio

supply)

33 DEC3 Power Power supply decoupling

34 XC1 Analog input Connection for 32 MHz crystal

35 XC2 Analog input Connection for 32 MHz crystal

36 VDD Power Power supply

**Top side of chip**

37 P0.25 Digital I/O General purpose I/O [2]

38 P0.26 Digital I/O General purpose I/O [2]

39 P0.27 Digital I/O General purpose I/O [2]


40 P0.28


AIN4

41 P0.29


AIN5

42 P0.30


AIN6

43 P0.31


AIN7


Digital I/O


Analog input

Digital I/O


Analog input

Digital I/O


Analog input

Digital I/O


Analog input


**Page 15**


General purpose I/O [2]


SAADC/COMP/LPCOMP input

General purpose I/O [2]


SAADC/COMP/LPCOMP input

General purpose I/O [2]


SAADC/COMP/LPCOMP input

General purpose I/O pin [2]


SAADC/COMP/LPCOMP input


4 Pin assignments


**Pin** **Name** **Type** **Description**

44 NC No connect


Leave unconnected

45 VSS Power Ground

46 DEC4 Power 1.3 V regulator supply decoupling


Input from DC/DC regulator


Output from 1.3 V LDO

47 DCC Power DC/DC regulator output

48 VDD Power Power supply

**Bottom of chip**

Die pad VSS Power Ground pad


Exposed die pad must be connected

to ground (VSS) for proper device

operation.

###### **4.2 WLCSP ball assignments**


1 2 3 4 5 6 7


A


B


C


D


E


F


G


H


#### N52832 CIAAHP YYWWLL


**Figure 3: WLCSP ball assignments, top view**


**Table 4: WLCSP ball assignments**


**Ball** **Name** **Description**

A1 XC2 Analog input Connection for 32 MHz crystal

A2 DEC2 Power 1.3 V regulator supply decoupling (Radio

supply)


A3 P0.28


AIN4

A4 P0.29


AIN5

A5 P0.30


AIN6


Digital I/O


Analog input

Digital I/O


Analog input

Digital I/O


Analog input


General purpose I/O [3]


SAADC/COMP/LPCOMP input

General purpose I/O [3]


SAADC/COMP/LPCOMP input

General purpose I/O [3]


SAADC/COMP/LPCOMP input


A6 DEC4 Power 1.3 V regulator supply decoupling


Input from DC/DC converter. Output

from 1.3 V LDO

A7 VDD Power Power supply

B2 XC1 Analog input Connection for 32 MHz crystal

B3 P0.25 Digital I/O General purpose I/O [3]


1 See _GPIO located near the radio_ on page 18 for more information.
2 See _NFC antenna pins_ on page 18 for more information.


**Page 16**


4 Pin assignments


**Ball** **Name** **Description**

B4 P0.27 Digital I/O General purpose I/O [3]


B5 P0.31


AIN7


Digital I/O


Analog input


General purpose I/O [3]


SAADC/COMP/LPCOMP input


B6 DCC Power DC/DC converter output

B7 DEC1 Power 0.9 V regulator digital supply decoupling

C2 DEC3 Power Power supply decoupling

C3 NC N/A Not connected

C4 VSS Power Ground

C5 VSS Power Ground


C6 P0.02


AIN0

C7 P0.01


XL2


Digital I/O


Analog input

Digital I/O


Analog input


General purpose I/O


SAADC/COMP/LPCOMP input

General purpose I/O


Connection for 32.768 kHz crystal (LFXO)


D1 ANT RF Single-ended radio antenna connection

D2 VSS_PA Power Ground (Radio supply)

D3 P0.26 Digital I/O General purpose I/O [3]


D6 P0.03


AIN1

D7 P0.00


XL1


Digital I/O


Analog input

Digital I/O


Analog input


General purpose I/O


SAADC/COMP/LPCOMP input

General purpose I/O


Connection for 32.768 kHz crystal (LFXO)


E1 P0.24 Digital I/O General purpose I/O [3]

E2 P0.23 Digital I/O General purpose I/O [3]

E3 VSS Power Ground


E6 P0.04


AIN2

E7 P0.05


AIN3


Digital I/O


Analog input

Digital I/O


Analog input


General purpose I/O


SAADC/COMP/LPCOMP input

General purpose I/O


SAADC/COMP/LPCOMP input


F1 SWDCLK Digital input Serial wire debug clock input for debug

and programming

F2 P0.22 Digital I/O General purpose I/O [3]

F3 P0.19 Digital I/O General purpose I/O

F4 P0.11 Digital I/O General purpose I/O

F5 VSS Power Ground

F6 P0.07 Digital I/O General purpose I/O

F7 P0.06 Digital I/O General purpose I/O

G1 SWDIO Digital I/O Serial wire debug I/O for debug and

programming


G2 P0.20


TRACECLK


Digital I/O General purpose I/O


Trace port clock output


G3 P0.17 Digital I/O General purpose I/O

G4 P0.13 Digital I/O General purpose I/O


G5 NFC2


P0.10

G6 NFC1


P0.09


NFC input


Digital I/O

NFC input


Digital I/O


NFC antenna connection


General purpose I/O [4]

NFC antenna connection


General purpose I/O [4]


G7 P0.08 Digital I/O General purpose I/O


H1 P0.21


nRESET

H2 P0.18


TRACEDATA[0]

H3 P0.16


TRACEDATA[1]


Digital I/O General purpose I/O


Configurable as pin reset

Digital I/O General purpose I/O


Trace port output

Digital I/O General purpose I/O


Trace port output


H4 P0.15 Digital I/O General purpose I/O


**Page 17**


4 Pin assignments


**Ball** **Name** **Description**

TRACEDATA[2] Trace port output


H5 P0.14


TRACEDATA[3]


Digital I/O General purpose I/O


Trace port output


H6 P0.12 Digital I/O General purpose I/O

H7 VDD Power Power supply

###### **4.3 GPIO usage restrictions**


For more information on standard drive, see _GPIO — General purpose input/output_ on page 114. Low
frequency I/O is a signal with a frequency up to 10 kHz.


**4.3.1 GPIO located near the radio**
Radio performance parameters, such as sensitivity, may be affected by high frequency digital I/O with large
sink/source current close to the Radio power supply and antenna pins.

_Table 5: GPIO recommended usage for QFN48 package_ on page 18 and _Table 6: GPIO recommended_
_usage for WLCSP package_ on page 18 identify some GPIO that have recommended usage guidelines to
maximize radio performance in an application.


**Table 5: GPIO recommended usage for QFN48 package**


**Pin** **GPIO** **Recommended usage**
27 P0.22 Low drive, low frequency I/O only.
28 P0.23
29 P0.24
37 P0.25
38 P0.26
39 P0.27
40 P0.28
41 P0.29
42 P0.30
43 P0.31


**Table 6: GPIO recommended usage for WLCSP package**


**Pin** **GPIO** **Recommended usage**
F2 P0.22 Low drive, low frequency I/O only.
E2 P0.23
E1 P0.24
B3 P0.25
D3 P0.26
B4 P0.27
A3 P0.28
A4 P0.29
A5 P0.30
B5 P0.31


**4.3.2 NFC antenna pins**
Two physical pins can be configured either as NFC antenna pins (factory default), or as GPIOs, as shown
below.


**Table 7: GPIO pins used by NFC**


**NFC pad name** **GPIO**
NFC1 P0.09
NFC2 P0.10


When configured as NFC antenna pins, the GPIOs on those pins will automatically be set to DISABLE state
and a protection circuit will be enabled preventing the chip from being damaged in the presence of a strong


3 See _GPIO located near the radio_ on page 18 for more information.
4 See _NFC antenna pins_ on page 18 for more information.


**Page 18**


4 Pin assignments


NFC field. The protection circuit will short the two pins together if voltage difference exceeds approximately 2
V.

For information on how to configure these pins as normal GPIOs, see _NFCT — Near field communication tag_
on page 420 and _UICR — User information configuration registers_ on page 55. Note that the device will
not be protected against strong NFC field damage if the pins are configured as GPIO and an NFC antenna
is connected to the device. The pins will always be configured as NFC pins during power-on reset until the
configuration is set according to the UICR register.

These two pins will have some limitations when configured as GPIO. The pin capacitance will be higher on
these pins, and there is some current leakage between the two pins if they are driven to different logical
values. To avoid leakage between the pins when configured as GPIO, these GPIOs should always be at the
same logical value whenever entering one of the device power saving modes. See _Electrical specification_ .


**Page 19**


5 Absolute maximum ratings

#### **5 Absolute maximum ratings**


Maximum ratings are the extreme limits to which the chip can be exposed for a limited amount of time
without permanently damaging it. Exposure to absolute maximum ratings for prolonged periods of time may
affect the reliability of the device.


**Table 8: Absolute maximum ratings**


**Min.** **Max.** **Unit**
**Supply voltages**
VDD -0.3 +3.9 V
VSS 0 V
**I/O pin voltage**
VI/O, VDD ≤3.6 V -0.3 VDD + 0.3 V V
VI/O, VDD >3.6 V -0.3 3.9 V V
**NFC antenna pin current**
INFC1/2 80 mA
**Radio**
RF input level 10 dBm
**Environmental QFN48, 6×6 mm package**
Storage temperature -40 +125 °C
MSL (moisture sensitivity level) 2
ESD HBM (human body model) 4 kV
ESD CDM (charged device model) 1000 V
**Environmental WLCSP, 3.0×3.2 mm package**
Storage temperature -40 +125 °C
MSL 1
ESD HBM 2 kV
ESD CDM 500 V
**Flash memory**
Endurance 10 000 Write/erase cycles
Retention 10 years at 85°C


**Page 20**


6 Recommended operating conditions

#### **6 Recommended operating conditions**


The operating conditions are the physical parameters that the chip can operate within.


**Table 9: Recommended operating conditions**


**Symbol** **Parameter** **Notes** **Min.** **Nom.** **Max.** **Units**
VDD Supply voltage, independent of DCDC enable 1.7 3.0 3.6 V
tR_VDD Supply rise time (0 V to 1.7 V) 60 ms
TA Operating temperature -40 25 85 °C


**Important:** The on-chip power-on reset circuitry may not function properly for rise times longer than
the specified maximum.

###### **6.1 WLCSP light sensitivity**

All WLCSP package variants are sensitive to visible and close-range infrared light. This means that a final
product design must shield the chip properly, either by final product encapsulation or by shielding/coating of
the WLCSP device.


**Page 21**


7 CPU

#### **7 CPU**


The ARM [®] Cortex [®] -M4 processor with floating-point unit (FPU) has a 32-bit instruction set (Thumb [®] -2
technology) that implements a superset of 16 and 32-bit instructions to maximize code density and
performance.

This processor implements several features that enable energy-efficient arithmetic and high-performance
signal processing including:

- Digital signal processing (DSP) instructions

- Single-cycle multiply and accumulate (MAC) instructions

- Hardware divide

- 8 and 16-bit single instruction multiple data (SIMD) instructions

- Single-precision floating-point unit (FPU)

The ARM Cortex Microcontroller Software Interface Standard (CMSIS) hardware abstraction layer for the
ARM Cortex processor series is implemented and available for the M4 CPU.

Real-time execution is highly deterministic in thread mode, to and from sleep modes, and when handling
events at configurable priority levels via the Nested Vectored Interrupt Controller (NVIC).

Executing code from flash will have a wait state penalty on the nRF52 Series. An instruction cache can be
enabled to minimize flash wait states when fetching instructions. For more information on cache, see _Cache_
on page 31. The section _Electrical specification_ on page 22 shows CPU performance parameters
including wait states in different modes, CPU current and efficiency, and processing power and efficiency
based on the CoreMark [®] benchmark.

###### **7.1 Floating point interrupt**

The floating point unit (FPU) may generate exceptions when used due to e.g. overflow or underflow. These
exceptions will trigger the FPU interrupt (see _Instantiation_ on page 25). To clear the IRQ line when an
exception has occurred, the relevant exception bit within the FPSCR register needs to be cleared. For more
information about the FPSCR or other FPU registers, see _Cortex-M4 Devices Generic User Guide_ .

###### **7.2 Electrical specification**


**7.2.1 CPU performance**


The CPU clock speed is 64 MHz. Current and efficiency data is taken when in System ON and the CPU is
executing the CoreMark [™] benchmark. It includes power regulator and clock base currents. All other blocks
are IDLE.


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

WFLASH CPU wait states, running from flash, cache disabled 0 2

WFLASHCACHE CPU wait states, running from flash, cache enabled 0 3

WRAM CPU wait states, running from RAM 0

IDDFLASHCACHE CPU current, running from flash, cache enabled, LDO 7.4 mA

IDDFLASHCACHEDCDC CPU current, running from flash, cache enabled, DCDC 3V 3.7 mA

IDDFLASH CPU current, running from flash, cache disabled, LDO 8.0 mA

IDDFLASHDCDC CPU current, running from flash, cache disabled, DCDC 3V 3.9 mA

IDDRAM CPU current, running from RAM, LDO 6.7 mA

IDDRAMDCDC CPU current, running from RAM, DCDC 3V 3.3 mA

IDDFLASH/MHz CPU efficiency, running from flash, cache enabled, LDO 125 µA/

MHz

IDDFLASHDCDC/MHz CPU efficiency, running from flash, cache enabled, DCDC 3V 58 µA/

MHz


**Page 22**


7 CPU


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

CMFLASH CoreMark [5], running from flash, cache enabled 215 CoreMark

CMFLASH/MHz CoreMark per MHz, running from flash, cache enabled 3.36 CoreMark/

MHz

CMFLASH/mA CoreMark per mA, running from flash, cache enabled, DCDC 3V 58 CoreMark/

mA

###### **7.3 CPU and support module configuration**

The ARM [®] Cortex [®] -M4 processor has a number of CPU options and support modules implemented on the
device.


**Option / Module** **Description** **Implemented**
Core options
NVIC Nested Vector Interrupt Controller 37 vectors
PRIORITIES Priority bits 3
WIC Wakeup Interrupt Controller NO
Endianness Memory system endianness Little endian
Bit Banding Bit banded memory NO
DWT Data Watchpoint and Trace YES
SysTick System tick timer YES
Modules
MPU Memory protection unit YES
FPU Floating point unit YES
DAP Debug Access Port YES
ETM Embedded Trace Macrocell YES
ITM Instrumentation Trace Macrocell YES
TPIU Trace Port Interface Unit YES
ETB Embedded Trace Buffer NO
FPB Flash Patch and Breakpoint Unit YES
HTM AHB Trace Macrocell NO


5 Using IAR v6.50.1.4452 with flags --endian=little --cpu=Cortex-M4 -e --fpu=VFPv4_sp –Ohs --no_size_constraints


**Page 23**


8 Memory

#### **8 Memory**


The nRF52832 contains flash and RAM that can be used for code and data storage.

The amount of RAM and flash will vary depending on variant, see _Table 10: Memory variants_ on page 24.


**Table 10: Memory variants**


**Device name** **RAM** **Flash** **Comments**
nRF52832-QFAA 64 kB 512 kB
nRF52832-QFAB 32 kB 256 kB
nRF52832-CIAA 64 kB 512 kB


The CPU and the EasyDMA can access memory via the AHB multilayer interconnect. The CPU is also able
to access peripherals via the AHB multilayer interconnect, as illustrated in _Figure 4: Memory layout_ on page
24.


Peripheral


EasyDMA


AHB multilayer interconnect


Data RAM
System


AHB2APB


APB


Peripheral


EasyDMA


CPU


ARM Cortex-M4


RAM7 0x2000 F000
AHB slave


RAM6
AHB slave


RAM5
AHB slave


RAM4
AHB slave


Section 1

Section 0

Section 1

Section 0

Section 1

Section 0

Section 1

Section 0

Section 1

Section 0


0x2000 E000

0x2000 D000

0x2000 C000

0x2000 B000

0x2000 A000

0x2000 9000

0x2000 8000


RAM3 0x2000 7000
AHB slave


Code RAM
ICODE/DCODE

0x0080 F000

0x0080 E000

0x0080 D000

0x0080 C000

0x0080 B000

0x0080 A000

0x0080 9000

0x0080 8000

0x0080 7000

0x0080 6000

0x0080 5000

0x0080 4000

0x0080 3000

0x0080 2000

0x0080 1000

0x0080 0000


0x2000 6000

0x2000 5000

0x2000 4000

0x2000 3000

0x2000 2000

0x2100 1000

0x2000 0000


Block 7


Block 2..6


Block 1

Block 0


RAM2
AHB slave


RAM1
AHB slave


RAM0
AHB slave


Section 1

Section 0

Section 1

Section 0

Section 1

Section 0


Page 127


Page 3..126


Page 2

Page 1

Page 0


Flash
ICODE/DCODE

0x0007 F000


0x0000 3000

0x0000 2000


AHB


**Figure 4: Memory layout**


ICODE


DCODE


0x0000 1000

0x0000 0E00


0x0000 0400

0x0000 0200

0x0000 0000


See _AHB multilayer_ on page 27 and _EasyDMA_ on page 28 for more information about the AHB
multilayer interconnect and the EasyDMA.

The same physical RAM is mapped to both the Data RAM region and the Code RAM region. It is up to the
application to partition the RAM within these regions so that one does not corrupt the other.

###### **8.1 RAM - Random access memory**

The RAM interface is divided into multiple RAM AHB slaves.

Each RAM AHB slave is connected to two 4-kilobyte RAM sections, see Section 0 and Section 1 in _Figure 4:_
_Memory layout_ on page 24.

Each of the RAM sections have separate power control for System ON and System OFF mode operation,
which is configured via RAM register (see the _POWER — Power supply_ on page 81).


**Page 24**


8 Memory

###### **8.2 Flash - Non-volatile memory**

The Flash can be read an unlimited number of times by the CPU, but it has restrictions on the number of
times it can be written and erased and also on how it can be written.

Writing to Flash is managed by the Non-volatile memory controller (NVMC), see _NVMC — Non-volatile_
_memory controller_ on page 30.

The Flash is divided into multiple pages that can be accessed by the CPU via both the ICODE and DCODE
buses as shown in, _Figure 4: Memory layout_ on page 24. Each page is divided into 8 blocks.

###### **8.3 Memory map**

The complete memory map is shown in _Figure 5: Memory map_ on page 25. As described in _Memory_ on
page 24, Code RAM and the Data RAM are the same physical RAM.


nRF52832 Address Map


0xFFFF FFFF


Cortex M4 System Address Map
nRF52832 Address Map


0xE010 0000
0xE0FF 0000

0xE004 2000
0xE004 1000

0xE004 0000

0xE004 0000

0xE000 F000


ETM
TPIU


Reserved

SCS

Reserved


SCS


FPB

DWT


ROM Table System
External PPB


Private Peripheral Bus - External

Private Peripheral Bus - Internal


0xA000 0000


0x6000 0000


0x5000 0000


0x4000 0000


0x4000 0000


0x2001 0000


0xE000 E000 External device 1.0GB

Reserved

0xE000 3000


External device


0xE000 2000

DWT

0xE000 1000
ITM
0xE000 0000


0x2000 0000
Reserved

0x1000 1000 UICR

Reserved


Reserved


AHB peripherals

Reserved


APB peripherals


Reserved


1.0GB


0.5GB


0.5GB


0x1000 0000


0x0081 0000


0x0080 0000


0x0008 0000


0x0000 0000


FICR


Reserved


Code RAM


Reserved


External RAM


Peripheral


SRAM


Data RAM


Flash Code 0.5GB 0x2000 0000


Code


0.5GB


**Figure 5: Memory map**

###### **8.4 Instantiation**


**Table 11: Instantiation table**


**ID** **Base Address** **Peripheral** **Instance** **Description**

0 0x40000000 POWER POWER Power control

0 0x40000000 CLOCK CLOCK Clock control

0 0x40000000 APPROTECT APPROTECT APPROTECT control

0 0x40000000 BPROT BPROT Block Protect

1 0x40001000 RADIO RADIO 2.4 GHz radio

2 0x40002000 UARTE UARTE0 Universal Asynchronous Receiver/Transmitter with EasyDMA

2 0x40002000 UART UART0 Universal Asynchronous Receiver/Transmitter Deprecated

3 0x40003000 SPIM SPIM0 SPI master 0

3 0x40003000 SPIS SPIS0 SPI slave 0

3 0x40003000 SPI SPI0 SPI master 0 Deprecated

3 0x40003000 TWIM TWIM0 Two-wire interface master 0


**Page 25**


8 Memory


**ID** **Base Address** **Peripheral** **Instance** **Description**

3 0x40003000 TWIS TWIS0 Two-wire interface slave 0

3 0x40003000 TWI TWI0 Two-wire interface master 0 Deprecated

4 0x40004000 TWI TWI1 Two-wire interface master 1 Deprecated

4 0x40004000 TWIM TWIM1 Two-wire interface master 1

4 0x40004000 TWIS TWIS1 Two-wire interface slave 1

4 0x40004000 SPI SPI1 SPI master 1 Deprecated

4 0x40004000 SPIM SPIM1 SPI master 1

4 0x40004000 SPIS SPIS1 SPI slave 1

5 0x40005000 NFCT NFCT Near Field Communication Tag

6 0x40006000 GPIOTE GPIOTE GPIO Tasks and Events

7 0x40007000 SAADC SAADC Analog to digital converter

8 0x40008000 TIMER TIMER0 Timer 0

9 0x40009000 TIMER TIMER1 Timer 1

10 0x4000A000 TIMER TIMER2 Timer 2

11 0x4000B000 RTC RTC0 Real-time counter 0

12 0x4000C000 TEMP TEMP Temperature sensor

13 0x4000D000 RNG RNG Random number generator

14 0x4000E000 ECB ECB AES Electronic Code Book (ECB) mode block encryption

15 0x4000F000 CCM CCM AES CCM Mode Encryption

15 0x4000F000 AAR AAR Acelerated Address Resolver

16 0x40010000 WDT WDT Watchdog timer

17 0x40011000 RTC RTC1 Real-time counter 1

18 0x40012000 QDEC QDEC Quadrature decoder

19 0x40013000 LPCOMP LPCOMP Low power comparator

19 0x40013000 COMP COMP General purpose comparator

20 0x40014000 EGU EGU0 Event Generator Unit 0

20 0x40014000 SWI SWI0 Software interrupt 0

21 0x40015000 EGU EGU1 Event Generator Unit 1

21 0x40015000 SWI SWI1 Software interrupt 1

22 0x40016000 SWI SWI2 Software interrupt 2

22 0x40016000 EGU EGU2 Event Generator Unit 2

23 0x40017000 SWI SWI3 Software interrupt 3

23 0x40017000 EGU EGU3 Event Generator Unit 3

24 0x40018000 SWI SWI4 Software interrupt 4

24 0x40018000 EGU EGU4 Event Generator Unit 4

25 0x40019000 SWI SWI5 Software interrupt 5

25 0x40019000 EGU EGU5 Event Generator Unit 5

26 0x4001A000 TIMER TIMER3 Timer 3

27 0x4001B000 TIMER TIMER4 Timer 4

28 0x4001C000 PWM PWM0 Pulse Width Modulation Unit 0

29 0x4001D000 PDM PDM Pulse Density Modulation (Digital Microphone Interface)

30 0x4001E000 NVMC NVMC Non-Volatile Memory Controller

31 0x4001F000 PPI PPI Programmable Peripheral Interconnect

32 0x40020000 MWU MWU Memory Watch Unit

33 0x40021000 PWM PWM1 Pulse Width Modulation Unit 1

34 0x40022000 PWM PWM2 Pulse Width Modulation Unit 2

35 0x40023000 SPIS SPIS2 SPI slave 2

35 0x40023000 SPI SPI2 SPI master 2 Deprecated

35 0x40023000 SPIM SPIM2 SPI master 2

36 0x40024000 RTC RTC2 Real-time counter 2

37 0x40025000 I2S I2S Inter-IC Sound Interface

38 0x40026000 FPU FPU FPU interrupt

0 0x50000000 GPIO GPIO General purpose input and output Deprecated

0 0x50000000 GPIO P0 General purpose input and output

N/A 0x10000000 FICR FICR Factory Information Configuration

N/A 0x10001000 UICR UICR User Information Configuration


**Page 26**


9 AHB multilayer

#### **9 AHB multilayer**


The CPU and all of the EasyDMAs are AHB bus masters on the AHB multilayer, while the RAM and various
other modules are AHB slaves.

See _Block diagram_ on page 13 for an overview of which peripherals implement EasyDMA.

The CPU has exclusive access to all AHB slaves except for the RAM that can also be accessed by the
EasyDMA.

Access rights to each of the RAM AHB slaves are resolved using the priority of the different bus masters in
the system

See _AHB multilayer priorities_ on page 27 for information about the priority of the different AHB bus
masters in the system. It is possible for two or more bus masters to have the same priority in cases where
it is guaranteed by design that the related masters will never be able to access the same slave at the same
time.

###### **9.1 AHB multilayer priorities**

Each master connected to the AHB multilayer is assigned a priority.


**Table 12: AHB bus masters**


**Bus master name** **Priority** **Description**
CPU Highest priority
SPIS1 Applies to SPIM1, SPIS1, TWIM1, TWIS1
RADIO
CCM/ECB/AAR
SAADC
UARTE
SERIAL0 Applies to SPIM0, SPIS0, TWIM0, TWIS0
SERIAL2 Applies to SPIM2, SPIS2
NFCT
I2S I2S
PDM PDM
PWM Lowest priority Applies to PWM0, PWM1, PWM2


**Page 27**


10 EasyDMA

#### **10 EasyDMA**


EasyDMA is an easy-to-use direct memory access module that some peripherals implement to gain direct
access to Data RAM.

The EasyDMA is an AHB bus master similar to the CPU and it is connected to the AHB multilayer
interconnect for direct access to the Data RAM. The EasyDMA is not able to access the Flash.

A peripheral can implement multiple EasyDMA instances, for example to provide a dedicated channel for
reading data from RAM into the peripheral at the same time as a second channel is dedicated for writing data
to the RAM from the peripheral. This concept is illustrated in _Figure 6: EasyDMA example_ on page 28


RAM


RAM


RAM


**Figure 6: EasyDMA example**


AHB Multilayer


Peripheral


Peripheral

Core


AHB


AHB


READER


EasyDMA


WRITER


EasyDMA


An EasyDMA channel is usually exposed to the user in the form illustrated below, but some variations may
occur:

```
 READERBUFFER_SIZE 5
 WRITERBUFFER_SIZE 6
 uint8_t readerBuffer[READERBUFFER_SIZE] __at__ 0x20000000;
 uint8_t writerBuffer[WRITERBUFFER_SIZE] __at__ 0x20000005;
 // Configuring the READER channel
 MYPERIPHERAL->READER.MAXCNT = READERBUFFER_SIZE;
 MYPERIPHERAL->READER.PTR = &readerBuffer;
 // Configure the WRITER channel
 MYPERIPHERAL->WRITER.MAXCNT = WRITEERBUFFER_SIZE;
 MYPERIPHERAL->WRITER.PTR = &writerBuffer;

```

This example shows a peripheral called MYPERIPHERAL that implements two EasyDMA channels, one
for reading, called READER, and one for writing, called WRITER. When the peripheral is started, it is here
assumed that the peripheral will read 5 bytes from the readerBuffer located in RAM at address 0x20000000,
process the data and then write no more than 6 bytes back to the writerBuffer located in RAM at address
0x20000005. The memory layout of these buffers is illustrated in _Figure 7: EasyDMA memory layout_ on page
29.


**Page 28**


0x20000000

0x20000004

0x20000008


10 EasyDMA


readerBuffer[0] readerBuffer[1] readerBuffer[2] readerBuffer[3]

readerBuffer[4] writerBuffer[0] writerBuffer[1] writerBuffer[2]

writerBuffer[3] writerBuffer[4] writerBuffer[5]


**Figure 7: EasyDMA memory layout**


The EasyDMA channel's MAXCNT register cannot be specified larger than the actual size of the buffer. If,
for example, the WRITER.MAXCNT register is specified larger than the size of the writerBuffer, the WRITER
EasyDMA channel may overflow the writerBuffer.

After the peripheral has completed the EasyDMA transfer, the CPU can read the EasyDMA channel's
AMOUNT register to see how many bytes that were transferred, e.g. it is possible for the CPU to read the
MYPERIPHERAL->WRITER.AMOUNT register to see how many bytes the WRITER wrote to RAM.

###### **10.1 EasyDMA array list**

The EasyDMA is able to operate in a mode called array list.

The EasyDMA array list can be represented by the data structure ArrayList_type illustrated in the code
example below.

This data structure includes only a buffer with size equal to READER.MAXCNT. EasyDMA will use the
READER.MAXCNT register to determine when the buffer is full.

This array list does not provide a mechanism to explicitly specify where the next item in the list is located.
Instead, it assumes that the list is organized as a linear array where items are located one after the other in
RAM.

```
 #define BUFFER_SIZE 4
 typedef struct ArrayList
 {
 uint8_t buffer[BUFFER_SIZE];
 } ArrayList_type;
 ArrayList_type ReaderList[3];
 READER.MAXCNT = BUFFER_SIZE;
 READER.PTR = &ReaderList;

```

READER.PTR = &ReaderList


0x20000000 : ReaderList[0] buffer[0] buffer[1]


buffer[2] buffer[3]


0x20000004 : ReaderList[1]

0x20000008 : ReaderList[2]


**Figure 8: EasyDMA array list**


buffer[0] buffer[1] buffer[2] buffer[3]

buffer[0] buffer[1] buffer[2] buffer[3]


**Page 29**


11 NVMC — Non-volatile memory controller

#### **11 NVMC — Non-volatile memory controller**


The Non-volatile memory controller (NVMC) is used for writing and erasing the internal Flash memory and
the UICR.

Before a write can be performed, the NVMC must be enabled for writing in CONFIG.WEN. Similarly, before
an erase can be performed, the NVMC must be enabled for erasing in CONFIG.EEN, see _CONFIG_ on page
32. The user must make sure that writing and erasing are not enabled at the same time. Failing to do so
may result in unpredictable behavior.

###### **11.1 Writing to Flash**

When writing is enabled, the Flash is written by writing a full 32-bit word to a word-aligned address in the
Flash.

The NVMC is only able to write '0' to bits in the Flash that are erased, that is, set to '1'. It cannot write back a
bit to '1'.

As illustrated in _Memory_ on page 24, the Flash is divided into multiple pages that are further divided into
multiple blocks. The same block in the Flash can only be written _nWRITE_ number of times before an erase
must be performed using _ERASEPAGE_ or _ERASEALL_ . See the memory size and organization in _Memory_ on
page 24 for block size.

Only full 32-bit words can be written to Flash using the NVMC interface. To write less than 32 bits to Flash,
write the data as a word, and set all the bits that should remain unchanged in the word to '1'. Note that the
restriction about the number of writes (see above) still applies in this case.

The time it takes to write a word to the Flash is specified by _tWRITE_ . The CPU is halted while the NVMC is
writing to the Flash.

Only word-aligned writes are allowed. Byte or half-word-aligned writes will result in a hard fault.

###### **11.2 Erasing a page in Flash**

When erase is enabled, the Flash can be erased page by page using the ERASEPAGE register.

After erasing a Flash page, all bits in the page are set to '1'. The time it takes to erase a page is specified by
_tERASEPAGE_ . The CPU is halted while the NVMC performs the erase operation.

###### **11.3 Writing to user information configuration registers (UICR)**

User information configuration registers (UICR) are written in the same way as Flash. After UICR has been
written, the new UICR configuration will only take effect after a reset.

UICR can only be written _nWRITE_ number of times before an erase must be performed using _ERASEUICR_ or
_ERASEALL_ .

The time it takes to write a word to the UICR is specified by _tWRITE_ . The CPU is halted while the NVMC is
writing to the UICR.

###### **11.4 Erasing user information configuration registers (UICR)**

When erase is enabled, UICR can be erased using the ERASEUICR register.

After erasing UICR all bits in UICR are set to '1'. The time it takes to erase UICR is specified by _tERASEPAGE_ .
The CPU is halted while the NVMC performs the erase operation.


**Page 30**


11 NVMC — Non-volatile memory controller

###### **11.5 Erase all**

When erase is enabled, the whole Flash and UICR can be erased in one operation by using the ERASEALL
register. ERASEALL will not erase the factory information configuration registers (FICR).

The time it takes to perform an ERASEALL command is specified by _tERASEALL_ The CPU is halted while the
NVMC performs the erase operation.

###### **11.6 Cache**

An instruction cache (I-Cache) can be enabled for the ICODE bus in the NVMC.

See the Memory map in _Memory map_ on page 25 for the location of Flash.

A cache hit is an instruction fetch from the cache, and it has a 0 wait-state delay. The number of wait-states
for a cache miss, where the instruction is not available in the cache and needs to be fetched from Flash,
depends on the processor frequency and is shown in _CPU_ on page 22

Enabling the cache can increase CPU performance and reduce power consumption by reducing the number
of wait cycles and the number of flash accesses. This will depend on the cache hit rate. Cache will use some
current when enabled. If the reduction in average current due to reduced flash accesses is larger than the
cache power requirement, the average current to execute the program code will reduce.

When disabled, the cache does not use current and does not retain its content.

It is possible to enable cache profiling to analyze the performance of the cache for your program using the
_ICACHECNF_ register. When profiling is enabled, the _IHIT_ and _IMISS_ registers are incremented for every
instruction cache hit or miss respectively. The hit and miss profiling registers do not wrap around after
reaching the maximum value. If the maximum value is reached, consider profiling for a shorter duration to get
correct numbers.

###### **11.7 Registers**


**Table 13: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x4001E000 NVMC NVMC Non-Volatile Memory Controller


**Table 14: Register Overview**


**Register** **Offset** **Description**

_READY_ 0x400 Ready flag

_CONFIG_ 0x504 Configuration register

_ERASEPAGE_ 0x508 Register for erasing a page in Code area

_ERASEPCR1_ 0x508 Register for erasing a page in Code area. Equivalent to ERASEPAGE. Deprecated

_ERASEALL_ 0x50C Register for erasing all non-volatile user memory

_ERASEPCR0_ 0x510 Register for erasing a page in Code area. Equivalent to ERASEPAGE. Deprecated

_ERASEUICR_ 0x514 Register for erasing User Information Configuration Registers

_ICACHECNF_ 0x540 I-Code cache configuration register.

_IHIT_ 0x548 I-Code cache hit counter.

_IMISS_ 0x54C I-Code cache miss counter.


**11.7.1 READY**

Address offset: 0x400

Ready flag


**Page 31**


11 NVMC — Non-volatile memory controller


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R READY NVMC is ready or busy

Busy 0 NVMC is busy (on-going write or erase operation)

Ready 1 NVMC is ready


**11.7.2 CONFIG**

Address offset: 0x504

Configuration register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW WEN Program memory access mode. It is strongly recommended

to only activate erase and write modes when they are actively

used. Enabling write or erase will invalidate the cache and keep

it invalidated.

Ren 0 Read only access

Wen 1 Write Enabled

Een 2 Erase enabled


**11.7.3 ERASEPAGE**

Address offset: 0x508

Register for erasing a page in Code area


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ERASEPAGE Register for starting erase of a page in Code area


The value is the address to the page to be erased. (Addresses of

first word in page). Note that code erase has to be enabled by

CONFIG.EEN before the page can be erased. Attempts to erase

pages that are outside the code area may result in undesirable

behaviour, e.g. the wrong page may be erased.


**11.7.4 ERASEPCR1 ( Deprecated )**

Address offset: 0x508

Register for erasing a page in Code area. Equivalent to ERASEPAGE.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ERASEPCR1 Register for erasing a page in Code area. Equivalent to

ERASEPAGE.


**11.7.5 ERASEALL**

Address offset: 0x50C

Register for erasing all non-volatile user memory


**Page 32**


11 NVMC — Non-volatile memory controller


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ERASEALL Erase all non-volatile memory including UICR registers. Note

that code erase has to be enabled by CONFIG.EEN before the

UICR can be erased.

NoOperation 0 No operation

Erase 1 Start chip erase


**11.7.6 ERASEPCR0 ( Deprecated )**

Address offset: 0x510

Register for erasing a page in Code area. Equivalent to ERASEPAGE.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ERASEPCR0 Register for starting erase of a page in Code area. Equivalent to

ERASEPAGE.


**11.7.7 ERASEUICR**

Address offset: 0x514

Register for erasing User Information Configuration Registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ERASEUICR Register starting erase of all User Information Configuration

Registers. Note that code erase has to be enabled by

CONFIG.EEN before the UICR can be erased.

NoOperation 0 No operation

Erase 1 Start erase of UICR


**11.7.8 ICACHECNF**

Address offset: 0x540

I-Code cache configuration register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CACHEEN Cache enable

Disabled 0 Disable cache. Invalidates all cache entries.

Enabled 1 Enable cache

B RW CACHEPROFEN Cache profiling enable

Disabled 0 Disable cache profiling

Enabled 1 Enable cache profiling


**11.7.9 IHIT**

Address offset: 0x548

I-Code cache hit counter.


**Page 33**


11 NVMC — Non-volatile memory controller


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW HITS Number of cache hits


**11.7.10 IMISS**

Address offset: 0x54C

I-Code cache miss counter.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MISSES Number of cache misses

###### **11.8 Electrical specification**


**11.8.1 Flash programming**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

nWRITE,BLOCK Amount of writes allowed in a block between erase 181

tWRITE Time to write one word 67.5 338 µs

tERASEPAGE Time to erase one page 2.05 89.7 ms

tERASEALL Time to erase all flash 6.72 295.3 ms


**11.8.2 Cache size**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

SizeICODE I-Code cache size 2048 Bytes


**Page 34**


12 BPROT — Block protection

#### **12 BPROT — Block protection**


The mechanism for protecting non-volatile memory can be used to prevent application code from erasing or
writing to protected blocks.

Non-volatile memory can be protected from erases and writes depending on the settings in the CONFIG
registers. One bit in a CONFIG register represents one protected block of 4 kB. There are four CONFIG
registers of 32 bits, which means there are 128 protectable blocks in total.

**Important:** If an erase or write to a protected block is detected, the CPU will hard fault. If an
ERASEALL operation is attempted from the CPU while any block is protected, it will be blocked and
the CPU will hard fault.

On reset, all the protection bits are cleared. To ensure safe operation, the first task after reset must be to set
the protection bits. The only way of clearing protection bits is by resetting the device from any reset source.

The protection mechanism is turned off when in debug interface mode (a debugger is connected) and the
DISABLEINDEBUG register is set to disable. For more information, see _Debug and trace_ on page 73.


Program Memory


127
126
125


l




CONFIG[3] 0


l


CONFIG[0] 0


...


2
1
0


0x00000000


**Figure 9: Protected regions of program memory**

###### **12.1 Registers**


**Table 15: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40000000 BPROT BPROT Block Protect


**Table 16: Register Overview**


**Register** **Offset** **Description**

_CONFIG0_ 0x600 Block protect configuration register 0

_CONFIG1_ 0x604 Block protect configuration register 1

_DISABLEINDEBUG_ 0x608 Disable protection mechanism in debug interface mode

0x60C Reserved

_CONFIG2_ 0x610 Block protect configuration register 2

_CONFIG3_ 0x614 Block protect configuration register 3


**Page 35**


12 BPROT — Block protection


**12.1.1 CONFIG0**

Address offset: 0x600

Block protect configuration register 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW REGION0 Enable protection for region 0. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

B RW REGION1 Enable protection for region 1. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

C RW REGION2 Enable protection for region 2. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

D RW REGION3 Enable protection for region 3. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

E RW REGION4 Enable protection for region 4. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

F RW REGION5 Enable protection for region 5. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

G RW REGION6 Enable protection for region 6. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

H RW REGION7 Enable protection for region 7. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

I RW REGION8 Enable protection for region 8. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

J RW REGION9 Enable protection for region 9. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

K RW REGION10 Enable protection for region 10. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

L RW REGION11 Enable protection for region 11. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

M RW REGION12 Enable protection for region 12. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

N RW REGION13 Enable protection for region 13. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

O RW REGION14 Enable protection for region 14. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

P RW REGION15 Enable protection for region 15. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

Q RW REGION16 Enable protection for region 16. Write '0' has no effect.

Disabled 0 Protection disabled


**Page 36**


12 BPROT — Block protection


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Protection enable

R RW REGION17 Enable protection for region 17. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

S RW REGION18 Enable protection for region 18. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

T RW REGION19 Enable protection for region 19. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

U RW REGION20 Enable protection for region 20. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

V RW REGION21 Enable protection for region 21. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

W RW REGION22 Enable protection for region 22. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

X RW REGION23 Enable protection for region 23. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

Y RW REGION24 Enable protection for region 24. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

Z RW REGION25 Enable protection for region 25. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

a RW REGION26 Enable protection for region 26. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

b RW REGION27 Enable protection for region 27. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

c RW REGION28 Enable protection for region 28. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

d RW REGION29 Enable protection for region 29. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

e RW REGION30 Enable protection for region 30. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable

f RW REGION31 Enable protection for region 31. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enable


**12.1.2 CONFIG1**

Address offset: 0x604

Block protect configuration register 1


**Page 37**


12 BPROT — Block protection


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW REGION32 Enable protection for region 32. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

B RW REGION33 Enable protection for region 33. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

C RW REGION34 Enable protection for region 34. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

D RW REGION35 Enable protection for region 35. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

E RW REGION36 Enable protection for region 36. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

F RW REGION37 Enable protection for region 37. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

G RW REGION38 Enable protection for region 38. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

H RW REGION39 Enable protection for region 39. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

I RW REGION40 Enable protection for region 40. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

J RW REGION41 Enable protection for region 41. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

K RW REGION42 Enable protection for region 42. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

L RW REGION43 Enable protection for region 43. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

M RW REGION44 Enable protection for region 44. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

N RW REGION45 Enable protection for region 45. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

O RW REGION46 Enable protection for region 46. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

P RW REGION47 Enable protection for region 47. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

Q RW REGION48 Enable protection for region 48. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

R RW REGION49 Enable protection for region 49. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

S RW REGION50 Enable protection for region 50. Write '0' has no effect.


**Page 38**


12 BPROT — Block protection


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Protection disabled

Enabled 1 Protection enabled

T RW REGION51 Enable protection for region 51. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

U RW REGION52 Enable protection for region 52. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

V RW REGION53 Enable protection for region 53. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

W RW REGION54 Enable protection for region 54. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

X RW REGION55 Enable protection for region 55. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

Y RW REGION56 Enable protection for region 56. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

Z RW REGION57 Enable protection for region 57. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

a RW REGION58 Enable protection for region 58. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

b RW REGION59 Enable protection for region 59. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

c RW REGION60 Enable protection for region 60. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

d RW REGION61 Enable protection for region 61. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

e RW REGION62 Enable protection for region 62. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

f RW REGION63 Enable protection for region 63. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled


**12.1.3 DISABLEINDEBUG**

Address offset: 0x608

Disable protection mechanism in debug interface mode


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000001** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DISABLEINDEBUG Disable the protection mechanism for NVM regions while

in debug interface mode. This register will only disable the

protection mechanism if the device is in debug interface mode.

Disabled 1 Disable in debug


**Page 39**


12 BPROT — Block protection


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000001** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 0 Enable in debug


**12.1.4 CONFIG2**

Address offset: 0x610

Block protect configuration register 2


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW REGION64 Enable protection for region 64. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

B RW REGION65 Enable protection for region 65. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

C RW REGION66 Enable protection for region 66. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

D RW REGION67 Enable protection for region 67. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

E RW REGION68 Enable protection for region 68. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

F RW REGION69 Enable protection for region 69. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

G RW REGION70 Enable protection for region 70. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

H RW REGION71 Enable protection for region 71. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

I RW REGION72 Enable protection for region 72. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

J RW REGION73 Enable protection for region 73. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

K RW REGION74 Enable protection for region 74. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

L RW REGION75 Enable protection for region 75. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

M RW REGION76 Enable protection for region 76. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

N RW REGION77 Enable protection for region 77. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

O RW REGION78 Enable protection for region 78. Write '0' has no effect.

Disabled 0 Protection disabled


**Page 40**


12 BPROT — Block protection


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Protection enabled

P RW REGION79 Enable protection for region 79. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

Q RW REGION80 Enable protection for region 80. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

R RW REGION81 Enable protection for region 81. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

S RW REGION82 Enable protection for region 82. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

T RW REGION83 Enable protection for region 83. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

U RW REGION84 Enable protection for region 84. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

V RW REGION85 Enable protection for region 85. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

W RW REGION86 Enable protection for region 86. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

X RW REGION87 Enable protection for region 87. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

Y RW REGION88 Enable protection for region 88. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

Z RW REGION89 Enable protection for region 89. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

a RW REGION90 Enable protection for region 90. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

b RW REGION91 Enable protection for region 91. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

c RW REGION92 Enable protection for region 92. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

d RW REGION93 Enable protection for region 93. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

e RW REGION94 Enable protection for region 94. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

f RW REGION95 Enable protection for region 95. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled


**Page 41**


12 BPROT — Block protection


**12.1.5 CONFIG3**

Address offset: 0x614

Block protect configuration register 3


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW REGION96 Enable protection for region 96. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

B RW REGION97 Enable protection for region 97. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

C RW REGION98 Enable protection for region 98. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

D RW REGION99 Enable protection for region 99. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

E RW REGION100 Enable protection for region 100. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

F RW REGION101 Enable protection for region 101. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

G RW REGION102 Enable protection for region 102. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

H RW REGION103 Enable protection for region 103. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

I RW REGION104 Enable protection for region 104. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

J RW REGION105 Enable protection for region 105. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

K RW REGION106 Enable protection for region 106. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

L RW REGION107 Enable protection for region 107. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

M RW REGION108 Enable protection for region 108. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

N RW REGION109 Enable protection for region 109. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

O RW REGION110 Enable protection for region 110. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

P RW REGION111 Enable protection for region 111. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

Q RW REGION112 Enable protection for region 112. Write '0' has no effect.

Disabled 0 Protection disabled


**Page 42**


12 BPROT — Block protection


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Protection enabled

R RW REGION113 Enable protection for region 113. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

S RW REGION114 Enable protection for region 114. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

T RW REGION115 Enable protection for region 115. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

U RW REGION116 Enable protection for region 116. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

V RW REGION117 Enable protection for region 117. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

W RW REGION118 Enable protection for region 118. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

X RW REGION119 Enable protection for region 119. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

Y RW REGION120 Enable protection for region 120. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

Z RW REGION121 Enable protection for region 121. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

a RW REGION122 Enable protection for region 122. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

b RW REGION123 Enable protection for region 123. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

c RW REGION124 Enable protection for region 124. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

d RW REGION125 Enable protection for region 125. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

e RW REGION126 Enable protection for region 126. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled

f RW REGION127 Enable protection for region 127. Write '0' has no effect.

Disabled 0 Protection disabled

Enabled 1 Protection enabled


**Page 43**


13 FICR — Factory information configuration
registers

#### **13 FICR — Factory information configuration registers**


Factory information configuration registers (FICR) are pre-programmed in factory and cannot be erased by
the user. These registers contain chip-specific information and configuration.

###### **13.1 Registers**


**Table 17: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x10000000 FICR FICR Factory Information Configuration


**Table 18: Register Overview**


**Register** **Offset** **Description**

_CODEPAGESIZE_ 0x010 Code memory page size

_CODESIZE_ 0x014 Code memory size

_DEVICEID[0]_ 0x060 Device identifier

_DEVICEID[1]_ 0x064 Device identifier

_ER[0]_ 0x080 Encryption Root, word 0

_ER[1]_ 0x084 Encryption Root, word 1

_ER[2]_ 0x088 Encryption Root, word 2

_ER[3]_ 0x08C Encryption Root, word 3

_IR[0]_ 0x090 Identity Root, word 0

_IR[1]_ 0x094 Identity Root, word 1

_IR[2]_ 0x098 Identity Root, word 2

_IR[3]_ 0x09C Identity Root, word 3

_DEVICEADDRTYPE_ 0x0A0 Device address type

_DEVICEADDR[0]_ 0x0A4 Device address 0

_DEVICEADDR[1]_ 0x0A8 Device address 1

_INFO.PART_ 0x100 Part code

_INFO.VARIANT_ 0x104 Part Variant, Hardware version and Production configuration

_INFO.PACKAGE_ 0x108 Package option

_INFO.RAM_ 0x10C RAM variant

_INFO.FLASH_ 0x110 Flash variant

0x114 Reserved

0x118 Reserved

0x11C Reserved

_TEMP.A0_ 0x404 Slope definition A0.

_TEMP.A1_ 0x408 Slope definition A1.

_TEMP.A2_ 0x40C Slope definition A2.

_TEMP.A3_ 0x410 Slope definition A3.

_TEMP.A4_ 0x414 Slope definition A4.

_TEMP.A5_ 0x418 Slope definition A5.

_TEMP.B0_ 0x41C y-intercept B0.

_TEMP.B1_ 0x420 y-intercept B1.

_TEMP.B2_ 0x424 y-intercept B2.

_TEMP.B3_ 0x428 y-intercept B3.

_TEMP.B4_ 0x42C y-intercept B4.

_TEMP.B5_ 0x430 y-intercept B5.

_TEMP.T0_ 0x434 Segment end T0.

_TEMP.T1_ 0x438 Segment end T1.

_TEMP.T2_ 0x43C Segment end T2.

_TEMP.T3_ 0x440 Segment end T3.

_TEMP.T4_ 0x444 Segment end T4.


**Page 44**


13 FICR — Factory information configuration
registers


**Register** **Offset** **Description**

_NFC.TAGHEADER0_ 0x450 Default header for NFC Tag. Software can read these values to populate NFCID1_3RD_LAST,

NFCID1_2ND_LAST and NFCID1_LAST.

_NFC.TAGHEADER1_ 0x454 Default header for NFC Tag. Software can read these values to populate NFCID1_3RD_LAST,

NFCID1_2ND_LAST and NFCID1_LAST.

_NFC.TAGHEADER2_ 0x458 Default header for NFC Tag. Software can read these values to populate NFCID1_3RD_LAST,

NFCID1_2ND_LAST and NFCID1_LAST.

_NFC.TAGHEADER3_ 0x45C Default header for NFC Tag. Software can read these values to populate NFCID1_3RD_LAST,

NFCID1_2ND_LAST and NFCID1_LAST.


**13.1.1 CODEPAGESIZE**

Address offset: 0x010

Code memory page size


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R CODEPAGESIZE Code memory page size


**13.1.2 CODESIZE**

Address offset: 0x014

Code memory size


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R CODESIZE Code memory size in number of pages


Total code space is: CODEPAGESIZE * CODESIZE


**13.1.3 DEVICEID[0]**

Address offset: 0x060

Device identifier


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R DEVICEID 64 bit unique device identifier


DEVICEID[0] contains the least significant bits of the device

identifier. DEVICEID[1] contains the most significant bits of the

device identifier.


**13.1.4 DEVICEID[1]**

Address offset: 0x064

Device identifier


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R DEVICEID 64 bit unique device identifier


**Page 45**


13 FICR — Factory information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

DEVICEID[0] contains the least significant bits of the device

identifier. DEVICEID[1] contains the most significant bits of the

device identifier.


**13.1.5 ER[0]**

Address offset: 0x080

Encryption Root, word 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R ER Encryption Root, word n


**13.1.6 ER[1]**

Address offset: 0x084

Encryption Root, word 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R ER Encryption Root, word n


**13.1.7 ER[2]**

Address offset: 0x088

Encryption Root, word 2


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R ER Encryption Root, word n


**13.1.8 ER[3]**

Address offset: 0x08C

Encryption Root, word 3


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R ER Encryption Root, word n


**13.1.9 IR[0]**

Address offset: 0x090

Identity Root, word 0


**Page 46**


13 FICR — Factory information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R IR Identity Root, word n


**13.1.10 IR[1]**

Address offset: 0x094

Identity Root, word 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R IR Identity Root, word n


**13.1.11 IR[2]**

Address offset: 0x098

Identity Root, word 2


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R IR Identity Root, word n


**13.1.12 IR[3]**

Address offset: 0x09C

Identity Root, word 3


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R IR Identity Root, word n


**13.1.13 DEVICEADDRTYPE**

Address offset: 0x0A0

Device address type


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R DEVICEADDRTYPE Device address type

Public 0 Public address

Random 1 Random address


**13.1.14 DEVICEADDR[0]**

Address offset: 0x0A4

Device address 0


**Page 47**


13 FICR — Factory information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R DEVICEADDR 48 bit device address


DEVICEADDR[0] contains the least significant bits of the device

address. DEVICEADDR[1] contains the most significant bits of

the device address. Only bits [15:0] of DEVICEADDR[1] are used.


**13.1.15 DEVICEADDR[1]**

Address offset: 0x0A8

Device address 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R DEVICEADDR 48 bit device address


DEVICEADDR[0] contains the least significant bits of the device

address. DEVICEADDR[1] contains the most significant bits of

the device address. Only bits [15:0] of DEVICEADDR[1] are used.


**13.1.16 INFO.PART**

Address offset: 0x100

Part code


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00052832** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **1** **0** **1** **0** **0** **0** **0** **0** **1** **1** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R PART Part code

N52832 0x52832 nRF52832

Unspecified 0xFFFFFFFF Unspecified


**13.1.17 INFO.VARIANT**

Address offset: 0x104

Part Variant, Hardware version and Production configuration


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x41414142** **0** **1** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R VARIANT Part Variant, Hardware version and Production configuration,

encoded as ASCII

AAAA 0x41414141 AAAA

AAAC 0x41414143 AAAC

AABA 0x41414241 AABA

AABB 0x41414242 AABB

AAB0 0x41414230 AAB0

ABB0 0x41424230 ABB0

AAE0 0x41414530 AAE0

ABE0 0x41424530 ABE0

AAGB 0x41414742 AAGB

ABGB 0x41424742 ABGB

AAG0 0x41414730 AAG0

ABG0 0x41424730 ABG0


**Page 48**


13 FICR — Factory information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x41414142** **0** **1** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Unspecified 0xFFFFFFFF Unspecified


**13.1.18 INFO.PACKAGE**

Address offset: 0x108

Package option


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00002000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R PACKAGE Package option

QF 0x2000 QFxx - 48-pin QFN

CH 0x2001 CHxx - 7x8 WLCSP 56 balls

CI 0x2002 CIxx - 7x8 WLCSP 56 balls

CK 0x2005 CKxx - 7x8 WLCSP 56 balls with backside coating for light

protection

Unspecified 0xFFFFFFFF Unspecified


**13.1.19 INFO.RAM**

Address offset: 0x10C

RAM variant


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000040** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R RAM RAM variant

K16 0x10 16 kByte RAM

K32 0x20 32 kByte RAM

K64 0x40 64 kByte RAM

Unspecified 0xFFFFFFFF Unspecified


**13.1.20 INFO.FLASH**

Address offset: 0x110

Flash variant


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000200** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R FLASH Flash variant

K128 0x80 128 kByte FLASH

K256 0x100 256 kByte FLASH

K512 0x200 512 kByte FLASH

Unspecified 0xFFFFFFFF Unspecified


**13.1.21 TEMP.A0**

Address offset: 0x404

Slope definition A0.


**Page 49**


13 FICR — Factory information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x00000320** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **0** **1** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R A A (slope definition) register.


**13.1.22 TEMP.A1**

Address offset: 0x408

Slope definition A1.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x00000343** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **1** **0** **0** **0** **0** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R A A (slope definition) register.


**13.1.23 TEMP.A2**

Address offset: 0x40C

Slope definition A2.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x0000035D** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **1** **0** **1** **1** **1** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R A A (slope definition) register.


**13.1.24 TEMP.A3**

Address offset: 0x410

Slope definition A3.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x00000400** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R A A (slope definition) register.


**13.1.25 TEMP.A4**

Address offset: 0x414

Slope definition A4.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x00000452** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **1** **0** **1** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R A A (slope definition) register.


**13.1.26 TEMP.A5**

Address offset: 0x418

Slope definition A5.


**Page 50**


13 FICR — Factory information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x0000037B** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **1** **1** **1** **1** **0** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R A A (slope definition) register.


**13.1.27 TEMP.B0**

Address offset: 0x41C

y-intercept B0.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00003FCC** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **0** **0** **1** **1** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R B B (y-intercept)


**13.1.28 TEMP.B1**

Address offset: 0x420

y-intercept B1.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00003F98** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **0** **0** **1** **1** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R B B (y-intercept)


**13.1.29 TEMP.B2**

Address offset: 0x424

y-intercept B2.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00003F98** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **0** **0** **1** **1** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R B B (y-intercept)


**13.1.30 TEMP.B3**

Address offset: 0x428

y-intercept B3.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00000012** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R B B (y-intercept)


**13.1.31 TEMP.B4**

Address offset: 0x42C

y-intercept B4.


**Page 51**


13 FICR — Factory information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x0000004D** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **1** **1** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R B B (y-intercept)


**13.1.32 TEMP.B5**

Address offset: 0x430

y-intercept B5.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00003E10** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **0** **0** **0** **0** **1** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R B B (y-intercept)


**13.1.33 TEMP.T0**

Address offset: 0x434

Segment end T0.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x000000E2** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R T T (segment end)register.


**13.1.34 TEMP.T1**

Address offset: 0x438

Segment end T1.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R T T (segment end)register.


**13.1.35 TEMP.T2**

Address offset: 0x43C

Segment end T2.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000014** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R T T (segment end)register.


**13.1.36 TEMP.T3**

Address offset: 0x440

Segment end T3.


**Page 52**


13 FICR — Factory information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000019** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R T T (segment end)register.


**13.1.37 TEMP.T4**

Address offset: 0x444

Segment end T4.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000050** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R T T (segment end)register.


**13.1.38 NFC.TAGHEADER0**

Address offset: 0x450

Default header for NFC Tag. Software can read these values to populate NFCID1_3RD_LAST,
NFCID1_2ND_LAST and NFCID1_LAST.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D D D D D D D D C C C C C C C C B B B B B B B B A A A A A A A A

**Reset 0xFFFFFF5F** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **0** **1** **0** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R MFGID Default Manufacturer ID: Nordic Semiconductor ASA has ICM

0x5F

B R UD1 Unique identifier byte 1

C R UD2 Unique identifier byte 2

D R UD3 Unique identifier byte 3


**13.1.39 NFC.TAGHEADER1**

Address offset: 0x454

Default header for NFC Tag. Software can read these values to populate NFCID1_3RD_LAST,
NFCID1_2ND_LAST and NFCID1_LAST.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D D D D D D D D C C C C C C C C B B B B B B B B A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R UD4 Unique identifier byte 4

B R UD5 Unique identifier byte 5

C R UD6 Unique identifier byte 6

D R UD7 Unique identifier byte 7


**13.1.40 NFC.TAGHEADER2**

Address offset: 0x458

Default header for NFC Tag. Software can read these values to populate NFCID1_3RD_LAST,
NFCID1_2ND_LAST and NFCID1_LAST.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D D D D D D D D C C C C C C C C B B B B B B B B A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R UD8 Unique identifier byte 8


**Page 53**


13 FICR — Factory information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D D D D D D D D C C C C C C C C B B B B B B B B A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

B R UD9 Unique identifier byte 9

C R UD10 Unique identifier byte 10

D R UD11 Unique identifier byte 11


**13.1.41 NFC.TAGHEADER3**

Address offset: 0x45C

Default header for NFC Tag. Software can read these values to populate NFCID1_3RD_LAST,
NFCID1_2ND_LAST and NFCID1_LAST.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D D D D D D D D C C C C C C C C B B B B B B B B A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R UD12 Unique identifier byte 12

B R UD13 Unique identifier byte 13

C R UD14 Unique identifier byte 14

D R UD15 Unique identifier byte 15


**Page 54**


14 UICR — User information configuration
registers

#### **14 UICR — User information configuration registers**


The user information configuration registers (UICRs) are non-volatile memory (NVM) registers for configuring
user specific settings.

For information on writing UICR registers, see the _NVMC — Non-volatile memory controller_ on page 30 and
_Memory_ on page 24 chapters.

###### **14.1 Registers**


**Table 19: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x10001000 UICR UICR User Information Configuration


**Table 20: Register Overview**


**Register** **Offset** **Description**

0x000 Reserved

0x004 Reserved

0x008 Reserved

0x010 Reserved

_NRFFW[0]_ 0x014 Reserved for Nordic firmware design

_NRFFW[1]_ 0x018 Reserved for Nordic firmware design

_NRFFW[2]_ 0x01C Reserved for Nordic firmware design

_NRFFW[3]_ 0x020 Reserved for Nordic firmware design

_NRFFW[4]_ 0x024 Reserved for Nordic firmware design

_NRFFW[5]_ 0x028 Reserved for Nordic firmware design

_NRFFW[6]_ 0x02C Reserved for Nordic firmware design

_NRFFW[7]_ 0x030 Reserved for Nordic firmware design

_NRFFW[8]_ 0x034 Reserved for Nordic firmware design

_NRFFW[9]_ 0x038 Reserved for Nordic firmware design

_NRFFW[10]_ 0x03C Reserved for Nordic firmware design

_NRFFW[11]_ 0x040 Reserved for Nordic firmware design

_NRFFW[12]_ 0x044 Reserved for Nordic firmware design

_NRFFW[13]_ 0x048 Reserved for Nordic firmware design

_NRFFW[14]_ 0x04C Reserved for Nordic firmware design

_NRFHW[0]_ 0x050 Reserved for Nordic hardware design

_NRFHW[1]_ 0x054 Reserved for Nordic hardware design

_NRFHW[2]_ 0x058 Reserved for Nordic hardware design

_NRFHW[3]_ 0x05C Reserved for Nordic hardware design

_NRFHW[4]_ 0x060 Reserved for Nordic hardware design

_NRFHW[5]_ 0x064 Reserved for Nordic hardware design

_NRFHW[6]_ 0x068 Reserved for Nordic hardware design

_NRFHW[7]_ 0x06C Reserved for Nordic hardware design

_NRFHW[8]_ 0x070 Reserved for Nordic hardware design

_NRFHW[9]_ 0x074 Reserved for Nordic hardware design

_NRFHW[10]_ 0x078 Reserved for Nordic hardware design

_NRFHW[11]_ 0x07C Reserved for Nordic hardware design

_CUSTOMER[0]_ 0x080 Reserved for customer

_CUSTOMER[1]_ 0x084 Reserved for customer

_CUSTOMER[2]_ 0x088 Reserved for customer

_CUSTOMER[3]_ 0x08C Reserved for customer

_CUSTOMER[4]_ 0x090 Reserved for customer

_CUSTOMER[5]_ 0x094 Reserved for customer

_CUSTOMER[6]_ 0x098 Reserved for customer


**Page 55**


14 UICR — User information configuration
registers


**Register** **Offset** **Description**

_CUSTOMER[7]_ 0x09C Reserved for customer

_CUSTOMER[8]_ 0x0A0 Reserved for customer

_CUSTOMER[9]_ 0x0A4 Reserved for customer

_CUSTOMER[10]_ 0x0A8 Reserved for customer

_CUSTOMER[11]_ 0x0AC Reserved for customer

_CUSTOMER[12]_ 0x0B0 Reserved for customer

_CUSTOMER[13]_ 0x0B4 Reserved for customer

_CUSTOMER[14]_ 0x0B8 Reserved for customer

_CUSTOMER[15]_ 0x0BC Reserved for customer

_CUSTOMER[16]_ 0x0C0 Reserved for customer

_CUSTOMER[17]_ 0x0C4 Reserved for customer

_CUSTOMER[18]_ 0x0C8 Reserved for customer

_CUSTOMER[19]_ 0x0CC Reserved for customer

_CUSTOMER[20]_ 0x0D0 Reserved for customer

_CUSTOMER[21]_ 0x0D4 Reserved for customer

_CUSTOMER[22]_ 0x0D8 Reserved for customer

_CUSTOMER[23]_ 0x0DC Reserved for customer

_CUSTOMER[24]_ 0x0E0 Reserved for customer

_CUSTOMER[25]_ 0x0E4 Reserved for customer

_CUSTOMER[26]_ 0x0E8 Reserved for customer

_CUSTOMER[27]_ 0x0EC Reserved for customer

_CUSTOMER[28]_ 0x0F0 Reserved for customer

_CUSTOMER[29]_ 0x0F4 Reserved for customer

_CUSTOMER[30]_ 0x0F8 Reserved for customer

_CUSTOMER[31]_ 0x0FC Reserved for customer

_PSELRESET[0]_ 0x200 Mapping of the nRESET function (see POWER chapter for details)

_PSELRESET[1]_ 0x204 Mapping of the nRESET function (see POWER chapter for details)

_APPROTECT_ 0x208 Access port protection

_NFCPINS_ 0x20C Setting of pins dedicated to NFC functionality: NFC antenna or GPIO


**14.1.1 NRFFW[0]**

Address offset: 0x014

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.2 NRFFW[1]**

Address offset: 0x018

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.3 NRFFW[2]**

Address offset: 0x01C

Reserved for Nordic firmware design


**Page 56**


14 UICR — User information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.4 NRFFW[3]**

Address offset: 0x020

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.5 NRFFW[4]**

Address offset: 0x024

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.6 NRFFW[5]**

Address offset: 0x028

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.7 NRFFW[6]**

Address offset: 0x02C

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.8 NRFFW[7]**

Address offset: 0x030

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**Page 57**


14 UICR — User information configuration
registers


**14.1.9 NRFFW[8]**

Address offset: 0x034

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.10 NRFFW[9]**

Address offset: 0x038

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.11 NRFFW[10]**

Address offset: 0x03C

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.12 NRFFW[11]**

Address offset: 0x040

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.13 NRFFW[12]**

Address offset: 0x044

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.14 NRFFW[13]**

Address offset: 0x048

Reserved for Nordic firmware design


**Page 58**


14 UICR — User information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.15 NRFFW[14]**

Address offset: 0x04C

Reserved for Nordic firmware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFFW Reserved for Nordic firmware design


**14.1.16 NRFHW[0]**

Address offset: 0x050

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.17 NRFHW[1]**

Address offset: 0x054

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.18 NRFHW[2]**

Address offset: 0x058

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.19 NRFHW[3]**

Address offset: 0x05C

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**Page 59**


14 UICR — User information configuration
registers


**14.1.20 NRFHW[4]**

Address offset: 0x060

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.21 NRFHW[5]**

Address offset: 0x064

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.22 NRFHW[6]**

Address offset: 0x068

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.23 NRFHW[7]**

Address offset: 0x06C

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.24 NRFHW[8]**

Address offset: 0x070

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.25 NRFHW[9]**

Address offset: 0x074

Reserved for Nordic hardware design


**Page 60**


14 UICR — User information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.26 NRFHW[10]**

Address offset: 0x078

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.27 NRFHW[11]**

Address offset: 0x07C

Reserved for Nordic hardware design


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NRFHW Reserved for Nordic hardware design


**14.1.28 CUSTOMER[0]**

Address offset: 0x080

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.29 CUSTOMER[1]**

Address offset: 0x084

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.30 CUSTOMER[2]**

Address offset: 0x088

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**Page 61**


14 UICR — User information configuration
registers


**14.1.31 CUSTOMER[3]**

Address offset: 0x08C

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.32 CUSTOMER[4]**

Address offset: 0x090

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.33 CUSTOMER[5]**

Address offset: 0x094

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.34 CUSTOMER[6]**

Address offset: 0x098

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.35 CUSTOMER[7]**

Address offset: 0x09C

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.36 CUSTOMER[8]**

Address offset: 0x0A0

Reserved for customer


**Page 62**


14 UICR — User information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.37 CUSTOMER[9]**

Address offset: 0x0A4

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.38 CUSTOMER[10]**

Address offset: 0x0A8

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.39 CUSTOMER[11]**

Address offset: 0x0AC

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.40 CUSTOMER[12]**

Address offset: 0x0B0

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.41 CUSTOMER[13]**

Address offset: 0x0B4

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**Page 63**


14 UICR — User information configuration
registers


**14.1.42 CUSTOMER[14]**

Address offset: 0x0B8

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.43 CUSTOMER[15]**

Address offset: 0x0BC

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.44 CUSTOMER[16]**

Address offset: 0x0C0

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.45 CUSTOMER[17]**

Address offset: 0x0C4

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.46 CUSTOMER[18]**

Address offset: 0x0C8

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.47 CUSTOMER[19]**

Address offset: 0x0CC

Reserved for customer


**Page 64**


14 UICR — User information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.48 CUSTOMER[20]**

Address offset: 0x0D0

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.49 CUSTOMER[21]**

Address offset: 0x0D4

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.50 CUSTOMER[22]**

Address offset: 0x0D8

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.51 CUSTOMER[23]**

Address offset: 0x0DC

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.52 CUSTOMER[24]**

Address offset: 0x0E0

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**Page 65**


14 UICR — User information configuration
registers


**14.1.53 CUSTOMER[25]**

Address offset: 0x0E4

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.54 CUSTOMER[26]**

Address offset: 0x0E8

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.55 CUSTOMER[27]**

Address offset: 0x0EC

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.56 CUSTOMER[28]**

Address offset: 0x0F0

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.57 CUSTOMER[29]**

Address offset: 0x0F4

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.58 CUSTOMER[30]**

Address offset: 0x0F8

Reserved for customer


**Page 66**


14 UICR — User information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.59 CUSTOMER[31]**

Address offset: 0x0FC

Reserved for customer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CUSTOMER Reserved for customer


**14.1.60 PSELRESET[0]**

Address offset: 0x200

Mapping of the nRESET function (see POWER chapter for details)

All PSELRESET registers have to contain the same value for a pin mapping to be valid. If values are not
the same, there will be no nRESET function exposed on a GPIO. As a result, the device will always start
independently of the levels present on any of the GPIOs.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN 21 GPIO number P0.n onto which Reset is exposed

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**14.1.61 PSELRESET[1]**

Address offset: 0x204

Mapping of the nRESET function (see POWER chapter for details)

All PSELRESET registers have to contain the same value for a pin mapping to be valid. If values are not
the same, there will be no nRESET function exposed on a GPIO. As a result, the device will always start
independently of the levels present on any of the GPIOs.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN 21 GPIO number P0.n onto which Reset is exposed

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**14.1.62 APPROTECT**

Address offset: 0x208

Access port protection


**Page 67**


14 UICR — User information configuration
registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PALL Enable or disable access port protection.


See _Debug and trace_ on page 73 for more information.

Disabled 0xFF Hardware disable of access port protection for devices where

access port protection is controlled by hardware

HwDisabled 0x5A Hardware disable of access port protection for devices where

access port protection is controlled by hardware and software

Enabled 0x00 Enable


**14.1.63 NFCPINS**

Address offset: 0x20C

Setting of pins dedicated to NFC functionality: NFC antenna or GPIO


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PROTECT Setting of pins dedicated to NFC functionality

Disabled 0 Operation as GPIO pins. Same protection as normal GPIO pins.

NFC 1 Operation as NFC antenna pins. Configures the protection for

NFC operation.


**Page 68**


15 Peripheral interface

#### **15 Peripheral interface**


Peripherals are controlled by the CPU by writing to configuration registers and task registers. Peripheral
events are indicated to the CPU by event registers and interrupts if they are configured for a given event.


Task signal from PPI


Peripheral


TASK


write


OR


task


Peripheral

core


event


Event signal to PPI


**Figure 10: Tasks, events, shortcuts, and interrupts**

###### **15.1 Peripheral ID**


k SHORTS


INTEN m


EVENT m


IRQ signal to NVIC


Every peripheral is assigned a fixed block of 0x1000 bytes of address space, which is equal to 1024 x 32 bit
registers.

See _Instantiation_ on page 25 for more information about which peripherals are available and where they are
located in the address map.

There is a direct relationship between the peripheral ID and base address. For example, a peripheral with
base address 0x40000000 is assigned ID=0, a peripheral with base address 0x40001000 is assigned ID=1,
and a peripheral with base address 0x4001F000 is assigned ID=31.

Peripherals may share the same ID, which may impose one or more of the following limitations:

- Some peripherals share some registers or other common resources.

- Operation is mutually exclusive. Only one of the peripherals can be used at a time.

- Switching from one peripheral to another must follow a specific pattern (disable the first, then enable the
second peripheral).

###### **15.2 Peripherals with shared ID**

In general, and with the exception of ID 0, peripherals sharing an ID and base address may not be used
simultaneously. The user can only enable one at the time on this specific ID.

When switching between two peripherals that share an ID, the user should do the following to prevent
unwanted behavior:

- Disable the previously used peripheral


**Page 69**


15 Peripheral interface


- Remove any PPI connections set up for the peripheral that is being disabled

- Clear all bits in the INTEN register, i.e. INTENCLR = 0xFFFFFFFF.

- Explicitly configure the peripheral that you enable and do not rely on configuration values that may be
inherited from the peripheral that was disabled.

- Enable the now configured peripheral.

For each of the rows in the following table, the instance ID listed is shared by the peripherals in the same
row.


**Table 21: Peripherals sharing an ID**


**Instance**
**ID 2 (0x40002000)** UARTE UART

 **ID 3 (0x40003000)** SPIM SPIS SPI TWIM TWIS TWI
**ID 4 (0x40004000)** SPIM SPIS SPI TWIM TWIS TWI
**ID 35 (0x40023000)** SPIM SPIS SPI

 **ID 15 (0x4000F000)** AAR CCM

 **ID 19 (0x40013000)** COMP LPCOMP

 **ID 20 (0x40014000)** SWI EGU
**ID 21 (0x40015000)** SWI EGU
**ID 22 (0x40016000)** SWI EGU
**ID 23 (0x40017000)** SWI EGU
**ID 24 (0x40018000)** SWI EGU
**ID 25 (0x40019000)** SWI EGU

###### **15.3 Peripheral registers**

Most peripherals feature an ENABLE register. Unless otherwise specified in the relevant chapter, the
peripheral registers (in particular the PSEL registers) must be configured before enabling the peripheral.

Note that the peripheral must be enabled before tasks and events can be used.

###### **15.4 Bit set and clear**

Registers with multiple single-bit bit fields may implement the "set-and-clear" pattern. This pattern enables
firmware to set and clear individual bits in a register without having to perform a read-modify-write operation
on the main register.

This pattern is implemented using three consecutive addresses in the register map where the main register
is followed by a dedicated SET and CLR register in that order.

The SET register is used to set individual bits in the main register while the CLR register is used to clear
individual bits in the main register. Writing a '1' to a bit in the SET or CLR register will set or clear the same
bit in the main register respectively. Writing a '0' to a bit in the SET or CLR register has no effect. Reading
the SET or CLR registers returns the value of the main register.

**Restriction:** The main register may not be visible and hence not directly accessible in all cases.

###### **15.5 Tasks**

Tasks are used to trigger actions in a peripheral, for example, to start a particular behavior. A peripheral can
implement multiple tasks with each task having a separate register in that peripheral's task register group.

A task is triggered when firmware writes a '1' to the task register or when the peripheral itself or another
peripheral toggles the corresponding task signal. See _Figure 10: Tasks, events, shortcuts, and interrupts_ on
page 69.


**Page 70**


15 Peripheral interface

###### **15.6 Events**

Events are used to notify peripherals and the CPU about events that have happened, for example, a state
change in a peripheral. A peripheral may generate multiple events with each event having a separate
register in that peripheral’s event register group.

An event is generated when the peripheral itself toggles the corresponding event signal, and the event
register is updated to reflect that the event has been generated. See _Figure 10: Tasks, events, shortcuts,_
_and interrupts_ on page 69. An event register is only cleared when firmware writes a '0' to it.

Events can be generated by the peripheral even when the event register is set to '1'.

###### **15.7 Shortcuts**

A shortcut is a direct connection between an event and a task within the same peripheral. If a shortcut is
enabled, its associated task is automatically triggered when its associated event is generated.

Using a shortcut is the equivalent to making the same connection outside the peripheral and through the
PPI. However, the propagation delay through the shortcut is usually shorter than the propagation delay
through the PPI.

Shortcuts are predefined, which means their connections cannot be configured by firmware. Each shortcut
can be individually enabled or disabled through the shortcut register, one bit per shortcut, giving a maximum
of 32 shortcuts for each peripheral.

###### **15.8 Interrupts**

All peripherals support interrupts. Interrupts are generated by events.

A peripheral only occupies one interrupt, and the interrupt number follows the peripheral ID. For example, the
peripheral with ID=4 is connected to interrupt number 4 in the Nested Vectored Interrupt Controller (NVIC).

Using the INTEN, INTENSET and INTENCLR registers, every event generated by a peripheral can be
configured to generate that peripheral’s interrupt. Multiple events can be enabled to generate interrupts
simultaneously. To resolve the correct interrupt source, the event registers in the event group of peripheral
registers will indicate the source.

Some peripherals implement only INTENSET and INTENCLR, and the INTEN register is not available
on those peripherals. Refer to the individual chapters for details. In all cases, however, reading back the
INTENSET or INTENCLR register returns the same information as in INTEN.

Each event implemented in the peripheral is associated with a specific bit position in the INTEN, INTENSET
and INTENCLR registers.

The relationship between tasks, events, shortcuts, and interrupts is shown in _Figure 10: Tasks, events,_
_shortcuts, and interrupts_ on page 69.


**15.8.1 Interrupt clearing**

When clearing an interrupt by writing "0" to an event register, or disabling an interrupt using the INTENCLR
register, it can take up to four CPU clock cycles to take effect. This means that an interrupt may reoccur
immediatelly even if a new event has not come, if the program exits an interrupt handler after the interrupt is
cleared or disabled, but before four clock cycles have passed.

**Important:** To avoid an interrupt reoccurring before a new event has come, the program should
perform a read from one of the peripheral registers, for example, the event register that has been
cleared, or the INTENCLR register that has been used to disable the interrupt.

This will cause a one to three-cycle delay and ensure the interrupt is cleared before exiting the interrupt
handler. Care should be taken to ensure the compiler does not remove the read operation as an
optimization. If the program can guarantee a four-cycle delay after event clear or interrupt disable another
way, then a read of a register is not required.


**Page 71**


15 Peripheral interface


**Page 72**


16 Debug and trace

#### **16 Debug and trace**


The debug and trace system offers a flexible and powerful mechanism for non-intrusive debugging.


DAP


SW-DP


CxxxPWRUPREQ


CxxxPWRUPRACK


TRACECLK

TRACEDATA[0] / SWO


TRACEDATA[1]


TRACEDATA[2]


DAP bus
interconnect


POWER


TPIU


Access Port Protection Enable


CPU


External
debugger


SWDCLK


SWDIO


&


AHB


APB/AHB


NVMC


UICR


APPROTECT


RAM & flash


Peripherals


CTRL-AP


AHB-AP


Power


Trace


ETM


ITM


ARM Cortex-M4


TRACEDATA[3] Trace


**Figure 11: Debug and trace overview**


The main features of the debug and trace system are the following:

- Two-pin serial wire debug (SWD) interface

- Flash patch and breakpoint (FPB) unit that supports the following comparators:

  - Two literal comparators

  - Six instruction comparators

- Data watchpoint and trace (DWT) unit with four comparators

- Instrumentation trace macrocell (ITM)

- Embedded trace macrocell (ETM)

- Trace port interface unit (TPIU)

  - 4-bit parallel trace of ITM and ETM trace data

  - Serial wire output (SWO) trace of ITM data

###### **16.1 DAP - Debug access port**

An external debugger can access the device via the DAP.

The debug access port (DAP) implements a standard ARM [®] CoreSight [™] serial wire debug port (SW-DP),
which implements the serial wire debug protocol (SWD). SWD is a two-pin serial interface, see SWDCLK
and SWDIO in _Figure 11: Debug and trace overview_ on page 73.

In addition to the default access port in CPU (AHB-AP), the DAP includes a custom control access port
(CTRL-AP). The CTRL-AP is described in more detail in _CTRL-AP - Control access port_ on page 76.

**Note:**

- The SWDIO line has an internal pull-up resistor.

- The SWDCLK line has an internal pull-down resistor.

###### **16.2 Access port protection**

Access port protection blocks the debugger from read and write access to all CPU registers and memorymapped addresses when enabled.


**Page 73**


16 Debug and trace


Access port protection is enabled and disabled differently depending on the build code of the device.


**16.2 Access port protection controlled by hardware**

This information refers to build codes Fxx and earlier.

By default, access port protection is disabled.

Access port protection is enabled by writing _UICR.APPROTECT_ to `Enabled` and performing any reset. See
_Reset_ on page 85 for more information.

Access port protection is disabled by issuing an ERASEALL command via CTRL-AP. This command will
erase the flash, UICR, and RAM, including _UICR.APPROTECT_ . Erasing UICR will set _UICR.APPROTECT_
value to `Disabled` . CTRL-AP is described in more detail in _CTRL-AP - Control access port_ on page 76.


**16.2 Access port protection controlled by hardware and software**

This information refers to build codes Gxx and later.

By default, access port protection is enabled.

Access port protection is disabled by issuing an ERASEALL command via CTRL-AP. Read _CTRL-_
_AP.APPROTECTSTATUS_ to ensure that access port protection is disabled, and repeat the ERASEALL
command if needed. This command will erase the flash, UICR, and RAM. CTRL-AP is described in more
detail in _CTRL-AP - Control access port_ on page 76. Access port protection will remain disabled until one
of the following occurs:

- Pin reset

- Power or brownout reset

- Watchdog reset if not in Debug Interface Mode, see _Debug Interface mode_ on page 77

- Wake from System OFF if not in Emulated System OFF

To keep access port protection disabled, the following actions must be performed:

- Program _UICR.APPROTECT_ to `HwDisabled` . This disables the hardware part of the access port
protection scheme after the first reset of any type. The hardware part of the access port protection will
stay disabled as long as UICR.APPROTECT is not overwritten.

- Firmware must write _APPROTECT.DISABLE_ to `SwDisable` . This disables the software part of the
access port protection scheme.

**Note:** Register _APPROTECT.DISABLE_ is reset after pin reset, power or brownout reset, watchdog
reset, or wake from System OFF as mentioned above.

The following figure is an example on how a device with access port protection enabled can be erased,
programmed, and configured to allow debugging. Operations sent from debugger as well as registers written
by firmware will affect the access port state.


Closed Open Closed


Open


Debugger


Access port state


Firmware


**Figure 12: Access port unlocking**


Write APPROTECT.DISABLE =

SwDisable


**Page 74**


16 Debug and trace


Access port protection is enabled when the disabling conditions are not present. For additional security,
it is recommended to write `Enabled` to _UICR.APPROTECT_, and have firmware write `Force` to
_APPROTECT.FORCEPROTECT_ . This is illustrated in the following figure.

**Note:** Register _APPROTECT.FORCEPROTECT_ is reset after any reset.


Closed Open Closed


Debugger


Access port state


Write APPROTECT.FORCEPROTECT =

Force

Firmware


**Figure 13: Force access port protection**


**16.2.1 Registers**


**Table 22: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40000000 APPROTECT APPROTECT APPROTECT control


**Table 23: Register Overview**


**Register** **Offset** **Description**

_FORCEPROTECT_ 0x550 Software force enable APPROTECT mechanism until next reset.


This register can only be written once.

_DISABLE_ 0x558 Software disable APPROTECT mechanism


**FORCEPROTECT**

Address offset: 0x550

Software force enable APPROTECT mechanism until next reset.

This register can only be written once.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW FORCEPROTECT Write 0x0 to force enable APPROTECT mechanism

Force 0x0 Software force enable APPROTECT mechanism


**DISABLE**

Address offset: 0x558

Software disable APPROTECT mechanism


**Page 75**


16 Debug and trace


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DISABLE Software disable APPROTECT mechanism

SwDisable 0x5A Software disable APPROTECT mechanism

###### **16.3 CTRL-AP - Control access port**

The control access port (CTRL-AP) is a custom access port that enables control of the device when other
access ports in the DAP are disabled by the access port protection.

Access port protection is described in more detail in _Access port protection_ on page 73.

Control access port has the following features:

- Soft reset - see _Reset_ on page 85 for more information

- Disabling of access port protection - device control is allowed through CTRL-AP even when all other
access ports in DAP are disabled by access port protection


**16.3.1 Registers**


**Table 24: Register Overview**


**Register** **Offset** **Description**

_RESET_ 0x000 Soft reset triggered through CTRL-AP

_ERASEALL_ 0x004 Erase all

_ERASEALLSTATUS_ 0x008 Status register for the ERASEALL operation

_APPROTECTSTATUS_ 0x00C Status register for access port protection

_IDR_ 0x0FC CTRL-AP identification register, IDR


**RESET**

Address offset: 0x000

Soft reset triggered through CTRL-AP


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW RESET Soft reset triggered through CTRL-AP. See Reset behavior in

POWER chapter for more details.

NoReset 0 Reset is not active

Reset 1 Reset is active. Device is held in reset.


**ERASEALL**

Address offset: 0x004

Erase all


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W ERASEALL Erase all flash and RAM

NoOperation 0 No operation

Erase 1 Erase all flash and RAM


**ERASEALLSTATUS**

Address offset: 0x008


**Page 76**


16 Debug and trace


Status register for the ERASEALL operation


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R ERASEALLSTATUS Status register for the ERASEALL operation

Ready 0 ERASEALL is ready

Busy 1 ERASEALL is busy (on-going)


**APPROTECTSTATUS**

Address offset: 0x00C

Status register for access port protection


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R APPROTECTSTATUS Status register for access port protection

Enabled 0 Access port protection enabled

Disabled 1 Access port protection not enabled


**IDR**

Address offset: 0x0FC

CTRL-AP identification register, IDR


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E E E D D D D C C C C C C C B B B B A A A A A A A A

**Reset 0x02880000** **0** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R APID AP identification

B R CLASS Access port (AP) class

NotDefined 0x0 No defined class

MEMAP 0x8 Memory access port

C R JEP106ID JEDEC JEP106 identity code

D R JEP106CONT JEDEC JEP106 continuation code

E R REVISION Revision


**16.3.2 Electrical specification**


**Control access port**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

Rpull Internal SWDIO and SWDCLK pull up/down resistance .. .. .. kΩ

fSWDCLK SWDCLK frequency .. .. .. MHz

###### **16.4 Debug Interface mode**

Before an external debugger can access either CPU's access port (AHB-AP) or the control access port
(CTRL-AP), the debugger must first request the device to power up via CxxxPWRUPREQ in the SWJ-DP.

If the device is in System OFF when power is requested via CxxxPWRUPREQ, the system will wake up and
the DIF flag in _RESETREAS_ on page 88 will be set. The device is in the Debug Interface mode as long
as the debugger is requesting power via CxxxPWRUPREQ. Once the debugger stops requesting power
via CxxxPWRUPREQ, the device is back in normal mode. Some peripherals behave differently in Debug
Interface mode compared to normal mode. These differences are described in more detail in the chapters of
the peripherals that are affected.


**Page 77**


16 Debug and trace


When a debug session is over, the external debugger must make sure to put the device back into normal
mode since the overall power consumption is higher in Debug Interface mode than in normal mode.

For details on how to use the debug capabilities, read the debug documentation of your IDE.

###### **16.5 Real-time debug**

The nRF52832 supports real-time debugging.

Real-time debugging allows interrupts to execute to completion in real time when breakpoints are set in
Thread mode or lower priority interrupts. This enables developers to set breakpoints and single-step through
the code without the risk of real-time event-driven threads running at higher priority failing. For example,
this enables the device to continue to service the high-priority interrupts of an external controller or sensor
without failure or loss of state synchronization while the developer steps through code in a low-priority
thread.

###### **16.6 Trace**

The device supports ETM and ITM trace.

Trace data from the ETM and the ITM is sent to an external debugger via a 4-bit wide parallel trace port
interface unit (TPIU), see TRACEDATA[0] through TRACEDATA[3] and TRACECLK in _Figure 11: Debug_
_and trace overview_ on page 73.

In addition to parallel trace, the TPIU supports serial trace via the serial wire output (SWO) trace protocol.
Parallel and serial trace cannot be used at the same time. ETM trace is only supported in Parallel Trace
mode, while ITM trace is supported in both Parallel and Serial Trace modes.

For details on how to use the trace capabilities, read the debug documentation of your IDE.

TPIU's trace pins are multiplexed with GPIOs. SWO and TRACEDATA[0] use the same GPIO. See _Pin_
_assignments_ on page 14 for more information.

Trace speed is configured in register _TRACECONFIG_ on page 111. The speed of the trace pins depends
on the DRIVE setting of the GPIOs that the trace pins are multiplexed with. Only S0S1 and H0H1 drives are
suitable for debugging. S0S1 is the default DRIVE setting at reset. If parallel or serial trace port signals are
not fast enough with the default settings, all GPIOs in use for tracing should be set to high drive (H0H1). The
DRIVE setting for these GPIOs should not be overwritten by firmware during the debugging session.


**16.6.1 Electrical specification**


**Trace port**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**


Tcyc Clock period as defined by Arm in the Timing specifications for

Trace Port Physical Interface of the Embedded Trace Macrocell

Architecture Specification


**Page 78**


62.5 500 ns


17 Power and clock management

#### **17 Power and clock management**


Power and clock management in nRF52832 is optimized for ultra-low power applications.

The core of the power and clock management system is the Power Management Unit (PMU) illustrated in
_Figure 14: Power Management Unit_ on page 79.


MCU


CPU


External
Power sources


External

crystals


Internal
voltage
regulators


Internal
oscillators


PMU


Memory


Peripheral


**Figure 14: Power Management Unit**


The user application is not required to actively control power and clock, since the PMU is able to
automatically detect which resources are required by the different components in the system at any given
time. The PMU will continuously optimize the system based on this information to achieve the lowest power
consumption possible without user interaction.

###### **17.1 Current consumption scenarios**


As the system is being constantly tuned by the PMU, estimating the energy consumption of an application
can be challenging if the designer is not able to do measurements on the hardware directly. See _Electrical_
_specification_ on page 79 for application scenarios showing average current drawn from the VDD supply.

Each scenario specifies a set of active operations and conditions applying to the given scenario. _Table 25:_
_Current consumption scenarios, common conditions_ on page 79 shows the conditions used for a scenario
unless otherwise is stated in the scenario description.


**Table 25: Current consumption scenarios, common conditions**


**Condition** **Value**
VDD 3 V
Temperature 25°C
CPU WFI/WFE sleep
Peripherals All idle
Clock Not running
Regulator DCDC


**17.1.1 Electrical specification**


**Current consumption: Radio**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

IRADIO_TX0 0 dBm TX @ 1 Mb/s Bluetooth Low Energy mode, Clock = HFXO 7.1 mA


IRADIO_TX1 -40 dBm TX @ 1 Mb/s Bluetooth Low Energy mode, Clock =

HFXO


4.1 mA


IRADIO_RX0 Radio RX @ 1 Mb/s Bluetooth Low Energy mode, Clock = HFXO 6.5 mA


**Page 79**


17 Power and clock management


**Current consumption: Radio protocol configurations**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**


IS0 CPU running CoreMark from Flash, Radio 0 dBm TX @ 1 Mb/s

Bluetooth Low Energy mode, Clock = HFXO, Cache enabled

IS1 CPU running CoreMark from Flash, Radio RX @ 1 Mb/s

Bluetooth Low Energy mode, Clock = HFXO, Cache enabled


**Current consumption: Ultra-low power**


9.2 mA


9.2 mA


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

ION_RAMOFF_EVENT System ON, No RAM retention, Wake on any event 1.2 µA

ION_RAMON_EVENT System ON, Full RAM retention, Wake on any event 1.5 µA

ION_RAMOFF_RTC System ON, No RAM retention, Wake on RTC 1.9 µA

IOFF_RAMOFF_RESET System OFF, No RAM retention, Wake on reset 0.3 µA

IOFF_RAMOFF_GPIO System OFF, No RAM retention, Wake on GPIO 0.3 µA

IOFF_RAMOFF_LPCOMP System OFF, No RAM retention, Wake on LPCOMP 1.9 µA

IOFF_RAMOFF_NFC System OFF, No RAM retention, Wake on NFC field 0.7 µA

IOFF_RAMON_RESET System OFF, Full 64 kB RAM retention, Wake on reset 0.7 µA


**Page 80**


18 POWER — Power supply

#### **18 POWER — Power supply**


This device has the following power supply features:

- On-chip LDO and DC/DC regulators

- Global System ON/OFF modes

- Individual RAM section power control for all system modes

- Analog or digital pin wakeup from System OFF

- Supervisor HW to manage power on reset, brownout, and power fail

- Auto-controlled refresh modes for LDO and DC/DC regulators to maximize efficiency

- Automatic switching between LDO and DC/DC regulator based on load to maximize efficiency

**Note:** Two additional external passive components are required to use the DC/DC regulator.

###### **18.1 Regulators**


The following internal power regulator alternatives are supported:

- Internal LDO regulator

- Internal DC/DC regulator

The LDO is the default regulator.

The DC/DC regulator can be used as an alternative to the LDO regulator and is enabled through the
_DCDCEN_ on page 91 register. Using the DC/DC regulator will reduce current consumption compared to
when using the LDO regulator, but the DC/DC regulator requires an external LC filter to be connected, as
shown in _Figure 16: DC/DC regulator setup_ on page 82.


POWER


DCDCEN


REG


Supply


**Figure 15: LDO regulator setup**


DCC DEC4 GND


**Page 81**


VDD


LDO


DC/DC


1.3V System power


18 POWER — Power supply


DCDCEN


LDO


DC/DC


Supply


**Figure 16: DC/DC regulator setup**

###### **18.2 System OFF mode**


POWER


REG


VDD


1.3V System power


DCC DEC4 GND


System OFF is the deepest power saving mode the system can enter. In this mode, the system’s core
functionality is powered down and all ongoing tasks are terminated.

The device can be put into System OFF mode using the POWER register interface. When in System OFF
mode, the device can be woken up through one of the following signals:

**1.** The DETECT signal, optionally generated by the GPIO peripheral
**2.** The ANADETECT signal, optionally generated by the LPCOMP module
**3.** The SENSE signal, optionally generated by the NFC module to “wake-on-field”
**4.** A reset

When the system wakes up from System OFF mode, it gets reset. For more details, see _Reset behavior_ on
page 86.

One or more RAM sections can be retained in System OFF mode depending on the settings in the
RAM[n].POWER registers.

RAM[n].POWER are retained registers, see _Reset behavior_ . Note that these registers are usually overwritten
by the startup code provided with the nRF application examples.

Before entering System OFF mode, the user must make sure that all on-going EasyDMA transactions have
been completed. This is usually accomplished by making sure that the EasyDMA enabled peripheral is not
active when entering System OFF.


**18.2.1 Emulated System OFF mode**
If the device is in debug interface mode, System OFF will be emulated to secure that all required resources
needed for debugging are available during System OFF.

See _Debug and trace_ on page 73 for more information. Required resources needed for debugging include
the following key components: _Debug and trace_ on page 73, _CLOCK — Clock control_ on page 104,
_POWER — Power supply_ on page 81, _NVMC — Non-volatile memory controller_ on page 30, CPU, Flash,
and RAM. Since the CPU is kept on in an emulated System OFF mode, it is recommended to add an infinite
loop directly after entering System OFF, to prevent the CPU from executing code that normally should not be
executed.


**Page 82**


18 POWER — Power supply

###### **18.3 System ON mode**

System ON is the default state after power-on reset. In System ON, all functional blocks such as the CPU or
peripherals, can be in IDLE or RUN mode, depending on the configuration set by the software and the state
of the application executing.

Register _RESETREAS_ on page 88 provides information about the source that caused the wakeup or
reset.

The system can switch on and off the appropriate internal power sources, depending on how much power is
needed at any given time. The power requirement of a peripheral is directly related to its activity level, and
the activity level of a peripheral is usually raised and lowered when specific tasks are triggered or events are
generated.


**18.3.1 Sub power modes**
In System ON mode, when both the CPU and all the peripherals are in IDLE mode, the system can reside in
one of the two sub power modes.

The sub power modes are:

- Constant latency

- Low power

In constant latency mode the CPU wakeup latency and the PPI task response will be constant and kept at
a minimum. This is secured by forcing a set of base resources on while in sleep. The advantage of having
a constant and predictable latency will be at the cost of having increased power consumption. The constant
latency mode is selected by triggering the CONSTLAT task.

In low power mode the automatic power management system, described in _System ON mode_ on page
83, ensures the most efficient supply option is chosen to save the most power. The advantage of having
the lowest power possible will be at the cost of having varying CPU wakeup latency and PPI task response.
The low power mode is selected by triggering the LOWPWR task.

When the system enters System ON mode, it will, by default, reside in the low power sub-power mode.

###### **18.4 Power supply supervisor**

The power supply supervisor initializes the system at power-on and provides an early warning of impending
power failure.

In addition, the power supply supervisor puts the system in a reset state if the supply voltage is too low for
safe operation (brownout). The power supply supervisor is illustrated in _Figure 17: Power supply supervisor_
on page 84.


**Page 83**


18 POWER — Power supply


Power on reset


VBOR Brownout reset


POFWARN


R


C


Vpof


1.7V


VDD


POFCON


MUX


2.8V


**Figure 17: Power supply supervisor**


**18.4.1 Power-fail comparator**


The power-fail comparator (POF) can provide the CPU with an early warning of impending power failure. It
will not reset the system, but give the CPU time to prepare for an orderly power-down.

The comparator features a hysteresis of VHYST, as illustrated in _Figure 18: Power-fail comparator (BOR =_
_Brownout reset)_ on page 84. The threshold VPOF is set in register _POFCON_ on page 89. If the POF
is enabled and the supply voltage falls below VPOF, the POFWARN event will be generated. This event will
also be generated if the supply voltage is already below VPOF at the time the POF is enabled, or if VPOF is reconfigured to a level above the supply voltage.

If power-fail warning is enabled and the supply voltage is below VPOF the power-fail comparator will prevent
the NVMC from performing write operations to the NVM. See _NVMC — Non-volatile memory controller_ on
page 30 for more information about the NVMC.


VDD


VPOF+VHYST
VPOF


1.7V


t


BOR


**Figure 18: Power-fail comparator (BOR = Brownout reset)**


To save power, the power-fail comparator is not active in System OFF or in System ON when HFCLK is not
running.


**Page 84**


18 POWER — Power supply

###### **18.5 RAM sections**

RAM section power control is used for retention in System OFF mode and for powering down unused
sections in System ON mode.

Each RAM section can power up and down independently in both System ON and System OFF mode. See
chapter _Memory_ on page 24 for more information on RAM sections.

###### **18.6 Reset**

There are multiple sources that may trigger a reset.

After a reset has occurred, register _RESETREAS_ can be read to determine which source generated the
reset.


**18.6.1 Power-on reset**
The power-on reset generator initializes the system at power-on.

The system is held in reset state until the supply has reached the minimum operating voltage and the internal
voltage regulators have started.

A step increase in supply voltage of 300 mV or more, with rise time of 300 ms or less, within the valid supply
range, may result in a system reset.


**18.6.2 Pin reset**
A pin reset is generated when the physical reset pin on the device is asserted.

Pin reset is configured via the _PSELRESET[0]_ and _PSELRESET[1]_ registers.

**Note:** Pin reset is not available on all pins.


**18.6.3 Wakeup from System OFF mode reset**
The device is reset when it wakes up from System OFF mode.

The DAP is not reset following a wake up from System OFF mode if the device is in debug interface mode.
Refer to chapter _Debug and trace_ on page 73 for more information.


**18.6.4 Soft reset**
A soft reset is generated when the SYSRESETREQ bit of the Application Interrupt and Reset Control
Register (AIRCR register) in the ARM® core is set.

Refer to _[ARM documentation](http://infocenter.arm.com/)_ for more details.

A soft reset can also be generated via the _RESET_ on page 76 register in the CTRL-AP.


**18.6.5 Watchdog reset**
A Watchdog reset is generated when the watchdog times out.

Refer to chapter _WDT — Watchdog timer_ on page 413 for more information.


**18.6.6 Brown-out reset**
The brown-out reset generator puts the system in reset state if the supply voltage drops below the brownout
reset (BOR) threshold.

Refer to section _Power fail comparator_ on page 102 for more information.


**Page 85**


18 POWER — Power supply

###### **18.7 Retained registers**

A retained register is a register that will retain its value in System OFF mode and through a reset, depending
on reset source. See individual peripheral chapters for information of which registers are retained for the
various peripherals.

###### **18.8 Reset behavior**


**Reset source** **Reset target**


**RESETREAS**


**CPU** **Peripherals** **GPIO** **Debug** **[a]** **SWJ-DP** **RAM** **WDT** **Retained**
**registers**


CPU lockup [6] x x x
Soft reset x x x
Wakeup from System OFF mode x x
reset


x x x [7] x [8]


Watchdog reset [9] x x x x x x x
Pin reset x x x x x x x
Brownout reset x x x x x x x x x
Power on reset x x x x x x x x x


**Note:** The RAM is never reset, but depending on reset source, RAM content may be corrupted.

###### **18.9 Registers**


**Table 26: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40000000 POWER POWER Power control


**Table 27: Register Overview**


**Register** **Offset** **Description**

TASKS_CONSTLAT 0x078 Enable constant latency mode

TASKS_LOWPWR 0x07C Enable low power mode (variable latency)

EVENTS_POFWARN 0x108 Power failure warning

EVENTS_SLEEPENTER 0x114 CPU entered WFI/WFE sleep

EVENTS_SLEEPEXIT 0x118 CPU exited WFI/WFE sleep

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_RESETREAS_ 0x400 Reset reason

_RAMSTATUS_ 0x428 RAM status register Deprecated

_SYSTEMOFF_ 0x500 System OFF register

_POFCON_ 0x510 Power failure comparator configuration

_GPREGRET_ 0x51C General purpose retention register

_GPREGRET2_ 0x520 General purpose retention register

_RAMON_ 0x524 RAM on/off register (this register is retained) Deprecated

_RAMONB_ 0x554 RAM on/off register (this register is retained) Deprecated

_DCDCEN_ 0x578 DC/DC enable register

_RAM[0].POWER_ 0x900 RAM0 power control register


a All debug components excluding SWJ-DP. See _Debug and trace_ on page 73 chapter for more
information about the different debug components in the system.
6 Reset from CPU lockup is disabled if the device is in debug interface mode. CPU lockup is not possible in System
OFF.
7 The Debug components will not be reset if the device is in debug interface mode.
8 RAM is not reset on wakeup from OFF mode, but depending on settings in the RAM register parts, or the whole
RAM, may not be retained after the device has entered System OFF mode.
9 Watchdog reset is not available in System OFF.


**Page 86**


18 POWER — Power supply


**Register** **Offset** **Description**

_RAM[0].POWERSET_ 0x904 RAM0 power control set register

_RAM[0].POWERCLR_ 0x908 RAM0 power control clear register

_RAM[1].POWER_ 0x910 RAM1 power control register

_RAM[1].POWERSET_ 0x914 RAM1 power control set register

_RAM[1].POWERCLR_ 0x918 RAM1 power control clear register

_RAM[2].POWER_ 0x920 RAM2 power control register

_RAM[2].POWERSET_ 0x924 RAM2 power control set register

_RAM[2].POWERCLR_ 0x928 RAM2 power control clear register

_RAM[3].POWER_ 0x930 RAM3 power control register

_RAM[3].POWERSET_ 0x934 RAM3 power control set register

_RAM[3].POWERCLR_ 0x938 RAM3 power control clear register

_RAM[4].POWER_ 0x940 RAM4 power control register

_RAM[4].POWERSET_ 0x944 RAM4 power control set register

_RAM[4].POWERCLR_ 0x948 RAM4 power control clear register

_RAM[5].POWER_ 0x950 RAM5 power control register

_RAM[5].POWERSET_ 0x954 RAM5 power control set register

_RAM[5].POWERCLR_ 0x958 RAM5 power control clear register

_RAM[6].POWER_ 0x960 RAM6 power control register

_RAM[6].POWERSET_ 0x964 RAM6 power control set register

_RAM[6].POWERCLR_ 0x968 RAM6 power control clear register

_RAM[7].POWER_ 0x970 RAM7 power control register

_RAM[7].POWERSET_ 0x974 RAM7 power control set register

_RAM[7].POWERCLR_ 0x978 RAM7 power control clear register


**18.9.1 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW POFWARN Write '1' to Enable interrupt for POFWARN event


See _EVENTS_POFWARN_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW SLEEPENTER Write '1' to Enable interrupt for SLEEPENTER event


See _EVENTS_SLEEPENTER_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW SLEEPEXIT Write '1' to Enable interrupt for SLEEPEXIT event


See _EVENTS_SLEEPEXIT_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**18.9.2 INTENCLR**

Address offset: 0x308

Disable interrupt


**Page 87**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW POFWARN Write '1' to Disable interrupt for POFWARN event


See _EVENTS_POFWARN_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW SLEEPENTER Write '1' to Disable interrupt for SLEEPENTER event


See _EVENTS_SLEEPENTER_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW SLEEPEXIT Write '1' to Disable interrupt for SLEEPEXIT event


See _EVENTS_SLEEPEXIT_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**18.9.3 RESETREAS**

Address offset: 0x400

Reset reason

Unless cleared, the RESETREAS register will be cumulative. A field is cleared by writing '1' to it. If none of
the reset sources are flagged, this indicates that the chip was reset from the on-chip reset generator, which
will indicate a power-on-reset or a brownout reset.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW RESETPIN Reset from pin-reset detected

NotDetected 0 Not detected

Detected 1 Detected

B RW DOG Reset from watchdog detected

NotDetected 0 Not detected

Detected 1 Detected

C RW SREQ Reset from soft reset detected

NotDetected 0 Not detected

Detected 1 Detected

D RW LOCKUP Reset from CPU lock-up detected

NotDetected 0 Not detected

Detected 1 Detected

E RW OFF Reset due to wake up from System OFF mode when wakeup is

triggered from DETECT signal from GPIO

NotDetected 0 Not detected

Detected 1 Detected

F RW LPCOMP Reset due to wake up from System OFF mode when wakeup is

triggered from ANADETECT signal from LPCOMP

NotDetected 0 Not detected

Detected 1 Detected

G RW DIF Reset due to wake up from System OFF mode when wakeup is

triggered from entering into debug interface mode

NotDetected 0 Not detected

Detected 1 Detected


**Page 88**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

H RW NFC Reset due to wake up from System OFF mode by NFC field

detect

NotDetected 0 Not detected

Detected 1 Detected


**18.9.4 RAMSTATUS ( Deprecated )**

Address offset: 0x428

RAM status register

Since this register is deprecated the following substitutions have been made: RAM block 0 is equivalent to
a block comprising RAM0.S0 and RAM1.S0, RAM block 1 is equivalent to a block comprising RAM2.S0 and
RAM3.S0, RAM block 2 is equivalent to a block comprising RAM4.S0 and RAM5.S0 and RAM block 3 is
equivalent to a block comprising RAM6.S0 and RAM7.S0. A RAM block field will indicate ON as long as any
of the RAM sections associated with a block are on.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R RAMBLOCK0 RAM block 0 is on or off/powering up

Off 0 Off

On 1 On

B R RAMBLOCK1 RAM block 1 is on or off/powering up

Off 0 Off

On 1 On

C R RAMBLOCK2 RAM block 2 is on or off/powering up

Off 0 Off

On 1 On

D R RAMBLOCK3 RAM block 3 is on or off/powering up

Off 0 Off

On 1 On


**18.9.5 SYSTEMOFF**

Address offset: 0x500

System OFF register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W SYSTEMOFF Enable System OFF mode

Enter 1 Enable System OFF mode


**18.9.6 POFCON**

Address offset: 0x510

Power failure comparator configuration


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B B B B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW POF Enable or disable power failure comparator

Disabled 0 Disable


**Page 89**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B B B B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Enable

B RW THRESHOLD Power failure comparator threshold setting

V17 4 Set threshold to 1.7 V

V18 5 Set threshold to 1.8 V

V19 6 Set threshold to 1.9 V

V20 7 Set threshold to 2.0 V

V21 8 Set threshold to 2.1 V

V22 9 Set threshold to 2.2 V

V23 10 Set threshold to 2.3 V

V24 11 Set threshold to 2.4 V

V25 12 Set threshold to 2.5 V

V26 13 Set threshold to 2.6 V

V27 14 Set threshold to 2.7 V

V28 15 Set threshold to 2.8 V


**18.9.7 GPREGRET**

Address offset: 0x51C

General purpose retention register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW GPREGRET General purpose retention register


This register is a retained register


**18.9.8 GPREGRET2**

Address offset: 0x520

General purpose retention register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW GPREGRET General purpose retention register


This register is a retained register


**18.9.9 RAMON ( Deprecated )**

Address offset: 0x524

RAM on/off register (this register is retained)

Since this register is deprecated the following substitutions have been made: RAM block 0 is equivalent to
a block comprising RAM0.S0 and RAM0.S1 and RAM block 1 is equivalent to a block comprising RAM1.S0
and RAM1.S1. For new designs it is recommended to use the POWER.RAM-0.POWER and its sibling
registers instead.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x00000003** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ONRAM0 Keep RAM block 0 on or off in system ON Mode

RAM0Off 0 Off


**Page 90**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x00000003** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

RAM0On 1 On

B RW ONRAM1 Keep RAM block 1 on or off in system ON Mode

RAM1Off 0 Off

RAM1On 1 On

C RW OFFRAM0 Keep retention on RAM block 0 when RAM block is switched off

RAM0Off 0 Off

RAM0On 1 On

D RW OFFRAM1 Keep retention on RAM block 1 when RAM block is switched off

RAM1Off 0 Off

RAM1On 1 On


**18.9.10 RAMONB ( Deprecated )**

Address offset: 0x554

RAM on/off register (this register is retained)

Since this register is deprecated the following substitutions have been made: RAM block 2 is equivalent to
a block comprising RAM2.S0 and RAM2.S1 and RAM block 3 is equivalent to a block comprising RAM3.S0
and RAM3.S1. For new designs it is recommended to use the POWER.RAM-0.POWER and its sibling
registers instead.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x00000003** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ONRAM2 Keep RAM block 2 on or off in system ON Mode

RAM2Off 0 Off

RAM2On 1 On

B RW ONRAM3 Keep RAM block 3 on or off in system ON Mode

RAM3Off 0 Off

RAM3On 1 On

C RW OFFRAM2 Keep retention on RAM block 2 when RAM block is switched off

RAM2Off 0 Off

RAM2On 1 On

D RW OFFRAM3 Keep retention on RAM block 3 when RAM block is switched off

RAM3Off 0 Off

RAM3On 1 On


**18.9.11 DCDCEN**

Address offset: 0x578

DC/DC enable register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DCDCEN Enable or disable DC/DC converter

Disabled 0 Disable

Enabled 1 Enable


**18.9.12 RAM[0].POWER**

Address offset: 0x900

RAM0 power control register


**Page 91**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW S0POWER Keep RAM section S0 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S0RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

B RW S1POWER Keep RAM section S1 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S1RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

C RW S0RETENTION Keep retention on RAM section S0 when RAM section is in OFF

Off 0 Off

On 1 On

D RW S1RETENTION Keep retention on RAM section S1 when RAM section is in OFF

Off 0 Off

On 1 On


**18.9.13 RAM[0].POWERSET**

Address offset: 0x904

RAM0 power control set register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM0 on or off in System ON mode

On 1 On

B W S1POWER Keep RAM section S1 of RAM0 on or off in System ON mode

On 1 On

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

On 1 On

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

On 1 On


**18.9.14 RAM[0].POWERCLR**

Address offset: 0x908

RAM0 power control clear register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM0 on or off in System ON mode

Off 1 Off

B W S1POWER Keep RAM section S1 of RAM0 on or off in System ON mode


**Page 92**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Off 1 Off

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

Off 1 Off

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

Off 1 Off


**18.9.15 RAM[1].POWER**

Address offset: 0x910

RAM1 power control register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW S0POWER Keep RAM section S0 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S0RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

B RW S1POWER Keep RAM section S1 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S1RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

C RW S0RETENTION Keep retention on RAM section S0 when RAM section is in OFF

Off 0 Off

On 1 On

D RW S1RETENTION Keep retention on RAM section S1 when RAM section is in OFF

Off 0 Off

On 1 On


**18.9.16 RAM[1].POWERSET**

Address offset: 0x914

RAM1 power control set register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM1 on or off in System ON mode

On 1 On

B W S1POWER Keep RAM section S1 of RAM1 on or off in System ON mode

On 1 On

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

On 1 On


**Page 93**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

On 1 On


**18.9.17 RAM[1].POWERCLR**

Address offset: 0x918

RAM1 power control clear register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM1 on or off in System ON mode

Off 1 Off

B W S1POWER Keep RAM section S1 of RAM1 on or off in System ON mode

Off 1 Off

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

Off 1 Off

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

Off 1 Off


**18.9.18 RAM[2].POWER**

Address offset: 0x920

RAM2 power control register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW S0POWER Keep RAM section S0 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S0RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

B RW S1POWER Keep RAM section S1 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S1RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

C RW S0RETENTION Keep retention on RAM section S0 when RAM section is in OFF

Off 0 Off

On 1 On

D RW S1RETENTION Keep retention on RAM section S1 when RAM section is in OFF

Off 0 Off

On 1 On


**Page 94**


18 POWER — Power supply


**18.9.19 RAM[2].POWERSET**

Address offset: 0x924

RAM2 power control set register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM2 on or off in System ON mode

On 1 On

B W S1POWER Keep RAM section S1 of RAM2 on or off in System ON mode

On 1 On

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

On 1 On

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

On 1 On


**18.9.20 RAM[2].POWERCLR**

Address offset: 0x928

RAM2 power control clear register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM2 on or off in System ON mode

Off 1 Off

B W S1POWER Keep RAM section S1 of RAM2 on or off in System ON mode

Off 1 Off

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

Off 1 Off

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

Off 1 Off


**18.9.21 RAM[3].POWER**

Address offset: 0x930

RAM3 power control register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW S0POWER Keep RAM section S0 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S0RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

B RW S1POWER Keep RAM section S1 ON or OFF in System ON mode.


**Page 95**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S1RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

C RW S0RETENTION Keep retention on RAM section S0 when RAM section is in OFF

Off 0 Off

On 1 On

D RW S1RETENTION Keep retention on RAM section S1 when RAM section is in OFF

Off 0 Off

On 1 On


**18.9.22 RAM[3].POWERSET**

Address offset: 0x934

RAM3 power control set register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM3 on or off in System ON mode

On 1 On

B W S1POWER Keep RAM section S1 of RAM3 on or off in System ON mode

On 1 On

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

On 1 On

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

On 1 On


**18.9.23 RAM[3].POWERCLR**

Address offset: 0x938

RAM3 power control clear register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM3 on or off in System ON mode

Off 1 Off

B W S1POWER Keep RAM section S1 of RAM3 on or off in System ON mode

Off 1 Off

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

Off 1 Off

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

Off 1 Off


**Page 96**


18 POWER — Power supply


**18.9.24 RAM[4].POWER**

Address offset: 0x940

RAM4 power control register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW S0POWER Keep RAM section S0 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S0RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

B RW S1POWER Keep RAM section S1 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S1RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

C RW S0RETENTION Keep retention on RAM section S0 when RAM section is in OFF

Off 0 Off

On 1 On

D RW S1RETENTION Keep retention on RAM section S1 when RAM section is in OFF

Off 0 Off

On 1 On


**18.9.25 RAM[4].POWERSET**

Address offset: 0x944

RAM4 power control set register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM4 on or off in System ON mode

On 1 On

B W S1POWER Keep RAM section S1 of RAM4 on or off in System ON mode

On 1 On

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

On 1 On

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

On 1 On


**18.9.26 RAM[4].POWERCLR**

Address offset: 0x948

RAM4 power control clear register

When read, this register will return the value of the POWER register.


**Page 97**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM4 on or off in System ON mode

Off 1 Off

B W S1POWER Keep RAM section S1 of RAM4 on or off in System ON mode

Off 1 Off

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

Off 1 Off

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

Off 1 Off


**18.9.27 RAM[5].POWER**

Address offset: 0x950

RAM5 power control register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW S0POWER Keep RAM section S0 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S0RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

B RW S1POWER Keep RAM section S1 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S1RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

C RW S0RETENTION Keep retention on RAM section S0 when RAM section is in OFF

Off 0 Off

On 1 On

D RW S1RETENTION Keep retention on RAM section S1 when RAM section is in OFF

Off 0 Off

On 1 On


**18.9.28 RAM[5].POWERSET**

Address offset: 0x954

RAM5 power control set register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM5 on or off in System ON mode

On 1 On

B W S1POWER Keep RAM section S1 of RAM5 on or off in System ON mode

On 1 On


**Page 98**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

On 1 On

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

On 1 On


**18.9.29 RAM[5].POWERCLR**

Address offset: 0x958

RAM5 power control clear register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM5 on or off in System ON mode

Off 1 Off

B W S1POWER Keep RAM section S1 of RAM5 on or off in System ON mode

Off 1 Off

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

Off 1 Off

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

Off 1 Off


**18.9.30 RAM[6].POWER**

Address offset: 0x960

RAM6 power control register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW S0POWER Keep RAM section S0 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S0RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

B RW S1POWER Keep RAM section S1 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S1RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

C RW S0RETENTION Keep retention on RAM section S0 when RAM section is in OFF

Off 0 Off

On 1 On

D RW S1RETENTION Keep retention on RAM section S1 when RAM section is in OFF

Off 0 Off


**Page 99**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

On 1 On


**18.9.31 RAM[6].POWERSET**

Address offset: 0x964

RAM6 power control set register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM6 on or off in System ON mode

On 1 On

B W S1POWER Keep RAM section S1 of RAM6 on or off in System ON mode

On 1 On

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

On 1 On

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

On 1 On


**18.9.32 RAM[6].POWERCLR**

Address offset: 0x968

RAM6 power control clear register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM6 on or off in System ON mode

Off 1 Off

B W S1POWER Keep RAM section S1 of RAM6 on or off in System ON mode

Off 1 Off

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

Off 1 Off

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

Off 1 Off


**18.9.33 RAM[7].POWER**

Address offset: 0x970

RAM7 power control register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW S0POWER Keep RAM section S0 ON or OFF in System ON mode.


**Page 100**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S0RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

B RW S1POWER Keep RAM section S1 ON or OFF in System ON mode.


RAM sections are always retained when ON, but can also be

retained when OFF dependent on the settings in S1RETENTION.

All RAM sections will be OFF in System OFF mode.

Off 0 Off

On 1 On

C RW S0RETENTION Keep retention on RAM section S0 when RAM section is in OFF

Off 0 Off

On 1 On

D RW S1RETENTION Keep retention on RAM section S1 when RAM section is in OFF

Off 0 Off

On 1 On


**18.9.34 RAM[7].POWERSET**

Address offset: 0x974

RAM7 power control set register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM7 on or off in System ON mode

On 1 On

B W S1POWER Keep RAM section S1 of RAM7 on or off in System ON mode

On 1 On

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

On 1 On

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

On 1 On


**18.9.35 RAM[7].POWERCLR**

Address offset: 0x978

RAM7 power control clear register

When read, this register will return the value of the POWER register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A W S0POWER Keep RAM section S0 of RAM7 on or off in System ON mode

Off 1 Off

B W S1POWER Keep RAM section S1 of RAM7 on or off in System ON mode

Off 1 Off


**Page 101**


18 POWER — Power supply


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x0000FFFF** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

C W S0RETENTION Keep retention on RAM section S0 when RAM section is

switched off

Off 1 Off

D W S1RETENTION Keep retention on RAM section S1 when RAM section is

switched off

Off 1 Off

###### **18.10 Electrical specification**


**18.10.1 Current consumption, sleep**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

IOFF System OFF current, no RAM retention 0.3 µA

ION System ON base current, no RAM retention 1.2 µA

IRAM Additional RAM retention current per 4 KB RAM section 20 nA


**18.10.2 Device startup times**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

tPOR Time in Power on Reset after VDD reaches 1.7 V for all supply

voltages and temperatures. Dependent on supply rise time. [10]

tPOR,10us VDD rise time 10us 1 ms

tPOR,10ms VDD rise time 10ms 9 ms

tPOR,60ms VDD rise time 60ms 23 ms

tPINR If a GPIO pin is configured as reset, the maximum time taken

to pull up the pin and release reset after power on reset.

Dependent on the pin capacitive load (C) [11] : t=5RC, R = 13kOhm

tPINR,500nF C = 500nF 32.5 ms

tPINR,10uF C = 10uF 650 ms

tR2ON Time from reset to ON (CPU execute)

tR2ON,NOTCONF If reset pin not configured tPOR ms


tR2ON,CONF If reset pin configured tPOR +

tPINR


ms


tOFF2ON Time from OFF to CPU execute 16.5 µs

tIDLE2CPU Time from IDLE to CPU execute 3.0 µs


tEVTSET,CL1 Time from HW event to PPI event in Constant Latency System

ON mode

tEVTSET,CL0 Time from HW event to PPI event in Low Power System ON

mode


**18.10.3 Power fail comparator**


0.0625 µs


0.0625 µs


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

IPOF Current consumption when enabled [12] <4 µA


VPOF Nominal power level warning thresholds (falling supply voltage).

Levels are configurable between Min. and Max. in 100mV

increments.


1.7 2.8 V


VPOFTOL Threshold voltage tolerance ±1 ±5 %


10 A step increase in supply voltage of 300 mV or more, with rise time of 300 ms or less, within the valid supply
range, may result in a system reset.
11 To decrease maximum time a device could hold in reset, a strong external pullup resistor can be used.
12 To save power, POF will not operate nor consume in System OFF, or while HFCLK is not running, even if left
enabled by software


**Page 102**


18 POWER — Power supply


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

VPOFHYST Threshold voltage hysteresis 50 mV

VBOR,OFF Brown out reset voltage range SYSTEM OFF mode 1.2 1.7 V

VBOR,ON Brown out reset voltage range SYSTEM ON mode 1.5 1.7 V


**Page 103**


19 CLOCK — Clock control

#### **19 CLOCK — Clock control**


The clock control system can source the system clocks from a range of internal or external high and low
frequency oscillators and distribute them to modules based upon a module’s individual requirements. Clock
distribution is automated and grouped independently by module to limit current consumption in unused
branches of the clock tree.

Listed here are the main features for CLOCK:

- 64 MHz on-chip oscillator

- 64 MHz crystal oscillator, using external 32 MHz crystal

- 32.768 kHz +/-250 ppm RC oscillator

- 32.768 kHz crystal oscillator, using external 32.768 kHz crystal

- 32.768 kHz oscillator synthesized from 64 MHz oscillator

- Firmware (FW) override control of oscillator activity for low latency start up

- Automatic oscillator and clock control, and distribution for ultra-low power


HFCLKSTART HFCLKSTOP LFCLKSTART LFCLKSTOP


CLOCK


HFINT
Internal oscillator


PCLK1M

PCLK16M


PCLK32M


HCLK64M


PCLK32KI


HFCLK
Clock control


CAL RC oscillatorLFRC SYNT


LFCLK
Clock control


32 MHz


32.768 kHz


XC1


XC2


XL1


XL2


HFXO
Crystal oscillator


LFXO
Crystal oscillator


HFCLKSTARTED LFCLKSTARTED


**Figure 19: Clock control**

###### **19.1 HFCLK clock controller**

The HFCLK clock controller provides the following clocks to the system.

- HCLK64M: 64 MHz CPU clock

- PCLK1M: 1 MHz peripheral clock

- PCLK16M: 16 MHz peripheral clock

- PCLK32M: 32 MHz peripheral clock

The HFCLK controller supports the following high frequency clock (HFCLK) sources:

- 64 MHz internal oscillator (HFINT)

- 64 MHz crystal oscillator (HFXO)

For illustration, see _Figure 19: Clock control_ on page 104.


**Page 104**


19 CLOCK — Clock control


When the system requests one or more clocks from the HFCLK controller, the HFCLK controller will
automatically provide them. If the system does not request any clocks provided by the HFCLK controller, the
controller will enter a power saving mode.

These clocks are only available when the system is in ON mode. When the system enters ON mode, the
internal oscillator (HFINT) clock source will automatically start to be able to provide the required HFCLK
clock(s) for the system.

The HFINT will be used when HFCLK is requested and HFXO has not been started. The HFXO is started by
triggering the HFCLKSTART task and stopped using the HFCLKSTOP task. A HFCLKSTARTED event will
be generated when the HFXO has started and its frequency is stable.

The HFXO must be running to use the RADIO, NFC module or the calibration mechanism associated with
the 32.768 kHz RC oscillator.


**19.1.1 64 MHz crystal oscillator (HFXO)**
The 64 MHz crystal oscillator (HFXO) is controlled by a 32 MHz external crystal

The crystal oscillator is designed for use with an AT-cut quartz crystal in parallel resonant mode. To achieve
correct oscillation frequency, the load capacitance must match the specification in the crystal data sheet.

_Figure 20: Circuit diagram of the 64 MHz crystal oscillator_ on page 105 shows how the 32 MHz crystal is
connected to the 64 MHz crystal oscillator.

```
                XC1 XC2

```

C1 C2
32 MHz

crystal


**Figure 20: Circuit diagram of the 64 MHz crystal oscillator**


The load capacitance (CL) is the total capacitance seen by the crystal across its terminals and is given by:


C1 and C2 are ceramic SMD capacitors connected between each crystal terminal and ground. For more
information, see _Reference circuitry_ on page 550. Cpcb1 and Cpcb2 are stray capacitances on the PCB. Cpin
is the pin input capacitance on the `XC1` and `XC2` pins. See table _64 MHz crystal oscillator (HFXO)_ on page
112. The load capacitors C1 and C2 should have the same value.

For reliable operation, the crystal load capacitance, shunt capacitance, equivalent series resistance, and
drive level must comply with the specifications in table _64 MHz crystal oscillator (HFXO)_ on page 112. It is
recommended to use a crystal with lower than maximum load capacitance and/or shunt capacitance. A low
load capacitance will reduce both start up time and current consumption.


**Page 105**


19 CLOCK — Clock control

###### **19.2 LFCLK clock controller**

The system supports several low frequency clock sources.

As illustrated in _Figure 19: Clock control_ on page 104, the system supports the following low frequency
clock sources:

- 32.768 kHz RC oscillator (LFRC)

- 32.768 kHz crystal oscillator (LFXO)

- 32.768 kHz synthesized from HFCLK (LFSYNT)

The LFCLK clock is started by first selecting the preferred clock source in register _LFCLKSRC_ on page
111 and then triggering the LFCLKSTART task. If the LFXO is selected as the clock source, the LFCLK
will initially start running from the 32.768 kHz LFRC while the LFXO is starting up and automatically switch to
using the LFXO once this oscillator is running. The LFCLKSTARTED event will be generated when the LFXO
has been started.

The LFCLK clock is stopped by triggering the LFCLKSTOP task.

It is not allowed to write to register _LFCLKSRC_ on page 111 when the LFCLK is running.

A LFCLKSTOP task will stop the LFCLK oscillator. However, the LFCLKSTOP task can only be triggered
after the STATE field in register _LFCLKSTAT_ on page 110 indicates a 'LFCLK running' state.

The LFCLK clock controller and all of the LFCLK clock sources are always switched off when in OFF mode.


**19.2.1 32.768 kHz RC oscillator (LFRC)**
The default source of the low frequency clock (LFCLK) is the 32.768 kHz RC oscillator (LFRC).

The LFRC frequency will be affected by variation in temperature. The LFRC oscillator can be calibrated to
improve accuracy by using the HFXO as a reference oscillator during calibration. See Table _32.768 kHz RC_
_oscillator (LFRC)_ on page 112 for details on the default and calibrated accuracy of the LFRC oscillator.
The LFRC oscillator does not require additional external components.


**19.2.2 Calibrating the 32.768 kHz RC oscillator**
After the 32.768 kHz RC oscillator is started and running, it can be calibrated by triggering the CAL task. In
this case, the HFCLK will be temporarily switched on and used as a reference.

A DONE event will be generated when calibration has finished. The calibration mechanism will only work as
long as HFCLK is generated from the HFCLK crystal oscillator, it is therefore necessary to explicitly start this
crystal oscillator before calibration can be started, see HFCLKSTART task.


**19.2.3 Calibration timer**
The calibration timer can be used to time the calibration interval of the 32.768 kHz RC oscillator.

The calibration timer is started by triggering the CTSTART task and stopped by triggering the CTSTOP task.
The calibration timer will always start counting down from the value specified in CTIV and generate a CTTO
timeout event when it reaches 0. The Calibration timer will stop by itself when it reaches 0.


CTSTART

CTSTOP


CTTO


**Figure 21: Calibration timer**


Calibration

timer


CTIV


Due to limitations in the calibration timer, only one task related to calibration, that is, CAL, CTSTART and
CTSTOP, can be triggered for every period of LFCLK.


**Page 106**


19 CLOCK — Clock control


**19.2.4 32.768 kHz crystal oscillator (LFXO)**
For higher LFCLK accuracy (when better than +/- 250 ppm accuracy is required), the low frequency crystal
oscillator (LFXO) must be used.

The following external clock sources are supported:

- Low swing clock signal applied to the _XL1_ pin. The _XL2_ pin shall then be grounded.

- Rail-to-rail clock signal applied to the _XL1_ pin. The _XL2_ pin shall then be grounded or left unconnected.

The _LFCLKSRC_ on page 111 register controls the clock source, and its allowed swing. The truth table for
various situations is as follows:


**Table 28: LFCLKSRC configuration depending on clock source**


**SRC** **EXTERNAL** **BYPASS** **Comment**
0 0 0 Normal operation, RC is source
0 0 1 DO NOT USE
0 1 X DO NOT USE
1 0 0 Normal XTAL operation
1 1 0 Apply external low swing signal to XL1, ground XL2
1 1 1 Apply external full swing signal to XL1, leave XL2 grounded or unconnected
1 0 1 DO NOT USE
2 0 0 Normal operation, synth is source
2 0 1 DO NOT USE
2 1 X DO NOT USE


To achieve correct oscillation frequency, the load capacitance must match the specification in the crystal
data sheet. _Figure 22: Circuit diagram of the 32.768 kHz crystal oscillator_ on page 107 shows the LFXO
circuitry.

```
                        XL1 XL2

```

C1 C2
32.768 kHz

crystal


**Figure 22: Circuit diagram of the 32.768 kHz crystal oscillator**


The load capacitance (CL) is the total capacitance seen by the crystal across its terminals and is given by:


C1 and C2 are ceramic SMD capacitors connected between each crystal terminal and ground. Cpcb1 and
Cpcb2 are stray capacitances on the PCB. Cpin is the pin input capacitance on the XC1 and XC2 pins (see
_32.768 kHz crystal oscillator (LFXO)_ on page 112). The load capacitors C1 and C2 should have the same
value.

For more information, see _Reference circuitry_ on page 550.


**Page 107**


19 CLOCK — Clock control


**19.2.5 32.768 kHz synthesized from HFCLK (LFSYNT)**
LFCLK can also be synthesized from the HFCLK clock source. The accuracy of LFCLK will then be the
accuracy of the HFCLK.

Using the LFSYNT clock avoids the requirement for a 32.768 kHz crystal, but increases average power
consumption as the HFCLK will need to be requested in the system.

###### **19.3 Registers**


**Table 29: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40000000 CLOCK CLOCK Clock control


**Table 30: Register Overview**


**Register** **Offset** **Description**

TASKS_HFCLKSTART 0x000 Start HFCLK crystal oscillator

TASKS_HFCLKSTOP 0x004 Stop HFCLK crystal oscillator

TASKS_LFCLKSTART 0x008 Start LFCLK source

TASKS_LFCLKSTOP 0x00C Stop LFCLK source

TASKS_CAL 0x010 Start calibration of LFRC oscillator

TASKS_CTSTART 0x014 Start calibration timer

TASKS_CTSTOP 0x018 Stop calibration timer

EVENTS_HFCLKSTARTED 0x100 HFCLK oscillator started

EVENTS_LFCLKSTARTED 0x104 LFCLK started

EVENTS_DONE 0x10C Calibration of LFCLK RC oscillator complete event

EVENTS_CTTO 0x110 Calibration timer timeout

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_HFCLKRUN_ 0x408 Status indicating that HFCLKSTART task has been triggered

_HFCLKSTAT_ 0x40C HFCLK status

_LFCLKRUN_ 0x414 Status indicating that LFCLKSTART task has been triggered

_LFCLKSTAT_ 0x418 LFCLK status

_LFCLKSRCCOPY_ 0x41C Copy of LFCLKSRC register, set when LFCLKSTART task was triggered

_LFCLKSRC_ 0x518 Clock source for the LFCLK

_CTIV_ 0x538 Calibration timer interval Retained

_TRACECONFIG_ 0x55C Clocking options for the Trace Port debug interface


**19.3.1 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW HFCLKSTARTED Write '1' to Enable interrupt for HFCLKSTARTED event


See _EVENTS_HFCLKSTARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW LFCLKSTARTED Write '1' to Enable interrupt for LFCLKSTARTED event


See _EVENTS_LFCLKSTARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**Page 108**


19 CLOCK — Clock control


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

C RW DONE Write '1' to Enable interrupt for DONE event


See _EVENTS_DONE_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW CTTO Write '1' to Enable interrupt for CTTO event


See _EVENTS_CTTO_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**19.3.2 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW HFCLKSTARTED Write '1' to Disable interrupt for HFCLKSTARTED event


See _EVENTS_HFCLKSTARTED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW LFCLKSTARTED Write '1' to Disable interrupt for LFCLKSTARTED event


See _EVENTS_LFCLKSTARTED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW DONE Write '1' to Disable interrupt for DONE event


See _EVENTS_DONE_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW CTTO Write '1' to Disable interrupt for CTTO event


See _EVENTS_CTTO_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**19.3.3 HFCLKRUN**

Address offset: 0x408

Status indicating that HFCLKSTART task has been triggered


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R STATUS HFCLKSTART task triggered or not

NotTriggered 0 Task not triggered

Triggered 1 Task triggered


**Page 109**


19 CLOCK — Clock control


**19.3.4 HFCLKSTAT**

Address offset: 0x40C

HFCLK status


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R SRC Source of HFCLK

RC 0 64 MHz internal oscillator (HFINT)

Xtal 1 64 MHz crystal oscillator (HFXO)

B R STATE HFCLK state

NotRunning 0 HFCLK not running

Running 1 HFCLK running


**19.3.5 LFCLKRUN**

Address offset: 0x414

Status indicating that LFCLKSTART task has been triggered


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R STATUS LFCLKSTART task triggered or not

NotTriggered 0 Task not triggered

Triggered 1 Task triggered


**19.3.6 LFCLKSTAT**

Address offset: 0x418

LFCLK status


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R SRC Source of LFCLK

RC 0 32.768 kHz RC oscillator

Xtal 1 32.768 kHz crystal oscillator

Synth 2 32.768 kHz synthesized from HFCLK

B R STATE LFCLK state

NotRunning 0 LFCLK not running

Running 1 LFCLK running


**19.3.7 LFCLKSRCCOPY**

Address offset: 0x41C

Copy of LFCLKSRC register, set when LFCLKSTART task was triggered


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R SRC Clock source

RC 0 32.768 kHz RC oscillator

Xtal 1 32.768 kHz crystal oscillator

Synth 2 32.768 kHz synthesized from HFCLK


**Page 110**


19 CLOCK — Clock control


**19.3.8 LFCLKSRC**

Address offset: 0x518

Clock source for the LFCLK


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW SRC Clock source

RC 0 32.768 kHz RC oscillator

Xtal 1 32.768 kHz crystal oscillator

Synth 2 32.768 kHz synthesized from HFCLK

B RW BYPASS Enable or disable bypass of LFCLK crystal oscillator with external

clock source

Disabled 0 Disable (use with Xtal or low-swing external source)

Enabled 1 Enable (use with rail-to-rail external source)

C RW EXTERNAL Enable or disable external source for LFCLK

Disabled 0 Disable external source (use with Xtal)

Enabled 1 Enable use of external source instead of Xtal (SRC needs to be

set to Xtal)


**19.3.9 CTIV ( Retained )**

Address offset: 0x538

This register is a retained register

Calibration timer interval


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CTIV Calibration timer interval in multiple of 0.25 seconds. Range:

0.25 seconds to 31.75 seconds.


**19.3.10 TRACECONFIG**

Address offset: 0x55C

Clocking options for the Trace Port debug interface

This register is a retained register. Reset behavior is the same as debug components.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TRACEPORTSPEED Speed of Trace Port clock. Note that the TRACECLK pin will

output this clock divided by two.

32MHz 0 32 MHz Trace Port clock (TRACECLK = 16 MHz)

16MHz 1 16 MHz Trace Port clock (TRACECLK = 8 MHz)

8MHz 2 8 MHz Trace Port clock (TRACECLK = 4 MHz)

4MHz 3 4 MHz Trace Port clock (TRACECLK = 2 MHz)

B RW TRACEMUX Pin multiplexing of trace signals.

GPIO 0 GPIOs multiplexed onto all trace-pins

Serial 1 SWO multiplexed onto P0.18, GPIO multiplexed onto other

trace pins

Parallel 2 TRACECLK and TRACEDATA multiplexed onto P0.20, P0.18,

P0.16, P0.15 and P0.14.


**Page 111**


19 CLOCK — Clock control

###### **19.4 Electrical specification**


**19.4.1 64 MHz internal oscillator (HFINT)**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fNOM_HFINT Nominal output frequency 64 MHz

fTOL_HFINT Frequency tolerance <±1.5 <±6 %

IHFINT Run current 60 µA

ISTART_HFINT Average startup current I_HFINT µA

tSTART_HFINT Startup time 3 us


**19.4.2 64 MHz crystal oscillator (HFXO)**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fNOM_HFXO Nominal output frequency 64 MHz

fXTAL_HFXO External crystal frequency 32 MHz


fTOL_HFXO Frequency tolerance requirement for 2.4 GHz proprietary radio

applications

fTOL_HFXO_BLE Frequency tolerance requirement, Bluetooth low energy

applications


±60 ppm


±40 ppm


CL_HFXO Load capacitance 12 pF

C0_HFXO Shunt capacitance 7 pF

RS_HFXO_7PF Equivalent series resistance C0 = 7 pF 60 ohm

RS_HFXO_5PF Equivalent series resistance C0 = 5 pF 80 ohm

RS_HFXO_3PF Equivalent series resistance C0 = 3 pF 100 ohm

PD_HFXO Drive level 100 uW

CPIN_HFXO Input capacitance XC1 and XC2 4 pF

ISTBY_X32M Core standby current [13] 50 µA

IHFXO Run current 250 µA

ISTART_HFXO Average startup current, first 1 ms 0.4 mA

tSTART_HFXO Startup time 0.36 ms


**19.4.3 32.768 kHz RC oscillator (LFRC)**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fNOM_LFRC Nominal frequency 32.768 kHz

fTOL_LFRC Frequency tolerance ±2 %

fTOL_CAL_LFRC Frequency tolerance for LFRC after calibration [14] ±250 ppm

ILFRC Run current for 32.768 kHz RC oscillator 0.6 1 µA

tSTART_LFRC Startup time for 32.768 kHz RC oscillator 600 us


**19.4.4 32.768 kHz crystal oscillator (LFXO)**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fNOM_LFXO Crystal frequency 32.768 kHz

fTOL_LFXO_BLE Frequency tolerance requirement for BLE stack ±250 ppm

fTOL_LFXO_ANT Frequency tolerance requirement for ANT stack ±50 ppm

CL_LFXO Load capacitance 12.5 pF

C0_LFXO Shunt capacitance 2 pF

RS_LFXO Equivalent series resistance 100 kohm

PD_LFXO Drive level 1 uW

Cpin Input capacitance on XL1 and XL2 pads 4 pF

ILFXO Run current for 32.768 kHz crystal oscillator 0.25 µA


13 Current drawn if HFXO is forced on through for instance using the low latency power mode.
14 Constant temperature within ±0.5 °C and calibration performed at least every 8 seconds


**Page 112**


19 CLOCK — Clock control


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

tSTART_LFXO Startup time for 32.768 kHz crystal oscillator 0.25 s


VAMP_IN_XO_LOW Peak to peak amplitude for external low swing clock. Input

signal must not swing outside supply rails.


**19.4.5 32.768 kHz synthesized from HFCLK (LFSYNT)**


200 1000 mV


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fNOM_LFSYNT Nominal frequency 32.768 kHz

fTOL_LFSYNT Frequency tolerance in addition to HFLCK tolerance [15] 8 ppm

ILFSYNT Run current for synthesized 32.768 kHz 100 µA

tSTART_LFSYNT Startup time for synthesized 32.768 kHz 100 us


15 Frequency tolerance will be derived from the HFCLK source clock plus the LFSYNT tolerance


**Page 113**


20 GPIO — General purpose input/output

#### **20 GPIO — General purpose input/output**


The general purpose input/output (GPIO) is organized as one port with up to 32 I/Os (dependent on
package) enabling access and control of up to 32 pins through one port. Each GPIO can be accessed
individually.

GPIO has the following user-configurable features:

- Up to 32 GPIO

- 8 GPIO with Analog channels for SAADC, COMP or LPCOMP inputs

- Configurable output drive strength

- Internal pull-up and pull-down resistors

- Wake-up from high or low level triggers on all pins

- Trigger interrupt on state changes on any pin

- All pins can be used by the PPI task/event system

- One or more GPIO outputs can be controlled through PPI and GPIOTE channels

- All pins can be individually mapped to interface blocks for layout flexibility

- GPIO state changes captured on SENSE signal can be stored by LATCH register

The GPIO Port peripheral implements up to 32 pins, `PIN0` through `PIN31` . Each of these pins can be
individually configured in the PIN_CNF[n] registers (n=0..31).

The following parameters can be configured through these registers:

- Direction

- Drive strength

- Enabling of pull-up and pull-down resistors

- Pin sensing

- Input buffer disconnect

- Analog input (for selected pins)

The PIN_CNF registers are retained registers. See _POWER — Power supply_ on page 81 chapter for more
information about retained registers.

###### **20.1 Pin configuration**

Pins can be individually configured, through the SENSE field in the PIN_CNF[n] register, to detect either a
high level or a low level on their input.

When the correct level is detected on any such configured pin, the sense mechanism will set the DETECT
signal high. Each pin has a separate DETECT signal, and the default behaviour, as defined by the
DETECTMODE register, is that the DETECT signal from all pins in the GPIO Port are combined into
a common DETECT signal that is routed throughout the system, which then can be utilized by other
peripherals, see _Figure 23: GPIO Port and the GPIO pin details_ on page 115. This mechanism is functional
in both ON and OFF mode.


**Page 114**


LDETECT


20 GPIO — General purpose input/output


GPIO Port


DETECTMODE


DETECT


LATCH


ANAEN

DIR_OVERRIDE

OUT_OVERRIDE

OUT


PIN0.DETECT


PIN1.DETECT


PIN31.DETECT


IN


INPUT_OVERRIDE


ANAIN


PIN[0].OUT


Sense


PIN[0].CNF.SENSE


PIN[0].IN


PIN0


PIN[0].CNF.DRIVE


O


PIN[0].CNF.PULL


PIN[0].CNF.DIR


PIN0


PIN[0].OUT

PIN[0].IN

PIN[0].CNF


..


PIN31


PIN[31].OUT

PIN[31].IN

PIN[31].CNF


PIN0


PIN31


PIN[0].CNF.INPUT


I


O: output buffer                                  I: input buffer


**Figure 23: GPIO Port and the GPIO pin details**


_Figure 23: GPIO Port and the GPIO pin details_ on page 115 illustrates the GPIO port containing 32
individual pins, where `PIN0` is illustrated in more detail as a reference. All the signals on the left side of the
illustration are used by other peripherals in the system, and therefore, are not directly available to the CPU.

Make sure that a pin is in a level that cannot trigger the sense mechanism before enabling it. Detect will
go high immediately if the sense condition configured in the PIN_CNF registers is met when the sense
mechanism is enabled. This will trigger a PORT event if the DETECT signal was low before enabling the
sense mechanism. See _GPIOTE — GPIO tasks and events_ on page 161.

See the following peripherals for more information about how the DETECT signal is used:

- POWER: uses the DETECT signal to exit from System OFF.

- GPIOTE: uses the DETECT signal to generate the PORT event.

When a pin's PINx.DETECT signal goes high, a flag will be set in the LATCH register, e.g. when the
PIN0.DETECT signal goes high, bit 0 in the LATCH register will be set to '1'.

The LATCH register will only be cleared if the CPU explicitly clears it by writing a '1' to the bit that shall be
cleared, i.e. the LATCH register will not be affected by a PINx.DETECT signal being set low.

If the CPU performs a clear operation on a bit in the LATCH register when the associated PINx.DETECT
signal is high, the bit in the LATCH register will not be cleared.

The LDETECT signal will be set high when one or more bits in the LATCH register are '1'. The LDETECT
signal will be set low when all bits in the LATCH register are successfully cleared to '0'.

If one or more bits in the LATCH register are '1' after the CPU has performed a clear operation on the
LATCH registers, a rising edge will be generated on the LDETECT signal, this is illustrated in _Figure 24:_
_DETECT signal behavior_ on page 116.

**Important:** The CPU can read the LATCH register at any time to check if a SENSE condition has
been met on one or more of the the GPIO pins even if that condition is no longer met at the time the
CPU queries the LATCH register. This mechanism will work even if the LDETECT signal is not used
as the DETECT signal.

The LDETECT signal is by default not connected to the GPIO port's DETECT signal, but via the
DETECTMODE register it is possible to change the behaviour of the GPIO port's DETECT signal from the
default behaviour described above to instead be derived directly from the LDETECT signal, see _Figure 23:_
_GPIO Port and the GPIO pin details_ on page 115. _Figure 24: DETECT signal behavior_ on page 116
illustrates the DETECT signals behaviour for these two alternatives.


**Page 115**


20 GPIO — General purpose input/output


PIN31.DETECT


PIN1.DETECT


PIN0.DETECT


DETECT
(Default mode)


LATCH.31


LATCH.1


LATCH.0


DETECT
(LDETECT mode)






**Figure 24: DETECT signal behavior**


The input buffer of a GPIO pin can be disconnected from the pin to enable power savings when the pin is
not used as an input, see _Figure 23: GPIO Port and the GPIO pin details_ on page 115. Inputs must be
connected in order to get a valid input value in the IN register and for the sense mechanism to get access to
the pin.

Other peripherals in the system can attach themselves to GPIO pins and override their output value and
configuration, or read their analog or digital input value, see _Figure 23: GPIO Port and the GPIO pin details_
on page 115.

Selected pins also support analog input signals, see ANAIN in _Figure 23: GPIO Port and the GPIO pin_
_details_ on page 115. The assignment of the analog pins can be found in _Pin assignments_ on page 14.

**Important:** When a pin is configured as digital input, care has been taken in the nRF52832 design
to minimize increased current consumption when the input voltage is between VIL and VIH. However,
it is a good practice to ensure that the external circuitry does not drive that pin to levels between VIL
and VIH for a long period of time.

###### **20.2 GPIO located near the RADIO**

Radio performance parameters, such as sensitivity, may be affected by high frequency digital I/O with large
sink/source current close to the radio power supply and antenna pins.

Refer to _Pin assignments_ on page 14 for recommended usage guidelines to maximize radio performance in
an application.

###### **20.3 Registers**


**Table 31: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x50000000 GPIO GPIO General purpose input and output Deprecated

0x50000000 GPIO P0 General purpose input and output


**Page 116**


20 GPIO — General purpose input/output


**Table 32: Register Overview**


**Register** **Offset** **Description**

_OUT_ 0x504 Write GPIO port

_OUTSET_ 0x508 Set individual bits in GPIO port

_OUTCLR_ 0x50C Clear individual bits in GPIO port

_IN_ 0x510 Read GPIO port

_DIR_ 0x514 Direction of GPIO pins

_DIRSET_ 0x518 DIR set register

_DIRCLR_ 0x51C DIR clear register

_LATCH_ 0x520 Latch register indicating what GPIO pins that have met the criteria set in the PIN_CNF[n].SENSE

registers

_DETECTMODE_ 0x524 Select between default DETECT signal behaviour and LDETECT mode

_PIN_CNF[0]_ 0x700 Configuration of GPIO pins

_PIN_CNF[1]_ 0x704 Configuration of GPIO pins

_PIN_CNF[2]_ 0x708 Configuration of GPIO pins

_PIN_CNF[3]_ 0x70C Configuration of GPIO pins

_PIN_CNF[4]_ 0x710 Configuration of GPIO pins

_PIN_CNF[5]_ 0x714 Configuration of GPIO pins

_PIN_CNF[6]_ 0x718 Configuration of GPIO pins

_PIN_CNF[7]_ 0x71C Configuration of GPIO pins

_PIN_CNF[8]_ 0x720 Configuration of GPIO pins

_PIN_CNF[9]_ 0x724 Configuration of GPIO pins

_PIN_CNF[10]_ 0x728 Configuration of GPIO pins

_PIN_CNF[11]_ 0x72C Configuration of GPIO pins

_PIN_CNF[12]_ 0x730 Configuration of GPIO pins

_PIN_CNF[13]_ 0x734 Configuration of GPIO pins

_PIN_CNF[14]_ 0x738 Configuration of GPIO pins

_PIN_CNF[15]_ 0x73C Configuration of GPIO pins

_PIN_CNF[16]_ 0x740 Configuration of GPIO pins

_PIN_CNF[17]_ 0x744 Configuration of GPIO pins

_PIN_CNF[18]_ 0x748 Configuration of GPIO pins

_PIN_CNF[19]_ 0x74C Configuration of GPIO pins

_PIN_CNF[20]_ 0x750 Configuration of GPIO pins

_PIN_CNF[21]_ 0x754 Configuration of GPIO pins

_PIN_CNF[22]_ 0x758 Configuration of GPIO pins

_PIN_CNF[23]_ 0x75C Configuration of GPIO pins

_PIN_CNF[24]_ 0x760 Configuration of GPIO pins

_PIN_CNF[25]_ 0x764 Configuration of GPIO pins

_PIN_CNF[26]_ 0x768 Configuration of GPIO pins

_PIN_CNF[27]_ 0x76C Configuration of GPIO pins

_PIN_CNF[28]_ 0x770 Configuration of GPIO pins

_PIN_CNF[29]_ 0x774 Configuration of GPIO pins

_PIN_CNF[30]_ 0x778 Configuration of GPIO pins

_PIN_CNF[31]_ 0x77C Configuration of GPIO pins


**20.3.1 OUT**

Address offset: 0x504

Write GPIO port


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN0 Pin 0

Low 0 Pin driver is low

High 1 Pin driver is high

B RW PIN1 Pin 1


**Page 117**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Low 0 Pin driver is low

High 1 Pin driver is high

C RW PIN2 Pin 2

Low 0 Pin driver is low

High 1 Pin driver is high

D RW PIN3 Pin 3

Low 0 Pin driver is low

High 1 Pin driver is high

E RW PIN4 Pin 4

Low 0 Pin driver is low

High 1 Pin driver is high

F RW PIN5 Pin 5

Low 0 Pin driver is low

High 1 Pin driver is high

G RW PIN6 Pin 6

Low 0 Pin driver is low

High 1 Pin driver is high

H RW PIN7 Pin 7

Low 0 Pin driver is low

High 1 Pin driver is high

I RW PIN8 Pin 8

Low 0 Pin driver is low

High 1 Pin driver is high

J RW PIN9 Pin 9

Low 0 Pin driver is low

High 1 Pin driver is high

K RW PIN10 Pin 10

Low 0 Pin driver is low

High 1 Pin driver is high

L RW PIN11 Pin 11

Low 0 Pin driver is low

High 1 Pin driver is high

M RW PIN12 Pin 12

Low 0 Pin driver is low

High 1 Pin driver is high

N RW PIN13 Pin 13

Low 0 Pin driver is low

High 1 Pin driver is high

O RW PIN14 Pin 14

Low 0 Pin driver is low

High 1 Pin driver is high

P RW PIN15 Pin 15

Low 0 Pin driver is low

High 1 Pin driver is high

Q RW PIN16 Pin 16

Low 0 Pin driver is low

High 1 Pin driver is high

R RW PIN17 Pin 17

Low 0 Pin driver is low

High 1 Pin driver is high

S RW PIN18 Pin 18

Low 0 Pin driver is low

High 1 Pin driver is high

T RW PIN19 Pin 19

Low 0 Pin driver is low


**Page 118**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

High 1 Pin driver is high

U RW PIN20 Pin 20

Low 0 Pin driver is low

High 1 Pin driver is high

V RW PIN21 Pin 21

Low 0 Pin driver is low

High 1 Pin driver is high

W RW PIN22 Pin 22

Low 0 Pin driver is low

High 1 Pin driver is high

X RW PIN23 Pin 23

Low 0 Pin driver is low

High 1 Pin driver is high

Y RW PIN24 Pin 24

Low 0 Pin driver is low

High 1 Pin driver is high

Z RW PIN25 Pin 25

Low 0 Pin driver is low

High 1 Pin driver is high

a RW PIN26 Pin 26

Low 0 Pin driver is low

High 1 Pin driver is high

b RW PIN27 Pin 27

Low 0 Pin driver is low

High 1 Pin driver is high

c RW PIN28 Pin 28

Low 0 Pin driver is low

High 1 Pin driver is high

d RW PIN29 Pin 29

Low 0 Pin driver is low

High 1 Pin driver is high

e RW PIN30 Pin 30

Low 0 Pin driver is low

High 1 Pin driver is high

f RW PIN31 Pin 31

Low 0 Pin driver is low

High 1 Pin driver is high


**20.3.2 OUTSET**

Address offset: 0x508

Set individual bits in GPIO port

Read: reads value of OUT register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN0 Pin 0

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

B RW PIN1 Pin 1

Low 0 Read: pin driver is low


**Page 119**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

C RW PIN2 Pin 2

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

D RW PIN3 Pin 3

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

E RW PIN4 Pin 4

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

F RW PIN5 Pin 5

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

G RW PIN6 Pin 6

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

H RW PIN7 Pin 7

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

I RW PIN8 Pin 8

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

J RW PIN9 Pin 9

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

K RW PIN10 Pin 10

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

L RW PIN11 Pin 11

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

M RW PIN12 Pin 12

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

N RW PIN13 Pin 13

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

O RW PIN14 Pin 14

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

P RW PIN15 Pin 15


**Page 120**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

Q RW PIN16 Pin 16

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

R RW PIN17 Pin 17

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

S RW PIN18 Pin 18

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

T RW PIN19 Pin 19

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

U RW PIN20 Pin 20

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

V RW PIN21 Pin 21

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

W RW PIN22 Pin 22

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

X RW PIN23 Pin 23

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

Y RW PIN24 Pin 24

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

Z RW PIN25 Pin 25

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

a RW PIN26 Pin 26

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

b RW PIN27 Pin 27

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

c RW PIN28 Pin 28

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect


**Page 121**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

d RW PIN29 Pin 29

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

e RW PIN30 Pin 30

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect

f RW PIN31 Pin 31

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Set 1 Write: writing a '1' sets the pin high; writing a '0' has no effect


**20.3.3 OUTCLR**

Address offset: 0x50C

Clear individual bits in GPIO port

Read: reads value of OUT register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN0 Pin 0

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

B RW PIN1 Pin 1

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

C RW PIN2 Pin 2

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

D RW PIN3 Pin 3

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

E RW PIN4 Pin 4

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

F RW PIN5 Pin 5

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

G RW PIN6 Pin 6

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

H RW PIN7 Pin 7

Low 0 Read: pin driver is low

High 1 Read: pin driver is high


**Page 122**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

I RW PIN8 Pin 8

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

J RW PIN9 Pin 9

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

K RW PIN10 Pin 10

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

L RW PIN11 Pin 11

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

M RW PIN12 Pin 12

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

N RW PIN13 Pin 13

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

O RW PIN14 Pin 14

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

P RW PIN15 Pin 15

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

Q RW PIN16 Pin 16

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

R RW PIN17 Pin 17

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

S RW PIN18 Pin 18

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

T RW PIN19 Pin 19

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

U RW PIN20 Pin 20

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

V RW PIN21 Pin 21

Low 0 Read: pin driver is low


**Page 123**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

W RW PIN22 Pin 22

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

X RW PIN23 Pin 23

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

Y RW PIN24 Pin 24

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

Z RW PIN25 Pin 25

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

a RW PIN26 Pin 26

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

b RW PIN27 Pin 27

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

c RW PIN28 Pin 28

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

d RW PIN29 Pin 29

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

e RW PIN30 Pin 30

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect

f RW PIN31 Pin 31

Low 0 Read: pin driver is low

High 1 Read: pin driver is high

Clear 1 Write: writing a '1' sets the pin low; writing a '0' has no effect


**20.3.4 IN**

Address offset: 0x510

Read GPIO port


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R PIN0 Pin 0

Low 0 Pin input is low

High 1 Pin input is high


**Page 124**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

B R PIN1 Pin 1

Low 0 Pin input is low

High 1 Pin input is high

C R PIN2 Pin 2

Low 0 Pin input is low

High 1 Pin input is high

D R PIN3 Pin 3

Low 0 Pin input is low

High 1 Pin input is high

E R PIN4 Pin 4

Low 0 Pin input is low

High 1 Pin input is high

F R PIN5 Pin 5

Low 0 Pin input is low

High 1 Pin input is high

G R PIN6 Pin 6

Low 0 Pin input is low

High 1 Pin input is high

H R PIN7 Pin 7

Low 0 Pin input is low

High 1 Pin input is high

I R PIN8 Pin 8

Low 0 Pin input is low

High 1 Pin input is high

J R PIN9 Pin 9

Low 0 Pin input is low

High 1 Pin input is high

K R PIN10 Pin 10

Low 0 Pin input is low

High 1 Pin input is high

L R PIN11 Pin 11

Low 0 Pin input is low

High 1 Pin input is high

M R PIN12 Pin 12

Low 0 Pin input is low

High 1 Pin input is high

N R PIN13 Pin 13

Low 0 Pin input is low

High 1 Pin input is high

O R PIN14 Pin 14

Low 0 Pin input is low

High 1 Pin input is high

P R PIN15 Pin 15

Low 0 Pin input is low

High 1 Pin input is high

Q R PIN16 Pin 16

Low 0 Pin input is low

High 1 Pin input is high

R R PIN17 Pin 17

Low 0 Pin input is low

High 1 Pin input is high

S R PIN18 Pin 18

Low 0 Pin input is low

High 1 Pin input is high

T R PIN19 Pin 19


**Page 125**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Low 0 Pin input is low

High 1 Pin input is high

U R PIN20 Pin 20

Low 0 Pin input is low

High 1 Pin input is high

V R PIN21 Pin 21

Low 0 Pin input is low

High 1 Pin input is high

W R PIN22 Pin 22

Low 0 Pin input is low

High 1 Pin input is high

X R PIN23 Pin 23

Low 0 Pin input is low

High 1 Pin input is high

Y R PIN24 Pin 24

Low 0 Pin input is low

High 1 Pin input is high

Z R PIN25 Pin 25

Low 0 Pin input is low

High 1 Pin input is high

a R PIN26 Pin 26

Low 0 Pin input is low

High 1 Pin input is high

b R PIN27 Pin 27

Low 0 Pin input is low

High 1 Pin input is high

c R PIN28 Pin 28

Low 0 Pin input is low

High 1 Pin input is high

d R PIN29 Pin 29

Low 0 Pin input is low

High 1 Pin input is high

e R PIN30 Pin 30

Low 0 Pin input is low

High 1 Pin input is high

f R PIN31 Pin 31

Low 0 Pin input is low

High 1 Pin input is high


**20.3.5 DIR**

Address offset: 0x514

Direction of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN0 Pin 0

Input 0 Pin set as input

Output 1 Pin set as output

B RW PIN1 Pin 1

Input 0 Pin set as input

Output 1 Pin set as output

C RW PIN2 Pin 2


**Page 126**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Input 0 Pin set as input

Output 1 Pin set as output

D RW PIN3 Pin 3

Input 0 Pin set as input

Output 1 Pin set as output

E RW PIN4 Pin 4

Input 0 Pin set as input

Output 1 Pin set as output

F RW PIN5 Pin 5

Input 0 Pin set as input

Output 1 Pin set as output

G RW PIN6 Pin 6

Input 0 Pin set as input

Output 1 Pin set as output

H RW PIN7 Pin 7

Input 0 Pin set as input

Output 1 Pin set as output

I RW PIN8 Pin 8

Input 0 Pin set as input

Output 1 Pin set as output

J RW PIN9 Pin 9

Input 0 Pin set as input

Output 1 Pin set as output

K RW PIN10 Pin 10

Input 0 Pin set as input

Output 1 Pin set as output

L RW PIN11 Pin 11

Input 0 Pin set as input

Output 1 Pin set as output

M RW PIN12 Pin 12

Input 0 Pin set as input

Output 1 Pin set as output

N RW PIN13 Pin 13

Input 0 Pin set as input

Output 1 Pin set as output

O RW PIN14 Pin 14

Input 0 Pin set as input

Output 1 Pin set as output

P RW PIN15 Pin 15

Input 0 Pin set as input

Output 1 Pin set as output

Q RW PIN16 Pin 16

Input 0 Pin set as input

Output 1 Pin set as output

R RW PIN17 Pin 17

Input 0 Pin set as input

Output 1 Pin set as output

S RW PIN18 Pin 18

Input 0 Pin set as input

Output 1 Pin set as output

T RW PIN19 Pin 19

Input 0 Pin set as input

Output 1 Pin set as output

U RW PIN20 Pin 20

Input 0 Pin set as input


**Page 127**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Output 1 Pin set as output

V RW PIN21 Pin 21

Input 0 Pin set as input

Output 1 Pin set as output

W RW PIN22 Pin 22

Input 0 Pin set as input

Output 1 Pin set as output

X RW PIN23 Pin 23

Input 0 Pin set as input

Output 1 Pin set as output

Y RW PIN24 Pin 24

Input 0 Pin set as input

Output 1 Pin set as output

Z RW PIN25 Pin 25

Input 0 Pin set as input

Output 1 Pin set as output

a RW PIN26 Pin 26

Input 0 Pin set as input

Output 1 Pin set as output

b RW PIN27 Pin 27

Input 0 Pin set as input

Output 1 Pin set as output

c RW PIN28 Pin 28

Input 0 Pin set as input

Output 1 Pin set as output

d RW PIN29 Pin 29

Input 0 Pin set as input

Output 1 Pin set as output

e RW PIN30 Pin 30

Input 0 Pin set as input

Output 1 Pin set as output

f RW PIN31 Pin 31

Input 0 Pin set as input

Output 1 Pin set as output


**20.3.6 DIRSET**

Address offset: 0x518

DIR set register

Read: reads value of DIR register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN0 Set as output pin 0

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

B RW PIN1 Set as output pin 1

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

C RW PIN2 Set as output pin 2


**Page 128**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

D RW PIN3 Set as output pin 3

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

E RW PIN4 Set as output pin 4

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

F RW PIN5 Set as output pin 5

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

G RW PIN6 Set as output pin 6

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

H RW PIN7 Set as output pin 7

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

I RW PIN8 Set as output pin 8

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

J RW PIN9 Set as output pin 9

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

K RW PIN10 Set as output pin 10

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

L RW PIN11 Set as output pin 11

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

M RW PIN12 Set as output pin 12

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

N RW PIN13 Set as output pin 13

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

O RW PIN14 Set as output pin 14

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

P RW PIN15 Set as output pin 15

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect


**Page 129**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Q RW PIN16 Set as output pin 16

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

R RW PIN17 Set as output pin 17

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

S RW PIN18 Set as output pin 18

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

T RW PIN19 Set as output pin 19

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

U RW PIN20 Set as output pin 20

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

V RW PIN21 Set as output pin 21

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

W RW PIN22 Set as output pin 22

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

X RW PIN23 Set as output pin 23

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

Y RW PIN24 Set as output pin 24

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

Z RW PIN25 Set as output pin 25

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

a RW PIN26 Set as output pin 26

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

b RW PIN27 Set as output pin 27

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

c RW PIN28 Set as output pin 28

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

d RW PIN29 Set as output pin 29

Input 0 Read: pin set as input

Output 1 Read: pin set as output


**Page 130**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

e RW PIN30 Set as output pin 30

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect

f RW PIN31 Set as output pin 31

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Set 1 Write: writing a '1' sets pin to output; writing a '0' has no effect


**20.3.7 DIRCLR**

Address offset: 0x51C

DIR clear register

Read: reads value of DIR register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN0 Set as input pin 0

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

B RW PIN1 Set as input pin 1

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

C RW PIN2 Set as input pin 2

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

D RW PIN3 Set as input pin 3

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

E RW PIN4 Set as input pin 4

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

F RW PIN5 Set as input pin 5

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

G RW PIN6 Set as input pin 6

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

H RW PIN7 Set as input pin 7

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

I RW PIN8 Set as input pin 8

Input 0 Read: pin set as input


**Page 131**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

J RW PIN9 Set as input pin 9

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

K RW PIN10 Set as input pin 10

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

L RW PIN11 Set as input pin 11

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

M RW PIN12 Set as input pin 12

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

N RW PIN13 Set as input pin 13

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

O RW PIN14 Set as input pin 14

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

P RW PIN15 Set as input pin 15

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

Q RW PIN16 Set as input pin 16

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

R RW PIN17 Set as input pin 17

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

S RW PIN18 Set as input pin 18

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

T RW PIN19 Set as input pin 19

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

U RW PIN20 Set as input pin 20

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

V RW PIN21 Set as input pin 21

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

W RW PIN22 Set as input pin 22


**Page 132**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

X RW PIN23 Set as input pin 23

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

Y RW PIN24 Set as input pin 24

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

Z RW PIN25 Set as input pin 25

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

a RW PIN26 Set as input pin 26

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

b RW PIN27 Set as input pin 27

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

c RW PIN28 Set as input pin 28

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

d RW PIN29 Set as input pin 29

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

e RW PIN30 Set as input pin 30

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect

f RW PIN31 Set as input pin 31

Input 0 Read: pin set as input

Output 1 Read: pin set as output

Clear 1 Write: writing a '1' sets pin to input; writing a '0' has no effect


**20.3.8 LATCH**

Address offset: 0x520

Latch register indicating what GPIO pins that have met the criteria set in the PIN_CNF[n].SENSE registers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN0 Status on whether PIN0 has met criteria set in PIN_CNF0.SENSE

register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

B RW PIN1 Status on whether PIN1 has met criteria set in PIN_CNF1.SENSE

register. Write '1' to clear.


**Page 133**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

C RW PIN2 Status on whether PIN2 has met criteria set in PIN_CNF2.SENSE

register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

D RW PIN3 Status on whether PIN3 has met criteria set in PIN_CNF3.SENSE

register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

E RW PIN4 Status on whether PIN4 has met criteria set in PIN_CNF4.SENSE

register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

F RW PIN5 Status on whether PIN5 has met criteria set in PIN_CNF5.SENSE

register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

G RW PIN6 Status on whether PIN6 has met criteria set in PIN_CNF6.SENSE

register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

H RW PIN7 Status on whether PIN7 has met criteria set in PIN_CNF7.SENSE

register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

I RW PIN8 Status on whether PIN8 has met criteria set in PIN_CNF8.SENSE

register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

J RW PIN9 Status on whether PIN9 has met criteria set in PIN_CNF9.SENSE

register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

K RW PIN10 Status on whether PIN10 has met criteria set in

PIN_CNF10.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

L RW PIN11 Status on whether PIN11 has met criteria set in

PIN_CNF11.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

M RW PIN12 Status on whether PIN12 has met criteria set in

PIN_CNF12.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

N RW PIN13 Status on whether PIN13 has met criteria set in

PIN_CNF13.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

O RW PIN14 Status on whether PIN14 has met criteria set in

PIN_CNF14.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met


**Page 134**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

P RW PIN15 Status on whether PIN15 has met criteria set in

PIN_CNF15.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

Q RW PIN16 Status on whether PIN16 has met criteria set in

PIN_CNF16.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

R RW PIN17 Status on whether PIN17 has met criteria set in

PIN_CNF17.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

S RW PIN18 Status on whether PIN18 has met criteria set in

PIN_CNF18.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

T RW PIN19 Status on whether PIN19 has met criteria set in

PIN_CNF19.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

U RW PIN20 Status on whether PIN20 has met criteria set in

PIN_CNF20.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

V RW PIN21 Status on whether PIN21 has met criteria set in

PIN_CNF21.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

W RW PIN22 Status on whether PIN22 has met criteria set in

PIN_CNF22.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

X RW PIN23 Status on whether PIN23 has met criteria set in

PIN_CNF23.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

Y RW PIN24 Status on whether PIN24 has met criteria set in

PIN_CNF24.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

Z RW PIN25 Status on whether PIN25 has met criteria set in

PIN_CNF25.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

a RW PIN26 Status on whether PIN26 has met criteria set in

PIN_CNF26.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

b RW PIN27 Status on whether PIN27 has met criteria set in

PIN_CNF27.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

c RW PIN28 Status on whether PIN28 has met criteria set in

PIN_CNF28.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met


**Page 135**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Latched 1 Criteria has been met

d RW PIN29 Status on whether PIN29 has met criteria set in

PIN_CNF29.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

e RW PIN30 Status on whether PIN30 has met criteria set in

PIN_CNF30.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met

f RW PIN31 Status on whether PIN31 has met criteria set in

PIN_CNF31.SENSE register. Write '1' to clear.

NotLatched 0 Criteria has not been met

Latched 1 Criteria has been met


**20.3.9 DETECTMODE**

Address offset: 0x524

Select between default DETECT signal behaviour and LDETECT mode


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DETECTMODE Select between default DETECT signal behaviour and LDETECT

mode

Default 0 DETECT directly connected to PIN DETECT signals

LDETECT 1 Use the latched LDETECT behaviour


**20.3.10 PIN_CNF[0]**

Address offset: 0x700

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 136**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.11 PIN_CNF[1]**

Address offset: 0x704

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.12 PIN_CNF[2]**

Address offset: 0x708

Configuration of GPIO pins


**Page 137**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.13 PIN_CNF[3]**

Address offset: 0x70C

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 138**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.14 PIN_CNF[4]**

Address offset: 0x710

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.15 PIN_CNF[5]**

Address offset: 0x714

Configuration of GPIO pins


**Page 139**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.16 PIN_CNF[6]**

Address offset: 0x718

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 140**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.17 PIN_CNF[7]**

Address offset: 0x71C

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.18 PIN_CNF[8]**

Address offset: 0x720

Configuration of GPIO pins


**Page 141**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.19 PIN_CNF[9]**

Address offset: 0x724

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 142**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.20 PIN_CNF[10]**

Address offset: 0x728

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.21 PIN_CNF[11]**

Address offset: 0x72C

Configuration of GPIO pins


**Page 143**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.22 PIN_CNF[12]**

Address offset: 0x730

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 144**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.23 PIN_CNF[13]**

Address offset: 0x734

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.24 PIN_CNF[14]**

Address offset: 0x738

Configuration of GPIO pins


**Page 145**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.25 PIN_CNF[15]**

Address offset: 0x73C

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 146**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.26 PIN_CNF[16]**

Address offset: 0x740

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.27 PIN_CNF[17]**

Address offset: 0x744

Configuration of GPIO pins


**Page 147**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.28 PIN_CNF[18]**

Address offset: 0x748

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 148**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.29 PIN_CNF[19]**

Address offset: 0x74C

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.30 PIN_CNF[20]**

Address offset: 0x750

Configuration of GPIO pins


**Page 149**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.31 PIN_CNF[21]**

Address offset: 0x754

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 150**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.32 PIN_CNF[22]**

Address offset: 0x758

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.33 PIN_CNF[23]**

Address offset: 0x75C

Configuration of GPIO pins


**Page 151**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.34 PIN_CNF[24]**

Address offset: 0x760

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 152**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.35 PIN_CNF[25]**

Address offset: 0x764

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.36 PIN_CNF[26]**

Address offset: 0x768

Configuration of GPIO pins


**Page 153**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.37 PIN_CNF[27]**

Address offset: 0x76C

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 154**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.38 PIN_CNF[28]**

Address offset: 0x770

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.39 PIN_CNF[29]**

Address offset: 0x774

Configuration of GPIO pins


**Page 155**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.40 PIN_CNF[30]**

Address offset: 0x778

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)


**Page 156**


20 GPIO — General purpose input/output


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level


**20.3.41 PIN_CNF[31]**

Address offset: 0x77C

Configuration of GPIO pins


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E E D D D C C B A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DIR Pin direction. Same physical register as DIR register

Input 0 Configure pin as an input pin

Output 1 Configure pin as an output pin

B RW INPUT Connect or disconnect input buffer

Connect 0 Connect input buffer

Disconnect 1 Disconnect input buffer

C RW PULL Pull configuration

Disabled 0 No pull

Pulldown 1 Pull down on pin

Pullup 3 Pull up on pin

D RW DRIVE Drive configuration

S0S1 0 Standard '0', standard '1'

H0S1 1 High drive '0', standard '1'

S0H1 2 Standard '0', high drive '1'

H0H1 3 High drive '0', high 'drive '1''

D0S1 4 Disconnect '0' standard '1' (normally used for wired-or

connections)

D0H1 5 Disconnect '0', high drive '1' (normally used for wired-or

connections)

S0D1 6 Standard '0'. disconnect '1' (normally used for wired-and

connections)

H0D1 7 High drive '0', disconnect '1' (normally used for wired-and

connections)

E RW SENSE Pin sensing mechanism

Disabled 0 Disabled

High 2 Sense for high level

Low 3 Sense for low level

###### **20.4 Electrical specification**


**20.4.1 GPIO Electrical Specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

VIH Input high voltage 0.7 x VDD VDD V


**Page 157**


20 GPIO — General purpose input/output


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

VIL Input low voltage VSS 0.3 x VDD V

VOH,SD Output high voltage, standard drive, 0.5 mA, VDD ≥1.7 VDD-0.4 VDD V

VOH,HDH Output high voltage, high drive, 5 mA, VDD >= 2.7 V VDD-0.4 VDD V

VOH,HDL Output high voltage, high drive, 3 mA, VDD >= 1.7 V VDD-0.4 VDD V

VOL,SD Output low voltage, standard drive, 0.5 mA, VDD ≥1.7 VSS VSS+0.4 V

VOL,HDH Output low voltage, high drive, 5 mA, VDD >= 2.7 V VSS VSS+0.4 V

VOL,HDL Output low voltage, high drive, 3 mA, VDD >= 1.7 V VSS VSS+0.4 V

IOL,SD Current at VSS+0.4 V, output set low, standard drive, VDD ≥1.7 1 2 4 mA

IOL,HDH Current at VSS+0.4 V, output set low, high drive, VDD >= 2.7 V 6 10 15 mA

IOL,HDL Current at VSS+0.4 V, output set low, high drive, VDD >= 1.7 V 3 mA

IOH,SD Current at VDD-0.4 V, output set high, standard drive, VDD ≥1.7 1 2 4 mA

IOH,HDH Current at VDD-0.4 V, output set high, high drive, VDD >= 2.7 V 6 9 14 mA

IOH,HDL Current at VDD-0.4 V, output set high, high drive, VDD >= 1.7 V 3 mA

tRF,15pF Rise/fall time, low drive mode, 10-90%, 15 pF load [1] 9 ns

tRF,25pF Rise/fall time, low drive mode, 10-90%, 25 pF load [1] 13 ns

tRF,50pF Rise/fall time, low drive mode, 10-90%, 50 pF load [1] 25 ns

tHRF,15pF Rise/Fall time, high drive mode, 10-90%, 15 pF load [1] 4 ns

tHRF,25pF Rise/Fall time, high drive mode, 10-90%, 25 pF load [1] 5 ns

tHRF,50pF Rise/Fall time, high drive mode, 10-90%, 50 pF load [1] 8 ns

RPU Pull-up resistance 11 13 16 kΩ

RPD Pull-down resistance 11 13 16 kΩ

CPAD Pad capacitance 3 pF

CPAD_NFC Pad capacitance on NFC pads 4 pF


INFC_LEAK Leakage current between NFC pads when driven to different

states


2 10 µA


The current drawn from the battery when GPIO is active as an output is calculated as follows:

IGPIO=VDD Cload f

Cload being the load capacitance and “f” is the switching frequency.


7.00


6.00


5.00


4.00


3.00


2.00


1.00


0.00

0.00 0.50 1.00 1.50 2.00 2.50 3.00 3.50

**Pad voltage [V]**


**Figure 25: GPIO drive strength vs Voltage, standard drive, VDD = 3.0 V**


1 Rise and fall times based on simulations


**Page 158**


30.00


25.00


20.00


15.00


10.00


5.00


0.00


20 GPIO — General purpose input/output


0 0.5 1 1.5 2 2.5 3 3.5

**Pad voltage [V]**


**Figure 26: GPIO drive strength vs Voltage, high drive, VDD = 3.0 V**


9.00


8.00


7.00


6.00


5.00


4.00


3.00


2.00


1.00


0.00

1.6 1.8 2 2.2 2.4 2.6 2.8 3 3.2 3.4 3.6

**VDD [V]**


**Figure 27: Max sink current vs Voltage, standard drive**


To ensure optimal performance, it is not recommended to sink/source more than 15 mA combined from the
GPIO pins.


35.00


30.00


25.00


20.00


15.00


10.00


5.00


0.00

1.6 1.8 2 2.2 2.4 2.6 2.8 3 3.2 3.4 3.6

**VDD [V]**


**Figure 28: Max sink current vs Voltage, high drive**


**Page 159**


20 GPIO — General purpose input/output


Rise time Fall time


17.00


16.00


15.00


14.00


13.00


12.00


11.00


10.00

-25 -15 -5 5 15 25 35 45 55 65 75


**Temperature [°C]**


**Figure 29: Rise and fall time vs Temperature, 10%-90%, 25pF load capacitance, VDD = 3.0 V**


**Page 160**


21 GPIOTE — GPIO tasks and events

#### **21 GPIOTE — GPIO tasks and events**


The GPIO tasks and events (GPIOTE) module provides functionality for accessing GPIO pins using tasks
and events. Each GPIOTE channel can be assigned to one pin.

A GPIOTE block enables GPIOs to generate events on pin state change which can be used to carry out
tasks through the PPI system. A GPIO can also be driven to change state on system events using the PPI
system. Low power detection of pin state changes is possible when in System ON or System OFF.


**Table 33: GPIOTE properties**


**Instance** **Number of GPIOTE channels**
GPIOTE 8


Up to three tasks can be used in each GPIOTE channel for performing write operations to a pin. Two tasks
are fixed (SET and CLR), and one (OUT) is configurable to perform following operations:

- Set

- Clear

- Toggle

An event can be generated in each GPIOTE channel from one of the following input conditions:

- Rising edge

- Falling edge

- Any change

###### **21.1 Pin events and tasks**

The GPIOTE module has a number of tasks and events that can be configured to operate on individual
GPIO pins.

The tasks (SET[n], CLR[n] and OUT[n]) can be used for writing to individual pins, and the events (IN[n]) can
be generated from changes occurring at the inputs of individual pins.

The SET task will set the pin selected in CONFIG[n].PSEL to high.

The CLR task will set the pin low.

The effect of the OUT task on the pin is configurable in CONFIG[n].POLARITY, and can either set the pin
high, set it low, or toggle it.

The tasks and events are configured using the CONFIG[n] registers. Every set of SET, CLR and OUT[n]
tasks and IN[n] events has one CONFIG[n] register associated with it.

As long as a SET[n], CLR[n] and OUT[n] task or an IN[n] event is configured to control a pin **n**, the pin's
output value will only be updated by the GPIOTE module. The pin's output value as specified in the GPIO will
therefore be ignored as long as the pin is controlled by GPIOTE. Attempting to write a pin as a normal GPIO
pin will have no effect. When the GPIOTE is disconnected from a pin, see MODE field in CONFIG[n] register,
the associated pin will get the output and configuration values specified in the GPIO module.

When conflicting tasks are triggered simultaneously (i.e. during the same clock cycle) in one channel, the
precedence of the tasks will be as described in _Table 34: Task priorities_ on page 161.


**Table 34: Task priorities**


**Priority** **Task**
**1** **OUT**
**2** **CLR**
**3** **SET**


**Page 161**


21 GPIOTE — GPIO tasks and events


When setting the CONFIG[n] registers, MODE=Disabled does not have the same effect as MODE=Task and
POLARITY=None. In the latter case, a CLR or SET task occurring at the exact same time as OUT will end
up with no change on the pin, according to the priorities described in the table above.

When a GPIOTE channel is configured to operate on a pin as a task, the initial value of that pin is configured
in the OUTINIT field of CONFIG[n].

###### **21.2 Port event**

PORT is an event that can be generated from multiple input pins using the GPIO DETECT signal.

The event will be generated on the rising edge of the DETECT signal. See _GPIO — General purpose input/_
_output_ on page 114 for more information about the DETECT signal.

Putting the system into System ON IDLE while DETECT is high will not cause DETECT to wake the system
up again. Make sure to clear all DETECT sources before entering sleep. If the LATCH register is used as a
source, if any bit in LATCH is still high after clearing all or part of the register (for instance due to one of the
PINx.DETECT signal still high), a new rising edge will be generated on DETECT, see _Pin configuration_ on
page 114.

Trying to put the system to System OFF while DETECT is high will cause a wakeup from System OFF reset.

This feature is always enabled although the peripheral itself appears to be IDLE, that is, no clocks or other
power intensive infrastructure have to be requested to keep this feature enabled. This feature can therefore
be used to wake up the CPU from a WFI or WFE type sleep in System ON with all peripherals and the CPU
idle, that is, lowest power consumption in System ON mode.

In order to prevent spurious interrupts from the PORT event while configuring the sources, the user
shall first disable interrupts on the PORT event (through INTENCLR.PORT), then configure the sources
(PIN_CNF[n].SENSE), clear any potential event that could have occurred during configuration (write '1' to
EVENTS_PORT), and finally enable interrupts (through INTENSET.PORT).

###### **21.3 Tasks and events pin configuration**

Each GPIOTE channel is associated with one physical GPIO pin through the CONFIG.PSEL field.

When Event mode is selected in CONFIG.MODE, the pin specified by CONFIG.PSEL will be configured as
an input, overriding the DIR setting in GPIO. Similarly, when Task mode is selected in CONFIG.MODE, the
pin specified by CONFIG.PSEL will be configured as an output overriding the DIR setting and OUT value
in GPIO. When Disabled is selected in CONFIG.MODE, the pin specified by CONFIG.PSEL will use its
configuration from the PIN[n].CNF registers in GPIO.

Only one GPIOTE channel can be assigned to one physical pin. Failing to do so may result in unpredictable
behavior.

###### **21.4 Registers**


**Table 35: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40006000 GPIOTE GPIOTE GPIO Tasks and Events


**Table 36: Register Overview**


**Register** **Offset** **Description**

TASKS_OUT[0] 0x000 Task for writing to pin specified in CONFIG[0].PSEL. Action on pin is configured in

CONFIG[0].POLARITY.

TASKS_OUT[1] 0x004 Task for writing to pin specified in CONFIG[1].PSEL. Action on pin is configured in

CONFIG[1].POLARITY.


**Page 162**


21 GPIOTE — GPIO tasks and events


**Register** **Offset** **Description**

TASKS_OUT[2] 0x008 Task for writing to pin specified in CONFIG[2].PSEL. Action on pin is configured in

CONFIG[2].POLARITY.

TASKS_OUT[3] 0x00C Task for writing to pin specified in CONFIG[3].PSEL. Action on pin is configured in

CONFIG[3].POLARITY.

TASKS_OUT[4] 0x010 Task for writing to pin specified in CONFIG[4].PSEL. Action on pin is configured in

CONFIG[4].POLARITY.

TASKS_OUT[5] 0x014 Task for writing to pin specified in CONFIG[5].PSEL. Action on pin is configured in

CONFIG[5].POLARITY.

TASKS_OUT[6] 0x018 Task for writing to pin specified in CONFIG[6].PSEL. Action on pin is configured in

CONFIG[6].POLARITY.

TASKS_OUT[7] 0x01C Task for writing to pin specified in CONFIG[7].PSEL. Action on pin is configured in

CONFIG[7].POLARITY.

TASKS_SET[0] 0x030 Task for writing to pin specified in CONFIG[0].PSEL. Action on pin is to set it high.

TASKS_SET[1] 0x034 Task for writing to pin specified in CONFIG[1].PSEL. Action on pin is to set it high.

TASKS_SET[2] 0x038 Task for writing to pin specified in CONFIG[2].PSEL. Action on pin is to set it high.

TASKS_SET[3] 0x03C Task for writing to pin specified in CONFIG[3].PSEL. Action on pin is to set it high.

TASKS_SET[4] 0x040 Task for writing to pin specified in CONFIG[4].PSEL. Action on pin is to set it high.

TASKS_SET[5] 0x044 Task for writing to pin specified in CONFIG[5].PSEL. Action on pin is to set it high.

TASKS_SET[6] 0x048 Task for writing to pin specified in CONFIG[6].PSEL. Action on pin is to set it high.

TASKS_SET[7] 0x04C Task for writing to pin specified in CONFIG[7].PSEL. Action on pin is to set it high.

TASKS_CLR[0] 0x060 Task for writing to pin specified in CONFIG[0].PSEL. Action on pin is to set it low.

TASKS_CLR[1] 0x064 Task for writing to pin specified in CONFIG[1].PSEL. Action on pin is to set it low.

TASKS_CLR[2] 0x068 Task for writing to pin specified in CONFIG[2].PSEL. Action on pin is to set it low.

TASKS_CLR[3] 0x06C Task for writing to pin specified in CONFIG[3].PSEL. Action on pin is to set it low.

TASKS_CLR[4] 0x070 Task for writing to pin specified in CONFIG[4].PSEL. Action on pin is to set it low.

TASKS_CLR[5] 0x074 Task for writing to pin specified in CONFIG[5].PSEL. Action on pin is to set it low.

TASKS_CLR[6] 0x078 Task for writing to pin specified in CONFIG[6].PSEL. Action on pin is to set it low.

TASKS_CLR[7] 0x07C Task for writing to pin specified in CONFIG[7].PSEL. Action on pin is to set it low.

EVENTS_IN[0] 0x100 Event generated from pin specified in CONFIG[0].PSEL

EVENTS_IN[1] 0x104 Event generated from pin specified in CONFIG[1].PSEL

EVENTS_IN[2] 0x108 Event generated from pin specified in CONFIG[2].PSEL

EVENTS_IN[3] 0x10C Event generated from pin specified in CONFIG[3].PSEL

EVENTS_IN[4] 0x110 Event generated from pin specified in CONFIG[4].PSEL

EVENTS_IN[5] 0x114 Event generated from pin specified in CONFIG[5].PSEL

EVENTS_IN[6] 0x118 Event generated from pin specified in CONFIG[6].PSEL

EVENTS_IN[7] 0x11C Event generated from pin specified in CONFIG[7].PSEL

EVENTS_PORT 0x17C Event generated from multiple input GPIO pins with SENSE mechanism enabled

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_CONFIG[0]_ 0x510 Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event

_CONFIG[1]_ 0x514 Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event

_CONFIG[2]_ 0x518 Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event

_CONFIG[3]_ 0x51C Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event

_CONFIG[4]_ 0x520 Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event

_CONFIG[5]_ 0x524 Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event

_CONFIG[6]_ 0x528 Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event

_CONFIG[7]_ 0x52C Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event


**21.4.1 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW IN0 Write '1' to Enable interrupt for IN[0] event


**Page 163**


21 GPIOTE — GPIO tasks and events


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

See _EVENTS_IN[0]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW IN1 Write '1' to Enable interrupt for IN[1] event


See _EVENTS_IN[1]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW IN2 Write '1' to Enable interrupt for IN[2] event


See _EVENTS_IN[2]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW IN3 Write '1' to Enable interrupt for IN[3] event


See _EVENTS_IN[3]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW IN4 Write '1' to Enable interrupt for IN[4] event


See _EVENTS_IN[4]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW IN5 Write '1' to Enable interrupt for IN[5] event


See _EVENTS_IN[5]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW IN6 Write '1' to Enable interrupt for IN[6] event


See _EVENTS_IN[6]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW IN7 Write '1' to Enable interrupt for IN[7] event


See _EVENTS_IN[7]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW PORT Write '1' to Enable interrupt for PORT event


See _EVENTS_PORT_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**21.4.2 INTENCLR**

Address offset: 0x308

Disable interrupt


**Page 164**


21 GPIOTE — GPIO tasks and events


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW IN0 Write '1' to Disable interrupt for IN[0] event


See _EVENTS_IN[0]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW IN1 Write '1' to Disable interrupt for IN[1] event


See _EVENTS_IN[1]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW IN2 Write '1' to Disable interrupt for IN[2] event


See _EVENTS_IN[2]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW IN3 Write '1' to Disable interrupt for IN[3] event


See _EVENTS_IN[3]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW IN4 Write '1' to Disable interrupt for IN[4] event


See _EVENTS_IN[4]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW IN5 Write '1' to Disable interrupt for IN[5] event


See _EVENTS_IN[5]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW IN6 Write '1' to Disable interrupt for IN[6] event


See _EVENTS_IN[6]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW IN7 Write '1' to Disable interrupt for IN[7] event


See _EVENTS_IN[7]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW PORT Write '1' to Disable interrupt for PORT event


See _EVENTS_PORT_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**21.4.3 CONFIG[0]**

Address offset: 0x510

Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event


**Page 165**


21 GPIOTE — GPIO tasks and events


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Mode

Disabled 0 Disabled. Pin specified by PSEL will not be acquired by the

GPIOTE module.

Event 1 Event mode


The pin specified by PSEL will be configured as an input and the

IN[n] event will be generated if operation specified in POLARITY

occurs on the pin.

Task 3 Task mode


The GPIO specified by PSEL will be configured as an output and

triggering the SET[n], CLR[n] or OUT[n] task will perform the

operation specified by POLARITY on the pin. When enabled as a

task the GPIOTE module will acquire the pin and the pin can no

longer be written as a regular output pin from the GPIO module.

B RW PSEL [0..31] GPIO number associated with SET[n], CLR[n] and OUT[n] tasks

and IN[n] event

C RW POLARITY When In task mode: Operation to be performed on output

when OUT[n] task is triggered. When In event mode: Operation

on input that shall trigger IN[n] event.

None 0 Task mode: No effect on pin from OUT[n] task. Event mode: no

IN[n] event generated on pin activity.

LoToHi 1 Task mode: Set pin from OUT[n] task. Event mode: Generate

IN[n] event when rising edge on pin.

HiToLo 2 Task mode: Clear pin from OUT[n] task. Event mode: Generate

IN[n] event when falling edge on pin.

Toggle 3 Task mode: Toggle pin from OUT[n]. Event mode: Generate

IN[n] when any change on pin.

D RW OUTINIT When in task mode: Initial value of the output when the GPIOTE

channel is configured. When in event mode: No effect.

Low 0 Task mode: Initial value of pin before task triggering is low

High 1 Task mode: Initial value of pin before task triggering is high


**21.4.4 CONFIG[1]**

Address offset: 0x514

Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Mode

Disabled 0 Disabled. Pin specified by PSEL will not be acquired by the

GPIOTE module.

Event 1 Event mode


The pin specified by PSEL will be configured as an input and the

IN[n] event will be generated if operation specified in POLARITY

occurs on the pin.

Task 3 Task mode


The GPIO specified by PSEL will be configured as an output and

triggering the SET[n], CLR[n] or OUT[n] task will perform the

operation specified by POLARITY on the pin. When enabled as a

task the GPIOTE module will acquire the pin and the pin can no

longer be written as a regular output pin from the GPIO module.


**Page 166**


21 GPIOTE — GPIO tasks and events


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

B RW PSEL [0..31] GPIO number associated with SET[n], CLR[n] and OUT[n] tasks

and IN[n] event

C RW POLARITY When In task mode: Operation to be performed on output

when OUT[n] task is triggered. When In event mode: Operation

on input that shall trigger IN[n] event.

None 0 Task mode: No effect on pin from OUT[n] task. Event mode: no

IN[n] event generated on pin activity.

LoToHi 1 Task mode: Set pin from OUT[n] task. Event mode: Generate

IN[n] event when rising edge on pin.

HiToLo 2 Task mode: Clear pin from OUT[n] task. Event mode: Generate

IN[n] event when falling edge on pin.

Toggle 3 Task mode: Toggle pin from OUT[n]. Event mode: Generate

IN[n] when any change on pin.

D RW OUTINIT When in task mode: Initial value of the output when the GPIOTE

channel is configured. When in event mode: No effect.

Low 0 Task mode: Initial value of pin before task triggering is low

High 1 Task mode: Initial value of pin before task triggering is high


**21.4.5 CONFIG[2]**

Address offset: 0x518

Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Mode

Disabled 0 Disabled. Pin specified by PSEL will not be acquired by the

GPIOTE module.

Event 1 Event mode


The pin specified by PSEL will be configured as an input and the

IN[n] event will be generated if operation specified in POLARITY

occurs on the pin.

Task 3 Task mode


The GPIO specified by PSEL will be configured as an output and

triggering the SET[n], CLR[n] or OUT[n] task will perform the

operation specified by POLARITY on the pin. When enabled as a

task the GPIOTE module will acquire the pin and the pin can no

longer be written as a regular output pin from the GPIO module.

B RW PSEL [0..31] GPIO number associated with SET[n], CLR[n] and OUT[n] tasks

and IN[n] event

C RW POLARITY When In task mode: Operation to be performed on output

when OUT[n] task is triggered. When In event mode: Operation

on input that shall trigger IN[n] event.

None 0 Task mode: No effect on pin from OUT[n] task. Event mode: no

IN[n] event generated on pin activity.

LoToHi 1 Task mode: Set pin from OUT[n] task. Event mode: Generate

IN[n] event when rising edge on pin.

HiToLo 2 Task mode: Clear pin from OUT[n] task. Event mode: Generate

IN[n] event when falling edge on pin.

Toggle 3 Task mode: Toggle pin from OUT[n]. Event mode: Generate

IN[n] when any change on pin.


**Page 167**


21 GPIOTE — GPIO tasks and events


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D RW OUTINIT When in task mode: Initial value of the output when the GPIOTE

channel is configured. When in event mode: No effect.

Low 0 Task mode: Initial value of pin before task triggering is low

High 1 Task mode: Initial value of pin before task triggering is high


**21.4.6 CONFIG[3]**

Address offset: 0x51C

Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Mode

Disabled 0 Disabled. Pin specified by PSEL will not be acquired by the

GPIOTE module.

Event 1 Event mode


The pin specified by PSEL will be configured as an input and the

IN[n] event will be generated if operation specified in POLARITY

occurs on the pin.

Task 3 Task mode


The GPIO specified by PSEL will be configured as an output and

triggering the SET[n], CLR[n] or OUT[n] task will perform the

operation specified by POLARITY on the pin. When enabled as a

task the GPIOTE module will acquire the pin and the pin can no

longer be written as a regular output pin from the GPIO module.

B RW PSEL [0..31] GPIO number associated with SET[n], CLR[n] and OUT[n] tasks

and IN[n] event

C RW POLARITY When In task mode: Operation to be performed on output

when OUT[n] task is triggered. When In event mode: Operation

on input that shall trigger IN[n] event.

None 0 Task mode: No effect on pin from OUT[n] task. Event mode: no

IN[n] event generated on pin activity.

LoToHi 1 Task mode: Set pin from OUT[n] task. Event mode: Generate

IN[n] event when rising edge on pin.

HiToLo 2 Task mode: Clear pin from OUT[n] task. Event mode: Generate

IN[n] event when falling edge on pin.

Toggle 3 Task mode: Toggle pin from OUT[n]. Event mode: Generate

IN[n] when any change on pin.

D RW OUTINIT When in task mode: Initial value of the output when the GPIOTE

channel is configured. When in event mode: No effect.

Low 0 Task mode: Initial value of pin before task triggering is low

High 1 Task mode: Initial value of pin before task triggering is high


**21.4.7 CONFIG[4]**

Address offset: 0x520

Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event


**Page 168**


21 GPIOTE — GPIO tasks and events


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Mode

Disabled 0 Disabled. Pin specified by PSEL will not be acquired by the

GPIOTE module.

Event 1 Event mode


The pin specified by PSEL will be configured as an input and the

IN[n] event will be generated if operation specified in POLARITY

occurs on the pin.

Task 3 Task mode


The GPIO specified by PSEL will be configured as an output and

triggering the SET[n], CLR[n] or OUT[n] task will perform the

operation specified by POLARITY on the pin. When enabled as a

task the GPIOTE module will acquire the pin and the pin can no

longer be written as a regular output pin from the GPIO module.

B RW PSEL [0..31] GPIO number associated with SET[n], CLR[n] and OUT[n] tasks

and IN[n] event

C RW POLARITY When In task mode: Operation to be performed on output

when OUT[n] task is triggered. When In event mode: Operation

on input that shall trigger IN[n] event.

None 0 Task mode: No effect on pin from OUT[n] task. Event mode: no

IN[n] event generated on pin activity.

LoToHi 1 Task mode: Set pin from OUT[n] task. Event mode: Generate

IN[n] event when rising edge on pin.

HiToLo 2 Task mode: Clear pin from OUT[n] task. Event mode: Generate

IN[n] event when falling edge on pin.

Toggle 3 Task mode: Toggle pin from OUT[n]. Event mode: Generate

IN[n] when any change on pin.

D RW OUTINIT When in task mode: Initial value of the output when the GPIOTE

channel is configured. When in event mode: No effect.

Low 0 Task mode: Initial value of pin before task triggering is low

High 1 Task mode: Initial value of pin before task triggering is high


**21.4.8 CONFIG[5]**

Address offset: 0x524

Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Mode

Disabled 0 Disabled. Pin specified by PSEL will not be acquired by the

GPIOTE module.

Event 1 Event mode


The pin specified by PSEL will be configured as an input and the

IN[n] event will be generated if operation specified in POLARITY

occurs on the pin.

Task 3 Task mode


The GPIO specified by PSEL will be configured as an output and

triggering the SET[n], CLR[n] or OUT[n] task will perform the

operation specified by POLARITY on the pin. When enabled as a

task the GPIOTE module will acquire the pin and the pin can no

longer be written as a regular output pin from the GPIO module.


**Page 169**


21 GPIOTE — GPIO tasks and events


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

B RW PSEL [0..31] GPIO number associated with SET[n], CLR[n] and OUT[n] tasks

and IN[n] event

C RW POLARITY When In task mode: Operation to be performed on output

when OUT[n] task is triggered. When In event mode: Operation

on input that shall trigger IN[n] event.

None 0 Task mode: No effect on pin from OUT[n] task. Event mode: no

IN[n] event generated on pin activity.

LoToHi 1 Task mode: Set pin from OUT[n] task. Event mode: Generate

IN[n] event when rising edge on pin.

HiToLo 2 Task mode: Clear pin from OUT[n] task. Event mode: Generate

IN[n] event when falling edge on pin.

Toggle 3 Task mode: Toggle pin from OUT[n]. Event mode: Generate

IN[n] when any change on pin.

D RW OUTINIT When in task mode: Initial value of the output when the GPIOTE

channel is configured. When in event mode: No effect.

Low 0 Task mode: Initial value of pin before task triggering is low

High 1 Task mode: Initial value of pin before task triggering is high


**21.4.9 CONFIG[6]**

Address offset: 0x528

Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Mode

Disabled 0 Disabled. Pin specified by PSEL will not be acquired by the

GPIOTE module.

Event 1 Event mode


The pin specified by PSEL will be configured as an input and the

IN[n] event will be generated if operation specified in POLARITY

occurs on the pin.

Task 3 Task mode


The GPIO specified by PSEL will be configured as an output and

triggering the SET[n], CLR[n] or OUT[n] task will perform the

operation specified by POLARITY on the pin. When enabled as a

task the GPIOTE module will acquire the pin and the pin can no

longer be written as a regular output pin from the GPIO module.

B RW PSEL [0..31] GPIO number associated with SET[n], CLR[n] and OUT[n] tasks

and IN[n] event

C RW POLARITY When In task mode: Operation to be performed on output

when OUT[n] task is triggered. When In event mode: Operation

on input that shall trigger IN[n] event.

None 0 Task mode: No effect on pin from OUT[n] task. Event mode: no

IN[n] event generated on pin activity.

LoToHi 1 Task mode: Set pin from OUT[n] task. Event mode: Generate

IN[n] event when rising edge on pin.

HiToLo 2 Task mode: Clear pin from OUT[n] task. Event mode: Generate

IN[n] event when falling edge on pin.

Toggle 3 Task mode: Toggle pin from OUT[n]. Event mode: Generate

IN[n] when any change on pin.


**Page 170**


21 GPIOTE — GPIO tasks and events


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

D RW OUTINIT When in task mode: Initial value of the output when the GPIOTE

channel is configured. When in event mode: No effect.

Low 0 Task mode: Initial value of pin before task triggering is low

High 1 Task mode: Initial value of pin before task triggering is high


**21.4.10 CONFIG[7]**

Address offset: 0x52C

Configuration for OUT[n], SET[n] and CLR[n] tasks and IN[n] event


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C C B B B B B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Mode

Disabled 0 Disabled. Pin specified by PSEL will not be acquired by the

GPIOTE module.

Event 1 Event mode


The pin specified by PSEL will be configured as an input and the

IN[n] event will be generated if operation specified in POLARITY

occurs on the pin.

Task 3 Task mode


The GPIO specified by PSEL will be configured as an output and

triggering the SET[n], CLR[n] or OUT[n] task will perform the

operation specified by POLARITY on the pin. When enabled as a

task the GPIOTE module will acquire the pin and the pin can no

longer be written as a regular output pin from the GPIO module.

B RW PSEL [0..31] GPIO number associated with SET[n], CLR[n] and OUT[n] tasks

and IN[n] event

C RW POLARITY When In task mode: Operation to be performed on output

when OUT[n] task is triggered. When In event mode: Operation

on input that shall trigger IN[n] event.

None 0 Task mode: No effect on pin from OUT[n] task. Event mode: no

IN[n] event generated on pin activity.

LoToHi 1 Task mode: Set pin from OUT[n] task. Event mode: Generate

IN[n] event when rising edge on pin.

HiToLo 2 Task mode: Clear pin from OUT[n] task. Event mode: Generate

IN[n] event when falling edge on pin.

Toggle 3 Task mode: Toggle pin from OUT[n]. Event mode: Generate

IN[n] when any change on pin.

D RW OUTINIT When in task mode: Initial value of the output when the GPIOTE

channel is configured. When in event mode: No effect.

Low 0 Task mode: Initial value of pin before task triggering is low

High 1 Task mode: Initial value of pin before task triggering is high

###### **21.5 Electrical specification**


**21.5.1 GPIOTE Electrical Specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**


IGPIOTE,IN Run current with 1 or more GPIOTE active channels in Input

mode


**Page 171**


0.1 0.5 µA


22 PPI — Programmable peripheral interconnect

#### **22 PPI — Programmable peripheral interconnect**


The Programmable peripheral interconnect (PPI) enables peripherals to interact autonomously with each
other using tasks and events independent of the CPU. The PPI allows precise synchronization between
peripherals when real-time application constraints exist and eliminates the need for CPU activity to
implement behavior which can be predefined using PPI.


CH[n].EEP


~~0~~

~~1~~


~~n~~

CHG[0]

16MHz


1


n
... CHG[m]


Peripheral 1


Peripheral 2


CH[1].EEP

CH[0].EEP


Event 1
Event 2


Event 1
Event 2
Event 3


1


n

CHEN


Task 1


Task 1
Task 2
Task 3


Peripheral 1


Peripheral 2


CH[0].TEP

**Figure 30: PPI block diagram**


FORK[0].TEP


The PPI system has, in addition to the fully programmable peripheral interconnections, a set of channels
where the event end point (EEP) and task end points (TEP) are fixed in hardware. These fixed channels
can be individually enabled, disabled, or added to PPI channel groups in the same way as ordinary PPI
channels.


**Table 37: Configurable and fixed PPI channels**


**Instance** **Channel** **Number of channels** **Number of groups**
PPI 0-19 20 6
PPI (fixed) 20-31 12


The PPI provides a mechanism to automatically trigger a task in one peripheral as a result of an event
occurring in another peripheral. A task is connected to an event through a PPI channel. The PPI channel
is composed of three end point registers, one EEP and two TEPs. A peripheral task is connected to a TEP
using the address of the task register associated with the task. Similarly, a peripheral event is connected to
an EEP using the address of the event register associated with the event.

On each PPI channel, the signals are synchronized to the 16 MHz clock, to avoid any internal violation of
setup and hold timings. As a consequence, events that are synchronous to the 16 MHz clock will be delayed
by one clock period, while other asynchronous events will be delayed by up to one 16 MHz clock period.


**Page 172**


22 PPI — Programmable peripheral interconnect


Note that shortcuts (as defined in the SHORTS register in each peripheral) are not affected by this 16 MHz
synchronization, and are therefore not delayed.

Each TEP implements a fork mechanism that enables a second task to be triggered at the same time as
the task specified in the TEP is triggered. This second task is configured in the task end point register in the
FORK registers groups, e.g. FORK.TEP[0] is associated with PPI channel CH[0].

There are two ways of enabling and disabling PPI channels:

- Enable or disable PPI channels individually using the CHEN, CHENSET, and CHENCLR registers.

- Enable or disable PPI channels in PPI channel groups through the groups’ ENABLE and DISABLE tasks.
Prior to these tasks being triggered, the PPI channel group must be configured to define which PPI
channels belongs to which groups.

Note that when a channel belongs to two groups m and n, and CHG[m].EN and CHG[n].DIS occur
simultaneously (m and n can be equal or different), EN on that channel has priority.

PPI tasks (for example, CHG[0].EN) can be triggered through the PPI like any other task, which means
they can be hooked up to a PPI channel as a TEP. One event can trigger multiple tasks by using multiple
channels and one task can be triggered by multiple events in the same way.

###### **22.1 Pre-programmed channels**

Some of the PPI channels are pre-programmed. These channels cannot be configured by the CPU, but can
be added to groups and enabled and disabled like the general purpose PPI channels. The FORK TEP for
these channels are still programmable and can be used by the application.

For a list of pre-programmed PPI channels, see the table below.


**Table 38: Pre-programmed channels**


**Channel** **EEP** **TEP**
20 TIMER0->EVENTS_COMPARE[0] RADIO->TASKS_TXEN
21 TIMER0->EVENTS_COMPARE[0] RADIO->TASKS_RXEN
22 TIMER0->EVENTS_COMPARE[1] RADIO->TASKS_DISABLE
23 RADIO->EVENTS_BCMATCH AAR->TASKS_START
24 RADIO->EVENTS_READY CCM->TASKS_KSGEN
25 RADIO->EVENTS_ADDRESS CCM->TASKS_CRYPT
26 RADIO->EVENTS_ADDRESS TIMER0->TASKS_CAPTURE[1]
27 RADIO->EVENTS_END TIMER0->TASKS_CAPTURE[2]
28 RTC0->EVENTS_COMPARE[0] RADIO->TASKS_TXEN
29 RTC0->EVENTS_COMPARE[0] RADIO->TASKS_RXEN
30 RTC0->EVENTS_COMPARE[0] TIMER0->TASKS_CLEAR
31 RTC0->EVENTS_COMPARE[0] TIMER0->TASKS_START

###### **22.2 Registers**


**Table 39: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x4001F000 PPI PPI Programmable Peripheral Interconnect


**Table 40: Register Overview**


**Register** **Offset** **Description**

TASKS_CHG[0].EN 0x000 Enable channel group 0

TASKS_CHG[0].DIS 0x004 Disable channel group 0

TASKS_CHG[1].EN 0x008 Enable channel group 1

TASKS_CHG[1].DIS 0x00C Disable channel group 1

TASKS_CHG[2].EN 0x010 Enable channel group 2

TASKS_CHG[2].DIS 0x014 Disable channel group 2

TASKS_CHG[3].EN 0x018 Enable channel group 3

TASKS_CHG[3].DIS 0x01C Disable channel group 3

TASKS_CHG[4].EN 0x020 Enable channel group 4


**Page 173**


22 PPI — Programmable peripheral interconnect


**Register** **Offset** **Description**

TASKS_CHG[4].DIS 0x024 Disable channel group 4

TASKS_CHG[5].EN 0x028 Enable channel group 5

TASKS_CHG[5].DIS 0x02C Disable channel group 5

_CHEN_ 0x500 Channel enable register

_CHENSET_ 0x504 Channel enable set register

_CHENCLR_ 0x508 Channel enable clear register

_CH[0].EEP_ 0x510 Channel 0 event end-point

_CH[0].TEP_ 0x514 Channel 0 task end-point

_CH[1].EEP_ 0x518 Channel 1 event end-point

_CH[1].TEP_ 0x51C Channel 1 task end-point

_CH[2].EEP_ 0x520 Channel 2 event end-point

_CH[2].TEP_ 0x524 Channel 2 task end-point

_CH[3].EEP_ 0x528 Channel 3 event end-point

_CH[3].TEP_ 0x52C Channel 3 task end-point

_CH[4].EEP_ 0x530 Channel 4 event end-point

_CH[4].TEP_ 0x534 Channel 4 task end-point

_CH[5].EEP_ 0x538 Channel 5 event end-point

_CH[5].TEP_ 0x53C Channel 5 task end-point

_CH[6].EEP_ 0x540 Channel 6 event end-point

_CH[6].TEP_ 0x544 Channel 6 task end-point

_CH[7].EEP_ 0x548 Channel 7 event end-point

_CH[7].TEP_ 0x54C Channel 7 task end-point

_CH[8].EEP_ 0x550 Channel 8 event end-point

_CH[8].TEP_ 0x554 Channel 8 task end-point

_CH[9].EEP_ 0x558 Channel 9 event end-point

_CH[9].TEP_ 0x55C Channel 9 task end-point

_CH[10].EEP_ 0x560 Channel 10 event end-point

_CH[10].TEP_ 0x564 Channel 10 task end-point

_CH[11].EEP_ 0x568 Channel 11 event end-point

_CH[11].TEP_ 0x56C Channel 11 task end-point

_CH[12].EEP_ 0x570 Channel 12 event end-point

_CH[12].TEP_ 0x574 Channel 12 task end-point

_CH[13].EEP_ 0x578 Channel 13 event end-point

_CH[13].TEP_ 0x57C Channel 13 task end-point

_CH[14].EEP_ 0x580 Channel 14 event end-point

_CH[14].TEP_ 0x584 Channel 14 task end-point

_CH[15].EEP_ 0x588 Channel 15 event end-point

_CH[15].TEP_ 0x58C Channel 15 task end-point

_CH[16].EEP_ 0x590 Channel 16 event end-point

_CH[16].TEP_ 0x594 Channel 16 task end-point

_CH[17].EEP_ 0x598 Channel 17 event end-point

_CH[17].TEP_ 0x59C Channel 17 task end-point

_CH[18].EEP_ 0x5A0 Channel 18 event end-point

_CH[18].TEP_ 0x5A4 Channel 18 task end-point

_CH[19].EEP_ 0x5A8 Channel 19 event end-point

_CH[19].TEP_ 0x5AC Channel 19 task end-point

_CHG[0]_ 0x800 Channel group 0

_CHG[1]_ 0x804 Channel group 1

_CHG[2]_ 0x808 Channel group 2

_CHG[3]_ 0x80C Channel group 3

_CHG[4]_ 0x810 Channel group 4

_CHG[5]_ 0x814 Channel group 5

_FORK[0].TEP_ 0x910 Channel 0 task end-point

_FORK[1].TEP_ 0x914 Channel 1 task end-point

_FORK[2].TEP_ 0x918 Channel 2 task end-point

_FORK[3].TEP_ 0x91C Channel 3 task end-point

_FORK[4].TEP_ 0x920 Channel 4 task end-point

_FORK[5].TEP_ 0x924 Channel 5 task end-point


**Page 174**


22 PPI — Programmable peripheral interconnect


**Register** **Offset** **Description**

_FORK[6].TEP_ 0x928 Channel 6 task end-point

_FORK[7].TEP_ 0x92C Channel 7 task end-point

_FORK[8].TEP_ 0x930 Channel 8 task end-point

_FORK[9].TEP_ 0x934 Channel 9 task end-point

_FORK[10].TEP_ 0x938 Channel 10 task end-point

_FORK[11].TEP_ 0x93C Channel 11 task end-point

_FORK[12].TEP_ 0x940 Channel 12 task end-point

_FORK[13].TEP_ 0x944 Channel 13 task end-point

_FORK[14].TEP_ 0x948 Channel 14 task end-point

_FORK[15].TEP_ 0x94C Channel 15 task end-point

_FORK[16].TEP_ 0x950 Channel 16 task end-point

_FORK[17].TEP_ 0x954 Channel 17 task end-point

_FORK[18].TEP_ 0x958 Channel 18 task end-point

_FORK[19].TEP_ 0x95C Channel 19 task end-point

_FORK[20].TEP_ 0x960 Channel 20 task end-point

_FORK[21].TEP_ 0x964 Channel 21 task end-point

_FORK[22].TEP_ 0x968 Channel 22 task end-point

_FORK[23].TEP_ 0x96C Channel 23 task end-point

_FORK[24].TEP_ 0x970 Channel 24 task end-point

_FORK[25].TEP_ 0x974 Channel 25 task end-point

_FORK[26].TEP_ 0x978 Channel 26 task end-point

_FORK[27].TEP_ 0x97C Channel 27 task end-point

_FORK[28].TEP_ 0x980 Channel 28 task end-point

_FORK[29].TEP_ 0x984 Channel 29 task end-point

_FORK[30].TEP_ 0x988 Channel 30 task end-point

_FORK[31].TEP_ 0x98C Channel 31 task end-point


**22.2.1 CHEN**

Address offset: 0x500

Channel enable register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CH0 Enable or disable channel 0

Disabled 0 Disable channel

Enabled 1 Enable channel

B RW CH1 Enable or disable channel 1

Disabled 0 Disable channel

Enabled 1 Enable channel

C RW CH2 Enable or disable channel 2

Disabled 0 Disable channel

Enabled 1 Enable channel

D RW CH3 Enable or disable channel 3

Disabled 0 Disable channel

Enabled 1 Enable channel

E RW CH4 Enable or disable channel 4

Disabled 0 Disable channel

Enabled 1 Enable channel

F RW CH5 Enable or disable channel 5

Disabled 0 Disable channel

Enabled 1 Enable channel

G RW CH6 Enable or disable channel 6

Disabled 0 Disable channel

Enabled 1 Enable channel

H RW CH7 Enable or disable channel 7


**Page 175**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Disable channel

Enabled 1 Enable channel

I RW CH8 Enable or disable channel 8

Disabled 0 Disable channel

Enabled 1 Enable channel

J RW CH9 Enable or disable channel 9

Disabled 0 Disable channel

Enabled 1 Enable channel

K RW CH10 Enable or disable channel 10

Disabled 0 Disable channel

Enabled 1 Enable channel

L RW CH11 Enable or disable channel 11

Disabled 0 Disable channel

Enabled 1 Enable channel

M RW CH12 Enable or disable channel 12

Disabled 0 Disable channel

Enabled 1 Enable channel

N RW CH13 Enable or disable channel 13

Disabled 0 Disable channel

Enabled 1 Enable channel

O RW CH14 Enable or disable channel 14

Disabled 0 Disable channel

Enabled 1 Enable channel

P RW CH15 Enable or disable channel 15

Disabled 0 Disable channel

Enabled 1 Enable channel

Q RW CH16 Enable or disable channel 16

Disabled 0 Disable channel

Enabled 1 Enable channel

R RW CH17 Enable or disable channel 17

Disabled 0 Disable channel

Enabled 1 Enable channel

S RW CH18 Enable or disable channel 18

Disabled 0 Disable channel

Enabled 1 Enable channel

T RW CH19 Enable or disable channel 19

Disabled 0 Disable channel

Enabled 1 Enable channel

U RW CH20 Enable or disable channel 20

Disabled 0 Disable channel

Enabled 1 Enable channel

V RW CH21 Enable or disable channel 21

Disabled 0 Disable channel

Enabled 1 Enable channel

W RW CH22 Enable or disable channel 22

Disabled 0 Disable channel

Enabled 1 Enable channel

X RW CH23 Enable or disable channel 23

Disabled 0 Disable channel

Enabled 1 Enable channel

Y RW CH24 Enable or disable channel 24

Disabled 0 Disable channel

Enabled 1 Enable channel

Z RW CH25 Enable or disable channel 25

Disabled 0 Disable channel


**Page 176**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Enable channel

a RW CH26 Enable or disable channel 26

Disabled 0 Disable channel

Enabled 1 Enable channel

b RW CH27 Enable or disable channel 27

Disabled 0 Disable channel

Enabled 1 Enable channel

c RW CH28 Enable or disable channel 28

Disabled 0 Disable channel

Enabled 1 Enable channel

d RW CH29 Enable or disable channel 29

Disabled 0 Disable channel

Enabled 1 Enable channel

e RW CH30 Enable or disable channel 30

Disabled 0 Disable channel

Enabled 1 Enable channel

f RW CH31 Enable or disable channel 31

Disabled 0 Disable channel

Enabled 1 Enable channel


**22.2.2 CHENSET**

Address offset: 0x504

Channel enable set register

Read: reads value of CH{i} field in CHEN register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CH0 Channel 0 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

B RW CH1 Channel 1 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

C RW CH2 Channel 2 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

D RW CH3 Channel 3 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

E RW CH4 Channel 4 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

F RW CH5 Channel 5 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel


**Page 177**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

G RW CH6 Channel 6 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

H RW CH7 Channel 7 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

I RW CH8 Channel 8 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

J RW CH9 Channel 9 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

K RW CH10 Channel 10 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

L RW CH11 Channel 11 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

M RW CH12 Channel 12 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

N RW CH13 Channel 13 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

O RW CH14 Channel 14 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

P RW CH15 Channel 15 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

Q RW CH16 Channel 16 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

R RW CH17 Channel 17 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

S RW CH18 Channel 18 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

T RW CH19 Channel 19 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled


**Page 178**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Set 1 Write: Enable channel

U RW CH20 Channel 20 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

V RW CH21 Channel 21 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

W RW CH22 Channel 22 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

X RW CH23 Channel 23 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

Y RW CH24 Channel 24 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

Z RW CH25 Channel 25 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

a RW CH26 Channel 26 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

b RW CH27 Channel 27 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

c RW CH28 Channel 28 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

d RW CH29 Channel 29 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

e RW CH30 Channel 30 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel

f RW CH31 Channel 31 enable set register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Set 1 Write: Enable channel


**22.2.3 CHENCLR**

Address offset: 0x508

Channel enable clear register


**Page 179**


22 PPI — Programmable peripheral interconnect


Read: reads value of CH{i} field in CHEN register.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CH0 Channel 0 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

B RW CH1 Channel 1 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

C RW CH2 Channel 2 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

D RW CH3 Channel 3 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

E RW CH4 Channel 4 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

F RW CH5 Channel 5 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

G RW CH6 Channel 6 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

H RW CH7 Channel 7 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

I RW CH8 Channel 8 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

J RW CH9 Channel 9 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

K RW CH10 Channel 10 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

L RW CH11 Channel 11 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

M RW CH12 Channel 12 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

N RW CH13 Channel 13 enable clear register. Writing '0' has no effect


**Page 180**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

O RW CH14 Channel 14 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

P RW CH15 Channel 15 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

Q RW CH16 Channel 16 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

R RW CH17 Channel 17 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

S RW CH18 Channel 18 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

T RW CH19 Channel 19 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

U RW CH20 Channel 20 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

V RW CH21 Channel 21 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

W RW CH22 Channel 22 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

X RW CH23 Channel 23 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

Y RW CH24 Channel 24 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

Z RW CH25 Channel 25 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

a RW CH26 Channel 26 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel


**Page 181**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

b RW CH27 Channel 27 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

c RW CH28 Channel 28 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

d RW CH29 Channel 29 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

e RW CH30 Channel 30 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel

f RW CH31 Channel 31 enable clear register. Writing '0' has no effect

Disabled 0 Read: channel disabled

Enabled 1 Read: channel enabled

Clear 1 Write: disable channel


**22.2.4 CH[0].EEP**

Address offset: 0x510

Channel 0 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.5 CH[0].TEP**

Address offset: 0x514

Channel 0 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.6 CH[1].EEP**

Address offset: 0x518

Channel 1 event end-point


**Page 182**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.7 CH[1].TEP**

Address offset: 0x51C

Channel 1 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.8 CH[2].EEP**

Address offset: 0x520

Channel 2 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.9 CH[2].TEP**

Address offset: 0x524

Channel 2 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.10 CH[3].EEP**

Address offset: 0x528

Channel 3 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.11 CH[3].TEP**

Address offset: 0x52C

Channel 3 task end-point


**Page 183**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.12 CH[4].EEP**

Address offset: 0x530

Channel 4 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.13 CH[4].TEP**

Address offset: 0x534

Channel 4 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.14 CH[5].EEP**

Address offset: 0x538

Channel 5 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.15 CH[5].TEP**

Address offset: 0x53C

Channel 5 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.16 CH[6].EEP**

Address offset: 0x540

Channel 6 event end-point


**Page 184**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.17 CH[6].TEP**

Address offset: 0x544

Channel 6 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.18 CH[7].EEP**

Address offset: 0x548

Channel 7 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.19 CH[7].TEP**

Address offset: 0x54C

Channel 7 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.20 CH[8].EEP**

Address offset: 0x550

Channel 8 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.21 CH[8].TEP**

Address offset: 0x554

Channel 8 task end-point


**Page 185**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.22 CH[9].EEP**

Address offset: 0x558

Channel 9 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.23 CH[9].TEP**

Address offset: 0x55C

Channel 9 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.24 CH[10].EEP**

Address offset: 0x560

Channel 10 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.25 CH[10].TEP**

Address offset: 0x564

Channel 10 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.26 CH[11].EEP**

Address offset: 0x568

Channel 11 event end-point


**Page 186**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.27 CH[11].TEP**

Address offset: 0x56C

Channel 11 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.28 CH[12].EEP**

Address offset: 0x570

Channel 12 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.29 CH[12].TEP**

Address offset: 0x574

Channel 12 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.30 CH[13].EEP**

Address offset: 0x578

Channel 13 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.31 CH[13].TEP**

Address offset: 0x57C

Channel 13 task end-point


**Page 187**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.32 CH[14].EEP**

Address offset: 0x580

Channel 14 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.33 CH[14].TEP**

Address offset: 0x584

Channel 14 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.34 CH[15].EEP**

Address offset: 0x588

Channel 15 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.35 CH[15].TEP**

Address offset: 0x58C

Channel 15 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.36 CH[16].EEP**

Address offset: 0x590

Channel 16 event end-point


**Page 188**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.37 CH[16].TEP**

Address offset: 0x594

Channel 16 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.38 CH[17].EEP**

Address offset: 0x598

Channel 17 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.39 CH[17].TEP**

Address offset: 0x59C

Channel 17 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.40 CH[18].EEP**

Address offset: 0x5A0

Channel 18 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.41 CH[18].TEP**

Address offset: 0x5A4

Channel 18 task end-point


**Page 189**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.42 CH[19].EEP**

Address offset: 0x5A8

Channel 19 event end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW EEP Pointer to event register. Accepts only addresses to registers

from the Event group.


**22.2.43 CH[19].TEP**

Address offset: 0x5AC

Channel 19 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register. Accepts only addresses to registers

from the Task group.


**22.2.44 CHG[0]**

Address offset: 0x800

Channel group 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CH0 Include or exclude channel 0

Excluded 0 Exclude

Included 1 Include

B RW CH1 Include or exclude channel 1

Excluded 0 Exclude

Included 1 Include

C RW CH2 Include or exclude channel 2

Excluded 0 Exclude

Included 1 Include

D RW CH3 Include or exclude channel 3

Excluded 0 Exclude

Included 1 Include

E RW CH4 Include or exclude channel 4

Excluded 0 Exclude

Included 1 Include

F RW CH5 Include or exclude channel 5

Excluded 0 Exclude

Included 1 Include

G RW CH6 Include or exclude channel 6


**Page 190**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Excluded 0 Exclude

Included 1 Include

H RW CH7 Include or exclude channel 7

Excluded 0 Exclude

Included 1 Include

I RW CH8 Include or exclude channel 8

Excluded 0 Exclude

Included 1 Include

J RW CH9 Include or exclude channel 9

Excluded 0 Exclude

Included 1 Include

K RW CH10 Include or exclude channel 10

Excluded 0 Exclude

Included 1 Include

L RW CH11 Include or exclude channel 11

Excluded 0 Exclude

Included 1 Include

M RW CH12 Include or exclude channel 12

Excluded 0 Exclude

Included 1 Include

N RW CH13 Include or exclude channel 13

Excluded 0 Exclude

Included 1 Include

O RW CH14 Include or exclude channel 14

Excluded 0 Exclude

Included 1 Include

P RW CH15 Include or exclude channel 15

Excluded 0 Exclude

Included 1 Include

Q RW CH16 Include or exclude channel 16

Excluded 0 Exclude

Included 1 Include

R RW CH17 Include or exclude channel 17

Excluded 0 Exclude

Included 1 Include

S RW CH18 Include or exclude channel 18

Excluded 0 Exclude

Included 1 Include

T RW CH19 Include or exclude channel 19

Excluded 0 Exclude

Included 1 Include

U RW CH20 Include or exclude channel 20

Excluded 0 Exclude

Included 1 Include

V RW CH21 Include or exclude channel 21

Excluded 0 Exclude

Included 1 Include

W RW CH22 Include or exclude channel 22

Excluded 0 Exclude

Included 1 Include

X RW CH23 Include or exclude channel 23

Excluded 0 Exclude

Included 1 Include

Y RW CH24 Include or exclude channel 24

Excluded 0 Exclude


**Page 191**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Included 1 Include

Z RW CH25 Include or exclude channel 25

Excluded 0 Exclude

Included 1 Include

a RW CH26 Include or exclude channel 26

Excluded 0 Exclude

Included 1 Include

b RW CH27 Include or exclude channel 27

Excluded 0 Exclude

Included 1 Include

c RW CH28 Include or exclude channel 28

Excluded 0 Exclude

Included 1 Include

d RW CH29 Include or exclude channel 29

Excluded 0 Exclude

Included 1 Include

e RW CH30 Include or exclude channel 30

Excluded 0 Exclude

Included 1 Include

f RW CH31 Include or exclude channel 31

Excluded 0 Exclude

Included 1 Include


**22.2.45 CHG[1]**

Address offset: 0x804

Channel group 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CH0 Include or exclude channel 0

Excluded 0 Exclude

Included 1 Include

B RW CH1 Include or exclude channel 1

Excluded 0 Exclude

Included 1 Include

C RW CH2 Include or exclude channel 2

Excluded 0 Exclude

Included 1 Include

D RW CH3 Include or exclude channel 3

Excluded 0 Exclude

Included 1 Include

E RW CH4 Include or exclude channel 4

Excluded 0 Exclude

Included 1 Include

F RW CH5 Include or exclude channel 5

Excluded 0 Exclude

Included 1 Include

G RW CH6 Include or exclude channel 6

Excluded 0 Exclude

Included 1 Include

H RW CH7 Include or exclude channel 7

Excluded 0 Exclude


**Page 192**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Included 1 Include

I RW CH8 Include or exclude channel 8

Excluded 0 Exclude

Included 1 Include

J RW CH9 Include or exclude channel 9

Excluded 0 Exclude

Included 1 Include

K RW CH10 Include or exclude channel 10

Excluded 0 Exclude

Included 1 Include

L RW CH11 Include or exclude channel 11

Excluded 0 Exclude

Included 1 Include

M RW CH12 Include or exclude channel 12

Excluded 0 Exclude

Included 1 Include

N RW CH13 Include or exclude channel 13

Excluded 0 Exclude

Included 1 Include

O RW CH14 Include or exclude channel 14

Excluded 0 Exclude

Included 1 Include

P RW CH15 Include or exclude channel 15

Excluded 0 Exclude

Included 1 Include

Q RW CH16 Include or exclude channel 16

Excluded 0 Exclude

Included 1 Include

R RW CH17 Include or exclude channel 17

Excluded 0 Exclude

Included 1 Include

S RW CH18 Include or exclude channel 18

Excluded 0 Exclude

Included 1 Include

T RW CH19 Include or exclude channel 19

Excluded 0 Exclude

Included 1 Include

U RW CH20 Include or exclude channel 20

Excluded 0 Exclude

Included 1 Include

V RW CH21 Include or exclude channel 21

Excluded 0 Exclude

Included 1 Include

W RW CH22 Include or exclude channel 22

Excluded 0 Exclude

Included 1 Include

X RW CH23 Include or exclude channel 23

Excluded 0 Exclude

Included 1 Include

Y RW CH24 Include or exclude channel 24

Excluded 0 Exclude

Included 1 Include

Z RW CH25 Include or exclude channel 25

Excluded 0 Exclude

Included 1 Include


**Page 193**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

a RW CH26 Include or exclude channel 26

Excluded 0 Exclude

Included 1 Include

b RW CH27 Include or exclude channel 27

Excluded 0 Exclude

Included 1 Include

c RW CH28 Include or exclude channel 28

Excluded 0 Exclude

Included 1 Include

d RW CH29 Include or exclude channel 29

Excluded 0 Exclude

Included 1 Include

e RW CH30 Include or exclude channel 30

Excluded 0 Exclude

Included 1 Include

f RW CH31 Include or exclude channel 31

Excluded 0 Exclude

Included 1 Include


**22.2.46 CHG[2]**

Address offset: 0x808

Channel group 2


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CH0 Include or exclude channel 0

Excluded 0 Exclude

Included 1 Include

B RW CH1 Include or exclude channel 1

Excluded 0 Exclude

Included 1 Include

C RW CH2 Include or exclude channel 2

Excluded 0 Exclude

Included 1 Include

D RW CH3 Include or exclude channel 3

Excluded 0 Exclude

Included 1 Include

E RW CH4 Include or exclude channel 4

Excluded 0 Exclude

Included 1 Include

F RW CH5 Include or exclude channel 5

Excluded 0 Exclude

Included 1 Include

G RW CH6 Include or exclude channel 6

Excluded 0 Exclude

Included 1 Include

H RW CH7 Include or exclude channel 7

Excluded 0 Exclude

Included 1 Include

I RW CH8 Include or exclude channel 8

Excluded 0 Exclude

Included 1 Include


**Page 194**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

J RW CH9 Include or exclude channel 9

Excluded 0 Exclude

Included 1 Include

K RW CH10 Include or exclude channel 10

Excluded 0 Exclude

Included 1 Include

L RW CH11 Include or exclude channel 11

Excluded 0 Exclude

Included 1 Include

M RW CH12 Include or exclude channel 12

Excluded 0 Exclude

Included 1 Include

N RW CH13 Include or exclude channel 13

Excluded 0 Exclude

Included 1 Include

O RW CH14 Include or exclude channel 14

Excluded 0 Exclude

Included 1 Include

P RW CH15 Include or exclude channel 15

Excluded 0 Exclude

Included 1 Include

Q RW CH16 Include or exclude channel 16

Excluded 0 Exclude

Included 1 Include

R RW CH17 Include or exclude channel 17

Excluded 0 Exclude

Included 1 Include

S RW CH18 Include or exclude channel 18

Excluded 0 Exclude

Included 1 Include

T RW CH19 Include or exclude channel 19

Excluded 0 Exclude

Included 1 Include

U RW CH20 Include or exclude channel 20

Excluded 0 Exclude

Included 1 Include

V RW CH21 Include or exclude channel 21

Excluded 0 Exclude

Included 1 Include

W RW CH22 Include or exclude channel 22

Excluded 0 Exclude

Included 1 Include

X RW CH23 Include or exclude channel 23

Excluded 0 Exclude

Included 1 Include

Y RW CH24 Include or exclude channel 24

Excluded 0 Exclude

Included 1 Include

Z RW CH25 Include or exclude channel 25

Excluded 0 Exclude

Included 1 Include

a RW CH26 Include or exclude channel 26

Excluded 0 Exclude

Included 1 Include

b RW CH27 Include or exclude channel 27


**Page 195**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Excluded 0 Exclude

Included 1 Include

c RW CH28 Include or exclude channel 28

Excluded 0 Exclude

Included 1 Include

d RW CH29 Include or exclude channel 29

Excluded 0 Exclude

Included 1 Include

e RW CH30 Include or exclude channel 30

Excluded 0 Exclude

Included 1 Include

f RW CH31 Include or exclude channel 31

Excluded 0 Exclude

Included 1 Include


**22.2.47 CHG[3]**

Address offset: 0x80C

Channel group 3


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CH0 Include or exclude channel 0

Excluded 0 Exclude

Included 1 Include

B RW CH1 Include or exclude channel 1

Excluded 0 Exclude

Included 1 Include

C RW CH2 Include or exclude channel 2

Excluded 0 Exclude

Included 1 Include

D RW CH3 Include or exclude channel 3

Excluded 0 Exclude

Included 1 Include

E RW CH4 Include or exclude channel 4

Excluded 0 Exclude

Included 1 Include

F RW CH5 Include or exclude channel 5

Excluded 0 Exclude

Included 1 Include

G RW CH6 Include or exclude channel 6

Excluded 0 Exclude

Included 1 Include

H RW CH7 Include or exclude channel 7

Excluded 0 Exclude

Included 1 Include

I RW CH8 Include or exclude channel 8

Excluded 0 Exclude

Included 1 Include

J RW CH9 Include or exclude channel 9

Excluded 0 Exclude

Included 1 Include

K RW CH10 Include or exclude channel 10


**Page 196**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Excluded 0 Exclude

Included 1 Include

L RW CH11 Include or exclude channel 11

Excluded 0 Exclude

Included 1 Include

M RW CH12 Include or exclude channel 12

Excluded 0 Exclude

Included 1 Include

N RW CH13 Include or exclude channel 13

Excluded 0 Exclude

Included 1 Include

O RW CH14 Include or exclude channel 14

Excluded 0 Exclude

Included 1 Include

P RW CH15 Include or exclude channel 15

Excluded 0 Exclude

Included 1 Include

Q RW CH16 Include or exclude channel 16

Excluded 0 Exclude

Included 1 Include

R RW CH17 Include or exclude channel 17

Excluded 0 Exclude

Included 1 Include

S RW CH18 Include or exclude channel 18

Excluded 0 Exclude

Included 1 Include

T RW CH19 Include or exclude channel 19

Excluded 0 Exclude

Included 1 Include

U RW CH20 Include or exclude channel 20

Excluded 0 Exclude

Included 1 Include

V RW CH21 Include or exclude channel 21

Excluded 0 Exclude

Included 1 Include

W RW CH22 Include or exclude channel 22

Excluded 0 Exclude

Included 1 Include

X RW CH23 Include or exclude channel 23

Excluded 0 Exclude

Included 1 Include

Y RW CH24 Include or exclude channel 24

Excluded 0 Exclude

Included 1 Include

Z RW CH25 Include or exclude channel 25

Excluded 0 Exclude

Included 1 Include

a RW CH26 Include or exclude channel 26

Excluded 0 Exclude

Included 1 Include

b RW CH27 Include or exclude channel 27

Excluded 0 Exclude

Included 1 Include

c RW CH28 Include or exclude channel 28

Excluded 0 Exclude


**Page 197**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Included 1 Include

d RW CH29 Include or exclude channel 29

Excluded 0 Exclude

Included 1 Include

e RW CH30 Include or exclude channel 30

Excluded 0 Exclude

Included 1 Include

f RW CH31 Include or exclude channel 31

Excluded 0 Exclude

Included 1 Include


**22.2.48 CHG[4]**

Address offset: 0x810

Channel group 4


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CH0 Include or exclude channel 0

Excluded 0 Exclude

Included 1 Include

B RW CH1 Include or exclude channel 1

Excluded 0 Exclude

Included 1 Include

C RW CH2 Include or exclude channel 2

Excluded 0 Exclude

Included 1 Include

D RW CH3 Include or exclude channel 3

Excluded 0 Exclude

Included 1 Include

E RW CH4 Include or exclude channel 4

Excluded 0 Exclude

Included 1 Include

F RW CH5 Include or exclude channel 5

Excluded 0 Exclude

Included 1 Include

G RW CH6 Include or exclude channel 6

Excluded 0 Exclude

Included 1 Include

H RW CH7 Include or exclude channel 7

Excluded 0 Exclude

Included 1 Include

I RW CH8 Include or exclude channel 8

Excluded 0 Exclude

Included 1 Include

J RW CH9 Include or exclude channel 9

Excluded 0 Exclude

Included 1 Include

K RW CH10 Include or exclude channel 10

Excluded 0 Exclude

Included 1 Include

L RW CH11 Include or exclude channel 11

Excluded 0 Exclude


**Page 198**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Included 1 Include

M RW CH12 Include or exclude channel 12

Excluded 0 Exclude

Included 1 Include

N RW CH13 Include or exclude channel 13

Excluded 0 Exclude

Included 1 Include

O RW CH14 Include or exclude channel 14

Excluded 0 Exclude

Included 1 Include

P RW CH15 Include or exclude channel 15

Excluded 0 Exclude

Included 1 Include

Q RW CH16 Include or exclude channel 16

Excluded 0 Exclude

Included 1 Include

R RW CH17 Include or exclude channel 17

Excluded 0 Exclude

Included 1 Include

S RW CH18 Include or exclude channel 18

Excluded 0 Exclude

Included 1 Include

T RW CH19 Include or exclude channel 19

Excluded 0 Exclude

Included 1 Include

U RW CH20 Include or exclude channel 20

Excluded 0 Exclude

Included 1 Include

V RW CH21 Include or exclude channel 21

Excluded 0 Exclude

Included 1 Include

W RW CH22 Include or exclude channel 22

Excluded 0 Exclude

Included 1 Include

X RW CH23 Include or exclude channel 23

Excluded 0 Exclude

Included 1 Include

Y RW CH24 Include or exclude channel 24

Excluded 0 Exclude

Included 1 Include

Z RW CH25 Include or exclude channel 25

Excluded 0 Exclude

Included 1 Include

a RW CH26 Include or exclude channel 26

Excluded 0 Exclude

Included 1 Include

b RW CH27 Include or exclude channel 27

Excluded 0 Exclude

Included 1 Include

c RW CH28 Include or exclude channel 28

Excluded 0 Exclude

Included 1 Include

d RW CH29 Include or exclude channel 29

Excluded 0 Exclude

Included 1 Include


**Page 199**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

e RW CH30 Include or exclude channel 30

Excluded 0 Exclude

Included 1 Include

f RW CH31 Include or exclude channel 31

Excluded 0 Exclude

Included 1 Include


**22.2.49 CHG[5]**

Address offset: 0x814

Channel group 5


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CH0 Include or exclude channel 0

Excluded 0 Exclude

Included 1 Include

B RW CH1 Include or exclude channel 1

Excluded 0 Exclude

Included 1 Include

C RW CH2 Include or exclude channel 2

Excluded 0 Exclude

Included 1 Include

D RW CH3 Include or exclude channel 3

Excluded 0 Exclude

Included 1 Include

E RW CH4 Include or exclude channel 4

Excluded 0 Exclude

Included 1 Include

F RW CH5 Include or exclude channel 5

Excluded 0 Exclude

Included 1 Include

G RW CH6 Include or exclude channel 6

Excluded 0 Exclude

Included 1 Include

H RW CH7 Include or exclude channel 7

Excluded 0 Exclude

Included 1 Include

I RW CH8 Include or exclude channel 8

Excluded 0 Exclude

Included 1 Include

J RW CH9 Include or exclude channel 9

Excluded 0 Exclude

Included 1 Include

K RW CH10 Include or exclude channel 10

Excluded 0 Exclude

Included 1 Include

L RW CH11 Include or exclude channel 11

Excluded 0 Exclude

Included 1 Include

M RW CH12 Include or exclude channel 12

Excluded 0 Exclude

Included 1 Include


**Page 200**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

N RW CH13 Include or exclude channel 13

Excluded 0 Exclude

Included 1 Include

O RW CH14 Include or exclude channel 14

Excluded 0 Exclude

Included 1 Include

P RW CH15 Include or exclude channel 15

Excluded 0 Exclude

Included 1 Include

Q RW CH16 Include or exclude channel 16

Excluded 0 Exclude

Included 1 Include

R RW CH17 Include or exclude channel 17

Excluded 0 Exclude

Included 1 Include

S RW CH18 Include or exclude channel 18

Excluded 0 Exclude

Included 1 Include

T RW CH19 Include or exclude channel 19

Excluded 0 Exclude

Included 1 Include

U RW CH20 Include or exclude channel 20

Excluded 0 Exclude

Included 1 Include

V RW CH21 Include or exclude channel 21

Excluded 0 Exclude

Included 1 Include

W RW CH22 Include or exclude channel 22

Excluded 0 Exclude

Included 1 Include

X RW CH23 Include or exclude channel 23

Excluded 0 Exclude

Included 1 Include

Y RW CH24 Include or exclude channel 24

Excluded 0 Exclude

Included 1 Include

Z RW CH25 Include or exclude channel 25

Excluded 0 Exclude

Included 1 Include

a RW CH26 Include or exclude channel 26

Excluded 0 Exclude

Included 1 Include

b RW CH27 Include or exclude channel 27

Excluded 0 Exclude

Included 1 Include

c RW CH28 Include or exclude channel 28

Excluded 0 Exclude

Included 1 Include

d RW CH29 Include or exclude channel 29

Excluded 0 Exclude

Included 1 Include

e RW CH30 Include or exclude channel 30

Excluded 0 Exclude

Included 1 Include

f RW CH31 Include or exclude channel 31


**Page 201**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id f e d c b a Z Y X W V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Excluded 0 Exclude

Included 1 Include


**22.2.50 FORK[0].TEP**

Address offset: 0x910

Channel 0 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.51 FORK[1].TEP**

Address offset: 0x914

Channel 1 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.52 FORK[2].TEP**

Address offset: 0x918

Channel 2 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.53 FORK[3].TEP**

Address offset: 0x91C

Channel 3 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.54 FORK[4].TEP**

Address offset: 0x920

Channel 4 task end-point


**Page 202**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.55 FORK[5].TEP**

Address offset: 0x924

Channel 5 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.56 FORK[6].TEP**

Address offset: 0x928

Channel 6 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.57 FORK[7].TEP**

Address offset: 0x92C

Channel 7 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.58 FORK[8].TEP**

Address offset: 0x930

Channel 8 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.59 FORK[9].TEP**

Address offset: 0x934

Channel 9 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**Page 203**


22 PPI — Programmable peripheral interconnect


**22.2.60 FORK[10].TEP**

Address offset: 0x938

Channel 10 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.61 FORK[11].TEP**

Address offset: 0x93C

Channel 11 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.62 FORK[12].TEP**

Address offset: 0x940

Channel 12 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.63 FORK[13].TEP**

Address offset: 0x944

Channel 13 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.64 FORK[14].TEP**

Address offset: 0x948

Channel 14 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.65 FORK[15].TEP**

Address offset: 0x94C

Channel 15 task end-point


**Page 204**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.66 FORK[16].TEP**

Address offset: 0x950

Channel 16 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.67 FORK[17].TEP**

Address offset: 0x954

Channel 17 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.68 FORK[18].TEP**

Address offset: 0x958

Channel 18 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.69 FORK[19].TEP**

Address offset: 0x95C

Channel 19 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.70 FORK[20].TEP**

Address offset: 0x960

Channel 20 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**Page 205**


22 PPI — Programmable peripheral interconnect


**22.2.71 FORK[21].TEP**

Address offset: 0x964

Channel 21 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.72 FORK[22].TEP**

Address offset: 0x968

Channel 22 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.73 FORK[23].TEP**

Address offset: 0x96C

Channel 23 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.74 FORK[24].TEP**

Address offset: 0x970

Channel 24 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.75 FORK[25].TEP**

Address offset: 0x974

Channel 25 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.76 FORK[26].TEP**

Address offset: 0x978

Channel 26 task end-point


**Page 206**


22 PPI — Programmable peripheral interconnect


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.77 FORK[27].TEP**

Address offset: 0x97C

Channel 27 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.78 FORK[28].TEP**

Address offset: 0x980

Channel 28 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.79 FORK[29].TEP**

Address offset: 0x984

Channel 29 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.80 FORK[30].TEP**

Address offset: 0x988

Channel 30 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**22.2.81 FORK[31].TEP**

Address offset: 0x98C

Channel 31 task end-point


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TEP Pointer to task register


**Page 207**


22 PPI — Programmable peripheral interconnect


**Page 208**


23 RADIO — 2.4 GHz Radio

#### **23 RADIO — 2.4 GHz Radio**


The RADIO contains a 2.4 GHz radio receiver and a 2.4 GHz radio transmitter that is compatible with
Nordic's proprietary 1 Mbps and 2 Mbps radio modes in addition to 1 Mbps and 2 Mbps _Bluetooth_ _[®]_ low
energy mode.

EasyDMA in combination with an automated packet assembler and packet disassembler, and an automated
CRC generator and CRC checker, makes it very easy to configure and use the RADIO. See _Figure 31:_
_RADIO block diagram_ on page 209 for details.


RAM


RADIO


Device
Address

match


Packet synch


Packet
disassembler


Packet
assembler


Address

match


Bit counter


CRC


CRC


S0


L


S1


Payload


S0


L


S1


Payload


PACKETPTR


EasyDMA


MAXLEN


Dewhitening


Whitening


RSSI


2.4 GHz
Receiver


IFS
control unit


2.4 GHz
Transmitter


ANT1


**Figure 31: RADIO block diagram**


The RADIO includes a Device Address Match unit and an interframe spacing control unit that can be
utilized to simplify address white listing and interframe spacing respectively, in _Bluetooth_ Smart and similar
applications.

The RADIO also includes a Received Signal Strength Indicator (RSSI) and a bit counter. The bit counter
generates events when a preconfigured number of bits have been sent or received by the RADIO.

###### **23.1 EasyDMA**

The RADIO use EasyDMA for reading and writing of data packets from and to the RAM without CPU
involvement.

As illustrated in _Figure 31: RADIO block diagram_ on page 209, the RADIO's EasyDMA utilizes the same
PACKETPTR for receiving and transmitting packets. The CPU should reconfigure this pointer every time
before the RADIO is started via the START task.

The structure of a radio packet is described in detail in _Packet configuration_ on page 210. The data that
is stored in Data RAM and transported by EasyDMA consists of S0, LENGTH, S1, the payload itself, and a
static add-on sent immediately after the payload.

The size of each of the above elements in the frame is configurable (see _Packet configuration_ on page
210), and the space occupied in RAM depends on these settings. A size of zero is possible for any of the
fields, it is up to the user to make sure that the resulting frame complies with the RF protocol chosen.

For the field sizes defined in bits, the occupation in RAM will always be rounded up to the next full byte size
(for instance 3 bit length will allocate 1 byte in RAM, 9 bit length will allocate 2 bytes, etc.).


**Page 209**


23 RADIO — 2.4 GHz Radio


In addition, the S0INCL field in PCNF0 determines if S0 is present in RAM at all if its length is zero. If
present, one byte is allocated in RAM.

The size of S0 is configured through the S0LEN field in PCNF0. The size of LENGTH is configured through
the LFLEN field in PCNF0. The size of S1 is configured through the S1LEN field in PCNF0. The size of the
payload is configured through the value in RAM corresponding to the LENGTH field. The size of the static
add-on to the payload is configured through the STATLEN field in PCNF1.

The MAXLEN field in the PCNF1 register configures the maximum packet payload plus add-on size in
number of bytes that can be transmitted or received by the RADIO. This feature can be used to ensure that
the RADIO does not overwrite, or read beyond, the RAM assigned to the packet payload. This means that
if the packet payload length defined by PCNF1.STATLEN and the LENGTH field in the packet specifies a
packet larger than MAXLEN, the payload will be truncated at MAXLEN.

Note that MAXLEN includes the payload and the add-on, but excludes the size occupied by the S0, LENGTH
and S1 fields. This has to be taken into account when allocating RAM.

If the payload plus add-on length is specified larger than MAXLEN, the RADIO will still transmit or receive in
the same way as before except the payload is now truncated to MAXLEN. The packet's LENGTH field will
not be altered when the payload is truncated. The RADIO will calculate CRC as if the packet length is equal
to MAXLEN.

If the PACKETPTR is not pointing to the Data RAM region, an EasyDMA transfer may result in a HardFault
or RAM corruption. See _Memory_ on page 24 for more information about the different memory regions.

The DISABLED event indicates that the EasyDMA has finished accessing the RAM.

###### **23.2 Packet configuration**

A Radio packet contains the following fields: PREAMBLE, ADDRESS, S0, LENGTH, S1, PAYLOAD and
CRC.

See _Figure 32: On-air packet layout_ on page 210. Not shown in the figure is the static payload add-on (the
length of which is defined in STATLEN, and which is 0 bytes long in a standard BLE packet), and would be
sent between PAYLOAD and CRC. The Radio sends the different fields in the packet in the order they are
illustrated below, from left to right. The preamble will be sent least significant bit first on-air.


0x55
0xAA


1 0 1 0 1 0 1 0 1
0 1 0 1 0 1 0 1 0


0 1 0 1 0 1

1 0 1 0 1 0




PREAMBLE


BASE PREFIX S0 LENGTH S1 PAYLOAD CRC


LSByte


LSByte MSByte


ADDRESS


**Figure 32: On-air packet layout**


For all modes, except for 2 Mbit/s Bluetooth Low Energy mode, the preamble is one byte long. For 2 Mbit/s
Bluetooth Low Energy mode the preamble is 2 bytes long. If the first bit of the ADDRESS is 0 the preamble
will be set to 0xAA otherwise the PREAMBLE will be set to 0x55.

Radio packets are stored in memory inside instances of a radio packet data structure as illustrated in
_Figure 33: In-RAM representation of radio packet, S0, LENGTH and S1 are optional_ on page 210. The
PREAMBLE, ADDRESS and CRC fields are omitted in this data structure.


S0 LENGTH S1 PAYLOAD


0 LSByte n


**Figure 33: In-RAM representation of radio packet, S0, LENGTH and S1 are optional**


**Page 210**


23 RADIO — 2.4 GHz Radio


The byte ordering on air is always Least Significant Byte First for the ADDRESS and PAYLOAD fields and
Most Significant Byte First for the CRC field. The ADDRESS fields are always transmitted and received least
significant bit first on-air. The CRC field is always transmitted and received Most Significant Bit first. The bitendian, i.e. which order the bits are sent and received in, of the S0, LENGTH, S1 and PAYLOAD fields can
be configured via the ENDIAN in PCNF1.

The S0INCL field in PCNF0 determines if S0 is present in RAM at all if its length is zero. If present, one byte
is allocated in RAM.

The sizes of the S0, LENGTH and S1 fields can be individually configured via S0LEN, LFLEN and S1LEN in
PCNF0 respectively. If any of these fields are configured to be less than 8 bit long the, the least significant
bits of the fields, as seen from the RAM representation, are used.

If S0, LENGTH or S1 are specified with zero length their fields will be omitted in memory, otherwise each
field will be represented as a separate byte, regardless of the number of bits in their on-air counterpart.

###### **23.3 Maximum packet length**

Independent of the configuration of MAXLEN, the combined length of S0, LENGTH, S1 and PAYLOAD
cannot exceed 258 bytes.

###### **23.4 Address configuration**

The on-air radio ADDRESS field is composed of two parts, the base address field and the address prefix
field.

The size of the base address field is configurable via BALEN in PCNF1. The base address is truncated from
LSByte if the BALEN is less than 4. See _Table 41: Definition of logical addresses_ on page 211.

The on-air addresses are defined in the BASEn and PREFIXn registers, and it is only when writing these
registers the user will have to relate to actual on-air addresses. For other radio address registers such as the
TXADDRESS, RXADDRESSES and RXMATCH registers, logical radio addresses ranging from 0 to 7 are
being used. The relationship between the on-air radio addresses and the logical addresses is described in
_Table 41: Definition of logical addresses_ on page 211.


**Table 41: Definition of logical addresses**


**Logical address** **Base address** **Prefix byte**
0 BASE0 PREFIX0.AP0
1 BASE1 PREFIX0.AP1
2 BASE1 PREFIX0.AP2
3 BASE1 PREFIX0.AP3
4 BASE1 PREFIX1.AP4
5 BASE1 PREFIX1.AP5
6 BASE1 PREFIX1.AP6
7 BASE1 PREFIX1.AP7

###### **23.5 Data whitening**

The RADIO is able to do packet whitening and de-whitening.

See WHITEEN in PCNF1 register for how to enable whitening. When enabled, whitening and de-whitening
will be handled by the RADIO automatically as packets are sent and received.

The whitening word is generated using polynomial g(D) = D [7] + D [4 ] + 1, which then is XORed with the data
packet that is to be whitened, or de-whitened. See the figure below.


**Page 211**


D [0] D [4] D [7]


23 RADIO — 2.4 GHz Radio


Data out


##### **+ +**

Position     0      1      2      3           4      5      6

Data in


**Figure 34: Data whitening and de-whitening**


Whitening and de-whitening will be performed over the whole packet (except for the preamble and the
address field).

The linear feedback shift register, illustrated in _Figure 34: Data whitening and de-whitening_ on page 212
can be initialised via the DATAWHITEIV register.

###### **23.6 CRC**

The CRC generator in the RADIO calculates the CRC over the whole packet excluding the preamble. If
desirable, the address field can be excluded from the CRC calculation as well

See CRCCNF register for more information.

The CRC polynomial is configurable as illustrated in _Figure 35: CRC generation of an n bit CRC_ on page
212 where bit 0 in the CRCPOLY register corresponds to X [0] and bit 1 corresponds to X [1] etc. See
CRCPOLY for more information.


X [n]


X [n-1] X [2] X [1] X [0]


Packet
(Clocked in serially)
+ + + + +

bn b0


**Figure 35: CRC generation of an n bit CRC**


As illustrated in _Figure 35: CRC generation of an n bit CRC_ on page 212, the CRC is calculated by feeding
the packet serially through the CRC generator. Before the packet is clocked through the CRC generator, the
CRC generator's latches b0 through bn will be initialized with a predefined value specified in the CRCINIT
register. When the whole packet is clocked through the CRC generator, latches b0 through bn will hold the
resulting CRC. This value will be used by the RADIO during both transmission and reception but it is not
available to be read by the CPU at any time. A received CRC can however be read by the CPU via the
RXCRC register independent of whether or not it has passed the CRC check.

The length (n) of the CRC is configurable, see CRCCNF for more information.

After the whole packet including the CRC has been received, the RADIO will generate a CRCOK event if no
CRC errors were detected, or alternatively generate a CRCERROR event if CRC errors were detected.


**Page 212**


23 RADIO — 2.4 GHz Radio


The status of the CRC check can be read from the CRCSTATUS register after a packet has been received.

###### **23.7 Radio states**

The RADIO can enter a number of states.

The RADIO can enter the states described the table below. An overview state diagram for the RADIO is
illustrated in _Figure 36: Radio states_ on page 213. This figure shows how the tasks and events relate to
the RADIO's operation. The RADIO does not prevent a task from being triggered from the wrong state. If a
task is triggered from the wrong state, for example if the RXEN task is triggered from the RXDISABLE state,
this may lead to incorrect behaviour. As illustrated in _Figure 36: Radio states_ on page 213, the PAYLOAD
event is always generated even if the payload is zero.


**Table 42: RADIO state diagram**


**State** **Description**
DISABLED No operations are going on inside the radio and the power consumption is at a minimum
RXRU The radio is ramping up and preparing for reception
RXIDLE The radio is ready for reception to start
RX Reception has been started and the addresses enabled in the RXADDRESSES register are being monitored
TXRU The radio is ramping up and preparing for transmission
TXIDLE The radio is ready for transmission to start
TX The radio is transmitting a packet
RXDISABLE The radio is disabling the receiver
TXDISABLE The radio is disabling the transmitter


DISABLE


**TXDISABLE**


/ DISABLED


**DISABLED**


/ DISABLED


**RXDISABLE**


**RXRU** **RXIDLE** **RX**


Address sent / ADDRESS


START


**TXRU** **TXIDLE** **TX**


Ramp-up
complete
/ READY


STOP


Packet sent / END


Payload sent [payload length >=0]

/ PAYLOAD


TXEN


RXEN


Ramp-up
complete
/ READY


Address received [Address match]
Packet received / END

/ ADDRESS


START


STOP


Payload received [payload length >=0]

DISABLE
/ PAYLOAD


**Figure 36: Radio states**

###### **23.8 Transmit sequence**

Before the RADIO is able to transmit a packet, it must first ramp-up in TX mode.

See TXRU in _Figure 36: Radio states_ on page 213 and _Figure 37: Transmit sequence_ on page 214.
A TXRU ramp-up sequence is initiated when the TXEN task is triggered. After the radio has successfully
ramped up it will generate the READY event indicating that a packet transmission can be initiate. A packet
transmission is initiated by triggering the START task. As illustrated in _Figure 36: Radio states_ on page 213
the START task can first be triggered after the RADIO has entered into the TXIDLE state.

_Figure 37: Transmit sequence_ on page 214 illustrates a single packet transmission where the CPU
manually triggers the different tasks needed to control the flow of the RADIO, i.e. no shortcuts are used. If
shortcuts are not used, a certain amount of delay caused by CPU execution is expected between READY
and START, and between END and DISABLE. As illustrated in _Figure 37: Transmit sequence_ on page 214


**Page 213**


23 RADIO — 2.4 GHz Radio


the RADIO will by default transmit '1's between READY and START, and between END and DISABLED.
What is transmitted can be programmed through the DTX field in the MODECNF0 register.


TXRU


TXIDLE


TX TXIDLE TXDISABLE


(carrier) P A S0 L S1 PAYLOAD CRC (carrier)


1 2 3


**Figure 37: Transmit sequence**


A slightly modified version of the transmit sequence from _Figure 37: Transmit sequence_ on page 214 is
illustrated in _Figure 38: Transmit sequence using shortcuts to avoid delays_ on page 214 where the RADIO
is configured to use shortcuts between READY and START, and between END and DISABLE, which means
that no delay is introduced.


TXRU


TX TXDISABLE


P A S0 L S1 PAYLOAD CRC


(carrier)


1 2


**Figure 38: Transmit sequence using shortcuts to avoid delays**


The RADIO is able to send multiple packets one after the other without having to disable and re-enable the
RADIO between packets, this is illustrated in _Figure 39: Transmission of multiple packets_ on page 215.


**Page 214**


23 RADIO — 2.4 GHz Radio


TXRU


TX TXIDLE TX TXDISABLE


TXIDLE


TX


P A S0 L S1 PAYLOAD CRC


(carrier) P A S0 L S1 PAYLOAD CRC (carrier)


1 2 3


**Figure 39: Transmission of multiple packets**

###### **23.9 Receive sequence**

Before the RADIO is able to receive a packet, it must first ramp up in RX mode

See RXRU in _Figure 36: Radio states_ on page 213 and _Figure 40: Receive sequence_ on page 215.
An RXRU ramp-up sequence is initiated when the RXEN task is triggered. After the radio has successfully
ramped up it will generate the READY event indicating that a packet reception can be initiated. A packet
reception is initiated by triggering the START task. As illustrated in _Figure 36: Radio states_ on page 213
the START task can, first be triggered after the RADIO has entered into the RXIDLE state.

_Figure 40: Receive sequence_ on page 215 illustrates a single packet reception where the CPU manually
triggers the different tasks needed to control the flow of the RADIO, i.e. no shortcuts are used. If shortcuts
are not used, a certain amount of delay, caused by CPU execution, is expected between READY and
START, and between END and DISABLE. As illustrated _Figure 40: Receive sequence_ on page 215 the
RADIO will be listening and possibly receiving undefined data, illustrated with an 'X', from START and until a
packet with valid preamble (P) is received.


RXRU


RXIDLE


’X’


RX RXIDLE RXDISABLE


P A S0 L S1 PAYLOAD CRC


1 2 3


**Figure 40: Receive sequence**


A slightly modified version of the receive sequence from _Figure 40: Receive sequence_ on page 215 is
illustrated in _Figure 41: Receive sequence using shortcuts to avoid delays_ on page 216 where the the
RADIO is configured to use shortcuts between READY and START, and between END and DISABLE, which
means that no delay is introduced.


**Page 215**


23 RADIO — 2.4 GHz Radio


RXRU


’X’


RX RXDISABLE


P A S0 L S1 PAYLOAD CRC


1 2


**Figure 41: Receive sequence using shortcuts to avoid delays**


The RADIO is able to receive multiple packets one after the other without having to disable and re-enable
the RADIO between packets, this is illustrated _Figure 42: Reception of multiple packets_ on page 216.


RXRU


RX RXIDLE RX RXDISABLE


RXIDLE


RX


’X’ P A S0 L S1 PAYLOAD CRC ’X’


P A S0 L S1 PAYLOAD CRC


1 2 3


**Figure 42: Reception of multiple packets**

###### **23.10 Received Signal Strength Indicator (RSSI)**

The radio implements a mechanism for measuring the power in the received radio signal. This feature is
called Received Signal Strength Indicator (RSSI).

Sampling of the received signal strength is started by using the RSSISTART task. The sample can be read
from the RSSISAMPLE register.

The sample period of the RSSI is defined by RSSIPERIOD, see the device product specification for details.
The RSSI sample will hold the average received signal strength during this sample period.

For the RSSI sample to be valid the radio has to be enabled in receive mode (RXEN task) and the reception
has to be started (READY event followed by START task).

###### **23.11 Interframe spacing**

Interframe spacing is the time interval between two consecutive packets.

It is defined as the time, in micro seconds, from the end of the last bit of the previous packet received and
to the start of the first bit of the subsequent packet that is transmitted. The RADIO is able to enforce this


**Page 216**


23 RADIO — 2.4 GHz Radio


interval as specified in the TIFS register as long as TIFS is not specified to be shorter than the RADIO’s turnaround time, i.e. the time needed to switch off the receiver, and switch back on the transmitter.

TIFS is only enforced if END_DISABLE and DISABLED_TXEN or END_DISABLE and DISABLED_RXEN
shortcuts are enabled. TIFS is only qualified for use in BLE_1MBIT mode, and default ramp-up mode.

###### **23.12 Device address match**

The device address match feature is tailored for address white listing in a Bluetooth Smart and similar
implementations.

This feature enables on-the-fly device address matching while receiving a packet on air. This feature only
works in receive mode and as long as RADIO is configured for little endian, see PCNF1.ENDIAN.

The Device Address match unit assumes that the 48 first bits of the payload is the device address and that
bit number 6 in S0 is the TxAdd bit. See the Bluetooth Core Specification for more information about device
addresses, TxAdd and whitelisting.

The RADIO is able to listen for eight different device addresses at the same time. These addresses are
specified in a DAB/DAP register pair, one pair per address, in addition to a TxAdd bit configured in the
DACNF register. The DAB register specifies the 32 least significant bits of the device address, while the DAP
register specifies the 16 most significant bits of the device address.

Each of the device addresses can be individually included or excluded from the matching mechanism. This is
configured in the DACNF register.

###### **23.13 Bit counter**

The RADIO implements a simple counter that can be configured to generate an event after a specific number
of bits have been transmitted or received.

By using shortcuts, this counter can be started from different events generated by the RADIO and hence
count relative to these.

The bit counter is started by triggering the BCSTART task, and stopped by triggering the BCSTOP task.
A BCMATCH event will be generated when the bit counter has counted the number of bits specified in the
BCC register. The bit counter will continue to count bits until the DISABLED event is generated or until the
BCSTOP task is triggered. The CPU can therefore, after a BCMATCH event, reconfigure the BCC value for
new BCMATCH events within the same packet.

The bit counter can only be started after the RADIO has received the ADDRESS event.

The bit counter will stop and reset on BCSTOP, STOP, END and DISABLE tasks.

The figure below illustrates how the bit counter can be used to generate a BCMATCH event in the beginning
of the packet payload, and again generate a second BCMATCH event after sending 2 bytes (16 bits) of the
payload.


**Page 217**


23 RADIO — 2.4 GHz Radio


RXRU RX RXDISABLE


0 1 2


’X’


P A S0 L S1 PAYLOAD CRC


This example
assumes that the
combined length
of S0, Length (L)
and S1 is 12
bits.





**Figure 43: Bit counter example**

###### **23.14 Registers**


**Table 43: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40001000 RADIO RADIO 2.4 GHz radio


**Table 44: Register Overview**


**Register** **Offset** **Description**

TASKS_TXEN 0x000 Enable RADIO in TX mode

TASKS_RXEN 0x004 Enable RADIO in RX mode

TASKS_START 0x008 Start RADIO

TASKS_STOP 0x00C Stop RADIO

TASKS_DISABLE 0x010 Disable RADIO

TASKS_RSSISTART 0x014 Start the RSSI and take one single sample of the receive signal strength.

TASKS_RSSISTOP 0x018 Stop the RSSI measurement

TASKS_BCSTART 0x01C Start the bit counter

TASKS_BCSTOP 0x020 Stop the bit counter

EVENTS_READY 0x100 RADIO has ramped up and is ready to be started

EVENTS_ADDRESS 0x104 Address sent or received

EVENTS_PAYLOAD 0x108 Packet payload sent or received

EVENTS_END 0x10C Packet sent or received

EVENTS_DISABLED 0x110 RADIO has been disabled

EVENTS_DEVMATCH 0x114 A device address match occurred on the last received packet

EVENTS_DEVMISS 0x118 No device address match occurred on the last received packet

EVENTS_RSSIEND 0x11C Sampling of receive signal strength complete.

EVENTS_BCMATCH 0x128 Bit counter reached bit count value.

EVENTS_CRCOK 0x130 Packet received with CRC ok

EVENTS_CRCERROR 0x134 Packet received with CRC error

_SHORTS_ 0x200 Shortcut register

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_CRCSTATUS_ 0x400 CRC status

_RXMATCH_ 0x408 Received address

_RXCRC_ 0x40C CRC field of previously received packet


**Page 218**


23 RADIO — 2.4 GHz Radio


**Register** **Offset** **Description**

_DAI_ 0x410 Device address match index

_PACKETPTR_ 0x504 Packet pointer

_FREQUENCY_ 0x508 Frequency

_TXPOWER_ 0x50C Output power

_MODE_ 0x510 Data rate and modulation

_PCNF0_ 0x514 Packet configuration register 0

_PCNF1_ 0x518 Packet configuration register 1

_BASE0_ 0x51C Base address 0

_BASE1_ 0x520 Base address 1

_PREFIX0_ 0x524 Prefixes bytes for logical addresses 0-3

_PREFIX1_ 0x528 Prefixes bytes for logical addresses 4-7

_TXADDRESS_ 0x52C Transmit address select

_RXADDRESSES_ 0x530 Receive address select

_CRCCNF_ 0x534 CRC configuration

_CRCPOLY_ 0x538 CRC polynomial

_CRCINIT_ 0x53C CRC initial value

0x540 Reserved

_TIFS_ 0x544 Inter Frame Spacing in us

_RSSISAMPLE_ 0x548 RSSI sample

_STATE_ 0x550 Current radio state

_DATAWHITEIV_ 0x554 Data whitening initial value

_BCC_ 0x560 Bit counter compare

_DAB[0]_ 0x600 Device address base segment 0

_DAB[1]_ 0x604 Device address base segment 1

_DAB[2]_ 0x608 Device address base segment 2

_DAB[3]_ 0x60C Device address base segment 3

_DAB[4]_ 0x610 Device address base segment 4

_DAB[5]_ 0x614 Device address base segment 5

_DAB[6]_ 0x618 Device address base segment 6

_DAB[7]_ 0x61C Device address base segment 7

_DAP[0]_ 0x620 Device address prefix 0

_DAP[1]_ 0x624 Device address prefix 1

_DAP[2]_ 0x628 Device address prefix 2

_DAP[3]_ 0x62C Device address prefix 3

_DAP[4]_ 0x630 Device address prefix 4

_DAP[5]_ 0x634 Device address prefix 5

_DAP[6]_ 0x638 Device address prefix 6

_DAP[7]_ 0x63C Device address prefix 7

_DACNF_ 0x640 Device address match configuration

_MODECNF0_ 0x650 Radio mode configuration register 0

_POWER_ 0xFFC Peripheral power control


**23.14.1 SHORTS**

Address offset: 0x200

Shortcut register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW READY_START Shortcut between READY event and START task


See _EVENTS_READY_ and _TASKS_START_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

B RW END_DISABLE Shortcut between END event and DISABLE task


See _EVENTS_END_ and _TASKS_DISABLE_


**Page 219**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

C RW DISABLED_TXEN Shortcut between DISABLED event and TXEN task


See _EVENTS_DISABLED_ and _TASKS_TXEN_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

D RW DISABLED_RXEN Shortcut between DISABLED event and RXEN task


See _EVENTS_DISABLED_ and _TASKS_RXEN_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

E RW ADDRESS_RSSISTART Shortcut between ADDRESS event and RSSISTART task


See _EVENTS_ADDRESS_ and _TASKS_RSSISTART_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

F RW END_START Shortcut between END event and START task


See _EVENTS_END_ and _TASKS_START_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

G RW ADDRESS_BCSTART Shortcut between ADDRESS event and BCSTART task


See _EVENTS_ADDRESS_ and _TASKS_BCSTART_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

H RW DISABLED_RSSISTOP Shortcut between DISABLED event and RSSISTOP task


See _EVENTS_DISABLED_ and _TASKS_RSSISTOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**23.14.2 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L K I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW READY Write '1' to Enable interrupt for READY event


See _EVENTS_READY_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ADDRESS Write '1' to Enable interrupt for ADDRESS event


See _EVENTS_ADDRESS_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW PAYLOAD Write '1' to Enable interrupt for PAYLOAD event


See _EVENTS_PAYLOAD_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW END Write '1' to Enable interrupt for END event


**Page 220**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L K I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

See _EVENTS_END_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW DISABLED Write '1' to Enable interrupt for DISABLED event


See _EVENTS_DISABLED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW DEVMATCH Write '1' to Enable interrupt for DEVMATCH event


See _EVENTS_DEVMATCH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW DEVMISS Write '1' to Enable interrupt for DEVMISS event


See _EVENTS_DEVMISS_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW RSSIEND Write '1' to Enable interrupt for RSSIEND event


See _EVENTS_RSSIEND_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW BCMATCH Write '1' to Enable interrupt for BCMATCH event


See _EVENTS_BCMATCH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

K RW CRCOK Write '1' to Enable interrupt for CRCOK event


See _EVENTS_CRCOK_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

L RW CRCERROR Write '1' to Enable interrupt for CRCERROR event


See _EVENTS_CRCERROR_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**23.14.3 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L K I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW READY Write '1' to Disable interrupt for READY event


See _EVENTS_READY_

Clear 1 Disable


**Page 221**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L K I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ADDRESS Write '1' to Disable interrupt for ADDRESS event


See _EVENTS_ADDRESS_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW PAYLOAD Write '1' to Disable interrupt for PAYLOAD event


See _EVENTS_PAYLOAD_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW END Write '1' to Disable interrupt for END event


See _EVENTS_END_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW DISABLED Write '1' to Disable interrupt for DISABLED event


See _EVENTS_DISABLED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW DEVMATCH Write '1' to Disable interrupt for DEVMATCH event


See _EVENTS_DEVMATCH_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW DEVMISS Write '1' to Disable interrupt for DEVMISS event


See _EVENTS_DEVMISS_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW RSSIEND Write '1' to Disable interrupt for RSSIEND event


See _EVENTS_RSSIEND_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW BCMATCH Write '1' to Disable interrupt for BCMATCH event


See _EVENTS_BCMATCH_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

K RW CRCOK Write '1' to Disable interrupt for CRCOK event


See _EVENTS_CRCOK_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

L RW CRCERROR Write '1' to Disable interrupt for CRCERROR event


See _EVENTS_CRCERROR_

Clear 1 Disable

Disabled 0 Read: Disabled


**Page 222**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L K I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Read: Enabled


**23.14.4 CRCSTATUS**

Address offset: 0x400

CRC status


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R CRCSTATUS CRC status of packet received

CRCError 0 Packet received with CRC error

CRCOk 1 Packet received with CRC ok


**23.14.5 RXMATCH**

Address offset: 0x408

Received address


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R RXMATCH Received address


Logical address of which previous packet was received


**23.14.6 RXCRC**

Address offset: 0x40C

CRC field of previously received packet


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R RXCRC CRC field of previously received packet


CRC field of previously received packet


**23.14.7 DAI**

Address offset: 0x410

Device address match index


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R DAI Device address match index


Index (n) of device address, see DAB[n] and DAP[n], that got an

address match.


**23.14.8 PACKETPTR**

Address offset: 0x504


**Page 223**


23 RADIO — 2.4 GHz Radio


Packet pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PACKETPTR Packet pointer


Packet address to be used for the next transmission or

reception. When transmitting, the packet pointed to by this

address will be transmitted and when receiving, the received

packet will be written to this address. This address is a byte

aligned ram address.


**23.14.9 FREQUENCY**

Address offset: 0x508

Frequency


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A A A

**Reset 0x00000002** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW FREQUENCY [0..100] Radio channel frequency


Frequency = 2400 + FREQUENCY (MHz).

B RW MAP Channel map selection.

Default 0 Channel map between 2400 MHZ .. 2500 MHz


Frequency = 2400 + FREQUENCY (MHz)

Low 1 Channel map between 2360 MHZ .. 2460 MHz


Frequency = 2360 + FREQUENCY (MHz)


**23.14.10 TXPOWER**

Address offset: 0x50C

Output power


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TXPOWER RADIO output power.


Output power in number of dBm, i.e. if the value -20 is specified

the output power will be set to -20dBm.

Pos4dBm 0x04 +4 dBm

Pos3dBm 0x03 +3 dBm

0dBm 0x00 0 dBm

Neg4dBm 0xFC -4 dBm

Neg8dBm 0xF8 -8 dBm

Neg12dBm 0xF4 -12 dBm

Neg16dBm 0xF0 -16 dBm

Neg20dBm 0xEC -20 dBm

Neg30dBm 0xD8 -40 dBm Deprecated

Neg40dBm 0xD8 -40 dBm


**23.14.11 MODE**

Address offset: 0x510

Data rate and modulation


**Page 224**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Radio data rate and modulation setting. The radio supports

Frequency-shift Keying (FSK) modulation.

Nrf_1Mbit 0 1 Mbit/s Nordic proprietary radio mode

Nrf_2Mbit 1 2 Mbit/s Nordic proprietary radio mode

Nrf_250Kbit 2 250 kbit/s Nordic proprietary radio mode Deprecated

Ble_1Mbit 3 1 Mbit/s Bluetooth Low Energy

Ble_2Mbit 4 2 Mbit/s Bluetooth Low Energy


**23.14.12 PCNF0**

Address offset: 0x514

Packet configuration register 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id G F E E E E C A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LFLEN Length on air of LENGTH field in number of bits.

C RW S0LEN Length on air of S0 field in number of bytes.

E RW S1LEN Length on air of S1 field in number of bits.

F RW S1INCL Include or exclude S1 field in RAM

Automatic 0 Include S1 field in RAM only if S1LEN > 0

Include 1 Always include S1 field in RAM independent of S1LEN

G RW PLEN Length of preamble on air. Decision point: TASKS_START task

8bit 0 8-bit preamble

16bit 1 16-bit preamble


**23.14.13 PCNF1**

Address offset: 0x518

Packet configuration register 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E D C C C B B B B B B B B A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXLEN [0..255] Maximum length of packet payload. If the packet payload is

larger than MAXLEN, the radio will truncate the payload to

MAXLEN.

B RW STATLEN [0..255] Static length in number of bytes


The static length parameter is added to the total length of the

payload when sending and receiving packets, e.g. if the static

length is set to N the radio will receive or send N bytes more

than what is defined in the LENGTH field of the packet.

C RW BALEN [2..4] Base address length in number of bytes


The address field is composed of the base address and the one

byte long address prefix, e.g. set BALEN=2 to get a total address

of 3 bytes.

D RW ENDIAN On air endianness of packet, this applies to the S0, LENGTH, S1

and the PAYLOAD fields.

Little 0 Least Significant bit on air first

Big 1 Most significant bit on air first

E RW WHITEEN Enable or disable packet whitening

Disabled 0 Disable


**Page 225**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E D C C C B B B B B B B B A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Enable


**23.14.14 BASE0**

Address offset: 0x51C

Base address 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW BASE0 Base address 0


Radio base address 0.


**23.14.15 BASE1**

Address offset: 0x520

Base address 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW BASE1 Base address 1


Radio base address 1.


**23.14.16 PREFIX0**

Address offset: 0x524

Prefixes bytes for logical addresses 0-3


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D D D D D D D D C C C C C C C C B B B B B B B B A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW AP0 Address prefix 0.

B RW AP1 Address prefix 1.

C RW AP2 Address prefix 2.

D RW AP3 Address prefix 3.


**23.14.17 PREFIX1**

Address offset: 0x528

Prefixes bytes for logical addresses 4-7


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D D D D D D D D C C C C C C C C B B B B B B B B A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW AP4 Address prefix 4.

B RW AP5 Address prefix 5.

C RW AP6 Address prefix 6.

D RW AP7 Address prefix 7.


**Page 226**


23 RADIO — 2.4 GHz Radio


**23.14.18 TXADDRESS**

Address offset: 0x52C

Transmit address select


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TXADDRESS Transmit address select


Logical address to be used when transmitting a packet.


**23.14.19 RXADDRESSES**

Address offset: 0x530

Receive address select


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ADDR0 Enable or disable reception on logical address 0.

Disabled 0 Disable

Enabled 1 Enable

B RW ADDR1 Enable or disable reception on logical address 1.

Disabled 0 Disable

Enabled 1 Enable

C RW ADDR2 Enable or disable reception on logical address 2.

Disabled 0 Disable

Enabled 1 Enable

D RW ADDR3 Enable or disable reception on logical address 3.

Disabled 0 Disable

Enabled 1 Enable

E RW ADDR4 Enable or disable reception on logical address 4.

Disabled 0 Disable

Enabled 1 Enable

F RW ADDR5 Enable or disable reception on logical address 5.

Disabled 0 Disable

Enabled 1 Enable

G RW ADDR6 Enable or disable reception on logical address 6.

Disabled 0 Disable

Enabled 1 Enable

H RW ADDR7 Enable or disable reception on logical address 7.

Disabled 0 Disable

Enabled 1 Enable


**23.14.20 CRCCNF**

Address offset: 0x534

CRC configuration


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LEN [1..3] CRC length in number of bytes.

Disabled 0 CRC length is zero and CRC calculation is disabled

One 1 CRC length is one byte and CRC calculation is enabled

Two 2 CRC length is two bytes and CRC calculation is enabled


**Page 227**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Three 3 CRC length is three bytes and CRC calculation is enabled

B RW SKIPADDR Include or exclude packet address field out of CRC calculation.

Include 0 CRC calculation includes address field

Skip 1 CRC calculation does not include address field. The CRC

calculation will start at the first byte after the address.


**23.14.21 CRCPOLY**

Address offset: 0x538

CRC polynomial


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CRCPOLY CRC polynomial


Each term in the CRC polynomial is mapped to a bit in this

register which index corresponds to the term's exponent. The

least significant term/bit is hard-wired internally to 1, and bit

number 0 of the register content is ignored by the hardware.

The following example is for an 8 bit CRC polynomial: x8 + x7 +

x3 + x2 + 1 = 1 1000 1101 .


**23.14.22 CRCINIT**

Address offset: 0x53C

CRC initial value


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CRCINIT CRC initial value


Initial value for CRC calculation.


**23.14.23 TIFS**

Address offset: 0x544

Inter Frame Spacing in us


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TIFS Inter Frame Spacing in us


Inter frame space is the time interval between two consecutive

packets. It is defined as the time, in micro seconds, from the

end of the last bit of the previous packet to the start of the first

bit of the subsequent packet.


**23.14.24 RSSISAMPLE**

Address offset: 0x548

RSSI sample


**Page 228**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R RSSISAMPLE [0..127] RSSI sample


RSSI sample result. The value of this register is read as a positive

value while the actual received signal strength is a negative

value. Actual received signal strength is therefore as follows:

received signal strength = -A dBm


**23.14.25 STATE**

Address offset: 0x550

Current radio state


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R STATE Current radio state

Disabled 0 RADIO is in the Disabled state

RxRu 1 RADIO is in the RXRU state

RxIdle 2 RADIO is in the RXIDLE state

Rx 3 RADIO is in the RX state

RxDisable 4 RADIO is in the RXDISABLED state

TxRu 9 RADIO is in the TXRU state

TxIdle 10 RADIO is in the TXIDLE state

Tx 11 RADIO is in the TX state

TxDisable 12 RADIO is in the TXDISABLED state


**23.14.26 DATAWHITEIV**

Address offset: 0x554

Data whitening initial value


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A

**Reset 0x00000040** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DATAWHITEIV Data whitening initial value. Bit 6 is hard-wired to '1', writing '0'

to it has no effect, and it will always be read back and used by

the device as '1'.


Bit 0 corresponds to Position 6 of the LSFR, Bit 1 to Position 5,

etc.


**23.14.27 BCC**

Address offset: 0x560

Bit counter compare


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW BCC Bit counter compare


Bit counter compare register


**Page 229**


23 RADIO — 2.4 GHz Radio


**23.14.28 DAB[0]**

Address offset: 0x600

Device address base segment 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAB Device address base segment 0


**23.14.29 DAB[1]**

Address offset: 0x604

Device address base segment 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAB Device address base segment 1


**23.14.30 DAB[2]**

Address offset: 0x608

Device address base segment 2


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAB Device address base segment 2


**23.14.31 DAB[3]**

Address offset: 0x60C

Device address base segment 3


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAB Device address base segment 3


**23.14.32 DAB[4]**

Address offset: 0x610

Device address base segment 4


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAB Device address base segment 4


**23.14.33 DAB[5]**

Address offset: 0x614

Device address base segment 5


**Page 230**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAB Device address base segment 5


**23.14.34 DAB[6]**

Address offset: 0x618

Device address base segment 6


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAB Device address base segment 6


**23.14.35 DAB[7]**

Address offset: 0x61C

Device address base segment 7


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAB Device address base segment 7


**23.14.36 DAP[0]**

Address offset: 0x620

Device address prefix 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAP Device address prefix 0


**23.14.37 DAP[1]**

Address offset: 0x624

Device address prefix 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAP Device address prefix 1


**23.14.38 DAP[2]**

Address offset: 0x628

Device address prefix 2


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAP Device address prefix 2


**Page 231**


23 RADIO — 2.4 GHz Radio


**23.14.39 DAP[3]**

Address offset: 0x62C

Device address prefix 3


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAP Device address prefix 3


**23.14.40 DAP[4]**

Address offset: 0x630

Device address prefix 4


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAP Device address prefix 4


**23.14.41 DAP[5]**

Address offset: 0x634

Device address prefix 5


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAP Device address prefix 5


**23.14.42 DAP[6]**

Address offset: 0x638

Device address prefix 6


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAP Device address prefix 6


**23.14.43 DAP[7]**

Address offset: 0x63C

Device address prefix 7


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DAP Device address prefix 7


**23.14.44 DACNF**

Address offset: 0x640

Device address match configuration


**Page 232**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENA0 Enable or disable device address matching using device address

Disabled 0 Disabled

Enabled 1 Enabled

B RW ENA1 Enable or disable device address matching using device address

Disabled 0 Disabled

Enabled 1 Enabled

C RW ENA2 Enable or disable device address matching using device address

Disabled 0 Disabled

Enabled 1 Enabled

D RW ENA3 Enable or disable device address matching using device address

Disabled 0 Disabled

Enabled 1 Enabled

E RW ENA4 Enable or disable device address matching using device address

Disabled 0 Disabled

Enabled 1 Enabled

F RW ENA5 Enable or disable device address matching using device address

Disabled 0 Disabled

Enabled 1 Enabled

G RW ENA6 Enable or disable device address matching using device address

Disabled 0 Disabled

Enabled 1 Enabled

H RW ENA7 Enable or disable device address matching using device address

Disabled 0 Disabled

Enabled 1 Enabled

I RW TXADD0 TxAdd for device address 0

J RW TXADD1 TxAdd for device address 1

K RW TXADD2 TxAdd for device address 2

L RW TXADD3 TxAdd for device address 3

M RW TXADD4 TxAdd for device address 4

N RW TXADD5 TxAdd for device address 5

O RW TXADD6 TxAdd for device address 6

P RW TXADD7 TxAdd for device address 7


**23.14.45 MODECNF0**

Address offset: 0x650

Radio mode configuration register 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C C A

**Reset 0x00000200** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW RU Radio ramp-up time

Default 0 Default ramp-up time (tRXEN), compatible with firmware

written for nRF51

Fast 1 Fast ramp-up (tRXEN,FAST), see electrical specification for more

information


**Page 233**


23 RADIO — 2.4 GHz Radio


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C C A

**Reset 0x00000200** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

C RW DTX Default TX value


Specifies what the RADIO will transmit when it is not started, i.e.

between:


RADIO.EVENTS_READY and RADIO.TASKS_START


RADIO.EVENTS_END and RADIO.TASKS_START


RADIO.EVENTS_END and RADIO.EVENTS_DISABLED

B1 0 Transmit '1'

B0 1 Transmit '0'

Center 2 Transmit center frequency


When tuning the crystal for centre frequency, the RADIO must

be set in DTX = Center mode to be able to achieve the expected

accuracy.


**23.14.46 POWER**

Address offset: 0xFFC

Peripheral power control


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000001** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW POWER Peripheral power control. The peripheral and its registers will be

reset to its initial state by switching the peripheral off and then

back on again.

Disabled 0 Peripheral is powered off

Enabled 1 Peripheral is powered on

###### **23.15 Electrical specification**


**23.15.1 General Radio Characteristics**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fOP Operating frequencies 2360 2500 MHz

fPLL,PROG,RES PLL programming resolution 2 kHz

fPLL,CH,SP PLL channel spacing 1 MHz

fDELTA,1M Frequency deviation @ 1 Msps ±170 kHz

fDELTA,BLE,1M Frequency deviation @ BLE 1Msps ±250 kHz

fDELTA,2M Frequency deviation @ 2 Msps ±320 kHz

fDELTA,BLE,2M Frequency deviation @ BLE 2 Msps ±500 kHz

fskSPS On-the-air data rate 1 2 Msps


**23.15.2 Radio current consumption (Transmitter)**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

ITX,PLUS4dBM,DCDC TX only run current (DCDC, 3V) PRF =+4 dBm 7.5 mA

ITX,PLUS4dBM TX only run current PRF = +4 dBm 16.6 mA

ITX,0dBM,DCDC TX only run current (DCDC, 3V)PRF = 0dBm 5.3 mA

ITX,0dBM TX only run current PRF = 0dBm 11.6 mA

ITX,MINUS4dBM,DCDC TX only run current DCDC, 3V PRF = -4dBm 4.2 mA

ITX,MINUS4dBM TX only run current PRF = -4 dBm 9.3 mA

ITX,MINUS8dBM,DCDC TX only run current DCDC, 3V PRF = -8 dBm 3.8 mA


**Page 234**


23 RADIO — 2.4 GHz Radio


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

ITX,MINUS8dBM TX only run current PRF = -8 dBm 8.4 mA

ITX,MINUS12dBM,DCDC TX only run current DCDC, 3V PRF = -12 dBm 3.5 mA

ITX,MINUS12dBM TX only run current PRF = -12 dBm 7.7 mA

ITX,MINUS16dBM,DCDC TX only run current DCDC, 3V PRF = -16 dBm 3.3 mA

ITX,MINUS16dBM TX only run current PRF = -16 dBm 7.3 mA

ITX,MINUS20dBM,DCDC TX only run current DCDC, 3V PRF = -20 dBm 3.2 mA

ITX,MINUS20dBM TX only run current PRF = -20 dBm 7.0 mA

ITX,MINUS40dBM,DCDC TX only run current DCDC, 3V PRF = -40 dBm 2.7 mA

ITX,MINUS40dBM TX only run current PRF = -40 dBm 5.9 mA

ISTART,TX,DCDC TX start-up current DCDC, 3V, PRF = 4 dBm 4.0 mA

ISTART,TX TX start-up current, PRF = 4 dBm 8.8 mA


**23.15.3 Radio current consumption (Receiver)**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

IRX,1M,DCDC RX only run current (DCDC, 3V) 1Msps / 1Msps BLE 5.4 mA

IRX,1M RX only run current 1Msps / 1Msps BLE 11.7 mA

IRX,2M,DCDC RX only run current (DCDC, 3V) 2Msps / 2Msps BLE 5.8 mA

IRX,2M RX only run current 2Msps / 2Msps BLE 12.9 mA

ISTART,RX,DCDC RX start-up current (DCDC 3V) 3.5 mA

ISTART,RX,LDO RX start-up current (LDO 3V) 7.5 mA


**23.15.4 Transmitter specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

PRF Maximum output power 4 6 dBm

PRFC RF power control range 24 dB

PRFCR RF power accuracy ±4 dB


PRF1,1 1st Adjacent Channel Transmit Power 1 MHz (1 Msps Nordic

proprietary mode)

PRF2,1 2nd Adjacent Channel Transmit Power 2 MHz (1 Msps Nordic

proprietary mode)

PRF1,2 1st Adjacent Channel Transmit Power 2 MHz (2 Msps Nordic

proprietary mode)

PRF2,2 2nd Adjacent Channel Transmit Power 4 MHz (2 Msps Nordic

proprietary mode)


-25 dBc


-50 dBc


-25 dBc


-50 dBc


PRF1,2,BLE 1st Adjacent Channel Transmit Power 2 MHz (2 Msps BLE mode) -20 dBc


PRF2,2,BLE 2nd Adjacent Channel Transmit Power 4 MHz (2 Msps BLE

mode)


**23.15.5 Receiver operation**


-50 dBc


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

PRX,MAX Maximum received signal strength at < 0.1% BER 0 dBm

PSENS,IT,1M Sensitivity, 1Msps nRF mode [16] -93 dBm

PSENS,IT,SP,1M,BLE Sensitivity, 1Msps BLE ideal transmitter, <=37 bytes BER=1E-3 [17] -96 dBm


PSENS,IT,LP,1M,BLE Sensitivity, 1Msps BLE ideal transmitter >=128 bytes BER=1E-4


-95 dBm


PSENS,IT,2M Sensitivity, 2Msps nRF mode [19] -89 dBm


16 Typical sensitivity applies when ADDR0 is used for receiver address correlation. When ADDR[1...7] are used for
receiver address correlation, the typical sensitivity for this mode is degraded by 3dB.
17 As defined in the Bluetooth Core Specification v4.0 Volume 6: Core System Package (Low Energy Controller
Volume)
18 Equivalent BER limit < 10E-04
19 Typical sensitivity applies when ADDR0 is used for receiver address correlation. When ADDR[1...7] are used for
receiver address correlation, the typical sensitivity for this mode is degraded by 3dB.


**Page 235**


23 RADIO — 2.4 GHz Radio


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**


PSENS,IT,SP,2M,BLE Sensitivity, 2Msps BLE ideal transmitter, Packet length

<=37bytes

PSENS,DT,SP,2M,BLE Sensitivity, 2Msps BLE dirty transmitter, Packet length

<=37bytes


-93 dBm


-93 dBm


PSENS,IT,LP,2M,BLE Sensitivity, 2Msps BLE ideal transmitter >= 128bytes -92 dBm


PSENS,DT,LP,2M,BLE Sensitivity, 2Msps BLE dirty transmitter, Packet length >=

128bytes


**23.15.6 RX selectivity**

RX selectivity with equal modulation on interfering signal [20]


-92 dBm


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

C/I1M,co-channel 1Msps mode, Co-Channel interference 9 dB

C/I1M,-1MHz 1 Msps mode, Adjacent (-1 MHz) interference -2 dB

C/I1M,+1MHz 1 Msps mode, Adjacent (+1 MHz) interference -10 dB

C/I1M,-2MHz 1 Msps mode, Adjacent (-2 MHz) interference -19 dB

C/I1M,+2MHz 1 Msps mode, Adjacent (+2 MHz) interference -42 dB

C/I1M,-3MHz 1 Msps mode, Adjacent (-3 MHz) interference -38 dB

C/I1M,+3MHz 1 Msps mode, Adjacent (+3 MHz) interference -48 dB

C/I1M,±6MHz 1 Msps mode, Adjacent (≥6 MHz) interference -50 dB

C/I1MBLE,co-channel 1 Msps BLE mode, Co-Channel interference 6 dB

C/I1MBLE,-1MHz 1 Msps BLE mode, Adjacent (-1 MHz) interference -2 dB

C/I1MBLE,+1MHz 1 Msps BLE mode, Adjacent (+1 MHz) interference -9 dB

C/I1MBLE,-2MHz 1 Msps BLE mode, Adjacent (-2 MHz) interference -22 dB

C/I1MBLE,+2MHz 1 Msps BLE mode, Adjacent (+2 MHz) interference -46 dB

C/I1MBLE,>3MHz 1 Msps BLE mode, Adjacent (≥3 MHz) interference -50 dB

C/I1MBLE,image Image frequency Interference -22 dB

C/I1MBLE,image,1MHz Adjacent (1 MHz) interference to in-band image frequency -35 dB

C/I2M,co-channel 2Msps mode, Co-Channel interference 10 dB

C/I2M,-2MHz 2 Msps mode, Adjacent (-2 MHz) interference 6 dB

C/I2M,+2MHz 2 Msps mode, Adjacent (+2 MHz) interference -14 dB

C/I2M,-4MHz 2 Msps mode, Adjacent (-4 MHz) interference -20 dB

C/I2M,+4MHz 2 Msps mode, Adjacent (+4 MHz) interference -44 dB

C/I2M,-6MHz 2 Msps mode, Adjacent (-6 MHz) interference -42 dB

C/I2M,+6MHz 2 Msps mode, Adjacent (+6 MHz) interference -47 dB

C/I2M,≥12MHz 2 Msps mode, Adjacent (≥12 MHz) interference -52 dB

C/I2MBLE,co-channel 2 Msps BLE mode, Co-Channel interference 7 dB

C/I2MBLE,±2MHz 2 Msps BLE mode, Adjacent (±2 MHz) interference 0 dB

C/I2MBLE,±4MHz 2 Msps BLE mode, Adjacent (±4 MHz) interference -47 dB

C/I2MBLE,≥6MHz 2 Msps BLE mode, Adjacent (≥6 MHz) interference -49 dB

C/I2MBLE,image Image frequency Interference -21 dB

C/I2MBLE,image, 2MHz Adjacent (2 MHz) interference to in-band image frequency -36 dB


**23.15.7 RX intermodulation**

RX intermodulation [21]


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

PIMD,1M IMD performance, 1 Msps (3 MHz, 4 MHz, and 5 MHz offset) -33 dBm


PIMD,1M,BLE IMD performance, BLE 1 Msps (3 MHz, 4 MHz, and 5 MHz

offset)


-30 dBm


PIMD,2M IMD performance, 2 Msps (6 MHz, 8 MHz, and 10 MHz offset) -33 dBm


20 Wanted signal level at PIN = -67 dBm. One interferer is used, having equal modulation as the wanted
signal. The input power of the interferer where the sensitivity equals BER = 0.1% is presented
21 Wanted signal level at PIN = -64 dBm. Two interferers with equal input power are used. The interferer
closest in frequency is not modulated, the other interferer is modulated equal with the wanted signal.
The input power of the interferers where the sensitivity equals BER = 0.1% is presented.


**Page 236**


23 RADIO — 2.4 GHz Radio


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**


PIMD,2M,BLE IMD performance, BLE 2 Msps (6 MHz, 8 MHz, and 10 MHz

offset)


**23.15.8 Radio timing**


-32 dBm


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**


tTXEN Time between TXEN task and READY event after channel

FREQUENCY configured

tTXEN,FAST Time between TXEN task and READY event after channel

FREQUENCY configured (Fast Mode)

tTXDISABLE Time between DISABLE task and DISABLED event when the

radio was in TX and mode is set to 1Msps

tTXDISABLE,2M Time between DISABLE task and DISABLED event when the

radio was in TX and mode is set to 2Msps

tRXEN Time between the RXEN task and READY event after channel

FREQUENCY configured in default mode

tRXEN,FAST Time between the RXEN task and READY event after channel

FREQUENCY configured in fast mode

tSWITCH The minimum time taken to switch from RX to TX or TX to RX

(channel FREQUENCY unchanged)

tRXDISABLE Time between DISABLE task and DISABLED event when the

radio was in RX


140 us


40 us


6 us


4 us


140 us


40 us


20 us


0 us


tTXCHAIN TX chain delay 0.6 us

tRXCHAIN RX chain delay 9.4 us

tRXCHAIN,2M RX chain delay in 2Msps mode 5 us


**23.15.9 Received Signal Strength Indicator (RSSI) specifications**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

RSSIACC RSSI Accuracy Valid range -90 to -20 dBm ±2 dB

RSSIRESOLUTION RSSI resolution 1 dB

RSSIPERIOD Sample period 0.25 us


**23.15.10 Jitter**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**


tDISABLEDJITTER Jitter on DISABLED event relative to END event when shortcut

between END and DISABLE is enabled.


0.25 us


tREADYJITTER Jitter on READY event relative to TXEN and RXEN task. 0.25 us


**23.15.11 Delay when disabling the RADIO**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**


tTXDISABLE,1M Disable delay from TX.


Delay between DISABLE and DISABLED for MODE = Nrf_1Mbit

and MODE = Ble_1Mbit

tRXDISABLE,1M Disable delay from RX.


Delay between DISABLE and DISABLED for MODE = Nrf_1Mbit

and MODE = Ble_1Mbit


**Page 237**


6 us


0 us


24 TIMER — Timer/counter


#### **24 TIMER — Timer/counter**

The TIMER can operate in two modes: timer and counter.


TIMER


Increment


TIMER Core


BITMODE


Counter


CC[0..n]


PCLK1M


PCLK16M


Prescaler


fTIMER


PRESCALER MODE


**Figure 44: Block schematic for timer/counter**


The timer/counter runs on the high-frequency clock source (HFCLK) and includes a four-bit (1/2X) prescaler
that can divide the timer input clock from the HFCLK controller. Clock source selection between PCLK16M
and PCLK1M is automatic according to TIMER base frequency set by the prescaler. The TIMER base
frequency is always given as 16 MHz divided by the prescaler value.

The PPI system allows a TIMER event to trigger a task of any other system peripheral of the device. The
PPI system also enables the TIMER task/event features to generate periodic output and PWM signals to any
GPIO. The number of input/outputs used at the same time is limited by the number of GPIOTE channels.

The TIMER can operate in two modes, Timer mode and Counter mode. In both modes, the TIMER is started
by triggering the START task, and stopped by triggering the STOP task. After the timer is stopped the timer
can resume timing/counting by triggering the START task again. When timing/counting is resumed, the timer
will continue from the value it had prior to being stopped.

In Timer mode, the TIMER's internal Counter register is incremented by one for every tick of the timer
frequency fTIMER as illustrated in _Figure 44: Block schematic for timer/counter_ on page 238. The timer
frequency is derived from PCLK16M as shown below, using the values specified in the PRESCALER
register:

```
 fTIMER = 16 MHz / (2 [PRESCALER] )

```

When fTIMER <= 1 MHz the TIMER will use PCLK1M instead of PCLK16M for reduced power consumption.

In counter mode, the TIMER's internal Counter register is incremented by one each time the COUNT task
is triggered, that is, the timer frequency and the prescaler are not utilized in counter mode. Similarly, the
COUNT task has no effect in Timer mode.

The TIMER's maximum value is configured by changing the bit-width of the timer in the _BITMODE_ on page
243 register.

_PRESCALER_ on page 243 and the _BITMODE_ on page 243 must only be updated when the timer
is stopped. If these registers are updated while the TIMER is started then this may result in unpredictable
behavior.


**Page 238**


24 TIMER — Timer/counter


When the timer is incremented beyond its maximum value the Counter register will overflow and the TIMER
will automatically start over from zero.

The Counter register can be cleared, that is, its internal value set to zero explicitly, by triggering the CLEAR
task.

The TIMER implements multiple capture/compare registers.

Independent of prescaler setting the accuracy of the TIMER is equivalent to one tick of the timer frequency
fTIMER as illustrated in _Figure 44: Block schematic for timer/counter_ on page 238.

###### **24.1 Capture**

The TIMER implements one capture task for every available capture/compare register.

Every time the CAPTURE[n] task is triggered, the Counter value is copied to the CC[n] register.

###### **24.2 Compare**

The TIMER implements one COMPARE event for every available capture/compare register.

A COMPARE event is generated when the Counter is incremented and then becomes equal to the value
specified in one of the capture compare registers. When the Counter value becomes equal to the value
specified in a capture compare register CC[n], the corresponding compare event COMPARE[n] is generated.

_BITMODE_ on page 243 specifies how many bits of the Counter register and the capture/compare register
that are used when the comparison is performed. Other bits will be ignored.

###### **24.3 Task delays**

After the TIMER is started, the CLEAR task, COUNT task and the STOP task will guarantee to take effect
within one clock cycle of the PCLK16M.

###### **24.4 Task priority**

If the START task and the STOP task are triggered at the same time, that is, within the same period of
PCLK16M, the STOP task will be prioritized.

###### **24.5 Registers**


**Table 45: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40008000 TIMER TIMER0 Timer 0 This timer instance has 4 CC registers

(CC[0..3])

0x40009000 TIMER TIMER1 Timer 1 This timer instance has 4 CC registers

(CC[0..3])

0x4000A000 TIMER TIMER2 Timer 2 This timer instance has 4 CC registers

(CC[0..3])

0x4001A000 TIMER TIMER3 Timer 3 This timer instance has 6 CC registers

(CC[0..5])

0x4001B000 TIMER TIMER4 Timer 4 This timer instance has 6 CC registers

(CC[0..5])


**Table 46: Register Overview**


**Register** **Offset** **Description**

TASKS_START 0x000 Start Timer


**Page 239**


24 TIMER — Timer/counter


**Register** **Offset** **Description**

TASKS_STOP 0x004 Stop Timer

TASKS_COUNT 0x008 Increment Timer (Counter mode only)

TASKS_CLEAR 0x00C Clear time

TASKS_SHUTDOWN 0x010 Shut down timer Deprecated

TASKS_CAPTURE[0] 0x040 Capture Timer value to CC[0] register

TASKS_CAPTURE[1] 0x044 Capture Timer value to CC[1] register

TASKS_CAPTURE[2] 0x048 Capture Timer value to CC[2] register

TASKS_CAPTURE[3] 0x04C Capture Timer value to CC[3] register

TASKS_CAPTURE[4] 0x050 Capture Timer value to CC[4] register

TASKS_CAPTURE[5] 0x054 Capture Timer value to CC[5] register

EVENTS_COMPARE[0] 0x140 Compare event on CC[0] match

EVENTS_COMPARE[1] 0x144 Compare event on CC[1] match

EVENTS_COMPARE[2] 0x148 Compare event on CC[2] match

EVENTS_COMPARE[3] 0x14C Compare event on CC[3] match

EVENTS_COMPARE[4] 0x150 Compare event on CC[4] match

EVENTS_COMPARE[5] 0x154 Compare event on CC[5] match

_SHORTS_ 0x200 Shortcut register

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_MODE_ 0x504 Timer mode selection

_BITMODE_ 0x508 Configure the number of bits used by the TIMER

_PRESCALER_ 0x510 Timer prescaler register

_CC[0]_ 0x540 Capture/Compare register 0

_CC[1]_ 0x544 Capture/Compare register 1

_CC[2]_ 0x548 Capture/Compare register 2

_CC[3]_ 0x54C Capture/Compare register 3

_CC[4]_ 0x550 Capture/Compare register 4

_CC[5]_ 0x554 Capture/Compare register 5


**24.5.1 SHORTS**

Address offset: 0x200

Shortcut register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW COMPARE0_CLEAR Shortcut between COMPARE[0] event and CLEAR task


See _EVENTS_COMPARE[0]_ and _TASKS_CLEAR_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

B RW COMPARE1_CLEAR Shortcut between COMPARE[1] event and CLEAR task


See _EVENTS_COMPARE[1]_ and _TASKS_CLEAR_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

C RW COMPARE2_CLEAR Shortcut between COMPARE[2] event and CLEAR task


See _EVENTS_COMPARE[2]_ and _TASKS_CLEAR_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

D RW COMPARE3_CLEAR Shortcut between COMPARE[3] event and CLEAR task


See _EVENTS_COMPARE[3]_ and _TASKS_CLEAR_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

E RW COMPARE4_CLEAR Shortcut between COMPARE[4] event and CLEAR task


See _EVENTS_COMPARE[4]_ and _TASKS_CLEAR_


**Page 240**


24 TIMER — Timer/counter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

F RW COMPARE5_CLEAR Shortcut between COMPARE[5] event and CLEAR task


See _EVENTS_COMPARE[5]_ and _TASKS_CLEAR_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

G RW COMPARE0_STOP Shortcut between COMPARE[0] event and STOP task


See _EVENTS_COMPARE[0]_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

H RW COMPARE1_STOP Shortcut between COMPARE[1] event and STOP task


See _EVENTS_COMPARE[1]_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

I RW COMPARE2_STOP Shortcut between COMPARE[2] event and STOP task


See _EVENTS_COMPARE[2]_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

J RW COMPARE3_STOP Shortcut between COMPARE[3] event and STOP task


See _EVENTS_COMPARE[3]_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

K RW COMPARE4_STOP Shortcut between COMPARE[4] event and STOP task


See _EVENTS_COMPARE[4]_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

L RW COMPARE5_STOP Shortcut between COMPARE[5] event and STOP task


See _EVENTS_COMPARE[5]_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**24.5.2 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW COMPARE0 Write '1' to Enable interrupt for COMPARE[0] event


See _EVENTS_COMPARE[0]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW COMPARE1 Write '1' to Enable interrupt for COMPARE[1] event


See _EVENTS_COMPARE[1]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW COMPARE2 Write '1' to Enable interrupt for COMPARE[2] event


**Page 241**


24 TIMER — Timer/counter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

See _EVENTS_COMPARE[2]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW COMPARE3 Write '1' to Enable interrupt for COMPARE[3] event


See _EVENTS_COMPARE[3]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW COMPARE4 Write '1' to Enable interrupt for COMPARE[4] event


See _EVENTS_COMPARE[4]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW COMPARE5 Write '1' to Enable interrupt for COMPARE[5] event


See _EVENTS_COMPARE[5]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**24.5.3 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW COMPARE0 Write '1' to Disable interrupt for COMPARE[0] event


See _EVENTS_COMPARE[0]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW COMPARE1 Write '1' to Disable interrupt for COMPARE[1] event


See _EVENTS_COMPARE[1]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW COMPARE2 Write '1' to Disable interrupt for COMPARE[2] event


See _EVENTS_COMPARE[2]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW COMPARE3 Write '1' to Disable interrupt for COMPARE[3] event


See _EVENTS_COMPARE[3]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW COMPARE4 Write '1' to Disable interrupt for COMPARE[4] event


See _EVENTS_COMPARE[4]_

Clear 1 Disable


**Page 242**


24 TIMER — Timer/counter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW COMPARE5 Write '1' to Disable interrupt for COMPARE[5] event


See _EVENTS_COMPARE[5]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**24.5.4 MODE**

Address offset: 0x504

Timer mode selection


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE Timer mode

Timer 0 Select Timer mode

Counter 1 Select Counter mode Deprecated

LowPowerCounter 2 Select Low Power Counter mode


**24.5.5 BITMODE**

Address offset: 0x508

Configure the number of bits used by the TIMER


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW BITMODE Timer bit width

16Bit 0 16 bit timer bit width

08Bit 1 8 bit timer bit width

24Bit 2 24 bit timer bit width

32Bit 3 32 bit timer bit width


**24.5.6 PRESCALER**

Address offset: 0x510

Timer prescaler register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000004** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PRESCALER [0..9] Prescaler value


**24.5.7 CC[0]**

Address offset: 0x540

Capture/Compare register 0


**Page 243**


24 TIMER — Timer/counter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CC Capture/Compare value


Only the number of bits indicated by BITMODE will be used by

the TIMER.


**24.5.8 CC[1]**

Address offset: 0x544

Capture/Compare register 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CC Capture/Compare value


Only the number of bits indicated by BITMODE will be used by

the TIMER.


**24.5.9 CC[2]**

Address offset: 0x548

Capture/Compare register 2


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CC Capture/Compare value


Only the number of bits indicated by BITMODE will be used by

the TIMER.


**24.5.10 CC[3]**

Address offset: 0x54C

Capture/Compare register 3


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CC Capture/Compare value


Only the number of bits indicated by BITMODE will be used by

the TIMER.


**24.5.11 CC[4]**

Address offset: 0x550

Capture/Compare register 4


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CC Capture/Compare value


**Page 244**


24 TIMER — Timer/counter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Only the number of bits indicated by BITMODE will be used by

the TIMER.


**24.5.12 CC[5]**

Address offset: 0x554

Capture/Compare register 5


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CC Capture/Compare value


Only the number of bits indicated by BITMODE will be used by

the TIMER.

###### **24.6 Electrical specification**


**24.6.1 Timers Electrical Specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

ITIMER_1M Run current with 1 MHz clock input (PCLK1M) 3 5 8 µA

ITIMER_16M Run current with 16 MHz clock input (PCLK16M) 50 70 120 µA

tTIMER,START Time from START task is given until timer starts counting 0.25 µs


**Page 245**


25 RTC — Real-time counter

#### **25 RTC — Real-time counter**


The Real-time counter (RTC) module provides a generic, low power timer on the low-frequency clock source
(LFCLK).


32.768 kHz


START
task


STOP
task


CLEAR
task


TRIGOVRFLW
task


**Figure 45: RTC block schematic**


PRESCALER


COUNTER


RTC


CC[0:3]


TICK
event


OVRFLW
event


COMPARE[0..N]
event


The RTC module features a 24-bit COUNTER, a 12-bit (1/X) prescaler, capture/compare registers, and a tick
event generator for low power, tickless RTOS implementation.

###### **25.1 Clock source**

The RTC will run off the LFCLK.

The COUNTER resolution will therefore be 30.517 µs. Depending on the source, the RTC is able to run while
the HFCLK is OFF and PCLK16M is not available.

The software has to explicitely start LFCLK before using the RTC.

See _CLOCK — Clock control_ on page 104 for more information about clock sources.

###### **25.2 Resolution versus overflow and the PRESCALER**


Counter increment frequency:

```
 fRTC [kHz] = 32.768 / (PRESCALER + 1 )

```

The PRESCALER register is read/write when the RTC is stopped. The PRESCALER register is read-only
once the RTC is STARTed. Writing to the PRESCALER register when the RTC is started has no effect.

The PRESCALER is restarted on START, CLEAR and TRIGOVRFLW, that is, the prescaler value is latched
to an internal register (<<PRESC>>) on these tasks.

Examples:

**1.** Desired COUNTER frequency 100 Hz (10 ms counter period)

PRESCALER = round(32.768 kHz / 100 Hz) - 1 = 327

fRTC = 99.9 Hz


**Page 246**


25 RTC — Real-time counter


10009.576 µs counter period
**2.** Desired COUNTER frequency 8 Hz (125 ms counter period)

PRESCALER = round(32.768 kHz / 8 Hz) – 1 = 4095

fRTC = 8 Hz

125 ms counter period


**Table 47: RTC resolution versus overflow**


**Prescaler** **Counter resolution** **Overflow**
0 30.517 μs 512 seconds
2 [8] -1 7812.5 μs 131072 seconds
2 [12] -1 125 ms 582.542 hours

###### **25.3 COUNTER register**

The COUNTER increments on LFCLK when the internal PRESCALER register (<<PRESC>>) is 0x00.
<<PRESC>> is reloaded from the PRESCALER register. If enabled, the TICK event occurs on each
increment of the COUNTER. The TICK event is disabled by default.

SysClk


LFClk


TICK


PRESC


<<PRESC>>


0x000


0x000


0x000 0x000 0x000


COUNTER 0x000000 0x000001 0x000002 0x000003

**Figure 46: Timing diagram - COUNTER_PRESCALER_0**


SysClk


LFClk


TICK


PRESC


<<PRESC>>


0x000


0x001


0x001 0x000 0x001


COUNTER 0x000000 0x000001

**Figure 47: Timing diagram - COUNTER_PRESCALER_1**

###### **25.4 Overflow features**

The TRIGOVRFLW task sets the COUNTER value to 0xFFFFF0 to allow SW test of the overflow condition.

OVRFLW occurs when COUNTER overflows from 0xFFFFFF to 0.

**Important:** The OVRFLW event is disabled by default.

###### **25.5 TICK event**

The TICK event enables low power "tick-less" RTOS implementation as it optionally provides a regular
interrupt source for a RTOS without the need to use the ARM [®] SysTick feature.


**Page 247**


25 RTC — Real-time counter


Using the RTC TICK event rather than the SysTick allows the CPU to be powered down while still keeping
RTOS scheduling active.

**Important:** The TICK event is disabled by default.

###### **25.6 Event control feature**

To optimize RTC power consumption, events in the RTC can be individually disabled to prevent PCLK16M
and HFCLK being requested when those events are triggered. This is managed using the EVTEN register.

For example, if the TICK event is not required for an application, this event should be disabled as it is
frequently occurring and may increase power consumption if HFCLK otherwise could be powered down for
long durations.

This means that the RTC implements a slightly different task and event system compared to the standard
system described in _Peripheral interface_ on page 69. The RTC task and event system is illustrated in _Figure_
_48: Tasks, events and interrupts in the RTC_ on page 248.


Task signal from PPI


RTC


TASK


EVTEN m


write


OR


task


RTC
core


event


Event signal to PPI


INTEN m


EVENT m


IRQ signal to NVIC


**Figure 48: Tasks, events and interrupts in the RTC**

###### **25.7 Compare feature**

There are a number of Compare registers.

For more information, see _Registers_ on page 252.

When setting a compare register, the following behavior of the RTC compare event should be noted:

- If a CC register value is 0 when a CLEAR task is set, this will not trigger a COMPARE event.


**Page 248**


SysClk


LFClk


PRESC


COUNTER


CLEAR


CC[0]


COMPARE[0]


25 RTC — Real-time counter


0x000


X 0x000000


0x000000



**Figure 49: Timing diagram - COMPARE_CLEAR**

- If a CC register is N and the COUNTER value is N when the START task is set, this will not trigger a
COMPARE event.

SysClk


LFClk


PRESC


COUNTER


START


CC[0]


COMPARE[0]


0x000


N-1 N


N



N+1


**Figure 50: Timing diagram - COMPARE_START**

- COMPARE occurs when a CC register is N and the COUNTER value transitions from N-1 to N.

SysClk


LFClk


PRESC


COUNTER


CC[0]


COMPARE[0]


0x000


N-2 N-1 N N+1


N


0 1


**Figure 51: Timing diagram - COMPARE**

- If the COUNTER is N, writing N+2 to a CC register is guaranteed to trigger a COMPARE event at N+2.


**Page 249**


SysClk


LFClk


PRESC


COUNTER


CC[0]


COMPARE[0]


25 RTC — Real-time counter


0x000


N-1 N N+1 N+2

- 62.5 ns


X N+2


0 1


**Figure 52: Timing diagram - COMPARE_N+2**

- If the COUNTER is N, writing N or N+1 to a CC register may not trigger a COMPARE event.

SysClk


LFClk


PRESC


COUNTER


CC[0]


COMPARE[0]


0x000


N-2 N-1 N N+1


>= 0
X N+1



**Figure 53: Timing diagram - COMPARE_N+1**

- If the COUNTER is N and the current CC register value is N+1 or N+2 when a new CC value is written,
a match may trigger on the previous CC value before the new value takes effect. If the current CC value
greater than N+2 when the new value is written, there will be no event due to the old value.


SysClk


LFClk


PRESC


COUNTER


CC[0]


COMPARE[0]


0x000


N-2 N-1 N N+1


>= 0
N X


0 1


**Figure 54: Timing diagram - COMPARE_N-1**

###### **25.8 TASK and EVENT jitter/delay**

Jitter or delay in the RTC is due to the peripheral clock being a low frequency clock (LFCLK) which is not
synchronous to the faster PCLK16M.

Registers in the peripheral interface, part of the PCLK16M domain, have a set of mirrored registers in the
LFCLK domain. For example, the COUNTER value accessible from the CPU is in the PCLK16M domain
and is latched on read from an internal register called COUNTER in the LFCLK domain. COUNTER is the
register which is actually modified each time the RTC ticks. These registers must be synchronised between
clock domains (PCLK16M and LFCLK).

The following is a summary of the jitter introduced on tasks and events. Figures illustrating jitter follow.


**Page 250**


25 RTC — Real-time counter


**Table 48: RTC jitter magnitudes on tasks**


**Task** **Delay**
CLEAR, STOP, START, TRIGOVRFLOW +15 to 46 μs


**Table 49: RTC jitter magnitudes on events**


**Operation/Function** **Jitter**
START to COUNTER increment +/- 15 μs
COMPARE to COMPARE [22] +/- 62.5 ns


**1.** CLEAR and STOP (and TRIGOVRFLW; not shown) will be delayed as long as it takes for the peripheral
to clock a falling edge and rising of the LFCLK. This is between 15.2585 µs and 45.7755 µs – rounded to
15 µs and 46 µs for the remainder of the section.

SysClk


CLEAR

LFClk


PRESC


COUNTER


CLEARa


0x000


X X+1 0x000000 0x000001


0 or more SysClk after

**<= ~46 us**

**>= ~15 us**


CLEARb 1 or more SysClk before

**Figure 55: Timing diagram - DELAY_CLEAR**


SysClk


STOP

LFClk


PRESC


COUNTER


STOPa


0x000


X X+1


0 or more SysClk after

**<= ~46 us**

**>= ~15 us**


STOPb 1 or more SysClk before

**Figure 56: Timing diagram - DELAY_STOP**
**2.** The START task will start the RTC. Assuming that the LFCLK was previously running and stable, the
first increment of COUNTER (and instance of TICK event) will be typically after 30.5 µs +/-15 µs. In
some cases, in particular if the RTC is STARTed before the LFCLK is running, that timing can be up to
~250 µs. The software should therefore wait for the first TICK if it has to make sure the RTC is running.
Sending a TRIGOVRFLW task sets the COUNTER to a value close to overflow. However, since the
update of COUNTER relies on a stable LFCLK, sending this task while LFCLK is not running will start
LFCLK, but the update will then be delayed by the same amount of time of up to ~250 us. The figures
show the smallest and largest delays to on the START task which appears as a +/-15 µs jitter on the first
COUNTER increment.


22 Assumes RTC runs continuously between these events.

**Note:** 32.768 kHz clock jitter is additional to the numbers provided above.


**Page 251**


25 RTC — Real-time counter


SysClk


LFClk


PRESC


First tick


0x000


COUNTER X X+1 X+2 X+3


START


**>= ~15 us**

0 or more SysClk before


**Figure 57: Timing diagram - JITTER_START-**


SysClk


LFClk


PRESC


First tick


0x000


COUNTER


START


X X+1 X+2


**<= ~250 us**


**Figure 58: Timing diagram - JITTER_START+**

###### **25.9 Reading the COUNTER register**

To read the COUNTER register, the internal <<COUNTER>> value is sampled.

To ensure that the <<COUNTER>> is safely sampled (considering an LFCLK transition may occur during
a read), the CPU and core memory bus are halted for three cycles by lowering the core PREADY signal.
The Read takes the CPU 2 cycles in addition resulting in the COUNTER register read taking a fixed five
PCLK16M clock cycles.


SysClk


PREADY


LFClk


<<COUNTER>> N-1 N


COUNTER X N

**375.2 ns**

COUNTER_READ

**Figure 59: Timing diagram - COUNTER_READ**

###### **25.10 Registers**


**Table 50: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x4000B000 RTC RTC0 Real-time counter 0 CC[0..2] implemented, CC[3] not

implemented

0x40011000 RTC RTC1 Real-time counter 1 CC[0..3] implemented


**Page 252**


25 RTC — Real-time counter


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40024000 RTC RTC2 Real-time counter 2 CC[0..3] implemented


**Table 51: Register Overview**


**Register** **Offset** **Description**

TASKS_START 0x000 Start RTC COUNTER

TASKS_STOP 0x004 Stop RTC COUNTER

TASKS_CLEAR 0x008 Clear RTC COUNTER

TASKS_TRIGOVRFLW 0x00C Set COUNTER to 0xFFFFF0

EVENTS_TICK 0x100 Event on COUNTER increment

EVENTS_OVRFLW 0x104 Event on COUNTER overflow

EVENTS_COMPARE[0] 0x140 Compare event on CC[0] match

EVENTS_COMPARE[1] 0x144 Compare event on CC[1] match

EVENTS_COMPARE[2] 0x148 Compare event on CC[2] match

EVENTS_COMPARE[3] 0x14C Compare event on CC[3] match

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_EVTEN_ 0x340 Enable or disable event routing

_EVTENSET_ 0x344 Enable event routing

_EVTENCLR_ 0x348 Disable event routing

_COUNTER_ 0x504 Current COUNTER value

_PRESCALER_ 0x508 12 bit prescaler for COUNTER frequency (32768/(PRESCALER+1)).Must be written when RTC is

stopped

_CC[0]_ 0x540 Compare register 0

_CC[1]_ 0x544 Compare register 1

_CC[2]_ 0x548 Compare register 2

_CC[3]_ 0x54C Compare register 3


**25.10.1 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TICK Write '1' to Enable interrupt for TICK event


See _EVENTS_TICK_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW OVRFLW Write '1' to Enable interrupt for OVRFLW event


See _EVENTS_OVRFLW_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW COMPARE0 Write '1' to Enable interrupt for COMPARE[0] event


See _EVENTS_COMPARE[0]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW COMPARE1 Write '1' to Enable interrupt for COMPARE[1] event


See _EVENTS_COMPARE[1]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**Page 253**


25 RTC — Real-time counter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

E RW COMPARE2 Write '1' to Enable interrupt for COMPARE[2] event


See _EVENTS_COMPARE[2]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW COMPARE3 Write '1' to Enable interrupt for COMPARE[3] event


See _EVENTS_COMPARE[3]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**25.10.2 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TICK Write '1' to Disable interrupt for TICK event


See _EVENTS_TICK_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW OVRFLW Write '1' to Disable interrupt for OVRFLW event


See _EVENTS_OVRFLW_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW COMPARE0 Write '1' to Disable interrupt for COMPARE[0] event


See _EVENTS_COMPARE[0]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW COMPARE1 Write '1' to Disable interrupt for COMPARE[1] event


See _EVENTS_COMPARE[1]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW COMPARE2 Write '1' to Disable interrupt for COMPARE[2] event


See _EVENTS_COMPARE[2]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW COMPARE3 Write '1' to Disable interrupt for COMPARE[3] event


See _EVENTS_COMPARE[3]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**Page 254**


25 RTC — Real-time counter


**25.10.3 EVTEN**

Address offset: 0x340

Enable or disable event routing


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TICK Enable or disable event routing for TICK event


See _EVENTS_TICK_

Disabled 0 Disable

Enabled 1 Enable

B RW OVRFLW Enable or disable event routing for OVRFLW event


See _EVENTS_OVRFLW_

Disabled 0 Disable

Enabled 1 Enable

C RW COMPARE0 Enable or disable event routing for COMPARE[0] event


See _EVENTS_COMPARE[0]_

Disabled 0 Disable

Enabled 1 Enable

D RW COMPARE1 Enable or disable event routing for COMPARE[1] event


See _EVENTS_COMPARE[1]_

Disabled 0 Disable

Enabled 1 Enable

E RW COMPARE2 Enable or disable event routing for COMPARE[2] event


See _EVENTS_COMPARE[2]_

Disabled 0 Disable

Enabled 1 Enable

F RW COMPARE3 Enable or disable event routing for COMPARE[3] event


See _EVENTS_COMPARE[3]_

Disabled 0 Disable

Enabled 1 Enable


**25.10.4 EVTENSET**

Address offset: 0x344

Enable event routing


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TICK Write '1' to Enable event routing for TICK event


See _EVENTS_TICK_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW OVRFLW Write '1' to Enable event routing for OVRFLW event


See _EVENTS_OVRFLW_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW COMPARE0 Write '1' to Enable event routing for COMPARE[0] event


See _EVENTS_COMPARE[0]_

Set 1 Enable


**Page 255**


25 RTC — Real-time counter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW COMPARE1 Write '1' to Enable event routing for COMPARE[1] event


See _EVENTS_COMPARE[1]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW COMPARE2 Write '1' to Enable event routing for COMPARE[2] event


See _EVENTS_COMPARE[2]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW COMPARE3 Write '1' to Enable event routing for COMPARE[3] event


See _EVENTS_COMPARE[3]_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**25.10.5 EVTENCLR**

Address offset: 0x348

Disable event routing


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TICK Write '1' to Disable event routing for TICK event


See _EVENTS_TICK_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW OVRFLW Write '1' to Disable event routing for OVRFLW event


See _EVENTS_OVRFLW_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW COMPARE0 Write '1' to Disable event routing for COMPARE[0] event


See _EVENTS_COMPARE[0]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW COMPARE1 Write '1' to Disable event routing for COMPARE[1] event


See _EVENTS_COMPARE[1]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW COMPARE2 Write '1' to Disable event routing for COMPARE[2] event


See _EVENTS_COMPARE[2]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**Page 256**


25 RTC — Real-time counter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

F RW COMPARE3 Write '1' to Disable event routing for COMPARE[3] event


See _EVENTS_COMPARE[3]_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**25.10.6 COUNTER**

Address offset: 0x504

Current COUNTER value


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R COUNTER Counter value


**25.10.7 PRESCALER**

Address offset: 0x508

12 bit prescaler for COUNTER frequency (32768/(PRESCALER+1)).Must be written when RTC is stopped


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PRESCALER Prescaler value


**25.10.8 CC[0]**

Address offset: 0x540

Compare register 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW COMPARE Compare value


**25.10.9 CC[1]**

Address offset: 0x544

Compare register 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW COMPARE Compare value


**25.10.10 CC[2]**

Address offset: 0x548

Compare register 2


**Page 257**


25 RTC — Real-time counter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW COMPARE Compare value


**25.10.11 CC[3]**

Address offset: 0x54C

Compare register 3


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW COMPARE Compare value

###### **25.11 Electrical specification**


**25.11.1 RTC Electrical Specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

IRTC Run current Real Time Counter (LFCLK source) 0.1 µA


**Page 258**


26 RNG — Random number generator

#### **26 RNG — Random number generator**


The Random number generator (RNG) generates true non-deterministic random numbers based on internal
thermal noise that are suitable for cryptographic purposes. The RNG does not require a seed value.


START
generator


Random number


VALRDY

VALUE


STOP


**Figure 60: Random number generator**


The RNG is started by triggering the START task and stopped by triggering the STOP task. When started,
new random numbers are generated continuously and written to the VALUE register when ready. A VALRDY
event is generated for every new random number that is written to the VALUE register. This means that after
a VALRDY event is generated the CPU has the time until the next VALRDY event to read out the random
number from the VALUE register before it is overwritten by a new random number.

###### **26.1 Bias correction**

A bias correction algorithm is employed on the internal bit stream to remove any bias toward '1' or '0'. The
bits are then queued into an eight-bit register for parallel readout from the VALUE register.

It is possible to enable bias correction in the CONFIG register. This will result in slower value generation, but
will ensure a statistically uniform distribution of the random values.

###### **26.2 Speed**

The time needed to generate one random byte of data is unpredictable, and may vary from one byte to the
next. This is especially true when bias correction is enabled.

###### **26.3 Registers**


**Table 52: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x4000D000 RNG RNG Random number generator


**Table 53: Register Overview**


**Register** **Offset** **Description**

TASKS_START 0x000 Task starting the random number generator

TASKS_STOP 0x004 Task stopping the random number generator

EVENTS_VALRDY 0x100 Event being generated for every new random number written to the VALUE register

_SHORTS_ 0x200 Shortcut register

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_CONFIG_ 0x504 Configuration register

_VALUE_ 0x508 Output random number


**26.3.1 SHORTS**

Address offset: 0x200

Shortcut register


**Page 259**


26 RNG — Random number generator


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW VALRDY_STOP Shortcut between VALRDY event and STOP task


See _EVENTS_VALRDY_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**26.3.2 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW VALRDY Write '1' to Enable interrupt for VALRDY event


See _EVENTS_VALRDY_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**26.3.3 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW VALRDY Write '1' to Disable interrupt for VALRDY event


See _EVENTS_VALRDY_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**26.3.4 CONFIG**

Address offset: 0x504

Configuration register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DERCEN Bias correction

Disabled 0 Disabled

Enabled 1 Enabled


**26.3.5 VALUE**

Address offset: 0x508

Output random number


**Page 260**


26 RNG — Random number generator


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R VALUE [0..255] Generated random number

###### **26.4 Electrical specification**


**26.4.1 RNG Electrical Specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

IRNG Run current, CPU sleeping. 500 µA


tRNG,START Time from setting the START task to generation begins. This is

a one-time delay on START signal and does not apply between

samples.

tRNG,RAW Run time per byte without bias correction. Uniform distribution

of 0 and 1 is not guaranteed.

tRNG,BC Run time per byte with bias correction. Uniform distribution

of 0 and 1 is guaranteed. Time to generate a byte cannot be

guaranteed.


**Page 261**


128 µs


30 µs


120 µs


27 TEMP — Temperature sensor

#### **27 TEMP — Temperature sensor**


The temperature sensor measures die temperature over the temperature range of the device. Linearity
compensation can be implemented if required by the application.

Listed here are the main features for TEMP:

- Temperature range is greater than or equal to operating temperature of the device

- Resolution is 0.25 degrees

TEMP is started by triggering the START task.

When the temperature measurement is completed, a DATARDY event will be generated and the result of the
measurement can be read from the TEMP register.

To achieve the measurement accuracy stated in the electrical specification, the crystal oscillator must be
selected as the HFCLK source, see _CLOCK — Clock control_ on page 104 for more information.

When the temperature measurement is completed, TEMP analog electronics power down to save power.

TEMP only supports one-shot operation, meaning that every TEMP measurement has to be explicitly started
using the START task.

###### **27.1 Registers**


**Table 54: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x4000C000 TEMP TEMP Temperature sensor


**Table 55: Register Overview**


**Register** **Offset** **Description**

TASKS_START 0x000 Start temperature measurement

TASKS_STOP 0x004 Stop temperature measurement

EVENTS_DATARDY 0x100 Temperature measurement complete, data ready

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_TEMP_ 0x508 Temperature in °C (0.25° steps)

_A0_ 0x520 Slope of 1st piece wise linear function

_A1_ 0x524 Slope of 2nd piece wise linear function

_A2_ 0x528 Slope of 3rd piece wise linear function

_A3_ 0x52C Slope of 4th piece wise linear function

_A4_ 0x530 Slope of 5th piece wise linear function

_A5_ 0x534 Slope of 6th piece wise linear function

_B0_ 0x540 y-intercept of 1st piece wise linear function

_B1_ 0x544 y-intercept of 2nd piece wise linear function

_B2_ 0x548 y-intercept of 3rd piece wise linear function

_B3_ 0x54C y-intercept of 4th piece wise linear function

_B4_ 0x550 y-intercept of 5th piece wise linear function

_B5_ 0x554 y-intercept of 6th piece wise linear function

_T0_ 0x560 End point of 1st piece wise linear function

_T1_ 0x564 End point of 2nd piece wise linear function

_T2_ 0x568 End point of 3rd piece wise linear function

_T3_ 0x56C End point of 4th piece wise linear function

_T4_ 0x570 End point of 5th piece wise linear function


**Page 262**


27 TEMP — Temperature sensor


**27.1.1 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DATARDY Write '1' to Enable interrupt for DATARDY event


See _EVENTS_DATARDY_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**27.1.2 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DATARDY Write '1' to Disable interrupt for DATARDY event


See _EVENTS_DATARDY_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**27.1.3 TEMP**

Address offset: 0x508

Temperature in °C (0.25° steps)


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R TEMP Temperature in °C (0.25° steps)


Result of temperature measurement. Die temperature in °C, 2's

complement format, 0.25 °C steps


Decision point: DATARDY


**27.1.4 A0**

Address offset: 0x520

Slope of 1st piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x00000320** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **0** **1** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW A0 Slope of 1st piece wise linear function


**27.1.5 A1**

Address offset: 0x524


**Page 263**


27 TEMP — Temperature sensor


Slope of 2nd piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x00000343** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **1** **0** **0** **0** **0** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW A1 Slope of 2nd piece wise linear function


**27.1.6 A2**

Address offset: 0x528

Slope of 3rd piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x0000035D** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **1** **0** **1** **1** **1** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW A2 Slope of 3rd piece wise linear function


**27.1.7 A3**

Address offset: 0x52C

Slope of 4th piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x00000400** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW A3 Slope of 4th piece wise linear function


**27.1.8 A4**

Address offset: 0x530

Slope of 5th piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x0000047F** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW A4 Slope of 5th piece wise linear function


**27.1.9 A5**

Address offset: 0x534

Slope of 6th piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A

**Reset 0x0000037B** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **1** **1** **1** **1** **0** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW A5 Slope of 6th piece wise linear function


**27.1.10 B0**

Address offset: 0x540

y-intercept of 1st piece wise linear function


**Page 264**


27 TEMP — Temperature sensor


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00003FCC** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **1** **0** **0** **1** **1** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW B0 y-intercept of 1st piece wise linear function


**27.1.11 B1**

Address offset: 0x544

y-intercept of 2nd piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00003F98** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **0** **0** **1** **1** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW B1 y-intercept of 2nd piece wise linear function


**27.1.12 B2**

Address offset: 0x548

y-intercept of 3rd piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00003F98** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **1** **1** **1** **0** **0** **1** **1** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW B2 y-intercept of 3rd piece wise linear function


**27.1.13 B3**

Address offset: 0x54C

y-intercept of 4th piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00000012** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW B3 y-intercept of 4th piece wise linear function


**27.1.14 B4**

Address offset: 0x550

y-intercept of 5th piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x0000006A** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **1** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW B4 y-intercept of 5th piece wise linear function


**27.1.15 B5**

Address offset: 0x554

y-intercept of 6th piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A

**Reset 0x00003DD0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **1** **0** **1** **1** **1** **0** **1** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW B5 y-intercept of 6th piece wise linear function


**Page 265**


27 TEMP — Temperature sensor


**27.1.16 T0**

Address offset: 0x560

End point of 1st piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x000000E2** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **1** **0** **0** **0** **1** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW T0 End point of 1st piece wise linear function


**27.1.17 T1**

Address offset: 0x564

End point of 2nd piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW T1 End point of 2nd piece wise linear function


**27.1.18 T2**

Address offset: 0x568

End point of 3rd piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000014** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW T2 End point of 3rd piece wise linear function


**27.1.19 T3**

Address offset: 0x56C

End point of 4th piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000019** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **1** **0** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW T3 End point of 4th piece wise linear function


**27.1.20 T4**

Address offset: 0x570

End point of 5th piece wise linear function


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000050** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **1** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW T4 End point of 5th piece wise linear function


**Page 266**


27 TEMP — Temperature sensor

###### **27.2 Electrical specification**


**27.2.1 Temperature Sensor Electrical Specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

tTEMP Time required for temperature measurement 36 µs

TTEMP,RANGE Temperature sensor range -40 85 °C

TTEMP,ACC Temperature sensor accuracy -5 5 °C

TTEMP,RES Temperature sensor resolution 0.25 °C

TTEMP,STB Sample to sample stability at constant device temperature +/-0.25 °C

TTEMP,OFFST Sample offset at 25°C -2.5 2.5 °C


**Page 267**


28 ECB — AES electronic codebook mode
encryption

#### **28 ECB — AES electronic codebook mode encryption**


The AES electronic codebook mode encryption (ECB) can be used for a range of cryptographic functions
like hash generation, digital signatures, and keystream generation for data encryption/decryption. The ECB
encryption block supports 128 bit AES encryption (encryption only, not decryption).

AES ECB operates with EasyDMA access to system Data RAM for in-place operations on cleartext
and ciphertext during encryption. ECB uses the same AES core as the CCM and AAR blocks and is an
asynchronous operation which may not complete if the AES core is busy.

AES ECB features:

- 128 bit AES encryption

- Supports standard AES ECB block encryption

- Memory pointer support

- DMA data transfer

AES ECB performs a 128 bit AES block encrypt. At the STARTECB task, data and key is loaded into
the algorithm by EasyDMA. When output data has been written back to memory, the ENDECB event is
triggered.

AES ECB can be stopped by triggering the STOPECB task.

###### **28.1 Shared resources**

The ECB, CCM, and AAR share the same AES module. The ECB will always have lowest priority and if there
is a sharing conflict during encryption, the ECB operation will be aborted and an ERRORECB event will be
generated.

###### **28.2 EasyDMA**

The ECB implements an EasyDMA mechanism for reading and writing to the Data RAM. This DMA cannot
access the program memory or any other parts of the memory area except RAM.

If the ECBDATAPTR is not pointing to the Data RAM region, an EasyDMA transfer may result in a HardFault
or RAM corruption. See _Memory_ on page 24 for more information about the different memory regions.

The EasyDMA will have finished accessing the Data RAM when the ENDECB or ERRORECB is generated.

###### **28.3 ECB data structure**

Input to the block encrypt and output from the block encrypt are stored in the same data structure.
ECBDATAPTR should point to this data structure before STARTECB is initiated.


**Table 56: ECB data structure overview**


**Property** **Address offset** **Description**
KEY 0 16 byte AES key
CLEARTEXT 16 16 byte AES cleartext input block
CIPHERTEXT 32 16 byte AES ciphertext output block


**Page 268**


28 ECB — AES electronic codebook mode
encryption

###### **28.4 Registers**


**Table 57: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x4000E000 ECB ECB AES Electronic Code Book (ECB) mode

block encryption


**Table 58: Register Overview**


**Register** **Offset** **Description**

TASKS_STARTECB 0x000 Start ECB block encrypt

TASKS_STOPECB 0x004 Abort a possible executing ECB operation

EVENTS_ENDECB 0x100 ECB block encrypt complete

EVENTS_ERRORECB 0x104 ECB block encrypt aborted because of a STOPECB task or due to an error

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_ECBDATAPTR_ 0x504 ECB block encrypt memory pointers


**28.4.1 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENDECB Write '1' to Enable interrupt for ENDECB event


See _EVENTS_ENDECB_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ERRORECB Write '1' to Enable interrupt for ERRORECB event


See _EVENTS_ERRORECB_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**28.4.2 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENDECB Write '1' to Disable interrupt for ENDECB event


See _EVENTS_ENDECB_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ERRORECB Write '1' to Disable interrupt for ERRORECB event


See _EVENTS_ERRORECB_

Clear 1 Disable

Disabled 0 Read: Disabled


**Page 269**


28 ECB — AES electronic codebook mode
encryption


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Read: Enabled


**28.4.3 ECBDATAPTR**

Address offset: 0x504

ECB block encrypt memory pointers


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ECBDATAPTR Pointer to the ECB data structure (see Table 1 ECB data

structure overview)

###### **28.5 Electrical specification**


**28.5.1 ECB Electrical Specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

tECB Run time per 16 byte block in all modes 6 µs


**Page 270**


29 CCM — AES CCM mode encryption

#### **29 CCM — AES CCM mode encryption**


Cipher block chaining - message authentication code (CCM) mode is an authenticated encryption algorithm
designed to provide both authentication and confidentiality during data transfer. CCM combines counter
mode encryption and CBC-MAC authentication. The CCM terminology "Message authentication code
(MAC)" is called the "Message integrity check (MIC)" in ' _Bluetooth_ terminology and also in this document.

The CCM block generates an encrypted keystream that is applied to input data using the XOR operation
and generates the 4 byte MIC field in one operation. The CCM and radio can be configured to work
synchronously. The CCM will encrypt in time for transmission and decrypt after receiving bytes into memory
from the Radio. All operations can complete within the packet RX or TX time. CCM on this device is
implemented according to _Bluetooth_ requirements and the algorithm as defined in IETF _[RFC3610](http://www.ietf.org/rfc/rfc3610.txt)_, and
depends on the AES-128 block cipher. A description of the CCM algorithm can also be found in _[NIST Special](http://csrc.nist.gov/publications/PubsSPs.html)_
_[Publication 800-38C](http://csrc.nist.gov/publications/PubsSPs.html)_ . The _Bluetooth_ specification describes the configuration of counter mode blocks and
encryption blocks to implement compliant encryption for BLE.

The CCM block uses EasyDMA to load key, counter mode blocks (including the nonce required), and to
read/write plain text and cipher text.

The AES CCM supports three operations: key-stream generation, packet encryption, and packet decryption.
All these operations are done in compliance with the _Bluetooth_ specification. [23] A new key-stream must be
generated before a new packet encryption or packet decryption operation can be started.

A key-stream is generated by triggering the KSGEN task. An ENDKSGEN event will be generated when the
new key-stream has been generated. The key-stream will be stored in the AES CCM’s temporary memory
area, specified by the SCRATCHPTR, where it will be used in subsequent encryption and decryption
operations.

Encryption is started by triggering the CRYPT task with the MODE register set to ENCRYPTION. Similarly,
decryption is started by triggering the same task with MODE set to DECRYPTION. An ENDCRYPT event
will be generated when packet encryption is completed as well as when packet decryption is completed, see
_Figure 61: Key-stream generation followed by encryption or decryption. The shortcut is optional._ on page
271.


key-stream

generation


encryption / decryption


ENDKSGEN CRYPT ENDCRYPT


SHORTCUT


KSGEN


**Figure 61: Key-stream generation followed by encryption or decryption. The shortcut is optional.**


Key-stream generation, packet encryption, and packet decryption operations utilize the configuration
specified in the data structure pointed to by the CNFPTR pointer. It is necessary to configure this pointer and
its underlying data structure, and the MODE register before the KSGEN task is triggered. It is also necessary
to configure the INPTR pointer and the OUTPTR pointer before the CRYPT task is triggered.

If a shortcut is used between ENDKSGEN event and CRYPT task, the INPTR pointer and the OUTPTR
pointer must be configured before the KSGEN task is triggered.

The AES CCM supports different packet lengths, this is configured via the PACKETLENGTH field in the
MODE register.


23 _Bluetooth_ AES CCM 128 bit block encryption, see _Bluetooth_ Core specification Version 4.0.


**Page 271**


29 CCM — AES CCM mode encryption

###### **29.1 Shared resources**

The CCM shares registers and other resources with other peripherals that have the same ID as the CCM.
The user must therefore disable all peripherals that have the same ID as the CCM before the CCM can be
configured and used.

Disabling a peripheral that have the same ID as the CCM will not reset any of the registers that are shared
with the CCM. It is therefore important to configure all relevant CCM registers explicitly to secure that it
operates correctly.

See the Instantiation table in _Instantiation_ on page 25 for details on peripherals and their IDs.

###### **29.2 Encryption**

During packet encryption, the AES CCM will read the unencrypted packet located in RAM at the address
specified in the INPTR pointer, encrypt the packet and append a four byte long Message Integrity Check
(MIC) field to the packet.

The AES CCM will also modify the length field of the packet to adjust for the appended MIC field, that is,
add four bytes to the length, and store the resulting packet back into RAM at the address specified in the
OUTPTR pointer, see _Figure 62: Encryption_ on page 272.

Empty packets (length field is set to 0) will not be encrypted but instead moved unmodified through the AES
CCM.


INPTR


OUTPTR


Unencrypted packet


H L RFU PL


Encrypted packet


H L+4 RFU EPL


AES CCM


MODE = ENCRYPTION


MIC


H: Header (S0)
L: Length
RFU: reserved for future use (S1)
PL: unencrypted payload
EPL: encrypted payload


SCRATCHPTR


CNFPTR


Scratch area


CCM data

structure


**Figure 62: Encryption**

###### **29.3 Decryption**

During packet decryption, the AES CCM will read the encrypted packet located in RAM at the address
specified in the INPTR pointer, decrypt the packet, authenticate the packet’s MIC field and generate the
appropriate MIC status.

The AES CCM will also modify the length field of the packet to adjust for the MIC field, that is, subtract
four bytes from the length, and then store the decrypted packet into RAM at the address pointed to by the
OUTPTR pointer, see _Figure 63: Decryption_ on page 273.

The CCM is only able to decrypt packets that are at least 5 bytes long, that is, 1 byte or more encrypted
payload (EPL) and 4 bytes of MIC. The CCM will therefore generate a MIC error for packets where the length
field is set to 1, 2, 3 or 4.

Empty packets (length field is set to 0) will not be decrypted but instead moved unmodified through the AES
CCM, these packets will always pass the MIC check.


**Page 272**


29 CCM — AES CCM mode encryption


OUTPTR


INPTR


Unencrypted packet


H L RFU PL


Encrypted packet


H L+4 RFU EPL


AES CCM


MODE = DECRYPTION


MIC


H: Header (S0)
L: Length
RFU: reserved for future use (S1)
PL: unencrypted payload
EPL: encrypted payload


SCRATCHPTR


CNFPTR


Scratch area


CCM data

structure


**Figure 63: Decryption**

###### **29.4 AES CCM and RADIO concurrent operation**

The AES CCM is designed to run in parallel with the RADIO to enable on-the-fly encryption and decryption
of RADIO packets without CPU involvement. To facilitate this, the RADIO has to be configured with specific
settings.


**Table 59: Radio configuration settings**


**Radio parameter** **Value** **Description**
PCNF0.S0LEN 1 Length of HEADER field in: _Table 61: Data structure for unencrypted packet_ on page 275 and _Table_
_62: Data structure for encrypted packet_ on page 275.
PCNF0.LFLEN 5 or 8 Length of LENGTH field in: _Table 61: Data structure for unencrypted packet_ on page 275 and _Table_
_62: Data structure for encrypted packet_ on page 275.
PCNF0.S1LEN 3 or 0 Length of the RFU field in: _Table 61: Data structure for unencrypted packet_ on page 275 and _Table_
_62: Data structure for encrypted packet_ on page 275. The combined length of LENGTH and RFU
must always be 8 bit.
PCNF0.S1 Include Always include the S1 field (RFU field) in RAM to secure that the same data structure can be used
for PCNF0.S1LEN = 3 and PCNF0.S1LEN = 0: _Table 61: Data structure for unencrypted packet_ on page
275 and _Table 62: Data structure for encrypted packet_ on page 275.
MODE Ble_1Mbit Data rate. Must match CCM->MODE.DATARATE
PCNF1.BALEN 3 Length of address (32 bit)
CRCCNF.LEN 3 Length of CRC (24 bit)

###### **29.5 Encrypting packets on-the-fly in radio transmit mode**

When the AES CCM is encrypting a packet on-the-fly at the same time as the RADIO is transmitting it, the
RADIO must read the encrypted packet from the same memory location as the AES CCM is writing to.

The OUTPTR pointer in the AES CCM must therefore point to the same memory location as the
PACKETPTR pointer in the RADIO, see _Figure 64: Configuration of on-the-fly encryption_ on page 273.


INPTR


OUTPTR

&
PACKETPTR


Unencrypted packet


H L RFU PL


Encrypted packet


H L+4 RFU EPL


AES CCM


MODE = ENCRYPTION


MIC


H: Header (S0)
L: Length
RFU: reserved for future use (S1)
PL: unencrypted payload
EPL: encrypted payload


To remote

receiver


SCRATCHPTR


CNFPTR


Scratch area


CCM data

structure


RADIO
TXEN


**Figure 64: Configuration of on-the-fly encryption**


In order to match the RADIO’s timing, the KSGEN task must be triggered no later than when the START task
in the RADIO is triggered, in addition the shortcut between the ENDKSGEN event and the CRYPT task must
be enabled. This use-case is illustrated in _Figure 65: On-the-fly encryption using a PPI connection_ on page
274 using a PPI connection between the READY event in the RADIO and the KSGEN task in the AES
CCM.


**Page 273**


SHORTCUT


ENDKSGEN CRYPT


29 CCM — AES CCM mode encryption


encryption


ENDCRYPT


AES CCM


RADIO


RU P A H L RFU EPL MIC CRC


KSGEN


key-stream

generation


PPI


READY


TXEN END


READY START


RU: Ramp-up of RADIO
P: Preamble
A: Address


EPL: encrypted payload


SHORTCUT


H: Header (S0)
L: Length
RFU: reserved for future use (S1)


**Figure 65: On-the-fly encryption using a PPI connection**

###### **29.6 Decrypting packets on-the-fly in radio receive mode**

When the AES CCM is decrypting a packet on-the-fly at the same time as the RADIO is receiving it, the AES
CCM must read the encrypted packet from the same memory location as the RADIO is writing to.

The INPTR pointer in the AES CCM must therefore point to the same memory location as the PACKETPTR
pointer in the RADIO, see _Figure 66: Configuration of on-the-fly decryption_ on page 274.


OUTPTR


INPTR

&
PACKETPTR


Unencrypted packet


H L RFU PL


Encrypted packet


H L+4 RFU EPL


MODE = DECRYPTION


MIC


RXEN


H: Header (S0)
L: Length
RFU: reserved for future use (S1)
PL: unencrypted payload
EPL: encrypted payload


From remote

transmitter


SCRATCHPTR


CNFPTR


Scratch area


CCM data

structure


AES CCM


RADIO


**Figure 66: Configuration of on-the-fly decryption**


In order to match the RADIO’s timing, the KSGEN task must be triggered no later than when the START task
in the RADIO is triggered. In addition, the CRYPT task must be triggered no earlier than when the ADDRESS
event is generated by the RADIO.

If the CRYPT task is triggered exactly at the same time as the ADDRESS event is generated by the RADIO,
the AES CCM will guarantee that the decryption is completed no later than when the END event in the
RADIO is generated.

This use-case is illustrated in _Figure 67: On-the-fly decryption using a PPI connection between the READY_
_event in the RADIO and the KSGEN task in the AES CCM_ on page 275 using a PPI connection between
the ADDRESS event in the RADIO and the CRYPT task in the AES CCM. The KSGEN task is triggered from
the READY event in the RADIO through a PPI connection.


**Page 274**


29 CCM — AES CCM mode encryption


decryption


AES CCM


RADIO


RU P A H L RFU EPL MIC CRC


key-stream

generation


KSGEN


ENDKSGEN CRYPT ENDCRYPT


PPI


READY


PPI


ADDRESS


RXEN END


READY START


H: Header (S0)
L: Length
RFU: reserved for future use (S1)


RU: Ramp-up of RADIO
P: Preamble
A: Address


SHORTCUT


EPL: encrypted payload
: RADIO receiving noise


**Figure 67: On-the-fly decryption using a PPI connection between the READY event in the RADIO and**
**the KSGEN task in the AES CCM**

###### **29.7 CCM data structure**

The CCM data structure is located in Data RAM at the memory location specified by the CNFPTR pointer
register.


**Table 60: CCM data structure overview**


**Property** **Address offset** **Description**

KEY 0 16 byte AES key

PKTCTR 16 Octet0 (LSO) of packet counter

17 Octet1 of packet counter

18 Octet2 of packet counter

19 Octet3 of packet counter

20 Bit 6 – Bit 0: Octet4 (7 most significant bits of packet counter, with Bit 6 being the most significant

bit) Bit7: Ignored

21 Ignored

22 Ignored

23 Ignored

24 Bit 0: Direction bit Bit 7 – Bit 1: Zero padded

IV 25 8 byte initialization vector (IV) Octet0 (LSO) of IV, Octet1 of IV, …, Octet7 (MSO) of IV


The NONCE vector (as specified by the _Bluetooth_ Core Specification) will be generated by hardware based
on the information specified in the CCM data structure from _Table 60: CCM data structure overview_ on page
275 .


**Table 61: Data structure for unencrypted packet**


**Property** **Address offset** **Description**

HEADER 0 Packet Header

LENGTH 1 Number of bytes in unencrypted payload

RFU 2 Reserved Future Use

PAYLOAD 3 Unencrypted payload


**Table 62: Data structure for encrypted packet**


**Property** **Address offset** **Description**

HEADER 0 Packet Header

LENGTH 1 Number of bytes in encrypted payload including length of MIC


**Important:** LENGTH will be 0 for empty packets since the MIC is not added to empty

packets

RFU 2 Reserved Future Use

PAYLOAD 3 Encrypted payload

MIC 3 + payload length ENCRYPT: 4 bytes encrypted MIC


**Page 275**


29 CCM — AES CCM mode encryption


**Property** **Address offset** **Description**

**Important:** MIC is not added to empty packets

###### **29.8 EasyDMA and ERROR event**

The CCM implements an EasyDMA mechanism for reading and writing to the RAM.

In some scenarios where the CPU and other DMA enabled peripherals are accessing the RAM at the same
time, the CCM DMA could experience some bus conflicts which may also result in an error during encryption.
If this happens, the ERROR event will be generated.

The EasyDMA will have finished accessing the RAM when the ENDKSGEN and ENDCRYPT events are
generated.

If the CNFPTR, SCRATCHPTR, INPTR and the OUTPTR are not pointing to the Data RAM region,
an EasyDMA transfer may result in a HardFault or RAM corruption. See _Memory_ on page 24 for more
information about the different memory regions.

###### **29.9 Registers**


**Table 63: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x4000F000 CCM CCM AES CCM Mode Encryption


**Table 64: Register Overview**


**Register** **Offset** **Description**

TASKS_KSGEN 0x000 Start generation of key-stream. This operation will stop by itself when completed.

TASKS_CRYPT 0x004 Start encryption/decryption. This operation will stop by itself when completed.

TASKS_STOP 0x008 Stop encryption/decryption

EVENTS_ENDKSGEN 0x100 Key-stream generation complete

EVENTS_ENDCRYPT 0x104 Encrypt/decrypt complete

EVENTS_ERROR 0x108 CCM error event

_SHORTS_ 0x200 Shortcut register

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_MICSTATUS_ 0x400 MIC check result

_ENABLE_ 0x500 Enable

_MODE_ 0x504 Operation mode

_CNFPTR_ 0x508 Pointer to data structure holding AES key and NONCE vector

_INPTR_ 0x50C Input pointer

_OUTPTR_ 0x510 Output pointer

_SCRATCHPTR_ 0x514 Pointer to data area used for temporary storage


**29.9.1 SHORTS**

Address offset: 0x200

Shortcut register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENDKSGEN_CRYPT Shortcut between ENDKSGEN event and CRYPT task


See _EVENTS_ENDKSGEN_ and _TASKS_CRYPT_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**Page 276**


29 CCM — AES CCM mode encryption


**29.9.2 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENDKSGEN Write '1' to Enable interrupt for ENDKSGEN event


See _EVENTS_ENDKSGEN_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ENDCRYPT Write '1' to Enable interrupt for ENDCRYPT event


See _EVENTS_ENDCRYPT_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW ERROR Write '1' to Enable interrupt for ERROR event


See _EVENTS_ERROR_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**29.9.3 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENDKSGEN Write '1' to Disable interrupt for ENDKSGEN event


See _EVENTS_ENDKSGEN_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ENDCRYPT Write '1' to Disable interrupt for ENDCRYPT event


See _EVENTS_ENDCRYPT_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW ERROR Write '1' to Disable interrupt for ERROR event


See _EVENTS_ERROR_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**29.9.4 MICSTATUS**

Address offset: 0x400

MIC check result


**Page 277**


29 CCM — AES CCM mode encryption


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R MICSTATUS The result of the MIC check performed during the previous

decryption operation

CheckFailed 0 MIC check failed

CheckPassed 1 MIC check passed


**29.9.5 ENABLE**

Address offset: 0x500

Enable


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENABLE Enable or disable CCM

Disabled 0 Disable

Enabled 2 Enable


**29.9.6 MODE**

Address offset: 0x504

Operation mode


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000001** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MODE The mode of operation to be used

Encryption 0 AES CCM packet encryption mode

Decryption 1 AES CCM packet decryption mode

B RW DATARATE Data rate that the CCM shall run in synch with

1Mbit 0 In synch with 1 Mbit data rate

2Mbit 1 In synch with 2 Mbit data rate

C RW LENGTH Packet length configuration

Default 0 Default length. Effective length of LENGTH field is 5-bit

Extended 1 Extended length. Effective length of LENGTH field is 8-bit


**29.9.7 CNFPTR**

Address offset: 0x508

Pointer to data structure holding AES key and NONCE vector


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CNFPTR Pointer to the data structure holding the AES key and the CCM

NONCE vector (see Table 1 CCM data structure overview)


**29.9.8 INPTR**

Address offset: 0x50C

Input pointer


**Page 278**


29 CCM — AES CCM mode encryption


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW INPTR Input pointer


**29.9.9 OUTPTR**

Address offset: 0x510

Output pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW OUTPTR Output pointer


**29.9.10 SCRATCHPTR**

Address offset: 0x514

Pointer to data area used for temporary storage


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW SCRATCHPTR Pointer to a scratch data area used for temporary storage

during key-stream generation, MIC generation and encryption/

decryption.


The scratch area is used for temporary storage of data during

key-stream generation and encryption.


A space of 43 bytes, or (16 + MAXPACKETSIZE) bytes, whatever

is largest, must be reserved in RAM.


**Page 279**


30 AAR — Accelerated address resolver

#### **30 AAR — Accelerated address resolver**


Accelerated address resolver is a cryptographic support function for implementing the "Resolvable Private
Address Resolution Procedure" described in the _Bluetooth Core specification_ v4.0. "Resolvable private
address generation" should be achieved using ECB and is not supported by AAR.

The procedure allows two devices that share a secret key to generate and resolve a hash based on their
device address. The AAR block enables real-time address resolution on incoming packets when configured
as described in this chapter. This allows real-time packet filtering (whitelisting) using a list of known shared
keys (Identity Resolving Keys (IRK) in _Bluetooth_ ).

###### **30.1 Shared resources**

The AAR shares registers and other resources with the peripherals that have the same ID as the AAR.
The user must therefore disable all peripherals that have the same ID as the AAR before the AAR can be
configured and used.

Disabling a peripheral that have the same ID as the AAR will not reset any of the registers that are shared
with the AAR. It is therefore important to configure all relevant AAR registers explicitly to secure that it
operates correctly.

See the Instantiation table in _Instantiation_ on page 25 for details on peripherals and their IDs.

###### **30.2 EasyDMA**

The AAR implements EasyDMA for reading and writing to the RAM. The EasyDMA will have finished
accessing the RAM when the END, RESOLVED, and NOTRESOLVED events are generated.

If the IRKPTR, ADDRPTR and the SCRATCHPTR is not pointing to the Data RAM region, an EasyDMA
transfer may result in a HardFault or RAM corruption. See _Memory_ on page 24 for more information about
the different memory regions.

###### **30.3 Resolving a resolvable address**

As per _Bluetooth_ specification, a private resolvable address is composed of six bytes.

LSB MSB


1 0


hash
(24-bit)


random


prand
(24-bit)


**Figure 68: Resolvable address**


To resolve an address the ADDRPTR register must point to the start of packet. The resolver is started by
triggering the START task. A RESOLVED event is generated when the AAR manages to resolve the address
using one of the Identity Resolving Keys (IRK) found in the IRK data structure. The AAR will use the IRK
specified in the register IRK0 to IRK15 starting from IRK0. How many to be used is specified by the NIRK
register. The AAR module will generate a NOTRESOLVED event if it is not able to resolve the address using
the specified list of IRKs.

The AAR will go through the list of available IRKs in the IRK data structure and for each IRK try to resolve
the address according to the Resolvable Private Address Resolution Procedure described in the _Bluetooth_
Specification [24] . The time it takes to resolve an address may vary depending on where in the list the


24 _Bluetooth_ Specification Version 4.0 [Vol 3] chapter 10.8.2.3.


**Page 280**


30 AAR — Accelerated address resolver


resolvable address is located. The resolution time will also be affected by RAM accesses performed by other
peripherals and the CPU. See the _Electrical specifications_ for more information about resolution time.

The AAR will only do a comparison of the received address to those programmed in the module. And not
check what type of address it actually is.

The AAR will stop as soon as it has managed to resolve the address, or after trying to resolve the address
using NIRK number of IRKs from the IRK data structure. The AAR will generate an END event after it has
stopped.


SCRATCHPTR


ADDR: resolvable address


ADDRPTR


AAR


Scratch area


IRK data
structure


S0 L S1


START


RESOLVED


ADDR


IRKPTR


**Figure 69: Address resolution with packet preloaded into RAM**

###### **30.4 Use case example for chaining RADIO packet reception with** **address resolution using AAR**

The AAR may be started as soon as the 6 bytes required by the AAR have been received by the RADIO and
stored in RAM. The ADDRPTR pointer must point to the start of packet.


SCRATCHPTR


PACKETPTR

ADDRPTR


START


RESOLVED


S0 L S1 ADDR


RXEN


S0: S0 field of RADIO (optional)
L: Length field of RADIO (optional)
S1: S1 field of RADIO (optional)
ADDR: resolvable address


From remote

transmitter


AAR


RADIO


Scratch area


IRK data
structure


IRKPTR


**Figure 70: Address resolution with packet loaded into RAM by the RADIO**

###### **30.5 IRK data structure**

The IRK data structure is located in RAM at the memory location specified by the CNFPTR pointer register.


**Table 65: IRK data structure overview**


**Property** **Address offset** **Description**
IRK0 0 IRK number 0 (16 - byte)
IRK1 16 IRK number 1 (16 - byte)
.. .. ..
IRK15 240 IRK number 15 (16 - byte)


**Page 281**


30 AAR — Accelerated address resolver

###### **30.6 Registers**


**Table 66: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x4000F000 AAR AAR Acelerated Address Resolver


**Table 67: Register Overview**


**Register** **Offset** **Description**

TASKS_START 0x000 Start resolving addresses based on IRKs specified in the IRK data structure

TASKS_STOP 0x008 Stop resolving addresses

EVENTS_END 0x100 Address resolution procedure complete

EVENTS_RESOLVED 0x104 Address resolved

EVENTS_NOTRESOLVED 0x108 Address not resolved

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_STATUS_ 0x400 Resolution status

_ENABLE_ 0x500 Enable AAR

_NIRK_ 0x504 Number of IRKs

_IRKPTR_ 0x508 Pointer to IRK data structure

_ADDRPTR_ 0x510 Pointer to the resolvable address

_SCRATCHPTR_ 0x514 Pointer to data area used for temporary storage


**30.6.1 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW END Write '1' to Enable interrupt for END event


See _EVENTS_END_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW RESOLVED Write '1' to Enable interrupt for RESOLVED event


See _EVENTS_RESOLVED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW NOTRESOLVED Write '1' to Enable interrupt for NOTRESOLVED event


See _EVENTS_NOTRESOLVED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**30.6.2 INTENCLR**

Address offset: 0x308

Disable interrupt


**Page 282**


30 AAR — Accelerated address resolver


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW END Write '1' to Disable interrupt for END event


See _EVENTS_END_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW RESOLVED Write '1' to Disable interrupt for RESOLVED event


See _EVENTS_RESOLVED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW NOTRESOLVED Write '1' to Disable interrupt for NOTRESOLVED event


See _EVENTS_NOTRESOLVED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**30.6.3 STATUS**

Address offset: 0x400

Resolution status


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R STATUS [0..15] The IRK that was used last time an address was resolved


**30.6.4 ENABLE**

Address offset: 0x500

Enable AAR


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENABLE Enable or disable AAR

Disabled 0 Disable

Enabled 3 Enable


**30.6.5 NIRK**

Address offset: 0x504

Number of IRKs


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000001** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW NIRK [1..16] Number of Identity root keys available in the IRK data structure


**30.6.6 IRKPTR**

Address offset: 0x508


**Page 283**


30 AAR — Accelerated address resolver


Pointer to IRK data structure


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW IRKPTR Pointer to the IRK data structure


**30.6.7 ADDRPTR**

Address offset: 0x510

Pointer to the resolvable address


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ADDRPTR Pointer to the resolvable address (6-bytes)


**30.6.8 SCRATCHPTR**

Address offset: 0x514

Pointer to data area used for temporary storage


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW SCRATCHPTR Pointer to a scratch data area used for temporary storage

during resolution.A space of minimum 3 bytes must be

reserved.

###### **30.7 Electrical specification**


**30.7.1 AAR Electrical Specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

tAAR,8 Time for address resolution of 8 IRKs 48 µs


**Page 284**


31 SPIM — Serial peripheral interface master with
EasyDMA

#### **31 SPIM — Serial peripheral interface master with** **EasyDMA**


The SPI master can communicate with multiple slaves using individual chip select signals for each of the
slave devices attached to a bus.

Listed here are the main features for the SPIM

- Three SPIM instances

- SPI mode 0-3

- EasyDMA direct transfer to/from RAM for both SPI Slave and SPI Master

- Individual selection of IO pin for each SPI signal


SPIM


GPIO


PSEL.MOSI


TXD.PTR


TXD+1 EasyDMA


MOSI


SCK


MISO


Pin


PSEL.SCK
Pin


Pin


RXD-1


PSEL.MISO


EasyDMA


RXD.PTR


RAM


buffer[0]

buffer[1]


buffer[TXD.MAXCNT-1]


buffer[0]

buffer[1]


buffer[RXD.MAXCNT-1]


TXD buffer


RXD buffer


**Figure 71: SPIM — SPI master with EasyDMA**


The SPIM does not implement support for chip select directly. Therefore, the CPU must use available GPIOs
to select the correct slave and control this independently of the SPI master. The SPIM supports SPI modes 0
through 3. The CONFIG register allows setting CPOL and CPHA appropriately.


**Table 68: SPI modes**


**Mode** **Clock polarity** **Clock phase**
**CPOL** **CPHA**
SPI_MODE00 (Active High) 0 (Leading)
SPI_MODE10 (Active High) 1 (Trailing)
SPI_MODE21 (Active Low) 0 (Leading)
SPI_MODE31 (Active Low) 1 (Trailing)

###### **31.1 Shared resources**

The SPI shares registers and other resources with other peripherals that have the same ID as the SPI.
Therefore, the user must disable all peripherals that have the same ID as the SPI before the SPI can be
configured and used.


**Page 285**


31 SPIM — Serial peripheral interface master with
EasyDMA


Disabling a peripheral that has the same ID as the SPI will not reset any of the registers that are shared with
the SPI. It is therefore important to configure all relevant SPI registers explicitly to secure that it operates
correctly.

See the Instantiation table in _Instantiation_ on page 25 for details on peripherals and their IDs.

###### **31.2 EasyDMA**

The SPI master implements EasyDMA for reading and writing of data packets from and to the DATA RAM
without CPU involvement.

The RXD.PTR and TXD.PTR point to the RXD buffer (receive buffer) and TXD buffer (transmit buffer)
respectively, see _Figure 71: SPIM — SPI master with EasyDMA_ on page 285. RXD.MAXCNT and
TXD.MAXCNT specify the maximum number of bytes allocated to the buffers.

The SPI master will automatically stop transmitting after TXD.MAXCNT bytes have been transmitted and
RXD.MAXCNT bytes have been received. If TXD.MAXCNT is larger than RXD.MAXCNT, the superfluous
received bytes will be ignored. If RXD.MAXCNT is larger than TXD.MAXCNT, the remaining transmitted
bytes will contain the value defined in the ORC register.

If the RXD.PTR and the TXD.PTR are not pointing to the Data RAM region, an EasyDMA transfer may result
in a HardFault or RAM corruption. See _Memory_ on page 24 for more information about the different memory
regions.

The .PTR and .MAXCNT registers are double-buffered. They can be updated and prepared for the next
transmission immediately after having received the STARTED event.

The ENDRX/ENDTX event indicate that EasyDMA has finished accessing respectively the RX/TX buffer in
RAM. The END event gets generated when both RX and TX are finished accessing the buffers in RAM.


**31.2.1 EasyDMA list**
EasyDMA supports one list type.

The supported list type is:

- Array list


**EasyDMA array list**
The EasyDMA array list can be represented by the data structure ArrayList_type.

For illustration, see the code example below. This data structure includes only a buffer with size equal
to Channel.MAXCNT. EasyDMA will use the Channel.MAXCNT register to determine when the buffer
is full. Replace 'Channel' by the specific data channel you want to use, for instance 'NRF_SPIM->RXD',
'NRF_SPIM->TXD', 'NRF_TWIM->RXD', etc.

The Channel.MAXCNT register cannot be specified larger than the actual size of the buffer. If
Channel.MAXCNT is specified larger than the size of the buffer, the EasyDMA channel may overflow the
buffer.

This array list does not provide a mechanism to explicitly specify where the next item in the list is located.
Instead, it assumes that the list is organized as a linear array where items are located one after the other in
RAM.

```
 #define BUFFER_SIZE 4
 typedef struct ArrayList
 {
 uint8_t buffer[BUFFER_SIZE];
 } ArrayList_type;
 ArrayList_type MyArrayList[3];

```

**Page 286**


31 SPIM — Serial peripheral interface master with
EasyDMA

```
//replace 'Channel' below by the specific data channel you want to use,
//     for instance 'NRF_SPIM->RXD', 'NRF_TWIM->RXD', etc.
Channel.MAXCNT = BUFFER_SIZE;
Channel.PTR = &MyArrayList;

```

Channel.PTR = &MyArrayList

Note: addresses are
assuming that
sizeof(buffer[n]) is one byte


buffer[2]

buffer[2]

buffer[2]


buffer[3]

buffer[3]

buffer[3]


0x20000000 : MyArrayList[0]

0x20000004 : MyArrayList[1]

0x20000008 : MyArrayList[2]


**Figure 72: EasyDMA array list**


buffer[0] buffer[1]

buffer[0] buffer[1]

buffer[0] buffer[1]


###### **31.3 SPI master transaction sequence**

An SPI master transaction consists of a sequence started by the START task followed by a number of
events, and finally the STOP task.

An SPI master transaction is started by triggering the START task. The ENDTX event will be generated
when the transmitter has transmitted all bytes in the TXD buffer as specified in the TXD.MAXCNT register.
The ENDRX event will be generated when the receiver has filled the RXD buffer, i.e. received the last
possible byte as specified in the RXD.MAXCNT register.

Following a START task, the SPI master will generate an END event when both ENDRX and ENDTX have
been generated.

The SPI master is stopped by triggering the STOP task. A STOPPED event is generated when the SPI
master has stopped.

If the ENDRX event has not already been generated when the SPI master has come to a stop, the SPI
master will generate the ENDRX event explicitly even though the RX buffer is not full.

If the ENDTX event has not already been generated when the SPI master has come to a stop, the SPI
master will generate the ENDTX event explicitly even though all bytes in the TXD buffer, as specified in the
TXD.MAXCNT register, have not been transmitted.

The SPI master is a synchronous interface, and for every byte that is sent, a different byte will be received at
the same time; this is illustrated in _Figure 73: SPI master transaction_ on page 288.


**Page 287**


CSN


SCK


MO ~~SI~~


31 SPIM — Serial peripheral interface master with
EasyDMA


0 1 2 n ORC ORC


MIS ~~O~~ A B C m-2 m-1 m


ENDTX


CPU 1


START


**Figure 73: SPI master transaction**

###### **31.4 Low power**


ENDRX



When putting the system in low power and the peripheral is not needed, lowest possible power consumption
is achieved by stopping, and then disabling the peripheral.

The STOP task may not be always needed (the peripheral might already be stopped), but if it is sent,
software shall wait until the STOPPED event was received as a response before disabling the peripheral
through the ENABLE register.

###### **31.5 Master mode pin configuration**

The SCK, MOSI, and MISO signals associated with the SPI master are mapped to physical pins according to
the configuration specified in the PSEL.SCK, PSEL.MOSI, and PSEL.MISO registers respectively.

The PSEL.SCK, PSEL.MOSI, and PSEL.MISO registers and their configurations are only used as long as
the SPI master is enabled, and retained only as long as the device is in ON mode. PSEL.SCK, PSEL.MOSI
and PSEL.MISO must only be configured when the SPI master is disabled.

To secure correct behavior in the SPI, the pins used by the SPI must be configured in the GPIO peripheral
as described in _Table 69: GPIO configuration_ on page 288 prior to enabling the SPI. This configuration
must be retained in the GPIO for the selected IOs as long as the SPI is enabled.

Only one peripheral can be assigned to drive a particular GPIO pin at a time. Failing to do so may result in
unpredictable behavior.


**Table 69: GPIO configuration**


**SPI master signal** **SPI master pin** **Direction** **Output value** **Comments**
SCK As specified in PSEL.SCK Output Same as CONFIG.CPOL
MOSI As specified in PSEL.MOSI Output 0
MISO As specified in PSEL.MISO Input Not applicable


**Page 288**


31 SPIM — Serial peripheral interface master with
EasyDMA

###### **31.6 Registers**


**Table 70: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40003000 SPIM SPIM0 SPI master 0

0x40004000 SPIM SPIM1 SPI master 1

0x40023000 SPIM SPIM2 SPI master 2


**Table 71: Register Overview**


**Register** **Offset** **Description**

TASKS_START 0x010 Start SPI transaction

TASKS_STOP 0x014 Stop SPI transaction

TASKS_SUSPEND 0x01C Suspend SPI transaction

TASKS_RESUME 0x020 Resume SPI transaction

EVENTS_STOPPED 0x104 SPI transaction has stopped

EVENTS_ENDRX 0x110 End of RXD buffer reached

EVENTS_END 0x118 End of RXD buffer and TXD buffer reached

EVENTS_ENDTX 0x120 End of TXD buffer reached

EVENTS_STARTED 0x14C Transaction started

_SHORTS_ 0x200 Shortcut register

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_ENABLE_ 0x500 Enable SPIM

_PSEL.SCK_ 0x508 Pin select for SCK

_PSEL.MOSI_ 0x50C Pin select for MOSI signal

_PSEL.MISO_ 0x510 Pin select for MISO signal

_FREQUENCY_ 0x524 SPI frequency. Accuracy depends on the HFCLK source selected.

_RXD.PTR_ 0x534 Data pointer

_RXD.MAXCNT_ 0x538 Maximum number of bytes in receive buffer

_RXD.AMOUNT_ 0x53C Number of bytes transferred in the last transaction

_RXD.LIST_ 0x540 EasyDMA list type

_TXD.PTR_ 0x544 Data pointer

_TXD.MAXCNT_ 0x548 Maximum number of bytes in transmit buffer

_TXD.AMOUNT_ 0x54C Number of bytes transferred in the last transaction

_TXD.LIST_ 0x550 EasyDMA list type

_CONFIG_ 0x554 Configuration register

_ORC_ 0x5C0 Over-read character. Character clocked out in case and over-read of the TXD buffer.


**31.6.1 SHORTS**

Address offset: 0x200

Shortcut register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW END_START Shortcut between END event and START task


See _EVENTS_END_ and _TASKS_START_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**31.6.2 INTENSET**

Address offset: 0x304

Enable interrupt


**Page 289**


31 SPIM — Serial peripheral interface master with
EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STOPPED Write '1' to Enable interrupt for STOPPED event


See _EVENTS_STOPPED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ENDRX Write '1' to Enable interrupt for ENDRX event


See _EVENTS_ENDRX_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW END Write '1' to Enable interrupt for END event


See _EVENTS_END_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW ENDTX Write '1' to Enable interrupt for ENDTX event


See _EVENTS_ENDTX_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW STARTED Write '1' to Enable interrupt for STARTED event


See _EVENTS_STARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**31.6.3 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STOPPED Write '1' to Disable interrupt for STOPPED event


See _EVENTS_STOPPED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ENDRX Write '1' to Disable interrupt for ENDRX event


See _EVENTS_ENDRX_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW END Write '1' to Disable interrupt for END event


See _EVENTS_END_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW ENDTX Write '1' to Disable interrupt for ENDTX event


See _EVENTS_ENDTX_


**Page 290**


31 SPIM — Serial peripheral interface master with
EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW STARTED Write '1' to Disable interrupt for STARTED event


See _EVENTS_STARTED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**31.6.4 ENABLE**

Address offset: 0x500

Enable SPIM


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENABLE Enable or disable SPIM

Disabled 0 Disable SPIM

Enabled 7 Enable SPIM


**31.6.5 PSEL.SCK**

Address offset: 0x508

Pin select for SCK


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

C RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**31.6.6 PSEL.MOSI**

Address offset: 0x50C

Pin select for MOSI signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

C RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**31.6.7 PSEL.MISO**

Address offset: 0x510

Pin select for MISO signal


**Page 291**


31 SPIM — Serial peripheral interface master with
EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

C RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**31.6.8 FREQUENCY**

Address offset: 0x524

SPI frequency. Accuracy depends on the HFCLK source selected.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x04000000** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW FREQUENCY SPI master data rate

K125 0x02000000 125 kbps

K250 0x04000000 250 kbps

K500 0x08000000 500 kbps

M1 0x10000000 1 Mbps

M2 0x20000000 2 Mbps

M4 0x40000000 4 Mbps

M8 0x80000000 8 Mbps


**31.6.9 RXD.PTR**

Address offset: 0x534

Data pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR Data pointer


**31.6.10 RXD.MAXCNT**

Address offset: 0x538

Maximum number of bytes in receive buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT Maximum number of bytes in receive buffer


**31.6.11 RXD.AMOUNT**

Address offset: 0x53C

Number of bytes transferred in the last transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes transferred in the last transaction


**Page 292**


31 SPIM — Serial peripheral interface master with
EasyDMA


**31.6.12 RXD.LIST**

Address offset: 0x540

EasyDMA list type


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LIST List type

Disabled 0 Disable EasyDMA list

ArrayList 1 Use array list


**31.6.13 TXD.PTR**

Address offset: 0x544

Data pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR Data pointer


**31.6.14 TXD.MAXCNT**

Address offset: 0x548

Maximum number of bytes in transmit buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT Maximum number of bytes in transmit buffer


**31.6.15 TXD.AMOUNT**

Address offset: 0x54C

Number of bytes transferred in the last transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes transferred in the last transaction


**31.6.16 TXD.LIST**

Address offset: 0x550

EasyDMA list type


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LIST List type

Disabled 0 Disable EasyDMA list

ArrayList 1 Use array list


**Page 293**


31 SPIM — Serial peripheral interface master with
EasyDMA


**31.6.17 CONFIG**

Address offset: 0x554

Configuration register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ORDER Bit order

MsbFirst 0 Most significant bit shifted out first

LsbFirst 1 Least significant bit shifted out first

B RW CPHA Serial clock (SCK) phase

Leading 0 Sample on leading edge of clock, shift serial data on trailing

edge

Trailing 1 Sample on trailing edge of clock, shift serial data on leading

edge

C RW CPOL Serial clock (SCK) polarity

ActiveHigh 0 Active high

ActiveLow 1 Active low


**31.6.18 ORC**

Address offset: 0x5C0

Over-read character. Character clocked out in case and over-read of the TXD buffer.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ORC Over-read character. Character clocked out in case and over
read of the TXD buffer.

###### **31.7 Electrical specification**


**31.7.1 SPIM master interface electrical specifications**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fSPIM Bit rates for SPIM [25] 8 [26] Mbps

ISPIM,2Mbps Run current for SPIM, 2 Mbps 50 µA

ISPIM,8Mbps Run current for SPIM, 8 Mbps 50 µA

ISPIM,IDLE Idle current for SPIM (STARTed, no CSN activity) 1 µA

tSPIM,START Time from START task to transmission started .. .. .. µs


**31.7.2 Serial Peripheral Interface Master (SPIM) timing specifications**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

tSPIM,CSCK SCK period .. .. .. ns

tSPIM,RSCK,LD SCK rise time, standard drive [a] tRF,25pF

tSPIM,RSCK,HD SCK rise time, high drive [a] tHRF,25pF

tSPIM,FSCK,LD SCK fall time, standard drive [a] tRF,25pF

tSPIM,FSCK,HD SCK fall time, high drive [a] tHRF,25pF

tSPIM,WHSCK SCK high time [a] (0.5*tCSCK)

- tRSCK


25 High bit rates may require GPIOs to be set as High Drive, see GPIO chapter for more details.
26 The actual maximum data rate depends on the slave's CLK to MISO and MOSI setup and hold timings.
a At 25pF load, including GPIO pin capacitance, see GPIO spec.


**Page 294**


31 SPIM — Serial peripheral interface master with
EasyDMA


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

tSPIM,WLSCK SCK low time [a] (0.5*tCSCK)

- tFSCK

tSPIM,SUMI MISO to CLK edge setup time 19 ns

tSPIM,HMI CLK edge to MISO hold time 18 ns

tSPIM,VMO CLK edge to MOSI valid 59 ns

tSPIM,HMO MOSI hold time after CLK edge 20 ns


tCSCK


CPOL=0
CPHA=0


CPOL=1
CPHA=0


CPOL=0
CPHA=1


CPOL=1
CPHA=1


MISO (in)


tWHSCK
tWLSCK


tSUMI tHMI


tRSCK
tFSCK


MSb LSb


tVMO


tHMO


MOSI (out) MSb LSb


**Figure 74: SPIM timing diagram**


**Page 295**


32 SPIS — Serial peripheral interface slave with
EasyDMA

#### **32 SPIS — Serial peripheral interface slave with** **EasyDMA**


SPI slave (SPIS) is implemented with EasyDMA support for ultra low power serial communication from an
external SPI master. EasyDMA in conjunction with hardware-based semaphore mechanisms removes all
real-time requirements associated with controlling the SPI slave from a low priority CPU execution context.


PSEL.CSN PSEL.MISO PSEL.MOSI PSEL.SCK


SPIS


MISO MOSI


SPI slave tranceiver


ACQUIRE


RELEASE


ACQUIRED


END


OVERREAD


OVERFLOW


CSN


Semaphore


DEF


TXD.PTR EasyDMA EasyDMA RXD.PTR


EasyDMA


EasyDMA


RAM


TXD


TXD+1


TXD+2


TXD+n


RXD


RXD+1


RXD+2


RXD+n


**Figure 75: SPI slave**


The SPIS supports SPI modes 0 through 3. The CONFIG register allows setting CPOL and CPHA
appropriately.


**Table 72: SPI modes**


**Mode** **Clock polarity** **Clock phase**
**CPOL** **CPHA**
SPI_MODE0 0 (Leading) 0 (Active High)
SPI_MODE1 0 (Leading) 1 (Active Low)
SPI_MODE2 1 (Trailing) 0 (Active High)
SPI_MODE3 1 (Trailing) 1 (Active Low)

###### **32.1 Shared resources**

The SPI slave shares registers and other resources with other peripherals that have the same ID as the SPI
slave. Therefore, you must disable all peripherals that have the same ID as the SPI slave before the SPI
slave can be configured and used.

Disabling a peripheral that has the same ID as the SPI slave will not reset any of the registers that are
shared with the SPI slave. It is important to configure all relevant SPI slave registers explicitly to secure that
it operates correctly.

The Instantiation table in _Instantiation_ on page 25 shows which peripherals have the same ID as the SPI
slave.

###### **32.2 EasyDMA**

The SPI slave implements EasyDMA for reading and writing to and from the RAM. The END event indicates
that EasyDMA has finished accessing the buffer in RAM.


**Page 296**


32 SPIS — Serial peripheral interface slave with
EasyDMA


If the TXD.PTR and the RXD.PTR are not pointing to the Data RAM region, an EasyDMA transfer may result
in a HardFault or RAM corruption. See _Memory_ on page 24 for more information about the different memory
regions.

###### **32.3 SPI slave operation**

SPI slave uses two memory pointers, RXD.PTR and TXD.PTR, that point to the RXD buffer (receive
buffer) and TXD buffer (transmit buffer) respectively. Since these buffers are located in RAM, which can be
accessed by both the SPI slave and the CPU, a hardware based semaphore mechanism is implemented to
enable safe sharing.

See _Figure 76: SPI transaction when shortcut between END and ACQUIRE is enabled_ on page 298.

Before the CPU can safely update the RXD.PTR and TXD.PTR pointers it must first acquire the SPI
semaphore. The CPU can acquire the semaphore by triggering the ACQUIRE task and then receiving
the ACQUIRED event. When the CPU has updated the RXD.PTR and TXD.PTR pointers the CPU must
release the semaphore before the SPI slave will be able to acquire it. The CPU releases the semaphore by
triggering the RELEASE task. This is illustrated in _Figure 76: SPI transaction when shortcut between END_
_and ACQUIRE is enabled_ on page 298. Triggering the RELEASE task when the semaphore is not granted
to the CPU will have no effect.

The semaphore mechanism does not, at any time, prevent the CPU from performing read or write access
to the RXD.PTR register, the TXD.PTR registers, or the RAM that these pointers are pointing to. The
semaphore is only telling when these can be updated by the CPU so that safe sharing is achieved.

The semaphore is by default assigned to the CPU after the SPI slave is enabled. No ACQUIRED event will
be generated for this initial semaphore handover. An ACQUIRED event will be generated immediately if the
ACQUIRE task is triggered while the semaphore is assigned to the CPU.

The SPI slave will try to acquire the semaphore when CSN goes low. If the SPI slave does not manage to
acquire the semaphore at this point, the transaction will be ignored. This means that all incoming data on
MOSI will be discarded, and the DEF (default) character will be clocked out on the MISO line throughout
the whole transaction. This will also be the case even if the semaphore is released by the CPU during the
transaction. In case of a race condition where the CPU and the SPI slave try to acquire the semaphore at
the same time, as illustrated in lifeline item 2 in _Figure 76: SPI transaction when shortcut between END and_
_ACQUIRE is enabled_ on page 298, the semaphore will be granted to the CPU.

If the SPI slave acquires the semaphore, the transaction will be granted. The incoming data on MOSI will be
stored in the RXD buffer and the data in the TXD buffer will be clocked out on MISO.

When a granted transaction is completed and CSN goes high, the SPI slave will automatically release the
semaphore and generate the END event.

As long as the semaphore is available the SPI slave can be granted multiple transactions one after the
other. If the CPU is not able to reconfigure the TXD.PTR and RXD.PTR between granted transactions, the
same TX data will be clocked out and the RX buffers will be overwritten. To prevent this from happening,
the END_ACQUIRE shortcut can be used. With this shortcut enabled the semaphore will be handed over to
the CPU automatically after the granted transaction has completed, giving the CPU the ability to update the
TXPTR and RXPTR between every granted transaction.

If the CPU tries to acquire the semaphore while it is assigned to the SPI slave, an immediate handover
will not be granted. However, the semaphore will be handed over to the CPU as soon as the SPI slave
has released the semaphore after the granted transaction is completed. If the END_ACQUIRE shortcut is
enabled and the CPU has triggered the ACQUIRE task during a granted transaction, only one ACQUIRE
request will be served following the END event.

The MAXRX register specifies the maximum number of bytes the SPI slave can receive in one granted
transaction. If the SPI slave receives more than MAXRX number of bytes, an OVERFLOW will be indicated
in the STATUS register and the incoming bytes will be discarded.

The MAXTX parameter specifies the maximum number of bytes the SPI slave can transmit in one granted
transaction. If the SPI slave is forced to transmit more than MAXTX number of bytes, an OVERREAD will be
indicated in the STATUS register and the ORC character will be clocked out.


**Page 297**


32 SPIS — Serial peripheral interface slave with
EasyDMA


The RXD.AMOUNT and TXD.AMOUNT registers are updated when a granted transaction is completed.
The TXD.AMOUNT register indicates how many bytes were read from the TX buffer in the last transaction,
that is, ORC (over-read) characters are not included in this number. Similarly, the RXD.AMOUNT register
indicates how many bytes were written into the RX buffer in the last transaction.

The ENDRX event is generated when the RX buffer has been filled.


SPI master can use the DEF
character to stop the transaction as
soon as possible if the transaction is
not granted.


Ignored Ignored Granted


~~0~~


~~DEF~~


DEF ~~DEF~~ ~~DEF~~ A B C


0 ~~1~~ ~~2~~ 0 1 2


~~DEF~~


~~1~~


~~2~~


~~DEF~~


CPU Free CPU Free SPIS CPUPENDING CPU


CPU


Free


SPIS


1 2 3 4




**Figure 76: SPI transaction when shortcut between END and ACQUIRE is enabled**

###### **32.4 Pin configuration**

The CSN, SCK, MOSI, and MISO signals associated with the SPI slave are mapped to physical pins
according to the configuration specified in the PSEL.CSN, PSEL.SCK, PSEL.MOSI, and PSEL.MISO
registers respectively. If the CONNECT field of any of these registers is set to Disconnected, the associated
SPI slave signal will not be connected to any physical pins.

The PSEL.CSN, PSEL.SCK, PSEL.MOSI, and PSEL.MISO registers and their configurations are only used
as long as the SPI slave is enabled, and retained only as long as the device is in System ON mode, see
_POWER — Power supply_ on page 81 chapter for more information about power modes. When the peripheral
is disabled, the pins will behave as regular GPIOs, and use the configuration in their respective OUT bit field
and PIN_CNF[n] register. PSEL.CSN, PSEL.SCK, PSEL.MOSI, and PSEL.MISO must only be configured
when the SPI slave is disabled.

To secure correct behavior in the SPI slave, the pins used by the SPI slave must be configured in the GPIO
peripheral as described in _Table 73: GPIO configuration before enabling peripheral_ on page 299 before
enabling the SPI slave. This is to secure that the pins used by the SPI slave are driven correctly if the SPI


**Page 298**


32 SPIS — Serial peripheral interface slave with
EasyDMA


slave itself is temporarily disabled, or if the device temporarily enters System OFF. This configuration must
be retained in the GPIO for the selected I/Os as long as the SPI slave is to be recognized by an external SPI
master.

The MISO line is set in high impedance as long as the SPI slave is not selected with CSN.

Only one peripheral can be assigned to drive a particular GPIO pin at a time. Failing to do so may result in
unpredictable behavior.


**Table 73: GPIO configuration before enabling peripheral**


**SPI signal** **SPI pin** **Direction** **Output value** **Comment**
CSN As specified in PSEL.CSN Input Not applicable
SCK As specified in PSEL.SCK Input Not applicable
MOSI As specified in PSEL.MOSI Input Not applicable
MISO As specified in PSEL.MISO Input Not applicable Emulates that the SPI slave is not selected.

###### **32.5 Registers**


**Table 74: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40003000 SPIS SPIS0 SPI slave 0

0x40004000 SPIS SPIS1 SPI slave 1

0x40023000 SPIS SPIS2 SPI slave 2


**Table 75: Register Overview**


**Register** **Offset** **Description**

TASKS_ACQUIRE 0x024 Acquire SPI semaphore

TASKS_RELEASE 0x028 Release SPI semaphore, enabling the SPI slave to acquire it

EVENTS_END 0x104 Granted transaction completed

EVENTS_ENDRX 0x110 End of RXD buffer reached

EVENTS_ACQUIRED 0x128 Semaphore acquired

_SHORTS_ 0x200 Shortcut register

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_SEMSTAT_ 0x400 Semaphore status register

_STATUS_ 0x440 Status from last transaction

_ENABLE_ 0x500 Enable SPI slave

_PSELSCK_ 0x508 Pin select for SCK Deprecated

_PSELMISO_ 0x50C Pin select for MISO Deprecated

_PSELMOSI_ 0x510 Pin select for MOSI Deprecated

_PSELCSN_ 0x514 Pin select for CSN Deprecated

_PSEL.SCK_ 0x508 Pin select for SCK

_PSEL.MISO_ 0x50C Pin select for MISO signal

_PSEL.MOSI_ 0x510 Pin select for MOSI signal

_PSEL.CSN_ 0x514 Pin select for CSN signal

_RXDPTR_ 0x534 RXD data pointer Deprecated

_MAXRX_ 0x538 Maximum number of bytes in receive buffer Deprecated

_AMOUNTRX_ 0x53C Number of bytes received in last granted transaction Deprecated

_RXD.PTR_ 0x534 RXD data pointer

_RXD.MAXCNT_ 0x538 Maximum number of bytes in receive buffer

_RXD.AMOUNT_ 0x53C Number of bytes received in last granted transaction

_TXDPTR_ 0x544 TXD data pointer Deprecated

_MAXTX_ 0x548 Maximum number of bytes in transmit buffer Deprecated

_AMOUNTTX_ 0x54C Number of bytes transmitted in last granted transaction Deprecated

_TXD.PTR_ 0x544 TXD data pointer

_TXD.MAXCNT_ 0x548 Maximum number of bytes in transmit buffer

_TXD.AMOUNT_ 0x54C Number of bytes transmitted in last granted transaction

_CONFIG_ 0x554 Configuration register


**Page 299**


32 SPIS — Serial peripheral interface slave with
EasyDMA


**Register** **Offset** **Description**

_DEF_ 0x55C Default character. Character clocked out in case of an ignored transaction.

_ORC_ 0x5C0 Over-read character


**32.5.1 SHORTS**

Address offset: 0x200

Shortcut register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW END_ACQUIRE Shortcut between END event and ACQUIRE task


See _EVENTS_END_ and _TASKS_ACQUIRE_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**32.5.2 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW END Write '1' to Enable interrupt for END event


See _EVENTS_END_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ENDRX Write '1' to Enable interrupt for ENDRX event


See _EVENTS_ENDRX_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW ACQUIRED Write '1' to Enable interrupt for ACQUIRED event


See _EVENTS_ACQUIRED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**32.5.3 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW END Write '1' to Disable interrupt for END event


See _EVENTS_END_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ENDRX Write '1' to Disable interrupt for ENDRX event


**Page 300**


32 SPIS — Serial peripheral interface slave with
EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

See _EVENTS_ENDRX_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW ACQUIRED Write '1' to Disable interrupt for ACQUIRED event


See _EVENTS_ACQUIRED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**32.5.4 SEMSTAT**

Address offset: 0x400

Semaphore status register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A

**Reset 0x00000001** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R SEMSTAT Semaphore status

Free 0 Semaphore is free

CPU 1 Semaphore is assigned to CPU

SPIS 2 Semaphore is assigned to SPI slave

CPUPending 3 Semaphore is assigned to SPI but a handover to the CPU is

pending


**32.5.5 STATUS**

Address offset: 0x440

Status from last transaction

Individual bits are cleared by writing a '1' to the bits that shall be cleared


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW OVERREAD TX buffer over-read detected, and prevented

NotPresent 0 Read: error not present

Present 1 Read: error present

Clear 1 Write: clear error on writing '1'

B RW OVERFLOW RX buffer overflow detected, and prevented

NotPresent 0 Read: error not present

Present 1 Read: error present

Clear 1 Write: clear error on writing '1'


**32.5.6 ENABLE**

Address offset: 0x500

Enable SPI slave


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENABLE Enable or disable SPI slave


**Page 301**


32 SPIS — Serial peripheral interface slave with
EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Disable SPI slave

Enabled 2 Enable SPI slave


**32.5.7 PSELSCK ( Deprecated )**

Address offset: 0x508

Pin select for SCK


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELSCK [0..31] Pin number configuration for SPI SCK signal

Disconnected 0xFFFFFFFF Disconnect


**32.5.8 PSELMISO ( Deprecated )**

Address offset: 0x50C

Pin select for MISO


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELMISO [0..31] Pin number configuration for SPI MISO signal

Disconnected 0xFFFFFFFF Disconnect


**32.5.9 PSELMOSI ( Deprecated )**

Address offset: 0x510

Pin select for MOSI


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELMOSI [0..31] Pin number configuration for SPI MOSI signal

Disconnected 0xFFFFFFFF Disconnect


**32.5.10 PSELCSN ( Deprecated )**

Address offset: 0x514

Pin select for CSN


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELCSN [0..31] Pin number configuration for SPI CSN signal

Disconnected 0xFFFFFFFF Disconnect


**32.5.11 PSEL.SCK**

Address offset: 0x508

Pin select for SCK


**Page 302**


32 SPIS — Serial peripheral interface slave with
EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**32.5.12 PSEL.MISO**

Address offset: 0x50C

Pin select for MISO signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**32.5.13 PSEL.MOSI**

Address offset: 0x510

Pin select for MOSI signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**32.5.14 PSEL.CSN**

Address offset: 0x514

Pin select for CSN signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**32.5.15 RXDPTR ( Deprecated )**

Address offset: 0x534

RXD data pointer


**Page 303**


32 SPIS — Serial peripheral interface slave with
EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW RXDPTR RXD data pointer


**32.5.16 MAXRX ( Deprecated )**

Address offset: 0x538

Maximum number of bytes in receive buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXRX Maximum number of bytes in receive buffer


**32.5.17 AMOUNTRX ( Deprecated )**

Address offset: 0x53C

Number of bytes received in last granted transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNTRX Number of bytes received in the last granted transaction


**32.5.18 RXD.PTR**

Address offset: 0x534

RXD data pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR RXD data pointer


**32.5.19 RXD.MAXCNT**

Address offset: 0x538

Maximum number of bytes in receive buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT Maximum number of bytes in receive buffer


**32.5.20 RXD.AMOUNT**

Address offset: 0x53C

Number of bytes received in last granted transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes received in the last granted transaction


**Page 304**


32 SPIS — Serial peripheral interface slave with
EasyDMA


**32.5.21 TXDPTR ( Deprecated )**

Address offset: 0x544

TXD data pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW TXDPTR TXD data pointer


**32.5.22 MAXTX ( Deprecated )**

Address offset: 0x548

Maximum number of bytes in transmit buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXTX Maximum number of bytes in transmit buffer


**32.5.23 AMOUNTTX ( Deprecated )**

Address offset: 0x54C

Number of bytes transmitted in last granted transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNTTX Number of bytes transmitted in last granted transaction


**32.5.24 TXD.PTR**

Address offset: 0x544

TXD data pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR TXD data pointer


**32.5.25 TXD.MAXCNT**

Address offset: 0x548

Maximum number of bytes in transmit buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT Maximum number of bytes in transmit buffer


**32.5.26 TXD.AMOUNT**

Address offset: 0x54C

Number of bytes transmitted in last granted transaction


**Page 305**


32 SPIS — Serial peripheral interface slave with
EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes transmitted in last granted transaction


**32.5.27 CONFIG**

Address offset: 0x554

Configuration register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ORDER Bit order

MsbFirst 0 Most significant bit shifted out first

LsbFirst 1 Least significant bit shifted out first

B RW CPHA Serial clock (SCK) phase

Leading 0 Sample on leading edge of clock, shift serial data on trailing

edge

Trailing 1 Sample on trailing edge of clock, shift serial data on leading

edge

C RW CPOL Serial clock (SCK) polarity

ActiveHigh 0 Active high

ActiveLow 1 Active low


**32.5.28 DEF**

Address offset: 0x55C

Default character. Character clocked out in case of an ignored transaction.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DEF Default character. Character clocked out in case of an ignored

transaction.


**32.5.29 ORC**

Address offset: 0x5C0

Over-read character


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ORC Over-read character. Character clocked out after an over-read

of the transmit buffer.


**Page 306**


32 SPIS — Serial peripheral interface slave with
EasyDMA

###### **32.6 Electrical specification**


**32.6.1 SPIS slave interface electrical specifications**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fSPIS Bit rates for SPIS [27] 8 [28] Mbps

ISPIS,2Mbps Run current for SPIS, 2 Mbps 45 µA

ISPIS,8Mbps Run current for SPIS, 8 Mbps 45 µA

ISPIS,IDLE Idle current for SPIS (STARTed, no CSN activity) 1 µA


tSPIS,LP,START Time from RELEASE task to ready to receive/transmit (CSN

active), Low power mode


tSPIS,CL,START Time from RELEASE task to receive/transmit (CSN active),

Constant latency mode


tSPIS,CL,START

+

tSTART_HFINT


µs


0.125 µs


**32.6.2 Serial Peripheral Interface Slave (SPIS) timing specifications**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

tSPIS,CSCKIN,8Mbps SCK input period at 8Mbps 125 ns

tSPIS,CSCKIN,4Mbps SCK input period at 4Mbps 250 ns

tSPIS,CSCKIN,2Mbps SCK input period at 2Mbps 500 ns

tSPIS,RFSCKIN SCK input rise/fall time 30 ns

tSPIS,WHSCKIN SCK input high time 30 ns

tSPIS,WLSCKIN SCK input low time 30 ns


tSPIS,SUCSN,LP CSN to CLK setup time, Low power mode tSPIS,SUCSN,CL

+

tSTART_HFINT


ns


tSPIS,SUCSN,CL CSN to CLK setup time, Constant latency mode 1000 ns

tSPIS,HCSN CLK to CSN hold time 2000 ns

tSPIS,ASO CSN to MISO driven [a] 1000 ns

tSPIS,DISSO CSN to MISO disabled [a] 68 ns

tSPIS,CWH CSN inactive time 300 ns

tSPIS,VSO CLK edge to MISO valid 59 ns

tSPIS,HSO MISO hold time after CLK edge 20 [29] ns

tSPIS,SUSI MOSI to CLK edge setup time 19 ns

tSPIS,HSI CLK edge to MOSI hold time 18 ns


CSN (in)


tSUCSN tCSCKIN tHCSN


tCWH


CPOL=0
CPHA=0


CPOL=1
CPHA=0


MISO (out)


tHSO


tRSCKIN
tFSCKIN


tASO


tWHSCKIN
tWLSCKIN


tVSO


tDISSO


tSUSI


MSb LSb


tHSI


MOSI (in) MSb LSb


**Figure 77: SPIS timing diagram**


27 Higher bit rates may require GPIOs to be set as High Drive, see GPIO chapter for more details.
28 The actual maximum data rate depends on the master's CLK to MISO and MOSI setup and hold timings.
a At 25pF load, including GPIO capacitance, see GPIO spec.
29 This is to ensure compatibility to SPI masters sampling MISO on the same edge as MOSI is output


**Page 307**


CSN (in)


32 SPIS — Serial peripheral interface slave with
EasyDMA


Master
Slave


tSUCSN tCSCK tHCSN


tCSCK


CPOL=0
CPHA=0 tWHSCK tRSCK
CPOL=1 tWLSCK tFSCK
CPHA=0


CPOL=0
CPHA=1


CPOL=1
CPHA=1


MISO (in)

MISO (out)


tSUMI tHMI


tASO


tVSO


tHSO


tDISSO


MSb LSb


tHMO


tSUSI


tVMO

tHSI


MOSI (out)

MSb LSb
MOSI (in)


**Figure 78: Common SPIM and SPIS timing diagram**


**Page 308**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA

#### **33 TWIM — I [2] C compatible two-wire interface master** **with EasyDMA**


TWI master with EasyDMA (TWIM) is a two-wire half-duplex master which can communicate with multiple
slave devices connected to the same bus

Listed here are the main features for TWIM:

- I [2] C compatible

- 100 kbps, 250 kbps, or 400 kbps

- Support for clock stretching

- EasyDMA

The two-wire interface can communicate with a bi-directional wired-AND bus with two lines (SCL, SDA).
The protocol makes it possible to interconnect up to 127 individually addressable devices. TWIM is not
compatible with CBUS.

The GPIOs used for each two-wire interface line can be chosen from any GPIO on the device and are
independently configurable. This enables great flexibility in device pinout and efficient use of board space
and signal routing.


TWIM


GPIO


PSEL.SDA


TXD.PTR


TXD+1 EasyDMA


SDA


SCL


Pin


Pin


RXD-1


PSEL.SCK


EasyDMA


RXD.PTR


RAM


buffer[0]

buffer[1]

buffer[TXD.MAXCNT-1]


buffer[0]

buffer[1]


buffer[RXD.MAXCNT-1]


TXD buffer


RXD buffer


**Figure 79: TWI master with EasyDMA**


A typical TWI setup consists of one master and one or more slaves. For an example, see _Figure 80: A typical_
_TWI setup comprising one master and three slaves_ on page 310. This TWIM is only able to operate as a
single master on the TWI bus. Multi-master bus configuration is not supported.


**Page 309**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


VDD


VDD


TWI slave


Address = b1011011


TWI master

(TWIM)


TWI slave
(EEPROM)


TWI slave

(Sensor)


Address = b1011000


R R SCL


R


Address = b1011001


SDA SCL SCL SDA SCL SDA SCL SDA


SCL SCL SDA SCL


**Figure 80: A typical TWI setup comprising one master and three slaves**


This TWI master supports clock stretching performed by the slaves. The TWI master is started by triggering
the STARTTX or STARTRX tasks, and stopped by triggering the STOP task. The TWI master will generate a
STOPPED event when it has stopped following a STOP task.

The TWI master cannot get stopped while it is suspended, so the STOP task has to be issued after the TWI
master has been resumed.

After the TWI master is started, the STARTTX task or the STARTRX task should not be triggered again
before the TWI master has stopped, i.e. following a LASTRX, LASTTX or STOPPED event.

If a NACK is clocked in from the slave, the TWI master will generate an ERROR event.

###### **33.1 Shared resources**

The TWI master shares registers and other resources with other peripherals that have the same ID as the
TWI master. Therefore, you must disable all peripherals that have the same ID as the TWI master before the
TWI master can be configured and used.

Disabling a peripheral that has the same ID as the TWI master will not reset any of the registers that are
shared with the TWI master. It is therefore important to configure all relevant registers explicitly to secure that
the TWI master operates correctly.

The Instantiation table in _Instantiation_ on page 25 shows which peripherals have the same ID as the TWI.

###### **33.2 EasyDMA**

The TWI master implements EasyDMA for reading and writing to and from the RAM.

If the TXD.PTR and the RXD.PTR are not pointing to the Data RAM region, an EasyDMA transfer may result
in a HardFault or RAM corruption. See _Memory_ on page 24 for more information about the different memory
regions.

The .PTR and .MAXCNT registers are double-buffered. They can be updated and prepared for the next RX/
TX transmission immediately after having received the RXSTARTED/TXSTARTED event.

The STOPPED event indicates that EasyDMA has finished accessing the buffer in RAM.


**33.2.1 EasyDMA list**
EasyDMA supports one list type.

The supported list type is:

- Array list


**EasyDMA array list**
The EasyDMA array list can be represented by the data structure ArrayList_type.

For illustration, see the code example below. This data structure includes only a buffer with size equal
to Channel.MAXCNT. EasyDMA will use the Channel.MAXCNT register to determine when the buffer
is full. Replace 'Channel' by the specific data channel you want to use, for instance 'NRF_SPIM->RXD',
'NRF_SPIM->TXD', 'NRF_TWIM->RXD', etc.


**Page 310**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


The Channel.MAXCNT register cannot be specified larger than the actual size of the buffer. If
Channel.MAXCNT is specified larger than the size of the buffer, the EasyDMA channel may overflow the
buffer.

This array list does not provide a mechanism to explicitly specify where the next item in the list is located.
Instead, it assumes that the list is organized as a linear array where items are located one after the other in
RAM.

```
 #define BUFFER_SIZE 4
 typedef struct ArrayList
 {
 uint8_t buffer[BUFFER_SIZE];
 } ArrayList_type;
 ArrayList_type MyArrayList[3];
 //replace 'Channel' below by the specific data channel you want to use,
 //     for instance 'NRF_SPIM->RXD', 'NRF_TWIM->RXD', etc.
 Channel.MAXCNT = BUFFER_SIZE;
 Channel.PTR = &MyArrayList;

```

Channel.PTR = &MyArrayList

Note: addresses are
assuming that
sizeof(buffer[n]) is one byte


buffer[2]

buffer[2]

buffer[2]


buffer[3]

buffer[3]

buffer[3]


0x20000000 : MyArrayList[0]

0x20000004 : MyArrayList[1]

0x20000008 : MyArrayList[2]


**Figure 81: EasyDMA array list**


buffer[0] buffer[1]

buffer[0] buffer[1]

buffer[0] buffer[1]


###### **33.3 Master write sequence**

A TWI master write sequence is started by triggering the STARTTX task. After the STARTTX task has
been triggered, the TWI master will generate a start condition on the TWI bus, followed by clocking out the
address and the READ/WRITE bit set to 0 (WRITE=0, READ=1).

The address must match the address of the slave device that the master wants to write to. The READ/
WRITE bit is followed by an ACK/NACK bit (ACK=0 or NACK=1) generated by the slave.

After receiving the ACK bit, the TWI master will clock out the data bytes found in the transmit buffer located
in RAM at the address specified in the TXD.PTR register. Each byte clocked out from the master will be
followed by an ACK/NACK bit clocked in from the slave.

A typical TWI master write sequence is illustrated in _Figure 82: TWI master writing data to a slave_ on page
312. Occurrence 2 in the figure illustrates clock stretching performed by the TWI master following a
SUSPEND task.

A SUSPENDED event indicates that the SUSPEND task has taken effect; this event can be used to
synchronize the software.


**Page 311**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA



ADDR




Stretch


~~N-1~~


~~N~~


1 2 3



**Figure 82: TWI master writing data to a slave**


The TWI master will generate a LASTTX event when it starts to transmit the last byte, this is illustrated in
_Figure 82: TWI master writing data to a slave_ on page 312

The TWI master is stopped by triggering the STOP task, this task should be triggered during the
transmission of the last byte to secure that the TWI will stop as fast as possible after sending the last byte. It
is safe to use the shortcut between LASTTX and STOP to accomplish this.

Note that the TWI master does not stop by itself when the whole RAM buffer has been sent, or when an error
occurs. The STOP task must be issued, through the use of a local or PPI shortcut, or in software as part of
the error handler.

The TWI master cannot get stopped while it is suspended, so the STOP task has to be issued after the TWI
master has been resumed.

###### **33.4 Master read sequence**

A TWI master read sequence is started by triggering the STARTRX task. After the STARTRX task has been
triggered the TWI master will generate a start condition on the TWI bus, followed by clocking out the address
and the READ/WRITE bit set to 1 (WRITE = 0, READ = 1). The address must match the address of the slave
device that the master wants to read from. The READ/WRITE bit is followed by an ACK/NACK bit (ACK=0 or
NACK = 1) generated by the slave.

After having sent the ACK bit the TWI slave will send data to the master using the clock generated by the
master.

Data received will be stored in RAM at the address specified in the RXD.PTR register. The TWI master will
generate an ACK after all but the last byte received from the slave. The TWI master will generate a NACK
after the last byte received to indicate that the read sequence shall stop.

A typical TWI master read sequence is illustrated in _Figure 83: The TWI master reading data from a slave_ on
page 313. Occurrence 2 in the figure illustrates clock stretching performed by the TWI master following a
SUSPEND task.

A SUSPENDED event indicates that the SUSPEND task has taken effect; this event can be used to
synchronize the software.

The TWI master will generate a LASTRX event when it is ready to receive the last byte, this is illustrated
in _Figure 83: The TWI master reading data from a slave_ on page 313. If RXD.MAXCNT > 1 the LASTRX
event is generated after sending the ACK of the previously received byte. If RXD.MAXCNT = 1 the LASTRX
event is generated after receiving the ACK following the address and READ bit.

The TWI master is stopped by triggering the STOP task, this task must be triggered before the NACK bit
is supposed to be transmitted. The STOP task can be triggered at any time during the reception of the last
byte. It is safe to use the shortcut between LASTRX and STOP to accomplish this.


**Page 312**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


Note that the TWI master does not stop by itself when the RAM buffer is full, or when an error occurs. The
STOP task must be issued, through the use of a local or PPI shortcut, or in software as part of the error
handler.

The TWI master cannot get stopped while it is suspended, so the STOP task has to be issued after the TWI
master has been resumed.



ADDR




Stretch


~~M-1~~


~~M~~


1 2 3



**Figure 83: The TWI master reading data from a slave**

###### **33.5 Master repeated start sequence**

A typical repeated start sequence is one in which the TWI master writes two bytes to the slave followed by
reading four bytes from the slave. This example uses shortcuts to perform the simplest type of repeated start
sequence, i.e. one write followed by one read. The same approach can be used to perform a repeated start
sequence where the sequence is read followed by write.

The figure _Figure 84: A repeated start sequence, where the TWI master writes two bytes followed by reading_
_4 bytes from the slave_ on page 313 illustrates this:


ADDR






ADDR






**Figure 84: A repeated start sequence, where the TWI master writes two bytes followed by reading 4**
**bytes from the slave**


If a more complex repeated start sequence is needed and the TWI firmware drive is serviced in a low priority
interrupt it may be necessary to use the SUSPEND task and SUSPENDED event to guarantee that the
correct tasks are generated at the correct time. This is illustrated in _Figure 85: A double repeated start_
_sequence using the SUSPEND task to secure safe operation in low priority interrupts_ on page 314.


**Page 313**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA



ADDR



ADDR



ADDR






Stretch




**Figure 85: A double repeated start sequence using the SUSPEND task to secure safe operation in low**
**priority interrupts**

###### **33.6 Low power**

When putting the system in low power and the peripheral is not needed, lowest possible power consumption
is achieved by stopping, and then disabling the peripheral.

The STOP task may not be always needed (the peripheral might already be stopped), but if it is sent,
software shall wait until the STOPPED event was received as a response before disabling the peripheral
through the ENABLE register.

###### **33.7 Master mode pin configuration**

The SCL and SDA signals associated with the TWI master are mapped to physical pins according to the
configuration specified in the PSEL.SCL and PSEL.SDA registers respectively.

The PSEL.SCL and PSEL.SDA registers and their configurations are only used as long as the TWI master
is enabled, and retained only as long as the device is in ON mode. When the peripheral is disabled, the pins
will behave as regular GPIOs, and use the configuration in their respective OUT bit field and PIN_CNF[n]
register. PSEL.SCL, PSEL.SDA must only be configured when the TWI master is disabled.

To secure correct signal levels on the pins used by the TWI master when the system is in OFF mode, and
when the TWI master is disabled, these pins must be configured in the GPIO peripheral as described in
_Table 76: GPIO configuration before enabling peripheral_ on page 314.

Only one peripheral can be assigned to drive a particular GPIO pin at a time. Failing to do so may result in
unpredictable behavior.


**Table 76: GPIO configuration before enabling peripheral**


**TWI master signal** **TWI master pin** **Direction** **Output value** **Drive strength**
SCL As specified in PSEL.SCL Input Not applicable S0D1
SDA As specified in PSEL.SDA Input Not applicable S0D1

###### **33.8 Registers**


**Table 77: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40003000 TWIM TWIM0 Two-wire interface master 0

0x40004000 TWIM TWIM1 Two-wire interface master 1


**Page 314**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


**Table 78: Register Overview**


**Register** **Offset** **Description**

TASKS_STARTRX 0x000 Start TWI receive sequence

TASKS_STARTTX 0x008 Start TWI transmit sequence

TASKS_STOP 0x014 Stop TWI transaction. Must be issued while the TWI master is not suspended.

TASKS_SUSPEND 0x01C Suspend TWI transaction

TASKS_RESUME 0x020 Resume TWI transaction

EVENTS_STOPPED 0x104 TWI stopped

EVENTS_ERROR 0x124 TWI error

EVENTS_SUSPENDED 0x148 Last byte has been sent out after the SUSPEND task has been issued, TWI traffic is now suspended.

EVENTS_RXSTARTED 0x14C Receive sequence started

EVENTS_TXSTARTED 0x150 Transmit sequence started

EVENTS_LASTRX 0x15C Byte boundary, starting to receive the last byte

EVENTS_LASTTX 0x160 Byte boundary, starting to transmit the last byte

_SHORTS_ 0x200 Shortcut register

_INTEN_ 0x300 Enable or disable interrupt

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_ERRORSRC_ 0x4C4 Error source

_ENABLE_ 0x500 Enable TWIM

_PSEL.SCL_ 0x508 Pin select for SCL signal

_PSEL.SDA_ 0x50C Pin select for SDA signal

_FREQUENCY_ 0x524 TWI frequency

_RXD.PTR_ 0x534 Data pointer

_RXD.MAXCNT_ 0x538 Maximum number of bytes in receive buffer

_RXD.AMOUNT_ 0x53C Number of bytes transferred in the last transaction

_RXD.LIST_ 0x540 EasyDMA list type

_TXD.PTR_ 0x544 Data pointer

_TXD.MAXCNT_ 0x548 Maximum number of bytes in transmit buffer

_TXD.AMOUNT_ 0x54C Number of bytes transferred in the last transaction

_TXD.LIST_ 0x550 EasyDMA list type

_ADDRESS_ 0x588 Address used in the TWI transfer


**33.8.1 SHORTS**

Address offset: 0x200

Shortcut register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LASTTX_STARTRX Shortcut between LASTTX event and STARTRX task


See _EVENTS_LASTTX_ and _TASKS_STARTRX_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

B RW LASTTX_SUSPEND Shortcut between LASTTX event and SUSPEND task


See _EVENTS_LASTTX_ and _TASKS_SUSPEND_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

C RW LASTTX_STOP Shortcut between LASTTX event and STOP task


See _EVENTS_LASTTX_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

D RW LASTRX_STARTTX Shortcut between LASTRX event and STARTTX task


See _EVENTS_LASTRX_ and _TASKS_STARTTX_

Disabled 0 Disable shortcut


**Page 315**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id F D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Enable shortcut

F RW LASTRX_STOP Shortcut between LASTRX event and STOP task


See _EVENTS_LASTRX_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**33.8.2 INTEN**

Address offset: 0x300

Enable or disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id J I H G F D A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STOPPED Enable or disable interrupt for STOPPED event


See _EVENTS_STOPPED_

Disabled 0 Disable

Enabled 1 Enable

D RW ERROR Enable or disable interrupt for ERROR event


See _EVENTS_ERROR_

Disabled 0 Disable

Enabled 1 Enable

F RW SUSPENDED Enable or disable interrupt for SUSPENDED event


See _EVENTS_SUSPENDED_

Disabled 0 Disable

Enabled 1 Enable

G RW RXSTARTED Enable or disable interrupt for RXSTARTED event


See _EVENTS_RXSTARTED_

Disabled 0 Disable

Enabled 1 Enable

H RW TXSTARTED Enable or disable interrupt for TXSTARTED event


See _EVENTS_TXSTARTED_

Disabled 0 Disable

Enabled 1 Enable

I RW LASTRX Enable or disable interrupt for LASTRX event


See _EVENTS_LASTRX_

Disabled 0 Disable

Enabled 1 Enable

J RW LASTTX Enable or disable interrupt for LASTTX event


See _EVENTS_LASTTX_

Disabled 0 Disable

Enabled 1 Enable


**33.8.3 INTENSET**

Address offset: 0x304

Enable interrupt


**Page 316**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id J I H G F D A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STOPPED Write '1' to Enable interrupt for STOPPED event


See _EVENTS_STOPPED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW ERROR Write '1' to Enable interrupt for ERROR event


See _EVENTS_ERROR_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW SUSPENDED Write '1' to Enable interrupt for SUSPENDED event


See _EVENTS_SUSPENDED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW RXSTARTED Write '1' to Enable interrupt for RXSTARTED event


See _EVENTS_RXSTARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW TXSTARTED Write '1' to Enable interrupt for TXSTARTED event


See _EVENTS_TXSTARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW LASTRX Write '1' to Enable interrupt for LASTRX event


See _EVENTS_LASTRX_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

J RW LASTTX Write '1' to Enable interrupt for LASTTX event


See _EVENTS_LASTTX_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**33.8.4 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id J I H G F D A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STOPPED Write '1' to Disable interrupt for STOPPED event


See _EVENTS_STOPPED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW ERROR Write '1' to Disable interrupt for ERROR event


See _EVENTS_ERROR_


**Page 317**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id J I H G F D A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW SUSPENDED Write '1' to Disable interrupt for SUSPENDED event


See _EVENTS_SUSPENDED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW RXSTARTED Write '1' to Disable interrupt for RXSTARTED event


See _EVENTS_RXSTARTED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW TXSTARTED Write '1' to Disable interrupt for TXSTARTED event


See _EVENTS_TXSTARTED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW LASTRX Write '1' to Disable interrupt for LASTRX event


See _EVENTS_LASTRX_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

J RW LASTTX Write '1' to Disable interrupt for LASTTX event


See _EVENTS_LASTTX_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**33.8.5 ERRORSRC**

Address offset: 0x4C4

Error source


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW OVERRUN Overrun error


A new byte was received before previous byte got transferred

into RXD buffer. (Previous data is lost)

NotReceived 0 Error did not occur

Received 1 Error occurred

B RW ANACK NACK received after sending the address (write '1' to clear)

NotReceived 0 Error did not occur

Received 1 Error occurred

C RW DNACK NACK received after sending a data byte (write '1' to clear)

NotReceived 0 Error did not occur

Received 1 Error occurred


**33.8.6 ENABLE**

Address offset: 0x500


**Page 318**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


Enable TWIM


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENABLE Enable or disable TWIM

Disabled 0 Disable TWIM

Enabled 6 Enable TWIM


**33.8.7 PSEL.SCL**

Address offset: 0x508

Pin select for SCL signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**33.8.8 PSEL.SDA**

Address offset: 0x50C

Pin select for SDA signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**33.8.9 FREQUENCY**

Address offset: 0x524

TWI frequency


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x04000000** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW FREQUENCY TWI master clock frequency

K100 0x01980000 100 kbps

K250 0x04000000 250 kbps

K400 0x06400000 400 kbps


**33.8.10 RXD.PTR**

Address offset: 0x534

Data pointer


**Page 319**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR Data pointer


**33.8.11 RXD.MAXCNT**

Address offset: 0x538

Maximum number of bytes in receive buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT [1..255] Maximum number of bytes in receive buffer


**33.8.12 RXD.AMOUNT**

Address offset: 0x53C

Number of bytes transferred in the last transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes transferred in the last transaction. In case of

NACK error, includes the NACK'ed byte.


**33.8.13 RXD.LIST**

Address offset: 0x540

EasyDMA list type


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LIST List type

Disabled 0 Disable EasyDMA list

ArrayList 1 Use array list


**33.8.14 TXD.PTR**

Address offset: 0x544

Data pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR Data pointer


**33.8.15 TXD.MAXCNT**

Address offset: 0x548

Maximum number of bytes in transmit buffer


**Page 320**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT [1..255] Maximum number of bytes in transmit buffer


**33.8.16 TXD.AMOUNT**

Address offset: 0x54C

Number of bytes transferred in the last transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes transferred in the last transaction. In case of

NACK error, includes the NACK'ed byte.


**33.8.17 TXD.LIST**

Address offset: 0x550

EasyDMA list type


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LIST List type

Disabled 0 Disable EasyDMA list

ArrayList 1 Use array list


**33.8.18 ADDRESS**

Address offset: 0x588

Address used in the TWI transfer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ADDRESS Address used in the TWI transfer

###### **33.9 Electrical specification**


**33.9.1 TWIM interface electrical specifications**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fTWIM Bit rates for TWIM [30] 100 400 kbps

ITWIM,100kbps Run current for TWIM, 100 kbps 50 µA

ITWIM,400kbps Run current for TWIM, 400 kbps 50 µA


tTWIM,START,LP Time from STARTRX/STARTTX task to transmission started, Low

power mode


tTWIM,START,CL Time from STARTRX/STARTTX task to transmission started,

Constant latency mode


tTWIM,START,CL

+

tSTART_HFINT


µs


1.5 µs


30 Higher bit rates or stronger pull-ups may require GPIOs to be set as High Drive, see GPIO chapter for more
details.


**Page 321**


33 TWIM — I [2] C compatible two-wire interface
master with EasyDMA


**33.9.2 Two Wire Interface Master (TWIM) timing specifications**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fTWIM,SCL,100kbps SCL clock frequency, 100 kbps 100 kHz

fTWIM,SCL,250kbps SCL clock frequency, 250 kbps 250 kHz

fTWIM,SCL,400kbps SCL clock frequency, 400 kbps 400 kHz

tTWIM,SU_DAT Data setup time before positive edge on SCL – all modes 300 ns

tTWIM,HD_DAT Data hold time after negative edge on SCL – all modes 500 ns


tTWIM,HD_STA,100kbps TWIM master hold time for START and repeated START

condition, 100 kbps

tTWIM,HD_STA,250kbps TWIM master hold time for START and repeated START

condition, 250kbps

tTWIM,HD_STA,400kbps TWIM master hold time for START and repeated START

condition, 400 kbps

tTWIM,SU_STO,100kbps TWIM master setup time from SCL high to STOP condition, 100

kbps

tTWIM,SU_STO,250kbps TWIM master setup time from SCL high to STOP condition, 250

kbps

tTWIM,SU_STO,400kbps TWIM master setup time from SCL high to STOP condition, 400

kbps

tTWIM,BUF,100kbps TWIM master bus free time between STOP and START

conditions, 100 kbps

tTWIM,BUF,250kbps TWIM master bus free time between STOP and START

conditions, 250 kbps

tTWIM,BUF,400kbps TWIM master bus free time between STOP and START

conditions, 400 kbps


**Figure 86: TWIM timing diagram, 1 byte transaction**


**R [kΩ]**




13




10000 ns


4000 ns


2500 ns


5000 ns


2000 ns


1250 ns


5800 ns


2700 ns


2100 ns


~~100 kbps~~
~~400 kbps~~


0 100 200 300 400 500
**cap [pF]**


**Figure 87: Recommended TWIM pullup value vs. line capacitance**


- The I2C specification allows a line capacitance of 400 pF at most.

- The nRF52832 internal pullup has a fixed value of typ. 13 kOhm, see RPU in the GPIO chapter.


**Page 322**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA

#### **34 TWIS — I [2] C compatible two-wire interface slave with** **EasyDMA**


TWI slave with EasyDMA (TWIS) is compatible with I [2] C operating at 100 kHz and 400 kHz. The TWI
transmitter and receiver implement EasyDMA.


PSELSDA PSELSCK PSELSDA


PREPARETX


PREPARERX


RXD
(signal)


TXD
(signal)


STOPPED


SUSPEND WRITE


RESUME


RXD.PTR EasyDMA EasyDMA TXD.PTR


READ


RAM


**Figure 88: TWI slave with EasyDMA**


RXD

RXD+1

RXD+2

RXD+n


TXD

TXD+1

TXD+2

TXD+n


A typical TWI setup consists of one master and one or more slaves. For an example, see _Figure 89: A typical_
_TWI setup comprising one master and three slaves_ on page 323. TWIS is only able to operate with a single
master on the TWI bus.


VDD


VDD


TWI slave

(Sensor)


TWI slave

(TWIS)


TWI master


TWI slave
(EEPROM)


Address = b1011000


SCL R R SCL SDA SCL SDA Address = b1011011SCL SDA


R R SCL


R


Address = b1011001


SDA SCL SCL SDA SCL SDA SCL SDA


**Figure 89: A typical TWI setup comprising one master and three slaves**


The TWI slave state machine is illustrated in _Figure 90: TWI slave state machine_ on page 324 and _Table_
_79: TWI slave state machine symbols_ on page 324 is explaining the different symbols used in the state
machine.


**Page 323**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


PREPARETX


ENABLE


**IDLE**


PREPARERX


/ STOPPED
_Unprepare TX_,

_Unprepare RX_


STOP

[ READ && ( _TX prepared)_ ] [ WRITE && ( _RX prepared)_ ]


Restart sequence


**RX**


**entry / U** _**nprepare RX**_

**entry / RXSTARTED**


Stop sequence


**Figure 90: TWI slave state machine**


**TX**


**entry /** _**Unprepare TX**_

**entry / TXSTARTED**


**Table 79: TWI slave state machine symbols**


**Symbol** **Type** **Description**
ENABLE Register The TWI slave has been enabled via the _ENABLE_ register
PREPARETX Task The _TASKS_PREPARETX_ task has been triggered
STOP Task The _TASKS_STOP_ task has been triggered
PREPARERX Task The _TASKS_PREPARERX_ task has been triggered
STOPPED Event The _EVENTS_STOPPED_ event was generated
RXSTARTED Event The _EVENTS_RXSTARTED_ event was generated
TXSTARTED Event The _EVENTS_TXSTARTED_ event was generated
TX prepared Internal Internal flag indicating that a _TASKS_PREPARETX_ task has been triggered. This flag is not visible to the user.
RX prepared Internal Internal flag indicating that a _TASKS_PREPARERX_ task has been triggered. This flag is not visible to the user.
Unprepare TX Internal Clears the internal 'TX prepared' flag until next _TASKS_PREPARETX_ task.
Unprepare RX Internal Clears the internal 'RX prepared' flag until next _TASKS_PREPARERX_ task.
Stop sequence TWI protocol A TWI stop sequence was detected
Restart sequence TWI protocol A TWI restart sequence was detected


The TWI slave supports clock stretching performed by the master.

The TWI slave operates in a low power mode while waiting for a TWI master to initiate a transfer. As long as
the TWI slave is not addressed, it will remain in this low power mode.

To secure correct behaviour of the TWI slave, PSEL.SCL, PSEL.SDA, CONFIG and the ADDRESS[n]
registers, must be configured prior to enabling the TWI slave through the ENABLE register. Similarly,
changing these settings must be performed while the TWI slave is disabled. Failing to do so may result in
unpredictable behaviour.


**Page 324**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA

###### **34.1 Shared resources**

The TWI slave shares registers and other resources with other peripherals that have the same ID as the TWI
slave.

Therefore, you must disable all peripherals that have the same ID as the TWI slave before the TWI slave can
be configured and used. Disabling a peripheral that has the same ID as the TWI slave will not reset any of
the registers that are shared with the TWI slave. It is therefore important to configure all relevant registers
explicitly to secure that the TWI slave operates correctly.

The Instantiation table in _Instantiation_ on page 25 shows which peripherals have the same ID as the TWI
slave.

###### **34.2 EasyDMA**

The TWI slave implements EasyDMA for reading and writing to and from the RAM.

The STOPPED event indicates that EasyDMA has finished accessing the buffer in RAM.

If the TXD.PTR and the RXD.PTR are not pointing to the Data RAM region, an EasyDMA transfer may result
in a HardFault or RAM corruption. See _Memory_ on page 24 for more information about the different memory
regions.

###### **34.3 TWI slave responding to a read command**

Before the TWI slave can respond to a read command the TWI slave must be configured correctly and
enabled via the ENABLE register. When enabled the TWI slave will be in its IDLE state where it will consume
IIDLE .

A read command is started when the TWI master generates a start condition on the TWI bus, followed by
clocking out the address and the READ/WRITE bit set to 1 (WRITE=0, READ=1). The READ/WRITE bit is
followed by an ACK/NACK bit (ACK=0 or NACK=1) response from the TWI slave.

The TWI slave is able to listen for up to two addresses at the same time. Which addresses to listen for is
configured in the ADDRESS registers and the CONFIG register.

The TWI slave will only acknowledge (ACK) the read command if the address presented by the master
matches one of the addresses the slave is configured to listen for. The TWI slave will generate a READ
event when it acknowledges the read command.

The TWI slave is only able to detect a read command from the IDLE state.

The TWI slave will set an internal 'TX prepared' flag when the PREPARETX task is triggered.

When the read command is received the TWI slave will enter the TX state if the internal 'TX prepared' flag is
set.

If the internal 'TX prepared' flag is not set when the read command is received, the TWI slave will stretch the
master's clock until the PREPARETX task is triggered and the internal 'TX prepared' flag is set.

The TWI slave will generate the TXSTARTED event and clear the 'TX prepared' flag ('unprepare TX') when
it enters the TX state. In this state the TWI slave will send the data bytes found in the transmit buffer to the
master using the master's clock. The TWI slave will consume ITX in this mode.

The TWI slave will go back to the IDLE state if the TWI slave receives a restart command when it is in the TX
state.

The TWI slave is stopped when it receives the stop condition from the TWI master. A STOPPED event will
be generated when the transaction has stopped. The TWI slave will clear the 'TX prepared' flag ('unprepare
TX') and go back to the IDLE state when it has stopped.

The transmit buffer is located in RAM at the address specified in the TXD.PTR register. The TWI slave will
only be able to send TXD.MAXCNT bytes from the transmit buffer for each transaction. If the TWI master


**Page 325**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


forces the slave to send more than TXD.MAXCNT bytes, the slave will send the byte specified in the ORC
register to the master instead. If this happens, an ERROR event will be generated.

The EasyDMA configuration registers, see TXD.PTR etc., are latched when the TXSTARTED event is
generated.

The TWI slave can be forced to stop by triggering the STOP task. A STOPPED event will be generated when
the TWI slave has stopped. The TWI slave will clear the 'TX prepared' flag and go back to the IDLE state
when it has stopped, see also _Terminating an ongoing TWI transaction_ on page 328.

Each byte sent from the slave will be followed by an ACK/NACK bit sent from the master. The TWI master
will generate a NACK following the last byte that it wants to receive to tell the slave to release the bus so
that the TWI master can generate the stop condition. The TXD.AMOUNT register can be queried after a
transaction to see how many bytes were sent.

A typical TWI slave read command response is illustrated in _Figure 91: The TWI slave responding to a read_
_command_ on page 326. Occurrence 2 in the figure illustrates clock stretching performed by the TWI slave
following a SUSPEND task.



ADDR




Stretch


~~N-1~~


~~N~~



2 3



**Figure 91: The TWI slave responding to a read command**

###### **34.4 TWI slave responding to a write command**

Before the TWI slave can respond to a write command the TWI slave must be configured correctly and
enabled via the ENABLE register. When enabled the TWI slave will be in its IDLE state where it will consume
IIDLE.

A write command is started when the TWI master generates a start condition on the TWI bus, followed by
clocking out the address and the READ/WRITE bit set to 0 (WRITE=0, READ=1). The READ/WRITE bit is
followed by an ACK/NACK bit (ACK=0 or NACK=1) response from the slave.

The TWI slave is able to listen for up to two addresses at the same time. Which addresses to listen for is
configured in the ADDRESS registers and the CONFIG register.

The TWI slave will only acknowledge (ACK) the write command if the address presented by the master
matches one of the addresses the slave is configured to listen for. The TWI slave will generate a WRITE
event if it acknowledges the write command.

The TWI slave is only able to detect a write command from the IDLE state.

The TWI slave will set an internal 'RX prepared' flag when the PREPARERX task is triggered.

When the write command is received the TWI slave will enter the RX state if the internal 'RX prepared' flag is
set.

If the internal 'RX prepared' flag is not set when the write command is received, the TWI slave will stretch the
master's clock until the PREPARERX task is triggered and the internal 'RX prepared' flag is set.


**Page 326**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


The TWI slave will generate the RXSTARTED event and clear the internal 'RX prepared' flag ('unprepare
RX') when it enters the RX state. In this state the TWI slave will be able to receive the bytes sent by the TWI
master. The TWI slave will consume IRX in this mode.

The TWI slave will go back to the IDLE state if the TWI slave receives a restart command when it is in the
RX state.

The TWI slave is stopped when it receives the stop condition from the TWI master. A STOPPED event will
be generated when the transaction has stopped. The TWI slave will clear the internal 'RX prepared' flag
('unprepare RX') and go back to the IDLE state when it has stopped.

The receive buffer is located in RAM at the address specified in the TXD.PTR register. The TWI slave will
only be able to receive as many bytes as specified in the RXD.MAXCNT register. If the TWI master tries to
send more bytes to the slave than the slave is able to receive,these bytes will be discarded and the bytes will
be NACKed by the slave. If this happens, an ERROR event will be generated.

The EasyDMA configuration registers, see RXD.PTR etc., are latched when the RXSTARTED event is
generated.

The TWI slave can be forced to stop by triggering the STOP task. A STOPPED event will be generated when
the TWI slave has stopped. The TWI slave will clear the internal 'RX prepared' flag and go back to the IDLE
state when it has stopped, see also _Terminating an ongoing TWI transaction_ on page 328.

The TWI slave will generate an ACK after every byte received from the master. The RXD.AMOUNT register
can be queried after a transaction to see how many bytes were received.

A typical TWI slave write command response is illustrated in _Figure 92: The TWI slave responding to a write_
_command_ on page 327. Occurrence 2 in the figure illustrates clock stretching performed by the TWI slave
following a SUSPEND task.



ADDR



Stretch
1


~~M-1~~


~~M~~


1 2 3



**Figure 92: The TWI slave responding to a write command**

###### **34.5 Master repeated start sequence**

An example of a repeated start sequence is one in which the TWI master writes two bytes to the slave
followed by reading four bytes from the slave.

This is illustrated in _Figure 93: A repeated start sequence, where the TWI master writes two bytes followed_
_by reading four bytes from the slave_ on page 328.

It is here assumed that the receiver does not know in advance what the master wants to read, and that
this information is provided in the first two bytes received in the write part of the repeated start sequence.
To guarantee that the CPU is able to process the received data before the TWI slave starts to reply to the
read command, the SUSPEND task is triggered via a shortcut from the READ event generated when the
read command is received. When the CPU has processed the incoming data and prepared the correct data
response, the CPU will resume the transaction by triggering the RESUME task.


**Page 327**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


ADDR






ADDR







**Figure 93: A repeated start sequence, where the TWI master writes two bytes followed by reading**
**four bytes from the slave**

###### **34.6 Terminating an ongoing TWI transaction**

In some situations, e.g. if the external TWI master is not responding correctly, it may be required to terminate
an ongoing transaction.

This can be achieved by triggering the STOP task. In this situation a STOPPED event will be generated
when the TWI has stopped independent of whether or not a STOP condition has been generated on the TWI
bus. The TWI slave will release the bus when it has stopped and go back to its IDLE state.

###### **34.7 Low power**

When putting the system in low power and the peripheral is not needed, lowest possible power consumption
is achieved by stopping, and then disabling the peripheral.

The STOP task may not be always needed (the peripheral might already be stopped), but if it is sent,
software shall wait until the STOPPED event was received as a response before disabling the peripheral
through the ENABLE register.

###### **34.8 Slave mode pin configuration**

The SCL and SDA signals associated with the TWI slave are mapped to physical pins according to the
configuration specified in the PSEL.SCL and PSEL.SDA registers respectively.

The PSEL.SCL and PSEL.SDA registers and their configurations are only used as long as the TWI slave is
enabled, and retained only as long as the device is in ON mode. When the peripheral is disabled, the pins
will behave as regular GPIOs, and use the configuration in their respective OUT bit field and PIN_CNF[n]
register. PSEL.SCL and PSEL.SDA must only be configured when the TWI slave is disabled.

To secure correct signal levels on the pins used by the TWI slave when the system is in OFF mode, and
when the TWI slave is disabled, these pins must be configured in the GPIO peripheral as described in _Table_
_80: GPIO configuration before enabling peripheral_ on page 328.

Only one peripheral can be assigned to drive a particular GPIO pin at a time. Failing to do so may result in
unpredictable behavior.


**Table 80: GPIO configuration before enabling peripheral**


**TWI slave signal** **TWI slave pin** **Direction** **Output value** **Drive strength**
SCL As specified in PSEL.SCL Input Not applicable S0D1
SDA As specified in PSEL.SDA Input Not applicable S0D1


**Page 328**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA

###### **34.9 Registers**


**Table 81: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40003000 TWIS TWIS0 Two-wire interface slave 0

0x40004000 TWIS TWIS1 Two-wire interface slave 1


**Table 82: Register Overview**


**Register** **Offset** **Description**

TASKS_STOP 0x014 Stop TWI transaction

TASKS_SUSPEND 0x01C Suspend TWI transaction

TASKS_RESUME 0x020 Resume TWI transaction

TASKS_PREPARERX 0x030 Prepare the TWI slave to respond to a write command

TASKS_PREPARETX 0x034 Prepare the TWI slave to respond to a read command

EVENTS_STOPPED 0x104 TWI stopped

EVENTS_ERROR 0x124 TWI error

EVENTS_RXSTARTED 0x14C Receive sequence started

EVENTS_TXSTARTED 0x150 Transmit sequence started

EVENTS_WRITE 0x164 Write command received

EVENTS_READ 0x168 Read command received

_SHORTS_ 0x200 Shortcut register

_INTEN_ 0x300 Enable or disable interrupt

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_ERRORSRC_ 0x4D0 Error source

_MATCH_ 0x4D4 Status register indicating which address had a match

_ENABLE_ 0x500 Enable TWIS

_PSEL.SCL_ 0x508 Pin select for SCL signal

_PSEL.SDA_ 0x50C Pin select for SDA signal

_RXD.PTR_ 0x534 RXD Data pointer

_RXD.MAXCNT_ 0x538 Maximum number of bytes in RXD buffer

_RXD.AMOUNT_ 0x53C Number of bytes transferred in the last RXD transaction

_TXD.PTR_ 0x544 TXD Data pointer

_TXD.MAXCNT_ 0x548 Maximum number of bytes in TXD buffer

_TXD.AMOUNT_ 0x54C Number of bytes transferred in the last TXD transaction

_ADDRESS[0]_ 0x588 TWI slave address 0

_ADDRESS[1]_ 0x58C TWI slave address 1

_CONFIG_ 0x594 Configuration register for the address match mechanism

_ORC_ 0x5C0 Over-read character. Character sent out in case of an over-read of the transmit buffer.


**34.9.1 SHORTS**

Address offset: 0x200

Shortcut register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW WRITE_SUSPEND Shortcut between WRITE event and SUSPEND task


See _EVENTS_WRITE_ and _TASKS_SUSPEND_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

B RW READ_SUSPEND Shortcut between READ event and SUSPEND task


See _EVENTS_READ_ and _TASKS_SUSPEND_


**Page 329**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**34.9.2 INTEN**

Address offset: 0x300

Enable or disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STOPPED Enable or disable interrupt for STOPPED event


See _EVENTS_STOPPED_

Disabled 0 Disable

Enabled 1 Enable

B RW ERROR Enable or disable interrupt for ERROR event


See _EVENTS_ERROR_

Disabled 0 Disable

Enabled 1 Enable

E RW RXSTARTED Enable or disable interrupt for RXSTARTED event


See _EVENTS_RXSTARTED_

Disabled 0 Disable

Enabled 1 Enable

F RW TXSTARTED Enable or disable interrupt for TXSTARTED event


See _EVENTS_TXSTARTED_

Disabled 0 Disable

Enabled 1 Enable

G RW WRITE Enable or disable interrupt for WRITE event


See _EVENTS_WRITE_

Disabled 0 Disable

Enabled 1 Enable

H RW READ Enable or disable interrupt for READ event


See _EVENTS_READ_

Disabled 0 Disable

Enabled 1 Enable


**34.9.3 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STOPPED Write '1' to Enable interrupt for STOPPED event


See _EVENTS_STOPPED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ERROR Write '1' to Enable interrupt for ERROR event


**Page 330**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

See _EVENTS_ERROR_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW RXSTARTED Write '1' to Enable interrupt for RXSTARTED event


See _EVENTS_RXSTARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW TXSTARTED Write '1' to Enable interrupt for TXSTARTED event


See _EVENTS_TXSTARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW WRITE Write '1' to Enable interrupt for WRITE event


See _EVENTS_WRITE_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW READ Write '1' to Enable interrupt for READ event


See _EVENTS_READ_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**34.9.4 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STOPPED Write '1' to Disable interrupt for STOPPED event


See _EVENTS_STOPPED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW ERROR Write '1' to Disable interrupt for ERROR event


See _EVENTS_ERROR_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW RXSTARTED Write '1' to Disable interrupt for RXSTARTED event


See _EVENTS_RXSTARTED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW TXSTARTED Write '1' to Disable interrupt for TXSTARTED event


See _EVENTS_TXSTARTED_

Clear 1 Disable


**Page 331**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id H G F E B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW WRITE Write '1' to Disable interrupt for WRITE event


See _EVENTS_WRITE_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW READ Write '1' to Disable interrupt for READ event


See _EVENTS_READ_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**34.9.5 ERRORSRC**

Address offset: 0x4D0

Error source


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW OVERFLOW RX buffer overflow detected, and prevented

NotDetected 0 Error did not occur

Detected 1 Error occurred

B RW DNACK NACK sent after receiving a data byte

NotReceived 0 Error did not occur

Received 1 Error occurred

C RW OVERREAD TX buffer over-read detected, and prevented

NotDetected 0 Error did not occur

Detected 1 Error occurred


**34.9.6 MATCH**

Address offset: 0x4D4

Status register indicating which address had a match


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R MATCH [0..1] Which of the addresses in {ADDRESS} matched the incoming

address


**34.9.7 ENABLE**

Address offset: 0x500

Enable TWIS


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENABLE Enable or disable TWIS

Disabled 0 Disable TWIS


**Page 332**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 9 Enable TWIS


**34.9.8 PSEL.SCL**

Address offset: 0x508

Pin select for SCL signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**34.9.9 PSEL.SDA**

Address offset: 0x50C

Pin select for SDA signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**34.9.10 RXD.PTR**

Address offset: 0x534

RXD Data pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR RXD Data pointer


**34.9.11 RXD.MAXCNT**

Address offset: 0x538

Maximum number of bytes in RXD buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT Maximum number of bytes in RXD buffer


**34.9.12 RXD.AMOUNT**

Address offset: 0x53C

Number of bytes transferred in the last RXD transaction


**Page 333**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes transferred in the last RXD transaction


**34.9.13 TXD.PTR**

Address offset: 0x544

TXD Data pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR TXD Data pointer


**34.9.14 TXD.MAXCNT**

Address offset: 0x548

Maximum number of bytes in TXD buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT Maximum number of bytes in TXD buffer


**34.9.15 TXD.AMOUNT**

Address offset: 0x54C

Number of bytes transferred in the last TXD transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes transferred in the last TXD transaction


**34.9.16 ADDRESS[0]**

Address offset: 0x588

TWI slave address 0


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ADDRESS TWI slave address


**34.9.17 ADDRESS[1]**

Address offset: 0x58C

TWI slave address 1


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ADDRESS TWI slave address


**Page 334**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


**34.9.18 CONFIG**

Address offset: 0x594

Configuration register for the address match mechanism


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A

**Reset 0x00000001** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ADDRESS0 Enable or disable address matching on ADDRESS[0]

Disabled 0 Disabled

Enabled 1 Enabled

B RW ADDRESS1 Enable or disable address matching on ADDRESS[1]

Disabled 0 Disabled

Enabled 1 Enabled


**34.9.19 ORC**

Address offset: 0x5C0

Over-read character. Character sent out in case of an over-read of the transmit buffer.


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ORC Over-read character. Character sent out in case of an over-read

of the transmit buffer.

###### **34.10 Electrical specification**


**34.10.1 TWIS slave interface electrical specifications**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fTWIS Bit rates for TWIS [31] 100 400 kbps


ITWIS,100kbps Run current for TWIS (Average current to receive and transfer a

byte to RAM), 100 kbps

ITWIS,400kbps Run current for TWIS (Average current to receive and transfer a

byte to RAM), 400 kbps


45 µA


45 µA


ITWIS,IDLE Idle current for TWIS 1 µA


tTWIS,START,LP Time from PREPARERX/PREPARETX task to ready to receive/

transmit, Low power mode


tTWIS,START,CL Time from PREPARERX/PREPARETX task to ready to receive/

transmit, Constant latency mode


**34.10.2 TWIS slave timing specifications**


tTWIS,START,CL

+

tSTART_HFINT


µs


1.5 µs


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fTWIS,SCL,400kbps SCL clock frequency, 400 kbps 400 kHz

tTWIS,SU_DAT Data setup time before positive edge on SCL – all modes 300 ns

tTWIS,HD_DAT Data hold time after negative edge on SCL – all modes 500 ns


tTWIS,HD_STA,100kbps TWI slave hold time from for START condition (SDA low to SCL

low), 100 kbps

tTWIS,HD_STA,400kbps TWI slave hold time from for START condition (SDA low to SCL

low), 400 kbps


5200 ns


1300 ns


31 Higher bit rates or stronger pull-ups may require GPIOs to be set as High Drive, see GPIO chapter for more
details.


**Page 335**


34 TWIS — I [2] C compatible two-wire interface
slave with EasyDMA


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

tTWIS,SU_STO,100kbps TWI slave setup time from SCL high to STOP condition, 100 kbps 5200 ns

tTWIS,SU_STO,400kbps TWI slave setup time from SCL high to STOP condition, 400 kbps 1300 ns


tTWIS,BUF,100kbps TWI slave bus free time between STOP and START conditions,

100 kbps

tTWIS,BUF,400kbps TWI slave bus free time between STOP and START conditions,

400 kbps


**Figure 94: TWIS timing diagram, 1 byte transaction**


**Page 336**


4700 ns


1300 ns


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA

#### **35 UARTE — Universal asynchronous receiver/** **transmitter with EasyDMA**


The Universal asynchronous receiver/transmitter with EasyDMA (UARTE) offers fast, full-duplex,
asynchronous serial communication with built-in flow control (CTS, RTS) support in hardware at a rate up to
1 Mbps, and EasyDMA data transfer from/to RAM.

Listed here are the main features for UARTE:

- Full-duplex operation

- Automatic hardware flow control

- Parity checking and generation for the 9 [th] data bit

- EasyDMA

- Up to 1 Mbps baudrate

- Return to IDLE between transactions supported (when using HW flow control)

- One stop bit

- Least significant bit (LSB) first


PSELRXD PSELCTS PSELRTS PSELTXD


STARTRX


STOPRX


RXTO


ENDRX


RAM


**Figure 95: UARTE configuration**


RXD
(signal)


RXD.PTR TXD.PTR


STARTTX


STOPTX


SUSPEND


RESUME


TXD
(signal)


ENDTX
FIFORX EasyDMA EasyDMA CTS


EasyDMA EasyDMA


CTS


NCTS


RXD

RXD+1

RXD+2

RXD+n


TXD

TXD+1

TXD+2

TXD+n


The GPIOs used for each UART interface can be chosen from any GPIO on the device and are
independently configurable. This enables great flexibility in device pinout and efficient use of board space
and signal routing.

###### **35.1 Shared resources**

The UARTE shares registers and other resources with other peripherals that have the same ID as the
UARTE.

Therefore, you must disable all peripherals that have the same ID as the UARTE before the UARTE can be
configured and used. Disabling a peripheral that has the same ID as the UARTE will not reset any of the
registers that are shared with the UARTE. It is therefore important to configure all relevant UARTE registers
explicitly to ensure that it operates correctly.

See the Instantiation table in _Instantiation_ on page 25 for details on peripherals and their IDs.

###### **35.2 EasyDMA**

The UARTE implements EasyDMA for reading and writing to and from the RAM.

If the TXD.PTR and the RXD.PTR are not pointing to the Data RAM region, an EasyDMA transfer may result
in a HardFault or RAM corruption. See _Memory_ on page 24 for more information about the different memory
regions.


**Page 337**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


The .PTR and .MAXCNT registers are double-buffered. They can be updated and prepared for the next RX/
TX transmission immediately after having received the RXSTARTED/TXSTARTED event.

The ENDRX/ENDTX event indicates that EasyDMA has finished accessing respectively the RX/TX buffer in
RAM.

###### **35.3 Transmission**

The first step of a DMA transmission is storing bytes in the transmit buffer and configuring EasyDMA. This
is achieved by writing the initial address pointer to TXD.PTR, and the number of bytes in the RAM buffer to
TXD.MAXCNT. The UARTE transmission is started by triggering the STARTTX task.

After each byte has been sent over the TXD line, a TXDRDY event will be generated.

When all bytes in the TXD buffer, as specified in the TXD.MAXCNT register, have been transmitted, the
UARTE transmission will end automatically and an ENDTX event will be generated.

A UARTE transmission sequence is stopped by triggering the STOPTX task, a TXSTOPPED event will be
generated when the UARTE transmitter has stopped.

If the ENDTX event has not already been generated when the UARTE transmitter has come to a stop, the
UARTE will generate the ENDTX event explicitly even though all bytes in the TXD buffer, as specified in the
TXD.MAXCNT register, have not been transmitted.

If flow control is enabled, a transmission will be automatically suspended when CTS is deactivated and
resumed when CTS is activated again, as illustrated in _Figure 96: UARTE transmission_ on page 338.
A byte that is in transmission when CTS is deactivated will be fully transmitted before the transmission is
suspended.


0 1 2 ~~N-2~~ ~~N-1~~ ~~N~~


1 ~~2~~


**Figure 96: UARTE transmission**


The UARTE transmitter will be in its lowest activity level, and consume the least amount of energy, when
it is stopped, i.e. before it is started via STARTTX or after it has been stopped via STOPTX and the
TXSTOPPED event has been generated. See _POWER — Power supply_ on page 81 for more information
about power modes.

###### **35.4 Reception**

The UARTE receiver is started by triggering the STARTRX task. The UARTE receiver is using EasyDMA to
store incoming data in an RX buffer in RAM.


**Page 338**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


The RX buffer is located at the address specified in the RXD.PTR register. The RXD.PTR register is doublebuffered and it can be updated and prepared for the next STARTRX task immediately after the RXSTARTED
event is generated. The size of the RX buffer is specified in the RXD.MAXCNT register and the UARTE will
generate an ENDRX event when it has filled up the RX buffer, see _Figure 97: UARTE reception_ on page
339.

For each byte received over the RXD line, an RXDRDY event will be generated. This event is likely to occur
before the corresponding data has been transferred to Data RAM.

The RXD.AMOUNT register can be queried following an ENDRX event to see how many new bytes have
been transferred to the RX buffer in RAM since the previous ENDRX event.


Data RAM


2

4


7

9


12

 
 
 


0x20000000

0x20000001

0x20000002

0x20000003

0x20000004


0x20000010

0x20000011

0x20000012

0x20000013

0x20000014


0x20000020

0x20000021

0x20000022

0x20000023

0x20000024


~~1~~ ~~2~~ ~~3~~ ~~4~~ ~~5~~ ~~6~~ ~~7~~ ~~8~~ ~~9~~


~~10~~


~~11~~ ~~12~~


~~1~~


~~2~~


~~3~~ ~~4~~ ~~5~~ ~~6~~ ~~7~~ ~~8~~



~~9~~


~~10~~


~~11~~ ~~12~~





**Figure 97: UARTE reception**


The UARTE receiver is stopped by triggering the STOPRX task. An RXTO event is generated when the
UARTE has stopped. The UARTE will make sure that an impending ENDRX event will be generated before
the RXTO event is generated. This means that the UARTE will guarantee that no ENDRX event will be
generated after RXTO, unless the UARTE is restarted or a FLUSHRX command is issued after the RXTO
event is generated.

**Important:** If the ENDRX event has not already been generated when the UARTE receiver has
come to a stop, which implies that all pending content in the RX FIFO has been moved to the RX
buffer, the UARTE will generate the ENDRX event explicitly even though the RX buffer is not full. In
this scenario the ENDRX event will be generated before the RXTO event is generated.

To be able to know how many bytes have actually been received into the RX buffer, the CPU can read the
RXD.AMOUNT register following the ENDRX event or the RXTO event.

The UARTE is able to receive up to four bytes after the STOPRX task has been triggered as long as these
are sent in succession immediately after the RTS signal is deactivated. This is possible because after the
RTS is deactivated the UARTE is able to receive bytes for an extended period equal to the time it takes to
send 4 bytes on the configured baud rate.

After the RXTO event is generated the internal RX FIFO may still contain data, and to move this data to RAM
the FLUSHRX task must be triggered. To make sure that this data does not overwrite data in the RX buffer,
the RX buffer should be emptied or the RXD.PTR should be updated before the FLUSHRX task is triggered.


**Page 339**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


To make sure that all data in the RX FIFO is moved to the RX buffer, the RXD.MAXCNT register must be set
to RXD.MAXCNT > 4, see _Figure 98: UARTE reception with forced stop via STOPRX_ on page 340. The
UARTE will generate the ENDRX event after completing the FLUSHRX task even if the RX FIFO was empty
or if the RX buffer does not get filled up. To be able to know how many bytes have actually been received
into the RX buffer in this case, the CPU can read the RXD.AMOUNT register following the ENDRX event.


~~1~~ ~~2~~ ~~3~~ ~~4~~ ~~5~~ ~~6~~ ~~7~~ ~~8~~ ~~9~~ ~~10~~ ~~11, 12, 13, 14~~


~~1~~


~~2~~


~~3~~ ~~4~~ ~~5~~ ~~6~~ ~~7~~ ~~8~~



~~9~~ ~~10~~ ~~11~~ ~~12~~ ~~13~~ ~~14~~







~~Timeout~~


**Figure 98: UARTE reception with forced stop via STOPRX**


If HW flow control is enabled the RTS signal will be deactivated when the receiver is stopped via the
STOPRX task or when the UARTE is only able to receive four more bytes in its internal RX FIFO.

With flow control disabled, the UARTE will function in the same way as when the flow control is enabled
except that the RTS line will not be used. This means that no signal will be generated when the UARTE has
reached the point where it is only able to receive four more bytes in its internal RX FIFO. Data received when
the internal RX FIFO is filled up, will be lost.

The UARTE receiver will be in its lowest activity level, and consume the least amount of energy, when it is
stopped, i.e. before it is started via STARTRX or after it has been stopped via STOPRX and the RXTO event
has been generated. See _POWER — Power supply_ on page 81 for more information about power modes.

###### **35.5 Error conditions**

An ERROR event, in the form of a framing error, will be generated if a valid stop bit is not detected in a
frame. Another ERROR event, in the form of a break condition, will be generated if the RXD line is held
active low for longer than the length of a data frame. Effectively, a framing error is always generated before a
break condition occurs.

An ERROR event will not stop reception. If the error was a parity error, the received byte will still be
transferred into Data RAM, and so will following incoming bytes. If there was a framing error (wrong stop bit),
that specific byte will NOT be stored into Data RAM, but following incoming bytes will.

###### **35.6 Using the UARTE without flow control**

If flow control is not enabled, the interface will behave as if the CTS and RTS lines are kept active all the
time.

###### **35.7 Parity configuration**

When parity is enabled, the parity will be generated automatically from the even parity of TXD and RXD for
transmission and reception respectively.

###### **35.8 Low power**

When putting the system in low power and the peripheral is not needed, lowest possible power consumption
is achieved by stopping, and then disabling the peripheral.


**Page 340**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


The STOPTX and STOPRX tasks may not be always needed (the peripheral might already be stopped),
but if STOPTX and/or STOPRX is sent, software shall wait until the TXSTOPPED and/or RXTO event is
received in response, before disabling the peripheral through the ENABLE register.

###### **35.9 Pin configuration**

The different signals RXD, CTS (Clear To Send, active low), RTS (Request To Send, active low), and TXD
associated with the UARTE are mapped to physical pins according to the configuration specified in the
PSEL.RXD, PSEL.CTS, PSEL.RTS, and PSEL.TXD registers respectively.

The PSEL.RXD, PSEL.CTS, PSEL.RTS, and PSEL.TXD registers and their configurations are only used
as long as the UARTE is enabled, and retained only for the duration the device is in ON mode. PSEL.RXD,
PSEL.RTS, PSEL.RTS and PSEL.TXD must only be configured when the UARTE is disabled.

To secure correct signal levels on the pins by the UARTE when the system is in OFF mode, the pins must be
configured in the GPIO peripheral as described in _Table 83: GPIO configuration before enabling peripheral_
on page 341.

Only one peripheral can be assigned to drive a particular GPIO pin at a time. Failing to do so may result in
unpredictable behavior.


**Table 83: GPIO configuration before enabling peripheral**


**UARTE signal** **UARTE pin** **Direction** **Output value**
RXD As specified in PSEL.RXD Input Not applicable
CTS As specified in PSEL.CTS Input Not applicable
RTS As specified in PSEL.RTS Output 1
TXD As specified in PSEL.TXD Output 1

###### **35.10 Registers**


**Table 84: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40002000 UARTE UARTE0 Universal Asynchronous Receiver/

Transmitter with EasyDMA


**Table 85: Register Overview**


**Register** **Offset** **Description**

TASKS_STARTRX 0x000 Start UART receiver

TASKS_STOPRX 0x004 Stop UART receiver

TASKS_STARTTX 0x008 Start UART transmitter

TASKS_STOPTX 0x00C Stop UART transmitter

TASKS_FLUSHRX 0x02C Flush RX FIFO into RX buffer

EVENTS_CTS 0x100 CTS is activated (set low). Clear To Send.

EVENTS_NCTS 0x104 CTS is deactivated (set high). Not Clear To Send.

EVENTS_RXDRDY 0x108 Data received in RXD (but potentially not yet transferred to Data RAM)

EVENTS_ENDRX 0x110 Receive buffer is filled up

EVENTS_TXDRDY 0x11C Data sent from TXD

EVENTS_ENDTX 0x120 Last TX byte transmitted

EVENTS_ERROR 0x124 Error detected

EVENTS_RXTO 0x144 Receiver timeout

EVENTS_RXSTARTED 0x14C UART receiver has started

EVENTS_TXSTARTED 0x150 UART transmitter has started

EVENTS_TXSTOPPED 0x158 Transmitter stopped

_SHORTS_ 0x200 Shortcut register

_INTEN_ 0x300 Enable or disable interrupt

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt


**Page 341**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


**Register** **Offset** **Description**

_ERRORSRC_ 0x480 Error source

_ENABLE_ 0x500 Enable UART

_PSEL.RTS_ 0x508 Pin select for RTS signal

_PSEL.TXD_ 0x50C Pin select for TXD signal

_PSEL.CTS_ 0x510 Pin select for CTS signal

_PSEL.RXD_ 0x514 Pin select for RXD signal

_BAUDRATE_ 0x524 Baud rate. Accuracy depends on the HFCLK source selected.

_RXD.PTR_ 0x534 Data pointer

_RXD.MAXCNT_ 0x538 Maximum number of bytes in receive buffer

_RXD.AMOUNT_ 0x53C Number of bytes transferred in the last transaction

_TXD.PTR_ 0x544 Data pointer

_TXD.MAXCNT_ 0x548 Maximum number of bytes in transmit buffer

_TXD.AMOUNT_ 0x54C Number of bytes transferred in the last transaction

_CONFIG_ 0x56C Configuration of parity and hardware flow control


**35.10.1 SHORTS**

Address offset: 0x200

Shortcut register


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

C RW ENDRX_STARTRX Shortcut between ENDRX event and STARTRX task


See _EVENTS_ENDRX_ and _TASKS_STARTRX_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

D RW ENDRX_STOPRX Shortcut between ENDRX event and STOPRX task


See _EVENTS_ENDRX_ and _TASKS_STOPRX_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**35.10.2 INTEN**

Address offset: 0x300

Enable or disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CTS Enable or disable interrupt for CTS event


See _EVENTS_CTS_

Disabled 0 Disable

Enabled 1 Enable

B RW NCTS Enable or disable interrupt for NCTS event


See _EVENTS_NCTS_

Disabled 0 Disable

Enabled 1 Enable

C RW RXDRDY Enable or disable interrupt for RXDRDY event


See _EVENTS_RXDRDY_

Disabled 0 Disable

Enabled 1 Enable

D RW ENDRX Enable or disable interrupt for ENDRX event


See _EVENTS_ENDRX_


**Page 342**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Disable

Enabled 1 Enable

E RW TXDRDY Enable or disable interrupt for TXDRDY event


See _EVENTS_TXDRDY_

Disabled 0 Disable

Enabled 1 Enable

F RW ENDTX Enable or disable interrupt for ENDTX event


See _EVENTS_ENDTX_

Disabled 0 Disable

Enabled 1 Enable

G RW ERROR Enable or disable interrupt for ERROR event


See _EVENTS_ERROR_

Disabled 0 Disable

Enabled 1 Enable

H RW RXTO Enable or disable interrupt for RXTO event


See _EVENTS_RXTO_

Disabled 0 Disable

Enabled 1 Enable

I RW RXSTARTED Enable or disable interrupt for RXSTARTED event


See _EVENTS_RXSTARTED_

Disabled 0 Disable

Enabled 1 Enable

J RW TXSTARTED Enable or disable interrupt for TXSTARTED event


See _EVENTS_TXSTARTED_

Disabled 0 Disable

Enabled 1 Enable

L RW TXSTOPPED Enable or disable interrupt for TXSTOPPED event


See _EVENTS_TXSTOPPED_

Disabled 0 Disable

Enabled 1 Enable


**35.10.3 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CTS Write '1' to Enable interrupt for CTS event


See _EVENTS_CTS_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW NCTS Write '1' to Enable interrupt for NCTS event


See _EVENTS_NCTS_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW RXDRDY Write '1' to Enable interrupt for RXDRDY event


**Page 343**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

See _EVENTS_RXDRDY_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW ENDRX Write '1' to Enable interrupt for ENDRX event


See _EVENTS_ENDRX_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW TXDRDY Write '1' to Enable interrupt for TXDRDY event


See _EVENTS_TXDRDY_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW ENDTX Write '1' to Enable interrupt for ENDTX event


See _EVENTS_ENDTX_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW ERROR Write '1' to Enable interrupt for ERROR event


See _EVENTS_ERROR_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW RXTO Write '1' to Enable interrupt for RXTO event


See _EVENTS_RXTO_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW RXSTARTED Write '1' to Enable interrupt for RXSTARTED event


See _EVENTS_RXSTARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

J RW TXSTARTED Write '1' to Enable interrupt for TXSTARTED event


See _EVENTS_TXSTARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

L RW TXSTOPPED Write '1' to Enable interrupt for TXSTOPPED event


See _EVENTS_TXSTOPPED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**35.10.4 INTENCLR**

Address offset: 0x308

Disable interrupt


**Page 344**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW CTS Write '1' to Disable interrupt for CTS event


See _EVENTS_CTS_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW NCTS Write '1' to Disable interrupt for NCTS event


See _EVENTS_NCTS_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW RXDRDY Write '1' to Disable interrupt for RXDRDY event


See _EVENTS_RXDRDY_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW ENDRX Write '1' to Disable interrupt for ENDRX event


See _EVENTS_ENDRX_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW TXDRDY Write '1' to Disable interrupt for TXDRDY event


See _EVENTS_TXDRDY_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW ENDTX Write '1' to Disable interrupt for ENDTX event


See _EVENTS_ENDTX_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW ERROR Write '1' to Disable interrupt for ERROR event


See _EVENTS_ERROR_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW RXTO Write '1' to Disable interrupt for RXTO event


See _EVENTS_RXTO_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW RXSTARTED Write '1' to Disable interrupt for RXSTARTED event


See _EVENTS_RXSTARTED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

J RW TXSTARTED Write '1' to Disable interrupt for TXSTARTED event


See _EVENTS_TXSTARTED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

L RW TXSTOPPED Write '1' to Disable interrupt for TXSTOPPED event


**Page 345**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id L J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

See _EVENTS_TXSTOPPED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**35.10.5 ERRORSRC**

Address offset: 0x480

Error source


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW OVERRUN Overrun error


A start bit is received while the previous data still lies in RXD.

(Previous data is lost.)

NotPresent 0 Read: error not present

Present 1 Read: error present

B RW PARITY Parity error


A character with bad parity is received, if HW parity check is

enabled.

NotPresent 0 Read: error not present

Present 1 Read: error present

C RW FRAMING Framing error occurred


A valid stop bit is not detected on the serial data input after all

bits in a character have been received.

NotPresent 0 Read: error not present

Present 1 Read: error present

D RW BREAK Break condition


The serial data input is '0' for longer than the length of a data

frame. (The data frame length is 10 bits without parity bit, and

11 bits with parity bit.).

NotPresent 0 Read: error not present

Present 1 Read: error present


**35.10.6 ENABLE**

Address offset: 0x500

Enable UART


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENABLE Enable or disable UARTE

Disabled 0 Disable UARTE

Enabled 8 Enable UARTE


**35.10.7 PSEL.RTS**

Address offset: 0x508

Pin select for RTS signal


**Page 346**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**35.10.8 PSEL.TXD**

Address offset: 0x50C

Pin select for TXD signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**35.10.9 PSEL.CTS**

Address offset: 0x510

Pin select for CTS signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**35.10.10 PSEL.RXD**

Address offset: 0x514

Pin select for RXD signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**35.10.11 BAUDRATE**

Address offset: 0x524

Baud rate. Accuracy depends on the HFCLK source selected.


**Page 347**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x04000000** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW BAUDRATE Baud rate

Baud1200 0x0004F000 1200 baud (actual rate: 1205)

Baud2400 0x0009D000 2400 baud (actual rate: 2396)

Baud4800 0x0013B000 4800 baud (actual rate: 4808)

Baud9600 0x00275000 9600 baud (actual rate: 9598)

Baud14400 0x003AF000 14400 baud (actual rate: 14401)

Baud19200 0x004EA000 19200 baud (actual rate: 19208)

Baud28800 0x0075C000 28800 baud (actual rate: 28777)

Baud38400 0x009D0000 38400 baud (actual rate: 38369)

Baud57600 0x00EB0000 57600 baud (actual rate: 57554)

Baud76800 0x013A9000 76800 baud (actual rate: 76923)

Baud115200 0x01D60000 115200 baud (actual rate: 115108)

Baud230400 0x03B00000 230400 baud (actual rate: 231884)

Baud250000 0x04000000 250000 baud

Baud460800 0x07400000 460800 baud (actual rate: 457143)

Baud921600 0x0F000000 921600 baud (actual rate: 941176)

Baud1M 0x10000000 1Mega baud


**35.10.12 RXD.PTR**

Address offset: 0x534

Data pointer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR Data pointer


**35.10.13 RXD.MAXCNT**

Address offset: 0x538

Maximum number of bytes in receive buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT Maximum number of bytes in receive buffer


**35.10.14 RXD.AMOUNT**

Address offset: 0x53C

Number of bytes transferred in the last transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes transferred in the last transaction


**35.10.15 TXD.PTR**

Address offset: 0x544

Data pointer


**Page 348**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PTR Data pointer


**35.10.16 TXD.MAXCNT**

Address offset: 0x548

Maximum number of bytes in transmit buffer


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW MAXCNT Maximum number of bytes in transmit buffer


**35.10.17 TXD.AMOUNT**

Address offset: 0x54C

Number of bytes transferred in the last transaction


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R AMOUNT Number of bytes transferred in the last transaction


**35.10.18 CONFIG**

Address offset: 0x56C

Configuration of parity and hardware flow control


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B B B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW HWFC Hardware flow control

Disabled 0 Disabled

Enabled 1 Enabled

B RW PARITY Parity

Excluded 0x0 Exclude parity bit

Included 0x7 Include parity bit

###### **35.11 Electrical specification**


**35.11.1 UARTE electrical specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

fUARTE Baud rate for UARTE [32] . 1000 kbps

IUARTE1M Run current at max baud rate. 55 µA

IUARTE115k Run current at 115200 bps. 55 µA

IUARTE1k2 Run current at 1200 bps. 55 µA

IUARTE,IDLE Idle current for UARTE (STARTed, no XXX activity) 1 µA

tUARTE,CTSH CTS high time 1 µs


32 Higher baud rates may require GPIOs to be set as High Drive, see GPIO chapter for more details.


**Page 349**


35 UARTE — Universal asynchronous receiver/
transmitter with EasyDMA


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**


tUARTE,START,LP Time from STARTRX/STARTTX task to transmission started, low

power mode


tUARTE,START,CL Time from STARTRX/STARTTX task to transmission started,

constant latency mode


**Page 350**


tUARTE,START,CL

+

tSTART_HFINT


µs


1 µs


36 QDEC — Quadrature decoder

#### **36 QDEC — Quadrature decoder**


The Quadrature decoder (QDEC) provides buffered decoding of quadrature-encoded sensor signals. It is
suitable for mechanical and optical sensors.

The sample period and accumulation are configurable to match application requirements. The QDEC
provides the following:

- Decoding of digital waveform from off-chip quadrature encoder.

- Sample accumulation eliminating hard real-time requirements to be enforced on application.

- Optional input de-bounce filters.

- Optional LED output signal for optical encoders.


ACCREAD


ACC


+


SAMPLE


ACCDBLREAD


ACCDBL


+


Quadrature decoder


IO router


On-chip

Off-chip


Phase A Phase B LED


Mechanical to electrical


Mechanical

device


Quadrature Encoder


**Figure 99: Quadrature decoder configuration**

###### **36.1 Sampling and decoding**

The QDEC decodes the output from an incremental motion encoder by sampling the QDEC phase input pins
(A and B).

The off-chip quadrature encoder is an incremental motion encoder outputting two waveforms, phase A and
phase B. The two output waveforms are always 90 degrees out of phase, meaning that one always changes
level before the other. The direction of movement is indicated by which of these two waveforms that changes
level first. Invalid transitions may occur, that is when the two waveforms switch simultaneously. This may
occur if the wheel rotates too fast relative to the sample rate set for the decoder.


**Page 351**


36 QDEC — Quadrature decoder


The QDEC decodes the output from the off-chip encoder by sampling the QDEC phase input pins (A and B)
at a fixed rate as specified in the SAMPLEPER register.

If the SAMPLEPER value needs to be changed, the QDEC shall be stopped using the STOP task.
SAMPLEPER can be then changed upon receiving the STOPPED event, and QDEC can be restarted using
the START task. Failing to do so may result in unpredictable behaviour.

It is good practice to change other registers (LEDPOL, REPORTPER, DBFEN and LEDPRE) only when the
QDEC is stopped.

When started, the decoder continuously samples the two input waveforms and decodes these by comparing
the current sample pair (n) with the previous sample pair (n-1).

The decoding of the sample pairs is described in the table below.


**Table 86: Sampled value encoding**


**Previous**
**sample pair(n**

**- 1)**


**Current**
**samples pair(n)**


**SAMPLE**
**register**


**ACC operation** **ACCDBL**
**operation**


**Description**


**A** **B** **A** **B**
0 0 0 0 0 No change No change No movement
0 0 0 1 1 Increment No change Movement in positive direction
0 0 1 0 -1 Decrement No change Movement in negative direction
0 0 1 1 2 No change Increment Error: Double transition
0 1 0 0 -1 Decrement No change Movement in negative direction
0 1 0 1 0 No change No change No movement
0 1 1 0 2 No change Increment Error: Double transition
0 1 1 1 1 Increment No change Movement in positive direction
1 0 0 0 1 Increment No change Movement in positive direction
1 0 0 1 2 No change Increment Error: Double transition
1 0 1 0 0 No change No change No movement
1 0 1 1 -1 Decrement No change Movement in negative direction
1 1 0 0 2 No change Increment Error: Double transition
1 1 0 1 -1 Decrement No change Movement in negative direction
1 1 1 0 1 Increment No change Movement in positive direction
1 1 1 1 0 No change No change No movement


###### **36.2 LED output**

The LED output follows the sample period, and the LED is switched on a given period before sampling and
switched off immediately after the inputs are sampled. The period the LED is switched on before sampling is
given in the LEDPRE register.

The LED output pin polarity is specified in the LEDPOL register.

For using off-chip mechanical encoders not requiring a LED, the LED output can be disabled by writing
value 'Disconnected' to the CONNECT field of the PSEL.LED register. In this case the QDEC will not acquire
access to a LED output pin and the pin can be used for other purposes by the CPU.

###### **36.3 Debounce filters**

Each of the two-phase inputs have digital debounce filters.

When enabled through the DBFEN register, the filter inputs are sampled at a fixed 1 MHz frequency during
the entire sample period (which is specified in the SAMPLEPER register), and the filters require all of the
samples within this sample period to equal before the input signal is accepted and transferred to the output
of the filter.

As a result, only input signal with a steady state longer than twice the period specified in SAMPLEPER are
guaranteed to pass through the filter, and any signal with a steady state shorter than SAMPLEPER will
always be suppressed by the filter. (This is assumed that the frequency during the debounce period never
exceeds 500 kHz (as required by the Nyquist theorem when using a 1 MHz sample frequency).

The LED will always be ON when the debounce filters are enabled, as the inputs in this case will be sampled
continuously.


**Page 352**


36 QDEC — Quadrature decoder


Note that when when the debounce filters are enabled, displacements reported by the QDEC peripheral are
delayed by one SAMPLEPER period.

###### **36.4 Accumulators**

The quadrature decoder contains two accumulator registers, ACC and ACCDBL, that accumulate
respectively valid motion sample values and the number of detected invalid samples (double transitions).

The ACC register will accumulate all valid values (1/-1) written to the SAMPLE register. This can be useful
for preventing hard real-time requirements from being enforced on the application. When using the ACC
register the application does not need to read every single sample from the SAMPLE register, but can
instead fetch the ACC register whenever it fits the application. The ACC register will always hold the relative
movement of the external mechanical device since the previous clearing of the ACC register. Sample values
indicating a double transition (2) will not be accumulated in the ACC register.

An ACCOF event will be generated if the ACC receives a SAMPLE value that would cause the register to
overflow or underflow. Any SAMPLE value that would cause an ACC overflow or underflow will be discarded,
but any samples not causing the ACC to overflow or underflow will still be accepted.

The accumulator ACCDBL accumulates the number of detected double transitions since the previous
clearing of the ACCDBL register.

The ACC and ACCDBL registers can be cleared by the READCLRACC and subsequently read using the
ACCREAD and ACCDBLREAD registers.

The ACC register can be separately cleared by the RDCLRACC and subsequently read using the ACCREAD
registers.

The ACCDBL register can be separately cleared by the RDCLRDBL and subsequently read using the
ACCDBLREAD registers.

The REPORTPER register allows automating the capture of several samples before it can send out a
REPORTRDY event in case a non-null displacement has been captured and accumulated, and a DBLRDY
event in case one or more double-displacements have been captured and accumulated. The REPORTPER
field in this register selects after how many samples the accumulators contents are evaluated to send (or not)
REPORTRDY and DBLRDY events.

Using the RDCLRACC task (manually sent upon receiving the event, or using the DBLRDY_RDCLRACC
shortcut), ACCREAD can then be read.

In case at least one double transition has been captured and accumulated, a DBLRDY event is sent. Using
the RDCLRDBL task (manually sent upon receiving the event, or using the DBLRDY_RDCLRDBL shortcut),
ACCDBLREAD can then be read.

###### **36.5 Output/input pins**

The QDEC uses a three-pin interface to the off-chip quadrature encoder.

These pins will be acquired when the QDEC is enabled in the ENABLE register. The pins acquired by the
QDEC cannot be written by the CPU, but they can still be read by the CPU.

The pin numbers to be used for the QDEC are selected using the PSEL.n registers.

###### **36.6 Pin configuration**

The Phase A, Phase B, and LED signals are mapped to physical pins according to the configuration
specified in the PSEL.A, PSEL.B, and PSEL.LED registers respectively.

If the CONNECT field value 'Disconnected' is specified in any of these registers, the associated signal
will not be connected to any physical pin. The PSEL.A, PSEL.B, and PSEL.LED registers and their
configurations are only used as long as the QDEC is enabled, and retained only as long as the device is in


**Page 353**


36 QDEC — Quadrature decoder


ON mode. When the peripheral is disabled, the pins will behave as regular GPIOs, and use the configuration
in their respective OUT bit field and PIN_CNF[n] register.

To secure correct behavior in the QDEC, the pins used by the QDEC must be configured in the GPIO
peripheral as described in _Table 87: GPIO configuration before enabling peripheral_ on page 354 before
enabling the QDEC. This configuration must be retained in the GPIO for the selected IOs as long as the
QDEC is enabled.

Only one peripheral can be assigned to drive a particular GPIO pin at a time. Failing to do so may result in
unpredictable behavior.


**Table 87: GPIO configuration before enabling peripheral**


**QDEC signal** **QDEC pin** **Direction** **Output value** **Comment**
Phase A As specified in PSEL.A Input Not applicable
Phase B As specified in PSEL.B Input Not applicable
LED As specified in PSEL.LED Input Not applicable

###### **36.7 Registers**


**Table 88: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40012000 QDEC QDEC Quadrature decoder


**Table 89: Register Overview**


**Register** **Offset** **Description**

TASKS_START 0x000 Task starting the quadrature decoder

TASKS_STOP 0x004 Task stopping the quadrature decoder

TASKS_READCLRACC 0x008 Read and clear ACC and ACCDBL

TASKS_RDCLRACC 0x00C Read and clear ACC

TASKS_RDCLRDBL 0x010 Read and clear ACCDBL

EVENTS_SAMPLERDY 0x100 Event being generated for every new sample value written to the SAMPLE register

EVENTS_REPORTRDY 0x104 Non-null report ready

EVENTS_ACCOF 0x108 ACC or ACCDBL register overflow

EVENTS_DBLRDY 0x10C Double displacement(s) detected

EVENTS_STOPPED 0x110 QDEC has been stopped

_SHORTS_ 0x200 Shortcut register

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_ENABLE_ 0x500 Enable the quadrature decoder

_LEDPOL_ 0x504 LED output pin polarity

_SAMPLEPER_ 0x508 Sample period

_SAMPLE_ 0x50C Motion sample value

_REPORTPER_ 0x510 Number of samples to be taken before REPORTRDY and DBLRDY events can be generated

_ACC_ 0x514 Register accumulating the valid transitions

_ACCREAD_ 0x518 Snapshot of the ACC register, updated by the READCLRACC or RDCLRACC task

_PSEL.LED_ 0x51C Pin select for LED signal

_PSEL.A_ 0x520 Pin select for A signal

_PSEL.B_ 0x524 Pin select for B signal

_DBFEN_ 0x528 Enable input debounce filters

_LEDPRE_ 0x540 Time period the LED is switched ON prior to sampling

_ACCDBL_ 0x544 Register accumulating the number of detected double transitions

_ACCDBLREAD_ 0x548 Snapshot of the ACCDBL, updated by the READCLRACC or RDCLRDBL task


**36.7.1 SHORTS**

Address offset: 0x200

Shortcut register


**Page 354**


36 QDEC — Quadrature decoder


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW REPORTRDY_READCLRACC Shortcut between REPORTRDY event and READCLRACC task


See _EVENTS_REPORTRDY_ and _TASKS_READCLRACC_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

B RW SAMPLERDY_STOP Shortcut between SAMPLERDY event and STOP task


See _EVENTS_SAMPLERDY_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

C RW REPORTRDY_RDCLRACC Shortcut between REPORTRDY event and RDCLRACC task


See _EVENTS_REPORTRDY_ and _TASKS_RDCLRACC_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

D RW REPORTRDY_STOP Shortcut between REPORTRDY event and STOP task


See _EVENTS_REPORTRDY_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

E RW DBLRDY_RDCLRDBL Shortcut between DBLRDY event and RDCLRDBL task


See _EVENTS_DBLRDY_ and _TASKS_RDCLRDBL_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

F RW DBLRDY_STOP Shortcut between DBLRDY event and STOP task


See _EVENTS_DBLRDY_ and _TASKS_STOP_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut

G RW SAMPLERDY_READCLRACC Shortcut between SAMPLERDY event and READCLRACC task


See _EVENTS_SAMPLERDY_ and _TASKS_READCLRACC_

Disabled 0 Disable shortcut

Enabled 1 Enable shortcut


**36.7.2 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW SAMPLERDY Write '1' to Enable interrupt for SAMPLERDY event


See _EVENTS_SAMPLERDY_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW REPORTRDY Write '1' to Enable interrupt for REPORTRDY event


See _EVENTS_REPORTRDY_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW ACCOF Write '1' to Enable interrupt for ACCOF event


See _EVENTS_ACCOF_

Set 1 Enable


**Page 355**


36 QDEC — Quadrature decoder


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW DBLRDY Write '1' to Enable interrupt for DBLRDY event


See _EVENTS_DBLRDY_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW STOPPED Write '1' to Enable interrupt for STOPPED event


See _EVENTS_STOPPED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**36.7.3 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW SAMPLERDY Write '1' to Disable interrupt for SAMPLERDY event


See _EVENTS_SAMPLERDY_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW REPORTRDY Write '1' to Disable interrupt for REPORTRDY event


See _EVENTS_REPORTRDY_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW ACCOF Write '1' to Disable interrupt for ACCOF event


See _EVENTS_ACCOF_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW DBLRDY Write '1' to Disable interrupt for DBLRDY event


See _EVENTS_DBLRDY_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW STOPPED Write '1' to Disable interrupt for STOPPED event


See _EVENTS_STOPPED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**36.7.4 ENABLE**

Address offset: 0x500

Enable the quadrature decoder


**Page 356**


36 QDEC — Quadrature decoder


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENABLE Enable or disable the quadrature decoder


When enabled the decoder pins will be active. When disabled

the quadrature decoder pins are not active and can be used as

GPIO .

Disabled 0 Disable

Enabled 1 Enable


**36.7.5 LEDPOL**

Address offset: 0x504

LED output pin polarity


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LEDPOL LED output pin polarity

ActiveLow 0 Led active on output pin low

ActiveHigh 1 Led active on output pin high


**36.7.6 SAMPLEPER**

Address offset: 0x508

Sample period


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW SAMPLEPER Sample period. The SAMPLE register will be updated for every

new sample

128us 0 128 us

256us 1 256 us

512us 2 512 us

1024us 3 1024 us

2048us 4 2048 us

4096us 5 4096 us

8192us 6 8192 us

16384us 7 16384 us

32ms 8 32768 us

65ms 9 65536 us

131ms 10 131072 us


**36.7.7 SAMPLE**

Address offset: 0x50C

Motion sample value


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R SAMPLE [-1..2] Last motion sample


**Page 357**


36 QDEC — Quadrature decoder


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

The value is a 2's complement value, and the sign gives the

direction of the motion. The value '2' indicates a double

transition.


**36.7.8 REPORTPER**

Address offset: 0x510

Number of samples to be taken before REPORTRDY and DBLRDY events can be generated


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW REPORTPER Specifies the number of samples to be accumulated in the ACC

register before the REPORTRDY and DBLRDY events can be

generated


The report period in [us] is given as: RPUS = SP * RP Where

RPUS is the report period in [us/report], SP is the sample period

in [us/sample] specified in SAMPLEPER, and RP is the report

period in [samples/report] specified in REPORTPER .

10Smpl 0 10 samples / report

40Smpl 1 40 samples / report

80Smpl 2 80 samples / report

120Smpl 3 120 samples / report

160Smpl 4 160 samples / report

200Smpl 5 200 samples / report

240Smpl 6 240 samples / report

280Smpl 7 280 samples / report

1Smpl 8 1 sample / report


**36.7.9 ACC**

Address offset: 0x514

Register accumulating the valid transitions


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R ACC [-1024..1023] Register accumulating all valid samples (not double transition)

read from the SAMPLE register


Double transitions ( SAMPLE = 2 ) will not be accumulated in

this register. The value is a 32 bit 2's complement value. If a

sample that would cause this register to overflow or underflow

is received, the sample will be ignored and an overflow event

( ACCOF ) will be generated. The ACC register is cleared by

triggering the READCLRACC or the RDCLRACC task.


**36.7.10 ACCREAD**

Address offset: 0x518

Snapshot of the ACC register, updated by the READCLRACC or RDCLRACC task


**Page 358**


36 QDEC — Quadrature decoder


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R ACCREAD [-1024..1023] Snapshot of the ACC register.


The ACCREAD register is updated when the READCLRACC or

RDCLRACC task is triggered


**36.7.11 PSEL.LED**

Address offset: 0x51C

Pin select for LED signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**36.7.12 PSEL.A**

Address offset: 0x520

Pin select for A signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**36.7.13 PSEL.B**

Address offset: 0x524

Pin select for B signal


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B A A A A A

**Reset 0xFFFFFFFF** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PIN [0..31] Pin number

B RW CONNECT Connection

Disconnected 1 Disconnect

Connected 0 Connect


**36.7.14 DBFEN**

Address offset: 0x528

Enable input debounce filters


**Page 359**


36 QDEC — Quadrature decoder


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW DBFEN Enable input debounce filters

Disabled 0 Debounce input filters disabled

Enabled 1 Debounce input filters enabled


**36.7.15 LEDPRE**

Address offset: 0x540

Time period the LED is switched ON prior to sampling


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A A A A A

**Reset 0x00000010** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LEDPRE [1..511] Period in us the LED is switched on prior to sampling


**36.7.16 ACCDBL**

Address offset: 0x544

Register accumulating the number of detected double transitions


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R ACCDBL [0..15] Register accumulating the number of detected double or illegal

transitions. ( SAMPLE = 2 ).


When this register has reached its maximum value the

accumulation of double / illegal transitions will stop. An

overflow event ( ACCOF ) will be generated if any double or

illegal transitions are detected after the maximum value was

reached. This field is cleared by triggering the READCLRACC or

RDCLRDBL task.


**36.7.17 ACCDBLREAD**

Address offset: 0x548

Snapshot of the ACCDBL, updated by the READCLRACC or RDCLRDBL task


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R ACCDBLREAD [0..15] Snapshot of the ACCDBL register. This field is updated when the

READCLRACC or RDCLRDBL task is triggered.

###### **36.8 Electrical specification**


**36.8.1 QDEC Electrical Specification**


**Symbol** **Description** **Min.** **Typ.** **Max.** **Units**

IQDEC Run current 5 µA

tSAMPLE Time between sampling signals from quadrature decoder 128 131072 µs

tLED Time from LED is turned on to signals are sampled 0 511 µs


**Page 360**


37 SAADC — Successive approximation analogto-digital converter

#### **37 SAADC — Successive approximation analog-to-** **digital converter**


The ADC is a differential successive approximation register (SAR) analog-to-digital converter.

Listed here are the main features of SAADC:

- 8/10/12-bit resolution, 14-bit resolution with oversampling

- Up to eight input channels

  - One channel per single-ended input and two channels per differential input

  - Scan mode can be configured with both single-ended channels and differential channels.

- Full scale input range (0 to VDD)

- Sampling triggered via a task from software or a PPI channel for full flexibility on sample frequency
source from low power 32.768kHz RTC or more accurate 1/16MHz Timers

- One-shot conversion mode to sample a single channel

- Scan mode to sample a series of channels in sequence. Sample delay between channels is tack + tconv
which may vary between channels according to user configuration of tack.

- Support for direct sample transfer to RAM using EasyDMA

- Interrupts on single sample and full buffer events

- Samples stored as 16-bit 2’s complement values for differential and single-ended sampling

- Continuous sampling without the need of an external timer

- Internal resistor string

- Limit checking on the fly

###### **37.1 Shared resources**

The ADC can coexist with COMP and other peripherals using one of `AIN0-AIN7`, provided these are
assigned to different pins.

It is not recommended to select the same analog input pin for both modules.

###### **37.2 Overview**

The ADC supports up to eight external analog input channels, depending on package variant. It can be
operated in a one-shot mode with sampling under software control, or a continuous conversion mode with a
programmable sampling rate.

The analog inputs can be configured as eight single-ended inputs, four differential inputs or a combination
of these. Each channel can be configured to select `AIN0` to `AIN7` pins, or the `VDD` pin. Channels can be
sampled individually in one-shot or continuous sampling modes, or, using scan mode, multiple channels can
be sampled in sequence. Channels can also be oversampled to improve noise performance.


**Page 361**


SAR
core


NC

AIN0
AIN1

AIN2
AIN3

AIN4
AIN5

AIN6
AIN7

VDD


ADC


RESP


RESN


CH[X].CONFIGPSEL_APSEL_APSEL_APSEL_APSEL_APSEL_A


GAIN


37 SAADC — Successive approximation analogto-digital converter


RAM


RESULT


RESULT


RESULT


EasyDMA


RESULT.PTR


RESULT


RESULT


RESULT


RESULT


RESULT


NC

AIN0
AIN1

AIN2
AIN3

AIN4
AIN5

AIN6
AIN7

VDD


CH[X].PSELPPSEL_APSEL_APSEL_APSEL_APSEL_APSEL_A


MUX


MUX


CH[X].PSELNPSEL_APSEL_APSEL_APSEL_APSEL_APSEL_A


**P**


**N**


START

SAMPLE

STOP


STARTED

END

STOPPED


VDD
REFSEL

Internal reference


**Figure 100: Simplified ADC block diagram**


Internally, the ADC is always a differential analog-to-digital converter, but by default it is configured with
single-ended input in the MODE field of the CH[n].CONFIG register. In single-ended mode, the negative
input will be shorted to ground internally.

The assumption in single-ended mode is that the internal ground of the ADC is the same as the external
ground that the measured voltage is referred to. The ADC is thus sensitive to ground bounce on the PCB in
single-ended mode. If this is a concern we recommend using differential measurement.

###### **37.3 Digital output**

The output result of the ADC depends on the settings in the CH[n].CONFIG and RESOLUTION registers as
follows:
```
 RESULT = [V(P) – V(N) ] * GAIN/REFERENCE * 2 [(RESOLUTION - m)]
```

where

**V(P)**
is the voltage at input P

**V(N)**
is the voltage at input N

**GAIN**
is the selected gain setting

**REFERENCE**
is the selected reference voltage

and m=0 if CONFIG.MODE=SE, or m=1 if CONFIG.MODE=Diff.

The result generated by the ADC will deviate from the expected due DC errors like offset, gain, differential
non-linearity (DNL), and integral non-linearity (INL). See _Electrical specification_ for details on these
parameters. The result can also vary due to AC errors like non-linearities in the GAIN block, settling errors
due to high source impedance and sampling jitter. For battery measurement the DC errors are most
noticeable.


**Page 362**


37 SAADC — Successive approximation analogto-digital converter


The ADC has a wide selection of gains controlled in the GAIN field of the CH[n].CONFIG register. If
CH[n].CONFIG.REFSEL=0, the input range of the ADC core is nominally ±0.6 V differential and the input
must be scaled accordingly.

The ADC has a temperature dependent offset. If the ADC is to operate over a large temperature range, we
recommend running CALIBRATEOFFSET at regular intervals, a CALIBRATEDONE event will be fired when
the calibration is complete

###### **37.4 Analog inputs and channels**

Up to eight analog input channels, CH[n](n=0..7), can be configured.

See _Shared resources_ on page 361 for shared input with comparators.

Any one of the available channels can be enabled for the ADC to operate in one-shot mode. If more than
one CH[n] is configured, the ADC enters scan mode.

An analog input is selected as a positive converter input if CH[n].PSELP is set, setting CH[n].PSELP also
enables the particular channel.

An analog input is selected as a negative converter input if CH[n].PSELN is set. The CH[n].PSELN register
will have no effect unless differential mode is enabled, see MODE field in CH[n].CONFIG register.

If more than one of the CH[n].PSELP registers is set, the device enters scan mode. Input selections in scan
mode are controlled by the CH[n].PSELP and CH[n].PSELN registers, where CH[n].PSELN is only used if
the particular scan channel is specified as differential, see MODE field in CH[n].CONFIG register.

**Important:** Channels selected for COMP cannot be used at the same time for ADC sampling, though
channels not selected for use by these blocks can be used by the ADC.


**Table 90: Legal connectivity CH[n] vs. analog input**


**Channel input** **Source** **Connectivity**
CH[n].PSELP AIN0…AIN7 Yes(any)
CH[n].PSELP VDD Yes
CH[n].PSELN AIN0…AIN7 Yes(any)
CH[n].PSELN VDD Yes

###### **37.5 Operation modes**

The ADC input configuration supports one-shot mode, continuous mode and scan mode.

Scan mode and oversampling cannot be combined.


**37.5.1 One-shot mode**
One-shot operation is configured by enabling only one of the available channels defined by CH[n].PSELP,
CH[n].PSELN, and CH[n].CONFIG registers.

Upon a SAMPLE task, the ADC starts to sample the input voltage. The CH[n].CONFIG.TACQ controls the
acquisition time.

A DONE event signals that one sample has been taken.

In this mode, the RESULTDONE event has the same meaning as DONE when no oversampling takes place.
Note that both events may occur before the actual value has been transferred into RAM by EasyDMA. For
more information, see _EasyDMA_ on page 365.


**37.5.2 Continuous mode**
Continuous sampling can be achieved by using the internal timer in the ADC, or triggering the SAMPLE task
from one of the general purpose timers through the PPI.

Care shall be taken to ensure that the sample rate fulfils the following criteria, depending on how many
channels are active:

`f` SAMPLE `< 1/[t` ACQ `+ t` conv `]`


**Page 363**


37 SAADC — Successive approximation analogto-digital converter


The SAMPLERATE register can be used as a local timer instead of triggering individual SAMPLE tasks.
When SAMPLERATE.MODE is set to Timers, it is sufficient to trigger SAMPLE task only once in order to
start the SAADC and triggering the STOP task will stop sampling. The SAMPLERATE.CC field controls the
sample rate.

The SAMPLERATE timer mode cannot be combined with SCAN mode, and only one channel can be
enabled in this mode.

A DONE event signals that one sample has been taken.

In this mode, the RESULTDONE event has the same meaning as DONE when no oversampling takes place.
Note that both events may occur before the actual value has been transferred into RAM by EasyDMA.


**37.5.3 Oversampling**
An accumulator in the ADC can be used to average noise on the analog input. In general, oversampling
improves the signal-to-noise ratio (SNR). Oversampling, however, does not improve the integral non-linearity
(INL), or differential non-linearity (DNL).

Oversampling and scan should not be combined, since oversampling and scan will average over input
channels.

The accumulator is controlled in the OVERSAMPLE register. The SAMPLE task must be set 2 [OVERSAMPLE]

number of times before the result is written to RAM. This can be achieved by:

- Configuring a fixed sampling rate using the local timer or a general purpose timer and PPI to trigger a
SAMPLE task

- Triggering SAMPLE 2 [OVERSAMPLE] times from software

- Enabling BURST mode

CH[n].CONFIG.BURST can be enabled to avoid setting SAMPLE task 2 [OVERSAMPLE] times. With
BURST = 1 the ADC will sample the input 2 [OVERSAMPLE] times as fast as it can (actual timing:
<(tACQ+tCONV)×2 [OVERSAMPLE] ). Thus, for the user it will just appear like the conversion took a bit longer time,
but other than that, it is similar to one-shot mode. Scan mode can be combined with BURST=1, if burst is
enabled on all channels.

A DONE event signals that one sample has been taken.

In this mode, the RESULTDONE event signals that enough conversions have taken place for an
oversampled result to get transferred into RAM. Note that both events may occur before the actual value has
been transferred into RAM by EasyDMA.


**37.5.4 Scan mode**
A channel is considered enabled if CH[n].PSELP is set. If more than one channel, CH[n], is enabled, the
ADC enters scan mode.

In scan mode, one SAMPLE task will trigger one conversion per enabled channel. The time it takes to
sample all channels is:

```
 Total time < Sum(CH[x].tACQ+tCONV), x=0..enabled channels
```

A DONE event signals that one sample has been taken.

In this mode, the RESULTDONE event signals has the same meaning as DONE when no oversampling
takes place. Note that both events may occur before the actual values have been transferred into RAM by
EasyDMA.

_Figure 101: Example of RAM placement (even RESULT.MAXCNT), channels 1, 2 and 5 enabled_ on page
365 provides an example of results placement in Data RAM, with an even RESULT.MAXCNT. In this
example, channels 1, 2 and 5 are enabled, all others are disabled.


**Page 364**



37 SAADC — Successive approximation analogto-digital converter


16 15 0

CH[2] 1 [st] result CH[1] 1 [st] result


RESULT.PTR


RESULT.PTR + 4 CH[1] 2 [nd] result CH[5] 1 [st] result


RESULT.PTR + 8 CH[5] 2 [nd] result CH[2] 2 [nd] result


(…)

RESULT.PTR + CH[5] last result CH[2] last result
2*(RESULT.MAXCNT – 2)


**Figure 101: Example of RAM placement (even RESULT.MAXCNT), channels 1, 2 and 5 enabled**


_Figure 102: Example of RAM placement (odd RESULT.MAXCNT), channels 1, 2 and 5 enabled_ on page
365 provides an example of results placement in Data RAM, with an odd RESULT.MAXCNT. In this
example, channels 1, 2 and 5 are enabled, all others are disabled. The last 32-bit word is populated only with
one 16-bit result.



16 15 0

CH[2] 1 [st] result CH[1] 1 [st] result


RESULT.PTR


RESULT.PTR + 4 CH[1] 2 [nd] result CH[5] 1 [st] result


RESULT.PTR + 8 CH[5] 2 [nd] result CH[2] 2 [nd] result


(…)

RESULT.PTR + CH[5] last result
2*(RESULT.MAXCNT – 1)


**Figure 102: Example of RAM placement (odd RESULT.MAXCNT), channels 1, 2 and 5 enabled**

###### **37.6 EasyDMA**

After configuring RESULT.PTR and RESULT.MAXCNT, the ADC resources are started by triggering the
START task. The ADC is using EasyDMA to store results in a Result buffer in RAM.

The Result buffer is located at the address specified in the RESULT.PTR register. The RESULT.PTR
register is double-buffered and it can be updated and prepared for the next START task immediately after
the STARTED event is generated. The size of the Result buffer is specified in the RESULT.MAXCNT register
and the ADC will generate an END event when it has filled up the Result buffer, see _Figure 103: ADC_ on
page 366. Results are stored in little-endian byte order in Data RAM. Every sample will be sign extended to
16 bit before stored in the Result buffer.

The ADC is stopped by triggering the STOP task. The STOP task will terminate an ongoing sampling. The
ADC will generate a STOPPED event when it has stopped. If the ADC is already stopped when the STOP
task is triggered, the STOPPED event will still be generated.


**Page 365**


37 SAADC — Successive approximation analogto-digital converter


Data RAM


Result 0

Result 1


Result 2

Result 3


0


0x20000000

0x20000002


0x20000010

0x20000012


0x20000020

0x20000022


~~Sample and convert  RAM~~


~~Sample and convert  RAM~~ ~~Sample and convert  RAM~~



~~Sample and convert  RAM~~




**Figure 103: ADC**


If the RESULT.PTR is not pointing to the Data RAM region, an EasyDMA transfer may result in a HardFault
or RAM corruption. See _Memory_ on page 24 for more information about the different memory regions.

The EasyDMA will have finished accessing the RAM when the END or STOPPED event has been
generated.

The RESULT.AMOUNT register can be read following an END event or a STOPPED event to see how many
results have been transferred to the Result buffer in RAM since the START task was triggered.

In Scan mode, the size of the Result buffer must be large enough to have room for a minimum one
result from each of the enabled channels. To secure this, RESULT.MAXCNT must be specified to
RESULT.MAXCNT >= "number of channels enabled". See _Scan mode_ on page 364 for more information
about Scan mode.

###### **37.7 Resistor ladder**

The ADC has an internal resistor string for positive and negative input.

See _Figure 104: Resistor ladder for positive input (negative input is equivalent, using RESN instead of_
_RESP)_ on page 367. The resistors are controlled in the CH[n].CONFIG.RESP and CH[n].CONFIG.RESN
registers.


**Page 366**


37 SAADC — Successive approximation analogto-digital converter


RESP = Pullup


R

Input Output


R


RESP = Pulldown


**Figure 104: Resistor ladder for positive input (negative input is equivalent, using RESN instead of**
**RESP)**

###### **37.8 Reference**

The ADC can use two different references, controlled in the REFSEL field of the CH[n].CONFIG register.

These are:

- Internal reference

- VDD as reference

The internal reference results in an input range of ±0.6 V on the ADC core. VDD as reference results in an
input range of ±VDD/4 on the ADC core. The gain block can be used to change the effective input range of
the ADC.

```
 Input range = (+- 0.6 V or +-VDD/4)/Gain
```

For example, choosing VDD as reference, single ended input (grounded negative input), and a gain of 1/4
the input range will be:

```
 Input range = (VDD/4)/(1/4) = VDD
```

With internal reference, single ended input (grounded negative input), and a gain of 1/6 the input range will
be:

```
 Input range = (0.6 V)/(1/6) = 3.6 V
```

The AIN0-AIN7 inputs cannot exceed VDD, or be lower than VSS.

###### **37.9 Acquisition time**

To sample the input voltage, the ADC connects a capacitor to the input.

For illustration, see _Figure 105: Simplified ADC sample network_ on page 368. The acquisition time
indicates how long the capacitor is connected, see TACQ field in CH[n].CONFIG register. The required
acquisition time depends on the source (Rsource) resistance. For high source resistance the acquisition time
should be increased, see _Table 91: Acquisition time_ on page 368.


**Page 367**


Rsource


**Figure 105: Simplified ADC sample network**


**Table 91: Acquisition time**


37 SAADC — Successive approximation analogto-digital converter


ADC


TACQ


**TACQ [µs]** **Maximum source resistance [kOhm]**
3 10
5 40
10 100
15 200
20 400
40 800

###### **37.10 Limits event monitoring**

A channel can be event monitored by configuring limit register CH[n].LIMIT.

If the conversion result is higher than the defined high limit, or lower than the defined low limit, the
appropriate event will get fired.


VIN


CH[n].LIMIT.HIGH


CH[n].LIMIT.LOW


t


events


**Figure 106: Example of limits monitoring on channel 'n'**


Note that when setting the limits, CH[n].LIMIT.HIGH shall always be higher than or equal to
CH[n].LIMIT.LOW . In other words, an event can be fired only when the input signal has been sampled


**Page 368**


37 SAADC — Successive approximation analogto-digital converter


outside of the defined limits. It is not possible to fire an event when the input signal is inside a defined range
by swapping high and low limits.

The comparison to limits always takes place, there is no need to enable it. If comparison is not required on a
channel, the software shall simply ignore the related events. In that situation, the value of the limits registers
is irrelevant, so it does not matter if CH[n].LIMIT.LOW is lower than CH[n].LIMIT.HIGH or not.

###### **37.11 Registers**


**Table 92: Instances**


**Base address** **Peripheral** **Instance** **Description** **Configuration**

0x40007000 SAADC SAADC Analog to digital converter


**Table 93: Register Overview**


**Register** **Offset** **Description**

TASKS_START 0x000 Start the ADC and prepare the result buffer in RAM

TASKS_SAMPLE 0x004 Take one ADC sample, if scan is enabled all channels are sampled

TASKS_STOP 0x008 Stop the ADC and terminate any on-going conversion

TASKS_CALIBRATEOFFSET0x00C Starts offset auto-calibration

EVENTS_STARTED 0x100 The ADC has started

EVENTS_END 0x104 The ADC has filled up the Result buffer

EVENTS_DONE 0x108 A conversion task has been completed. Depending on the mode, multiple conversions might be

needed for a result to be transferred to RAM.

EVENTS_RESULTDONE 0x10C A result is ready to get transferred to RAM.

EVENTS_CALIBRATEDONE0x110 Calibration is complete

EVENTS_STOPPED 0x114 The ADC has stopped

EVENTS_CH[0].LIMITH 0x118 Last results is equal or above CH[0].LIMIT.HIGH

EVENTS_CH[0].LIMITL 0x11C Last results is equal or below CH[0].LIMIT.LOW

EVENTS_CH[1].LIMITH 0x120 Last results is equal or above CH[1].LIMIT.HIGH

EVENTS_CH[1].LIMITL 0x124 Last results is equal or below CH[1].LIMIT.LOW

EVENTS_CH[2].LIMITH 0x128 Last results is equal or above CH[2].LIMIT.HIGH

EVENTS_CH[2].LIMITL 0x12C Last results is equal or below CH[2].LIMIT.LOW

EVENTS_CH[3].LIMITH 0x130 Last results is equal or above CH[3].LIMIT.HIGH

EVENTS_CH[3].LIMITL 0x134 Last results is equal or below CH[3].LIMIT.LOW

EVENTS_CH[4].LIMITH 0x138 Last results is equal or above CH[4].LIMIT.HIGH

EVENTS_CH[4].LIMITL 0x13C Last results is equal or below CH[4].LIMIT.LOW

EVENTS_CH[5].LIMITH 0x140 Last results is equal or above CH[5].LIMIT.HIGH

EVENTS_CH[5].LIMITL 0x144 Last results is equal or below CH[5].LIMIT.LOW

EVENTS_CH[6].LIMITH 0x148 Last results is equal or above CH[6].LIMIT.HIGH

EVENTS_CH[6].LIMITL 0x14C Last results is equal or below CH[6].LIMIT.LOW

EVENTS_CH[7].LIMITH 0x150 Last results is equal or above CH[7].LIMIT.HIGH

EVENTS_CH[7].LIMITL 0x154 Last results is equal or below CH[7].LIMIT.LOW

_INTEN_ 0x300 Enable or disable interrupt

_INTENSET_ 0x304 Enable interrupt

_INTENCLR_ 0x308 Disable interrupt

_STATUS_ 0x400 Status

_ENABLE_ 0x500 Enable or disable ADC

_CH[0].PSELP_ 0x510 Input positive pin selection for CH[0]

_CH[0].PSELN_ 0x514 Input negative pin selection for CH[0]

_CH[0].CONFIG_ 0x518 Input configuration for CH[0]

_CH[0].LIMIT_ 0x51C High/low limits for event monitoring a channel

_CH[1].PSELP_ 0x520 Input positive pin selection for CH[1]

_CH[1].PSELN_ 0x524 Input negative pin selection for CH[1]

_CH[1].CONFIG_ 0x528 Input configuration for CH[1]

_CH[1].LIMIT_ 0x52C High/low limits for event monitoring a channel

_CH[2].PSELP_ 0x530 Input positive pin selection for CH[2]


**Page 369**


37 SAADC — Successive approximation analogto-digital converter


**Register** **Offset** **Description**

_CH[2].PSELN_ 0x534 Input negative pin selection for CH[2]

_CH[2].CONFIG_ 0x538 Input configuration for CH[2]

_CH[2].LIMIT_ 0x53C High/low limits for event monitoring a channel

_CH[3].PSELP_ 0x540 Input positive pin selection for CH[3]

_CH[3].PSELN_ 0x544 Input negative pin selection for CH[3]

_CH[3].CONFIG_ 0x548 Input configuration for CH[3]

_CH[3].LIMIT_ 0x54C High/low limits for event monitoring a channel

_CH[4].PSELP_ 0x550 Input positive pin selection for CH[4]

_CH[4].PSELN_ 0x554 Input negative pin selection for CH[4]

_CH[4].CONFIG_ 0x558 Input configuration for CH[4]

_CH[4].LIMIT_ 0x55C High/low limits for event monitoring a channel

_CH[5].PSELP_ 0x560 Input positive pin selection for CH[5]

_CH[5].PSELN_ 0x564 Input negative pin selection for CH[5]

_CH[5].CONFIG_ 0x568 Input configuration for CH[5]

_CH[5].LIMIT_ 0x56C High/low limits for event monitoring a channel

_CH[6].PSELP_ 0x570 Input positive pin selection for CH[6]

_CH[6].PSELN_ 0x574 Input negative pin selection for CH[6]

_CH[6].CONFIG_ 0x578 Input configuration for CH[6]

_CH[6].LIMIT_ 0x57C High/low limits for event monitoring a channel

_CH[7].PSELP_ 0x580 Input positive pin selection for CH[7]

_CH[7].PSELN_ 0x584 Input negative pin selection for CH[7]

_CH[7].CONFIG_ 0x588 Input configuration for CH[7]

_CH[7].LIMIT_ 0x58C High/low limits for event monitoring a channel

_RESOLUTION_ 0x5F0 Resolution configuration

_OVERSAMPLE_ 0x5F4 Oversampling configuration. OVERSAMPLE should not be combined with SCAN. The RESOLUTION is

applied before averaging, thus for high OVERSAMPLE a higher RESOLUTION should be used.

_SAMPLERATE_ 0x5F8 Controls normal or continuous sample rate

_RESULT.PTR_ 0x62C Data pointer

_RESULT.MAXCNT_ 0x630 Maximum number of buffer words to transfer

_RESULT.AMOUNT_ 0x634 Number of buffer words transferred since last START


**37.11.1 INTEN**

Address offset: 0x300

Enable or disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STARTED Enable or disable interrupt for STARTED event


See _EVENTS_STARTED_

Disabled 0 Disable

Enabled 1 Enable

B RW END Enable or disable interrupt for END event


See _EVENTS_END_

Disabled 0 Disable

Enabled 1 Enable

C RW DONE Enable or disable interrupt for DONE event


See _EVENTS_DONE_

Disabled 0 Disable

Enabled 1 Enable

D RW RESULTDONE Enable or disable interrupt for RESULTDONE event


See _EVENTS_RESULTDONE_

Disabled 0 Disable

Enabled 1 Enable


**Page 370**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

E RW CALIBRATEDONE Enable or disable interrupt for CALIBRATEDONE event


See _EVENTS_CALIBRATEDONE_

Disabled 0 Disable

Enabled 1 Enable

F RW STOPPED Enable or disable interrupt for STOPPED event


See _EVENTS_STOPPED_

Disabled 0 Disable

Enabled 1 Enable

G RW CH0LIMITH Enable or disable interrupt for CH[0].LIMITH event


See _EVENTS_CH[0].LIMITH_

Disabled 0 Disable

Enabled 1 Enable

H RW CH0LIMITL Enable or disable interrupt for CH[0].LIMITL event


See _EVENTS_CH[0].LIMITL_

Disabled 0 Disable

Enabled 1 Enable

I RW CH1LIMITH Enable or disable interrupt for CH[1].LIMITH event


See _EVENTS_CH[1].LIMITH_

Disabled 0 Disable

Enabled 1 Enable

J RW CH1LIMITL Enable or disable interrupt for CH[1].LIMITL event


See _EVENTS_CH[1].LIMITL_

Disabled 0 Disable

Enabled 1 Enable

K RW CH2LIMITH Enable or disable interrupt for CH[2].LIMITH event


See _EVENTS_CH[2].LIMITH_

Disabled 0 Disable

Enabled 1 Enable

L RW CH2LIMITL Enable or disable interrupt for CH[2].LIMITL event


See _EVENTS_CH[2].LIMITL_

Disabled 0 Disable

Enabled 1 Enable

M RW CH3LIMITH Enable or disable interrupt for CH[3].LIMITH event


See _EVENTS_CH[3].LIMITH_

Disabled 0 Disable

Enabled 1 Enable

N RW CH3LIMITL Enable or disable interrupt for CH[3].LIMITL event


See _EVENTS_CH[3].LIMITL_

Disabled 0 Disable

Enabled 1 Enable

O RW CH4LIMITH Enable or disable interrupt for CH[4].LIMITH event


See _EVENTS_CH[4].LIMITH_

Disabled 0 Disable

Enabled 1 Enable

P RW CH4LIMITL Enable or disable interrupt for CH[4].LIMITL event


See _EVENTS_CH[4].LIMITL_

Disabled 0 Disable

Enabled 1 Enable

Q RW CH5LIMITH Enable or disable interrupt for CH[5].LIMITH event


See _EVENTS_CH[5].LIMITH_


**Page 371**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Disable

Enabled 1 Enable

R RW CH5LIMITL Enable or disable interrupt for CH[5].LIMITL event


See _EVENTS_CH[5].LIMITL_

Disabled 0 Disable

Enabled 1 Enable

S RW CH6LIMITH Enable or disable interrupt for CH[6].LIMITH event


See _EVENTS_CH[6].LIMITH_

Disabled 0 Disable

Enabled 1 Enable

T RW CH6LIMITL Enable or disable interrupt for CH[6].LIMITL event


See _EVENTS_CH[6].LIMITL_

Disabled 0 Disable

Enabled 1 Enable

U RW CH7LIMITH Enable or disable interrupt for CH[7].LIMITH event


See _EVENTS_CH[7].LIMITH_

Disabled 0 Disable

Enabled 1 Enable

V RW CH7LIMITL Enable or disable interrupt for CH[7].LIMITL event


See _EVENTS_CH[7].LIMITL_

Disabled 0 Disable

Enabled 1 Enable


**37.11.2 INTENSET**

Address offset: 0x304

Enable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STARTED Write '1' to Enable interrupt for STARTED event


See _EVENTS_STARTED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW END Write '1' to Enable interrupt for END event


See _EVENTS_END_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW DONE Write '1' to Enable interrupt for DONE event


See _EVENTS_DONE_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW RESULTDONE Write '1' to Enable interrupt for RESULTDONE event


See _EVENTS_RESULTDONE_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**Page 372**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

E RW CALIBRATEDONE Write '1' to Enable interrupt for CALIBRATEDONE event


See _EVENTS_CALIBRATEDONE_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW STOPPED Write '1' to Enable interrupt for STOPPED event


See _EVENTS_STOPPED_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW CH0LIMITH Write '1' to Enable interrupt for CH[0].LIMITH event


See _EVENTS_CH[0].LIMITH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW CH0LIMITL Write '1' to Enable interrupt for CH[0].LIMITL event


See _EVENTS_CH[0].LIMITL_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW CH1LIMITH Write '1' to Enable interrupt for CH[1].LIMITH event


See _EVENTS_CH[1].LIMITH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

J RW CH1LIMITL Write '1' to Enable interrupt for CH[1].LIMITL event


See _EVENTS_CH[1].LIMITL_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

K RW CH2LIMITH Write '1' to Enable interrupt for CH[2].LIMITH event


See _EVENTS_CH[2].LIMITH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

L RW CH2LIMITL Write '1' to Enable interrupt for CH[2].LIMITL event


See _EVENTS_CH[2].LIMITL_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

M RW CH3LIMITH Write '1' to Enable interrupt for CH[3].LIMITH event


See _EVENTS_CH[3].LIMITH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

N RW CH3LIMITL Write '1' to Enable interrupt for CH[3].LIMITL event


See _EVENTS_CH[3].LIMITL_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

O RW CH4LIMITH Write '1' to Enable interrupt for CH[4].LIMITH event


**Page 373**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

See _EVENTS_CH[4].LIMITH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

P RW CH4LIMITL Write '1' to Enable interrupt for CH[4].LIMITL event


See _EVENTS_CH[4].LIMITL_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

Q RW CH5LIMITH Write '1' to Enable interrupt for CH[5].LIMITH event


See _EVENTS_CH[5].LIMITH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

R RW CH5LIMITL Write '1' to Enable interrupt for CH[5].LIMITL event


See _EVENTS_CH[5].LIMITL_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

S RW CH6LIMITH Write '1' to Enable interrupt for CH[6].LIMITH event


See _EVENTS_CH[6].LIMITH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

T RW CH6LIMITL Write '1' to Enable interrupt for CH[6].LIMITL event


See _EVENTS_CH[6].LIMITL_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

U RW CH7LIMITH Write '1' to Enable interrupt for CH[7].LIMITH event


See _EVENTS_CH[7].LIMITH_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

V RW CH7LIMITL Write '1' to Enable interrupt for CH[7].LIMITL event


See _EVENTS_CH[7].LIMITL_

Set 1 Enable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**37.11.3 INTENCLR**

Address offset: 0x308

Disable interrupt


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW STARTED Write '1' to Disable interrupt for STARTED event


See _EVENTS_STARTED_

Clear 1 Disable


**Page 374**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

B RW END Write '1' to Disable interrupt for END event


See _EVENTS_END_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

C RW DONE Write '1' to Disable interrupt for DONE event


See _EVENTS_DONE_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

D RW RESULTDONE Write '1' to Disable interrupt for RESULTDONE event


See _EVENTS_RESULTDONE_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

E RW CALIBRATEDONE Write '1' to Disable interrupt for CALIBRATEDONE event


See _EVENTS_CALIBRATEDONE_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

F RW STOPPED Write '1' to Disable interrupt for STOPPED event


See _EVENTS_STOPPED_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

G RW CH0LIMITH Write '1' to Disable interrupt for CH[0].LIMITH event


See _EVENTS_CH[0].LIMITH_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

H RW CH0LIMITL Write '1' to Disable interrupt for CH[0].LIMITL event


See _EVENTS_CH[0].LIMITL_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

I RW CH1LIMITH Write '1' to Disable interrupt for CH[1].LIMITH event


See _EVENTS_CH[1].LIMITH_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

J RW CH1LIMITL Write '1' to Disable interrupt for CH[1].LIMITL event


See _EVENTS_CH[1].LIMITL_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

K RW CH2LIMITH Write '1' to Disable interrupt for CH[2].LIMITH event


See _EVENTS_CH[2].LIMITH_

Clear 1 Disable

Disabled 0 Read: Disabled


**Page 375**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Read: Enabled

L RW CH2LIMITL Write '1' to Disable interrupt for CH[2].LIMITL event


See _EVENTS_CH[2].LIMITL_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

M RW CH3LIMITH Write '1' to Disable interrupt for CH[3].LIMITH event


See _EVENTS_CH[3].LIMITH_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

N RW CH3LIMITL Write '1' to Disable interrupt for CH[3].LIMITL event


See _EVENTS_CH[3].LIMITL_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

O RW CH4LIMITH Write '1' to Disable interrupt for CH[4].LIMITH event


See _EVENTS_CH[4].LIMITH_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

P RW CH4LIMITL Write '1' to Disable interrupt for CH[4].LIMITL event


See _EVENTS_CH[4].LIMITL_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

Q RW CH5LIMITH Write '1' to Disable interrupt for CH[5].LIMITH event


See _EVENTS_CH[5].LIMITH_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

R RW CH5LIMITL Write '1' to Disable interrupt for CH[5].LIMITL event


See _EVENTS_CH[5].LIMITL_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

S RW CH6LIMITH Write '1' to Disable interrupt for CH[6].LIMITH event


See _EVENTS_CH[6].LIMITH_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

T RW CH6LIMITL Write '1' to Disable interrupt for CH[6].LIMITL event


See _EVENTS_CH[6].LIMITL_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled

U RW CH7LIMITH Write '1' to Disable interrupt for CH[7].LIMITH event


See _EVENTS_CH[7].LIMITH_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**Page 376**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id V U T S R Q P O N M L K J I H G F E D C B A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

V RW CH7LIMITL Write '1' to Disable interrupt for CH[7].LIMITL event


See _EVENTS_CH[7].LIMITL_

Clear 1 Disable

Disabled 0 Read: Disabled

Enabled 1 Read: Enabled


**37.11.4 STATUS**

Address offset: 0x400

Status


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A R STATUS Status

Ready 0 ADC is ready. No on-going conversion.

Busy 1 ADC is busy. Conversion in progress.


**37.11.5 ENABLE**

Address offset: 0x500

Enable or disable ADC


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW ENABLE Enable or disable ADC

Disabled 0 Disable ADC

Enabled 1 Enable ADC


When enabled, the ADC will acquire access to the analog input

pins specified in the CH[n].PSELP and CH[n].PSELN registers.


**37.11.6 CH[0].PSELP**

Address offset: 0x510

Input positive pin selection for CH[0]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELP Analog positive input channel

NC 0 Not connected

AnalogInput0 1 AIN0

AnalogInput1 2 AIN1

AnalogInput2 3 AIN2

AnalogInput3 4 AIN3

AnalogInput4 5 AIN4

AnalogInput5 6 AIN5

AnalogInput6 7 AIN6

AnalogInput7 8 AIN7

VDD 9 VDD


**Page 377**


37 SAADC — Successive approximation analogto-digital converter


**37.11.7 CH[0].PSELN**

Address offset: 0x514

Input negative pin selection for CH[0]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELN Analog negative input, enables differential channel

NC 0 Not connected

AnalogInput0 1 AIN0

AnalogInput1 2 AIN1

AnalogInput2 3 AIN2

AnalogInput3 4 AIN3

AnalogInput4 5 AIN4

AnalogInput5 6 AIN5

AnalogInput6 7 AIN6

AnalogInput7 8 AIN7

VDD 9 VDD


**37.11.8 CH[0].CONFIG**

Address offset: 0x518

Input configuration for CH[0]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id G F E E E D C C C B B A A

**Reset 0x00020000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW RESP Positive channel resistor control

Bypass 0 Bypass resistor ladder

Pulldown 1 Pull-down to GND

Pullup 2 Pull-up to VDD

VDD1_2 3 Set input at VDD/2

B RW RESN Negative channel resistor control

Bypass 0 Bypass resistor ladder

Pulldown 1 Pull-down to GND

Pullup 2 Pull-up to VDD

VDD1_2 3 Set input at VDD/2

C RW GAIN Gain control

Gain1_6 0 1/6

Gain1_5 1 1/5

Gain1_4 2 1/4

Gain1_3 3 1/3

Gain1_2 4 1/2

Gain1 5 1

Gain2 6 2

Gain4 7 4

D RW REFSEL Reference control

Internal 0 Internal reference (0.6 V)

VDD1_4 1 VDD/4 as reference

E RW TACQ Acquisition time, the time the ADC uses to sample the input

voltage

3us 0 3 us

5us 1 5 us

10us 2 10 us

15us 3 15 us

20us 4 20 us


**Page 378**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id G F E E E D C C C B B A A

**Reset 0x00020000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

40us 5 40 us

F RW MODE Enable differential mode

SE 0 Single ended, PSELN will be ignored, negative input to ADC

shorted to GND

Diff 1 Differential

G RW BURST Enable burst mode

Disabled 0 Burst mode is disabled (normal operation)

Enabled 1 Burst mode is enabled. SAADC takes 2^OVERSAMPLE number of

samples as fast as it can, and sends the average to Data RAM.


**37.11.9 CH[0].LIMIT**

Address offset: 0x51C

High/low limits for event monitoring a channel


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B B B B B B B B B B B B B B B B A A A A A A A A A A A A A A A A

**Reset 0x7FFF8000** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LOW [-32768 to +32767] Low level limit

B RW HIGH [-32768 to +32767] High level limit


**37.11.10 CH[1].PSELP**

Address offset: 0x520

Input positive pin selection for CH[1]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELP Analog positive input channel

NC 0 Not connected

AnalogInput0 1 AIN0

AnalogInput1 2 AIN1

AnalogInput2 3 AIN2

AnalogInput3 4 AIN3

AnalogInput4 5 AIN4

AnalogInput5 6 AIN5

AnalogInput6 7 AIN6

AnalogInput7 8 AIN7

VDD 9 VDD


**37.11.11 CH[1].PSELN**

Address offset: 0x524

Input negative pin selection for CH[1]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELN Analog negative input, enables differential channel

NC 0 Not connected

AnalogInput0 1 AIN0


**Page 379**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

AnalogInput1 2 AIN1

AnalogInput2 3 AIN2

AnalogInput3 4 AIN3

AnalogInput4 5 AIN4

AnalogInput5 6 AIN5

AnalogInput6 7 AIN6

AnalogInput7 8 AIN7

VDD 9 VDD


**37.11.12 CH[1].CONFIG**

Address offset: 0x528

Input configuration for CH[1]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id G F E E E D C C C B B A A

**Reset 0x00020000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW RESP Positive channel resistor control

Bypass 0 Bypass resistor ladder

Pulldown 1 Pull-down to GND

Pullup 2 Pull-up to VDD

VDD1_2 3 Set input at VDD/2

B RW RESN Negative channel resistor control

Bypass 0 Bypass resistor ladder

Pulldown 1 Pull-down to GND

Pullup 2 Pull-up to VDD

VDD1_2 3 Set input at VDD/2

C RW GAIN Gain control

Gain1_6 0 1/6

Gain1_5 1 1/5

Gain1_4 2 1/4

Gain1_3 3 1/3

Gain1_2 4 1/2

Gain1 5 1

Gain2 6 2

Gain4 7 4

D RW REFSEL Reference control

Internal 0 Internal reference (0.6 V)

VDD1_4 1 VDD/4 as reference

E RW TACQ Acquisition time, the time the ADC uses to sample the input

voltage

3us 0 3 us

5us 1 5 us

10us 2 10 us

15us 3 15 us

20us 4 20 us

40us 5 40 us

F RW MODE Enable differential mode

SE 0 Single ended, PSELN will be ignored, negative input to ADC

shorted to GND

Diff 1 Differential

G RW BURST Enable burst mode

Disabled 0 Burst mode is disabled (normal operation)


**Page 380**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id G F E E E D C C C B B A A

**Reset 0x00020000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

Enabled 1 Burst mode is enabled. SAADC takes 2^OVERSAMPLE number of

samples as fast as it can, and sends the average to Data RAM.


**37.11.13 CH[1].LIMIT**

Address offset: 0x52C

High/low limits for event monitoring a channel


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B B B B B B B B B B B B B B B B A A A A A A A A A A A A A A A A

**Reset 0x7FFF8000** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LOW [-32768 to +32767] Low level limit

B RW HIGH [-32768 to +32767] High level limit


**37.11.14 CH[2].PSELP**

Address offset: 0x530

Input positive pin selection for CH[2]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELP Analog positive input channel

NC 0 Not connected

AnalogInput0 1 AIN0

AnalogInput1 2 AIN1

AnalogInput2 3 AIN2

AnalogInput3 4 AIN3

AnalogInput4 5 AIN4

AnalogInput5 6 AIN5

AnalogInput6 7 AIN6

AnalogInput7 8 AIN7

VDD 9 VDD


**37.11.15 CH[2].PSELN**

Address offset: 0x534

Input negative pin selection for CH[2]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELN Analog negative input, enables differential channel

NC 0 Not connected

AnalogInput0 1 AIN0

AnalogInput1 2 AIN1

AnalogInput2 3 AIN2

AnalogInput3 4 AIN3

AnalogInput4 5 AIN4

AnalogInput5 6 AIN5

AnalogInput6 7 AIN6

AnalogInput7 8 AIN7


**Page 381**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

VDD 9 VDD


**37.11.16 CH[2].CONFIG**

Address offset: 0x538

Input configuration for CH[2]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id G F E E E D C C C B B A A

**Reset 0x00020000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW RESP Positive channel resistor control

Bypass 0 Bypass resistor ladder

Pulldown 1 Pull-down to GND

Pullup 2 Pull-up to VDD

VDD1_2 3 Set input at VDD/2

B RW RESN Negative channel resistor control

Bypass 0 Bypass resistor ladder

Pulldown 1 Pull-down to GND

Pullup 2 Pull-up to VDD

VDD1_2 3 Set input at VDD/2

C RW GAIN Gain control

Gain1_6 0 1/6

Gain1_5 1 1/5

Gain1_4 2 1/4

Gain1_3 3 1/3

Gain1_2 4 1/2

Gain1 5 1

Gain2 6 2

Gain4 7 4

D RW REFSEL Reference control

Internal 0 Internal reference (0.6 V)

VDD1_4 1 VDD/4 as reference

E RW TACQ Acquisition time, the time the ADC uses to sample the input

voltage

3us 0 3 us

5us 1 5 us

10us 2 10 us

15us 3 15 us

20us 4 20 us

40us 5 40 us

F RW MODE Enable differential mode

SE 0 Single ended, PSELN will be ignored, negative input to ADC

shorted to GND

Diff 1 Differential

G RW BURST Enable burst mode

Disabled 0 Burst mode is disabled (normal operation)

Enabled 1 Burst mode is enabled. SAADC takes 2^OVERSAMPLE number of

samples as fast as it can, and sends the average to Data RAM.


**37.11.17 CH[2].LIMIT**

Address offset: 0x53C

High/low limits for event monitoring a channel


**Page 382**


37 SAADC — Successive approximation analogto-digital converter


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id B B B B B B B B B B B B B B B B A A A A A A A A A A A A A A A A

**Reset 0x7FFF8000** **0** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW LOW [-32768 to +32767] Low level limit

B RW HIGH [-32768 to +32767] High level limit


**37.11.18 CH[3].PSELP**

Address offset: 0x540

Input positive pin selection for CH[3]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELP Analog positive input channel

NC 0 Not connected

AnalogInput0 1 AIN0

AnalogInput1 2 AIN1

AnalogInput2 3 AIN2

AnalogInput3 4 AIN3

AnalogInput4 5 AIN4

AnalogInput5 6 AIN5

AnalogInput6 7 AIN6

AnalogInput7 8 AIN7

VDD 9 VDD


**37.11.19 CH[3].PSELN**

Address offset: 0x544

Input negative pin selection for CH[3]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id A A A A A

**Reset 0x00000000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW PSELN Analog negative input, enables differential channel

NC 0 Not connected

AnalogInput0 1 AIN0

AnalogInput1 2 AIN1

AnalogInput2 3 AIN2

AnalogInput3 4 AIN3

AnalogInput4 5 AIN4

AnalogInput5 6 AIN5

AnalogInput6 7 AIN6

AnalogInput7 8 AIN7

VDD 9 VDD


**37.11.20 CH[3].CONFIG**

Address offset: 0x548

Input configuration for CH[3]


Bit number 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0

Id G F E E E D C C C B B A A

**Reset 0x00020000** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **1** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0** **0**

**Id** **RW** **Field** **Value Id** **Value** **Description**

A RW RESP Positive channel resistor control


**Page 383**


37 SAADC — Successive approximation ana

[Truncated at ~229986 tokens]
