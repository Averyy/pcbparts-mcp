---
source: "Microchip AN228 -- A CAN Physical Layer Discussion"
url: "https://ww1.microchip.com/downloads/en/appnotes/00228a.pdf"
format: "PDF 12pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 24797
---

M
AN228
A CAN Physical Layer Discussion
The Physical Medium Attachment (PMA) and Medium
Author: Pat Richards
Dependent Interface (MDI) are the two parts of the
Microchip Technology Inc.
physical layer which are not defined by CAN. The
Physical Signaling (PS) portion of the physical layer is
INTRODUCTION
defined by the CAN specification. The system designer
can choose any driver/receiver and transport medium
Many network protocols are described using the seven
layer Open System Interconnection (OSI) model, as as long as the PS requirements are met.
shown in Figure1. The Controller Area Network (CAN) The International Standards Organization (ISO) has
protocol defines the Data Link Layer and part of the defined a standard which incorporates the CAN speci-
Physical Layer in the OSI model. The remaining physi- fication as well as the physical layer. The standard,
cal layer (and all of the higher layers) are not defined by ISO-11898, was originally created for high-speed in-
the CAN specification. These other layers can either be vehicle communications using CAN. ISO-11898 speci-
defined by the system designer, or they can be imple- fies the physical layer to ensure compatibility between
mented using existing non-proprietary Higher Layer CAN transceivers.
Protocols (HLPs) and physical layers.
A CAN controller typically implements the entire CAN
The Data Link Layer is defined by the CAN specifica- specification in hardware, as shown in Figure1. The
tion. The Logical Link Control (LLC) manages the over- PMA is not defined by CAN, however, it is defined by
load control and notification, message filtering and ISO-11898. This document discusses the MCP2551
recovery management functions. The Medium Access CAN transceiver and how it fits in with the ISO-11898
Control (MAC) performs the data encapsulation/decap- specification.
sulation, error detection and control, bit stuffing/de-
stuffing and the serialization and deserialization
functions.
FIGURE 1: CAN AND THE OSI MODEL
7- Layer OSI
Application
Presentation
Session
Logical Link Control (LLC)
Transport - Acceptance filtering
- Overload notification
Network - Recovery management
Data Link
Medium Access Control (MAC)
- Data encapsulation/decapsulation
Physical Defined by CAN Controller
- Frame coding (stuffing/de-stuffing)
- Error detection/signaling
- Serialization/deserialization
Physical Signaling
- Bit encoding/decoding
ISO11898
- Bit timing/synchronization
Physical Medium Attachment
Transceiver
- Driver/receiver characteristics
MCP2551
Medium Dependent Interface
- Connectors/wires
 2002 Microchip Technology Inc. Preliminary DS00228A-page 1

ISO11898-2 OVERVIEW FIGURE 2: DIFFERENTIAL BUS
ISO11898 is the international standard for high-speed
CAN communications in road vehicles. ISO-11898-2
specifies the PMA and MDA sublayers of the Physical
Layer. See Figure3 for a representation of a common
CAN node/bus as described by ISO-11898.
Bus Levels
CAN specifies two logical states: recessive and domi-
nant. ISO-11898 defines a differential voltage to repre-
sent recessive and dominant states (or bits), as shown
in Figure2.
In the recessive state (i.e., logic ‘1’ on the MCP2551
TXD input), the differential voltage on CANH and CANL
is less than the minimum threshold (<0.5V receiver
input or <1.5V transmitter output)(See Figure4).
Connectors and Wires
In the dominant state (i.e., logic ‘0’ on the MCP2551
TXD input), the differential voltage on CANH and CANL ISO-11898-2 does not specify the mechanical wires
is greater than the minimum threshold. A dominant bit and connectors. However, the specification does
overdrives a recessive bit on the bus to achieve require that the wires and connectors meet the electri-
nondestructive bitwise arbitration. cal specification.
The specification also requires 120Ω (nominal) termi-
nating resistors at each end of the bus. Figure3 shows
an example of a CAN bus based on ISO-11898.
FIGURE 3: CAN BUS
DS00228A-page 2 Preliminary  2002 Microchip Technology Inc.
)V(
leveL
egatloV
Dominant
CANH
Recessive Recessive
VDIFF
CANL
Time (t)
MCU
CAN Controller
Transceiver
Node Node
120Ω 120Ω

FIGURE 4: ISO11898 NOMINAL BUS LEVELS
V
3.5
2.5
1.5
V V
5.0
Dominant 3.0 Dominant
Differential Differential
Output Input
Range 1.5 Range
0.9
0.5
Recessive
0.05 Recessive
Differential
Differential
Output
-0.5 Input
Range
Range
-1.0
Robustness communications of the CAN node. The transceiver
must survive short circuits on the CAN bus inputs from
The ISO11898-2 specification requires that a compliant -3V to +32V and transient voltages from -150V to
or compatible transceiver must meet a number of elec- +100V. Table1 shows the major ISO11898-2 electrical
trical specifications. Some of these specifications are
requirements, as well as MCP2551 specifications.
intended to ensure the transceiver can survive harsh
electrical conditions, thereby protecting the
TABLE 1: COMPARING THE MCP2551 TO ISO11898-2
ISO-11898-4 MCP2551
Parameter Unit Comments
min max min max
DC Voltage on CANH and CANL -3 +32 -40 +40 V Exceeds ISO-11898
Transient voltage on CANH and CANL -150 +100 -250 +250 V Exceeds ISO-11898
Common Mode Bus Voltage -2.0 +7.0 -12 +12 V Exceeds ISO-11898
Recessive Output Bus Voltage +2.0 +3.0 +2.0 +3.0 V Meets ISO-11898
Recessive Differential Output Voltage -500 +50 -500 +50 mV Meets ISO-11898
Differential Internal Resistance 10 100 20 100 kΩ Meets ISO-11898
Common Mode Input Resistance 5.0 50 5.0 50 kΩ Meets ISO-11898
Differential Dominant Output Voltage +1.5 +3.0 +1.5 +3.0 V Meets ISO-11898
Dominant Output Voltage (CANH) +2.75 +4.50 +2.75 +4.50 V Meets ISO-11898
Dominant Output Voltage (CANL) +0.50 +2.25 +0.50 +2.25 V Meets ISO-11898
Permanent Dominant Detection (Driver) Not Required 1.25 — ms
Power-On Reset and Brown-Out Detection Not Required Yes --
 2002 Microchip Technology Inc. Preliminary DS00228A-page 3

Bus Lengths the same bit time. Figure5 shows a one-way propaga-
tion delay between two nodes. Extreme propagation
ISO11898 specifies that a transceiver must be able to
delays (beyond the sample point) will result in invalid
drive a 40m bus at 1Mb/s. A longer bus length can be arbitration. This implies that bus lengths are limited at
achieved by slowing the data rate. The biggest limita- given CAN data rates.
tion to bus length is the transceiver’s propagation
A CAN system’s propagation delay is calculated as
delay.
being a signal’s round-trip time on the physical bus
PROPAGATION DELAY (tbus), the output driver delay (tdrv) and the input com-
parator delay (tcmp). Assuming all nodes in the system
The CAN protocol has defined a recessive (logic ‘1’) have similar component delays, the propagation delay
and dominant (logic ‘0’) state to implement a non- is explained mathematically:
destructive bit-wise arbitration scheme. It is this arbitra-
tion methodology that is affected most by propagation
EQUATION 1:
delays. Each node involved with arbitration must be
able to sample each bit level within the same bit time.
tprop = 2⋅(tbus+tcmp+tdrv)
For example, if two nodes at opposite ends of the bus
start to transmit their messages at the same time, they
must arbitrate for control of the bus. This arbitration is
only effective if both nodes are able to sample during
FIGURE 5: ONE-WAY PROPAGATION DELAY
Transmitted Bit from “Node A”
SyncSeg PropSeg PhaseSeg1 (PS1) PhaseSeg2 (PS2)
Sample Point
Propagation Delay
“Node A” bit received by “Node B”
SyncSeg PropSeg PhaseSeg1 (PS1) PhaseSeg2 (PS2)
Time (t)
DS00228A-page 4 Preliminary  2002 Microchip Technology Inc.

MCP2551 CAN TRANSCEIVER General MCP2551 Operation
The MCP2551 is a CAN Transceiver that implements TRANSMIT
the ISO-11898-2 physical layer specification. It sup-
ports a 1 Mb/s data rate and is suitable for 12 V and 24 The CAN protocol controller outputs a serial data
V systems. The MCP2551 provides short-circuit stream to the logic TXD input of the MCP2551. The cor-
protection up to ±40V and transient protection up to responding recessive or dominant state is output on the
±250V. CANH and CANL pins.
In addition to being ISO-11898-2-compatible, the RECEIVE
MCP2551 provides power-on reset and brown-out pro-
tection, as well as permanent dominant detection to The MCP2551 receives dominant or recessive states
ensure an unpowered or faulty node will not disturb the on the same CANH and CANL pins as the transmit
bus. The device implements configurable slope control occurs. These states are output as logic levels on the
on the bus pins to help reduce RFI emissions. Figure RXD pin for the CAN protocol controller to receive CAN
6 shows the block diagram of the MCP2551. frames.
RECESSIVE STATE
A logic ‘1’ on the TXD input turns off the drivers to the
CANH and CANL pins and the pins “float” to a nominal
2.5V via biasing resistors.
DOMINANT STATE
A logic ‘0’ on the TXD input turns on the CANH and
CANL pin drivers. CANH drives ~1V higher than the
nominal 2.5V recessive state to ~3.5V. CANL drives
~1V less than the nominal 2.5V recessive state to
~1.5V.
FIGURE 6: MCP2551 BLOCK DIAGRAM
VDD
TXD Thermal
Dominant Shutdown
VDD Detect
TXD Driver
Control
Slope Power-On CANH
RS
Control Reset
0.5VDD
RXD GND
Receiver
Reference
VREF
Voltage
VSS
 2002 Microchip Technology Inc. Preliminary DS00228A-page 5

Modes of Operation STANDBY
There are three modes of operation that are externally Standby (or sleep) mode is entered by connecting the
controlled via the RS pin: RS pin to VDD. In sleep mode, the transmitter is
switched off and the receiver operates in a reduced
1. High-Speed
power mode. While the receive pin (RXD) is still
2. Slope Control
functional, it will operate at a slower rate.
3. Standby
Standby mode can be used to place the device in low
HIGH-SPEED power mode and to turn off the transmitter in case the
CAN controller malfunctions and sends unexpected
The high-speed mode is selected by connecting the RS data to the bus.
pin to VSS. In this mode, the output drivers have fast
rise and fall times that support the higher bus rates up Permanent Dominant Detection on
to 1Mb/s and/or maximum bus lengths by providing the Transmitter
minimum transceiver loop delays.
The MCP2551 will turn off the transmitter to CANH and
SLOPE CONTROL CANL if an extended dominant state is detected on the
transmitter. This ability prevents a faulty node (CAN
If reduced EMI is required, the MCP2551 can be placed
controller or MCP2551) from permanently corrupting
in slope control mode by connecting a resistor (REXT)
the CAN bus.
from the RS pin to ground. In slope control mode, the
single-ended slew rate (CANH or CANL) is basically The drivers are disabled if TXD is low for more than
proportional to the current out of the RS pin. The current ~1.25ms (minimum) (See Figure7).
must be in the range of 10µA < -IRS < 200µA, which The drivers will remain disabled as long as TXD
corresponds to a voltage on the pin of 0.4VDD < VRS < remains low. A rising edge on TXD will reset the timer
0.6VDD respectively (or 0.5VDD typical). logic and enable the drivers.
The decreased slew rate implies a slower CAN data
rate at a given bus length, or a reduced bus length at a
given CAN data rate.
FIGURE 7: TXD PERMANENT DOMINANT DETECTION
Transmitter
Enabled
tDOM
TXD
Transmitter
Disabled
Recessive Recessive
Dominant Dominant
DS00228A-page 6 Preliminary  2002 Microchip Technology Inc.

Power-On Reset and Brown-Out CANH and CANL pins will remain in high impedance
until TXD goes high. After which, the drivers will
The MCP2551 incorporates both Power-On Reset
function normally.
(POR) and Brown-Out Detection (BOD) (see Figure8).
BROWN-OUT DETECTION (BOD)
POWER-ON RESET (POR)
BOD occurs when VDD goes below the power-on reset
When the MCP2551 is powered on, the CANH and
low voltage (VPORL). At this point, the CANH and CANL
CANL pins remain in the high impedance state until
pins enter a high impedance state and will remain there
VDD reaches the POR high voltage (VPORH). until VPORH is reached.
Additionally, if the TXD pin is low at power-up, the
FIGURE 8: POWER-ON RESET AND BROWN-OUT DETECTION
4.0
VPORH
POR
D
D
3.5
VPORL
BOD
3.0
t
TXD
High High
Impedance Impedance
 2002 Microchip Technology Inc. Preliminary DS00228A-page 7

Ground Offsets (2.5V typical). However, the resulting common mode
voltage in the recessive state becomes 6.25V for the
Since it is not required to provide a common ground
receiving node and -1.25V for the transmitting node.
between nodes, it is possible to have ground offsets
Figure10 shows the transmitting node with a negative
between nodes. That is, each node may observe differ-
ground offset with respect to the receiving node. The
ent single-ended bus voltages (common mode bus
MCP2551 receiver can operate with CANL = -12V. The
voltages) while maintaining the same differential volt-
age. While the MCP2551 is specified to handle ground
minimum CAN dominant output voltage (VO(CANL))
from the transmitting node is 0.5V. Subtracting this min-
offsets from -12V to +12V, the ISO-11898 specification
imum yields an actual ground offset, with respect to the
only requires -2V to +7V. Figure9 and Figure10
receiving node, of -12.5V. The common mode voltage
demonstrate how ground offsets appear between
for the recessive state is -6.25V for the receiving node
nodes.
and 6.25V for the transmitting node.
Figure9 shows the transmitting node with a positive
Since all nodes act as a transmitter for a portion of each
ground offset with respect to the receiving node. The
message (i.e., each receiver must acknowledge (ACK)
MCP2551 receiver can operate with CANH = +12V.
valid messages during the ACK slot), the largest
The maximum CAN dominant output voltage
ground offset allowed between nodes is 7.5V, as shown
(VO(CANH)) from the transmitting node is 4.5V. Subtract-
in Figure9.
ing this maximum yields an actual ground offset (with
respect to the receiving node) of 7.5V for the transmit- Operating a CAN system with large ground offsets can
ting node. In the recessive state, each node attempts to lead to increased electromagnetic emissions. Steps
pull the CANH and CANL pins to their biasing levels must be taken to eliminate ground offsets if the system
is sensitive to emissions.
FIGURE 9: RECEIVING (NODE GROUND) BELOW TRANSMITTING (NODE GROUND)
Common Mode
Bus Voltage
(Single Ended)
12
VO(CANH)(max)VDIFF(max)
4.5V 3V
Transmitting Node Ground
-1.25V
6
CANL 12V
7.5V
6.25V
0
Receiving Node Ground
DS00228A-page 8 Preliminary  2002 Microchip Technology Inc.

FIGURE 10: RECEIVING (NODE GROUND) ABOVE TRANSMITTING (NODE GROUND)
Common Mode
Bus Voltage
(Single-Ended)
Receiving Node Ground
0
-6.25V
12.5V -12V
-6 CANH
6.25V
VDIFF(max)
VO(CANL)(max) 3V
0.5V
-13 Transmitting Node Ground
BUS TERMINATION Standard Termination
Bus termination is used to minimize signal reflection on As the name implies, this termination uses a single
the bus. ISO-11898 requires that the CAN bus have a 120Ω resistor at each end of the bus. This method is
nominal characteristic line impedance of 120Ω. There- acceptable in many CAN systems.
fore, the typical terminating resistor value for each end
of the bus is 120Ω. There are a few different termination Split Termination
methods used to help increase EMC performance (see
Split termination is a concept that is growing in popular-
Figure11).
ity because emission reduction can be achieved very
1. Standard Termination easily. Split termination is a modified standard termina-
2. Split Termination tion in which the single 120Ω resistor on each end of
the bus is split into two 60Ω resistors, with a bypass
3. Biased Split Termination
capacitor tied between the resistors and to ground. The
Note: EMC performance is not determined solely two resistors should match as close as possible.
by the transceiver and termination method,
but rather by careful consideration of all
components and topology of the system.
 2002 Microchip Technology Inc. Preliminary DS00228A-page 9

Biased Split Termination REFERENCES
This termination method is used to maintain the com- MCP2551 Data Sheet, “High Speed CAN Transceiver”,
mon mode recessive voltage at a constant value, DS21667, Microchip Technology, Inc.
thereby increasing EMC performance. This circuit is
AN754, “Understanding Microchip’s CAN Module Bit
the same as the split termination with the addition of a
Timing”, DS00754, Microchip Technology, Inc.
voltage divider circuit to achieve a voltage of VDD/2
between the two 60Ω resistors (see Figure11). ISO-11898-2, “Road Vehicles - Interchange of Digital
Information - Part 2: High Speed Medium Access Unit
Note: The biasing resistors in Figure11, as well and Medium Dependant Interface”, International
as the split termination resistors, should Organization for Standardization.
match as close as possible.
CAN System Engineering, “From Theory to Practical
Applications”, Wolfhard Lawrenz, Springer.
FIGURE 11: TERMINATION
CONCEPTS
Standard
120Ω
Termination
60Ω
Split
C
60Ω
R1 60Ω
Biased
Split
C
R2 60Ω
DS00228A-page 10 Preliminary  2002 Microchip Technology Inc.

Note the following details of the code protection feature on Microchip devices:
• Microchip products meet the specification contained in their particular Microchip Data Sheet.
• Microchip believes that its family of products is one of the most secure families of its kind on the market today, when used in the
intended manner and under normal conditions.
• There are dishonest and possibly illegal methods used to breach the code protection feature. All of these methods, to our knowl-
edge, require using the Microchip products in a manner outside the operating specifications contained in Microchip's Data
Sheets. Most likely, the person doing so is engaged in theft of intellectual property.
• Microchip is willing to work with the customer who is concerned about the integrity of their code.
• Neither Microchip nor any other semiconductor manufacturer can guarantee the security of their code. Code protection does not
mean that we are guaranteeing the product as “unbreakable.”
Code protection is constantly evolving. We at Microchip are committed to continuously improving the code protection features of our
products.
Information contained in this publication regarding device Trademarks
applications and the like is intended through suggestion only
and may be superseded by updates. It is your responsibility to The Microchip name and logo, the Microchip logo, KEELOQ,
ensure that your application meets with your specifications. MPLAB, PIC, PICmicro, PICSTART and PRO MATE are
No representation or warranty is given and no liability is registered trademarks of Microchip Technology Incorporated
assumed by Microchip Technology Incorporated with respect in the U.S.A. and other countries.
to the accuracy or use of such information, or infringement of
FilterLab, microID, MXDEV, MXLAB, PICMASTER, SEEVAL
patents or other intellectual property rights arising from such
and The Embedded Control Solutions Company are
use or otherwise. Use of Microchip’s products as critical com-
registered trademarks of Microchip Technology Incorporated
ponents in life support systems is not authorized except with
in the U.S.A.
express written approval by Microchip. No licenses are con-
veyed, implicitly or otherwise, under any intellectual property
dsPIC, dsPICDEM.net, ECONOMONITOR, FanSense,
rights.
FlexROM, fuzzyLAB, In-Circuit Serial Programming, ICSP,
ICEPIC, microPort, Migratable Memory, MPASM, MPLIB,
MPLINK, MPSIM, PICC, PICDEM, PICDEM.net, rfPIC, Select
Mode and Total Endurance are trademarks of Microchip
Technology Incorporated in the U.S.A. and other countries.
Serialized Quick Turn Programming (SQTP) is a service mark
of Microchip Technology Incorporated in the U.S.A.
All other trademarks mentioned herein are property of their
respective companies.
© 2002, Microchip Technology Incorporated, Printed in the
U.S.A., All Rights Reserved.
Printed on recycled paper.
Microchip received QS-9000 quality system
certification for its worldwide headquarters,
design and wafer fabrication facilities in
Chandler and Tempe, Arizona in July 1999
and Mountain View, California in March 2002.
The Company’s quality system processes and
procedures are QS-9000 compliant for its
PICmicro® 8-bit MCUs, KEELOQ® code hopping
devices, Serial EEPROMs, microperipherals,
non-volatile memory and analog products. In
addition, Microchip’s quality system for the
design and manufacture of development
systems is ISO 9001 certified.
 2002 Microchip Technology Inc. DS00228A - page 11

M
WORLDWIDE SALES AND SERVICE
AMERICAS ASIA/PACIFIC Japan
Corporate Office Australia Microchip Technology Japan K.K.
Benex S-1 6F
2355 West Chandler Blvd. Microchip Technology Australia Pty Ltd
3-18-20, Shinyokohama
Chandler, AZ 85224-6199 Suite 22, 41 Rawson Street
Kohoku-Ku, Yokohama-shi
Tel: 480-792-7200 Fax: 480-792-7277 Epping 2121, NSW
Kanagawa, 222-0033, Japan
Technical Support: 480-792-7627 Australia
Tel: 81-45-471- 6166 Fax: 81-45-471-6122
Web Address: http://www.microchip.com Tel: 61-2-9868-6733 Fax: 61-2-9868-6755
Korea
Rocky Mountain China - Beijing
Microchip Technology Korea
2355 West Chandler Blvd. Microchip Technology Consulting (Shanghai) 168-1, Youngbo Bldg. 3 Floor
Chandler, AZ 85224-6199 Co., Ltd., Beijing Liaison Office Samsung-Dong, Kangnam-Ku
Tel: 480-792-7966 Fax: 480-792-4338 Unit 915 Seoul, Korea 135-882
Bei Hai Wan Tai Bldg.
Atlanta Tel: 82-2-554-7200 Fax: 82-2-558-5934
No. 6 Chaoyangmen Beidajie
500 Sugar Mill Road, Suite 200B Beijing, 100027, No. China Singapore
Atlanta, GA 30350 Tel: 86-10-85282100 Fax: 86-10-85282104 Microchip Technology Singapore Pte Ltd.
Tel: 770-640-0034 Fax: 770-640-0307 200 Middle Road
China - Chengdu
Boston Microchip Technology Consulting (Shanghai) #07-02 Prime Centre
Singapore, 188980
2 Lan Drive, Suite 120 Co., Ltd., Chengdu Liaison Office Tel: 65-6334-8870 Fax: 65-6334-8850
Westford, MA 01886 Rm. 2401, 24th Floor,
Tel: 978-692-3848 Fax: 978-692-3821 Ming Xing Financial Tower Taiwan
Microchip Technology (Barbados) Inc.,
Chicago No. 88 TIDU Street
Chengdu 610016, China Taiwan Branch
333 Pierce Road, Suite 180 Tel: 86-28-86766200 Fax: 86-28-86766599 11F-3, No. 207
Itasca, IL 60143 Tung Hua North Road
Tel: 630-285-0071 Fax: 630-285-0075 China - Fuzhou Taipei, 105, Taiwan
Dallas Microchip Technology Consulting (Shanghai) Tel: 886-2-2717-7175 Fax: 886-2-2545-0139
Co., Ltd., Fuzhou Liaison Office
4570 Westgrove Drive, Suite 160
Unit 28F, World Trade Plaza EUROPE
Addison, TX 75001
Tel: 972-818-7423 Fax: 972-818-2924 No. 71 Wusi Road Austria
Fuzhou 350001, China
Detroit Tel: 86-591-7503506 Fax: 86-591-7503521 Microchip Technology Austria GmbH
Durisolstrasse 2
Tri-Atria Office Building China - Shanghai
A-4600 Wels
32255 Northwestern Highway, Suite 190 Microchip Technology Consulting (Shanghai)
Farmington Hills, MI 48334 Co., Ltd. A Te u l s : t 4 ri 3 a -7242-2244-399
Tel: 248-538-2250 Fax: 248-538-2260 Room 701, Bldg. B Fax: 43-7242-2244-393
Kokomo Far East International Plaza Denmark
2767 S. Albright Road No. 317 Xian Xia Road Microchip Technology Nordic ApS
Kokomo, Indiana 46902 Shanghai, 200051 Regus Business Centre
Tel: 765-864-8360 Fax: 765-864-8387 Tel: 86-21-6275-5700 Fax: 86-21-6275-5060 Lautrup hoj 1-3
Los Angeles China - Shenzhen Ballerup DK-2750 Denmark
18201 Von Karman, Suite 1090 Microchip Technology Consulting (Shanghai) Tel: 45 4420 9895 Fax: 45 4420 9910
Irvine, CA 92612 Co., Ltd., Shenzhen Liaison Office France
Rm. 1315, 13/F, Shenzhen Kerry Centre,
Tel: 949-263-1888 Fax: 949-263-1338 Microchip Technology SARL
Renminnan Lu
Parc d’Activite du Moulin de Massy
San Jose Shenzhen 518001, China 43 Rue du Saule Trapu
Microchip Technology Inc. Tel: 86-755-82350361 Fax: 86-755-82366086
Batiment A - ler Etage
2107 North First Street, Suite 590 China - Hong Kong SAR 91300 Massy, France
San Jose, CA 95131 Microchip Technology Hongkong Ltd. Tel: 33-1-69-53-63-20 Fax: 33-1-69-30-90-79
Tel: 408-436-7950 Fax: 408-436-7955
Unit 901-6, Tower 2, Metroplaza Germany
Toronto 223 Hing Fong Road Microchip Technology GmbH
6285 Northam Drive, Suite 108 Kwai Fong, N.T., Hong Kong Steinheilstrasse 10
Mississauga, Ontario L4V 1X5, Canada Tel: 852-2401-1200 Fax: 852-2401-3431 D-85737 Ismaning, Germany
Tel: 905-673-0699 Fax: 905-673-6509 India Tel: 49-89-627-144 0 Fax: 49-89-627-144-44
Microchip Technology Inc. Italy
India Liaison Office Microchip Technology SRL
Divyasree Chambers Centro Direzionale Colleoni
1 Floor, Wing A (A3/A4) Palazzo Taurus 1 V. Le Colleoni 1
No. 11, O’Shaugnessey Road 20041 Agrate Brianza
Bangalore, 560 025, India Milan, Italy
Tel: 91-80-2290061 Fax: 91-80-2290062 Tel: 39-039-65791-1 Fax: 39-039-6899883
United Kingdom
Microchip Ltd.
505 Eskdale Road
Winnersh Triangle
Wokingham
Berkshire, England RG41 5TU
Tel: 44 118 921 5869 Fax: 44-118 921-5820
10/18/02
DS00228A-page 12  2002 Microchip Technology Inc.