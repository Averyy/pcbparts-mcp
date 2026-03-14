---
source: "Microchip AN3580 -- Designing 1-port PoE System Using PD69201 (PSE)"
url: "https://ww1.microchip.com/downloads/aemDocuments/documents/POE/ApplicationNotes/ApplicationNotes/AN3580-Designing_1-port_PoE_System_Using_PD69201.pdf"
format: "PDF 18pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 26190
---

Designing 1-port PoE System Using PD69201

Introduction
This application note provides detailed information and circuitry design guidelines for the implementation of
a single port Power over Ethernet (PoE) system, based on Microchip’s 1-port PSE PoE manager, PD69201. This
®
enables the designer to integrate PoE capabilities, as defined by the IEEE 802.3af/at standard into an Ethernet
switch or a router.
A PD69201 based design is intended for low-cost applications where PoE implementation is required but there
is no need for sophisticated features such as power management.
For ease of design and development of an Ethernet switch using PD69201, order evaluation board PD-IM-7601.
The document describes both the managed and the unmanaged configuration for a 1-port system. In the
managed configuration, PD69201 is controlled by a HOST processor through an I2C bus. In the unmanaged
configuration, PD69201 operates as a standalone system without any communication to the host.
PD69201 executes all the real-time functions as specified in the IEEE 802.3af and IEEE 802.3at standards,
including load detection and “AF” and “AT” classification using Multiple Classification Attempts (MCA). PD69201
also supports legacy or pre-standard detection. PD69201 supports the DC disconnection method, as specified
in the IEEE 802.3at standard. PD69201 provides PD real-time protection through the following mechanisms:
overload, under load, over voltage, over temperature, and short-circuit.
Features
• Designed to support IEEE 802.3af and IEEE 802.3at including two event classification
• Supports pre-standard PD detection
• Single DC voltage input: 32V–57V
• Wide temperature range: –40 °C to 85 °C
• Low thermal dissipation (internal 100 mΩ sense resistor)
• Includes I2C communication
• Continuous port and system data monitoring (port current is not measured)
• Power soft-start algorithm
• On-chip thermal protection
• Voltage and temperature monitoring and protection
• Internal Power On Reset (POR)
• MSL1 and RoHS compliant
Application Note DS00003580E - 1
© 2025 Microchip Technology Inc. and its subsidiaries

Table of Contents
Introduction...........................................................................................................................................................................1
Features..........................................................................................................................................................................1
1. Overview.........................................................................................................................................................................3
2. Circuit Description.........................................................................................................................................................4
2.1. Main Supply........................................................................................................................................................4
2.2. Grounds..............................................................................................................................................................4
2.3. 5V Regulator.......................................................................................................................................................4
2.4. Control.................................................................................................................................................................4
2.5. Indicators............................................................................................................................................................4
2.6. Reference Current Source.................................................................................................................................4
2.7. Communication Interface.................................................................................................................................5
2.8. Surge Requirements..........................................................................................................................................6
2.9. Unmanaged Mode.............................................................................................................................................7
2.10. Managed Mode..................................................................................................................................................8
3. Bill of Material for Unmanaged Applications.............................................................................................................9
4. Bill of Material for Managed Applications................................................................................................................11
5. Layout Design Guidelines...........................................................................................................................................13
5.1. Isolation.............................................................................................................................................................13
5.2. Component Placement...................................................................................................................................14
5.3. Port Outputs.....................................................................................................................................................14
6. Reference Documents................................................................................................................................................16
7. Revision History...........................................................................................................................................................17
Microchip Information.......................................................................................................................................................18
Trademarks..................................................................................................................................................................18
Legal Notice..................................................................................................................................................................18
Microchip Devices Code Protection Feature............................................................................................................18
Application Note DS00003580E - 2

Overview
1. Overview
The main mode of operation of the system is a 2-pair PoE port, based on one PD69201 PoE
manager.
Figure 1-1. 2-Pair Mode
Application Note DS00003580E - 3

Circuit Description
2. Circuit Description
The 1-port, 2-pair configuration shown in Figure 1-1 comprises one PoE manager circuit (PD69201),
acting as alternative-A feeding power over the data lines.
2.1 Main Supply
The PoE system operates within a range of 44 VDC to 57 VDC with no need for additional power
supply sources.
This power must be isolated from the switch supply and chassis by 1500 Vrms.
2.2 Grounds
The system utilizes chassis and analog grounds.
The chassis ground is connected to the chassis ground of the switch. This ground plane must be
1500 Vrms isolated from the PoE circuitry.
2.3 5V Regulator
PD69201 includes an internal 5 VDC regulator (DRV_VAUX5) that provides up to 10 mA current. This
current is utilized for powering PD69201 and up to 3 mA is available for the components external to
the PoE domain. Those components must also be isolated by 1500 Vrms from the switch circuitry.
If more than 3 mA is required, then the 5 VDC regulator can be boosted by an external transistor,
which enables powering the peripheral circuitry up to 20 mA.
2.4 Control
An active low signal is utilized to disable the port. PD69201 is still active and able to communicate
with the host.
2.5 Indicators
PD69201 produces a direct LED indication that is utilized to indicate PoE events.
2.6 Reference Current Source
Reference for internal voltages within PD69201 is set by a 240 kΩ 1% resistor to AGND.
Application Note DS00003580E - 4

2.7 Communication Interface
The Host CPU issues commands utilizing I2C Communication Protocol to PD69201 through an
isolation component U3 (refer to Figure 2-2).
PD69201 transmits the port and system data.
• Data stream is transmitted through Mode/SDA (pin 4)
• Clock stream is transmitted through Power_set/SCL (pin 5)
Setting: Reading:
• Port on/off • Port voltage
• Modes: • Resistor detection result
– Alt A/B • Classification result
– Current set (Ilim) • Port state machine status
– Legacy detection • Device version
• Timing:
– Tcut
– Tlim
– UDL (TMPS)
Application Note DS00003580E - 5

2.8 Surge Requirements
Surge requirements are system requirements and must be tested on a system level. This application
note assists the designer to implement primary protection mechanisms from outdoor surge events
usually located between Equipment Under Test (EUT) and external cable.
This application note also contains recommendations for the system containing PD69201 to meet
PoE surge requirements of the standards and levels, as listed in the following table.
Table 2-1. Surge Standards
# Standard Test Circuit Waveform Level [±] Tested Channel Coupling Comments
Condition Mode
1 ITU-T K21 2018 1.2/50 μs–8/20 μs 6 kV Channel OFF Differential With additional
Test 2.1.11 R1 = 10Ω external
components
R2 = 10Ω
2 ITU-T K21 2018 1.2 μs/50 μs–8 μs/20 μs 6 kV Channel OFF Common With additional
Test 2.1.8 R = 10Ω external
3 ITU-T K21 2018 10 μs/700 μs 6 kV Channel OFF Common With additional
Test 2.1.4a R = 25Ω and ON external
4 IEC61000-4-5 :2014 1.2 μs/50 μs 1 kV Channel OFF Common —
R = 40Ω (4x160Ω) and ON
5 EN55024:2010 10 μs/700 μs 1 kV Channel OFF Common —
R = 40Ω (4x160Ω) and ON
Application Note DS00003580E - 6

2.9 Unmanaged Mode
In the unmanaged application, as shown in Figure 2-1, Mode and Power are set by the Mode (pin 4)
and Power_set (pin 5) by connecting the external resistor to the GND.
In this application, PD69201 is configured to work in the following mode:
• Resistor on Mode (pin 4) is 34.8 kΩ
– Function:
• Alt A (PoE on data pair)
• Detection resistor only
• Startup Ilim check
• Resistor on Power_set pin is 200 kΩ
– Function:
• AT 30W
• Perform classification
For different configuration options, see the PD69201 Data Sheet, DS00003454.
Figure 2-1. PD69201 Unmanaged Application Circuitry
5 4 3 2 1
Vmain
D D
VPORT_POS
GND_Analog R 68 1 .1K PD-0805
VPORT_NEG
Note 1
C Note 1 C
Note 1: Optional components for 6kV surge
C8
VAUX5 100n
pd-0805-w
100v
B X7R B
D4 Green
SSL-LX3044GC LED-EVERLIGHT-204
VAUX5
A A
Application Note DS00003580E - 7
2
1
C2 100n100v RV1
X7R PD-0805 C7 1n 2000V
X7R
C1 1n 2000V
C4 1n 2000V
R2
24.9K
PD-1206-W
U1
1 Iref PORT_NEG 10
2 ATB_N/Disable Vmain 9
3 ATB_P LED 8
4 MODE/SDA DRV_Vaux5 7
5 Power_set/SCL Vaux5 6
R4 R6 R7
240K 34.8K 200K
PD-0402 PD-0402 PD-0402 PD69201ILD-TR.
PD-DFN-10-4X3-1
11
DNG
C3 47u + 100v D2
ALU STPS1H100A PD-SMA
2 TRS1 P0640SCLRP PD-SMB-1
1 2 2
D1 1SMA58AT3 C6
100n PD-SMA X7 1 R 00V PD-SMA-W PD-1206
R5 C9 50V C1025V
10M PD-0805 4.7uF
PD-0402 X7R X7R
100n PD-1206
D3
STPS1H100A
PD-SMA
vmain
C5 R8 1n 2000V 7.15M X7R
Vport_Neg_out
R3 4.75K PD-0402

2.10 Managed Mode
In the managed application, as shown in Figure 2-2, Disable_Port (pin 2) is driven by the HOST CPU
to disable the PoE port. When PD69201 detects low level voltage at pin 2, it immediately disables the
port.
When driving this line by the HOST CPU, use an opto-coupler to isolate it by 1500 VDC from the
switch domain and use a 4.75 kΩ pull-up resistor to 5V.
In the unmanaged application, connect Disable_Port (pin 2) with a 4.75 kΩ pull-up resistor to 5V.
Figure 2-2. PD69201 Managed Application Circuitry
D Input voltage 44-57V Vmain D
VPORT_POS
GND_Analog
VPORT_NEG
Note 1
C C
VAUX5 Note 1
Note 1: Optional components for 6kV surge C8 To HOST
100n
pd-0805-w
100v X7R D4
Host side PoE side Green B B 5V VAUX5
C10
0.1uF 10V
X7R PD-0805 VAUX5
To HOST To HOST
A A
Application Note DS00003580E - 8
RV1 C6
100n 100V X7R PD-1206
R5
3.32K PD-0402
2 TRS1 P0640SCLRP PD-SMB-1
1 2 2
C2 100n100v
X7R C4 PD-0805 1n 2000V
D3
STPS1H100A
PD-SMA
R9 61.9 PD-0805
1 6
2 5
U1 MOC217 R2 PD-SO8
7
3 8
4
Q1
1 MJD47 PD-DPAK
3
2 1 0 C n 0 1 0V C 4 + 7 3 u 100v
ALU R1 68.1K PD-0805 C7 1n 2000V
X7R
R2
4.75K
PD-0402
R3
24.9K PD-1206 U2
1 Iref PORT_NEG 10 2 ATB_N/Disable Vmain 9
3 ATB_P LED 8
R6 4 MODE/SDA DRV_Vaux5 7
PD-0 2 40 4 2 0K 5 Power_set/SCL Vaux5 6
PD69201ILD-TR. PD-DFN-10-4X3-1
11
DNG
D2
STPS1H100A PD-SMA
C13
4.7uF X7R
PD-1206
C1150V 100n X7R PD-0805
C5 D1 R8 1n 2000V 1SMA58AT3 7.15M X7R
PD-SMA PD-SMA-W
R4 R7
3.32K 10M PD-0402 PD-0402
U3
1 2 3 4 V S S G D D C N D A L D 1 1 1 1 G V S S D N D C D D A L 2 2 2 2 5 6 7 8
ADUM1251
PD-SO8
vmain
Disable
Vport_Neg_out Disable
C9 I2C_SDA 0.1uF
10V I2C_SCL X7R
PD-0805
C1225V S S D C A L_ _ I I S S O O I I 2 2 C C _ _ S S D C A L X 4 7 .7 R uF PD-1206

Bill of Material for Unmanaged Applications
3. Bill of Material for Unmanaged Applications
The following table lists the bill of material for the unmanaged application.
Table 3-1. Bill of Material for Unmanaged Application
Line Qty Reference Description Manufacturer Manufacturer’s P/N
1 4 C1, C4, C5, C7 CAP CRM 1 nF/2000V 10% X7R AVX 1206GC102KAT1A
1206 SMT
Kemet C1206C102KGRAC
Meritek HC1206XR102K202
2 2 C2, C8 Capacitor, X7R, 100 nF 100V 10% AVX 08051C104KAT2A
0805
Murata GRM21BR72A104KAC4L
Vishay VJ0805Y104KXBTM
3 1 C6 CAP CRM 100 nF 100V 10% X7R AVX 12061C104KAT2A
Kemet C1206C104K1RACTU
Murata GRM319R72A104KA01D
4 1 C9 Capacitor, X7R, 100 nF, 50V, 10% AVX 08055C104KAT4A
0805
Kemet C0805X104K5RACTU
Vishay VJ0805Y104KXAMR
5 1 C3 CAP ALU 47 uF 100V 20% 10X16 Nichicon UPW2A470MPD
SUNCON 100ME47AX
6 1 C10 CAP CRM X7R 4.7 uF 25V 10% AVX 12063C475KAT2A
Kemet C1206C475K3RACTU
Murata GRM31CR71E475KA88L
7 1 D1 DIO TVS 58V 40A SRG 400 WPK Diodes Inc. SMAJ58A-13-F
SMA SMT
ON Semi 1SMA58AT3G
STMicro SMAJ58A
8 2 D2, D3 DIO SCHOTTKY 100V 1A SMA ON Semi MBRA1H100T3G
STMicro STPS1H100A
9 1 D4 LED 3 mm Green TH Lumex SSL-LX3044GC
10 1 R1 RES 68.1K 125 mW 1% 0805 SMT Samsung RC2012F6812CS
Yageo RC-0805FR-07 68K1L
11 1 R2 RES 4.75K 62.5 mW 1% 0402 SMT Vishay CRCW04024K75FKED
Yageo RC0402FR-074K75L
12 1 R3 RES 24.9K 250 mW 1% 1206 SMT Vishay CRCW120624K9FKEA
Yageo RC1206FR-0724K9L
13 1 R7 RES 200K 62.5 mW 1% 0402 SMT Vishay CRCW0402200KFKED
Yageo RC0402FR-07200KL
14 1 R6 RES 0R 62.5 mW 5% 0402 SMT Samsung RC1005J000CS
Vishay CRCW04020000Z0ED
15 1 R4 RES 240K 62.5 mW 1% 0402 SMT Vishay CRCW0402240KFKED
Yageo RC0402FR-07240KL
16 1 R5 RES 10M 62.5 mW 1% 0402 SMT Vishay CRCW040210M0FKED
Yageo RC0402FR-0710ML
17 1 R8 RES 7.15M 125 mW 1% 1206 SMT Vishay CRCW12067M15FKEA
Yageo RC1206FR-077M15L
18 1 RV1 VARISTOR 680 Vrms 5 KA 14 MM Epcos/TDK B72214S2421K101
ON Semi NP0640SCT3G
Application Note DS00003580E - 9

Bill of Material for Unmanaged Applications
Table 3-1. Bill of Material for Unmanaged Application (continued)
19 1 TRS1 SIDACtor 58V SMB Litlefuse P0640SCLRP
20 1 U2 PoE PSE IC Microchip PD69201ILQ-TR
Notes:
• RV1, TRS1, D2, D3, and R8 are optional components for 6 kV surge test requirements.
• These components can be removed if the system requires to pass up to 1 kV surge.
• Capacitors C5 and C7 are optional components to improve EMI.
Application Note DS00003580E - 10

Bill of Material for Managed Applications
4. Bill of Material for Managed Applications
The following table lists the bill of material for the managed application.
Table 4-1. Bill of Material for Managed Application
1 4 C1,C4,C5,C7 CAP CRM 1nF/2000V 10% AVX 1206GC102KAT1A
X7R 1206 SMT
Kemet C1206C102KGRAC
Meritek HC1206XR102K202
2 2 C2,C8 Capacitor, X7R, 100nF 100V AVX 08051C104KAT2A
10% 0805
Murata GRM21BR72A104KAC4L
Vishay VJ0805Y104KXBTM
3 1 C6 CAP CRM 100nF 100V 10% AVX 12061C104KAT2A
X7R 1206 SMT
Kemet C1206C104K1RACTU
Murata GRM319R72A104KA01D
4 1 C11 Capacitor, X7R, 100nF, 50V, AVX 08055C104KAT4A
10% 0805
Kemet C0805X104K5RACTU
Vishay VJ0805Y104KXAMR
5 1 C3 CAP ALU 47uF 100V 20% Nichicon UPW2A470MPD
10X16
SUNCON 100ME47AX
6 2 C9,C10 CAP CRM 100n 10V 10% X7R AVX 0805ZC104KAT2A
0805 SMT
Kemet C0805C104K8RACTU
Vishay VJ0805Y104KXQCW1BC
7 1 C12 CAP CRM X7R 4.7uF 25V AVX 12063C475KAT2A
10% 1206 SMT
Kemet C1206C475K3RACTU
Murata GRM31CR71E475KA88L
8 1 D1 DIO TVS 58V 40A SRG Diodes Inc. SMAJ58A-13-F
400WPK SMA SMT
ON Semi 1SMA58AT3G
STMicro SMAJ58A
9 2 D2,D3 DIO SCHOTTKY 100V 1A ON Semi MBRA1H100T3G
SMA
STMicro STPS1H100A
10 1 D4 LED 3mm Green TH Lumex SSL-LX3044GC
11 1 Q1 TRN NPN 250V 1A 15W D- Fairchild MJD47TF
Pak SMT
ON Semi MJD47T4G
STMicro MJD47T4
12 1 R1 RES 68.1K 125mW 1% 0805 Samsung RC2012F6812CS
SMT
Yageo RC-0805FR-07 68K1L
13 1 R2 RES 4.75K 62.5mW 1% 0402 Vishay CRCW04024K75FKED
Yageo RC0402FR-074K75L
14 1 R3 RES 24.9K 250mW 1% 1206 Vishay CRCW120624K9FKEA
Yageo RC1206FR-0724K9L
15 2 R4,R5 RES 3.32K 62.5mW 1% 0402 Samsung RC1005F3321CS
Yageo RC0402FR-073K32L
16 1 R6 RES 240K 62.5mW 1% 0402 Vishay CRCW0402240KFKED
Yageo RC0402FR-07240KL
17 1 R7 RES 10M 62.5mW 1% 0402 Vishay CRCW040210M0FKED
Yageo RC0402FR-0710ML
Application Note DS00003580E - 11

Bill of Material for Managed Applications
Table 4-1. Bill of Material for Managed Application (continued)
18 1 R8 RES 7.15M 125mW 1% 1206 Vishay CRCW12067M15FKEA
Yageo RC1206FR-077M15L
19 R9 RES 61.9R 125mW 1% 0805 Vishay CRCW080561R9FKEA
Yageo RC0805FR-0761R9L
20 1 RV1 VARISTOR 680Vrms 5KA Epcos/TDK B72214S2421K101
14MM
21 1 TRS1 SIDACtor 58V SMB Litlefuse P0640SCLRP
ON Semi NP0640SCT3G
22 1 U1 IC OPTOISOLATOR Fairchild MOC217R2-M
23 1 U2 PoE PSE IC Microsemi PD69201ILQ-TR
24 1 U3 IC Hot-Swap I2C Isolator Analog Devices ADUM1251ARZ-RL7
2Ch SO-8
Notes:
• RV1, TRS1, D2, D3, and R8 are optional components for 6 kV surge test requirements.
• These components can be removed, if the system requires to pass up to 1 kV surge.
• Capacitors C5 and C7 are optional components to improve EMI.
Application Note DS00003580E - 12

Layout Design Guidelines
5. Layout Design Guidelines
To properly integrate the PD69201 PoE manager into a new circuit or adapt an existing one, it is
essential to follow the presented guidelines. The information sets out limitations and restrictions
imposed by isolation demands of the circuit, as well as circuit:
• Isolation
• Component Placement
• Port Outputs
5.1 Isolation
As specified in the IEEE PoE standards, 1500 V rms isolation is required between the switch’s main
AC
board circuitry, including protective and frame ground, and the Media Dependent Interface (MDI).
To comply with the isolation requirements, the PoE managers must be isolated in regards to all
other switch circuitries.
One of the following methods is used:
• A separate DC input for the switch and the PoE circuitry and isolated serial communication
between the PoE circuitry and the switch circuitry. Refer to the following figure for more
information.
Figure 5-1. Switch Circuitry with a Single DC Source
• A single DC input (separate power supplies) for both the switch and PoE circuit. Additional
or integrated isolated DC-DC circuitry for the switch input and isolated serial communication
port between the PoE circuitry and the switch circuitry. Refer to the following figure for more
information.
Application Note DS00003580E - 13

Figure 5-2. Switch Circuitry with Two DC Sources
To maintain 1500 Vrms isolation between two adjacent layers of FR–4 multi–layer PCB, a minimum
of 15 mils isolation thickness is recommended to provide a safe margin for hi–pot requirements.
5.2 Component Placement
• To prevent heat transfer among various components, leave an open gap in the ground plane if
possible to isolate the heat transfer.
• Locate the bypass capacitors for the PoE manager operating voltage close to the relevant pin (Pin
9). In cases where two bypass capacitors are placed on the same line:
– Locate the lower value capacitor closest to the pin on the same layer.
– The higher value capacitor can be located at a more distant location.
• Place 4.7 μF and 0.1 μF bypass capacitors from VAUX5 to GND as close as possible to the
respective pin. Its conductors to VAUX5 and GND should be as short as possible.
• Connect the IREF resistor (connects to pin 1), used for current reference, directly to GND (E-pad)
pin and keep the trace as short as practically possible.
• Connect resistors for Mode (pin 4) and Power_Set (pin 5) directly to GND (E-pad) pin with a trace
(in Unmanaged mode).
• Connect optoisolators ground pins directly to GND pin (E-pad) with a trace to minimize noise and
ground loop potentials (in Managed mode).
• If possible, locate the protection 58V TVS (D1) and the 47uF bulk capacitor (C3) close to the PoE
manager
• For surge protection application, locate the varistor (RV1) close to the RJ45/magnetic, away from
the PoE manger.
5.3 Port Outputs
For robust design, the port output traces are to be 45-mil wide so as to handle maximum current
and port power. However, to obtain maximum 10 °C copper rise, minimum width for traces is set in
accordance with the layer location and copper thickness:
• For 2-ounce copper, external layer: 15 mils
• For 2-ounce copper, internal layer: 20 mils
• For 1-ounce copper, external layer: 25 mils
• For 1-ounce copper, internal layer: 30 mils
• For 1/2-ounce copper, external layer: 30 mils
• For 1/2-ounce copper, internal layer: 55 mils (20 °C copper rise)
Application Note DS00003580E - 14

The port output traces must be short and parallel to each other, to reduce RFI coupling and to keep
the series resistance low.
Application Note DS00003580E - 15

Reference Documents
6. Reference Documents
For access to documents, device datasheets, or application notes, consult your local Microchip Client
Engagement Manager or visit our website at www.microchip.com/poe.
• IEEE 802.3af-2003 standard, DTE Power via MDI
• IEEE802.3at-2009 standard, DTE Power via MDI
• PD69201 Data Sheet, Document Number DS00003454
Application Note DS00003580E - 16

Revision History
7. Revision History
Revision Date Description
E 02/2025 • Updated information for 3. Bill of Material for Unmanaged Applications and
4. Bill of Material for Managed Applications.
• Updated Figure 2-1 and Figure 2-2.
D 4/2021 Following is the summary of changes:
• Added the Layout Design Guidelines section.
C November 2020 Following is the summary of changes:
• Updated 5V Regulator.
• Updated Figure 2-2.
• Changed Table 4-1.
B October 2020 Following is the summary of changes:
• Updated Figure 2-1.
• Updated Figure 2-2.
• Changed Table 3-1.
• Changed Table 4-1.
• Updated document ID of the PD69201 datasheet to DS00003454 in the
Unmanaged Mode and the Reference Documents sections.
• Added the Surge Requirements section.
A August 2020 Initial revision
Application Note DS00003580E - 17

Microchip Information
Trademarks
The “Microchip” name and logo, the “M” logo, and other names, logos, and brands are registered
and unregistered trademarks of Microchip Technology Incorporated or its affiliates and/or
subsidiaries in the United States and/or other countries (“Microchip Trademarks”). Information
regarding Microchip Trademarks can be found at https://www.microchip.com/en-us/about/legal-
information/microchip-trademarks.
ISBN: 979-8-3371-0493-5
Legal Notice
This publication and the information herein may be used only with Microchip products, including
to design, test, and integrate Microchip products with your application. Use of this information
in any other manner violates these terms. Information regarding device applications is provided
only for your convenience and may be superseded by updates. It is your responsibility to ensure
that your application meets with your specifications. Contact your local Microchip sales office for
additional support or, obtain additional support at www.microchip.com/en-us/support/design-help/
client-support-services.
THIS INFORMATION IS PROVIDED BY MICROCHIP “AS IS”. MICROCHIP MAKES NO REPRESENTATIONS
OR WARRANTIES OF ANY KIND WHETHER EXPRESS OR IMPLIED, WRITTEN OR ORAL, STATUTORY
OR OTHERWISE, RELATED TO THE INFORMATION INCLUDING BUT NOT LIMITED TO ANY IMPLIED
WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR
PURPOSE, OR WARRANTIES RELATED TO ITS CONDITION, QUALITY, OR PERFORMANCE.
IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE, INCIDENTAL, OR
CONSEQUENTIAL LOSS, DAMAGE, COST, OR EXPENSE OF ANY KIND WHATSOEVER RELATED TO THE
INFORMATION OR ITS USE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS BEEN ADVISED OF THE
POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE FULLEST EXTENT ALLOWED BY LAW,
MICROCHIP’S TOTAL LIABILITY ON ALL CLAIMS IN ANY WAY RELATED TO THE INFORMATION OR
ITS USE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY, THAT YOU HAVE PAID DIRECTLY TO
MICROCHIP FOR THE INFORMATION.
Use of Microchip devices in life support and/or safety applications is entirely at the buyer’s risk,
and the buyer agrees to defend, indemnify and hold harmless Microchip from any and all damages,
claims, suits, or expenses resulting from such use. No licenses are conveyed, implicitly or otherwise,
under any Microchip intellectual property rights unless otherwise stated.
Microchip Devices Code Protection Feature
Note the following details of the code protection feature on Microchip products:
• Microchip products meet the specifications contained in their particular Microchip Data Sheet.
• Microchip believes that its family of products is secure when used in the intended manner, within
operating specifications, and under normal conditions.
• Microchip values and aggressively protects its intellectual property rights. Attempts to breach the
code protection features of Microchip products are strictly prohibited and may violate the Digital
Millennium Copyright Act.
• Neither Microchip nor any other semiconductor manufacturer can guarantee the security of its
code. Code protection does not mean that we are guaranteeing the product is “unbreakable”.
Code protection is constantly evolving. Microchip is committed to continuously improving the
code protection features of our products.
Application Note DS00003580E - 18