Source: https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf
Retrieved: 2026-11-09

[Upgraded from PDF to HTML datasheet]

# SCLS264 Data sheet | TI.com

Data Sheet

# SNx4AHCT125 Quadruple Bus Buffer Gates With 3-State Outputs

# 1 Features

- Inputs are TTL-voltage compatible
- Latch-up performance exceeds 250mA   
   per JESD 17

# 2 Applications

- [Enable or disable a digital signal](https://training.ti.com/tlm-app-enable)
- [Controlling an indicator LED](https://training.ti.com/tlm-app-drivingled)
- [Debounce a switch](https://training.ti.com/debounce-switch)
- [Eliminate slow or noisy input signals](https://training.ti.com/eliminate-slow-or-noisy-input-signals)

# 3 Description

The ’AHCT125 devices are quadruple bus buffer
gates featuring independent line drivers with 3-state outputs. Each output is
disabled when the associated output-enable (OE) input is high.
When OE is low, the respective gate passes the data from the A
input to its Y output.

For the high-impedance state during power up or
power down, OE should be tied to VCC through a
pullup resistor; the minimum value of the resistor is determined by the
current-sinking capability of the driver.

Device Information

| PART NUMBER | RATING | PACKAGE[(1)](#NOTE1) |
| --- | --- | --- |
| SN54AHCT125 | Military | J (CDIP, 14) |
| W (CFP, 14) |
| FK (LCCC, 20) |
| SN74AHCT125 | Commercial | D (SOIC, 14) |
| DB (SSOP, 14) |
| DGV (TVSOP, 14) |
| N (PDIP, 14) |
| NS (SOP, 14) |
| PW (SOP, 14) |
| RGY (VQFN, 14) |
| BQA (WQFN, 14) |

(1) For more information, see [Section 11](GUID-B62798D0-6148-457A-A4F4-03228BE88D59.xml).

![GUID-20230612-SS0I-ZXXW-0N1H-PSFPFVD90SNW-low.png](https://www.ti.com/ods/images/SCLS264R/GUID-20230612-SS0I-ZXXW-0N1H-PSFPFVD90SNW-low.png "SN54AHCT125 SN74AHCT125 Logic Diagram (Positive Logic)")

Pin numbers are for D, DB, DGV,
J, N, NS, PW, RGY, and W packages.

Logic Diagram (Positive Logic)

# 4 Pin Configuration and Functions

![GUID-20230612-SS0I-9BXW-LLJZ-4C20GMJ11TW6-low.svg](https://www.ti.com/ods/images/SCLS264R/GUID-20230612-SS0I-9BXW-LLJZ-4C20GMJ11TW6-low.svg "SN54AHCT125 SN74AHCT125 SN54AHCT125 J or W Package,SN74AHCT125 D, DB, DGV, N, NS, or PW Package (Top View)")Figure 4-1 SN54AHCT125 J or W Package,  
SN74AHCT125 D, DB, DGV, N, NS, or PW Package (Top View)

![GUID-20230612-SS0I-TCFF-KH0K-TC0STSZD00DQ-low.svg](https://www.ti.com/ods/images/SCLS264R/GUID-20230612-SS0I-TCFF-KH0K-TC0STSZD00DQ-low.svg "SN54AHCT125 SN74AHCT125 SN54AHCT125 FK Package, (Top View)")Figure 4-3 SN54AHCT125 FK Package, (Top View)

![GUID-20230612-SS0I-NKCS-KBZF-CZCWJ92FJTRS-low.svg](https://www.ti.com/ods/images/SCLS264R/GUID-20230612-SS0I-NKCS-KBZF-CZCWJ92FJTRS-low.svg "SN54AHCT125 SN74AHCT125 SN74AHCT125 RGY or BQA Package (Top View)")Figure 4-2 SN74AHCT125 RGY or BQA Package (Top View)

Table 4-1 Pin Functions

| PIN | | | I/O | DESCRIPTION |
| --- | --- | --- | --- | --- |
| NAME | D, DB, DGV, N,  NS, J, W, PW, RGY or BQA | FK |
| 1 OE | 1 | 2 | I | Output enable for gate 1 |
| 1A | 2 | 3 | I | Gate 1 input |
| 1Y | 3 | 4 | O | Gate 1 output |
| 2 OE | 4 | 6 | I | Output enable for gate 2 |
| 2A | 5 | 8 | I | Gate 2 input |
| 2Y | 6 | 9 | O | Gate 2 output |
| 3 OE | 10 | 14 | I | Output enable for gate 3 |
| 3A | 9 | 13 | I | Gate 3 input |
| 3Y | 8 | 12 | O | Gate 3 output |
| 4 OE | 13 | 19 | I | Output enable for gate 4 |
| 4A | 12 | 18 | I | Gate 4 input |
| 4Y | 11 | 16 | O | Gate 4 output |
| GND | 7 | 10 | — | Ground pin |
| NC | — | 1, 5, 7,  11, 15, 17 | — | No internal connection |
| VCC | 14 | 20 | — | Power pin |

# 5 Specifications

## 5.1 Absolute Maximum Ratings

over operating free-air temperature range (unless otherwise noted)
[(1)](#SCLS2646576)

|  | | | MIN | MAX | UNIT |
| --- | --- | --- | --- | --- | --- |
| VCC | Supply voltage range | | –0.5 | 7 | V |
| VI | Input voltage range[(2)](#SCLS2648828) | | –0.5 | 7 | V |
| VO | Output voltage range[(2)](#SCLS2648828) | | –0.5 | VCC + 0.5 | V |
| IIK | Input clamp current | VI < 0 |  | –20 | mA |
| IOK | Output clamp current | VO < 0 or VO > VCC |  | ±20 | mA |
| IO | Continuous output current | VO = 0 to VCC |  | ±25 | mA |
|  | Continuous current through VCC or GND | |  | ±50 | mA |
| Tstg | Storage temperature range | | –65 | 150 | °C |

(1) Stresses beyond those listed under *Absolute Maximum Ratings* may cause
permanent damage to the device. These are stress ratings only, and functional
operation of the device at these or any other conditions beyond those indicated
under *Recommended Operating Conditions* is not implied. Exposure to
absolute-maximum-rated conditions for extended periods may affect device
reliability.

(2) The input and output voltage ratings may be exceeded if the input and output current ratings are observed.

## 5.2 Recommended Operating Conditions[(1)](#SCLS2644195)

|  |  | SN54AHCT125 | | SN74AHCT125 | | UNIT |
| --- | --- | --- | --- | --- | --- | --- |
| MIN | MAX | MIN | MAX |
| VCC | Supply voltage | 4.5 | 5.5 | 4.5 | 5.5 | V |
| VIH | High-level input voltage | 2 |  | 2 |  | V |
| VIL | Low-level input voltage |  | 0.8 |  | 0.8 | V |
| VI | Input voltage | 0 | 5.5 | 0 | 5.5 | V |
| VO | Output voltage | 0 | VCC | 0 | VCC | V |
| IOH | High-level output current |  | –8 |  | –8 | mA |
| IOL | Low-level output current |  | 8 |  | 8 | mA |
| Δt/Δv | Input transition rise or fall rate |  | 20 |  | 20 | ns/V |
| TA | Operating free-air temperature | –55 | 125 | –40 | 85 | °C |

(1) All unused inputs of the device must be held at VCC or GND to ensure proper device operation. Refer to the TI application report, *Implications of Slow or Floating CMOS Inputs*, literature number [SCBA004](https://www.ti.com/lit/pdf/SCBA004).

## 5.3 Thermal Information

| THERMAL METRIC[(1)](#GUID-894FEEFF-EA0F-407D-A89A-0E48DCD30CC8) | | SNx4AHCT125 | | | | | | | | UNIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D (SOIC) | DB (SSOP) | DGV (TVSOP) | N (PDIP) | NS (SO) | PW (TSSOP) | RGY (VQFN) | BQA (WQFN) |
| 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 |
| θJA | Package thermal impedance | 124.5 | 96 | 127 | 80 | 76 | 147.7 | 87.1 | 88.3 | °C/W |

(1) For more information about traditional and new thermal metrics, see the [*Semiconductor and IC package thermal metrics*](https://www.ti.com/lit/pdf/SPRA953) application report.

## 5.4 Electrical Characteristics

over operating free-air temperature range (unless
otherwise noted) 

| PARAMETER | TEST CONDITIONS | | VCC | TA = 25°C | | | SN54AHCT125 | | SN74AHCT125 | | UNIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MIN | TYP | MAX | MIN | MAX | MIN | MAX |
| VOH | IOH = –50 µA | | 4.5 V | 4.4 | 4.5 |  | 4.4 |  | 4.4 |  | V |
| IOH = –8 mA | | 3.94 |  |  | 3.8 |  | 3.8 |  |
| VOL | IOL = 50 µA | | 4.5 V |  |  | 0.1 |  | 0.1 |  | 0.1 | V |
| IOL = 8 mA | |  |  | 0.36 |  | 0.44 |  | 0.44 |
| II | VI = 5.5 V or GND | | 0 V to   5.5 V |  |  | ±0.1 |  | ±1[(1)](#SCLS2644303) |  | ±1 | µA |
| IOZ | VO = VCC or GND | | 5.5 V |  |  | ±0.25 |  | ±2.5 |  | ±2.5 | µA |
| ICC | VI = VCC or GND, | IO = 0 | 5.5 V |  |  | 2 |  | 20 |  | 20 | µA |
| ΔICC[(2)](#SCLS2646202) | One input at 3.4 V,  Other inputs at VCC or GND | | 5.5 V |  |  | 1.35 |  | 1.5 |  | 1.5 | mA |
| Ci | VI = VCC or GND | | 5 V |  | 4 | 10 |  |  |  | 10 | pF |
| Co | VO = VCC or GND | | 5 V |  | 15 |  |  |  |  |  | pF |

(1) On products compliant to MIL-PRF-38535, this parameter is not
production tested at VCC = 0 V.

(2) This is the increase in supply current for each input at one of
the specified TTL voltage levels, rather than 0 V or VCC.

## 5.5 Switching Characteristics

over recommended operating free-air temperature range, VCC = 5 V ± 0.5 V (unless otherwise noted) (see [Figure 6-1](GUID-FDB0810F-CA5C-4A1D-B009-02666650C6CD.html#SCLS264982))

| PARAMETER | FROM   (INPUT) | TO  (OUTPUT) | LOAD  CAPACITANCE | TA = 25°C | | | SN54AHCT125 | | SN74AHCT125 | | UNIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MIN | TYP | MAX | MIN | MAX | MIN | MAX |
| tPLH | A | Y | CL = 15 pF |  | 3.8[(1)](#SCLS264793) | 5.5[(1)](#SCLS264793) | 1[(1)](#SCLS264793) | 6.5[(1)](#SCLS264793) | 1 | 6.5 | ns |
| tPHL |  | 3.8[(1)](#SCLS264793) | 5.5[(1)](#SCLS264793) | 1[(1)](#SCLS264793) | 6.5[(1)](#SCLS264793) | 1 | 6.5 |
| tPZH | OE | Y | CL = 15 pF |  | 3.6[(1)](#SCLS264793) | 5.1[(1)](#SCLS264793) | 1[(1)](#SCLS264793) | 6[(1)](#SCLS264793) | 1 | 6 | ns |
| tPZL |  | 3.6[(1)](#SCLS264793) | 5.1[(1)](#SCLS264793) | 1[(1)](#SCLS264793) | 6[(1)](#SCLS264793) | 1 | 6 |
| tPHZ | OE | Y | CL = 15 pF |  | 4.6[(1)](#SCLS264793) | 6.8[(1)](#SCLS264793) | 1[(1)](#SCLS264793) | 8[(1)](#SCLS264793) | 1 | 8 | ns |
| tPLZ |  | 4.6[(1)](#SCLS264793) | 6.8[(1)](#SCLS264793) | 1[(1)](#SCLS264793) | 8[(1)](#SCLS264793) | 1 | 8 |
| tPLH | A | Y | CL = 50 pF |  | 5.3 | 7.5 | 1 | 8.5 | 1 | 8.5 | ns |
| tPHL |  | 5.3 | 7.5 | 1 | 8.5 | 1 | 8.5 |
| tPZH | OE | Y | CL = 50 pF |  | 5.1 | 7.1 | 1 | 8 | 1 | 8 | ns |
| tPZL |  | 5.1 | 7.1 | 1 | 8 | 1 | 8 |
| tPHZ | OE | Y | CL = 50 pF |  | 6.1 | 8.8 | 1 | 10 | 1 | 10 | ns |
| tPLZ |  | 6.1 | 8.8 | 1 | 10 | 1 | 10 |
| tsk(o) |  |  | CL = 50 pF |  |  | 1[(2)](#SCLS2646830) |  |  |  | 1 | ns |

(1) On products compliant to MIL-PRF-38535, this parameter is not production tested.

(2) On products compliant to MIL-PRF-38535, this parameter does not apply.

## 5.6 Noise Characteristics

VCC = 5 V, CL = 50 pF,
TA = 25°C[(1)](#SCLS2645302)

| PARAMETER | | SN74AHCT125 | | UNIT |
| --- | --- | --- | --- | --- |
| MIN | MAX |
| VOL(P) | Quiet output, maximum dynamic VOL |  | 0.8 | V |
| VOL(V) | Quiet output, minimum dynamic VOL |  | –0.8 | V |
| VOH(V) | Quiet output, minimum dynamic VOH | 4.4 |  | V |
| VIH(D) | High-level dynamic input voltage | 2 |  | V |
| VIL(D) | Low-level dynamic input voltage |  | 0.8 | V |

(1) Characteristics are for surface-mount packages only.

## 5.7 Operating Characteristics

VCC = 5 V, TA = 25°C

| PARAMETER | | TEST CONDITIONS | | TYP | UNIT |
| --- | --- | --- | --- | --- | --- |
| Cpd | Power dissipation capacitance | No load, | f = 1 MHz | 14 | pF |

# 6 Parameter Measurement Information

![GUID-E744E3B8-2E88-4682-8B28-27AA55D0746B-low.gif](https://www.ti.com/ods/images/SCLS264R/GUID-E744E3B8-2E88-4682-8B28-27AA55D0746B-low.gif "SN54AHCT125 SN74AHCT125 Load
                    Circuit and Voltage Waveforms")
Figure 6-1 Load
Circuit and Voltage Waveforms

# 7 Detailed Description

## 7.1 Overview

The SNx4AHTC125 devices have four integrated bus buffer gates. Each gate can be individually controlled from their respective output enable pins or tied together and controlled simultaneously. This allows for control of up to four different lines from one device. Often times a microcontroller have multiple function options for a single pin. By using GPIO pins to enable specific buffers, the SNx4AHCT125 can act as a multiplexer to select a specific data line depending on what pin function is selected on the microcontroller. At the same time, the lines that are not selected are isolated from the pin.

## 7.2 Functional Block Diagram

![GUID-8F3DA877-9F04-4CEB-B62F-692925279669-low.gif](https://www.ti.com/ods/images/SCLS264R/GUID-8F3DA877-9F04-4CEB-B62F-692925279669-low.gif)

Pin numbers shown are for
the D, DB, DGV, J, N, NS, PW, RGY, and W packages.

## 7.3 Feature Description

Each buffer has its own output enable. This allows for control of each buffer individually. When the output enable is LOW, the input is passed to the output. When the output enable is HIGH, the output is high impedance. This feature is useful in applications that might require isolation.

## 7.4 Device Functional Modes

Function Table  
 (Each Buffer)

| INPUTS | | OUTPUT  Y |
| --- | --- | --- |
| **OE** | A |
| L | H | H |
| L | L | L |
| H | X | Z |

# 8 Application and Implementation

Note:

Information in the following applications sections is not part of the TI
component specification, and TI does not warrant its accuracy or completeness.
TI’s customers are responsible for determining suitability of components for
their purposes, as well as validating and testing their design implementation to
confirm system functionality.

## 8.1 Application Information

In this application, a buffer with a 3-state
output is used to disable a data signal as shown in [Figure 8-1](GUID-A87DB724-8FCC-4E49-96BB-42AE85E9D83E.html#APP1_SCHEM). The remaining three buffers can be used for
signal conditioning in other places in the system, or the inputs can be grounded and
the channels left unused.

## 8.2 Typical Application

![GUID-F9D0888F-5E4C-4826-8C21-2FA14301983A-low.gif](https://www.ti.com/ods/images/SCLS264R/GUID-F9D0888F-5E4C-4826-8C21-2FA14301983A-low.gif "SN54AHCT125 SN74AHCT125 Typical
                    Application Block Diagram")
Figure 8-1 Typical
Application Block Diagram

### 8.2.1 Design Requirements

#### 8.2.1.1 Power Considerations

Ensure the desired supply voltage is
within the range specified in the *Recommended Operating Conditions*. The
supply voltage sets the device's electrical characteristics as described in the
*Electrical Characteristics* section.

The positive voltage supply must be
capable of sourcing current equal to the total
current to be sourced by all outputs of the SNx4AHCT125 plus the maximum static supply current,
ICC, listed in the *Electrical Characteristics*, and any transient
current required for switching. The logic device
can only source as much current that is provided by the positive supply source.
Be sure to not exceed the maximum total current through VCC listed in
the *Absolute Maximum Ratings*.

The ground must be capable of sinking
current equal to the total current to be sunk by all outputs of the SNx4AHCT125 plus the maximum supply current,
ICC, listed in the *Electrical Characteristics*, and any
transient current required for switching. The logic device can only sink as much
current that can be sunk into its ground connection. Be sure to not exceed the
maximum total current through GND listed in the *Absolute Maximum Ratings*.

The SNx4AHCT125 can drive a load with a total capacitance less than or equal to
50 pF while still meeting all of the data sheet specifications. Larger capacitive
loads can be applied; however, it is not recommended to exceed 50 pF.

The SNx4AHCT125 can drive a load with total resistance
described by RL ≥ VO / IO, with the output voltage
and current defined in the *Electrical Characteristics* table with VOH
and VOL. When outputting in the HIGH state, the output voltage
in the equation is defined as the difference between the measured output voltage and
the supply voltage at the VCC pin.

Total power consumption can be
calculated using the information provided in [*CMOS Power Consumption and Cpd
Calculation*](https://www.ti.com/lit/pdf/SCAA035).

Thermal increase can be calculated
using the information provided in [*Thermal Characteristics of Standard
Linear and Logic (SLL) Packages and Devices*](https://www.ti.com/lit/pdf/SCZA005).

CAUTION: The maximum junction
temperature, TJ(max) listed in the *Absolute Maximum Ratings*, is an
additional limitation to prevent damage to the device. Do not violate any values
listed in the *Absolute Maximum Ratings*. These limits are provided to prevent
damage to the device.

#### 8.2.1.2 Input Considerations

Input signals must cross VIL(max) to be considered a logic LOW, and VIH(min) to be considered a logic HIGH. Do not exceed the
maximum input voltage range found in the *Absolute Maximum Ratings*.

Unused inputs must be terminated to
either VCC or ground. The unused inputs can be directly terminated if the
input is completely unused, or they can be connected with a pull-up or pull-down
resistor if the input will be used sometimes, but not always. A pull-up resistor is
used for a default state of HIGH, and a pull-down resistor is used for a default
state of LOW. The drive current of the controller, leakage current into the SNx4AHCT125 (as specified in the *Electrical
Characteristics*), and the desired input transition rate limits the resistor
size. A 10-kΩ resistor value is often used due to these factors.

The SNx4AHCT125 has CMOS inputs and thus requires fast input
transitions to operate correctly, as defined in the *Recommended Operating
Conditions* table. Slow input transitions can cause oscillations, additional
power consumption, and reduction in device reliability.

Refer to the *Feature
Description* section for additional information regarding the inputs for this
device.

#### 8.2.1.3 Output Considerations

The positive
supply voltage is used to produce the output HIGH voltage. Drawing current from
the output will decrease the output voltage as specified by the VOH
specification in the *Electrical Characteristics*. The ground voltage
is used to produce the output LOW voltage. Sinking current into the output will
increase the output voltage as specified by the VOL specification in the
*Electrical Characteristics*.

Push-pull outputs
that could be in opposite states, even for a very short time period, should never be
connected directly together. This can cause excessive current and damage to the
device.

Two channels within
the same device with the same input signals can be connected in parallel for
additional output drive strength.

Unused outputs can be left floating.
Do not connect outputs directly to VCC or ground.

Refer to the *Feature
Description* section for additional information regarding the outputs for
this device.

### 8.2.2 Application Curves

![GUID-1AA6BC6C-4EE4-4334-A096-296F1FC68937-low.gif](https://www.ti.com/ods/images/SCLS264R/GUID-1AA6BC6C-4EE4-4334-A096-296F1FC68937-low.gif "SN54AHCT125 SN74AHCT125 Application Timing
                        Diagram")Figure 8-2 Application Timing
Diagram

## 8.3 Power Supply Recommendations

The power supply can be any voltage between the
minimum and maximum supply voltage rating located in the *Recommended Operating
Conditions*. Each VCC terminal should have a good bypass capacitor
to prevent power disturbance. A 0.1-μF capacitor is recommended for this device. It
is acceptable to parallel multiple bypass capacitors to reject different frequencies
of noise. The 0.1-μF and 1-μF capacitors are commonly used in parallel. The bypass
capacitor should be installed as close to the power terminal as possible for best
results, as shown in the following layout example.

## 8.4 Layout

### 8.4.1 Layout Guidelines

When using multiple-input and multiple-channel
logic devices, inputs must never be left floating. In many cases, functions or parts
of functions of digital logic devices are unused (for example, when only two inputs
of a triple-input AND gate are used or only 3 of the 4 buffer gates are used). Such
unused input pins must not be left unconnected because the undefined voltages at the
outside connections result in undefined operational states. All unused inputs of
digital logic devices must be connected to a logic high or logic low voltage, as
defined by the input voltage specifications, to prevent them from floating. The
logic level that must be applied to any particular unused input depends on the
function of the device. Generally, the inputs are tied to GND or VCC,
whichever makes more sense for the logic function or is more convenient.

### 8.4.2 Layout Example

![GUID-BCC38B0F-2A22-4412-9FA0-C2EE039FEEE4-low.gif](https://www.ti.com/ods/images/SCLS264R/GUID-BCC38B0F-2A22-4412-9FA0-C2EE039FEEE4-low.gif "SN54AHCT125 SN74AHCT125 Example Layout for the SNx4AHCT125")Figure 8-3 Example Layout for the SNx4AHCT125

# 9 Device and Documentation Support

TI offers an extensive line of development tools. Tools and software to evaluate the
performance of the device, generate code, and develop solutions are listed
below.

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

| GUID-D6F43A01-4379-4BA1-8019-E75693455CED-low.gif | This integrated circuit can be damaged by ESD. Texas Instruments recommends that all integrated circuits be handled with appropriate precautions. Failure to observe proper handling and installation procedures can cause damage. |
| --- | --- |
| ESD damage can range from subtle performance degradation to complete device failure. Precision integrated circuits may be more susceptible to damage because very small parametric changes could cause the device not to meet its published specifications. |

## 9.5 Glossary

[TI Glossary](https://www.ti.com/lit/pdf/SLYZ022)
This glossary lists and explains terms, acronyms, and definitions.

# 10 Revision History

**Changes from Revision Q (October 2023) to Revision R (February 2024)**

- Updated RθJA value: RGY = 47 to 87.1, all values in °C/W [Go](GUID-6A064918-C0E0-4665-966A-0DCADAC4957A.html)

**Changes from Revision P (June 2023) to Revision Q (October 2023)**

- Updated RθJA values: D = 86 to 124.5, PW = 113 to 147.7, all values in °C/W [Go](GUID-6A064918-C0E0-4665-966A-0DCADAC4957A.html)

# 11 Mechanical, Packaging, and Orderable Information

The following pages include
mechanical, packaging, and orderable information. This information is the most
current data available for the designated devices. This data is subject to change
without notice and revision of this document. For browser-based versions of this
data sheet, refer to the left-hand navigation.
