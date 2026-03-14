---
source: "TI SLLA486 -- Top Design Questions About Isolated CAN Bus Design"
url: "https://www.ti.com/document-viewer/lit/html/SLLA486"
format: "HTML"
method: "pdfplumber"
extracted: 2026-02-16
chars: 25664
---

Application Note
Top Design Questions About Isolated CAN Bus Design
Vikas Kumar Thawani
ABSTRACT
The controller area network (CAN) bus is a multi-master, message broadcast networking interface. It is
usually preferred over other differential wired interfaces in safety-critical applications because of the features
defined in its protocol such as priority based messaging, bitwise arbitration to handle bus contention and error
detection and recovery. Isolating a CAN port is a common design challenge encountered in many industrial
and automotive applications. TI’s integrated isolated CAN transceivers ISO1042, ISO1044, and ISOW1044 are
referenced throughout this article. The following is a compilation of the most frequently asked questions about
isolating CAN nodes.
Table of Contents
1 When Do I Need to Isolate CAN?...........................................................................................................................................2
2 What are the Options Available to Isolate CAN Bus?.........................................................................................................2
3 Now That I Have Isolated CAN Signal Path, How Do I Generate Isolated Power?............................................................3
4 What’s the Reason Behind Terminating the Bus, Do I Need it, and How to Achieve it?..................................................5
5 What’s the Difference Between Common Mode Range and Bus Standoff Mentioned in Data Sheet?...........................6
6 Now That I Have Taken Care of the Termination Resistor, What Other Components do I Need on the Bus Side?.......6
7 When Connecting Isolated CAN Nodes in a Network, What Should be Done with the Floating Bus-Side
Ground Connection?.............................................................................................................................................................6
8 Is There a Limitation on Minimum Data Rate That I Can Operate? What About the Maximum Data Rate
Achievable in a Network?......................................................................................................................................................6
9 Is There a Limit on Maximum Number of Nodes That I Can Connect in CAN Network?.................................................7
10 What Factors Decide the Maximum Communication Distance in a CAN Network?.......................................................7
11 What is the Maximum Value of Bus Capacitance That Can be Introduced Between CANH to GND and CANL
to GND? Can Higher Capacitance Damage the Device?....................................................................................................8
12 Is There a Way to Extend the Maximum Communication Distance?...............................................................................8
13 What is Stub Length? What are the Design Considerations Around it?.........................................................................9
14 I am Seeing Larger Differential CAN Voltage for Some Bits of CAN Packet Compared to Rest of the Packet
When I am Communicating in a Network with Multiple Nodes Connected. Why?.........................................................10
15 References...........................................................................................................................................................................11
16 Revision History.................................................................................................................................................................12

1 When Do I Need to Isolate CAN?
The CAN standard ISO11898-2(2016) requires ±12 V common mode voltage range support for a compliant CAN
transceiver. This means a CAN receiver needs to tolerate up to ±12 V common mode voltage on CAN lines
with respect to bus-side ground and still be able to faithfully replicate differential voltage transitions on the bus.
There are CAN transceivers available from TI, such as TCAN1042, which support an extended common mode
range of up to ±30 V. When the communicating nodes in a CAN network have larger ground potential differences
(GPDs), which are higher than the supported common mode voltage range of the transceiver, due to longer
communication distance or system ground being noisy (such as in motor drive applications), isolating the CAN
node becomes necessary. The isolation barrier also acts as high impedance to common mode noise transients
(such as ESD/EFT/Surge) that are common in industrial environments. Proper design in some application
scenarios can enable system designers to drop all common mode noise across the isolation barrier, thereby
eliminating some external components commonly seen on CAN bus. For more details, please refer to: How to
use isolation to improve ESD, EFT and surge immunity in industrial systems.
2 What are the Options Available to Isolate CAN Bus?
Isolation of CAN bus is accomplished by placing an isolation barrier at digital logic interface between the
MCU and CAN transceiver. System designers use either discrete or integrated solutions for isolating CAN bus.
Discrete solution can be implemented using a digital Isolator such as ISO7721, and a CAN transceiver. The CAN
standard places strict timing requirements on total loop delay and on pulse width distortion for FD data rates (2
Mbps and 5 Mbps). Discrete solutions will need to account for PCB parasitics that exist in the signal path which
can impact timing, to ensure they are compliant to the CAN standard since timing is critical for bit-wise arbitration
and signal integrity. Integrated isolated CAN devices such as ISO1042, ISO1044, and ISOW1044, other than
providing board space savings, have these timing specifications guaranteed in the data sheet, eliminating extra
simulations and tests needed for discrete solutions. Figure 2-1 shows this concept using ISO1044.
VCC1 1
VCC1 VCC2
8 VCC2
VDD 2 CANH 6
TXD TXD
ISO1044 CANL 5 CAN Bus
MCU
3
RXD RXD
DGND
4 GND2 7
GND1
Digital Galvanic ISO
Ground Isolation Barrier Ground
Figure 2-1. Integrated Ultra-Small Package Isolated CAN Device ISO1044
2 Top Design Questions About Isolated CAN Bus Design SLLA486B – MAY 2020 – REVISED OCTOBER 2024

3 Now That I Have Isolated CAN Signal Path, How Do I Generate Isolated Power?
Multiple options are available for isolated power generation for a CAN node. If the field side (for example, bus
side) circuitry needs more power than just powering the CAN transceiver, push-pull transformer drivers like
TI’s SN6505B driving an external transformer is a simple-to-use and low cost solution as shown in Figure 3-1.
For space-constrained applications the ISOW1044 provides signal isolation, DC/DC converter, and a CAN FD
transceiver in a single chip to reduce solution size and simplify the design process, as shown in Figure 3-2.
Sometimes in certain industrial applications, such as DeviceNet, a 24-V supply is available on the field side
which can be used as shown in Figure 3-3. To learn more on this topic, read the application brief, How to Isolate
Signal and Power in Isolated CAN Systems
4 8 1 5
GND D2 IN OUT
SN6505 3 7 EN
3.3 V EN VCC 2 6 TPS76350
2 4
GND NC
1 5
CLK D1
3.3 V 1 8 5 V
100 nF 100 nF
VDD 2 GND2 7
TXD TXD ISO
MCU 3 ISO1044 Ground
RXD RXD CANH 6
DGND Optional bus
protection
4 CANL 5 circuitry
Digital Galvanic
Ground Isolation Barrier
Figure 3-1. Isolated Power Generation Using Push-Pull Topology
1 20
5 V
9
VIO VISOIN
VDD VISOOUT 12,13
VDD TXD 3 TXD CANH 19
MCU ISOW1044 18
RXD 5 RXD CANL Optional Bus
DGND 6,10 GND1 GND2 11,15,16,17 Protection Function
ISO
Ground
Figure 3-2. Isolated Signal and Power Using Small Form-Factor ISOW1044

VCC1
ISO1042
VDD 1 VCC1 VCC2 8 VCC2 = 5 V VOUT LDO VIN 24 V
GND
2 7 CANH
TXD TXD CANH
MCU 3 6 CANL
RXD RXD CANL
DGND
5 24RET
4 GND1 GND2
Digital ISO Ground
Ground
VCC1 24 V
Isolated
DC-DC
24RET
Figure 3-3. DeviceNet Application Schematic
4 Top Design Questions About Isolated CAN Bus Design SLLA486B – MAY 2020 – REVISED OCTOBER 2024

4 What’s the Reason Behind Terminating the Bus, Do I Need it, and How to Achieve it?
The ISO11898 standard specifies the network interconnect medium to be a single twisted pair cable (shielded
or unshielded) with 120-Ω characteristic impedance (Z ). Resistors equal to the characteristic impedance of
O
the line should be used to terminate both ends of the cable to prevent signal reflections. Termination resistors
should be placed at the two extreme ends of the network as shown in Figure 4-1. Another reason of CAN bus
needing a termination for proper functionality (unlike another industrial interface, RS-485, where termination is
optional) is that the dominant-to-recessive signal edge is not actively driven, so the RC decay of the bus brings
that transition. If no termination is present on the bus, the dominant-to recessive transition may be missed if the
TXD input is continuously changing, resulting in data loss.
For the networks where new nodes will continually be added, and if there is a requirement to keep hardware
design of nodes similar, software-controlled termination is a good design option as shown in Figure 4-2. An opto-
emulator (ISOM8610) or optoMOS (photorelay) circuit can be added to each node design. Through software, the
design can enable or disable termination across CANH-CANL by driving TERM through a GPIO of the MCU. So
the two farthest end nodes in the network can drive TERM=High to enable termination of 120 ohm across the
bus, while all other nodes can drive TERM=Low. This way the CAN bus effective termination is 60 ohm (120
ohm on both ends in parallel); while the hardware design of each node can be the same.
Node 1 Node 2 Node 3 Node n
(with termination)
MCU or DSP MCU or DSP MCU or DSP MCU or DSP
CAN CAN CAN CAN
Controller Controller Controller Controller
CAN CAN CAN CAN
Transceiver Transceiver Transceiver Transceiver
RTERM
RTERM
Figure 4-1. Typical CAN bus Network
2 CANH 6
TXD TXD ISO1044 CANL 5 CAN Bus
4 GND2 7
Digital ISO 120 Ω
Ground Ground
ISOM8610
TERM 1 4
2 3
Figure 4-2. Software-Controlled Termination Using ISOM8610

5 What’s the Difference Between Common Mode Range and Bus Standoff Mentioned in
Data Sheet?
The CAN standard ISO11898-2(2016) defines common mode voltage range as the range of common mode
voltage present on CAN bus lines for which a CAN receiver is able to faithfully recover differential signals on the
bus and replicate them on RXD. ISO1044 and ISOW1044 have ±12 V common mode voltage range, whereas
ISO1042 has ±30 V, both mentioned in valid operating conditions. This voltage range is with respect to bus side
ground, for example, GND2. Bus standoff, also known as bus short circuit voltage or bus fault protection, is
specified in the absolute maximum ratings table. For ISO1042, it is ±70 V whereas for ISO1044 and ISOW1044
it is ±58 V. This means under temporary fault conditions of say 12-V/24-V/48-V supply voltage shorting to the
CAN bus, both devices will withstand that short condition and not get damaged.
6 Now That I Have Taken Care of the Termination Resistor, What Other Components do
I Need on the Bus Side?
ISO1042, ISO1044, and ISOW1044 have integrated ±8 kV IEC ESD protection (per 61000-4-2) on the bus
side, which is tested with no other components present on the bus. Sometimes, system designers use common-
mode-chokes (CMCs) to reduce Emissions to meet requirements such as CISPR32, or to improve Immunity
performance to meet Electrical Fast Transients per IEC61000-4-4. The CMC attenuates the common mode
signal going into the device or coming out of it. Split termination capacitor may also help in noisy-system
scenarios-this again helps in emissions reduction or immunity improvement.
A low value series resistors (~10 ohm) can be used on both CANH/CANL lines in case lightning surges (tested
per IEC61000-4-5) are expected on the cable to reduce the current that flows to internal clamping structures of
the device during surge events. These series resistor will attenuate differential signal as it forms a divider with
the 60 ohm loading on the bus. Final components on the bus are very system specific and the end equipment
should be tested to fully confirm which components are needed in the its design. Please refer to the TI design
Isolated CAN Module With Integrated Power Reference Design that implements these design considerations and
shows practical lab-tested results.
7 When Connecting Isolated CAN Nodes in a Network, What Should be Done with the
Floating Bus-Side Ground Connection?
Since CAN is a differential interface, the entire network will work fine if just two wires for CANH/CANL are
interconnected between all nodes of a network, as long as common mode voltage of CAN lines with respect
to bus-side ground of the receiving CAN node is within its recommended operating conditions. However, under
noisy-system scenarios, best practice is to use a third ground reference line and connect it between all nodes.
This way, receiver of each CAN node has a reference, and common mode voltage range will not be violated. If
the cable is shielded, the shield can act as a common ground reference with shield connected to earth potential
at just one node to avoid any ground loops. Proper system design can ensure large common mode voltages
induced on the CAN bus (due to noise pickup) drop across the isolation barrier by connecting the logic-side
ground of the isolated CAN transceiver to local ground.
8 Is There a Limitation on Minimum Data Rate That I Can Operate? What About the
Maximum Data Rate Achievable in a Network?
Most isolated or non-isolated CAN transceivers have a protection feature called Dominant-Timeout (DTO). This
feature disables the transmitter of a device if it holds the bus dominant for a time greater than DTO. This feature
is useful in case of a software failure or a hardware failure that makes TXD low continuously. The CAN protocol
does not allow transmission of more than 5 bits of same state in a row due to bit stuffing rules except in error
condition. So in an error scenario, 5 dominant bits followed by 6 consecutive dominant bits of error frame needs
to be transmitted. Hence, 11*bit time of one dominant bit <= DTO time. This decides minimum data rate (or
maximum one bit dominant time period).
Though ISO1042, ISO1044, and ISOW1044 are able to support a maximum 5 Mbps data rate, the actual
maximum achievable in a network is dependent on maximum cable length (for example, distance between
farthest nodes), type of cable (which will decide signal speed in the interconnect medium), and total capacitance
that exists across the CAN bus due to cable, individual nodes, PCB traces, connectors, and so forth. Bitwise
arbitration is the key to CAN protocol. This means during arbitration phase of CAN packet, a bit sent by a
6 Top Design Questions About Isolated CAN Bus Design SLLA486B – MAY 2020 – REVISED OCTOBER 2024

transmitter needs to reach the farthest receiver and back to the transmitter which monitors via RXD for it to move
to the subsequent bit in the CAN-ID part of a data packet. So the fastest bit time in arbitration phase has to be
more than the loop delay of a transmitter node + 2*prop delay of cable (typically 5 ns/meter of CAT5e cable).
This indicates there is an inverse relationship between maximum data rate in arbitration period and maximum
communication distance. The maximum data rate during data-phase of CAN packet would be limited by the bit
timing distortion introduced by the transceiver and by the controller's sampling point margin. Overall capacitance
seen on the bus also impacts timing as dominant to recessive edge transitions may be elongated if a higher
capacitance is seen on the bus.
9 Is There a Limit on Maximum Number of Nodes That I Can Connect in CAN Network?
Each node presents a certain differential load across the CAN bus which is specified as R (differential
ID
input resistance) in the Receiver Electrical Characteristics section of the device data sheet. For ISO1044 and
ISOW1044 is specified at minimum of 40 kohm. Other than the two 120 ohm termination resistors on far ends of
the network, each node’s differential resistance combines in parallel to load the transmitter that is about to drive
dominant on the bus. The equivalent parallel resistance that a driver should see needs to be more than 45 ohm
because 45 ohm is the minimum load a driver is specified to drive and produce a minimum differential voltage of
1.4 V (as specified in Driver Electrical Characteristics). So in the case of ISO1044 and ISOW1044, if we connect
222 nodes on the bus, the equivalent differential resistance all CAN nodes offer on the bus is 40000/222 = 180
ohm. This 180 ohm in parallel to two 120 ohm termination resistors gives a 45 ohm equivalent loading on the
driver. This is the theoretical limit on the maximum number of nodes on a CAN bus. Practical system aspects will
limit this further.
10 What Factors Decide the Maximum Communication Distance in a CAN Network?
Several factors that impact maximum communication distance in a CAN network are:
1. I*R drop of cable due to DC resistance will attenuate the signal as it reaches the farthest receiver. The
minimum possible dominant signal at farthest receiver needs to be more than 900 mV (based on receiver
threshold) for it to be recognized as valid dominant.
2. As cable length is increased, capacitive load on the CAN bus increases which impacts dominant to recessive
edge transition time which in turn is tied to minimum possible bit period (for example, maximum data rate).
3. As explained in Section 8, during arbitration, a bit from the transmitter needs to reach the farthest receiver.
So the maximum communication distance is closely dependent on the inverse of maximum data rate needed
for end application. A conservative rule of thumb for bus lengths over 100 meters is derived from the product
of the signaling rate in Mbps and the bus length in meters, which should be less than or equal to 50.
Signaling Rate (Mbps) x Bus Length (m) <= 50

What is the Maximum Value of Bus Capacitance That Can be Introduced Between CANH to GND and CANL to

11 What is the Maximum Value of Bus Capacitance That Can be Introduced Between
CANH to GND and CANL to GND? Can Higher Capacitance Damage the Device?
CANH to GND or CANL to GND capacitance will eventually end up as differential capacitance across CAN bus.
C1
CANH
C(effective) = (C1*C2)
CANL (C1 + C2)
C2
Figure 11-1. CAN Bus Capacitance
Isolated CAN data sheet gives rise/fall times with 100 pF bus capacitance, but if differential capacitance is
increased, driver rise and fall times will slow down eating up the timing budget. Various components will
contribute to this capacitance:
• External protection components such as CMC, TVS etc
• Cable (typical CAT5 cable can offer 50 pF/meter mutual capacitance)
• Connector
• Number of nodes on bus (each node will offer certain differential capacitance) across the bus
Recessive to dominant edge will depend on the driver to charge up this differential bus capacitance. Usually this
process will be faster given an active current source is charging up this capacitance. On dominant to recessive
edge, driver is turned off, so this transition will happen due to RC decay of the network. Here R is the effective
differential resistance, say 60 ohm (two terminations in parallel). C is the effective differential capacitance of the
network (which is the sum of all 4 components that were stated above as all are in parallel).
Say L is total cable length in meter, N is number of nodes each offering C differential capacitance per selected
ID
ISOCAN data sheet (ignoring external CMC / TVS, and connector capacitance just for simplicity here):
C(effective)={L×50} + {N×Cid} pF (1)
• RC time constant will decay the dominant to recessive edge. This should complete going below 500 mV
(recessive lower going threshold of CAN receiver: V ) just before 75% of bit width (assuming CAN controller
IT
is sampling around this time)
• Assuming T is minimum bit period (corresponding to max data rate of the application)
Entering values in Equation 2.
3×R×C <=0.75× Bit time(T) (2)
From previous equation, maximum bus capacitance that can be introduced across the bus, C can be
max
calculated. CANH to GND and CANL to GND can be double this value. This is the theoretical maximum.
Components ignored will also impact. Our recommendation to the customer is to thoroughly test for any bit
errors in their system.
12 Is There a Way to Extend the Maximum Communication Distance?
The easiest method is to reduce the data rate to allow more time for signals to reach the farthest node. For a
particular data rate required for an application, one way to extend the maximum communication distance is by
installing a CAN repeater in series to overcome attenuation of signal caused by I*R drop of cable DC resistance.
CAN repeater takes signal from CAN bus and replicates it on the other side of bus with higher signal swing.
Another advantage of a repeater is that it allows for additional terminations to be used without overloading a
single bus segment, which can be useful in operating with non-linear topologies. For more details, refer to the
Isolated CAN Flexible Data (FD) Rate Repeater reference design.
8 Top Design Questions About Isolated CAN Bus Design SLLA486B – MAY 2020 – REVISED OCTOBER 2024

13 What is Stub Length? What are the Design Considerations Around it?
A stub is the electrical length of cable between a node’s terminal and connection to the CAN bus as shown in
Figure 13-1. Since stub-lines are unterminated, signal reflections can develop in a stub that drives signal levels
back and forth across a receiver's input thresholds, creating errors.
The ISO 11898-2 Standard specifies a maximum bus length of 40 meters, max speed of 1 Mbps, and maximum
stub length of 0.3 meters. However with careful design, stub lengths can be longer. Below is a conservative
rule of thumb to calculate maximum stub length with the idea that signal reflection due to a stub remains during
transition time itself and dies down later. Designs with longer stubs than this may be possible with slower data
rates and if the signal quality is acceptable in the network. We recommend system designers perform thorough
testing with their network design to arrive at a conclusion.
Figure 13-1. CAN Network Showing Stubs
2*propagation delay of signal in stub <= (1/3)* Rise or fall time of transceiver (3)
For ISO1044: Fall time= 40 ns typical, say if x is stub length in meters, signal travels at 5 ns/meter in twisted pair
cable.
Putting values in Equation 3, 2*x*5 ns/m <= (1/3)*40
x<= 1.33 meters.

I am Seeing Larger Differential CAN Voltage for Some Bits of CAN Packet Compared to Rest of the Packet

14 I am Seeing Larger Differential CAN Voltage for Some Bits of CAN Packet Compared
to Rest of the Packet When I am Communicating in a Network with Multiple Nodes
Connected. Why?
Figure 14-1. Differential CAN Bus Voltage Showing Higher Voltage on Some Bits
The CAN packet (shown in Figure 14-2) is made up of ID bits at the start of packet which are used for bitwise
arbitration to determine the priority over which node will continue transmission and which other node(s) will
stop. Also, towards the end of packet, ACK is acknowledgment bit which is driven dominant by all nodes which
correctly receive the packet. So when multiple nodes on bus drive dominant at the same time, the differential
voltage is higher in amplitude as opposed to other bits which are just driven by master transmitter node. Figure
14-3 shows a snapshot of CAN bus traffic with three nodes communicating, where we can clearly see larger
voltage magnitude on CAN bus. These time instances are during acknowledgment bit or when B and C are
transmitting together during ID phase.
Figure 14-2. CAN Packet: See ID Bits at Start of the Frame and ACK Near End of the Frame
2 CANH 6
TXD TXD ISO1044 CANL 5 CAN Bus
DGND 4 GND2 7
G D r i o g u it n a d l Isol G at a io lv n a B n a ic rrier Gr IS ou O n d 120 Ÿ
TERM
Figure 14-3. CAN Bus Waveforms Describing Why Some Bits are Larger in Magnitude
10 Top Design Questions About Isolated CAN Bus Design SLLA486B – MAY 2020 – REVISED OCTOBER 2024

15 References
• Texas Instruments, ISO1044 data sheet
• Texas Instruments, Controller Area Network Physical Layer Requirements

16 Revision History
Changes from Revision A (May 2021) to Revision B (October 2024) Page
• Updated the numbering format for tables, figures, and cross-references throughout the document.................1
• Added opto-emulator and ISOM8610 references where opto-coupler is used throughout the document..........1
• Changed Software-Controlled Termination Using ISOM8610 image to include ISOM8610...............................5
• Changed equation 2 to 3×R×C <=0.75× Bit time(T) ..........................................................................................8
Changes from Revision * (May 2020) to Revision A (May 2021) Page
• Added ISOW1044 throughout document............................................................................................................2
• Updated Isolation Signal and Power Using Small form-Factor ISOW8721 image.............................................3
12 Top Design Questions About Isolated CAN Bus Design SLLA486B – MAY 2020 – REVISED OCTOBER 2024