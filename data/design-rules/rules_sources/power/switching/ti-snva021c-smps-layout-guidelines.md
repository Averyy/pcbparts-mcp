---
source: "TI SNVA021C -- SMPS Layout Guidelines"
url: "https://www.ti.com/lit/an/snva021c/snva021c.pdf"
format: "PDF 5pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 7387
---

Application Report

AN-1149 Layout Guidelines for Switching Power Supplies
.....................................................................................................................................................
ABSTRACT
When designing a high frequency switching regulated power supply, layout is very important. Using a
good layout can solve many problems associated with these types of supplies. The problems due to a bad
layout are often seen at high current levels and are usually more obvious at large input to output voltage
differentials. Some of the main problems are loss of regulation at high output current and/or large input to
output voltage differentials, excessive noise on the output and switch waveforms, and instability. Using the
simple guidelines that follow will help minimize these problems.
Contents
1 Inductor ....................................................................................................................... 2
2 Feedback ..................................................................................................................... 2
3 Filter Capacitors ............................................................................................................. 2
4 Compensation ............................................................................................................... 2
5 Traces and Ground Plane ................................................................................................. 2
6 Heat Sinking ................................................................................................................. 2
List of Figures
1 Step-Up Switching Regulator Schematic ................................................................................ 3
2 Bad Layout Example ....................................................................................................... 3
3 Good Layout Example, Top Layer........................................................................................ 3
4 Good Layout Example, Bottom Layer .................................................................................... 3

1 Inductor
Always try to use a low EMI inductor with a ferrite type closed core. Some examples would be toroid and
encased E core inductors. Open core can be used if they have low EMI characteristics and are located a
bit more away from the low power traces and components. It would also be a good idea to make the poles
perpendicular to the PCB as well if using an open core. Stick cores usually emit the most unwanted noise.
2 Feedback
Try to run the feedback trace as far from the inductor and noisy power traces as possible. You would also
like the feedback trace to be as direct as possible and somewhat thick. These two sometimes involve a
trade-off, but keeping it away from inductor EMI and other noise sources is the more critical of the two. It
is often a good idea to run the feedback trace on the side of the PCB opposite of the inductor with a
ground plane separating the two.
3 Filter Capacitors
When using a low value ceramic input filter capacitor, it should be located as close to the V pin of the IC
IN
as possible. This will eliminate as much trace inductance effects as possible and give the internal IC rail a
cleaner voltage supply. Some designs require the use of a feed-forward capacitor connected from the
output to the feedback pin as well, usually for stability reasons. In this case it should also be positioned as
close to the IC as possible. Using surface mount capacitors also reduces lead length and lessens the
chance of noise coupling into the effective antenna created by through-hole components.
4 Compensation
If external compensation components are needed for stability, they should also be placed closed to the IC.
Surface mount components are recommended here as well for the same reasons discussed for the filter
capacitors. These should not be located very close to the inductor as well.
5 Traces and Ground Plane
Make all of the power (high current) traces as short, direct, and thick as possible. It is a good practice on a
standard PCB board to make the traces an absolute minimum of 15 mils (0.381mm) per Ampere. The
inductor, output capacitors, and output diode should be as close to each other possible. This helps reduce
the EMI radiated by the power traces due to the high switching currents through them. This will also
reduce lead inductance and resistance as well, which in turn reduces noise spikes, ringing, and resistive
losses that produce voltage errors. The grounds of the IC, input capacitors, output capacitors, and output
diode (if applicable) should be connected close together directly to a ground plane. It would also be a
good idea to have a ground plane on both sides of the PCB. This will reduce noise as well by reducing
ground loop errors as well as by absorbing more of the EMI radiated by the inductor. For multi-layer
boards with more than two layers, a ground plane can be used to separate the power plane (where the
power traces and components are) and the signal plane (where the feedback and compensation and
components are) for improved performance. On multi-layer boards the use of vias will be required to
connect traces and different planes. It is good practice to use one standard via per 200 mA of current if
the trace will need to conduct a significant amount of current from one plane to the other.
Arrange the components so that the switching current loops curl in the same direction. Due to the way
switching regulators operate, there are two power states. One state when the switch is on and one when
the switch is off. During each state there will be a current loop made by the power components that are
currently conducting. Place the power components so that during each of the two states the current loop is
conducting in the same direction. This prevents magnetic field reversal caused by the traces between the
two half-cycles and reduces radiated EMI.
6 Heat Sinking
When using a surface mount power IC or external power switches, the PCB can often be used as the
heatsink. This is done by simply using the copper area of the PCB to transfer heat from the device. For
information on using the PCB as a heatsink for that particular device, see the device-specific data sheet.
This can often eliminate the need for an externally attached heatsink.

These guidelines apply for any inductive switching power supply. These include step-down (Buck), step-up
(Boost), Flyback, inverting Buck/Boost, and SEPIC among others. The guidelines are also useful for linear
regulators, that also use a feedback control scheme, that are used in conjunction with switching regulators
or switched capacitor converters. Some layout pictures are included: Figure 1 shows step-up switching
regulator schematic to be used for some layout examples. Figure 2 is an example of a bad layout that
violates many of the suggestions given. Figure 3 and Figure 4 show an example of a good layout that
incorporates most of the suggestion given.
Figure 1. Step-Up Switching Regulator Schematic
Figure 2. Bad Layout Example Figure 3. Good Layout Example, Top Layer

Figure 4. Good Layout Example, Bottom Layer
