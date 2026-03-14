---
source: "TI SLVA951 -- Layout Guide for the DRV832x Family of Three-Phase Smart Gate Drivers"
url: "https://www.ti.com/lit/pdf/slva951"
format: "PDF 14pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 23423
---

Application Report

Layout Guide for the DRV832x Family of Three-Phase
Smart Gate Drivers
ABSTRACT
Effective printed circuit board (PCB) layout is required to achieve the best performance for high-power,
high-speed, or low-noise systems. Issues with PCB layout can cause EMI or EMC radiation, additional
heat, noise coupling, device faults, and a host of other possible problems on the board. The DRV832x
family of Smart Gate Drivers is no exception to this rule, and, although the device is designed to operate
in the harshest conditions, knowledge on the best way to layout the PCB can lead to maximizing the
effectiveness of the driver. This document describes two-layer PCB layout with the DRV832x devices,
however these principles also apply to boards with more than two layers. This application report can also
be applied to the DRV8304 device, which has the same pin out as DRV8323. However, some external
component values may be different.
For additional layout examples, refer to the following resources:
• BOOSTXL-DRV8320S EVM or BOOSTXL-DRV8320H EVM
• BOOSTXL-DRV8323RS EVM or BOOSTXL-DRV8323RH EVM
• TIDA-00774
• TIDA-01485
• TIDA-01516
Contents
1 DRV832x Family Introduction .............................................................................................. 2
2 Proper Device Grounding................................................................................................... 3
3 Heat Sinking.................................................................................................................. 5
4 Traces and Vias.............................................................................................................. 5
5 DRV832x Base External Components.................................................................................... 5
6 Gate Driver Layout........................................................................................................... 7
6.1 VDRAIN Pin ......................................................................................................... 7
6.2 GHx Pins............................................................................................................. 7
6.3 SHx Pins ............................................................................................................ 8
6.4 GLx Pins ............................................................................................................ 8
6.5 SLx or SPx Pins .................................................................................................... 8
7 Half-H Bridge Layout ........................................................................................................ 8
7.1 High-Side MOSFET (Q ).......................................................................................... 8
HS
7.2 Low-Side MOSFET (Q ) .......................................................................................... 8
LS
7.3 Decoupling Capacitor (C ).................................................................................... 8
BYPASS
7.4 Sense Resistor (R ) ............................................................................................ 8
SENSE
8 Sense Amplifier Layout.................................................................................................... 10
9 DC-DC Buck Regulator Layout........................................................................................... 11
9.1 Small Current Loops .............................................................................................. 12
9.2 Continuous Ground Plane........................................................................................ 12
9.3 Feedback Path..................................................................................................... 13
9.4 Split Ground Plane ................................................................................................ 13
List of Figures
1 DRV832x Device Legend .................................................................................................. 2

2 DRV8320 Common Ground Plane ........................................................................................ 3
3 DRV8320 Split Ground Plane.............................................................................................. 3
4 DRV8320R Common Ground Plane ...................................................................................... 3
5 DRV8320R Split Ground Plane............................................................................................ 3
6 DRV8323 Common Ground Plane ........................................................................................ 3
7 DRV8323 Split Ground Plane.............................................................................................. 3
8 DRV8323R Common Ground Plane ...................................................................................... 4
9 DRV8323R Split Ground Plane............................................................................................ 4
10 DRV8320 Base External Component Layout ........................................................................... 6
11 DRV8320R Base External Component Layout ......................................................................... 6
12 DRV8323 Base External Component Layout ........................................................................... 6
13 DRV8323R Base External Component Layout ......................................................................... 6
14 Half-H Bridge Layout ........................................................................................................ 9
15 Half-H Bridge Current Loop ................................................................................................ 9
16 DRV8323 Sense Amplifier Layout ....................................................................................... 10
17 DRV8323R Sense Amplifier Layout ..................................................................................... 10
18 Shielding on a Split-Supply System ..................................................................................... 11
19 DRV8320R Buck Regulator Layout...................................................................................... 11
20 DRV8323R Buck Regulator Layout...................................................................................... 11
21 Small Current Loop Layout ............................................................................................... 12
Trademarks
SIMPLE SWITCHER is a trademark of Texas Instruments.
All other trademarks are the property of their respective owners.
1 DRV832x Family Introduction
The DRV832x family of Smart Gate Drivers includes several device variants that integrate optional sense
amplifiers, a DC/DC buck regulator, or both. The packages for this family are QFN-type, ranging from 5 ×
5 mm and 32 pins, to 7 × 7 mm and 48 pins. For more information on the DRV832x family of devices,
refer to the DRV832x 6 to 60-V Three-Phase Smart Gate Driver data sheet.
DRV83 (2) (3) (R) (S) (RGZ) (R)
Prefix Tape and Reel
DRV83 ± Three Phase Brushless DC R ± Tape and Reel
T ± Small Tape and Reel
Package
RTV ± 5 × 5 × 0.75 mm QFN
Series RHA ± 6 x 6 × 0.9 mm QFN
2 ± 60 V device RTA ± 6 x 6 × 0.75 mm QFN
RGZ ± 7 × 7 × 0.9 mm QFN
Interface
Sense amplifiers
0 ± No sense amplifiers S ± SPI interface
3 ± 3x sense amplifiers H ± Hardware interface
Buck Regulator
[blank] ± No buck regulator
R ± Buck regulator
Figure 1. DRV832x Device Legend

Ground (common)
INHA
INLA
INHB
PGND
CPL
DDVD DNGA
ELBANE CN/SCSn
EVIRDI/IDS
SLC
GLC
SHC
GHC
GHB
SHB
GLB
SLB
HPC MV NIARDV AHG AHS ALG ALS
16
15
14
13
12
11
10
9
1 2 3 4 5 6 7 8
25
26
28
29
30
31
42 32 22 12 02 91 81 71
INLB
INHC
INLC
32
PCV
27
SDV/KLCS EDOM/ODS
TLUAFn
Thermal Pad & INHB
Vias
Top Layer
Bottom Layer
PCV

2 Proper Device Grounding
Typical systems using the DRV832x device have one ground plane encompassing the system. In common
ground plane systems, all ground pins should be connected directly to the thermal pad and to the ground
plane. Typically, a mostly solid ground plane is included on the bottom layer (or some inner layer for multi-
layer boards) underneath the DRV832x device, and the thermal pad is connected to the solid ground
plane using vias. Thermal reliefs should never be used to attach thermal pads to the PCB.
In some systems, splitting the power and logic ground planes is required to isolate noise from power
switching from the logic and microcontroller (MCU). In this case more care must be used when connecting
the pins of the DRV832x device to the correct ground plane (either power or logic). The two ground planes
must be connected at a place close enough to the DRV832x device. The thermal pad on the DRV832x
device is connected to the power ground plane in this case, and TI recommends having a power ground
that fills the area directly beneath the component on a different layer to let the vias from the thermal pad
connect.
Logic Ground
(MCU Side)
Recommended Ground
Connection Point
Alternative Thermal Pad &
Ground Vias
Connection
Point
Power Ground
(FET Side)
Figure 2. DRV8320 Common Ground Plane Figure 3. DRV8320 Split Ground Plane

CAL
AGND
DVDD
ELBANE
NIAG/SCSn SDV/KLCS EVIRDI/IDS
BOS COS
SNC
SPC
SNB
SPB
LPC PCV MV NIARDV AHG AHS ALG APS ANS
20
19
18
17
1 2 3 4 5 6 7 8 9 01
33
34
36
37
38
39
03 92 82 72 62 52 42 32 22
40
HPC
35
EDOM/ODS
FERV
AOS
Thermal Pad & Vias
BGND
CB
nSHDN
FB
Recommended
Ground Connection
Alternative Thermal Pad & Vias
Ground
BHNI ALNI AHNI DDVD
ELBANE EVIRDI/IDS EDOM/ODS
nFAULT
GND
DNGP HPC PCV MV NIARDV AHG AHS ALG ALS
SW
NC
VIN
LPC
DNGA
CN/SCSn SDV/KLCS

Alternative Ground Connection Point
Reommended
Figure 4. DRV8320R Common Ground Plane Figure 5. DRV8320R Split Ground Plane
Figure 6. DRV8323 Common Ground Plane Figure 7. DRV8323 Split Ground Plane

DDVD DNGA LAC
NIAG/SCSn SDV/KLCS EVIRDI/IDS EDOM/ODS
DNGD FERV AOS
SOB
SOC
BF LPC HPC PCV MV NIARDV AHG AHS ALG APS ANS
24
23
22
21
1 2 3 4 5 6 7 8 9 01 11 21
41
42
44
45
46
47
63 53 43 33 23 13 03 92 82 62 52
48
DNGP
43
72
INHA Alternative Ground
Connection Point INLA
Recommended
Ground Connection

Figure 8. DRV8323R Common Ground Plane Figure 9. DRV8323R Split Ground Plane
3 Heat Sinking
The DRV832x device is a gate driver and therefore it is not the primary power generator in the system.
However, the gate driver and additional DC/DC buck regulator dissipate power while in operation. This
power is removed from the device through the thermal pad into the copper of the ground plane on the
PCB. Adequate PCB area for the ground plane should be a priority in layout because a constricted or
isolated ground plane will cause the DRV832x device to operate with a temperature that is hotter than
required. As mentioned previously, thermal reliefs should never be used on thermal pads.
4 Traces and Vias
In general, all traces should be as short and thick as possible. Typically, rules such as 15 mils (0.381mm)
per Ampere of current are used to minimize the parasitic inductance and resistance of board components.
Long, skinny traces result in a large inductor effect and can even act as an antenna to radiate EMI. Vias
are usually an inductive element and follow a general rule that each via is capable of at most 200 mA. A
good practice is to avoid vias wherever possible, especially in high-speed switching or power elements.
This practice usually leads to more traces on the top layer of the board, which in turn allows for a more
solid ground plane on the bottom layer. Another good practice is to make sure the diameter of the via is at
least the width of the incoming trace.
5 DRV832x Base External Components
The DRV832x basic features include a charge pump to power the high-side N-channel MOSFETs as well
as DVDD, a 3.3-V low-dropout (LDO) regulator that powers internal digital circuits but can also be used to
power other circuits externally (up to 30 mA). The external components for these features are defined as
follows:
C — The C capacitor is the supply bypass capacitor which should be a supply-rated X5R or X7R type,
VM VM
0.1-µF ceramic capacitor connected from the VM pin to the PGND pin.

CDVDD
Thermal Pad & BGND
Vias CB
CSW
CVCP
CVM
EVIRDI/IDS EDOM/ODS
CN/SCSn
SDV/KLCS

C — The C capacitor is the charge pump bucket capacitor which should be a supply-rated X5R or
VCP VCP
X7R type, 47-nF ceramic capacitor connected from the CPH pin to the CPL pin.
C — The C capacitor is the charge pump storage capacitor which should be a 16-V, X5R or X7R
SW SW
type, 1-µF ceramic capacitor connected from the VCP pin to the VM pin.
C — The C capacitor is the LDO bypass capacitor which should be a 6.3-V, X5R or X7R type, 1-
DVDD DVDD
µF ceramic capacitor connected from the DVDD pin to the AGND pin.
These components should be placed as close as possible to the pins without any long traces or ground
loops.
Figure 10. DRV8320 Base External Component Layout Figure 11. DRV8320R Base External Component Layout

1 2 3 4
ELBANE NIAG/SCSn SDV/KLCS EVIRDI/IDS TLUAFn
5 6 7 8 9 01
DDVD DNGA LAC ELBANE
TLUAFn DNGD FERV AOS

Figure 12. DRV8323 Base External Component Layout Figure 13. DRV8323R Base External Component Layout
6 Gate Driver Layout
The gate driver pins on the DRV832x family of devices are the VDRAIN, GHx, SHx, GLx, and SLx or SPx
pins. The following sections describe these pins.
6.1 VDRAIN Pin
The VDRAIN pin is used to sense the high-side MOSFET drain voltage, which is the supply to the external
MOSFETs, for overcurrent VDS sensing. The DRV832x device monitors the drain-to-source voltage
across the external MOSFETs to determine if an overcurrent event occurs. Typically, the VDRAIN pin is
on the same net as the VM pin on the DRV832x device. In some boards, some distance between the
DRV832x and the FETs can exist, and traces may add inductance or voltage drops to affect the accuracy
of this overcurrent protection. The device has a dedicated pin so that a Kelvin connection can be made to
the high-side FETs. This connection allows the VDRAIN pin to be routed as close to the external MOSFET
drains as possible without interference from other sources. Net Ties are components that can be used in
schematics to make sure that the Kelvin connection is maintained.
6.2 GHx Pins
The GHx pins are the high-side gate and should be connected directly to the gate pin of the high-side
MOSFETs. These traces will conduct the source or sink current into and out of the external MOSFET
gate. TI recommends that a gate signal stays in the same layer when possible to avoid vias and maintain
at least a 20 mil wide trace.

6.3 SHx Pins
The SHx pins are the high-side source, also called the output or the phase node. These pins route to the
connection between the high-side MOSFET source and low-side MOSFET drain, which is the same node
that is connected to the brushless-DC motor. This pin is used internally for overcurrent VDS sensing of the
high-side (VDRAIN to SHx) and low-side (SHx to SLx or SPx) MOSFETS. The SHx pin should be routed
as close to the low-side MOSFET drain and high-side MOSFET source as possible.
6.4 GLx Pins
The GLx pins are the low-side gate, and should be connected directly to the gate pin of the low-side
MOSFETs. These traces will conduct the source or sink current into and out of the external MOSFET
gate. TI recommends that a gate signal stays in the same layer when possible to avoid vias and maintain
at least a 20 mil wide trace.
6.5 SLx or SPx Pins
On the DRV8320 and DRV8320R devices, which have no integrated sense amplifiers, the SLx pin is the
low-side MOSFET VDS monitor. The low-side MOSFET overcurrent monitor measures the voltage across
the SHx to SLx pins. On the DRV8323 and DRV8323R devices, the SLx pin is replaced by the SPx pin.
The SPx pin is actually a sense amplifier input pin, however the functionality of the low-side VDS monitor
is included on the SPx pin as well. On the DRV832x devices with sense amplifiers the low-side MOSFET
overcurrent monitor measures the voltage across SHx to SPx. These signals should be routed as a
differential for a more accurate measurement.
7 Half-H Bridge Layout
The DRV832x device interfaces with the external MOSFETs in a half-H configuration. The half-H bridge
has two N-channel MOSFETs (high-side and low-side) as well as any decoupling capacitor and (usually) a
sense resistor.
7.1 High-Side MOSFET (Q )
The Q component is connected to the supply voltage (on the drain), the motor (on the source), and the
DRV832x device (on the gate). Do not use thermal relief on any pads of this component. The GHx pin of
the DRV832x device should be routed to the gate of Q with as short of a trace as possible.
7.2 Low-Side MOSFET (Q )
The Q component is connected to the motor (on the drain), ground or the sense resistor (on the source),
and the DRV832x device (on the gate). Do not use thermal relief on any pads of this component. The GLx
pin of the DRV832x device should be routed to the gate of Q with as short of a trace as possible.
7.3 Decoupling Capacitor (C )
The C component is connected between the drain of the high-side MOSFET and the source of the
low-side MOSFET. This component supplies current to the half-H bridge during fast switching. Do not use
thermal relief on any pads of this component.
7.4 Sense Resistor (R )
The R component (if present) is connected between the low-side MOSFET source and power ground.
The SPx and SNx pins are connected to the terminals of the sense resistor to amplify and measure the
voltage across the resistor when current is flowing. The SPx and SNx pins must be routed as independent
traces directly to the terminals of the sense resistor. Do not use thermal relief on the sense resistor
terminals because it can cause large voltage spikes because of increased parasitic inductance.

S D
R
QLS
(to SNx)
(to SPx) G D
(to GLx)
(to SHx)
(to GHx) OUTx
D G
D S
Q
C
(to VDRAIN)
Figure 14. Half-H Bridge Layout
NOTE: The VDRAIN pin should be a unique connection to the supply close to the external high-side
MOSFET drain which ensures best operation of the VDS overcurrent monitors. Similarly, the
SHx pin should be routed to the connection between the high-side MOSFET source and low-
side MOSFET drain as an independent trace.
The following path should have a minimal length: GND-C -VM-Q -OUTx-Q -R -GND. This path
BYPASS HS LS SENSE
is the high-current path in the system and all traces in this loop should have traces sized to carry the
motor current (with additional margin).
RSENSE
QLS
(to SNx)
(to SPx) G D
(to GLx)
OUTx
(to SHx)
(to GHx)
D G
QHS
CBYPASS
(to VDRAIN)
Figure 15. Half-H Bridge Current Loop

1 2 3 4
ELBANE NIAG/SCSn SDV/KLCS EVIRDI/IDS TLUAFn
5 6 7 8 9 01
FERV AOS
CVREF
Current Sense
Amplifier Outputs
(To MCU)
Current Sense
Amplifier Inputs
(Phase A)
)C
esahP(
)B
LAC
ELBANE NIAG/SCSn SDV/KLCS EVIRDI/IDS EDOM/ODS TLUAFn DNGD FERV
Current CDVDD Sense
Amplifier
Outputs
(To MCU)
Current Sense Amplifier
Inputs
(Phase A)
)C
)B

8 Sense Amplifier Layout
The DRV8323 and DRV8323R devices contain three current sense amplifiers which are used with the
external current sense resistors to measure the current in each winding of the motor. The SPx and SNx
pins are the sense amplifier inputs and are routed directly across the sense resistor. The SOx pin is the
sense amplifier output. The VREF pin is a voltage input which sets the range of the sense amplifier output
and sets the bias of the amplifier output at VREF/2. The VREF pin requires one ceramic bypass capacitor,
a VREF-rated X5R to X7R type, 0.1-µF ceramic capacitor from the VREF pin to either the AGND (on
DRV8323) or DGND (on DRV8323R) pin.
Figure 16. DRV8323 Sense Amplifier Layout Figure 17. DRV8323R Sense Amplifier Layout
Occasionally, designers want to shield traces by surrounding the traces with additional ground traces. If a
split supply is used, the SPx and SNx pins should exist in the power ground domain because they are
connected to the power stage. Any trace shielding should be done using the power ground. The VREF
and SOx pins should be on the logic ground domain, and shielding should be done using the logic ground.

Recommended Ground
Connection Point
Alternative Thermal Pad & Vias
AOS BOS COS

Figure 18. Shielding on a Split-Supply System
9 DC-DC Buck Regulator Layout
For best practices on layout of switching power supplies, refer to the following:
• Texas Instruments, AN-1149 Layout Guidelines for Switching Power Supplies application report
• Texas Instruments, LMR16006 SIMPLE SWITCHER™ 60 V 0.6 A Buck Regulators With High
Efficiency ECO Mode data sheet

BF
2
CB 44
NC 46
INLB LSW CBOOT I
I
N
N
H
L
BGND CB
DSW nSHDN FB
CVIN
COUT
LSW
CBOOT
SW 45
DSW VIN 47
RFB1 RFB2
COUT
nFAULT GND
GLC SHC GHC
SHB GLB SLB
DNGP HPC PCV MV AHG AHS ALG ALS
20 19
17 16 15
13 12 11
31 32
34 36
38 39
VIN 40
RFB2
RFB1 CSW
NIARDV
INHB INLB
INLC BGND
VIN nSHDN
ELBANE NIAG/SCSn SDV/KLCS EVIRDI/IDS EDOM/ODS TLUAFn
SNC SPC
SHC GHC GHB
GLB SPB SNB
22 21
Thermal Pad & Vias 19 18 17
15 14 13
39 40
42 44
46 47
NC 48

LSW CBOOT
DSW
RFB1 RFB2
COUT CVCP
Figure 19. DRV8320R Buck Regulator Layout Figure 20. DRV8323R Buck Regulator Layout
The following sections describe some specific concerns regarding the DC-DC regulator present on the
DRV8320R and DRV8323R devices.
9.1 Small Current Loops
A DC/DC system has two key current loops. The primary loop is GND-D -SW-L -OUT-C -GND, and
SW SW OUT
the secondary loop is GND-C -VIN-SW-L -OUT-C -GND. Make sure these paths are as small as
VIN SW OUT
possible.
Figure 21. Small Current Loop Layout
9.2 Continuous Ground Plane
Underneath the two current loops mentioned previously, make sure a solid ground plane exists that is not
cut by traces. Routing traces around these loops is more efficient than routing straight through them (see
Section 9.3).

9.3 Feedback Path
The FB pin uses the feedback voltage to control the output of the DC/DC regulator. A resistor divider
(RFB1, RFB2) is tapped from the output and fed into the FB pin. Make sure that the resistor divider is
placed as close to the FB pin as possible. If the resistor divider is far away from the pin, the FB trace may
pick up extra noise because it is high impedance. Another consideration is routing the DC/DC output
voltage back to the resistor divider. Make sure not to interrupt the ground plane underneath the current
loops previously mentioned.
9.4 Split Ground Plane
The BGND pin is actually a very-low current node. The majority of the current into or out of the ground in
the system is sourced through the D component or from the C and C capacitors. When the logic
SW OUT VIN
ground and power ground are split, the DC/DC buck regulator normally acts as the interface between the
two domains, providing a low voltage logic supply in the logic domain. One strategy to have better noise
immunity is to have BGND on the logic ground, as well as the ground reference for the resistor divider into
the FB pin and C capacitor. The power ground can be connected to the D diode and C capacitor. If
OUT SW VIN
the grounds are split it is critical to have the ground connection point as close to the C and C
VIN OUT
capacitors as possible.