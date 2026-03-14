---
source: "Microchip -- LAN8720 QFN Routing Checklist"
url: "https://ww1.microchip.com/downloads/en/DeviceDoc/LAN8720_QFN_Rev_A_Routing_Checklist.pdf"
format: "PDF 15pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 11040
---

REV CHANGE DESCRIPTION NAME DATE
A Release 7-25-12
Any assistance, services, comments, information, or suggestions provided by SMSC (including without limitation any comments to the
effect that the Company’s product designs do not require any changes) (collectively, “SMSC Feedback”) are provided solely for the purpose
of assisting the Company in the Company’s attempt to optimize compatibility of the Company’s product designs with certain SMSC
products. SMSC does not promise that such compatibility optimization will actually be achieved. Circuit diagrams utilizing SMSC products
are included as a means of illustrating typical applications; consequently, complete information sufficient for construction purposes is not
necessarily given. Although the information has been checked and is believed to be accurate, no responsibility is assumed for inaccuracies.
SMSC reserves the right to make changes to specifications and product descriptions at any time without notice.
DOCUMENT DESCRIPTION
Routing Checklist for the LAN8720, 24-pin QFN Package
SMSC
80 Arkay Drive
Hauppauge, New York 11788
Document Number Revision
RC614946 A

Routing Checklist for LAN8720
Information Particular for the 24-pin QFN Package
LAN8720 QFN Phy Interface:
1. The traces connecting the transmit outputs (TXP, pin 21) & (TXN, pin 20) to the
magnetics must be run as differential pairs. The differential impedance should be 100
ohms.
2. The traces connecting the receive inputs (RXP, pin 23) & (RXN, pin 22) from the
magnetics must be run as differential pairs. The differential impedance should be 100
ohms.
3. For differential traces running from the LAN controller to the magnetics, SMSC
recommends routing these traces on the component side of the PCB with a contiguous
digital ground plane on the next layer. This will minimize the use of vias and avoid
impedance mismatches by switching PCB layers.
4. Refer to Figure No. 1 for differential pair routing details.
5. The VDD1A/VDD2A power supply should be routed as a mini-plane and can be routed
on an internal power plane layer.
6. Refer to Figure No. 2 for VDD1A/VDD2A power plane details.
Page 2 of 15
Revision A

Figure No. 1
Page 3 of 15

Figure No. 2
Page 4 of 15

LAN8720 QFN Magnetics:
1. The traces connecting the transmit outputs from the magnetics to pins 1 & 2 on the RJ45
connector must be run as differential pairs. Again, the differential impedance should be
100 ohms.
2. The traces connecting the receive inputs on the magnetics from pins 3 & 6 on the RJ45
connector must be run as differential pairs. Again, the differential impedance should be
100 ohms.
3. For differential traces running from the magnetics to the RJ45 connector, SMSC
recommends routing these traces on the component side of the PCB with all power
planes (including chassis ground) cleared out from under these traces. This will minimize
the use of vias and minimize any unwanted noise from coupling into the differential pairs.
The plane clear out boundary is usually halfway through the magnetics.
RJ45 Connector:
1. Try to keep all other signals out of the Ethernet front end (RJ45 through the magnetics to
the LAN chip). Any noise from other traces may couple into the Ethernet section and
cause EMC problems.
2. Also recommended, is the construction of a separate chassis ground that can be easily
connected to digital ground at one point. This plane provides the lowest impedance path
to earth ground.
3. Refer to Figure No. 3 for Ethernet front end routing details.
Page 5 of 15

Figure No. 3
Page 6 of 15

Power Supply Connections:
1. Route the (2) VDD1A and VDD2A pins of the LAN8720 QFN directly into a solid, +3.3V
power plane (created with a ferrite bead). The pin-to-plane trace should be as short as
possible and as wide as possible.
2. In addition, route the (2) VDD1A and VDD2A decoupling capacitors for the LAN8720
QFN power pins as short as possible to each separate power pin. There should be a
short, direct copper connection as well as a connection to each power plane (+3.3V &
digital ground plane) for each cap.
3. Route the (1) VDDIO pin of the LAN8720 QFN directly into a solid, variable voltage
(+1.8V to +3.3V) power plane. The pin-to-plane trace should be as short as possible and
as wide as possible.
4. In addition, route the (1) VDDIO decoupling capacitor for the LAN8720 power pin as short
as possible to the power pin. There should be a short, direct copper connection as well
as a connection to each power plane (power plane & digital ground plane) for the cap.
Ground Connections:
1. The single digital ground pin (pin 25, EDP) on the LAN8720 QFN should be connected
directly into a solid, contiguous, internal ground plane. The EDP pad on the component
side of the PCB should be connected to the internal digital ground plane with 4 power
vias in a 2x2 grid.
2. We recommend that all Ground pins be tied together to the same ground plane. We do
not recommend running separate ground planes for any of our LAN products.
VDDCR:
1. The VDDCR pin, pin 6, must be routed with a heavy, wide trace with multiple vias to the
single decoupling cap and the single bulk capacitor associated with it. A mini-plane is
also acceptable.
Page 7 of 15

Crystal Connections:
1. The routing for the crystal or clock circuitry should be kept as small as possible and as
short as possible. Refer to Figure No. 4 below for details.
2. A small ground flood routed under the crystal package on the component layer of PCB
may improve the emissions signature. Stitch the flood with multiple vias into the digital
ground plane directly below it.
3. The REF_CLK Out Mode is not part of the RMII Specification. Timing in this mode is not
compliant with the RMII specification. To ensure proper system operation, a timing
analysis of the MAC and LAN8720 must be performed. Some MACs may require a small
delay (500 pS – 1.0 nS) to the RXD[1..0] & CRS_DV signals. One method to achieve
such a delay is to serpentine the signals from the Phy to the MAC.
Figure No. 4
Page 8 of 15

Clock Oscillator Connections:
1. Place the 50 MHz clock oscillator approximately half-way between the LAN8720 and the
RMII MAC in the application. This should ensure relatively matched clock runs to each.
2. Place the series terminations for splitting the 50 MHz clock as close as possible to the
clock oscillator in the design.
3. As controlled by the different component placements, the two resultant clock traces
should be matched to within 0.10” and have an overall trace length of less than 6.0”.
MAC REFCLK Connections:
1. Place the series termination for the MAC supplied 50 MHz clock as close as possible to
the MAC in the design.
2. As controlled by the different component placements, the resultant clock trace should be
as short as possible.
RBIAS Resistor:
1. The RBIAS resistor (pin 24) should be routed with a short, wide trace. Any noise induced
onto this trace may cause system failures. Do not run any traces under the RBIAS
resistor.
RMII Interface:
1. The RMII interface on the LAN8720 should be constructed using 68-ohm traces.
2. Similar groups of the RMII interface should be routed together on the PCB. Transmit
channel signals should be routed together and separate from Receive channel signals.
3. RMII signals considered critical should be routed on the top layer next to a contiguous,
digital ground plane. Slower RMII signals can be routed on the bottom layer of the PCB.
4. As with any high-speed digital design, inter-space and intra-space guidelines between
RMII signals should help to improve crosstalk and signal integrity issues.
5. Refer to Figures No. 5 and No. 6 for details on RMII signal routing.
Page 9 of 15

Figure No. 5
Page 10 of 15

Figure No. 6
Page 11 of 15

RMII Series Terminations:
1. If the designer has elected to use impedance matching terminations in his design, these
series resistors should be placed as close as possible to the source of the driving signal.
2. The RMII Series Terminations should be considered critical components. To ensure the
best signal integrity and good EMI performance, these critical components should be
placed on the component side of the PCB. This will ensure that these components will be
referenced to a contiguous ground plane reference on Layer 2 of the design. This will
also minimize the use of vias in routing these signals.
Required External Pull-ups:
1. There are no critical routing instructions for the Required External Pull-up connections.
Mode Pins:
1. Since the MODE Pins are shared with the RXD[1..0] and CRS_DV signals of the
LAN8720, any resistor used for termination for the power-on-reset MODE selection,
should be placed on the component side of the PCB. This will minimize vias and ensure
the reference plane remains constant.
2. Any stub added to the RMII lines due to MODE pin terminations should be kept to a
minimum.
Phy Address Pins:
1. Phy Address pin PHYAD0 should also be considered critical. This pin is shared with the
RX_ER function of the RMII interface. Any resistor used for termination for the power-on-
reset Phy Address selection, should be placed on the component side of the PCB. This
will minimize vias and ensure the reference plane remains constant for these three
signals.
2. Any stub added to the RMII line due to PHYAD0 termination should be kept to a
minimum.
Page 12 of 15

LED Pins:
1. There are no critical routing instructions for the LED Pin connections.
Interrupt Functionality:
1. There are no critical routing instructions for the Interrupt connection.
Miscellaneous:
1. SMSC recommends utilizing at least a four-layer design for boards for the LAN8720 QFN
device. The design engineer should be aware, however, as tighter EMC standards are
applied to his product and as faster signal rates are utilized by his design, the product
design may benefit by utilizing up to eight layers for the PCB construction.
2. As with any high-speed design, the use of series resistors and AC terminations is very
application dependant. Buffer impedances should be anticipated and series resistors
added to ensure that the board impedance matches the driver. Any critical clock lines
should be evaluated for the need for AC terminations. Prototype validation will confirm
the optimum value for any series and/or AC terminations.
3. Bulk capacitors for each power plane should be routed immediately into power planes
with traces as short as possible and as wide as possible.
4. Following these guidelines and other general design rules in PCB construction should
ensure a clean operating system.
5. Trace impedance depends upon many variables (PCB construction, trace width, trace
spacing, etc.). The electrical engineer needs to work with the PCB designer to determine
all these variables.
Page 13 of 15

Figure No. 7
Page 14 of 15

Figure No. 8
Page 15 of 15