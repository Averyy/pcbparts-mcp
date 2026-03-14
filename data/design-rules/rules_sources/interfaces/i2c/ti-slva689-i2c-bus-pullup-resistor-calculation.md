---
source: "TI SLVA689 -- I2C Bus Pullup Resistor Calculation"
url: "https://www.ti.com/lit/pdf/slva689"
format: "PDF 5pp"
method: "ti-html"
extracted: 2026-02-16
chars: 4055
---

## I2C Bus Pullup Resistor Calculation

Pullup resistor calculation for I2C interface is a commonly asked question. In this application note we show how to use simple equations for this calculation.

### 1 Introduction

I2C communication standard is the mostly widely used inter-chip communication standard in today’s electronic systems. It is an open-drain/open-collector communication standard which implies integrated circuits (IC’s) with different voltage supply rails can be connected for communication. Pullup resistors need to be connected from the I2C lines to the supply to enable communication as shown in [Figure 1](#SLVA6897264). The pullup resistors pull the line high when it is not driven low by the open-drain interface. The value of the pullup resistor is an important design consideration for I2C systems as an incorrect value can lead to signal loss. In this article we show the simple equations for the pullup resistor calculation which the system designer can use to do quick calculations for their design.

Figure 1. Application Example Showing I2C Communication Between the Different IC's on a System and With Pullup Resistors on I2C Bus

### 2 Pullup Resistor Calculation

A strong pullup (small resistor) prevents the I2C pin on an IC from being able to drive low. The VOL level that can be read as a valid logical low by the input buffers of an IC determines the minimum pullup resistance [RP(min)]. RP(min) is a function of VCC, VOL (max), and IOL:

Equation 1.

The maximum pullup resistance is limited by the bus capacitance (Cb) due to I2C standard rise time specifications. If the pullup resistor value is too high, the I2C line may not rise to a logical high before it is pulled low. The response of an RC circuit to a voltage step of amplitude VCC, starting at time t = 0 is characterized by time constant RC. The voltage waveform can be written as:

Equation 2.

For VIH = 0.7 × VCC:

Equation 3.

For VIL = 0.3 × VCC:

Equation 4.

The rise time for the I2C bus can be written as:

Equation 5.

The maximum pullup resistance is a function of the maximum rise time (tr):

Equation 6.

where parametrics from I2C specifications are listed in [Table 1](#SLVA6896324).

### Table 1. Parametrics from I2C specifications

| Parameter | | Standard Mode   (Max) | Fast Mode   (Max) | Fast Mode Plus   (Max) | Unit |
| --- | --- | --- | --- | --- | --- |
| tr | Rise time of both SDA and SCL signals | 1000 | 300 | 120 | ns |
| Cb | Capacitive load for each bus line | 400 | 400 | 550 | pF |
| VOL | Low-level output voltage (at 3 mA current sink, VCC > 2 V) | 0.4 | 0.4 | 0.4 | V |
| Low-level output voltage (at 2 mA current sink, VCC ≤ 2 V) | – | 0.2 × VCC | 0.2 × VCC | V |

The RP (min) is plotted as a function of VCC in [Figure 2](#SLVA6898173). The RP (max) is plotted as a function of Cb in [Figure 3](#SLVA6898260) for standard-mode and fast-mode I2C.

Figure 2. Minimum Pullup Resistance [RP (min)] vs Pullup Reference Voltage (VCC)

Figure 3. Maximum Pullup Resistance [RP (max)] vs Bus Capacitance (Cb)

### 3 Speed Versus Power Trade-off

Once the minimum and maximum value of the pullup resistor has been selected, the decision for the value of resistor can be made based on trade-off between the speed and power budget. A smaller resistor will give a higher speed because of smaller RC delay, and a larger resistor will give lower power consumption.

### 4 Example

For Fast-mode I2C communication with the following parameters, calculate the pullup resistor value.

Cb = 200 pF, VCC = 3.3 V

Solution:

Taking the values from [Table 1](pullup-resistor-calculation-slva6899380.html#SLVA6896324):

Equation 7.

Equation 8.

Therefore, we can select any available resistor value between 966.667 Ω and 1.77 kΩ. The value of the pullup resistor can be selected based on the trade-off for the power consumption and speed.