---
source: "NXP AN11420 -- GPS LNA Voltage Supply via Coax Cable"
url: "https://www.nxp.com/docs/en/application-note/AN11420.pdf"
format: "PDF 11pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 16167
---

NXP GPS LNA - GPS LNA voltage supply via a coax cable
coming from the GPS receiver
Rev. 1 — 4 October 2013 Application note
Document information
Info Content
Keywords GPS, GNSS, LNA, AEC-Q100, automotive, voltage supply, coax cable
Abstract This application note describes how to supply NXP GPS LNA voltage
via a coax cable coming from the GPS receiver

NXP Semiconductors
NXP GPS LNA voltage supply from receiver via coax cable
Revision history
Rev Date Description
1 20131004 First publication
Contact information
For more information, please visit: http://www.nxp.com
For sales office addresses, please send an email to: salesaddresses@nxp.com
AN11420 All information provided in this document is subject to legal disclaimers. © NXP B.V. 2013. All rights reserved.
Application note Rev. 1 — 4 October 2013 2 of 11

1. Introduction
GPS LNAs are needed in active antenna applications due to the losses of a long cable
between the antenna and the receiver.
This application note gives practical information how to supply an NXP GPS LNA via a
coax cable coming from the GPS receiver. This applies to automotive qualified BGU7004
and BGU7008 since they both have the same architecture. They are AEC-Q100 qualified
Low Noise Amplifiers (LNAs) for GPS receiver applications in a plastic leadless 6-pin,
extremely small SOT886 package. Both of them require only one external matching
inductor and one external decoupling capacitor. They adapt itself to the changing
environment resulting from co-habitation of different radio systems in modern cellular
handsets. During high jamming power levels, resulting for example from a cellular
transmit burst, it temporarily increases its bias current to improve sensitivity. Both of them
cover full GNSS L1 band, from 1559 MHz to 1610 MHz and work with a supply voltage
from 1.5 V to 2.85 V.
The BGU7004 and BGU7008 performance information is available in their datasheets.
2. System features
• AEC-Q100 qualified
• Covers full GNSS L1 band, from 1559 MHz to 1610 MHz
• Noise figure = 0.85 dB for BGU7008 and 0.9 dB for BGU7004
• Gain 18.5 dB for BGU7008 and 16.5 dB for BGU7004
• High 1 dB compression point of −12 dBm for BGU7008 and -11 dBm for BGU7004
• High out of band IP3 of 4 dBm for BGU7008 and 9 dBm for BGU7004
i
• Supply voltage 1.5 V to 2.85 V, optimized for 1.8 V
• Power down mode current consumption < 1 uA
• Optimized performance at low supply current of 4.8 mA for BGU7008 and 4.5 mA for
BGU7004.
• Integrated temperature stabilized bias for easy design
• Requires only one input matching inductor and one supply decoupling capacitor
• Input and output DC decoupled
• ESD protection on all pins (HBM > 2 kV)
• Integrated matching for the output
• Small 6-pin leadless package 1 mm × 1.45 mm × 0.5 mm
• 110 GHz transit frequency - SiGe:C technology
3. Application Information
The application circuit shows how to supply the NXP GPS LNA voltage in an active
antenna application via a coax cable coming from the GPS receiver is depicted in Figure
1. Table 1 shows the bill of materials.
AN11420 All information provided in this document is subject to legal disclaimers. © NXP B.V. 2013. All rights reserved.
Application note Rev. 1 — 4 October 2013 3 of 11

3.1 NXP GPS LNA voltage supply in an active antenna application via a
coax cable coming from the GPS receiver
Fig 1. NXP GPS LNA voltage supply via a coax cable coming from the GPS receiver
A GPS signal comes from antenna to the NXP GPS LNA. An optional external ESD
protection diode can be used to increase the system’s ESD performance from 2kV up to
10kV. At the input of the GPS LNA only one external coil L1 is needed for the matching.
At the input there is no external DC blocking capacitor needed since the NXP GPS LNA
has an integrated input DC blocking capacitor.
Note that now at the output of the GPS LNA, there are an RF signal and a DC voltage.
For the voltage supply of the GPS LNA, since the voltage supply comes from the GPS
receiver to the output of the GPS LNA via a coax cable, the voltage supply is tapped from
the output of the GPS LNA to the voltage supply Vcc of the GPS LNA via an RF choke,
which blocks the RF signal and passes the DC supply voltage.
Close to the Vcc pin (pin 2) of the GPS LNA, an external decoupling capacitor C1 is
needed to decouple and to give an extra filtering of the RF signal in the DC supply line.
At the output of the GPS LNA, there is no external DC blocking capacitor needed either
because the NXP GPS LNA has an integrated output DC blocking capacitor as well,
which blocks the DC supply voltage and passes the RF signal.
The enable (pin 6 of the GPS LNA) voltage can be connected to Vcc for “always on” or
supplied separately. Pin 1 and 4 of the GPS LNA are grounded. The BGU7004 and
BGU7008 pinning information is available in their datasheets.
Figure 2 until Figure 5 show the comparison for BGU7008 at 2.85V between the default
application and the one using supply voltage via a coax cable in term of NF, Gain, Input
Return Loss, and Output Return Loss respectively. The figures show that there are no
significant differences in term of performance between the default application and the
one using supply voltage via a coax cable.
AN11420 All information provided in this document is subject to legal disclaimers. © NXP B.V. 2013. All rights reserved.
Application note Rev. 1 — 4 October 2013 4 of 11

Fig 2. NF comparison between default application (red trace) vs. using voltage supply
via coax cable (blue trace).
Fig 3. Gain comparison between default application (S21) vs. using voltage supply via
coax cable (S43).
AN11420 All information provided in this document is subject to legal disclaimers. © NXP B.V. 2013. All rights reserved.
Application note Rev. 1 — 4 October 2013 5 of 11

Fig 4. Input Return Loss comparison between default application (S11) vs. using
voltage supply via coax cable (S33).
Fig 5. Output Return Loss comparison between default application (S22) vs. using
voltage supply via coax cable (S44).
3.2 Bill of materials
Table 1. Evaluation board BOM
Component Description Value Supplier
C1 Decoupling capacitor 1 nF various
IC1 BGU7004 or BGU7008 GPS LNA - NXP
L1 High quality matching inductor 5.6 nH Murata LQW15A
RF choke RF choke 100 nH Murata LQG15HS
D1 ESD Diode (optional) PESD5V0F1BL NXP
AN11420 All information provided in this document is subject to legal disclaimers. © NXP B.V. 2013. All rights reserved.
Application note Rev. 1 — 4 October 2013 6 of 11

4. Abbreviations
Table 2. Abbreviations
Acronym Description
DC Direct Current
RF Radio Frequency
GPS Global Positioning System
LNA Low Noise Amplifier
GNSS Global Navigation Satellite System
ESD Electro Static Discharge
HBM Human Body Model
SiGe:C Silicon Germanium Carbon
AN11420 All information provided in this document is subject to legal disclaimers. © NXP B.V. 2013. All rights reserved.
Application note Rev. 1 — 4 October 2013 7 of 11

5. Legal information
Semiconductors accepts no liability for any assistance with applications or
5.1 Definitions customer product design. It is customer’s sole responsibility to determine
whether the NXP Semiconductors product is suitable and fit for the
Draft — The document is a draft version only. The content is still under customer’s applications and products planned, as well as for the planned
internal review and subject to formal approval, which may result in application and use of customer’s third party customer(s). Customers should
modifications or additions. NXP Semiconductors does not give any provide appropriate design and operating safeguards to minimize the risks
representations or warranties as to the accuracy or completeness of associated with their applications and products.
information included herein and shall have no liability for the consequences
NXP Semiconductors does not accept any liability related to any default,
of use of such information.
damage, costs or problem which is based on any weakness or default in the
customer’s applications or products, or the application or use by customer’s
5.2 Disclaimers third party customer(s). Customer is responsible for doing all necessary
testing for the customer’s applications and products using NXP
Limited warranty and liability — Information in this document is believed to
Semiconductors products in order to avoid a default of the applications and
be accurate and reliable. However, NXP Semiconductors does not give any
the products or of the application or use by customer’s third party
representations or warranties, expressed or implied, as to the accuracy or
customer(s). NXP does not accept any liability in this respect.
completeness of such information and shall have no liability for the
consequences of use of such information. NXP Semiconductors takes no Export control — This document as well as the item(s) described herein
responsibility for the content in this document if provided by an information may be subject to export control regulations. Export might require a prior
source outside of NXP Semiconductors. authorization from national authorities.
In no event shall NXP Semiconductors be liable for any indirect, incidental, Evaluation products — This product is provided on an “as is” and “with all
punitive, special or consequential damages (including - without limitation - faults” basis for evaluation purposes only. NXP Semiconductors, its affiliates
lost profits, lost savings, business interruption, costs related to the removal and their suppliers expressly disclaim all warranties, whether express,
or replacement of any products or rework charges) whether or not such implied or statutory, including but not limited to the implied warranties of non-
damages are based on tort (including negligence), warranty, breach of infringement, merchantability and fitness for a particular purpose. The entire
contract or any other legal theory. risk as to the quality, or arising out of the use or performance, of this product
remains with customer.
Notwithstanding any damages that customer might incur for any reason
whatsoever, NXP Semiconductors’ aggregate and cumulative liability In no event shall NXP Semiconductors, its affiliates or their suppliers be
towards customer for the products described herein shall be limited in liable to customer for any special, indirect, consequential, punitive or
accordance with the Terms and conditions of commercial sale of NXP incidental damages (including without limitation damages for loss of
Semiconductors. business, business interruption, loss of use, loss of data or information, and
the like) arising out the use of or inability to use the product, whether or not
Right to make changes — NXP Semiconductors reserves the right to make
based on tort (including negligence), strict liability, breach of contract, breach
changes to information published in this document, including without
of warranty or any other theory, even if advised of the possibility of such
limitation specifications and product descriptions, at any time and without
damages.
notice. This document supersedes and replaces all information supplied prior
to the publication hereof. Notwithstanding any damages that customer might incur for any reason
whatsoever (including without limitation, all damages referenced above and
Suitability for use — NXP Semiconductors products are not designed,
all direct or general damages), the entire liability of NXP Semiconductors, its
authorized or warranted to be suitable for use in life support, life-critical or
affiliates and their suppliers and customer’s exclusive remedy for all of the
safety-critical systems or equipment, nor in applications where failure or
foregoing shall be limited to actual damages incurred by customer based on
malfunction of an NXP Semiconductors product can reasonably be expected
reasonable reliance up to the greater of the amount actually paid by
to result in personal injury, death or severe property or environmental
customer for the product or five dollars (US$5.00). The foregoing limitations,
damage. NXP Semiconductors and its suppliers accept no liability for
exclusions and disclaimers shall apply to the maximum extent permitted by
inclusion and/or use of NXP Semiconductors products in such equipment or
applicable law, even if any remedy fails of its essential purpose.
applications and therefore such inclusion and/or use is at the customer’s
own risk.
5.3 Trademarks
Applications — Applications that are described herein for any of these
products are for illustrative purposes only. NXP Semiconductors makes no Notice: All referenced brands, product names, service names and
representation or warranty that such applications will be suitable for the trademarks are property of their respective owners.
specified use without further testing or modification.
Customers are responsible for the design and operation of their applications
and products using NXP Semiconductors products, and NXP
AN11420 All information provided in this document is subject to legal disclaimers. © NXP B.V. 2013. All rights reserved.
Application note Rev. 1 — 4 October 2013 8 of 11

6. List of figures
Fig 1. NXP GPS LNA voltage supply via a coax cable
coming from the GPS receiver .......................... 4
Fig 2. NF comparison between default application (red
trace) vs. using voltage supply via coax cable
(blue trace). ....................................................... 5
Fig 3. Gain comparison between default application
(S21) vs. using voltage supply via coax cable
(S43). ................................................................ 5
Fig 4. Input Return Loss comparison between default
application (S11) vs. using voltage supply via
coax cable (S33). .............................................. 6
Fig 5. Output Return Loss comparison between default
application (S22) vs. using voltage supply via
coax cable (S44). .............................................. 6
AN11420 All information provided in this document is subject to legal disclaimers. © NXP B.V. 2013. All rights reserved.
Application note Rev. 1 — 4 October 2013 9 of 11

7. List of tables
Table 1. Evaluation board BOM ...................................... 6
Table 2. Abbreviations .................................................... 7
AN11420 All information provided in this document is subject to legal disclaimers. © NXP B.V. 2013. All rights reserved.
Application note Rev. 1 —4 October 2013 10 of 11

8. Contents
1. Introduction ......................................................... 3
2. System features ................................................... 3
3. Application Information ...................................... 3
3.1 NXP GPS LNA voltage supply in an active
antenna application via a coax cable coming
from the GPS receiver ........................................ 4
3.2 Bill of materials ................................................... 6
4. Abbreviations ...................................................... 7
5. Legal information ................................................ 8
5.1 Definitions .......................................................... 8
5.2 Disclaimers......................................................... 8
5.3 Trademarks ........................................................ 8
6. List of figures ....................................................... 9
7. List of tables ...................................................... 10
8. Contents ............................................................. 11
Please be aware that important notices concerning this document and the product(s)
described herein, have been included in the section 'Legal information'.
© NXP B.V. 2013. All rights reserved.
For more information, visit: http://www.nxp.com
For sales office addresses, please send an email to: salesaddresses@nxp.com
Date of release: 4 October 2013
Document identifier: AN11420