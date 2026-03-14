---
source: "TI SLUA376 -- Battery Charger Power-Path Management"
url: "https://www.ti.com/lit/an/slua376/slua376.pdf"
format: "PDF 14pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 18645
---

Application Report

Implementations of Battery Charger and Power-Path
Management System Using bq2410x/11x/12x
(bqSWITCHER™)
Lingyin Zhao........................................................................................................ PMP Portable Power
ABSTRACT
This application report presents four system topologies that can be used to fully
implement a portable power management system solution using the bqSWITCHER™.
Test results and the advantages and issues of each topology are discussed.
Contents
1 Introduction .......................................................................................... 2
2 Portable Power Supply and Battery Charger Architecture .................................... 2
3 Various Charger and Power-Path Management Solutions Using bqSWITCHER.......... 3
4 Conclusion ......................................................................................... 13
List of Figures
1 Direct Connection and Path Selection Topologies ............................................. 3
2 Topology 1........................................................................................... 4
3 Charge Current Response to the System Current Transients................................ 5
4 Waveforms at Power Up........................................................................... 6
5 Waveforms at Power Off........................................................................... 6
6 Topology 2........................................................................................... 7
7 Waveforms at Power On........................................................................... 7
8 Waveforms at Power Off........................................................................... 8
9 Waveforms Under a Transient System Load ................................................... 9
10 Topology 3 ......................................................................................... 10
11 Waveforms at Power On ......................................................................... 10
12 Waveforms at Power Off ......................................................................... 11
13 Topology 4 ......................................................................................... 12
14 Waveforms at Power On ......................................................................... 12
15 Waveforms at Power Off ......................................................................... 13
bqSWITCHER is a trademark of Texas Instruments.

Introduction
1 Introduction
The bqSWITCHER™ (bq2410x/1x/2x) series are highly integrated Li-ion and Li-polymer switch-mode,
charge-management devices. They are able to handle up to 20 V of input voltage and 2 A of charge
current with significant voltage difference between the input and output. The integrated power FETs and
the internal loop compensation circuitry minimize the number of external components and lower the design
and maintenance complexity. A high switching frequency (1.1 MHz) results in smaller external inductors
and capacitors. Therefore, the bqSWITCHER has emerged as one of the favorite battery charger solutions
for portable electronics, such as portable DVD players, MP3 players, etc.
Current trends in portable devices require operating the system while charging the battery pack. After the
ac adapter is disconnected, the battery pack powers the equipment. Each of the multiple approaches to
implementing this functionality has a specific impact on system cost, performance, and technical
challenges. The bqSWITCHER was designed as a stand-alone battery charger but can be easily adapted
to power a system load if one considers a few minor issues. This application report presents various
battery charger and power path management solutions based on the bqSWITCHER. Test results of each
solution are included and comprehensive discussions are presented.
2 Portable Power Supply and Battery Charger Architecture
The power-switching circuit connects external power supplies such as battery packs and external AC
adapters to the internal system power bus, which is the main supply for internal end-equipment
subsystems. The power-switching circuit architecture has a direct impact on end-equipment operation, and
it can lead to end-equipment malfunction if improperly designed.
The most common symptoms of problems related to the power-switching circuitry design are incorrect
status information such as false charge termination indication and unexpected end-equipment reset,
power down, or lockup.
Two main topologies are commonly used for the power-switching network: direct connection and path
selection topologies. Direct connection topologies isolate the external power supply from the battery pack
and system by connecting the battery pack positive terminal and the charger stage output to the system
power bus, as shown in Figure 1(a). In such a system, the maximum power delivered from the external
input supply to the system power bus is limited by the charger settings; the external supply is isolated from
the system power bus by the charger power stage.
In path selection topologies, the input power is split between the charger stage and the system. As shown
in Figure 1(b), the power sharing is made possible by the implementation of a switching network that
provides independent paths for the charger stage power and system power. The external input power is
directly connected to the system power bus.

Various Charger and Power-Path Management Solutions Using bqSWITCHER
SYSTEM POWER
BUS
CHARGER g Isys EQU E I N PM D- ENT
STAGE c h SUBSYSTEMS
I
EXTERNAL
INPUT
POWER
BATTERY
PACK
(a) Direct Connection Topology
EXTERNAL SYSTEM POWER
INPUT BUS
POWER
(Ichg + Isys) Isys END-
EQUIPMENT
SUBSYSTEMS
Ichg
CHARGER
STAGE
BBATTERY
PACK
(b) Path Selection Topology
Figure 1. Direct Connection and Path Selection Topologies
Based on the bqSWITCHER, the choice of a topology is dictated by the following end-equipment usage
modes:
1. Some types of direct connection topologies achieve the highest efficiency when the system is powered
by the battery due to the elimination of the switch between the system and the battery.
2. Direct connection topologies are simpler and more cost-effective.
3. If the end-equipment requires a peak current higher than 2.5 A, the direct connection topology is not
recommended due to the possibility of triggering the cycle-by-cycle current-limit protection.
4. If the end-equipment requires an average current higher than 2 A, the direct connection topology is not
applicable due to the potential thermal issues.
5. If the end-equipment requires an average current lower than 2 A but higher than 1 A, the direct
connection topology can be considered, but one needs to ensure that the resulting longer battery
charge time is acceptable.
6. The system voltage variation can be minimized by using direct connection topologies.
7. If the adapter input voltage is higher than the system voltage rating, a path selection topology cannot
be adopted.
3 Various Charger and Power-Path Management Solutions Using bqSWITCHER
As discussed, the candidate topologies can be classified into two categories: direct connection and path
selection.

3.1 Direct Connection Topologies
3.1.1 Topology 1: System Load After Sense Resistor
One of the simpler high-efficiency topologies connects the system load directly across the battery pack, as
shown in Figure 2. The input voltage has been converted to a usable system voltage with good efficiency
from the input. When the input power is on, it supplies the system load and charges the battery pack at
the same time. When the input power is off, the battery pack powers the system directly.
Bq24100/03/05
PG
V IN LL Isns Isys V sys (V Bat )
IN OUT
Rsns
CC Ichrg System
VTSB TTC Load
10 kW
Figure 2. Topology 1
The advantages:
1. When the AC adapter is disconnected, the battery pack powers the system load with minimum power
dissipations. Consequently, the time that the system runs on the battery pack can be maximized.
2. It saves the external path selection components and offers a low-cost solution.
3. Dynamic power management (DPM) can be achieved. The total of the charge current and the system
current can be limited to a desired value by setting the resistance connected to the ISET1 pin. When
the system current increases, the charge current drops by the same amount, as shown in Figure 3. As
a result, no potential overcurrent or over-heating issues are caused by excessive system load demand.
4. The total of the charge current and the system current can be limited to a desired value by setting the
resistance connected to the ISET1 pin. As a result, no potential overcurrent or over-heating issues are
caused by excessive system load demand.
5. The supply voltage variation range for the system can be minimized.
6. The input current soft-start can be achieved by the generic soft-start feature of the IC.

Figure 3. Charge Current Response to the System Current Transients
Design considerations and potential issues:
1. If the system always demands a high current (but lower than the regulation current), the charging
never terminates. Thus, the battery is always charged, and the lifetime may be reduced.
2. Because the total current regulation threshold is fixed and the system always demands some current,
the battery may not be charged with a full-charge rate and thus may lead to a longer charge time.
3. If the system load current is large after the charger has been terminated, the IR drop across the battery
impedance may cause the battery voltage to drop below the refresh threshold and start a new charge.
The charger would then terminate due to low charge current. Therefore, the charger would cycle
between charging and terminating. If the load is smaller, the battery has to discharge down to the
refresh threshold, resulting in a much slower cycling.
4. In a bqSWITCHER-based charger system, the precharge current is typically limited to about 10% of
the fast-charge current value, if the sensed battery voltage is below the precharge threshold, around 3
V for Li-ion battery packs. This results in a low power availability at the system bus. If an external
supply is connected and the battery is deeply discharged, below the precharge threshold, the charge
current is clamped to the precharge current limit. This then is the current available to the system during
the power-up phase. Most systems cannot function with such limited supply current, and the battery
supplements the additional power required by the system. Note that the battery pack is already at the
depleted condition, and it discharges further until the battery protector opens, resulting in a system
shutdown.
5. If the battery is below the precharge threshold and the system requires a bias current budget lower
than the precharge current limit, the end-equipment will be operational, but the charging process can
be affected depending on the current left to charge the battery pack. Under extreme conditions, the
system current is close to the precharge current levels and the battery may not reach the fast-charge
region in a timely manner. As a result, the precharge safety timers flag the battery pack as defective,
terminating the charging process. Because the bqSWITCHER precharge timer cannot be disabled, the
inserted battery pack must not be depleted to make the application possible.
6. For instance, if the battery pack voltage is too low, highly depleted, or totally dead or even shorted, the
system voltage is clamped by the battery and it cannot operate even if the input power is on.
7. Note that grounding the TTC pin disables both the timer (excluding the precharge timer) and the
termination functions, and keeps the converter on continuously. Pulling up the TTC pin disables the
timer but not the termination function. If TTC is pulled up or grounded, the battery is kept at 4.2 V (not
much different than leaving a fully charged battery set unloaded).

The test waveforms when input power is turned on and off are shown in Figure 4 or Figure 5, respectively.
The test was conducted under V = 12 V, V = 8 V, I = 1.3 A, I = 0.5 A.
IN BAT sns sys
Figure 4. Waveforms at Power Up
Figure 5. Waveforms at Power Off
3.1.2 Topology 2: System Load Before Sense Resistor
Topology 2 is similar to topology 1; the difference is that the system load is connected before the sense
resistor, as shown in Figure 6. The test waveforms when input power is turned on and off are shown in
Figure 7 and Figure 8, respectively. The test was conducted under V = 12 V, V = 8 V, I = 1.3 A, I
IN BAT sns sys
= 0.5 A.

Bq24100/03/05
PG Isys V SYS
V IN LL Ichrg (Isns) V
BAT
IINN OOUUTT
CC
System
VVTTSSBB TTTTCC Load
Figure 6. Topology 2
Figure 7. Waveforms at Power On

Figure 8. Waveforms at Power Off
The advantages of topology 2 compared to topology 1:
1. The charger controller is based only on what current goes through the current-sense resistor. So, the
precharge, constant current fast charge, and termination functions all work well and are not affected by
the system load. This is the major advantage of this topology compared to topology 1.
2. A depleted battery pack can be connected to the charger without the risk of the precharge safety timer
expiration due to high system load.
3. The TTC pin can be grounded to disable termination and keep the converter running and the battery
fully charged, or let the switcher terminate when the battery is full and then run off of the battery via the
sense resistor.
1. The total current is only limited by the IC peak current protection and the thermal protection thresholds
but not the charge current setting pin ISET1. The charge current does not drop when the system
current load increases, as shown in Figure 9. This solution is not applicable if the system requires a
high current.
2. Efficiency declines when discharging through the sense resistor to the system.

Figure 9. Waveforms Under a Transient System Load
3.2 Path Selection Topologies
3.2.1 Topology 3: PG Signal Driven Path Selection, Back-to-Back MOSFETs From Input to System
When the system requires a relatively high current, a charger with a power-path selection circuit is
preferred. The first option is employing two back-to-back MOSFETs (Q1 and Q2) driven by the PG signal
in the path from the input to the system, as shown in Figure 10. Driven by the reverse of the PG signal,
another power MOSFET Q3 is placed across the battery and the system.
When VIN is on, the input powers the system directly via Q1 and Q2 and the charger at the same time.
Q3 is off during this time. When the input adapter is removed, Q1 and Q2 turn off and Q3 turns on. This
action ties the battery to the system.
Soft turnon of Q2 may be necessary to minimize the inrush current during the transition. The turnon time
of Q2 can be adjusted by changing the value of the capacitor C1 across the gate and source.

Q1 Q2
V IN Isys V SYS
CC11
10 kW 10 nF System
20 kW Load
BATDRV
QQ33
LL
V
IINN OUOTUT BAT
Ichrg
C
bqSWITCHER
Figure 10. Topology 3
The test waveforms at power on and power off are shown in Figure 11 and Figure 12.
Figure 11. Waveforms at Power On

Figure 12. Waveforms at Power Off
1. Capable of carrying high system load current.
2. The precharge, constant current fast charge, and termination functions all work well and are not
affected by the system load.
3. Independent of each other, the system load does not impact the battery charger.
4. Because the system load current is supplied by the battery only after the input is too low and the
charger has been terminated, the charger does not cycle between charging and termination like
topology 1 and topology 2 can possibly do.
5. Even if the battery pack voltage is too low, for instance, highly depleted, totally dead, or even shorted,
the system still operates well as long as the input power is on.
6. Efficiency possibly higher than topology 1 and topology 2 when input is on, especially when a
significant voltage difference between the input and the system exists.
1. The topology is more complex, and the cost is higher.
2. The efficiency is lower than topology 1 when the battery powers the system due to the on-resistance of
Q3.
3. Higher system line voltage variation range.
If Q2 is removed, this topology still works, and one power MOSFET can be saved, thereby reducing the
cost. However, the input conducts to the system immediately via the body diode of Q1 at power up without
the reverse blocking MOSFET. It may lead to a significant battery current ringing.
If Q1 and Q2 are replaced by a power diode, the cost can be further reduced. However, the efficiency may
decline by 1%–15% while experiencing the similar high current ringing problem as previously discussed.

3.2.2 Topology 4: Input Driven Path Selection, Power Diode From Input to System
Topology 4 replaces Q1 and Q2 in topology 3 with a power diode D1. The gate drive of Q3 consists of a
diode D2, a resistor R1, and a capacitor C1 connecting to ground, as shown in Figure 13.
V D1 Isys V
IN SYS
R
SYS
CC SSYYSS
System
D2 BATDRV Q3 Load
10 nF 15 kW
PG C1
PG R1
LL
V
IINN OOUUTT BAT
II cchhrrgg
CC
bqSWITCHER
Figure 13. Topology 4
To ensure the break-before-make function of the path selector at VIN removal, one needs to ensure that
R ×© +C ) > R ×Csys, in which C is the gate-source capacitance of Q3 whereas R is
1 1 gs_Q3 sys_min gs_Q3 sys_min
the equivalent system resistance at the lightest load.
The test waveforms are shown in Figure 14 and Figure 15.
Figure 14. Waveforms at Power On

Conclusion
Figure 15. Waveforms at Power Off
1. Topology 4 is the lowest cost solution among the path selection topologies.
2. Without the time delay of PG signal, Q3 turns off more quickly during input power up. Therefore, the
current ringing problem may be relieved compared to the two non-back-to-back versions of topology 3.
4 Conclusion
With many remarkable features such as high integration, high input and output difference, and high
current, bqSWITCHER has emerged as one of the favorite charger ICs of portable electronics
manufacturers. To fully implement a portable power management system solution using bqSWITCHER,
this application report presents four system topologies which can be classified into two fundamental
architectures: direct connection and path selection. This application report demonstrated the test results
and comprehensively discussed the advantages and issues of each topology.
