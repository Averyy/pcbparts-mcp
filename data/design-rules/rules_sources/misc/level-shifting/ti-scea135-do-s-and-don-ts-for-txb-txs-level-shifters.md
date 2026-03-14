---
source: "TI SCEA135 -- Do's and Don'ts for TXB/TXS Level-Shifters"
url: "https://www.ti.com/lit/pdf/scea135"
format: "PDF 10pp"
method: "fetchaller"
extracted: 2026-02-14
chars: 9537
---

# Do's and Don'ts for TXB and TXS Voltage Level-Shifters with Edge Rate Accelerators

Michael Ikwuyum, Ajith Narayansetty, Sahil Garg

## Abstract

Auto Directional level shifter families are designed with weaker outputs than devices from other level shifting families, to be easily overdriven by the hosts. This makes Auto Direction devices a requirement for bidirectional interfaces such as I2C, MDIO, Quad-SPI, and so on.

The TXS and TXB Auto Directional level shifter families are designed with edge rate accelerators (commonly known as one-shots). The one-shots are designed for a set duration of pulse width for optimal signal integrity, impacted by RC components. Therefore, intentional and careful considerations should be made when used with additional external components as majority of one-shot concerns are due to improper use of the devices, false triggering of the one-shots and poor layout design.

## 1 Introduction

Texas Instruments' portfolio of level shifter devices contains many different types of level translation functions that collectively is able to address almost any application requirement. TI's level translation portfolio includes Auto Directional, Direction Controlled, Fixed Direction, and Application Specific Level Translators in Industrial and Automotive ratings.

### Table 1-1. Recommended Translator by Interface

| Interface | Up to 3.6 V | Up to 5.5 V |
|---|---|---|
| FET Replacement | 2N7001T | SN74LXC1T45 / TXU0101 |
| 1 Bit GPIO/Clock Signal | SN74AXC1T45 | SN74LXC1T45 / TXU0101 |
| 2 Bit GPIO | SN74AXC2T245 | SN74LXC2T45 / TXU0102 |
| 2-Pin JTAG/UART | SN74AXC2T45 | SN74LXC2T45 / TXU0202 |
| I2C/MDIO/SMBus | TXS0102 / LSF0102 | TXS0102 / LSF0102 |
| IC-USB | SN74AVC2T872 / TXS0202 | NA |
| 4 Bit GPIO | SN74AXC4T245 | TXB0104 / TXU0104 |
| UART | SN74AXC4T245 | TXU0204 |
| SPI | SN74AXC4T774 | TXU0304 |
| JTAG | SN74AXC4T774 | TXU0304 |
| I2S/PCM | SN74AXC4T774 / TXB0104 | TXB0104 / TXU0204 |
| Quad-SPI | TXB0106 | TXB0106 |
| SDIO/SD/MMC | TXS0206 / TWL1200 | NA |
| 8 Bit GPIO/RGMII | SN74AXC8T245 | SN74LXC8T245 |

## 2 The One-shot's Designed Duration

*Figure 2-1. Example of the one-shot timing out before reaching the designed duration.*

### 2.1 Design Considerations

- Figure 2-1 shows the one-shot expiring at about 200 pF.
- Do not expire or time-out the one-shot prior to reaching the designed duration.
- Consider short enough traces for round-trip delay reflections within the one-shot duration of 10-30 ns.
- Avoid excessive loading (similar to the datasheets) as the longer the trace length, the more the lumped capacitive loading.

### 2.2 Recommended Parts

Applications with higher capacitive loading from longer trace lengths, connectors etc, typically do not require Auto Direction. Such applications (SPI for example) require devices with stronger output buffers.

#### Table 2-1. Recommended Parts

| Part Number | AEC-Q100 | Voltage Translation Range | Features |
|---|---|---|---|
| TXU0304 | | 1.1 V - 5.5 V | Schmitt-trigger inputs, Integrated pull-down resistors, VCC Isolation and VCC Disconnect, Glitch-free power supply sequencing |
| TXU0304-Q1 | Yes | 1.1 V - 5.5 V | (same) |
| SN74AXC4T774 | | 0.65 V - 3.6 V | Direction controlled, Glitch-free power supply sequencing, VCC Isolation |
| SN74AXC4T774-Q1 | Yes | 0.65 V - 3.6 V | (same) |

## 3 Design Considerations for Slow Rise and Fall Times

*Figure 3-1. Example of Slow Rise and Fall Times, 2.4 us/V*

### 3.1 Design Considerations

- Figure 3-1 shows the one-shot false triggering due to a slow input rise time outside of the data sheet recommendation.
- Do not use slow input rise or fall transition rates.
- As shown, the one-shots can trigger or expire prior to the designed duration for adverse system-level effects.
- Consider using fast enough input edges per the data sheet's input transition rate.
- See TI app note: Implications of Slow or Floating CMOS Inputs.

### 3.2 Recommended Parts

#### Table 3-1. Recommended Parts

| Device Family | AEC-Q100 | Voltage Translation Range | Features |
|---|---|---|---|
| TXU and LXC | Yes | 1.1 V - 5.5 V | Schmitt-trigger inputs, Integrated pull-down resistors |
| AUP | Yes | 0.6 V - 3.6 V | Input hysteresis allows the input to support slew rates as slow as 200 ns/V, improving switching noise immunity |
| LSF | Yes | 0.65 V - 5.5 V | No input transition rate requirement |

## 4 Consider the Impact of External RC Components on Rise and Fall Times

*Figure 4-1. Example of Rise and Fall Times Increasing with Lumped Capacitance*

### 4.1 Design Considerations

- Figure 4-1 shows the relationship for rise/fall times being directly proportional to the lumped capacitance.
- Do not exceed the data sheet loading conditions as the rise or fall times will increase, impacting data throughput.
- Consider any tolerances of any additional RC components, similar to the data sheet recommendations.

### 4.2 Recommended Parts

The Auto Directional device family with the most flexibility for external resistors per RC components (for applications such as I2C), is the LSF family and then the TXS family.

#### Table 4-1. Recommended Parts

| Part Number | AEC-Q100 | Voltage Translation Range | Features |
|---|---|---|---|
| LSF0102 | | 0.65 V - 5.5 V | Over-voltage tolerant I/O, Low RON for low output voltage levels |
| LSF0102-Q1 | Yes | 0.65 V - 5.5 V | (same) |
| TXS0102 | | 1.65 V - 5.5 V | Edge-rate acceleration, Supports Partial-Power-Down applications, Integrated pull-up resistors |
| TXS0102-Q1 | Yes | 1.65 V - 5.5 V | (same) |

## 5 Consider the Lumped Capacitance

*Figure 5-1. Example Voltage Translation showing Lumped Capacitance with a One-Shot Device*

### 5.1 Design Considerations

- Unless otherwise noted in the data sheets, ensure <70 pF lumped capacitance for optimal performance per the data sheet's recommended data rates.
- Additional parasitic capacitance is added from trace length and connectors.
- Additional loading impacts signal integrity at faster data rates.

### 5.2 Recommended Parts

The Fixed and Direction Control families are most suitable for applications for high data throughput. Consider Table 5-1 for applications with connectors or excessive lumped capacitance such as GPIO, instead of TXB.

#### Table 5-1. Recommended Parts

| Part Number | AEC-Q100 | Data Rates | Voltage Translation Range | Features |
|---|---|---|---|---|
| SN74LXC8T245 | | Up To 420 Mbps | 1.1 V - 5.5 V | Schmitt-trigger inputs, Dynamic pull-downs on I/O, VCC Isolation and VCC Disconnect |
| SN74LXC8T245-Q1 | Yes | Up To 420 Mbps | 1.1 V - 5.5 V | (same) |
| TXU0104 | | Up To 200 Mbps | 1.1 V - 5.5 V | Schmitt-trigger inputs, Integrated pull-down resistors, VCC Isolation and VCC Disconnect |
| TXU0104-Q1 | Yes | Up To 200 Mbps | 1.1 V - 5.5 V | (same) |
| SN74AXC1T45 | | Up To 500 Mbps | 0.65 V - 3.6 V | Direction controlled, Glitch-free power supply sequencing, VCC Isolation |
| SN74AXC1T45-Q1 | Yes | Up To 500 Mbps | 0.65 V - 3.6 V | (same) |

## 6 Consider the Effects of Temperature on the Output Impedance

*Figure 6-1. Example of Outputs at Varying Temperature*

### Design Considerations

- Minimize reflections / ringing.
- Consider the impact of temperature on the output impedance, as mismatched impedance with PCB traces yield reflections.
- Reflections or ringing can be amplified by the one-shot as false edge triggers.
- Excessive ringing can cause false triggers observed as oscillating outputs.
- Ringing is also caused by capacitance and inductance of long cables or traces and can be amplified by unstable GND or VCC voltages.
- Use bypass capacitors or stable GND to minimize noise.
- Devices with Schmitt-Trigger are most recommended for noisy applications. See Section 3.2 for recommendations.

## 7 Summary

- Consider short enough traces for round-trip delay reflections within the one-shot duration of 10-30 ns.
- Consider any tolerances of any additional RC components, similar to the data sheet recommendations.
- Consider utilizing fast enough input edges per the input transition rate while avoiding floating inputs as stated in the data sheets.
- Unless otherwise noted in the data sheets, ensure <70 pF lumped capacitance designed for performance per the data sheet's recommended data rates.
- Avoid timing-out the one-shot duration with additional parasitic capacitance as trace length and connectors yields additional capacitive loading.
- One-shot triggers when they detect rising or falling edges. Reflections and/or ringing can cause false triggers. Ringing is also caused by capacitance and inductance of long cables and/or traces and can also be amplified by unstable GND or VCC voltages.
- Consider the impact on temperature per the output impedance, as mismatched impedance with PCB traces yield reflections that can be amplified by the one-shot as false edge triggers.

## 8 References

- Texas Instruments, Designing With the SN74LVC1G123 Monostable Multivibrator, application note.
- Texas Instruments, A Guide to Voltage Translation With TXS-Type Translators, application note.
- Texas Instruments, A Guide to Voltage Translation With TXB-Type Translators, application note.
- Texas Instruments, Effects of Pullup and Pulldown Resistors on TXS and TXB Devices, application note.
- Texas Instruments, Implications of Slow or Floating CMOS Inputs, application note.
