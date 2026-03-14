---
source: "Nexperia AN10441 -- Level Shifting Techniques in I2C-bus Design"
url: "https://assets.nexperia.com/documents/application-note/AN10441.pdf"
format: "PDF 5pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 12041
---

Level shifting techniques in I²C-bus design
Rev. 2 — 10 February 2020 Application note
Document information
Information Content
Keywords I²C-bus, level shifting
Abstract Logic level shifting may be required when interfacing legacy devices with newer devices that use a
smaller geometry process. For bidirectional bus systems like the I²C-bus, such a level shifter must
also be bidirectional, without the need of a direction control signal. The simplest way to solve this
problem is by connecting a discrete MOSFET to each bus line.

Nexperia AN10441
1. Introduction
Present technology processes for integrated circuits with clearances of 0.5 µm and less limit the
maximum supply voltage and consequently the logic levels for the digital I/O signals. To interface
these lower voltage circuits with existing 5 V devices, a level shifter is needed. For bidirectional
2
bus systems like the I C-bus, such a level shifter must also be bidirectional, without the need
of a direction control signal. The simplest way to solve this problem is by connecting a discrete
MOSFET to each bus line.
2. Bidirectional level shifter for Fast-mode and Standard-mode I C-bus
systems
In spite of its surprising simplicity, such a solution not only fulfils the requirement of bidirectional
level shifting without a direction control signal, it also:
• Isolates a powered-down bus section from the rest of the bus system
• Protects the ‘lower voltage’ side against high voltage spikes from the ‘higher-voltage’ side.
The bidirectional level shifter can be used for both Standard-mode (up to100 kbit/s) or in
Fast-mode (up to 400 kbit/s) I C-bus systems. It is not intended for Hs-mode systems, which may
have a bridge with a level shifting possibility.
2.1. Connecting devices with different logic levels
Different voltage devices could be connected to the same bus by using pull-up resistors to the
supply voltage line. Although this is the simplest solution, the lower voltage devices must be 5 V
tolerant, which can make them more expensive to manufacture. By using a bidirectional level
shifter, however, it is possible to interconnect two sections of an I C-bus system, with each section
having a different supply voltage and different logic levels. Such a configuration is shown in
Fig. 1. The left ‘low-voltage’ section has pull-up resistors and devices connected to a 3.3 V supply
voltage; the right ‘high-voltage’ section has pull-up resistors and devices connected to a 5 V supply
voltage. The devices of each section have I/Os with supply voltage related logic input levels and an
open-drain output configuration.
The level shifter for each bus line is identical and consists of one discrete N-channel enhancement
MOSFET; TR1 for the serial data line SDA and TR2 for the serial clock line SCL. The gates
(g) have to be connected to the lowest supply voltage V , the sources (s) to the bus lines of
DD1
the ‘lower-voltage’ section, and the drains (d) to the bus lines of the ‘higher-voltage’ section.
Many MOSFETs have the substrate internally connected with its source, if this is not the case, an
external connection should be made. Each MOSFET has an integral diode (n-p junction) between
the drain and substrate.
VDD1 = 3.3 V VDD2 = 5 V
Rp Rp g TR1 Rp Rp
SDA1 s d SDA2
g TR2
SCL1 s d SCL2
3.3 V DEVICE 3.3 V DEVICE 5 V DEVICE 5 V DEVICE
mgk879
Fig. 1. Bidirectional level shifter circuit connecting two different voltage sections in an
I C-bus system
AN10441 All information provided in this document is subject to legal disclaimers. © Nexperia B.V. 2020. All rights reserved
Application note Rev. 2 — 10 February 2020 2 / 5

2.1.1. Operation of the level shifter
The following three states should be considered during the operation of the level shifter:
1. No device is pulling down the bus line. The bus line of the ‘lower-voltage’ section is pulled up by
its pull-up resistors R to 3.3 V. The gate and the source of the MOSFET are both at 3.3 V, so
p
its V is below the threshold voltage and the MOSFET is not conducting. This allows the bus
GS
line at the ‘higher-voltage’ section to be pulled up by its pull-up resistor R to 5 V. So the bus
p
lines of both sections are HIGH, but at a different voltage level.
2. A 3.3 V device pulls down the bus line to a LOW level. The source of the MOSFET also
becomes LOW, while the gate stays at 3.3 V. V rises above the threshold and the MOSFET
starts to conduct. The bus line of the ‘higher-voltage’ section is then also pulled down to a LOW
level by the 3.3 V device via the conducting MOSFET. So the bus lines of both sections go
LOW to the same voltage level.
3. A 5 V device pulls down the bus line to a LOW level. The drain-substrate diode of the MOSFET
the ‘lower-voltage’ section is pulled down until V passes the threshold and the MOSFET
starts to conduct. The bus line of the ‘lower-voltage’ section is then further pulled down to a
LOW level by the 5 V device via the conducting MOSFET. So the bus lines of both sections go
LOW to the same voltage level.
The three states show that the logic levels are transferred in both directions of the bus system,
independent of the driving section. State 1 performs the level shift function. States 2 and 3
perform a ‘wired-AND’ function between the bus lines of both sections as required by the I C-bus
specification.
Supply voltages other than 3.3 V for V and 5 V for V can also be applied, e.g., 2 V for V
DD1 DD2 DD1
and 10 V for V is feasible. In normal operation V must be equal to or higher than V
DD2 DD2 DD1
(V is allowed to fall below V during switching power on/off).
DD2 DD1
3. Abbreviations
Table 1. Abbreviations
Acronym Description
I C-bus Inter-Integrated Circuit bus
I/O Input/Output
MOSFET Metal-Oxide Semiconductor Field-Effect Transistor
4. Revision history
Table 2. Revision history
Rev Date Description
AN10441 v.2 20200210 • The format of this data sheet has been redesigned to comply
with the identity guidelines of Nexperia.
• Legal texts have been adapted to the new company name
where appropriate.
AN10441 v.1 20070618 Initial version
AN10441 All information provided in this document is subject to legal disclaimers. © Nexperia B.V. 2020. All rights reserved
Application note Rev. 2 — 10 February 2020 3 / 5

5. Legal information
Definitions
Draft — The document is a draft version only. The content is still under
internal review and subject to formal approval, which may result in
modifications or additions. Nexperia does not give any representations or
warranties as to the accuracy or completeness of information included herein
and shall have no liability for the consequences of use of such information.
Disclaimers
Limited warranty and liability — Information in this document is believed
to be accurate and reliable. However, Nexperia does not give any
representations or warranties, expressed or implied, as to the accuracy
or completeness of such information and shall have no liability for the
consequences of use of such information. Nexperia takes no responsibility
for the content in this document if provided by an information source outside
of Nexperia.
In no event shall Nexperia be liable for any indirect, incidental, punitive,
special or consequential damages (including - without limitation - lost
profits, lost savings, business interruption, costs related to the removal
or replacement of any products or rework charges) whether or not such
damages are based on tort (including negligence), warranty, breach of
contract or any other legal theory.
Notwithstanding any damages that customer might incur for any reason
whatsoever, Nexperia’s aggregate and cumulative liability towards customer
for the products described herein shall be limited in accordance with the
Terms and conditions of commercial sale of Nexperia.
Right to make changes — Nexperia reserves the right to make changes
to information published in this document, including without limitation
specifications and product descriptions, at any time and without notice. This
document supersedes and replaces all information supplied prior to the
publication hereof.
Suitability for use — Nexperia products are not designed, authorized or
warranted to be suitable for use in life support, life-critical or safety-critical
systems or equipment, nor in applications where failure or malfunction
of an Nexperia product can reasonably be expected to result in personal
injury, death or severe property or environmental damage. Nexperia and its
suppliers accept no liability for inclusion and/or use of Nexperia products in
such equipment or applications and therefore such inclusion and/or use is at
the customer’s own risk.
Applications — Applications that are described herein for any of these
products are for illustrative purposes only. Nexperia makes no representation
or warranty that such applications will be suitable for the specified use
without further testing or modification.
Customers are responsible for the design and operation of their applications
and products using Nexperia products, and Nexperia accepts no liability for
any assistance with applications or customer product design. It is customer’s
sole responsibility to determine whether the Nexperia product is suitable
and fit for the customer’s applications and products planned, as well as
for the planned application and use of customer’s third party customer(s).
Customers should provide appropriate design and operating safeguards to
minimize the risks associated with their applications and products.
Nexperia does not accept any liability related to any default, damage, costs
or problem which is based on any weakness or default in the customer’s
applications or products, or the application or use by customer’s third party
customer(s). Customer is responsible for doing all necessary testing for the
customer’s applications and products using Nexperia products in order to
avoid a default of the applications and the products or of the application or
use by customer’s third party customer(s). Nexperia does not accept any
liability in this respect.
Export control — This document as well as the item(s) described herein
may be subject to export control regulations. Export might require a prior
authorization from competent authorities.
Translations — A non-English (translated) version of a document is for
reference only. The English version shall prevail in case of any discrepancy
between the translated and English versions.
Trademarks
Notice: All referenced brands, product names, service names and
trademarks are the property of their respective owners.
AN10441 All information provided in this document is subject to legal disclaimers. © Nexperia B.V. 2020. All rights reserved
Application note Rev. 2 — 10 February 2020 4 / 5

Contents
1. Introduction...................................................................2
2. Bidirectional level shifter for Fast-mode and
Standard-mode I C-bus systems......................................2
2.1. Connecting devices with different logic levels..............2
2.1.1. Operation of the level shifter....................................3
3. Abbreviations................................................................3
4. Revision history............................................................3
5. Legal information.........................................................4
© Nexperia B.V. 2020. All rights reserved
For more information, please visit: http://www.nexperia.com
For sales office addresses, please send an email to: salesaddresses@nexperia.com
Date of release: 10 February 2020
AN10441 All information provided in this document is subject to legal disclaimers. © Nexperia B.V. 2020. All rights reserved
Application note Rev. 2 — 10 February 2020 5 / 5