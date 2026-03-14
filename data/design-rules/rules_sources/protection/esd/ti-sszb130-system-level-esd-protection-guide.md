---
source: "TI SSZB130 -- System-Level ESD Protection Guide"
url: "https://www.ti.com/lit/pdf/sszb130"
format: "PDF 25pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 30803
---

Application Note
System-Level ESD Protection Guide
ABSTRACT
Electrostatic discharge (ESD) poses a risk to many electronic devices and can cause unexpected and
catastrophic damage. While many ICs have device level ESD protection, ICs are still at risk of damage from
system-level ESD events. To provide adequate system-level ESD protection, ESD and surge devices are used
to guard against these higher power transient events. This guide discusses diode selection and parameters,
explains the importance of system-level ESD protection, and provides device recommendations for a number of
applications.
To learn more about ESD protection and TI’s ESD devices, visit ti.com.
Table of Contents
1 Overview of System Level ESD Protection..............................................................2
1.1 What is ESD Protection?...........................................................................2
1.2 Why External ESD?..............................................................................3
2 Definitions of ESD Device Specifications................................................................5
2.1 Working Voltage (V )...........................................................................5
RWM
2.2 Polarity.........................................................................................5
2.3 Channels.......................................................................................5
2.4 IEC 61000-4-2 Rating.............................................................................5
2.5 Capacitance.....................................................................................5
2.6 Clamping Voltage at 16A TLP.......................................................................5
3 ESD Devices by Application..........................................................................6
3.1 Antenna Circuit Protection..........................................................................6
3.2 Audio Circuit Protection............................................................................7
3.3 CAN Circuit Protection.............................................................................8
3.4 DisplayPort Circuit Protection.......................................................................9
3.5 Ethernet Circuit Protection.........................................................................10
3.6 FPD-Link Protection.............................................................................1
3.7 HDMI Circuit Protection...........................................................................12
3.8 Keypad and Pushbutton Circuit Protection............................................................13
3.9 LIN Circuit Protection.............................................................................14
3.10 LVDS Circuit Protection..........................................................................15
3.11 MHL Circuit Protection...........................................................................16
3.12 PCIe Circuit Protection...........................................................................17
3.13 RS-485 Protection..............................................................................18
3.14 SD- and SIM-Card Circuit Protection................................................................19
3.15 USB 2.0 Circuit Protection........................................................................20
3.16 USB 3.1 Circuit Protection........................................................................21
3.17 USB Type C Circuit Protection....................................................................2
3.18 4-20mA Protection..............................................................................24
Trademarks
USB Type C™ is a trademark of USB Implementers Forum.

1 Overview of System Level ESD Protection
1.1 What is ESD Protection?
IC
Interface
Connector
GND
Figure 1-1. ESD Strike Without Protection
Interface
GND GND
Figure 1-2. ESD Strike With Protection
Electrostatic discharge (ESD) is the sudden release of electricity from one charged object to another when the
two objects come into contact. While we’ve all experienced ESD when we’ve been shocked by a metal doorknob
or car door, most ESD strikes are quite harmless to humans. However, for sensitive integrated circuits (ICs), the
high peak voltage and current of these ESD strikes can cause catastrophic failures.
If ESD protection is not present in a system, the high voltage of an ESD strike through an interface connection
causes a large current spike to flow directly into the IC, causing damage. To protect sensitive circuitry from
electrical overstress failures, ESD protection diodes are connected to each signal line between the interface
connector and the IC.
In the event of an ESD strike, the ESD diode breaks down and creates a low impedance path that limits the peak
voltage and current by diverting the current flow to ground, thereby protecting the IC.
Figure 1-3 compares the peak voltage of a typical ESD strike without protection to the same ESD strike on a
signal line with ESD diode protection.
Figure 1-3. Voltage Waveforms With and Without ESD Protection

1.2 Why External ESD?
Many semiconductor devices based off advanced processes only offer device-level ESD specifications such as
the charge device model (CDM) and the human body model (HBM) shown in Figure 1-4. Device-level ESD
specifications are not sufficient to protect devices in a system. The energy associated with a system-level ESD
strike is much higher than a device-level ESD strike. This means a more robust design is required to protect
against this excess energy.
Figure 1-4. IEC vs. CDM vs. HBM
The silicon area required to implement system-level ESD protection is much larger than what is required for
device-level HBM and CDM. This difference in silicon area translates to additional cost. As technology gets
smaller, technology becomes increasingly difficult and more costly to integrate sufficient system-level protection
with microcontroller or core chipsets.
Left:Silicondieareasforsystem-
level ESD (8-kV IEC).
Pad Right:Silicondieareasfordevice-
level ESD (2-kV HBM).
Figure 1-5. Silicon Die Area Comparison
System-level ESD protection can be added with discrete components. However, in many applications, discrete
designs consume board space, complicate layout, and compromise signal integrity at high data rates. Stand-
alone ESD devices from Texas Instruments (TI) provide space-saving designs to protect system ICs from
external ESD strikes while maintaining signal integrity.
ESD protection is often considered at the last phase of system design. Designers require flexibility to select an
ESD device that does not compromise the PCB layout or consume additional board space. TI’s ESD designs
with pass-through packaging as shown in Figure 1-6 allow designers to add ESD components in the final stages
of a design with minimal change in board layout.

VIA to GND Plane
2 + 2 - 1 + 1 - 0 + 0 - k + k -
DD DD DD ClCl
G N I/O G N I/O G N I/O G N I/O
D D D D
DD DD DD DD
OO NN OO NN OO NN OO NN
II// GG II// GG II// GG II// GG
Figure 1-6. Example of Pass-Through Routing

2 Definitions of ESD Device Specifications
2.1 Working Voltage (V )
RWM
The working voltage is the recommended operating voltage of the ESD device. The signal voltage of the
interface must not exceed the working voltage of the ESD device in either the negative or positive direction to
prevent unwanted clamping and leakage. To learn more, click here.
2.2 Polarity
An ESD diode is bidirectional or unidirectional. A bidirectional diode has a breakdown voltage range from +V
rwm
to -V , which allows the diode to support signals with negative ranges such as analog audio. A unidirectional
diode has a breakdown range from 0V to +V , which helps protect downstream devices that cannot tolerate a
negative voltage. To learn more, click here.
2.3 Channels
ESD devices can come in a variety of channels and configurations. Depending on the interface, multichannel
devices can offer board space savings over single-channel devices. In other applications, single-channel devices
can offer more design flexibility than multichannel designs.
2.4 IEC 61000-4-2 Rating
A system-level ESD standard that shows the robustness of the ESD device. The IEC 61000-4-2 rating consists
of two measurements. First, the contact rating shows the maximum voltage a device can withstand when the
source of ESD is discharged directly onto the device. Second, the airgap rating shows the maximum voltage a
device can withstand when the source of ESD is discharged over a gap of air onto the device. The higher the
IEC 61000-4-2 rating, the higher a voltage the ESD device can withstand. To learn more, click here.
2.5 Capacitance
Since the ESD diodes are connected in parallel to the signal trace, the diodes add some parasitic capacitance to
the system. The capacitance of the ESD device becomes especially important in high-speed interfaces because
capacitance must be minimized to maintain signal integrity. To learn more, click here.
2.6 Clamping Voltage at 16A TLP
When an ESD strike occurs, the ESD diode clamps the voltage so that the downstream circuitry is not exposed
to a voltage greater than the clamping voltage. Therefore, clamping voltage is a measurement of how well the
diode can protect downstream circuitry. The clamping voltage of a device exposed to an 8kV IEC ESD strike is
best approximated with a transmission line pulse (TLP) at 16A. Clamping voltage is a function of the dynamic
resistance of the device during an ESD strike. To learn more, click here.

3 ESD Devices by Application
3.1 Antenna Circuit Protection
Filtering Network Power Amplifier WiFi Transceiver
Figure 3-1. Antenna Application Diagram
Description
In wireless applications such as GPS, WLAN, Wi-Fi®, and so on., the antenna can act as a low-impedance path
for ESD strikes to enter the system and damage downstream circuitry such as the filtering network, amplifier
or transceiver. Signal frequencies in these applications can reach upwards of 15GHz which means that any
capacitance on signal paths must be minimized to avoid signal degradation.
Design
The ESD devices listed in Table 3-1 provide IEC 61000-4-2 ESD protection with ultra-low capacitance to
maintain signal integrity. These designs are available in a variety of small flow-through footprint options,
including 0201 (0.6 × 0.3mm) and 0402 (1.0 × 0.6mm). These devices also come in a wide range of working
voltages to support a variety of antenna applications.
Table 3-1. ESD Designs for Antenna Applications (Click here for more products on Ti.com)
IEC 61000-4-1-2
Working Package Size
Device ESD Rating (kV) Capacitance (pF) Channels Package
Voltage (V) (mm)
(Contact)
0.6 × 0.3 DFN0603
TPD1E0B04 ±3.6 8 0.13 1
1.0 × 0.6 DFN1006
TPD1E01B04-Q1 ±3.6 15 0.2 1
ESD601-Q1 ±18 15 0.3 1 1.0 × 0.6 DFN1006
ESD701-Q1 ±24 15 0.3 1 1.0 × 0.6 DFN1006

3.2 Audio Circuit Protection
L Audio IN
Audio Amplifier L
Speaker Input
R Audio IN
Audio Amplifier R
Figure 3-2. Audio Application Diagram
Audio jacks and connectors can present an entry point for ESD to enter the system. Analog audio signals do not
typically exceed ±5V before amplification but can reach higher voltages after the amplifier. Since the maximum
frequency does not exceed 30kHz, the capacitance of the ESD diode is not a concern. Because analog audio
can have both positive and negative voltage swings, ESD designs must be bidirectional to prevent premature
breakdown which can interfere with the signal.
The ESD designs below offer ESD protection that exceeds the IEC 61000-4-2 level 4 standard. These designs
are bidirectional which allow for both the positive and negative voltage swings of audio signals. The designs
below also come in a variety of working voltages to support different audio-voltage levels.
Table 3-2. ESD Designs for Audio Applications (Click here for more products on Ti.com)
IEC 610000-4-2
ESD341 ±3.6 30 0.66 1 0.6 × 0.3 DFN0603
ESD451 ±5.5 30 0.5 1 0.6 × 0.3 DFN0603
TPD1E10B09 ±9 20 10 1 1.0 × 0.6 DFN1006
ESD501-Q1 ±12 15 0.3 1 1.0 × 0.6 DFN1006
ESD761-Q1 ±24 15 1.1 1 1.0 × 0.6 DFN1006

3.3 CAN Circuit Protection
CANH
R
T/2
CAN CAN Transceiver
bus
R
T/2
CANL
C
G
Figure 3-3. CAN Application Diagram
The CAN interface has two lines that require ESD protection (CANH and CANL). In the common 12V battery
automotive systems, there is also the requirement to allow for 24V. This is due to the possibility miswiring when
the battery is being charged, shorting the signal line to the CAN bus.
For automotive systems a 24V working voltage diode is required and uses two channels for layout and
capacitance matching. TI offers devices for CAN, CAN-FD, and CAN-XL, in addition to supporting working
voltages up to 36V. For more details about CAN ESD protection, see Protecting Automotive CAN Bus Systems
from ESD Overvoltage Events.
Table 3-3. ESD Designs for CAN Applications (Click here for more products on Ti.com)
IEC 610000-4-2
Working Capacitance Package Size
Device ESD Ratings Channels Package
Voltage (V) (pF) (mm)
(kV) (Contact)
2.92 × 1.3 SOT-23-3
ESD2CAN24-Q1 ±24 30 3 2
2.0 × 1.25 SC-70-3
ESD2CANFD24-Q1 ±24 25 2.5 2 2.92 × 1.3 SOT-23-3
ESD2CANXL24-Q1 ±24 20 1.7 2 2.92 × 1.3 SOT-23-3
ESD2CAN36-Q1 ±36 25 2.8 2 2.92 × 1.3 SOT-23-3
ESD2CANFD36-Q1 ±36 18 2.6 2 2.92 × 1.3 SOT-23-3

3.4 DisplayPort Circuit Protection
ML_Lane0+
ML_Lane0-
ML_Lane1+
ML_Lane1-
ML_Lane2+
ML_Lane2-
ML_Lane3+
ML_Lane3-
DisplayPort Connector DisplayPort Controller
CONFIG1
CONFIG2
AUX+
AUX-
HPD
Return
VBUS
Figure 3-4. DisplayPort Application Diagram
DisplayPort connectors require protection on eight high-speed ML data lines and four low-speed data lines, all at
3.3V. DisplayPort 2.1 uses four UHBR data lines which can reach speeds of 20Gbps, or 80Gbps total. At these
speeds, protection requires ultra-low capacitance to maintain signal integrity.
For the eight high-speed UHBR lines, TI recommends using two 4-channel ESD devices with ultra-low
capacitance. TI also recommends using another 4-channel device for the four low-speed lines, although the
capacitance requirements are not as strict. To protect the remaining lines, single channel, 3.3V tolerant devices
can be used. These lines are not passing data, so the capacitance of the device is not very important.
Table 3-4. ESD Designs for DisplayPort Applications (Click here for more products on Ti.com)
IEC 61000-4-2
Working Capacitance Package
Device ESD Rating Channels Package
Voltage (V) (pF) Size (mm)
ESD204 ±3.6 30 0.55 4 2.5 × 1.0 DFN2510
ESD341 ±3.6 30 0.66 1
TPD4E02B04-Q1 ±3.6 12 0.25 4 2.5 × 1.0 DFN2510
TPD1E01B04-Q1 ±3.6 15 0.18 1 0.6 × 0.3 DFN0603

3.5 Ethernet Circuit Protection
TX+
TX-
Ethernet Transceiver
GND GND (PHY)
RX+
RX-
Figure 3-5. Ethernet Application Diagram
Ethernet applications requires four channels of ESD protection for the Tx/Rx signal lines in the connector. The
voltage of these signals can range from 1V to 2.5V and the bandwidth options include 10Mbps, 100Mbps for
Fast Ethernet, and 1Gbps for Gigabit Ethernet. At these speeds, the capacitance of the ESD diode must be
considered.
4-channel devices are recommended for Ethernet applications for layout convenience. To maintain signal
integrity, capacitance also must be considered, especially for Gigabit Ethernet (< 5pF is recommended). For
more details on Ethernet protection, see Protecting Ethernet Ports from Surge Events.
Table 3-5. ESD Designs for Ethernet Applications (Click here for more products on Ti.com)
Working IEC 61000-4-5
Device ESD Rating Capacitance (pF) Channels Package
Voltage (V) Surge (A)
ESDS304 3.6 30 2.3 4 12 SOT-23
ESD204 ±3.6 30 0.55 4 5.5 DFN2510
TPD4E02B04-Q1 ±3.6 12 0.25 4 2 DFN2510
SOT-23-3
TPD2E2U06-Q1 5.5 25 1.5 2 5.5
SC-70-3

3.6 FPD-Link Protection
Power Regulator Power Source
GND GND GND
TX RX
Figure 3-6. FPDLink Application Diagram
FPD-Link is commonly used in vehicles for video applications, such as camera feeds or touchscreens. FPD-Link
enables these high bandwidth signals to be sent over relatively cheap coaxial or twisted pair cables. The forward
channel can reach speeds up to 7.55Gbps, meaning that diode capacitance is an important factor to minimize.
FPD-Link transceivers can support 3.3V or 5V signaling, so selected devices must match this working voltage.
TI recommends placing ESD diodes on both sides of cable to protect both the transceiver and receiver. At these
data speeds, capacitance must be <= 0.3pF to minimize signal attenuation.
Table 3-6. ESD Designs for FPD-Link Applications (Click here for more products on Ti.com)
Device ESD Rating Capacitance Channels Package
DFN0603
TPD1E01B04-Q1 ±3.6 15 0.2 1 0.6 × 0.31.0 × 0.6
DFN1006
ESD501-Q1 ±12 15 0.3 1 1.0 × 0.6 DFN1006
ESD601-Q1 ±18 15 0.3 1 1.0 × 0.6 DFN1006
ESD701-Q1 ±24 15 0.3 1 1.0 × 0.6 DFN1006
ESD801-Q1 ±36 15 0.3 1 1.0 × 0.6 DFN1006

3.7 HDMI Circuit Protection
TMDS_D2+
TMDS_D2-
TMDS_D1+
TMDS_D1-
TMDS_D0+
TMDS_D0-
HDMI Connector HDMI Controller
TMDS_CLK+
TMDS_CLK-
CEC
Utility
DDC_CLK
DDC_DATA
Figure 3-7. HDMI Application Diagram
The HDMI connector requires ESD protection for all 12 data lines: eight low-voltage, high-speed TMDS lines and
four 5V control lines. The speed of the TMDS lines can reach a maximum of 16Gbps per lane (48Gbps for the
whole connector) for HDMI 2.1 so minimizing capacitance is crucial.
For the eight TMDS lines, TI recommends using two 4-channel ESD devices with ultra-low capacitance to
minimize board layout and maintain signal integrity. A 5V tolerant, 4-channel device must be used to protect the
lower-speed control lines. 5V tolerant, single-channel devices can also be used for greater layout flexibility. For
more details about HDMI protection, see ESD Protection for HDMI Applications.
Table 3-7. ESD Designs for HDMI Applications (Click here for more products on Ti.com)
ESD441 5.5 30 1.1 1 0.6 × 0.3 DFN0603
TPD4E05U06 5.5 12 0.4 4 2.5 × 1.0 DFN2510

3.8 Keypad and Pushbutton Circuit Protection
1 I/O Line 1
2 I/O Line 2
Buttons
Figure 3-8. Pushbutton Application Diagram
Pushbuttons and keyboards on cell phones, laptops and TVs are high-contact areas that can present a low-
impedance path for ESD to enter the system. These I/O signals are typically low speed and low voltage (< 5V).
Since the signal frequency of pushbuttons is low, the capacitance of the ESD device is not very important.
Single-channel and multichannel designs with IEC 61000-4-2 ESD protection are preferred designs. For more
information on Keypad and Pushbutton protection, see ESD Protection for Keypads, Pushbuttons, and Side
Keys.
Table 3-8. ESD Designs for Keypad/Pushbutton Applications (Click here for more products on Ti.com)
Device ESD Rating (kV) Channels Package
TPD1E6B06 ±5.5 15 6 1 0.6 × 0.3 DFN0603
TPD1E10B06-Q1 ±5.5 30 12 1
1.6 × 0.8 SOD-523

3.9 LIN Circuit Protection
CBAT
1 k
LIN
LIN Transceiver
LIN Node
(cid:1)
V
BAT
SUP
SUP
Figure 3-9. LIN Application Diagram
LIN is a common interface used across automotive and industrial applications and favored because LIN offers a
robust design. Unlike CAN, LIN uses a single ended connection only requiring one wire. However, LIN also must
be protected from possible ESD events introduced during assembly or maintenance to keep the system robust.
In the more common 12V battery automotive systems, an ESD diode with a 24V working voltage diode is
required. This is due to the possibility of a battery miswire, putting 2x battery voltage on the lines. A single
channel device is typically preferred due to the flexibility that the single channel device gives in layout. Also,
minimizing capacitance helps add robustness to the signal integrity of the bus. For more information on LIN
protection, see ESD Protection for LIN Data Lines.
Table 3-9. ESD Designs for LIN Applications (Click here for more on Ti.com)
ESD1LIN24-Q1 ±24 30 3 1 2.5 × 1.2 SOD-323
ESD751-Q1 ±24 22 2.5 1 1.6 × 0.8 SOD-523
ESD761-Q1 ±24 15 1.1 1 1.0 × 0.6 DFN1006

3.10 LVDS Circuit Protection
Twisted Pair
GND GND Twisted Pair GND GND
Twisted Pair
GND GND Twisted Pair GND GND
100
(cid:0)
(cid:2)
(cid:3)
LVDS TX LVDS RX
Figure 3-10. LVDS Application Diagram
LVDS (Low Voltage Differential Signaling) is a popular standard used for high speed, long distance
communication, reaching speeds up to 1.3Gbps. At these speeds, minimizing capacitance is crucial. Protecting
both the transceiver and receiver from ESD events is important, with the strike occuring from the twisted pair.
At these data speeds, a capacitance of < 3pF is required to maintain signal integrity. TI recommends a 5V
tolerant, 4-channel device with low capacitance to protect two tranceivers or receivers, with a device required on
both ends of the line. A 2-channel device is a good choice to protect a single tranceiver or receiver.
Table 3-10. ESD Designs for LVDS Applications (Click here for more products on Ti.com)
ESD122 ±3.6 18 0.2 2 1.0 × 0.6 DFN1006-3
2.0 × 1.25 SC70
TPD4E1U06 5.5 15 0.8 4
2.9 × 1.6 SOT-23
TPD4E05U06-Q1 5.5 12 0.5 4 2.5 × 1.0 DFN2510

3.11 MHL Circuit Protection
MHL-
Micro USB Connector MHL Controller
MHL+
CBUS
Figure 3-11. MHL Application Diagram
MHL (Mobile High-Definition Link) has three data lines and one power line that require protection. The MHL+/
MHL- lines can reach speeds of up to 6Gbps, meaning devices must have capacitance < 0.5pF. The CBUS line
passes data at a rate of up to 750Mbps, which also requires low capacitance.
An ultra-low capacitance, two-channel device is used to protect the MHL lines while minimizing board layout.
Single channel devices can also be used if required. The CBUS line must be protected by a 5V tolerant, low
capacitance device. The VBUS line does not pass data, so a 5V device with a higher capacitance is sufficient.
Table 3-11. ESD Designs for MHL Applications (Click here for more products on Ti.com)
Working Voltage Package Size
(V) (mm)
ESD122 ±3.6 17 0.2 2 1.0 × 0.6 DFN1006-3
ESD451 ±5.5 30 0.5 1 0.6 × 0.3 DFN0603
TPD1E10B06 ±5.5 30 12 1
1.6 × 0.8 SOD-523

3.12 PCIe Circuit Protection
12V
3.3V
HSOp_0
HSOn_0
HSIp_0 GND GND
HSIn_0
PCIe Connector PCIe Receiver
...
HSOp_15
HSOn_15
HSIp_15 GND GND
HSIn_15
Figure 3-12. PCIe Application Diagram
A PCIe connector has two power lines at 12V and 3.3V, as well as numerous high speed HSI/HSO data lines.
The number of data lines depends on the length of the connector. These lines can run at extremely high rates,
from 16Gbps for 4.0 HSI/HSO all the way to 64Gbps for 6.0 HSI/HSO. This requires ultra-low capacitance
devices to maintain the signal.
TI recommends using a 4-channel device to minimize board space while protecting a set of HSI/HSO high speed
lines. TPD4E02B04 has a capacitance of 0.25pF which can support data rates up to 20Gbps. In case higher
data rates are used, TI also offers devices with lower capacitance to support those requirements.
Table 3-12. ESD Designs for PCIe Applications (Click here for more products on Ti.com)
TPD4E02B04 ±3.6 12 0.25 4 2 DFN2510
TPD1E0B04 ±3.6 8 0.13 1
TSD12 12 30 12 1 2.65 × 1.3 SOD-323
ESD341 ±3.3 30 0.66 1 0.6 × 0.3 DFN0603

3.13 RS-485 Protection
R RxD
RE
XCVR MCU
DE DIR
D TxD
10k
10k
(cid:0)
VCC
0.1 μF
A
B
10
(cid:2)
10
(cid:3)
Figure 3-13. RS-485 Application Diagram
RS-485 is an electrical standard used in many industrial applications, where RS-485 is able to transmit data
over long distances while still remaining robust. RS-485 also supports multipoint communication, allowing many
devices to communicate over the network. Signaling rates can reach up to 50Mbps, meaning that capacitance is
not important to minimize.
ESD diodes for RS-485 must be bidirectional to provide support for positive and negative voltages on the lines.
TI recommends using a 2-channel device at the connector to protect both signaling lines. The standard defines
that the receiver and transceiver must operate between -7V and 12V, so any diode must have a working voltage
of 12V.
Table 3-13. ESD Designs for RS-485 Applications (Click here for more products on Ti.com)
Device ESD Rating (kV) Capacitance Channels Package
ESDS552 ±12 30 9.5 2 2.92 × 2.37 SOT-23-3
ESD562 ±12 22 1.5 2 2.92 × 2.37 SOT-23-3
ESD501 ±12 15 0.3 1 1.0 × 0.6 DFN1006

3.14 SD- and SIM-Card Circuit Protection
DAT2
DAT3
CMD IO
SD Card VDD SD Card Controller
CLK
DAT1
DAT0
Figure 3-14. SD/SIM Application Diagram
SD cards have seven pins that require ESD protection: four data pins (DAT0, DAT1, DAT2, DAT3), a clock pin
(CLK), input and output command (CMD IO), and the 2.6V to 3.3V power pin (VDD). The sequential write speed
of the fastest SD speed class is 90Mbps (VSC90) so the capacitance on these interface lines do not need to be
minimized. SIM cards have similar specs and do not require capacitance to be minimized.
The footprint of the ESD designs must be as small as possible because the board space around the SD card is
very constrained. TI recommends using single-channel devices to minimize footprint but 4-channel devices can
also be used if necessary.
Table 3-14. ESD Designs for SD- and SIM-Card Applications (Click here for more products on Ti.com)
TPD4E05U06 5.5 12 0.5 4 2.5 × 1.0 DFN2510
ESD441 5.5 30 1 1 0.6 × 0.3 DFN0603

3.15 USB 2.0 Circuit Protection
VBUS Battery Charger
D-
USB 2.0
Connector USB Transceiver
D+
Figure 3-15. USB 2.0 Application Diagram
The USB 2.0 connector has four pins: VBUS for power, D+ and D– for differential data signals and a ground pin.
The VBUS pin carries a 5V DC power supply so the capacitance on this line is of little importance. The D+ and
D– data lines carry a 480Mbps differential signal.
The VBUS line requires ESD protection with at least a 5V working voltage to make sure that breakdown does not
occur in normal operation. The D+ and D– data lines require low-capacitance ESD protection that can support a
480Mbps signal. Single-channel and dual-channel devices are designs to simplify routing. For more details about
USB protection, see ESD and Surge Protection for USB Interfaces.
Table 3-15. ESD Designs for USB 2.0 Applications (Click here for more products on Ti.com)
TPD1E01B06 ±5.5 30 12 1 1.0 × 0.6 DFN1006

3.16 USB 3.1 Circuit Protection
VBUS Battery Charger
USB 3.2 Connector GND
TX+ USB Transceiver
TX-
RX+ GND GND
RX-
Figure 3-16. USB 3.1 Application Diagram
USB 3.1 incorporates the Tx/Rx differential lines to reach speeds up to 10Gbps. For these speeds, the
capacitance of ESD protection must be minimized to maintain signal integrity.
ESD designs for the Tx/Rx lines of USB 3.1 Gen 2 must have a capacitance of 0.3pF or lower for signal
integrity purposes and have a working voltage of >3.6V. One design is a 4-channel ESD device with ultra-low
capacitance for the datalines (Tx, Rx), combined with a 2-channel ESD device with low capacitance for D+/D–
and a single-channel ESD device for the VBUS line. For more details about USB protection, see ESD and Surge
Protection for USB Interfaces.
Table 3-16. ESD Designs for USB 3.1 Applications (Click here for more products on Ti.com)
TPD4E02B04 ±3.6 12 0.25 4 2.5 × 1.0 DFN2510
TPD1E01B04 ±3.6 15 0.18 1

3.17 USB Type C Circuit Protection
RX1/2+
RX1/2-
SBU1/CC2
USB-C Connector USB Transceiver
CC1/SBU2
TX1/2-
TX1/2+
Figure 3-17. USB Type C Application Diagram
USB Type C™ has a 24-pin connector that can support USB 3.2, USB 4.0, DisplayPort, HDMI, and a variety of
other alternate modes. There are 16 pins that require ESD protection. Since the SuperSpeed USB lines for USB
4.0 (Tx1+, Tx1–, Rx1+, Rx1–, Tx2+, Tx2–, Rx2+ and Rx2–) can reach speeds up to 20Gbps, capacitance must
be minimized. The USB 2.0 lines (D+ top, D+ bottom, D– top and D– bottom) also require low capacitance. The
CC1, CC2 and SBU1, SBU2 Type-C pins can reach up to 5.5V and while low capacitance is not required, TI
recommends using low capacitance for applications that use alternate modes. The VBUS lines can also supply
power at voltages up to 20V for fast charging applications.
The USB Type-C connector houses 24 pins in a small form factor so board space becomes very constrained.
For this reason, space saving 4-channel ESD devices with ultra-low capacitance (TPD4E02B04) are
recommended for all high-speed data lines in USB Type-C. Low capacitance 2-channel devices (ESD122) can
be used for Tx/Rx lines if preferred. Single-channel 5.5V ESD devices (ESD441) are recommended for the
SBU and CC lines to simplify routing to the PD or CC controller. However, 4-channels can also be used. For
power delivery applications, the VBUS lines can be protected with a flat clamp device, which can operate at
higher voltages while still maintaining low clamping. For more details about USB protection, see ESD and Surge
Protection for USB Interfaces.

Table 3-17. ESD Designs for USB Type C Applications (Click here for more products on Ti.com)
TPD1E01B04 ±3.6 15 0.18 1 1.0 × 0.6 DFN1006
TPD1E05U06 5.5 12 4.2 1 1.0 × 0.6 DFN1006
TVS2200 22 17 105 1 2.0 × 2.0 DFN2020

3.18 4-20mA Protection
VSOURCE
4-20-mA Loop
Cable
4-20-mA
Sensor
Transmitter
4-20-mA Loop
Cable Receiver
Figure 3-18. 4-20mA Application Diagram
The 4–20mA signal standard is one of the most popular interfaces for sensor-signal transmission in industrial
applications. At a high level, the programmable logic controller (PLC) supplies a voltage source to power the
system. The field transmitters and sensors uses this source to transmit the data the transmitters and sensors
receive from the external environment in the form of a 4–20mA current which is measured by the receiver in the
PLC. This 4–20mA loop has the advantage of transmitting data with little to no signal loss. However, since the
4–20mA cables can be very long, there are opportunities for ESD (IEC 61000-4-2) and surge (IEC 61000-4-5)
pulses to couple onto the cable and damage the system.
Surge diodes that are rated to IEC 61000-4-2 and IEC 61000-4-5 must be placed in front of the transmitter,
source, and receiver to protect them from a surge or ESD strike that can couple onto the long 4–20mA cable.
Since most 4–20mA voltage sources are 24V, a diode with a slightly higher working voltage is a preferred
design. Since PLC I/O modules and field transmitters can get space constrained, the smaller the protection
diodes, the better.
Table 3-18. ESD Designs for 4-20mA Loop Applications (Click here for more products on Ti.com)
Working Voltage IEC 61000-4-5 Package Size
(V) Surge Rating (A) (mm)
1.1 × 1.1 WCSP-4
TVS3300 33 11 35 1
2 × 2 SON-6
TVS3301 ±33 8 27 1 3 × 3 SON-8
TSM36A 36 30 41 1 2.92 × 2.37 SOT-23