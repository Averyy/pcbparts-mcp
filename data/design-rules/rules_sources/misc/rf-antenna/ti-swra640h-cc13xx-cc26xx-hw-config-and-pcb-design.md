---
source: "TI SWRA640H -- CC13xx/CC26xx HW Config and PCB Design"
url: "https://www.ti.com/lit/an/swra640h/swra640h.pdf"
format: "PDF 44pp"
method: "ti-html"
extracted: 2026-02-16
chars: 87295
---

Application Note

# CC13xx/CC26xx Hardware Configuration and PCB Design Considerations

# Abstract

This application report provides
design guidelines for the CC13xx/CC26xx SimpleLink™
ultra-low-power wireless MCU platform. There is an overview of the different
reference designs followed by RF front-end, schematic, PCB, and antenna design
considerations. The document also covers crystal oscillator tuning, optimum load
impedance as well as a brief explanation of the different power supply
configurations. The last section of the document provides a summary of steps to
carry out at board bring-up.

# Trademarks

SimpleLink™, LaunchPad™, and SmartRF™ are trademarks of Texas Instruments.

Bluetooth® is a registered trademark of Bluetooth SIG, Inc and used by Motorola, Inc. under license.

# 1 Reference Design

A TI LaunchPad™ is the main
development platform for CC13xx and CC26xx devices. A LaunchPad includes optimized
external RF components on-board, PCB antenna and built-in debugger providing an
easy-to-use development environment with a single core software development kit
(SDK) and rich tool set. Each CC13xx/CC26xx family member is featured on a dedicated
LaunchPad with RF matching network and an antenna optimized for operation at one or
more of the supported ISM bands. All TI LaunchPad design files, including
Gerber-files and CAD source, are available for download at [ti.com](http://www.ti.com) and can be used as a
reference design when integrating CC13xx/CC26xx into custom hardware.

## 1.1 Sub-1GHz LaunchPads

This section provides the different
LaunchPad designs and which design to follow for a specific CC13xx/CC26xx device and
ISM band.

### 1.1.1 LAUNCHXL-CC1310

|  |  |
| --- | --- |
| **Featured device:** | CC1310 |
| **ISM band:** | 868MHz and 915MHz |
| **Antenna:** | [*Monopole PCB Antenna with Single or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA227) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*LAUNCHXL-CC1310 Design Files*](https://www.ti.com/lit/zip/swrc319) |

### 1.1.2 LAUNCHXL-CC1312R

|  |  |
| --- | --- |
| **Featured device:** | CC1312R |
| **ISM band:** | 868MHz and 915MHz |
| **Antenna:** | [*Monopole PCB Antenna with Single or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA227) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*SimpleLink Sub-1GHz CC1312R Wireless (MCU) LaunchPad Dev Kit 868MHz/915MHz App*](https://www.ti.com/lit/zip/swrr160) |

## 1.2 2.4GHz LaunchPads

### 1.2.1 LAUNCHXL-CC2640R2

The LAUNCHXL-CC2640R2 is a
single-protocol LaunchPad that operates in 2.4GHz supporting BLE 5.1 and earlier LE
specifications. The RF front end enables up to +5dBm of output power.

|  |  |
| --- | --- |
| **Featured device:** | CC2640R2F |
| **ISM band:** | 2.4GHz |
| **Antenna:** | [*2.4GHz Inverted F Antenna*](https://www.ti.com/lit/pdf/SWRU120) |
| **RF front-end:** | Differential, internal bias |
| **Design files:** | [*LAUNCHXL-CC2640R2 Design Files*](https://www.ti.com/lit/zip/swrc335) |

### 1.2.2 LAUNCHXL-CC26x2R

The LAUNCHXL-CC26x2R is a multi-protocol
LaunchPad that operates at 2.4GHz. The RF front end enables up to +5dBm of output power.
LAUNCHXL-CC26x2R can also be used for development with CC2642R.

|  |  |
| --- | --- |
| **Featured device:** | CC2652R |
| **ISM band:** | 2.4GHz |
| **Antenna:** | [*2.4GHz Inverted F Antenna*](https://www.ti.com/lit/pdf/SWRU120) |
| **RF front end:** | Differential, internal bias |
| **Design files:** | [*CC26x2R LaunchPad Design Files*](https://www.ti.com/lit/zip/swrc346) |

### 1.2.3 LP-CC26x1

The LP-CC26x1 is a multi-protocol
LaunchPad that operates at 2.4GHz. The LaunchPad comes in two versions: LP-CC2651R3
which enables up to +5dBm of output power and LP-CC2651P3 which enables up to +20dBm
of output power.

|  |  |
| --- | --- |
| **Featured device** | CC2651R3 and CC2651P3 |
| **ISM band** | 2.4GHz |
| **Antenna** | [*2.4GHz Inverted F Antenna*](https://www.ti.com/lit/pdf/SWRU120) |
| **RF Front End** | Differential, external bias |
| **Design Files** | [*LP-CC26x1 LaunchPad Design Files*](http://www.ti.com/lit/zip/SWRC375) |

## 1.3 Dual-Band LaunchPads

### 1.3.1 LAUNCHXL-CC1350EU/US

The LAUNCHXL-CC1350EU/US is a
dual-band LaunchPad that operates between 868MHz/915MHz or 2.4GHz. The sub-1 GHz
path enables up to +15dBm of output power, and the 2.4GHz path enables up to +9dBm
of output power. The LaunchPad comes in two different versions: EU (868MHz) and US
(915MHz). Both paths share a dual-band antenna optimized for both frequency
bands.

|  |  |
| --- | --- |
| **Featured device:** | CC1350 |
| **ISM band:** | 868MHz, 915MHz, and 2.4GHz |
| **Antenna:** | * [*Miniature Helical PCB Antenna for 868MHz or   915/920MHz*](https://www.ti.com/lit/pdf/SWRA416) * [*2.4GHz Inverted F Antenna*](https://www.ti.com/lit/pdf/SWRU120) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*LAUNCHXL-CC1350 Design Files*](https://www.ti.com/lit/zip/swrc320) |

### 1.3.2 LAUNCHXL-CC1350-4

The LAUNCHXL-CC1350-4 is a
dual-band LaunchPad that operates between 433MHz
or 2.4GHz. The sub-1GHz path enables up to +15dBm
of output power, and the 2.4GHz path enables up to
+9dBm of output power. Both paths share a
dual-band antenna optimized for both frequency
bands.

|  |  |
| --- | --- |
| **Featured device:** | CC1350 |
| **ISM band:** | 433MHz and 2.4GHz |
| **Antenna:** | * [*Miniature Helical PCB Antenna for 868MHz or   915/920MHz*](https://www.ti.com/lit/pdf/SWRA416) * [*2.4GHz   Inverted F Antenna*](https://www.ti.com/lit/pdf/SWRU120) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*CC1350 Dual Band Launchpad for 433 MHz/ 2.4GHz Band Rev A*](https://www.ti.com/lit/zip/swrr158) |

### 1.3.3 LAUNCHXL-CC1352R

The LAUNCHXL-CC1352R is a dual-band
LaunchPad that operates between 868MHz/915MHz or 2.4GHz. The sub-1GHz path enables
up to +14dBm of output power, and the 2.4GHz path enables up to +5dBm of output
power. The current revision uses a diplexer instead of a switch to allow both
frequency bands to share an RF path, which frees up one DIO pin. Both paths share a
dual-band antenna optimized for both frequency bands.

|  |  |
| --- | --- |
| **Featured device:** | CC1352R |
| **ISM band:** | 868MHz, 915MHz, and 2.4GHz |
| **Antenna:** | [*Monopole PCB Antenna with Single or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA227) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*CC1352R LaunchPad Design Files*](https://www.ti.com/lit/zip/swrc345) |

### 1.3.4 LAUNCHXL-CC1352P1

The LAUNCHXL-CC1352P1 is a dual-band
LaunchPad that operates between 868MHz/915MHz or the 2.4GHz. The sub-1GHz has a
high-power PA path enabling up to +20dBm output power, and a regular path with up to
+14dBm output power. The 2.4GHz path enables up to +10dBm output power. All three
paths share a dual-band antenna optimized for both frequency bands.

|  |  |
| --- | --- |
| **Featured device:** | CC1352P |
| **ISM band:** | 868MHz, 915MHz, and 2.4GHz |
| **Antenna:** | [*Monopole PCB Antenna with Single or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA227) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*CC1352R LaunchPad Design Files*](https://www.ti.com/lit/zip/swrc345) |

### 1.3.5 LAUNCHXL-CC1352P-2

The LAUNCHXL-CC1352P-2 is a dual-band
LaunchPad that operates between 868MHz/915MHz or 2.4GHz. The sub-1GHz path enables
up to +14dBm output power. The 2.4GHz output has a high-power PA path enabling up to
+20dBm output power, and a regular path with up to +5dBm output power. All three
paths share a dual-band antenna optimized for both frequency bands.

|  |  |
| --- | --- |
| **Featured device:** | CC1352P |
| **ISM band:** | 868MHz, 915MHz and 2.4GHz |
| **Antenna:** | [*Monopole PCB Antenna with Single or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA227) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*LAUNCHXL-CC1352P-2 Design Files*](https://www.ti.com/lit/zip/swrc350) |

### 1.3.6 LAUNCHXL-CC1352P-4

The LAUNCHXL-CC1352P-4 is a dual-band
LaunchPad that operates between 433MHz or 2.4GHz. The sub-1GHz path enables up to
+13dBm output power. The 2.4GHz path biases the high-power PA to provide up to
+10dBm output power, and a regular that enables up to +5dBm of output power. All
three paths share a dual-band antenna optimized for both frequency bands.

|  |  |
| --- | --- |
| **Featured device:** | CC1352P |
| **ISM band:** | 433MHz and 2.4GHz |
| **Antenna:** | [*Monopole PCB Antenna with Single or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA227) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*LAUNCHXL-CC1352P-4 Design Files*](https://www.ti.com/lit/zip/swrc352) |

### 1.3.7 LP-CC1352P7-1

The LP-CC1352P7-1 is a dual-band LaunchPad
that operates between 868MHz/915MHz or 2.4GHz. The sub-1 GHz output has a high-power
PA path enabling up to +20dBm output power or a regular path with up to +14dBm
output power. The 2.4GHz path enables up to +5dBm output power. All three paths
share a dual-band antenna optimized for both frequency bands.

|  |  |
| --- | --- |
| **Featured device:** | CC1352P7-1 |
| **ISM band:** | 868MHz, 915MHz and 2.4GHz |
| **Antenna:** | [*Monopole PCB Antenna with Single or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA372) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*LAUNCHXL-CC1352P7-1 Design Files*](https://www.ti.com/lit/zip/swrc372) |

### 1.3.8 LP-CC1352P7-4

The LP-CC1352P7-4 is a dual-band LaunchPad
that operates between 433MHz or 2.4GHz. The sub-1 GHz output has a high-power PA
path enabling up to +20dBm output power, and a regular path with up to +14dBm output
power. The 2.4GHz path enables up to +5dBm output power. All three paths share a
dual-band antenna optimized for both frequency bands.

|  |  |
| --- | --- |
| **Featured device:** | CC1352P7-4 |
| **ISM band:** | 433MHz and 2.4GHz |
| **Antenna:** | [*Monopole PCB Antenna with Single or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA373) |
| **RF front-end:** | Differential, external bias |
| **Design files:** | [*LAUNCHXL-CC1352P7-4 Design Files*](https://www.ti.com/lit/zip/swrc373) |

### 1.3.9 LP-EM-CC1354P10-6

The LP-EM-CC1354P10-6 is a dual-band
LaunchPad that operates between 868MHz/915MHz or 2.4GH. The sub-1 GHz path enables
up to +14dBm output power. The 2.4GHz high-power PA path can be configured up to
+10dBm or +20dBm, and the regular path enables +5dBm of output power. All three
paths share a dual-band antenna optimized for both frequency bands.

Please note that this LaunchPad requires an LP-XDS110 debugger.

|  |  |
| --- | --- |
| **Featured device:** | CC1354P |
| **ISM band:** | 868MHz, 915MHz, and 2.4GHz |
| **Antenna:** | [*Monopole PCB Antenna with Single or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA227) |
| **RF front end:** | Differential, external bias |
| **Design files:** | [*LP-EM-CC1354P10-6 Design Files*](https://www.ti.com/lit/zip/SPRR437) |

## 1.4 Reference Design Overview

When designing a custom board the
reference design should be closely followed. Not all combinations of CC13xx/CC26xx
devices and ISM bands are covered by any one reference design, but it is possible to
use an RF front-end from one reference design and combine it with a compatible
CC13xx/CC26xx device. [Table 1-1](#X4871) shows which CC13xx/CC26xx reference design to use for a given ISM band.

If the application requires operation in the 433MHz band, but does not need 2.4GHz
operation or +20dBm transmit power, the CC1312R device can be used instead of
CC1352P. Then, the LAUNCHXL-CC1352P-4 reference design should be followed, but only
the RF front-end on the SUB-1\_GHZ\_RF\_P/N pins is required.

Table 1-1 CC13xx/CC26xx Reference Design
Overview

| Frequency Band | Supported Device | Reference Design | Comment |
| --- | --- | --- | --- |
| 433MHz   470MHz   510MHz | CC1310 | [CC13xxEM-7XD-4251](http://www.ti.com/lit/zip/swrc330) |  |
| CC1312R | [LAUNCHXL-CC1352P-4](http://www.ti.com/lit/zip/swrc352) | Use the 433MHz front-end from the CC1352P reference design |
| 779MHz   868MHz   915MHz | CC1310 | [LAUNCHXL-CC1310](http://www.ti.com/lit/zip/swrc319) | For other reference designs, see the following [link](https://www.ti.com/product/CC1310/technicaldocuments) |
| CC1311R3 | [LP-CC1311R3](https://www.ti.com/lit/zip/sprr488) |  |
| CC1311P3 | [LP-CC1311P3](https://www.ti.com/lit/zip/sprr488) |  |
| CC1312R | [LAUNCHXL-CC1312R1](http://www.ti.com/lit/zip/swrr160) |  |
| 2.4GHz | CC26x0 | [CC2650EM-7ID](http://www.ti.com/lit/zip/swrc298) | Characterization board for CC26x0. Using the 7x7 QFN in combination with differential RF, internal bias. |
| [CC2650EM-5XD](http://www.ti.com/lit/zip/swrc299) | Characterization board for CC26x0. Using the 5x5 QFN in combination with differential RF, external bias. |
| [CC2650EM-4XS](http://www.ti.com/lit/zip/swrc300) | Characterization board for CC26x0. Using the 4x4 QFN in combination with single ended RF, internal bias. |
| [CC2650EM-4XS\_Ext\_Reg](http://www.ti.com/lit/zip/swrc301) | Characterization board for CC26x0. Using the 4x4 QFN in External Regulator mode configuration. |
| CC2640R2 | [LAUNCHXL-CC2640R2](http://www.ti.com/lit/zip/swrc335) | Evaluation and development platform. |
| [CC2640EM-CXS](http://www.ti.com/lit/zip/swrc336) | Characterization board for the CC2640R2F WCSP. |
| CC2642R   CC2652R | [LAUNCHXL-CC26x2R1](http://www.ti.com/lit/zip/swrc346) | Evaluation and development platform. |
| [CC26x2REM-7ID](http://www.ti.com/lit/zip/swrc359) | Characterization board. |
| Multi-band | CC1350 | [LAUNCHXL-CC1350-4](http://www.ti.com/lit/zip/swrr158) | * 433MHz * 2.4GHz |
| CC1352P | [LAUNCHXL-CC1352P-4](http://www.ti.com/lit/zip/swrc352) |
| CC1350 | [LAUNCHXL-CC1350](http://www.ti.com/lit/zip/swrc320) | * 868/915MHz * 2.4GHz |
| CC1352R | [LAUNCHXL-CC1352R1](http://www.ti.com/lit/zip/swrc345) |
| [CC1352REM-XD7793-XD24](http://www.ti.com/lit/zip/swrc361) |
| CC1352P | [LAUNCHXL-CC1352P1](http://www.ti.com/lit/zip/swrc349) | * 868/915MHz at   20dBm * 2.4GHz at   5dBm |
| [CC1352PEM-XD7793-XD24-PA9093](http://www.ti.com/lit/zip/swrc362) |
| [LAUNCHXL-CC1352P-2](http://www.ti.com/lit/zip/swrc350) | * 868/915MHz at   14dBm * 2.4GHz at   20dBm |
| [CC1352PEM-XD7793-XD24-PA24](http://www.ti.com/lit/zip/swrc363) |
| CC1354P10 | [LP-EM-CC1354P10-6](https://www.ti.com/lit/zip/SPRR437) | * 868/915MHz at   14dBm * 2.4GHz at   10/20dBm |

# 2 Front-End Configurations

## 2.1 Overview of Front-end Configurations

CC13xx and CC26xx have the following
front-end configuration:

* Single ended: Either the RF\_P pin or the RF\_N pin is used as
  the RF path.
* Differential: Both RF\_P and RF\_N are used as a differential RF
  interface.
* Internal or external bias of the LNA: The LNA can be biased by
  an internal or external inductor. Both types of biasing can be selected for
  single-ended and differential configuration.

[Figure 2-1](#T5659416-31) shows the front-end configuration. Components and connections highlighted in red
color are not required if an internal bias is used. The component values depend on
the frequency band of operation.

Figure 2-1 CC13xx/CC26xx Front-End
Configuration (red = Required if an External Bias is Used)

[Figure 2-2](#T5659416-32) summarizes the pros and cons of the different solutions. All numbers in the
figure are compared to a differential front-end and external biasing.

Figure 2-2 Comparison of CC13xx/CC26xx
Front-End Configuration

## 2.2 Configuring the Front-End Mode

The front-end mode is set in the CMD\_RADIO\_SETUP command:

* Config.frontEndMode = 0x00: Differential mode
* Config.frontEndMode = 0x01: Single-ended mode RFP
* Config.frontEndMode = 0x02: Single-ended mode RFN

For single-ended operation that uses one RF pin in RX and the other RF pin in TX, an additional override has to be set:

Equation 1. ADI\_HALFREG\_OVERRIDES(0, 16, 0x7, x)

where, x = 1 configures the PA output on RFP and x = 2 configures the PA output on RFN.

For single-ended operation, the pin set by CMD\_RADIO\_SETUP Config.frontEndMode will be used in RX and the pin set by the ADI\_HALFREG\_OVERRIDE override will be used in TX.

The LNA biasing is set in the CMD\_RADIO\_SETUP command:

* config.biasMode = 0: Internal bias
* config.biasMode = 1: External bias

## 2.3 CC13xx Single-Ended Mode

### 2.3.1 Single-Ended Modes

A typical sub-1GHz design usually
requires long range and a differential design is typically used. For lower cost and
a smaller footprint, a single-ended design can be used at the expense of shorter
range shown in [Figure 2-3](#FIG_WVZ_ZGL_S5B).

If a CC13xx device is interfaced to a
front-end module (FEM) with dedicated 50Ω ports for RX and TX, fewer components than
in the combined single-ended RX/TX design are needed. This is covered in [Section 2.3.2](GUID-995BC48C-EA56-45A5-9F0C-4719D53272E1.html#GUID-995BC48C-EA56-45A5-9F0C-4719D53272E1) and [Section 2.3.3](GUID-759372B6-ADCA-4B4B-9BD6-B3206B5FD48F.html#GUID-759372B6-ADCA-4B4B-9BD6-B3206B5FD48F) for TX- and RX-only.

Figure 2-3 Single-Ended TX and RX With an
External Bias (868/915MHz)

### 2.3.2 Single-Ended TX-Only

A suggested matching network is shown in [Figure 2-4](#T5659416-44).

Figure 2-4 Single-Ended TX-Only
(868/915MHz)

### 2.3.3 Single-Ended RX-Only

A suggested matching network is shown
in [Figure 2-5](#T5659416-46). This match
gives sensitivity of -110dBm (measured on 3 units at 25°C, 3.0V, 868MHz).

Figure 2-5 Single-Ended Rx-Only with
External Bias (868/915MHz)

Figure 2-6 Single-Ended Rx-Only with
Internal Bias (868/915MHz)

### 2.3.4 Single-Ended Modes - 2.4GHz

For CC13x2, the single-ended
configuration shown in [Figure 2-7](#FIG_XXN_VS2_JSB) can be used
for the 2.4GHz path.

Figure 2-7 Single-Ended RX/TX with External Bias (2.4GHz)

## 2.4 CC26xx Single-End Mode

For CC26xx, a single-ended
configuration is recommended when maximum output power is not needed. For 0dBm
output power using single-ended mode, the current consumption and component count
can be lower than for the corresponding differential mode.

Reference designs for both
single-ended and differential configurations are available.

1. Go to: <https://www.ti.com/product/CC2640R2F/technicaldocuments>.
2. Scroll down to *Design Files*.
3. The designs are named 4XS, 5XD, and 7ID. The first number
   indicate the packet size, X - External bias, I - Internal bias, S –
   Single-ended, D – Differential.

# 3 Schematic

## 3.1 Schematic Overview

[Figure 3-1](#T5659416-53) shows the RF section and components discussed.

Figure 3-1 RF Section and Components of the CC1312R
Schematic

### 3.1.1 24/48MHz Crystal

A 24/48MHz crystal is required as the frequency
reference for the radio.

For CC26x2/CC13x2, there will be spurs at N x
48MHz offset from the carrier. These spurs are
caused by the current going back and forth between
the crystal and the XOSC tuning capacitors (which
form the oscillator tank together with off-chip
capacitances). This current is quite large due to
the high Q of the crystal tank and can create an
IR drop on the power rails that are shared with
the PA and VCO. Setting the XOSC tuning capacitors
to zero reduces the spurs by approximately 5dB for
the largest spur compared to the default
setting.

The internal capacitor array can be used in most
use cases, but it is recommended to use external crystal loading capacitors and
setting the internal XOSC tuning capacitors to zero for systems targeting compliance
with ARIB STD T-108 and Chinese regulations in 470 – 510MHz frequency band as well
as when using the +20dBm PA. For information on how to set the internal XOSC tuning
capacitors, see [Section 6.4](GUID-6E7DB384-706B-4FA7-813D-EAAF5E4629CE.html#GUID-6E7DB384-706B-4FA7-813D-EAAF5E4629CE).

### 3.1.2 32.768kHz Crystal

The 32.768kHz crystal is optional. The
internal low-speed RC oscillator (32kHz) can be used as a reference if the low-power
crystal oscillator is not used. The RC oscillator can be calibrated automatically to
provide a sleep timer accurate enough for *Bluetooth®* Low Energy. Using an external crystal has the advantage that
it increases sleep clock accuracy and reduces the power consumption for Bluetooth
Low Energy (shorter RX windows around connection events). An external crystal is
required for time synchronous protocols such as TI 15.4-Stack and wM-Bus.

### 3.1.3 Balun

A balun is a network that transforms
from a balanced (differential) to an unbalanced (single-ended) signal. The design is
a lumped, lattice-type LC that has a ±90° phase shift implemented by using a
low-pass filter and a high-pass filter. It is important to keep the balun as
symmetrical as possible. If only one of the RF pins is used for RF output/input, no
balun is required. In this case a filter is required between the chip and the
antenna. For more details, see [Section 2.3](GUID-2668A74B-6595-46D1-BE98-21C2138EF227.html#GUID-2668A74B-6595-46D1-BE98-21C2138EF227).

### 3.1.4 Filter

An LC filter is placed between the balun and the
antenna. The filter has two functions: attenuate
harmonics and perform an impedance transformation
to 50Ω. The latter is important since measuring
equipment, such as spectrum analyzers and RF
signal generators, have a port impedance of 50Ω.
The word "filter balun" is sometimes used to
describe all the components necessary to implement
a balun, filter and to ensure proper impedance
matching between the radio and the antenna.

### 3.1.5 RX\_TX Pin

This pin is not present on all CC26x0/CC13x0 and
CC26x2/CC13x2 devices. This pin provides a ground
connection in RX mode. This is referred to an
external bias and improves sensitivity by
approximately 1dB compared to internally biasing
of the LNA.

### 3.1.6 Decoupling Capacitors

In the reference design there are several
decoupling capacitors. The schematic indicates which supply pin the decoupling
capacitor needs to be placed close to.

Figure 3-2 LAUNCHXL-CC1312R1 Decoupling
Capacitors

### 3.1.7 Antenna Components

A pi-match network is recommended between the LC filter and the antenna for antenna impedance matching. For more information, see [Section 5.1](GUID-2F20ED89-E534-4B40-BEAB-E2978616D144.html#GUID-2F20ED89-E534-4B40-BEAB-E2978616D144).

### 3.1.8 RF Shield

An RF shield is used on some of the TI reference
designs to reduce the radiation of spurious signals, in particular the 3rd harmonic
radiated power levels.

### 3.1.9 I/O Pins Drive Strength

The I/O pins have configurable drive
strength and maximum current. All I/O pins support 2mA and 4mA, while five pins
support up to 8mA.

Table 3-1 CC26x0/CC13x0, CC26x2/CC13x2
and CC26x4/CC13x4 Pins With up to 8mA Drive Strength

| 8 x 8 QFN (RSK) | 7 × 7 QFN (RGZ) | 5 × 5 QFN (RHB) | WCSP (YFV) | 4 × 4 QFN (RSM) |
| --- | --- | --- | --- | --- |
| DIO5 | DIO5 | DIO2 | DIO2 | DIO0 |
| DIO6 | DIO6 | DIO3 | DIO3 | DIO1 |
| DIO7 | DIO7 | DIO4 | DIO4 | DIO2 |
| DIO16 | DIO16 | DIO5 | DIO5 | DIO3 |
| DIO17 | DIO17 | DIO6 | DIO6 | DIO4 |

## 3.2 Bootloader Pins

The bootloader communicates with an
external device over a 2-pin universal asynchronous receiver/transmitter (UART) or a
4-pin SSI interface. The SSI0 port has the advantage of supporting higher and more
flexible data rates, but it also requires more connections to the CC13xx/CC26xx
devices. The UART0 has the disadvantage of having slightly lower and possibly less
flexible rates. However, the UART0 requires fewer pins and can be easily implemented
with any standard UART connection. The serial interface signals are configured to
specific DIOs. These pins are fixed and cannot be reconfigured.

Table 3-2 CC13x0/CC26x0: Configuration
of Signal Interfaces

| Signal | Pin Configuration | 7 × 7 QFN (RGZ) | 5 × 5 QFN (RHB) | 4 × 4 QFN (RSM) | 2.7 × 2.7 WCSP (YFV) |
| --- | --- | --- | --- | --- | --- |
| UART0 RX | Input with pull-up | DIO2 | DIO1 | DIO1 | DIO1 |
| UART0 TX | No pull (output when selected) | DIO3 | DIO0 | DIO2 | DIO0 |
| SSI0 CLK | Input with pull-up | DIO10 | DIO10 | DIO8 | DIO10 |
| SSI0 FSS | Input with pull-up | DIO11 | DIO9 | DIO7 | DIO9 |
| SSI0 RX | Input with pull-up | DIO9 | DIO11 | DIO9 | DIO11 |
| SSI0 TX | No pull (output when selected) | DIO8 | DIO12 | DIO0 | DIO12 |

Table 3-3 CC1311Rx, CC1312Rx, CC2651Rx,
CC2652Rx: Configuration of Signal Interfaces

| Signal | Pin Configuration |  |
| --- | --- | --- |
| UART0 RX | Input with pull-up | DIO2 |
| UART0 TX | No pull (output when selected) | DIO3 |
| SSI0 CLK | Input with pull-up | DIO10 |
| SSI0 FSS | Input with pull-up | DIO11 |
| SSI0 RX | Input with pull-up | DIO9 |
| SSI0 TX | No pull (output when selected) | DIO8 |

Table 3-4 CC13x4x10, CC26x4x10:
Configuration of Signal Interfaces

| Signal | Pin Configuration | CC26x4x10 | CC1314R10 | CC1354x10 |
| --- | --- | --- | --- | --- |
| UART0 RX | Input with pull-up | DIO12 | DIO2 | DIO12 |
| UART0 TX | No pull (output when selected) | DIO13 | DIO3 | DIO13 |
| SPI0 MISO | No pull (output when selected) | DIO8 | DIO8 | DIO8 |
| SPI0 MOSI | Input with pull-up | DIO9 | DIO9 | DIO9 |
| SPI0 CLK | Input with pull-up | DIO10 | DIO10 | DIO10 |
| SPI0 CS | Input with pull-up | DIO11 | DIO11 | DIO11 |

## 3.3 AUX Pins

### 3.3.1 Reference

There are up to 31 signals (AUXIO0 to
AUXIO30) in the sensor controller domain (AUX Domain). These signals can be routed
to specific DIO pins given in [Table 3-5](#GUID-92DF9A7C-7BD2-4169-B63D-BA99A95E5B78). The signals AUXIO19 to AUXIO26 have analog capability, but can also be used as
digital I/Os. All the other AUXIOn signals are digital only.

Table 3-5 CC13x4/CC26x4 Pin Mapping

| DIO | AUX Domain I/O | DIO | AUX Domain I/O | DIO | AUX Domain I/O |
| --- | --- | --- | --- | --- | --- |
| DIO30 | 19 | DIO19 | 30 | DIO8 | 10 |
| DIO29 | 20 | DIO18 | 31 | DIO7 | 11 |
| DIO28 | 21 | DIO17 | 1 | DIO6 | 12 |
| DIO27 | 22 | DIO16 | 2 | DIO5 | 13 |
| DIO26 | 23 | DIO15 | 3 | DIO4 | 14 |
| DIO25 | 24 | DIO14 | 4 | DIO3 | 15 |
| DIO24 | 25 | DIO13 | 5 | DIO2 | 16 |
| DIO23 | 26 | DIO12 | 6 | DIO1 | 17 |
| DIO22 | 27 | DIO11 | 7 | DIO0 | 18 |
| DIO21 | 28 | DIO10 | 8 |  |  |
| DIO20 | 29 | DIO9 | 9 |  |  |

### 3.3.2 CC26x2/CC13x2 AUX Pins

There are up to 32 signals (AUXIO0 to
AUXIO31) in the sensor controller domain (AUX Domain). These signals can be routed
to specific DIO pins given in [Table 3-6](#X6861). The signals AUXIO19 to AUXIO26 have analog capability, but can also be used as
digital I/Os. All the other AUXIOn signals are digital only.

Table 3-6 CC13x2/CC26x2 Pin
Mapping

| DIO | AUX Domain I/O | DIO | AUX Domain I/O | DIO | AUX Domain I/O |
| --- | --- | --- | --- | --- | --- |
| DIO30 | 19 | DIO19 | 30 | DIO8 | 10 |
| DIO29 | 20 | DIO18 | 31 | DIO7 | 11 |
| DIO28 | 21 | DIO17 | 1 | DIO6 | 12 |
| DIO27 | 22 | DIO16 | 2 | DIO5 | 13 |
| DIO26 | 23 | DIO15 | 3 | DIO4 | 14 |
| DIO25 | 24 | DIO14 | 4 | DIO3 | 15 |
| DIO24 | 25 | DIO13 | 5 | DIO2 | 16 |
| DIO23 | 26 | DIO12 | 6 | DIO1 | 17 |
| DIO22 | 27 | DIO11 | 7 | DIO0 | 18 |
| DIO21 | 28 | DIO10 | 8 |  |  |
| DIO20 | 29 | DIO9 | 9 |  |  |

### 3.3.3 CC26x0/CC13x0 AUX Pins

There are up to 16 signals (AUXIO0 to
AUXIO15) in the sensor controller domain (AUX). These signals can be routed to
specific pins given in [Table 3-7](#X3300). AUXIO0 to AUXIO7 have analog capability, but can also be used as digital I/Os,
while AUXIO8 to AUXIO15 are digital only.

Table 3-7 CC13x0/CC26x0 Pin
Mapping

| 7 × 7 QFN (RGZ) | 5 × 5 QFN (RHB) | WCSP (YFV) | 4 × 4 QFN (RSM) | AUX Domain I/O |
| --- | --- | --- | --- | --- |
| DIO30 | DIO14 |  |  | 0 |
| DIO29 | DIO13 | DIO13 |  | 1 |
| DIO28 | DIO12 | DIO12 |  | 2 |
| DIO27 | DIO11 | DIO11 | DIO9 | 3 |
| DIO26 | DIO9 | DIO9 | DIO8 | 4 |
| DIO25 | DIO10 | DIO10 | DIO7 | 5 |
| DIO24 | DIO8 | DIO8 | DIO6 | 6 |
| DIO23 | DIO7 | DIO7 | DIO5 | 7 |
| DIO7 | DIO4 | DIO4 | DIO2 | 8 |
| DIO6 | DIO3 | DIO3 | DIO1 | 9 |
| DIO5 | DIO2 | DIO2 | DIO0 | 10 |
| DIO4 | DIO1 | DIO1 |  | 11 |
| DIO3 | DIO0 | DIO0 |  | 12 |
| DIO2 |  |  |  | 13 |
| DIO1 |  |  |  | 14 |
| DIO0 |  |  |  | 15 |

## 3.4 JTAG Pins

The on-chip debug support is done
through a dedicated cJTAG (IEEE 1149.7) or JTAG (IEEE 1149.1) interface. The 2-pin
cJTAG mode using only TCK and TMS I/O pads is the default configuration after power
up. The 4-pin JTAG uses TCK, TMS, TDI, and TDO.

Table 3-8 CC26x0/CC13x0, CC26x2/CC13x2,
and CC26x4x10/CC13x4x10 JTAG Pins

| Signal | 8 x 8 QFN (RSK) | 7 × 7 QFN (RGZ) | 5 × 5 QFN (RHB) | WCSP (YFV) | 4 × 4 QFN (RSM) |
| --- | --- | --- | --- | --- | --- |
| TCK | Pin 25 | Pin 25 | Pin 14 | Pin F2 | Pin 14 |
| TMS | Pin 24 | Pin 24 | Pin 13 | Pin E4 | Pin 13 |
| TDI | DIO17 | DIO17 | DIO6 | DIO6 | DIO4 |
| TDO | DIO16 | DIO16 | DIO5 | DIO5 | DIO3 |

# 4 PCB Layout

## 4.1 Board Stack-Up

It is important that the distance from the top
layer to the ground layer matches the reference
design. Deviating from the recommended board
stack-up can change the parasitics and can in some
cases lead to a re-design of the filter balun.

Figure 4-1 LAUNCHXL-CC2640R2 Board Stack Up

## 4.2 Balun - Sub-1GHz

It is important to keep the balun as close and
symmetrical as possible with regard to the RF ports. Therefore, the trace length
from the single ended port to each of the RF pins should be equal to achieve best
amplitude and phase balance. For a good balun PCB layout, see [Figure 4-2](#T5659416-73). An unbalance in the balun causes higher harmonic levels, especially at the 2nd
and 4th harmonics. Another effect of having an unsymmetrical balun is reduced output
power at the single ended side of the balun. Both component values and component
placement is important to achieve best possible symmetry in the balun. Amplitude
imbalance should be a maximum of 1.5dB and the phase imbalance a maximum of 10°.

To ensure optimal performance it is important to
implement the same layout of the balun, match, and
filter as in the reference design. Changing the
placement of these parts might require tuning on
the component values to obtain the desired
performance. Tuning requires advanced RF skills
and the proper equipment.

There must be an uninterrupted and solid ground plane under all the RF components, stretching from the antenna and all the way back to the ground vias in the chip exposed ground pad (EGP). There must not be any traces under the RF path.

Figure 4-2 CC1312R Balun and LC Filter PCB Layout

## 4.3 Balun - 2.4GHz

We recommend following the reference
design closely as some designs require the use of a longer path length from the RF
port and the balun is optimized based on this extended length. Any attempts to
shorten the extended length requires the balun and matching circuit to be re-tuned.
For example, the figure below shows LP-EM-CC1354P10-6 2.4GHz path has an extended
length due to space restrictions that prevent parts from being placed closer to the
RF port.

Figure 4-3 LP-EM-CC1354P10-6 Balun
Layout

### 4.3.1 Recommended Layout and Considerations for 20dBm

When designing for a high-powered,
20dBm path, we recommend removing all header pins to help reduce 2nd harmonic
emissions, using high-Q, tight tolerance inductors and capacitors to help achieve
maximum output power, and a fully enclosed shield to help reduce 2nd and 3rd
harmonics.

Regarding the shield, we present the
following two options:

**Option A**

A fully enclosed shield is generally
the lower cost option to help used to reduce harmonics, but all traces must either
be contained with the shield or routed out to different layer using vias.
Consequentially, the RF path has to be routed on a different layer using transition
vias which must follow the reference design closely to maintain maximum output power
and minimum harmonics.

**Option B**

A custom, fully-enclosed shield with a
single opening for the RF trace can also be used to achieve the same performance.
This option allows the RF trace to be routed on the same layer without the need for
transition vias.

Note: We highly recommend EM simulations to characterize your
shield cavity as variations in performance can occur depending component density
and placements.

## 4.4 LC Filter

The LC filter should be laid out so
that crosstalk between the shunt components is minimized. [Figure 4-4](#T5659416-75) shows three different layouts from worse to best. The advantage with the layout
to the right is that the parasitic inductance in the PCB track (in black) between
the shunt capacitor and the series inductor is in series with the inductor. In the
middle figure, the parasitic inductance is in series with the shunt capacitor
forming a series LC circuit. The placement of C12, L13, C13, L14, and C14 in [Figure 4-2](GUID-07E07645-7BE6-461C-9F80-279E90F1B915.html#T5659416-73) shows good design practice.

If the design cannot use the reference
design as-is (for example, use of a different component size) the filter balun will
most likely have to be re-tuned. Simulate both the TI reference design and the
custom design using an electromagnetic simulator. The two designs should have the
same S21/S22.

Figure 4-4 LC Filter PCB Layout Design
Guideline

## 4.5 Decoupling Capacitors

General rules for decoupling capacitors:

* Ensure decoupling capacitors are on same layer as the active component for best
  results.
* Route power into the decoupling capacitor and then into the active
  component.
* Each decoupling capacitor should have a separate via to ground to minimize
  noise coupling (see [Figure 4-5](#T5659416-82)).
* The decoupling capacitor should be placed close to the pin it is supposed
  decouple (see [Figure 3-2](GUID-E1F5C140-7A66-45B1-AFF9-02B6AB42988A.html#T5659416-60)).
* The ground current return path between decoupling capacitor and chip should be
  short and direct (low impedance). For details, see [Section 4.7](GUID-34537DE8-8445-48BF-A77F-624BE0547003.html#GUID-34537DE8-8445-48BF-A77F-624BE0547003).

Figure 4-5 Decoupling Capacitors and VIA to Ground

The right side of [Figure 4-5](#T5659416-82) that uses
separate vias to ground has less noise coupling.

## 4.6 Placement of Crystal Load Capacitors

The main oscillation loop current is flowing between the crystal and the load capacitors. Keep this signal path (crystal to CL1 to CL2 to crystal) as short as possible and use a symmetrical layout. Hence, both the capacitors' ground connections should always be as close as possible. Never route the ground connection between the capacitors or all around the crystal, because this long ground trace is sensitive to crosstalk and EMI.

## 4.7 Current Return Path

There needs to be a solid ground plane
from the capacitor ground pad back to the chip. [Figure 4-6](#T5659416-84) illustrates this. In the bad example, notice the break in ground plane on layer 2
causing a longer return path while the good example has no breaks. Failure to follow
this can lead to reduced RF performance and higher spurious emissions.

Figure 4-6 Current Return Path

## 4.8 DC/DC Regulator

The DCDC components must be placed close to the DCDC\_SW pin. The capacitor at the DC/DC regulator output (DCDC\_SW pin) must have a short and direct ground connection to the chip (low impedance). Keep a solid ground plane from the capacitor ground pad back to the chip as shown for C331 in [Figure 4-7](#T5659416-86).

Figure 4-7 CC1312R DC/DC Regulator PCB Layout

## 4.9 Antenna Matching Components

A pi-network is recommended for antenna impedance matching. The antenna matching components should be placed as close to the antenna as possible.

## 4.10 Transmission Lines

Traces in the balun and LC filter are too short to
be considered transmission lines, but longer traces, such as from the LC filter,
towards the antenna should have a 50Ω impedance. TXLine is a free tool for PCB trace
impedance calculations: [TXLine Transmission Line Calculator](https://www.cadence.com/en_US/home/tools/system-analysis/rf-microwave-design/awr-tx-line.html).

## 4.11 Electromagnetic Simulation

If the design does not follow the reference design (for example, different filter balun component placement or component size), it is recommended to use Advanced Design System (ADS) or similar to simulate and then compare the impedances and S-parameters of the custom design with the reference design. Changes to the filter balun component values might be required if the custom design deviates too much from the reference design.

# 5 Antenna

## 5.1 Single-Band Antenna

The existing antenna documentation
available at TI is mainly orientated towards antennas that operate at a single
frequency. Two antenna selection guides are available: the [*Antenna Selection Quick
Guide*](https://www.ti.com/lit/pdf/SWRA351) and a comprehensive [*Antenna Selection Guide*](https://www.ti.com/lit/pdf/SWRA161). In
addition to the documentation, there is a [*CC-Antenna-DK2 and Antenna
Measurements Summary*](https://www.ti.com/lit/pdf/SWRA496) available on ti.com, as well, with complete
documentation. All antenna documentation that is available from TI can be accessed
from the [*Antenna Selection Quick Guide*](https://www.ti.com/lit/pdf/SWRA351) since it contains hyperlinks to
all antenna documentation, antenna measurement reports, and all antenna reference
designs.

It is always advised to include an
antenna matching network to tune and to reduce the mismatch losses of the antenna.
For a single-band antenna, the recommendation is to always include a pi-match
network prior to the antenna, see [Figure 5-1](#T5659416-98). Only two of the three footprints/components are required. The impedance of the
antenna will determine if footprint/component ANT1 or ANT3 is used. ANT2 will always
be used and even if the antenna is perfectly matched, then this can just be set as a
0Ω resistor.

Figure 5-1 Recommended Antenna PI-Match
Network for Single-Band Antennas

## 5.2 Dual-Band Antenna

The introduction of dual-band
operation with advantages of Bluetooth Low Energy combined with long-range
advantages of sub-1GHz sets the need of dual-band antennas. Separate antennas can be
used for each of the bands, but physical space is normally limited on most handheld
devices that promote usage of dual-band antennas. The most popular dual-band
configurations are shown below:

* 863/928MHz and 2.4GHz
* 433-450MHz and 2.4GHz
* 470-510MHz and 2.4GHz

For dual-band operation that contains
a low-band and a high-band, the antenna pi-match shown in [Figure 5-1](GUID-2F20ED89-E534-4B40-BEAB-E2978616D144.html#T5659416-98) is not recommended. It is recommended to use an LC, CL match network instead as
shown in [Figure 5-2](#T5659416-103). The LC part is used to match the high-band and the CL part is used for the
low-band. Therefore, the LC section will be denoted as LHIGH
CHIGH and the CL section as CLOW LLOW in order
to identify the components.

Figure 5-2 Recommended Antenna Match
Network for Dual-Band Antennas

### 5.2.1 Dual-Band Antenna Match Example: 863-928 MHz and 2.4 GHz

This example is based on
LaunchPad-CC1352P1.

* Assemble LHIGH: 0Ω and CLOW : 0Ω;
  CHIGH: NC and LLOW : NC
* Measure initial impedance with a network analyzer (VNA) at the
  low-band (868MHz) and high-band (2440MHz)
  + 868MHz: 54 + j30, VSWR: 1.78:1
  + 2.44GHz: 14 - j32, VSWR: 5.05:1 (This is not required
    at this stage but included for documentation purposes to note the
    delta).
* Match the low-band with only the CLOW and
  LLOW components
  + CLOW: 5.6pF and LLOW: NC; see
    [Figure 5-3](#T5659416-112)

  Figure 5-3 Matching the Low-Band
  With CLOW: 5.6pF and LLOW: NC
* Confirm the low-band is matched by measuring the impedance
  again:
  + 868MHz: 42 + j2, VSWR: 1.18:1. Good match at the
    low-band
  + 2.44GHz: 16+j34, VSWR: 5.38:1
* Match the high-band with only the CHIGH and
  LHIGH components
  + LHIGH : 2.2nH and CHIGH: NC; see
    [Figure 5-4](#T5659416-118)

  Figure 5-4 Matching the High-Band
  With an Ideal Value of LHIGH: 2.2nH and CHIGH:
  NC
* LHIGH : 2.2nH was not
  sufficient when measured and a value of 3.3nH was used instead. The antenna
  match components are based on ideal components with no parasitics. The match is
  not ideal but the CHIGH component could not be used due to the
  impedance position in the Smith chart.
* Measure final impedance with a network analyzer (VNA) at the
  low-band (868MHz) and high-band (2440MHz),
  + 868MHz: 37 + j8, VSWR: 1.36:1 Good match at the
    low-band
  + 2.44GHz: 16+j8, VSWR: 3.18:1 Reasonable match at the
    high-band but would prefer VSWR < 2.00:1; see [Figure 5-5](#T5659416-123) and [Figure 5-6](#T5659416-124).

    Figure 5-5 Smith Chart
    With Final Match Values of LHIGH: 3.3nH and
    CLOW: 5.6pF

    Figure 5-6 VSWR Chart
    With Final Match Values of LHIGH: 3.3nH and
    CLOW: 5.6pF
* With the matching components, the antenna match was improved
  by:
  + 868MHz: VSWR: 1.78:1 –> 1.36:1
  + 2.44GHz: VSWR: 5.05:1 –> 3.18:1

The example shown above used a
low-band of 868MHz but a main requirement of the LaunchPad-CC1352P-1 was for good
operation for the complete 863 – 928MHz band since it was important to cover both
ETSI (863-870MHz) and FCC bands (902-928MHz). The antenna length on CC1352P1 has a
natural resonance of approximately 900MHz with no matching components.

If the
performance at 2.44GHz is more important than supporting both 868MHz and 915MHz ISM
bands, then the length of the antenna can be increased so the natural resonance will
be around 813MHz (2440MHz/3). This would give very good performance at 868 MHz and
2.4GHz but the 915MHz band would suffer. A common antenna match for dual-bands is a
compromise of performance between the high-band and low-band.

### 5.2.2 Dual-Band Antenna Match: 433-510MHz and 2.4GHz

This antenna design is based on
LaunchPad-CC1352P-4 that uses the *433MHz to 930MHz and 2.4GHz BOM Tunable PCB
Antenna*. This BOM Tunable Antenna is fully documented *[433 to 930-MHz and
2.4-GHz BOM Tunable PCB Antenna](https://www.ti.com/lit/pdf/swra730)*, application note.

In order to cover the frequency band
433 – 510MHz, an external component (LANT) is added to the antenna structure
normally used for 863-928MHz and 2.4GHz. This is required to keep the antenna
relatively small and to maintain a high efficiency. The LANT component extends the
length of the antenna structure with the extra inductance added. It is difficult to
cover the entire frequency band of 433 – 510MHz with just one BOM due to the wide
bandwidth so the frequency range is divided up into the several regions. An
additional antenna structure has also been added that also extends the length of the
standard antenna, see [Figure 5-7](#T5659416-131).

Value of LANT component for
433-510MHz operation:

* 51nH: 433MHz
* 39nH: 470MHz
* 33nH: 490MHz

Figure 5-7 Recommended Antenna Match
Network for Dual-Band Antennas (433-510MHz and 2.4GHz)

Once the LANT component has been
chosen then the matching procedure is similar as shown in the previous example.
After the antenna matching process, the final values of the antenna match components
can be fixed. As can be seen in [Figure 5-8](#T5659416-132), the matching of 490MHz and 2.4GHz are both below VSWR 1.90 :1, which are good
results.

Figure 5-8 VSWR Chart with Final Match
Values of LANT: 33nH LHIGH: 3.9nH and CLOW: 0
Ω

Matching the antenna should be
performed in the final casing of the product including all surrounding components
such as batteries, displays, and so forth. Casing can affect the antenna’s resonance
even if the material choice is plastic. The positioning of the antenna or body
effects will also affect the antenna’s resonance. The antenna is always detuned by a
shift downwards in frequency. Therefore, if there are two different environments for
the antenna such as handheld and stand-alone on a wooden desk, then it is preferable
to have the stand-alone resonance slightly higher so the antenna’s bandwidth can be
utilized when detuned by body effects/metal objects, and so forth.

# 6 Crystal Tuning

## 6.1 CC13xx/CC26xx Crystal Oscillators

The CC13xx/CC26xx devices have two crystal
oscillators as shown in [Figure 6-1](#T5659416-135). The high frequency crystal oscillator
(HFXOSC), running at 24MHz for CC13x0/CC26x0 and
48MHz for CC13x2/CC26x2, is mandatory to operate
the radio. The low frequency crystal oscillator
(LFXOSC) is used for RTC timing and only required
when accurate RTC timing is necessary, for example
for synchronous protocols such as Bluetooth Low
Energy. For more details, please see *[The Crystal Selection
Guide](https://www.ti.com/lit/pdf/swra495)*.

Figure 6-1 CC1312R With 32kHz and 48MHz Crystals

Both crystal oscillators are pierce type
oscillators are shown in [Figure 6-2](#T5659416-136). In this type of oscillator, the crystal and the load capacitors form a pi-filter
providing a 180° phase shift to the internal amplifier keeping the oscillator locked
at the specified frequency. For this frequency to be correct, the load capacitance
must be dimensioned properly based on the crystal´s capacitive load (CL)
parameter.

Figure 6-2 Pierce-Type Oscillator

A key difference between the oscillators is that the high frequency oscillator has internal variable load capacitance inside the IC and does in most cases not require external load capacitors. For details on when it is required to use external capacitors instead of the internal variable load capacitance, see [Section 3.1.1](GUID-C5E557D9-D8EF-490A-BA02-68605C07D7DF.html#GUID-C5E557D9-D8EF-490A-BA02-68605C07D7DF). The low frequency oscillator on the other hand needs to have external capacitors to operate properly.

## 6.2 Crystal Selection

When selecting a crystal part, it is important to look at the device-specific CC13xx/CC26xx data sheets that lists requirements for the crystal parameters. All of these requirements must be fulfilled to ensure proper operation of the oscillator(s) and proper operation of the device.

## 6.3 Tuning the LF Crystal Oscillator

The frequency of the 32kHz crystal oscillator is
set by properly dimensioning the load capacitors relative to the crystal´s wanted
load capacitance, CL. From the crystal´s point of view, the two capacitors are
placed in series, which means that the “resistor parallel” equation to calculate the
resulting total capacitance must be used. Also keep in mind that the PCB traces and
the pads add some parasitic capacitance. [Equation 2](#T5659416-139) shows how to calculate the right load capacitance value.

Equation 2.

The last simplification requires that C1 and C2 are equal.

The best way to measure the frequency accuracy of
the oscillator is to output the clock signal on an
I/O pin. This way the frequency can be measured
using a frequency counter without affecting the
oscillator. The following Driverlib calls can
output the selected 32kHz clock source in all
power states except Shutdown:

```
#include <driverlib/aon_ioc.h>
IOCPortConfigureSet(IOIDn, IOC_PORT_AON_CLK32K, IOC_STD_OUTPUT);
AONIOC32kHzOutputEnable();
```

## 6.4 Tuning the HF Oscillator

The HF oscillator has internal variable load capacitors (cap-array) in the IC and does not require external capacitors to be mounted. There are some exceptions. For details on when it is required to use external capacitors instead of the internal cap-array, see [Section 3.1.1](GUID-C5E557D9-D8EF-490A-BA02-68605C07D7DF.html#GUID-C5E557D9-D8EF-490A-BA02-68605C07D7DF).

The load capacitance is set in CCFG.c through the following defines:

```
#ifndef SET_CCFG_MODE_CONF_XOSC_CAP_MOD
// #define SET_CCFG_MODE_CONF_XOSC_CAP_MOD            0x0        // Apply cap-array delta
#define SET_CCFG_MODE_CONF_XOSC_CAP_MOD               0x1        // Don't apply cap-array delta
#endif
#ifndef SET_CCFG_MODE_CONF_XOSC_CAPARRAY_DELTA
#define SET_CCFG_MODE_CONF_XOSC_CAPARRAY_DELTA        0xFF       // Signed 8-bit value, directly modifying trimmed XOSC cap-array value
#endif
```

The SET\_CCFG\_MODE\_CONF\_XOSC\_CAP\_MOD defines tells
the system whether it should use the default value or use an offset from the default
value set by SET\_CCFG\_MODE\_CONF\_XOSC\_CAPARRAY\_DELTA. The default cap-array values
are 9pF for CC13x0/CC26x0 QFN, 5pF for CC2640R2F WCSP, and 6.7pF for
CC13x2/CC26x2.

The cap-array delta value is an offset from the
default value that can be either negative or positive. [Table 6-1](#ID-459AD1CC-0E52-45C2-EB55-53677F589FCB) shows the resulting total capacitance measured on an evaluation board versus
cap-array delta values. Note that the resulting capacitance value includes parasitic
capacitances, which is why the lowest setting is not 0pF. Using a delta value equal
to or lower than the most negative value in the table completely disables the
internal load capacitor array.

The best way to measure the accuracy of the HF crystal oscillator is to output an unmodulated carrier wave from the radio and measuring the frequency offset from the wanted frequency using a spectrum analyzer. The relative offset of crystal frequency, typically stated in Parts per Million (ppm), is the same as the relative offset of the RF carrier.

For testing purposes cap-array delta values can be adjusted in
SmartRF™ Studio. This simplifies tuning greatly by allowing on-the-fly updates of the load capacitance. The optimum value found in SmartRF Studio can then be entered into CCFG in the applicable software project.

Table 6-1 Cap-Array Delta

| Measured Capacitance on Reference Board (pF) | CCFG Delta Value for CC13x0/CC26x0 QFN | CCFG Delta Value for CC2640R2F WCSP | CCFG Delta Value for CC13x1/CC26x1 QFN | CCFG Delta Value for CC13x2/CC26x2 QFN | CCFG Delta Value for CC13x4/CC26x4 QFN |
| --- | --- | --- | --- | --- | --- |
| **2.1** | < -55 | < -28 | < -40 | < -40 | < -40 |
| **2.1** | -55 | -28 | -40 | -40 | -40 |
| **2.2** | -54 | -27 | -39 | -39 | -39 |
| **2.3** | -53 | -26 | -38 | -38 | -38 |
| **2.4** | -52 | -25 | -37 | -37 | -37 |
| **2.5** | -51 | -24 | -36 | -36 | -36 |
| **2.6** | -50 | -23 | -35 | -35 | -35 |
| **2.7** | -49 | -22 | -34 | -34 | -34 |
| **2.7** | -48 | -21 | -33 | -33 | -33 |
| **2.8** | -47 | -20 | -32 | -32 | -32 |
| **2.9** | -46 | -19 | -31 | -31 | -31 |
| **3.0** | -45 | -18 | -30 | -30 | -30 |
| **3.1** | -44 | -17 | -29 | -29 | -29 |
| **3.2** | -43 | -16 | -28 | -28 | -28 |
| **3.3** | -42 | -15 | -27 | -27 | -27 |
| **3.4** | -41 | -14 | -26 | -26 | -26 |
| **3.4** | -40 | -13 | -25 | -25 | -25 |
| **3.6** | -38 | -12 | -24 | -24 | -24 |
| **3.7** | -37 | -11 | -23 | -23 | -23 |
| **3.8** | -36 | -10 | -22 | -22 | -22 |
| **3.9** | -35 | -9 | -21 | -21 | -21 |
| **4.0** | -34 | -8 | -20 | -20 | -20 |
| **4.1** | -33 | -7 | -19 | -19 | -19 |
| **4.3** | -32 | -6 | -18 | -18 | -18 |
| **4.4** | -31 | -5 | -17 | -17 | -17 |
| **4.5** | -30 | -4 | -16 | -16 | -16 |
| **4.6** | -29 | -3 | -15 | -15 | -15 |
| **4.7** | -28 | -2 | -14 | -14 | -14 |
| **4.8** | -27 | -1 | -13 | -13 | -13 |
| **5.0** | -26 | 0 | -12 | -12 | -12 |
| **5.1** | -25 | 1 | -11 | -11 | -11 |
| **5.2** | -24 | 2 | -10 | -10 | -10 |
| **5.3** | -23 | 3 | -9 | -9 | -9 |
| **5.5** | -21 | 4 | -8 | -8 | -8 |
| **5.6** | -20 | 5 | -7 | -7 | -7 |
| **5.8** | -19 | 6 | -6 | -6 | -6 |
| **5.9** | -18 | 7 | -5 | -5 | -5 |
| **6.1** | -17 | 8 | -4 | -4 | -4 |
| **6.2** | -16 | 9 | -3 | -3 | -3 |
| **6.4** | -15 | 10 | -2 | -2 | -2 |
| **6.5** | -14 | 11 | -1 | -1 | -1 |
| **6.7** | -13 | 12 | 0 | 0 | 0 |
| **6.8** | -12 | 13 | 1 | 1 | 1 |
| **7.0** | -11 | 14 | 2 | 2 | 2 |
| **7.1** | -10 | 15 | 3 | 3 | 3 |
| **7.3** | -9 | 16 | 4 | 4 | 4 |
| **7.4** | -8 | 17 | 5 | 5 | 5 |
| **7.6** | -7 | 18 | 6 | 6 | 6 |
| **7.7** | -6 | 19 | 7 | 7 | 7 |
| **7.9** | -5 | 21 | 8 | 8 | 8 |
| **8.2** | -4 | 22 | 9 | 9 | 9 |
| **8.4** | -3 | 23 | 10 | 10 | 10 |
| **8.6** | -2 | 24 | 11 | 11 | 11 |
| **8.8** | -1 | 25 | 12 | 12 | 12 |
| **9.0** | 0 | 26 | 13 | 13 | 13 |
| **9.2** | 1 | 27 | 14 | 14 | 14 |
| **9.4** | 2 | 28 | 15 | 15 | 15 |
| **9.6** | 3 | 29 | 16 | 16 | 16 |
| **9.8** | 4 | 30 | 17 | 17 | 17 |
| **10.1** | 5 | 31 | 18 | 18 | 18 |
| **10.3** | 6 | 32 | 19 | 19 | 19 |
| **10.5** | 7 | 33 | 20 | 20 | 20 |
| **10.7** | 8 | 34 | 21 | 21 | 21 |
| **10.9** | 9 | 35 | 22 | 22 | 22 |
| **11.1** | 10 | 36 | 23 | 23 | 23 |
| **11.1** | > 10 | > 36 | > 23 | > 23 | > 23 |

# 7 TCXO Support

CC13x0 and CC26x0 do not support a
TCXO as clock source. The CC13x2 family of devices has support for TCXO. Two types
of TCXO are supported: clipped sine wave and CMOS output. The TCXO output should be
connected to the X48M\_P input. If a clipped sine wave type is used, a series cap is
required since internal common mode bias is used in this case. The data sheet for
the selected TCXO should be checked for the recommended value for the series
cap.

## 7.1 Hardware

For reference design, see the design files for the [CC1312R Launchpad](http://www.ti.com/lit/zip/swrr160). It is important that the TCXO comply with the requirements in the data sheet. Note the maximum output voltage.

## 7.2 Software

SDK version 4.10 or newer has to be
used. TCXO usage is enabled in syscfg. Under TI Devices → Device Configuration,
select *External 48MHz TCXO* as HF Clock source. When TCXO is selected as
source, select the TCXO type and the TCXO Max Startup Time. It is important that
this time is set correctly. If a too short time is set, the chip could attempt to
switch to the TCXO before this is stable, which again could cause the chip to
malfunction.

When a TCXO is used, the internal load
capacitors have to be reduced to avoid loading the TCXO. The required setting will
be dependent on the selected TCXO. Turning off the capacitor array could cause the
output swing to be too large from some TCXOs. In these cases, the capacitor in the
capacitor array will help reducing the voltage swing. The capacitor array should be
set to a value where the swing on the X48M\_P is within the value set in the CC13x2
data sheet, both for minimum and maximum swing. Care has to be taken when doing the
measurement to avoid that the measurement does not increase the load on this node,
which will impact the measurement result.

In syscfg go to TI Devices → Device
Configuration and tick the box next to “Enable XOSC Cap array modification” and set
the wanted value.

The power driver contains a function
hook PowerCC26X2\_Config.enableTCXOFxn that has to be added to the code. If this
function is not defined, the code will compile but it will hang when the system
requests the radio to turn on. The function hook makes it possible to power the TCXO
from a DIO and turn off the TCXO when the CC13x2 is in standby and turn it on again
in time for a RF operation.

The following code snippet show how
this function can look when the TCXO is powered by a DIO:

```
void Power_enableTCXO(bool turnOn)
{
    if ( turnOn ) {
        // Set corresponding DIO high to enable the TCXO
        GPIO_write(GPIO_TCXO_PIN, 1);
    }
    else {
        // Set the corresponding DIO low to disable the TCXO
        GPIO_write(GPIO_TCXO_PIN, 0);
    }
}
```

SmartRF Studio 2.17 or earlier does
not support TCXO.

## 7.3 Example: Usage of TCXO on CC1312R Launchpad

The CC1312R Launchpad has a TCXO mounted but the crystal is used by default. To select the TCXO the following changes have to be done on the board:

* Remove R5 and R6
* Mount 0Ω resistors for R7 and R8.

In syscfg:

1. Go to TI Devices → Device configuration.
2. Set the following:
   1. Enable XOSC Cap array modification: Tick to enable
   2. XOSC Cap Array Delta: 0xE7
   3. HF Clock Source: External 48 MHz TCXO
   4. TCXO Type: Clipped Sine Type
   5. TCXO Max Start-up Time: 0x14

# 8 Integrated Passive Component (IPC)

An Integrated Passive Component (IPC)
is a matched-filter balun component specially designed or matched to the RF section.
The IPC reduces the component count that saves space and reduces pick-and-place
assembly costs. In addition, there is less risk of a poor RF layout with an IPC
since the RF crosstalk is minimized. [Table 8-1](#X5768) lists the available IPC’s.

Table 8-1 Available IPC’s

| Chip Family | Frequency (MHz) | Vendor | Part Number | Application Note |
| --- | --- | --- | --- | --- |
| CC1101, CC1111, CC1110, CC110L, CC113L, CC115L, CC430 | 430 - 435 | Johanson Technology | [0433BM15A0001](https://www.johansontechnology.com/datasheets/0433BM15A0001/0433BM15A0001.pdf) | [SWRA250](https://www.ti.com/lit/pdf/SWRA250) |
| CC1101, CC1111, CC1110, CC110L, CC113L, CC115L, CC430 | 430 - 435 | Johanson Technology | [0433BM15A0001E-AEC\*1](https://www.johansontechnology.com/datasheets/0433BM15A0001E-AEC/0433BM15A0001E-AEC.pdf) | [SWRA250](https://www.ti.com/lit/pdf/SWRA250) |
| CC1101, CC1111, CC1110, CC110L, CC113L, CC115L, CC430 | 863 - 873 | Johanson Technology | [0868BM15C0001](https://www.johansontechnology.com/datasheets/0868BM15C0001/0868BM15C0001.pdf) | [SWRA250](https://www.ti.com/lit/pdf/SWRA250) |
| CC1101, CC1111, CC1110, CC110L, CC113L, CC115L, CC430 | 863 - 873 | Johanson Technology | [0868BM15C0001E-AEC\*1](https://www.johansontechnology.com/datasheets/0868BM15C0001E-AEC/0868BM15C0001E-AEC.pdf) | [SWRA250](https://www.ti.com/lit/pdf/SWRA250) |
| CC1101, CC1111, CC1110, CC110L, CC113L, CC115L, CC430 | 863 - 928 | Johanson Technology | [0896BM15A0001](https://www.johansontechnology.com/datasheets/0896BM15A0001/0896BM15A0001.pdf) | [SWRA250](https://www.ti.com/lit/pdf/SWRA250) |
| CC1120, CC1121, CC1175, CC1200, CC1201 | 863 - 928 | Johanson Technology | [0900PC15J0013](https://www.johansontechnology.com/datasheets/0900PC15J0013/0900PC15J0013.pdf) | [SWRA407](https://www.ti.com/lit/pdf/SWRA407) |
| CC1101, CC1111, CC1110, CC110L, CC113L, CC115L, CC430 | 902 - 928 | Johanson Technology | [0915BM15A0001](https://www.johansontechnology.com/datasheets/0915BM15A0001/0915BM15A0001.pdf) | [SWRA297](https://www.ti.com/lit/pdf/SWRA297) |
| CC1101, CC1111, CC1110, CC110L, CC113L, CC115L, CC430 | 902 - 928 | Johanson Technology | [0915BM15A0001E-AEC\*1](https://www.johansontechnology.com/datasheets/0915BM15A0001E-AEC/0915BM15A0001E-AEC.pdf) | [SWRA297](https://www.ti.com/lit/pdf/SWRA297) |
| CC13xx | 430-510 | Walsin | [RFBLN2520090YC3T10](http://www.ti.com.cn/cn/lit/an/zhca772/zhca772.pdf) | [SWRA524](https://www.ti.com/lit/pdf/SWRA524) |
| CC13xx | 770-928 | Murata | [LFB18868MBG9E212](https://www.murata.com/products/productdetail?partno=LFB18868MBG9E212) | [SWRA524](https://www.ti.com/lit/pdf/SWRA524) |
| CC13xx | 770-928 | Johanson Technology | [0850BM14E0016](https://www.johansontechnology.com/datasheets/0850BM14E0016/0850BM14E0016.pdf) | [SWRA524](https://www.ti.com/lit/pdf/SWRA524) |
| CC1352R, CC1352P | 863 – 928   2400 - 2480 | Murata | LFB21868MDZ5E757 | [SWRA629](https://www.ti.com/lit/pdf/SWRA629) |
| CC1352R, CC1352P | 430 - 435, 2400 - 2480 | Murata | LFB21433MDZ6F112 | [SWRA629](https://www.ti.com/lit/pdf/SWRA629) |
| CC1352R, CC1352P | 863 – 928   2400 - 2480 | Johanson Technology | 0900PC15A0036 | [SWRA629](https://www.ti.com/lit/pdf/SWRA629) |
| CC2420 | 2400 - 2480 | Anaren | [BD2425N50200A00](https://www.anaren.com/catalog/xinger/balun-transformers) | [SWRA155](https://www.ti.com/lit/pdf/SWRA155) |
| CC2430 | 2400 - 2480 | Anaren | [BD2425N50200A00](https://www.anaren.com/catalog/xinger/balun-transformers) | [SWRA156](https://www.ti.com/lit/pdf/SWRA156) |
| CC2430, CC2480 | 2400 - 2480 | Johanson Technology | [2450BM15A0001](https://www.johansontechnology.com/datasheets/2450BM15A0001/2450BM15A0001.pdf) |  |
| CC2520 | 2400 - 2480 | Johanson Technology | [2450BM15B0002](https://www.johansontechnology.com/datasheets/2450BM15B0002/2450BM15B0002.pdf) |  |
| CC2500, CC2510 | 2400 - 2480 | Johanson Technology | [2450BM15B0003](https://www.johansontechnology.com/datasheets/2450BM15B0003/2450BM15B0003.pdf) |  |
| CC1352R, CC1352P, CC2620, CC2630, CC2640, CC2650 | 2400 - 2480 | Murata | [LFB182G45BG5D920](https://www.murata.com/~/media/webrenewal/products/balun/balun/forconnectivity/lfb182g45bg5d920.ashx?la=en) |  |
| CC1352R, CC1352P, CC2620, CC2630, CC2640, CC2650 | 2400 - 2480 | Johanson Technology | [2450BM14G0011](https://www.johansontechnology.com/datasheets/2450BM14G0011/2450BM14G0011.pdf) | [SWRA572](https://www.ti.com/lit/pdf/SWRA572) |
| CC1352R, CC1352P, CC2620, CC2630, CC2640, CC2650 | 2400 - 2480 | Johanson Technology |  |  |
| CC13xP, CC26xP  For HPA port, TX only. | 2400 - 2480 | Murata | LFB182G45BGEF296 | [SWRA729](https://www.ti.com/lit/pdf/swra729) |

# 9 Optimum Load Impedance

The matching environment for optimum performance is determined through a combination
of load- and source-pull measurements, given as a terminating load/source impedance.
This requires comprehensive measurements to characterize the nonlinear response of
the RF front-end.

The parameters considered include:

* TX Output Power
* TX Efficiency
* TX Harmonic Power Levels
* TX Output Spectrum
* RX Sensitivity

The operating conditions considered include:

* Frequency
* Voltage Range
* TX Power Settings
* Package Parasitics

Additionally, the effect of temperature variation on TX/RX performance must also be
considered.

These impedance locations are typically located in different regions of the Smith
chart and a design space giving the best tradeoff between TX and RX performance is
identified for a given set of operating conditions.

The identified target impedance(s) can also be highly dependent on the power and
ground planes of the application circuit as well as accurate measurement system
calibration, along with the effects of differential and common current components
due to the PCB layout. Whilst detailed simulations of the PCB using EDA tools can
add confidence to a design, simulation inaccuracies (such as component models) add
additional errors that can be difficult to account for.

Due to the number of parameters that must be considered and amount of testing
required for a robust design, it is strongly recommended to follow the reference
design.

# 10 PA Table

The PA table for the various devices is provided
in SmartRF Studio. The txpower values used in the
table are selected to provide as low as possible
device to device variation. In addition, the
txpower setting has a built-in temperature
compensation giving a very low output variation as
a function of temperature.

The PA used is designed to be highly effective on
maximum power. With maximum power the PA is in
saturation and due to this the device to device
variation is low. For lower power settings, the PA
is in the linear region and the output power will
therefore be dependent on the transistor gain,
which will have a higher device to device
variation. For the output powers not covered by
the PA table provided by SmartRF Studio, it has
not been possible to find a txpower setting that
gives a low device to device variation or a stable
output power over temperature.

It
is possible for customers to generate a custom PA
table if that is needed. The output power of a FEM
will typically not be constant as a function of
temperature and it could be possible to find a
txpower value that gives a more constant output
power over temperature when using a FEM.

The parameter txPower contains temp. coefficient
setting, gain setting, IB setting and the TX BOOST
bit:

* txPower[15:9]: temp
  coefficient
* txPower[8]: TX BOOST
  bit
* txPower[7:6]: Gain
* txPower[5:0]: IB

The temperature coefficient is applied to
automatically compensate the IB setting based on
the temperature readout of AON\_BATMON\_TEMP.

There are three different gain settings and for
each gain setting the IB can be adjusted from 0x0
to 0x3F resulting in 64\*3 192 available settings
for TX output power. The temperature coefficient
is given as an input in addition to the requested
gain and IB setting.Based on the readout from the
temperature sensor and the temperature coefficient
setting the IB is adjusted. IB is adjusted based
on [Equation 3](#ID-5ED24207-4C60-4AEC-D748-FB097637EB9A).

Equation 3.

A
custom TX power table should be generated by the
following method (to obtain constant Tx power over
temperature for a certain Tx parameter value):

1. Room
   temp setting: Adjust the gain and IB setting to
   get the requested output power level at room
   temperature with temperature compensation
   disabled. This setting will be the
   Ib\_requested.
2. Low temp setting: Use the
   same gain setting and adjust the IB setting to get
   the closest output power level from step 1 at low
   temperature. This setting will be the
   Ib\_low\_temp.
3. High
   temp setting: Use the same gain setting and adjust
   the IB setting to get the closest output power
   level from step 1 at high temperature. This
   setting will be the Ib\_high\_temp.
4. Calculate temp coefficient.
   Use the IB settings from the low and high
   temperature measurements to calculate the
   temperature coefficients. The temp coefficient is
   based on a linear approximation between the two
   temperature extremes and calculated as shown in
   [Equation 4](#ID-F4549768-D0F7-4142-CEB0-4BF2AE762A75).

   Equation 4.

   Equation 5.

   I
   b

   =

   I

   b

   r
   e
   q
   u
   e
   s
   t
   e
   d
   +

   (
   T
   e
   m
   p
   e
   r
   a
   t
   u
   r
   e

   -

   25

   d
   e
   g
   )
   ·
   t
   e
   m
   c
   o
   e
   f
   f
   256

   Equation 6.

   t
   e
   m
   p
   \_
   c
   o
   e
   f
   f

   =

   256
   ·

   (
   I
   b
   \_
   h
   i
   g
   h
   \_
   t
   e
   m
   p
   -
   I
   b
   \_
   l
   o
   w
   \_
   t
   e
   m
   p
   )

   h
   i
   g
   h
   \_
   t
   e
   m
   p
   -
   l
   o
   w
   \_
   t
   e
   m
   p
5. Repeat step [1](#T5659416-253)-[3](#T5659416-254) for all the desired power levels.

# 11 Power Supply Configuration

## 11.1 Introduction

The CC13xx/CC26xx devices have three power rails
that are exposed on external pins: VDDS, VDDR and
DCOUPL. VDDS is the main power source for the
wireless microcontroller and must be supplied
externally with 1.8V to 3.8V. VDDR is an internal
power rail that is supplied from the internal
DC/DC converter, or the internal Global LDO, but
can be powered from an external supply. VDDR is
regulated to approximately 1.68V, or 1.95V when
running in boost mode for maximum output power in
sub-1GHz bands. In boost mode, a minimum VDDS
voltage of 2.1V is required. DCOUPL is supplied
internally by either Digital LDO or Micro LDO
depending on the power state. This power rail is
trimmed to approximately 1.28V and requires an
external decoupling capacitor of 1µF.

## 11.2 DC/DC Converter Mode

Figure 11-1 DC/DC Mode

Note: The VDDS\_DCDC pin is not present on all devices.

Maximum efficiency is obtained by using the internal DC/DC converter, and it requires an external inductor (LDCDC) and capacitor (CDCDC). The components should be placed as close as possible to the CC13xx/CC26xx device and it is important to have a short current return path for from the CDCDC ground to the pad on the chip (see [Section 4.8](GUID-5530AC18-0DD1-4A3C-BCD7-329AD5FF3772.html#GUID-5530AC18-0DD1-4A3C-BCD7-329AD5FF3772)). In addition, the bulk capacitor on VDDS should be placed close to the VDDS\_DCDC-pin. The actual value of LDCDC, CDCDC and CBULK vary from device to device. For the actual values, see the device-specific reference design.

When operating in DC/DC mode, the power system
dynamically switches between the Global LDO and DC/DC converter depending on the
required load to achieve maximum efficiency. If VDDS drops below 2.0V, the DC/DC
converter will be less efficient than the LDO and the device will run in global LDO
mode. For systems operating with VDDS less than 2.0V, consider either global LDO or
external regulator mode to save component cost and board area.

The software setup required to use the DCDC
converter or the GLDO operation is done in the
Customer Configuration (CCFG) register bank.

For devices that use SDK up to version 5.x
(CC2640R2), the settings below must be made to the
file ccfg.c.

```
#ifndef SET_CCFG_MODE_CONF_DCDC_RECHARGE
#define SET_CCFG_MODE_CONF_DCDC_RECHARGE       0x0   // Use the DC/DC during recharge in powerdown
// #define SET_CCFG_MODE_CONF_DCDC_RECHARGE    0x1   // Do not use the DC/DC during recharge in powerdown
#endif
#ifndef SET_CCFG_MODE_CONF_DCDC_ACTIVE
#define SET_CCFG_MODE_CONF_DCDC_ACTIVE         0x0   // Use the DC/DC during active mode
// #define SET_CCFG_MODE_CONF_DCDC_ACTIVE      0x1   // Do not use the DC/DC during active mode
#endif
```

For devices that use SDK version 6.x and above, this is set up in the section TI DEVICES
followed by Device Configuration of the Sysconfig file as indicated in the following image.

## 11.3 Global LDO Mode

Figure 11-2 Global LDO Mode

Note: The VDDS\_DCDC pin is not present on all devices.

To save cost and PCB area the DC/DC inductor can be removed and VDDR can be supplied from the Global LDO at the cost of higher power consumption. In this mode a bulk capacitor on VDDR is still required and should be placed close to the VDDR pin. The VDDS\_DCDC-pin must be connected to VDDS and the DCDC\_SW should be left floating to avoid short circuiting VDDS if the DC/DC converter is mistakenly enabled from software. The VDDS bulk capacitor does not need to be close to the VDDS\_DCDC pin and should rather be placed close to the VDDS pin.

The software setup
required to use the DCDC converter or the GLDO operation is done in the Customer
Configuration (CCFG) register bank.

For devices that use SDK up to version 5.x (CC2640R2), the settings below must be
made to the file ccfg.c.

```
#ifndef SET_CCFG_MODE_CONF_DCDC_RECHARGE
// #define SET_CCFG_MODE_CONF_DCDC_RECHARGE    0x0   // Use the DC/DC during recharge in powerdown
#define SET_CCFG_MODE_CONF_DCDC_RECHARGE       0x1   // Do not use the DC/DC during recharge in powerdown
#endif
#ifndef SET_CCFG_MODE_CONF_DCDC_ACTIVE
// #define SET_CCFG_MODE_CONF_DCDC_ACTIVE      0x0   // Use the DC/DC during active mode
#define SET_CCFG_MODE_CONF_DCDC_ACTIVE         0x1   // Do not use the DC/DC during active mode
#endif
```

For devices that use SDK version 6.x
and above, this is set up in the section TI DEVICES followed by Device Configuration
of the Sysconfig file as indicated in the following image.

## 11.4 External Regulator Mode

Figure 11-3 External Regulator Mode

In external regulator mode, neither the Global LDO
nor the DC/DC is active and both VDDS and VDDR
must be powered from the same rail. The regulators
are disabled by connecting VDDS\_DCDC to ground.
Note that the maximum voltage level on the
external regulator is limited by VDDR and should
not exceed the absolute maximum rating defined in
the device-specific data sheet. To achieve maximum
output power for the sub-1GHz PA, the supply
voltage should be set to 1.95V.

Note: External Regulator Mode is only supported on
CC26x0 devices.

# 12 Board Bring-Up

Before starting to develop software or doing range testing, It is recommended to do conducted measurements to verify that the board has the expected performance. Typically, the sensitivity, output power, harmonics, and current consumption should be measured to verify the hardware design.

The required measurements depend on the type of
board and application. If it is a design with 10m range requirement the checkout
does not need to be as detailed as for a design with a range extender. For the
latter, and other designs that require high performance, having access to a spectrum
analyzer and a signal generator with the option to send RF packets is highly
recommended.

Different measurement methods are discussed in the following sections. It is up to the reader to select the methods applicable for their board.

## 12.1 Power On

When powering on the board for the first time, check that the voltages on the following pins are as expected.

**CC13xx and CC26xx**

* VDDR = 1.68 V for CCFG\_FORCE\_VDDR\_HH = 0
* VDDR = 1.95 V for CCFG\_FORCE\_VDDR\_HH = 1
* DCOUPL = 1.27 V

Do NOT measure directly on the X24M\_P and X24M\_N nor X48M\_P and X48M\_N pins since this could brick the device.

## 12.2 RF Test: SmartRF Studio

In order to use SmartRF Studio for testing, the board needs a connector that enables a debugger to be connected directly to the RF chip:

* For the CC13xx and CC26xx, an XDS100v3, XDS110 or XDS200 should be used.

The required pins in cJTAG-mode are VDDS, GND, RESET, TCK and TMS.

1. Connect a debugger to the board. Open SmartRF Studio and verify that the device is visible in the list of connected devices.
2. Place two good known boards with 2m distance. In this context “good known
   boards“ are EM’s or LaunchPads from TI. Use a predefined PHY setting in SmartRF
   Studio that is a closest match to the PHY that will be used in the final
   product
3. Set one board to PacketRX and the other to PacketTX and transmit 100 packets. Confirm that the packets are received and note the RSSI for the received packets.
4. Replace the board used in TX with the device under test (DUT). Repeat the test described in [3](#T5659416-221).
5. Replace the board used in RX with the DUT. Replace the board used in TX with a good known board. Repeat the test described in [3](#T5659416-221).
6. If possible, the measurements should be done with a good known antenna first and then repeated with the antenna that is going to be used in the final design later. A poorly tuned antenna could cause a significant loss in sensitivity/output power.
7. If the results are satisfactory, change the settings from the predefined setting to the RF settings planned to be used in the final product. Repeat the tests described in [3](#T5659416-221) to [5](#T5659416-222) with the wanted RF settings.

If the RSSI deviates from the reference, the schematic and layout should be reviewed. Note that if the network between the RF ports and the antenna on the customer board is different from the TI evaluation board, the losses due to SAW filters and switches must be to be taken into consideration.

## 12.3 RF Test: Conducted Measurements

For high performance designs it is highly recommended to perform conducted measurements to verify the performance before setting up an RF link.

### 12.3.1 Sensitivity

1. Disconnect the antenna and perform conducted measurements at
   the SMA connector or solder a semi rigid coax cable at the 50Ω point.
2. Configure the board under test and use the PacketRX option in
   SmartRF Studio similar to the test described in [Section 12.2](GUID-543C2585-FAEA-4D63-872F-4DE9AC234517.html#GUID-543C2585-FAEA-4D63-872F-4DE9AC234517). In PacketRX mode, you can set an expected packet count.
3. Preferred: Use a signal generator that is capable of
   transmitting data packets. Remember to set up the sync word and CRC
   correctly.
4. If a signal generator is not available, use an EM/LaunchPad as
   a transmitter. Use coax cables and attenuation between the EM/LauncPad SMA
   connector and the 50Ω point on the custom board. It is difficult to get an
   accurate number using this method since the exact values of output power and
   attenuation are normally not known. Some energy will also travel over the air
   from the EM to the DUT. In addition, background noise could impact the results.
   To get more accurate results, the receiver should be placed in a shielded
   box.
5. SmartRF Studio will calculate the packet error rate (PER) and
   bit error rate (BER).

If the wanted RF settings are
different from the predefined setting, PER vs level should be run in addition. The
input power level should be increased in 1- 2dB steps from the sensitivity limit to
around 0 dBm. For each power level, transmit at least 100 packets and record the
PER. If the AGC settings are not optimal it is common that the PER for some of the
steps will be above 0 (residual PER) and if that is the case the AGC settings have
to be reviewed.

**If the conducted sensitivity is
poor:**

* Are the settings the same as the recommended values from
  SmartRF Studio? If the sensitivity is good when using SmartRF Studio and not
  with the settings used for the project the settings have to be reviewed.
* What is the frequency difference between the DUT and the
  signal source? Frequency offset can be measured by transmitting an un-modulated
  continuous wave
* Is the schematic, including all component values, in
  accordance with the reference design?
* Is the layout in accordance with the reference design?

### 12.3.2 Output Power

1. Disconnect the antenna and perform conducted measurements at the SMA connector
   or solder a semi-rigid coax cable at the 50Ω point.
2. Preferred: Use a spectrum analyzer (SA). Use 1MHz RBW for measuring output
   power.
3. If an SA is not available use an EM or Launchpad with a SMA connection point.
   Use coax cables and attenuation between the EM/LaunchPad SMA connector and the
   50Ω point on the custom board. Use SmartRF Studio and set the EM/Launchpad in
   continuous RX and read the RSSI. Note that the RSSI has a given tolerance so the
   measurement will not be as accurate as the preferred method.

## 12.4 Software Bring-Up

**For CC13xx:**

Basic examples for RF and other drivers can be found under TI Drivers under software -> Examples -> Development Tools -> <Development board in question> at <http://dev.ti.com/tirex/#/>. Before starting to write own software it is recommended to run the RF examples that are closest to the wanted application unmodified and verify that they work. Then, if required, change the RF settings to the wanted data rate, and so forth.

**For CC26xx and Bluetooth Low Energy:**

For more information, see [Initial Board Bring Up](http://software-dl.ti.com/lprf/simplelink_cc2640r2_latest/docs/blestack/ble_user_guide/html/ble-stack-3.x/custom-hardware.html#initial-board-bring-up) on recommended software images to run initially.

Basic examples for RF and other drivers can be
found under TI Drivers under software -> Examples -> Development Tools ->
<Development board in question> at [https://dev.ti.com/tirex/#/](http://dev.ti.com/tirex/#/).

## 12.5 Hardware Troubleshooting

This section covers some of the common causes for poor performance.

### 12.5.1 No Link: RF Settings

To get a link between two RF chips the two RF chips have to operate on the same frequency and with the same RF settings. This means that the two have to use the same data rate, deviation and modulation format. A common mistake is that the sync word has been set differently on the two devices, they have to be equal.

### 12.5.2 No Link: Frequency Offset

For narrow band systems a too large frequency offset between the TX and RX devices could result in no link or a very poor link.

The minimum required RX bandwidth to ensure reception is given by:

Equation 7. RX BW = Signal Bandwidth + 4\*ppm Crystal \* RF Frequency of Operation

For FSK the signal bandwidth can be approximated as data rate + 2\*frequency deviation (Carson’s rule).

For CC13x0: For low data rates, the bit repetition patch [*CC13x0 Low Data Rate Operation*](https://www.ti.com/lit/pdf/SWRA566) should be used. If this patch is not used, the frequency offset tolerance could be under 10 ppm, which could cause loss of link with a normal crystal tolerance.

### 12.5.3 Poor Link: Antenna

An antenna needs a matching network in order to tune and reduce the mismatch losses of the antenna. If the antenna is not tuned, energy will be lost both in TX and RX and the link budget will be lower. For more details, see [Section 5](GUID-57F0D63B-9ED2-46D4-8FCD-11B30990B401.html#GUID-57F0D63B-9ED2-46D4-8FCD-11B30990B401).

### 12.5.4 Bluetooth Low Energy: Device Does Advertising But Cannot Connect

If using the 32kHz crystal oscillator as RTC
source:

* Incorrect load capacitors for the 32.768kHz crystal – causes frequency
  offset
* 32kHz crystal does not start up (incorrect load capacitors, crystal missing,
  soldering issues) – the device defaults to run the RTC from the 48MHz RC
  oscillator at 31.25kHz. For more information, see the *PRCM* chapter in the
  [*CC13x0, CC26x0 SimpleLink™ Wireless MCU*](https://www.ti.com/lit/pdf/SWCU117) and [*C13x2, CC26x2 SimpleLink™ Wireless MCU*](https://www.ti.com/lit/pdf/SWCU185)  technical
  reference manuals.

If using the 32kHz RC oscillator as RTC
source:

* Calibration is not configured correctly. For more information, see the Bluetooth Low Energy Stack User's Guide that is provided with the SDK.

Incorrect RTC frequency will lead to the device missing the connection events and thus breaking the link with the central device.

To debug this problem, the 32kHz clock can be
output on an I/O pin and measured with a frequency counter. For more information on
how to do this, see the *I/O* chapter in the [*CC13x0, CC26x0 SimpleLink™ Wireless
MCU*](https://www.ti.com/lit/pdf/SWCU117) and [*C13x2, CC26x2 SimpleLink™ Wireless MCU*](https://www.ti.com/lit/pdf/SWCU185) technical
reference manuals. By outputting the clock on a pin, you will always measure the
\_selected\_ RTC clock source, as well as be able to measure without affecting the
clock source (which probing the crystal for example will do).

If using a 32.768kHz crystal make sure the crystal
part is within the requirements outlined in the device-specific CC13xx/CC26xx data
sheets. Also make sure that the load capacitors are dimensioned properly as shown in
[Section 6.3](GUID-B48F3148-4285-4620-B69B-F1902CF95EDC.html#GUID-B48F3148-4285-4620-B69B-F1902CF95EDC).

Verify that the BLE-Stack has been configured with
the correct Sleep Clock Accuracy. The default setting is 40ppm and can be adjusted
with the HCI\_EXT\_SetSCACmd API, see hci.h or the TI Vendor Specific API Guide
included in the SDK.

### 12.5.5 Poor Sensitivity: DCDC Layout

It is highly recommended to follow the reference
design when it comes to the components connected to the DCDC\_SW pin. The shunt
capacitor following the series inductor from the DCDC\_SW pin has to have a short
return path to chip ground from the ground pad (see [Section 4.8](GUID-5530AC18-0DD1-4A3C-BCD7-329AD5FF3772.html#GUID-5530AC18-0DD1-4A3C-BCD7-329AD5FF3772)). A poor DCDC layout could cause more than 5dB loss in sensitivity. To check if
the sensitivity is limited by the DCDC, turn off the DCDC in the CCFG.c file.

### 12.5.6 Poor Sensitivity: Background noise

A RF channel will receive all radio traffic in the selected frequency span. In addition to the wanted signal the channel will also receive background noise. Part of the background noise is other RF traffic on the selected band. To receive a RF packet the received signal has to have a given SNR. If the background noise increases, the practical sensitivity will be poorer.

Example: If the conducted sensitivity is -110dBm,
the required SNR is 7dB and the background noise is -100dBm, the practical radiated
sensitivity will be -93dBm.

Before doing a range test the background noise
should be measured. One method is to turn off all known TX sources, attach a
Launchpad or a known good board to SmartRF Studio, select the *Continuous RX*
tab and press play. The average of the resulting graph could be used as an input to
find the practical sensitivity.

### 12.5.7 High Sleep Power Consumption

* Note that the chip is not going into the lowest power modes when a debugger is
  connected.
* Software: Use the pinStandby or pinShutdown examples in the relevant SDK.
* When measuring current draw on a Launchpad, remove all jumpers.
* Ensure that every IC on the board is powered down.
* If the application is configured to use the 32kHz crystal (set in CCFG.c),
  check that this is connected and that the oscillator is running.

# 13 References

* [TXLine Transmission Line Calculator](https://www.cadence.com/en_US/home/tools/system-analysis/rf-microwave-design/awr-tx-line.html)
* Texas Instruments, [*Antenna Selection Quick
  Guide*](https://www.ti.com/lit/pdf/SWRA351)
* Texas Instruments, [*Antenna Selection
  Guide*](https://www.ti.com/lit/pdf/SWRA161)
* [CC-Antenna-DK2](https://www.ti.com/tool/CC-ANTENNA-DK2)
* Texas Instruments, [*CC-Antenna-DK2 and Antenna
  Measurements Summary*](https://www.ti.com/lit/pdf/SWRA496)
* Texas Instruments, [CC13x0 Low Data Rate
  Operation](https://www.ti.com/lit/pdf/SWRA566)
* Texas Instruments, [*Monopole PCB Antenna with Single
  or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA227)
* Texas Instruments, [*LAUNCHXL-CC1310 Design Files*](https://www.ti.com/lit/zip/swrc319)
* Texas Instruments, [*SimpleLink
  sub-1GHz CC1312R Wireless (MCU) LaunchPad Dev Kit 868MHz/915MHz
  App*](https://www.ti.com/lit/zip/swrr160)
* Texas Instruments, [*2.4-GHz Inverted F
  Antenna*](https://www.ti.com/lit/pdf/SWRU120)
* Texas Instruments, [*LAUNCHXL-CC2640R2 Design Files*](https://www.ti.com/lit/zip/swrc335)
* Texas Instruments, [*CC26x2R
  LaunchPad Design Files*](https://www.ti.com/lit/zip/swrc346)
* Texas Instruments, [*Miniature Helical PCB Antenna for
  868 MHz or 915/920 MHz*](https://www.ti.com/lit/pdf/SWRA416)
* Texas Instruments, [*LAUNCHXL-CC1350 Design Files*](https://www.ti.com/lit/zip/swrc320)
* Texas Instruments, [*Monopole PCB Antenna with Single
  or Dual Band Option*](https://www.ti.com/lit/pdf/SWRA227)
* Texas Instruments, [*2.4-GHz Inverted F
  Antenna*](https://www.ti.com/lit/pdf/SWRU120)
* Texas Instruments, [*CC1352R
  LaunchPad Design Files*](https://www.ti.com/lit/zip/swrc345)
* Texas Instruments, [*LAUNCHXL-CC1352P-2 Design Files*](https://www.ti.com/lit/zip/swrc350)
* Texas Instruments, [*LAUNCHXL-CC1352P-4 Design Files*](https://www.ti.com/lit/zip/swrc352)
* Texas Instruments, [*CC1350STK
  Design Files*](https://www.ti.com/lit/zip/swrc321)
* Texas Instruments, [*CC1125 BoosterPack™ for 868/915
  MHz BOOSTXL-CC1125*](https://www.ti.com/lit/pdf/SWRA520)
* Texas Instruments, [*Matched Integrated Passive
  Component for 868 / 915 MHz operation with the CC112x, CC117x &
  CC12xx high performance radio series*](https://www.ti.com/lit/pdf/SWRA407)
* Texas Instruments, [*Johanson Technology, Inc. Highly
  temperature-stable Impedance Matched RF Front End Differential
  Balun-Band Pass Filter Integrated Ceramic Component*](https://www.ti.com/lit/pdf/SWRA297)
* Texas Instruments, [*CC1310 Integrated Passive
  Component for 779-928 MHz*](https://www.ti.com/lit/pdf/SWRA524)
* Texas Instruments, [*Matched Filter Balun for CC1352
  and CC1352P*](https://www.ti.com/lit/pdf/SWRA629)
* Texas Instruments, [*Anaren 0404 (BD2425N50200A00)
  balun optimized for Texas Instruments CC2420 Transceiver*](https://www.ti.com/lit/pdf/SWRA155)
* Texas Instruments, [*Anaren 0404 (BD2425N50200A00)
  balun optimized for Texas Instruments CC2430 Transceiver*](https://www.ti.com/lit/pdf/SWRA156)
* Texas Instruments, [*Johanson Balun for the CC26xx
  Device Family*](https://www.ti.com/lit/pdf/SWRA572)
* Texas Instruments, [*CC13x0, CC26x0 SimpleLink™
  Wireless MCU Technical Reference Manual*](https://www.ti.com/lit/pdf/SWCU117)
* Texas Instruments, [*C13x2, CC26x2 SimpleLink™ Wireless
  MCU Technical Reference Manual*](https://www.ti.com/lit/pdf/SWCU185)