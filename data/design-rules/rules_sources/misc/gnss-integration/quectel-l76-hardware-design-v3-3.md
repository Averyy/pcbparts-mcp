---
source: "Quectel L76 Hardware Design V3.3"
url: "https://centerclick.com/ntp/docs/Quectel_L76L76-L_Hardware_Design_V3.3.pdf"
format: "PDF 59pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 82722
---

L76&L76-L
Hardware Design
GNSS Module Series
Version: 3.3
Date: 2023-07-04
Status: Released

At Quectel, our aim is to provide timely and comprehensive services to our customers. If you
require any assistance, please contact our headquarters:
Quectel Wireless Solutions Co., Ltd.
Building 5, Shanghai Business Park Phase III (Area B), No.1016 Tianlin Road, Minhang District, Shanghai
200233, China
Tel: +86 21 5108 6236
Email: info@quectel.com
Or our local offices. For more information, please visit:
http://www.quectel.com/support/sales.htm.
For technical support, or to report documentation errors, please visit:
http://www.quectel.com/support/technical.htm.
Or email us at: support@quectel.com.
Legal Notices
We offer information as a service to you. The provided information is based on your requirements and we
make every effort to ensure its quality. You agree that you are responsible for using independent analysis
and evaluation in designing intended products, and we provide reference designs for illustrative purposes
only. Before using any hardware, software or service guided by this document, please read this notice
carefully. Even though we employ commercially reasonable efforts to provide the best possible
experience, you hereby acknowledge and agree that this document and related services hereunder are
provided to you on an “as available” basis. We may revise or restate this document from time to time at
our sole discretion without any prior notice to you.
Use and Disclosure Restrictions
License Agreements
Documents and information provided by us shall be kept confidential, unless specific permission is
granted. They shall not be accessed or used for any purpose except as expressly provided herein.
Copyright
Our and third-party products hereunder may contain copyrighted material. Such copyrighted material shall
not be copied, reproduced, distributed, merged, published, translated, or modified without prior written
consent. We and the third party have exclusive rights over copyrighted material. No license shall be
granted or conveyed under any patents, copyrights, trademarks, or service mark rights. To avoid
ambiguities, purchasing in any form cannot be deemed as granting a license other than the normal
non-exclusive, royalty-free license to use the material. We reserve the right to take legal action for
noncompliance with abovementioned requirements, unauthorized use, or other illegal or malicious use of
the material.
L76&L76-L_Hardware_Design 1 / 59

Trademarks
Except as otherwise set forth herein, nothing in this document shall be construed as conferring any rights
to use any trademark, trade name or name, abbreviation, or counterfeit product thereof owned by Quectel
or any third party in advertising, publicity, or other aspects.
Third-Party Rights
This document may refer to hardware, software and/or documentation owned by one or more third parties
(“third-party materials”). Use of such third-party materials shall be governed by all restrictions and
obligations applicable thereto.
We make no warranty or representation, either express or implied, regarding the third-party materials,
including but not limited to any implied or statutory, warranties of merchantability or fitness for a particular
purpose, quiet enjoyment, system integration, information accuracy, and non-infringement of any
third-party intellectual property rights with regard to the licensed technology or use thereof. Nothing herein
constitutes a representation or warranty by us to either develop, enhance, modify, distribute, market, sell,
offer for sale, or otherwise maintain production of any our products or any other hardware, software,
device, tool, information, or product. We moreover disclaim any and all warranties arising from the course
of dealing or usage of trade.
Privacy Policy
To implement module functionality, certain device data are uploaded to Quectel’s or third-party’s servers,
including carriers, chipset suppliers or customer-designated servers. Quectel, strictly abiding by the
relevant laws and regulations, shall retain, use, disclose or otherwise process relevant data for the
purpose of performing the service only or as permitted by applicable laws. Before data interaction with
third parties, please be informed of their privacy and data security policy.
Disclaimer
a) We acknowledge no liability for any injury or damage arising from the reliance upon the information.
b) We shall bear no liability resulting from any inaccuracies or omissions, or from the use of the
information contained herein.
c) While we have made every effort to ensure that the functions and features under development are
free from errors, it is possible that they could contain errors, inaccuracies, and omissions. Unless
otherwise provided by valid agreement, we make no warranties of any kind, either implied or express,
and exclude all liability for any loss or damage suffered in connection with the use of features and
functions under development, to the maximum extent permitted by law, regardless of whether such
loss or damage may have been foreseeable.
d) We are not responsible for the accessibility, safety, accuracy, availability, legality, or completeness of
information, advertising, commercial offers, products, services, and materials on third-party websites
and third-party resources.
Copyright © Quectel Wireless Solutions Co., Ltd. 2023. All rights reserved.
L76&L76-L_Hardware_Design 2 / 59

Safety Information
The following safety precautions must be observed during all phases of operation, such as usage, service,
or repair of any terminal or mobile incorporating the module. Manufacturers of the terminal should notify
users and operating personnel of the following safety information by incorporating these guidelines into all
product manuals. Otherwise, Quectel assumes no liability for customers’ failure to comply with these
precautions.
Ensure that the product may be used in the country and the required environment,
as well as that it conforms to the local safety and environmental regulations.
Keep away from explosive and flammable materials. The use of electronic
products in extreme power supply conditions and locations with potentially
explosive atmospheres may cause fire and explosion accidents.
The product must be powered by a stable voltage source, and the wiring shall
conform to security precautions and fire prevention regulations.
Proper ESD handling procedures must be followed throughout the mounting,
handling and operation of any devices and equipment that incorporate the module
to avoid ESD damages.
L76&L76-L_Hardware_Design 3 / 59

About the Document
Document Information
Title L76&L76-L Hardware Design
Subtitle GNSS Module Series
Document Type Hardware Design
Document Status Released
Revision History
Version Date Description
- 2013-02-08 Creation of the document
1.0 2013-02-08 First official release
1. Deleted PMTK 291 command.
2. Changed R3 to 100R in figure 17.
1.1 2013-03-21
3. Updated chapter 2.4.
4. Changed typical voltage of V_BCKP to 3.3 V.
1. Modified the input power at RF_IN.
1.2 2014-05-10
2. Changed the tracking sensitivity to -165 dBm.
1.3 2014-06-11 1. Updated packaging information.
1. Added related information of L76B module.
2.0 2014-08-28
2. Added the description of power supply requirement.
1. Added the description of 1PPS VS NMEA.
2.1 2015-11-11
2. Added the information about L76G module.
1. Deleted the information about L76G module.
3.0 2016-04-26 2. Added the information about L76-L module.
3. Added chapter 3.9: EPO Data Service
3.1 2016-05-18 Added the description of I2C about L76-L module.
L76&L76-L_Hardware_Design 4 / 59

1. Deleted the information about L76B;
2. Added the information about the L76-L(L) module;
3. Updated the name of PIN2 from TXD1 to TXD;
4. Updated the name of PIN3 from RXD1 to RXD;
5. Updated the name of PIN9 from RESET to RESET_N;
6. Updated the name of PIN14 from VCC_RF to VDD_RF;
7. Updated the name of PIN18 from WAKE_UP to WAKEUP;
3.2 2021-08-16
8. Added chapters 1.5, 1.6, 3.1, 3.4, 3.5, 5.2.2, 5.3, 8.2, and 9;
9. Updated the maximum altitude and accuracy of 1 PPS signal value
(Table 2);
10. Added the GLP mode (Chapter 3.3.5);
11. Updated the reference design for I2C interface (Figure 12);
12. Updated the recommended reflow soldering thermal profile
(Chapter 8.3).
1. Updated the module height size (Chapter 1.1, Table 1 and Figure 26).
2. Updated the weight and added the number of concurrent GNSS
3.3 2023-07-04 (Table 1).
3. Added the power data for power consumption (Table 2).
4. Updated the manufacturing and soldering (Chapter 8.3).
L76&L76-L_Hardware_Design 5 / 59

Contents
Safety Information ....................................................................................................................................... 3
About the Document ................................................................................................................................... 4
Contents ....................................................................................................................................................... 6
Table Index ................................................................................................................................................... 8
Figure Index ................................................................................................................................................. 9
1 Product Description ........................................................................................................................... 10
1.1. Overview.................................................................................................................................. 10
1.2. Features .................................................................................................................................. 11
1.3. Performance ............................................................................................................................ 13
1.4. Block Diagram ......................................................................................................................... 14
1.5. GNSS Constellations .............................................................................................................. 14
1.6. Augmentation System ............................................................................................................. 15
1.6.1. SBAS .............................................................................................................................. 15
1.7. AGNSS .................................................................................................................................... 15
1.7.1. EASY .............................................................................................................................. 15
1.7.2. EPO ................................................................................................................................ 16
1.8. LOCUS .................................................................................................................................... 16
1.9. Multi-tone AIC .......................................................................................................................... 16
2 Pin Assignment .................................................................................................................................. 18
3 Power Management ........................................................................................................................... 21
3.1. Power Unit ............................................................................................................................... 21
3.2. Power Supply .......................................................................................................................... 22
3.2.1. VCC ................................................................................................................................ 22
3.2.2. V_BCKP ......................................................................................................................... 23
3.3. Power Mode ............................................................................................................................ 24
3.3.1. Continuous Mode ........................................................................................................... 24
3.3.2. Standby Mode ................................................................................................................ 24
3.3.3. Backup Mode ................................................................................................................. 25
3.3.4. Periodic Mode ................................................................................................................ 26
3.3.5. GLP Mode ...................................................................................................................... 27
3.3.6. AlwaysLocate™ Mode ................................................................................................... 28
3.4. Power-up Sequence ................................................................................................................ 29
3.5. Power-down Sequence ........................................................................................................... 30
4 Application Interfaces ....................................................................................................................... 31
4.1. I/O Pins .................................................................................................................................... 31
4.1.1. Communication Interfaces ............................................................................................. 31
4.1.1.1. UART Interface ...................................................................................................... 31
4.1.1.2. I2C Interface .......................................................................................................... 32
4.1.2. ANTON ........................................................................................................................... 33
L76&L76-L_Hardware_Design 6 / 59

4.1.3. 1PPS .............................................................................................................................. 33
4.1.4. System Pin ..................................................................................................................... 34
4.1.4.1. RESET_N .............................................................................................................. 34
5 Design ................................................................................................................................................. 36
5.1. Antenna Design ....................................................................................................................... 36
5.1.1. Antenna Specification .................................................................................................... 36
5.1.2. Antenna Selection Guide ............................................................................................... 36
5.1.3. Active Antenna Reference Design ................................................................................. 37
5.1.3.1. Active Antenna Reference Design without ANTON .............................................. 37
5.1.3.2. Active Antenna Reference Design with ANTON ................................................... 38
5.1.4. Passive Antenna Reference Design .............................................................................. 39
5.1.4.1. Passive Antenna Reference Design without Additional LNA ................................ 39
5.1.4.2. Passive Antenna Reference Design with Additional LNA ..................................... 39
5.2. Coexistence with Cellular Systems ......................................................................................... 40
5.2.1. In-band Interference ....................................................................................................... 41
5.2.2. Out-of-band Interference ................................................................................................ 42
5.2.3. Ensuring Interference Immunity ..................................................................................... 42
5.3. Recommended Footprint ......................................................................................................... 44
6 Electrical Specification ...................................................................................................................... 45
6.1. Absolute Maximum Ratings .................................................................................................... 45
6.2. Recommended Operating Conditions ..................................................................................... 46
6.3. ESD Protection ........................................................................................................................ 47
7 Mechanical Dimensions .................................................................................................................... 48
7.1. Top, Side and Bottom View Dimensions ................................................................................ 48
7.2. Top and Bottom Views ............................................................................................................ 49
8 Product Handling ............................................................................................................................... 50
8.1. Packaging ................................................................................................................................ 50
8.1.1. Tapes ............................................................................................................................. 50
8.1.2. Reels .............................................................................................................................. 51
8.2. Storage .................................................................................................................................... 51
8.3. Manufacturing and Soldering .................................................................................................. 52
9 Labelling Information ........................................................................................................................ 54
10 Appendix References ........................................................................................................................ 55
L76&L76-L_Hardware_Design 7 / 59

Table Index
Table 1: Product Features .......................................................................................................................... 11
Table 2: Product Performance ................................................................................................................... 13
Table 3: GNSS Constellations and Frequency Bands ............................................................................... 15
Table 4: I/O Parameter Definition .............................................................................................................. 18
Table 5: Pinout ........................................................................................................................................... 19
Table 6: Recommended Antenna Specifications ....................................................................................... 36
Table 7: Intermodulation Distortion (IMD) Products................................................................................... 42
Table 8: Absolute Maximum Ratings ......................................................................................................... 45
Table 9: Recommended Operating Conditions .......................................................................................... 46
Table 10: Reel Packaging .......................................................................................................................... 51
Table 11: Recommended Thermal Profile Parameters ............................................................................. 53
Table 12: Related Documents .................................................................................................................... 55
Table 13: Terms and Abbreviations ........................................................................................................... 55
L76&L76-L_Hardware_Design 8 / 59

Figure Index
Figure 1: Block Diagram ............................................................................................................................. 14
Figure 2: Pin Assignment ........................................................................................................................... 18
Figure 3: Internal Power Supply ................................................................................................................. 22
Figure 4: VCC Input Reference Circuit ...................................................................................................... 23
Figure 5: RTC Powered by Non-rechargeable Battery .............................................................................. 23
Figure 6: Reference Charging Circuit for a Rechargeable Battery ............................................................ 24
Figure 7: Enter/Exit from Backup Mode Sequence ................................................................................... 26
Figure 8: Periodic Mode ............................................................................................................................. 27
Figure 9: AlwaysLocate™ Mode ................................................................................................................ 28
Figure 10: Power-up Sequence ................................................................................................................. 29
Figure 11: Power-down Sequence ............................................................................................................. 30
Figure 12: UART Interface Reference Design ........................................................................................... 31
Figure 13: RS-232 Level Shift Circuit ......................................................................................................... 32
Figure 14: I2C Interface Reference Design for L76-L Module ................................................................... 33
Figure 15: 1PPS & NMEA Timing .............................................................................................................. 34
Figure 16: Reference OC Circuit for Module Reset ................................................................................... 34
Figure 17: Reset Sequence ....................................................................................................................... 35
Figure 18: Active Antenna Reference Design without ANTON ................................................................. 37
Figure 19: Reference Design for Active Antenna with ANTON ................................................................. 38
Figure 20: Passive Antenna Reference Design without Additional LNA ................................................... 39
Figure 21: Reference Design for Passive Antenna with Additional LNA ................................................... 40
Figure 22: In-band Interference on GPS L1 ............................................................................................... 41
Figure 23: Out-of-band Interference on GPS L1 ........................................................................................ 42
Figure 24: Interference Source and Its Path .............................................................................................. 43
Figure 25: Recommended Footprint .......................................................................................................... 44
Figure 26: Top, Side and Bottom View Dimensions .................................................................................. 48
Figure 27: Top and Bottom Views .............................................................................................................. 49
Figure 28: Tape and Reel Specifications ................................................................................................... 50
Figure 29: Recommended Reflow Soldering Thermal Profile ................................................................... 52
Figure 30: Labelling Information ................................................................................................................ 54
L76&L76-L_Hardware_Design 9 / 59

1
Product Description
1.1. Overview
The document contains L76, L76-L, L76-L(L) modules. You can choose the dedicated module based on
your requirement.
The modules support multiple global positioning and navigation systems: GPS, GLONASS, Galileo, BDS
and QZSS. These modules also support SBAS (including WAAS, EGNOS, MSAS and GAGAN) and
AGNSS functions. The default constellation configuration is GPS + GLONASS.
Key features:
⚫ All the modules are single-band, multi-constellation GNSS devices and feature high-performance
and high reliability positioning engines. The modules facilitate a fast and precise GNSS positioning
capability.
⚫ All the modules support serial UART communication interfaces. I2C is only supported by L76-L
module.
⚫ Embedded with many advanced power saving modes including GLP, AlwaysLocate™, Standby and
Backup, the modules feature low-power consumption in different scenes.
⚫ All the modules are featured with EASY™ technology, one kind of AGNSS. Capable of collecting and
processing all internal aiding information like GPS time, ephemeris, last position, etc., the modules
deliver a very short Time to First Fix (TTFF) in either hot or warm start.
⚫ The embedded flash memory provides the capacity for storing user-specific configurations and future
firmware updates.
⚫ L76 and L76-L, the standard I/O voltage variants, have 2.7–2.9 V I/O voltage; L76-L(L), the low I/O
voltage variant has a 1.7–1.9 V I/O voltage.
⚫ The three module variants are of a SMD form factor measuring 10.1 mm x 9.7 mm x 2.3 mm and can
be embedded in your application using the 18 LCC pins.
⚫ The three modules are EU ROHS Directive compliant.
L76&L76-L_Hardware_Design 10 / 59

1.2. Features
Table 1: Product Features
Features L76 L76-L L76-L(L)
Industrial   
Grade
Automotive - - -
Standard Precision
  
GNSS
High Precision GNSS - - -
Category DR - - -
RTK - - -
Timing - - -
VCC Supply 2.8–4.3 V, Typical: 3.3 V   
V_BCKP Supply 1.5–4.5 V, Typical: 3.3 V   
Typical: 2.8 V   -
I/O
Typical: 1.8 V - - 
UART   
Communication
SPI - - -
Interfaces
I2C 1 -  -
Additional LNA -  
Additional Filter   
Features RTC crystal   
TCXO oscillator   
6-axis IMU - - -
Constellations Number of Concurrent 3 + QZSS 3 + QZSS 3 + QZSS
1 The I2C interface is supported only on certain firmware versions.
L76&L76-L_Hardware_Design 11 / 59

Features L76 L76-L L76-L(L)
and Frequency GNSS
Bands
L1 C/A   
GPS
L5 - - -
GLONASS L1   

E1  
Galileo
E5a - - -
B1I   
BDS
B2a - - -
L1 C/A   
QZSS
L5 - - -
NavIC L5 - - -
SBAS L1   
Temperature Operating temperature range: -40 °C to +85 °C
Range Storage temperature range: -40 °C to +90 °C
Physical Size: (10.1 ±0.15) mm × (9.7 ±0.15) mm × (2.3 ±0.20) mm
Characteristics Weight: Approx. 0.5 g
NOTE
For more information about GNSS constellation configuration, see document [1] protocol specification.
L76&L76-L_Hardware_Design 12 / 59

1.3. Performance
Table 2: Product Performance
Parameter Specification L76 L76-L L76-L(L)
25 mA 31 mA 31 mA
Acquisition
(82.5 mW) (102.3 mW) (102.3 mW)
18 mA 31 mA 31 mA
Tracking
(59.4 mW) (102.3 mW) (102.3 mW)
Power Consumption 2
0.5 mA 0.5 mA 0.5 mA
Standby mode
(1.65 mW) (1.65 mW) (1.65 mW)
7 μA 8 μA 8 μA
Backup mode
(23.1 μW) (26.4 μW) (26.4 μW)
Acquisition -148 dBm -149 dBm -149 dBm
Sensitivity Reacquisition -160 dBm -161 dBm -161 dBm
Tracking -165 dBm -167 dBm -167 dBm
Cold Start 15 s 15 s 15 s
TTFF 2
Warm Start 5 s 5 s 5 s
(with AGNSS)
Hot Start 1 s 2 s 2 s
Cold Start 35 s 32 s 32 s
TTFF 3
Warm Start 30 s 30 s 30 s
(without AGNSS)
Hot Start 1 s 2 s 2 s
Horizontal Position Accuracy 4 2.5 m
Update Rate 1 Hz (Max. 10 Hz)
Accuracy of 1PPS Signal Typical accuracy: 100 ns
Velocity Accuracy 2 Without aid: 0.1 m/s
Acceleration Accuracy 2 Without aid: 0.1 m/s²
2 Room temperature, all satellites at -130 dBm.
3 Open-sky, active high precision GNSS antenna, less than 1 km baseline length.
4 CEP, 50 %, 24 hours static, -130 dBm, more than 6 SVs.
L76&L76-L_Hardware_Design 13 / 59

Parameter Specification L76 L76-L L76-L(L)
Maximum Altitude: 10000 m
Dynamic Performance 2 Maximum Velocity: 515 m/s
Acceleration: 4g
1.4. Block Diagram
The following figure shows a block diagram of the modules. The modules include a GNSS IC, an
additional LNA (only supported by L76-L and L76-L(L)), an additional SAW filter, a TCXO and a XTAL.
The LNA is less susceptible to in-band interference in challenged environment (i.e. with a cellular module
transmitting B13 at the same time). This ensures enhanced performance in an environment where
jamming may be encountered.
Saw Active VCC
RF Front-
filter End Interference VDD_RF
RF_IN LNA Cancellation PMU V_BCKP
Integrated
LNA WAKEUP
GNSS
(Only supported by F S r y a n c t t h io e n s a z l e -N r Engine
L76-L and L76-L(L)) TCXO I2C(Only supported by L76-L )
UART
Peripheral RESET_N
ROM controller STANDBY
1PPS
ARM7
Processor ANTON
RAM
Flash RTC
32.768K XTAL
Figure 1: Block Diagram
1.5. GNSS Constellations
The module is a single-band concurrent GNSS receiver that can receive and track multiple GNSS signals.
Owing to its RF front-end architecture, it can track the following GNSS constellations: GPS, GLONASS,
Galileo, BDS, and QZSS, plus SBAS satellites. If low power consumption is a key factor, the module can
be configured to track only a subset of GNSS constellations.
QZSS is a regional navigation satellite system that transmits signals compatible with the GPS L1 C/A,
L1C, L2C and L5 signals for the Pacific region covering Japan and Australia. The module can detect and
L76&L76-L_Hardware_Design 14 / 59

track QZSS L1 C/A signal concurrently with GPS signals, leading to better availability especially under
challenging conditions, e.g., in urban canyons.
Table 3: GNSS Constellations and Frequency Bands
System Signal
GPS L1 C/A: 1575.42 MHz
GLONASS L1: 1602 MHz + K × 562.5 kHz, K= (-7 to +6, integer)
Galileo E1: 1575.42 MHz
BDS B1I: 1561.098 MHz
QZSS L1 C/A: 1575.42 MHz
1.6. Augmentation System
1.6.1. SBAS
The modules all support SBAS (Satellite-Based Augmentation System) broadcast signal reception, and
GPS data are complemented by additional regional or wide area GPS enhancement data. The system
enhances the data through satellite broadcasting, and the data can be used in GNSS receivers to improve
the accuracy of the results. SBAS satellites can also be used as additional signals for range or distance
measurement, further improving availability. Supported SBAS systems include WAAS, EGNOS, MSAS
and GAGAN.
1.7. AGNSS
The module supports AGNSS feature that significantly reduces the module’s TTFF, especially under
lower signal conditions. To implement the AGNSS feature, the module should get the assistance data
including the current time and rough position. For more information, see document [2] AGNSS application
note.
1.7.1. EASY
The modules support the EASY feature to improve TTFF and improve the acquisition sensitivity. To
achieve that goal, the EASY feature provides assistant information, such as the ephemeris, almanac, last
rough position, time, and a satellite status.
L76&L76-L_Hardware_Design 15 / 59

EASY feature works as embedded software which can accelerate TTFF by predicting satellite navigation
messages from received ephemeris. The GNSS engine automatically calculates and predicts orbit
information for up to 3 days after first receiving the broadcast ephemeris, and saves the predicted
information into the internal memory. The GNSS engine will use the information for positioning if there is
not enough information from satellites. As a result, the function is helpful for positioning and TTFF
improvement.
The EASY function can reduce TTFF to 5 s in warm start. In this case, RTC domain should be valid. In
order to gain enough broadcast ephemeris information from GNSS satellites, the GNSS module should
keep tracking the information for at least 5 minutes in good signal conditions after it fixes the position.
EASY function is enabled by default. For more information about the corresponding command to disable
EASY function, see document [1] protocol specification.
1.7.2. EPO
The modules all feature a function called EPO (Extended Prediction Orbit) which is a world leading
technology that supports 14-day orbit predictions to customers. Occasional download from the EPO
server is needed. For more information, see document [2] AGNSS application note.
1.8. LOCUS
These modules support the embedded logger function called LOCUS. This function can automatically log
position information to internal flash memory when enabled by dedicated LOCUS commands. With this
function, the host can save power consumption and does not need to track the NMEA information all the
time. LOCUS provides typically more log capacity without any added costs.
Software commands can be used to query the current state of LOCUS. For more information about these
commands, see document [1] protocol specification.
The raw data which MCU gets must be parsed via LOCUS parser code provided by Quectel. For more
details, please contact Quectel technical support.
1.9. Multi-tone AIC
The modules all support a function called Active Interference Cancellation (multi-tone AIC) to decease
harmonic distortion of GNSS signal induced by RF signal from Wi-Fi, Bluetooth, and the 2G and 3G
networks.
L76&L76-L_Hardware_Design 16 / 59

Up to 12 multi-tone AIC embedded in each module can provide effective narrow-band interference and
jamming elimination. The GNSS signal could be demodulated from the jammed signal, which can ensure
better navigation quality. AIC function is enabled by default. For more information about the commands
that can be used to set AIC function, see document [1] protocol specification.
L76&L76-L_Hardware_Design 17 / 59

2
Pin Assignment
The modules are equipped with 18 LCC pins by which they can be mounted on the PCB.
L76&L76-L_Hardware_Design 18 / 59
S
R
T
V
E
A
_
G
1 P
N D
B C
E T
N
X
P
B
K
C
D
Y
I/O
3
4
5
6
7
8
9
P O W E R
L
&
(
&
o
p
-
ie
w
Y
(
)
-
)
M A N T
0
N C
W
RI2
RI2
EC
EC
F
K E
S E
_ S
S E
_ S
D _
T O
_ IN
U
RC
RD
VL
VA
/
/
Figure 2: Pin Assignment
Table 4: I/O Parameter Definition
Type Description
AI Analog Input
DI Digital Input
DO Digital Output
DIO Digital Input/Output

Type Description
PI Power Input
PO Power Output
Table 5: Pinout
Function Name No. I/O Description Remarks
Requires clean and steady
voltage.
VCC 8 PI Main power supply
Assure load current not less
Power than 150 mA.
Supplies power to the RTC
Backup power supply for
V_BCKP 6 PI domain when VCC power
RTC domain
supply is disconnected.
TXD 2 DO Transmits data UART port is used for NMEA
output, PMTK/PQ commands
RXD 3 DI Receives data input and firmware upgrade.
For L76/L76-L(L) modules,
RESERVED/ keep it open. For L76-L
16 DIO For L76-L module, I2C Interface
I2C_SDA module, this pin is
outputs NMEA data by default
I2C_SDA.
when reading; it can also
For L76/L76-L(L) modules,
receive PMTK/PQ commands
RESERVED/ keep it open. For L76-L
17 DIO through I2C bus.
I2C_SCL module, this pin is
I2C_SCL.
Control the ENABLE pin of
additional LNA and the If unused, leave the pin N/C (not
I/O ANTON 13 DO
power supply of active connected).
antenna.
The pin is pulled up internally. It
Enter or exit from Standby is edge-triggered.
STANDBY 5 DI
mode If unused, leave the pin N/C (not
connected).
Keep this pin open or pulled low
before entering Backup mode. It
Wake up the modules from
WAKEUP 18 DI belongs to RTC domain.
Backup mode
If unused, leave the pin N/C (not
Synchronized on rising edge,
1PPS 4 DO One pulse per second
and the pulse width is 100 ms.
L76&L76-L_Hardware_Design 19 / 59

Function Name No. I/O Description Remarks
VDD_RF = VCC, the output
current capacity depends on
VCC.
Power supply for external Typically used to supply power
VDD_RF 14 PO
RF components for an external active antenna or
Antenna
LNA.
RF_IN 11 AI GNSS antenna interface 50 Ω characteristic impedance.
System RESET_N 9 DI Resets the modules Active low.
Ensures good GND connections
1,
to all GND pins of the modules,
GND GND 10, - Ground
with a large ground plane
12
preferred.
7, If unused, leave the pin N/C (not
NC NC - Not connected
15 connected).
Leave RESERVED and unused pins N/C (not connected).
L76&L76-L_Hardware_Design 20 / 59

Power Management
These modules provide a power optimized architecture with built-in autonomous energy saving
capabilities to minimize power consumption at any given time. The receiver can be used in six operating
modes: Periodic mode, AlwaysLocate™ mode, GLP mode, Standby mode, and Backup mode for best
power consumption and Continuous mode used for best performance.
3.1. Power Unit
VCC is the supply voltage pin of the modules. It supplies power for the PMU which in turn supplies the
entire system and RTC domains. The load current of the VCC pin varies according to VCC voltage level,
processor load, and satellite acquisition. It is important to supply sufficient current and make sure the
power supply is clean and stable.
The V_BCKP pin supplies power for the RTC domain. If the VCC voltage drops under the acceptable
level, the V_BCKP pin keeps the RTC domain powered. To achieve quick startup and improve TTFF, the
RTC domain power supply should be valid during the interval when the VCC pin does not have a valid
level. SRAM memory also belongs to the RTC domain. If the VCC is not valid, the V_BCKP pin supplies
power for SRAM memory that contains all the necessary GNSS data and some of the user configuration
variables.
VDD_RF is an output pin, equal in voltage to the VCC input. In Continuous mode, VDD_RF pin supplies
power for the external active antenna or the LNA. In Standby mode, VDD_RF pin is turned off.
The two diodes in the following figure construct an OR gate to supply power for RTC domain. WAKEUP
pin belongs to RTC domain. The signal shown as red line in Figure 3 can open and close the switch. The
following steps will close or open the switch:
Step 1: The switch will be closed by default when VCC pin is supplying power (VCC off on).
Step 2: Keeping WAKEUP open or low and sending PMTK command can open the switch
(Continuous Backup).
Step 3: Keeping WAKEUP logic high can close the switch (Backup Continuous).
The modules’ internal power supply is shown below:
L76&L76-L_Hardware_Design 21 / 59

L76&L76-L_Hardware_Design 22 / 59
A R M
L o g ic
c irc u it
R T C
p o w e r
M U
R T C
U P
Figure 3: Internal Power Supply
3.2. Power Supply
3.2.1. VCC
The VCC pin supplies power for BB, RF, and RTC domain. VCC pin load current varies according to VCC
voltage level, processor load and satellite acquisition state.
Module power consumption may vary in several orders of magnitude, especially when low power mode is
enabled. Therefore, it is important that the power supply can sustain peak power for a short time, ensuring
that the load current does not exceed the rated value. When the modules switch from Backup mode to
normal operation or startup, it must charge the internal capacitors in the core domain. In some cases, this
can lead to a significant current drain.
For low-power applications using power saving and backup modes, it is important that the LDO at the
power supply or module input can provide the current/drain. An LDO with a high PSRR should be chosen
for good performance. In addition, a TVS diode, and a combination of a 10 μF, 100 nF and a 33 pF
decoupling capacitor network should be added near the VCC pin. The lowest value capacitor should be
the closest to module pins.
It is not recommended to use a switching DC-DC power supply.

L76&L76-L_Hardware_Design 23 / 59
1 0 µ
C C
1 0 0 n F 3 3 p F
E S D 5
5 1
P M U
M o d u le
Figure 4: VCC Input Reference Circuit
3.2.2. V_BCKP
The V_BCKP pin supplies power for the RTC domain. If the module power supply fails, the V_BCKP pin
supplies power for the real-time clock (RTC) and RAM. Use of valid time and GNSS orbit data at startup,
allows GNSS hot (warm) start. If no backup power is connected, the modules perform a cold start at
power up.
If there is a constant power supply in your system, it can be used to provide a suitable voltage to power
V_BCKP.
V_BCKP can be directly powered by an external battery (rechargeable or non-rechargeable). It is
recommended to place a battery with the combination of a 4.7 μF, a 100 nF and a 33 pF capacitor near
the V_BCKP pin. The figure below illustrates the reference design for supplying power for the RTC
domain with a non-rechargeable battery.
r ea cc hk
Nau o n -
r g e a
p B a
b le
tte r y 4
.7
μ
C K P
1 0 0 n F 3 3 p F
Ro Tm Ca
M
in
o d u le
Figure 5: RTC Powered by Non-rechargeable Battery

If V_BCKP is powered by a rechargeable battery, it is necessary to implement an external charging circuit
for the battery. A reference charging circuit is illustrated below.
1K
VCC
Module
V_BCKP
RTC
Domain
Rechargeable
Backup Battery
4.7 μF 100 nF 33 pF
Figure 6: Reference Charging Circuit for a Rechargeable Battery
3.3. Power Mode
3.3.1. Continuous Mode
If VCC is powered on, the modules automatically enter Continuous mode. Continuous mode comprises
acquisition mode and tracking mode. In acquisition mode, the modules start to search satellites, and to
determine visible satellites, coarse frequency, as well as the code phase of satellite signals. When the
acquisition is completed, the modules automatically switch to tracking mode. In tracking mode, the
modules track satellites and demodulate the navigation data from specific satellites.
3.3.2. Standby Mode
Standby mode is a low-power consumption mode. In Standby mode, the internal core and I/O power
domain are still active, but RF and TCXO are powered off, and the modules stop satellites search and
navigation. The UART interface still receives commands or any other data in Standby mode, but NMEA
messages can’t be output via the interface.
The following describes how to enter or exit from Standby mode:
⚫ Pulling STANDBY pin low will make the GNSS module enter Standby mode and releasing STANDBY
pin which has been pulled high internally will make the modules back to Continuous mode. Note that
pulling down STANDBY pin to ground will cause the extra current consumption which makes the
typical Standby current reach to about 600 μA @ VCC=3.3 V.
L76&L76-L_Hardware_Design 24 / 59

⚫ Sending corresponding command will make the modules enter Standby mode. Sending any data via
UART will make the modules exit standby mode as UART is still accessible in Standby mode.
When the modules exit from Standby mode, it will use all internal aiding information like GPS time,
ephemeris, last position, etc., resulting in the fastest possible TTFF in either hot or warm start. For more
information about these commands to enter or exit from Standby mode, see document [1] protocol
specification.
The STANDBY pin is edge-triggered, so the modules may unexpectedly enter Standby mode when it
starts. To avoid this, it is recommended to set your GPIO which controls STANDBY pin as input before
the modules start. After that, you can reset the GPIO as output to control the STANDBY pin. If it is
unused, keep it open.
3.3.3. Backup Mode
For power-sensitive applications, the module receiver provides a Backup mode to reduce power
consumption.
Backup mode requires lower power consumption than Standby mode. In this mode, the modules stop
acquiring and tracking satellites. The UART is not accessible. But the backed-up memory in RTC domain
which contains all the necessary GPS information for quick start-up and a small amount of user
configuration variables is maintained. Due to the backed-up memory, EASY™ technology is available.
If the power supply to VCC pin is cut off and V_BCKP pin is powering the RTC domain, the modules
switch from Continuous mode to Backup mode. Only RTC domain is active in Backup mode and it keeps
tracking time. As soon as the VCC pin is powered, the modules immediately switch to Continuous mode.
The following describes how to switch between Backup mode and Continuous mode.
⚫ Keep the WAKEUP pin open or low (the signal shown as red line in Figure 3: Internal Power Supply)
and send software command to enter Backup mode. The only way to wake up the modules is by
pulling the WAKEUP pin high (signal shown as a red line in Figure 3: Internal Power Supply). For
more information about the command, see document [1] protocol specification.
⚫ Cutting off the power supply to VCC pin and keeping V_BCKP pin powered will make the modules
exit from Continuous mode and enter Backup mode.
L76&L76-L_Hardware_Design 25 / 59

L76&L76-L_Hardware_Design 26 / 59
C K
U P
R T
o n tin u
o u
a
s
E n te r B a c k u
m o d e
lid
S e n d in g
c o m m a n d
B a
In
c k
v
u
a
m o
≥
d
E x it fro m
a c k u p m o
1 0 m s
e
P u llin g
W A K E U P
H ig h
d e
C o n
tin
a lid
u o u s
m
Cp
n
uo
te r B a c k u p
B d e
ttin g o ff th e
w e r s u p p ly
o f V C C
a c
In v a
k u p
B a
o d
Ec
xk
it fro m
u p m o d e
V a lid
C o n tin u
to re V C C
o u s m o d e
Figure 7: Enter/Exit from Backup Mode Sequence
Keep WAKEUP pin open or low before entering Backup mode. Or else, the Backup mode will be
unavailable.
3.3.4. Periodic Mode
Periodic mode is a mode that can control the Continuous mode and Standby/Backup mode periodically to
reduce power consumption. It contains Periodic standby mode and Periodic backup mode.
The modules enter or exit from the Periodic mode through software commands. For more information
about these commands, see document [1] protocol specification.
The following figure has shown the operation of Periodic mode. When you send corresponding command,
the modules will be into the Continuous mode. After several minutes, the modules enter the Periodic
mode and follows the parameters. When the modules fail to fix the position in Run time, the modules will
switch to Second run time and Second sleep time automatically. As long as the modules fix the position
again, the modules will return to Run time and Sleep time.
The average current value can be calculated by the following formula:
I = (I × T1+I × T2) / (T1 + T2)
periodic tracking standby/backup
T1: Run time, T2: Sleep time

Power
Continuous
Run time Run time Second run time Second run time Run time Run time
mode
Sleep time Sleep time Second sleep time Second sleep time Sleep time Sleep time
Figure 8: Periodic Mode
1. The STANDBY pin is edge-triggered, so the modules may unexpectedly enter Periodic standby
mode when it starts. To avoid this, it is recommended to set your GPIO which controls STANDBY
pin as input before the modules start. After that, you can reset the GPIO as output to control the
STANDBY pin. If it is unused, keep it open.
2. Keep WAKEUP pin open or low before entering Periodic backup mode. Or else, the Periodic
backup mode will be unavailable.
3. Before entering Periodic mode, assure the modules are in the tracking mode; otherwise, the
modules will have a risk of failure to track the satellite. If GNSS module is located under weak signal
environment, it is better to set a longer Second run time to ensure the success of reacquisition.
3.3.5. GLP Mode
The GLP (GNSS Low Power) mode is an optimized solution for wearable fitness and tracking devices. It
reduces power consumption by disabling high accuracy positioning.
In GLP mode, the modules provide relatively good positioning performance walking or running in dynamic
scenarios. The modules automatically switch to Continuous mode under challenged environment to keep
better accuracy. As a result, the modules can still achieve maximum performance with the lowest power
Software commands can make the modules enter or exit from GLP mode. For more information about
these commands, see document [1] protocol specification.
L76&L76-L_Hardware_Design 27 / 59

1. When the modules enter GLP mode, the 1PPS and the SBAS functions are disabled.
2. In highly dynamic scenarios, the positioning accuracy of the modules in GLP mode is slightly
reduced.
3.3.6. AlwaysLocate™ Mode
AlwaysLocate™ is an intelligent power saving mode. It contains AlwaysLocate™ backup mode and
AlwaysLocate™ standby mode.
AlwaysLocate™ standby mode allows the modules to switch automatically between Continuous mode
and Standby mode. According to the environmental and motion conditions, the modules can adaptively
adjust the Continuous time and Standby time to achieve the balance between positioning accuracy and
power consumption. Sending software command and the modules returning a corresponding command
means the modules access AlwaysLocate™ standby mode successfully. It will benefit power saving in
this mode. Sending software command in any time will make the modules back to Continuous mode.
AlwaysLocate™ backup mode is like AlwaysLocate™ standby mode. The difference is that
AlwaysLocate™ backup mode switches automatically between Continuous mode and Backup mode.
Sending software command makes the modules enter AlwaysLocate™ backup mode. Pulling WAKEUP
high and immediately sending software command will make the modules enter Continuous mode.
For more information about these commands, see document [1] protocol specification.
The position accuracy in AlwaysLocate™ mode will be degraded, especially in highly dynamic scenarios.
The following figure shows the rough consumption in different scenes.
Figure 9: AlwaysLocate™ Mode
L76&L76-L_Hardware_Design 28 / 59

Example
The average consumption of the modules which are located outdoors in a static position and equipped
with an active antenna after tracking satellites is about 2.7 mA in AlwaysLocate™ standby mode based
on GPS + GLONASS.
The average consumption of the modules which are located in outdoors in static and equipped active
antenna after tracking satellites is about 2.6 mA in AlwaysLocate™ backup mode based on GPS +
GLONASS.
1. The STANDBY pin is edge-triggered, so the modules may unexpectedly enter AlwaysLocate™
standby mode when they start. To avoid this, it is recommended to set your GPIO which controls
STANDBY pin as input before the modules start. After that, you can reset the GPIO as output to
control the STANDBY pin. If it is unused, keep it open.
2. Keep WAKEUP pin open or low before entering AlwaysLocate™ backup mode. Or else, the
AlwaysLocate™ backup mode will be unavailable.
3.4. Power-up Sequence
When VCC is powered up, the modules start up automatically.
To ensure correct power-up sequence, the RTC logic should start up before the PMU. So, the V_BCKP
must be supplied with power at the same time or before the VCC.
Ensure that the VCC has no rush or drop during rising time, and then keep the voltage stable. The
recommended ripple is < 100 mV.
V_BCKP Don t care
0 s
UART Invalid Valid
Figure 10: Power-up Sequence
L76&L76-L_Hardware_Design 29 / 59

3.5. Power-down Sequence
When the VCC is shut down, voltage should drop quickly with a drop time of less than 50 ms. It is
recommended to use a voltage regulator that supports fast discharge.
To avoid abnormal voltage condition, if VCC falls below specified minimum value, the system must initiate
a power-on reset by lowering VCC to less than 100 mV for at least 100 ms.
below 100 mV
< 50 ms 0 s
below 100 mV > 100 ms
UART valid Invalid Valid
Figure 11: Power-down Sequence
L76&L76-L_Hardware_Design 30 / 59

Application Interfaces
4.1. I/O Pins
4.1.1. Communication Interfaces
The following interfaces can be used for data reception and transmission.
4.1.1.1. UART Interface
The three modules all provide one UART interface. The UART port has the following features:
⚫ Support for firmware upgrade, NMEA output and PMTK/PQ proprietary messages input.
⚫ Supported baud rates: 4800, 9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, and
921600 bps.
⚫ Default settings: 9600 bps, 8 bits, no parity bit, 1 stop bit.
⚫ Hardware flow control and synchronous operation are not supported.
A reference design is shown in the figure below.
Customer Module
TXD TXD
RXD RXD
GND GND
Figure 12: UART Interface Reference Design
If the I/O voltage of MCU is not matched with that of the modules, a level shifter must be selected.
L76&L76-L_Hardware_Design 31 / 59

The UART port does not support the RS-232 level shifter but only CMOS level shifter. If the module’s
UART port is connected to the UART port of a computer, it is necessary to add a level shift circuit between
the module and the computer. Please refer to the following figure.
L76&L76-L_Hardware_Design 32 / 59
3 .3 V
2 8
2 5
2 4
2 3
2 2
1 9
1 7
1 6
2 1
2 0
1 8
1 3
C 1 +
C 1 -
C 2 +
C 2 -
T 1 IN
T 2 IN
T 3 IN
T 4 IN
T 5 IN
/R 1 O U T
R 1 O U T
R 2 O U T
R 3 O U T
O N L IN E
S P 3 2
/S
H
/S
U T
V +
G N D
V C C
V -
4 O U T
2 O U T
3 O U T
1 O U T
5 O U T
R 1 IN
R 2 IN
R 3 IN
A T U S
O W N
2 7
2 6
1 0
1 2
1 1
1 5
1 4
3 .3 V
T o P C S e ria l P o
rt
12
4 5
G N D
Figure 13: RS-232 Level Shift Circuit
As the GNSS module outputs more data than a single GPS system, the default output NMEA messages
running at 4800 bps baud rate and at a 1 Hz update rate may result in data loss. The solution to avoid
losing data is to decrease the output NMEA types and increase the baud rate to 9600 bps.
4.1.1.2. I2C Interface
The L76-L module provides one I2C interface which is supported only on certain firmware versions. The
I2C features are listed below:
⚫ Supports NMEA data output and receive PMTK/PQ commands via I2C bus.
⚫ Supports fast mode, with bit rate up to 400 kbps.
⚫ Supports 7-bit address.
⚫ Works in slave mode.
⚫ Default I2C address values are: Write: 0x20; Read: 0x21.

For more information, see document [3] reference design.
IO
Customer Module
R1 R2
4K7 4K7
SDA I2C_SDA
SCL I2C_SCL
GND GND
Figure 14: I2C Interface Reference Design for L76-L Module
1. I2C_SDA/I2C_SCL should be externally pulled up to V = 2.8 V.
IO
2. The I2C voltage threshold of L76-L module is 2.8 V. If the system voltage of MCU is not consistent
with it, a level shifter circuit must be used.
4.1.2. ANTON
The modules provide a pin called ANTON which is related to module state. Its voltage level will change in
different module states. When the modules work in Continuous mode, this pin is in high level. While the
modules work in Standby mode, GLP mode, Backup mode, AlwaysLocate™ mode, and during sleep time
in periodic mode, this pin is in low level. Based on this characteristic, the ANTON pin can be used to
control the power supply of active antenna or the ENABLE pin of the additional LNA to reduce power
4.1.3. 1PPS
The 1PPS output generates one pulse per second trains synchronized with a GPS or UTC time grid with
intervals configurable over a wide range of frequencies. The accuracy is < 100 ns. Thus, it may be used
as a low frequency time synchronization pulse or as a high frequency reference signal.
The latency range is 465-485 ms between the beginning of UART TXD and the rising edge of PPS.
L76&L76-L_Hardware_Design 33 / 59

L76&L76-L_Hardware_Design 34 / 59
1 P
R T
4 6 5 m s ~ 4
8 5
T C
2 :0
0 :0
:0 0 :0 0
U T C 1
2 :0
0 :0 1
1 2 :0 0 :0 1
Figure 15: 1PPS & NMEA Timing
The feature only supports 1 Hz NMEA output at baud rate 19200-115200 bps. Because at lower baud
rates, the time needed for transmission may exceed 1 second if there are many NMEA sentences. For
more information about the commands to enable/disable this function, see document [1] protocol
specification.
4.1.4. System Pin
4.1.4.1. RESET_N
RESET_N is an input pin. The modules can be reset by driving RESET_N low for at least 100 ms and
then releasing it.
The pin is pulled up internally by default. As the power domain of RESET_N is 2.8 V/1.8 V and the pin has
been pulled up inside the modules, no external pull-up circuit is allowed for this pin.
An OC driver circuit as shown below is recommended to control the RESET_N pin.
RESET_N
4.7K
Input pulse
47K
Figure 16: Reference OC Circuit for Module Reset

Not cared
Pull down
> 100 ms
UART Invalid Valid Invalid Valid
Figure 17: Reset Sequence
1. Ensure RESET_N is connected so that it can be used to reset the modules if the modules enter an
abnormal state.
2. The power domain of RESET_N is 2.8 V for L76/L76-L modules, 1.8 V for L76-L(L) module.
L76&L76-L_Hardware_Design 35 / 59

Design
5.1. Antenna Design
5.1.1. Antenna Specification
The module can be connected to a dedicated passive or an active single-band GNSS antenna in order to
track the GNSS satellite signals. The recommended antenna specifications are given in the table below.
Table 6: Recommended Antenna Specifications
Antenna Type Specifications
Frequency Range: 1559–1609 MHz
Polarization: RHCP
Passive Antenna
VSWR: < 2 (Typ.)
Passive Antenna Gain: > 0 dBi
Frequency Range: 1559–1609 MHz
Polarization: RHCP
VSWR: < 2 (Typ.)
Active Antenna
Passive Antenna Gain: > 0 dBi
Active Antenna Noise Figure: < 1.5 dB
Active Antenna Total Gain: < 18 dB
1. For recommended antenna and design, see document [4] GNSS antenna selection&application
guide or contact Quectel Technical Support (support@quectel.com).
2. The total antenna gain equals the internal LNA gain minus total insertion loss of cables and
components inside the antenna.
5.1.2. Antenna Selection Guide
Both active and passive GNSS antennas can be used for the three modules. A passive antenna is
recommended if the antenna can be placed close to the modules, for instance, when the distance
between the modules and the antenna is less than 1 m. Otherwise, use an active antenna, since the
L76&L76-L_Hardware_Design 36 / 59

insertion loss of RF cable can decrease the CNR of GNSS signal.
CNR is an important factor for GNSS receivers, and it is defined as the ratio of the received modulated
carrier signal power to the received noise power in one Hz bandwidth. CNR formulais as below:
The “Power of GNSS signal” is GNSS signal level. In practical environment, the signal level at the earth
surface is about -130 dBm. “Thermal Noise” is -174 dBm/Hz at 290 K. To improve CNR of GNSS signal, a
LNA could be added to reduce “System NF”.
“System NF”, formula:
“F” is the noise factor of receiver system:
“F1” is the first stage noise factor, “G1” is the first stage gain, etc. This formula indicates that LNA with
enough gain can compensate for the noise factor behind the LNA. In this case, “System NF” depends
mainly on the noise figure of components and traces before first stage LNA plus noise figure of LNA itself.
This explains the need for using an active antenna, if the antenna connection cable is too long.
5.1.3. Active Antenna Reference Design
5.1.3.1. Active Antenna Reference Design without ANTON
The following figure is a typical reference design of an active antenna without ANTON. In this case, the
antenna is powered by the VDD_RF. When selecting the active antenna, it is necessary to pay attention
to operating voltage range.
L76&L76-L_Hardware_Design 37 / 59
Hn
74
1L
R2 10R
MN
2C
3C
π Matching Circuit Module
C1 100 pF
R1
RF_IN
0R
VDD_RF
Fp
001
4C
Fn
001
5C
D1
TVS
Figure 18: Active Antenna Reference Design without ANTON

The components C2, R1 and C3 are reserved for matching antenna impedance. By default, R1 is 0 Ω,
while C2 and C3 are not mounted; C1 is 100 pF; D1 is an electrostatic discharge (ESD) protection device
to protect the RF signal input from the potential damage caused by ESD.
An active antenna can use the power supply from the VDD_RF pin. In that case, the inductor L1 is used to
prevent the RF signal from leaking into the VDD_RF and to prevent noise propagation from the VDD_RF
to the antenna. The L1 inductor routes the bias voltage to the active antenna without losses. The
recommended value of L1 is no less than 47 nH. The resistor R2 is used to protect the modules in case
the active antenna is short-circuited to the ground plane.
The existing footprints in the matching circuit can be used to mount other type of components than the
ones presented in the figure above. In that case, you must pay attention to the DC power supply. For
example, if an inductor is mounted on the C1 footprint, then the circuit needs a DC-blocking capacitor
between L1 and C1 to prevent short-circuiting of the DC power supply through the inductor to the ground.
The same applies to the C2 footprint.
5.1.3.2. Active Antenna Reference Design with ANTON
All the modules can also reduce power consumption by controlling the power supply of active antenna
through the ANTON pin.
The reference circuit for active antenna with ANTON function is given as below.
π Matching Circuit Module
D1 R3
0R
TVS C1 NM C2 NM
H
L 10R
VDD_RF
F F
p n R1
0 0 R2
0 1 0 1 Q1 10K
4 5
Q2
Power Control Circuit ANTON
Figure 19: Reference Design for Active Antenna with ANTON
ANTON is an optional pin which can be used to control the power supply of the active antenna. When the
ANTON pin is pulled down, MOSFET Q1 and Q2 are in high impedance state and the power supply for
antenna is cut off. When ANTON pin is pulled high, it will make Q1 and Q2 in the on-state, and VDD_RF
L76&L76-L_Hardware_Design 38 / 59

will provide power supply for the active antenna. The high and low level of ANTON pin is determined by
the modules’ state.
For minimizing the current consumption, the value of resistor R2 should not be too small, and the
recommended value is 10 kΩ.
5.1.4. Passive Antenna Reference Design
5.1.4.1. Passive Antenna Reference Design without Additional LNA
The following figure is a typical reference design of a passive antenna.
L76&L76-L_Hardware_Design 39 / 59
P a s
1D
s iv e A n
SVT
te n n a
1C
π M a tc h
g C ir c u it
2C
R F _ IN
Figure 20: Passive Antenna Reference Design without Additional LNA
The components C1, R1 and C2 are reserved for matching antenna impedance. By default, R1 is 0 Ω,
while C1 and C2 are not mounted. D1 is an electrostatic discharge (ESD) protection device to protect one
signal line from the damage caused by ESD. The impedance of RF trace should be controlled to 50 Ω and
the trace length should be kept as short as possible.
5.1.4.2. Passive Antenna Reference Design with Additional LNA
In order to improve the receiver sensitivity and reduce the TTFF, an additional LNA between the passive
antenna and the module is recommended. The reference design is shown as below.

Module
Passive Antenna
π Matching Circuit C3 56 pF
RF OUT
R1 ENABLE
RF IN VCC
M 0R M
N N
LNA
R2
ANTON
100R
R3
No need to add for L76-L And L76-L(L) VDD_RF
which has an embedded LNA 100R
Figure 21: Reference Design for Passive Antenna with Additional LNA
C1, R1, C2 form a reserved matching circuit for passive antenna and LNA. By default, C1 and C2 are not
mounted; R1 is 0 Ω. C3 is reserved for impedance matching between LNA and the module and the default
value of C3 capacitor is 56 pF which you might optimize according to the real conditions. ANTON is an
optional pin which can be used to control the ENABLE pin of an additional LNA.
1. There is no need to use an additional LNA for L76-L and L76-L(L) modules, because there is
already an embedded LNA inside these two modules.
2. The selected LNA should support both GPS and GLONASS system. For more information, please
contact Quectel technical supports.
3. The power consumption of the device can be reduced by controlling the LNA ENABLE pin through
the ANTON pin of the modules. If ANTON function is not used, please connect the LNA ENABLE
pin to VCC and keep LNA always on.
5.2. Coexistence with Cellular Systems
Since GNSS signals are usually very weak, a GNSS receiver could be vulnerable to environmental
interference. According to 3GPP specifications, a cellular terminal should transmit a signal of up to
33 dBm at GSM bands, or of about 24 dBm at WCDMA and LTE bands, or of about at 26 dBm at 5G
bands. Therefore, coexistence with cellular systems must be optimized to avoid significant deterioration of
the GNSS performance.
In a complex communication environment, interference signals can come from in-band and out-of-band
signals. Therefore, interference can be divided into two types: in-band interference and out-of-band
L76&L76-L_Hardware_Design 40 / 59

interference, which are both described in this chapter.
In this chapter, you can also find suggestions for decreasing the impact of interference signals that will
ensure the interference immunity of a GNSS receiver.
5.2.1. In-band Interference
I n-band interference refers to the signal whose frequency is within or near the operating frequency range
of a GNSS signal. For example, GPS L1 is centered at 1575.42 MHz with a bandwidth of 2.046 MHz. As
shown in the figure below, the frequency of the interfering signal is within the GPS operation band, and
the power of the interfering signal is higher than the power of the received GPS signal.
See the following figure for more details.
L76&L76-L_Hardware_Design 41 / 59
-1 1
w
e r [d
5 2 5
B m ]
P S
5 0
b a
pn ed ras tio n G P S c a rrie r fre
1 5 7 5 .4 2 M
1 5 7 5
qH u ez n c y In te rfe re
s ig n a
1 6 0 0
nl c e
1 6 2 5
F re q u e n c y [M H z ]
Figure 22: In-band Interference on GPS L1
The most common in-band interferences usually come from:
⚫ Harmonics, caused by crystals, high-speed signal lines, MCUs, switch-mode power supply etc., or
⚫ Intermodulation from different communication systems.
Common frequency combinations are presented in the table below. The table lists some probable in-band
interferences generated by two kinds of out-of-band signal intermodulation, or the second harmonic of
LTE Band 13.

Table 7: Intermodulation Distortion (IMD) Products
Source F1 Source F2 IM Calculation IMD Products
GSM850/Band 5 Wi-Fi 2.4 GHz F2 (2412 MHz) - F1 (837 MHz) IMD2 = 1575 MHz
Band 1 n78 F2 (3500 MHz) - F1 (1925 MHz) IMD2 = 1575 MHz
DCS1800/Band 3 PCS1900/Band 2 2 × F1 (1712.6 MHz) - F2 (1850.2 MHz) IMD3 = 1575 MHz
PCS1900/Band 2 Wi-Fi 5 GHz F2 (5280 MHz) - 2 × F1 (1852 MHz) IMD3 = 1576 MHz
LTE Band 13 - 2 × F1 (786.9 MHz) IMD2 = 1573.8 MHz
5.2.2. Out-of-band Interference
Strong signals transmitted by other communication systems can cause GNSS receiver saturation, thus
greatly deteriorating its performance, as illustrated in the following figure. In practical applications,
common strong interference signals originate from wireless communication modules, such as GSM, 3G,
LTE, 5G, Wi-Fi and Bluetooth.
Power [dBm] GPS carrier frequency
1575.42 MHz
0 GSM850 GSM900 DCS1800 PCS1900 Wi-Fi 2.4 GHz
GPS 带宽
-110
Frequency [MHz]
0 500 1000 2000 2500
Figure 23: Out-of-band Interference on GPS L1
5.2.3. Ensuring Interference Immunity
There are several things you can do to decrease the impact of interference signals and thus ensure the
interference immunity of a GNSS receiver:
⚫ Keep the GNSS antenna away from interference sources;
⚫ Add a band-pass filter in front of the GNSS module;
⚫ Use shielding and multi-layer PCB and ensure adequate grounding;
⚫ Optimize layout and component placement of the PCB and the whole device.
L76&L76-L_Hardware_Design 42 / 59

The following figure illustrates the interference source and its possible interference path. In a complex
communication system, there are usually RF power amplifiers, MCUs, crystals, etc. These devices should
be far away from a GNSS receiver, or a GNSS module. In particular, shielding should be used to prevent
strong signal interference for power amplifiers. The cellular antenna should be placed away from a GNSS
receiving antenna to ensure enough isolation. Usually, a good design should provide at least a 20 dB
isolation between two antennas. Take DCS1800 for example, the maximum transmitted power of
DCS1800 is around 30 dBm. After a 20 dB attenuation, the signal received by the GNSS antenna will be
around 10 dBm, which is still too high for a GNSS module. With a GNSS band-pass filter with around
40 dB rejection in front of the GNSS module, the out-of-band signal will be attenuated to -30 dBm.
L76&L76-L_Hardware_Design 43 / 59
Is o la tio n = 2 0 d B
C S 1 8 0 0
3 0 d B m
S h ie
R F P o w e r
C e l l u l a r
A m p lifie r
ld in g
M
C r y s
- 3 0
t a l
e je c t io n = 4
d B m
G N S S
R e c e iv e r
0 d B
Figure 24: Interference Source and Its Path

5.3. Recommended Footprint
The figure below describes module footprint. These are recommendations, not specifications.
L76&L76-L_Hardware_Design 44 / 59
0 . 9
1.1
0 . 8 0
.9
.7
.5
0 . 9 0
0 .6 5
1 0 .1 0
Figure 25: Recommended Footprint
For easy maintenance, keep a distance of at least 3 mm between the module and other components on
the PCB.

Electrical Specification
6.1. Absolute Maximum Ratings
Absolute maximum ratings for power supply and voltage on digital pins of the three modules are listed in
table below.
Table 8: Absolute Maximum Ratings
Parameter Description Min. Max. Unit
VCC Main Power Supply Voltage -0.3 4.5 V
V_BCKP Backup Supply Voltage -0.3 4.5 V
Input Voltage at I/O Pins
-0.3 3.1 V
(L76&L76-L)
V _IO
IN
Input Voltage at I/O Pins
-0.3 2.1 V
(L76-L(L))
P Input Power at RF_IN - 15 dBm
T storage Storage Temperature -40 90 °C
Stressing the device beyond the “Absolute Maximum Ratings” may cause permanent damage. The
product is not protected against over-voltage or reversed voltage. Therefore, it is necessary to use
appropriate protection diodes to keep voltage spikes within the parameters given in the table above.
L76&L76-L_Hardware_Design 45 / 59

6.2. Recommended Operating Conditions
All specifications are at an ambient temperature of +25°C. Extreme operating temperatures can
significantly impact the specified values. Applications operating near the temperature limits should be
tested to ensure the validity of the specification.
Table 9: Recommended Operating Conditions
Parameter Description Min. Typ. Max. Unit
VCC Main Power Supply Voltage 2.8 3.3 4.3 V
V_BCKP Backup Supply Voltage 1.5 3.3 4.5 V
Domain Voltage at Digital I/O Pins
- 2.8 - V
I/O_Domain
Domain Voltage at Digital I/O Pins
- 1.8 - V
Digital I/O Pin Low-Level Input Voltage
-0.3 - 0.7 V
IL
Digital I/O Pin Low-Level Input Voltage
-0.3 - 0.45 V
Digital I/O Pin High-Level Input Voltage
2.1 - 3.1 V
IH
Digital I/O Pin High-Level Input Voltage
1.35 - 2.1 V
Digital I/O Pin Low-Level Output Voltage
- - 0.42 V
OL
Digital I/O Pin Low-Level Output Voltage
- - 0.27 V
Digital I/O Pin High-Level Output
Voltage 2.4 2.8 - V
OH
Digital I/O Pin High-Level Output
Voltage 1.53 1.8 - V
Low-Level Input Voltage -0.3 - 0.7 V
Low-Level Input Voltage -0.3 - 0.45 V
VDD_RF VDD_RF Voltage - VCC - V
L76&L76-L_Hardware_Design 46 / 59

Parameter Description Min. Typ. Max. Unit
T_operating Operating Temperature -40 25 +85 °C
Operation beyond the "Operating Conditions" is not recommended and extended exposure beyond the
"Operating Conditions" may affect device reliability.
6.3. ESD Protection
Static electricity occurs naturally and it may damage the module. Therefore, applying proper ESD
countermeasures and handling methods is imperative. For example, wear anti-static gloves during the
development, production, assembly, and testing of the module; add ESD protective components to the
ESD sensitive interfaces and points in the product design.
Measures to ensure protection against ESD damage while handling the module:
⚫ When mounting the module onto a motherboard, make sure to connect the GND first, and then the
RF_IN pin.
⚫ When handling the RF_IN pin, do not come into contact with any charged capacitors or materials that
may easily generate or store charges (such as patch antenna, coaxial cable, and soldering iron).
⚫ When soldering the RF_IN pin, make sure to use an ESD safe soldering iron (tip).
L76&L76-L_Hardware_Design 47 / 59

Mechanical Dimensions
This chapter describes the mechanical dimensions of the three modules. All dimensions are in millimeters
(mm). The dimensional tolerances are ±0.20 mm, unless otherwise specified.
7.1. Top, Side and Bottom View Dimensions
L76&L76-L_Hardware_Design 48 / 59
0 9
Figure 26: Top, Side and Bottom View Dimensions
The package warpage level of the modules conforms to the JEITA ED-7306 standard.

7.2. Top and Bottom Views
L76&L76-L_Hardware_Design 49 / 59
Figure 27: Top and Bottom Views
The above images are for illustrative purposes only and may differ from the actual modules. For
authentic appearance and label, see the module received from Quectel.

Product Handling
8.1. Packaging
All the three modules are delivered as a reeled tape, which enables efficient production, set-up and
dismantling of production batches. It is shipped in a vacuum-sealed packaging to prevent moisture intake
and electrostatic discharge.
8.1.1. Tapes
The following figure shows the position of the three modules when delivered in tape and the dimensions
of the tape.
L76&L76-L_Hardware_Design 50 / 59
6P S
700860095010 211121304159867
1.0±
57.1
51.0±
3.0±
00.42
05.11
± 4.00 0.15
?1.50±0.15 ± 0.15 16.00±
0.15 2.00
10.10? à 0.15
0.30± 0.05
51.0à
?00.3
± 10.10 0.15
51.0± 51.0±
01.11 01.11
3 3 0
UQL nue ian t :ng mt
i
t h
t y
pe e r
r r
2 8 .5
1 0 0
r e e l :
e e l : 8
4 .5
5.6 04 0m p c s
O u t d ire c tio n
Figure 28: Tape and Reel Specifications

8.1.2. Reels
Each reel contains 500 Quectel GNSS modules. See the figure above.
Table 10: Reel Packaging
Model Name MOQ Minimum Package (MP): 500 pcs Minimum Package x 4 = 2000 pcs
Size: 370 mm × 350 mm × 56 mm Size: 380 mm × 250 mm × 365 mm
L76/L76-L
500 pcs N.W: 0.25 kg N.W: 1.1 kg
/L76-L(L)
G.W: 1.0 kg G.W: 4.4 kg
8.2. Storage
The module is provided in a vacuum-sealed packaging. MSL of the module is rated at 3. The storage
requirements are shown below.
1. Recommended Storage Condition: the temperature should be 23 ±5 °C and the relative humidity
should be 35–60 %.
2. Shelf life (in a vacuum-sealed packaging): 12 months in Recommended Storage Condition.
3. Floor life: 168 hours 5 in a factory where the temperature is 23 ±5 °C and relative humidity is below
60 %. After the vacuum-sealed packaging is removed, the module must be processed in reflow
soldering or other high-temperature operations within 168 hours. Otherwise, the module should be
stored in an environment where the relative humidity is less than 10 % (e.g., a dry cabinet).
4. The module should be pre-baked to avoid blistering, cracks and inner-layer separation in PCB under
the following circumstances:
⚫ The module is not stored in Recommended Storage Condition;
⚫ Violation of the third requirement above;
⚫ Vacuum-sealed packaging is broken, or the packaging has been removed for over 24 hours;
⚫ Before module repairing.
5. If needed, the pre-baking should meet the requirements below:
5 This floor life is only applicable when the environment conforms to IPC/JEDEC J-STD-033. It is recommended to start the
solder reflow process within 24 hours of removing the package if the temperature and moisture do not conform, or if it is not
certain that they conform to IPC/JEDEC J-STD-033. Do not unpack the modules in large quantities until they are ready for
soldering.
L76&L76-L_Hardware_Design 51 / 59

⚫ The module should be baked for 8 hours at 120 ±5 °C;
⚫ The module must be soldered to PCB within 24 hours after the baking, otherwise it should be put
in a dry environment such as in a dry cabinet.
1. To avoid blistering, layer separation and other soldering issues, extended exposure of the module to
the air is forbidden.
2. Take the module out of the packaging and put it on high-temperature-resistant fixtures before
baking. If shorter baking time is desired, see IPC/JEDEC J-STD-033 for the baking procedure.
3. Pay attention to ESD protection, such as wearing anti-static gloves, when touching the module.
8.3. Manufacturing and Soldering
Push the squeegee to apply solder paste on the stencil surface, thus making the paste fill the stencil
openings and then penetrate the PCB. Apply proper force on the squeegee to produce a clean stencil
surface on a single pass. For more information about the stencil thickness of the module, see document
[5] module SMT application note.
The recommended peak reflow temperature should be 235–246 ºC, with 246 ºC as the absolute
maximum reflow temperature. To avoid module damage caused by repeated heating, it is recommended
to mount the module only after reflow soldering the other side of the PCB. The recommended reflow
soldering thermal profile (lead-free reflow soldering) and related parameters are shown in the figure and
table below.
Temp. (°C)
Reflow Zone
Ramp-up slope: Cool-down slope:
0–3 °C/s C-3–0 °C/s
246
235
217
B D
200
Soak Zone
150 A
100
Ramp-to-soak slope:
0–3 °C/s
Figure 29: Recommended Reflow Soldering Thermal Profile
L76&L76-L_Hardware_Design 52 / 59

Table 11: Recommended Thermal Profile Parameters
Factor Recommendation
Soak Zone
Ramp-to-soak Slope 0–3 °C/s
Soak Time (between A and B: 150 °C and 200 °C) 70–120 s
Reflow Zone
Ramp-up Slope 0–3 °C/s
Reflow Time (D: over 217 °C) 40–70 s
Max. Temperature 235–246 °C
Cooling Down Slope -3–0 °C/s
Reflow Cycle
Max. Reflow Cycle 1
1. The above profile parameter requirements are for the measured temperature of the solder joints.
Both the hottest and coldest spots of solder joints on the PCB should meet the above requirements.
2. During manufacturing and soldering, or any other processes that may require direct contact with the
module, NEVER wipe the module shielding can with organic solvents, such as acetone, ethyl
alcohol, isopropyl alcohol, and trichloroethylene. Otherwise, the shielding can may become rusty.
3. The module shielding can is made of cupronickel base material. The Neutral Salt Spray Test has
shown that after 12 hours the laser-engraved label information on the shielding can is still clearly
identifiable and the QR code is still readable, although white rust may be found.
4. If a conformal coating is necessary for the module, DO NOT use any coating material that may
react with the PCB or shielding cover. Prevent the coating material from penetrating the module
shield.
5. Avoid using ultrasonic technology for module cleaning since it can damage crystals inside the
module.
6. Due to SMT process complexity, contact Quectel Technical Support in advance regarding any
ambiguous situation, or any process (e.g., selective soldering, ultrasonic soldering) that is not
addressed in document [5] module SMT application note.
L76&L76-L_Hardware_Design 53 / 59

Labelling Information
The label of the Quectel GNSS modules contains important product information. The location of the
product type number is shown in figure below.
L76&L76-L_Hardware_Design 54 / 59
r o
r o
d u
d u
c
ic a
t N
ic a
t N
t io
a m
t io
a m
O
O
r
g
Q
Q
t e
t e
l L
l L
Figure 30: Labelling Information
The image above is for illustrative purposes only and may differ from the actual modules. For authentic
appearance and label, see the module received from Quectel.

10
Appendix References
Table 12: Related Documents
SN Document Name
[1] Quectel_Lx0&Lx6&LC86L&LG77L_GNSS_Protocol_Specification
[2] Quectel_Lx6&Lx0&LC86L&LG77L_AGNSS_Application_Note
[3] Quectel_Lx6&LG77L_I2C_Application_Note
[4] Quectel_GNSS_Antenna_Selection&Application_Guide
[5] Quectel_Module_SMT_Application_Note
Table 13: Terms and Abbreviations
Abbreviation Description
AGNSS Assisted Global Positioning System
AIC Active Interference Cancellation
CEP Circular Error Probable
CNR or C/N Carrier-to-noise Ratio
DCE Data Communications Equipment
DCS1800 Digital Cellular System at 1800 MHz
DR Dead Reckoning
DTE Data Terminal Equipment
EASY Embedded Assist System
EGNOS European Geostationary Navigation Overlay Service
EPO Extended Prediction Orbit
L76&L76-L_Hardware_Design 55 / 59

ESD Electrostatic Discharge
GAGAN GPS Aided Geo Augmented Navigation
Galileo Galileo Satellite Navigation System (EU)
GLONASS Global Navigation Satellite System (Russian)
GNSS Global Navigation Satellite System
GPS Global Positioning System
GSM Global System for Mobile Communications
G.W Gross Weight
I/O Input/Output
I2C Inter-integrated Circuit
IC Integrated Circuit
NavIC Indian Regional Navigation Satellite System
kbps kilobits per second
LCC Leadless Chip Carrier (package)
LDO Low-dropout Regulator
LNA Low-noise Amplifier
LTE Long Term Evolution
LTO Long-term Orbit
Mbps Megabits per second
MCU Microcontroller Unit/Microprogrammed Control Unit
MEMS Micro-electro-mechanical System
MOQ Minimum Order Quantity
MP Mass Production
MSAS Multi-functional Satellite Augmentation System (Japan)
MSL Moisture Sensitivity Levels
L76&L76-L_Hardware_Design 56 / 59

N. W Net Weight
NMEA National Marine Electronics Association
OC Open Connector
PCB Printed Circuit Board
PMU Power Management Unit
ppm parts per million
1PPS One Pulse Per Second
PQ Quectel Proprietary Protocol
PSRR Power Supply Rejection Ratio
QR (code) Quick Response (Code)
QZSS Quasi-Zenith Satellite System
RAM Random Access Memory
RF Radio Frequency
RHCP Right Hand Circular Polarization
RMC Recommended Minimum Specific GNSS Data
RoHS Restriction of Hazardous Substances
ROM Read Only Memory
RTC Real-time Clock
RTK Real-time Kinematic
RTS Ready to Send/Request to Send
RXD Receive Data
3GPP 3rd Generation Partnership Project
SAW Surface Acoustic Wave
SBAS Satellite-Based Augmentation System
SMD Surface Mount Device
L76&L76-L_Hardware_Design 57 / 59

SMT Surface Mount Technology
SN Serial Number
SNR Signal-to-noise Ratio
SPI Serial Peripheral Interface
SRAM Static Random Access Memory
TCXO Temperature Compensated Crystal Oscillator
TTFF Time to First Fix
TVS Transient Voltage Suppressor
UART Universal Asynchronous Receiver/Transmitter
UTC Coordinated Universal Time
VSWR Voltage Standing Wave Ratio
WAAS Wide Area Augmentation System
XTAL External Crystal Oscillator
L76&L76-L_Hardware_Design 58 / 59