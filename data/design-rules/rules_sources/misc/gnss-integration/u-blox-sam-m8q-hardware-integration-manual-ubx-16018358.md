---
source: "u-blox SAM-M8Q Hardware Integration Manual UBX-16018358"
url: "https://content.u-blox.com/sites/default/files/SAM-M8Q_HardwareIntegrationManual_%28UBX-16018358%29.pdf"
format: "PDF 23pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 42498
---

SAM-M8Q
Easy-to-use u-blox M8 GNSS antenna module
Hardware integration manual
Abstract
This document describes the hardware features and specifications of the SAM-M8Q patch antenna
module, which features the u-blox M8 concurrent GNSS engine with reception of GPS, GLONASS,
Galileo and QZSS signals.
www.u-blox.com
UBX-16018358 - R07

SAM-M8Q - Hardware integration manual
Document information
Title SAM-M8Q
Subtitle Easy-to-use u-blox M8 GNSS antenna module
Document type Hardware integration manual
Document number UBX-16018358
Revision and date R07 28-May-2020
Document status Production information
Product status Corresponding content status
In Development / Objective Specification Target values. Revised and supplementary data will be published later.
Prototype
Engineering Sample Advance Information Data based on early testing. Revised and supplementary data will be published later.
Initial Production Early Production Information Data from product verification. Revised and supplementary data may be published later.
Mass Production / Production Information Document contains the final product specification.
End of Life
European Union regulatory compliance
SAM-M8Q smart antenna module complies with all relevant requirements for RED 2014/53/EU. The SAM-M8Q Declaration
of Conformity (DoC) is available at www.u-blox.com within Support > Product resources > Conformity Declaration.
This document applies to the following products:
Product name Type number Firmware version PCN reference
SAM-M8Q SAM-M8Q-0-10 ROM SPG 3.01 N/A
u-blox or third parties may hold intellectual property rights in the products, names, logos and designs included in this
document. Copying, reproduction, modification or disclosure to third parties of this document or any part thereof is only
permitted with the express written permission of u-blox.
The information contained herein is provided “as is” and u-blox assumes no liability for its use. No warranty, either express or
implied, is given, including but not limited to, with respect to the accuracy, correctness, reliability and fitness for a particular
purpose of the information. This document may be revised by u-blox at any time without notice. For the most recent
documents, visit www.u-blox.com.
Copyright © u-blox AG.
UBX-16018358 - R07 Page 2 of 23
Production information Document information

Contents
Document information ................................................................................................................................ 2
Contents .......................................................................................................................................................... 3
1 Hardware description ........................................................................................................................... 4
1.1 Overview ........................................................................................................................................................ 4
1.2 Configuration ............................................................................................................................................... 4
1.3 Connecting power ....................................................................................................................................... 4
1.4 Interfaces ...................................................................................................................................................... 5
1.4.1 UART ..................................................................................................................................................... 5
1.4.2 Display data channel (DDC) .............................................................................................................. 5
1.5 I/O pins ........................................................................................................................................................... 6
1.5.1 RESET_N: Reset .................................................................................................................................. 6
1.5.2 EXTINT: External interrupt ............................................................................................................... 6
1.5.3 TIMEPULSE.......................................................................................................................................... 6
1.5.4 SAFEBOOT_N ...................................................................................................................................... 7
1.6 Electromagnetic interference on I/O lines ............................................................................................. 7
2 Design ........................................................................................................................................................ 8
2.1 Pin description ............................................................................................................................................. 8
2.2 Minimal design............................................................................................................................................. 8
2.3 Footprint and paste mask ......................................................................................................................... 9
2.4 Antenna .......................................................................................................................................................10
2.5 Embedded antenna operation ................................................................................................................11
2.6 PCB layout suggestion .............................................................................................................................12
2.7 Layout design-in: Thermal management .............................................................................................12
3 Product handling ................................................................................................................................. 14
3.1 Packaging, shipping, storage and moisture preconditioning ..........................................................14
3.2 Soldering .....................................................................................................................................................14
3.3 EOS/ESD/EMI precautions ......................................................................................................................17
3.3.1 Electromagnetic interference (EMI) .............................................................................................18
3.4 Applications with cellular modules ........................................................................................................18
Appendix ....................................................................................................................................................... 21
A Glossary ................................................................................................................................................. 21
B Recommended parts ......................................................................................................................... 21
Related documents ................................................................................................................................... 22
Revision history .......................................................................................................................................... 22
Contact .......................................................................................................................................................... 23
UBX-16018358 - R07 Page 3 of 23
Production information Contents

1 Hardware description
1.1 Overview
The SAM‑M8Q module is a concurrent GNSS patch antenna module featuring the high performance
u-blox M8 GNSS engine with reception of GPS, GLONASS, Galileo and QZSS signals. Available in an
LGA package, it is easy to integrate and combines exceptional positioning performance with highly
flexible power, design, and connectivity options. SMT pads allow fully automated assembly with
standard pick and place and reflow-soldering equipment for cost-efficient, high-volume production
enabling short time-to-market.
☞ For product features see the SAM-M8Q Data sheet [1].
☞ To determine which u-blox product best meets your needs, see the product selector tables on the
u-blox website (www.u-blox.com).
1.2 Configuration
The configuration settings can be modified using UBX protocol configuration messages; see the u-
blox 8 / u-blox M8 Receiver Description including Protocol Specification [2]. The modified settings
remain effective until power-down or reset. If these settings have been stored in battery-backed RAM
(BBR), the modified configuration will be retained, as long as the backup battery supply is not
interrupted.
1.3 Connecting power
The SAM‑M8Q antenna module has three power supply pins: VCC, VCC_IO and V_BCKP.
VCC: Main supply voltage
The VCC pin provides the main supply voltage. During operation, the current drawn by the module can
vary by some orders of magnitude, especially if enabling low-power operation modes. For this reason,
it is important that the supply circuitry be able to support the peak power for a short time (see the
SAM-M8Q Data sheet [1] for specification).
☞ When switching from backup mode to normal operation or at start-up, the SAM‑M8Q antenna
module must charge its internal capacitors in the core domain. In certain situations, this can result
in a significant current draw. For low power applications using power save and backup modes, it is
important that the power supply or low ESR capacitors at the module input can deliver this
current/charge.
☞ Use a proper GND concept. Do not use any series resistors, ferrite beads or coils in the power line.
☞ The equipment must be supplied by an external limited power source in compliance with the clause
2.5 of the standard IEC 60950-1.
VCC_IO: IO supply voltage
VCC_IO from the host system supplies the digital I/Os. The wide range of VCC_IO allows seamless
interfacing to standard logic voltage levels independent of the VCC voltage level. In many applications,
VCC_IO is simply connected to the main supply voltage.
☞ Without a VCC_IO supply, the system will remain in reset state.
UBX-16018358 - R07 Contents Page 4 of 23
Production information

V_BCKP: Backup supply voltage
In case of a power failure on the module supply, V_BCKP supplies the real-time clock (RTC) and battery
backed RAM (BBR). Use of valid time and the GNSS orbit data at start-up improves the GNSS
performance, that is, hot starts and warm starts. If no backup battery is connected, the module
performs a cold start at power-up.
☞ Avoid high resistance on the V_BCKP line: During the switch from main supply to backup supply,
a short current adjustment peak can cause high voltage drop on the pin with possible
malfunctions.
☞ If no backup supply voltage is available, connect the V_BCKP pin to VCC_IO.
☞ As long a supply is connected to VCC_IO of SAM‑M8Q antenna module, the backup battery is
disconnected from the RTC and the BBR to avoid unnecessary battery drain (see Figure 1). In this
case, VCC_IO supplies power to the RTC and BBR. V_BCKP supplies the RTC and BBR in case
VCC_IO voltage goes below 1.4V.
Figure 1: Backup battery and voltage
1.4 Interfaces
1.4.1 UART
The SAM‑M8Q antenna module includes a universal asynchronous receiver transmitter (UART) serial
interface, RxD/TxD, which supports configurable baud rates, as specified in the SAM-M8Q Data sheet
[1]. The signal output and input level is 0 V to VCC_IO. An interface based on RS232 standard levels
(+/- 12 V) can be implemented using level shifters, such as Maxim MAX3232. Hardware handshake
signals and synchronous operation are not supported.
1.4.2 Display data channel (DDC)
An I2C-compatible display data channel (DDC) interface is available with SAM‑M8Q antenna modules
for serial communication with an external host CPU. The interface only supports operation in slave
mode (master mode is not supported). The DDC protocol and electrical interface are fully compatible
with the Fast-Mode of the I2C industry standard. DDC pins SDA and SCL have internal pull-up
resistors to VCC_IO.
For more information about the DDC implementation, see the u-blox 8 / u-blox M8 Receiver
Description including Protocol Specification [2]. For bandwidth information, see the SAM-M8Q Data
sheet [1]. For timing parameters, consult the I2C-bus specification [6].
☞ The SAM-M8Q DDC interface supports serial communication with u-blox cellular modules. See the
specification of the applicable cellular module to confirm compatibility.
UBX-16018358 - R07 Contents Page 5 of 23

TX_READY
The TX_READY function is used to indicate when the receiver has data to transmit on DDC interface.
A listener can wait on the TX_READY signal instead of polling the DDC interfaces. The UBX-CFG-PRT
message lets you configure the polarity and the number of bytes in the buffer before the TX READY
signal goes active. The TX_READY function can be mapped to TXD (PIO 06). The TX_READY function
is disabled by default.
☞ The TX_READY functionality can be enabled and configured by AT commands sent to the u-blox
cellular module supporting the feature. For more information see the GPS Implementation and
Aiding Features in u-blox wireless modules [7].
1.5 I/O pins
1.5.1 RESET_N: Reset
Driving RESET_N low activates a hardware reset of the system. Use this pin only to reset the module.
Do not use RESET_N to turn the module on and off, since the reset state increases power
consumption. The SAM-M8Q RESET_N pin is for input only.
☞ The RTC time is also reset (but not BBR). This means that the hot start performance will be
degraded after a reset.
☞ No additional capacitance should be added at RESET_N pin to GND (otherwise it could cause a
reset at startup).
1.5.2 EXTINT: External interrupt
EXTINT is an external interrupt pin with fixed input voltage thresholds with respect to VCC_IO (see
the SAM-M8Q Data sheet [1] for more information). It can be used for wake-up functions in power
save mode on and for aiding. Leave open if unused, function is disabled by default.
If EXTINT is not used for an external interrupt function, the pin can be used as a generic PIO (PIO13).
The PIO13 can be configured to function, for example, as an output pin for the TXD Ready feature to
indicate that the receiver has data to transmit. For further information, see u-blox 8 / u-blox M8
Receiver Description including Protocol Specification [2].
Power control
The power control feature allows overriding the automatic active/inactive cycle of power save mode.
The state of the receiver can be controlled through the EXTINT pin. The receiver can also be forced
OFF using EXTINT when power save mode is not active.
Frequency aiding
The EXTINT pin can be used to supply time or frequency aiding data to the receiver.
For time aiding, hardware time synchronization can be achieved by connecting an accurate time pulse
to the EXTINT pin.
Frequency aiding can be implemented by connecting a periodic rectangular signal with a frequency up
to 500 kHz and arbitrary duty cycle (low/high phase duration must not be shorter than 50 ns) to the
EXTINT pin. Provide the applied frequency value to the receiver using UBX messages.
1.5.3 TIMEPULSE
A configurable time pulse signal is available with SAM‑M8Q antenna module. By default, the time
pulse signal is configured to one pulse per second. For more information see the u-blox 8 / u-blox M8
Receiver Description including Protocol Specification [2].
UBX-16018358 - R07 Contents Page 6 of 23

1.5.4 SAFEBOOT_N
The SAFEBOOT_N pin is for future service, updates and reconfiguration.
1.6 Electromagnetic interference on I/O lines
Any I/O signal line with a length greater than approximately 3 mm can act as an antenna and may pick
up arbitrary RF signals transferring them as noise into the GNSS receiver. This specifically applies to
unshielded lines, in which the corresponding GND layer is remote or missing entirely, and lines close
to the edges of the printed circuit board.
If, for example, a cellular signal radiates into an unshielded high-impedance line, it is possible to
generate noise in the order of volts and not only distort receiver operation but also damage it
permanently.
On the other hand, noise generated at the I/O pins will emit from unshielded I/O lines. Receiver
performance may be degraded when this noise is coupled into the GNSS antenna (see Figure 11).
To avoid interference by improperly shielded lines, it is recommended to use resistors (for example,
R>20 ), ferrite beads (for example, BLM15HD102SN1) or inductors (for example, LQG15HS47NJ02)
on the I/O lines in series. Choose these components with care because they also affect the signal rise
times.
Figure 2 shows an example of EMI protection measures on the RXD/TXD line using a ferrite bead. More
information can be found in section 3.3.
Figure 2: EMI precautions
UBX-16018358 - R07 Contents Page 7 of 23

2 Design
2.1 Pin description
Function Pin No. I/O Description Remarks
Power VCC 17 Main supply Provide clean and stable supply (low impedance, < 0.2
Ohms).
GND 1, 4, 5, 6, Ground Assure a good GND connection to all GND pins of the
10, 11, 15, module.
16, 20
VCC_IO 2 VCC_IO IO supply voltage. Must always be supplied. Usually connect
to VCC pin 17.
V_BCKP 3 Backup supply It is recommended to connect a backup supply voltage to
V_BCKP to enable warm- and hot start features on the
positioning module. Otherwise, connect to VCC_IO.
UART TXD 13 O Serial port Can be configured as TX_Ready for DDC interface. Leave
open if not used.
RXD 14 I Serial port Leave open if not used.
DDC SCL 12 I Serial port Leave open if not used.
SDA 9 I/O Serial port Leave open if not used.
System RESET_N 18 I Reset (Active Leave open if not used. Do not drive high. Do not connect a
Low) capacitor at this pin.
TIMEPULSE 7 O 1PPS Configurable timepulse signal (one pulse per second by
default). Leave open if not used.
EXTINT / 19 I Ext. interrupt Leave open if not used. The pin can also be used as a
PIO13 generic PIO (PIO13).
SAFEBOOT_N 8 I Leave open.
Table 1: SAM-M8Q pinout
2.2 Minimal design
This is a minimal setup for a SAM-M8Q GNSS antenna module:
Figure 3: SAM-M8Q GNSS patch antenna design
UBX-16018358 - R07 Contents Page 8 of 23

2.3 Footprint and paste mask
The suggested solder mask openings are the same as the pad layout.
☞ Be sure to comply with special PCB layout design rules to ensure proper embedded antenna
operation when the customer PCB is used as part of antenna. This requires solid ground plane
around the module, see section 2.6 for PCB layout suggestions.
Footprint
Figure 4: SAM-M8Q footprint
Symbol Typical [mm]
A 15.50
B 7.60
C 3.80
D R1.00
E 11.00
F 6.30
H 1.80
I 1.50
J 13.20
Table 2: SAM-M8Q footprint dimensions
UBX-16018358 - R07 Contents Page 9 of 23

Paste mask
 Stencil thickness: 120 µm
 Orange: Pad
 Grey: stencil opening
Figure 5: Suggested pad layout and occupied area, top view
Figure 6: Paste mask detail for each pad
2.4 Antenna
SAM-M8Q GNSS patch antenna module is designed with an integrated GPS/Galileo/GLONASS patch
antenna.
Antenna input
The module has an embedded GNSS patch antenna and a SAW band-pass filter before LNA, which
provides excellent protection against out-of-band GNSS blocking caused by possible near-by wireless
transmitters. The signal is further amplified by the internal low noise amplifier (LNA) inside u-blox’s
UBX-M8030 GNSS chip.
☞ Be sure to comply with special PCB layout design rules to ensure proper embedded antenna
operation when the customer PCB is used as part of antenna. This requires solid ground plane
around the module, see section 2.6 for PCB layout suggestions.
UBX-16018358 - R07 Contents Page 10 of 23

2.5 Embedded antenna operation
The embedded GPS/Galileo/GLONASS patch antenna provides optimal performance in the middle of
a 50 x 50 mm ground plane.
Figure 7: 1.575 GHz typical free space radiation patterns
Place any tall nearby components (h > 3 mm) at least 10 mm away from the SAM-M8Q module. An
enclosure or plastic cover should have a minimum distance of 5 mm to the antenna.
Placement near a human body (or any biological tissue) can be acceptable by keeping a minimum
distance of 10 mm between motherboard and the body. With smaller distances to the body, the
radiation efficiency of the antenna will start to reduce due to signal losses in biological tissue.
UBX-16018358 - R07 Contents Page 11 of 23

2.6 PCB layout suggestion
For good performance, it is essential to have a proper layout and placement.
Figure 8: Layout recommendation (top layer)
SAM‑M8Q GNSS patch antenna module is intended to be placed in the middle of 50 x 50 mm GND
size board, but a larger or a smaller ground plane can also be used. When using a smaller than 40 x 40
mm ground plane, the performance may decrease significantly.
Some important recommendations:
 Easy to connect, but make sure all noisy lines / components are shielded or on inner layers.
 Do not place any noisy parts close to SAM-M8Q, place them as far away as possible or on other
side of the PCB.
 It is recommended not to place anything closer than 1 cm to each edge of SAM-M8Q.
 Performance decreases significantly if GND size is smaller than 40 x 40 mm.
 Use at least one layer for solid GND plane, preferably the layer SAM-M8Q is placed on.
 Use a solid GND plane under SAM-M8Q, which forms the shield. No signal traces are allowed below
SAM-M8Q.
 Route signal traces away from the module on top layer.
 When necessary, allow signal swap from top to bottom layer clearly away from the module, > 20
mm.
 Use copper pour ground planes on the top and bottom layers; use multiple GND net via holes to tie
separate ground plane areas tightly together.
2.7 Layout design-in: Thermal management
During design-in do not place the module near sources of heating or cooling. The receiver oscillator is
sensitive to sudden changes in ambient temperature which can adversely impact satellite signal
tracking. Sources can include co-located power devices, cooling fans or thermal conduction via the
PCB. Take into account the following questions when designing in the module.
UBX-16018358 - R07 Contents Page 12 of 23

 Is the receiver placed away from heat sources?
 Is the receiver placed away from air-cooling sources?
 Is the receiver shielded by a cover/case to prevent the effects of air currents and rapid
environmental temperature changes?
⚠ High temperature drift and air vents can affect the GNSS performance. For best performance,
avoid high temperature drift and air vents near the module.
UBX-16018358 - R07 Contents Page 13 of 23

3 Product handling
3.1 Packaging, shipping, storage and moisture preconditioning
For information pertaining to reels and tapes, moisture sensitivity levels (MSL), shipment and storage
information, as well as drying for preconditioning see the SAM-M8Q Data sheet [1].
Population of modules
☞ When populating the modules, make sure that the pick and place machine is aligned to the copper
pins of the module and not to the module edge.
3.2 Soldering
Soldering paste
Use of "no clean" soldering paste is highly recommended, as it does not require cleaning after the
soldering process has taken place. The paste in the example below meets these criteria.
Soldering paste: OM338 SAC405 / Nr.143714 (Cookson Electronics)
Alloy specification: Sn 95.5/ Ag 4/ Cu 0.5 (95.5% tin/ 4% silver/ 0.5% copper)
Melting temperature: 217 °C
Stencil thickness: 120 um
The final choice of the soldering paste depends on the approved manufacturing procedures.
The paste-mask geometry for applying soldering paste should meet the recommendations.
Reflow soldering
A convection-type soldering oven is highly recommended over the infrared-type radiation oven.
Convection-heated ovens allow precise control of the temperature, and all parts will heat up evenly,
regardless of material properties, thickness of components and surface color.
As a reference, see the "IPC-7530 Guidelines for temperature profiling for mass soldering (reflow
and wave) processes”, published in 2001.
Preheat phase
During the initial heating of component leads and balls, residual humidity will be dried out. Note that
this preheat phase will not replace prior baking procedures.
 Temperature rise rate: max. 3 °C/s. If the temperature rise is too rapid in the preheat phase it may
cause excessive slumping.
 Time: 60 - 120 s. If the preheat is insufficient, rather large solder balls tend to generate.
Conversely, if performed excessively, fine balls and large balls will be generated in clusters.
 End temperature: 150 - 200 °C. If the temperature is too low, non-melting tends to be caused in
areas containing large heat capacity.
Heating/ Reflow phase
The temperature rises above the liquidus temperature of 217 °C. Avoid a sudden rise in temperature
as the slump of the paste could become worse.
 Limit time above 217 °C liquidus temperature: 40 - 60 s
 Peak reflow temperature: 245 °C
UBX-16018358 - R07 Contents Page 14 of 23

Cooling phase
A controlled cooling avoids negative metallurgical effects of the solder (the solder becomes more
brittle) and possible mechanical tensions in the products. Controlled cooling helps to achieve bright
solder fillets with a good shape and low contact angle.
 Temperature fall rate: max 4 °C/s
☞ To avoid falling off, place the SAM‑M8Q antenna module on the topside of the motherboard during
soldering.
The final soldering temperature chosen at the factory depends on additional external factors like
choice of soldering paste, size, thickness and properties of the baseboard. Exceeding the maximum
soldering temperature in the recommended soldering profile may permanently damage the module.
Figure 9: Recommended soldering profile
☞ SAM-M8Q module must not be soldered with a damp heat process.
Optical inspection
After soldering the SAM‑M8Q antenna module, consider an optical inspection step to check whether:
 The module is properly aligned and centered over the pads.
Cleaning
In general, cleaning the populated modules is strongly discouraged. Residues underneath the
modules cannot be easily removed with a washing process.
 Cleaning with water will lead to capillary effects where water is absorbed into the gap between the
baseboard and the module. The combination of residues of soldering flux and encapsulated water
leads to short circuits or resistor-like interconnections between neighboring pads.
 Cleaning with alcohol or other organic solvents can result in soldering flux residues flooding into
the two housings, areas that are not accessible for post-wash inspections. The solvent will also
damage the sticker and the ink-jet printed text.
 Ultrasonic cleaning will permanently damage the module, in particular the quartz oscillators.
The best approach is to use a "no clean" soldering paste and eliminate the cleaning step after the
soldering.
UBX-16018358 - R07 Contents Page 15 of 23

Repeated reflow soldering
Only single reflow soldering process is recommended for boards populated with SAM‑M8Q GNSS
patch antenna module. To avoid upside down orientation during the second reflow cycle, do not
submit the SAM‑M8Q antenna module to two reflow cycles on a board populated with components
on both sides. In such a case, the modules should always be placed on the side of the board that is
submitted into the last reflow cycle. This is because of the risk of the module falling off due to the
significantly higher weight in relation to other components.
☞ Repeated reflow soldering processes and soldering the module upside down are not
recommended.
Wave soldering
Baseboards with combined through-hole technology (THT) components and surface-mount
technology (SMT) devices require wave soldering to solder the THT components. Only a single wave
soldering process is encouraged for boards populated with SAM‑M8Q antenna module.
Rework
The SAM-M8Q module can be unsoldered from the baseboard using a hot air gun. When using a hot
air gun for unsoldering the module, a maximum of one reflow cycle is allowed. In general, we do not
recommend using a hot air gun because this is an uncontrolled process and might damage the
module.
⚠ Attention: use of a hot air gun can lead to overheating and severely damage the module. Always
avoid overheating the module.
After the module is removed, clean the pads before placing and hand soldering a new module.
⚠ Never attempt a rework on the module itself, for example, replacing individual components. Such
actions immediately terminate the warranty.
Conformal coating
Certain applications employ a conformal coating of the PCB using HumiSeal® or other related coating
products. These materials affect the HF properties of the GNSS patch antenna module.
☞ Conformal coating of the module will void the warranty.
Casting
These materials affect the HF properties of the GNSS patch antenna including resonant frequency
shifts and are not suggested with SAM-M8Q.
☞ Casting will void the warranty.
Use of ultrasonic processes
Some components on the SAM-M8Q module is sensitive to ultrasonic waves. Use of any ultrasonic
processes (cleaning, welding, and so on) may cause damage to the GNSS receiver.
☞ u-blox offers no warranty against damages to the SAM‑M8Q antenna module caused by any
ultrasonic processes.
Oxidation of patch antenna
The patch antenna is metalized by silver paste and thus tends to oxidize and changes color. This is
normal and is not a case for warranty.
UBX-16018358 - R07 Contents Page 16 of 23

3.3 EOS/ESD/EMI precautions
When integrating GNSS positioning modules into wireless systems, consider electromagnetic and
voltage susceptibility issues carefully. Wireless systems include components that can produce
electrical overstress (EOS) and electro-magnetic interference (EMI). CMOS devices are more sensitive
to such influences because their failure mechanism is defined by the applied voltage, whereas bipolar
semiconductors are more susceptible to thermal overstress. The following design guidelines are
provided to help in designing robust yet cost-effective solutions.
⚠ To avoid overstress damage during production or in the field it is essential to observe strict
EOS/ESD/EMI handling and protection measures.
⚠ To prevent overstress damage at the RF_IN of your receiver, never exceed the maximum input
power (see the SAM-M8Q Data sheet [1]).
Electrostatic discharge (ESD)
Electrostatic discharge (ESD) is the sudden and momentary electric current that flows
between two objects at different electrical potentials caused by direct contact or
induced by an electrostatic field. The term is usually used in the electronics and other
industries to describe momentary unwanted currents that may cause damage to
electronic equipment.
ESD handling precautions
ESD prevention is based on establishing an electrostatic protective area (EPA). The EPA can be a
small working station or a large manufacturing area. The main principle of an EPA is that there are no
highly charging materials near ESD-sensitive electronics, all conductive materials are grounded,
workers are grounded, and charge build-up on ESD-sensitive electronics is prevented. International
standards are used to define typical EPA and can be obtained, for example, from International
Electrotechnical Commission (IEC) or American National Standards Institute (ANSI).
GNSS positioning modules are sensitive to ESD and require special precautions when handling.
Exercise particular care when handling patch antennas, due to the risk of electrostatic charges. In
addition to standard ESD safety practices, take the following measures into account whenever
handling the receiver.
 Unless there is a galvanic coupling between the local GND (i.e.
the work table) and the PCB GND, the first point of contact
when handling the PCB must always be between the local GND
and PCB GND.
 Before mounting an antenna patch, connect ground of the
device
 When handling the RF pin, do not come into contact with any
charged capacitors and be careful when contacting materials
that can develop charges (e.g. patch antenna ~10 pF, coax cable
~50 - 80 pF/m, soldering iron).
 To prevent electrostatic discharge through the RF input, do not
touch any exposed antenna area. If there is any risk that such
exposed antenna area is touched in a non-ESD protected work
area, implement proper ESD protection measures in the design.
 When soldering RF connectors and patch antennas to the
receiver’s RF pin, make sure to use an ESD safe soldering iron
(tip).
UBX-16018358 - R07 Contents Page 17 of 23

⚠ Failure to observe these precautions can result in severe damage to the GNSS module!
⚠ GNSS positioning modules are sensitive to electrostatic discharge (ESD). Special precautions are
required when handling.
Electrical overstress (EOS)
Electrical overstress (EOS) usually describes situations when the maximum input power exceeds the
maximum specified ratings. EOS failure can happen if RF emitters are close to a GNSS receiver or its
antenna. EOS causes damage to the chip structures. If EOS damages the RF_IN, it is hard to
determine whether the chip structures have been damaged by ESD or EOS.
EOS protection measures
☞ For designs with GNSS positioning modules and wireless (for example, GSM/GPRS) transceivers
in close proximity, ensure sufficient isolation between the wireless and GNSS antennas. If wireless
power output causes the specified maximum power input at the GNSS RF_IN to be exceeded,
employ EOS protection measures to prevent overstress damage.
3.3.1 Electromagnetic interference (EMI)
Electromagnetic interference (EMI) is the addition or coupling of energy originating from any RF
emitting device. This can cause a spontaneous reset of the GNSS receiver or result in unstable
performance. Any unshielded line or segment (>3 mm) connected to the GNSS receiver can effectively
act as antenna and lead to EMI disturbances or damage.
The following elements are critical regarding EMI:
 Unshielded connectors (such as pin rows)
 Weakly shielded lines on PCB (for example, on top or bottom layer and especially at the border of
a PCB)
 Weak GND concept (for example, small and/or long ground line connections)
EMI protection measures are recommended when RF emitting devices are near the GNSS receiver. To
minimize the effect of EMI a robust grounding concept is essential. To achieve electromagnetic
robustness follow the standard EMI suppression techniques.
http://www.murata.com/products/emc/knowhow/index.html
http://www.murata.com/products/emc/knowhow/pdf/4to5e.pdf
Improved EMI protection can be achieved by inserting a resistor (for example, R > 20 ), or, better yet,
a ferrite bead (BLM15HD102SN1) or an inductor (LQG15HS47NJ02), into any unshielded PCB lines
connected to the GNSS receiver. Place the resistor as close to the GNSS receiver pin as possible.
Alternatively, feed-through capacitors with good GND connection can be used to protect against EMI.
A selection of feed-through capacitors is listed in Table 4.
Intended use
☞ In order to mitigate any performance degradation of a radio equipment under EMC disturbance,
system integration shall adopt appropriate EMC design practice and not contain cables over three
meters on signal and supply ports.
3.4 Applications with cellular modules
GSM terminals transmit power levels up to 2 W (+33 dBm) peak, 3G and LTE up to 250 mW
continuous. Consult the corresponding product data sheet for the absolute maximum power input at
the GNSS receiver.
UBX-16018358 - R07 Contents Page 18 of 23

☞ See the GPS Implementation and Aiding Features in u-blox wireless modules [7].
Isolation between GNSS and cellular antenna
In a handheld type design, an isolation of approximately 20 dB can be reached with careful placement
of the antennas. If such isolation cannot be achieved, for example, in the case of an integrated cellular
/GNSS antenna, an additional input filter is needed on the GNSS side to block the high energy emitted
by the cellular transmitter. Examples of these kinds of filters would be the SAW Filters from Epcos
(B9444 or B7839) or Murata.
Increasing interference immunity
Interference signals come from in-band and out-band frequency sources.
In-band interference
With in-band interference, the signal frequency is very close to the GNSS constellation frequency
used, for example, GPS frequency of 1575 MHz (see Figure 10 ). Such interference signals are typically
caused by harmonics from displays, micro-controller, bus systems, and so on.
GPS Carrier
Power [dBm]
Jamming 1575.4 MHz GPS
signal signals
00
Jammin
g signal
GGPPSS iinnppuutt ffiilltteerr
-110
cchhaarraacctteerriissttiiccss
Frequency [MHz]
11552255 11555500 11557755 11660000 11662255
Figure 10: In-band interference signals
Figure 11: In-band interference sources
Measures against in-band interference include:
 Maintaining a good grounding concept in the design
 Shielding
 Layout optimization
 Filtering
 Placement of the GNSS antenna
 Adding a CDMA, cellular, WCDMA band pass filter before handset antenna
UBX-16018358 - R07 Contents Page 19 of 23

Out-band interference
Out-band interference is caused by signal frequencies that are different from the GNSS carrier (see
Figure 12). The main sources are wireless communication systems such as cellular, CDMA, WCDMA,
Wi-Fi, BT.
Figure 12: Out-band interference signals
Measures against out-band interference include maintaining a good grounding concept in the design
and keep enough distance in between the antennas.
☞ See the GPS Implementation and Aiding Features in u-blox wireless modules [7].
UBX-16018358 - R07 Contents Page 20 of 23

Appendix
A Glossary
Abbreviation Definition
ANSI American National Standards Institute
CDMA Code Division Multiple Access
EMC Electromagnetic compatibility
EMI Electromagnetic interference
EOS Electrical Overstress
EPA Electrostatic Protective Area
ESD Electrostatic discharge
Galileo European navigation system
GLONASS Russian satellite system
GND Ground
GNSS Global Navigation Satellite System
GPS Global Positioning System
GSM Global System for Mobile Communications
IEC International Electrotechnical Commission
PCB Printed circuit board
QZSS Quasi-Zenith Satellite System
Table 3: Explanation of the abbreviations and terms used
B Recommended parts
Recommended parts are selected on data sheet basis only. Other components may also be used.
Part Manufacturer Part ID Remarks Parameters to consider
Ferrite Murata BLM15HD102SN1 FB High IZI at fGSM
bead
Feed- Murata NFL18SP157X1A3 Monolithic type For data signals, 34 pF load
through capacitance
capacitor
NFA18SL307V1A45 Array type For data signals, 4 circuits in 1
for signal package
Feed- Murata NFM18PC …. 0603 2A Rs < 0.5 
through NFM21P…. 0805 4A
capacitor
Table 4: Recommended parts
UBX-16018358 - R07 Appendix Page 21 of 23

Related documents
[1] SAM M8Q Data sheet, UBX-16012619
[2] u-blox 8 / u-blox M8 Receiver Description Including Protocol Specification, UBX-13003221
[3] GNSS FW3.01 Release Notes (Public version), UBX-16000319
[4] GPS Antenna Application Note, GPS-X-08014
[5] GPS Compendium, GPS-X-02007
[6] I2C-bus specification, Rev. 6 - 4 April 2014,
http://www.nxp.com/documents/user_manual/UM10204.pdf
[7] GNSS Implementation in Cellular Modules, UBX-13001849
☞ For regular updates to u-blox documentation and to receive product change notifications, register
on our homepage (www.u-blox.com).
Revision history
Revision Date Name Comments
R01 25-Nov-2016 mdur Initial release
R02 mdur Added the preface page and the document status (Objective Specification),
22-Dec-2016
minor update in Table 2.
R03 14-Feb-2017 mdur Advance Information
R04 13-Mar-2017 mdur Early Production Information
R05 24-Oct-2017 mdur Production Information, added information on RED DoC in European Union
regulatory compliance (page 2), added Intended use statement in section
3.3.1 Electromagnetic interference (EMI)
R06 29-Jan-2019 mdur Added information on EXTINT pin usage as generic PIO13 in Section 1.5.2
and Table 1: SAM-M8Q pinout
R07 28-May-2020 mala Added section 2.7 Layout design-in: Thermal management. Editorial
changes to reflect the latest style guide updates.
UBX-16018358 - R07 Related documents Page 22 of 23

Contact
For complete contact information, visit us at www.u-blox.com.
u-blox Offices
North, Central and South America Headquarters Asia, Australia, Pacific
Europe, Middle East, Africa
u-blox America, Inc. u-blox Singapore Pte. Ltd.
Phone: +1 703 483 3180 u-blox AG Phone: +65 6734 3811
E-mail: info_us@u-blox.com Phone: +41 44 722 74 44 E-mail: info_ap@u-blox.com
E-mail: info@u-blox.com Support: support_ap@u-blox.com
Regional Office West Coast:
Support: support@u-blox.com
Phone: +1 408 573 3640 Regional Office Australia:
E-mail: info_us@u-blox.com Phone: +61 2 8448 2016
E-mail: info_anz@u-blox.com
Technical Support:
Support: support_ap@u-blox.com
Phone: +1 703 483 3185
E-mail: support@u-blox.com Regional Office China (Beijing):
Phone: +86 10 68 133 545
E-mail: info_cn@u-blox.com
Support: support_cn@u-blox.com
Regional Office China (Chongqing):
Phone: +86 23 6815 1588
Regional Office China (Shanghai):
Phone: +86 21 6090 4832
Regional Office China (Shenzhen):
Phone: +86 755 8627 1083
Regional Office India:
Phone: +91 80 405 092 00
E-mail: info_in@u-blox.com
Support: support_in@u-blox.com
Regional Office Japan (Osaka):
Phone: +81 6 6941 3660
E-mail: info_jp@u-blox.com
Support: support_jp@u-blox.com
Regional Office Japan (Tokyo):
Phone: +81 3 5775 3850
E-mail: info_jp@u-blox.com
Support: support_jp@u-blox.com
Regional Office Korea:
Phone: +82 2 542 0861
E-mail: info_kr@u-blox.com
Support: support_kr@u-blox.com
Regional Office Taiwan:
Phone: +886 2 2657 1090
E-mail: info_tw@u-blox.com
Support: support_tw@u-blox.com
UBX-16018358 - R07 Contact Page 23 of 23