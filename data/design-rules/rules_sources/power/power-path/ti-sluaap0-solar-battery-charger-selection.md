---
source: "TI SLUAAP0 -- Solar Battery Charger Selection"
url: "https://www.ti.com/lit/an/sluaap0/sluaap0.pdf"
format: "PDF 6pp"
method: "ti-html"
extracted: 2026-02-16
chars: 9085
---

Application Note

# Choosing the Correct Solar Battery Charger for Your Solar Application

# Abstract

With the introduction of the widespread availability of solar panels as a power source, there is becoming an increasing need to be able to flexibly charge batteries with a solar input source. Different topologies are needed to meet the requirements of the different input sources and/or batteries. Several battery chargers (together will be referred to as *Solar Battery Chargers* throughout the remainder of this document) use Maximum Power Point Tracking (MPPT) algorithms to extract the maximum power from a solar panel and to charge a battery. These devices cover a wide range of battery voltages as well as feature different topologies to accommodate these input voltages and charge voltages.

# 1 Introduction

The output voltage of a solar panel is tightly
linked to the current drawn from the solar panel. If too much current is drawn from the
solar panel the output of the solar panel will crash. The key to successful solar panel
utilization is to find what is called the Maximum Power Point (MPP). At the MPP the
maximum amount of power available from the solar panel is delivered [[1](GUID-C341108B-D572-42B5-BF69-DA8D2F0D1FF3.html#GUID-0CF96F36-44ED-4D36-B871-B1374F367760)], [[2](GUID-C341108B-D572-42B5-BF69-DA8D2F0D1FF3.html#GUID-B648FC91-BBE8-4575-9414-D8A5D41418BB)], [[3](GUID-C341108B-D572-42B5-BF69-DA8D2F0D1FF3.html#GUID-62DA9A1D-F101-48EA-AA6A-A62710C94667)]. [Figure 1-1](#GUID-D5B99ADC-F9A6-44EA-9FB1-421F442270E3) shows Current vs. Voltage and Power vs. Voltage curves. Note how
there is a clear MPP of approximately 7W and 13.5V for the Power vs. Voltage curve.
Increasing or decreasing the panel voltage beyond this point lowers the panel output
power.

Figure 1-1 Sample I-V and P-V Curve

Different switch mode topologies are used to accommodate the different input and output voltages as well as allow for the higher efficiencies of a switching charger. In this application note, the buck, boost, and buck-boost topologies are discussed.

# 2 How MPPT and VINDPM Works on Solar Battery Chargers

To extract the MPP from a solar panel, a MPPT
algorithm is used. One good way is to use the Fractional Open Circuit Voltage (FOCV)
technique. In this method, the solar battery charger input voltage is regulated to a
percentage of the open circuit voltage (OCV) of the solar panel. This OCV is the output
voltage of the solar panel under a no load condition [[4](GUID-C341108B-D572-42B5-BF69-DA8D2F0D1FF3.html#GUID-43C04F05-DC5A-4AD5-B5A9-D76A0C0ACB85)]. During normal sunlight conditions this ratio, also known as a K-factor, is
typically between 75% to 85%. Another method is to regulate the input voltage to a fixed
value. All of the Solar Battery Chargers presented here work by using one of these two
algorithms. The following sections detail how specifically each charger achieves MPPT
operation.

Using MPPT requires input voltage regulation, also known as VINDPM (Input Voltage Dynamic Power
Management). VINDPM activates when the battery charger requires more output power than
the input can handle which starts to lower the input voltage. By selecting the
appropriate VINDPM setting, the charge current will reduce under VINDPM to prioritize
the system load and to prevent the input voltage from dropping below the VINDPM value.
The VINDPM setting is determined by external resistor divider or I2C setting.
The combination of choosing the desired K-factor from the OCV and regulating with VINDPM
to the target input voltage presents a clear MPPT solution.

## 2.1 Buck MPPT

In a buck converter the input voltage is always
greater than the output voltage. Please see [Figure 2-1](#GUID-291593A7-CE08-4B29-8ECA-BDC379AF3308) demonstrating the buck topology in grey. A simple way to program
VINDPM in a buck charger is to use a resistor divider such as R3 and R4 in [Figure 2-1](#GUID-291593A7-CE08-4B29-8ECA-BDC379AF3308). A reference voltage is targeted at MPPSET. The goal is to program
the resistor divider such that the MPPSET reference voltage is met when the input is at
the VINDPM threshold.

The BQ24650 is a 26-V 10-A buck charge controller with MPPT through the MPPSET pin. The target
reference voltage for MPPSET is 1.2 V. The charger will pull only the current from the
solar panel that keeps the input voltage set at the desired MPPT voltage and the MPPSET
voltage at 1.2 V. The BQ24650 is standalone, but comes with two STATx pins to detail the
status of the device.

Figure 2-1 Solar Buck
Charger

## 2.2 Boost MPPT

In a boost converter the input voltage is always
less than the output voltage. Please see [Figure 2-2](#GUID-01E7E962-2F04-4183-BCBF-0EDA4F37FF24) demonstrating the boost topology in gray. A simple way to program
VINDPM in a boost charger is to user a resistor divider such as the VOC\_SAMP divider
shown with ROC2 and ROC1 in [Figure 2-2](#GUID-01E7E962-2F04-4183-BCBF-0EDA4F37FF24). First, the converter is disabled and then the VOC of the solar
panel is sampled at the input voltage. A reference voltage is measured at VOC\_SAMP in
the VOC condition and this is the VINDPM setting until the next sample.

The BQ25504, BQ25505, and BQ25570 are 100-mA boost
chargers with MPPT via VOC\_SAMP pin. In this family of devices, the input voltage is
sampled once every 16 seconds (typical) by disabling the converter. The converter then
regulates the input voltage to the desired percentage of the OCV. The BQ25505 and
BQ25570 provide options for an 80% MPPT (or K-factor) for solar devices. For both of
these devices and the BQ25504, the K-factor can be set by adjusting the VOC\_SAMP
divider.

Figure 2-2 Solar Boost Charger

## 2.3 Buck-Boost MPPT

In a buck-boost converter the input voltage can be
greater than, less than, or equal to the output voltage. Please see [Figure 2-3](#GUID-731CFF5E-937D-4550-B3F9-A2DECF215B49) demonstrating the buck-boost topology in grey. A host-controlled
charger presents more options to program MPPT. A robust way to implement MPPT is to
program the desired K-factor via I2C as shown by SDA and SCL pins in [Figure 2-3](#GUID-731CFF5E-937D-4550-B3F9-A2DECF215B49). The charger will periodically disable charging and measure the
input voltage, also known as the OCV of the solar panel. Next, the charger multiplies
the OCV by the K-factor and will hold the input to this value as VINDPM if the panel is
overloaded.

The BQ25798 is a 18.8-V 5-A I2C
buck-boost charger with MPPT. The BQ25798 is well suited for environments that change
temperature because as the panel cools or heats the BQ25798 will change the input
voltage regulation accordingly without having to set a fixed OCV. The I2C
capability also gives flexibility to change the K-factor on the fly.

Figure 2-3 Solar Buck-Boost Charger

# 3 Summary

There are many options to choose for Solar Battery
Chargers. Buck, boost, and buck-boost converter topologies are accessible as well as a
wide range of charge currents. Each battery charger works fixing the MPP Voltage or by
measuring the unloaded input voltage (or OCV) and regulating the input voltage at a
fixed ratio of the OCV.

For detailed features and operation, see [Table 3-1](#GUID-794CB959-0F25-4192-B0AE-00D2963E1021) for a comparison of the solar battery chargers.

Table 3-1 Feature Comparison of Solar Battery Chargers

| Device | BQ24650 | BQ25798 | BQ25504, BQ25505, BQ25570 |
| --- | --- | --- | --- |
| Input Voltage (max) | 28 V | 24 V | 3 V (BQ25504) and 5.1 V (BQ25505 and BQ25570) |
| Battery Voltage (max) | 26 V | 18.8 V | 5.25 V (BQ25504) and 5.5 V (BQ25505 and BQ25570) |
| Charge Current (max) | 10 A | 5 A | 0.1 A |
| Topology | Buck | Buck-Boost | Boost |
| Chemistry | Lead Acid, Li-Ion/Li-Polymer, Lithium Phosphate/LiFePO4 | Li-Ion/Li-Polymer, Lithium Phosphate/LiFePO4 | Li-Ion/Li-Polymer, SuperCap |
| Interface | Standalone (RC-Settable) | I2C | Standalone (RC-Settable) |
| How to Program MPPT | Resistor Programmable | I2C Programmable | Resistor Programmable |
| Type of MPPT | Fixed MPP Voltage | FOCV | FOCV |

# 4 References

1. S. Negi, A. Maity,
   A. Patra, and M. Sharad, *Adaptive Fractional Open Circuit Voltage Method for
   Maximum Power Point Tracking in a Photovoltaic Panel*, *2019 32nd
   International Conference on VLSI Design and 2019 18th International
   Conference on Embedded Systems (VLSID)*, Delhi, India, 2019, pp.
   482-487.
2. Texas Instruments,
   *[Implementing a Simple Maximum Power Point Tracking
   (MPPT) Algorithm](https://www.ti.com/lit/pdf/SLUAAI1)* application note.
3. Texas Instruments,
   *[Maximum Power Point Tracking With the bq24650
   Charger](https://www.ti.com/lit/pdf/SLUA586)* application note.
4. T. Esram and P. L.
   Chapman, *Comparison of Photovoltaic Array Maximum Power Point Tracking
   Techniques*, in IEEE Transactions on Energy Conversion, vol. 22, no. 2,
   pp. 439-449, June 2007.