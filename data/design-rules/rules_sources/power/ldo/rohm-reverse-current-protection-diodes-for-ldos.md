---
source: "ROHM -- Reverse Current Protection Diodes for LDOs"
url: "https://fscdn.rohm.com/en/products/databook/applinote/common/how_to_choose_reverse_current_protection_diode_for_ldo_an-e.pdf"
format: "PDF 6pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 15718
---

2017.4
Application Note
Linear regulator
How to Select Reverse Current Protection
Diodes for LDO Regulators
LDO regulators allow reverse current to flow inside the IC chip from the output pin to the input pin when the input/output voltage
is reversed. To prevent damage to the IC, normally connect a reverse current protection diode outside the IC. This application
note provides guidelines on whether a protection diode is necessary and how to select a diode.
1. Guidelines on whether or not a protection diode is necessary
Table 1 shows the guidelines as to whether or not a protective diode is necessary for each case. Note, however, that the guidelines
vary depending on the type of output transistor. For details on each item, see the reference sections provided in the table.
Table 1. Table for determining whether or not a protective diode is necessary
Protection diode necessary or not
Bipolar type MOSFET type
Output transistor type →
→ Refer to Section 4-1. → Refer to Section 4-2.
When voltage drops rapidly on the input side - Necessary, but not necessary
Case 1 - Necessary
→ Refer to Section 5-1. depending on the conditions
When reverse current always flows
Case 2 - Necessary - Necessary
→ Refer to Section 5-2.
When the input is open
Case 3 - Not necessary - Not necessary
→ Refer to Section 5-3.
2. Selection of the protection circuit
There are two ways to make a protection circuit: inserting a diode on the input side of the LDO to prevent reverse current (Figure
1) or placing a diode between the input and the output to bypass reverse current (Figure 2). The advantage and disadvantage of
each protection circuit are shown in Table 2. Use a circuit that is suitable for your application.
Table 2. Types of protection circuits and their advantage and disadvantage
Reverse current prevention circuit Reverse current bypass circuit
Circuit diagram

1/5
January 2024
V IN
C
IN
L D
O
O U T
IR
E V E R S E
V
O U
T
U T
LDO
I
REVERSE
V IN OUT V IN OUT
C C
IN OUT
Figure 1 Figure 2
- Reverse current flow to the circuit of the - The dropout voltage of the LDO is not affected.
Advantage
previous stage can be prevented.
- The input/output voltage difference necessary - Reverse current flows into the circuit of the
for operations becomes large since the forward previous stage.
Disadvantage
voltage of the diode is added to the dropout
voltage of the LDO.

How to Select Reverse Current Protection Diodes for LDO Regulators Application Note
3. Selection of the diode
Table 3 summarizes the types of diodes used in the two types of protection circuits described in the previous section and the
requirements for their electrical characteristics.
Table 3. Diode types and requirements for electrical characteristics
Reverse current prevention circuit Reverse current bypass circuit
REVERSE
V IN OUT V
C C
2/5
L D
IR
E V E
R S EV
Diode types - Schottky barrier diode - Schottky barrier diode
- Rectifier diode
- Switching diode
Reverse voltage VR - Use at 80% or less of the absolute maximum - Use at 80% or less of the absolute
rating. maximum rating.
Forward current IO - Use at 50% or less of the absolute maximum - Use at 50% or less of the absolute
rating. maximum rating.
Forward voltage VF - Select a product with a value that can be - Select a product with a value of
tolerated in the application. approximately 0.7 V or less.
Reverse current IR - Select a product with a value that can be - Select a product with a value of 1 µA or less.
tolerated in the application. - ROHM offers a lineup of ultra-small IR
products, among which typical product
names are listed in Table 4.
3-1. Reverse current prevention circuit temperature rises to several tens of mA in some products.
Figure 3 is an example of an LDO with a shutdown switch
As for the diode types, a Schottky barrier diode and rectifier
function, where current flows into the load because of the
diode are often used considering the electrical characteristics
reverse current IR in the diode and because the input voltage
and cost, although a rectifier diode, Schottky barrier diode, fast
is applied even though the LDO output is turned off. This may
recovery diode, and switching diode can all be used. For small
cause a malfunction in the circuit of the subsequent stage. In
currents of 100 mA or less, a switching diode can also be used.
addition, the LDO allows a leakage current to always flow from
Although a fast recovery diode can also be used, its
the input to the output during normal operation, which may
characteristics are excessive for this application.
deteriorate the voltage regulation characteristics. Thus, it is
If there is a margin for dropout voltage between input and necessary to select a product with a small IR. Recommended
output, a rectifier diode can be used. If there is not enough Schottky barrier diodes are shown in Table 4.
margin, use a Schottky barrier diode with a low forward
voltage; however, note that the reverse current increases I R
exponentially at high temperatures.
3-2. Reverse current bypass circuit
V IN OUT
Since it is necessary for the bypass diode to turn on (conduct) V OUT
EN
before the parasitic elements inside the IC, use a Schottky C IN GND C OUT R LOAD
barrier diode with a low forward voltage. Shutdown
A Schottky barrier diode has a large reverse current IR, which Figure 3. Current flows into the load because of the reverse
causes the current to increase exponentially as the
current IR in the diode even though the LDO output is shut
down.

Table 4. Ultra-small IR Schottky barrier diodes
Absolute maximum ratings Forward voltage Reverse current
Package
Part No. See Reverse Forward Typ. Max. Max. AEC-Q101
voltage current
Figure 4
VR [V] IO [A]
VF [V] VF [V] IR [µA]
RB168VWM-30 30 1 0.64 (1A) 0.69 (1A) 0.6 (30V) −
RB168VWM-30TF 30 1 0.64 (1A) 0.69 (1A) 0.6 (30V) ✓
RB168VWM-40 40 1 0.64 (1A) 0.69 (1A) 0.5 (40V) −
RB168VWM-40TF 40 1 0.64 (1A) 0.69 (1A) 0.5 (40V) ✓
RB168VWM-60 60 1 0.71 (1A) 0.76 (1A) 0.5 (60V) −
RB168VWM-60TF 60 1 0.71 (1A) 0.76 (1A) 0.5 (60V) ✓
PMDE
RB068VWM-30 30 2 0.70 (2A) 0.75 (2A) 0.6 (30V) −
RB068VWM-30TF 30 2 0.70 (2A) 0.75 (2A) 0.6 (30V) ✓
RB068VWM-40 40 2 0.74 (2A) 0.79 (2A) 0.5 (40V) −
RB068VWM-40TF 40 2 0.74 (2A) 0.79 (2A) 0.5 (40V) ✓
RB068VWM-60 60 2 0.79 (2A) 0.84 (2A) 0.5 (60V) −
RB068VWM-60TF 60 2 0.79 (2A) 0.84 (2A) 0.5 (60V) ✓
RB168MM-30 30 1 0.64 (1A) 0.69 (1A) 0.6 (30V) −
RB168MM-30TF 30 1 0.64 (1A) 0.69 (1A) 0.6 (30V) ✓
RB168MM-40 40 1 0.60 (1A) 0.65 (1A) 0.55 (40V) −
RB168MM-40TF 40 1 0.60 (1A) 0.65 (1A) 0.55 (40V) ✓
RB068MM-30 30 2 0.65 (2A) 0.7 (2A) 0.8 (30V) −
PMDU
RB068MM-30TF 30 2 0.65 (2A) 0.7 (2A) 0.8 (30V) ✓
RB068MM-40 40 2 0.675 (2A) 0.725 (2A) 0.55 (40V) −
RB068MM-40TF 40 2 0.675 (2A) 0.725 (2A) 0.55 (40V) ✓
RB068MM100 100 2 0.82 (2A) 0.87 (2A) 0.4 (100V) −
RB068MM100TF 100 2 0.82 (2A) 0.87 (2A) 0.4 (100V) ✓
RSX048LAP2S 200 3 0.80 (3A) 0.87 (3A) 0.2 (200V) −
PMDTP
RSX088LAP2S 200 5 0.84 (5A) 0.92 (5A) 0.2 (200V) −
As of January 2024
PMDE PMDU (SOD-123FL, SC-109B) PMDTP (SOD-128)
1.3 1.6 0.8 2.5 1.0
0.88 0.95
2 5 65
.2 .2 .2.3
8 7
.3 .4
0.65 0.17
0.9 0.1
0.2
1.75
Figure 4. Package dimensions and appearance
3/5

4. Output transistor types
There are two types of output transistors for LDO regulators,
the bipolar type and the MOSFET type, each of which has
different guidelines. ROHM’s bipolar type LDO regulators have
product names that start with “BA,” and MOSFET type LDO
regulators start with “BD,” “BU,” or “BH.”
4-1. Bipolar type
Figure 5 shows the block diagram. When viewing the input
side from the output side, there may be a pn junction that
functions as a parasitic diode due to the manufacturing
structure of the silicon wafer. Since this parasitic diode is not
designed as an electrical circuit, the device may be damaged,
or the circuit may malfunction when current flows through it.
For the bipolar type, be sure to implement countermeasures
to prevent the flow of reverse current.
4/5
n
R E F
+
p
Figure 5. Block diagram of bipolar type LDO
Example of output with PNP transistor
4-2. MOSFET type
Figure 6 shows the block diagram. There is a body diode in
the output MOSFET, through which reverse current flows.
Figure 7 is a sectional view of a P-channel MOSFET. The body
diode exists as a parasitic element at the pn junction between
the drain and the back gate. Since the device size of this body
diode is the same as the output transistor, a certain amount of
current can be tolerated.
B o
d y d io d e
R E F
Figure 6. Block diagram of MOSFET type LDO
Example of output with P-channel MOSFET
BG aa
n
c k
te
S
p +
p
n -w
-s u b
G
e ll
s tra te
D
p +
B o d y d io d e
Figure 7. Sectional structure of P-channel MOSFET
5. Case-specific guidelines
This section describes for each case whether or not a
protective diode is necessary.
5-1. When voltage drops rapidly on the
input side
This is a common case. When the voltage of the power supply
circuit of the previous stage of the LDO drops rapidly at power
down, the voltage between the input and the output is
temporarily reversed, causing reverse current IREVERSE to flow.
This is because the charge remains in the capacitors
connected on the output side of the LDO. The circuit diagram
is shown in Figure 8 and the relationship between input/output
voltage and the reverse current is shown in Figure 9. This
reverse current flow is a temporary phenomenon that lasts
until the output capacitor is discharged. The value of the
reverse current and the time can vary depending on the circuit
because they are determined by the impedance at power
down with the power supply of the previous stage, the total
charge of the capacitor on the output side, and the load current.

5/5
Pcp o w e r s u p p
irc u it o f th e
re v io u s s ta
V O U T
ly
g e
L
N
IR E V E R
S E
R
LO A D
5-3. When the input is open
The circuit diagram is shown in Figure 10 and the input/output
voltage relationship is shown in Figure 11. When the input is
open at power down, there is no difference in input/output
voltage, so reverse current does not flow. For this reason, a
protection diode is not necessary.
Figure 8. Circuit when voltage drops rapidly on input side
Figure 9. Input/output voltage and reverse current when
voltage drops rapidly on input side
Basically, a protection diode is necessary if the reverse voltage
is 0.6 V or higher but not necessary if all of the following
conditions are met.
Conditions under which a diode is not necessary (all of the
conditions must be met)
- The peak value of the reverse current must be no more than
the maximum output current value written in the
recommended operating range on the data sheet.
- The power supply must not be turned ON and OFF
frequently.
- The final product must not require high reliability and safety.
5-2. When reverse current always flows
In a circuit configuration with multiple power supply systems,
a protection diode is necessary regardless of the current value
if reverse current constantly flows into the LDO from other
circuit blocks at power down or if reverse current flows into the
LDO when voltage is applied to the LDO output from another
power supply during the product delivery inspection process.
V C C O N O F F V
L
N
U
1 I E REVERSE_PEAK S
E V
E
0
14
0.0009
V12
IN Figure 10. Circuit when input is open
10
8
14
6
O4UT V12
2
10
0 t
0.0009 Power down 8
6
OUT
4
2
0 t
0.003 0.004Po0w.0e0r 5dow0n.006 0.007 0.008 0.009 0.01
Figure 11. Relationship between input voltage and output
voltage when input is open

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