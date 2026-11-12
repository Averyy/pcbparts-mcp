Source: https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf
Retrieved: 2026-11-09

[Upgraded from PDF to HTML datasheet]

# SCES351 Data sheet | TI.com

Data Sheet

# SN74LVC1G17 Single Schmitt-Trigger Buffer

# 1 Features

- Available in ultra small 0.64mm2
  package (DPW) with 0.5mm pitch
- Supports 5V VCC operation
- Inputs accept voltages to 5.5V
- Maximum tpd of 4.6ns at 3.3V
- Low power consumption, 10μA maximum
  ICC
- ±24mA output drive at 3.3V
- Ioff supports live insertion,
  partial-power-down mode, and back-drive protection
- Latch-up performance exceeds 100mA per JESD 78,
  Class II
- ESD protection exceeds JESD 22
  - 2000V human-body model
    (A114A)
  - 200V machine model
    (A115A)
  - 1000V charged-device
    model (C101)

# 2 Applications

- AV receiver
- Audio dock: portable
- Blu-ray player and home theater
- MP3 player/recorder
- Personal Digital Assistant (PDA)
- Power: telecom/server AC/DC supply: single
  controller: analog and digital
- Solid State Drive (SSD): client and
  enterprise
- TV: LCD/Digital and High-Definition (HDTV)
- Tablet: enterprise
- Video analytics: server
- Wireless headset, keyboard, and mouse

# 3 Description

This single Schmitt-trigger buffer is designed for 1.65V to 5.5V VCC operation.

The SN74LVC1G17 device contains one buffer and performs the Boolean function Y = A.

The CMOS device has high output drive while maintaining low static power dissipation over a broad VCC operating range.

The SN74LVC1G17 is available in a variety of packages, including the ultra-small DPW package with a body size of 0.8mm × 0.8mm.

Package Information

| DEVICE NAME | PACKAGE[(1)](#SCES2121815_li:1;1:8160) | PACKAGE SIZE[(2)](#GUID-D33D613C-8335-43AF-90F6-579F7E6155E2_li:2;1:8489) | BODY SIZE[(3)](#GUID-C325AC05-2E02-4184-8DD8-288D5DCF98E4_li:3;1:8654) |
| --- | --- | --- | --- |
| SN74LVC1G17 | DBV (SOT-23, 5) | 2.9mm × 2.8mm | 2.9mm × 1.6mm |
| DRL (SOT-5X3, 5) | 1.6mm × 1.6mm | 1.6mm × 1.2mm |
| DCK (SC70, 5) | 2.0mm × 2.1mm | 2.0mm × 1.25mm |
| DPW (X2SON, 5) | 0.8mm × 0.8mm | 0.8mm × 0.8mm |
| DRY (USON, 6) | 1.45mm × 1mm | 1.45mm × 1.0mm |
| DSF (X2SON, 6) | 1.0mm × 1.0mm | 1.0mm × 1.0mm |
| YZP (DSBGA, 5) | 1.75mm × 1.25mm | 1.75mm × 1.25mm |
| YZV (DSBGA, 4) | 1.25mm × 1.25mm | 1.25mm × 1.25mm |

(1) For all available packages, see [Mechanical, Packaging, and Orderable Information](GUID-C940274C-2DE4-4F19-BBBF-B27E4C77106A.html#TITLE-SCES351IMPNOTE).

(2) The package size (length × width) is a nominal value and includes pins, where applicable.

(3) The body size (length × width) is a nominal value and does not include pins.

![SN74LVC1G17 Functional Block
                        Diagram](https://www.ti.com/ods/images/SCES351Y/GUID-BA05E519-53FC-4C1A-9530-0F8F5FB723E5-low.gif "SN74LVC1G17 Functional Block
                        Diagram")Functional Block
Diagram

# 4 Pin Configuration and Functions

![SN74LVC1G17 ](https://www.ti.com/ods/images/SCES351Y/GUID-A94E4681-0415-444B-813E-DA345ADD53C0-low.gif)

Pin Functions

| PIN | | | | | DESCRIPTION |
| --- | --- | --- | --- | --- | --- |
| NAME | DBV, DCK, DRL, DPW | DRY, DSF | YZP | YZV |
| NC | 1 | 1, 5 | A1, B2 | – | Not connected |
| A | 2 | 2 | B1 | A1 | Input |
| GND | 3 | 3 | C1 | B1 | Ground |
| Y | 4 | 4 | C2 | B2 | Output |
| VCC | 5 | 6 | A2 | A2 | Power terminal |

# 5 Specifications

## 5.1 Absolute Maximum Ratings

over operating free-air temperature range (unless
otherwise noted)[(1)](#SCES424121901_li:1;107:160)

|  |  | | MIN | MAX | UNIT |
| --- | --- | --- | --- | --- | --- |
| VCC | Supply voltage range | | –0.5 | 6.5 | V |
| VI | Input voltage range[(2)](#SCES424121902_li:2;113:129) | | –0.5 | 6.5 | V |
| VO | Voltage range applied to any output in the high-impedance or power-off state[(2)](#SCES424121902_li:2;113:129) | | –0.5 | 6.5 | V |
| VO | Voltage range applied to any output in the high or low state[(2)](#SCES424121902_li:2;113:129)[(3)](#SCES424121903_li:3;113:292) | | –0.5 | VCC + 0.5 | V |
| IIK | Input clamp current | VI < 0 |  | –50 | mA |
| IOK | Output clamp current | VO < 0 |  | –50 | mA |
| IO | Continuous output current |  |  | ±50 | mA |
|  | Continuous current through VCC or GND |  |  | ±100 | mA |
| Tstg | Storage temperature range |  | –65 | 150 | °C |

(1) Operation outside the *Absolute Maximum Ratings* may cause permanent
device damage. *Absolute Maximum Ratings* do not imply functional operation
of the device at these or any other conditions beyond those listed under
*Recommended Operating Conditions*. If used outside the *Recommended
Operating Conditions* but within the *Absolute Maximum Ratings*, the
device may not be fully functional, and this may affect device reliability,
functionality, performance, and shorten the device lifetime.

(2) The input and output negative-voltage ratings may be exceeded if the input and output current ratings are observed.

(3) The value of VCC is provided in the *Recommended Operating Conditions* table.

## 5.2 ESD Ratings

|  | | | VALUE | UNIT |
| --- | --- | --- | --- | --- |
| V(ESD) [(1)](#SCES3513302_li:1;34:379) | Electrostatic discharge | Human body model (HBM), per ANSI/ESDA/JEDEC JS-001[(2)](#SCES3517854_li:2;34:574) | ±2000 | V |
| Charged device model (CDM), per JEDEC specification JESD22-C101[(3)](#SCES3518873_li:3;34:726) | ±1000 | V |

(1) Electrostatic discharge (ESD) to measure device sensitivity and immunity to damage caused by assembly line electrostatic discharges in to the device.

(2) JEDEC document JEP155 states that 500V HBM allows safe manufacturing with a standard ESD control process.

(3) JEDEC document JEP157 states that 250V CDM allows safe manufacturing with a standard ESD control process

## 5.3 Recommended Operating Conditions

See [(1)](#IDA0WN0B_li:1;6:1655)

|  | | | MIN | MAX | UNIT |
| --- | --- | --- | --- | --- | --- |
| VCC | Supply voltage | Operating | 1.65 | 5.5 | V |
| Data retention only | 1.5 |  |
| VI | Input voltage |  | 0 | 5.5 | V |
| VO | Output voltage |  | 0 | VCC | V |
| IOH | High-level output current | VCC = 1.65V |  | –4 | mA |
| VCC = 2.3V |  | –8 |
| VCC = 3V |  | –16 |
|  | –24 |
| VCC = 4.5V |  | –32 |
| IOL | Low-level output current | VCC = 1.65V |  | 4 | mA |
| VCC = 2.3V |  | 8 |
| VCC = 3V |  | 16 |
|  | 24 |
| VCC = 4.5V |  | 32 |
| TA | Operating free-air temperature | | –40 | 125 | °C |

(1) All unused inputs of the device must be held at VCC or GND to ensure
proper device operation. Refer to the [*Implications of Slow or Floating
CMOS Inputs*](https://www.ti.com/lit/pdf/SCBA004) application note.

## 5.4 Thermal Information

| THERMAL METRIC[(1)](#APPNOTE_SPRA953_li:1;75:10027) | | SN74LVC1G17 | | | | | | | UNIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DBV | DCK | DRL | DRY | YZP | DPW | YZV |
| 5 PINS | 5 PINS | 5 PINS | 6 PINS | 5 PINS | 4 PINS | 4 PINS |
| RθJA | Junction-to-ambient thermal resistance | 357.1 | 371.0 | 350 | 608 | 130 | 340 | 181 | °C/W |
| RθJC(top) | Junction-to-case (top) thermal resistance | 263.7 | 297.5 | 121 | 432 | 54 | 215 | 1 |
| RθJB | Junction-to-board thermal resistance | 264.4 | 258.6 | 171 | 446 | 51 | 294 | 39 |
| ψJT | Junction-to-top characterization parameter | 195.6 | 195.6 | 11 | 191 | 1 | 41 | 8 |
| ψJB | Junction-to-board characterization parameter | 262.2 | 256.2 | 169 | 442 | 50 | 294 | 38 |
| RθJC(bot) | Junction-to-case (bottom) thermal resistance | – | – | – | 198 | – | 250 | – |

(1) For more information about traditional and new thermal metrics, see the
[*Semiconductor and IC Package Thermal Metrics*](https://www.ti.com/lit/pdf/spra953) application
note.

## 5.5 Electrical Characteristics—DC Limit Changes

Table 5-1 DC Limit Changes over recommended operating free-air temperature range (unless otherwise noted)

| PARAMETER | | | TEST CONDITIONS | | | VCC | 25°C | | | –40°C TO 85°C | | | –40°C TO 125°C | | | UNIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MIN | TYP[(1)](#SCES223121201_li:1;22:2929) | MAX | MIN | TYP[(1)](#SCES223121201_li:1;22:2929) | MAX | MIN | TYP | MAX |
| VT+   (Positive-going input threshold voltage) | | |  | | | 1.65V |  |  |  | 0.76 |  | 1.13 | 0.76 |  | 1.13 | V |
| 2.3V |  |  |  | 1.08 |  | 1.56 | 1.08 |  | 1.56 |
| 3V |  |  |  | 1.48 |  | 1.92 | 1.48 |  | 1.92 |
| 4.5V |  |  |  | 2.19 |  | 2.74 | 2.19 |  | 2.74 |
| 5.5V |  |  |  | 2.65 |  | 3.33 | 2.65 |  | 3.33 |
| VT–   (Negative-going input threshold voltage) | | |  | | | 1.65V |  |  |  | 0.35 |  | 0.59 | 0.35 |  | 0.59 | V |
| 2.3V |  |  |  | 0.56 |  | 0.88 | 0.56 |  | 0.88 |
| 3V |  |  |  | 0.89 |  | 1.2 | 0.89 |  | 1.2 |
| 4.5V |  |  |  | 1.51 |  | 1.97 | 1.51 |  | 1.97 |
| 5.5V |  |  |  | 1.88 |  | 2.4 | 1.88 |  | 2.4 |
| ΔVT  Hysteresis  (VT+ – VT–) | | |  | | | 1.65V |  |  |  | 0.36 |  | 0.64 | 0.36 |  | 0.64 | V |
| 2.3V |  |  |  | 0.45 |  | 0.78 | 0.45 |  | 0.78 |
| 3V |  |  |  | 0.51 |  | 0.83 | 0.51 |  | 0.83 |
| 4.5V |  |  |  | 0.58 |  | 0.93 | 0.58 |  | 0.93 |
| 5.5V |  |  |  | 0.69 |  | 1.04 | 0.69 |  | 1.04 |
| VOH | | | IOH = –100μA | | | 1.65V to 5.5V |  |  |  | VCC – 0.1 |  |  | VCC – 0.1 |  |  | V |
| IOH = –4mA | | | 1.65V |  |  |  | 1.2 |  |  | 1.2 |  |  |
| IOH = –8mA | | | 2.3V |  |  |  | 1.9 |  |  | 1.9 |  |  |
| IOH = –16mA | | | 3V |  |  |  | 2.4 |  |  | 2.4 |  |  |
| IOH = –24mA | | |  |  |  | 2.3 |  |  | 2.3 |  |  |
| IOH = –32mA | | | 4.5V |  |  |  | 3.8 |  |  | 3.8 |  |  |
| VOL | | | IOL = 100μA | | | 1.65V to 5.5V |  |  |  |  |  | 0.1 |  |  | 0.1 | V |
| IOL = 4mA | | | 1.65V |  |  |  |  |  | 0.45 |  |  | 0.45 |
| IOL = 8mA | | | 2.3V |  |  |  |  |  | 0.3 |  |  | 0.3 |
| IOL = 16mA | | | 3V |  |  |  |  |  | 0.4 |  |  | 0.4 |
| IOL = 24mA | | |  |  |  |  |  | 0.55 |  |  | 0.55 |
| IOL = 32mA | | | 4.5V |  |  |  |  |  | 0.55 |  |  | 0.55 |
| II | | A input | VI = 5.5V or GND | | | 0 to 5.5V |  |  |  |  |  | ±5 |  |  | ±5 | μA |
| Ioff | | | VI or VO = 5.5V | | | 0 |  |  |  |  |  | ±10 |  |  | ±10 | μA |
| ICC | | | VI = 5.5V or GND, | | IO = 0 | 1.65V to 5.5V |  |  |  |  |  | 10 |  |  | 10 | μA |
| VI = 3.6V or GND, | | 3V to 3.6V |  | 0.5 | 1.5 |  |  |  |  |  |  |
| ΔICC | | | One input at VCC – 0.6V,  Other inputs at VCC or GND | | | 3V to 5.5V |  |  |  |  |  | 500 |  |  | 500 | μA |
| CI | | | VI = VCC or GND | | | 3.3V |  | 4.5 |  |  |  |  |  |  |  | pF |

(1) All typical values are at VCC = 3.3V, TA = 25°C.

## 5.6 Switching Characteristics, CL = 15pF

Table 5-2 CL = 15pF over recommended operating free-air temperature range, CL =
15pF (unless otherwise noted) (see [Figure 6-1](GUID-732216E4-AB9C-4627-B8AB-ED793B891255.html#SCES351122001))

| PARAMETER | FROM  (INPUT) | TO  (OUTPUT) | –40°C TO 85°C | | | | | | | | UNIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VCC = 1.8V ± 0.15V | | VCC = 2.5V ± 0.2V | | VCC = 3.3V ± 0.3V | | VCC = 5V ± 0.5V | |
| MIN | MAX | MIN | MAX | MIN | MAX | MIN | MAX |
| tpd | A | Y | 2.8 | 9.9 | 1.6 | 5.5 | 1.5 | 4.6 | 0.9 | 4.4 | ns |

## 5.7 Switching Characteristics AC Limit, –40°C to 85°C

Table 5-3 AC Limit, –40°C to 85°C over recommended operating free-air temperature range, CL =
30pF or 50pF (unless otherwise noted) (see [Figure 6-2](GUID-732216E4-AB9C-4627-B8AB-ED793B891255.html#SCES351122002))

| PARAMETER | FROM  (INPUT) | TO  (OUTPUT) | –40°C TO 85°C | | | | | | | | UNIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VCC = 1.8V ± 0.15V | | VCC = 2.5V ± 0.2V | | VCC = 3.3V ± 0.3V | | VCC = 5V ± 0.5V | |
| MIN | MAX | MIN | MAX | MIN | MAX | MIN | MAX |
| tpd | A | Y | 3.8 | 11 | 2 | 6.5 | 1.8 | 5.5 | 1.2 | 5 | ns |

## 5.8 Switching Characteristics AC Limit, –40°C to 125°C

Table 5-4 AC Limit –40°C to 125°C over recommended operating free-air temperature range, CL =
30pF or 50pF (unless otherwise noted) (see [Figure 6-2](GUID-732216E4-AB9C-4627-B8AB-ED793B891255.html#SCES351122002))

| PARAMETER | FROM  (INPUT) | TO  (OUTPUT) | –40°C TO 125°C | | | | | | | | UNIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VCC = 1.8V ± 0.15V | | VCC = 2.5V ± 0.2V | | VCC = 3.3V ± 0.3V | | VCC = 5V ± 0.5V | |
| MIN | MAX | MIN | MAX | MIN | MAX | MIN | MAX |
| tpd | A | Y | 3.8 | 13 | 2 | 8 | 1.8 | 6.5 | 1.2 | 6 | ns |

## 5.9 Operating Characteristics

TA = 25°C 

| PARAMETER | | | TEST CONDITIONS | VCC = 1.8V | VCC = 2.5V | VCC = 3.3V | VCC = 5V | UNIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TYP | TYP | TYP | TYP |
| Cpd | Power dissipation capacitance | | f = 10MHz | 20 | 21 | 22 | 26 | pF |

## 5.10 Typical Characteristics

![SN74LVC1G17 Across Temperature at 3.3V Vcc](https://www.ti.com/ods/images/SCES351Y/GUID-47BF012A-FC26-4CFF-A7C7-B59DF7437E3F-low.gif "SN74LVC1G17 Across Temperature at 3.3V Vcc")Figure 5-1 Across Temperature at 3.3V Vcc

![SN74LVC1G17 Across Vcc at 25°C](https://www.ti.com/ods/images/SCES351Y/GUID-C3AD94BD-5BEE-4132-93D1-5B8C2A7B75BA-low.gif "SN74LVC1G17 Across Vcc at 25°C")Figure 5-2 Across Vcc at 25°C

# 6 Parameter Measurement Information

![SN74LVC1G17 Load
                    Circuit and Voltage Waveforms](https://www.ti.com/ods/images/SCES351Y/GUID-CEE5941B-842C-4BA0-862C-46112BF00C99-low.gif "SN74LVC1G17 Load
                    Circuit and Voltage Waveforms")
Figure 6-1 Load
Circuit and Voltage Waveforms

![SN74LVC1G17 Load
                    Circuit and Voltage Waveforms](https://www.ti.com/ods/images/SCES351Y/GUID-3D2B0770-348B-4EF8-9361-6B665896770E-low.gif "SN74LVC1G17 Load
                    Circuit and Voltage Waveforms")
Figure 6-2 Load
Circuit and Voltage Waveforms

# 7 Detailed Description

## 7.1 Overview

The SN74LVC1G17 device contains one Schmitt
trigger buffer and performs the Boolean function Y
= A. The device functions as an independent
buffer, but because of the Schmitt action, the
device has different input threshold levels for
positive-going (VT+) and negative-going signals.

The DPW package technology is a major breakthrough
in IC packaging. The DPW package is 0.64mm square footprint that saves board space
over other package options while still retaining the traditional and
manufacturing-friendly lead pitch of 0.5mm.

The SN74LVC1G17 is fully specified for
partial-power-down applications using
Ioff. The Ioff circuitry
disables the outputs, preventing damaging current
backflow through the device when the device is
powered down.

## 7.2 Functional Block Diagram

![SN74LVC1G17 ](https://www.ti.com/ods/images/SCES351Y/GUID-BA05E519-53FC-4C1A-9530-0F8F5FB723E5-low.gif)

## 7.3 Feature Description

- Wide operating voltage range
  - Operates from 1.65V to
    5.5V
- Allows down voltage
  translation
- Inputs accept voltages to
  5.5V
- Ioff feature allows
  voltages on the inputs and outputs when VCC is 0V

## 7.4 Device Functional Modes

Table 7-1 Function Table

| INPUT  A | OUTPUT  Y |
| --- | --- |
| H | H |
| L | L |

# 8 Applications and Implementation

Note:

Information in the following applications sections is not part of the TI
component specification, and TI does not warrant its accuracy or completeness.
TI’s customers are responsible for determining suitability of components for
their purposes, as well as validating and testing their design implementation to
confirm system functionality.

## 8.1 Application Information

The SN74LVC1G17 is a high drive CMOS device that
can be used for a multitude of buffer type functions where the input is slow or
noisy. SN74LVC1G17 can produce 24mA of drive current at 3.3V; engineers can use it
for driving multiple outputs and good for high speed applications up to 100MHz. The
inputs are 5.5V tolerant allowing SN74LVC1G17 to translate down to
VCC.

## 8.2 Typical Application

![SN74LVC1G17 ](https://www.ti.com/ods/images/SCES351Y/GUID-20200921-CA0I-RRBF-FNPH-LHCFQ7JKV9N7-low.gif)

### 8.2.1 Design Requirements

This device uses CMOS technology and has balanced
output drive. Take care to avoid bus contention,
because bus contention can drive currents to
exceed maximum limits. Consider routing and load
conditions to prevent ringing because the high
drive also creates fast edges into light
loads.

### 8.2.2 Detailed Design Procedure

1. Recommended Input Conditions
   - Specified high and low levels. See (VIH and VIL) in the [Recommended Operating Conditions](GUID-7BB39708-2B68-4F0C-837D-7C2F2441D6FD.html#GUID-7BB39708-2B68-4F0C-837D-7C2F2441D6FD) table.
   - Inputs are overvoltage tolerant allowing them to
     go as high as (VI max) in the [Recommended Operating Conditions](GUID-7BB39708-2B68-4F0C-837D-7C2F2441D6FD.html#GUID-7BB39708-2B68-4F0C-837D-7C2F2441D6FD) table at any valid
     VCC.
2. Recommend Output Conditions
   - Do not exceed load currents (IO max)
     per output or (continuous current through VCC or GND) total
     current for the part. These limits are located in the [Absolute Max Ratings](GUID-EFEFE4AA-954D-4D7C-AD3C-FA10F8A468F3.html#GUID-EFEFE4AA-954D-4D7C-AD3C-FA10F8A468F3) table.
   - Do not pull outputs above VCC.

### 8.2.3 Application Curves

![SN74LVC1G17 ICC
                        vs Frequency](https://www.ti.com/ods/images/SCES351Y/GUID-A9440FA7-CC0E-4FB0-B94C-4C781BF337DF-low.gif "SN74LVC1G17 ICC
                        vs Frequency")Figure 8-1 ICC
vs Frequency

## 8.3 Power Supply Recommendations

The power supply can be any
voltage between the min and max supply voltage rating located in the [Recommended Operating Conditions](GUID-7BB39708-2B68-4F0C-837D-7C2F2441D6FD.html#GUID-7BB39708-2B68-4F0C-837D-7C2F2441D6FD) table.

Each Vcc pin should have a good
bypass capacitor to prevent power disturbance. For devices with a single supply,
a 0.1μF capacitor is recommended. If there are multiple Vcc pins, then a 0.01μF
or 0.022μF capacitor is recommended for each power pin. It is acceptable to
parallel multiple bypass caps to reject different frequencies of noise. 0.1μF
and 1μF capacitors are commonly used in parallel. For best results, install the
bypass capacitor as close to the power pin as possible.

## 8.4 Layout

### 8.4.1 Layout Guidelines

When using multiple bit logic devices, verify that
inputs do not ever float. In many cases, functions or parts of functions of digital
logic devices are unused, for example, when only two inputs of a triple-input AND
gate are used or only 3 of the 4 buffer gates are used. Do no leave such input
terminals unconnected because the undefined voltages at the outside connections
result in undefined operational states. In all circumstances, observe the rules
specified below. Connect all unused inputs of digital logic devices to a high or low
bias to prevent them from floating. The logic level that applies to any particular
unused input depends on the function of the device. Generally the logic level is
tied to the Gnd or Vcc, whichever is the better choice.

### 8.4.2 Layout Example

![SN74LVC1G17 ](https://www.ti.com/ods/images/SCES351Y/GUID-5C86EF02-1717-4174-8532-BE0ABB4A64E3-low.gif)

# 9 Device and Documentation Support

## 9.1 Receiving Notification of Documentation Updates

To receive notification of
documentation updates, navigate to the device product folder on [ti.com](https://www.ti.com). Click on
*Notifications* to register and receive a weekly digest of any product
information that has changed. For change details, review the revision history
included in any revised document.

## 9.2 Support Resources

[TI E2E™ support forums](https://e2e.ti.com)
are an engineer's go-to source for fast, verified answers and design help — straight
from the experts. Search existing answers or ask your own question to get the quick
design help you need.

Linked content is provided "AS IS" by the respective contributors. They do not constitute
TI specifications and do not necessarily reflect TI's views; see TI's [Terms of Use](https://www.ti.com/corp/docs/legal/termsofuse.shtml).

## 9.3 Trademarks

TI E2E™ is a trademark of Texas Instruments.

All trademarks are the property of their respective owners.

## 9.4 Electrostatic Discharge Caution

| SN74LVC1G17 | This integrated circuit can be damaged by ESD. Texas Instruments recommends that all integrated circuits be handled with appropriate precautions. Failure to observe proper handling and installation procedures can cause damage. |
| --- | --- |
| ESD damage can range from subtle performance degradation to complete device failure. Precision integrated circuits may be more susceptible to damage because very small parametric changes could cause the device not to meet its published specifications. |

## 9.5 Glossary

[TI Glossary](https://www.ti.com/lit/pdf/SLYZ022)
This glossary lists and explains terms, acronyms, and definitions.

# 10 Revision History

**Changes from Revision X (June 2025) to Revision Y (October 2025)**

- Changed Junction-to-ambient thermal resistance value for DCK package
  from: 280°C/W to: 371.0°C/W [Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)
- Changed Junction-to-case (top) thermal resistance value for DCK
  package from: 66°C/W to: 297.5°C/W[Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)
- Changed Junction-to-board thermal resistance value for DCK package
  from: 67°C/W to: 258.6°C/W[Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)
- Changed Junction-to-top characterization value for DCK package from:
  2°C/W to: 195.6°C/W[Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)
- Changed Junction-to-board characterization value for DCK package
  from: 66°C/W to: 256.2°C/W[Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)

**Changes from Revision W (September 2020) to Revision X (June 2025)**

- Updated the document to reflect TI writing standards[Go](GUID-D229EA7B-A7E1-4143-95AE-DC5FE93AA6B2.html)
- Changed *Device Information* table to *Package Information*
  [Go](GUID-D229EA7B-A7E1-4143-95AE-DC5FE93AA6B2.html)
- Moved Tstg to *Absolute Maximum Ratings*
  table[Go](GUID-EFEFE4AA-954D-4D7C-AD3C-FA10F8A468F3.html)
- Changed *Handling Ratings* to *ESD Ratings*
  [Go](GUID-3D5F2DAD-30D7-4EC6-9CE7-7F9CFE090DAD.html)
- Changed Junction-to-ambient thermal resistance value for DBV package
  from: 229°C/W to: 357.1°C/W [Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)
- Changed Junction-to-case (top) thermal resistance value for DBV
  package from: 164°C/W to: 263.7°C/W[Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)
- Changed Junction-to-board thermal resistance value for DBV package
  from: 62°C/W to: 264.4°C/W[Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)
- Changed Junction-to-top characterization value for DBV package from:
  44°C/W to: 195.6°C/W[Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)
- Changed Junction-to-board characterization value for DBV package
  from: 62°C/W to: 262.2°C/W[Go](GUID-C23CCAFA-3702-4EC3-B3E0-6313644D4D04.html)
- Removed rise time and fall time information from the recommended
  input conditions in the *Detailed Design Procedure*
  [Go](GUID-6008C7E6-B520-4E21-99DA-685435D84870.html)

# 11 Mechanical, Packaging, and Orderable Information

The following pages include
mechanical packaging and orderable information. This information is the most
current data available for the designated devices. This data is subject to
change without notice and revision of this document. For browser-based versions
of this data sheet, refer to the left-hand navigation.
