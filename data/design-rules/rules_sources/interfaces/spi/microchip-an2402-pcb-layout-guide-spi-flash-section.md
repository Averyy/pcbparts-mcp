---
source: "Microchip AN2402 -- PCB Layout Guide (SPI Flash Section)"
url: "https://ww1.microchip.com/downloads/en/AppNotes/00002402A.pdf"
format: "PDF 21pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 16509
---
# PCB Layout Guide for CEC1702

Author: Tom Tse, Microchip Technology Inc.

## Introduction

This application note provides information on design considerations for a printed circuit board (PCB) for the Microchip CEC1702 device.

The design of the PCB requires care to provide good supply and ground paths; in addition, other design issues are addressed in this document.

The functional blocks in the CEC1702 have different requirements for routing and external connections, which are also outlined in this application note.

This document includes the following topics:

- Section 1.0, General Layout Considerations
- Section 2.0, Miscellaneous Considerations
- Section 3.0, JTAG Design and Layout Guide

### Audience

This document is written for a reader that is familiar with hardware design. The goal of this application note is to provide information about sensitive areas of the CEC1702 PCB layout.

### References

- Microchip CEC1702 Data Sheet
- Microchip CEC1702 EVB Reference Schematic
- I2C-bus specification and user manual, Rev. 6 - 4 April, 2014 or later

### Package Information

The CEC1702 device is currently available in: CEC1702 for 84-pin, WFBGA

## 1.0 General Layout Considerations

### 1.1 Decoupling Capacitors

Decoupling capacitors should be placed as close to the chip as possible to keep series inductance low. When the capacitors are mounted on the bottom side of the PCB, the capacitors are connected to the ground plane from the bottom layer directly using the shortest path to the device. Each VCC pin should have a 0.1 uF capacitor located as close to the pin as possible. Bypass capacitors should be placed close to the supply pins of the CEC1702 with short and wide traces.

The CEC1702 has an integrated voltage regulator to supply the core circuitry. Decoupling this regulator requires a critical capacitor of 1 uF on the CAP pin. ESR of this 1 uF capacitor, including the routing resistance, must be less than 100 mOhm.

Capacitors may carry large currents that generate magnetic fields, inducing noise on nearby traces. Sensitive traces such as the 32kHz crystal should be separated by at least five times the trace width from decoupling capacitors when possible.

Connecting decoupling caps to power and ground planes using two vias per pad will reduce series inductance.

#### 1.1.1 CEC1702 WFBGA Capacitors

Decoupling for the CEC1702 84-pin WFBGA package:

- C9 = 0.1uF on VBAT
- C10 = 0.1uF on VTR1
- C11 = 0.1uF on VTR2
- C14 = 0.1uF on VTR_REG
- C13 = 0.1uF and C20 = 22uF between VTR_PLL and VSS_PLL
- C7 = 1uF Low ESR +/-20% <100 mOhm on VR_CAP (X5R or X7R)
- Y1 = 9pF load crystal, with C5, C6 = 10pF decoupling

The VCC pin decoupling capacitors can use any typical 16V 10% Ceramic.

### 1.2 32.768kHz Crystal Oscillator

This section describes specific layout and design considerations for the 32.768kHz crystal oscillator; this can be used to source the internal 32kHz clock domain, in lieu of the silicon oscillator or an external pin. The crystal implementation is required to support the RTC function within the CEC1702.

#### 1.2.1 32.768kHz Crystal Oscillator Layout

The CEC1702 32kHz crystal oscillator is designed to generate a synchronous on-chip clock signal with an appropriate external oscillator crystal. The design has been optimized for low power (1.5 uW typical), stability and minimum jitter using a general purpose parallel resonant 32kHz crystal.

This unique low power crystal oscillator drive circuit means that a standard inverter crystal layout should not be used. The design has been characterized to allow a variation of 4pF to 18pF on each pin. Based on the load capacitance calculation, Microchip recommends 10pF load capacitors with a crystal that has a 9pF CL rating.

Effective Load Capacitance = (C11 + Cpin_xtal2)(C12 + Cpin_xtal1) / (C11 + Cpin_xtal2 + C12 + Cpin_xtal1) + Cbrd

Where:

- C12 is the cap from pin XTAL1 to ground
- C13 is the cap from pin XTAL2 to ground
- Cpin_xtal2 is the pin capacitance of pin XTAL2 (estimated 5pF)
- Cpin_xtal1 is the pin capacitance of pin XTAL1 (estimated 3pF)
- Cbrd is estimated at 1.5pF

#### 1.2.2 Crystal Accuracy

The accuracy of the 32kHz input translates directly into accuracy of the internal clock and the functions in the CEC1702 using the 32kHz: 32KHZ_OUT, week timer, hibernation timers, etc.

+/-1ppm of error in frequency corresponds to 32.768 kHz x 1ppm x 10^-6 = +/-0.032768 Hz. This translates into ~1 usec/sec or ~+/-0.086 sec/day.

Microchip recommends using a +/-20ppm crystal, which equals approximately +/-2 sec/day.

The effect of each picofarad of additional capacitance:

ppm/pF = C1 x 10^6 / (2(C0 + CL)^2)

For example, using a crystal with C0 = 0.8pF, C1 = 0.0019pF, CL = 12.5pF, yields 5.37ppm/pF, or approximately +/-462 msec/day per pF.

#### 1.2.3 Single Ended Clocking

An external clock source (maximum voltage of 3.3V) may be applied to the XTAL2 pin if the XOSEL bit in Clock Enable Register configures as a single-ended 32.768 kHz clock input (SUSCLK). The XTAL1 pin should be left floating.

### 1.3 CAP Pins, AVSS/GND Connection

The recommended filtering for the CAP pin on the CEC1702 should be placed close to the device and away from noise sources. AVSS is directly connected to GND.

### 1.4 PCB Mounted Analog Power Supply Filter for PLL Usage

To achieve a reasonable level of long term jitter, it is vital to deliver an analog-grade power supply to the PLL. Typically an R-C or R-L-C filter is used, with the "C" being composed of multiple devices to achieve a wide spectrum of noise absorption.

The series resistance of this filter is limited for DC reasons; generally less than 5% voltage drop across this device under worst-case conditions. High quality series inductors should not be used without a series resistor lest a high gain series resonator is created.

The power (VDD) path must be a single wire from the IC package pin to the high frequency cap, then to the low frequency cap, and then through the series element (e.g. resistor) then to board power (VDD). The distance from the IC pin to the high frequency cap should be as short as possible.

Similarly, the ground (VSS) path should be from the IC pin to the high frequency cap, to the low frequency cap, with the distance from IC pin to high frequency cap being very short. Modern PLLs will have the DC ground connection made on chip, so the external ground connection must not be connected to PCB ground.

In all applications, the power and ground traces should be short, and run close and parallel as far as possible, with large spacing to adjacent traces. On no account should any connection be made from VDD or VSS_PLL to board power planes.

#### 1.4.1 Real World Component Selection

Throughout the attenuating frequency range, there should be no resonant non-absorptions. The series element will either be a resistor or a very poor (i.e. resistive) inductor.

The filter requires the highest value high frequency capacitor in a small package (often 100nF). In applications with a low PLL reference frequency, it is often beneficial to add a large value capacitor such as an electrolytic (often 22uF).

Reference schematic: R = 100 ohm in series, C = 22 uF and C = 100 nF in parallel between VTR_PLL and VSS_PLL.

### 1.5 BGA Package PCB Layout Considerations

84-pin WFBGA: 7mm x 7mm, 0.65mm ball pitch

BGA routing guidelines:

- Through-hole vias technology is not recommended for pitches less than 0.8mm (unless the ball matrix is depopulated in the center)
- NSMD ball pads for pitches 0.8mm - 0.4mm
- Solder Mask to be 1:1 scale of the land size, when routing 0.5mm pitch ball pads
- Eliminate through-hole vias for tighter pitches
- Increase routing density and enhance electrical performance
- Provide fan-out solutions for multiple layers (stacked Vias)

## 2.0 Miscellaneous Considerations

### 2.1 Strapping Options

| GPIO | Strap Name | Pull High | Pull Low |
|---|---|---|---|
| GPIO171 | TAP Controller Select Strap | (Default) Internal pull high selects Boundary Scan TAP Controller | External pull Low selects Debug TAP Controller |

This strap option is sampled on VTR power up, and is not affected by a Watchdog Timer reset. This pin MUST be pull-low for normal operation.

### 2.2 Battery Circuit

VBAT must always be present if VTR is present. A recommended battery circuit is provided in the data sheet.

### 2.3 EOS Considerations

For SMBus signals that terminate external to the main system board (e.g., Smart Battery) the designer should take care in protecting these signals from EOS and ESD. The specification recommends a series protection resistor and an optional ESD transorb. Using 2 high speed Schottky diodes on each SMBus trace (instead of the transorb) is an effective way to improve immunity to EOS and ESD events.

Any other signal that goes to an external connector should also be considered for EOS/ESD susceptibility.

- **EOS:** Damage caused by voltages beyond the power supply rails, usually forward biasing internal protection diodes, resulting in high current. Typically low voltage, high current.
- **ESD:** Applied reverse bias to the PN junction -- heat due to power dissipation melts the silicon. Typically high transient voltage spike with low current.

### 2.4 ADC Input Layout Requirements

- The ADC Source AVSS reference should connect to CEC1702 AVSS via a low noise AVSS island.
- A low pass filter should be used on each ADC input: R = 100 ohm to 1.1 kohm, C = 100pF to 2500pF. The RC values are based on high frequency cut off: F = 1 / (2 * pi * RC).
- ADC nets should be spaced at least 20 mils from any high speed switching signals.

### 2.5 SPI Flash Implementation

The CEC1702 SPI flash interface enables the embedded controller (EC) access to an external SPI flash device.

**Note:** The SPI Flash Interface of CEC1702 can be selected either 3.3V or 1.8V. The QSPI0 interface is on VTR2 power rail.

#### SPI Interface Signals

| Signal Name | Function | CEC1702 Pin | Description |
|---|---|---|---|
| SPICLK | QSPI0_CLK | K6 | Shared SPI Clock |
| SPI_CS# | QSPI0_CS# | K7 | Shared SPI Chip Select |
| IO0 / MOSI | QSPI0_IO0 | K5 | Shared SPI Data I/O 0 (also SPI_MOSI in single wire mode) |
| IO1 / MISO | QSPI0_IO1 | K3 | Shared SPI Data I/O 1 (also SPI_MISO in single wire mode) |
| IO2 | QSPI0_IO2 | K4 | Shared SPI Data I/O 2 (Quad Mode only, also used as WP) |
| IO3 | QSPI0_IO3 | K2 | Shared SPI Data I/O 3 (Quad Mode only, also used as HOLD) |

#### 2.5.1 SPI Flash Interface Topology

PCB trace specifications:

| Code | Description | Spec |
|---|---|---|
| L0 | Connection between CEC1702 or SPI flash device and termination resistors | 0.1-inch to 0.5-inch |
| L1 | PCB trace between terminating resistors on the IO lines | 1-inch to 10-inch |
| L2 | PCB trace from CEC1702 or R1 resistor to SPI flash | 1-inch to 10-inch |
| L3 | PCB trace from CEC1702 to SPI flash for chip select | L3 = L0 + L1 |
| R1 | Resistors between the trace and the CEC1702 | 25 ohm |
| R2 | Resistor on the IO lines between the SPI flash and trace | 45 ohm |
| R3 | Pull-High resistor (to +3.3V) for SPI CS connections | 4.7K ohm |

**Note:** The final value of the series resistors should be chosen based on electrical analysis to ensure electrical timings and min/max voltage specifications are met for each device, including the undershoot/overshoot specifications for the CEC1702 (-0.3V min. to VCC1 +0.3V max).

#### 2.5.2 SPI Flash Implementation Recommendations

- The CEC1702 SPI memory interface has serial flash device compatibility requirements defined in the data sheet.
- SPI_CLK must be 20mils spacing from any other high frequency (>1GHz) signal.
- The SPI flash parts should support operating at 12MHz for the ROM code loader, and up to 48MHz clock speed in RAM code loading.
- IBIS models are available to aid in simulating the SPI system topology.
- The chip select CS# signals should have weak pullup resistors to the same power rail as the SPI flash.
- The characteristic impedance of the PCB trace should be 50 ohms +/-15% at 50MHz operating frequency.
- Within the SPI flash device, Schmitt trigger inputs are assumed on both the clock line and IO data lines.
- The output drivers for the SPI flash chip select pins should be programmed as open-drain.
- The SPI Data IO traces should be length-matched to the CLK lines within 0.100-inch.
- Signal Integrity should be checked for each SPI part on your BOM.

#### 2.5.3 SPI Flash External Programmer

The SPI Flash must be programmed externally using a suitable programmer. Provisions for a programming header for the SPI flash are recommended if the SPI is not socketed.

### 2.6 1MHz Pullup Resistor Requirement

Refer to the I2C-bus specification and user manual for more information.

### 2.7 5V Tolerant Pins

There are ten 3.3V/5V tolerant (over-voltage) pins on the CEC1702. It is recommended to select strong pull-up resistor value (less than 10k ohms) that keep the pull-up voltage on the pin less than 3.8V and above 4.5V.

### 2.9 Power Switch Input

For the VBAT-powered power switch inputs (VCI_INx#), the resistors can use any typical 1/10W, +/-1% carbon, thick, metal, or thin film. The capacitors can use any typical 16V 10% ceramic. Unused VCI pins should be pulled up to VBAT via a 100K resistor.

### 2.10 VCI_IN Pins when Used as GPIO

All VCI_IN pins can be used as GPIOs. The firmware must clear both the VCI_BUFFER_EN bit in the VCI BUFFER ENABLE REGISTER and the IE bit in the VCI INPUT ENABLE REGISTER.

## 3.0 JTAG Design and Layout Guide

### 3.1 CEC1702 JTAG Capabilities

- JTAG-Based DAP Port, Comprised of SWJ-DP and AHB-AP Debugger Access Functions
- Full DWT Hardware Functionality: 4 Data Watchpoints and Execution Monitoring
- Full FPB Hardware Breakpoint Functionality: 6 Execution Breakpoints and 2 Literal (Data) Breakpoints
- Accessed via 4-wire JTAG or 2-wire ARM SWD (Default)
- Comprehensive ARM-Standard Trace Support: Full DWT, ITM, ETM, TPIU functionalities

### 3.2 General PCB Layout Considerations for JTAG

Follow the PCI Specification's Routing and Layout Guidelines for the JTAG interface signals to support speeds up to 33MHz.

- Keep the clock traces as straight as possible
- Use arc-shaped traces instead of right-angle bends
- Do not use multiple signal layers
- Do not use vias to reduce impedance change and reflection
- Place a ground plane next to the outer layer to minimize noise effect
- Terminate clock signals to minimize reflection

### 3.3 Pin Connections

#### 3.3.1 4-Wire JTAG Connection

| Name | Description |
|---|---|
| VTR | 3.3V. Recommended to add a 49-ohm series resistor for motherboard protection. |
| TDI | Test Data In |
| TMS | Test Mode Select |
| CLK | Test Clock |
| TDO | Test Data Out |
| GND | Motherboard ground connect |

Notes:
1. 10K pullups on JTAG inputs prevent floating when JTAG cable is not attached.
2. CEC1702 JTAG RST# pin connects to a 100K pullup to always enable the JTAG interface.
3. Use a keyed connector to avoid plugging the cable in backward.
4. Add zero-ohm resistors to the JTAG link if a JTAG chain is used.

#### 3.3.2 2-Wire JTAG Connection

| Name | Description |
|---|---|
| VTR | 3.3V |
| SWDCLK | Use on JTAG_CLK pin if selected |
| SWO | Use on JTAG_TDO pin if selected |
| SWDIO | Use on JTAG_TMS pin if selected |
| GND | Motherboard ground connect |

Standard ARM Cortex 10 pins connector: Samtec FTSH-105-01 w/ pin 7 removed.

### 3.4 JTAG Internal Pull-Up

The firmware can select which debug pins to enable the internal pull-high. Default is disabled. See CEC1702 Data Sheet DEBUG ENABLE REGISTER (4000_FC20h).

### 3.5 JTAG Reset

JTAG_RST# pin must be held low for at least 5.00 msec when applying VTR power. If JTAG_RST# is high during power up, the JTAG registers may be set to unpredictable values and the system may not run correctly.

Options for handling JTAG_RST#:

- **Production Mode with JTAG Port Disable:** Hold JTAG_RST# pin low with pulldown resistor. Add a pullup resistor option (do not populate) for failure analysis.
- **Production Mode with JTAG Port Enable:** Add a jumper to hold JTAG_RST# line low during power up, then remove the jumper. Optionally, use RC circuitry (100K ohms pullup to VTR and 1uF capacitor) to force JTAG_RST# low for at least 5.00 msec.
