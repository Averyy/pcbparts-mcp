---
source: "Microchip ATAN0103 -- ATA6560/ATA6561 CAN FD Transceiver Application Note"
url: "https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ApplicationNotes/ApplicationNotes/Atmel-9310-ATA6560-EK-ATA6561-EK_Application-Note.pdf"
format: "PDF 17pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 28953
---

APPLICATION NOTE
ATA6560-EK, ATA6561-EK
ATAN0103
Introduction
The development board for the Atmel® ATA6560 and ATA6561 enables users to rapidly
carry out prototyping and testing of new CAN designs with the Atmel ATA6560 and Atmel
ATA6561 high-speed CAN transceivers.
Figure 1. Atmel ATA6560-EK, ATA6561-EK Development Board
The Atmel ATA6560/ATA6561 is a high-speed CAN transceiver that provides an interface
between a controller area network (CAN) protocol controller and the physical two-wire CAN
bus. The transceiver is designed for high-speed (up to 5Mbit/s) automotive CAN applica-
tions delivering differential transmit and receive capability to (a microcontroller with) a CAN
protocol controller. It offers superior electromagnetic compatibility (EMC) and electrostatic
discharge (ESD) performance, as well as features such as:
● Ideal passive behavior to the CAN bus when the supply voltage is off
● Direct interfacing to microcontrollers with supply voltages from 3V to 5V (ATA6561)
9310E-AUTO-10/16

Three operating modes together with dedicated fail-safe features make the Atmel® ATA6560/ATA6561 an excellent choice
for all types of high-speed CAN networks, especially in nodes requiring low-power mode with wake-up capability via the CAN
bus.
The Atmel ATA6560/ATA6561 is available in a SO8 package as well as in a DFN8 package for space-saving application, as
shown in Figure 2 and Figure 3. There are footprints for both package types on the development board.
Figure 2. SO8 Pinning
TXD 1 8 STBY TXD 1 8 STBY
GND 2 7 CANH GND 2 7 CANH
ATA6561 ATA6560
VCC 3 6 CANL VCC 3 6 CANL
RXD 4 5 VIO RXD 4 5 NSIL
Figure 3. DFN8 Pinning
TXD STBY TXD STBY
GND CANH GND CANH
VCC CANL VCC CANL
RXD VIO RXD NSIL
The CAN transceiver has the following features:
● Fully compliant with ISO 11898-2,-5 and SAE J2284
● Low electromagnetic emission (EME) and high electromagnetic immunity (EMI)
● Communication speed up to 5Mbit/s
● Differential receiver with wide common-mode range
● Silent Mode (receive only mode, only available at the ATA6560)
● Standby mode
● Remote wake-up capability via CAN bus
● Functional behavior predictable under all supply conditions
● Transceiver disengages from the bus when not powered up
● RXD recessive clamping detection
● High electrostatic discharge (ESD) handling capability on the bus pins
● Bus pins protected against transients in automotive environments
● Transmit data (TXD) dominant time-out function
● Undervoltage detection on VCC and VIO pins
● CANH/CANL short-circuit and overtemperature protected
2 ATAN0103 [APPLICATION NOTE]
9310E–AUTO–10/16

1. Development Kit Features
The development board for the Atmel® ATA6560/ATA6561 ICs supports the following features:
● All components necessary to put the ATA6560/ATA6561 into operation are included
● Placeholders for some optional components for extended functions are included (e.g., common-mode choke)
● All pins are easily accessible
● Footprint for DFN8 and SO8 package
● Ground coulter clip for easy probe connection during oscilloscope measurement
2. Quick Start
The development board for the Atmel ATA6560/ATA6561 is shipped including all components allowing immediate CAN
node development.
Connecting an external 5V DC power supply between the terminals VCC and GND puts the IC in one of the three operating
modes: normal, silent (with the Atmel ATA6560 only) and standby, which can be selected via the STBY and NSIL pins (see
Section 3.1.7 “System Control Pins (STBY, NSIL)” on page 6 for more information). See Table 2-1 for a description of the
operating modes under normal supply conditions.
Table 2-1. Operating Modes
Inputs Outputs
Mode STBY NSIL Pin TXD CAN Driver Pin RXD
Normal LOW HIGH(2) LOW Dominant LOW
LOW HIGH(2) HIGH Recessive HIGH
Standby HIGH x(3) x(3) Recessive Active(4)
Silent LOW LOW x(3) Recessive Active(1)
Notes: 1. LOW if the CAN bus is dominant, HIGH if the CAN bus is recessive
2. Internally pulled up if not bonded out
3. Irrelevant
4. Reflects the bus only for wake-up
Figure 2-1. Switch Jumpers for Changing the Operating Mode (J2 Available for the Atmel ATA6560 only)
ATAN0103 [APPLICATION NOTE] 3

2.1 Normal Mode
A low level on the STBY pin together with a high level on pins TXD and NSIL (if applicable) selects the normal mode. In this
mode the transceiver is able to transmit and receive data via the CANH and CANL bus lines. The output driver stage is
active and drives data from the TXD input to the CAN bus. The high-speed comparator (HSC) converts the analog data on
the bus lines into digital data which is output to the RXD pin. The bus biasing is set to VCC/2 and the undervoltage
monitoring of VCC is active.
The slope of the output signals on the bus lines is controlled and optimized in a way that guarantees the lowest possible
electromagnetic emission (EME).
To switch the device in normal operating mode, set the STBY pin to low (switch jumper J1 set to the right side) and the NSIL
pin (if available) to high (switch jumper J2 set to upper position). For example for test purposes also a signal generator can
be connected to the STBY pin and/or to the NSIL pin (at the pin header X1 on the left side of the board). Therefore the switch
jumper J1 and/or J2 should be set to the middle position.
Please note that the device cannot enter normal mode as long as TXD is at GND level.
The STBY and the NSIL pins each provide a pull-up resistor to VIO, thus ensuring defined levels if the pins are open.
2.2 Silent Mode (with the Atmel ATA6560 only)
A low level on the NSIL pin and on the STBY pin switches the ATA6560 into silent mode. This receive-only mode can be
used to test the connection of the bus medium. In silent mode the Atmel® ATA6560 can still receive data from the bus, but
the transmitter is disabled and therefore no data can be sent to the CAN bus. The bus pins are released to recessive state.
All other IC functions, including the high-speed comparator (HSC), continue to operate as they do in normal mode. Silent
mode can be used to prevent a faulty CAN controller from disrupting all network communications.
2.3 Standby Mode
A high level on the STBY pin selects standby mode. In this mode the transceiver is not able to transmit or correctly receive
data via the bus lines. The transmitter and the high-speed comparator (HSC) are switched off to reduce current consumption
and only the low-power wake-up comparator (WUC) monitors the bus lines for a valid wake-up signal. A signal change on
the bus from “Recessive” to “Dominant” followed by a dominant state longer than t switches the RXD pin to low to signal
wake
a wake-up request to the microcontroller.
In standby mode the bus lines are biased to ground to reduce current consumption to a minimum. The wake-up comparator
(WUC) monitors the bus lines for a valid wake-up signal. When the RXD pin switches to low to signal a wake-up request, a
transition to normal mode is not triggered until the STBY pin is forced back to low by the microcontroller. A bus dominant
time-out timer prevents the device from generating a permanent wake-up request by switching the RXD pin to high.
For Atmel ATA6560 only: In the event the NSIL input pin is set to low in standby mode, the internal pull-up resistor causes an
additional quiescent current from VIO to GND. Atmel therefore recommends setting the NSIL pin to high in standby mode.
4 ATAN0103 [APPLICATION NOTE]

3. Hardware Description
3.1 Pin Description
The following sections show and describe the external elements required for some of the pins. Please see the specific
datasheet for more information about this topic.
3.1.1 Power Supply
In order to get the development board running, an external stabilized 5V DC power supply has to be connected to the VCC
header. Please keep in mind the maximum rating for the VCC pin is 5.5V and a higher voltage may cause permanent
damage to the device.
3.1.2 VIO Supply Pin
There are two versions of the device available, with the function of pin 5 as the only difference.
● On the Atmel® ATA6561 pin 5 is VIO and should be connected to the supply voltage of the connected microcontroller.
This adjusts the signal levels of the TXD, RXD, NSIL, and STBY pins to the I/O levels of the microcontroller. A jumper
is implemented on the board (J3) connecting the VIO to VCC for test purposes or quick measurements. If the VIO pin
has to be supplied with a different voltage, jumper J3 has to be removed and the VIO pin header connected to the
second external DC power supply (typically 3.3V)
● On the Atmel ATA6560 without the VIO pin, the VIO input is internally connected to VCC. This sets the signal levels of
the TXD, RXD, STBY, and NSIL pins to levels compatible with 5V microcontrollers.
3.1.3 CAN Interface (CANH, CANL, TXD, and RXD)
The CAN transceiver is only active when it is in normal mode. In silent mode the transmitter is switched off and the Atmel
ATA6560 is in receive-only mode. In standby mode the transceiver is completely switched off and no communication is
possible. Only a low power wake-up comparator (WUC) is active in order to reflect the bus for a wake-up.
3.1.4 CANH and CANL Pins
The CANH and CANL pins are the interface to the bus network. Nodes connected to the bus end must show a differential
termination, which is approximately equal to the characteristic impedance of the bus line in order to suppress signal
reflection. Instead of a one-resistor termination it is highly recommended to use a so-called split termination. EMC
measurements have shown that the split termination is able to significantly improve the signal symmetry between CANH and
CANL, thus reducing emission. Basically each of the two termination resistors is split into two resistors of equal value, i.e.,
two resistors of 60 (or 62) (R2 and R3) instead of one resistor of 120. The special characteristic of this approach is that
the common-mode signal, available at the center tap of the termination, is terminated to ground via a capacitor. The
recommended value for this capacitor is in the range of 4.7nF to 47nF (C7).
As the symmetry of the two signal lines is crucial for the emission performance of the system, the matching tolerance of the
two termination resistors should be as low as possible (<1% is desirable).
In addition, loading the CANH and CANL pin each with a capacitor of about 100pF close to the connector of the ECU (there
are placeholders on the PCB for the capacitors C7 and C8) is recommended. The main reason for doing this is to increase
the robustness to automotive transients and ESD. The matching tolerance of the two capacitors should be as low as
possible.
OEM specifications may require dedicated circuits. Please refer to the corresponding OEM specifications for specific details.
The footprint for an optional common-mode choke, to improve EMC performance, is implemented (L1).
Placeholders (R1, C6, and C4) are implemented on the board for timing measurements.
ATAN0103 [APPLICATION NOTE] 5

3.1.5 TXD Input Pin
The signal sent to the TXD input pin controls the state of the CANH/CANL outputs. An internal pull-up resistor to VIO is
implemented. The TXD input pin must be pulled to ground in order to drive the CAN bus into dominant state.
An internal timer prevents the bus lines from being driven permanently in the dominant state. If TXD is forced to low longer
than t >3ms, the transceiver internally switches the TXD state to high and the CAN bus driver is switched to the
to(DOM)TXD
recessive state. This feature is used to prevent a single faulty node (for example with a short to ground at the TXD pin) from
paralyzing communication on the entire CAN bus the faulty node is connected to.
3.1.6 RXD Output Pin
This pin reports the state of the CAN bus to the microcontroller. CAN high (recessive state) is reported by a high level at
RXD; CAN low (dominant state) is reported by a low level at RXD. The RXD output is a push-pull stage and is short-circuit
protected.
3.1.7 System Control Pins (STBY, NSIL)
These input pins are mode pins used for mode control. They are typically directly connected to an output port pin of a
microcontroller. The Atmel® ATA6560/ATA6561 supports three operating modes: normal, silent (only with the Atmel
ATA6560) and standby, which can be selected via the STBY and NSIL pins. See Table 2-1 on page 3 for a description of the
operating modes under normal supply conditions.
The STBY and the NSIL pins each provide a pull-up resistor to VIO, thus ensuring defined levels if the pins are open.
The operating mode can be easily changed via the on-board switch jumpers (switch jumper J1 for STBY pin control and
switch jumper J2 for NSIL pin control). If desired this can be done also via an external signal generator, but therefore the
switch jumper J1 and/or J2 should be set to the middle position.
6 ATAN0103 [APPLICATION NOTE]

4. Applications
Figure 4-1 and Figure 4-2 illustrate a typical circuit example using the Atmel® ATA6560 and Atmel ATA6561 devices. The
Atmel ATA656x-EK board is designed to be used either with the Atmel ATA6560 or Atmel ATA6561 device. The application
examples assume either a 5V or a 3V supplied host microcontroller. In each example there is a dedicated 5V regulator
supplying the Atmel ATA6560/ATA6561 transceiver on its VCC supply pin (necessary for proper CAN transmit capability).
Depending on which device is soldered on the board, all corresponding components required are mounted on the board.
Figure 4-1. Typical Application Circuit Atmel ATA6561 – the VIO Pin allows Direct Interfacing to Microcontrollers
with Supply Voltages down to 3V
3.3V
BAT
12V
5V
22µF(1) + 12V
100nF 100nF
VIO VCC
VDD 5 3 CANH
STBY 7 CANH
8
TXD
Microcontroller 1 ATA6561
RXD
4 CANL
6 CANL
GND 2
GND GND
(1) The size of this capacitor depends on the used external voltage regulator.
Figure 4-2. Typical Application Circuit Atmel ATA6560 – the NSIL Pin Allows the Device to be Switched to Receive-
Only Mode, Only One LDO is Necessary with a 5V Microcontroller
5V
BAT
22µF(1) + 12V
100nF
VCC
VDD STBY 8 3 7 CANH CANH
NSIL
5
Microcontroller ATA6560
1
GND RXD 4 2 6 CANL CANL
GND GND
(1) The size of this capacitor depends on the used external voltage regulator.
ATAN0103 [APPLICATION NOTE] 7

5. Test Setups and Measurements
5.1 Timing Measurements
The required components on the basic application board can be found below. A two-channel, or optimally, a four-channel
oscilloscope is sufficient to measure the timing characteristics of the Atmel® ATA6560/ATA6561. The transmit data signal
TXD can be generated by any signal generator that is capable of delivering a rectangular or pulse signal with 3.3V to 5V
amplitude, referred to GND. The characteristics of TXD, RXD and the CANH, CANL signals can be examined.
Figure 5-1. Test Setup for Timing Measurements
+5V
+
47µF 100nF
5 3
VIO/NSIL VCC
1 7
TXD CANH
R 100pF
L
4 6
RXD CANL
15pF GND STBY
2 8
Figure 5-2. Components to be Removed (Red) or Replaced (Green) for the Timing Measurement Setup
The footprint for an optional common mode choke (L1) is implemented on the development board. This common mode
choke (L1) is per default replaced by two 0 resistors.
Instead of a one-resistor termination it is highly recommended to use the commonly used so-called split termination, which is
per default assembled. EMC measurements have shown that the split termination is able to significantly improve the signal
symmetry between CANH and CANL, thus reducing emissions. Basically the termination is split into two resistors of equal
value (R2=R3=62) and a capacitor (C1) to GND at the center tap, which represents one of the two usual bus end
terminations. The special characteristic of this approach is that the common-mode signal, available at the center tap of the
two resistors, is terminated to ground via the capacitor C1. The recommended value for this capacitor C1 is in the range of
4.7nF to 47nF (4.7nF assembled per default).
8 ATAN0103 [APPLICATION NOTE]

As the symmetry of the two signal lines is crucial for the emission performance of the system, the matching tolerance of the
two termination resistors R1 and R2 should be as low as possible (< 1% is desirable).
Additionally placeholders are implemented on the board for timing measurements (R1, C6 and C4). If a function generator is
connected to the TXD header, it can be adjusted to output a rectangular signal up to a frequency corresponding to the
maximum data rate of the final application. Please pay attention that its output signal levels are in the appropriate range
particularly that no negative voltage occurs. Of course the function generator can be replaced by a dedicated data generator
in order to form a better approach to the desired application. The high-impedance inputs of the oscilloscope can be
connected directly - however it's advantageous to use probes, so that the signals are not noticeable affected by the
capacitance of the coaxial cable.
Figure 5-3. Timing Diagram for High Speed CAN Bus
HIGH
LOW
CANH
CANL
dominant
0.9V
VO(dif) (bus)
0.5V
recessive
HIGH
RXD 0.7VIO
0.3VIO
LOW
td(TXD-busdom) td(TXD-busrec)
td(busdom-RXD) td(busrec-RXD)
tPD(TXD-RXD) tPD(TXD-RXD)
ATAN0103 [APPLICATION NOTE] 9

Figure 5-4. Measurement of the TXD, CANH, CANL and RXD Signal at a Data Rate of 1Mbit/s
The plot above shows the typical bus line signals for a 0-1 bit sequence at a data rate of 1Mbit/s and VCC=VIO=5V. The
excellent symmetry of the CANH and CANL signals ensures superior EMC performance.
5.2 Measurement Hints
5.2.1 Passive Behavior
Partial networking is implemented in the most recent in-vehicle networks. In these applications some transceivers can
become unpowered (e.g., clamp-15 nodes) while other transceivers are continuously supplied (e.g., clamp-30 nodes). In
such networks the Atmel® ATA6560/ATA6561 is favored for partially unpowered applications because of its excellent
passive behavior to the bus when the VCC supply is switched off. In addition, the Atmel ATA6560/ATA6561 is protected
against reverse currents via the TXD, RXD, and STB pins. There is no backward current via those pins if the accompanying
microcontroller continues to be supplied.
5.2.2 Optional Circuitry at CANH and CANL
The EMC performance of the Atmel ATA6560/ATA6561 has been optimized for use of the CAN termination without a
common-mode choke. The excellent output stage symmetry allows use without chokes. If, however, system performance is
still not sufficient, there is the option of using additional measures such as common-mode chokes (a footprint for a common-
mode choke is implemented at the Atmel ATA656x-EK board), capacitors, and ESD clamping diodes.
Please note that if any critical measurements on EMI (electromagnetic interference) performance, such as electromagnetic
immunity or electromagnetic emission, are to be taken, Atmel recommends using a dedicated board with a highly
symmetrical layout for the bus lines and ground vias at each connection to the ground plane. For investigations on complete
links such as bit error measurements, a test board with at least two transceivers is required in any case.
10 ATAN0103 [APPLICATION NOTE]

5.2.2.1 Common-Mode Choke
A common-mode choke provides high impedance for common-mode signals and low impedance for differential signals.
Because of this, common-mode signals produced by RF noise and/or by non-perfect transceiver driver symmetry are
effectively reduced while passing the choke. In fact, a common-mode choke helps to reduce emission and to improve
immunity against common-mode disturbances. Earlier transceiver devices usually needed a common-mode choke to comply
with stringent emission and immunity requirements of the automotive industry when using unshielded twisted-pair cables.
The Atmel ATA6560/ATA6561 makes it possible to build in-vehicle bus systems without chokes. Whether a choke is needed
or not ultimately depends on the specific system implementation such as the wiring harness and the symmetry of the two bus
lines (matching tolerances of resistors and capacitors). Besides the RF noise reduction, the stray inductance (non-coupled
portion of inductance) may establish a resonant circuit together with pin capacitance. This can result in unwanted oscillations
between the bus pins and the choke both with differential and common-mode signals as well as result in extra emission
around the resonant frequency. To avoid oscillations of this kind, it is highly recommended to use only chokes with a stray
inductance lower than 500nH. Bifilar wound chokes typically show an even lower stray inductance. The choke should be
placed nearest to the transceiver bus pins.
The use of common-mode chokes in CAN systems might cause extremely high transient voltages at the bus pins of the
transceiver. These transients are generated by the change in current through the inductance of the common-mode chokes if
the CAN bus is shorted to DC voltages. The actual transients that might be generated are highly dependent on the common-
mode type and value but also depend on the CAN system architecture, termination, components, and location and the
severity of the short circuit.
For systems where common-mode chokes are required, care should be used in the choice of the common-mode choke and
the system circuit to avoid the introduction of severe transients during DC short-circuit conditions on the bus.
The best methods to avoid transients generated from common-mode chokes during CAN bus line shorts to DC voltages are:
● Remove common-mode chokes from systems, where applicable
● Move transient suppression circuits between the common-mode choke and the CAN bus pins on the transceiver
● Choose a dedicated common-mode choke and a CAN termination scheme to minimize transients
5.2.2.2 Capacitors
Matched capacitors (in pairs) at CANH and CANL to GND are frequently used to enhance immunity against electromagnetic
interferences. Along with the impedance of corresponding noise sources (RF), capacitors at CANH and CANL to GND form
an RC low-pass filter. Regarding immunity, the capacitor value should be as large as possible to achieve a low corner
frequency. The overall capacitive load and impedance of the output stage establish an RC low-pass filter for the data
signals. The associated corner frequency must be well above the data transmission frequency. This results in a limit for the
capacitor value depending on the number of nodes and the data transmission frequency. Notice that capacitors increase the
signal loop delay due to longer rise and fall times. Due to these time reductions, bit timing requirements, especially at
1Mbit/s, call for a value lower than 100pF (see also SAE J2284 and ISO11898). At a bit rate of 125kBit/s the capacitor value
should not exceed 470pF. Typically, the capacitors are placed between the common-mode choke (if applied at all) and the
ESD clamping diodes.
5.2.2.3 ESD Protection
The Atmel ATA6560/61 is designed to withstand ESD pulses of up to 8kV according to the human body model at the CANH
and CANL bus pins and thus typically does not need any additional external protection methods. Nevertheless, if a higher
protection level is required, external clamping devices can be applied to the CANH and CANL lines.
Care must be taken when selecting the right protection devices. The transient protectors must be fast enough to clamp the
transient voltages. In addition, their capacitance must be considered. If the capacitance is too high, it can work together with
the choke’s inductance and cause ringing on the bus signals. Although this ringing does not corrupt the CAN signals, it might
show up as electromagnetic emission at higher frequencies.
ATAN0103 [APPLICATION NOTE] 11

6. Schematic of the Atmel ATA656x-EK Board
Figure 6-1. Atmel ATA6560-EK/ATA6561-EK Board Schematic
12 ATAN0103 [APPLICATION NOTE]

7. Board Layout
Figure 7-1. Atmel ATA6560-EK/ATA6561-EK Board Layout, Top View
ATAN0103 [APPLICATION NOTE] 13

8. Atmel ATA656x-EK Board BOM
8.1 Bill of Material of the Atmel ATA656x-EK Board
Table 8-1. Atmel ATA656x-EK Board BOM
Part Description Part Size Part Value (Pin 5 = VIO) (Pin 5 = NSIL)
Header 14 or 14, 2.54mm or Header 14 or
X1 Header 13 Header 14
Header 13 13, 2.54mm Header 13
Header 14 or 14, 2.54mm or Header 14 or
X2 Header 14 Header 12
Header 12 12, 2.54mm Header 12
X3 Header 14 14, 2.54mm Header 14 Header 14 Header 14
PCB jumper switch PCB jumper switch PCB jumper switch
J1 PCB jumper switch 13, 2.54mm
13, 2.54mm 13, 2.54mm 13, 2.54mm
PCB jumper switch PCB jumper switch
J2 PCB jumper switch 13, 2.54mm -
13, 2.54mm 13, 2.54mm
J3 Header 12 12, 2.54mm Header 12 Header 12 -
C1 Capacitor SMD 0805 4.7nF/50V 4.7nF/50V 4.7nF/50V
C2 Capacitor SMD 1210 47µF/10V 47µF/10V 47µF/10V
C3 Capacitor SMD 0805 100nF 100nF 100nF
C4 Capacitor SMD 0805 15pF - -
C5 Capacitor SMD 0805 100nF 100nF -
C6 Capacitor SMD 0805 100pF - -
C7 Capacitor SMD 0805 100pF/50V - -
C8 Capacitor SMD 0805 100pF/50V - -
GND shackle Measuring bracket GND shackle GND2 GND2 GND2
R1 Resistor SMD 1206 62/0.5W - -
R2 Resistor SMD 1206 62/0.5W 62/0.5W 62/0.5W
R3 Resistor SMD 1206 62/0.5W 62/0.5W 62/0.5W
0 resistor 0805 0 resistor 0805
Common-mode between term. 1 between term. 1
L1 EPCOS B82799 EPCOS B82799
choke and 2 and between and 2 and between
term. 3 and 4 term. 3 and 4
BR1 0 resistor SMD 0805 0 0 -
BR2 0 resistor SMD 0805 0 - 0
BR3 0 resistor SMD 0805 0 0 -
BR4 0 resistor SMD 0805 0 - 0
IC - SO8 CAN transceiver SO8 ATA656x ATA6561-GAQW ATA6560-GAQW
IC - DFN8 CAN transceiver DFN8 ATA656x ATA6561-GBQW ATA6560-GBQW
14 ATAN0103 [APPLICATION NOTE]

8.2 Atmel ATA6560-EK Board
Figure 8-1. Atmel ATA6560-EK Board
8.3 Atmel ATA6561-EK Board
Figure 8-2. Atmel ATA6561-EK Board
ATAN0103 [APPLICATION NOTE] 15

9. Revision History
Please note that the following page numbers referred to in this section refer to the specific revision mentioned, not to this
document.
Revision No. History
9310E-AUTO-10/16 Section 5.1 “Timing Measurements” on pages 8 to 9 updated
Section “Introduction” on page 2 updated
9310D-AUTO-09/14 Section 1 “Development Kit Features” on page 3 updated
Section 4 “Applications” on page 7 updated
16 ATAN0103 [APPLICATION NOTE]

X X X X X X
Atmel Corporation 1600 Technology Drive, San Jose, CA 95110 USA T: (+1)(408) 441.0311 F: (+1)(408) 436.4200 | www.atmel.com
© 2016 Atmel Corporation. / Rev.: 9310E–AUTO–10/16
Atmel®, Atmel logo and combinations thereof, Enabling Unlimited Possibilities®, and others are registered trademarks or trademarks of Atmel Corporation in U.S. and
other countries. Other terms and product names may be trademarks of others.
DISCLAIMER: The information in this document is provided in connection with Atmel products. No license, express or implied, by estoppel or otherwise, to any intellectual property right
is granted by this document or in connection with the sale of Atmel products. EXCEPT AS SET FORTH IN THE ATMEL TERMS AND CONDITIONS OF SALES LOCATED ON THE
ATMEL WEBSITE, ATMEL ASSUMES NO LIABILITY WHATSOEVER AND DISCLAIMS ANY EXPRESS, IMPLIED OR STATUTORY WARRANTY RELATING TO ITS PRODUCTS
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT. IN NO EVENT
SHALL ATMEL BE LIABLE FOR ANY DIRECT, INDIRECT, CONSEQUENTIAL, PUNITIVE, SPECIAL OR INCIDENTAL DAMAGES (INCLUDING, WITHOUT LIMITATION, DAMAGES
FOR LOSS AND PROFITS, BUSINESS INTERRUPTION, OR LOSS OF INFORMATION) ARISING OUT OF THE USE OR INABILITY TO USE THIS DOCUMENT, EVEN IF ATMEL HAS
BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. Atmel makes no representations or warranties with respect to the accuracy or completeness of the contents of this
document and reserves the right to make changes to specifications and products descriptions at any time without notice. Atmel does not make any commitment to update the information
contained herein. Unless specifically provided otherwise, Atmel products are not suitable for, and shall not be used in, automotive applications. Atmel products are not intended,
authorized, or warranted for use as components in applications intended to support or sustain life.
SAFETY-CRITICAL, MILITARY, AND AUTOMOTIVE APPLICATIONS DISCLAIMER: Atmel products are not designed for and will not be used in connection with any applications where
the failure of such products would reasonably be expected to result in significant personal injury or death (“Safety-Critical Applications”) without an Atmel officer's specific written
consent. Safety-Critical Applications include, without limitation, life support devices and systems, equipment or systems for the operation of nuclear facilities and weapons systems.
Atmel products are not designed nor intended for use in military or aerospace applications or environments unless specifically designated by Atmel as military-grade. Atmel products are
not designed nor intended for use in automotive applications unless specifically designated by Atmel as automotive-grade.