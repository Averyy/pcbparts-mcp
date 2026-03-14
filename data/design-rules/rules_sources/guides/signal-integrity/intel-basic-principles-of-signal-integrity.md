---
source: "Intel -- Basic Principles of Signal Integrity"
url: "https://cdrdv2-public.intel.com/650327/wp_sgnlntgry.pdf"
format: "PDF 4pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 12778
---

White Paper
Basic Principles of Signal Integrity
Introduction
Digital designs have not traditionally suffered by issues associated with transmission line effects. At lower
frequencies the signals remain within data characterization and the system performs as designed. But as system
speeds increase, the higher frequency impact on the system means that not only the digital properties, but also the
analog effects within the system must be considered. These problems are likely to come to the forefront with
increasing data rates for both I/O interfaces and memory interfaces, but particularly with the high-speed transceiver
technology being embedded into FPGAs.
Transmission line effects can have a significant effect on the data being sent. At low speeds, the frequency response
has little influence on the signal, unless the transmission medium is particularly long. However, as speed increases,
high-frequency effects take over and even the shortest lines can suffer from problems such as ringing, crosstalk,
reflections, and ground bounce, seriously hampering the integrity (response) of the signal. You can overcome these
issues by following good design techniques and simple layout guidelines, as described in this document.
Transmission Line Effects and Signal Integrity
A transmission line can be defined as a “conductive connection between a transmitter and a receiver capable of
carrying a signal.” Traditionally, transmission lines are thought of as telecom-based cables operating over long
distances. However, with high-speed digital signal transmission, even the shortest passive printed circuit board (PCB)
track suffers from transmission line effects.
At low frequencies a wire or a PCB track may be considered to be an ideal circuit without resistance, capacitance, or
inductance. But at high frequencies, AC circuit characteristics dominate, causing impedances, inductances, and
capacitances to become prevalent in the wire. A circuit model can be calculated, as shown in Figure1, and used to
determine the characteristic impedance of the wire or track. This wire impedance is extremely important, as any
mismatch within the transmission path results in a reduction in signal quality.
Figure 1. Circuit Model Representation of a Transmission Line
Impedance Mismatch and Signal Integrity
Unequal impedance of the source output (Z ), line (Z ), and receiver or load (Z ) causes impedance mismatch. This
S O L
mismatch means the transmitted signal is not fully absorbed within the receiver and the excess energy is reflected
back to the transmitter. This process continues back and forth until all the energy is absorbed. At high data rates this
can cause signal overshoot, undershoot, and ringing and stairstep waveforms, which produce signal errors.
Impedance mismatch can be overcome by matching the transceiver buffers to the transmission media. In the case of a
PCB, this can be achieved by careful selection of the medium and by the use of termination schemes.
WP-SGNLNTGRY-1.3
December 2007, ver. 1.3 1

Basic Principles of Signal Integrity Altera Corporation
The termination scheme used to overcome impedance mismatch depends on the application. The schemes include
simple parallel termination (see Figure2) and more complex RC termination where a resistor capacitor network
provides a low pass filter to remove low frequency effects but passes the high frequency signal.
Figure 2. Simple Parallel Termination
Although external components can often help the situation, they require PCB real estate and may also require
additional track stubs, which can lead to further reflections on the signal.
Altera® high-speed I/O solutions provide on-device programmable termination to reduce the need of external
component. Stratix® II, Stratix, and Stratix GX devices all provide on-device termination technology. This technology
provides receiver and transmitter driver impedance matching for serial, parallel and differential I/O. The high-speed
transceiver blocks on the Stratix GX device additionally provide a programmable termination scheme within the
high-speed transceiver circuitry to support most high-speed I/O standards.
Signal Attenuation and Signal Integrity
High-frequency signal transmission line losses make it difficult for the receiver to interpret the information correctly.
The following two causes of transmission line losses are due to the transmission medium:
■ Dielectric absorption: High-frequency signals excite molecules in the insulator, which causes the insulator to
absorb signal energy. This absorption reduces the signal strength. Dielectric absorption relates to the PCB material
and can be lessened by careful material selection.
■ Skin effect: Varying current waveforms caused by AC and high-frequency signals tend to travel on the conductor’s
surface. Signals traveling on the surface cause the self-inductance of the material to produce an increased
inductive reactance at high frequencies, which forces electrons to the material’s surface. The effective reduction
of conductive area causes an increase of resistance and, therefore, attenuation of the signal. Increasing track width
can reduce the skin effect, but this is not always possible. Figure3 shows a cross sectional view of a printed circuit
board (PCB).
Figure 3. The Skin Effect
2

Altera Corporation Basic Principles of Signal Integrity
Stratix GX Transceiver Features for Reducing Signal Attenuation
Careful selection of the insulating material and track layout can reduce signal attenuation. Additionally, the following
Stratix GX transceiver circuitry features reduce signal attenuation:
■ Programmable differential output voltages (V ): Programmable V settings ensure that the drive strength aligns
OD OD
with the line impedance and trace length. Increasing the V at the driver improves the signal at the receiver.
OD
■ Pre-emphasis: Reducing high-frequency attenuation is not achieved only by boosting the signal strength because
it also amplifies associated signal noise and jitter. Pre-emphasis boosts only the high-frequency signal components
by increasing the level of the first transmitted symbol. The subsequent symbol levels are untouched if they were
transmitted at the same level. For example, if a signal transmits a high level for three symbols, only the first
symbol is boosted. The next two symbols are transmitted at the usual level. Figure4 illustrates pre-emphasis. If a
single symbol is transmitted at a high level, this symbol is also boosted. Pre-emphasis is also key to overcoming
the effects of pattern dependant jitter, including loss of amplitude, displacement in time, and rounded signal edges.
■ Receiver equalization: Dedicated receiver circuitry is used to attenuate the signal’s low-frequency components as
they arrive at the receiver to compensate for line losses. Stratix GX devices have programmable equalization for
0", 20", and 40" transmission lines.
Figure 4. Pre-Emphasis Over Two Unit Intervals (UI)
Crosstalk and Signal Integrity
Whenever a signal is driven along a wire, a magnetic field develops around the wire. If two wires are placed adjacent
to each other, it is possible that the two magnetic fields interact causing a cross-coupling of energy between signals
known as crosstalk. The following two energy coupling types are the predominant causes of crosstalk:
■ Mutual inductance: A magnetic field causes induced current from the driven wire to appear on the quiet wire. This
mutual inductance causes positive waves to appear near the transmitter end of the quiet line (near end inductance)
and negative waves at the receiver end of the transmission line (far end crosstalk).
■ Mutual capacitance: The coupling of two electric fields when current is injected in the quiet line proportional to
the rate of change of voltage in the driver. This mutual capacitance causes positive waves near both ends of the
transmission line.
Techniques for Reducing Crosstalk
The following PCB design techniques can significantly reduce crosstalk in micro-strip or strip-line layouts:
■ Widen spacing between signal lines as much as routing restrictions allow.
■ Design the transmission line so that the conductor is as close to the ground plane as possible. This couples the
transmission line tightly to the ground plane and helps decouple it from adjacent signals.
■ Use differential routing techniques where possible, especially for critical nets.
■ Route signals on different layers orthogonal to each other, if there is significant coupling.
■ Minimize parallel run lengths between signals. Route with short parallel sections and minimize long coupled
sections between nets.
3

Basic Principles of Signal Integrity Altera Corporation
Simultaneous Switching Output (SSO) Effects on Signal Integrity
As digital circuitry speed increases, output-switching times decrease. Faster switching times cause higher transient
currents within the outputs as the load capacitors discharge. If a number of outputs switch simultaneously from logic
high to logic low, it causes the charge stored in the I/O load capacitances to flow into the device. This sudden flow of
current exits the device through internal inductances onto the board ground, which develops a voltage. This voltage
results in a voltage difference between the device and the board ground, momentarily developing a low voltage signal
on the I/O above the ground level. This low voltage signal is known as ground bounce. The bounce effect can cause
an output low to be seen as a high by other devices on the board.
Ground bounce can be reduced by following a number of board-based design rules as outlined in the Altera
publication AN 224: High-Speed Board Layout Guidelines. Altera high-speed solutions provide pin slew rate control,
which allows the designer to slow down the driver and thus reduce ground bounce. Additionally, the devices include
multiple power and ground pins, thereby allowing the designer to locate a high-speed I/O pin close to a ground pin to
reduce the effects of SSO.
Conclusion
The challenges of high-speed design require some additional effort to ensure signal integrity. This can be achieved by
following some simple analog design rules and using careful PCB layout techniques. Altera high-speed
programmable logic devices provide features to help support high-speed design. In Stratix GX devices these range
from programmable slew rate control and on-device termination technology in the standard high-speed I/O to
advanced features such as programmable drive strength, pre-emphasis, and receiver equalization in the high-speed
transceiver interfaces. These features help make the designer’s life simpler.
Further Information
■ AN 75: High Speed Board Design:
www.altera.com/literature/an/an075.pdf
■ AN 224: High-Speed Board Design Guidelines Using Stratix Devices:
www.altera.com/literature/an/an224.pdf
■ Dally, William J. and Poulton, John W., “Digital Systems Engineering,” Cambridge University Press, 1998.
■ Johnson, H. and Graham, M., “High-Speed Board Design,” Prentice Hall, Inc., 1993.
■ Hall, Stephen, Hall Garrett, and McCall, James, “High-Speed Digital System Design,” John Wiley and Sons, Inc.,
2000.
■ Johnson, Howard W. and Graham, Martin, “High-Speed Digital Design, A Handbook of Black Magic,” Prentice
Hall, 1993.
Copyright © 2007 Altera Corporation. All rights reserved. Altera, The Programmable Solutions Company, the stylized Altera logo, specific device
designations, and all other words and logos that are identified as trademarks and/or service marks are, unless noted otherwise, the trademarks and service
marks of Altera Corporation in the U.S. and other countries. All other product or service names are the property of their respective holders. Altera products
are protected under numerous U.S. and foreign patents and pending applications, maskwork rights, and copyrights. Altera warrants performance of its
101 Innovation Drive
semiconductor products to current specifications in accordance with Altera's standard warranty, but reserves the right to make changes to any products and
San Jose, CA 95134 services at any time without notice. Altera assumes no responsibility or liability arising out of the application or use of any information, product, or service
described herein except as expressly agreed to in writing by Altera Corporation. Altera customers are advised to obtain the latest version of device
www.altera.com specifications before relying on any published information and before placing orders for products or services.
4