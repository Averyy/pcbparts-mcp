---
source: "TI -- TLV803 3-Pin Voltage Supervisor with Active-Low, Open-Drain Reset (SBVS157E)"
url: "https://www.ti.com/lit/gpn/tlv803"
format: "HTML datasheet (TI SBVS157E, December 2020)"
method: "fetchaller"
extracted: 2026-11-06
chars: 4016
---

# TLV803, TLV853, TLV863 3-Pin Voltage Supervisors with Active-Low, Open-Drain Reset (SBVS157E, December 2020)

Excerpts: pin functions, ratings, electrical characteristics and the sections on reset behavior and pull-ups.

## 3 Description

During power on, RESET asserts when the supply voltage (VDD) exceeds 1.1 V. Thereafter, the supervisory circuit monitors VDD and keeps RESET active as long as VDD remains below the threshold voltage VIT. An internal timer delays the return of the output to the inactive state (high) to ensure proper system reset. The delay time (td(typ) = 200 ms) starts after VDD exceeds the threshold voltage, VIT. When the supply voltage drops below the VIT threshold voltage, the output is active (low) again.

## 6 Pin Functions

| PIN | TLV803 | TLV853 | TLV863 | I/O | DESCRIPTION |
| --- | --- | --- | --- | --- | --- |
| GND | 1 | 2 | 3 | — | Ground pin. |
| RESET | 2 | 1 | 1 | O | RESET is an open-drain output that is driven to a low impedance state when RESET is asserted. RESET remains low (asserted) for the delay time (td) after VDD exceeds VIT–. Use a 10-kΩ to 1-MΩ pullup resistor on this pin. The pullup voltage is not limited by VDD. |
| VDD | 3 | 3 | 2 | I | Supply voltage pin. It is good analog design practice to place a 0.1-µF ceramic capacitor close to this pin. |

## 7.1 Absolute Maximum Ratings

| Parameter | MIN | MAX | UNIT |
| --- | --- | --- | --- |
| VDD | 0 | 6.5 | V |
| All other pins | –0.3 | +6.5 | V |
| Maximum low output current, IOL |  | 5 | mA |
| Maximum high output current, IOH |  | –5 | mA |

## 7.4 Recommended Operating Conditions

| VDD | Supply voltage | 1.1 | 6 | V |

## 7.5 Electrical Characteristics

| PARAMETER | TEST CONDITIONS | MIN | TYP | MAX | UNIT |
| --- | --- | --- | --- | --- | --- |
| VOL Low-level output voltage | VDD = 2 V to 6 V, IOL = 500 µA |  |  | 0.3 | V |
|  | VDD = 3.3 V, IOL = 2 mA |  |  | 0.4 | V |
|  | VDD = 6 V, IOL = 4 mA |  |  | 0.4 | V |
| Power-up reset voltage (1) | IOL = 50 µA, VOL < 0.2 V | 1.1 |  |  | V |
| IOH Output leakage current | VDD = 6 V |  |  | 350 | nA |

(1) The lowest supply voltage at which RESET becomes valid. tr,VDD ≤ 66.7 V/ms.

## 8.3.2 Reset During Power Up and Power Down

The TLV803 output is valid when VDD is greater than 1.1 V. When VDD is less than 1.1 V, the output transistor turns off and becomes high impedance. The voltage on the RESET pin rises to the voltage level connected to the pull-up resistor. Figure 8-2 shows a typical waveform for power-up, assuming the RESET pin has a pull-up resistor connected to the VDD pin.

## 8.4.2 Power On Reset (VDD < Power-Up Reset Voltage)

When the voltage on VDD is lower than the required voltage to internally pull the asserted output to GND (power-up reset voltage), both outputs are in a high-impedance state.

## 9.1.1 Monitoring Multiple Supplies

Because the TLV803 has an open-drain output, multiple TLV803 outputs can be directly tied together to form a logical OR-ing function for the RESET line. Only one pull-up resistor is required for this configuration.

## 9.1.2 Output Level Shifting

The RESET output of the TLV803 can be pulled to a maximum voltage of 6 V and can be pulled higher in voltage than VDD. It is useful to provide level shifting of the output for cases where the monitored voltage is less than the useful logic levels of the load. Figure 9-2 shows the TLV803Z used to monitor a 2.5-V power rail, with a logic RESET input to a microprocessor that is connected to 5.0 V and has 5.0-V logic levels.

## 9.2 Typical Application

Figure 9-3 shows TLV803S being used to monitor the supply rail for a DSP, FPGA, or ASIC.

### 9.2.1 Design Requirements

This design calls for a 3.3-V rail to be monitored. The design resets if the supply rail falls below 2.93 V. The output must satisfy 3.3-V CMOS logic.

### 9.2.2 Detailed Design Procedure

Select the TLV803S to satisfy the voltage threshold requirement.

Place a pullup resistor on RESET to VDD in order to satisfy the output logic requirement.
