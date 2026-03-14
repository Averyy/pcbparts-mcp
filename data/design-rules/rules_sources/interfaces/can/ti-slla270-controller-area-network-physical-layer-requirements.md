---
source: "TI SLLA270 -- Controller Area Network Physical Layer Requirements"
url: "https://www.ti.com/lit/pdf/SLLA270"
format: "PDF 15pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 35021
---

Application Report

Controller Area Network Physical Layer Requirements
Steve Corrigan ................................................................................................ ICP - Industrial Interface
ABSTRACT
The multipoint bus structure and robust protocol of the High-Speed Controller Area
Network (CAN), ISO 11898:1993, is finding widespread use in building automation,
process control, and other industries. This paper provides the reader with the
fundamentals of CAN technology, then focuses on the physical layer requirements.
Contents
1 Introduction .......................................................................................... 2
2 Data-Flow Model.................................................................................... 3
3 Basic Bus Communication Requirements....................................................... 3
4 Physical Layer Requirements..................................................................... 4
4.1 Bus Length vs Signaling Rate ........................................................... 5
4.2 Cables....................................................................................... 6
4.3 Shield Termination......................................................................... 6
4.4 Grounding .................................................................................. 6
4.5 Line Terminations.......................................................................... 6
4.6 Connectors ................................................................................. 8
4.7 Filters/Chokes.............................................................................. 9
4.8 Stub Length and Loop Delays ........................................................... 9
4.9 Galvanic Isolation and Total Propagation Delay ..................................... 10
4.10 Physical Layer Variables (bit timing requirements).................................. 11
4.11 Node Differential Capacitance and Spacing.......................................... 11
4.12 Maximum Number of Nodes............................................................ 14
5 Conclusion ......................................................................................... 14
List of Figures
1 The Layered ISO 11898:1993 Standard Architecture ......................................... 2
2 The CAN Data-Flow Model........................................................................ 3
3 Standard CAN: 11-Bit Identifier .................................................................. 3
4 Extended CAN: 29-Bit Identifier .................................................................. 3
5 CAN Bus Traffic..................................................................................... 4
6 Details of a Typical CAN Node ................................................................... 5
7 Unterminated and Properly Terminated Bus Signals .......................................... 7
8 Standard Termination .............................................................................. 7
9 ISO 11898 Termination – Single or Split Termination ......................................... 7
10 Split Termination.................................................................................... 8
11 CANopen DSUB Connector....................................................................... 8
12 5-Pin Mini-Connector (ANSI/B.93.55M-1981)................................................... 9
13 Coupled Noise ...................................................................................... 9
14 Propagation Delay Timing Budget .............................................................. 10
15 Partitioning of the Bit Timing Segments........................................................ 11
16 CAN Bus Schematic Diagram ................................................................... 11
17 Minimum CAN Device Spacing on a Bus With Device Capacitance and Media
TMS320F2812 is a trademark of Texas Instruments.

Introduction
Capacitance........................................................................................ 13
List of Tables
1 Suggested Cable Length vs Signaling Rate .................................................... 5
1 Introduction
Aside from CAN’s high reliability, the main advantage of CAN over alternative networks is the low
development cost. CAN controller and interface cost are as low as legacy data transmission products and
are available off-the-shelf from leading semiconductor manufacturers. There are many CAN-related
system development packages, hardware interface cards, and software packages that provide system
designers with a wide range of design and diagnostic tools. These components provide for the
development of complex control applications without having to build each node of a system network.
DSP
or
Application Layer
m Controller
Logic Link Control
Data-Link Embedded † CAN
controller,
Layer
Medium Access Control CAN embedded or
separate
Controller
Physical Signaling
Physical
Layer Physical Medium Attachment † Electrical
CAN specifications:
transceivers,
Transceiver
Medium Dependant Interface connectors, cable
CAN BusLine
Figure 1. The Layered ISO 11898:1993 Standard Architecture
Figure 1 displays the ISO 11898 standard architecture using the bottom two layers of the OSI model, the
Data-Link Layer and the Physical Layer.
The Data-Link Layer is responsible for transferring messages from a node to the network without errors.
It handles bit stuffing and checksums, and after sending a message, waits for acknowledgment from the
receivers.
The Physical Layer is the basic hardware required for a CAN network, i.e. the ISO 11898 electrical
specifications. It converts 1’s and 0’s into electrical pulses leaving a node, then back again for a CAN
message entering a node. Although the other layers may be implemented in software or in hardware as a
chip function, the Physical Layer is always implemented in hardware.
In the Figure 1 model, the Application Layer provides the upper-level communication functions of the OSI
layered model. These functions may be implemented by a system software developer or handled by a
higher-layer protocol such as the vendor-independent CANopen protocol.

Data-Flow Model
2 Data-Flow Model
CAN CAN CAN RECEIVE-ONLY
NODE 1 NODE 2 NODE 3 NODE n
LOCAL LOCAL LOCAL LOCAL
INTELLIGENCE INTELLIGENCE INTELLIGENCE INTELLIGENCE
DATA FILTER DATA FILTER DATA FILTER DATA FILTER
Figure 2. The CAN Data-Flow Model
Since CAN is a broadcast system, a transmitting node places data on the network for all nodes to access.
As shown in Figure 2, only those nodes requiring updated data allow the message to pass through a filter
that is set by the network designer – i.e., messages from certain nodes can pass, and all others are
ignored. If this filter is not used by a system designer, much of a node's m C processing time is spent
sorting through messages that are not needed.
Every message begins with the 11-bit or 29-bit identifier shown in Figure 3 and Figure 4, that a system
designer can use to identify the content of a message, such as temperature or shaft position. In this way,
a designer can prioritize messages. For instance, an automotive message with brake information is given
a higher priority identifier than a turn-signal identifier. This priority is discussed in the next section.
S R II EEE I
11- bit
O T DD rr00 DDLLCC 0…8Bytes Data CCRRCC ACK OOO F
I dentifier
F R EE FFF S
Figure 3. Standard CAN: 11-Bit Identifier
S 11-bit S I 18-bit R EEE I
O R D T r 1 r 0 DL C 0…8 Bytes Data C R C AC K OOO F
F I dentifier R E Identifier R FFF S
Figure 4. Extended CAN: 29-Bit Identifier
CAN's multiple reception provides for the concept of modular electronics and the synchronization of
distributed control processes: data needed by several nodes is broadcast on the network in such a way
that it becomes unnecessary for a node to know origin of the data. This allows for easy servicing and
upgrading networks since data transmission is not dependant upon the availability of a specific type of
node.
System flexibility is achieved as a result of the content-oriented addressing scheme. This enables the
reconfiguration of an existing CAN network without making any hardware or software modifications. A new
node may be added that only receives operating data from the other transmitting nodes in a system, and
never sends data.
3 Basic Bus Communication Requirements
Note that a minimum of two nodes must be used to initialize communication on a CAN bus. Since a
transmitted message must be acknowledged in the ACK bit by a receiver, the transmitting controller will
send out an error flag if the message is not properly ACKed.

Physical Layer Requirements
All nodes on a bus participate in each bit – as it is being written. The device sending a message is also
receiving that message itself – checking each bit as it is written. In this way, the second node fills in the
ACK bit while the bit is still being transmitted by the first node. This is why it takes two nodes to complete
a message transmission. This function is best displayed during the arbitration shown in Figure 5. The
nodes of Figure 5 could theoretically be sending messages from a sensing circuit and motor controller.
An actual application may include a temperature sensor sending out a temperature update that is used to
adjust the motor speed of a fan. If a pressure sensor node wants to send a message at the same time, the
arbitration in Figure 5 assures that the message will be sent. On the left side of the scope Node A finishes
sending its message as Nodes B and C fill in the ACK bit indicating that a message is received without
errors. After the mandatory inter-frame space between messages, Nodes B and C then begin arbitration –
Node C wins the arbitration with the final dominant bit and sends its message. Nodes A and B then ACK
C's message. Node B then continues on with its uncontested arbitration and message which is ACKed by
Nodes A and C.
Note that if the ACK bit is missing, the transmitting controller will generate its own error flag. If a message
is not ACKed, an error is generated with each occurrence until the controller reaches an error limit that is
internally set by the CAN protocol. The controller places itself in a bus-off state when this internal limit is
reached. This is a protocol controller function that prevents a single node from blocking all communication
on a bus.
CAN
Bus
NODE
A
ACK bit
ACK bit
B
ACK bit Node C wins arbitration
C
Figure 5. CAN Bus Traffic
4 Physical Layer Requirements
The data link and physical signaling layers of Figure 1, which are normally transparent to a system
operator, are included in any controller that implements the CAN protocol such as the Texas Instruments
TMS320F2812™ 3.3-V DSP with integrated CAN controller. Connection to the physical medium (the bus)
is then implemented through a line transceiver such as TI’s SN65HVD233 3.3-V CAN transceiver to form
a system node shown in Figure 6.

(Node #1) (Node #2) (Node #3) (Node #n)
DSP or µ C DSP or µ C DSP or µ C DSP or µ C
CAN CAN CAN CAN
Controller Controller Controller Controller
CAN CAN CAN CAN
Transceiver Transceiver Transceiver Transceiver
CANH
R L CAN Bus-Line R L
CANL
Figure 6. Details of a Typical CAN Node
The High-Speed ISO 11898 Standard specifications are given for a maximum signaling rate of 1 Mbps
with a bus length of 40 m and a maximum of 30 nodes. It also recommends a maximum un-terminated
stub length of 0.3 m. The cable is specified to be a shielded or unshielded twisted-pair with a 120-W
characteristic impedance (Z ). The Standard defines a single line of twisted-pair cable with the network
O
topology as shown in Figure 6. It is terminated at both ends with 120-W resistors, which match the
characteristic impedance of the line to prevent signal reflections. According to ISO 11898, placing R on a
L
node should be avoided since the bus lines lose termination if the node is disconnected from the bus.
4.1 Bus Length vs Signaling Rate
Table 1. Suggested Cable Length vs Signaling Rate
Bus Length Signaling Rate
(m) (Mbps)
40 1
100 0.5
200 0.25
500 0.10
1000 0.05
Basically, the maximum bus length is determined by, or rather is a trade-off with the selected signaling
rate as listed in Table 1.
A signaling rate decreases as transmission distance increases. While steady-state losses may become a
factor at the longest transmission distances, the major factors limiting signaling rate as distance is
increased are time varying. Cable bandwidth limitations, which degrade the signal transition time and
introduce inter-symbol interference (ISI), are primary factors reducing the achievable signaling rate when
transmission distance is increased.
For a CAN bus, the signaling rate is also determined from the total system delay – down and back
between the two most distant nodes of a system and the sum of the delays into and out of the nodes on a
bus with the typical 5ns/m prop delay of a twisted-pair cable. Also, consideration must be given the signal
amplitude loss due to resistance of the cable and the input resistance of the transceivers. Under strict
analysis, skin effects, proximity to other circuitry, dielectric loss, and radiation loss effects all act to
influence the primary line parameters and degrade the signal.
A conservative rule of thumb for bus lengths over 100 m is derived from the product of the signaling rate
in Mbps and the bus length in meters, which should be less than or equal to 50.
Signaling Rate (Mbps) · Bus Length (m) £ 50

If a 1000 m bus is required by an application, then by this approximation a 50 kbps signaling rate may
safely be used. Lab experiments show that an actual safe signaling rate with 1000 m of 120-W
characteristic impedance twisted-pair cable is indeed approximately 50 kbps. By providing this extra
margin of safety, a lot of system variation can still take place without disruptions in communication.
A long cable length with a higher number of nodes than the Standard’s recommended 30 nodes may
require the use of higher cable quality, a CAN bus repeater, and tighter operating tolerances such as a 5%
voltage supply regulation. In practice, however, almost any type of cable works to a certain degree, even a
cheap phone line for short distances.
4.2 Cables
Although unshielded 120-W cable is used in many applications, data transmission circuits employing CAN
transceivers are used for jobs requiring a rugged interconnection with a wide common-mode voltage
range. Therefore, shielded cable such as Belden Cable 3105A is recommended in these electronically
harsh environments. Shielded cable and the Standard’s –2 V to 7 V common-mode range of tolerable
ground off-set, help to ensure data integrity. Note that the HVD1050 CAN transceiver has an extended
common-mode range of –12 V to 12 V.
While prefabricated cables for CAN applications are more expensive, they are more easily installed and
verified, and may, therefore, reduce overall installation cost and time-to-market.
4.3 Shield Termination
If a shield must be used, it is recommended that a short pig-tail be crimped to the shield end at each
connector and then brought through a separate connector pin to a ground pin located as close to the
connector as possible. Note that the network should be grounded at a single point at the source location.
This prevents parasitic currents from flowing in the shield between ground connections.
If individual shielding of the signal pairs is used, use the same terminating technique as for the overall
shield.
4.4 Grounding
There should be only one path for return current between the host and receiving nodes. This follows the
same discussion in the shielding section. If a network is grounded in more than one location, parasitic
current will flow. By grounding a network only at the source, potentially hazardous ground loops are
avoided. The use of digital isolators such as the ISO721 (SLLS629) is recommended if it becomes
necessary to connect the grounds of different sources.
Unused pins in connectors as well as unused wires in cables should be single-point grounded at the
connector. Unused wires should be grounded at alternate ends to nearby ground pins.
4.5 Line Terminations
The 120-W characteristic impedance twisted-pair cable is terminated with an impedance of the same value
to minimized reflected waves that occur from miss-matched impedances. Figure 7 is an example of the
reflected waves that build up on a signal when termination is removed.

Figure 7. Unterminated and Properly Terminated Bus Signals
Each step in the signal is a reflected wave adding to the original signal across 1 meter of unterminated
twisted-pair cable. The length of each of the steps is approximately 10 ns, the typical down-and-back
propagation delay per meter of cable. The signal continues to build in magnitude until the supply voltage is
reached.
Two different termination models are recommended for high-speed CAN as shown in Figure 8 and
Figure 9. The traditional 120 W R on each end of the bus, or the split termination using two 60 W , R /2
L L
resistors and a coupling capacitor C . These are often used to filter high frequency components on the
bus.
4.5.1 Standard Termination
120 W Stub 120 W
CAN CAN CAN
Transceiver Transceiver Transceiver
Figure 8. Standard Termination
Care must be taken to allow for short-circuits to power supplies when selecting appropriately rated
termination resistors. While 1/4 W 5% tolerance resistors are generally acceptable, a bus-line short-circuit
to a 24 V supply line would generate a transceiver’s I short-circuit output current multiplied by the supply
OS
voltage. The 1/4 W resistor would blow up in this circumstance.
4.5.2 Split Termination
CANH CANH
R L
2 OPTIONAL
VREF
RL C L R L
2
Figure 9. ISO 11898 Termination – Single or Split Termination

Note that transceivers such as the SN65HVD1050 have a V or V pin shown in Figure 9 that is
ref split
specifically designed to stabilize the common-mode bus voltage during communication (this also helps
reduce radiated emissions). The HVD1050’s Vref pin has the same wide common-mode operating range
and ESD protection as the bus pins.
node 1 node 2 node n
60 W 60 W
60 W 60 W
CL CANL CL
1
Low- pass filter with fc =
2
p
RC L
Figure 10. Split Termination
Unwanted high frequency noise is filtered from bus lines with the split termination of Figure 10. This is
accomplished with coupling capacitor between two ~60 W – 1% termination resistors to couple high
frequency noise to a solid ground potential. Care must be taken to match the two resistors carefully so as
to not reduce the effective immunity. This technique improves the electromagnetic compatibility of a
network. A typical value of C for a high-speed CAN is 4.7 nF, which generates a 3 dB point at 1.1 Mbps.
This, of course is a signaling rate dependant value.
4.6 Connectors
Connectors, while not specified by the Standard, should have a characteristic impedance matching that of
the bus line and terminators, and it should not affect standard operating parameters such as the minimum
V .
OD
The higher layer protocols such as CANopen and DeviceNet define the specific hardware required for
implementation, including bus wire and connectors. Recommended products may be found on
organization web-sites such as the CiA’s CAN-cia.com which list connector and pin-out specifications for
use in CANopen applications. These include the 9-pin DSUB shown in Figure 11, Multipole, RJ10, RJ45,
M12, the 5-pin mini-style in Figure 12 and more micro-style connectors in the CiA specification document
DR 303-1, V1-3.
Pin Description
1 Reserved
2 CANL CANL bus pin
3 V+ Optional 3.3-V or 5-V power supply for
transceivers and digital isolators if required
4 Reserved
5 CAN_SHLD Optional shield
6 V- Ground return path/ 0V
7 CANH CANH bus pin
8 Reserved
9 V+ Optional 3.3-V or 5-V power supply for
transceivers and digital isolators if required
Figure 11. CANopen DSUB Connector

Pin Description
3 3
1 CAN_SHLD Optional shield
4 2 2 4
2 V+ Optional 3.3-V or 5-V power supply
for transceivers and digital isolators
5 1 1 5
if required
3 V- Ground return path/ 0V
4 CANH CANH bus pin
Male Female
5 CANL CANL bus pin
Figure 12. 5-Pin Mini-Connector (ANSI/B.93.55M-1981)
4.7 Filters/Chokes
Bus-lines and a ground plane can form a loop for inductively coupled noise signals and depending upon
the topology, a bus can easily become an antenna for local noise.
Figure 13. Coupled Noise
The cables used in Figure 13 are different lengths of unshielded twisted-pair 24 AWG copper wire and the
figure clearly displays the inducted noise from nearby florescent lighting. Properly filtered, these would be
four noise-free straight lines. Induced voltages of 10 V or more are commonly found on industrial buses.
Chokes such as the ZJYS81RS-2PL51(T)-G01 have been developed by TDK specifically to address this
problem in CAN applications.
4.8 Stub Length and Loop Delays
Since stub-lines are unterminated, signal reflections can develop in a stub that drive signal levels back
and forth across a receiver's input thresholds, creating errors. Bit-sampling occurs near the end of a bit, so
it is mandatory that all signal reflections in a CAN stub-line be attenuated before or during the propagation
delay segment in Figure 15 to provide an adequate margin of safety.
To minimized reflections, stub-line length should not exceed one-third (1/3) of the line's critical length.
Beyond this stub-length, many variables come into play since the stub is no longer considered to be a
lumped parameter. This is the maximum length that a stub remains invisible to a transmission line.
The critical length of a bus line occurs at the point where the down-and-back propagation delay
(tprop(total)) of a signal through a line equals the transition time(t ) of a signal (the greater of the rise or fall
t
times).
Network Critical Length = t = tprop(total)
t
Therefore, a typical CAN driver may have a 50 ns transition time, and when considering a typical
twisted-pair transmission line prop delay of 5 ns/m, the down-and-back delay for one meter becomes
10ns/m. The critical length becomes 5 m (50 ns / 10ns/m = 5 m), and the max un-terminated stub length
for the network is 1/3rd of the critical length, or 5/3 m (1.67 m).

When critical length is taken into consideration, driver slew-rate control becomes a valuable design asset.
The Standard recommends a maximum un-terminated stub length of 0.3 m with a 1 Mbps signaling rate,
but with slew rate control, reduced signaling rate, and careful design, longer stub lengths are easily
obtained.
For example, if a 10 kW resistor is applied for slope-control at the Rs pin (pin 8) of the HVD230 CAN
transceiver, a 160 ns driver transition time increases the maximum stub length to 16/3 m or 5 1/3 meters.
4.9 Galvanic Isolation and Total Propagation Delay
If galvanic isolation is required on a network, it is necessary to compensate for signal propagation delays
on the bus line as well as through the electronic interface circuits of the bus nodes. The sum of the
propagation delay times of controllers, galvanic isolators, transceivers and bus lines has to be a small
fraction of the time of a single bit. A prop delay total must be calculated and depends on the selected
components: CAN controller (50 ns to 75 ns), digital isolator ( 17 ns for a TI isolator and up to 140 ns for
an optocoupler), transceiver (100 ns to 250 ns), and cable (about 5 ns/m).
These delays have to be carefully considered because a round trip has to be made back from the most
distant CAN controller on the bus while the bit is still being written by the sender. Remember that each
node actively participates in the writing of every bit, and then actively fills in the ACK slot if it is not the
source of the message.
A typical propagation delay budget is comprised of : a transmitted bit from Figure 14's Node #1's m C –
isolator delay, driver delay, 10 m bus delay, receiver delay, isolator delay, controller delay, isolator delay,
driver delay, bus delay, receiver delay, isolator delay – receive it back to #1's m C. The total is calculated
using 50 ns for the controller, 17 ns for the TI isolator, 100 ns for transceivers driver and 100 ns for the
transceiver’s receiver, then 5 ns per meter for the cable.
Most Distant Nodes
down & back
RL RL
Transceivers
Isolators
Node #1 Node #2 Node #3 mControllers Node #n
t = t + t + t + t + t + #n t down
BUDGET ISOLATOR TRANSCEIVER BUS_PROP TRANSCEIVER ISOLATOR CONTROLLER
t + t + t + t + t back
ISOLATOR TRANSCEIVER BUS_PROP TRANSCEIVER ISOLATOR
Figure 14. Propagation Delay Timing Budget
Therefore, in Figure 14, the total prop delay is: 1st transmit bit from m C – isolator delay (17 ns), driver
delay (100 ns), bus delay [10 m (5 ns/m)], receiver delay (100 ns), isolator delay (17 ns), controller delay
(50 ns), isolator delay (17 ns), driver delay (100 ns), bus delay [10 m (5 ns/m)], receiver delay (100 ns),
isolator delay (17 ns) = 618 ns. Once these delays are totaled, allowances for oscillator variations,
operating variables, etc must be accounted for before a signaling rate is selected, since the incident wave
of the first bit must be back to the sending node long before the bit is sampled as a dominant or recessive
bit.

4.10 Physical Layer Variables (bit timing requirements)
Each CAN bit is divided into the four segments in Figure 15, with a sample point typically located at the
75% point of a bit width. The first segment, the synchronization segment (SYNC_SEG), is the time that a
recessive to dominant transition is expected to occur. All the nodes on a bus synchronize on rising edges.
The second segment, the propagation time segment (PROP_SEG), is designed to compensate for the
physical delay times of the network. The third and fourth segments, both phase buffer segments
(PHASE_SEG1 and PHASE_SEG2), are used for resynchronization. The bit value is sampled immediately
following PHASE_SEG1.
Nominal Bit Length
(Unit Interval )
Sample Point
SYNC _SEG PROP _SEG PHASE _SEG 1 PHASE _SEG 2
Hard Compensates for SEG 1 may be lengthened
synchronization propagation or SEG 2 may be shortened
forces rising edge delays for resynchronization
in first segment
Figure 15. Partitioning of the Bit Timing Segments
4.11 Node Differential Capacitance and Spacing
The ISO-11898 CAN bus of Figure 16 is a distributed parameter circuit whose electrical characteristics
and responses are primarily defined by the distributed inductance and capacitance(1) along the physical
media. The media is defined here as the interconnecting cable or conducting paths, connectors,
terminators, and CAN devices added along the bus. The following analysis derives a guideline for the
amount of capacitance that can be added and its spacing on the bus while maintaining signal integrity.
For a good approximation, the characteristic transmission line impedance seen in any cut point in the
Z = L
unloaded CAN bus is defined by , where L is the inductance per unit length and C is the
capacitance per unit length. As capacitance is added to the bus with unequal spacing between nodes, in
the form of devices and their interconnection, the bus impedance is lowered to Z' and when the bus
impedance is lowered, an impedance mismatch occurs between an unloaded section and a loaded section
of the bus.
d
t = 0
S 1
VS 120 W Z O = 120 W Load Load Load Load 120 W
Figure 16. CAN Bus Schematic Diagram
(1) Capacitance here is defined as differential, which is approximately one-half of the single-ended capacitance.

The resulting worst-case problem occurs during a dominant-to-recessive transition in arbitration or an ACK
bit. When S1 switches at time zero from a dominant state to a recessive steady state, the CAN driver
differential output voltage, V , moves from the standard maximum 3 V signal on the bus to a 0 V recessive
S
state. As this signal wave propagates down the line and arrives at the loaded section of the bus in
Figure 14, the mismatch in impedance reflects voltage back towards the source.
With fast transfer rates and electrically long(2) media, it becomes essential to achieve a valid input voltage
level on the first signal transition from an output driver anywhere on the bus. This is called incident-wave
switching. If incident-wave conditions are not achieved, reflected-wave switching must be used.
Reflected-wave switching depends upon reflected energy occurring some time after the first transition
arrives to achieve a valid logic voltage level.
As the input signal wave arrives at this mismatch in impedance, an attenuation (or amplification) of the
signal will occur. The signal voltage at an impedance mismatch is V = V + V + V , where V is the
L1 L0 J1 R1 L0
initial dominant differential voltage, V is the input signal recessive differential voltage, and V is the
J1 R1
reflected differential voltage.
Z ¢ - Z
rL =
The voltage reflected back from the mismatch is V = r L · V where, Z ¢ + Z and is the coefficient
R1 J1
of reflection commonly used in transmission line analysis. The voltage equation can now be written as
V = V + V + r L · V .
L1 L0 J1 J1
Assuming the bus is terminated at both ends with the nominal media impedance, a CAN driver creates a
high-to-low differential voltage change from the standard maximum V of 3 V to 0 V, or a V of –3 V. The
LO J1
signal voltage at the load, V , must go below the receiver recessive bit input voltage threshold of 0.5 V.
L1
In equation form,
0.5 > 3 + (-3) + ρL× (-3)
0.5
ρL > = -0.167
-3 (1)
Now, solving for Z′
Z¢ - Z
ρL =
Z¢ + Z
0 >-0.167
0
Z¢ - Z >-0.167(Z¢ + Z )
0 0
Z¢ (1 + 0.167) > Z (1-0.167)
Z¢ >0.71 Z
0 (2)
If the loaded bus impedance is no less than 0.71 Z , the minimum threshold level should be achieved on
the incident wave under all allowed cases.
What bus configuration rules should be used to keep the loaded bus impedance above 0.71 Z ?
In the derivation of the minimum loaded-bus impedance, the addition of devices, and their capacitance is
treated as a distributed model. As such, the loaded-bus impedance can be approximated by
Z¢ = L (C+C¢)
where C′ is the added capacitance per unit length. If the distributed inductance and
capacitance of the media were known, Z′ could be calculated directly. Unfortunately, these are not
commonly specified by manufacturers. However, the characteristic impedance Z and the capacitance per
Z0 = L
unit length, C, is generally specified. With these, L can be solved from the relationship as L =
Z 2C. Substituting into the equation for Z′ and simplifying,
Z¢ = Z0 2C (C+C¢) = Z0 C C+C'
(3)
C′ is the distributed device capacitance, C , divided by the distance, d, between devices or C′ = C /d.
L L
Substituting this into the equation and solving for d,
(2) Electrically long is defined here as t > (t )/3, where t is the one-way time delay across the bus and (t ), is the 10% to 90%
10%–90% 10%–90%
transition time of the fastest driver output signal.

Z¢ = Z
C+C
(Z' )2 = C
Z 0 C + C L
C (Z 0 )2 = C + C L
Z' d
d =
æ(Z
)2
-1
ö
ç Z' ÷
è ø (4)
Now substituting our minimum Z′ of 0.71 Z gives,
d > L
æ æ Z ö2 ö
Cç ç ç è 0 0.71Z ÷ ø -1÷ ÷ meters (if C is pF/m) or feet (if C is pF/ft).
è 0 ø
d > L
0.98C (5)
This is a relationship for the minimum device spacing on a bus as a function of the distributed media
capacitance and lumped load capacitance. Figure 17 displays this relationship graphically.
Minimum Distance between CAN Nodes
1.4
C = 50 pF
1.2
C = 40 pF
1 C = 30 pF
m C = 20 pF
e
- 0.8 L
c C = 10 pF
n L
a
st 0.6
Di
0.4
0.2
40 50 60 70 80 90 100
Media Distributed Capacitance - pF/m
Figure 17. Minimum CAN Device Spacing on a Bus With Device Capacitance and Media Capacitance
Load capacitance, C , includes contributions from the CAN bus pins, connector contacts, printed-circuit
board traces, protection devices, and any other physical connections as long as the distance from the bus
to the transceiver is electrically short.
The typical 5-V CAN transceiver, such as the SN65HVD251, has a capacitance of 10 pF. The three-volt
supplied transceivers, such as the SN65HVD230, have a bit more capacitance than the 5-V device with 16
pF. Board traces add about 0.5 pF/cm to 0.8 pF/cm depending upon their construction. Media distributed
capacitance ranges from 40 pF/m for low-capacitance unshielded-twisted-pair cable to 70 pF/m for
backplanes. Note that connector and suppression device capacitance can vary widely.
This derivation gives guidelines for spacing CAN nodes along a bus segment based upon the lumped load
capacitance. The method is equally applicable to other multipoint or multidrop buses, such as RS-485,
RS-422, or M-LVDS, with appropriate adaptation of the parameter values.

Conclusion
4.12 Maximum Number of Nodes
In practice, up to 64 nodes may be connected to a DeviceNet bus, 127 on a CANopen bus and up to 255
nodes may be connected together on a CANKingdom bus. When more than the standard 30 nodes are
used on a bus, it is recommended that a transceiver with a high bus-input impedance, such as an
HVD230 or HVD251 be used.
A problem may develop when too many transceivers source or sink current onto or from the bus. When a
device begins to transmit a message, it has to sink or source all of the leakage current on the bus, plus
drive the standard signal voltage levels across the termination resistance. If the current demand is too
great, the device may be driven into thermal shut-down or destroyed.
To prevent transceiver damage, the voltage difference between reference grounds of the nodes on a bus
should be held to a minimum. This is the common-mode voltage across the entire system and although
many transceivers such as the HVD251 are designed to operate over an extended common-mode range,
the cumulative current demand of too many devices at a common-mode voltage extreme may jeopardize
network security. To enhance this common-mode security, most higher layer protocols like DeviceNet
specify that power and ground wires be carried along with the signaling pair of wires. Several cable
companies have developed 4-wire bundled cables specifically for these applications.
5 Conclusion
CAN is an open collector technology – the protocol could not work otherwise. This means that the
recessive state of a CAN transceiver is not actively driven. The termination resistors together with
transceiver input capacitance and cable capacitance create an RC time-constant discharge when an
actively-driven dominant bit on the bus transitions to an un-driven recessive bit. For signaling rates greater
than CAN's 1Mbps, a technology that actively drives the bus in both states such as RS-485 is required to
facilitate the bus transitions required for high-speed signaling rates.
