---
source: "Wurth DC/DC Handbook Extract -- SMPS from EMC POV"
url: "https://www.we-online.com/components/media/o784081v410%20Extract-DCDC_Converter-1.0.pdf"
format: "PDF 10pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 16468
---

HANDBOOK
SMPS topologies from an
EMC point of view
1st edition
KKOOOOBBDDNNAAHH DC/DC CONVERTER

Table of conTenTs
Table of contents
1. General Information ........................................................9
1.1. Selection of the storage inductors ..............................................10
1.1.1 Rated current .................................................................13
1.1.2 Saturation current .............................................................15
1.2. Core material ..................................................................17
1.3. Selection of suitable capacitors ................................................18
1.3.1 Ripple current .................................................................18
1.3.2 Impedance ....................................................................22
1.3.3 Determining Interference current ...............................................31
1.4. Input filters for DC/ DC converters ..............................................38
1.4.1 Input stability criteria ..........................................................40
1.4.2 REDEXPERT – EMC Filter Designer .............................................42
2. calculation of common topologies ..........................................45
2.1. Buck topology .................................................................45
2.1.1 Block diagram and general thoughts ...........................................45
2.1.2 Layout considerations .........................................................46
2.1.3 Example design ...............................................................48
2.2. Boost topology ................................................................52
2.2.1 Block diagram and general thoughts ...........................................52
2.2.2 Example design ...............................................................54
2.3. SEPIC topology ................................................................58
2.3.1 Block diagram and general thoughts ...........................................58
2.3.2 Example design ...............................................................60
2.4. Flyback topology ..............................................................64
2.4.1 Block diagram and general thoughts ...........................................64
2.4.2 Example design ...............................................................65
3. appendix .................................................................79
3.1. Basic formulas of the topologies ...............................................79
8 DC/DC CONVERTER HANDBOOK – SMPS TOPOLOGIES FROM AN EMC POINT OF VIEW

1. General InformaTIon
1. General Information
Every electronic device needs a power source with DC or AC voltage. While devices connected to
the mains usually require the AC voltage to be rectified first, battery-powered devices already
work directly with DC voltage.
Frequently, the available DC voltage does not match the powered circuit, so a DC/DC converter is
needed to provide the required DC voltage and regulation. These DC/DC converters play a crucial
role in various applications such as battery chargers, renewable energy and portable electronic
devices where different voltage levels are required for proper operation.
DC/DC converters can basically be divided into two cases: A buck converter reduces a higher in-
put voltage to a lower output voltage, while a boost converter produces a higher output voltage
from a lower input voltage. Example calculations can be found in chapters 2.1 and 2.2.
In addition, there are also DC/DC converter topologies that can operate with both higher and
lower input voltages, so-called buck-boost converters. Typical representatives of this group are
SEPIC converters and flyback converters. Example calculations can be found in chapters 2.3 and
2.4. It is important that a DC/DC converter operates as energy-efficiently as possible and at the
same time provides a stable, regulated output voltage, even if the input voltage fluctuates or
load changes occur on the output side. EMC behavior also deserves special attention. Thus, a
DC/DC converter should be neither susceptible to interference nor interfere with other circuits in
the environment.
In order to take these requirements into account, a designer of a DC/DC converter should first
deal with selected basics. A good starting point is to deal intensively with rated and saturation
currents when selecting the appropriate storage inductor (chapter 1.1). The core material used in
the inductors has a major influence on the saturation behavior, the maximum possible switching
frequency, and the component size (chapter 1.2). In the same way, the selection of suitable ca-
pacitors in terms of ripple current, impedance and the determination of the interference current
is of great importance (chapter 1.3). Finally, the input filters for the DC/DC converters and the
input stability criteria deserve attention (Chapter 1.4).
Well prepared with the basic knowledge, one can then turn attention to the design examples of
the following four widely used DC/DC converter topologies:
• Buck Converter
• Boost converter
• SEPIC Converter
• Flyback Converter
DC/DC CONVERTER HANDBOOK – SMPS TOPOLOGIES FROM AN EMC POINT OF VIEW 9

1.1 selection of the storage inductors
Different approaches can be found in the literature for calculating storage inductors.
Recommendations differ widely, especially in determining the percentage of maximum AC ripple
current (ΔI) in relation to the DC rated current. The various sources show values ranging from 0.1
· Ī to 0.9 · Ī. A low current ripple ΔI means that, other things being equal, the inductance value (L)
L L
must be higher, whereas a lower inductance value is sufficient if ΔI is larger. However, it is often
forgotten that the amplitude level of the AC inductor current ΔI has a direct effect on current
flow in the input and output capacitors and thus ultimately affects the voltage ripple, as well as
heating of the capacitors. Therefore, when dimensioning the storage inductor, it is also impor-
tant to consider the circuit as a whole. In practice in most applications, a value of current ripple
between 30% and 60% in relation to the average inductor current Ī has become established.
L
The percentage of ripple current (ripple current ratio) is specified in the formulas of this chapter
with the ripple current factor r (e.g., 0.35 which corresponds to 35%).
Important: To calculate the peak current Î, add half of the ripple current to the average inductor
current. The peak inductor current is decisive for selecting the minimum necessary saturation
current of a storage choke.
Peak inductor current:
r
I = I 1 + (1.1)
L L 2
̂ ̅ ⋅� �
With
Î = peak current
Ī = average inductor current
r = ripple current factor
The storage inductor is often selected based on the datasheets of the switching regulator. In
this context, reference design proposals are all too often preferred over computational methods,
such as the one presented here. A switching regulator can only develop its full potential with an
individually selected storage inductor.
10 DC/DC CONVERTER HANDBOOK – SMPS TOPOLOGIES FROM AN EMC POINT OF VIEW

To understand the calculations, let’s take a closer look at the inductor current:
Fig. 1.1: Inductor current with AC component.
The duty cycle D of the switching event determines the output voltage:
V
out
D = (1.2)
in
With
D = duty cycle
V = output voltage
V = input voltage
In the following, we consider a simple step-down converter with a transistor as well as a free-
wheeling diode, known as an “asynchronous buck converter”.
When the transistor in an asynchronous buck converter is turned off, the diode takes over
the current flow, causing the inductor to be momentarily at a voltage between the supply and
ground. Without inductance, this would be equivalent to a short circuit at the output. This results
in a minimum inductance which, together with the output voltage, defines the maximum current
rise.
From:
di
V =V =L ∙ (1.3)
out L dt
DC/DC CONVERTER HANDBOOK – SMPS TOPOLOGIES FROM AN EMC POINT OF VIEW 11
tnerruC
Time
NE-101-CDH
IL
̂ ∆IL=rI O
⋅⋅ Io=IL
̅
∆I = AC ripple

with di = I and the switch-off time
1 - D
dt = t off = f (1.4)
sw
the result is:
V ∙ (1 - D)
L min = o I ut ∙ f (1.5)
out sw
The relationships can be derived in the same way for the active phase of the transistor. Here,
however, the difference between the output and input voltage is across the storage inductor,
which makes the resulting formula more complicated.
The magnitude of the inductance value does not affect the duty cycle (D) with continuous cur-
rent flow. If a value of at least L is not used in the application, the converter works in dis-
min
continuous conduction mode. In this mode there is a poor ratio between the average inductor
current and the ripple current, which results in relatively high AC losses. Therefore, this operating
mode should be avoided at nominal output current.
example:
For a step-down converter with an input voltage of 12 V to an output voltage of 3.3 V at 1 A
with a 500 kHz switching frequency:
V 33V
D= out= =0275 (1.6)
V 12V
in .
.
V ∙(1-D) 33V (1-0275)
L = out = =48µH (1.7)
min I f 1A 500kHz
ou t sw . ⋅ .
.
⋅ ⋅
Dimensioning with a 4.8 µH inductor would fully utilize the energy storage capacity of the induc-
tor. In order to compensate temperature drift, inductor tolerance and overload, reserves should
be provided for when constructing a circuit in practice. In addition, an inductance value of 4.8
µH with its 100% ripple current factor would highly stress the other components in the circuit
and worsen the EMC behavior. Therefore, the ripple current factor r (0.3 to 0.6) is added to this
formula. Similarly, the voltage drop (V ) of 0.3 V to 0.7 V at the diode should also be taken into
D
consideration. In a synchronous regulator with two transistors this can be omitted, as the volt-
age drop, due to the low R , is far below 0.1 V.
DS,on
12 DC/DC CONVERTER HANDBOOK – SMPS TOPOLOGIES FROM AN EMC POINT OF VIEW

For a ΔI = 40% and with a diode forward voltage of V = 0.4 V, the inductance of the choke is now
calculated as follows:
V + V 3.3 V + 0.4 V
D = out D = = 0.298 (1.8)
+ V
12 V + 0.4 V
V + V 1 - D 3.3 V + 0.4 V ∙ 1 - 0.298
L opt = out r ∙ I D ∙ f = 0.4 1 A ∙ 500 kHz = 13 µH (1.9)
( out)⋅(sw ) ( ) ( )
⋅
An inductor with a standard value of 15 µH could be used in practice for this design example. As
component tolerances and the drop in inductance from the current must be taken into consid-
eration, the choke in this case should not have a minimum tolerance greater than –15% so it
does not go below 13 µH; the influence of temperature has not been taken into consideration
here. For practical purposes, it must be noted that the ripple current cannot be chosen arbitrarily
small. The graph below shows that below ΔI = 20% the inductance value, and thus the inductor
size, increases exponentially. Furthermore, it must be observed that the ripple ΔI for a “Current
Mode Controlled IC” must have a certain amplitude in order to be able to control in an “agile”
manner.
120 %
100 %
80 %
60 %
40 %
20 %
0 %
5 µH 10 µH 15 µH 20 µH 25 µH
Fig. 1.2: Relationship between inductance and resulting ripple current percentage.
1.1.1 Rated current
First, we focused on calculating the necessary inductance value. Now we will look at the rated
current that the inductor must withstand.
The average current through the inductor corresponds to the output current of the step-down
converter. The RMS current is responsible for heating the inductor, which also generates a
DC/DC CONVERTER HANDBOOK – SMPS TOPOLOGIES FROM AN EMC POINT OF VIEW 13
elppiR
Inductance
NE-201-CDH

power loss with the DC resistance (R ) of the winding. The RMS current is composed of the
DC
average inductor current (DC component) and the ripple current ΔI (AC component). Mainly the
maximum DC output current of the converter is of interest for determining the rated current of a
storage inductor. Also taking other losses (core losses/AC copper losses) into consideration and
depending on the ambient temperature in the application, the average inductor current should
always be less than the rated inductor current. This ‘rated current’ is measured as DC and so
only takes the ohmic losses of the wire into consideration. Here it is important to mention that
the heating is a quadratic function of the current (from P = I2 · R ). The rated current is only a
DC DC
numerical value in a table and is not intended in any way to precisely design the components.
This value can often only be used to compare the series from a particular manufacturer, as
competitors differ in their views on the “standard copper thickness” on printed circuit boards. In
practice, you either allow plenty of tolerance for the temperature increase, or you use the online
design platform REDEXPERT and simulate the expected heating. Würth Elektronik bases its
calculations on a real measurement with a defined test setup. The following equation is used for
the temperature extrapolation in REDEXPERT, where two coefficients k and k are determined
1 2
from the heating curve (see Figure 1.3) by curve fitting. The total temperature rise inside the
inductor is then:
P + I2 R k2
T = AC L DC,typ (1.10)
tot k
1⋅
Δ � �
60 K
50 K
40 K
30 K
20 K
10 K
0 K
0.0 A 0.2 A 0.4 A 0.6 A 0.8 A 1.0 A 1.2 A 1.4 A
Fig. 1.3: Self-heating of an inductor taking the example of WE-PD 744777133.
14 DC/DC CONVERTER HANDBOOK – SMPS TOPOLOGIES FROM AN EMC POINT OF VIEW
esiR
erutarepmeT
Current
NE-300-CDH

7 A 350 mΩ
6 A 300 mΩ
5 A 250 mΩ
4 A 200 mΩ
3 A 150 mΩ
2 A 100 mΩ
1 A 50 mΩ
0 A 0 mΩ
0 mm³ 400 mm³ 800 mm³ 1200 mm³ 1600 mm³
Fig. 1.4: Example: Relationship between component volume and DC current heating using different
WE-PD series designs with the same inductance value.
1.1.2 Saturation current
An inductor goes into saturation as the maximum magnetic flux in the core is reached. If this
point is exceeded, the storage inductor then resembles an air coil in its electrical behavior and
the core material has no influence.
This point is indicated by a drop in inductance. Depending on the core material, the transition is
either abrupt or smooth. The terms hard and soft saturation are used. Generally, ferrite cores
with discrete air gaps exhibit hard saturation, witnessed by a sharp drop in inductance whereas
powder cores with distributed air gaps have soft saturation evidenced by a gradual decrease in
inductance.
DC/DC CONVERTER HANDBOOK – SMPS TOPOLOGIES FROM AN EMC POINT OF VIEW 15
tnerruC
ecnatsiseR
CD
Volume
Isat IR RDC
NE-400-CDH
7332
6033 7345 1245 1260 1280 1210

Fig. 1.5: Inductance vs. current of two storage chokes at 40°C. Orange: WE-LHMI series with soft
saturation; Blue: WE-PD series with hard saturation behavior.
Both variants have advantages and disadvantages. If hard saturation lies too close to the DC
operating point, even a slight increase in the regulator output current can cause a sharp drop in
inductance. This leads to a large increase in current, which can damage the semiconductors or
force the regulator to shut down (overcurrent protection).
Soft saturation avoids such faults. The inductance of this type drops somewhat earlier, just not
abruptly. These inductors react less strongly to short-term load peaks of DC/DC application (e.g.,
PoL converters).
When calculating the ripple current ΔI, care must always be taken to ensure that sufficient
distance is maintained from the inductor’s saturation current. This margin is especially important
for inductors that exhibit temperature dependent saturation behavior, and this is the case for
almost all common inductors with classical ferrite core material.
The saturation behavior of WE inductors can be easily verified with REDEXPERT. The ambient
temperature of the application can also be taken into consideration in the simulation and its ef-
fect on the saturation behavior of the selected inductor is displayed.
16 DC/DC CONVERTER HANDBOOK – SMPS TOPOLOGIES FROM AN EMC POINT OF VIEW