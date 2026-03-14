---
source: "TI SNLA079 (AN-1469) -- PHYTER Design and Layout Guide"
url: "https://www.ti.com/lit/pdf/snla079"
format: "PDF 16pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 28749
---

Application Report

AN-1469 PHYTER Design & Layout Guide
.....................................................................................................................................................
ABSTRACT
This application report describes PHYTER™ design and layout guidelines.
Contents
1 Introduction .................................................................................................................. 3
2 MDI (TP/CAT-V) Connections ............................................................................................. 4
2.1 PCB Layout Considerations ...................................................................................... 5
2.2 Calculating Impedance ............................................................................................ 6
2.3 RJ-45 Connections ................................................................................................ 6
2.4 MDI EMI Recommendations ...................................................................................... 7
3 Fiber Optic Implementations ............................................................................................... 7
4 Power Supply Filtering ..................................................................................................... 7
4.1 Power Feedback Supply .......................................................................................... 8
5 MAC Interface (MII/RMII) .................................................................................................. 8
5.1 Termination Requirement ......................................................................................... 8
5.2 Recommended Maximum Trace Length ........................................................................ 8
6 Clock Requirements ........................................................................................................ 9
6.1 External Oscillator Clock Source ................................................................................. 9
6.2 Crystal Clock Source .............................................................................................. 9
7 LED and non-LED Strap Pins ............................................................................................ 10
8 PCB Layer Stacking ....................................................................................................... 11
9 Unused Pins/Reserved Pins ............................................................................................. 12
10 Component Selection ..................................................................................................... 12
10.1 Oscillator or Crystal .............................................................................................. 12
10.2 Magnetics .......................................................................................................... 13
11 Reset Operation ........................................................................................................... 14
11.1 Hardware Reset .................................................................................................. 14
11.2 Software Reset ................................................................................................... 14
12 Other Applicable Documents ............................................................................................. 15
List of Figures
1 Typical Application.......................................................................................................... 4
2 10/100 Mb/s Twisted Pair Interface....................................................................................... 4
3 Differential Signal Pair - Stubs ............................................................................................ 5
4 Differential Signal Pair-Plane Crossing .................................................................................. 5
5 Microstrip Impedance - Single-Ended.................................................................................... 6
6 Stripline Impedance - Single-Ended...................................................................................... 6
7 Microstrip Impedance - Differential ....................................................................................... 6
8 Stripline Impedance - Differential ......................................................................................... 6
9 Vdd Bypass Layout ......................................................................................................... 7
10 Power Feedback Connection.............................................................................................. 8
11 Oscillator Circuit............................................................................................................. 9
PHYTER is a trademark of Texas Instruments.
All other trademarks are the property of their respective owners.

12 Crystal Oscillator Circuit .................................................................................................. 10
13 AN Strapping and LED Loading Example.............................................................................. 10
14 PCB Stripline Layer Stacking ............................................................................................ 11
15 Alternative PCB Stripline Layer Stacking............................................................................... 12
List of Tables
1 25 MHz Crystal Oscillator Requirements............................................................................... 13
2 25 MHz Crystal Requirements........................................................................................... 13
3 Recommended Crystal Oscillators ...................................................................................... 13
4 Magnetics Requirements ................................................................................................. 14
5 Recommended Magnetics................................................................................................ 14

1 Introduction
The PHYTER family of products are robust, full featured, low power, 10/100 Physical Layer devices. With
cable length performance far exceeding IEEE specifications and features that provide lower cost solutions,
for both 10BASE-T and 100BASE-TX Ethernet protocols, the devices ensure compatibility and inter-
operability with other standards based Ethernet products in these applications:
• High End Peripheral Devices
• Industrial Controls
• Factory Automation
• General Embedded Applications
Use of this application report, in conjunction with the product datasheets, and reference designs, will help
ensure issue-free system products.
Topics covered include:
• MDI (Twisted Pair/CAT-V) Connections
• Power Supply Decoupling
• MAC Interface
• Clock Connections
• LED Connections
• Configuration (Strap) Connections
• Unused/Reserved Pins
• PCB Layers (stack-up)
• Component Selection/Recommendations
Product Applicability:
DP83640 DP83849C DP83848C
DP83630 DP83849I DP83848I
DP83620 DP83849ID DP83848YB
DP83849IF DP83848VYB
DP83848M
DP83848T
DP83848H
DP83848J
DP83848K
DP83848Q-Q1

Figure 1. Typical Application
2 MDI (TP/CAT-V) Connections
The network or Medium Dependent Interface (MDI) connection is via the transmit (TD+ & TD-) and receive
(RD+ & RD-) differential pair pins. These connect to a termination network, then to 1:1 magnetics
(transformer) and an RJ-45. For space savings the magnetics and RJ-45 may be a single integrated
component. A standard CAT-V Ethernet cable is then used to connect to the rest of the network. Figure 2
shows the recommended 10/100 Mb/s twisted pair interface circuit. PHYTER family termination and center
tap connections are different from previous Ethernet devices.
In certain applications, an alternate method of connecting the PHYTER component to another device may
be desirable. Specifically, designs for applications where a backplane is the choice of media between
devices. In these applications DC isolation must be maintained, while providing an AC signal coupling
path. This can be accomplished using capacitors for the connection instead of the magnetics. Specifics of
this method of connection are provided in the AN-1519 DP83848 PHYTER® Transformerless Ethernet
Operation Application Report (SNLA088).
Figure 2. 10/100 Mb/s Twisted Pair Interface

2.1 PCB Layout Considerations
• Place the 49.9 ohm,1% resistors, and 0.1μF decoupling capacitor, near the PHYTER TD+/- and RD+/-
pins and via directly to the Vdd plane.
• Stubs should be avoided on all signal traces, especially the differential signal pairs. See Figure 3.
• Within the pairs (for example, TD+ and TD-) the trace lengths should be run parallel to each other and
matched in length. Matched lengths minimize delay differences, avoiding an increase in common mode
noise and increased EMI. See Figure 3.
• Ideally there should be no crossover or via on the signal paths. Vias present impedance discontinuities
and should be minimized. Route an entire trace pair on a single layer if possible.
Does Not Maintain Parallelism
Avoid
Stubs
Ground or Power Plane
Figure 3. Differential Signal Pair - Stubs
• PCB trace lengths should be kept as short as possible.
• Signal traces should not be run such that they cross a plane split. See Figure 4. A signal crossing a
plane split may cause unpredictable return path currents and would likely impact signal quality as well,
potentially creating EMI problems.
Figure 4. Differential Signal Pair-Plane Crossing
• MDI signal traces should have 50 ohm to ground or 100 ohm differential controlled impedance. Many
tools are available online to calculate this.

2.2 Calculating Impedance
The following equations can be used to calculate the differential impedance of the board.
For microstrip traces, a solid ground plane is needed under the signal traces. The ground plane helps
keep the EMI localized and the trace impedance continuous. Since stripline traces are typically
sandwiched between the ground/supply planes, they have the advantage of lower EMI radiation and less
noise coupling. The trade off of using strip line is lower propagation speed.
Microstrip Impedance - Single-Ended Stripline Impedance - Single-Ended
W = Width of the trace H = Height of dielectric above the
return plane T = Trace thickness Er = Relative permittivity of
the dielectric
return plane T = Trace thickness Er = Relative permittivity of
the dielectric
Figure 5. Microstrip Impedance - Single-Ended Figure 6. Stripline Impedance - Single-Ended
Microstrip Impedance - Differential Stripline Impedance - Differential
return plane T = Trace thickness S = Space between traces
Er = Relative permittivity of the dielectric W = Width of the trace H = Height of dielectric above the
return plane T = Trace thickness S = space between traces
Er = Relative permittivity of the dielectric
Figure 7. Microstrip Impedance - Differential Figure 8. Stripline Impedance - Differential
2.3 RJ-45 Connections
The transformer used in the MDI connection provides DC isolation between local circuitry and the network
cable. The center tap of the isolated winding has “Bob Smith” termination through a 75 ohm resistor and a
1000 pF cap to chassis ground. The termination capacitor should be rated to a voltage of at least 2kV.
Note: “Bob-Smith termination does not apply for Power Over Ethernet (PoE) applications.
“Bob-Smith” termination is used to reduce noise resulting from common mode current flows, as well as
reduce susceptibility to any noise from unused wire pairs on the RJ-45.

2.4 MDI EMI Recommendations
The following recommendations are provided to help improve EMI performance:
• Use a metal shielded RJ-45 connector, and connect the shield to chassis ground.
• Use magnetics with integrated common mode choking devices.
• Do not overlap the circuit and chassis ground planes, keep them isolated. Connect chassis ground and
system ground together using two size 1206 zero ohm resistors across the void between the ground
planes on either side of the RJ-45. These resistors can be removed or replaced with alternative
components (that is, capacitors or EMI beads) during system level certification testing if necessary.
3 Fiber Optic Implementations
Some PHYTER family products include the ability to utilize the MDI interface to connect to fiber optic
transceivers. Individual device datasheets describe how to terminate the MDI signals when enabling Fiber
Mode in these devices.
Although the termination requirements for fiber mode operation differ from the termination requirements of
twisted pair operation, the characteristic impedance of the terminations and the associated signal traces
are the same. Therefore, the same MDI signal routing recommendations described in Section 2.1 of this
document apply to Fiber enabled systems as well.
4 Power Supply Filtering
The device Vdd supply pins should be bypassed with low impedance 0.1 µF surface mount capacitors. To
reduce EMI, the capacitors should be places as close as possible to the component Vdd supply pins,
preferably between the supply pins and the vias connecting to the power plane. In some systems it may
be desirable to add 0 ohm resistors in series with supply pins, as the resistor pads provide flexibility if
adding EMI beads becomes necessary to meet system level certification testing requirements. (See
Figure 9.)
It is recommended the PCB have at least one solid ground plane and one solid Vdd plane to provide a low
impedance power source to the component. This also provides a low impedance return path for non-
differential digital MII and clock signals.
A 10.0 µF capacitor should also be placed near the PHY component for local bulk bypassing between the
Vdd and ground planes.
Vdd PHY
Component
Optional 0: Vdd
or Bead Pin
PCB
Via
0.1 PF
Ground Pin
PCB Via
Figure 9. Vdd Bypass Layout

4.1 Power Feedback Supply
Some PHYTER products utilize PCB traces to connect an internal regulator to core supply pins. On these
products, the PFBOUT pin should be tied to the PFBIN1 & 2 pins using as much PCB copper as possible.
A 10.0 µF tantalum capacitor in parallel with a 0.1 µF cap should be placed close to the PFBOUT pin, and
0.1 µF caps should be placed close to the PFBIN1 and PFBIN2 pins. (See Figure 10)
Figure 10. Power Feedback Connection
5 MAC Interface (MII/RMII)
The Media Independent Interface (MII) connects the PHYTER component to the Media Access Controller
(MAC). The MAC may in fact be a discrete device, integrated into a microprocessor, CPU or FPGA. On
the MII signals, the IEEE specification states the bus should be 68 ohm impedance.
For space critical designs, the PHYTER family of products also support Reduced MII (RMII). For additional
information on this mode of operation, refer to the AN-1405 DP83848 Single 10/100 Mb/s Ethernet
Transceiver Reduced Media Independent Interface (RMII) Mode Application Report (SNLA076).
5.1 Termination Requirement
To reduce digital signal energy, 50 ohm series termination resistors are recommended for all MII output
signals (including RXCLK, TXCLK, and RX Data signals.) Note that DP83849 and DP83640 products
provide integrated 50 ohm signal terminations, making external termination resistors unnecessary.
5.2 Recommended Maximum Trace Length
Although RMII and MII are synchronous bus architectures, there are a number of factors limiting signal
trace lengths. With a longer trace, the signal becomes more attenuated at the destination and thus more
susceptible to noise interference. Longer traces also act as antennas, and if run on the surface layer, can
increase EMI radiation. If a long trace is running near and adjacent to a noisy signal, the unwanted signals
could be coupled in as cross talk.
It is recommended to keep the signal trace lengths as short as possible. Ideally, keep the traces under 6
inches.
Trace length matching, to within 2.0 inches on the MII or RMII bus is also recommended. Significant
differences in the trace lengths can cause data timing issues.
As with any high speed data signal, good design practices dictate that impedance should be maintained
and stubs should be avoided throughout the entire data path.

6 Clock Requirements
PHYTER family products support either an external CMOS level oscillator source or a crystal resonator
device. The X1 pin is the clock input, requiring either 25 or 50 MHz depending on the MII mode used.
In MII mode (or RMII master mode in some products) either a 25 MHz crystal or 25 MHz oscillator may be
used. For all PHYTER family products, the use of standard RMII mode (not RMII master mode) requires
the use of a 50 MHz oscillator.
The input clock signal is also buffered and provided as an output signal on some PHYTER family
products.
6.1 External Oscillator Clock Source
If an oscillator is used, X1 should be tied to the clock source and X2 should be left floating. No series or
load termination is required from the clock source, but may prove beneficial in some circumstances.
For EMI purposes, it may be beneficial to include series termination to limit the energy sourced from the
oscillator. If series termination is used, the termination resistor should be placed as close to the oscillator
output as possible on the PCB.
For longer traces, series termination coupled with matched parallel termination to ground and matched
trace impedance may prove beneficial as well. If a parallel termination resistor is used, it should be placed
as closely as possible to the X1 pin.
Connections for using an oscillator are shown in Figure 11.
Specifications for CMOS oscillators are listed in Section 10.1 .
Figure 11. Oscillator Circuit
6.2 Crystal Clock Source
For MII mode (or RMII master mode on the DP83640), the recommended crystal to use is a 25 MHz,
parallel, 20 pF load crystal resonator. Figure 12 shows a typical circuit for a crystal resonator. The load
capacitor values will vary with the crystal vendors; check with the vendor for load recommendations.
Approximate load capacitor values can be calculated by:
2 × Crystal load spec - 7 pF = C (1)
L
The oscillator circuit is designed to drive a parallel resonance AT cut crystal with a minimum drive level of
100 mW and a maximum of 500 mW. If a crystal is specified for a lower drive level, a current limiting
resistor should be placed in series between X2 and the crystal.
As a starting point for evaluating an oscillator circuit, if the requirements for the crystal are not known, C
L1
and C should be set at 33 pF, and R should be set at 0 Ohms.
L2 1
Specifications for the crystal are listed in Section 10.1.

:
k
2 .2 Vdd :
011
,h g n iP O iH d e w o L /I D E L p p a rtS e v itc A
: : :
2 .2 2
2.
2 .2 :
011

Figure 12. Crystal Oscillator Circuit
7 LED and non-LED Strap Pins
PHYTER products support both conventional configuration strap input/output pins and multi-purpose Light
Emitting Diode (LED) I/O pins. The LED pins can display the status of Link, Speed, Activity, or the
presence of Collisions.
Many conventional strap input/output pins have high impedance (10k to 20k) default strap resistors
present internal to the device. In order to overdrive these internal strap resistors, it is recommended that
2.2k resistors be used for selecting non-default strap options.
Additionally, even though the internal strap resistors are adequate for configuring the device in most
applications, in some applications with noisy environments it is recommended that additional external 2.2k
straps be used to select default options as well.
With regard to multi-purpose LED I/O pins, in order to achieve dual input/output functionality, the active
state of each LED output driver is dependent on the input logic level sampled during power-up/reset. For
example, if a multifunction LED pin is resistively pulled low, then the corresponding output will be
configured as active high. Conversely, if an input is resistively pulled high, then the corresponding output
will be configured as active low.
Figure 13 illustrates examples of both conventional and multi-purpose LED pin strap configurations.
la n o itn e v n o C tu p tu O /tu p n I h g iH d e p p a rtS la n o itn e v n o C tu p tu O /tu p n I w o L d e p p a rtS n iP O /I D E L ,w o L d e p p a rtS h g iH e v itc A
Figure 13. AN Strapping and LED Loading Example

8 PCB Layer Stacking
To meet signal integrity and performance requirements, at minimum a four layer PCB is recommended for
implementing PHYTER components in end user systems. The following layer stack-ups are recommended
for four, six, and eight-layer boards, although other options are possible.
Figure 14. PCB Stripline Layer Stacking
Within a PCB it may be desirable to run traces using different methods, microstrip vs. stripline, depending
on the location of the signal on the PCB. For example, it may be desirable to change layer stacking where
an isolated chassis ground plane is used. Figure 15 illustrates alternative PCB stacking options.

Figure 15. Alternative PCB Stripline Layer Stacking
9 Unused Pins/Reserved Pins
The PHYTER family of products provide internal pull-ups or pull-downs on most pins. The datasheets for
the specific products detail which pins have internal pull-ups or pull-downs, and which pins require
external pull resistors.
Even though a device may have internal pull-up or pull-down resistors, a good practice is to terminate
unused CMOS inputs, rather than allowing them to float. Floating inputs could result in unstable
conditions.
In theory, CMOS inputs can be tied directly to Vdd or ground, minimizing component count and board
area. However, its considered a safer practice to pull an unused input pin high or low with a pull-up or pull-
down resistor. It is also possible to group together adjacent unused input pins, and as a group pull them
up or down using a single resistor.
10 Component Selection
Within a design, selection of certain components is critical. This is due to the device being designed to
specific criteria of critical parameters. These components include:
• Clock source - oscillator or crystal
• Magnetics
10.1 Oscillator or Crystal
The parametric specifications for utilizing an external oscillator are shown in Table 1.
The commonly used crystal is “AT cut” and fundamental frequency. This is the recommended type for
PHYTER components since AT cut exhibits the most frequency stability over a wide temperature range.
The requirements for 25 MHz crystals are listed Table 2.
In the case where multiple clock sources are needed, a high speed PLL clock distribution driver is
recommended. The drivers may be obtained from vendors such as Texas Instruments, Pericom, and
Integrated Device Technology. Please consult vendor for specifics.
Contact oscillator manufactures for latest information on part numbers and product specifications. All
oscillators and circuits should be thoroughly tested and validated before use in production.

Table 1. 25 MHz Crystal Oscillator Requirements
Parameter Min Typ Max Units Condition
Frequency - 25 / 50 - MHz
Frequency Stability - - ± 50 ppm 0°C to 70°C, 1 year aging, load change
Rise/Fall Time - - 6 ns 20 - 80%
Jitter (short term) - - 25 ps Cycle-to-cycle, driving 10 pF load
Jitter (long term) - - 200 ps Accumulative over 10 µs
Load Capacitance 15 - - pF
Symmetry 40 - 60 %
Logic 0 - - 10% VDD V VDD = 3.3 V nominal
Logic 1 90% VDD - - V VDD = 3.3 V nominal
Table 2. 25 MHz Crystal Requirements
Parameter Min Typ Max Units Condition
Frequency - 25 - MHz -
Frequency Tolerance - - ± 50 ppm 0°C to 70°C
Frequency Stability - - ± 50 ppm 1 year aging
Load Capacitance C 15 - 40 pF Total C including C1 and C2
L L
Table 3. Recommended Crystal Oscillators
Manufacturer Part Number
Vectron International 25 MHz 7.5 x 5 mm Crystal Oscillator
VCC1-B2B-25M000
Raltron Electronics Corporation 25 MHz 7.5 x 5 mm Crystal Oscillator
C04305L-25.000MHz
CTS Valpey Corporation
10.2 Magnetics
The magnetics have a large impact on the PHY performance as well. While several components are listed
below, others may be compatible following the requirements listed in Table 4. It is recommended that the
magnetics include both an isolation transformer and an integrated common mode choke to reduce EMI.
When doing the layout, do not run signals under the magnetics. This could cause unwanted noise
crosstalk. Likewise void the planes under discrete magnetics, this will help prevent common mode noise
coupling.
To save board space and reduce component count, an RJ-45 with integrated magnetics may be used.
Current recommended magnetics are listed in Table 5. Contact magnetics manufactures for latest part
numbers and product specifications. All magnetics should be thoroughly tested and validated before using
them in production. Other magnetics with comparable characteristics should operate equally well. For a
more complete list, visit the PHYTER web page at: www.ti.com.

Table 4. Magnetics Requirements
Parameter Typ Units Condition
Turn Ratio 1:1 - ± 2%
Insertion Loss -1 dB 1 - 100 MHz
Return Loss -16 dB 1 - 30 MHz
- 12 dB 30 - 60 MHz
- 10 dB 60 - 80 MHz
Differential to Common Rejection Ration - 30 dB 1 - 50 MHz
- 20 dB 50 - 150 MHz
Crosstalk - 35 dB 30 MHz
- 30 dB 60 MHz
Isolation 1,500 Vrms HPOT
Table 5. Recommended Magnetics
Manufacturer Part Number
Bel Fuse, Inc. S558-5999-U7 Typical Application
SI-60062-F Integrated
Pulse Electronics H1102 Typical Applications
H2019 POE Applications
J0011D21B Integrated
11 Reset Operation
PHYTER products include an internal power-on reset (POR) function and does not need to be explicitly
reset after power up, for normal operation. If required during normal operation, the device can be reset by
a hardware or a software reset.
11.1 Hardware Reset
A hardware reset is accomplished by applying a low pulse (TTL level), with a duration of at least 1 ms, to
the RESET_N. This will reset the device such that all registers will be re-initialized to default values and
the hardware configuration values will be re-latched into the device (similar to the power-up/reset
operation).
11.2 Software Reset
A software reset is accomplished by setting the reset bit (bit 15) of the Basic Mode Control Register
(BMCR). The period of time from setting the reset bit, to the time when software reset has concluded is
approximately 1 ms.
The software reset will reset the device such that all registers will be reset to default values and the
hardware configuration values will be maintained. Software driver code must wait 3 ms following a
software reset before allowing further serial MII (MDIO/MDC) communications with the device.

12 Other Applicable Documents
The following documents should be used in conjunction with this document, to assist in designing with
PHYTER products:
• DP83848C PHYTER Comm Temp Single Port 10/100Mb/s Ethernet Phy Layer Transceiver
(SNOSAT2)
• DP83848I Ind Temp Single Port 10/100 Mb/s Ethernet Phy Layer Transceiver (SNLS207)
• DP83848YB Extreme Temp Single Port 10/100 Mb/s Ethernet Phy Layer Transceiver (SNLS208)
• DP83848M PHYTER Mini - Commercial Temperature Single 10/100 Ethernet Transciver (SNLS227)
• DP83848T PHYTER Mini - Industrial Temp Single 10/100 Ethernet Transceiver (SNLS228)
• DP83848VYB PHYTER - Extended Temperature Single Port 10/100 Mb/s Ethernet Physical Layer X-
ceiver (SNLS266)
• DP83848J PHYTER Mini LS Commercial Temperature Single Port 10/100 Mb/s Ethernet Transceiver
(SNLS250)
• DP83848K PHYTER Mini LS Industrial Temperature Single Port 10/100 Ethernet Transceiver
(SNLS251)
• DP83848C/I/YB Schematic (SNLR019)
• DP83848C/I/YB Bill of Materials (SNLR020)
• DP83848M/T/H Schematic (SNLR015)
• DP83848M/T/H Bill of Materials (SNLR016)
• DP83848J/K Schematic (SNLR011)
• DP83848J/K Bill of Materials (SNLR012)
• DP83849C PHYTER DUAL Commercial Temperature Dual Port 10/100 Mb/s Ethernet Physical Layer
(SNOSAX0)
• DP83849I PHYTER DUAL Industrial Temperature with Flexible Port Switching Dual Port (SNOSAX1)
• DP83849ID PHYTER DUAL Industrial Temperature with Fiber Support (FX), Dual Port 10/100 Mb/s
Ethernet PHY X-ceiver (SNOSAX2)
• DP83849IF PHYTER DUAL Industrial Temperature with Fiber Support (FX) and Fl (SNOSAX8)
• DP83640 Precision PHYTER - IEEE® 1588 Precision Time Protocol Transceiver (SNOSAY8)
• AN-1519 DP83848 PHYTER® Transformerless Ethernet Operation Application Report (SNLA088)
• IEEE 802.3 and 802.3u specifications (For 10/100 Mb/s operation)
• PCB Trace Impedance Calculator
• Differential Impedance
