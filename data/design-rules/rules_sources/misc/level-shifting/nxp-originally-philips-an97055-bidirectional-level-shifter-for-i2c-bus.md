---
source: "NXP (originally Philips) AN97055 -- Bidirectional Level Shifter for I2C-Bus"
url: "https://cdn-shop.adafruit.com/datasheets/an97055.pdf"
format: "PDF 16pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 25398
---

APPLICATION NOTE
Bi-directional level shifter for
I²C-bus and other systems.

Philips Semiconductors
Bi-directional level shifter for I²C-bus and other Application Note
systems. AN97055
Abstract
With a single MOS-FET a bi-directional level shifter circuit can be realised to connect devices with different
supply voltages of e.g. 5 Volt and 3.3 Volt to one I2C-bus system. The level shifter can also isolate a bus
section of powered-down devices from the I2C-bus, allowing the powered part of the I2C-bus to operate in a
normal way.
The level shifter can also be used in other bus systems or point to point connections for level shifting and/or
isolation.
Purchase of Philips I2C components conveys
a license under the I2C patent to use the com-
ponents in the I2C system, provided the system
conforms to the I2C specifications defined by
Philips.
© Philips Electronics N.V. 1997
All rights are reserved. Reproduction in whole or in part is prohibited without the prior written consent of the
copyright owner.
The information presented in this document does not form part of any quotation or contract, is believed to be
accurate and reliable and may be changed without notice. No liability will be accepted by the publisher for any
consequence of its use. Publication thereof does not convey nor imply any license under patent- or other
industrial or intellectual property rights.
2

APPLICATION NOTE
Bi-directional level shifter for
I²C-bus and other systems.

Author:
Herman Schutte
Philips Semiconductors Systems Laboratory Eindhoven,
The Netherlands
Keywords
Level shifter, bi-directional, I²C-bus, gate way, power-off, protection.
Number of pages: 16
Date: 97-08-04
3

Summary
Present technologies for integrated circuit with clearances of 0.5 m m and less, limit the maximum supply voltage
and consequently the logic levels for the digital I/O signals. To interface these lower voltage circuits with
existing 5 Volt devices a level shifter is needed. For bi-directional bus systems as e.g. the I2C-bus, such a level
shifter must be bi-directional, without the need of a direction control signal. With only one appropriate MOS-FET
for each bus line the desired level shifting with automatic direction control can be done. The levels may have a
vast range, depending on the used MOS-FET, e.g. down to 2 Volt at the “Lower voltage” side and up to 10
Volt or more at the “Higher voltage” side of the level shifter.
An additional function of the level shifter is that it can isolate a powered-down section in a bus system, without
obstructing the powered part. Another feature is the protection of the “Lower voltage” section against high
voltage spikes at the “Higher voltage” section, as long as the MOS-FET can withstand this spikes.
4

CONTENTS
1. INTRODUCTION..........................................................................................................................................7
1.1 References............................................................................................................................................7
1.2 World Wide Web...................................................................................................................................7
2. INTERCONNECTION OF DEVICES WITH DIFFERENT LOGIC LEVELS...................................................8
2.1 Logic levels of the I2C-bus.....................................................................................................................8
2.2 I2C-bus devices with different supply voltages and 5V tolerant I/O’s.......................................................9
2.3 Devices with different logic levels connected via the bi-directional level shifter.....................................10
2.3.1 Description of the level shift operation.........................................................................................10
2.3.2 Protection of the “Lower voltage” section against high voltage spikes..........................................11
2.3.3 The level shifter used in point to point connections......................................................................11
2.3.4 Isolation of the powered-down “Lower voltage” section...............................................................11
2.3.5 Extended circuit for isolation of the powered-down “higher voltage” section.................................12
3. CHARACTERISTICS OF THE MOS-FET’S...............................................................................................13
4. WAVE FORMS OF THE LOGIC LEVELS...................................................................................................14
4.1 Shifting from a 3V to a 5V level............................................................................................................14
4.2 Shifting from a 5V to a 3V level............................................................................................................15
4.3 Wave forms when a bus section is powered-down...............................................................................16
5

1. INTRODUCTION
The I2C-bus has been introduced in 1980 by Philips, and has become a de-facto world standard. More than
1000 different IC devices have been provided with an I2C-bus interface, most of them having a 5 Volt supply
voltage and corresponding logic I/O levels. These 5 Volt devices can be interconnected to an I2C-bus system
without any glue logic.
Present technology processes for integrated circuits with clearances of 0.5 m m and less, limit the maximum
supply voltage to 3.3 Volt and in the near future to 2 Volt and less. Also the I/O signals have this limitation, so
there is a problem to interconnect them with existing 5 Volt devices. The same problem will exist in the future to
interconnect e.g. 3.3 Volt devices and 2 Volt devices.
One solution for this problem is the use of 5 Volt tolerant I/O’s. Most present IC technology processes have a
high voltage option to make I/O signals 5V tolerant. This gives the possibility to connect lower voltage devices
to 5 Volt devices or to 5 Volt bus systems. The disadvantage of this 5 Volt option is that it requires more masks
and process steps in the IC manufacturing, which makes the IC devices significantly more expensive.
Another solution is the use of external level shifters. In the different logic families level shifters are available,
most of them for one direction, which cannot be used in a bi-directional bus system. The bi-directional level
shifters in these families require a direction control signal, which is not available in a serial bus system, so these
level shifters are not applicable.
The bi-directional level shifter circuit described in this application note consists of one discrete MOS-FET for
each bus line. In spite of its surprising simplicity, it not only fulfils the requirement of bi-directional level shifting
without a direction control signal, but it also has the next additional features:
- isolating of a powered-down bus section from the rest of the bus system,
- protection of the “Lower voltage” side against high voltage spikes at the ‘Higher voltage” side.
The bi-directional level shifter can be used in standard mode ( 0 to 100 kbit/s) or in fast mode (0 to 400 kbit/s)
I2C-bus systems, without any change. The following description apply for both modes.
1.1 References.
Useful references for I2C-bus related documentation: ordering inf.
• The I2C-bus and how to use it. (including specification) 9398 393 40011
• I2C Peripherals, DATA HANDBOOK IC12 (includes I2C-bus spec.) 9397 750 00306
• Application Notes and Development Tools for 80C51 Microcontrollers 9397 750 00963
(includes I2C-bus application notes, articles and I2C-bus spec.)
1.2 World Wide Web.
Internet access for Philips Semiconductors:
http://www.semiconductors.philips.com
7

2. INTERCONNECTION OF DEVICES WITH DIFFERENT LOGIC LEVELS.
2.1 Logic levels of the I2C-bus.
An overview of the different logic levels, used in I2C-bus systems, is given below.
The I2C-bus specifies two types of logic levels:
a) fixed levels,
b) supply voltage related levels.
a) The fixed levels are intended for non-CMOS devices and/or devices with higher supply voltages than 5 Volt,
e.g. 12 Volt. The I/O levels for fixed level devices are:
LOW level input voltage V min. -0.5V max. 1.5V
IL
HIGH level input voltage V min. 3.0V max. V +0.5V
IH DDmax
LOW level output voltage V min. 0V max. 0.4V
OL1
HIGH level output voltage V open drain output, determined by V via an external pull-up resistor.
OH DD
b) The supply voltage related levels are intended for CMOS devices and/or devices with supply voltages of 5V
or lower. Their I/O levels are:
LOW level input voltage V min. -0.5V max. 0.3V
IL DD
HIGH level input voltage V min. 0.7V max. V +0.5V
IH DD DDmax
LOW level output voltage V min. 0V max. 0.4V
OL1
HIGH level output voltage V open drain output, determined by V via an external pull-up resistor.
OH DD
The logic levels of the bus lines depends on the pull-up resistors to V , leakage current and, if present, series
DD
resistors to the I/O pins of the devices. Their values must be chosen in such a way that during the LOW level a
minimum noise margin of 0.1 V is present and 0.2 V during the HIGH level.
DD DD
8

2.2 I2C-bus devices with different supply voltages and 5V tolerant I/O’s.
From the listed values in 2.1 can be concluded that fixed level devices and 5V supply voltage related devices
can be connected directly to the same bus lines, without additional components. Also 3.3V supply voltage
related devices can be connected directly to these bus lines as long as they have 5V tolerant I/O pins, because
the pull-up resistors have to be connected to the 5V supply voltage (see Figure 1).
VDD= 5V
Rp Rp
SDA
SCL
3.3V device 3.3V device 5V device 5V device
(5V tolerant) (5V tolerant)
Figure 1. I2C-bus system with 3.3V devices (5V tolerant) and 5V devices, all connected to the same bus lines.
This is the most simple solution, but the lower voltage devices must be 5 Volt tolerant, which may make them
more expensive to manufacture. Lower voltage devices with a supply voltage as low as 2 Volt still meet the I2C-
bus specification and can be connected to the bus system of Figure 1.
If devices with a supply voltage lower than 2.7 Volt are connected via series resistors to the bus lines, then
attention must be paid to meet the 0.1 V noise margin during the LOW level, required by the I2C-bus
specification. The required 0.2 V noise margin during the HIGH level does not depend on the supply voltage.
Devices with a supply voltage lower than 2 Volt do not meet the noise margin requirement of 0.1 V because
the LOW level on the bus lines is 0.4V and their input level of 0.3 V is less than 0.6V. This will be solved in
the next update of the I2C-bus specification.
9

2.3 Devices with different logic levels connected via the bi-directional level shifter.
The bi-directional level shifter is used to interconnect two sections of an I2C-bus system, each section with a
different supply voltage and different logic levels. In the bus system of Figure 2 the left section has pull-up
resistors and devices connected to a 3.3 Volt supply voltage, the right section has pull-up resistors and devices
connected to a 5 Volt supply voltage. The devices of each section have I/O’s with supply voltage related logic
input levels and an open drain output configuration.
VDD1= 3.3 V VDD2= 5V
Rp Rp g Rp Rp
T1
s d
SDA 1 SDA 2
g
T2
s d
SCL 1 SCL 2
3.3 V device 3.3 V device 5 V device 5 V device
”Lower voltage” section “Higher voltage” section
Figure 2. Bi-directional level shifter circuit connects two different voltage sections of an I2C-bus system.
The level shifter for each bus line is identical and consists of one discrete N-channel enhancement MOS-FET,
T1 for the serial data line SDA and T2 for the serial clock line SCL. The gates (g) has to be connected to the
lowest supply voltage VDD1 , the sources (s) to the bus lines of the “Lower voltage” section, and the drains (d)
to the bus lines of the “Higher voltage” section. Many MOS-FET’s have the substrate internally already
connected with its source, otherwise it should be done externally. The diode between the drain (d) and
substrate is inside the MOS-FET present as n-p junction of drain and substrate.
2.3.1 Description of the level shift operation.
For the level shift operation three states has to be considered:
• State 1. No device is pulling down the bus line and the bus line of the “Lower voltage” section is pulled up
by its pull-up resistors Rp to 3.3 V. The gate and the source of the MOS-FET are both at 3.3 V, so its V
GS
is below the threshold voltage and the MOS-FET is not conducting. This allows that the bus line at the
“Higher voltage” section is pulled up by its pull-up resistor Rp to 5V. So the bus lines of both sections are
HIGH, but at a different voltage level.
• State 2. A 3.3 V device pulls down the bus line to a LOW level. The source of the MOS-FET becomes
also LOW, while the gate stay at 3.3 V. The V rises above the threshold and the MOS-FET becomes
conducting. Now the bus line of the “Higher voltage” section is also pulled down to a LOW level by the 3.3
V device via the conducting MOS-FET. So the bus lines of both sections become LOW at the same
voltage level.
10

• State 3. A 5 V device pulls down the bus line to a LOW level. Via the drain-substrate diode of the MOS-
FET the “Lower voltage” section is in first instance pulled down until V passes the threshold and the
MOS-FET becomes conducting. Now the bus line of the “Lower voltage” section is further pulled down to
a LOW level by the 5 V device via the conducting MOS-FET. So the bus lines of both sections become
LOW at the same voltage level.
The three states show that the logic levels are transferred in both directions of the bus system, independent of
the driving section. State 2 and state 3 perform the “wired AND” function between the bus lines of both sections
as required by the I2C-bus specification.
Other supply voltages than 3.3V for VDD1 and 5V for VDD2 can be applied, e.g. 2V for VDD1 and 10V for
VDD2 is feasible. In normal operation VDD2 must be equal to or higher than VDD1.
The MOS-FET’s allow that VDD2 is lower than VDD1 during switching power on/off, of course the bus system
is not operational during that time.
The maximum VDD2 is not critical as long as the drain of the MOS-FET can withstand this voltage. At a higher
VDD2 a slower falling edge for both bus sections has to be taken in account, both in state 2 and state 3,
because it takes more discharge time of the bus line.
The lowest possible supply voltage VDD1 depends on the threshold voltage V of the MOS-FET’s. With a
GS(th)
threshold voltage of about 1 Volt below the lowest VDD1, the level shifter circuit will operate properly. If for
example the lowest VDD1 is 3 Volt, a threshold voltage V of maximum 2 Volt is allowed.
2.3.2 Protection of the “Lower voltage” section against high voltage spikes.
If an I2C-bus system has to be connected with e.g. external bus lines on which high voltage spikes can be
expected, the level shifter circuit may be used as protection circuit as long as the drain of the MOS-FET can
withstand these high voltage spikes. The ”Lower voltage” section is the protected side, the “Higher voltage”
section the is the side of the external bus lines (see Figure 2). If in this application no level shifting is required,
VDD1 and VDD2 can be interconnected.
2.3.3 The level shifter used in point to point connections.
The circuit of figure 2 can also be used as a one-directional level shifter between an output signal and one or
more inputs, which have higher or lower logic levels than that output signal.
If the output signal is generated by a push-pull stage, then the Rp at the output circuit side, (“Lower voltage” or
“Higher voltage” section) can be omitted. The Rp at the input circuit(s) side remains needed.
The protection and isolation features, described in 2.3.2 and 2.3.4 also apply here.
2.3.4 Isolation of the powered-down “Lower voltage” section.
An additional feature of the level shifter circuit in figure 2 is the isolation of the “Lower voltage” section when
VDD1 is switched off. In that case VDD1 is about 0 Volt and the MOS-FET’s are switched off because V is
below the threshold voltage. The “Higher voltage” section is not hindered and stays operational. To assure a
noise margin, the MOS-FET’s should have a minimum threshold voltage V of e.g. 0.4V and VDD1 must
stay below this value. The isolation feature can also be applied if no level shifting is required, VDD1 and VDD2
may have the same value, e.g. both 3.3V or both 5V.
11

2.3.5 Extended circuit for isolation of the powered-down “higher voltage” section.
If it is necessary to isolate also the “Higher voltage” section when it is powered off, then the level shifter circuit
can be extended as shown in figure 3.
VDD3
VDD1= 3.3 V VDD2= 5V
Rp Rp
Rp Rp g g Rp Rp
T1 T3
SDA1 s d d s SDA2
g g
T2 T4
SCL1 s d d s SCL2
3.3 V device 3.3 V device 5 V device 5 V device
”Lower voltage” section “Higher voltage” section
Figure 3. I2C-bus system in which the “Higher voltage” section is isolated at power-off.
If VDD2 is switched-off then T3 and T4 becomes not conducting and the “Higher voltage” section is isolated
from the other part of the bus system. The pull-up resistors Rp to VDD3 are not necessary for the proper
operation and may have a high resistance value, they can be added to prevent the MOS-FET drains become
floating at a HIGH level. VDD3 is preferably connected to the highest supply voltage. If VDD3 has a lower
value, then care must be taken that the logic HIGH levels of the bus lines are not decreased too much.
The “Lower voltage” section is isolated if VDD1 is switched off, in the same way as in Figure 2 and described in
2.3.4, but now independent of the value of VDD2.
Because this level shifter circuit is symmetrical, the “Lower voltage” section and “Higher voltage” section can be
chosen arbitrary at the left or right side in figure 3. Even more sections with a higher, a lower or a same supply
voltage value can be added by connecting these sections via additional MOS-FET’s to the common drain
terminals (d) in the same way as the other sections in Figure 3. Every section is isolated from the rest of the
bus system when its supply voltage is switched off, while level shifting between all other sections remain
operational.
12

3. CHARACTERISTICS OF THE MOS-FET’S.
The requirements for the most important characteristics of the MOS-FET’s, used as bi-directional level shifter in
an I2C-bus system with max. 6V and min. 2.7V levels, are listed below. The values are intended as an indication
and may be adapted for other supply voltages, other logic levels and/or other applications.
Type : N-channel enhancement mode MOS-FET.
Gate threshold voltage : V min. 0.1V max. 2V
On resistance : R max. 100 Ohm @ I = 3mA, V = 2.5V
DS(on) D GS
Input capacitance : C max. 100 pF @ V = 1V, V = 0V
iss DS GS
Switching times : t t max. 50 ns.
on off
Allowed drain current : I 10 mA or higher.
D
Values of pull-up resistors and series resistors are not given here, they depend on the worst case values of the
supply voltages and logic levels, length and load of the bus lines, and the requirements for rise and fall times.
These resistors have to be calculated for each bus system separately. A good approach for the calculation is to
keep the RC values for the different sections about the same, it gives the best timing tolerances for set-up and
hold times.
MOS-FET’s in table 1 are suitable to be used as level shifter. See Philips Data Handbook SC07 for their full
specification. BSN10 or BSN20 are low cost devices and have good properties for 3V/5V level shifting, isolation
and protection.
TABLE 1
TYPE V R C Package
GS(th) DS(on) iss
BSN10 min. 0.4V max. 1.8V 25 Ohm (typ) 15 pF TO-92
BSN20 min. 0.4V max. 1.8V 25 Ohm (typ) 15 pF SOT23
BSS83 min. 0.1V max. 2.0V 70 Ohm (typ) 1.5 pF (typ) SOT143
BSS88 min. 0.4V max. 1.2V 15 Ohm 50 pF (typ) TO-92
13

4. WAVE FORMS OF THE LOGIC LEVELS.
Figures 4, 5, 6, 7 and 8 show the wave forms of the logic levels of an implementation according Figure 2. Figure
9 shows the wave forms of the implementation according figure 3. T1, T2, T3 and T4 are MOS-FET’s type
BSN10. The “Lower voltage” section has an Rp of 3k3 W and a bus line capacitance of 50 pF. The “Higher
voltage” section 4K7 W and 30 pF. Only the wave forms of the SCL lines are shown. The driving devices have
slope controlled outputs for the falling edges with a fall time of 50 ns.
4.1 Shifting from a 3V to a 5V level.
SCL2 SCL2
5 V 5 V
3 V SCL1 3 V SCL1
0 V 0 V
Figure 4. Figure 5.
Shifting from a 3V to a 5V level (200 ns/div). Enlarged falling edge of fig. 4 (25 ns/div).
Figure 4 shows the level shifting from a “Lower level” to a “Higher level” section at 200 ns/div. time scale. A 3V
device drives the SCL1 line and this wave form is shifted upwards to a 5 Volt wave form at SCL2. At about 2
Volt on the rising edge, the MOS-FET is switched off and each section rises smoothly with its own curve to its
end value. Figure 5 gives an enlarged view of the falling edges at 25 ns/div. time scale. At about 2 Volt on the
falling edge of SCL1, the MOS-FET becomes conducting and interconnects both bus line sections. It takes
about 25 ns (between 100 and 125 ns of the time scale) to discharge SCL2 to the same voltage level of SCL1,
showing an increase of the fall time of SCL1, but far within the 300 ns requirement of the I2C-bus specification.
Afterwards both lines SCL1 and SCL2 are pulled LOW together smoothly.
Capacitive coupling via the MOS-FET between SCL1 and SCL2 shows some minor effect on the curves:
- a small overshoot of SCL1 during the rising edge of SCL2 (Figure 4),
- the first slow part of the falling edge of SCL2 due to the falling edge of SCL1 (Figure 5).
14

4.2 Shifting from a 5V to a 3V level.
SCL2 SCL2
5V 5V
SCL1 SCL1
3V 3V
0V 0V
Figure 6. Figure 7.
Shifting from 5V to a 3V level (200 ns/div). Enlarged falling edge of fig. 6 (25 ns/div).
Figure 6 shows the level shifting from a “Higher level” to a “Lower level” at 200 ns/div. time scale. A 5V device
drives the SCL2 line and this wave form is shifted downwards to a 3 Volt wave form at SCL1. At about 2 Volt on
the rising edge, the MOS-FET is switched off and each section rises smoothly with its own curve to its end
value. Figure 7 gives an enlarged view of the falling edges at 25 ns/div. time scale. At about 2 Volt on the falling
edge of SCL2, the MOS-FET becomes conducting and interconnects both bus line sections. SCL2 and SCL1
are then about at the same voltage level, and both lines are pulled LOW together smoothly. Capacitive coupling
via the MOS-FET between SCL1 and SCL2 shows some minor effect on the curves:
- a small overshoot of SCL1 during the rising edge of SCL2 (Figure 6),
- the first slow part of the falling edge of SCL1 due to the falling edge of SCL2 (Figure 7).
15

4.3 Wave forms when a bus section is powered-down.
Figure 8 and 9 show the wave forms of the logic levels if a section is powered-down in the bus systems of figure
2 and figure 3 respectively.
SCL2
5V
SCL1
3V
Common drains (n)
SCL1 SCL2
0V 0V
Figure 8. Figure 9.
“Lower voltage” section in fig.2 is powered-down. “Higher voltage” section in fig.3 is powered-down
Figure 8 shows the situation when VDD1 is 0 Volt, so the “Lower voltage” section is powered-down in the bus
system of fig.2. The “Higher voltage” section stays operational and a clock pulse is present on the SCL2 line.
The SCL1 line stays at a LOW level with some positive and negative cross-talk effects via the drain-source
capacitance of the not conducting MOS-FET T2.
Figure 9 shows the situation when VDD2 is 0 Volt and the “High voltage” section is powered-down in the bus
system of fig.3. The “Lower voltage” section stays operational and a clock pulse is present on the SCL1 line.
The SCL2 line stays at a LOW level with some positive and negative capacitive cross-talk effects via the drain-
source capacitance of the not conducting MOS-FET T4. The pull-up resistors to VDD3 are not present, and the
common drains follow the SCL1 HIGH level minus the voltage drop of the internal drain-substrate diode of T2.
During the LOW level T2 is conducting and the common drains (d) have the same level as SCL1.
If pull-up resistors to VDD3 are present, then the HIGH level of the common drains (d) will be pulled up to the
VDD3 level when SCL1 line is HIGH (equal as SCL2 in fig.4). In this case it is also possible to connect “Higher
voltage” devices direct to the common drains (d). These devices have VDD3 as supply voltage, which is not
switched off.
The use of the above level shift circuits gives extensive possibilities to I2C-bus systems to connect, power-down
and protect I2C-bus devices with different supply voltages and logic levels.
-----------------------------
16