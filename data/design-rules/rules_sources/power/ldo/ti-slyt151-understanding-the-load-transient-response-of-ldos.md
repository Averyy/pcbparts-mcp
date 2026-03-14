---
source: "TI SLYT151 -- Understanding the Load-Transient Response of LDOs"
url: "https://www.ti.com/lit/an/slyt151/slyt151.pdf"
format: "PDF 6pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 18682
---

Understanding the load-transient
response of LDOs
By Brian M. King
Advanced Analog Products
Introduction
Figure 1. Typical LDO components
Low-dropout linear regulators
(LDOs) are commonly used to
provide power to low-voltage
digital circuits, where point-of-
Input
load regulation is important. In Pass
these applications, it is common Element
for the digital circuit to have
Reference +
several different modes of opera- Error
tion. As the digital circuit switches Amplifier
Input Output
from one mode of operation to Capacitor – Feedback Capacitor Dynamic
another, the load demand on the Load
Network
LDO can change quickly. This
quick change of load results in a
temporary glitch of the LDO out-
put voltage. Most digital circuits
do not react favorably to large
voltage transients. For the digital
circuit designer, minimizing an
LDO’s transient response is an
important task.
LDOs are available in a wide
variety of output voltages and current capacities.Some LDO compensation
LDOs are tailored to applications where a good response to
The primary feedback loop of the LDO, consisting of the
a fast transientis important. The TPS751xx, TPS752xx,
output capacitor, feedback network, error amplifier, and
TPS753xx, and TPS754xx families of LDOs from Texas
pass element, determines the LDO’s frequencyresponse.
Instrumentsare examples of fast-transient-response LDOs.
The unity gain crossover frequency and stability of the
The TPS751xx and TPS753xx families are rated at 1.5 A of
LDO circuit affect the overall transient response of the LDO.
output current,while the TPS752xx and TPS754xx fami-
The crossover frequency affects the settling time of the
lies can provide up to 2 A. All four families use PMOS pass
linear regulator circuit, where the settling time is the time
elements to provide a low dropout voltage and low ground
elapsed from the initial onset of the load transient to the
current. These devices come in a PowerPADTMpackage
time where the output voltage returns to within a few per-
that provides an effective way of managing the power
cent of a steady-state value. A highercrossover frequency
dissipation in a TSSOP footprint.
will decrease the duration of a transient condition. In most
Figure 1 shows the circuit elements of a typical LDO
LDOs, the output capacitor and its associated equivalent
application. The main components within a monolithic
series resistance (ESR) form a dominant pole in the loop
LDO include a pass element, precision reference, feedback
response. Although larger output capacitors tend to
network, and error amplifier. The input and output capaci-
decrease the magnitude of the transient response, they
tors are usually the only key elements of the LDO that are
also tend to increase the settling time.
not contained in a monolithic LDO. There are a number of
The stability of an LDO circuit can be assessed from the
factors that affect the response of an LDO circuit to a load
gain and phase margins of the loop response. A stable reg-
transient. These factors include the internal compensation
ulator will respond to a transient in a smooth, controlled
of the LDO, the amount of output capacitance, and the
manner, while an unstable or quasi-stable regulator will
parasitics of the output capacitor.
produce a more oscillatory transient response. Since the
internal compensation of an LDO is fixed, only the output
capacitor can be adjusted to insure stability. To assist in
This article was adapted from “Optimized LDO Response to Load Transients the proper selection of an output capacitor, LDO manufac-
Requires the Appropriate Output Capacitor and Device Performance” by Brian
turers typically provide limits on the acceptable values of
King in the September 2000 issue of PCIM Power Electronics Systemsby
permission of Primedia’s Intertec Publishing Group. capacitance and ESR.
Figure 2. LDO with secondary loop for fast-transient response
In addition to the main feedback loop,
some LDOs contain a second feedback
loop that allows the LDO to respond Input Output
Pass
faster to large-output transients. This Element
fast-transient loop basically bypasses
the error amplifier stage and drives the Fast
Reference Transient
pass element directly. A symbolic Loop
representation of an LDO with this
Input Output
s F e ig c u on re d a 2 r . y B c y o r m es p p e o n n s d at in io g n f i a s s t s e h r o t w h n a n in the Capacitor Am E p rr l o if r ier Buffer Capacitor
error amplifier compensation, LDOs
that contain this loop are better able to Sampling
minimize the effects of a load transient. Network
The TPS751xx, TPS752xx, TPS753xx,
and TPS754xx families of LDOs from
Texas Instruments are examples of
devices that contain this secondary loop.
Figures 3 and 4 show the transient
response of a TPS75433 with a 100-µF,
55-mΩoutput capacitor to different load transients. The The equivalent model of a typical capacitor is shown in
transient in Figure 3 transitions from no load to 250 mA, Figure 5. All capacitors have an equivalent series resist-
while the transient in Figure 4 steps from no load to 2 A. ance (ESR) and an equivalent series inductance (ESL).
The 250-mA-load transient is not large enough to trigger A number of factors affect the ESR and ESL values, such
the secondary loop. However, the response of the as the package type, case size, dielectric material, temper-
secondary feedback loop is clearly visible in the LDO ature,and frequency. The amount of capacitance, ESR, and
response to the 2-A transient. If the secondary loop were ESL each affect the transient response in a different way.
not present, the voltage drop in Figure 4 would be much To demonstrate the effects of the parasitics of the out-
more severe. put capacitor, a test circuit was built by using a TPS75433
and an adjustable output capacitor model. The capacitor
Output capacitor
model was built using discrete components to model the
Since the LDO cannot respond instantaneously to a tran- ESL, ESR, and capacitance so that the effects of each
sient condition, there is some inherent delay time before parasitic element could be evaluated independently. Small
the current through the pass element can be adjusted to valued air-core inductors were used to model the ESL.
accommodate the increased load current. During this Low-inductance metal film resistors were used to model
delay time, the output capacitor is left to supply the entire the ESR. The capacitance was modeled by combining
transient current. Because of this, the amount of output multiple 10-µF ceramic capacitors in parallel. The low ESL
capacitance and its associated parasitic elements greatly and low ESR of the ceramic capacitors make them good
impact the transient response of the LDO circuit. models of an ideal capacitor.
Figure 3. TPS75433 response to a Figure 4. TPS75433 response to a
250-mA-load transient 2-A-load transient

Equivalent series inductance
Figure 5. Equivalent capacitor model
When a load transient occurs, the first factor that comes
into play is the ESL. The transient response of various
amounts of ESL is shown in Figure 6. The voltage across
the ESL is equal to the product of the inductance and the
rate of change of current. Initially, the ESL voltage is zero.
ESL ESR C
During the rising edge of the current, a negative potential
will appear across the ESL. Once the transient has reached
its final value, the voltage across the ESL will return to zero.
The net result is a negative voltage spike whose width is
determined by the rise time of the transient and whose
magnitude is determined by the slew rate of the transient
step and the ESL value. The ESL value of capacitors is
quite small. However, as the rate of change in current
increases, the ESL-induced voltage may become bother-
some. For this reason, it is a good idea to consider the
ESL when selecting a capacitor for a fast-switching appli- Figure 6. ESL load-transient response
cation, particularly if the load is sensitive to voltage spikes.
Since the parasitic inductance of PWB traces will add in
series with the ESL, a good layout is key to minimizing the
effects of ESL. The inductance of a trace is dependent
upon the geometry of the layout. However, as a general
rule, 10 nH to 15 nH are added for every inch of trace.
Ideally, the input and output capacitors should be located
as close as possible to the LDO. In addition, the entire
LDO circuit should be located as close as possible to the
load. Using planes for the LDO output and its return will
also help to reduce the stray inductance.
Equivalent series resistance
The voltage across the ESR of a capacitor also adds to the
transient response. The voltage across various amounts of
ESR is shown in Figure 7. The ESR voltage is equal to the
product of the capacitor current and the resistance.
Before the transient, while there is no current flowing in
the capacitor, the ESR voltage is zero. As the output
capacitor begins to supply the transient current, the ESR
voltage ramps down proportionally to the rise in load cur-
rent. The voltage across the ESR remains at a steady value
until the LDO begins to respond to the transient condition. Figure 7. ESR load-transient response
After the LDO has responded to the transient, the entire
load current is again supplied by the LDO, and the voltage
drop across the ESR returns to zero. The resulting
response is a negative pulse of voltage. The magnitude of
the load transient and the amount of series resistance
determine the magnitude of the ESR voltage pulse. The
period of the voltage pulse is determined by the response
time of the LDO and is significantly longer than the period
of the ESL voltage spike. Because of the integrating nature
of the LDO error amplifier, the LDO responds faster to
larger dips in output voltage. Basically, a larger dip in
output voltage generates a larger differential error voltage
that causes the error amplifier to drive the pass element
harder. Consequently, the LDO responds faster to larger
voltage drops caused by larger ESR values. As a result, the
period of the ESR-induced voltage droop decreases as the
amount of ESR increases. From a transient point of view,
it is desirable to minimize the amount of ESR. However,
since the ESR and output capacitance form a dominant
pole in the compensation of most LDOs, some finite
amount of ESR is usually required to guarantee stability of
the LDO.
Aluminum electrolytic capacitors are available in a wide
range of capacitance values and case sizes. Because the
Bulk capacitance loss of electrolyte over time limits the useful life of aluminum
electrolytics, reliability can be a concern. The ESR of alu-
The voltage across the actual output capacitance begins to
minum electrolytic capacitors is much higher than that of
decay as the capacitor supplies current to the transient
ceramic capacitors, but it decreases substantially as the
load. The transient response of various amounts of output
voltage rating increases. In addition, aluminum electrolytic
capacitance is shown in Figure 8. The rate of change of
capacitors typically have more ESL than either ceramic or
capacitor voltage is equal to the transient current divided
tantalum capacitors. However, the ESL of aluminum electro-
by the capacitance. While the load is at its new value, the
lyticcapacitors usually is not large enough to cause concern.
capacitor voltage decays at a constant rate until the LDO
While the footprint areas of surface-mount electrolytics
begins to respond. The larger voltage dip associated with a
are comparable to ceramics, they tend to have taller pro-
smaller capacitance value produces a larger error signal at
files than their ceramic counterparts. However, since most
the input of the error amplifier that causes the LDO to
LDO applications require a large amount of capacitance
respond faster. Consequently, as the output capacitance is
(more than 4.7 µF), aluminum electrolytics offer an
increased, the magnitude of the voltage dip decreases,
attractive solution.
while the period of the voltage dip increases. In order to
Tantalum capacitors offer a large capacitance in a com-
minimize the output voltage dip, the amount of bulk
pact size. The low ESR values of tantalums are well suited
capacitance must be increased.
to LDO applications. The ESL of tantalum capacitors
The combined effect of the capacitance, ESL, and ESR
usually is higher than that of ceramic capacitors but less
is shown in Figure 9. In Figure 9, the capacitor consists of
200 µF of capacitance, 33 mΩof ESR, and 100 nH of ESL. than that of aluminum electrolytic capacitors. As with
aluminum electrolytic capacitors, the ESL usually is small
The actual response of a given capacitor will vary depend-
enough not to cause concern in LDO applications. Most
ing on the relative values of the ESR, ESL, and capacitance.
tantalum capacitors have an unsafe failure mode, which
The initial voltage spike during the rising slope of transient
dictates that their operating voltage should be substantially
load will be less pronounced for capacitors with lower ESL
less than their rated voltage (usually less than 50%.)
values. Similarly, the voltage offset caused by the ESR will
Although tantalum capacitors are well suited to LDO
be smaller for smaller values of ESR, and the output volt-
applications, their popularity has skyrocketed in recent
age droop will be smaller for larger values of capacitance.
years, reducing availability and raising cost.
Capacitor technology
Design example
Although there are many types of capacitors, there are
Consider a 3.3-V application that must be able to supply a
three that are most commonly used in LDO applications.
load transient that transitions from no load to 1 A in 2 µs.
These capacitor types include ceramic, aluminum electro-
Assume that the specifications do not allow the output
lytic, and tantalum.
voltage to drop below 3.0 V under any transient condition.
Ceramic capacitors offer a compact size, low cost, and
First, an LDO must be selected that the designer feels can
very low ESR and ESL. Until recently, ceramics were limited
handle the output requirements. Given the high load rating
to about 4.7 µF maximum. However, ceramics up to 22 µF
and the transient requirements, a TPS75333 may be used,
recently have been introduced to the market. In situations
which provides 3.3 V at up to 1.5 A. From the TPS75333
where the low ESR of ceramics becomes a stability problem
data sheet, it can be seen that the minimum guaranteed
for the LDO, a low-value external resistor can be added in
output voltage is 3.234 V. Subtracting the 3.0-V output
series with the capacitor.
Figure 8. Capacitance load-transient response Figure 9. Total capacitor response

requirement from the minimum LDO voltage allows 234 mV
Figure 10. Design example transient response
for the transient.
Next, an output capacitor must be selected that, in con-
junction with the TPS75333, will keep the output at an
acceptable level. First, the ESL requirement must be
checked. The maximum allowable ESL can be calculated
as follows:
∆t 2µs
ESL =V × 1 =234mV× =466nH, (1)
max dip,max ∆I 1A
where V is the maximum allowable voltage dip, ∆t
dip, max 1
is the current rise time, and ∆I is the stepped load change.
In this example, as in most situations, the maximum allow-
able ESL is quite large and will not impact the capacitor
selection.
Next, assume that the response time of the TPS75333 is
going to be around 5 µs. Since LDO response times vary
based on the ESR, capacitance, and the magnitude of the
transient, this information typically is not published in the
data sheets. Consequently, this assumption must be based
on the evaluation or prior knowledge of the part. Having
made this assumption, the voltage droop can be calculated
for different capacitance values. The droop associated References
with the capacitance is given by
For more information related to this article, you can down-
∆I×∆t 1A×5µs loadan Acrobat Reader file at www-s.ti.com/sc/techlit/
∆V C = C 2 = 100µF =50mV, (2) litnumberand replace “litnumber”with the TI Lit. #for
the materials listed below.
where C is the output capacitance and ∆t is the response
2 Document Title TI Lit. #
time of the LDO. Assuming that 100 µF of output capaci-
1. Bang S. Lee, “Technical Review of Low
tance is needed, the associated voltage drop will be about
Dropout Voltage Regulator Operation and
50 mV. Subtracting this 50 mV from the 234-mV allowable
Performance,” Application Report . . . . . . . .slva072
drop leaves 184 mV for the ESR voltage drop.
2. Bang S. Lee, “Understanding the Stable
The maximum allowable ESR can now be calculated:
Range of Equivalent Series Resistance of
ESR max = ∆V ES ∆ R I ,max = 18 1 4 A mV =184mΩ. (3) a J n o u L r D n O a l R ( e N g o u v la e t m or b , e ” r A 1 n 9 a 9 l 9 o ) g , A pp p . p 1 li 4 c - a 1 t 6 io . n . s . . .slyt187
3. Bang S. Lee, “Understanding the Terms
For the assumed 5-µs response time and 100-µF capaci- and Definitions of LDO Voltage
tance, the ESR should be less than 184 mΩ. There are Regulators,” Application Report . . . . . . . . .slva079
numerous electrolytic and tantalum capacitors that meet 4. Joseph G. Renauer, “Challenges in
this requirement. Selecting a 10-V, 100-µF tantalum with Powering High Performance, Low Voltage
55 mΩof ESR should provide plenty of margin in meeting Processors,” Proc. of Applied Power
the specifications. The transient response for this example Electronics Conference, Vol. 2 (1996),
is shown in Figure 10. In fact, the output voltage droops pp. 977-983. —
about 120 mV, which is well within the specifications. 5. Everett Rogers, “Stability Analysis of
Low-Dropout Linear Regulators with a
Summary
PMOS Pass Element,” Analog
Selecting an LDO that is tailored to fast-transient loads is Applications Journal(August 1999),
the first step in minimizing the effects of transients. Equally pp. 10-12 . . . . . . . . . . . . . . . . . . . . . . . . . . . . .slyt194
as important is the selection of the output capacitor.
Related Web sites
Understanding the load requirements and the behavior of
the LDO and output capacitor can provide confidence in http://power.ti.com
the design of a power distribution strategy. With this www.ti.com/sc/docs/products/analog/tps75333.html
understanding, the designer can optimize a design for
www.ti.com/sc/docs/products/analog/tps75433.html
performance, board area, and cost.