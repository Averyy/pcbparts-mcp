---
source: "NXP AN3208 -- Crystal Oscillator Troubleshooting Guide"
url: "https://www.nxp.com/docs/en/application-note/AN3208.pdf"
format: "PDF 10pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 25614
---

Freescale Semiconductor AN3208
Rev. 0, 1/2006
Application Note
Crystal Oscillator
Troubleshooting Guide
by: Sergio Garcia de Alba Garcin
RTAC Americas
1 Overview Table of Contents
1 Overview. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
This document is a quick-reference troubleshooting 2 Introduction. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
guide for solving crystal oscillator problems that might 3 Oscillator Configurations. . . . . . . . . . . . . . . . . . . . 2
4 Components in the Colpitts Configuration . . . . . . 3
be encountered when working with microcontrollers.
5 Components in the Pierce Configuration . . . . . . . 3
6 Crystal Overdriving. . . . . . . . . . . . . . . . . . . . . . . . 4
A practical explanation of the Pierce and Colpitts
7 Insufficient Loop Gain. . . . . . . . . . . . . . . . . . . . . . 5
oscillators used in Freescale microcontrollers and
8 Long Start-Up Time. . . . . . . . . . . . . . . . . . . . . . . . 5
recommendations to help solve common problems with 9 Temperature and Voltage Issues . . . . . . . . . . . . . 5
microcontroller crystal oscillators are presented in the 10 Noise Immunity. . . . . . . . . . . . . . . . . . . . . . . . . . . 6
11 Layout Issues . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
following sections. Nevertheless, a particular problem
12 Other Problems. . . . . . . . . . . . . . . . . . . . . . . . . . . 7
might require a different solution from those proposed in
13 Conclusion . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
this application note. Most of the points discussed will 14 References . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
help in the design stage to come about with a more
reliable oscillator.
2 Introduction
Most microcontrollers can use a crystal oscillator as their
clock source. Other options include external canned
oscillators, resonators, RC oscillators, and internal
clocks. The main advantages of a crystal oscillator are
frequency accuracy, stability, and low power
consumption. However, high reliability is needed to fully
benefit from these advantages.
©Freescale Semiconductor, Inc., 2006. All rights reserved.

Oscillator Configurations
To solve common problems with crystal oscillators and to achieve high reliability, it is important to pay
attention to the configuration used, the components and their values, and the layout. This paper will show
how these elements affect such factors as crystal power dissipation, stability, variations with temperature,
feedback strength, start-up time, noise immunity, and thus, reliability and correct operation. It also
contains suggestions for solving problems in these areas.
3 Oscillator Configurations
The two most common oscillator configurations for microcontrollers are the Pierce and the Colpitts
configurations. The M68HC08 and HCS08 microcontrollers implement the Pierce oscillator
configuration.
The MC68HC12 and HCS12 microcontrollers use either a variation of the Colpitts configuration (the
translated ground Colpitts configuration) or the Pierce configuration. In some microcontrollers both
options are available and it is possible to choose between the two.
To select the best option when a choice is possible, it’s important to understand the respective advantages
of the Pierce and the Colpitts configurations. The two configurations have a similar AC equivalent circuit,
but the location of the common ground node differs. Many of the performance differences between these
configurations can be attributed to the varying effects of stray reactances as the ground is moved and to
the effects of the biasing elements.
In the Colpitts configuration stray reactances tend to appear across the crystal. This degrades performance
and reliability, and the effect is worsened by biasing elements in this configuration. In the Pierce
configuration, performance and reliability are considerably less affected because stray elements tend to
appear across the load capacitors (i.e., stray capacitance tends to add to the load capacitors, so it’s easy to
compensate by simply reducing the load capacitors' value).
Freescale’s Colpitts configuration provides an amplitude limitation control (ALC) loop which permits
lower current consumption and lower levels of RF emissions. However, the Pierce configuration is less
susceptible to noise, doesn't have a DC voltage across the crystal, and starts up faster.
Unless the lower current consumption of the Colpitts configuration is required, it is highly recommended
to opt for the Pierce configuration due to its better reliability.
Figure1. Colpitts Oscillator
Crystal Oscillator Troubleshooting Guide, Rev. 0
2 Freescale Semiconductor

Components in the Colpitts Configuration
Figure2. Pierce Oscillator
4 Components in the Colpitts Configuration
An important remark with the Colpitts configuration is that it produces a DC voltage across the crystal.
This causes some crystals to age faster, and the specific effect will depend on the crystal's manufacturing
process. Since this is a long-term reliability issue, problems won't be observed in the initial testing. To
solve the problem, a capacitor can be added to block the DC voltage, as shown in Figure 1.
Consult the crystal manufacturer on the value for the capacitor and whether it should be included. If it’s
impossible to consult with the crystal manufacturer, it is recommended that you add a capacitor to block
the DC voltage. A good rule of thumb is to use a capacitor approximately 100 times the load capacitance
of the crystal. The exact value is not critical, and should be a value around 1nF.
The series combination of C1 and C2: (C1*C2) / (C1+C2), should give a value close to the load
capacitance, C , specified by the crystal manufacturer. Be sure to consider stray capacitances when
L
performing this calculation. Since the feedback voltage is taken from the voltage divisor made up from C1
and the crystal, increasing C1 will result in stronger feedback, while reducing its value will result in weaker
feedback. Insufficient feedback could prevent oscillation from starting or make oscillation difficult to
sustain. In the past, excessive feedback sometimes resulted in crystal overdrive. Crystal overdrive is very
unlikely with modern ICs because they now operate at very low voltages.
5 Components in the Pierce Configuration
In general, the smaller the value of R (Figure 2), the faster the oscillator will start. R must be large
S S
enough to avoid overdriving the crystal, yet small enough to provide enough current to start oscillation
quickly (an R that’s too large could cause the oscillator to fail to start). R can in some cases be zero
S S
(shorted), especially with high-frequency crystals.
Freescale Semiconductor 3

Crystal Overdriving
R , also known as feedback resistance (Rf) and shown in Figure 2, is used to bias the input of the inverting
B
amplifier. By pulling the input of the amplifier toward the voltage at the output, an unstable condition is
created, stimulating oscillation. It can also be observed that feedback resistance affects the loop gain of
the amplifier, which is augmented as the value for the feedback resistance is increased.
The value for capacitors C and C must be chosen so that the series combination: (C *C ) / (C +C ) gives
1 2 1 2 1 2
a value close to the load capacitance, C , specified by the crystal manufacturer. Be sure to add stray
capacitances in the previous calculation. Occasionally, C can be chosen to be slightly smaller than C to
1 2
increase the voltage swing at EXTAL without compromising stability; using a trimmer capacitor in lieu of
C or C can help find the ideal value.For most applications it is recommended to have the same value for
C and C .
6 Crystal Overdriving
Overdriving a crystal can create a number of problems, from high RF emissions and added power
consumption to long-term reliability issues (physical damage to the crystal) to the crystal attempting to
start at an overtone, or failing to start at all. This is more common with low-frequency crystals, since the
maximum power they can dissipate (maximum drive level) is typically much lower than what is specified
for high-frequency crystals.
The total power the crystal will have to dissipate depends on several factors. It is proportional to R ,the
1
series resistance of the crystal. It is also proportional to the square of: the voltage across the crystal,
frequency, and total capacitance, C + C .
0 L
Assuming the peak voltage across the crystal is close to V , the following formula provides a rough
DD
approximation for the power dissipated by the crystal:
P=2×R
[
π×freq.×V ×
(
C +C
)]2
1 DD L 0 Eqn.1
This formula makes use of the fact that at resonance, the impedance of the motional arm of the crystal is
equal to the impedance of C + C (load capacitance + shunt capacitance of the crystal). In oscillators with
L 0
amplitude limitation control (ALC), V should be replaced with the maximum voltage amplitude
obtained (approximately 400 - 600mV).
To reduce the power that has to be dissipated by the crystal the following could be done:
• Specify a lower maximum series resistance, R , to the crystal manufacturer
1(max)
• Reduce C (reducing capacitors C1 & C2)
This must be done carefully, since it could increase the voltage across the crystal, which would, in
turn, increase the power.
Reducing load capacitance will slightly increase the frequency of oscillation.
• For the Pierce configuration, add or increase the value of the series-damping resistor, R . Crystal
S
overdriving is not a common problem with the Colpitts configuration.
It is important to have a good margin of safety between the power dissipated and the maximum drive level
specified by the crystal manufacturer in part because loop gain can increase with colder temperatures and
higher supply voltages, increasing the risk of overdriving the crystal.
4 Freescale Semiconductor

Insufficient Loop Gain
7 Insufficient Loop Gain
Just as overdriving the crystal can be a problem, insufficient drive can also be the source of many failures.
For adequate loop gain, load capacitors must be sized correctly, and R and R values must be appropriate
B S
in the Pierce configuration.
Load capacitance affects loop gain since the feedback voltage is obtained in both configurations from the
voltage divider formed by C and the crystal, so it is very important to account for stray capacitance when
1
calculating the value of C and C . In the Pierce configuration, adding load capacitance will reduce loop
gain in some cases.
Resistors R and R also have an effect on loop gain in the Pierce configuration. Making R bigger
B S B
increases the loop gain, while reducing R decreases it. In general, lower-frequency crystals require higher
values for R because their impedance is normally higher than that of high-frequency crystals. A typical
value for R is usually given in the microcontrollers' datasheet. Resistor R has the opposite effect on loop
B S
gain, since loop gain is reduced when the resistor is increased and is increased when the resistor is reduced.
To make sure that loop gain is sufficient, a potentiometer can be placed in series with the crystal. If loop
gain is barely sufficient, increasing the resistance will soon prevent the oscillator from starting. The
recommended procedure is to start with the potentiometer set at 0Ω, then slowly increase the resistance.
After each increment, power to the board should be removed and then restored. Eventually, the circuit will
fail to start. When this happens, the total resistance (crystal + potentiometer) should be substantially larger
than the worst-case resistance specified for the crystal. For example, for a good margin of safety, it would
be nice to have the circuit oscillate with at least twice the maximum specified crystal resistance. The size
of the potentiometer required for the test will increase as the crystal frequency decreases (i.e., 1kΩ for a
10 MHz crystal and 10 kΩ for a 32kHz crystal).
It is recommended that the previous test also be carried out at the highest temperature and lowest V at
which the circuit is expected to operate, since loop gain in many oscillators tends to decrease as
temperature increases and as V decreases.
8 Long Start-Up Time
A long start-up time is usually a more common problem with low-frequency crystals, since they tend to
start much more slowly than high-frequency crystals. One of the causes of a long start-up time is weak
loop gain, which was addressed in Section7, “Insufficient Loop Gain”. Oscillator start-up times will also
be affected by the rise time of the power supply. When the power supply has a sharp rise time, the crystal
will experience an energy impulse that will usually make it start faster than it would using a power supply
with a slow rise time.
9 Temperature and Voltage Issues
The circuit should be tested over the entire temperature and voltage range in which it is expected to
operate. Tests are especially important at the highest temperature and lowest supply voltage, which lead to
minimum loop gain and could result in a slow or no start-up. It’s also important to test at the coldest
temperature and highest supply voltage, which lead to maximum loop gain and could overdrive and
damage the crystal, force it to oscillate at an overtone or harmonic, or cause it to stop working.
Freescale Semiconductor 5

Noise Immunity
If possible, testing under both low- and high-humidity conditions is also recommended. To minimize
undesirable temperature effects, use capacitors with a low temperature coefficient, such as NP0 or COG
types. Verify that all components are specified to work for the entire temperature and voltage range,
especially the crystal.
10 Noise Immunity
Noise is a common cause of oscillator failures; therefore, it’s important to know how to make the oscillator
as immune to noise as possible and to know how to identify when noise is the source of the problem. One
of the easiest ways to know when noise is the problem is if the oscillator malfunction appears when a big
load is activated (i.e., a motor), or a power or high-frequency trace is activated. A noise problem is also
indicated if the problem appears when another device is turned on or when it is brought nearby, because
noise could be conducted or radiated.
To make the oscillator circuit more resistant to noise, make sure there’s an adequate loop gain with good
margin; see Section 7, “Insufficient Loop Gain” . It is also important to check for a good amplitude level.
Some microcontrollers can be configured to provide a higher amplitude output for improved noise
immunity, although higher current consumption is a drawback. Other microcontrollers, especially those
that implement Colpitts oscillators, have non-adjustable on-chip amplitude limitation control (ALC) loops
that make increasing the amplitude level impossible.
Proper layout is also critical in attaining good noise immunity. Traces must be as short as possible. Besides
adding stray elements, long traces absorb and radiate more noise since they act like antennas. Route power
and high-frequency traces far from the oscillator circuit to minimize noise coupling. In some cases, it
might be convenient to shield the oscillator circuit to further isolate it from noise sources. One way to
accomplish this is by surrounding the circuit with a wide grounded trace. For this to work, the grounded
trace must have zero current flowing through it. This is why data sheet examples use a “floating ground”
with no connections other than the oscillator’s V . Finally, ensure adequate power supply decoupling and
SS
filtering to minimize noise in the power supply.
11 Layout Issues
Good layout practices are fundamental to the correct operation and reliability of the oscillator. It is critical
to locate the oscillator’s components very close to the XTAL and EXTAL pins to minimize routing
distances. Long traces in the oscillator circuit are a very common source of problems. Don't route other
signals across the oscillator circuit, and make sure power and high-frequency traces are routed as far away
as possible to avoid crosstalk and noise coupling. Power supply decoupling capacitors should be located
very close to the microcontroller’s power pins.
Avoid the use of vias; if the routing becomes very complex, it is much better to use 0 Ω resistors as bridges
to go over other signals. Vias in the oscillator circuit should only be used for connections to the ground
plane. Don't share ground connections; instead, make a separate connection to ground for each component
that requires grounding. If possible, place multiple vias in parallel for each connection to the ground plane.
Especially in the Colpitts configuration, the oscillator is very sensitive to capacitance in parallel with the
crystal or resonator. Therefore, the layout must be designed to minimize stray capacitance across the
crystal or resonator. For example, in the Colpitts configuration, it’s possible to remove the ground plane
6 Freescale Semiconductor

Other Problems
from all layers under the EXTAL trace and to leave considerable spacing from the EXTAL trace to all other
traces and planes. When stray capacitance appears across capacitors C and C , they should be resized to
compensate for this added capacitance. Be sure to take into account both printed circuit board (PCB) and
pin capacitance.
The use of high-quality components in the oscillator circuit is equally important to achieve correct and
reliable operation. The use of low-inductance resistors, such as carbon composition resistors, is
recommended. Capacitors should be high-quality capacitors with very low ESR, designed for use in
high-frequency applications (i.e., NP0 and COG). If a resonator is used, it is critical to choose a very
high-quality resonator.
Remember that poor layout practices (like long traces) can also contribute to EMC susceptibility and
unintentional electromagnetic radiation.
12 Other Problems
Other common problems include the build up of contaminants on the PCB, hermetic seal fracture, and
issues caused by an inadequate soldering process.
PCB contaminants, like flux, humidity, and finger prints, can reduce the impedance between nodes, which
in turn can create a number of issues. To overcome this problem, check for contaminant accumulation
between the crystal leads and beneath sufrace mount technology (SMT) devices.
Although uncommon, it is possible for a crystal’s hermetic seal to fracture. This would allow moisture and
other contaminants to infiltrate the case, causing sporadic operation or complete failure. To avoid this
problem, the crystal should be handled carefully and its case should be adhered to the PCB. A small
SMT-type crystal is recommended.
Excessive temperatures or excessive exposure time to high temperatures due to an inappropriate soldering
process can also damage the crystal. Make sure the soldering process is compatible with the crystal’s
soldering profile.
13 Conclusion
After following best design practices, if the oscillator doesn't work properly, it is possible that the selected
crystal (or resonator) has poor operating characteristics. In that case, consider choosing a different crystal,
but remember that the new crystal’s required external component values will probably be completely
different. Selecting an appropriate high-quality crystal is a very important part of the design process and
is critical to achieving correct operation and high reliability.
Once the oscillator design has been optimized, it’s possible to further increase reliability through software.
Many microcontrollers now have the capability to monitor clock quality and include tools like loss of clock
interrupts to respond to oscillator problems.
Consult the microcontroller's datasheet for specific recommendations and the electrical specifications
section for electrical and timing characteristics. If possible, consult the crystal or resonator manufacturer
with respect to the component values. Many crystal manufacturers will validate your application board
with their crystal or resonator and such an evaluation is strongly recommended.
Freescale Semiconductor 7

References
14 References
1. Cox, Cathy, and Clay Merritt. “Microcontroller Oscillator Circuit Design Considerations”.
Freescale Semiconductor Application Note AN1706, 1997.
2. Bujanos, Norman. “Choosing the Right Crystal for your Oscillator”. Circuit Cellar Ink Feb. 1998:
66-70
3. Sridharan, Meera, and Charles Melear. “Practical Considerations for Working With
Low-Frequency Oscillators”. Freescale Semiconductor Application Note AN2606, 2004.
4. Frerking, Marvin. Crystal Oscillator Design and Temperature Compensation. New York: Van
Nostrand Reinhold Company, 1978.
5. Burch, Ken, and Jim Feddeler. Crystal Oscillators Presentation.
6. Yan-Tai Ng, “Power-On, Clock Selection, and Noise Reduction Techniques for the Freescale
MC68HC908GP32”, Freescale Semiconductor Application Note AN2105, 2001.
7. Yan-Tai Ng, “Designing with the MC68HC908JL/JK Microcontroller Family”, Freescale
Semiconductor Application Note AN2158, 2001.
8. Ross Carlton, Greg Racino, John Suchyta, “Improving the Transient Immunity Performance of
Microcontroller-Based Applications”, Freescale Semiconductor Application Note, Freescale
Semiconductor Application Note AN2764, 2001, 2005.
9. Dugald, Campbell, “Designing for Electromagnetic Compatibility with Single-Chip
Microcontrollers”, Freescale Semiconductor Application Note AN1263, 1995.
10.Stuart Robb, David Brook, and Andreas Rusznyak, “Determining MCU Oscillator Start-up
Parameters”, Freescale Semiconductor Application Note AN1783, 1998.
8 Freescale Semiconductor

References
Freescale Semiconductor 9

How to Reach Us:
Home Page:
www.freescale.com
E-mail:
support@freescale.com
Information in this document is provided solely to enable system and software
implementers to use Freescale Semiconductor products. There are no express or
USA/Europe or Locations Not Listed:
Freescale Semiconductor implied copyright licenses granted hereunder to design or fabricate any integrated
Technical Information Center, CH370 circuits or integrated circuits based on the information in this document.
1300 N. Alma School Road
Chandler, Arizona 85224
Freescale Semiconductor reserves the right to make changes without further notice to
+1-800-521-6274 or +1-480-768-2130
support@freescale.com any products herein. Freescale Semiconductor makes no warranty, representation or
guarantee regarding the suitability of its products for any particular purpose, nor does
Europe, Middle East, and Africa: Freescale Semiconductor assume any liability arising out of the application or use of any
Freescale Halbleiter Deutschland GmbH product or circuit, and specifically disclaims any and all liability, including without
Technical Information Center limitation consequential or incidental damages. “Typical” parameters that may be
Schatzbogen 7 provided in Freescale Semiconductor data sheets and/or specifications can and do vary
81829 Muenchen, Germany
in different applications and actual performance may vary over time. All operating
+44 1296 380 456 (English)
parameters, including “Typicals”, must be validated for each customer application by
+46 8 52200080 (English)
+49 89 92103 559 (German) customer’s technical experts. Freescale Semiconductor does not convey any license
+33 1 69 35 48 48 (French) under its patent rights nor the rights of others. Freescale Semiconductor products are
support@freescale.com not designed, intended, or authorized for use as components in systems intended for
surgical implant into the body, or other applications intended to support or sustain life,
Japan: or for any other application in which the failure of the Freescale Semiconductor product
Freescale Semiconductor Japan Ltd. could create a situation where personal injury or death may occur. Should Buyer
Headquarters
purchase or use Freescale Semiconductor products for any such unintended or
ARCO Tower 15F
unauthorized application, Buyer shall indemnify and hold Freescale Semiconductor and
1-8-1, Shimo-Meguro, Meguro-ku,
Tokyo 153-0064 its officers, employees, subsidiaries, affiliates, and distributors harmless against all
Japan claims, costs, damages, and expenses, and reasonable attorney fees arising out of,
0120 191014 or +81 3 5437 9125 directly or indirectly, any claim of personal injury or death associated with such
support.japan@freescale.com unintended or unauthorized use, even if such claim alleges that Freescale
Semiconductor was negligent regarding the design or manufacture of the part.
Asia/Pacific:
Freescale Semiconductor Hong Kong Ltd.
Technical Information Center Freescale™ and the Freescale logo are trademarks of Freescale Semiconductor, Inc.
2 Dai King Street All other product or service names are the property of their respective owners.
Tai Po Industrial Estate
© Freescale Semiconductor, Inc. 2006. All rights reserved.
Tai Po, N.T., Hong Kong
+800 2666 8080
support.asia@freescale.com
For Literature Requests Only:
Freescale Semiconductor Literature Distribution Center
P.O. Box 5405
Denver, Colorado 80217
1-800-441-2447 or 303-675-2140
Fax: 303-675-2150
LDCForFreescaleSemiconductor@hibbertgroup.com

Rev. 0, 1/2006