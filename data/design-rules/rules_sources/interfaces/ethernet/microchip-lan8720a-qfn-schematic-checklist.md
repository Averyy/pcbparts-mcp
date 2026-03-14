---
source: "Microchip -- LAN8720A QFN Schematic Checklist"
url: "https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/SupportingCollateral/LAN8720AQFNRevDSchematicChecklist.pdf"
format: "PDF 18pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 23519
---

REV CHANGE DESCRIPTION NAME DATE
A Release 06-04-10
B Changed VDDCR Bypass Capacitor Value 01-19-11
C Added CLKIN Voltage Levels At Reduced VDDIO Voltage Levels 01-27-12
D Added Required REFCLKO Timing Analysis 07-25-12
Any assistance, services, comments, information, or suggestions provided by SMSC (including without limitation any comments to the
effect that the Company’s product designs do not require any changes) (collectively, “SMSC Feedback”) are provided solely for the purpose
of assisting the Company in the Company’s attempt to optimize compatibility of the Company’s product designs with certain SMSC
products. SMSC does not promise that such compatibility optimization will actually be achieved. Circuit diagrams utilizing SMSC products
are included as a means of illustrating typical applications; consequently, complete information sufficient for construction purposes is not
necessarily given. Although the information has been checked and is believed to be accurate, no responsibility is assumed for inaccuracies.
SMSC reserves the right to make changes to specifications and product descriptions at any time without notice.
DOCUMENT DESCRIPTION
Schematic Checklist for the LAN8720, 24-pin QFN Package
SMSC
80 Arkay Drive
Hauppauge, New York 11788
Document Number Revision
SC471228 D

Schematic Checklist for LAN8720
Information Particular to the 24-pin QFN Package
LAN8720 QFN PHY Interface:
1. TXP (pin 21): This pin is the transmit twisted pair output positive connection from the
internal PHY. It requires a 49.9, 1.0% pull-up resistor to VDDA (created from +3.3V).
This pin also connects to the transmit channel of the magnetics.
2. TXN (pin 20): This pin is the transmit twisted pair output negative connection from the
internal PHY. It requires a 49.9, 1.0% pull-up resistor to VDDA (created from +3.3V).
This pin also connects to the transmit channel of the magnetics.
3. For transmit channel connection and termination details, refer to Figure 1.
4. RXP (pin 23): This pin is the receive twisted pair input positive connection to the internal
PHY. It requires a 49.9, 1.0% pull-up resistor to VDDA (created from +3.3V). This pin
also connects to the receive channel of the magnetics.
5. RXN (pin 22): This pin is the receive twisted pair input negative connection to the internal
PHY. It requires a 49.9, 1.0% pull-up resistor to VDDA (created from +3.3V). This pin
also connects to the receive channel of the magnetics.
6. For receive channel connection and termination details, refer to Figure 2.
7. For added EMC flexibility in a LAN8720 design, the designer should include four low
valued capacitors on the TXP, TXN, RXP & RXN pins. Low valued capacitors (22 F or
less) can be added to each line and terminated to digital ground. These components can
be added to the schematic and should be designated as Do Not Populate (DNP).
Page 2 of 18
Revision D (07-25-12)

VDDA (+3.3V)
R3 R4
49.9 Ohms 49.9 Ohms Magnetics Module
1.0% 1.0%
Transmit Channel
21
TXP TD+ T + X
LAN8720 TCT TCMT
20
TXN TD- TX-
Connect TX
Center Tap to RX
Center Tap
Page 3 of 18
A1DDV A2DDV
Figure 1 – Transmit Channel Connections and Terminations
Connect RX
Center Tap to TX
VDDA (+3.3V) Center Tap
R1 R2
49.9 Ohms 49.9 Ohms Magnetics Module
1.0% 1.0%
Receive Channel
23
RXP RD+ RX+
LAN8720 RCT RCMT
22
RXN RD- RX-
C1
0.022 uF
A1DDV A2DDV
Figure 2 – Receive Channel Connections and Terminations

LAN8720 QFN Magnetics:
1. On the LAN8720 side, the transmit channel center tap connection must be connected to
VDDA (created from +3.3V) directly. The transmit channel center tap of the magnetics
also connects to the receive channel center tap of the magnetics.
2. On the LAN8720 side, the receive channel center tap connection is connected to the
transmit channel center tap on the magnetics. In addition, a 0.022 F capacitor is
required from the receive channel center tap of the magnetics to digital ground.
3. On the cable side (RJ45 side), the transmit channel center tap connection should be
terminated with a 75 resistor through a 1000 F, 2KV capacitor (C ) to chassis
magterm
ground.
4. On the cable side (RJ45 side), receive channel center tap connection should be
terminated with a 75 resistor through a 1000 F, 2KV capacitor (C ) to chassis
ground.
5. Only one 1000 F, 2KV capacitor (C ) to chassis ground is required. It is shared by
both TX & RX center taps.
6. Assuming the design of an end-point device (NIC), pin 1 of the RJ45 is TX+ and should
trace through the magnetics to TXP (pin 21) of the LAN8720 QFN.
7. Assuming the design of an end-point device (NIC), pin 2 of the RJ45 is TX- and should
trace through the magnetics to TXN (pin 20) of the LAN8720 QFN.
8. Assuming the design of an end-point device (NIC), pin 3 of the RJ45 is RX+ and should
trace through the magnetics to RXP (pin 23) of the LAN8720 QFN.
9. Assuming the design of an end-point device (NIC), pin 6 of the RJ45 is RX- and should
trace through the magnetics to RXN (pin 22) of the LAN8720 QFN.
10. When using the SMSC LAN8720 device in the HP Auto MDIX mode of operation, the use
of an Auto MDIX style magnetics module is required. Please refer to the SMSC
Application Note 8.13 “Suggested Magnetics” for proper magnetics.
Page 4 of 18

RJ45 Connector:
1. Pins 4 & 5 of the RJ45 connect to one pair of unused wires in CAT-5 type cables. These
should be terminated to chassis ground through a 1000 F, 2KV capacitor (C ). There
rjterm
are two methods of accomplishing this:
a) Pins 4 & 5 can be connected together with two 49.9 resistors. The common
connection of these resistors should be connected through a third 49.9 to the
1000 F, 2KV capacitor (C ).
b) For a lower component count, the resistors can be combined. The two 49.9
resistors in parallel look like a 25 resistor. The 25 resistor in series with the
49.9 makes the entire circuit behave like a 75 resistor. So, by shorting pins 4
& 5 together on the RJ45 and terminating them with a 75 resistor in series with
the 1000 F, 2KV capacitor (C ) to chassis ground, an equivalent circuit is
created.
2. Pins 7 & 8 of the RJ45 connect to one pair of unused wires in CAT-5 type cables. These
should be terminated to chassis ground through a 1000 F, 2KV capacitor (C ). There
are two methods of accomplishing this:
a) Pins 7 & 8 can be connected together with two 49.9 resistors. The common
connection of these resistors should be connected through a third 49.9 to the
1000 F, 2KV capacitor (C ).
b) For a lower component count, the resistors can be combined. The two 49.9
resistors in parallel look like a 25 resistor. The 25 resistor in series with the
49.9 makes the entire circuit behave like a 75 resistor. So, by shorting pins 4
& 5 together on the RJ45 and terminating them with a 75 resistor in series with
the 1000 F, 2KV capacitor (C ) to chassis ground, an equivalent circuit is
created.
3. The RJ45 shield should be attached directly to chassis ground.
Page 5 of 18

Power Supply Connections:
1. The analog supply (VDD1A & VDD2A) pins on the LAN8720 QFN are 1 & 19. They
require a connection to VDDA (created from +3.3V through a ferrite bead). Be sure to
place bulk capacitance on each side of the ferrite bead.
Note: Pins 1 & 19 (VDD1A & VDD2A) must always be connected to a +3.3V power
supply; even in the case of having the internal +1.2V regulator of the LAN8720 disabled.
Other blocks within the LAN8720 require power from +3.3V.
2. Each VDDxA pin should have one .01 F (or smaller) capacitor to decouple the
LAN8720. The capacitor size should be SMD_0603 or smaller.
3. Pin 9 (VDDIO) is a variable supply voltage for the I/O pads. This pin must be connected
to a voltage supply between +1.8V and +3.3V. The VDDIO power plane should have
proper bulk capacitance.
4. The VDDIO pin should have one .01 F (or smaller) capacitor to decouple the LAN8720.
The capacitor size should be SMD_0603 or smaller.
Ground Connections:
1. The digital ground pins (GND), the analog ground pins (AVSS), and the GND_CORE pins
on the LAN8720 QFN are all connected internally to the exposed die paddle ground. The
EDP Ground pad on the underside of the LAN8720 must be connected directly to a solid,
contiguous digital ground plane.
2. It is recommended that all ground connections be tied together to the same ground plane.
It is not recommended to run separate ground planes for any SMSC LAN products.
Page 6 of 18

VDDCR:
1. VDDCR (pin 6) is used to provide bypassing for the +1.2V core regulator. This pin requires a 470
ρF bypass capacitor. This capacitor should be located as close as possible to the pin without
using vias. In addition, pin 6 requires a bulk capacitor placed as close as possible to the pin. The
bulk capacitor must have a value of at least 1.0 F, and have an ESR (equivalent series
resistance) of no more than 1.0 . SMSC recommends a very low ESR ceramic capacitor for
design stability. Other values, tolerances & characteristics are not recommended.
Caution: This +1.2V supply is for internal logic only. Do Not power other circuits or devices
with this supply.
+3.3V
FB1
LAN8720
Page 7 of 18
OIDDV A1DDV
+1.8V - +3.3V
Connect to RX &
TX terminations
Two Caps on Pin 6
6
VDDCR
470 pF 1.0 uF
Low ESR
A2DDV
Figure 3 – LAN8720 Power Connections

Crystal Connections:
1. A 25.000 MHz crystal should be used to provide the clock source for the LAN8720 QFN.
For exact specifications and tolerances refer to the latest revision of the LAN8720 data
sheet.
2. XTAL1/CLKIN (pin 5) on the LAN8720 QFN is the clock circuit input. This pin requires a
15 – 33 F capacitor to digital ground. One side of the crystal connects to this pin.
3. XTAL2 (pin 4) on the LAN8720 QFN is the clock circuit output. This pin requires a 15 –
33 F capacitor to digital ground. One side of the crystal connects to this pin.
4. Since every system design is unique, the capacitor values are system dependant. The
PCB design, selected crystal, layout, and the type of capacitors selected, all contribute to
the characteristics of this circuit. Once the board is complete and operational, it is up to
the system engineer to analyze this circuit in a lab environment. The system engineer
should verify the frequency, stability, and voltage level of the circuit to guarantee that the
circuit meets all design criteria as put forth in the data sheet.
5. An additional external 1.0M  resistor across the crystal is not required. The necessary
resistance has been designed into the LAN8720 internally.
6. When using a 25.000 MHz crystal with the LAN8720, the PHY generates the required
50.000 MHz for the RMII interface internally for its own use. A copy of the 50.000 MHz
clock is provided as an output on pin 14 (nINT/REFCLK0) for use as the 50.000 MHz
MAC REFCLK.
7. It is recommended that the designer use a series 33 Ω termination resistor on the
REFCLKO pin. The value can then be adjusted to compensate for any PCB trace
impedance inconsistencies.
8. The REF_CLK Out Mode is not part of the RMII Specification. Timing in this mode is not
compliant with the RMII specification. To ensure proper system operation, a timing
analysis of the MAC and LAN8720 must be performed. Some MACs may require a small
delay (500 pS – 1.0 nS) to the RXD[1..0] & CRS_DV signals. One method to achieve
such a delay is to serpentine the signals from the Phy to the MAC.
9. In this application, nINTSEL must be a level zero during POR or nRST.
Figure 4 – LAN8720 Crystal Connections
Page 8 of 18

Clock Oscillator Connections:
1. A 50.000 MHz clock oscillator may be used to provide the clock source for the LAN8720.
The clock oscillator must provide a 50.000 MHz clock for the PHY and RMII MAC in the
design. For exact specifications and tolerances refer to the latest revision LAN8720 data
sheet.
2. In order to provide two copies of the 50.000 MHz clock, it is recommended that the
designer use two series 33 Ω resistors. The values can then be adjusted to compensate
for any PCB trace inconsistencies.
3. XTAL1/CLKIN (pin 5) on the LAN8720 QFN is the clock circuit input. With low VDDIO
voltages (+1.8V), CLKIN voltage may range from +1.8V to +3.3V.
4. XTAL2 (pin 4) on the LAN8720 QFN is the clock circuit output. When using a single
ended clock source, this pin can be left floating as a No Connect (NC).
5. Since every system design is unique, the PCB design, oscillator selected, and layout all
contribute to the characteristics of this circuit. Once the board is complete and
operational, it is up to the system engineer to analyze this circuit in a lab environment.
The system engineer should verify the frequency, stability, and voltage level of the circuit
to guarantee that the circuit meets all design criteria as put forth in the data sheet.
6. In this application, nINTSEL must be a level one during POR or nRST.
Page 9 of 18
OIDDV
Figure 5 – LAN8720 Clock Oscillator Connections

MAC REFCLK Connections:
1. A 50.000 MHz REFCLK output from the MAC may be used to provide the clock source
for the LAN8720. For exact specifications and tolerances refer to the latest revision
LAN8720 data sheet.
2. It is recommended that the designer use a series 33 Ω resistor at the MAC to connect to
the Phy. The value can then be adjusted to compensate for any PCB trace
inconsistencies.
3. XTAL1/CLKIN (pin 5) on the LAN8720 QFN is the clock circuit input. With low VDDIO
voltages (+1.8V), CLKIN voltage may range from +1.8V to +3.3V.
4. XTAL2 (pin 4) on the LAN8720 QFN is the clock circuit output. When using a single
ended clock source, this pin can be left floating as a No Connect (NC).
5. Since every system design is unique, the PCB design and layout all contribute to the
characteristics of this circuit. Once the board is complete and operational, it is up to the
system engineer to analyze this circuit in a lab environment. The system engineer should
verify the frequency, stability, and voltage level of the circuit to guarantee that the circuit
meets all design criteria as put forth in the data sheet.
6. In this application, nINTSEL must be a level one during POR or nRST.
LAN8720
Page 10 of 18
OIDDV
+1.8V - +3.3V +1.8V - +3.3V
MAC R Term
33 Ohms
5 14
REFCLK XTAL1/CLKIN nINT
4
XTAL2
Figure 6 – LAN8720 MAC REFCLK Connections

RBIAS Resistor:
1. RBIAS (pin 24) on the LAN8720 QFN should connect to digital ground through a 12.1K 
resistor with a tolerance of 1.0%. This pin is used to set-up critical bias currents for the
embedded 10/100 Ethernet Physical device.
RMII Interface:
1. When utilizing an external RMII MAC interface, the following table indicates the proper
connections for the 9 signals:
From: Connects To:
LAN8720 QFN RMII MAC Device Notes
RXD0 (pin 8) RXD<0>
RXD1 (pin 7) RXD<1>
RXD2 RXD<2> Not Used in RMII Mode
RXD3 RXD<3> Not Used in RMII Mode
RX_DV RX_DV Not Used in RMII Mode
RX_ER (pin 10) RX_ER This signal is optional in RMII Mode
RX_CLK RX_CLK Not Used in RMII Mode
TX_ER TX_ER Not Used in RMII Mode
TXD0 (pin 17) TXD<0>
TXD1 (pin 18) TXD<1>
TXD2 TXD<2> Not Used in RMII Mode
TXD3 TXD<3> Not Used in RMII Mode
TX_EN (pin 16) TX_EN
TX_CLK TX_CLK Not Used in RMII Mode
CRS_DV (pin 11) CRS_DV
CRS CRS Not Used in RMII Mode
COL COL Not Used in RMII Mode
MDIO (pin 12) MDIO
MDC (pin 13) MDC
2. Provisions should be made for series terminations for all outputs on the RMII Interface.
Series resistors will enable the designer to closely match the output driver impedance of
the LAN8720 and PCB trace impedance to minimize ringing on these signals. Exact
resistor values are application dependant and must be analyzed in-system. A suggested
starting point for the value of these series resistors is 10.0 .
Page 11 of 18

RMII Series Terminations:
Series Terminations
Signal RMII Mode Notes
RXD0 10 
RXD1 10 
RX_ER 10 
CRS_DV 10 
Required External Pull-ups:
1. Because the nINT (pin 14) output is open drain, an external pull-up resistor to VDDIO is
required.
2. When using the RMII interface of the LAN8720 QFN with a MAC device on board, a pull-
up resistor on the MDIO signal (pin 12) is required. A pull-up resistor of 1.5K to VDDIO
is required for this application.
Mode Pins:
1. The Mode pins of the LAN8720 (MODE[2:0]) control the default configuration of the
10/100 PHY. Speed, Duplex, Auto-Negotiation & power down functionality can be
configured through these pins. The value of these three pins are latched upon power-up
and reset. The latched values are reflected in Register 0 & Register 4 of the LAN8720.
Refer to the LAN8720 data sheet for complete details for the operation of these pins.
These three pins have weak internal pull-ups and can be left as no-connects. To set any
Mode bit low, an external 10K pull-down resistor should be used.
Page 12 of 18

PHY Address Pins:
1. The PHY Address pin of the LAN8720 (PHYAD0) determines which of the 2 PHY
addresses, of the 32 possible, the LAN8720 will respond to. The value of this pin is
latched upon power-up and reset. The latched value is reflected in Register 18 of the
LAN8720. Refer to the LAN8720 data sheet for complete details on the operation of this
pin. This pin has a weak internal pull-down and can be left as no-connect. To set the PHY
Address bit high, an external 10K pull-up resistor to VDDIO should be used. Address bits
PHYAD1, PHYAD2, PHYAD3 & PHYAD4 are tied low inside the LAN8720.
2. A basic PHY Address of 01h is usually recommended.
3. The PHY Address pin is shared with an MII signal on the LAN8720. The pinout is as
follows:
PHY Address 0 is shared with RX_ER on pin 10.
PHY Address 1 is tied low.
PHY Address 2 is tied low.
PHY Address 3 is tied low.
PHY Address 4 is tied low.
LED Pins:
1. The LAN8720 provides two LED signals. These indicators will display speed, link and
activity information about the current state of the PHY. The LED outputs have the ability
to be either active high or active low. The polarity is determined by the level latched at
nRST or POR. The LAN8720 senses each strap level value and changes the polarity of
the LED signal accordingly. If the strap value is set as a level one, the LED polarity will be
set to an active-low. If the strap value is set as a level zero, the LED polarity will be set to
an active high. Refer to the LAN8720 data sheet for further details on how to strap each
pin for correct operation and LED polarity outcomes.
2. The LED functionality signal pins are shared with the REGOFF & nINTSEL functionality
of the LAN8720. The pinouts are as follows:
LED1 is shared with REGOFF on pin 3.
LED2 is shared with nINTSEL on pin 2.
Page 13 of 18

Interrupt Functionality:
1. For added flexibility, the LAN8720 QFN provides a discrete interrupt line for embedded
applications. This is advantageous as there is no interrupt facility across the standard MII
Bus interface.
2. The nINT pin (pin 14) provides the interrupt signal from the LAN8720. To enable the
interrupt functionality on pin 14, the LED2/nINTSEL pin (pin 2) must be left as a no-
connection. The LED2/nINTSEL pin has a weak internal pull-up and therefore can be left
as a no-connect to select the interrupt functionality. The LED2/nINTSEL level is latched in
on POR or nRST.
3. When the LED2/nINTSEL pin (pin 2) is used in conjunction with a LED, refer to Figure 6
below for details.
VDD2A
LED2/nINTSEL
332 Ohms 332 Ohms 10K Ohms
LED2/nINTSEL
nINTSEL Bit = 1 nINTSEL Bit = 0
LED Output Signal from LED Output Signal from
LAN8720 is Active Low LAN8720 is Active High
Interrupt Functionality REFCLKO Functionality
Selected for Pin 14 Selected for Pin 14
Figure 7 – Interrupt Select / LED Polarity
Page 14 of 18

Miscellaneous:
1. REGOFF (pin 3) enables/disables the internal +1.2V core regulator of the LAN8720. This
pin has a weak internal pull-down and can be left as a no-connect to enable the internal
+1.2V regulator. To disable the +1.2V regulator, this pin should be pulled high with a
10.0K resistor to VDD2A. The REGOFF level is latched in on POR only.
2. When the LED1/REGOFF pin (pin 3) is used in conjunction with a LED, refer to Figure 7
below for details.
VDD2A
LED1/REGOFF
10K Ohms
332 Ohms 332 Ohms
LED1/REGOFF
REGOFF Bit = 1 REGOFF Bit = 0
LED Output Signal from LED Output Signal from
LAN8720 is Active Low LAN8720 is Active High
Internal +1.2V Core Regulator Internal +1.2V Core Regulator
is Disabled is Enabled (Default)
Figure 7 – REGOFF / LED Polarity
Page 15 of 18

Miscellaneous:
3. The nRST pin (pin 15) is an active-low reset input. This signal resets all logic and
registers within the LAN8720. This pin has a weak internal pull-up termination. A
hardware reset (nRST assertion) is required following power-up. Please refer to the latest
copy of the LAN8720 data sheet for reset timing requirements. SMSC does not
recommend the use of an RC circuit for this required pin reset. A reset generator /
voltage monitor is one option to provide a proper reset. Better yet, for increased design
flexibility, a controllable reset (GPIO, dedicated reset output) should be considered. In
this case, SMSC recommends a push-pull type output (not an open-drain type) for the
monotonic reset to ensure a sharp rise time transition from low-to-high.
4. Due to possible lower I/O voltages used on the LAN8720, lower strapping resistor values
need to be used to ensure the strapped configuration is properly latched into the PHY
device upon power-on reset. Refer to the latest revision of the LAN8720 QFN data sheet
for details of proper resistor values when using lower I/O voltages on VDDIO.
5. Incorporate a large SMD resistor (SMD_1210) to connect the chassis ground to the
digital ground. This will allow some flexibility during EMI testing for different grounding
options in order to determine the best performing configuration:
o Leave the footprint blank for two separate ground planes
o Short the ground planes together at a single point with a zero ohm resistor
o AC couple the grounds together with a high voltage capacitor
o Connect the two planes together with a ferrite bead
6. Be sure to incorporate enough bulk capacitors (4.7 - 22F caps) for each power plane.
Page 16 of 18

LAN8720 QFN QuickCheck Pinout Table:
Use the following table to check the LAN8720 QFN shape in your schematic:
LAN8720 QFN
Pin No. Pin Name Pin No. Pin Name
1 VDD2A 13 MDC
2 LED2/nINTSEL 14 nINT/REFCLKO
3 LED1/REGOFF 15 nRST
4 XTAL2 16 TXEN
5 XTAL1/CLKIN 17 TXD0
6 VDDCR 18 TXD1
7 RXD1/MODE1 19 VDD1A
8 RXD0/MODE0 20 TXN
9 VDDIO 21 TXP
10 RXER/PHYAD0 22 RXN
11 CRS_DV/MODE2 23 RXP
12 MDIO 24 RBIAS
EDP Ground Connection
25 Exposed Die Paddle Ground
Pad on Bottom of Package
Page 17 of 18

Reference Material:
Concepts and material available in the following documents may be helpful in designing the
LAN8720 into an application. Refer to www.smsc.com for the latest revisions.
1. SMSC LAN8720 Data Sheet
2. SMSC LAN8720 MII EVB Schematic, Assembly No. 6584 Rev C
3. SMSC LAN8720 EVB PCB, Assembly No. EVB8720; order PCB from web site.
4. SMSC Suggested Magnetics Application Note 8-13
5. SMSC EVB8720 Evaluation Board User Guide
6. SMSC PCB Design Guidelines for QFN and DQFN Packages Application Note 18-15
7. SMSC Ethernet Physical Layer Layout Guidelines Application Note 18-6
Page 18 of 18