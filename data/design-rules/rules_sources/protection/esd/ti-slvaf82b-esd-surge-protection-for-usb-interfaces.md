---
source: "TI SLVAF82B -- ESD/Surge Protection for USB Interfaces"
url: "https://www.ti.com/lit/pdf/slvaf82"
format: "PDF 19pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 31881
---

Application Note
ESD and Surge Protection for USB Interfaces
Obi Oji Multiplexers and Protection Devices
ABSTRACT
Universal Serial Bus, more commonly known as USB, is an industry standard that defines communication,
power supply, and connectors between computers and peripherals. There are many variations of USB standards
that range from 1.5Mbps all the way up to 40Gbps with the more common standards being USB 2.0 and
USB 3.x. There are also numerous connector types such as USB Type-A and USB Type-C®. With the recent
European Union regulations, USB Type-C® is soon to be the single charging design for electronic devices
in the EU, increasing the popularity of the connector. USB Type-C® is able to support alternate modes like
DisplayPort, HMDI, and others as well as supporting USB Power Delivery (USB-PD) that allows for increased
power transmission over USB.
Table of Contents
1 Overview..........................................................................................2
2 USB 1.1...........................................................................................3
2.1 Overview.......................................................................................3
2.2 ESD Protection Requirements.......................................................................3
2.3 System Level Design..............................................................................4
3 USB 2.0 Circuit Protection............................................................................5
3.1 Overview.......................................................................................5
3.2 ESD Protection Requirements.......................................................................5
3.3 System Level Designs.............................................................................6
4 USB 5Gbps........................................................................................7
4.1 Overview.......................................................................................7
4.2 ESD Protection Requirements.......................................................................7
4.3 System Level Designs.............................................................................8
5 USB 10Gbps.......................................................................................9
5.1 Overview.......................................................................................9
5.2 ESD Protection Requirements.......................................................................9
5.3 System Level Designs............................................................................10
6 USB 20Gbps......................................................................................11
6.1 Overview......................................................................................1
6.2 ESD Protection Requirements......................................................................11
6.3 System Level Designs............................................................................12
7 USB Type-C® Protection.............................................................................13
7.1 Overview......................................................................................13
7.2 ESD Protection Requirements......................................................................14
7.3 System Level Designs............................................................................15
8 USB Power Delivery (USB-PD) Surge Protection........................................................16
8.1 Overview......................................................................................16
8.2 VBUS Protection................................................................................16
8.3 Short to VBUS..................................................................................17
9 References.......................................................................................17
10 Revision History..................................................................................17

SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024 ESD and Surge Protection for USB Interfaces 1

1 Overview
The Universal Serial Bus (USB) is an industry standard that specifies connection, communication, and power
supply between host systems and peripherals. USB has evolved over the years through a series of standards
focusing on increased data rates. The following table breaks down the standards including naming convention,
data lines, nominal rates, and connector types.
There are two types of data pairs: half-duplex (HDx) and full-duplex (FDx). USB 2.0 and earlier standards use a
single half-duplex which provides communication in both directions but only one direction at a time. A half-duplex
translates to the D+ and D- data lines. USB 3.0 and later implement a single half-duplex (D+, D-) for USB 2.0
compatibility and two or four pairs in full-duplex with the full-duplex allowing for bidirectional communication
simultaneously. A pair is considered to be either the transmit lines (TX+, TX-) or the receive lines (RX+, RX-).
USB 3.0 and later include at least two pairs (TX+, TX-, RX+, RX-), also known as a lane.
Since there are many USB standards, determining the data rates can be confusing specifically for USB 3.2 and
USB 4. The general consensus is that if the format is AxB then the last digit determines the number of lanes.
For example, USB 3.2 Gen 2x2 has a nominal rate of 20Gbps, but since there is a 2 as the last digit, this means
there are 2 data lanes each with 10Gbps totaling 20Gbps.
The following sections go into detail on ESD protection based on the nominal rate for USB interfaces.
Table 1-1. USB Standards
Standards Data Pairs Nominal Rate USB-IF Name Connector Types
USB 1.1 1 HDx 12Mbps Basic-Speed USB Type-A, Type-B
Type-A, Type-B, Type-C, Micro,
USB 2.0 1 HDx 480Mbps Hi-Speed USB
Mini
USB 3.0/USB 3.1 Gen 1/
2 FDx + 1 HDx 5Gbps USB 5Gbps Type-A, Type-B, Type-C, Micro
USB 3.2 Gen 1x1
USB 3.1 Gen 2/ USB 3.2
2 FDx + 1 HDx 10Gbps USB 10Gbps Type-A, Type-C
Gen 2x1
USB 3.2 Gen 1x2 4 FDx + 1 HDx 10Gbps USB 10Gbps Type-C
USB 3.2 Gen 2x2 4 FDx + 1 HDx 20Gbps USB 20Gbps Type-C
USB 4 Gen 2x1 2 FDx + 1 HDx 10Gbps USB 10Gbps Type-C
USB 4 Gen 2x2 4 FDx + 1 HDx 20Gbps USB 20Gbps Type-C
USB 4 Gen 3x1 2 FDx + 1 HDx 20Gbps USB 20Gbps Type-C
2 ESD and Surge Protection for USB Interfaces SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024

2 USB 1.1
2.1 Overview
USB 1.0 was the first USB standard released with a revision, USB 1.1, shortly after. USB 1.0/1.1 has a 4-wire
interface: V for power, D+ and D- for differential data signals, and a ground pin. USB 1.0/1.1 is able to
BUS
support Low Speed (1.5Mbps) and Full Speed (12Mbps). Figure 2-1 details the pin configuration in a Type-A
connector for USB 1.0/1.1.
VBUS D- D+ GND
1 2 3 4
Figure 2-1. USB 1.0/1.1 Pin Configuration
USB 1.0/1.1 is a fairly uncommon standard used today in new systems but still at risk of high voltage strikes
due to the external connector. An ESD strike can enter through the connector and can cause damage to the
downstream components in the system. The following sections discuss the ESD protection requirements and the
system-level design for USB 1.0/1.1.
2.2 ESD Protection Requirements
For protecting UBS 1.0/1.1, follow the list of parameters related to each pin:
• D+ and D-
– Working Voltage: The reverse working voltage (V ) of the protection diode is recommended to be
RWM
greater than or equal to the operating voltage of the system being protected. For USB 1.0/1.1 data lines,
the typical operating voltage is 3.3V. A working voltage greater than or equal to 3.3V is recommended.
– Clamping Voltage: There can be many systems utilizing USB. This results in the clamping voltage of the
ESD diode being dependent on the circuity downstream from the USB connector. The clamping voltage is
recommended to be below the absolute maximum rating of the downstream component.
– Capacitance: For USB 1.0/1/1, the signal speeds can reach up to 12Mbps. A capacitance less than 20pF
is recommended to support the signal speed.
– IEC 61000-4-2 Rating: Real-world ESD strikes are defined by the IEC 61000-4-2 testing standard. This
standard consists of two measurements: contact and air-gap discharge. The higher the contact and
air-gap rating, the higher the voltage a device can withstand. For USB 1.0/1.1, a minimum IEC 61000-4-2
rating of 8kV for contact and 15kV for air-gap is recommended.
• V
– Working Voltage: For V , the operating voltage is 5V. An ESD diode with a working voltage greater than
or equal to 5V is recommended.
Table 2-1 lists devices that support these specifications.
Table 2-1. USB 1.0/1.1 Device Recommendations
IEC 61000-4-2 (kV)
Device VRWM (V)
(Contact/Air-gap)
Capacitance (pF) Channel Count Package Size (mm) Recommended For
DFN1006 (1.00 x 0.60),
ESD321 3.6 30/30 0.9 1 D+, D-
SOD523 (1.60 x 0.80)
ESD441 5.5 30/30 1 1 DFN0603 (0.60 x 0.30) VBUS
TPD4E05U06 5.5 12/15 0.5 4 USON (2.50 x 1.00) D+, D-, VBUS
SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024 ESD and Surge Protection for USB Interfaces 3

2.3 System Level Design
TI offers ESD protection diodes with options to protect USB 1.0/1.1. Figure 2-2 shows a block diagram
implementing three ESD protection diodes. The diodes are connected to each data and power line between
the connector and either the battery charger or USB controller. To properly protect the system, place the diodes
as close to the source of ESD, in this case the connector, as design rules allow.
ESD441
Battery
VBUS
Charger
D-
USB
Controller
D+
ESD321 (x2)
PowerLine Protection
Data Line Protection
rotcennoC
BSU

Figure 2-2. USB 1.0/1.1 ESD Protection
For Figure 2-2, ESD321 is used to the protect the D+ and D- lines and ESD441 is used to protect the VBUS line.
There is also an option to use one ESD diode that protects both the data and power lines. For this to work, the
diode is recommended to have a working voltage greater than or equal to 5V. A device that can handle both data
and power lines is TPD4E05U06.
4 ESD and Surge Protection for USB Interfaces SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024

3 USB 2.0 Circuit Protection
3.1 Overview
USB 2.0, also known as hi-speed USB, is an updated version of USB 1.0/1.1 with improved functionality and
increased data speeds. USB 2.0 has a 4-wire interface: V for power, D+ and D- for differential data signals,
and a ground pin. The pin configuration for USB 2.0 is shown in Figure 3-1 for a Type-A connector. USB 2.0 is
able to support Low Speed (1.5Mbps), Full Speed (12Mbps), and High Speed (480Mbps).
VBUS D- D+ GND
1 2 3 4
Figure 3-1. USB 2.0 Pin Configuration
USB 2.0 is a common interface still used today across a range of devices and applications. Since the connector
is exposed to the outside world, the system is at risk of a high voltage strike. This transient event can cause
damage to the downstream components in the system. The following sections discuss the ESD protection
requirements and the system-level design for USB 2.0.
3.2 ESD Protection Requirements
For protecting UBS 2.0, follow the list of parameters related to each pin:
• D+ and D-
greater than or equal to the operating voltage of the system being protected. For USB 2.0 data lines, the
typical operating voltage 3.3V. This translates to a working voltage of greater than or equal to 3.3V.
– Clamping Voltage: There can be many systems utilizing USB. This results in the clamping voltage of the
ESD diode being dependent on the circuity downstream from the USB connector. The clamping voltage is
– Capacitance: Since the signal speeds for USB 2.0 can reach up to 480Mbps, a low-capacitance ESD
diode with less than 4pF is recommended to support the signal speed.
– IEC 61000-4-2 Rating: Real-world ESD strikes are defined by the IEC 61000-4-2 testing standard. This
air-gap rating, the higher the voltage a device can withstand. For USB 2.0, a minimum IEC 61000-4-2
– Working Voltage: For V , the operating voltage is 5V. An ESD diode with a working voltage greater than
Table 3-1 lists devices that support these specifications.
Table 3-1. USB 2.0 Device Recommendations
SOD523(1.60 x 0.80)
DFN1006, 3 pins (1.00
ESD122 3.6 17/17 0.2 2 D+, D-
x 0.60)
TPD4E05U06 5.5 12/15 0.5 4 USON (2.50 x 1.00) D+, D-, VBUS
SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024 ESD and Surge Protection for USB Interfaces 5

3.3 System Level Designs
TI offers a multitude of ESD diodes with options to protect USB 2.0. Figure 3-2 shows a block diagram
implementing three ESD protection diodes. The diodes are connected to each data and power line between
the connector and either the battery charger or USB controller. To properly protect the system, place the diodes
PowerLine Protection

Figure 3-2. USB 2.0 ESD Protection
For the above diagram, ESD321 is used to the protect the D+ and D- lines and ESD441 is used to protect the
VBUS line. There is also an option to use one ESD diode that protects both the data and power lines. For this to
work, the diode is recommended to have a working voltage greater than or equal to 5V. A device that can handle
both data and power lines is TPD4E05U06.
6 ESD and Surge Protection for USB Interfaces SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024

4 USB 5Gbps
4.1 Overview
USB standards that reach a nominal rate of 5Gbps include: USB 3.0, USB 3.1 Gen 1, and USB 3.2 Gen 1x1.
These standards use the following pins: V for power, D+ and D- for differential data signals, TX+, TX-, RX+,
and RX- for transmitting and receiving signals, and ground.
USB 5Gbps is used in various devices and applications. There is an external connector which puts the system
at risk of a high voltage strike. This transient event can cause damage to the downstream components in the
system if the system is not protected properly. The following sections discuss the ESD protection requirements
and the system-level design for protecting speeds up to 5Gbps.
4.2 ESD Protection Requirements
For protecting USB 5Gbps, follow the list of parameters related to each pin:
• D+, D-, TX+, TX-, RX+, RX-
greater than or equal to the operating voltage of the system being protected. For USB 5Gbps data lines,
the typical operating voltage is 3.3V. A protection diode with a working voltage greater than or equal to
3.3V is recommended.
– Clamping Voltage: There can be many systems utilizing USB. This results in the clamping voltage of the
ESD diode being dependent on the circuity downstream from the USB connector. The clamping voltage is
– Capacitance (D+, D-): Since D+ and D- are specific to USB 2.0 data transfer, the signal speeds can reach
up to 480Mbps. An ESD diode with a capacitance less than 4pF is recommended.
– Capacitance (TX+, TX-, RX+, RX-): The signal speeds can reach up to 5Gbps, a low-capacitance ESD
diode with less than 0.5pF is recommended to support the signal speed.
– IEC 61000-4-2 Rating: Real-world ESD strikes are defined by the IEC 61000-4-2 testing standard. This
air-gap rating, the higher the voltage a device can withstand. For USB 5Gbps, a minimum IEC 61000-4-2
– Working Voltage: For V , the operating voltage is 5V. An ESD diode with a working voltage greater than
Table 4-1 lists devices that support these specifications.
Table 4-1. USB 5Gbps Device Recommendations
DFN1006, 3 pins (1.00 D+, D-, TX+, TX-, RX+,
ESD122 3.6 17/17 0.2 2
x 0.60) RX-
D+, D-, TX+, TX-, RX+,
TPD4E02B04 3.6 12/15 0.25 4 USON (2.50 x 1.00)
RX-
TPD6E05U06 5.5 12/15 0.47 6 USON (3.50 x 1.35)
SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024 ESD and Surge Protection for USB Interfaces 7

4.3 System Level Designs
TI has a range of ESD diodes with options to protect USB 5Gbps. Figure 4-1 shows a block diagram
implementing four ESD protection diodes. The diodes are connected to each data and power line between
the connector and either the battery charger or USB controller. To properly protect the system, place the diodes
VBDU+S
TX+
TX-
RX+
TPD4E02B04
Power Line Protection

Figure 4-1. USB 5Gbps ESD Protection
For Figure 4-1, ESD321 is used to the protect D+ and D-. TPD4E02B04 is used for the TX/RX lines. There are
a few other options for protecting the D/TX/RX lines such as using a 6-channel device, using multiple 2-channel
devices, or even using 1-channel devices. ESD441 is used to protect the VBUS line.
8 ESD and Surge Protection for USB Interfaces SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024

5 USB 10Gbps
5.1 Overview
USB standards that reach up to a nominal rate of 10Gbps are: USB 3.1 Gen 2, USB 3.2 Gen 2x1, USB 3.2 Gen
1x2, and USB 4 Gen 2x1. These standards use the following pins: V for power, D+ and D- for differential data
signals, one lane (USB 3.1 Gen 2, USB 3.2 Gen 2x1, and USB 4 Gen 2x1) or two lanes (USB 3.2 Gen 1x2) for
transmitting and receiving signals (TX1/RX1, TX2/RX2), and ground.
USB 10Gbps is commonly used today, and since there is an external connection, the system is at risk of a
high voltage strike. An ESD strike can enter through the connector and cause damage to the downstream
components if the system is not protected properly. The following sections discuss the ESD protection
requirements and the system-level design for protecting USB 10Gbps signals.
5.2 ESD Protection Requirements
For protecting USB 10Gbps, follow the list of parameters related to each pin:
• D+, D-, TX1+, TX1-, RX1+, RX1-, TX2+, TX2-, RX2+, RX2-
greater than or equal to the operating voltage of the system being protected. For USB 10Gbps data lines,
the typical operating voltage range is 3.3V. This translates to a working voltage of greater than or equal to
3.3V.
– Clamping Voltage: There can be many systems utilizing USB. This results in the clamping voltage of the
ESD diode being dependent on the circuity downstream from the USB connector. The clamping voltage is
– Capacitance (D+, D-): Since D+ and D- are specific to USB 2.0 data transfer, the signal speeds can reach
– Capacitance (TX+, TX-, RX+, RX-): Since the signal speeds can reach up to 10Gbps, a low-capacitance
ESD diode with less than 0.3pF is recommended to support the signal speed. For USB 3.2 Gen 1x2, there
are two lanes each with 5Gbps, a capacitance less than 0.5pF is recommended to support each lane.
– IEC 61000-4-2 Rating: Real-world ESD strikes are defined by the IEC 61000-4-2 testing standard. This
air-gap rating, the higher the voltage a device can withstand. For USB 10Gbps, a minimum IEC 61000-4-2
– Working Voltage: For V , the operating voltage is 5V. An ESD diode with a working voltage greater than
Table 5-1 lists devices that support these specifications.
Table 5-1. USB 10Gbps Device Recommendations
DFN0603 (0.60 x 0.30), D+, D-, TX+, TX-, RX+,
TPD1E01B04 3.6 15/17 0.18 1
DFN1006 (1.00 x 0.60) RX-
TPD4E02B04 3.6 12/15 0.25 4 USON (2.5 x 1.0)
SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024 ESD and Surge Protection for USB Interfaces 9

5.3 System Level Designs
TI has a variety of ESD diodes that are able to protect USB 10Gbps. Figure 5-1 shows a block diagram
implementing four ESD protection diodes. The diodes are connected to each data and power line between the
connector and either the battery charger or USB controller. To properly protect the system, place the diodes as
close to the source of ESD, in this case the connector, as design rules allow.
VBDU+S
TX+
TX-
RX+
TPD4E02B04

Figure 5-1. USB 10Gbps ESD Protection
For Figure 5-1, ESD321 is used to the protect D+ and D-. TPD4E02B04 is used for the TX/RX lines. There are
a few other options for protecting the D/TX/RX lines such as using a 6-channel device, using multiple 2-channel
devices, or even using 1-channel devices. ESD441 is used to protect the VBUS line.
10 ESD and Surge Protection for USB Interfaces SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024

6 USB 20Gbps
6.1 Overview
USB standards that reach a nominal rate of 20Gbps are: USB 3.2 Gen 2x2, USB 4 Gen 2x2, and USB 4 Gen
3x1. These standards use the following pins: V for power, D+ and D- for differential data signals, one lane
(USB 4 Gen 3x1) or two lanes (USB 3.2 Gen 2x2 and USB 4 Gen 2x2) for transmitting and receiving signals
(TX1/RX1, TX2/RX2), and ground.
USB 20Gbps is used in a range of devices and applications. Since there is a connection exposed to the outside
world, there is a risk of a high voltage strike occurring. An transient event can cause damage to the downstream
components in the system. The following sections discuss the ESD protection requirements and the system-level
design for protecting speeds up to 20Gbps.
6.2 ESD Protection Requirements
For protecting USB 20Gbps, follow the list of parameters related to each pin:
greater than or equal to the operating voltage of the system being protected. For USB 20Gbps data lines,
the typical operating voltage is 3.3V. This translates to a working voltage of greater than or equal to 3.3V.
– Clamping Voltage: There can be many systems utilizing USB. This results in the clamping voltage of the
ESD diode being dependent on the circuity downstream from the USB connector. The clamping voltage is
– Capacitance (D+, D-): Since D+ and D- are specific to USB 2.0 data transfer, the signal speeds can reach
– Capacitance (TX+, TX-, RX+, RX-): For USB 4 Gen 3x1, the signal speeds can reach up to 20Gbps
meaning an ultra low capacitance ESD diode with less than 0.25pF is recommended. For the two lane
standards that reach up to 10Gbps per lane, a very low capacitance ESD diode with less than 0.3-pF is
recommended.
– IEC 61000-4-2 Rating: Real-world ESD strikes are defined by the IEC 61000-4-2 testing standard. This
air-gap rating, the higher the voltage a device can withstand. For USB 20Gbps, a minimum IEC 61000-4-2
– Working Voltage: For V , the operating voltage is 5V. An ESD diode with a working voltage greater than
Table 6-1 lists devices that support these specifications.
Table 6-1. USB 20Gbps Device Recommendations
D+, D-, TX/RX for 10-
Gbps per lane
SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024 ESD and Surge Protection for USB Interfaces 11

6.3 System Level Designs
TI has an array of ESD diodes able to protect USB 20Gbps. Figure 6-1 shows a block diagram implementing
multiple ESD protection diodes. The diodes are connected to each data and power line between the connector
and either the battery charger or USB controller. To properly protect the system, place the diodes as close to the
source of ESD, in this case the connector, as design rules allow.

TX1+
TX1-
TPD1E01B04
(x4)
RX1+
RX1-
TX2+
TX2-
TPD1E01B04
(x4)
RX2+
RX2-
Figure 6-1. USB 20Gbps ESD Protection
For Figure 6-1, ESD321 is used to the protect the D+ and D- lines, eight TPD1E01B04's are used to protect the
TX/RX lines, and ESD441 is used to protect the VBUS line. The possibilities are endless for protecting the USB
lines and can use multi-channel or single-channel protection diodes.
12 ESD and Surge Protection for USB Interfaces SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024

7 USB Type-C® Protection
7.1 Overview
USB Type-C® is a 24-pin connector that allows for transmission of large amounts of power and data on a single
cable. USB Type-C® is able to support USB 2.0 and all standards after as well as alternate modes like HDMI
and DisplayPort. The standard also supports the USB-PD standard which is primarily implemented on the USB
Type-C connector. Figure 7-1 details the pin configuration for the USB Type-C® connector.
USB 2.0
Interface
High Speed High Speed
Data Path Data Path
For Alt Mode &
accessory mode
GND TX1+ TX1- VBUS CC1 D+ D- SBU1 VBUS RX2- RX2+ GND
GND RX1+ RX1- VBUS SBU2 D- D+ CC2 VBUS TX2- TX2+ GND
Cable Cable Bus Plug Configuration
Ground Power Detection
Figure 7-1. USB Type-C® Pin Configuration
While USB Type-C® incorporates the same pins mentioned throughout the application note such as D+ and D-
and the TX/RX lines, there are additional pins specific to USB Type-C®: CC1/CC2 and SBU1/SBU2. The CC
pins are the channel configuration pins. The pins are able to detect cable attachment, cable orientation, and
current advertisement. The SBU pins are for sideband use. The pins are used in audio adapter accessory mode
and alternate modes. The alternate modes include DisplayPort, HDMI, and Thunderbolt. The following section
means the ESD protection requirements to properly protect a USB Type-C® connector.
SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024 ESD and Surge Protection for USB Interfaces 13

7.2 ESD Protection Requirements
For protecting USB Type-C®, follow the list of parameters related to each pin:
greater than or equal to the operating voltage of the system being protected. For data lines, the typical
operating voltage range is 3.3V. This translates to a working voltage of greater than or equal to 3.3V.
– Clamping Voltage: There can be many systems using USB. This results in the clamping voltage of the
ESD diode being dependent on the circuity downstream from the USB connector. The clamping voltage is
– Capacitance (D+, D-): Since D+ and D- are specific to USB 2.0 data transfer, the signal speeds can reach
– Capacitance (TX+, TX-, RX+, RX-): For speeds up to 5Gbps per lane, the capacitance is recommended
to be less than 0.5pF. For 10Gbps per lane, the capacitance is recommended to be less than 0.3pF, and
20Gbps per lane, the capacitance is recommended to be less than 0.25pF.
– IEC 61000-4-2 Rating: Real-world ESD strikes are defined by the IEC 61000-4-2 testing standard. This
air-gap rating, the higher the voltage a device can withstand. A minimum IEC 61000-4-2 rating of 8kV for
contact and 15kV for air-gap is recommended.
• CC
greater than or equal to the operating voltage of the system being protected. The typical operating voltage
for the CC pins can reach up to 5V. This translates to a working voltage of greater than or equal to 5V.
• SBU
greater than or equal to the operating voltage of the system being protected. The typical operating voltage
for the SBU pins is up to 3.6V. This translates to a working voltage of greater than or equal to 3.6V.
– Capacitance: Due to higher data speeds on the SBU lines, a low capacitance diode is needed. Depending
on the signal speed, the capacitance can vary. For speeds up to 5Gbps, a capacitance less than 0.5pF is
recommended.
• VBUS
– Working Voltage: For V , the operating voltage is 5V. An ESD diode with a working voltage greater than
Table 7-1. USB Type-C® Device Recommendations
ESD341 3.6 30/30 0.66 1 DFN0603 (0.60 x 0.30) SBU
ESD441 5.5 30/30 1 1 DFN0603 (0.60 x 0.30) CC, VBUS
14 ESD and Surge Protection for USB Interfaces SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024

7.3 System Level Designs
TI has a variety of ESD protection diodes able to protect each pin of a USB Type-C® connector. Figure 7-2
shows a block diagram implementing single-channel ESD protection diodes. The diodes are connected to each
data and power line between the connector and USB controller. To properly protect the system, place the diodes
USB Controller
TPD1E01B04 ESD441 ESD341 TPD1E01B04
TPD1E01B04 ESD441 ESD321 ESD321 ESD441 TPD1E01B04
GND TX1+ TX1- VBUS CC1 D+ D- SBU1 VBUS RX2- RX2+ GND
GND RX1+ RX1- VBUS SBU2 D- D+ CC2 VBUS TX2- TX2+ GND
TPD1E01B04 ESD441 ESD321 ESD321 ESD441 TPD1E01B04
TPD1E01B04 ESD341 ESD441 TPD1E01B04
USB Controller
Figure 7-2. USB Type-C® ESD Protection
For Figure 7-2, TPD1E04B04 is used to protect the TX/RX lines, ESD321 is used for the D+ and D- lines,
ESD441 is protecting the CC pins and VBUS, and ESD341 is used to protect the SBU pins. There are many
options for protecting USB Type-C® including using multi-channel devices.
SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024 ESD and Surge Protection for USB Interfaces 15

8 USB Power Delivery (USB-PD) Surge Protection
8.1 Overview
Over the years, the USB standard has become an interface that not only allows data to be transferred but one
that allows for transfer of power. In USB 2.0 and USB 3.x standards, the maximum power that can be delivered
is 15W, with a maximum of 5V on V . The USB-Power Delivery (USB-PD) standard allows for more power
(up to 240 W) to be supplied to systems over a compliant USB cable. The voltage on the V pin can vary
depending on the power that needs to be supplied. Common voltages are 5V, 9V, 15V, and 20V and more
recently 28V, 36V, and 48V.
8.2 VBUS Protection
As with all power lines, consideration must be taken about how to protect against transient over voltage
events. For example, when there is a plug or unplug event while there is current flowing through the cable,
inductive ringing can cause a 20V line to temporarily go up to 50V which can damage downstream circuitry.
A recommendation to protect the system is to use a protection diode and a key specification to consider is
the clamping voltage, confirming the voltage experienced by the system is below the maximum voltage of the
system. The TVS2200 is a device that protects a 20V line with a very low clamping voltage. This results in the
system seeing a maximum voltage of 28V during a transient event. The plots in Figure 8-1 and Figure 8-2 show
the result and benefits of using a TVS device. Also, Table 8-1 shows recommended TVS diodes for USB-PD
voltage levels.
Table 8-1. USB-PD VBUS Surge Protection Recommendations
USB-PD Recommended TVS Surge Package | Size
Voltage Clamping
Voltage
5V TVS0500 9V DRV | 2 × 2 mm
9V TVS1400 18V DRV |2 × 2 mm
15V TVS1800 23V DRV | 2 × 2 mm
20V TVS2200 28V DRV | 2 × 2 mm
28V TVS3300 38V DRV | 2 × 2 mm
YZF | 1.1 × 1.1 mm
Figure 8-1. USB-PD VBUS Over Voltage Event
Figure 8-2. USB-PD VBUS Over Voltage Clamped
Without TVS
by TVS2200
16 ESD and Surge Protection for USB Interfaces SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024

8.3 Short to VBUS
Protecting against a short to V is another care about. In the case of short to V , the CC and SBU pins can
BUS BUS
be exposed to the voltage on V due to the proximity to V . Figure 8-3 represents a cause of a short to
BUS BUS
VBUS event such as removing the connector improperly.
Figure 8-3. Short to VBUS
As mentioned, the voltages for USB-PD can be in the range of 5V all the way up to 48V. This requires the same
working voltage of a protection diode across CC, SBU, and VBUS pins to verify the system is protected from
ESD. Device recommendations for these conditions are shown in Table 8-2. For more devices on short to V
protection, check out the USB-PD team at TI.
Table 8-2. Short to VBUS Device Recommendations
ESD2CAN24-Q1 / SOT023 (2.92 x 2.37 ),
24 30/30 3 2 VBUS, CC, SBU
ESD752 SOT-SC70 (2.0 x 2.1)
9 References
• Texas Instruments, A primer on USB Type-C® and USB Power Delivery Applications and Requirements,
marketing white paper.
• Texas Instruments, System-Level ESD Protection Guide.
• Texas Instruments, Reading and Understanding an ESD Protection Data Sheet, user's guide.
• Texas Instruments, ESD Packaging and Layout Guide, application note.
SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024 ESD and Surge Protection for USB Interfaces 17

10 Revision History
Changes from Revision A (August 2022) to Revision B (January 2024) Page
• Added and updated information on USB to include the majority of protocols as well as added device
recommendations for each protocol...........................................................1
Changes from Revision * (November 2021) to Revision A (August 2022) Page
• Updated the numbering format for tables, figures, and cross-references throughout the document..........1
• Added ESD341 to the USB 2.0 Data Line Protection Recommendations table..........................6
18 ESD and Surge Protection for USB Interfaces SLVAF82B – AUGUST 2022 – REVISED JANUARY 2024