---
source: "TI SLAA896 -- PCB Layout Guidelines for TAS2xxx Class-D Boosted Audio Amplifier"
url: "https://www.ti.com/lit/an/slaa896/slaa896.pdf"
format: "PDF 10pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 17628
---

Application Report

PCB Layout Guidelines for TAS2xxx Series Class-D
Boosted Audio Amplifier
Karan Gandhi
ABSTRACT
As the performance of class-D audio amplifiers gets better and system complexity increases, special care
must be taken in the printed circuit board (PCB) layout phase of a design to ensure a robust solution. As
in most engineering practices, there is no unique solution to a given problem or unique layout, but this
application note helps guide you to reach an optimal layout solution.
Contents
1 Introduction ................................................................................................................... 2
2 Layout Guidelines............................................................................................................ 2
3 Typical Board Parasitic...................................................................................................... 7
4 Summary...................................................................................................................... 8
5 References ................................................................................................................... 8
List of Figures
1 Top Layer for TAS2562 PCB Shows All GND Pins Are Shorted Right at the Device Ball......................... 3
2 Layer 2 is Solid Ground Just Below the Device Area Also to Provide the Shortest Return Current Path ....... 4
3 Capacitor Placement for TAS2562 Device as Close to Device as Possible......................................... 5
4 PCB Top View Shows Routing Switching Net Without Providing Cross Sectional Area for Coupling with
Other Net in Adjacent Layer................................................................................................ 5
5 PCB Top View Shows the Decoupling of Switching Net With Other Net by having a Ground Layer
Between the Two ............................................................................................................ 5
6 PCB Top View Shows Switching Net Routed Parallel to Other Signal in Adjacent Layer Without Any
Ground Shielding Between the Two....................................................................................... 6
7 GREG Capacitor on Top Layer, Multiple Vias to Connect to Swap Between Layers to Connect to PVDD,
and GREG Device Pin ...................................................................................................... 6
8 PVDD Routed as Thick Trace to PVDD Device Ball from the Capacitor and Star Connected to PVDD Pin
Using a Via ................................................................................................................... 7
9 GREG Routed to Device Ball Using a Thick Trace ..................................................................... 7
List of Tables
1 Critical Signals and Description............................................................................................ 2
2 Optimum Parasitic on the Device Pin..................................................................................... 4
3 Resistance and Current Carrying Capability of Output Trace ......................................................... 7
4 Resistance, Inductance, and Current Carrying Capability of Typical Epoxy-filled Via.............................. 8

1 Introduction
1.1 Scope
This application note can help system designers implement best practices and understand PCB layout
options while designing audio segments of the system. It serves as a guide to laying out critical nets
reliably. This helps in extracting best possible audio quality from the class-D audio amplifier. This is
intended for the audiences who are involved in designing audio systems.
1.2 Critical Signals
The main concern while designing audio systems includes choosing the right passive component, which
maintains quality of the audio, along with small system size and less cost. Another big concern which
arises due to SoC IC is routing Analog, Digital, and Power signals with integrity, avoiding interference with
each other, and maintaining audio quality. The third concern while routing signals is that other system
devices must not interfere with the audio chip and vice versa negatively due to EMI and other voltage and
current switching.
Table 1 outlines the signals requiring the most attention when laying out a PCB that incorporates a Texas
Instruments boosted audio amplifier System-on-Chip (SoC).
Table 1. Critical Signals and Description
SIGNAL NAME DESCRIPTION
BGND Boost ground. Connect to PCB GND plane.
DREG Digital core voltage regulator output. Bypass to GND with a cap.
Do not connect to external load.
GREG High-side gate CP regulator output. Do not connect to external
load.
GND Digital ground. Connect to PCB GDN plane
OUT_N Class-D negative output for receiver channel
OUT_P Class-D positive output for receiver channel
PGND Power stage ground. Connect to PCB GND plane.
PVDD Power stage supply
SW Boost converter switch input
VBAT Battery power supply input
VBST Boost converter output. Do not connect to external load.
VDD Analog, digital, and IO power supply
VSNS_N Voltage sense negative input
VSNS_P Voltage sense positive input
ADDR/MODE Address detect pin
AVDD Analog and digital power supply
IOVDD IO supply
2 Layout Guidelines
After selecting the right set of components, the next important task is to lay out the PCB in such a way
that the device gives optimum performance for the particular system. A guide to choose right set of
passive components for an audio amplifier can be found in the Passive Component Selection Guide for
Class-D Audio Amplifier Application Report. Four to six layers with epoxy-filled vias is ideal for optimum
layout of the device.

2.1 Power Planes
Power planes must be routed thick enough to carry to the maximum current supply pin demands. Take
special care when the supply plane is shared amongst multiple ICs in the system. Best layout practice is
providing the planes/thick traces to different ICs in the system from the power management IC or main
supply source in a star-connected way at the source itself. This reduces the adverse effect caused on
other ICs because of the high switching ICs shared on the same line.
VBST is the output of boost supply and PVDD serves as power supply to output power stage. VBST
should be connected to PVDD strongly just below the device on the top layer itself to avoid and voltage
droop due to IR losses and ringing due to Via parasitic inductance.
AVDD/VDD and IOVDD must be routed from the PMIC/source as star-connected thick traces (20–30 mils)
at the source for several ICs in the system.
Bypass capacitors serve two main purposes. It fulfills the sudden switching current requirement for the
device and helps in decoupling voltage noise fluctuations on power pins ensuring reliable constant solid
power supply seen by device pin and thus better performance also. In order to reduce parasitic inductance
and resistance of the routing, the decoupling capacitors should be placed right next to the corresponding
pin on the top layer and route with as thick of trace as possible. For the internal pin where connection to
the decoupling capacitor is not possible on top layer, try to route it in immediate layer to top layer to
reduce parasitic.
2.2 Ground Plane/Connections
All the ground pins of the devices are expected to be connected to the ground plane as strongly as
possible. All the device grounds are expected to be shorted in such a way that there is no formation of
multiple ground loops. A direct via on the device pads to the ground plane is preferable. The point to
consider here is all the ground pins must be strongly connected to the plane because the logical current
return path for different supplies is served by different ground pins (for example, VDD-GND, VBST-BGND,
PVDD-PGND, and so forth). A dedicated layer for the ground is strongly recommended. Figure 1 and
Figure 2 show an example of the TAS2562 device where all the ground pins are shorted on the top layer
just below the device balls and then stitched to ground layer present on layer 2 though multiple vias on the
device balls and as close to device balls as possible.
Figure 1. Top Layer for TAS2562 PCB Shows All GND Pins Are Shorted Right at the Device Ball

Figure 2. Layer 2 is Solid Ground Just Below the Device Area Also to Provide the Shortest Return
Current Path
2.3 Capacitor Placement
Decoupling capacitors must be placed as close to a specific pin on the top layer as possible to avoid
parasitic resistance and inductance. Higher resistance and inductance can lead to overshoot/undershoot
in the voltage spike due to switching current requirements as per Equation 1.
(1)
For small finite time duration equation can be approximated to:
(2)
The voltage spikes due to the switching current requirement from the power supplies. Due to the sudden
current requirement, even the nH of inductance can cause large voltage ripple and hinder the device
operation. Another reason for keeping the parasitic inductance and resistance minimal is to provide the
least impedance decoupling path.
The expectation from the system design is that the smallest decoupling cap is placed less than 1 mm of
distance from the device pin and any further caps are placed next to it as close as possible.
Parasitic matters for the complete decoupling loop include a parasitic from power supply pin to one end of
decoupling capacitor, parasitic of capacitor component, and parasitic between the second end of the
capacitor to ground pin of the device. Using multiple vias to connect the capacitor to ground helps in
reducing parasitic inductance because of multiple parallel via connections. Vias should be placed as close
to capacitor pad as possible. Table 2 shows the total acceptable loop inductance on different supply pins
for optimum device performance. It also shows the requirement for the charge pump bootstrap capacitor.
Table 2. Optimum Parasitic on the Device Pin
PARASITIC INDUCTANCE
PIN-PIN CAPACITOR ESL (pH) TOTAL (pH)
(pH)
DREG-GND 650 500 1150
GREG-PVDD 300 500 800
VBAT-GND 650 500 1150
VBST-BGND 250 500 750
VDD-GND 350 500 850

Figure 3. Capacitor Placement for TAS2562 Device as Close to Device as Possible
2.4 Switching Signals
Class-D output, SW node, and Vsense signals are continuously switching signals and should be routed in
such a way that so they do not couple and interfere with each other or any other signal on the PCB. They
must not be routed in the adjacent layer with any other signal without ground shielding in between layers.
Figure 4, Figure 5, and Figure 6 illustrate the carebout for routing a switching net. Figure 4 shows top level
view of the PCB and demonstrates the nets on the different layers. The basic principle here is to avoid
coupling between different switching nets and between switching nets and any other signal. Figure 4 and
Figure 5 show valid routing conditions while Figure 6 is an invalid scenario.
Layer N
(switching net)
Layer N+/-1
(Other signal)
Figure 4. PCB Top View Shows Routing Switching Net Without Providing Cross Sectional Area for
Coupling with Other Net in Adjacent Layer
(Switching net)
(GND shielding)
Layer N+/-2
Figure 5. PCB Top View Shows the Decoupling of Switching Net With Other Net by having a Ground
Layer Between the Two

(switching net)
Figure 6. PCB Top View Shows Switching Net Routed Parallel to Other Signal in Adjacent Layer Without
Any Ground Shielding Between the Two
2.5 SW
SW refers to the boost switching node which is connected to supply through the boost inductor. The
routing of this signal should be capable of carrying 5 A (boost maximum current limit, number varies from
device to device) of current and should offer minimum resistance and capacitance between SW and VBAT
source in order to avoid efficiency loss.
2.6 Vsense Signals
Vsense signals must be routed as close to speaker terminals as possible. Vsense is used to sense actual
voltage across speaker terminals and used for speaker protection. The speaker protection algorithm works
optimally if the Vsense is closed closest to speaker terminals. 6 mil trace width is sufficient for these
signals and should be routed differentially to avoid any non-differential noise coupling to these signals.
2.7 Charge Pump Capacitor
The charge pump capacitor smust be connected between the GREG/VREG pin and PVDD pin with the
least possible parasitic inductance and resistance. Refer to Table 2 for quantitative details. Note that the
charge pump capacitor must be connected as close as possible to the PVDD pin as star connection and
not on the PVDD plane. Use thick routing and immediate to the top layer for routing this signal to offer
minimum parasitic on this pin.
Figure 7, Figure 8, and Figure 9 illustrate the GREG-PVDD routing for the TAS2562 device. GREG is
being routed to the PVDD via a capacitor in a star-connected fashion at the PVDD end. Multiple vias are
used to connect swap layers and thick GREG trace is used to avoid large parasitic inductance offered by
trace.
Figure 7. GREG Capacitor on Top Layer, Multiple Vias to Connect to Swap Between Layers to Connect to
PVDD, and GREG Device Pin

Figure 8. PVDD Routed as Thick Trace to PVDD Device Ball from the Capacitor and Star Connected to
PVDD Pin Using a Via
Figure 9. GREG Routed to Device Ball Using a Thick Trace
2.8 Class-D Output Signals
Class-D output signals should be routed at least 30 mil wide in two layers. Effectively, each output must
be routed 60 mil wide to the speaker for the EM requirements. In case the EMI filter is placed on the
board, it must be placed as close to device pins as possible. For the best THDN performance, output
signals should be length matched to each other in order to avoid any mismatch degraded THDN due to
difference in routing resistance.
2.9 Digital Signals
Digital signals must be routed in a way so they do not interfere with other signals and their integrity is
maintained. Make sure they are not routed adjacent to any switching net, which can couple and inject
noise in digital signals.
3 Typical Board Parasitic
For a quick estimation of the parasitic while layout, Table 3 and Table 4 can be quite helpful.
Tables in this section consider the most common fabrication practice of FR-4 STD material, 1-oz of
copper, 62 mil PCB thickness, and epoxy-filled via.
Table 3. Resistance and Current Carrying Capability of Output Trace
WIDTH DC RESISTANCE (mΩ/INCH) CURRENT CARRYING CAPABILITY (A)
30 9.68 3.18
40 7.08 3.63

Table 3. Resistance and Current Carrying Capability of Output Trace (continued)
WIDTH DC RESISTANCE (mΩ/INCH) CURRENT CARRYING CAPABILITY (A)
50 5.58 4.32
80 3.41 5.55
Table 4. Resistance, Inductance, and Current Carrying Capability of Typical Epoxy-filled Via
CURRENT CARRYING
VIA DIAMETER (mils)(1) DC RESISTANCE (mΩ) INDUCTANCE (nH)
CABABILITY (A)
4 2.9 1.61 1.4
6 2.1 1.48 1.53
10 1.3 1.32 2.01
12 1.1 1.26 2.21
18 0.7 1.14 2.72
(1) Via properties mentioned in the table are for the complete 62-mil via. In case signals are routed in internal layer, these numbers
can be linearly scaled. For example, a 4-mil via offers 0.8-nH inductance between the top layer and a layer 32 mil below the top
layer.
4 Summary
This article concludes the optimum layout for a Class-D boosted Audio amplifier. The following table can
be used as a checklist for a quick reference while layout.
PIN
Short BGND, GND, GNDD, and PGDN below the package and connect them to PCB
BGND, GND, PGND, GNDD
ground plane strongly through multiple vias. Minimize inductance as much as possible.
Bypass to GND with capacitor recommended in section above. Do not connect to external
DREG load. Both ends of the decoupling cap should see as low inductance as possible between
this pin and GND pins.
Connect it to PVDD with a star connection and not to boost plane with recommended in
GREG/VREG
section above. Do not connect to external load.
Short it to VBST (boost) plane through strong connection. Connect it to GREG with a star
PVDD
connection and not to boost plane.
Connect to VBAT with boost inductor. Reduce parasitic capacitor and resistance for
efficiency. Boost inductor must be as close as possible to the SW pin. The inductor must
SW
be connected to SW through thick plane. Traces should support currents up to device
boost current limit. No other net should couple to this.
Bypass to GND with a recommended capacitor. Must be connected to the inductor through
VBAT a thick plane. Both ends of decoupling capacitor should see as low inductance as possible
between VBAT pin and PGND pin.
Do not connect to external load. Bypass to GND with a recommended capacitor. Connect
to PVDD through a thick plane. Both ends of decoupling capacitor should see as low
VBST
inductance as possible between VBST pin and BGND pin. Traces should support currents
up to device overcurrent limit.
Bypass to GND with capacitor recommended. Both ends of decoupling cap see as low
VDD
inductance as possible between this pin and GND pin.
Should not couple with any other net in the system. Connect EMI filter if required as close
OUT_P, OUT_N
to device pin as possible. Traces must support currents up to device overcurrent limit.
5 References
• Texas Instruments, TAS2562 6.1-W Boosted Class-D Audio Amplifier with IV Sense Datasheet
(SLASEI7)
• Texas Instruments, Layout Guidelines For TPA300x Series Parts Application Report (SLOA103)
• Texas Instruments, Post Filter Feedback Class-D Amplifier Benefits and Design Considerations
Application Report (SLOA260)

• Singing Capacitors (Piezoelectric Effect)
• Texas Instruments, Passive Component Selection Guide for Class-D Audio Amplifier Application
Report (SLAA903)