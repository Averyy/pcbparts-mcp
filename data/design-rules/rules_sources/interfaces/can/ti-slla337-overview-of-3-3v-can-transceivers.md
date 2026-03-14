---
source: "TI SLLA337 -- Overview of 3.3V CAN Transceivers"
url: "https://www.ti.com/document-viewer/lit/html/SLLA337"
format: "HTML"
method: "pdfplumber"
extracted: 2026-02-16
chars: 14164
---

Application Note
Overview of 3.3V Controller Area Network (CAN)
Transceivers
Jason Blackman and Scott Monroe
ABSTRACT
3.3V Controller Area Network (CAN) transceivers offer advantages and flexibility with respect to 5V CAN
transceivers while being compatible and interoperable with each other. Power consumption is lower with 3.3V
transceiver compared with 5V transceivers. There is potential for power supply simplification and cost savings
when the microprocessor communicating with the transceiver is also at 3.3V. This application note explains
these advantages and the devices in TI's CAN transceiver portfolio that can be used for 3.3V CAN systems.
Table of Contents
1 Theory of Operation................................................................................................................................................................2
2 Measurements Demonstrating Operation............................................................................................................................3
3 Conformance Testing.............................................................................................................................................................7
4 3.3V Device Advantages........................................................................................................................................................7
5 Summary.................................................................................................................................................................................7
6 References..............................................................................................................................................................................7
7 Revision History......................................................................................................................................................................8
List of Figures
Figure 1-1. Typical CAN Network................................................................................................................................................2
Figure 1-2. Typical CAN Bus Levels for 5V and 3.3V Transceivers.............................................................................................2
Figure 2-1. Waveforms of Two 5V SN65HVD255 Transceivers..................................................................................................3
Figure 2-2. Waveforms of Two 3.3V SN65HVD234 Transceivers...............................................................................................4
Figure 2-3. Waveform of Two SN65HVD255 Transceivers, One With a +1V Ground Shift.........................................................4
Figure 2-4. Waveform of Two 5V SN65HVD255 Transceivers With Split Termination, One With a +1V Ground Shift................5
Figure 2-5. Single Termination (left) and Split Termination (right)................................................................................................5
Figure 2-6. Waveform of a 5V SN65HVD255 and a 3.3V SN65HVD234....................................................................................6
Figure 2-7. Bus Communication of a 5V SN65HVD1050 and a 3.3V SN65HVD230..................................................................6
List of Tables
Table 4-1. Chart of Supply Current for Three Different Two-Node Buses....................................................................................7

1 Theory of Operation
The ISO 11898 specification details the physical layer requirements for CAN bus communications. CAN is a
low-level communication protocol over a twisted pair cable, similar to RS-485
Figure 1-1. Typical CAN Network
An important feature of CAN is that the bus is not actively driven during logic ‘High’ transmission, referred to as
‘recessive.’ During this time, both bus lines are typically at the same voltage, approximately VCC /2. The bus
is only driven during ‘dominant’ transmission, or during logic ‘Low.’ In Dominant, the bus lines are driven such
that (CANH – CANL) ≥ 1.5V. This allows a node transmitting a ‘High’ to detect if another node is trying to send
a ‘Low’ at the same time. This is used for non-destructive arbitration, where nodes start each message with an
address (priority code) to determine which node gets to use the bus. The node with the lowest binary address
wins arbitration and continues with its message. There is no need to back-off and retransmit like other protocols.
CAN receivers measure differential voltage on the bus to determine the bus level. Since 3.3V transceivers
generate the same differential voltage (≥1.5V) as 5V transceivers, all transceivers on the bus (regardless of
supply voltage) can decipher the message. In fact, the other transceivers cannot tell there if anything is different
about the differential voltage levels.
Figure 1-2 shows bus voltages for 5V transceivers as well as 3.3V transceivers. For 5V CAN, CANH and CANL
are weakly biased at about 2.5V (V CC /2) during recessive. The recessive common-mode voltage for 3.3V CAN
is biased higher than V CC /2, typically about 2.3V. This is done to better match the common mode point of the
5V CAN transceivers and minimize the common mode changes on the bus between 3.3V and 5V transceivers.
Since CAN was defined as a differential bus with wide common mode allowing for ground shifts (DC offsets
between nodes) this isn’t needed for operation, but minimizes emissions in a mixed network. In addition, by
using split termination to filter the common mode of the network a significant reduction in emissions is possible.
The ISO 11898-2 standard states that transceivers must operate with a common-mode range of -2V to 7V, so the
typical 0.2V common-mode shift between 3.3V and 5V transceivers doesn’t pose a problem.
5V CAN
CANH
Vdiff(D)
Vdiff(R)
CANL
Time, t
Recessive Dominant Recessive
Logic H Logic L Logic H
)V(
egatloV
suB
lacipyT
4
3
2
1
3.3V CAN
Vdiff(D)
Vdiff(R)
CANL
Time, t
Recessive Dominant Recessive
Logic H Logic L Logic H
)V(
egatloV
suB
lacipyT
4
3
2
1

Figure 1-2. Typical CAN Bus Levels for 5V and 3.3V Transceivers
2 Overview of 3.3V Controller Area Network (CAN) Transceivers SLLA337A – JANUARY 2013 – REVISED MAY 2025

Previously, 3.3V CAN transceivers were not used for automotive applications because they cannot meet strict
EMC requirements required by major automotive manufacturers. This application note references legacy 3.3V
CAN family such as SN65HVD23x, which were not approved for use in heterogeneous automotive networks.
TI's new generation of automotive 3.3V CAN transceivers, TCAN3403-Q1 and TCAN3404-Q1, overcome this
challenge and pass IEC 62228-3:2019 under both homogeneous and heterogeneous network conditions. For
more detailed information, see How Automotive-Qualified Electromagnetic-Compliant 3.3V CAN FD Transceivers
Improve ECU Performance.
2 Measurements Demonstrating Operation
Figure 2-1 shows two 5V transceivers communicating on the same bus. In this case, transceiver (XCVR) 1 and
2 are both Texas Instruments’ SN65HVD255 CAN transceiver. The signals ‘TXD1’ and ‘TXD2’ show what each
transceiver is driving onto the bus, while ‘RXD1’ and ‘RXD2’ show what each transceiver is reading from the bus.
The two upper signals are the bus lines, CANH (yellow) and CANL (light blue). The red waveform below them is
the calculated differential voltage between CANH and CANL.
Figure 2-1. Waveforms of Two 5V SN65HVD255 Transceivers
A simplified bit pattern was used to demonstrate CAN bus principles.
• Bit time 1: one transceiver transmits a dominant bit while the other remains recessive.
• Bit time 2: both transceivers are recessive.
• Bit time 3: both transmit dominant, showing what can happen during arbitration.
As shown, the differential voltage is slightly greater when both transceivers are dominant due to the output
transistors of each transceiver being in parallel, resulting in a smaller voltage drop and greater differential
voltage output.

Figure 2-2 shows the same setup but with two 3.3V transceivers (TI SN65HVD234). The differential voltage
between the bus lines during dominant bits is lower than the 5V devices that were tested, but is still meets the
requirements of the ISO 11898-2 standard. In addition, the minimum differential bus voltage for the 5V devices is
the same as with the 3.3V devices (1.5V). This means that designers have no advantage if choosing 5V devices
for their higher differential driving abilities, since it is not specified that the differential output is higher.
Figure 2-2. Waveforms of Two 3.3V SN65HVD234 Transceivers
Figure 2-3 shows how robust CAN is with common mode differences. The red Math signal shows the common
mode voltage instead of differential voltage in previous plots. The bus signals become very ugly when arbitration
between ground shifted transceivers occurs. However, the RXD1 signal shows that the transceivers don’t have a
problem because the differential signal is good and the transceiver correctly detects the signal on the bus.
Figure 2-3. Waveform of Two SN65HVD255 Transceivers, One With a +1V Ground Shift
4 Overview of 3.3V Controller Area Network (CAN) Transceivers SLLA337A – JANUARY 2013 – REVISED MAY 2025

Figure 2-4 shows the same situation as the previous figure, now with split termination instead of traditional single
termination. Split termination, shown in Figure 2-4, helps filter out high frequency noise that can occur when
there are ground potential differences between nodes. The setup for Figure 2-4 used a C of 4.7nF, which is
L
typical.
Figure 2-4. Waveform of Two 5V SN65HVD255 Transceivers With Split Termination, One With a +1V
Ground Shift
R/2
R
CANL R L /2
C
L CANL
Figure 2-5. Single Termination (left) and Split Termination (right)

Figure 2-6 shows communication with a mixed network of one 3.3V transceiver and one 5V transceiver. As
before, the digital signals TXD1, TXD2, RXD1 and RXD2 show that both transceivers are accurately talking to
each other and there is little common mode shift during the communication in contrast to the 5V homogeneous
network with a 1V ground shift.
Figure 2-6. Waveform of a 5V SN65HVD255 and a 3.3V SN65HVD234
Figure 2-7 shows a CAN frame in a mixed network of two 3.3V transceivers and one 5V transceiver to
demonstrate these principles in a CAN frame from a functional mixed system.
Figure 2-7. Bus Communication of a 5V SN65HVD1050 and a 3.3V SN65HVD230
6 Overview of 3.3V Controller Area Network (CAN) Transceivers SLLA337A – JANUARY 2013 – REVISED MAY 2025

3 Conformance Testing
The TI SN65HVD23x 3.3V CAN families have been successfully tested by the internationally recognized
third party communications and systems (C&S) group GmbH to the GIFT/ICT CAN High-Speed Transceiver
Conformance Test. This testing covers a homogeneous network of all 3.3V transceivers and a heterogeneous
network where four out of sixteen CAN nodes are the 3.3V transceiver and the remaining twelve CAN nodes
are a mix of three other “golden” reference, non TI 5V CAN transceivers. Both TI 3.3V CAN transceiver families
successfully passed this testing with no findings and the certificates of authentication were issued.
4 3.3V Device Advantages
The 3.3V transceivers tested clearly operate in mixed supply networks, which provides advantages. The first
advantage is lower power. Not only are 3.3V transceivers lower voltage, they are also lower current.
Table 4-1 shows the supply current for 3.3V devices is reduced by nearly half. Combined with the already lower
supply voltage, this results in significant power reduction.
Table 4-1. Chart of Supply Current for Three Different Two-Node Buses
Case1: 2X SN65HVD234 SN65HVD234#1 ICC(mA) SN65HVD234#1 ICC(mA)
Both recessive 7.1 7.2
#1dominant 38.4 7.2
Both dominant 25.9 26.1
Case2: 2X SN65HVD255 SN65HVD255#1ICC(mA) SN65HVD255#1 ICC(mA)
Both recessive 18.6 18.6
#1dominant 61.8 18.4
Both dominant 44.6 44.8
Case3: Mixed SN65HVD234ICC(mA) SN65HVD255ICC(mA)
Both recessive 7.2 18.6
SN65HVD234dominant 38.6 18.6
SN65HVD255dominant 7.2 61.8
Both dominant 11.7 58.9
Several other advantages emerge when used with a 3.3V microcontroller. The digital I/O of a 5V transceiver
would be level shifted either externally or in the 5V CAN transceiver to avoid damaging the microcontroller
(unless it is 5V tolerant) whereas, a 3.3V transceiver could be directly connected to this microcontroller. The
SN65HVD233/234/235 3.3V transceivers have 5V tolerant inputs so they may be used directly with a 3.3V or a
5V microcontroller. If 5V was only used in the system for CAN, a 3.3V CAN transceiver would eliminate the need
for the 5V power supply, simplifying the power domains and lowering the cost.
5 Summary
3.3V and 5V CAN transceivers are interoperable because the high-speed CAN physical layer uses differential
signaling that is the same for a 3.3V and 5V CAN transceiver. In addition, both the 3.3V and 5V CAN
transceivers have the same wide common mode range accommodating not only the typical signaling but also
providing wide margin for ground shift potential. For systems that can benefit from the advantages of 3.3V
transceivers, such as simplified power supplies and lower power consumption, they offer clear advantages in
their use either in a homogeneous 3.3V CAN network or in a mixed 3.3V and 5V CAN network.
6 References
• How Automotive-Qualified Electromagnetic-Compliant 3.3V CAN FD Transceivers Improve ECU Performance

7 Revision History
NOTE: Page numbers for previous revisions may differ from page numbers in the current version.
Changes from Revision * (January 2023) to Revision A (May 2025) Page
• Added information that the newer 3.3V transceivers are available in Section 1.................................................2
8 Overview of 3.3V Controller Area Network (CAN) Transceivers SLLA337A – JANUARY 2013 – REVISED MAY 2025