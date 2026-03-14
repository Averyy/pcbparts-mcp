---
source: "Wurth Elektronik RD016 -- Gigabit-Ethernet Front End Reference Design"
url: "https://www.we-online.com/components/media/o721295v410%20RD016a%20EN.pdf"
format: "PDF 11pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 26116
---

REFERENCE DESIGN
RD016 | Gigabit-Ethernet Front End
Dr.-Ing. Heinz Zenkner
01. INTRODUCTION some special features. The 1000BASE-T (Gigabit Ethernet)
PHY executes a connection configuration protocol known as
This document provides the circuit developer with an
Autonegotiation. The 8-bit data bytes are converted into
optimized circuit design and layout with all technical data for a
10-bit code groups, the 8B/10B code is robust and has
Gigabit Ethernet Front End.
outstanding properties such as transition density, run-length
The electronics board has two interfaces, one USB C (USB 3.1)
limitation, DC compensation and error robustness. All single,
- and one Gigabit RJ45/Ethernet interface. The GB-Ethernet-
double and triple bit errors in a frame are detected with 100%
USB adapter was developed on the basis of the EVB-
reliability. The signal voltage for 1000BASE-T averages
LAN7800LC Evaluation Board from Microchip. The circuit is
750 mV differential; the limits are > 670 mV, < 820 mV at
built on a 4-layer PCB and in the present design is supplied
100 Ω load.
with voltage via the USB interface. The first part of this
Application Note presents the technical basics necessary for 2.2 Interface structure, necessary hardware
understanding the reference design. The second part details
RJ45 interfaces are designed for full-duplex transmission, i.e.,
the 1 GB Ethernet interface up to the physical layer (PHY in
simultaneous transmission of send and receive data. This is
the OSI model). EMC aspects are dealt with in detail in
possible because the connector has four wire pairs, whereby
Application Note ANP116.
one pair is always required for one direction (differential
voltage principle). Basically, an unshielded twisted pair (UTP)
02. THE 1 GIGABIT ETHERNET INTERFACE
has an impedance of 100 Ω and a shielded twisted pair (STP)
150 Ω (1000BASE-T: IEEE 802.3, e.g., section 39). In the case
2.1 Data rate, technology, signals
of branded cables: CAT5e, 6 and 6a are available both
Ethernet was initially distributed worldwide at 10 Mbps
shielded and unshielded, whereas categories 7 and 7a are
(megabits per second) over coaxial cable and later over
always shielded. For each RJ45 connection, the IEEE standard
unshielded twisted-pair lines with 10BASE-T. Today we have
requires galvanic isolation with a transformer. This
100BASE-TX (Fast Ethernet, 100 Mbps), Gigabit Ethernet
transformer protects the devices from damage due to high
(1 Gbps), 10-Gigabit Ethernet (10 Gbps) and 100-Gigabit
voltage on the line and prevents voltage offsets that can arise
Ethernet (100 Gbps) at our disposal. For most purposes,
due to potential differences between the devices. Figure 1
Gigabit Ethernet works well with a regular Ethernet cable,
shows the schematic of the interface.
specifically using the CAT5e, CAT6 and CAT6a cabling
standards. These cable types follow the 1000BASE-T cabling
standard, also known as IEEE 802.3ab.
Factors such as network protocol overhead, retransmission
due to collisions on the transmission path, or sporadic data
errors, limit the maximum usable data rate under normal
conditions to 900 Mbps. The average connection speed varies
due to many factors, such as the hardware structure of the
PC, the number of clients on the router and not least the
“quality” of the Ethernet cabling.
The 1 GB Ethernet interface operates according to the
Figure 1: Schematic of the GB-Ethernet interface, one of four
802.3ab-1999 (CL40) standard and requires 4 wire pairs /
channels is shown
channels for signal transmission. This results in a symbol rate
The Ethernet signal from the RJ45 interface reaches the
of 125 megabaud (MBd) with a bandwidth of 62.5 MHz per
transformers via the common-mode choke. Figure 1 shows
channel (2 bits per symbol). The GB-Ethernet protocol has
RD016a | 2022-09-21 1 | 11
WÜRTH ELEKTRONIK eiSos® www.we-online.com

APPLICATION NOTE
one of the four channels. The transformer has a center tap
which, in signal terms, represents a zero potential.
Asymmetries lead to a voltage at the center tap and are
terminated to ground via the 75 Ω resistors, which are AC
decoupled via the capacitor. The transformer has a
transformation ratio of 1:1. On the secondary side, the
Ethernet signal reaches the PHY via the four channels. Here,
too, the impedance is 100 Ω differential, or 50 Ω to ground
(GND) in each case. The center tap on the secondary side of
Figure 3: Graphical representation of the GB-Ethernet-USB adapter in
the transformer is AC connected to ground via capacitors. the integrated V2.0 variant. The module shown in Figure 2 is
integrated into the RJ45 jack.
03. CONCEPT AND CONSTRUCTION OF THE
ADAPTER BOARD 3.1 Block diagram
The LAN7800 USB 3.1 Gigabit Ethernet controller connects
The GB-Ethernet-USB Adapter is available in two different
the USB interface to the Ethernet interface as a “bridge”
variants.
(Figure 4). So only the signal adaptations and decouplings
The V1.0 variant contains discrete components in the
have to be realized for wiring the interfaces. On the USB side,
Ethernet interface. This means that the matching network
a DC-DC controller generates the 3.3 V supply voltage
and the inductance block, consisting of common-mode
required for the LAN7800. The LAN7800 requires an
chokes and transformers, are individual components placed
additional 4 kbit EEPROM for the firmware.
on the printed circuit board (Figure 2). In the V2.0 variant, the
above components are integrated into the housing of the
RJ45 jack (Figure 3).
Figure 4: Block diagram of the GB-Ethernet-USB adapter, both
variants
The overall schematics of both variants, analogous to the
Figure 2: Graphical representation of the GB-Ethernet-USB adapter in
the discrete V1.0 version; the module with the transformers and block diagram, are shown in Figure 5 and Figure 6.
common-mode chokes is placed next to the RJ45 jack.
RD016a | 2022-09-21 2 | 11

3.2 Overall schematic
Figure 5: Overall schematic of the GB-Ethernet-USB adapter, V1.0, variant with discrete components at the Ethernet interface
RD016a | 2022-09-21 3 | 11

Figure 6: Overall schematic of the GB-Ethernet-USB adapter, V2.0, variant with integrated components at the Ethernet interface
RD016a | 2022-09-21 4 | 11

3.3 Subcomponents
The following subcomponents are only briefly discussed here,
since this document focuses on the 1 GB-Ethernet interface.
Controller
The LAN7800 is a 1 GB-Ethernet, high-performance USB 3.1
controller with integrated Ethernet PHY. An external 4 kbit
EEPROM was connected for the onboard software. The circuit Figure 8: Circuit diagram of the DC-DC converter from +5 V to 3.3 V
diagram is shown in Figure 7. The upper part of the controller
USB 3.1 interface
in the figure is the signal section, clocked with a 25-MHz
Figure 9 shows the circuit diagram of the USB interface The
quartz; the lower part is the controller’s relatively complex
data lines are connected with common-mode chokes against
chip-internal power supply.
radio interference and with TVS diode arrays against transient
overvoltages. The PCB ground (GND) is connected to the GND
terminals of the cable at X1, but to the housing via a capacitor
(C19) and a resistor (R1).
Figure 9: Circuit diagram of USB interface with power supply filter
If the capacitor C19 is fitted, the connection between GND
and the housing/shielding connection is also high-frequency
and low-impedance. If the circuit is installed in a metal
housing, it may be advantageous for improving EMC
(emission and immunity) to fit an SDM ferrite (e.g.,
742792642) instead of C19. R1 is then omitted. The
connection remains galvanic via the housing and the PCB
mounting holes. The high-frequency reference point shifts
from the electronics / controller, to the housing, however.
This means that any interference there may be in the
immediate vicinity of the controller at its ground connections
Figure 7: Circuit diagram of the controller, upper part: Signal section,
lower part: onboard power supply is not conducted into the cable. The +5 V power supply at X1
is extensively filtered.
Power supply +5 V to +3.3 V
C44 blocks high-frequency interference directly against the
The controller requires a supply voltage of 3.3 V. This is
housing, after which the supply voltage is broadband
generated with the TLV757P linear regulator in this case. The
decoupled via FB1, L1 and FB2 with capacitors C1 and C2
LDO (low dropout regulator) reduces the voltage from 5.0 V to
configured as a Double-π- filter. D1 is a TVS diode that limits
3.3 V. The 10 µF input and output electrolytic capacitors
transient overvoltage from 25 V up to a peak current of 80 A.
ensure stable operation, and the 100 nF X7R capacitor
As this diode has a parasitic capacitance of 240 pF, FB2 forms
reduces high-frequency interference.
an effective low-pass filter against high-frequency
interference.
RD016a | 2022-09-21 5 | 11

3.4 Ethernet interface
The Ethernet transformer (LAN transformer) is the interface
between the device and the Ethernet cable. The transformer
provides the safety-relevant galvanic isolation between
device and cable while providing impedance matching to the
internal logic on the one hand and to the balanced wire pairs,
on the other. The transformer also protects the device from
transient interference, suppresses common mode signals
between the transceiver IC and the cable, both from the
device to the outside as well as from the outside cable to the
electronics in the device. The component must also transmit
broadband data up to 1 Gbps, however, without significantly
attenuating the signal transmitted and received. Additional
components are necessary to achieve matching and satisfy
EMC requirements. There are two approaches to building the
interface:
1. The use of a ready-made module, which integrates the
Ethernet jack, the transformer and the Bob Smith
termination, is the V2.0 variant described above.
2. A setup with discrete technology, in this case V1.0
Figure 10: WE-LAN AQ transformer for galvanic isolation between the
variant. All components must be adapted to each other PHY and the Ethernet network
in this case, but the solution offers more degrees of
freedom while the selection of components as well as The center tap of the primary side winding, i.e., to the
the configuration and the layout are left to the Ethernet port, has the "Bob Smith" termination mentioned
developer. Although a little more design work is above (Figure 11). For each wire pair, a 75 Ω resistor is
required, the discrete version is less expensive and, for connected to form a "star point”, the whole circuit is then
special requirements, isolation voltages of up to 6 kV galvanically isolated and connected to the chassis ground by
can be achieved. means of two parallel 100 pF capacitors; capacitors up to 2 nF
are mentioned in the literature, which is a relatively high value
As there is no functional difference between the two variants,
in relation to the frequency range. The capacitors should have
the circuitry of the GB-Ethernet interface is explained below
a dielectric strength of at least 2 kV.
using the V1.0 variant with discrete components.
The “Bob Smith” termination is used to reduce interference
3.5 Circuit description of the 1 GB Ethernet front end caused by common-mode current flows as well as
The LAN transformer X3 in Figure 10 provides DC isolation susceptibility to interference from unused wire pairs on the
between the electronics and the network cable. The minimum RJ45 connector.
test voltage for the transformer between primary and Bob Smith referenced an impedance of about 145 Ω per wire
secondary is 1,500 VRMS. pair. Due to the wealth of cable types on the market, the
differences in the base impedances of the various cable types,
and the fact that the cables do not have a constant
impedance over the length caused by twisting, common-
mode chokes were also implemented (Figure 10). In the X3
module, for example, one transformer and one common-
mode choke are connected together per channel. These
chokes cannot correct impedance matching deviations, but
they do significantly improve EMC.
RD016a | 2022-09-21 6 | 11

capacitors should be fitted to connect the Ethernet cable
shield to the reference ground. The 0 Ω R19 and R20
resistors serve the same purpose, but there is no galvanic
isolation as would be realized with the capacitors. The
alternative fitting options are provided here for
“experimental” purposes, the Application Note ANP116 goes
into this in more detail.
The capacitors C32 to C35 in Figure 13, on the secondary side
of the transformers, connect the center taps of the
transformers with the ground (GND) for HF.
Figure 11: Primary interface zone between the Ethernet jack and
transformer
R9, R10 and C52 in Figure 11 are provided to supply power to
the LEDs integrated in the connection jack. The two
connections B1 and B2 at the X2 Ethernet jack must be Figure 13: Secondary interface zone between the transformer and the
connected directly, i.e., with low impedance (!) to the chassis PHY
ground. This connection is crucial for the shield connection of
To avoid DC equalization currents from the PHY, galvanic
the cable and thus for the "quality" of the shielding
isolation using capacitors is necessary. Resistors R27 to R30
attenuation.
are provided based on the requirements of some PHY
With C36 to C38 and C41 to C43 (Figure 12), the shielding of
manufacturers (current-mode line driver option), but are
the Ethernet jack and therefore also the cable shield can be
usually not needed when the PHY is operating in standard
connected to the board ground (GND).
voltage mode.
The TVS diode arrays D6 and D7 are indispensable, however,
as they limit transient interference occurring on the interface
side to the PHY to the circuit ground (GND). On the secondary
side, i.e., after the transformers of the X3 module, the
transient interference occurs in common mode, so a TVS
diode must be connected to the reference ground at each
transformer connection. However, the interference level is
lower on the secondary side of the transformer than on the
primary side. Low impedance connection of the diodes is
important for the function of the TVS diodes, looped into the
signal lines, on the one hand, and to ground, on the other. The
TVS diode arrays WE-TVS (824014885) used here feature a
particularly low parasitic capacitance. Besides the array's
Figure 12: Capacitors for connecting between the board GND and the special Schottky diodes, the “absent” connection to the
shield ground or housing positive supply voltage also helps achieve low parasitic
capacitance (Figure 14). The “Ccross” value of 0.08 pF is the
With sheet metal housing, it makes sense not to fit these
capacitance with which the Ethernet signal is loaded.
capacitors and to connect the electronics GND directly to the
Nevertheless, it should not be forgotten that the parasitic
housing with screw connections. For plastic housing, the
RD016a | 2022-09-21 7 | 11

capacities of the entire design must be added: solder pads, 4. Spacing between the Ethernet signal traces and the
vias, capacitances between components and the housing. GND islands in the same plane: > 2S
5. Spacing between adjacent Ethernet difference pairs: >
2S
Additional points to consider:
1. The blocking capacitors for the PHY must be placed
directly beside the IC.
2. 4.7 µF / 0.1 µF / 1 nF capacitors on each VCC pin.
3. Inductance of the traces to the components L < 1.5 nH
– 2 nH, i.e., connections shorter than 2 mm between
capacitor and the IC pin.
An essential point is the maximum signal skew (propagation
delay time) of the wires within a pair (intra-pair) and between
the pairs (inter-pair). The maximum “skew” values can be
found in the Ethernet specification (IEEE 802.3-2008
standard), general reference values:
1. Maximum length offset between the wire pairs (inter-
pair): 50 mm (< 330 ps)
Figure 14: TVS diode array WE-TVS (824014885) with its very low
2. Maximum skew within a wire pair (intra-pair): < 1.6 ps
parasitic capacitance
corresponding to 250 µm
3.6 Component placement and layout of the 1 GB The conversion between temporal and path offset is achieved
Ethernet front end with the following relationship:
Layout is an essential factor in the design of circuits with
C 299,792458mm mm
V = V = =146.28
high-frequency signals, or signals with very short rise times. P ɛr P F R4 4.2
,
s ns
The layout of the GB-Ethernet design must also be VP: pro√pagation speed( (mm) /ns) √
HF-compatible. C: speed of light
r: dielectric permittivity of the PCB material
ɛ
The following Figure 16- Figure 19 show the layout regions of
the Ethernet interface; according to the figures, the
explanation follows.
Figure 15: Schematic representation of the dimensions for the layout
of the traces
Figure 16: Top layer with positioning of the “Bob Smith” components
With reference to Figure 15, the following points should be
and the TVS diodes
noted:
1. It goes without saying that a PCB with a minimum of 4
layers must be used.
2. The VCC and GND layers are on the inside.
3. Spacing from other traces to Ethernet traces to avoid
coupling: > 3S
RD016a | 2022-09-21 8 | 11

1. The TVS diode arrays must be connected directly into
the signal path and to GND so as to avoid a voltage drop
due to parasitic inductance. An extract of the layout
Figure 16 is shown in Figure 20.
Figure 17: Bottom layer with positioning of the “Bob Smith”
components and the TVS diodes
Figure 20: Layout extract, via pads of the TVS diode array routed into
the signal path
2. The chassis/connector ground SGND is separated from
the electronics GND in all four layers.
3. The SGND layers must not overlap with other layers, as
otherwise capacitive coupling will occur.
4. Ground planes through-contacted with a pitch of
approx. 4 mm (vias).
5. Symmetrical signal lines, differential impedance of
100 Ω to reference ground.
6. Symmetrical signal lines:
 Width of the traces: 0.154 mm
 Spacing between the traces: 0.125 m
 Spacing of the signal to the reference plane (prepreg
thickness): 0.2 mm
04. SUMMARY, LIST OF ESSENTIAL POINTS
FOR THE DESIGN
1. Chassis/jack ground to electronics GND is separated in
all four layers. This avoids that the surfaces of the
chassis ground overlap with other layers in order to
Figure 18: 3D view with positioning of the “Bob Smith” components keep capacitive coupling as low as possible.
and the TVS diodes
2. The ground planes are connected to each other with a
pitch of approx. 4 mm by means of vias.
3. The signal lines coming from the Ethernet jack are
symmetrical, with a differential impedance of 100 Ω
routed to the reference ground. The conductor pairs
have a trace width of 0.154 mm and are spaced
0.125 mm apart. Spacing of the signal to the reference
plane (prepreg thickness): 0.2 mm
4. The Ethernet jack is positioned at the edge of the PCB to
ensure a low-impedance connection to a metal housing,
if necessary. The transformer (X3) is placed in close
proximity in order to keep the electrical coupling
influences or impairments caused by long conductor
Figure 19: The four layers of the interface zone in the same section
paths to a minimum.
Layout considerations, with reference to Figure 16 to Figure
5. As on the primary side, a differential impedance of
19:
100 Ω to the reference ground must also be maintained
RD016a | 2022-09-21 9 | 11

on the secondary side of the transformer module for the remain symmetrical. Shifting of layers has to be
traces. The TVS arrays must be connected directly into minimized. The differential pairs must be referenced to
the signal path and to GND so as to avoid a voltage drop the same power supply plane / ground plane. Routing
due to parasitic inductance. must never be via different planes!
6. Each TRxP/TRxN signal group should be routed as a 11. If the four differential pairs are routed from the PHY to
differential trace pair. This includes the entire length of the RJ45 jack, generally at least one pair requires a via to
the traces from the RJ45 connector to the PHY. The the external plane on the other side. In this case, it must
differential pairs should be as short as possible and be ensured that routing on the other side of the board
have a differential impedance of 100 Ω i.e., each 50 Ω to (usually layer 4) is via a continuous reference plane with
ground. low impedance to ground.
7. Differential pairs should be routed as close to each other 12. All impedance terminations must always be referenced
as possible. The smallest trace spacing (0.1 - 0.13 mm) to the same reference plane as the differential lines. The
is typically selected at the start of impedance resistive terminations, i.e., resistors, should have a 1.0%
calculation. Then the width of the trace is adjusted to tolerance. All capacitive terminations, i.e., capacitors in
achieve the required impedance. This ensures high the Ethernet front end, should have tight tolerances and
coupling between the signal pairs. high-quality dielectrics.
8. Differential pairs should be routed away from all other
traces to avoid coupling to other traces and therefore
05. FINAL REMARKS
asymmetry. The spacing should be at least 4 mm. The
The 1 GB USB 3.1 – Interface Board was originally developed
intra-pair and inter-pair offset between the signal pairs
as an EMC test board to investigate the performance of
should be less than 1.3 mm over the full length. To
different EMC concepts. The results of this may be found in
achieve optimum interference immunity, each pair
Application Note ANP116. Numerous requests for design
should be routed as far apart as possible.
details of a 1 GB Ethernet interface have helped make this
9. For optimal separation, GND planes can be inserted
document available to our customers as a reference design.
between differential pairs. A spacing of 3-5 times the
The details described here should allow you to build a replica
dielectric spacing (spacing between the copper layers
of a 1 GB Ethernet interface without any problems. The data
within the PCB) should be maintained from this ground
for Altium Designer®, as well as the Gerber data, are available
plane to one of the traces.
on our homepage for unrestricted use.
10. The use of vias has to be minimized. If vias are used,
they must be adapted such that the differential pairs
RD016a | 2022-09-21 10 | 11

IMPORTANT NOTICE
The Application Note is based on our knowledge and experience of RIGHT, COPYRIGHT, MASK WORK RIGHT, OR OTHER INTELLECTUAL
typical requirements concerning these areas. It serves as general PROPERTY RIGHT RELATING TO ANY COMBINATION, MACHINE, OR
guidance and should not be construed as a commitment for the PROCESS IN WHICH WE PRODUCTS OR SERVICES ARE USED.
suitability for customer applications by Würth Elektronik eiSos INFORMATION PUBLISHED BY WE REGARDING THIRD-PARTY
GmbH & Co. KG. The information in the Application Note is subject to PRODUCTS OR SERVICES DOES NOT CONSTITUTE A LICENSE
change without notice. This document and parts thereof must not FROM WE TO USE SUCH PRODUCTS OR SERVICES OR A
be reproduced or copied without written permission, and contents WARRANTY OR ENDORSEMENT THEREOF.
thereof must not be imparted to a third party nor be used for any WE products are not authorized for use in safety-critical
unauthorized purpose. applications, or where a failure of the product is reasonably
Würth Elektronik eiSos GmbH & Co. KG and its subsidiaries and expected to cause severe personal injury or death. Moreover, WE
affiliates (WE) are not liable for application assistance of any kind. products are neither designed nor intended for use in areas such as
Customers may use WE’s assistance and product recommendations military, aerospace, aviation, nuclear control, submarine,
for their applications and design. The responsibility for the transportation (automotive control, train control, ship control),
applicability and use of WE Products in a particular customer design transportation signal, disaster prevention, medical, public
is always solely within the authority of the customer. Due to this information network etc. Customers shall inform WE about the
fact it is up to the customer to evaluate and investigate, where intent of such usage before design-in stage. In certain customer
appropriate, and decide whether the device with the specific product applications requiring a very high level of safety and in which the
characteristics described in the product specification is valid and malfunction or failure of an electronic component could endanger
suitable for the respective customer application or not. human life or health, customers must ensure that they have all
The technical specifications are stated in the current data sheet of necessary expertise in the safety and regulatory ramifications of
the products. Therefore the customers shall use the data sheets their applications. Customers acknowledge and agree that they are
and are cautioned to verify that data sheets are current. The current solely responsible for all legal, regulatory and safety-related
data sheets can be downloaded at www.we-online.com. Customers requirements concerning their products and any use of WE products
shall strictly observe any product-specific notes, cautions and in such safety-critical applications, notwithstanding any
warnings. WE reserves the right to make corrections, modifications, applications-related information or support that may be provided by
enhancements, improvements, and other changes to its products WE.
and services. CUSTOMERS SHALL INDEMNIFY WE AGAINST ANY DAMAGES
WE DOES NOT WARRANT OR REPRESENT THAT ANY LICENSE, ARISING OUT OF THE USE OF WE PRODUCTS IN SUCH SAFETY-
EITHER EXPRESS OR IMPLIED, IS GRANTED UNDER ANY PATENT CRITICAL APPLICATIONS.
U S E F UL L I NK S CONTACT I NF OR MATI ON
Application Notes appnotes@we-online.de
www.we-online.com/appnotes Tel. +49-7942-945-0
REDEXPERT Design Plattform Würth Elektronik eiSos GmbH & Co. KG
www.we-online.com/redexpert Max-Eyth-Str. 1 ⋅ 74638 Waldenburg
Germany
Toolbox www.we-online.com
www.we-online.com/toolbox
Product Catalog
www.we-online.com/products
RD016a | 2022-09-21 11 | 11