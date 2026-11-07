---
source: "TI -- TPS3808 Low-Quiescent-Current, Programmable-Delay Supervisory Circuit (SBVS050N)"
url: "https://www.ti.com/lit/gpn/tps3808"
format: "HTML datasheet (TI SBVS050N, August 2026)"
method: "fetchaller"
extracted: 2026-11-06
chars: 3374
---

# TPS3808 Low-Quiescent-Current, Programmable-Delay Supervisory Circuit (SBVS050N, revision N August 2026)

Excerpts: RESET pin, ratings, electrical characteristics and the sections on the RESET output and power-on behavior.

## 5 Pin Functions

| RESET | SOT-23 pin 1, WSON pin 6 | O | RESET is an open-drain output that is driven to a low-impedance state when RESET is asserted (either the SENSE input is lower than the threshold voltage (VIT) or the MR pin is set to a logic low). RESET remains low (asserted) for the reset period after both SENSE is above VIT and MR is set to a logic high. A pull-up resistor from 10kΩ to 1MΩ should be used on this pin, and allows the reset pin to attain voltages higher than VDD. |

## 6.1 Absolute Maximum Ratings

| Current | RESET pin | –5 | 5 | mA |

## 6.3 Recommended Operating Conditions

| VDD | Input supply range | 1.7 |  | 6.5 | V |
| I RESET | RESET pin current | 0.0003 |  | 5 | mA |

## 6.5 Electrical Characteristics (1.7V ≤ VDD ≤ 6.5V, RLRESET = 100kΩ, CLRESET = 50pF, TJ = –40°C to 125°C)

| PARAMETER | TEST CONDITIONS | MIN | TYP | MAX | UNIT |
| --- | --- | --- | --- | --- | --- |
| VOL Low-level output voltage | 1.3V ≤ VDD < 1.8V, IOL = 0.4mA |  |  | 0.3 | V |
|  | 1.8V ≤ VDD ≤ 6.5V, IOL = 1mA |  |  | 0.4 | V |
| VPOR Power-up reset voltage (1) | VOL (max) = 0.2V, I RESET = 15μA |  |  | 0.8 | V |
| VHYS Hysteresis on VIT pin, TPS3808G01 |  |  | 1.5% | 3% | VIT |
| IOH RESET leakage current | V RESET = 6.5V, RESET not asserted |  |  | 300 | nA |

(1) The lowest supply voltage (VDD) at which RESET becomes active. Trise(VDD) ≥ 15 μs/V.

## 7.3.4 RESET Output

RESET remains high (unasserted) as long as SENSE is above its threshold (VIT) and the manual reset (MR) is logic high. If either SENSE falls below VIT or MR is driven low, RESET is asserted, driving the RESET pin to a low impedance.

Once MR is again logic high and SENSE is above VIT + VHYS (the threshold hysteresis), a delay circuit is enabled that holds RESET low for a specified reset delay period. Once the reset delay has expired, the RESET pin goes to a high-impedance state. The pullup resistor from the open-drain RESET to the supply line can be used to allow the reset signal for the microprocessor to have a voltage higher than VDD (up to 6.5V). The pullup resistor must be no smaller than 10kΩ as a result of the finite impedance of the RESET line.

## 7.4.2 Above Power-On Reset but Less Than VDD(min) (VPOR < VDD < VDD(min))

When the voltage on VDD is less than the device VDD(min) voltage, and greater than the power-on reset voltage (VPOR), the RESET signal is asserted and low impedance, respectively, regardless of the voltage on the SENSE pin.

## 7.4.3 Below Power-On Reset (VDD < VPOR)

When the voltage on VDD is lower than the required voltage (VPOR) needed to internally pull the asserted output to GND, RESET is undefined, do not rely on RESET for proper device function.

## 8.2 Typical Application

Figure 8-1 shows a typical application of the TPS3808G25 used with a 2.5V processor. The open-drain RESET output is typically connected to the RESET input of a microprocessor. Use a pullup resistor to hold this line high when RESET is not asserted. The RESET output is undefined for voltage below 0.8V, but this characteristic is normally not a problem because most microprocessors do not function below this voltage.
