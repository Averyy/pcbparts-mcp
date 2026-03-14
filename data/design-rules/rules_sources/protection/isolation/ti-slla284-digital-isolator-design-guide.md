---
source: "TI SLLA284 -- Digital Isolator Design Guide"
url: "https://www.ti.com/document-viewer/lit/html/SLLA284"
format: "HTML"
method: "pdfplumber"
extracted: 2026-02-16
chars: 50900
---

Application Note
Digital Isolator Design Guide
ABSTRACT
This design guide helps system designers of galvanically isolated systems to begin designing with TI's broad
portfolio of digital isolators and isolated functions in the shortest time possible. This portfolio includes the
ISO78xx family of 5.7-kVrms reinforced digital isolators, the ISO67xx and ISO77xx family of 5-kVrms digital
isolators, the ISO73xx family of 3-kVrms digital isolators, and the ISO71xx family of 2.5-kVrms digital isolators,
among others. This document explains the basic operating principle of an isolator, suggests where to place
it within a system design, and recommends guidelines for an electromagnetic compatible (EMC) circuit-board
design. When looking for a reliable and robust upgrade to your optocoupler designs, consider TI's pin-to-pin
opto-emulator products.
Further information is available in the respective product data sheets and the EVM manuals.
Table of Contents
1 Operating Principle.................................................................................................................................................................3
1.1 Edge-Based Communication.............................................................................................................................................3
1.2 On-Off Keying (OOK) Based Communication....................................................................................................................4
2 Typical Applications for Digital Isolators and Isolated Functions.....................................................................................5
3 Digital Isolator Selection Guide.............................................................................................................................................8
3.1 Parameters of Interest........................................................................................................................................................8
3.2 Isolator Families.................................................................................................................................................................9
4 PCB Design Guidelines........................................................................................................................................................10
4.1 PCB Material....................................................................................................................................................................10
4.2 Layer Stack......................................................................................................................................................................10
4.3 Creepage Distance..........................................................................................................................................................10
4.4 Controlled Impedance Transmission Lines......................................................................................................................11
4.5 Reference Planes.............................................................................................................................................................13
4.6 Routing.............................................................................................................................................................................14
4.7 Vias..................................................................................................................................................................................15
4.8 Decoupling Capacitors.....................................................................................................................................................17
5 Summary...............................................................................................................................................................................19
6 References............................................................................................................................................................................19
7 Revision History...................................................................................................................................................................19
List of Figures
Figure 1-1. Conceptual Block Diagram of Edge-Based Architecture...........................................................................................3
Figure 1-2. Conceptual Block Diagram of On-Off Keying (OOK) Architecture.............................................................................4
Figure 1-3. Representative Signal in OOK Architecture..............................................................................................................4
Figure 2-1. Example Isolator in a 16-Pin Package......................................................................................................................5
Figure 2-2. Isolated SPI Interface................................................................................................................................................6
Figure 2-3. Isolated RS-232 Interface..........................................................................................................................................6
Figure 2-4. Isolated RS-485 Interface..........................................................................................................................................7
Figure 2-5. Integrated Isolated RS-485 Interface........................................................................................................................7
Figure 4-1. Recommended Layer Stack....................................................................................................................................10
Figure 4-2. Groove Cutting Extends Effective Creepage Distance............................................................................................11
Figure 4-3. Source Impedance Matching: Z ~ r .....................................................................................................................11
0 O
Figure 4-4. Isolator Output Characteristic..................................................................................................................................11
Figure 4-5. Characteristic Impedance as a Function of the w/h Ratio.......................................................................................12
Figure 4-6. Reducing Field Fringing Through Close Electric Coupling Between Conductors...................................................13
Figure 4-7. Ground Plane Acting as a Single Return Trace.......................................................................................................14

Figure 4-8. Return Current Paths in Solid Versus Slotted Ground Planes................................................................................14
Figure 4-9. Separate Traces to Minimize Crosstalk...................................................................................................................14
Figure 4-10. Use 45° Bends Instead of 90° Bends....................................................................................................................14
Figure 4-11. Avoiding Via Clearance Sections...........................................................................................................................15
Figure 4-12. Connect Bypass Capacitor Directly to V Terminal.............................................................................................15
CC
Figure 4-13. Return Current Paths for a Single and a Multiple Layer Change..........................................................................16
Figure 4-14. Return Current Paths for a Single and a Multiple Layer Change..........................................................................17
Figure 4-15. Capacitor Losses Modeled by a Series Resonance Circuit..................................................................................17
Figure 4-16. Capacitor Impedance Versus Frequency..............................................................................................................18
List of Tables
Table 3-1. Digital Isolator Families and Isolated Functions..........................................................................................................9
Table 4-1. Microstrip Equations for 0.2 < w/d < 1(1) ..................................................................................................................13

2 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023

1 Operating Principle
Isolation is a means of preventing dc and unwanted ac currents between two parts of a system, while
allowing signal and power transfer between those two parts. Electronic devices and semiconductor ICs used for
isolation are called isolators. In general, an isolator can be abstracted as comprising of a high-voltage isolation
component or barrier, a transmitter (TX) to couple signal into one side of the isolation component, and a receiver
(RX) to convert the signal available on the other side of the isolation component into digital levels.
TI's isolators use SiO (silicon dioxide) based, high-voltage capacitors to serve as the isolation component. For
2
the TX and RX circuits, two different architectures are used: Edge based and On-Off Keying (OOK) based.
These architectures are explained in Section 1.1 and Section 1.2.
1.1 Edge-Based Communication
The conceptual block diagram of edge-based communication is shown in Figure 1-1. The isolators of ISO73xx,
ISO74xx, ISO71xx, ISO76xx, ISO75xx, and ISO72xx families use this architecture in some form.
The device consists of at least two data channels, a high-frequency channel (HF) with a bandwidth from 100kbps
up to 150Mbps, and a low-frequency channel (LF) covering the range from 100kbps down to dc.
In principle, a single-ended input signal entering the HF-channel is split into a differential signal via the inverter
gate at the input. The following capacitor-resistor networks differentiate the signal into small and narrow
transients, which then are converted into rail-to-rail differential pulses by two comparators. The comparator
outputs drive a NOR-gate flip-flop whose output feeds an output multiplexer. A decision logic (DCL) at the
driving output of the flip-flop measures the durations between signal transients. If the duration between two
consecutive transients exceeds a certain time limit (as in the case of a low-frequency signal) the DCL forces the
output-multiplexer to switch from the high-frequency to the low-frequency channel.
Because low-frequency input signals require the internal capacitors to assume prohibitively large values, these
signals are pulse-width modulated (PWM) with the carrier frequency of an internal oscillator, thus creating a
sufficiently high frequency, capable of passing the capacitive barrier. As the input is modulated, a low-pass filter
(LPF) is needed to remove the high-frequency carrier from the actual data before passing it on to the output
multiplexer.
Isolation Barrier
OSC
LPF
Low-Frequency
Channel PWM VREF
(DC...100 kbps)
0
OUT
1 S
IN
TXP RXP
DCL
High-Frequency
Channel VREF
(100 kbps...150 Mbps)
TXN RXN
Figure 1-1. Conceptual Block Diagram of Edge-Based Architecture

1.2 On-Off Keying (OOK) Based Communication
The conceptual operation of OOK-based communication is shown in Figure 1-2. The corresponding signaling is
shown in Figure 1-3. The isolators in the ISO67xx, ISO78xx and ISO77xx family use this architecture.
In this architecture, the incoming digital bit stream is modulated with an internal spread spectrum oscillator
clock to generate OOK signaling, such that one of the input states is represented by transmission of a carrier
frequency, and the other state by no transmission. This modulated signal is coupled to the isolation barrier and
appears in an attenuated form on the receive side. The receive path consists of a pre-amplifier to gain up the
incoming signal followed by an envelope detector that serves as a demodulator to regenerate the original digital
pattern. The TX and RX signal conditioning circuits are used to improve the common mode rejection of the
channel resulting in better Common Mode Transient Immunity (CMTI).
OOK
Modulation
TX IN SiO2 Based
TX Signal Capacitive RX Signal Pre-amp Envelope RX OUT
Conditioning Isolation Conditioning Detection
Barrier
Spread
Oscillator
Spectrum
Figure 1-2. Conceptual Block Diagram of On-Off Keying (OOK) Architecture
TX IN
Signal through
isolation barrier
RX OUT
Figure 1-3. Representative Signal in OOK Architecture
4 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023

2 Typical Applications for Digital Isolators and Isolated Functions
noitalosI

V 1 16 V
CC1 CC2
GND1 2 15 GND2
INA 3 14 OUTA
INB 4 13 OUTB
OUTC 5 12 INC
OUTD 6 11 IND
EN1 7 10 EN2
GND1 8 9 GND2
Not to scale
Figure 2-1. Example Isolator in a 16-Pin Package
A pin diagram of a typical digital isolator is shown in Figure 2-1. It consists of two supplies: V and V , two
grounds: GND1 and GND2, and input and output pins on either side referred to the respective grounds. That is,
in Figure 2-1, pins 1 through 8 are referred to GND1 and pins 9 through 16 are referred to GND2.
Digital isolators use single-ended, CMOS or TTL logic, switching technology. The voltage range normally ranges
3 V to 5.5 V for both supplies, V and V , though some devices may support a larger supply voltage range.
For example, ISO78xx devices can work with supplies down to 2.25 V. When designing with digital isolators, it is
important to keep in mind that due to the single-ended design structure, digital isolators do not conform to any
specific interface standard and are only intended for isolating single-ended digital signal lines.
Isolated functions are devices where additional functionality, such as a transceiver or a gate-driver is integrated
along with an isolator. An example is the integrated isolated-RS485 described later on in this section. Unlike
digital isolators, an isolated function may need to conform to certain standards. For example, an isolated-I2C
buffer will be compatible to the I2C standard. Also, an isolated function may run off higher supplies, for example,
an isolated gate-driver may use ±15 V to be able to drive an IGBT gate.
Isolation is required in modern electrical systems for a variety of reasons. Some examples are to protect
human operators from high voltage transients and preventing damage to expensive processors, ASICs or
FPGAs in high-voltage systems, breaking the ground loop in communication networks and communication to
high-side devices in motor drive or power converter systems. Examples of applications that need isolation
include industrial automation systems, motor drives, medical equipment, solar inverters, power supplies, and
hybrid electric vehicles (HEV).
Some example applications of digital isolators and isolated functions are presented in this section. Read more
on the performance of digital isolators in relation to common mode transient immunity and high working voltages
in Pushing the envelope with high-performance, digital-isolation technology white paper. For more examples,
detailed application diagrams and use cases, please refer the respective product datasheets.
Figure 2-2 presents the most simple isolator application. Here the entire circuit constitutes a single-ended,
low-voltage system in which a digital isolator connects the SPI interface of a controller with the SPI interface
of a data converter. The most commonly applied isolators in SPI interfaces are ISO7x31 and ISO7x41, hence
often designated as 3- and 4-channel SPI isolators. For an implementation of isolated SPI read, How to Replace
Optocouplers with Digital Isolators in Standard Interface Circuits, and Simplify current and voltage monitoring
with isolated SPI and I2C in your battery management systems (BMS).

3V 3V 3V 3V
ISO ISO
CS CS
SCK o n SCK
Microcontroller ati ADC
PICO ol PICO
s
I
POCI POCI
Figure 2-2. Isolated SPI Interface
The full-blown, isolated RS-232 interface in Figure 2-3 requires two quad isolators due to the six control
signals required in addition to the actual data lines, RX and TX. Although the entire system is single-ended,
the high-voltage requirements of the symmetric, 13-V bus supply make it necessary to galvanically isolate the
data link between the UART and the low-voltage side of the bus transceiver. Also, the 13-V dc bus may be in
turn generated from a higher supply, in which case the isolation also serves as a means of protection against
high-voltage transients on the system supply lines.
+12V
3V 3V 5V 5V
RX
RX
TX
D0–D7 D0–D7 TX o n
ati
/RTS
/RTS ol
MEMRorI/OR /DTR
/IOR /DTR 5
MEMWorI/OW 9
S /IOW
C P U - B U R I E N S T E R T INT UART 3V 5V ISO D R r R i e v S c e e - r 2 s iv 3 e a 2 r n s d D B S- 9 C o n n e ct or
RESET /DSR
/DSR 6
A0 1
A0 /CD
/CD n
A1
A1
ati o
/CTS
/CTS ol
A2 A2 I s /RI
/RI
-12V
Figure 2-3. Isolated RS-232 Interface
6 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023

As in the example in Figure 2-3, the isolation of the RS-485 interface in Figure 2-4 occurs between the controller
and the bus transceiver. Despite the entire interface circuit being a low-volt system, the differential nature
of the transmission bus requires prior isolation on the single-ended side. In a multi-node distributed RS-485
network, different nodes may be referenced to grounds at different potential, in which case isolation enables
communication by level shifting between those ground potentials.
3V 3V 3V 3V
DOUT D
n
Co
H
nt
o
r
t
ller
DIR
ol
ati o D
R
E
DIN I R
Figure 2-4. Isolated RS-485 Interface
Due to the simplicity of the interface shown in Figure 2-5, it is possible to integrate the isolator function into the
transceiver circuit, thus providing an application-specific isolator device featuring low-cost and low component
count. Figure 2-5 is an example of an isolated function. For diagrams of how to implement these RS-485
solutions, read How to isolate signal and power for an RS-485 system.
3V 3V 3V
ISO
DOUT D
n
Co
H
nt
t
ller
DIR D
R
E ol
ati o
DIN R I
Figure 2-5. Integrated Isolated RS-485 Interface
Not all applications of digital isolators and isolated functions are covered here. These are just examples to
understand how the isolator is placed in a system. For more examples, detailed application diagrams, and use
cases, please refer the respective product data sheets.

3 Digital Isolator Selection Guide
This section first describes key parameters to look for while choosing a digital isolator or isolated function, and
then gives a brief introduction to families of isolators and isolated functions currently available from TI. Please
refer the following links for a comprehensive isolator selection guide.
For a step by step flow chart guiding you to the best digital isolator family, please visit: https://e2e.ti.com/
blogs_/b/analogwire/posts/how-to-select-a-digital-isolator
For an overview of all isolation products, with links to different parameterized product selection guides, please
visit:
http://www.ti.com/isolation/overview.html
For a parameterized selection guide for digital isolators please visit:
https://www.ti.com/isolation/digital-isolators/products.html
For a parameterized selection guide for isolated RS485 transceivers please visit:
https://www.ti.com/isolation/isolated-interfaces/rs-485-transceivers/products.html
3.1 Parameters of Interest
This section briefly describes some of the parameters that are present in a typical isolator datasheet and their
relevance to system design.
Isolation Performance:
1. Maximum transient isolation voltage (V ) and isolation withstand voltage (V ) indicate an isolator’s
IOTM ISO
ability to withstand temporary (less than 60 seconds) high voltage.
2. Maximum repetitive peak voltage (V ) and working voltage (V ) indicate the continuous voltage that
IORM IOWM
the isolator can withstand throughout its lifetime.
3. Maximum surge isolation voltage (V ) indicates the maximum impulse voltage (waveform with 1.2-µs rise
IOSM
and 50-µs decay time) that the isolator can withstand.
Timing Parameters:
1. Data rate.
2. Propagation delay is important in systems where the round trip delay adds to the timing budget (for example,
SPI interface) or if the delay is part of a control loop.
3. Propagation delay skew is important if timing budget relies on matching between channels; for example, if
clock is transmitted on one channel and data on another channel in the same direction.
4. Glitch filter: Some digital isolators come with an integrated glitch filter that helps them operate well, even in
noisy environments. However, the glitch filter increases propagation delay and reduces data rate.
Common Mode Transient Immunity (CMTI):
CMTI indicates the isolator’s ability to tolerate fast changes in the potential difference between its grounds, or in
other words, fast changes in common mode, without causing bit errors. High CMTI indicates a robust isolation
channel.
Power Consumption:
Power consumption per channel at data rate of interest.
Package:
1. Creepage and Clearance: Distance along the surface of the package and through the air between pins on
one side of the isolator to the pins on the other side. System level standards mandate minimum values of
these parameters based on the working voltage, the peak transient voltage, and the surge voltage.
2. Comparative Tracking Index (CTI) indicates the ability of the package mold compound to handle steady high
voltage without surface degradation. A higher CTI allows the use of smaller packages for the same working
voltage.
8 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023

3.2 Isolator Families
Table 3-1 briefly describes the key features of a few digital isolator families and isolated functions from TI. For a
more exhaustive listing of devices please visit:
http://www.ti.com/lsds/ti/analog/isolators/overview.page
Table 3-1. Digital Isolator Families and Isolated Functions
Power per
Isolation
Isolator Type Device Timing Performance CMTI Package Channel
Performance
(5 typ, 1Mbps)
Data rate = 50Mbps
V = 7071 Vpk 150 CTI > 600
IOTM Prop delay = 11 ns typ
Digital Isolator ISO67xx V IORM = 2121 Vpk Skew = 6ns max kV/µs typ 16-SOIC, CTI > 1.8 mA
Surge = 10 kV 100 kV/µs min 400 8-SOIC
Glitch filter not required
Data rate = 100Mbps
V = 8000 Vpk
IOTM Prop delay = 11 ns typ CTI > 600
Digital Isolator ISO78xx V = 2121 Vpk 100 kV/µs min 1.7 mA
IORM Skew = 2.5 ns max 16-SOIC
Surge = 12.8 kV
Data rate = 100Mbps CTI > 600
V = 8000 Vpk
IOTM Prop delay = 10.7 ns typ 100 kV/µs typ 16-SOIC, 8-
Digital Isolator ISO77xx V = 2121 Vpk 1.4 mA
IORM Skew = 4.1 ns max 85 kV/µs min SOIC,
Surge = 12.8 kV
Glitch filter not required 16-SSOP
Data rate = 4Mbps
V = 4000 Vpk CTI > 600
IOTM Prop delay = 140 ns typ 100 kV/µs typ
Digital Isolator ISO70xx V = 566 Vpk 8-SOIC, 0.116 mA
IORM Skew = 10ns max 50 kV/µs min
Surge = 6.4 kV 16-SSOP
Data rate = 25Mbps
V = 4242 Vpk 400 < CTI < 600
IOTM Prop delay = 35 ns typ 50 kV/µs typ 1.1 mA (5 V)
Digital Isolator ISO73xx V = 1414 Vpk 8-SOIC,
IORM Skew = 3 ns max 25 kV/µs min 0.85 mA (3.3 V)
Surge = 6 kV 16-SOIC
Integrated glitch filter
Data rate = 50Mbps
V = 4242 Vpk
IOTM Prop delay = 21 ns typ 50 kV/µs typ 400 < CTI < 600 1.65 mA (5 V)
Digital Isolator ISO71xx V = 566 Vpk
IORM Skew = 2 ns max 25 kV/µs min 16-QSOP 1.3 mA (3.3 V)
Surge = 4 kV
Integrated glitch filter
V = 7071, 4242
IOTM
Vpk CTI > 600
ISO1042 100 kV/µs typ State
Isolated CAN V = 1500, 637 Loop delay = 150 ns typ 16-SOIC, 8-
ISO1044 IORM 85 kV/µs min dependent
Vpk SOIC
Surge = 8, 10 kV
IOTM
ISO14xx Prop delay = 19 to 310 100 kV/µs typ State
Isolated RS-485 V = 1500, 566 16-SOIC, 8-
ISO1500 IORM ns 85 kV/µs min dependent
Vpk SOIC
Surge = 10 kV
IOTM Clock freq max = 1.7
Mbps, GPIO data rate = 100 kV/µs typ State
Isolated I2C ISO16xx V = 2121, 637 16-SOIC, CTI >
IORM 50 Mbps 50 kV/µs min dependent
Vpk 400 8-SOIC
Loop delay = 84 ns typ
Surge = 10, 6.5 kV
V = 3600 Vpk CTI > 600
IOTM 70 kV/µs typ Current limit
Isolated Digital Input ISO121x V = 566 Vpk Prop delay = 110 ns 8-SOIC,
IORM 25 kV/µs min dependent
Surge = 5.2 kV 16-SSOP
V = 7071 Vpk
Digital Isolator with IOTM 100 kV/µs typ CTI > 600
ISOW77xx V = 1500 Vpk Prop delay = 11 ns 5 mA
Power IORM 85 kV/µs min 16-SOIC
Surge = 10kV
V = 7071 Vpk
Digital Isolator with IOTM 100 kV/µs typ CTI > 600 State
ISOW1044 V = 1500 Vpk Loop delay = 150 ns typ
Power and CAN IORM 85 kV/µs min 20-DFM dependent
Surge = 10kV
Digital Isolator with V = 7071 Vpk
IOTM Prop delay = 49 to 450 100 kV/µs typ CTI > 600 State
Power and ISOW14xx V = 1500 Vpk
IORM ns 85 kV/µs min 20-DFM dependent
RS-485 Surge = 10kV

4 PCB Design Guidelines
4.1 PCB Material
For digital circuit boards operating below 150 Mbps, (or rise and fall times higher than 1 ns), and trace lengths of
up to 10 inches, use standard FR-4 epoxy-glass as printed-circuit board (PCB) material. FR-4 (Flame Retardant
4) meets the requirements of Underwriters Laboratories UL94-V0 and is preferred over cheaper alternatives due
to its lower dielectric losses at high frequencies, less moisture absorption, greater strength and stiffness, and its
self-extinguishing, flammability characteristics.
4.2 Layer Stack
A minimum of four layers is required to accomplish a low EMI PCB design (see Figure 4-1). Layer stacking must
be in the following order (top-to-bottom): high-speed signal layer, ground plane, power plane, and low-frequency
signal layer.
High-speed traces
10 mils
Ground plane
Keep this space
FR-4
40 mils t f r r a e c e e f s ro , m pa p d l s a , n a e n s d , 0 r ~ 4.5
vias
Power plane
10 mils
Low-speed traces
Figure 4-1. Recommended Layer Stack
• Routing the high-speed traces on the top layer avoids the use of vias (and the introduction of their
inductances) and allows for clean interconnects between the isolator and the transmitter and receiver circuits
of the data link.
• Placing a solid ground plane next to the high-speed signal layer establishes controlled impedance for
transmission line interconnects and provides an excellent low-inductance path for the return current flow.
• Placing the power plane next to the ground plane creates additional high-frequency bypass capacitance of
approximately 100 pF/in2.
• Routing the slower speed control signals on the bottom layer allows for greater flexibility as these signal links
usually have margin to tolerate discontinuities such as vias.
If an additional supply voltage plane or signal layer is needed, add a second power/ground plane system
to the stack to keep it symmetrical. This makes the stack mechanically stable and prevents it from warping.
Also, the power and ground plane of each power system can be placed closer together, thus increasing the
high-frequency bypass capacitance significantly.
4.3 Creepage Distance
Creepage distance is the shortest path between two conductive parts measured along the surface of the
insulation. An adequate creepage distance protects against tracking, a process that produces a partially
conducting path of localized deterioration on the surface of an insulating material as a result of the electric
discharges on or close to an insulation surface.
The degree of tracking occurring depends on the comparative tracking index (CTI) of the material and the
degree of pollution in the environment. Used for electrical insulating materials, the CTI provides a numerical
value of the voltage that will cause failure by tracking during standard testing. IEC 112 provides a fuller
explanation of tracking and CTI.
Tracking damaging the insulating material normally occurs because of one or more of the following reasons:
humidity in the atmosphere, presence of contamination, corrosive chemicals, and altitude at which equipment is
to be operated.
10 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023

As isolation voltage levels continue to rise, it is more important than ever to have a robust PCB design that not
only reduces electromagnetic interference emissions, but also reduces creepage problems. In addition to wide
isolator packaging, techniques such as grooves can be used to attain a desired creepage distance (see Figure
4-2).
Dirt Particles
Groove
Figure 4-2. Groove Cutting Extends Effective Creepage Distance
For a groove (>1 mm wide), the only depth requirement is that the existing creepage distance plus the width of
the groove and twice the depth of the groove must equal or exceed the required creepage distance. The groove
must not weaken the substrate to a point that it fails to meet mechanical test requirements.
Also, on all layers keep the space under the isolator free from traces, vias, and pads to maintain maximum
creepage distance (see Figure 4-1).
4.4 Controlled Impedance Transmission Lines
A controlled impedance transmission line is a trace whose characteristic impedance, Z , is tightly controlled by
the trace geometries. In general, these traces match the differential impedance of the transmission medium,
such as cables and line terminators, to minimize signal reflections. Around digital isolators, controlled impedance
traces must match the isolator output impedance, Z ~ r , which is known as source-impedance matching.
Isolator
Output
Trace
O
Receiver
Z ~r
Figure 4-3. Source Impedance Matching: Z ~ r
To determine Z , the dynamic output impedance of the isolator, r = ΔV /ΔI , needs to be established. For
0 O OUT OUT
that purpose the output characteristic in Figure 4-4, (taken from the ISO7240 data sheet), is approximated by
two linear segments indicating an r ~ 260 Ω at low voltages, while for the majority of the curve, (and thus the
transition region of the output), r ~ 70 Ω.
50
40
Z ~ 260W
30
A)
m
(
T
U
O20
Z ~ 70W
10
0 1 2 3 4 5 6
V (V)
OUT
Figure 4-4. Isolator Output Characteristic

The required trace geometries, such as trace thickness (t) and width (w), the distance between trace and an
adjacent ground layer (d), and the PCB dielectric (ε), are partially dictated by the copper-plating capabilities of
the board manufacturing process and the dielectric of the chosen board material. Typical values are 1 and 2 oz
of copper-plating, resulting in trace thicknesses of t = 1.37 mils and t = 2.74 mils, respectively. Dielectric values
for FR-4 epoxy-glass vary between ε = 2.8 to 4.5 for microstrip, and ε = 4.5 for stripline traces.
r r
With t and ε given, the designer has the freedom to define Z through trace width w, and distance d. For PCB
r 0
designs, however, the most critical dimensions are not the absolute values of w and d, but their ratio w/d. Easing
the designer’s task, Figure 4-5 plots the characteristic trace impedance as a function of the width-to-height (w/h)
for a trace thickness of 2.74 mils (2-oz copper plating), an FR-4 dielectric of 4.5, and a trace-height of 10 mils
above the ground plane.
100
h=10mils
t=2.74mils
50
er=4.5
w
W
-
0 t
Z
20
e r h
10
0.1 0.2 0.5 1 2 5 10
w/h - ratio
Figure 4-5. Characteristic Impedance as a Function of the w/h Ratio
From Figure 4-5 it is apparent that a 70-Ω design requires a w/h ratio of about 0.8. As described in the following
section, Reference Planes, designing a low EMI board requires close electric coupling between signal trace and
ground plane, which is accomplished by ensuring that h = 10 mils. The corresponding trace-width is therefore
8 mils. This width must be maintained across the entire trace length. Otherwise, variations in trace width cause
discontinuities in the characteristic impedance, thus leading to increased reflections and EMI.
Note, that the preceding design example is only one of many possibilities to achieve the desired Z . Different
trace thickness due to higher or lower copper plating, or different PCB material can be used, but require the w/d
ratio to change. The rather complex, mathematic equations for calculating the characteristic impedance Z , while
taking trace thickness, width, and dielectric into account, are presented in Table 4-1.
12 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023

Table 4-1. Microstrip Equations for 0.2 < w/d < 1(1)
ε = effective dielectric, taking into account:
eff
é ù
• dielectric of air
e eff = e r 2 +1 + e r 2 - 1 × ê ê ê 1 1 2 ´ h +0.04 ´ è ç æ 1- w hø ÷ ö 2 - 2.3 ´ t w ´ hú ú ú • dielectric of PCB material
ê 1+ ú • height above ground
ë w û
• nominal trace width
w = effective trace width, taking into account:
eff
1.25×t é æ2 ´ höù • nominal trace width
w eff =w+ p × ê ë 1+ln ç è t ÷ ø ú û • trace thickness
• height above ground
Z = characteristic impedance, taking into account:
60 ´ ln æ ç 8 ´ h + w eff ö ÷ • effective trace width
Z = è w eff 4 ´ hø • height above ground
e
eff • effective dielectric
(1) Keep all dimensions in inch, or mils (1 in = 1000 mils), or mm (1 in = 25.4 mm).
4.5 Reference Planes
The power and ground planes of a high-speed PCB design usually must satisfy a variety of requirements.
At dc and low frequencies, they must deliver stable reference voltages, such as V and ground, to the supply
terminals of integrated circuits (IC).
At high frequencies reference planes, and in particular ground planes, serve numerous purposes. For the design
of controlled impedance transmission systems, the ground plane must provide strong electric coupling with the
signal traces of an adjacent signal layer.
Consider a single, ac-carrying conductor with its associated electric and magnetic fields, shown in Figure 4-6.
Loose or no electric coupling allows the transversal electromagnetic (TEM) wave, created by the current flow, to
freely radiate into the outside environment, causing severe electromagnetic interference (EMI).
Coupled
E fields E
Fringing
fields
t Fringing t
H fields
Fringing
fields
Figure 4-6. Reducing Field Fringing Through Close Electric Coupling Between Conductors
Now imagine a second conductor in close proximity, carrying a current of equal amplitude but opposite polarity.
In this case, the conductors’ opposing magnetic fields cancel, while their electric fields tightly couple. The TEM
waves of the two conductors, now being robbed of their magnetic fields, cannot radiate into the environment.
Only the far smaller fringing fields might be able to couple outside, thus yielding significantly lower EMI.
Figure 4-7 shows the same effect occurring between a ground plane and a closely coupled signal trace.
High-frequency currents follow the path of least inductance, not the path of least impedance. Because the return
path of least inductance lies directly under a signal trace, returning signal currents tend to follow this path. The
confined flow of return current creates a region of high current density in the ground plane, right below the signal
trace. This ground plane region then acts as a single return trace, allowing the magnetic fields to cancel while
providing tight electric coupling to the signal trace above.

fringing fields
Current coupled fields
density
Figure 4-7. Ground Plane Acting as a Single Return Trace
To provide a continuous, low-impedance path for return currents, reference planes (power and ground planes)
must be of solid copper sheets and free from voids and crevices. For reference planes, it is important that the
clearance sections of vias do not interfere with the path of the return current. In the case of an obstacle, the
return current finds its way around it. However, by doing so, the current’s electromagnetic fields will most likely
interfere with the fields of other signal traces introducing crosstalk. Moreover, this obstacle adversely affects the
impedance of the traces passing over it, thus leading to discontinuities and increased EMI.
Load
Circuit trace
D g ri a vi t n e g High-speed Return path
return current around
obstacle
disruption
Figure 4-8. Return Current Paths in Solid Versus Slotted Ground Planes
4.6 Routing
Guidelines for routing PCB traces and placing components are necessary when trying to maintain signal
integrity, avoiding noise pick-up, and lower EMI. Although an endless number of precautions seems to be taken,
this section provides only a few main recommendations as layout guidance.
1. Keep signal traces 3 times the trace-to-ground height, (d = 3h), apart to reduce crosstalk down to 10%.
Because the return current density under a signal trace diminishes via a 1/ [1+(d/h)2] function, its density at a
point d > 3h, is sufficiently small to avoid causing significant crosstalk in an adjacent trace.
d
1
1+ (d/h)2 h
Figure 4-9. Separate Traces to Minimize Crosstalk
2. Use 45° bends (chamfered corners), instead of right-angle (90°) bends. Right-angle bends increase the
effective trace width, and thus the trace impedance. This creates additional impedance mismatch, which
may lead to higher reflections.
Figure 4-10. Use 45° Bends Instead of 90° Bends
3. For permanent operation in noisy environments, connect the Enable inputs of an isolator through a via to
the appropriate reference plane, that is, High-Enable inputs to the V plane and Low-Enable inputs to the
ground plane.
14 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023

4. When routing traces next to a via or between an array of vias, ensure that the via clearance section does
not interrupt the path of the return current on the ground plane below. If a via clearance section lies in the
return path, the return current finds a path of least inductance around it. By doing so, it may cross below
other signal traces, thus generating cross-talk and increase EMI.
Figure 4-11. Avoiding Via Clearance Sections
5. Avoid changing layers with signal traces as this causes the inductance of the signal path to increase.
6. If, however, signal trace routing over different layers is unavoidable, accompany each signal trace via with
a return-trace via. In this case, use the smallest via size possible to keep the increase in inductance at a
minimum.
7. Use solid power and ground planes for impedance control and minimum power noise.
8. Use short trace lengths between isolator and surrounding circuits to avoid noise pick-up. Digital isolators
are usually accompanied by isolated dc-to-dc converters, providing supply power across the isolation barrier.
Because single-ended transmission signaling is sensitive to noise pick-up, the switching frequencies of
close-by dc-to-dc converters can be easily picked up by long signal traces.
9. Place bulk capacitors, (i.e., 10 μF), close to power sources, such as voltage regulators or where the power is
supplied to the PCB.
10. Place smaller 0.1-μF or 0.01-μF bypass capacitors at the device by connecting the power-side of the
capacitor directly to the supply terminal of the device and through two vias to the V plane, and the
cc
ground-side of the capacitor through two vias to the ground plane.
V
V plane
Figure 4-12. Connect Bypass Capacitor Directly to V Terminal
4.7 Vias
The term via commonly refers to a plated hole in a printed-circuit board. Although some applications require
through-hole vias to be wide enough to accommodate the leads of through-hole components, high-speed board
designs mainly use them as trace routing vias when changing signal layers, or as connecting vias to connect
SMT components to the required reference plane, and also to connect reference planes of the same potential to
each other.
Layers connecting to a via do so by making direct contact with a pad surrounding the via, (the via pad). Layers
that must not connect are separated by a clearance ring. Every via has a capacitance to ground which can be
approximated using the following equation:
1.41 ×e ×T ×D
C = r 1
D - D
2 1 (1)
where
• D = diameter of clearance hole in ground planes, [in.].
2
• D = diameter of pad surround via, [in.].
1
• T = thickness of printed circuit board, [in.].
• ε = dielectric constant of the circuit board.
• C = parasitic via capacitance, [pF].

Because the capacitance increases proportional with size, trace vias in high-speed designs must be as small as
possible to avoid signal degradation caused by heavy capacitive loading.
When connecting decoupling capacitors to a ground plane or interconnecting ground planes, the via inductance
becomes more important than its capacitance. The magnitude of this inductance is approximately:
é æ4 ´ hö ù
L =5.08 ´ h ´ ê ln ç ÷ +1 ú
ë è d ø û
(2)
where
• L = via inductance, [nH].
• h = via length, [in.].
• d = via diameter, [in.].
Because this equation involves a logarithm, changing the via diameter does little to influence the inductance.
A big change may be effected by changing the via length or by using multiple vias in parallel. Therefore,
connect decoupling capacitors to ground by using two paralleled vias per device terminal. For low inductance
connections between ground planes, use multiple vias in regular intervals across the board.
Although it is highly recommended not to change layers of high-speed traces, if the necessity still occurs, ensure
a continuous return current path. Figure 4-13 on the left shows the flow of the return current for a single layer
change and on the right for a multiple layer change.
Signal
current
Return
current Ground Ground
plane plane
Power
plane
Figure 4-13. Return Current Paths for a Single and a Multiple Layer Change
The ability for the current flow to change from the bottom to the top of the ground plane is provided by a metallic
laminate of the inner clearance ring. Thus, when a signal passes through a via and continues on the opposite
side of the same plane, a return current discontinuity does not exist.
Changing a signal trace from one layer to another by crossing multiple reference planes complicates the design
of the return current path. In the case of two ground planes, a ground-to-ground via must be placed near the
signal via to ensure a continuous return current path, (right diagram in Figure 4-13).
If the reference planes are of different voltage potentials, such as the power and ground planes in Figure 4-14,
the design of the return path becomes messy as it requires a third via and a decoupling capacitor. The return
current flow begins at the bottom of the power plane, where it is closest to the signal current. It then flows
through the power via, across the decoupling capacitor into the ground via and returns on top of the ground
plane.
16 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023

Decoupling
capacitor
Ground
Power
Figure 4-14. Return Current Paths for a Single and a Multiple Layer Change
Current return paths comprising multiple vias and decoupling capacitors possess high inductance, thus
compromising signal integrity and increasing EMI. If possible, avoid changing layers during high-speed trace
routing, as it usually worsens board performance, complicates design, and increases manufacturing cost.
4.8 Decoupling Capacitors
Decoupling capacitors provide a local source of charge for ICs requiring a significant amount of supply current
in response to internal switching. Insufficient decoupling causes a lack of supply current required which may
prevent the IC from working properly, resulting in signal integrity data errors to occur. This requires them to
provide low impedance across the frequency range of interest. To accomplish that, a common approach is to
distribute an array of decoupling capacitors evenly across the board. In addition to maintaining signal integrity,
decoupling capacitors serve as EMC filters preventing high-frequency RF signals from propagating throughout
the PCB.
When connecting a capacitor between the power and ground planes, the power supply is actually loaded with a
series resonant circuit, whose frequency dependent R-L-C components represent the equivalent circuit of a real
capacitor. Figure 4-15 shows the parasitic components of an initial equivalent circuit and their conversion into a
series resonant circuit.
RL
C C
RS ESL ESR ESL
RD CD
Figure 4-15. Capacitor Losses Modeled by a Series Resonance Circuit
The leakage resistance R represents the loss through leakage current at low frequencies. R and C indicate
L D D
the losses due to molecular polarization, (R ), and dielectric absorption, (C ). R depicts the resistance in
D D S
the leads and the plates of the capacitor. The three resistive losses are combined into one equivalent series
resistance (ESR). As in the ESR case, the equivalent series inductance (ESL) combines the inductance of the
capacitor plates and the internal leads.

Note that the capacitor connecting vias, although low in impedance, contribute a significant amount to the series
inductance. Therefore, reduce via inductance by using two vias per capacitor terminal.
Figure 4-16 shows the progression of capacitor impedance (Z) versus frequency for a 10-nF capacitor. At
frequencies far below the self-resonance frequency (SRF), the capacitive reactance is dominant. Closer to SRF,
the inductive reactance gains influence trying to neutralize the capacitive component. At SRF, the capacitive
and inductive reactance cancel, and only the ESR is effective. Note that the ESR is frequency dependent, and
contrary to popular belief, does not reach its minimum at SRF. The impedance Z, however, does.
100,000
10,000
1,000 0.1nF
W 100 1nF
-
c
a n 10
d
m p 1 10nF
0.1
0.01
0.001
0.1 1 10 100 1,000
f - Frequency - MHz
Figure 4-16. Capacitor Impedance Versus Frequency
The reason why the paralleling of capacitors in a distributed decoupling network works is because the total
capacitance increases to C = C × n, where n is the number of decoupling capacitors used. And with X = 1/(ω
TOT c
× C), the capacitor impedance is reduced to X = 1/(n × ω × C) for frequencies below SRF. Similarly, this holds
c
true for the inductance. Here L = L/n, and because X = ω × L, the impedance decreases to X = ω × L/n for
TOT L L
frequencies above SRF.
Designing a solid decoupling network must include lower frequencies down to dc, which requires the
implementation of large bypass capacitors. Therefore, to provide sufficient low impedance at low frequencies,
place 1-μF to 10-μF tantalum capacitors at the output of voltage regulators and at the point where power is
supplied to the PCB. For the higher frequency range, place several 0.1-μF or 0.01-μF ceramic capacitors next to
every high-speed switching IC.
18 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023

5 Summary
This design guide helps system designers of galvanically isolated systems to begin designing with TI's broad
portfolio of digital isolators and isolated functions in the shortest time possible. This document explains the basic
operating principle of an isolator, suggests where to place it within a system design, and recommends guidelines
for an EMC-compatible circuit-board design. Despite the enormous amount of technical literature, seminars,
newsletters, and internet forums on PCB design, this document provides designers with layout guidelines in
a comprehensive way. By following the recommendations presented herein, designers can accomplish EMC-
compliant board design in the shortest time possible.
Read our blog, Robust isolators prevent you from saying “I see dead circuits!”
6 References
1. Texas Instruments, Pushing the envelope with high-performance, digital-isolation technology analog
applications journal.
2. Texas Instruments, Enabling high voltage signal isolation quality and reliability white paper.
3. Texas Instruments, High-voltage reinforced isolation: Definitions and test methodologies marketing white
paper.
4. High-speed Digital Design, Johnson/Graham, 1993.
5. Noise Reduction Techniques in Electronic Systems, Ott, 1988.
6. Eliminating the myths about printed circuit board power/ground plane decoupling, Archambeault, 2001.

7 Revision History
Changes from Revision F (July 2022) to Revision G (September 2023) Page
• Added link to TI's opto-emulator overview..........................................................................................................1
Changes from Revision E (July 2022) to Revision F (August 2022) Page
• Updated Digital Isolator Families and Isolated Functions table..........................................................................9
Changes from Revision D (November 2021) to Revision E (July 2022) Page
• Updated the Isolated SPI Interface image..........................................................................................................5
Changes from Revision C (July 2021) to Revision D (November 2021) Page
• Added availability of the ISO67xx family.............................................................................................................1
• Added ISO67xx to list of isolators that use OOK-based communication............................................................4
• Added several devices to the Digital Isolator Families and Isolated Functions table.........................................9
Changes from Revision B (August 2018) to Revision C (July 2021) Page
• Updated the numbering format for tables, figures and cross-references throughout the document..................1
Changes from Revision A (November 2014) to Revision B (July 2018) Page
• Added the ISO77x family of digital isolators to the document............................................................................3
Changes from Revision * (January 2009) to Revision A (October 2014) Page
• Changed Abstract for revision A.........................................................................................................................1
• Changed Operating Principle section including both sub-sections.....................................................................3
• Changed images 1 - 4, beginning on this page..................................................................................................3
• Changed entire section titled Typical Applications for Digital Isolators and Isolated Functions.........................5
• Added Digital Isolator Selection Guide section...................................................................................................8
• Changed Summary...........................................................................................................................................19
20 Digital Isolator Design Guide SLLA284G – JULY 2022 – REVISED SEPTEMBER 2023