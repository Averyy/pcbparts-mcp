---
source: "Altium/Lee Ritchey -- Crosstalk or Coupling in High-Speed Design"
url: "https://resources.altium.com/p/crosstalk-or-coupling"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 14658
---
The words crosstalk and coupling are used to describe the injection of electromagnetic energy from one transmission line to another running nearby. In printed circuit boards crosstalk is usually two traces running side by side in the same layer or one over the top of the other in adjacent layers. This coupled energy appears as noise on the victim trace and can cause malfunctions if the amplitude is too large. Learn how this noise is transferred from trace to trace and methods for preventing it from happening.

## CROSSTALK OR COUPLING

Either crosstalk or coupling describes the injection of electromagnetic energy from one transmission line to another running nearby. In printed circuit boards, this alien crosstalk is usually two traces running side by side in the same layer or one over the top of the other in adjacent layers. This coupled energy appears as noise on the victim trace and can cause malfunctions if the amplitude is too large. Though inductive coupling, or magnetic field crosstalk, can occur in PCBs, usually crosstalk comes from electric field-based capacitive coupling. This section will describe how this noise is transferred from trace to trace and methods for preventing it from happening.

Figure 1 is a diagram showing capacitive coupling in two transmission lines traveling side by side. The upper transmission line is shown switching and the lower one is inactive. Notice that there are two waveforms alongside the victim line. One is at the end of the lines where the driver is on the driven line, and the other is at the opposite end or far end. Note that the waveshapes are different. The wave frequency and form at the driver end of the victim line is usually called backward cross talk or “near end crosstalk”, “NEXT” and the waveform at the far end of the victim line is “forward crosstalk or “far end crosstalk”, “FEXT”.

Exactly what these two wave frequency forms will look like depends on what is on the four ends of the transmission lines. The possibilities are: a short circuit, a termination, or an open circuit. Reference 1 at the end of this unit describes in detail how these end terminations cause alien crosstalk and affect the signals seen on the victim line. From that paper it will be observed that the worst case is when the far ends of both lines are open circuits and the near end of the victim line is a short circuit. That happens to be how most CMOS circuits operate. Under these conditions, the waveforms seen on the victim line will look very much like those shown in Figure 1.

In this discussion, the analysis will be done using this “worst case” set of conditions.

Figure 1 Two Transmission Lines Side by Side Interacting

Figure 2 shows how the two forms of capacitive coupling crosstalk (forward and backward) vary as the length that the two transmission lines traveling side by side grow longer. Notice that forward crosstalk increases more slowly than backward crosstalk as the coupled length gets longer Also, notice that there comes a point where backward crosstalk does not increase with increases in coupled length. This is called the “critical length” or the length at which backward crosstalk does not continue to increase or saturate.

Forward crosstalk increases much more slowly than backward crosstalk and does not become a factor in printed circuits as the length of the parallel run is too short. This form of crosstalk was a major problem for phone companies when lines were many meters long. This section will focus on ways to control backward crosstalk.

Figure 2. Forward and Backward Crosstalk as a Function of Coupled Length

## Methods for Controlling Backward Crosstalk with Side by Side Routing

When transmission lines run side by side, the capacitive coupling mechanism is dominated by the magnetic component of the electromagnetic field. In over and under routing the electric field will dominate.

Several methods have been proposed for controlling backward crosstalk. Among these are:

* Restricting length that transmission lines run side by side
* Inserting “guard traces” between the two transmission lines
* Rows of “ground” vias on both sides of a sensitive signal

## Restricting Length of Parallel Run

The most common method proposed for controlling capacitive coupling crosstalk is to limit the length that two transmission lines run side by side. There are even routines in several PCB routers that allow the designer to insert a length number and allow the routing tool to prevent routing longer than this amount to reduce coupling capacitance. For this method to work, this length must be less than the critical length shown in Figure 2. If the length of a parallel run reaches the critical length, it can be seen that continuing to run parallel beyond that point does not result in increased crosstalk. Figure 3 is a plot of critical length as a function of signal rise time. There are three curves on the graph corresponding to three different dielectric constants (er). two corresponds to Teflon, three corresponds to most ribbon cables and four corresponds to most dielectrics found in PCBs.

As can be seen, as rise times get faster the critical length gets shorter. With a rise time of 1.4 nSec, the critical length is about 6 inches or 15 cm. If the router were set to allow three inches of parallel run, it would be possible to make most of the connections in most designs without running out of board space or layers. Unfortunately, very few modern integrated circuits are that slow. Currently, rise times as fast as 100 picoseconds are very common. Looking at Figure 3, it can be seen that critical length at 100 picoseconds is less than half an inch or about 1.5 cm. At these rise times, length control will not work. This has been well known in the supercomputer industry for a very long time and has not been the method used to control backward crosstalk.

Figure 3. Critical Length as a Function of Signal Rise Time

If length control for limiting crosstalk does not work, what method does work?

Referring back to Figure 2, it can be seen that once critical length has been reached, continuing to route parallel does not result in additional crosstalk. At this point, there are only two parameters that affect the amount of crosstalk. These are height to the nearest plane and edge-to-edge separation. Figure 4 is a graph showing how crosstalk varies with height above the nearest plane and edge-to-edge separation once critical length has been reached.

Figure 4. Backward Crosstalk as a Function of Height Above Plane and Separation Stripline

Figure 4 is titled “Offcenter” Stripline. This means that the transmission lines are between two planes but are not centered between the two planes. This is typical of PCBs that have two signal layers between a pair of planes. Notice that crosstalk decreases substantially as the height above the nearest plane is reduced. It also decreases even more rapidly as the traces are moved apart from each other. Figure 5 is a plot showing these values for micro-stripline signal layers that are on the outside of a PCB.

Figure 5. Backward Crosstalk as a Function of Height Above Plane and Separation, Micro-stripline

## Guard Traces

Many rules of thumb have recommended inserting “guard traces” between transmission lines as a method for controlling capacitive crosstalk. If this works, why does it work? And if it works, is there any downside to using this method? The “standard practice” in many companies is to route with 5 mil line and 5 mils spaces. Referring to Figure 4, if a PCB were routed to these rules and the height above the nearest plane was 5 mils (also common) the crosstalk would be about 8%. If this were determined to be excessive and a guard trace were added, what would that involve? To make room for the guard trace a 5 mil space and a 5 mil trace need to be added. Now, the edge to edge separations is 15 mils instead of 5 mils and the crosstalk is less than 1%. It was not the guard trace that caused this decrease. It was the separation.

Downsides to adding guard traces are: This makes routing much more difficult. The guard trade is not a barrier. It is a resonant circuit that may enhance crosstalk by creating a band pass filter.

The proper method for controlling crosstalk in side-by-side routing is separation only.

## Rows of “Ground” Vias

One method proposed by some applications notes and gurus is to place “ground” vias on both sides of a “critical” trace to protect a sensitive transmission line. This sort of rule is not accompanied by any valid proof. It is also accompanied with vague answers when asked how many vias to use and at what spacing. If it were useful and necessary, none of the servers and routers we design every day would be possible as there would not be enough room for all of those vias. This is a bogus rule and should not be used. An overriding observation is that valid design rules have straight forward proofs. This one does not.

## Methods for Controlling Backward Crosstalk with Over-Under Routing

When over and under routing is done, where one transmission line is in one layer and the other is in the layer above or below, coupling is dominated by the electric field much as if a small capacitor had been connected between the two transmission lines. The coupled waveforms have that appearance. With the fast edges of modern logic, the amount of energy coupled, grows so fast with the overlap between two traces, that it exceeds allowable limits with very short runs.

The only safe way to control crosstalk with adjacent signal layers is by routing traces in one layer in the X direction, and in the other layer in the Y direction. Most PCB layout systems have the ability to specify one layer as X and the other as Y to prevent this kind of overlap. Unfortunately, many of them will violate this constraint from time to time, so a designer needs to double check after routing to ensure that this rule has been followed.

## Calculating Crosstalk

There are many rules of thumb circulating on how to space traces to control crosstalk for different wave frequency and PCB design. Among these are: three times the height above the nearest plane; two times the trace width and four times the trace width. These sound a bit arbitrary and they are. In order to determine what the spacing needs to be, the first question that needs to be answered is how much crosstalk noise is acceptable? Since PCB designers must factor many elements, from circuit board size, signal integrity, or impedance to name a few, this is an important question. This depends on several things including: is the victim trace running next to another trace with a much higher amplitude, or is it running alongside another trace with the same amplitude signal?

## Determining How Much Noise is Acceptable

In reference 2 at the end of this section, there is a chapter on design rule creation using noise margin analysis. In this section, it shows that the noise budget of a logic family is consumed by several noise sources. For CMOS there are four primary noise sources. These are: crosstalk, reflections, ripple on Vdd, and Vdd and ground bounce in the IC packages. Once the amount of noise from the last three is calculated, this is subtracted from the noise margin of the logic family to arrive at the amount of crosstalk that can be tolerated.

## An Analytical Method for Determining Crosstalk

There are analytical tools that allow one to calculate the crosstalk that will result from a proposed geometry between two transmission lines. Figure 6 is a screen shot in Hyperlynx® of a pair of transmission lines that will be used to calculate crosstalk for a proposed geometry. It is two CMOS circuits with the upper one active and the lower one set at a logic 0.

Figure 6. Circuit Diagram used to Calculate Crosstalk

Figure 7 is a screen showing how the separation between traces is specified, as well as the trace width and height above the plane. It should be noted that trace width has no bearing on crosstalk, only edge-to-edge separation and height above the nearest plane are involved once transmission lines have been routed beyond the “critical length”.

Figure 7. Screen Showing Geometry of Coupled Pair in Figure 6

Figure 8 is a set of waveforms that result when the driven line switches from a logic 1 to a logic 0. The red waveform is the signal at the driver on the driven line and the purple waveform is the signal at the receiver on the driven line. The flat yellow line is the output of the victim line which is at a logic 0 and the waveform with the bump on it, is the receiver end of the victim line.

Figure 8. Waveforms When Driven Line in Figure 6 Switches

The noise on the victim line appears at the “forward’ or receiver end of the victim line and does not seem to be backward crosstalk which should appear at the “backward” end of the victim line. The reason for this is the driven end of the victim line is a logic 0, which is a short circuit. From the section on transmission lines, it was observed that short circuits do not absorb energy. Instead, they reflect it as an inverted waveform as has been shown in Figure 8. The second observation in the transmission line section is that open circuits also do not absorb the energy but reflect it back doubled, as is the case in Figure 8.

The crosstalk amplitude in Figure 8 is about 1 volt on a 3.3 volt signal line. This is clearly too large. The solution is to return to the screen where height and spacing are set and adjust one or both until the crosstalk that results is within the design window. Once this analysis has been done, the crosstalk rules that result will be precise and not the result of some arbitrary rule of thumb.

## HIGH SPEED DESIGN REFERENCES

* “90 Degree Corners, The Final Turn” Doug Brooks, etal, Printed Circuit Design, January 1998.
* SIGNAL INTEGRITY- SIMPLIFIED, Eric Bogatin, Prentice Hall, 2004.
* “Reflections and Crosstalk in Logic Circuit Connections,” John A DeFalco, IEEE Spectrum, July 1970.
* “Right the First Time, a Practical Handbook on High Speed PCB and System Design, Volumes 1 & 2,” Zasio and Ritchey, Speeding Edge 2003 and 2006.

Altium Designer is a top-notch PCB design software platform that gives you all the tools you need to design the best circuit boards. Click on the free trial to try it for yourself.
