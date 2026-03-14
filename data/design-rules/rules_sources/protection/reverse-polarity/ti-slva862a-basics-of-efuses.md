---
source: "TI SLVA862A -- Basics of eFuses"
url: "https://www.ti.com/lit/pdf/slva862"
format: "PDF 14pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 29586
---

Application Report

Basics of eFuses
Rakesh Panguloori.................................................... Power Switches
ABSTRACT
eFuses are integrated power path protection devices that are used to limit circuit currents, voltages to safe
levels during fault conditions. eFuses offer many benefits to the system and can include protection
features that are often difficult to implement with discrete components. This application note highlights the
challenges and limitations of discrete circuit-protection solutions and discusses how they can be improved
with an eFuse. This report also provides an example comparison between eFuse solution and discrete
circuit-protection solution for a typical hard disk drive (HDD) application.
Contents
1 Need for Protection and Ways to Achieve......................................... 2
2 Discrete Circuit-Protection Solutions ........................................... 2
3 What is an eFuse?...................................................... 4
4 Typical Application Example for Comparison...................................... 11
5 Conclusion ......................................................... 12
6 References ......................................................... 12
List of Figures
1 Typical Discrete Protection Circuit............................................. 3
2 Active Current Protection Circuit Using Discrete Components ............................ 3
3 Block Diagram of eFuse .................................................. 4
4 Overload Response of eFuse With Current-Limiting Function............................. 5
5 Overload Response of eFuse With Circuit-Breaker Function.............................. 5
6 Fast-Trip Current....................................................... 6
7 Short-Circuit Response of TPS259241 With I Set to 5 A .............................. 6
LIM
8 Fast-Trip Comparator Response for a Hot-Short Fault ................................. 6
9 Reverse Current Protection Using (a) Diode (b) External MOSFET and Ideal Diode Controller (c) eFuse ..... 6
10 Output Voltage-Cutoff for an Overvoltage Fault .................................... 7
11 Output Voltage-Clamp during Transient Input Overvoltage............................... 7
12 TPS25942L: Latched for Short-Circuit Fault ....................................... 8
13 TPS25942A: Auto-Retry and Recovery From Short Circuit .............................. 8
14 Input Reverse Polarity Protection Using (a) Diode (b) P-MOSFET (c) Fuse + TVS Diode (d) TPS2600 eFuse 9
15 Surge Protection Solution Using TPS2660 eFuse ................................... 9
16 Circuit Implementation With Quick Output Discharge Function............................ 10
List of Tables
1 Design Parameters..................................................... 11
2 Comparison Table...................................................... 11

1 Need for Protection and Ways to Achieve
Modern electronic systems are designed with high level of integration to offer superior performance with
multitude of functionality. These systems use multi-voltage power distribution to support various types of
loads for their proper operation. One of the major expectations is the minimal system downtime during any
transient abnormal events such as overload or short-circuit conditions. For example, while hot-plugging a
hard disk drive into a storage system, huge inrush current can result in voltage sag on the connected bus
and eventually affect other operating loads on the same bus. To overcome this scenario, today’s system
designers use protection devices to manage inrush, overload, short circuit, and overvoltage events and to
guard the sensitive loads for reliable system operation. The key requirement is to bring down the fault
currents within the limits and bring the system back to active state once the fault is cleared, without any
manual intervention.
Fuses, positive temperature coefficient (PTC) resistors, and active circuit protection are a few of the
protection devices with varied capabilities and drawbacks. Fuses are traditionally considered as protection
devices used to isolate overload or short-circuit faults from the main system. Although these devices
provide protection, the fault current needs to be exceedingly higher than the rating of the fuse with
response time ranging from milliseconds to seconds. This makes it extremely difficult to predict the precise
overcurrent level at which the fuse will open. A conservative selection on fuse current rating may lead to
fuse blowup during inrush current events. In addition, once the fuse blows during an overload event, it has
to be physically replaced, which increases system down time and maintenance costs. On the other hand,
PTC resistors provide resettable overcurrent protection and, unlike a fuse, these can avoid the physical
intervention. However, because they are actuated by the heating effect of an overcurrent load, their
reaction time is limited to several milliseconds. Also the ON-resistance of PTC fuse increases after every
reset, which raises concerns on achieving repeatable performance over time.
The best way to prevent system downtime is to detect, respond and correct potentially damaging
conditions as quickly as possible. As the response of fuse and PTC resistors depends on heating effect
(temperature, a lagging parameter) for their operation, many system designers prefer to use a leading
indicator, current, to provide effective circuit protection. Both fuse and PTC resistors do not cover many of
the protection requirements such as inrush control, overvoltage; reverse current, reverse polarity
protections needed in modern electronic systems. The next section describes the active circuit-protection
solutions using discrete components and the challenges involved.
2 Discrete Circuit-Protection Solutions
Many of the discrete circuit-protection solutions use a combination of fuses, diodes, MOSFETs, and TVS
diodes to meet a specific protection requirement. A typical discrete circuit using a combination of fuse and
MOSFET is shown in Figure 1. The protection circuit incorporates inrush current control using P-MOSFET,
a series diode to block the reverse current as well as reverse polarity, a fuse for overload or short-circuit
protection, and comparator logic to disconnect the power path during undervoltage or overvoltage events.
The inrush current limiter avoids voltage sag on the connected bus during hot plug events and helps in
optimal fuse-sizing for a precise overcurrent level. However, challenges with current-limit inaccuracies with
temperature and slower response still exist. An active current-protection circuit shown in Figure 2 can
respond faster to overcurrent faults and provides better current-limit accuracies. However, many of the
discrete circuit-protection realizations have the following shortcomings which limit their wider usage:
• Discrete circuits use P-MOSFET as pass FET, which is more expensive than N-MOSFET to achieve
the same ON resistance (R ).
DS(ON)
• Discrete solutions are bulky and inefficient. For example, a 2-A load current results in around 1.4-W
power dissipation across the diode and corresponding rise in board temperature.
• Discrete circuits do not incorporate thermal protection for the pass FET. So the thermal design is often
more oversized than safe operating area (SOA) limits for device protection under extreme cases.
• A discrete circuit needs more components and occupies more board space. More components also
raise concerns on protection-circuit robustness and reliability.
• Though the output voltage slew rate is adjustable with RC components, these components must be
sized in consideration with the gate characteristic of the pass FET.

VIN VOUT
System Load
ENABLE
VIN
+
±
Figure 1. Typical Discrete Protection Circuit
System Load
ENABLE
Figure 2. Active Current Protection Circuit Using Discrete Components

3 What is an eFuse?
An integrated circuit protection solution called “eFuse” can overcome the limitations with discrete circuit
protection realizations. An eFuse is an “active circuit protection device with an integrated FET used to limit
currents, voltages to safe levels during fault conditions”. It embeds various functions to protect system
against inrush current, overcurrent, overvoltage, reverse current, reverse polarity and short circuit faults.
The eFuse is more accurate, faster and can ‘repair’ itself without user intervention. Most of the TI eFuses
are recognized as Solid State Overcurrent Protectors under the UL2367 standard. Also these are certified
under safety standard UL 60950 and are safe to use.
Figure 3 shows a block diagram of an eFuse. An understanding of the functionality of various features in
an eFuse helps in choosing the right eFuse for a particular application. This section discusses the
functionality of each feature the eFuse offers. As shown in Figure 3, an eFuse requires very few external
components (resistor R for current limit setting and a capacitor C for setting the output voltage ramp
ILIM dVdT
rate) resulting in significant board space saving and robust protection when compared to discrete
solutions.
Blocking FET* Pass FET
Overvoltage Protection
Reverse Current
or Charge Pump
Protection*
Overvoltage Clamp
EN /
UVLO Enable/
Undervoltage Gate
Lockout Control
Output Ramp Fast-Trip with Current Limiting
Control or
Fast-Trip with Circuit Breaker
CdVdT Thermal
Shutdown Load Current Monitor* RILIM
Power Good Indicator*
Fault Indicator*
Diode Mode*
Low Power Mode*
*Not present on all eFuses
Figure 3. Block Diagram of eFuse
3.1 Inrush Current Control
Inrush currents are a major concern in DC power systems. For example, while hot-plugging a hard disk
drive into a storage system, huge inrush current can result due to quickly charging its filter or load
capacitor. This huge inrush current with fast slew rate causes voltage sag on the backplane which could
affect operation of other connected loads. This problem can be solved by controlling the output voltage
ramp rate, thereby limiting the inrush current and disturbance on the backplane. Discrete circuits
(Figure 1, Figure 2) use RC components around pass FET for inrush current control, which must be sized
in consideration with the gate characteristic of the pass FET and the load. Sometimes, it needs many
design iterations to keep inrush current within the desired limit. If the input power is cycled rapidly, the
load capacitor gets discharged quickly while the external gate capacitor remains charged and maintains
pass FET in the ON condition. This inhibits the current-limiting feature allowing a large current surge when
power is restored.
In an eFuse, the output voltage ramp rate is inversely proportional to the C capacitor value and can be
dVdT
configured easily at the desired rate. The built-in overtemperature protection in an eFuse prevents device
failure that could happen due to severe dynamic power stress during startup. Refer to Section 4 for the
inrush performance comparison between eFuse and a discrete solution.

3.2 Overcurrent Protection
When an overcurrent event happens, protection for the downstream circuitry from excessive currents is
essential to avoid any potential circuit damage or fire. The active current protection circuit shown in
Figure 2 uses an external current sense resistor and a fast comparator for overcurrent protection. This
circuit realization often needs tradeoff between accuracy, cost, and power loss. TI eFuses provide active
current protection either by limiting the fault current (called current-limiting operation) or by breaking the
fault circuit after an overload timeout (called circuit-breaker operation). The latest devices, such as the
TPS25942 and TPS25944, offer ±8% current-limit accuracy over the load range of 0.6 A to 5.3 A.
An eFuse with the current-limiting feature limits the output current to a threshold set by an external resistor
R . Figure 4 shows the current-limit response of the TPS25942A eFuse, with the current limit (I ) set to
ILIM LIM
5 A. For an overload condition, the eFuse limits the input current to 5 A until either the overload is
removed or the eFuse junction temperature T reaches thermal shutdown temperature (typically T =
J TSD
150°C). Once the eFuse enters thermal shutdown, it either remains in the OFF position (a latch-off
version) or attempts to restart after T falls below T by 12°C and with auto retry delay (128 ms for
TPS25942A, an auto-retry device). It is observed in Figure 4, the TPS25942A makes circuit closure after
every thermal shutdown and finally restores to normal condition when the overload fault is cleared. The
current-limiting feature is beneficial in applications such as solid-state drives (SSDs), especially if the
overcurrent event is temporary and to avoid system downtime.
Figure 4. Overload Response of eFuse With Current- Figure 5. Overload Response of eFuse With Circuit-
Limiting Function Breaker Function
For sensitive loads, such as a hard drive in data servers, an immediate power path opening is a safe
option in response to an overcurrent fault. An eFuse TPS25944A provides circuit-breaker operation with
overload timeout. When the load current exceeds the set current limit of 5 A, the TPS25944A starts the
fault timer and breaks the circuit path if the load current does not fall below I before the fault timer
expires (4 ms). Figure 5 shows circuit-breaker response of the TPS25944A eFuse, and since the
TPS25944A is an auto retry device, it attempts to restart after a circuit-breaker retry delay of 128 ms. The
circuit-breaker feature essentially avoids system downtime by allowing pulsed overloads at the output for a
fault period interval of 4 ms..
3.3 Short-Circuit Protection
One of the advantages of an eFuse over discrete solutions is the ability to respond faster for hot-short
faults at the output. During a transient short-circuit event, the current through the eFuse increases very
rapidly. The current-limit amplifier of an eFuse cannot respond very quickly due to its limited bandwidth. TI
eFuses incorporate a fast-trip current comparator, which shuts down the pass FET very quickly when the
load current I > fast-trip current threshold I . This terminates the rapid short-circuit peak current in
OUT FASTRIP
less than 200 ns as shown in Figure 8. The fast trip threshold is set to 60% higher than the programmed
overload current limit (I = 1.6 × I ). After the transient short-circuit peak current has been
FASTRIP LIM
terminated by the fast-trip comparator, the current-limit amplifier smoothly regulates the output current to
I as shown in Figure 7. If during current-limit operation, power dissipation of the pass FET [(VIN –
VOUT) × I ] exceeds 10 W, there is approximately a 0 to 15% thermal fold back in the current-limit value
OUT
so that I drops to I . Eventually, the device shuts down due to over temperature.
LIM SC

IFASTRIP
Blocking FET Pass FET
VIN VOUT VIN VOUT VIN VOUT
S L y o s a te d m IN OUT S L y o s a te d m S C m o a n rt t r D ol i l o e d r e High S C i o d n e t r P o r l o le t r ection S L y o s a te d m
Ideal Diode Controller
GND
(a) (b) (c)
timiL
tnerruC
IFASTRIP = 1.6 × ILIM
ILIM
Thermal Foldback
0-15%
ISC
Figure 6. Fast-Trip Current
Figure 8. Fast-Trip Comparator Response for a Hot-Short
Figure 7. Short-Circuit Response of TPS259241 With I
LIM Fault
Set to 5 A
3.4 Reverse Current Protection
Reverse currents can flow through the system when the voltage at the output is higher than at the input. In
applications such as power muxing for redundant power systems or SSD with a large hold-up output
capacitor, there is a risk of large reverse currents when the input power is disconnected. The reverse
current can damage internal circuitry or system power supplies, if it is not limited. For certain applications
such as PLC controller modules, this feature is mandatory to pass ‘voltage interruption tests’.
Figure 9. Reverse Current Protection Using (a) Diode (b) External MOSFET and Ideal Diode Controller (c)
eFuse

A series diode can block reverse currents but results in significant power loss in the system which could
lower the system efficiency and battery life. An external MOSFET with an ideal diode controller IC (shown
in Figure 9(b)) is a more efficient option and also offers flexibility in current support; however, it occupies
more board space. TI's TPS2594 family of eFuses integrates blocking FET and a fast reverse comparator
to provide true reverse current blocking. When an input power fail condition is detected, the internal FET is
turned OFF in 1 µs (typical). True reverse current blocking facilitates simplified efficient power muxing in
redundant power systems. For additional information regarding power multiplexing using eFuses, see
reference (1).
3.5 Overvoltage Protection
Transient induced voltages or inductive switching can cause overvoltage in the system which lasts from a
few hundred microseconds to milliseconds. An eFuse with output voltage-cutoff guards the sensitive
circuits from overvoltage by turning OFF the internal FET. The trip point for overvoltage cutoff can be
programmable through an external resistor at the OVP pin of eFuse. As shown in Figure 10, the
TPS25942x remains active for a nominal 12-V input voltage. When the input voltage exceeds the
overvoltage trip point (16.5 V here), the eFuse turns OFF the internal FET causing the output voltage
VOUT to fall to zero. The eFuse remains in the OFF condition as long as the input voltage exceeds the
set overvoltage trip point. Once the input voltage returns to nominal operating voltage, the device turns
back ON and VOUT once again returns to 12 V. The latest eFuse device, TPS2660, protects the load up
to 60-V DC Safe Extra Low Voltage (SELV) faults and is suitable for industrial applications.
Figure 10. Output Voltage-Cutoff for an Overvoltage Fault Figure 11. Output Voltage-Clamp during Transient Input
Overvoltage
Some of the TI eFuses have an output voltage-clamp (OVC) feature, which keeps eFuse in operation by
clamping the output voltage to the nominal voltage. As shown in Figure 11, the TPS25926x eFuse
integrates a 15-V output voltage-clamp. When the input voltage exceeds the internal OVC trip point, the
internal clamping circuitry activates and limits the output voltage to 15.6 V (typically 15 V). If the transient
on the input is only temporary, the eFuse hides the overvoltage fault from downstream circuitry. If the fault
lasts long enough to activate the eFuse’s thermal shutdown (typically T = 150°C), then the fault will still
J
cause the eFuse to turn OFF (similar to output voltage-cutoff).
3.6 Over Temperature Protection
Discrete protection realizations need careful selection of pass FET and thermal design to keep the device
in SOA limits under any extreme fault conditions. However, TI eFuses come with inbuilt over temperature
protection and gets shutdown if the eFuse junction temperature, T , exceeds 150°C (typ). Once eFuse
J
enters thermal shutdown, it either remains in the OFF position (a latch-off version) or attempts to restart
(an auto retry version) after T falls below T by 12°C and with auto retry delay.

3.7 Fault Response and Recovery
TI eFuses are available in two versions; latch off and auto retry. A latch-off version remains in the OFF
position and needs power recycle to turn ON again. A system with the latch-off version provides more
safety by immediately isolating the faulty component but also reduces the system uptime. Figure 12 shows
the short-circuit response of the latched device TPS25942L, where the device provides a limited current of
5 A before getting into thermal shutdown. A reset at the enable pin is required to bring the device back
into operation. On the other hand, a device with auto retry continues to power cycle itself until the fault is
cleared. As shown in Figure 13, the device TPS25942A attempts to power cycle after retry delay (128 ms)
and resumes normal operation when short circuit is cleared. Since, over-temperature protection is inbuilt,
no special thermal considerations are required for surviving a prolonged output short.
Figure 12. TPS25942L: Latched for Short-Circuit Fault
Figure 13. TPS25942A: Auto-Retry and Recovery From
Short Circuit
3.8 Input Reverse Polarity Protection
In applications such as PLC systems, the input side needs reverse polarity protection against any field
supply mis-wiring. A blocking diode is the simplest means of protecting against reverse polarity
connections. Since no control signal is required, circuit complexity and component count are low. On the
other hand, the diode dissipates energy all the time due to its forward voltage (V ) drop, which can cause
F
significant power loss in high-current applications and needs thermal management. Another approach is to
use a P-MOSFET, which can be implemented with simpler drive circuitry comprising a Zener diode and a
resistor, as shown in Figure 14(b). A P-MOSFET based solution is expensive and has the risk of failure
when the input power is removed causing the output capacitor discharge through the fully enhanced P-
MOSFET. Another simple solution, shown in Figure 14(c), uses a combination of fuse and TVS diode,
where the fuse blows and protects the load against reverse polarity. But after the fault, the fuse needs to
be replaced. As shown in Figure 14(d), the TI eFuse TPS2660 integrates a reverse input polarity
protection circuit and does not need any external components. The TPS2660 ensures that the device is
not functional during reverse polarity conditions and internal FET blocks the reverse current path.

VIN VOUT VIN VOUT
System System
Load Load System
Load
(a) (b) (c)
Blocking FET Pass FET
System
Load
Reverse Input Polarity
Protection Circuit
GND
(d)
Figure 14. Input Reverse Polarity Protection Using (a) Diode (b) P-MOSFET (c) Fuse + TVS Diode (d)
TPS2600 eFuse
3.9 Surge Protection
The TPS2660 eFuse-based surge protection solution (reference (2)) is shown in Figure 15. It requires only
a single TVS diode to protect the load from surges. The device does not need any passive wave shaping
circuits to reduce the slew rate of the surge. It can handle slew rates as fast as 20 V/µs. Built-in back-to-
back FETs and reverse polarity protection circuits effectively block negative voltage that can be generated
due to a negative surge. The ±70-V transient absolute maximum ratings of the TPS2660 device enable
the use of a single TVS diode for clamping the surge. Overvoltage and undervoltage protection makes
sure that the downstream converters are isolated from input when the surge is at peak or valley level. A
proprietary high-speed protection algorithm immediately disconnects the output from the input and
prevents the surge passing from the input to the output.
TPS2660
Field-Side Single Protected
DC Supply TVS Load
Figure 15. Surge Protection Solution Using TPS2660 eFuse
3.10 Controlled Power Down
When the device is disabled, the output voltage is left floating and power down profile is entirely dictated
by the load. In some applications, this can lead to undesired activity as the load is not powered down to a
defined state. Controlled output discharge can ensure the load is turned OFF completely and not in an
undefined operational state. The BFET pin in the TPS25927x family of eFuses facilitates the quick output
discharge (QOD) function as illustrated in Figure 16. When the device is disabled, the BFET pin pulls low
which enables the external P-MOSFET, Q , for the discharge feature to function. The output voltage
1
discharge rate is dictated by the output capacitor, C , the discharge resistance, R , and the load.
OUT DCHG

VIN VIN OUT VOUT
CIN 28 m(cid:13)
R1
RDCHG
EN/UVLO
BFET
Q1 COUT
ZXM61P03F
dVdT
ILIM
R2
GND TPS25927x RILIM
CdVdT

Figure 16. Circuit Implementation With Quick Output Discharge Function
3.11 UL Certifications
Most of the TI eFuses are UL 2367 (solid-state overcurrent protectors) recognized which would help in
designing sections of the system as “limited energy” or “low power” circuits to expedite the UL certification
process. Additionally, these devices are also UL 60950 (safe during single-point failure) recognized, which
restricts the voltage, current within the circuit limits under any single fault. For additional information
regarding benefits of UL recognition, the reader is directed to reference (3).
3.12 Additional Features
3.12.1 Health Monitoring and Reporting
The TPS2594xx family of eFuses provide advanced features such as precise load current monitor, voltage
monitoring, and fault flag. The current source at the I terminal of the TPS2594xx eFuse is configured to
MON
be proportional to the current flowing through the device. A resistor from this pin to GND converts current
to proportional voltage, which can be used as a means of monitoring the health of the system.
The power good comparator has an internal reference of V( ) = 0.99 V at the negative terminal and
PGTHR
the positive terminal PGTH can be utilized for monitoring of either input or output of the device or any
other voltage rail in the system. The comparator output PGOOD is an open-drain, active-high signal,
which can be used to indicate the status and control the downstream units for power sequencing. PGOOD
is asserted high when the internal FET is fully enhanced and the PGTH pin voltage is higher than internal
reference, V( ), eliminating the need for a separate supply voltage supervisor chip.
PGTHR
The FLT open-drain output is asserted (active low) during undervoltage, overvoltage, reverse voltage,
reverse current, and thermal shutdown conditions.
3.12.2 Diode Mode
The TPS25942x and TPS25944x family of eFuses incorporate the diode mode feature, where the power
path from IN to OUT acts as a non-ideal diode rather than a FET. This feature is useful in power-mux
applications to switch over from master to slave supplies and vice-versa smoothly, when two supplies are
within a diode drop of each other.
3.12.3 Low Power Mode
The TPS25940 eFuse provides a dedicated DevSleep interface terminal (DEVSLP) to drive the device to
low power mode. The DEVSLP terminal is compatible with standard hardware signals asserted from the
host controller. When pulled high, it puts the device in low power DevSleep mode. In this mode, the
quiescent current consumption of the device is limited to less than 95 μA (typical) and the functionality of
several non-critical modes are disabled.

4 Typical Application Example for Comparison
In this section, a comparison between the eFuse solution and a discrete circuit-protection solution is
shown for HDD application. This application requires inrush and reverse current protection while managing
holdup capacitor charge at the output. It is observed that the output voltage and the inrush current rises
exponentially in the discrete solution and sometimes the discrete solution needs design iterations to limit
inrush current in the desired limit.
Table 1. Design Parameters
Design Parameter Value
Input voltage range, VIN 12 V
Undervoltage lockout set point, V(UV) 10.8 V
Load capacitance, C 2 × 1800 µF
OUT
Load at start-up, R 10 Ω
L(SU)
Current limit, I 1.5 A
Table 2. Comparison Table
eFuse Solution:
Discrete Circuit-Protection Solution
TPS259241+ External Blocking FET
STD30PF03LT4
VIN PDS1040L 100 m(cid:13) VOUT
Blocking FET 0.1 (cid:29)F 0.1 (cid:29)F 330 k(cid:13)
VIN VIN OUT VOUT 2 x 1800 (cid:29)F
CVIN 28 m(cid:13) CHOLD-UP
R1 0.1 (cid:29)F BFET 2 x 1800 (cid:29)F 470 k(cid:13)
1 M(cid:13) 47 k(cid:13) 47 k(cid:13)
EN/UVLO
Circuit ENABLE 2N7002
Schematic 10 k(cid:13)
15 R 0 2 k(cid:13) d G V N d D T TPS25924x ILIM RILIM
76.8 k(cid:13)
CdVdT 470 k(cid:13)
22 nF
BAT54 +
470 k(cid:13)

Total no. of
7 15
Components
> 100 mm2
Approximately 20 mm2
space
TPS259241 STD3 P 0 - P F F E 0 T 3LT4 PDS1040L
Schottky Diode
eFuse CSD16411 N-FET
Area Occupied 3.96 mm
by
6.5 mm
Semiconductors
B D A io T d 5 e 4 2 N N - 7 F 0 E 0 T 2 Co L m M p V a 3 r 3 a 1 tor
Steady State
Power Loss at 38 mW 0.488 mW
1-A Load

Table 2. Comparison Table (continued)
eFuse Solution:
Discrete Circuit-Protection Solution
TPS259241+ External Blocking FET
Inrush
Performance
with R =
OPEN
Inrush
Performance
with R = 10
Ω
5 Conclusion
Modern electronic systems need more than one type of protection. Though each of the protection
requirements can be met with discrete components, the solution needs more board space, is less efficient,
more expensive, and inferior in performance than TI’s integrated circuit protection solution “eFuse”. The
eFuse is more accurate, faster, and can ‘repair’ itself without user intervention. Most of the TI eFuses are
recognized as Solid State Overcurrent Protectors under UL2367 standard. Also these are certified under
safety standard UL 60950 and are safe during single point failure.
6 References
1. Power Multiplexing Using Load Switches and eFuses (SLVA811)
2. The TPS2660 Simplifies Surge and Power-Fail Protection Circuits in PLC System (SLVA833)
3. How to save time and money with low power circuits
(https://e2e.ti.com/blogs_/b/industrial_strength/archive/2015/10/23/low-power-circuits)

Revision History
Changes from Original (December 2016) to A Revision ................................................ Page
• Changed title of the Application Report to Basics of eFuses..................................... 1