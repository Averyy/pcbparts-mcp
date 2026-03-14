---
source: "ROHM 66AN046E -- Selection Method and Usage of TVS Diodes"
url: "https://fscdn.rohm.com/en/products/databook/applinote/discrete/diodes/selection_method_and_usage_of_tvs_diodes_an-e.pdf"
format: "PDF 15pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 29110
---

2017.4
Application Note
Diode
Selection Method and Usage of TVS Diodes
Transient voltage suppressor (TVS) diodes are a voltage clamp type of surge protection elements. They are designed to absorb
a large amount of energy in a short time with a low operation resistance and high current rating characteristics. To support a wide
range of applications, products of various types are listed in ROHM’s lineup. This application note explains points for selecting the
TVS diodes and introduces application examples.
Points for selecting TVS diodes
A list of selection points is shown below. Points 1 to 3 explain how to select the TVS diodes in a way that prevents various
characteristics from being deteriorated when the TVS diodes are added to the existing wiring in order to protect devices. Points 4
to 6 describe how to confirm that the TVS diodes themselves will not be damaged by overvoltage pulses, such as electrostatic
breakdown and surges. Point 7 describes how to select a product with a higher protective performance. The details of these
methods are explained in the following pages.
- Confirm that the TVS diodes will not affect the wiring to be protected.
1. Selection with consideration of the voltage on the wiring
2. Selection with consideration of the signal frequency on the wiring
3. Selection based on the signal polarities
- Confirm the breakdown ratings of the TVS diodes.
4. Selection of the TVS diodes that can withstand ESD as required
5. Selection of the TVS diodes that can withstand overcurrent as required
6. Selection of the TVS diodes that can withstand overpower as required
- Confirm the protective performance of the TVS diodes.
7. Selection of products with a low clamping voltage

1/14
December 2023

Selection Method and Usage of TVS Diodes Application Note
The TVS diodes are added to the existing wiring in order to
protect devices. The wiring includes power lines to supply the
power, signal lines to transmit analog and digital signals,
communication lines to link devices using controllers, and
control lines to transmit commands for turning devices ON and
OFF and setting conditions. This application note explains
how to select the TVS diodes in a way that prevents various
characteristics of the existing wiring from being deteriorated
due to additions of the TVS diodes.
1. Selection with consideration of the
voltage on the wiring
Figure 1 shows schematic diagrams of the TVS diode
operations. The left diagram shows the operation under
normal conditions. In this example, the connector is located on
the left end and the IC, which is a device to be protected, is
located on the right end. They are connected via the wiring
and a TVS diode is placed between them. The wiring carries
the designed DC voltage and analog or digital signals
depending on the applications. The TVS diode is not operated
normally because no breakdown has occurred in the TVS
diode.
The right diagram shows the operation when a surge is applied.
If the surge voltage exceeds the breakdown voltage of the TVS
diode, the surge current flows through the TVS diode and a
large part of the current flows to the ground. Then, the TVS
diode clamps the voltage and protects the target device.
2/14
A n
D
D C
a lo g
ig ita l
T V S
t
IC
S u rg e
V F
V C
L
Figure 2 shows the I-V characteristics of the TVS diode.
Standoff voltage VRWM is important among these
characteristics. This parameter is the maximum voltage
immediately before the TVS diode enters the breakdown state.
The TVS diode does not operate below this voltage. Therefore,
select a TVS diode with VRWM higher than the voltage
processed with the wiring.
It should be noted that reverse current IR always flows to the
ground because of reverse voltage VR. This current is
regarded as a leakage current in terms of the application
circuit and may cause malfunction in some circuits. Select a
product with an IR value that the circuit can tolerate. Be sure
to check the operation with the actual equipment.
In addition, since IR is increased as the signal waveform
approaches VRWM, the distortion rate could be exacerbated for
analog signals. Be sure to check the operation with the actual
equipment.
Normal conditions When overvoltage surge
is applied
Figure 1. Schematic diagrams of TVS diode operations
Operations under normal conditions and when an
overvoltage surge is applied
To prevent breakdown of the TVS diode under normal
conditions, it is necessary to select a product according to the
voltage and signals transmitted on the wiring.
V C
V
B RV
R W M V R
I
IR
IB
IP
R
P
IR
I : Reverse current (leakage current) R
V : Standoff voltage
RWM
V : Breakdown voltage
BR
V : Clamping voltage
CL
Figure 2. I-V characteristics of TVS diode
Characters in blue indicate important characteristics.

2. Selection with consideration of the
signal frequency on the wiring
Since the TVS diode is connected to the wiring even under
normal conditions, capacitance between terminals Ct is always
added in addition to reverse current IR described in the
previous section (Figure 3).
3/14
C t
Standards for capacitance
Applications
between terminals C
USB3.2 Gen 2x2 (20Gbps)
Thunderbolt 2 (20Gbps)
Thunderbolt 3 (40Gbps)
HDMI 2.0 (14Gbps)
HDMI 2.0a/b (18GHz) ≤ 0.15 pF
HDMI 2.1 (48Gbps)
Wi-Fi antenna (2.4 GHz)
Wi-Fi antenna (5 GHz)
Bluetooth antenna (2.4 GHz)
USB3.2 Gen 2NOTE2 (10Gbps)
HDMI 1.3 (10.2Gbps) ≤ 0.35 pF
HDMI 1.4 (10.2Gbps)
NFC antenna (13.56 MHz)
USB 3.2 Gen 1NOTE1 (5Gbps)
Figure 3. Capacitance between terminals Ct of the TVS diode
HDMI 1.2 (4.95Gbps)
is added to the wiring under normal conditions
DisplayPort 1.0 (2.7Gbps)
LVDS (1Gbps)
MIPI D-PHY v1.1 (1.5Gbps)
The wiring is not affected by the capacitance if it is a power ≤ 0.5 pF
MIPI D-PHY v1.2 (2.5Gbps)
line with a DC voltage only. However, signal, communication, MIPI D-PHY v2.0 (4.5Gbps)
MIPI D-PHY v2.1 (4.5Gbps)
and control lines may be affected depending on the frequency
MIPI D-PHY v2.5 (4.5Gbps)
and communication speed. Therefore, it is necessary to select GPS antenna (1.5 GHz)
a capacitance value suitable for the application. If the USB 2.0 (480Mbps)
≤ 1.5 pF
Ethernet 1000BASE (1Gbps)
capacitance value is too large on the signal lines, the distortion
MOST150 (150Mbps)
rate is exacerbated and waveforms are delayed for analog ≤ 5 pF
Ethernet 100BASE (100Mbps)
signals. Digital signals are delayed and their waveforms are
I2C (3.4Mbps) ≤ 8 pF
blunted. For the communication lines, the eye patterns (bit
USB 1.1 (12Mbps)
error rate) could be degraded. For the control lines, CAN FD (5Mbps)
FlexRay (10Mbps)
malfunction could occur due to delayed or blunted waveforms. ≤ 12 pF
MOST50 (50Mbps)
LIN (20kbps)
Figure 4 shows typical applications and the standards for
CXPI (20kbps)
capacitance between terminals Ct. The capacitance values in
CAN (1Mbps)
this figure are standard values. Be sure to check the operation RS-232C (20kbps)
RS-423 (100kbps)
with the actual equipment.
RS-422 (10Mbps) ≤ 30 pF
RS-485 (10Mbps)
Audio microphone (100 kHz)
Push button switch
Audio headphones (100 kHz)
Audio speaker (100 kHz)
≤ 50 pF
Power line
All
Toggle switch
NOTE1: Earlier USB 3.0 and USB 3.1 Gen 1
NOTE2: Earlier USB 3.1 Gen 2
Figure 4. Applications and standards for capacitance
between terminals Ct
The capacitance values in this figure are standard values. Be
sure to check the operation with the actual equipment.

3. Selection based on the signal polarities
TVS diodes are available as unidirectional and bidirectional
products, as shown in Figure 5.
Figure 5. Unidirectional and bidirectional TVS diodes
Figure 6 shows their I-V characteristics. For the unidirectional
product, the reverse bias causes no current to flow until it
approaches breakdown voltage VBR. However, the forward
bias causes the current to start flowing at 0.5 V or less. For the
bidirectional products, neither the reverse or forward bias
causes the current to flow until it approaches VBR. To prevent
any current from flowing through the TVS diode under normal
conditions, select a product suitable for the application based
on these two characteristics.
Reverse bias Forward bias Reverse bias Forward bias
I I
V V
BR BR
F BR
Unidirectional Bidirectional
Figure 6. I-V characteristics of TVS diode
Figure 7 shows the waveforms if a unidirectional product is
connected to the wiring transmitting digital signals designed
with reference to the ground and analog signals designed to
provide signals centering around the bias voltage. Since the
waveform of each signal has positive polarity with reference to
the ground (the reverse bias with reference to the diode
anode), no current flows through the TVS diode. Therefore,
the unidirectional products can be used. For the same reason,
the bidirectional products can be used for the signal wiring with
positive polarity (Figure 8).
4/14
A
ig
n a
ita
lo
l
0
g
T V
S
B
IA S
B R
F
Figure 7. Unidirectional products can be used for the signal
wiring with positive polarity
n a
ita
lo
g
T V
IA S
Unidirectional Bidirectional Bidirectional configuration
product product with a combination of
unidirectional products
Figure 8. Bidirectional products can also be used for the
signal wiring with positive polarity
Next, we explain the situations with wirings for differential
digital and analog signals and analog signals with DC cutoff.
As shown in Figure 9, since the amplitudes of these signals
are centered around the ground, the bidirectional products are
used. The bidirectional products can be used because no
current flows until the voltage approaches VBR, regardless of
whether the signal swings to positive or negative polarity.
V I
+
Digital0 t
Analog0 t
IC BR
TVS
Figure 9. Bidirectional products are used for the signal wiring
with both positive and negative polarities

Consider what happens if a unidirectional product is used for
bipolar signal wiring. Figure 10 shows the waveforms obtained
as a result. Since the amplitude of the waveforms on the
negative polarity is clamped by forward voltage VF of the diode,
the information of the transmitted signals is lost. Therefore, the
unidirectional products cannot be used for bipolar signal wiring.
5/14
A n
a
ita l
lo g
+0
+0
Figure 10. Unidirectional products cannot be used for bipolar
signal wiring with positive and negative polarities
Here, we will outline the protective operation against
electrostatic discharge (ESD). As shown in Figure 11 for the
unidirectional products, when ESD enters, a surge with
positive polarity causes the reverse bias. The voltage is
clamped when a breakdown occurs and the current flows. A
surge with negative polarity causes the forward bias. The
voltage is clamped when it exceeds VF and the current flows.
The subsequent stage is protected in this way.
Surge
IC F
Figure 11. ESD protective operation with unidirectional
product
As shown in Figure 12 for the bidirectional products, surges
with positive and negative polarities cause the reverse bias.
The voltage is clamped when a breakdown occurs and the
current flows.
S u rg e
Surge with
Surge with
negative polarity
positive polarity
Figure 12. ESD protective operation with bidirectional
product
As described above, the unidirectional and bidirectional
products perform the ESD protective operation for both
positive and negative polarities.
In the following sections, we explain the points for selecting
the TVS diodes that can withstand surge pulses as required
for the applications. When the energy of the entering surge
pulse exceeds the protective performance of the TVS diode,
the TVS diode cannot absorb the energy completely, possibly
causing damage to the TVS diode itself and the device to be
protected.
4. Selection of the TVS diodes that can
withstand ESD as required
To protect the target device, the TVS diode itself must not be
damaged. Select a product with a rating value larger than the
ESD rating required for the application.
Tests were performed in accordance with IEC 61000-4-2 and Surge with Surge with
positive polarity negative polarity the two values of the ESD ratings (VESD) for the direct contact
and air discharges are listed as the rating values on the data
sheets. The values at ±30 kV were obtained as the maximum
values with the testing equipment (electrostatic discharge
generator, as of August 2023).
In the earliest years of development of the TVS diodes, the
ESD rating tended to decrease as the capacitance between
terminals was decreased, causing a trade-off. In recent years,
however, products having a small capacitance between
terminals and a high ESD rating simultaneously have been
developed. Therefore, this relationship is resolved to some
degree. Figure 13 shows the relationship between these two
values among the ROHM products. When selecting products
on a higher level than the test level required by IEC 61000-4-
2, approximately 40 pF or larger capacitance between
terminals can be considered as a high rating.

The TVS diodes have achieved a faster response compared
1000
]F IEC61000-4-2 Contact Discharge with other protective elements. However, there is a region
p Level1: 2kV
[
tC Level 2: 4kV where they cannot sufficiently respond immediately after ESD
:S
L A 100
e
v
v
3
4
:
:
6
8
k
V is applied. Therefore, a voltage higher than VCL may be applied
N Level X: special to the subsequent stage, causing damage to the device to be
IM
E protected.
T
N
E 10
E
W 50
VVC
C
==5 53.33.V3 V(S (MSFM3F3V3T3FV)TF)
C N A T 1 ]V [ 40 V V V V C C C C L L L L = = = = 1 1 1 1 9 0 . . 9 0 9 3 . . V V 9 3 V V ( ( S S ( ( M M S S F F M M 1 6 F F 2 V V 0 1 6 T T 2 V F F V 0 ) ) T T F F ) )
IC L
A V
A :E
30
C G
0.1 A
0 10 20 30 T
L 20
O
ESD CAPABILITY: V [±kV] V
ESD
G
Figure 13. Relationship between capacitance between IP 10
terminals and ESD rating among ROHM products M
IEC 61000-4-2 direct contact discharge test L
±30 kV is the maximum value of the testing equipment 0
(electrostatic discharge generator)
-10
5. Selection of the TVS diodes that can -100 0 100 200 300 400 500 600 700 800
TIME [ns]
withstand overcurrent as required
Figure 14. Comparison of peak voltages immediately after
Select a product with a rating value larger than the peak pulse
ESD application among products with different clamping
current required for the application. voltages
IEC 61000-4-2 +8 kV direct contact discharge test
The rating values are listed as peak pulse current IPP on the
data sheets. The test waveform used is a 10/1000 µs impulse
waveform as specified in Telcordia GR-1089-CORE, which is
the industry standard test condition, or a 8/20 µs impulse
waveform as specified in IEC 61000-4-5.
6. Selection of the TVS diodes that can
withstand overpower as required
Select a product with a rating value larger than the peak pulse
power required for the application.
The rating values are listed as peak pulse power PPP on the
data sheets. The test waveform is the same as the one used
for peak pulse current IPP above.
7. Selection of products with a low
clamping voltage (V )
CL
Select a product with VCL as low as possible for VRWM selected
in point 1.
6/14

Figure 14 shows a comparison of peak voltages immediately reduced further if the total area of the clamping waveform is
after ESD is applied among products with different VCL. It can smaller, products with a lower VCL are considered to show a
be seen that the peak voltage is lower as VCL is lower. In higher protective performance.
addition, since damage to the subsequent stage can be
Summary
The points for selecting the TVS diodes are summarized as follows.
Characteristics to be
Item Point for selection
noted
1. Selection with consideration of the Standoff voltage VRWM Select a product with VRWM higher than the voltage
voltage on the wiring processed with the wiring.
Reverse current Select a product with an IR value that the circuit can
(leakage current) IR tolerate. Be sure to check the operation with the actual
equipment.
2. Selection with consideration of the Capacitance between Select a product with a Ct value that can be tolerated in
signal frequency on the wiring terminals Ct the application. Be sure to check the operation with the
actual equipment.
3. Selection based on the signal Configuration of TVS - The unidirectional and bidirectional products can be
polarities diode used for the signal wiring if the signal swings only to
positive polarity with reference to the ground.
- Use the bidirectional products for the signal wiring if the
signal swings to positive and negative polarities
centering around the ground.
4. Selection of the TVS diodes that can ESD rating VESD Select a product with a rating value larger than the ESD
withstand ESD as required rating required for the application.
5. Selection of the TVS diodes that can Peak pulse current IPP Select a product with a rating value larger than IPP
withstand overcurrent as required required for the application.
6. Selection of the TVS diodes that can Peak pulse power PPP Select a product with a rating value larger than PPP
withstand overpower as required required for the application.
7. Selection of products with a low Clamping voltage VCL Select a product with VCL as low as possible for VRWM
clamping voltage selected in point 1.
7/14

Application examples
1. Protection of switching systems
Since switches and buttons are touched by the human body when they are operated, ESD may cause damage to the IC or
malfunction. They require protection with the TVS diodes.
8/14
P u s h -b u tto n s w itc h
IN
IN IC
Figure 15. Protection against ESD entering via switches and buttons touched by human body
2. Protection of DC plug/jack system
Hot-plugging (hot swapping) could be used to connect a DC output plug of an AC adapter to electronic equipment. However, the
inductance component of long wiring causes a high-voltage surge when the connection is established. Use the TVS diodes to
provide protection so that the devices inside the equipment are not damaged by the surge voltage. In addition, they also provide
protection against ESD entry caused by the plug and jack being touched by the human body.
Cp oo mw m e
e r s
rc ia
u p p
lly
A C
c
A C
o n
d a
-D
v e
p te r
Crte
r
D C O U T
L o n g w
irin g
C p lu g / ja c
C IN
E le c tro n
ic
q
u
Do
ip
Cn
m e n
-D C
v e rte
Figure 16. Protection when DC plug of AC adapter is connected to electronic equipment using hot plugging
3. Protection of audio system
When wired headphones or headset are plugged into a jack of a mobile device, ESD may occur and damage the inside of the
device if the human body is electrically charged. In addition, the wiring must be protected because the speaker and microphone
inside the device are usually placed on the peripheral part of the device, making them susceptible to ESD.
Portable Devices
Audio Codec IC
Plug / Jack
TVS TVS
Figure 17. Protection of audio system including speaker and microphone

4. Protection of USB 2.0 interface
USB connectors must be protected from ESD because they are frequently touched by the human body when USB cables and
USB devices are plugged in or unplugged.
9/14
U S B H o s t C
o n tro
D +
N D
lle r IC
5
o n n
B U
c to r
Figure 18. Protection of USB 2.0 interface
5. Protection of USB 3.2 interface
To accommodate fast data transfer rates at 5 Gbps for USB 3.2 Gen 1 (earlier USB 3.0 and USB 3.1 Gen 1) and 10 Gbps for USB
3.2 Gen 2 (earlier USB 3.1 Gen 2), use the TVS diodes with a small capacitance between terminals for the communication lines.
VBUS
Receptacle
USB Type C
TVS GND GND
USB Controller IC
RX1+ TX1+
RX1 TX1
VBUS VBUS
SBU2 CC1
D D+
D+ D
CC2 SBU1
VBUS VBUS
TX2 RX2
TX2+ RX2+
GND GND
Figure 19. Protection of USB 3.2 interface

6. Protection of HDMI interface
To accommodate a fast transmission rate at 10.2 Gbps for HDMI 1.4, use the TVS diodes with a small capacitance between
terminals for the TMDS signal lines.
10/14
CT
U
H
o n n
y p e
M D
T M
E C
T IL
C L
D A
5 V
P D
e c to r
S D a ta
D S D a
S C lo c
IT Y
2 +
2 S
2
1 +
1 S
1
ta 0
0 S
k +
k S
h
ie
ld
Figure 20. Protection of HDMI interface

7. Protection of LIN/CXPI interface
To accommodate a slow communication speed for LIN/CXPI of 20 kbps at maximum, a TVS diode with a large capacitance
between terminals may be considered acceptable. However, since the maximum capacitance is limited to 250 pF as the responder
node, care must be taken so that the total capacitance including C1 does not exceed this value.
11/14
T ra
B A T
L IN
n s c e iv
L IN
e r
*
*1 C
μ 0 .1 F
Ω 1 k
1C
1 T V S
o m m a n d e r N o d e : 1 0 0 0 p
e sp o n d e r N o d e : 2 2 0 p F
LC
IN n o d e
o n n e c to
B A T
IN B U S
Figure 21. Protection of LIN/CXPI interface
The figure shows an example for LIN. The same applies to CXPI.
8. Protection of CAN/CAN FD interface
The maximum communication speed is 1 Mbps for CAN and 5 Mbps for CAN-FD. Therefore, provide protection by selecting the
TVS diodes with a capacitance between terminals that will not affect the signal quality.
CT Ara Nn /Cs
A N F D
e iv e r
C A N
S P L
C A N
H
IT
Ω
Ω
CC
Ao
Nn
n
B U S
e c to
_ H
_ L
Figure 22. Protection of CAN/CAN FD interface

9. Protection of automotive Ethernet (LAN) interface
Since the automotive Ethernet performs high-speed communications at 100 Mbps to 1 Gbps, use the TVS diodes with a small
capacitance between terminals. If the ESD protection with the TVS diodes is insufficient, place an ESD suppressor or varistor that
complies with OPEN Alliance standards directly below the automotive connector.
12/14
E th e rn e t P H Y
C o m m o n
M o d e
C h o k e
(C M C )
e c o u p lin g
Fp0074
C oT me
Ωk1
Ωk
Ω 00
k1
m o n M o d
rm in a tio n
(C M T )
In -v e
C o n n
D A +
D A
he ic le
c to r
Figure 23. Protection of automotive Ethernet interface
10. Protection of RS-232C/RS-423 interface
If the I/O of a transceiver IC is not equipped with an ESD protection function, it is necessary to provide protection against ESD by
placing the TVS diodes directly below the connector.
RS-232C
Connector
DCD
DSR
RXD
RTS
RS-232C 7
Transceiver TXD 3
CTS
8
DTR
4
RI
9
5
Figure 24. Protection of RS-232C/RS-423 interface

11. Protection of NFC antenna
An NFC antenna is built in directly under the cover of equipment. This environment is vulnerable to the ESD entry. Therefore, the
ESD protection must be provided.
13/14
N F C IC
X
E M C F ilte r
MN ae tctw h in g
o rk
A n te n n
C o il
Figure 25. Protection of NFC antenna
12. Protection of wireless power supply antenna
A wireless power supply antenna is built in directly under the cover of equipment. This environment is vulnerable to the ESD entry.
Therefore, the ESD protection must be provided.
T ra
Pn o w
s mIC
eis
T X
s io
T X
R X
R X
n
E M C F ilte r
A n te n n
C o il
R e c tific a tio n
_ A N
X 0
R e
X 1
o w e r
c e iv in g
Figure 26. Protection of wireless power supply antenna

13. Snubber circuit for AC-DC converter
This circuit is a pseudo-resonant converter. In this example, an RCD snubber circuit is incorporated to suppress a surge that
occurs in the primary side of the transformer at the moment the MOSFET is turned from ON to OFF. A snubber circuit is usually
configured with a resistor, capacitor, and fast recovery diode (FRD). However, a TVS diode can be connected in parallel with R
and C if a higher protective performance is required. The transient spike noise can be clamped by adding the TVS diode. Check
the switching waveform of the MOSFET to determine whether or not to use the TVS diode. If the voltage applied to this part is
higher than clamping voltage VCL of one TVS diode, connect several TVS diodes with the same item number in series so that the
sum of VCL becomes higher than the voltage applied to this part in order to clamp the transient voltage.
14/14
A C IN
F C
F B
Do C -D
n tro
Clle
S n u
b b e
R D
r C irc u it
M O S F E T
F B F e e d b a c k
O
U T
Figure 27. Clamping transient spike noise by adding TVS diodes to snubber circuit for AC-DC converter
14. Overvoltage protection on the secondary side of a power supply circuit
An overshoot of the output voltage may occur in a power supply circuit for some reason. If the IC is not equipped with an
overvoltage protection (OVP ) function, countermeasures must be taken as needed. Clamp the overvoltage by inserting a TVS
diode for the output of a DC-DC or AC-DC converter. TVS diodes are designed to clamp transient voltages that occur for a short
time (order of nanoseconds), such as ESD and surge waveforms. Therefore, to clamp a voltage in waveforms longer than about
several tens of milliseconds, it is necessary to select a product with a power dissipation of the package larger than the power in
the overvoltage part. In addition, when the overvoltage is continuously applied, for example, due to a short circuit between the
input and output, the TVS diode could be damaged if the power in the overvoltage part exceeds the power dissipation of the
package.
VIN VIN LX VOUT
DC-DC
Converter
GND GND
FB
GND
Figure 28. Overvoltage protection for DC-DC converter output

Notice
Notice
1) The information contained in this document is intended to introduce ROHM Group (hereafter
referred to asROHM) products. When using ROHM products, please verify the latest specifications
or datasheets before use.
2) ROHM products are designed and manufactured for use in general electronic equipment and
applications (such as Audio Visual equipment, Office Automation equipment, telecommunication
equipment, home appliances, amusement devices, etc.) or specified in the datasheets. Therefore,
please contact the ROHM sales representative before using ROHM products in equipment or
devices requiring extremely high reliability and whose failure or malfunction may cause danger or
injury to human life or body or other serious damage (such as medical equipment, transportation,
traffic, aircraft, spacecraft, nuclear power controllers, fuel control, automotive equipment including
car accessories, etc. hereafter referred to as Specific Applications). Unless otherwise agreed in
writing by ROHM in advance, ROHM shall not be in any way responsible or liable for any damages,
expenses, or losses incurred by you or third parties arising from the use of ROHM Products for
Specific Applications.
3) Electronic components, including semiconductors, can fail or malfunction at a certain rate. Please
be sure to implement, at your own responsibilities, adequate safety measures including but not
limited to fail-safe design against physical injury, and damage to any property, which a failure or
malfunction of products may cause.
4) The information contained in this document, including application circuit examples and their
constants, is intended to explain the standard operation and usage of ROHM products, and is not
intended to guarantee, either explicitly or implicitly, the operation of the product in the actual
equipment it will be used. As a result, you are solely responsible for it, and you must exercise your
own independent verification and judgment in the use of such information contained in this
document. ROHM shall not be in any way responsible or liable for any damages, expenses, or
losses incurred by you or third parties arising from the use of such information.
5) When exporting ROHM products or technologies described in this document to other countries, you
must abide by the procedures and provisions stipulated in all applicable export laws and regulations,
such as the Foreign Exchange and Foreign Trade Act and the US Export Administration
Regulations, and follow the necessary procedures in accordance with these provisions.
6) The technical information and data described in this document, including typical application circuits,
are examples only and are not intended to guarantee to be free from infringement of third parties
intellectual property or other rights. ROHM does not grant any license, express or implied, to
implement, use, or exploit any intellectual property or other rights owned or controlled by ROHM or
any third parties with respect to the information contained herein.
7) No part of this document may be reprinted or reproduced in any form by any means without the
prior written consent of ROHM.
8) All information contained in this document is current as of the date of publication and subject to
change without notice. Before purchasing or using ROHM products, please confirm the latest
information with the ROHM sales representative.
9) ROHM does not warrant that the information contained herein is error-free. ROHM shall not be in
any way responsible or liable for any damages, expenses, or losses incurred by you or third parties
resulting from errors contained in this document.
Thank you for your accessing to ROHM prod uct informations.
More detail product informations and catalogs are available, please contact us.
ROHM Customer Support System
https://www.rohm.com/contactus
www.rohm.com
R2043A
© 2023 ROHM Co., Ltd. All rights reserved.