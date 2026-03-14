---
source: "ADI MT-094 -- Microstrip and Stripline Design"
url: "https://www.analog.com/media/en/training-seminars/tutorials/mt-094.pdf"
format: "PDF 7pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 14480
---

MT-094
TUTORIAL
Microstrip and Stripline Design
INTRODUCTION
Much has been written about terminating PCB traces in their characteristic impedance, to avoid
signal reflections. However, it may not be clear when transmission line techniques are
appropriate.
A good guideline to determine when the transmission line approach is necessary for logic signals
is as follows:
Terminate the transmission line in its characteristic impedance when the one-way propagation
delay of the PCB track is equal to or greater than one-half the applied signal rise/fall time
(whichever edge is faster).
For example, a 2 inch microstrip line over an E = 4.0 dielectric would have a delay of about 270
r
ps. Using the above rule strictly, termination would be appropriate whenever the signal rise time
is less than approximately 500 ps.
A more conservative rule is to use a 2 inch (PCB track length)/nanosecond (rise/fall time) rule. If
the signal trace exceeds this trace-length/speed criterion, then termination should be used.
For example, PCB tracks for high-speed logic with rise/fall time of 5 ns should be terminated in
their characteristic impedance if the track length is equal to or greater than 10 inches (where
measured length includes meanders).
In the analog domain, it is important to note that this same 2 inch/nanosecond guideline should
also be used with op amps and other circuits, to determine the need for transmission line
techniques. For instance, if an amplifier must output a maximum frequency of f , then the
max
equivalent risetime t is related to this f . This limiting risetime, t, can be calculated as:
r max r
t = 0.35/f Eq. 1
r max
The maximum PCB track length is then calculated by multiplying t by 2 inch/nanosecond. For
example, a maximum frequency of 100 MHz corresponds to a risetime of 3.5 ns, so a 7-inch or
more track carrying this signal should be treated as a transmission line.
DESIGNING CONTROLLED IMPEDANCES TRACES ON PCBS
A variety of trace geometries are possible with controlled impedance designs, and they may be
either integral to or allied to the PCB pattern. In the discussions below, the basic patterns follow
those of the IPC, as described in standard 2141A (see Reference 1).
Rev.0, 01/09, WK Page 1 of 7

Note that the figures below use the term "ground plane". It should be understood that this plane
is in fact a large area, low impedance reference plane. In practice it may actually be either a
ground plane or a power plane, both of which are assumed to be at zero ac potential.
The first of these is the simple wire-over-a-plane form of transmission line, also called a wire
microstrip. A cross-sectional view is shown in Figure 1. This type of transmission line might be
a signal wire used within a breadboard, for example. It is composed simply of a discrete
insulated wire spaced a fixed distance over a ground plane. The dielectric would be either the
insulation wall of the wire, or a combination of this insulation and air.
DD
WIRE
DIELECTRIC HH
GROUND PLANE
Figure 1: A Wire Microstrip Transmission Line With Defined Impedance is Formed
by an Insulated Wire Spaced From a Ground Plane
The impedance of this line in ohms can be estimated with Eq. 2. Here D is the conductor
diameter, H the wire spacing above the plane, and ε the dielectric constant.
60 ⎡4H⎤
Z (Ω)= ln . Eq. 2
o ⎢ ⎥
ε ⎣ D ⎦
For patterns integral to the PCB, there are a variety of geometric models from which to choose,
single-ended and differential. These are covered in some detail within IPC standard 2141A (see
Reference 1), but information on two popular examples is shown here.
Before beginning any PCB-based transmission line design, it should be understood that there are
abundant equations, all claiming to cover such designs. In this context, "Which of these are
accurate?" is an extremely pertinent question. The unfortunate answer is, none are perfectly so!
All of the existing equations are approximations, and thus accurate to varying degrees,
depending upon specifics. The best known and most widely quoted equations are those of
Reference 1, but even these come with application caveats.
Reference 2 has evaluated the Reference 1 equations for various geometric patterns against test
PCB samples, finding that predicted accuracy varies according to target impedance. The
equations quoted below are from Reference 1, and are offered here as a starting point for a
design, subject to further analysis, testing and design verification. The bottom line is, study
carefully, and take PCB trace impedance equations with a proper dose of salt.
Page 2 of 7

MICROSTRIP PCB TRANSMISSION LINES
For a simple two-sided PCB design where one side is a ground plane, a signal trace on the other
side can be designed for controlled impedance. This geometry is known as a surface microstrip,
or more simply, microstrip.
A cross-sectional view of a two-layer PCB illustrates this microstrip geometry as shown in
Figure 2.
TRACE
WWW
TT
DIELECTRIC HH
GROUND PLANE
Figure 2: A Microstrip Transmission Line with Defined Impedance is Formed by a
PCB Trace of Appropriate Geometry, Spaced from a Ground Plane
For a given PCB laminate and copper weight, note that all parameters will be predetermined
except for W, the width of the signal trace. Eq. 3 can then be used to design a PCB trace to match
the impedance required by the circuit. For the signal trace of width W and thickness T, separated
by distance H from a ground (or power) plane by a PCB dielectric with dielectric constant ε, the
characteristic impedance is:
87 ⎡ 5.98H ⎤
Z o (Ω) = ln ⎢() ⎥ Eq. 3
ε r +1.41 ⎣ 0.8W+T ⎦
Note that in these expressions, measurements are in common dimensions (mils).
These transmission lines will have not only a characteristic impedance, but also capacitance.
This can be calculated in terms of pF/in as shown in Eq. 4.
0.67
(ε
+1.41
)
C ( pF/in ) = r Eq. 4
o [] ( )
ln5.98H 0.8W+T
As an example including these calculations, a 2-layer board might use 20-mil wide (W),
1 ounce (T=1.4) copper traces separated by 10-mil (H) FR-4 (ε = 4.0) dielectric material. The
resulting impedance for this microstrip would be about 50 Ω. For other standard impedances, for
example the 75-Ω video standard, adjust "W" to about 8.3 mils.
Page 3 of 7

SOME MICROSTRIP GUIDELINES
This example touches an interesting and quite handy point. Reference 2 discusses a useful
guideline pertaining to microstrip PCB impedance. For a case of dielectric constant of 4.0 (FR-
4), it turns out that when W/H is 2/1, the resulting impedance will be close to 50 Ω (as in the first
example, with W = 20 mils).
Careful readers will note that Eq. 3 predicts Z to be about 46 Ω, generally consistent with
o
accuracy quoted in Reference 2 (>5%). The IPC microstrip equation is most accurate between 50
and 100 Ω, but is substantially less so for lower (or higher) impedances.
The propagation delay of the microstrip line can also be calculated, as per Eq. 5. This is the one-
way transit time for a microstrip signal trace. Interestingly, for a given geometry model, the
delay constant in ns/ft is a function only of the dielectric constant, and not the trace dimensions
(see Reference 6). Note that this is quite a convenient situation. It means that, with a given PCB
laminate (and given ε), the propagation delay constant is fixed for various impedance lines.
t ( ns/ft ) =1.017 0.475ε +0.67 Eq. 5
pd r
This delay constant can also be expressed in terms of ps/in, a form which will be more practical
for smaller PCBs. This is:
t ( ps/in ) =85 0.475ε +0.67 Eq. 6
Thus for an example PCB dielectric constant of 4.0, it can be noted that a microstrip's delay
constant is about 1.63 ns/ft, or 136 ps/in. These two additional rules-of-thumb can be useful in
designing the timing of signals across PCB trace runs.
SYMMETRIC STRIPLINE PCB TRANSMISSION LINES
A method of PCB design preferred from many viewpoints is a multi-layer PCB. This
arrangement embeds the signal trace between a power and a ground plane, as shown in the cross-
sectional view of Figure 3. The low-impedance ac-ground planes and the embedded signal trace
form a symmetric stripline transmission line.
As can be noted from the figure, the return current path for a high frequency signal trace is
located directly above and below the signal trace on the ground/power planes. The high
frequency signal is thus contained entirely inside the PCB, minimizing emissions, and providing
natural shielding against incoming spurious signals.
Page 4 of 7

DIELECTRIC
HHH
WWW
GROUND,
POWER TT BB
PLANES
HHH
EMBEDDED
TRACE
Figure 3: A Symmetric Stripline Transmission Line With Defined Impedance is
Formed by a PCB Trace of Appropriate Geometry Embedded Between Equally
Spaced Ground and/or Power Planes
The characteristic impedance of this arrangement is again dependent upon geometry and the ε of
the PCB dielectric. An expression for Z of the stripline transmission line is:
O
( )
60 ⎡ 1.9 B ⎤
Z o ( Ω ) = ln ⎢() ⎥ . Eq. 7
ε ⎣ 0.8W+T ⎦
Here, all dimensions are again in mils, and B is the spacing between the two planes. In this
symmetric geometry, note that B is also equal to 2H + T. Reference 2 indicates that the accuracy
of this Reference 1 equation is typically on the order of 6%.
Another handy guideline for the symmetric stripline in an ε = 4.0 case is to make B a multiple of
W, in the range of 2 to 2.2. This will result in an stripline impedance of about 50 Ω. Of course
this rule is based on a further approximation, by neglecting T. Nevertheless, it is still useful for
ballpark estimates.
The symmetric stripline also has a characteristic capacitance, which can be calculated in terms of
pF/in as shown in Eq. 8.
1.41
(ε )
C o ( pF/in ) = [] ( r ) . Eq. 8
ln3.81H 0.8W+T
The propagation delay of the symmetric stripline is shown in Eq. 9.
t ( ns/ft ) =1.017 ε Eq. 9
or, in terms of ps:
t ( ps/in ) =85 ε Eq. 10
Page 5 of 7

For a PCB dielectric constant of 4.0, it can be noted that the symmetric stripline's delay constant
is almost exactly 2 ns/ft, or 170 ps/in.
SOME PROS AND CONS OF EMBEDDING TRACES
The above discussions allow the design of PCB traces of defined impedance, either on a surface
layer or embedded between layers. There of course are many other considerations beyond these
impedance issues.
Embedded signals do have one major and obvious disadvantage—the debugging of the hidden
circuit traces is difficult to impossible. Some of the pros and cons of embedded signal traces are
summarized in Figure 4.
NNOOTT EMBEDDED EMBEDDED
Route Power
Power Route
Ground Route
Route Ground
(cid:139)(cid:139)Advantages
(cid:122)(cid:122) Signal traces shielded aanndd protected
(cid:122)(cid:122) Lower impedance, thus lower emissions aanndd crosstalk
(cid:122)(cid:122) Significant improvement >> 50MHz
(cid:139)(cid:139)Disadvantages
(cid:122)(cid:122) Difficult prototyping aanndd troubleshooting
(cid:122)(cid:122) Decoupling mmaayy bbee more difficult
(cid:122)(cid:122) Impedance mmaayy bbee ttoooo llooww ffoorr easy matching
Figure 4: The Pros and Cons of Not Embedding Vs. the Embedding of Signal
Traces in Multi-Layer PCB Designs
Multi-layer PCBs can be designed without the use of embedded traces, as is shown in the left-
most cross-sectional example. This embedded case could be considered as a doubled two-layer
PCB design (i.e., four copper layers overall). The routed traces at the top form a microstrip with
the power plane, while the traces at the bottom form a microstrip with the ground plane. In this
example, the signal traces of both outer layers are readily accessible for measurement and
troubleshooting purposes. But, the arrangement does nothing to take advantage of the shielding
properties of the planes.
This non embedded arrangement will have greater emissions and susceptibility to external
signals, vis-a-vis the embedded case at the right, which uses the embedding, and does take full
advantage of the planes. As in many other engineering efforts, the decision of embedded vs. not-
embedded for the PCB design becomes a tradeoff, in this case one of reduced emissions vs. ease
of testing.
Page 6 of 7

REFERENCES:
1. Standard IPC-2141A, "Controlled Impedance Circuit Boards and High Speed Logic Design," 2004,
Institute for Interconnection and Packaging Electronic Circuits, 3000 Lakeside Drive, 309 S, Bannockburn,
IL 60015, 847-615-7100.
2. Eric Bogatin, BTS015, PCB Impedance Design: Beyond the IPC Recommendations, BeTheSignal.com.
3. Eric Bogatin, Signal Integrity – Simplified, Prentice Hall PTR, 2003, ISBN-10: 0130669466, ISBN-13:
978-0130669469.
4. Andrew Burkhardt, Christopher Gregg, Alan Staniforth, "Calculation of PCB Track Impedance," Technical
Paper S-19-5, presented at the IPC Printed Circuits Expo '99 Conference, March 14–18, 1999.
5. Brian C. Wadell, Transmission Line Design Handbook, Artech House, Norwood, MA, 1991, ISBN: 0-
89006-436-9.
6. William R. Blood, Jr., MECL System Design Handbook (HB205/D, Rev. 1A May 1988), ON
Semiconductor, August, 2000.
7. Hank Zumbahlen, Basic Linear Design, Analog Devices, 2006, ISBN: 0-915550-28-1. Also available as
Linear Circuit Design Handbook, Elsevier-Newnes, 2008, ISBN-10: 0750687037, ISBN-13: 978-
0750687034. Chapter 12
8. Walt Kester, Analog-Digital Conversion, Analog Devices, 2004, ISBN 0-916550-27-3, Chapter 9. Also
available as The Data Conversion Handbook, Elsevier/Newnes, 2005, ISBN 0-7506-7841-0, Chapter 9.
9. Walter G. Jung, Op Amp Applications, Analog Devices, 2002, ISBN 0-916550-26-5, Chapter 7. Also
available as Op Amp Applications Handbook, Elsevier/Newnes, 2005, ISBN 0-7506-7844-5. Chapter 7.
Copyright 2009, Analog Devices, Inc. All rights reserved. Analog Devices assumes no responsibility for customer
product design or the use or application of customers’ products or for any infringements of patents or rights of others
which may result from Analog Devices assistance. All trademarks and logos are property of their respective holders.
Information furnished by Analog Devices applications and development tools engineers is believed to be accurate
and reliable, however no responsibility is assumed by Analog Devices regarding technical accuracy and topicality of
the content provided in Analog Devices Tutorials.
Page 7 of 7