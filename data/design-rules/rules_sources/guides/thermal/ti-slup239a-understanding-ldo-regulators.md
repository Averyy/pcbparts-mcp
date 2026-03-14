---
source: "TI SLUP239A -- Understanding LDO Regulators"
url: "https://www.ti.com/lit/ml/slup239/slup239.pdf"
format: "PDF 9pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 17822
---

Portable Power Design Seminar
Understanding Low Drop Out (LDO)
Regulators
2006 Texas Instruments Portable Power Design Seminar
Topic 9
TI Literature Number: SLUP239A
© 2006, 2019 Texas Instruments Incorporated
All rights reserved

Understanding Low Drop Out (LDO) Regulators
Michael Day, Texas Instruments
ABSTRACT
This paper provides a basic understanding of the dropout performance of a low dropout linear regulator
(LDO). It shows how both LDO and system parameters affect an LDO’s dropout performance, as well
as how operating an LDO in, or near, dropout affects other device parameters. Most importantly, this
paper explains how to interpret an LDO’s datasheet to determine the dropout voltage under operating
conditions not specifically stated in the datasheet.
I. INTRODUCTION III. UNDERSTANDING LDO
Low dropout regulators (LDOs) are a simple For standard regulators, the pass element is
inexpensive way to regulate an output voltage either a Darlington NPN or PNP output stage.
that is powered from a higher voltage input. They Fig. 1 shows that a Darlington transistor has a
are easy to design with and use. For most high collector-to-emitter voltage drop because the
applications, the parameters in an LDO datasheet gate drive voltage encounters two base-to-emitter
are usually very clear and easy to understand. drops before reaching the output. Standard linear
However, other applications require the designer regulators have voltage drops as high as 2 V
to examine the datasheet more closely to which are acceptable for applications with large
determine whether or not the LDO is suitable for input-to-output voltage difference such as
the specific circuit conditions. Unfortunately, generating 2.5 V from a 5 V input.
datasheets can’t provide all parameters under all
possible operating conditions. To the designer
NPN Darlington Pass Element
must interpret and extrapolate the available V V
IN OUT
information to determine the performance under
non-specified conditions.
II. LINEAR REGULATORS
There are two types of linear regulators:
Gate
standard linear regulators and low dropout linear
Drive
regulators (LDOs). The difference between the
two is in the pass element and the amount of
headroom, or dropout voltage, required to
maintain a regulated output voltage. The dropout
voltage is the minimum voltage required across N-Channel FET Pass Element
V V
the regulator to maintain regulation. A 3.3 V IN OUT
regulator that has 1 V of dropout requires the
input voltage to be at least 4.3 V. The input
voltage minus the voltage drop across the pass
element equals the output voltage. This brings up
the question, “What is the minimum voltage drop
Gate
across the pass element?” The answer to this
Drive
question depends upon several factors.
Fig.1. LDO pass elements.

A typical application such as generating For example, with the following operating
3.3 V from a 3.6 V Li-Ion battery requires a conditions: V =5 V, V =3.3 V, and
much lower dropout voltage (less than 300 mV). I =500 mA, the LDO pass device behaves
LOAD
These applications require the use of an LDO to like a 3.4-Ω resistor. This equivalent resistance is
achieve the lower dropout voltage. Most LDOs determined by calculating the voltage drop across
use an N-channel or P-channel FET pass element the LDO and dividing by the load current:
and can have dropout voltages less than 100 mV.
(5 V-3.3 V)/0.5 A = 3.4 Ω. (1)
Fig. 1 shows that the dropout voltage of an N-
channel FET LDO is only dependent upon the Under these specific application operating
minimum voltage drop across the FET. This conditions, the LDO can be replaced by a
voltage drop is a function of the R of the 3.4 Ω.resistor with no change in output voltage or
DS(on)
FET. current. In a practical application, however,
Fig. 2 shows an LDO block diagram in its operating conditions are never static; therefore,
most basic form. The input voltage is applied to a feedback is necessary to change the LDO’s
pass element, which is typically an N-channel or effective resistance to maintain a regulated output
P-channel FET, but can also be an NPN or PNP voltage.
transistor. The pass element operates in the linear Fig. 3 shows the operating region of an
region to drop the input voltage down to the LDO’s N-channel pass element. The range of
desired output voltage. The resulting output operation is limited in the x-axis by the saturation
voltage is sensed by the error amplifier and region of the pass element, and limited in the y-
compared to a reference voltage. The error axis by either the pass element’s saturation region
amplifier drives the pass element’s gate to the or by the IC’s programmed current limit. In order
appropriate operating point to ensure that the to operate properly and maintain a regulated
output is at the correct voltage. As the operating output voltage, the pass element must operate
current or input voltage changes, the error within the boundaries set by these two lines. In
amplifier modulates the pass element to maintain the example, the drain-to-source voltage of 1.7 V
a constant output voltage. Under steady state and the drain current of 500 mA set the operating
operating conditions, an LDO behaves like a point at “A.” At this point, the LDO sets the pass
simple resistor. element’s gate-to-source voltage at 3 V to
maintain regulation. A line drawn through the
origin and point “A” represents the 3.4 Ω
resistance.
5 V V V 3.3 V
Pass Element
Error Amplifier
+
Gate Load
Drive +
V
REF
Fig. 2. LDO block diagram.

.
0.5
0
0 0.5
A
-
tnerruC
daoL
=
tnerruC
niarD
When considering a decrease in input voltage,
the pass element must reduce its drain-to- source
e
n voltage to keep the output in regulation. If V is
Li IN
n LDO's Programmed reduced to 4 V, the operating point moves to “C.”
1.0 o
ur
ati Current Limit
This point represents a 1-Ω .resistance. Note that
S
at
the gate-to-source voltage remained unchanged.
D C V GS = 3.5 V B Any further increase in current or decrease in
input voltage forces the operating point onto the
V = 3.0 V saturation line of the pass element. At this point,
GS A
the LDO is said to be in “dropout.” The
saturation line is the minimum FET drain-to-
V GS = 2.5 V source resistance (R DS(on) ). If the system
operating conditions dictate that the LDO operate
at point “D”, the LDO cannot reduce the drain-to-
source voltage any further to stay in regulation.
In practice, this results in the output voltage
1.0 1.5 2.0
falling out of regulation. The pass element now
V = V - V (V)
DS IN OUT
operates up and down the saturation line to
Fig. 3 Operating region of an LDO’s N-channel
correspond with changes in input voltage, or load
pass element.
resistance. Note that a line drawn from the origin
Consider a change to the static conditions in through the saturation line represents the FET’s
the example: if the load resistance decreases (an minimum R . If this were a 1A LDO, it
increase in load current), the LDO must react to would have a datasheet dropout rating of 800 mV
maintain regulation. If it doesn’t react, the LDO at 1 A. Note that when the LDO is operated at a
has a higher voltage drop across the pass element fraction of its rated output current, its dropout
which causes the output voltage to fall out of voltage is a fraction of the maximum specified
regulation. The LDO must decrease the pass dropout voltage.
element’s resistance by increasing the gate-to- LDO datasheets can only specify the IC’s
source voltage on the FET. When the gate-to- dropout voltage under a limited number of
source voltage increases, the operating point operating conditions. Few datasheets provide a
moves upward, assuming a fixed input and output graph like that shown in Fig. 3. For all other
voltage. If I =700 mA, the error amplifier conditions, the user must interpolate the data to
OUT
increases the pass element’s gate-to-source determine the dropout voltage at a specific output
voltage to 3.5 V to maintain regulation. This current. This task is surprisingly easy. As an
corresponds to “B.” A line drawn through the example, consider an application that requires
origin and point “B” now represents a pass V = 3 V at 170 mA with an input voltage that
element resistance of 2.4 Ω. Fig. 3 shows that varies between 3.15 V and 3.45 V. The designer
with a drain-to-source voltage of 1.7 V, the has chosen a TPS79330 LDO and needs to know
LDO’s maximum current draw is only limited by if it can be ensured that the LDO doesn’t enter
the maximum programmed current limit. dropout.

Table 1 shows the datasheet’s ensured Several factors affect an LDO’s minimum
dropout voltage from the parametric table. The dropout resistance. The main contributor is the
datasheet shows that the maximum dropout size of the pass element. A characteristic of both
voltage (ensured over all temperatures) for a discrete FETs and an LDO’s integrated FET is
3.0 V output at 200 mA is 200 mV. The that their resistance is inversely proportional to
minimum input voltage of 3.15 V for this the die-size. With all other factors being equal, a
application requires the effective dropout voltage larger die-size has a lower resistance. Fig. 6
be less than 150 mV at 200 mA. For this shows a graph of minimum LDO resistance
regulator, the actual dropout is less than 200 mV versus package-size for several different LDOs.
since the current is less than 200 mA, but the This graph is not linear for two reasons: the
datasheet does not specify the dropout voltage at entire package size is not devoted to the pass
170 mA. When operating in dropout, the LDO element, and because not all LDOs are produced
pass element is at its minimum R which is with the same manufacturing process. This graph
equivalent to operating on the saturation line like shows that an extremely low dropout voltage may
the one shown in Fig. 3. This minimum be achieved by using a larger LDO at only a
resistance is calculated by dividing the dropout fraction of its maximum current rating.
voltage by the test current. The TPS79330 pass
10.0
element minimum R is shown in Equation SC-70
(3).
R = 200 mV/200 mA = 1 Ω. (3)
The dropout voltage at any other current is
calculated by multiplying this minimum R
by the actual load current. Operating at lower SOT-23
1.0
currents corresponds to moving down and to the
MSOP-8
left on the saturation line. Since the R is
known, the dropout voltage in this application is
calculated as
SOT-223
V = 1 Ω • 170 mA = 170 mV. In this
DO
example, this is still not low enough to ensure
PWP-20 regulation. The designer must find an LDO with
0.1
a lower dropout voltage at 170 mA to meet 0 10 20 30 40
Size - mm2
requirements desired.
Ω
ecnatsiseR
ecruoS-ot-niarD
TEF
R
)no(SD
Fig. 6. R variability by package-size.
TABLE 1. TPS79330 ENSURED DROPOUT VOLTAGE
PARAMETER TEST CONDITIONS Min Typ Max Units
TPS79328 I – 200 mA 120 200
TPS793285 I – 200 mA 120 200
Dropout voltage(2) OUT
TPS79330 I – 200 mA 112 200 mV
(V = V – 0.1 V) OUT
IN OUT(nom) TPS79333 I – 200 mA 102 180
TPS793475 I – 200 mA 77 125
TABLE 2. TPS79430 ENSURED DROPOUT VOLTAGE
PARAMETER TEST CONDITIONS Min Typ Max Units
TPS79428 I – 250 mA 155 210
Dropout voltage(2) OUT
TPS79430 I – 250 mA 155 210 mV
(V = V – 0.1 V) OUT
IN OUT(nom) TPS79433 I – 250 mA 145 200

Another factor affecting an LDO’s minimum
dropout resistance is the input voltage to the
device. This is a second-order effect, but is worth
noting. The higher output voltage options require
a higher input voltage, which allows the device to
drive the pass element harder, and in turn
provides a slightly lower resistance. Most
discrete FET datasheets show a change in R
versus gate-to-source voltage. Some LDO
datasheets provide a graph (Fig. 7) of dropout
versus input voltage, but this is rare. Even
without a graph, this information is evident from
the dropout data shown in Fig. 4. The 3.0-V
option (TPS79330) in Fig. 3 has a 200-mV
dropout voltage while the 4.75-V option
(TPS793475) has a 125-mV dropout voltage.
This is a 37 % reduction in dropout voltage.
110
100 I = 200 mA OUT
90
80
70
60
50
40
30
20
10
2.5 3.0 3.5 4.0 4.5 5.0 5.5 6.0 6.5 7.0
V - Input Voltage - V IN
Vm
egatloV
tuoporD
V
DD
output voltage is measured. The dropout voltage
is the differential between the input voltage and
the output voltage. If V is 2.9 V, the LDO has
a 300 mV dropout voltage. An LDO tested in this
method has a note similar to that shown below.
V = V – 0.1 V (4)
IN OUT(nom)
Another test method is to measure the output
voltage when V is 1 V above the nominal IN
output voltage and then load the LDO with the
specified test current. The input voltage is then
reduced until V drops by a specified number OUT
of millivolts. For example, 4.3 V is applied to a
3.3-V LDO. The output voltage is measured
(assuming at 3.3 V), and then the input voltage is
reduced until the output voltage measures 3.2 V.
Dropout is defined as the input voltage minus the
output voltage at this point. If V = 3.5 V when
IN
V = 3.2 V, the LDO has a 300-mV dropout
voltage. An LDO tested in this method will have
a note similar to that shown below.
“Dropout voltage is defined as the
differential voltage between V and V when
OUT IN
V drops 100 mV below the value measured
with V = V + 1 V “ IN OUT
Some LDO parameters are affected when an
LDO is in or near dropout. One parameter
affected is the power supply rejection ratio
(PSRR). Most manufacturers specify and
measure PSRR with an input voltage that is 1 V
above the nominal output voltage. This
specification and measurement ensures that the
Fig. 7. TPS79901 dropout voltage vs. input LDO is not on the edge of dropout when PSRR is
voltage. measured. PSRR is measured by modulating the
input voltage to the LDO and measuring the
Different manufacturers test dropout
change on the output. The test results are only
differently which leads to confusion when
valid if the LDO’s pass element stays in the
reading different datasheets. Even various LDOs
active region. If the LDO starts to enter dropout,
from the same manufacturer are tested
the data is invalid. When the LDO starts to enter
differently, and one method is not necessarily
dropout, the error-amplifier output voltage
better than another. The choice to test one way or
reaches a maximum value because it is trying to
another is typically driven by manufacturing and
drive the pass element harder to maintain
test constraints. One test method is to apply an
regulation.
input voltage that is some number of millivolts
below the nominal output voltage and then load
the LDO with the test current. For example,
3.2 V is applied to a 3.3-V LDO and then the

At that point, the error amplifier is said to be
in saturation. Since the pass element is already in
saturation, its resistance is at the minimum value
and cannot be decreased any further. .
At this point, the LDO cannot react to
changes in the input voltage and the PSRR drops
significantly. This data is not typically provided
in LDO datasheets and the user is left to generate
these curves on their own. Fig. 8 shows a typical
plot of PSRR versus an LDO’s input to output
voltage differential. The LDO starts entering
dropout at about V -V =0.4 V. If high PSRR
IN OUT=
is a system requirement, LDOs should be
operated with enough headroom to stay away
from the saturation region. For most LDOs, this
is usually about 1 V.
40
35
30
25
20
15
10 f = 100 kHz
OSC
C = 10 μF OUT
5 V = 2.5 V
0 0.4 0.8 1.2 1.6 2.0
V = V - V (V)
DS IN OUT
Bd
oitaR
noitcejeR
ylppuS
rewoP
- RRSP
Entering dropout also affects an LDO’s
output noise. An LDO’s output noise is reduced
when the LDO is in or near dropout. All bandgap
references (V ) produce noise, and in an LDO,
REF
the bandgap noise is fed directly into the error
amplifier as shown in Fig. 1. The noise on the
output of the amplifier modulates the pass
element’s gate voltage which generates noise on
the LDO output. When an LDO is in dropout, the
error amplifier output voltage is at its maximum,
and its ability to pass bandgap noise from its
input to its output is reduced. This reduces output
noise. This feature is sometimes used with
standard LDOs in a low noise application like
powering a phased lock loop (PLL). If tight
regulation is not needed, the LDO can be
intentionally operated in dropout to provide this
feature. For example, a 3.3-V LDO can be
powered from a 3.3-V input to drive a PLL that
requires a low noise input, but not a tightly-
regulated input. The input voltage to the PLL is
3.3-V minus the LDO dropout voltage. If the
LDO has a high-current rating and the PLL has a
low-load current, the dropout voltage may be 50
mV or lower. A drop of 50 mV is only 1.5% of a
3.3-V output. However, PSRR may be a big
concern in this case. The user must determine the
tradeoff between PSRR and low-noise
performance. If the input voltage has a lot of
power supply ripple voltage, a high PSRR, low
noise LDO must be used. If the input voltage
comes from a battery or another LDO and has
very little ripple, a standard LDO can be used in
Fig. 8. Typical LDO power supply rejection ratio dropout to achieve a low noise output.
vs V - V
IN OUT.
CONCLUSION
In summary, LDO dropout is rarely specified
for a designer’s specific operating conditions.
The actual dropout is easily determined by
interpolating the available datasheet information.
LDO dropout is influenced by FET size and input
voltage, and LDOs entering dropout affect circuit
performance. Once a designer understands this
information, he can select an LDO that is
optimized for his specific circuit requirements.