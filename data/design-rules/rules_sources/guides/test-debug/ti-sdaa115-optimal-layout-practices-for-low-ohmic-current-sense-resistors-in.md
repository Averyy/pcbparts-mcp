---
source: "TI SDAA115 -- Optimal Layout Practices for Low-Ohmic Current Sense Resistors in Parallel"
url: "https://www.ti.com/lit/an/sdaa115/sdaa115.pdf"
format: "PDF 11pp"
method: "ti-html"
extracted: 2026-03-02
chars: 14570
---

Application Note

# Optimal Layout Practices for Low-Ohmic Current Sense Resistors in Parallel

# Abstract

Accurate current measurement is a basic requirement in motor control, power management, and energy monitoring systems. Among traditional sensing techniques such as current transformers (CTs), current shunts provide a direct measurement approach that is the most reliable and cost-effective.

Current shunt resistors of few µΩ or mΩ are
generally used for current sensing. However, voltage measurements using low
ohmic values in the range of few µΩ have a higher probability of being affected
by PCB trace resistance, Temperature Coefficient of Resistance (TCR), and solder
resistance. This effect becomes more challenging when current sense resistors
are mounted in parallel. This application note will discuss best layout
practices and considerations for designing shunts in parallel.

# 1 Introduction

Placing current shunt resistors in parallel is a common design strategy, particularly in high-current applications. It distributes current among multiple resistors, allowing for increased power and better heat dissipation. Moreover, it enables the use of small shunts which are relatively cheaper and more easily available.

Shunts in parallel also have a lower effective
resistance, minimizing the voltage drop across the shunt, which reduces power loss (

P

=


I
2
R
) and increases system efficiency. In addition, a
single shunt resistor designed for high currents can have a larger physical size,
and therefore, a higher parasitic inductance. Using multiple smaller resistors in
parallel can help to reduce the overall inductance of the shunt . This is
particularly important in fast-switching circuits, like those in motor drives or
power supplies, where inductance can cause voltage spikes and measurement errors.
​

On the other hand, parallel shunt designs may
introduce uneven current sharing since it is difficult to ensure that the current is
split evenly among parallel resistors. Variations in resistance due to manufacturing
tolerances and differences in the resistance of the PCB traces leading to each
resistor causes an unequal current distribution. This can lead to one resistor
carrying more current than intended, causing it to overheat, which can alter the
resistance and further worsen the imbalance. [Figure 1-1](#GUID-C5F52515-9C0F-4825-8C88-D75EA4CF3363) details the various sources of resistances that may become significant as shunt
resistances in the µΩ range are used.

Aside from the shunt resistors, auxiliary
resistances such as the solder between the shunt and resistor pad, solder between
shunt and trace, and copper around the shunts contribute to the effective
resistance, approximately 10 to 100µΩ, 1 to 10µΩ, and 500µΩ/square respectively, as
shown in [Figure 1-1](#GUID-C5F52515-9C0F-4825-8C88-D75EA4CF3363).

Figure 1-1 Sources of Resistance in
Parallel Shunt Layout

An accurate parallel
shunt design requires a very careful and symmetrical PCB layout. The layout must
make sure that copper, solder, and trace resistances are compensated for, so that
the shunt resistors predominantly contribute to the overall shunt voltage drop. To
mitigate the issue of uneven current sharing, the traces connecting to each resistor
should be as identical as possible in length and width. Moreover, it must make sure
that the current prefers the path through the shunt, as opposed to through the sense
traces.

One method to minimize the effect of trace resistance is to use kelvin connections. However, when multiple shunts in parallel are involved, it is important to ensure the voltage is measured from a central, symmetrical point or that all shunts have independent kelvin connections, otherwise, the measurement accuracy will be compromised.

This paper examines the effectiveness of various
parallel resistor layouts on total shunt voltage drop in shunt-based current
sensing. The analysis is supported by TINA-TI simulations and experimental PCB
measurements. Recommendations are provided for achieving layout practices when
designing with the INA190, one of TI's ultra-precise current sense amplifiers with a
maximum of 3nA of input bias current. This focus helps ensure proper current sharing
among the shunts. This layout can be applied to other devices in our portfolio by
taking into account any additional input bias current.

# 2 Simulation and Best Layout Practices

To illustrate the impact of layout on
total voltage drop across the shunts, three TINA-TI simulations were performed,
representing different design approaches. The following section details the effect
of trace geometry and shunt placement on the overall effective shunt voltage.

Three shunt resistor values - 270µΩ,
300µΩ and 330µΩ - were used across the designs. The 10% variation in these values
simulate the worst-case tolerance and resistance variations encountered in practical
applications. Resistors in µΩ range were specifically chosen to maximize the impact
of auxiliary resistances, as their impedance is comparable to that of the shunt.

The following is a list of the
components and configuration-details of the TINA-TI simulation [(Fig 2-1)](#GUID-E58DF304-0DFD-434B-90D4-AB19958E4865):

* All three approaches have 20A
  current flowing across the shunts
* Rsolder\_SR and
  Rsolder\_ST represent the solder resistance between shunt -
  resistor pad and shunt - trace respectively
* Rcu and
  Rtrace are the simulation resistances between shunts due to the
  copper layer
* Current sources (Ib) above the
  output voltage represent the input bias current of the INA190 (3nA)
* Rcu(TL),
  Rcu(TR), Rcu(BL), Rcu(BR) represent the
  resistances associated with the surface mount spade connectors
* Voltage-controlled voltage source
  is used to simulate the INA190's ideal gain stage and is set to 200 V/V

The trace resistances (10m, 20m, 30m)
are length-dependent approximates based on trace resistivity calculations from the
Saturn PCB Design Toolkit. The copper resistance is based on the concept that sheet
resistance of 1 ounce copper is 500µΩ/square. There are a total of two spade
connectors on either side of the shunts [Figure 5-4](GUID-7043D023-CE7A-4F0D-A168-17D55DC218B0.html#GUID-40D1F443-474D-4825-B299-5B78B921EF9C) through which current is supplied to the circuit, hence there are five
connections possible, for example. Top-Right to Bottom-Right (TR-BR), Top-Right to
Bottom-Left (TR-BL), Top-Left to Bottom-Right (TL-BR), Top-Left to Bottom-Left
(TL-BL) and both together (TR,TL to BR,BL).

In a complex resistor network ([Figure 5-5](GUID-7043D023-CE7A-4F0D-A168-17D55DC218B0.html#GUID-56A6005C-0D7D-4FF0-8371-48E819EF98B3)), the total resistance encountered by the current is highly
dependent on the specific path taken. [Table 2-1](#TABLE_EZD_5LD_HHC) lists
simulation results from [Layout 2](#GUID-8CB72384-3921-42EE-8929-29F371BFBF96) and [3](#GUID-11A3EE2B-FAE3-4CB9-AA6D-41B68F6F37EF), with the current path in different combinations.

Table 2-1 Current Path
Combinations

| Current Path | Layout 2 Vout (mV( | Layout 3 Vout (mV) |
| --- | --- | --- |
| TL-BR | 346.1 | 399.04 |
| TR-BR | 350.03 | 406.63 |
| TL-BL | 342.17 | 395.2 |
| TR-BL | 346.1 | 399.04 |
| Both (TRTL)- Both (BRBL) | 346.09 | 399.02 |

From [Table 2-1](#TABLE_EZD_5LD_HHC), deduce
that the best possible combinations for current flow are *TL - BR, TR-BL* or
*Both - Both.*
[Figure 5-5](GUID-7043D023-CE7A-4F0D-A168-17D55DC218B0.html#GUID-56A6005C-0D7D-4FF0-8371-48E819EF98B3) in the supplementary section depicts how the simulation's
resistor network was designed for the PCB layout.

All three layouts utilize the
established Kelvin sensing principle, particularly since it is most critical for
accuracy with low-value shunt resistors. Moreover, with Rshunts of 270µΩ, 300µΩ and
330µΩ in parallel, the effective resistance is 99.3311 *(Reffective = 1/((1/270u)
+ (1/300u) + (1/330u)*), and hence expected Vout is
**397.32mV**
*(99.3311µΩ x 20A x 200V/V)*. The following three layouts attempt to get as
close as possible to the expected value.

Figure 2-1 Layout 1: Kelvin Sensing from
Shunt Closest to Device

In [Figure 2-1](#GUID-E58DF304-0DFD-434B-90D4-AB19958E4865), the sense traces are designed to connect to the shunt
closest to the device. Since the sense traces are tapping the shunt resistors from
further down the high-current path, this includes the voltage drop across solder
joints and traces in the effective shunt voltage drop.

This is an example of a bad layout
because it deliberately introduces the maximum amount of unwanted, external
parasitic resistances into the differential measurement path, leading to maximum
output voltage offset (56.47mV) i.e. largest difference between measured Vout and
expected Vout.

Figure 2-2 Layout 2: Kelvin Sensing from
Middle Shunt

[Layout 2](#GUID-8CB72384-3921-42EE-8929-29F371BFBF96) has Kelvin connections setup to the shunt in the middle. There
are lower-resistance parallel paths for current to flow through as opposed to
through the middle shunt, hence the current through the middle shunt is
comparatively less (5.77A). In addition, since the copper layer provides many
alternative paths for current to flow through instead of through the shunt, there
will be a significant voltage drop in the PCB's copper layer - greater than the
voltage drop across shunt.

Thus kelvin sensing from the
centre-shunt leads to a output voltage offset of 51.22mV.

Figure 2-3 Layout 3: Kelvin Sensing from
Each Shunt (Best-Case Layout)

[Layout 3](#GUID-11A3EE2B-FAE3-4CB9-AA6D-41B68F6F37EF) is considered the best layout practice because it has Kelvin
connections from each shunt resistor. Individual Kelvin sensing lines minimize the
effect of parasitic resistance of trace and solder on the total effective shunt
voltage. It also accounts for all three shunt voltage drops, hence you can get an
accurate output regardless of how current is split between the resistors.

Moreover, when multiple Kelvin
connections are used, the traces can inadvertently form low impedance loops,
providing a path for the circulation of undesired currents. Therefore, to mitigate
this issue and maintain measurement integrity, current-limiting resistors that are
at least 100 times greater than the shunt resistors are incorporated in series with
the Kelvin traces. Without these resistors hundreds of milliamps of current is
circulating in the Kelvin traces, generating detrimental heat. If greater
circulating current suppression is required, use a larger limiting resistor as
depicted in the layout. These resistors also enable averaging of the voltage across
each shunt, hence improving accuracy. Note, the current-limiting resistors may cause
error in devices with higher input bias currents.

In summary, this the best layout
practice since the effective voltage drop across the shunts measured at VM4 is the
closest to the calculated value of **397.32mV**.

# 3 Results

To test the PCB layouts, first the Device Under Test (DUT) was connected to a DC supply (Xantrex XHR 7.5-80**)**, electronic load (Kikusui PLZ1205W) and a precision resistor as shown below in [Figure 3-1](#GUID-F830B1B4-BB69-4BEB-83A3-FB7B057A6150). The shunts used in bench test were all 300µΩ, hence Reffective is calculated to be 100µΩ. TL-BR spade connector combination was used to flow current through the DUT.

Figure 3-1 Bench Test Setup Schematic

The precision resistor of 0.01Ω used in the bench test was to accurately determine the load current flowing in the circuit. A Keysight 3458A digital multimeter was used here to determine voltage drop across the precision resistor (Vshunt), then this value is divided by the resistance (0.01Ω) to calculate the load current (Iload Real). Another Keysight 3458A was connected across the OUT pin of DUT and ground to measure Vout.

The results are listed in [Table 3-1](#GUID-21456DD1-E8A8-4A40-B752-B986DD8A5ACD) and the Error% against load current is plotted in [Figure 3-2](#GUID-83B19A02-B7A0-482F-B302-B67EF4240721).

Error % = ((| Expected Vout - Measured Vout |) / Expected Vout) × 100

Table 3-1 Bench Test Results

|  | Layout 1 | | | Layout 2 | | | Layout 3 | | | Expected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Iload (A)** | **DUT Vout (V)** | **Vshunt (mV)** | **Iload Real (A)** | **DUT Vout (V)** | **Vshunt (mV)** | **Iload Real (A)** | **DUT Vout (V)** | **Vshunt (mV)** | **Iload Real (A)** | **DUT Vout (V)** |
| 5 | 0.1042879 | 50.03929 | 5.003929 | 0.089697 | 50.02368 | 5.003966 | 0.1013517 | 50.03966 | 5.002368 | 0.100 |
| 10 | 0.2095919 | 100.0095 | 10.00095 | 0.180312 | 100.0349 | 10.004928 | 0.2036846 | 100.04928 | 10.00349 | 0.200 |
| 15 | 0.3148474 | 150.0678 | 15.00678 | 0.27096 | 150.0546 | 15.0068 | 0.3061003 | 150.068 | 15.00546 | 0.300 |
| 20 | 0.4200059 | 200.0935 | 20.00935 | 0.361594 | 200.0807 | 20.00913 | 0.4085625 | 200.0913 | 20.00807 | 0.400 |

Figure 3-2 Layout Comparison Plot

# 4 Summary

This paper has discussed the challenges and high
susceptibility of low-ohmic shunts to parasitic effects such as PCB trace, solder
and copper plane resistance. To mitigate these issues, this paper has also discussed
variations across three PCB layouts through TINA-TI simulations and bench-test data,
which show similar trends. Layout 1 is has the greatest output voltage offset in
simulations, but Layout 2's measured output offset is larger. This could be
attributed to smaller solder resistances and shunt resistance variations. Layout 1
and 2's measured Vout mirror the simulation results. Finally, Layout 3 is proved to
be the most robust and effective since it has the smallest Vout offset,
as seen in both simulation and bench-testing.

# 5 Supplementary

## Supplementary Figures

Figure 5-1 INA190-Based Parallel Shunts
Schematics

Figure 5-2 Top-Side PCB Layout.

Figure 5-3 Bottom-Side PCB Layout

Figure 5-4 3D View of PCB Layout

Figure 5-5 Resistor Network
Configuration

# 6 References

* Texas Instruments and DesignSoft,
  *TINA-TI Analog Simulation Software (Version X.9.3.200.277 SF-TI)*,
  software.
* The Voltera Team. (2018, Oct.
  31). Resistance, Resistivity, and Sheet Resistance
  *https://www.voltera.io/blog/resistance-resistivity-and-sheet-resistance*
* Gou, X., Tang, Z., Gao, Y., Chen,
  K., & Wang, H. (2023). Current-Sensing Topology with Multi Resistors in
  Parallel and Its Protection Circuit. *Applied Sciences*, *13*(14),
  8382. https://doi.org/10.3390/app13148382
* KOA Speer Electronics,
  *Parallel Placement of Current Sensing Resistors* (TN003-v0100)