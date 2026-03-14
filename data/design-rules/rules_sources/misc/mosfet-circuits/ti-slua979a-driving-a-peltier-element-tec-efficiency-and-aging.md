---
source: "TI SLUA979A -- Driving a Peltier Element (TEC): Efficiency and Aging"
url: "https://www.ti.com/lit/an/slua979a/slua979a.pdf"
format: "PDF 7pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 11836
---

Application Report

Driving a Peltier Element (TEC): Efficiency and Aging
Olivier Mellin, Florent Muret
ABSTRACT
The Peltier module is used on certain equipments in the industry that require critical temperature
protection. However, it is often perceived as inefficient, cumbersome, and expensive. The purpose of this
application report is to determine the module performances by driving it with Texas Instruments
components, and seeing what performances can be achieved with reasonable power and equipment. A
comparison between constant current drive and PWM drive is made, as constant current is often
perceived as more efficient. Moreover, this application report gives a study of the aging of the module,
depending on the drive.
Contents
1 Introduction ................................................................................................................... 1
2 Definition of Peltier Efficiency .............................................................................................. 2
3 Setup TPS54201-Q1 and DRV8873-Q1.................................................................................. 2
4 Peltier Aging.................................................................................................................. 4
5 Conclusion.................................................................................................................... 5
6 References ................................................................................................................... 5
List of Figures
1 Peltier Module: Drive Schematic Example ............................................................................... 1
2 Peltier Module: Cold Side Efficiency ...................................................................................... 1
3 Constant Current Setup..................................................................................................... 2
4 PWM Current Setup......................................................................................................... 2
5 Efficiency Test: 1 A Constant Current Drive ............................................................................. 3
6 Efficiency Test: 2 A Peak - 50% Duty Cycle - 1 A Average PWM Current Drive ................................... 3
7 Performance Differences Between Ambient Temperature and Cold Side Temperature for Constant
Current and PWM Current ................................................................................................. 3
8 Performance Differences Between Ambient Temperature and Hot Side Temperature for Constant
Current and PWM Current.................................................................................................. 3
9 Peltier Aging Test Over One Month ....................................................................................... 4
List of Tables

1 Introduction
The Peltier Module is a device with an interesting feature. When voltage is applied across its inputs, a flow
of DC current is created across the junction of the semiconductors, causing a temperature difference. The
side with the cooling plate absorbs heat which is then moved to the other side of the device where the
heat sink is. Thermoelectric coolers (TECs) are typically connected side-by-side and sandwiched between
two ceramic plates. The cooling ability of the total unit is then proportional to the number of TECs in it.

Figure 1. Peltier Module: Drive Schematic Example Figure 2. Peltier Module: Cold Side Efficiency
This behavior can be used to generate heat, cold, or switch between the two options just by reversing the
drive polarity.
2 Definition of Peltier Efficiency
This section gives an overview about the performance that can be reached using a reasonable amount of
power. For this test, a 17.9 W, 3.9 A, 7.6 V, 30-mm x 15-mm ET-063-10-13 Peltier module is used. The
performances can be defined by the difference of temperature between the ambient temperature and the
cold side, as well as the difference of temperature between the ambient temperature and the hot side.
(1)
(2)
In order to test the Peltier performances, a heat sink is added, which allows dissipating the heat generated
by the hot side. This is an important parameter, which needs to be seriously taken in to consideration, as it
influences a lot of the performances of the Peltier.
3 Setup TPS54201-Q1 and DRV8873-Q1
In this study, the Peltier module is driven in current as it is made with PN junction. Therefore, it is more
accurate to use constant current drive than voltage drive as its impedance varies with temperature. Delta
T remains constant across the entire temperature range when driven in current. While driven in voltage,
the delta T does not remain constant as the TEC impedance varies with temperature.
In order to determine which type of current is more efficient, tests are performed with both constant current
and PWM current (at 50% duty cycle).
• Constant current: The simplest way to drive the module is with a constant current. In this application, a
TPS54201-Q1 was used to supply a constant current. Although it is a switcher, the output filter
provides a near constant current source with only marginal ripple.
• PWM driving: A common way of modulating the current is to pulse current through the load, then
keeping the peak current constant and varying the ON and OFF duty cycle to make the average
current change. This is commonly referred to as PWM driving. In this use case, the full bridge motor
driver DRV8873-Q1 was used to reverse the heat and cold side when needed.
Figure 3 and Figure 4 show the two block diagrams of the two setups.
Figure 3. Constant Current Setup Figure 4. PWM Current Setup

Precise that no filtering is used between the H bridge driver and the Peltier module (the hardware used for
this demo is the DRV8873-Q1 without modification). The temperature is recorded by using three accurate
sensors, the TMP107-Q1, which respectively senses the hot side, the cold side, and the ambient
temperature. Thermal paste is added under the temperature sensors to increase the thermal transfer,
which leads to more accurate temperature reading.
Figure 5 and Figure 6 show the performances with a 1 A drive: one with constant current, and one with
PWM current (0 A/2 A – 50% duty cycle which leads to a 1-A average current, with a 20-Khz PWM
frequency).
Figure 5. Efficiency Test: 1 A Constant Current Drive Figure 6. Efficiency Test: 2 A Peak - 50% Duty Cycle - 1
A Average PWM Current Drive
As seen in Figure 6, while using constant current, the difference of temperature between the cold side and
the ambient temperature is 8.1°C greater than while using PWM current. Using constant current is 39.2%
more efficient than the PWM current. As the ambient temperature for the tests are around 25°C, ice was
created all around the module, as seen in Figure 2. After several tests at different currents, efficiency
slopes were created to compare both drives. See Figure 7 and Figure 8 for the efficiency slopes.
Figure 7. Performance Differences Between Ambient Figure 8. Performance Differences Between Ambient
Temperature and Cold Side Temperature for Constant Temperature and Hot Side Temperature for Constant
Current and PWM Current Current and PWM Current

As shown in Figure 7 and Figure 8, the PWM current is constantly inferior in terms of efficiency for a wide
current range. The temperature differences created with the two types of drive are constant with a 8.2°C
gap between the cold side and the ambient temperature, and a 2.5°C gap between the hot side and
ambient temperature, for both current drive.
An alternative to the full bridge to drive the Peltier module in constant current while keeping the ability to
reverse the drive polarity would have been to use a buck boost converter, such as the TPS63020. See the
Low-power TEC Driver Application Report for more information about this topology.
4 Peltier Aging
This section studies the impact of aging on the Peltier module. In order to know how much the
performances are reduced due to the wear out, the following test was performed. During five months, two
Peltier modules with the same efficiency performances were continuously submitted to a constant current
drive of 1.4 A. One Peltier module was with PWM current, and the other one was with constant current
(using the DRV8873-Q1 and the TPS54201-Q1 respectively).
During this time, an autonomous setup recorded the temperature of the cold side, the hot side, and the
ambient temperature every 20 minutes. Figure 9 shows the result of this test after one month of aging.
Figure 9. Peltier Aging Test Over One Month
As seen in Figure 9, there is a constant fluctuation for all temperatures (hot side/cold side/ambient
temperature), which is due to the variation of the temperature in the room where the tests are performed.
It shows that the temperature on the cold side of the Peltier module is really dependent on the ambient
temperature. However, the performances (ΔT between ambient temperature and cold side) remain almost
stable. The performance decreases slightly as shown by the purple trendline slope.

After this month of aging, the efficiency tests were performed again and showed no performance
difference. The observed loss of efficiency actually corresponded to the degradation of the thermal paste
(which permits to improve the thermal bonding) between the Peltier module and the temperature sensors.
The same test was then performed four months afterward. The following are the results:
• PWM current: The ΔT between the cold side and the ambient temperature does not change. The
results stay the same over the time.
• Linear current: The ΔT between the cold side remains the exact same.
5 Conclusion
This application report shows that with a reasonable amount of power budget (2.5 V at 1 A, 2.5 W), even
though the Peltier is not cooling anything, significant temperature differences were obtained, which can be
interesting in some applications.
Moreover, constant current drive is definitively preferred over PWM drive. If the design requires the ability
to reverse polarity, the full bridge is the most flexible option but it significantly reduces the efficiency. The
buck boost TPS63020 is an alternative. Finally, testing for five months continuously (3600 hours) does not
seem to have any significant measurable performance influence.
6 References
• TPS54201-Q1: TPS54201 4.5-V to 28-V Input Voltage, 1.5-A Output Current, Synchronous Buck
Mono-Color or IR LED Driver
• TPS54201 EVM: TPS54201 4.5V-to-28V Input Voltage, Synchronous Buck LED Driver Evaluation
Module
• DRV8873-Q1: Automotive H-bridge Motor Driver with Integrated Current Sensing and Current Sense
Output
• DRV8873-Q1 EVM: Automotive 10A H-Bridge Motor Driver with SPI Interface and Integrated Current
Sensing EVM
• TMP107-Q1: ±0.4°C Temperature Sensor with Daisy-Chain UART, EEPROM, and Alert Function,
• TMP107EVM: TMP107 Evaluation Module
• MSP430F5529 Launchpad: 25 MHz MCU with Integrated USB Phy, 128 KB Flash, 8 KB RAM,
12Bit/14 Channel ADC, 32BIT HW Multiplier
• TPS63020: High Efficiency Single Inductor Buck-Boost Converter with 4 A Switch, EVM

Revision History
NOTE: Page numbers for previous revisions may differ from page numbers in the current version.
Changes from Original (July 2019) to A Revision ........................................................................................................... Page
• Updated content in Section 3............................................................................................................ 2