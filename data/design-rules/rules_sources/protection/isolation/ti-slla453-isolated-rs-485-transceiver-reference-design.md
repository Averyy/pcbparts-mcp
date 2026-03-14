---
source: "TI SLLA453 -- Isolated RS-485 Transceiver Reference Design"
url: "https://www.ti.com/document-viewer/lit/html/SLLA453"
format: "HTML"
method: "pdfplumber"
extracted: 2026-02-16
chars: 6415
---

Application Note
Isolated RS-485 Transceiver Reference Design
Anthony Viviano
ABSTRACT
This design note presents the reference designs of isolated RS-485 nodes using isolated RS-485 transceivers
and a transformer driver, SN6505B. Table 1-1 lists featured isolated RS-485 transceivers from Texas
Instruments.
Table 1-1. Isolated RS-485 Transceivers
Maximum Secondary-
Primary-Supply
Data Rate Transient Supply Package Size
Device Transmission Voltage Range
[Mbps] Isolation Voltage Voltage Range [mm]
[V]
[Vrms] [V]
ISO1500 1 3000 1.71 to 5.5 4.5 to 5.5 4.90 x 3.90
ISO1410 0.5 5000 1.71 to 5.5 3.0 to 5.5 10.30 x 7.50
Half-duplex
ISO1430 12 5000 1.71 to 5.5 3.0 to 5.5 10.30 x 7.50
ISO1450 50 5000 1.71 to 5.5 3.0 to 5.5 10.30 x 7.50
ISO1412 0.5 5000 1.71 to 5.5 3.0 to 5.5 10.30 x 7.50
ISO1432 Full-duplex 12 5000 1.71 to 5.5 3.0 to 5.5 10.30 x 7.50
ISO1452 50 5000 1.71 to 5.5 3.0 to 5.5 10.30 x 7.50
Table of Contents
1 Design......................................................................................................................................................................................2
2 References..............................................................................................................................................................................4
3 Revision History......................................................................................................................................................................5
List of Figures
Figure 1-1. Half-duplex Isolated RS-485 Node............................................................................................................................2
Figure 1-2. Full-duplex Isolated RS-485 Node............................................................................................................................3
List of Tables
Table 1-1. Isolated RS-485 Transceivers.....................................................................................................................................1

1 Design
All ISO14xx and ISO1500 transceivers use TI's SiO based isolation technology to provide reliable high voltage
2
isolation for the RS-485 transmit, receive, and enable signals. The ISO14xx family is Profibus compliant to
support a larger differential voltage at 5-V bus-side supply to ensure reliable communication in noisy industrial
environments. The ISO1500 is a small solution size option with lowered isolation specifications, ideal for isolating
ground loops in long distance communication. The wide primary side supply voltage of ISO14xx and ISO1500
provide the option to interface directly with low-voltage microcontrollers to conserve power, whereas the 5 V
option on the secondary side maintains a high signal-to-noise ratio of the bus signals. These transceivers all
present 1/8 unit load to the bus for support of up to 256 nodes and have a typical common mode transient
immunity of 100 kV/us.
The push-pull transformer driver SN6505B paired with an external transformer and optional rectifying LDO
create an isolated power supply to power the isolated transceiver. The SN6505B device allows a maximum of 5
W of power to systems that need isolated power for multiple devices and alternatively SN6501 can be used for
up to 1.5 W of output power. This solution provides a compact, efficient, and low noise solution for creating an
isolated power supply.
The ISO14xx family has robust EMC protection integrated into the device capable of 30 kV HBM ESD, 16 kV
IEC ESD, and 4 kV IEC EFT. To further enhance the transient protection, a low-capacitive transient voltage
suppressor (TVS), such as PSM712, is optional. The device provides a 600 W surge capability, 75 pF of
capacitance, and up to 40 kV ESD protection, while its stand-off voltages cover the RS-485 common-mode
range of –7 V to +12 V. Implementation of additional noise filtering to the signal paths between the node
controller and the single-ended side of the transceiver through simple R-C low-pass filters is recommended.
Calculate the filter component values such that RF × CF = 0.032 / fS with fS being the highest signal frequency
of interest.
Figure 1-1 shows the system diagram for a half-duplex isolated RS-485 node using ISO1410 for signal isolation
and SN6505B with transformer for power isolation. Figure 1-2 shows the system diagram for a full-duplex
isolated RS-485 node using ISO1412 for signal isolation and SN6505B with transformer for power isolation.
GND D2 4 8 1 IN OUT 5
TPS76350
3 7 3 EN
SN6505 VCC 2 6
2 4
GND NC
CLK D1 1 5
1 16
VDD
0.01 µF 0.1 µF
VCC1
ISO1410
VCC2
0.1 …F
RF1
5 DE
DIR
CF1
RF2
6 D
TxD
MSP430Œ CF2
B 13 10 (cid:13) Optional
3 R
B
RxD A 12 10 (cid:13)
CF2 A
4 RE 2 1
RTN
2, 8 9, 15
DGND GND1 GND2
3
Galvanic PSM712
Isolation Barrier (600 W)
Figure 1-1. Half-duplex Isolated RS-485 Node
2 Isolated RS-485 Transceiver Reference Design SLLA453A – MAY 2019 – REVISED SEPTEMBER 2022

GND D2 4 8 1 IN OUT 5
TPS76350
3 7 3 EN
SN6505 VCC 2 6
2 4
GND NC
CLK D1 1 5
1 16
VDD
0.01 µF 0.1 µF
VCC1
ISO1412
VCC2
0.1 …F
RF1
5 DE
DIR
CF1 Z 12 10 (cid:13)
6 D
Z
TxD Y 11 10 (cid:13)
MSP430Œ CF2 Y
B 13 10 (cid:13)
3 R
B
RxD A 14 10 (cid:13)
CF2 A
4 RE 2 1 2 1
RTN
2, 8 9, 15
DGND GND1 GND2
3 2 × PSM712 3
Galvanic (600 W)
Isolation Barrier
Optional
Figure 1-2. Full-duplex Isolated RS-485 Node

2 References
Refer to theses references for more information on the devices listed in this application report:
1. Texas Instruments, Isolated RS-485 Transceivers
2. Texas Instruments, How to Isolate Signal and Power for an RS-485 System, application note
3. Texas Instruments, How to Isolate RS-485 for Smallest Size and Highest Reliability, application brief
4. Texas Instruments, Isolated RS-485 with Integrated Signal and Power Reference Design
4 Isolated RS-485 Transceiver Reference Design SLLA453A – MAY 2019 – REVISED SEPTEMBER 2022

3 Revision History
Changes from Revision * (May 2019) to Revision A (September 2022) Page
• Deleted the Rise Time column and added the ISO1176 device in theIsolated RS-485 Transceivers table........1
• Updated the numbering format for tables, figures, and cross-references throughout the document..................1