---
source: "TI SBVA084 -- Increase Battery Life With Nano Quiescent Current LDO"
url: "https://www.ti.com/lit/an/sbva084/sbva084.pdf"
format: "PDF 6pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 9422
---

Application Report

Increase Your Battery Life With Nano Quiescent
Current LDO
ABSTRACT
With the increase in battery powered applications like metering, wearables, building automation and other
internet-of-things (IoT) systems, one of the major challenges that is faced by the power design industry is
to design an efficient power supply circuit that reduces the overall power consumption of the system and
prolongs battery life. One common solution to this problem is to sub regulate the power supply of the
system using a power IC like a low-dropout regulator (LDOs), that provides a stable DC supply converted
down from the battery voltage. This document explains how the power consumption of a low-power nano
I LDO like TPS7A02 will impact the overall battery life of the system compared to one using a traditional
Q
LDO.
Contents
1 Description ................................................................................................................... 2
2 Components of the System ................................................................................................ 2
3 Conclusion ................................................................................................................... 4
List of Figures
1 System Block Diagram ..................................................................................................... 2
2 MCU Timing Diagram ...................................................................................................... 2
3 TPS7A02 LDO Current Efficiency ........................................................................................ 3
4 Battery Life in Years vs LDO Quiescent Current ........................................................................ 5
List of Tables
1 Battery Life Comparison .................................................................................................... 4

1 Description
For this analysisa simple system is used in which a low-power MCU is being powered by an LDO. Next,
an assessment of the impact of current consumption from the individual components in the circuit on
battery life is made. The LDO is used to sub-regulate the battery power supply voltage down to a fixed DC
voltage needed for the MCU.
VBATT = 1.8 Ví4.2 V
Battery
LiOn Pulsed Load
Li-Coin LDO
LiMnO2
AA (2s) COUT
AAA (2s)
MCU
IQ (LDO)
Figure 1. System Block Diagram
For a system like this, there are 4 main components that contribute to the total power consumption; the
quiescent current consumption of the LDO, the current consumption of the MCU, the self-discharge of the
battery, and the leakage of the output capacitor. The total current consumption of the system therefore
can be calculated using Equation 1:
I Total = I Q(AVG, LDO + MCU) + I BL + I CL (1)
The total battery life in years can be calculated with Equation 2:
Battery Capacity
Battery Life =
I Total (2)
2 Components of the System
2.1 MCU
Modern low-power MCUs are designed to maximize battery life by spending most of the time in standby or
sleep mode (T ) and wake up periodically or with interrupts to perform specific software operations in
S
active mode and then return to standby mode once completed. This creates a pulsed current load
behavior on the supply and is illustrated in Figure 2.
Standby Period
T
s
T
a
Active Period
Figure 2. MCU Timing Diagram
Typically during the active mode the MCU consumes a current that is a function of its internal clock
frequency. Calculate this using Equation 3.
æ I ö
Active Current, I = ç Q ÷ ´Frequency
QA è Hz ø (3)
In standby mode, the current consumed (I ) of the MCU is much lower compared to the active current
QS(MCU)
to save power.

Output Current (mA)
I = I + I
QS(total) QS(MCU) QS(LDO)
Active Current ´ Active Time + S tandby Current ´ S tandby Time
I =
Q(AVG)
Total Time
I ´ T + I ´ T
I = QA(Total) A QS(Total) S
Q(AVG) T + T
A S
Q ´I %
I = L
BL 24 ´ 365
)%(
ycneiciffE
tnerruC

2.2 LDO
The LDO powering the MCU is an important component of the total current consumed in the system. Most
traditional LDOs are designed to consume low quiescent current. This means that they will typically have
low bandwidth and demonstrate slow dynamic response to fast current load changes.
Modern low I LDOs like the TPS7A02 device use novel biasing techniques which allow the LDO to
dynamically increase its bandwidth (and current consumption) based on its instantaneous load current.
Furthermore, the TPS7A02 device achieves this while maintaining high current efficiency with respect to
the current load. Current efficiency is defined in Equation 4:
I
OUT
Current Efficiency (h )% = ´100%
i I OUT + I Q (4)
Figure 3 shows how the TPS7A02 device maintains a current efficiency of ≥ 98% for loads higher than
10 µA.
102
100
98
96
94
92
90
88
86
84
0.001 0.01 0.1 1 10 100200
Figure 3. TPS7A02 LDO Current Efficiency
In active mode, the MCU would consume current in the order of several 100 s of µA. As Figure 3 shows,
at this level of current load the TPS7A02 operates at close to 100% efficiency. So we can assume that in
active mode, most of the current consumed by the system is due to the MCU and the impact of the current
consumption of the LDO on the total I is negligible.
Whereas during the standby mode the I consumed by the MCU is much lower in magnitude. At lower
current loads the LDO’s current efficiency also decreases. So the quiescent current of the LDO can
become a significant portion of the total system current consumption in standby mode.
(5)
Considering that this system runs a majority of the time in the standby mode and turns on only for a small
duration of the time, the average quiescent current it consumes can be calculated using Equation 6:
(6)
2.3 Battery Leakage
As batteries age over their lifetime, they start experiencing higher leakage currents and undergo self
discharge even when they are not connected to any electrodes. The amount of self discharge the battery
undergoes is a function of the battery type and chemistry and can be elevated by the aging and
temperature of operation. As an example, consider that the self-leakage of the battery is I % per year. This
L
means for a battery of capacity Q mAh, the total current consumed due to its self-leakage is calculated
using Equation 7:
(7)

2.4 Output Capacitor Leakage
Most LDOs require an output capacitor for stability. The leakage current consumed by this output
capacitor is also a component of the total system current consumption. The TPS7A02 LDO can be
stabilized with a very small ceramic capacitor which helps to reduce this effect. The leakage current of the
ceramic capacitor is usually specified in insulation resistance (Ω) and the leakage current can be
estimated by the ratio of the rated capacitor voltage and insulation resistance (I = V/R). This parameter is
defined as I . This capacitor leakage varies by manufacturer, temperature, charging profile, and product
CL
family so the actual part measurement over operating conditions is strongly recommended.
3 Conclusion
All the components discussed in this application report contribute to the total current consumed by this
system. So as Equation 1 shows, the total current consumption of the system therefore can be calculated
with Equation 8:
I = I + I + I
Total Q(AVG) BL CL (8)
The total battery life can be calculated as a function of the capacity of the battery and the total current
consumed in the system and can be shown to be the same as Equation 2:
Battery Capacity
Battery Life =
I Total (9)
Use these equations to calculate and compare the battery life of a nano power LDO like the TPS7A02,
which consumes current of only 25nA with a traditional low I LDO like the TPS7A05 device, which
consumes current of 1 µA. Observe that the battery life of a system can be increased from 5 years to 8.7
years by using a nano-I LDO compared to a traditional low I LDO.
Q Q
Table 1. Battery Life Comparison
Parameter LDO (1) TPS7A02 LDO (2) TPS7A05
LDO I (µA) 0.025 1
MCU active mode µA/MHz 100 100
MCU frequency (MHz) 16 16
Active MCU current (µA) 1600 1600
Standby MCU current (µA) 1 1
Time ratio (Ts, standby/ Ta, active) 10000 10000
Average active current (µA) 1.18 2.16
Battery capacity (mAh) 100 100
Battery leakage % per year 1% 1%
Battery leakage - µA 0.11 0.11
LDO output capacitor leakage - µA 0.01 0.01
Total hours 76392 43784
Total years 8.7 5.0

LDO Quiescent Current (PA)
sraeY
ni
efiL
yrettaB

A plot can be made using the same equations that shows how the battery life of the system is impacted by
varying quiescent current. Figure 4 shows how using an LDO with low I in standby mode can significantly
affect the battery life of the system.
9
8.5
8
7.5
7
6.5
6
5.5
5
4.5
4
3.5
3
2.5
2
0 0.25 0.5 0.75 1 1.25 1.5 1.75 2 2.25 2.5
Batt
Figure 4. Battery Life in Years vs LDO Quiescent Current
This demonstrates the impact of the quiescent current of the LDO on the battery life of the system and the
benefit that the ultra low I LDO like the TPS7A02 device provides. For a duty-cycled system where the
system stays in standby mode for most of the duration and turns on only for a small amount of time, the
battery life of the system can be doubled using a 25-nA I LDO vs a 1.5-µA I LDO.
Q Q