---
source: "ST AN5878 -- How to Design a Robust Automotive CAN System"
url: "https://www.st.com/resource/en/application_note/an5878-how-to-design-a-robust-automotive-can-system-stmicroelectronics.pdf"
format: "PDF 21pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 40685
---

Application note
How to design a robust automotive CAN system
Introduction
Controller area network (CAN) communication bus is extremely popular in the automotive industry. On top of standalone CAN
transceivers, many ASICs or SBCs embed one or several CAN transceivers.
To comply with the high-level of reliability required by the automotive industry and the various surges and standards applicable
on CAN links, the CAN transceivers and the electronics components part of the CAN physical layer must be protected by an
external TVS.
This application note will:
• Describe the CAN bus electrical parameters.
• Detail the applicable surges to a CAN node.
• Explain the main characteristics of a CAN protection device and how to select the right ESDCAN part number.

1 CAN bus overview
1.1 Topology
This protocol has been developed by Bosch in the 1980’s and is now widely used, not only in the automotive
industry, but also in the industrial segment.
CAN, controller area network, protocol allows serial half-duplex multimaster communication between various
ECUs through a multiplexed bus. It therefore limits the number of wires.
Each node can send and receive messages, but not simultaneously (half-duplex data transmission).
Figure 1. CAN bus topology
Node A Node B Node C
MCU/ASIC MCU/ASIC MCU/ASIC
CAN CAN CAN
controller controller controller
CAN transceiver CAN transceiver CAN transceiver
.mreT Term.
CAN bus overview
CAN protection CAN protection
CAN_H
CAN bus line
CAN_L
CAN communication uses a differential signal through CAN_H (CAN HIGH) and CAN_L (CAN LOW) and can
reach several data speeds that will be detailed in the following sections.
1.2 CAN standards
As many network protocols, the CAN protocol can be described using the 7-layer open system interconnection
(OSI) model.
To properly understand the scope of CAN standards from the hardware point of view, only the physical layer and
the data link layer are interesting.

CAN standards
Figure 2. CAN standards ecosystem
7 layers ISO model Physical and data link sublayers Hardware Standards
7. Application
6. Presentation
Logic link control
r
F
e
il
c
te
o
v
in
g
ry
, overload,
5. Session ISO 11898-1
4. Transport
Med
i
a
n
tr
l
ess D F
E
(D
a a
t
m a
)
s
e e
m
n c
a d
p
z
u
tio
t Controller C
S
C
as
A
E
N
e q
J
2
1
.
.
9
0
0
3
B
(
d
f
&
im
k
le
:
b
i n
Physical coding off-roads vehicles)
Bit coding, bit timing, …
3. Network sublayer (PCS)
AUI ISO 11898- 3
Physical media
Drivers/receivers (CAN fault tolerant)
2. Data link attachment (PMA) characteristics Transceiver ISO 11898- 2
MDI (CAN High speed)
1. Physical
de
P
h
y
ic
(P
ed
M
ia
D )
de
in
li
ca
t i
y
n -
s p
c i
fi
o t
Conn
w
re
to
r and
- F
lia
D
w
x
th
ib
I
S O
da
a-
8
r a
8
-
i s
NB: SAE - J2962 (communication transceivers qualification requirements) is based on ISO 11898- 1 and ISO 11898- 2
*AUI: Attachment unit interface *MDI: Media- dependent interface
As shown in the figure above, the physical layer itself is divided into three sublayers.
The first sublayer called physical media dependent or PMD corresponds to the connector and wires. The CAN
standards do not define this part which is highly specific to the application. The connector can be a DB9, an
OBD-II or any other connectors and the pins assignment for these connectors are not fixed.
The second sublayer called physical media attachment or PMA is the one defining the CAN transceiver (also
called CAN PHY) characteristics at the hardware level.
Two standards exist at this level:
• ISO 11898-2 for CAN high-speed (CAN high-speed medium access unit).
• ISO 11898-3 for CAN fault tolerant (CAN low-speed, fault tolerant, medium-dependent interface).
The CAN-FD or flexible data rate is compliant with the ISO 11898-2 CAN high-speed standard.
Between the CAN transceiver and the CAN connector, various electronic components ensure a proper
conditioning of the CAN signals and are part of the media dependent interface (MDI). See next figure.
The last sublayer physical coding sublayer (PCS) as well as the media control access (MAC) and logic link
control (LLC) sub layers of the data link layer are covered by the ISO 11898-1 (CAN data link layer and physical
signaling).
Within ISO 11898-1, two formats of frames can coexist on the same network and are defined by:
• CAN 2.0 A, implementing an identifier field of 11-bits. This allows to theoretically 2048 different message
types. Practically slightly less: 2032.
• CAN 2.0 B, implementing an identifier field of 29 bits. This allows more than 500 million of different
messages. The SAE J1939 (recommended practice for a serial control and communications vehicle
network) standard is based on CAN 2.0B. The 29-bit length for this field enables a more structured
identifier needed for heavy-duty vehicles like trucks, bus, agricultural vehicles.
The attachment unit interface (AUI) is the physical link between the CAN controller (MCU, ASIC, SBC, …) and the
CAN transceiver. Most of the time it is made of one line for reception (RXD) and one line for Transmission (TXD)
as shown in the following figure.

Figure 3. CAN physical layer
MCU TXD CAN_H
or
I/O SBC CAN_L
circuitry or
ASIC
RXD
srotautcA
srosneS
CAN data rates and electrical specifications
AUI MDI
CAN
TRANSCEIVER
CMC
L
R
T
TVS
S PLIT
GND
GND
Between the CAN transceiver and the connector, a common mode choke (CMC) is often used to reject the
common mode signal.
Since the CAN bus is bidirectional, the termination resistors R is needed to suppress or deeply attenuate the
reflection caused by the impedance mismatch of the cable ends. It is particularly required on extended CAN bus
with long wires. To preserve the symmetry between CAN_H and CAN_L signals, R must have the same value
with a small tolerance.
Adding a split capacitor C combined with the termination resistors R makes a low pass filter for common-
SPLIT T
mode noise between CAN_H and CAN_L lines and will improve the EMC.
To even reinforce the noise filtering, two optional data line capacitors C can be used as well between the CAN
data line and the ground.
Finally, the TVS, placed close to the connector, will protect all the components downstream against ESD events
and surges. The line capacitance of the TVS may play the same role as C capacitors and provides an additional
low pass filter.
1.3 CAN data rates and electrical specifications
The ISO 11898-2 for the high-speed CAN and ISO 11898-3 for the low-speed CAN provide the electrical
characteristics of the CAN bus.
Table 1. CAN bus characteristics
Parameters High-speed CAN Low-speed CAN
Physical layer standard ISO 11898-2 ISO 11898-3
Maximum length 30 m 500 m
Termination 120 Ω shunt 2.2 kΩ serial on each line
VCAN_H ~ 0 V
Recessive voltage level VCAN_H = VCAN_L = 2.5 V
VCAN_L ~ 5 V
VCAN_H = 3.6 V VCAN_H = 4 V
Dominant voltage level
VCAN_L = 1.4 V VCAN_L = 1 V
Signal waveforms See Figure 4. High-speed CAN signal waveform See Figure 5. Low-speed CAN signal waveform

Figure 4. High-speed CAN signal waveform
5
4 V
2 V
Recessive Dominant Recessive
)V(
egatloV
Figure 5. Low-speed CAN signal waveform
5
V
4
Recessive Dominant Recessive
)V(
egatloV
CAN data rates and electrical specifications
The data rate of the CAN bus depends on the CAN version and the selected CAN transceiver like shown in the
following table.
Table 2. CAN data rates
CAN version Data rate
CAN low-speed, Fault Tolerant 125 kbps
CAN high-speed 1 Mbps
CAN FD (flexible data rate) 2 Mbps (5 Mbps on simple network)
CAN FD SIC (signal improvement capability) 5 Mbps (8 Mbps on simple network)
CAN SIC XL (FAST mode) 10 Mbps (20 Mbps on simple network)
CAN high-speed, CAN FD, CAN SIC and CAN SIC XL are using the same physical layer described in ISO
11898-2.

Surges and applicable standards for automotive applications
2 Surges and applicable standards for automotive applications
When implemented in a vehicle, the CAN bus can be subject to many surges, hazards and mistakes during
servicing or repairing.
2.1 ESD events – ISO 10605
ESD events can be caused by manual handling of CAN connector during mounting or repairing and sometimes by
indirect coupling depending on the location of the CAN bus lines inside the vehicle.
The ISO 10605 describes the test set-up and the expected level of robustness for ESD in the automotive
environment.
Even if IEC 61000-4-2 is covering all other industries but automotive, it remains a reference for automotive
players.
Both ISO 10605 and IEC 61000-4-2 are system-level standards and are much more stringent than HBM (human
body model) or CDM (charge device model) stress specified in ICs datasheets. HBM and CDM ESD stresses are
intended to provide a minimum level of ESD robustness to enable a proper mounting of this IC on the PCB in an
ESD-controlled environment (ionizer, grounded equipment) with trained people.
System levels ESD standards (ISO 10605 and IEC 61000-4-2) guarantee the ESD robustness in the real world as
Different standards for ESD and EOS
shown in the following figure.
Figure 6. ESD standards
ESD
Component System
Level Level
Makesure the component is safe
during PCB mounting in the assembly
factory
HBM CDM ISO 10605
Human Body Model Charged Device IEC 61000 - 4 - 2
Model
Modelizing ….
Manualhandling Equipment, conveyor
ESDcontrolledenvironment Real operating conditions
ESD testing shall consist of direct or indirect application of discharges to the DUT using an ESD gun. Two distinct
types of discharges can be applied:
• Contact discharge: the ESD gun is directly in contact with the device under test (DUT). Conductive
surfaces must be tested using contact discharges.
• Air discharge: the ESD gun is being approached at a constant speed to the DUT. Non-conductive surfaces
shall be tested using air mode discharges. Air discharge may also be applied to conductive surfaces, if
required in the test plan.
The ESD gun can be modelized as shown in the following figure.

Fast transients - ISO 7637-3 pulse 3a/3b
Figure 7. ESD gun model
G
(MW ) R
High supply C Device Under
voltage Test
The severity of the ESD spike applied obviously depends on the RC network. The standards define these RC
networks that must be selected according to the use case in the vehicle.
In the following table, the RC networks are ranked by severity (the upper, the more stressful).
Table 3. ESD RC network defined by the standards
RC network Use cases Standards
Powered-up electronics module easily accessible from inside the vehicle (human
R = 330 Ω, C = 330 pF ISO 10605
body discharge through a metallic part)
Powered-up electronics module only accessible from outside the vehicle (human
ISO 10605
R = 330 Ω, C = 150 pF body discharge through a metallic part)
IEC 61000-4-2
Unpowered electronics module
Powered-up electronics module easily accessible from inside the vehicle (human
R = 2 kΩ, C = 330 pF ISO 10605
body discharge through the skin)
Powered-up electronics module only accessible from outside the vehicle (human
R = 2 kΩ, C = 150 pF body discharge through the skin) ISO 10605
Unpowered electronics module
2.2 Fast transients - ISO 7637-3 pulse 3a/3b
Fast transient test pulses a and b simulate transients which occur because of the switching processes due to
bounces of relays opening or closing on the battery bus as instance and that are coupled on the data line.
Two different methods can be used to simulate the coupled voltage for fast transients:
1. Capacitive coupling clamp (CCC) method: harness is placed inside the metallic clamp and transient pulses
defined in a standard are applied on this metallic clamp.
2. Direct capacitive coupling (DCC) method consists in applying transient pulses to the capacitor in series
with the DUT. For fast transients, the value of this capacitor is 100 pF.
After the tests, the DUT must be operational.
These transients and the test set-up are defined in ISO 7637-3 standard, and they are also called fast 3a pulse
(for negative) and fast 3b pulse (for positive).
They are repetitive pulses with a short duration of 150 ns and a very fast rise time of 5 ns. These repetitive pulses
are applied during 10 minutes on the DUT.
The following table defines the more stressful peak pulse voltages (corresponding to the level IV of ISO 7637-3).

Slow transients - ISO 7637-3 negative and positive pulses 2a
Table 4. Fast transients maximum peak pulse voltages
Transient pulses test 12 V electrical system 24 V electrical system
Fast 3a -110 V -150 V
Fast 3b +75 V +150 V
2.3 Slow transients - ISO 7637-3 negative and positive pulses 2a
Slow transient test pulses simulate transients which occur because of interrupting the current in a circuit with large
inductive load (such as a radiator fan motor, air conditioning compressor clutch, …) and that are coupled on data
lines.
Two different methods can be used to simulate the coupled voltages for slow transients:
• Direct capacitive coupling (DCC) method consists in applying transient pulses to the capacitor in series
with the DUT. For slow transient, the capacitor value is 100 nF.
• Inductive coupling clamp (ICC) method: harness is placed inside the injection probe and transient pulses
defined in the standard are applied on this injection probe.
After the tests, the DUT must be operational.
These transients are defined in ISO 7637-3 standard, and they are also called slow positive and negative pulses
2a.
These transients are repetitive with a pulse duration of approximately 50 µs and a rise time of 1 µs. These
repetitive pulses are applied during 5 minutes on the DUT.
The following table defines the most stressful peak pulse voltages (corresponding to level IV of ISO 7637-3).
Table 5. Slow transients maximum peak pulse voltages
Transient pulses test 12 V electrical system 24 V electrical system
Slow DCC + + 30 V + 45 V
Slow DCC - - 30 V - 45 V
Slow ICC + + 6 V + 10 V
Slow ICC - - 6 V - 10 V
2.4 Regulator failure – ISO 16750-2
This test simulates a failure on the regulator device, leading to an overvoltage to the battery power line (V ).
BAT
The ISO 16750-2 standard describes this test and the voltage to be applied on all the relevant inputs of the
electronics module depends on the electrical system type as shown in the following table.
Table 6. Regulator failure – applicable voltage
12 V electrical system 24 V electrical system
+ 18 V + 36 V
This test is applied for 60 min.
2.5 Jump start - ISO 16750-2
As shown in the following figure, the jump start test corresponds to the application of 24 V on all inputs to simulate
for examples:
• Wrong connection of an auxiliary battery in series with a flat battery of a passenger car.
• A garage battery booster with a wrong voltage selection connected to power a passenger car with no
battery.
• A truck battery connected to power a passenger car to start the engine.

ISO 16750 – reverse battery
Figure 8. Jump start wrong connection
Commercial vehicle, Trucks Light vehicle
with 24V nominal battery with 12V nominal battery
·
+
Garage battery booster
with incorrect voltage selection
ECU ECU ECU
12V nominal battery
In these different cases, 24 V is applied on the entire system. Not only the ECUs and all the circuits have to
withstand the overvoltage but also the TVS.
The ISO 16750-2 standard describes this test which is applicable only for 12 V electrical systems.
A voltage of 24 V must be applied on all relevant points for 1 minute ±10%.
2.6 ISO 16750 – reverse battery
As shown in the following figure, the reverse battery test corresponds to the application of -14 V for 12 V battery
nominal voltage over 60 s to simulate a reversed battery connection for example when:
• Using an auxiliary battery (from another passenger car, a battery booster, …).
• Reconnecting a battery to the car power net.
• Repairing the car power net (junction boxes, …).
Figure 9. Reverse battery wrong connection
Garage battery booster
Light vehicle
with 12V nominal battery
12V
24V
+
Car servicing
X X
ECU ECU ECU
12V nominal battery

ISO 16750 – reverse battery
The ISO 16750 standard describes this test.
The reverse voltage must be applied for 1 minute ±10% and the voltage level depends on the electrical system
type as shown in the next table.
Table 7. Reverse battery – applicable voltage
12 V electrical system 24 V electrical system
- 14 V - 28 V

Requirements on CAN protection
3 Requirements on CAN protection
As we have seen on the previous sections, on top of the normal operating conditions, the CAN links must
withstand many types of surges, transients and survive wrong connections. The CAN TVS protection, as part of
the MDI must comply with all the standards and must protect all the CAN bus components against these surges.
In this section, we will detail the impact of the previously described standards constraints on the CAN protection
devices and we will review how the ST ESDCAN series can match them.
3.1 Breakdown voltage
A TVS is meant to clamp transient voltages, but it is not supposed to operate in the avalanche mode in DC mode,
sinking a high current.
So when the CAN bus is submitted to overvoltage due to regulator failure, jump start or reverse battery, as the
current is not limited and the test duration is very long (from one minute to one hour), the CAN protection TVS
must not enter in avalanche mode.
Therefore, one should select a CAN protection TVS with a reverse breakdown voltage adapted to the regulator
overvoltage, jump start or reverse battery applicable to the electrical system of the vehicle as described in the
following table.
Table 8. Constraints on directionality and V of CAN TVS protection
BR
Regulator failure Jump start Reverse battery Impact on CAN TVS protection
Bidirectional
12 V electrical system +18 V + 24 V -14 V
VBR> 24 V
Bidirectional
24 V electrical system + 36 V Not applicable -28 V
VBR > 36 V
As one can see in the extract of the datasheet of the SOT323-3L ESDCAN series in the following figure, several
part numbers with various V are available.
Figure 10. SOT323-3L ESDCAN series breakdown voltages at 25 °C
12 V electrical systems
24 V electrical systems
ST offers several values of V even within the 12 V or 24 V electrical systems series, to address all the
customers’ specific requirements. Indeed, some OEMs may want to be more stressful than ISO 16750-2 with the
jump start voltages that they apply on their vehicle models, by adding a safety margin of a few Volts.

Breakdown voltage
This variety of V allows to answer all the specific requirements with an optimized maximum clamping voltage
V / maximum jump start voltage ratio.
CL
It is important to consider the maximum ambient temperature of the application when checking the V values.
The regulator failure test is supposed to be applied at 20 °C below the maximum operating temperature.
The variation of breakdown voltage (and thus clamping voltage) versus the temperature can be calculated thanks
to the αT of the devices (see next figure) and the following equation:
VBR@Tj=VBR@25°C× 1+αT × Tj−25°C
Figure 11. SOT323-3L ESDCAN series αT values
αT values
B R
@ T
J
formula
Thanks to the last generation of protection technology with snapback effect, the need to offer various V values
tends to disappear.
As shown in the next figure, the ESDCAN03-2BM3Y features a trigger voltage V at 28 V (covering all jump
TRIG
start specifics) avoiding compromising the clamping voltage V .
CL

Line capacitance
Figure 12. ESDCAN03-2BM3Y – snapback effect
ESDCAN03-2BM3Y datasheet extract
Related links
2.4 Regulator failure – ISO 16750-2 on page 8
2.5 Jump start - ISO 16750-2 on page 8
2.6 ISO 16750 – reverse battery on page 9
ESDCAN03-2BW3Y datasheet
3.2 Line capacitance
The parasitic line capacitance of a TVS is critical regarding the data rate of the signal. If the line capacitance is
too high, the signal integrity may be degraded, and the bits can be lost.
As shown in the following figure, the line capacitance impacts both rise and fall times.

Package
Figure 13. Impact of the line capacitance of a TVS on the signal integrity
Host Client High state allowed
window
TVS placed on signal
Low speed line
OK
signal
Bit period
L The rise time and fall time are Low state allowed window
impacted by the parasitic capacitors
of the protection
Host Client High state allowed
window
TVS placed on signal
High speed line NOK
signal Transmission failed
Bit period L Low state allowed window
The signal never reaches high state and low state voltage levels
= parasitic line capacitance
Obviously, the parasitic capacitances of the whole components and wires between the emitter and the receiver
can impact the rise times and fall times of the CAN signals.
The SAE J2962-2 requests a maximum total line-to-ground capacitance of 100 pF on each CAN line (CAN_H and
CAN_L) on their test set-up for high-speed CAN transceivers qualification requirements.
The lower the capacitance of the TVS, the more margin for the rest of the circuit.
ESDCAN series offers part number with 3 pF parasitic capacitance to save as much as possible on the CAN lines
capacitance budgets.
Figure 14. Line capacitance of SOT323-3L ESDCAN series
As the CAN communication is a differential link, the matching between both TVS embedded in the same package
is key. On low capacitance ESDCAN (ESDCAN02, 03 and 05) the difference of the line capacitance between the
two TVS in the same package is as low as 10 fF which guarantees an excellent matching.
3.3 Package
The digitalization of the car leads to an increasing number of ECUs (electronic control unit). Moreover, these
ECUs are more complex, connected to many sensors, with a high-level of computation. Many comfort and safety
devices are also added in the new cars.

Robustness
All these trends create heavy space constraints in the car and therefore on the electronics boards. To address this
new need for miniaturization, the ESDCAN series offer three different packages as shown in the following figure.
Figure 15. ESDCAN series–packages offer
SOT- 23 SOT - 323 DFN1110
2.9 mm x 2.6 mm 2.1 mm x 2.0 mm 1.1 mm x 1.0 mm
The SOT-23 and the SOT-323 are very popular and mature leaded packages. It is easy to implement an
automated optical inspection (AOI) with one or several camera modules during the PCB mounting to control the
soldering process.
To move forward in the package miniaturization, the DFN packages are the most appropriate. However, standard
DFN packages used in other non-automotive industry (personal electronics, factory automation, consumer
goods, ...) do not allow to implement an AOI during PCB mounting. The solder pads being located in the bottom of
the package, the solder joints are not visible and impose to implement an automated X-ray inspection (AXI).
The AXI usually requires a longer programming time, a higher capital investment and generates additional
constraints on the PCB layout (two-side PCB cannot be easily inspected for example).
So, to adapt the DFN packages to the AOI, it was necessary to add wettable flanks on DFN packages. As shown
in the following figure, the side of the pads are exposed and wettable so solder menisci are visible and can be
optically inspected.
If the CW dimension (see next figure) is short enough (50 µm maximum on ESDCAN03-2BM3Y), the shadow on
the solder fillet is minimized and even 2D AOI can be sufficient in some cases to inspect the solder joints of this
DFN package (no need for 3D AOI).
Figure 16. Wettable flank profile on ESDCAN03-2BM3Y
3.4 Robustness
If the CAN protection TVS must not degrade the signal nor complicate the PCB layout and mounting, the primary
role is to efficiently protect the CAN transceivers and the components of the MDI.
On one hand, the robustness will characterize the severity of the surges (in terms of voltage, current, power, …)
that the TVS can withstand.

On the other hand, the quality of protection will be characterized, most of the time, by the clamping performances
of the TVS that is, the residual voltage and the residual current that will actually hit the CAN transceivers and the
components of the MDI.
On top of all the surges and hazards described in the section 2, a way to quantify the robustness of a TVS versus
pulses longer than ESD is to measure the destructive peak pulse current I against 8/20 µs current waveform.
PP
This test consists in applying an exponential current waveform as shown in the following figure with a rise time
(10% - 90%) of 8 µs and a pulse time (tp) corresponding to 20 µs (time difference between rise time to I /2 and
fall time to I /2).
Figure 17. Exponential current waveform
It is quite easy to summarize the robustness of a STMicroelectronics CAN protection TVS versus all the
previous surges described above. All the data are available in the datasheet. Let us take the example of
ESDCAN03-2BWY.
The performances regarding ISO 7637-3 and ISO 10605 are given on the cover page (see the next figure) but
also in the absolute ratings table in page 2 (see Figure 19. ESDCAN03-2BWY absolute ratings table).

Figure 18. ESDCAN03-2BWY cover page
ISO 10605 (ESD) robustness
ISO 7637- 3 robustness

Figure 19. ESDCAN03-2BWY absolute ratings table
Finally, the Table 9. ESDCAN03-2BWY robustness summary gives a summary of the robustness of the
ESDCAN03-2BWY versus the standards.

Table 9. ESDCAN03-2BWY robustness summary
Standard Most severe standard requirement ESDCAN03-2BWY robustness PASS/FAIL status
Component test direct discharge
(R= 330 Ω, C= 330 pF) ± 30 kV PASS
Category 3 / Level 4i: ± 15 kV
Contact discharge
(R= 330 Ω, C= 330 pF) ± 30 kV PASS
Category 3 / Level 4i: ± 25 kV
Air discharge
ISO 10605 Vehicle test
(R= 330 Ω, C= 150 pF) (DUT accessible from outside) ± 30 kV PASS
Contact discharge Category 3 / Level 4i: ± 8 kV
(R= 330 Ω, C= 150 pF) (DUT accessible from outside) ± 30 kV PASS
Air discharge Category 3 / Level 4i: ± 25 kV
(R= 2 kΩ, C= 330 pF) (DUT accessible from inside) ± 30 kV PASS
Contact discharge Category 3 / Level 4i: ± 8 kV
(R= 2 kΩ, C= 330 pF) (DUT accessible from inside) ± 30 kV PASS
Air discharge Category 3 / Level 4i: ± 15 kV
Component test direct contact discharge
(R= 2 kΩ, C= 150 pF) ± 30 kV PASS
Category 3 / Level 4i: ± 15 kV
Contact discharge
or
(R= 2 kΩ, C= 150 pF) ± 30 kV PASS
Vehicle test
Air discharge
(DUT accessible from outside)
Fast transients Test level IV (DCC / CCC): -110 V
-150 V PASS
ISO 7637-3 pulse 3a (12 V electrical system)
Fast transients Test level IV (DCC / CCC): +75 V
+150 V PASS
ISO 7637-3 pulse 3b (12 V electrical system)
Slow transients Test level IV (DCC): +30 V
+ 85 V PASS
ISO 7637-3 positive (12 V electrical system)
Slow transients Test level IV (DCC): -30 V
- 85 V PASS
ISO 7637-3 negative (12 V electrical system)
Regulator failure
18 V for 60 min VBR ≥ 26.5 V PASS
ISO 16750-2
Jump start
24 V for 1 min VBR ≥ 26.5 V PASS
Reverse battery
-14 V for 1 min -26.5 V ≤ VBR PASS

Clamping voltage
3.5 Clamping voltage
As mentioned above, the clamping voltage is related to the quality of protection of the CAN protection TVS.
The clamping voltage is the residual voltage seen by the components (CAN transceivers, termination resistors,
capacitors, …) when a surge is applied.
The role of the CAN protection TVS is to sink as much as possible of the pulse current to the ground and limits
the voltage increase on the line. So, we understand that the main electrical characteristics of a CAN protection
TVS is the dynamic resistance. As a first approach, the lower the dynamic resistance, the better the quality of
protection.
Decreasing the dynamic resistance of a TVS can be easily done by increasing the active area of the PN junction
of the TVS diode (to increase its current capability). But increasing the active area will obviously increase:
• the die size and then limits the package miniaturization.
• the parasitic capacitance of the diode and then limits the bandwidth of the TVS and its ability to address
high data rate or save the capacitance budget of the CAN lines.
So, an efficient CAN protection TVS is a trade-off between all these electrical characteristics.
As shown in Figure 12. ESDCAN03-2BM3Y – snapback effect for ESDCAN03-2BM3Y, another way to
significantly decrease the clamping voltage is to use technologies with snapback. When the voltage applied on
the TVS exceeds the “trigger” voltage, V , its voltage suddenly decreases to the holding voltage V and then
TRIG H
it acts like a standard clamping voltage (see the following figure). This helps to decrease the clamping voltage by
10% to 20% without compromising the other electrical characteristics.
Figure 20. ESDCAN03-2BM3Y – electrical characteristics with snapback
All the clamping voltages versus the various automotive pulses are given in the ESDCAN datasheets. The
surges are directly applied on the ESDCAN part, so without any other circuit or component limiting the surges.
It is the most stressful condition and so the worst case for the protection device. A datasheet extract of
ESDCAN03-2BM3Y is given as example in the following figure.

Clamping voltage
Figure 21. ESDCAN03-2BM3Y – responses to automotive surges
In the final application, on the real PCB embedding all the MDI components, the value of the clamping voltage will
be different (most of the time lower) when applying a surge. It is particularly important to perform the test on the
final design to make sure that the CAN protection TVS will clamp enough energy not to degrade any downstream
components.
The layout and the placement of the TVS plays a critical role in maximizing the protection efficiency. Thorough
recommendations are given in AN5686 : PCB layout tips to maximize ESD protection efficiency.
ESDCAN03-2BM3Y datasheet
AN5686: PCB layout tips to maximize ESD protection efficiency

Junction temperature
3.6 Junction temperature
Finally, the last important parameter when selecting a CAN protection TVS is the “Operating junction temperature
range”. In normal operation, the CAN protection TVS is quiet and is not supposed to sink any current so there is
no self-heating phenomenon.
So, the operating junction temperature range, is the temperature range at which the device can operate without
drastically impacting its lifetime. The reliability tests of the ESDCAN series (H3TRB, thermal cycling, …) are
always performed at the worst conditions so meaning at 175 °C for example for ESDCAN series in SOT323-3L
and DFN1110.

How to select the right ESDCAN
4 How to select the right ESDCAN
All the parameters and characteristics presented above allow to select the right CAN protection TVS in most of
the cases.
However, to make it even faster, we developed a tool for the ESDCAN series as shown in the following figure.
By answering five simple questions, one can get the right part number:
1. Is it for cars or trucks?
2. Which package is needed?
3. Which kind of CAN: low speed CAN or high speed CAN?
4. Is a jump start voltage value higher than 28 V necessary?
5. Which item is the most critical in the design or project?
– the surge level so high robustness is preferred.
– the capacitance budget so low capacitance is preferred.
– the CAN transceiver vulnerability so low clamping voltage is preferred.
Figure 22. Five steps to select the right ESDCAN
(1)car or truck: If you consider:
• 12V system/battery → [car] path (light vehicles) Move to SOT323
• 24V system/battery → [truck] path (trucks, off - roads, etc.)
CAN- FD (2) ?
Y
(2) CAN- F D: High- speed CAN, CAN- FD, or FlexRay → [Y] path SOT23 3
Low ESDCAN01- 2BLY
(3) Jump- s tart (j ump- start voltage + tolerance): N
• ≤ 26.5V → [Low] path 4 ESDCAN24- 2BLY
• ≥ 26.5V → [High] path Package? Jump - start( 3) ? High 5 High robustness
Car 2 QFN 1.1 x 1.0 3L ESDCAN03- 2BM3Y
ESDCAN04- 2BLY
High ESDCAN02- 2BWY Low capacitance
Jump- start( 3) ?
Car 4
truc
k
( 1) ?
CAN- FD( 2) ?
Y ESDCAN05- 2BWY
SOT
32
N - FD (2) ?
Y
Low
ESDCAN03- 2BWY
SOT323 3 Low
N ESDCAN06- 2BWY 4 ESDCAN02- 2BWY
Truck 2 Jump- start( 3) ? Low capacitance
Package? Y Move to SOT323 High 5
SOT23 3 ESDCAN04- 2BWY
CAN- FD( 2) ? N Low clamping voltage
ESDCAN06- 2BLY

Conclusion
5 Conclusion
This application note describes the CAN communication link from the physical layer point of view as well as
the automotive surges that CAN transceivers and components part of the MDI must survive. Based on this
information, the requirements on the electrical characteristics on CAN protection TVS are listed and explained.
Ultimately, this document shows how to select the proper CAN protection TVS using the ESDCAN series
example.
It is mandatory to confirm with measurements and tests, that the ESDCAN device selected based on these
criteria is suitable in the final design and layout.

Revision history
Table 10. Document revision history
Date Revision Changes
21-Nov-2022 1 Initial release.
22-Nov-2022 2 Minor document structure changes to improve readability.

Contents
Contents
1 CAN bus overview.................................................................2
1.1 Topology......................................................................2
1.2 CAN standards ................................................................2
1.3 CAN data rates and electrical specifications ........................................4
2 Surges and applicable standards for automotive applications ......................6
2.1 ESD events – ISO 10605........................................................6
2.2 Fast transients - ISO 7637-3 pulse 3a/3b...........................................7
2.3 Slow transients - ISO 7637-3 negative and positive pulses 2a .........................8
2.4 Regulator failure – ISO 16750-2 ..................................................8
2.5 Jump start - ISO 16750-2........................................................8
2.6 ISO 16750 – reverse battery .....................................................9
3 Requirements on CAN protection .................................................11
3.1 Breakdown voltage............................................................11
3.2 Line capacitance..............................................................13
3.3 Package.....................................................................14
3.4 Robustness ..................................................................15
3.5 Clamping voltage..............................................................20
3.6 Junction temperature ..........................................................22
4 How to select the right ESDCAN ..................................................23
5 Conclusion.......................................................................24
Revision history .......................................................................25
List of tables ..........................................................................27
List of figures..........................................................................28

List of tables
List of tables
Table 1. CAN bus characteristics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
Table 2. CAN data rates . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
Table 3. ESD RC network defined by the standards . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
Table 4. Fast transients maximum peak pulse voltages. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
Table 5. Slow transients maximum peak pulse voltages . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
Table 6. Regulator failure – applicable voltage. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
Table 7. Reverse battery – applicable voltage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
Table 8. Constraints on directionality and V of CAN TVS protection. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
Table 9. ESDCAN03-2BWY robustness summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
Table 10. Document revision history. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
Table 8. Constraints on directionality and V of CAN TVS protection. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 0
Table 6. Regulator failure – applicable voltage. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 0
Table 7. Reverse battery – applicable voltage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 0
Table 9. ESDCAN03-2BWY robustness summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 0

List of figures
List of figures
Figure 1. CAN bus topology. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
Figure 2. CAN standards ecosystem. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
Figure 3. CAN physical layer . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
Figure 4. High-speed CAN signal waveform. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
Figure 5. Low-speed CAN signal waveform . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
Figure 6. ESD standards. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
Figure 7. ESD gun model . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
Figure 8. Jump start wrong connection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
Figure 9. Reverse battery wrong connection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
Figure 10. SOT323-3L ESDCAN series breakdown voltages at 25 °C. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
Figure 11. SOT323-3L ESDCAN series αT values . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
Figure 12. ESDCAN03-2BM3Y – snapback effect. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
Figure 13. Impact of the line capacitance of a TVS on the signal integrity . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
Figure 14. Line capacitance of SOT323-3L ESDCAN series . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
Figure 15. ESDCAN series–packages offer. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
Figure 16. Wettable flank profile on ESDCAN03-2BM3Y. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
Figure 17. Exponential current waveform . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
Figure 18. ESDCAN03-2BWY cover page. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
Figure 19. ESDCAN03-2BWY absolute ratings table. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
Figure 20. ESDCAN03-2BM3Y – electrical characteristics with snapback . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
Figure 21. ESDCAN03-2BM3Y – responses to automotive surges . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
Figure 22. Five steps to select the right ESDCAN. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
