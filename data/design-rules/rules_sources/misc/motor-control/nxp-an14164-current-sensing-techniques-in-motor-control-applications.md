---
source: "NXP AN14164 -- Current Sensing Techniques in Motor Control Applications"
url: "https://www.nxp.com/docs/en/application-note/AN14164.pdf"
format: "PDF 20pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 40786
---

Current Sensing Techniques in Motor Control Applications
Rev. 1.0 — 21 February 2024 Application note
Document information
Information Content
Keywords Current sensing, sensing techniques, motor control
Abstract There are many ways of current measurement in motor control or power electronics applications.
Moreover, electrical current can be measured with different sensor types. The selection of
appropriate current sensors together with appropriate current sensing strategy is therefore a
complex issue. System requirements need to be analyzed and appropriate current sensor and
sensing technique need to be selected. This document focuses on current sensors based on
Ohm’s law and low-side or DC Bus current sensing approach.

NXP Semiconductors AN14164
1 Introduction
Measurement of current is an essential process in every power electronics system. Measured current signals
can be processed for monitoring purposes in less complex systems or can be processed to suit control
purposes in complex and more sophisticated systems.
There are many ways of current measurement in power electronics applications. Moreover, electrical current
can be measured with different sensor types. The selection of appropriate current sensors together with the
appropriate current sensing strategy is therefore a complex issue. System requirements need to be analyzed
and appropriate current sensor and sensing techniques need to be selected.
2 Current sensors
Electric current represents one of the most important and high dynamic feedback signals in motor control
applications. Current feedback accuracy is crucial for current control loop and observers. Current sensors work
based on specific physical laws and can be categorized as follows:
• Current sensors based on Ohm’s law.
• Current sensors based on Faraday’s law.
• Current sensors based on electromagnetic field laws.
• Current sensors based on the Faraday effect.
The current sensing technique in the power electronic systems can be categorized according to the placement
of the current sensor in the power path:
• High-side current sensing approach.
• Low-side current sensing approach.
• Phase current sensing approach.
• DC bus current sensing approach.
This document focuses on current sensors based on Ohm’s law and low-side or DC bus current sensing
approach.
3 Current sensing techniques based on Ohm’s law
Current sensors based on Ohm’s law are called shunt resistors. These sensors are widely used in many
application domains, especially in automotive, due to their cost and simplicity benefits. They allow to sense DC
and AC current, sense current bidirectionally and cope well with high dynamic currents.
Shunt resistors are connected to power circuitry in series. Their nominal resistance is relatively small, typically
around several milliohms. Higher resistance is not recommended due to additional power losses. The low
nominal resistance of the shunt resistor brings challenges with the signal/noise ratio. Therefore, there is always
a trade-off between power loss reduction and the signal/noise ratio. The voltage drop over the shunt resistor is
low and usually does not have a noticeable impact on the performance of the connected motor. In applications
comprising an analog-to-digital converter (ADC), the current signal (shunt resistor voltage drop) must be further
processed by the conditioning circuitry. This voltage drop is amplified to the range of ADC. The current signal in
the form of voltage drop is linear dependent on the current flowing through the shunt resistor.
Benefits of such sensors are low cost, simplicity, stability, and linearity.
4 Low-side current sensing
In the case of low-side current sensing, shunt resistors are connected between low-side transistors and a
negative DC bus terminal.
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
Application note Rev. 1.0 — 21 February 2024
2 / 20

There are two low-side current sensing techniques available:
• Triple-shunt
• Dual-shunt
4.1 Triple-shunt
Triple-shunt current sensing technique employs a current sensing resistor in each phase leg of a power inverter.
Figure 1 depicts schematic of power inverter using low-side triple-shunt current sensing approach and
waveforms of duty cycles, phase currents, and currents flowing through shunt resistors. Shunt resistors R ,
A
R R are inserted between the respective low-side transistor (T , T , T ) and the negative DC link terminal.
B, C 2 4 6
The current flowing through the motor windings and subsequently through the low-side transistors and shunt
resistors creates a voltage drop across these shunt resistors. The voltage drop is proportional to the current
according to:
(1)
The voltage drop across the shunt resistors is further processed by differential operational amplifiers (OP
amps) and amplified to exploit the range of the ADC best. The current flowing through the shunt resistor is then
calculated in the software (SW) based on Equation 1.
ON/OFF states of the transistors, motor phase currents, and shunt resistor currents are illustrated in Figure 1.
It is obvious that the shunt resistor current is equal to the motor phase current only if the respective low-
side transistor is switched on, that is: current i readings are valid only if low-side transistors T
RA,RB,RC 2,4,6
are switched on. Therefore, the current measurement (ADC conversion) and pulse-width modulation (PWM)
switching algorithm need to be synchronized.
- deadtime
T 1 T 3 T 5 T 1
T
2
3
i
A T
4
B Motor T
V DC i C 5
T 2 T 4 T 6 T 6
B
R A R B R C i
i RA i RB i RC C
RA
V V V
RA RB RC i
RB
ADC i
RC
time
Figure 1. Low-side triple-shunt current sensing technique – principal topology, switching states and current
waveforms during one PWM period
The synchronization not only needs to consider the switching states of the transistors, but also the conversion
time of the ADC needs to be considered. If the low-side transistor is opened for a time period shorter than the
ADC conversion time, the current reading will be inaccurate. Moreover, the current reading needs to be done in
steady state to avoid transients and disturbances caused by transistor switching.
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
3 / 20

The ADC conversion events, PWM algorithm and their synchronization are explained in Figure 2, where duty
cycle waveforms and switching patterns of space vector modulation (SVM) technique are shown. SVM is
commonly used in modern electric drives. It is based on center-aligned PWM patterns, which allow to measure
average motor currents (per PWM cycle) easily.
sector I. sector II. sector III. sector IV sector V. sector VI.
1
0.8
0.6
0.4
0.2
0
].u.p[
elcyc
ytuD
PWM A
PWM B
PWM C
T1
Phase A
T2
Phase B
T3
T4
T5
Phase C
T6
time calculated current
measured current
ADC sampling point
Figure 2. Triple-shunt - SVM duty cycle waveforms and switching states examples
The inverter topology shown in Figure 1 is assumed. Current samples are taken in the middle of the PWM
period. The average PWM period current value can be measured in this manner. The currents are obtained
simultaneously in all 3 phases, that assures the current feedback to the motor controller is in accordance with
real-time motor behavior. (As Park, Clarke transformations, observers/estimators, and current controllers need
simultaneous phase current readings in order to produce accurate results).
Observe that in the middle of each sector the duty cycle of one of the phases reaches 100% (provided there is
max. DC Bus voltage utilization). In such a case it is impossible to measure the phase current as the low-side
transistor will be open (and the high-side transistor closed) throughout the whole PWM period. Therefore, valid
current measurements of the corresponding phase cannot be obtained during certain periods of the respective
sector duration. Due to this reason, two of the phase currents are measured and the remaining current (which
reaches 100% duty cycle) is calculated based on the assumption of symmetrical inverter load (which is fulfilled
by a 3-phase motor under normal operating conditions):
(2)
The calculated and measured current values are acquired in the corresponding SVM sectors according to
Table 1. In each sector two phase currents are measured and the remaining current is calculated.
Table 1. Phase currents acquisition vs SVM sector
SVM sector 1 2 3 4 5 6
Phase A current measured measured measured measured
Phase B current measured measured measured measured
Phase C current measured measured measured measured
This approach does allow full DC Bus voltage utilization and requires only 2 ADC modules to obtain motor
currents simultaneously. Since in each sector 2 currents are measured (the third one is calculated), one ADC
module per measured current is necessary for their simultaneous A/D conversion. It is also possible to achieve
redundancy for current measurement. In that case, the full utilization of DC Bus needs to be sacrificed in
exchange for having the current sensing circuit in one phase available as a backup if one of the remaining
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
4 / 20

current sensing circuits should fail. In that case, the setup is operated as a dual-shunt and if a failure occurs
then the current reading is taken from the backup current sensing circuitry.
The disadvantage of the triple-shunt method is its higher cost because the shunt resistor and the OP amp
conditioning circuitry in each phase is necessary.
4.2 Dual-shunt
The higher cost disadvantage of the triple-shunt method can be dealt with by using Equation 2. If two-phase
currents are measured (for example, i and i ) throughout all SVM sectors and the remaining current (i ) is
a b c
calculated, then only 2 shunt resistors and 2 OP amp circuits are necessary. The resulting topology is illustrated
in Figure 3.
T1 T3 T5 T1
T2
iA
T4
VDC i i C B Motor T5
T2 T4 T6 T6
iB
iRA
RA
iRB
RB
iC
iRA
VRA VRB
iRB
ADC iC
(calculated)
Figure 3. Low-side dual-shunt current sensing technique – principal topology, switching states and current
waveforms during one PWM period
As explained in the chapter 4.1 and Figure 2 , in case of full DC Bus voltage utilization (operation with 100%
peak duty cycle) there is always one phase per sector, where current cannot be measured. As there is now
no option to select in which two phases the current is to be measured (dual-shunt configuration), the required
output voltage amplitude (that is, duty cycle) has to be limited. The duty cycle limit needs to be set in a way that
the low-side transistor minimum ON time is longer than ADC conversion time. Since we consider symmetrical
PWM pattern and measurement in the middle of the PWM period, the minimum low-side transistor ON time
needs to be equal or larger than 2*ADC conversion time (in a real system also transient settling and deadtime
need to be considered). The situation is depicted in Figure 4.
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
5 / 20

Figure 4. Dual-shunt - SVM duty cycle waveforms and switching states examples
As mentioned earlier, the advantage of this method compared to triple-shunt is the bill of material reduction but
at the cost of DC Bus voltage not being fully utilized.
5 DC Bus current sensing – single shunt
5.1 DC bus current sensing – phase current reconstruction
If measuring the DC Bus current, the shunt resistor needs to be placed in series with the negative pole of the
DC Bus. The method is shown in Figure 5.
This method is called single-shunt and relies upon the fact that while there is a switching combination in the
inverter corresponding to an active vector, the DC Bus current is equal to one of the motor phase currents or its
inverted value (depending on the active vector).
This statement is explained in Figure 6. In the middle of the picture there are the active voltage vectors available
(each vector is pointing at its physical representation in the inverter - schematic with corresponding switching
combination). For each switching combination there is a DC Bus current either flowing to one motor phase and
st
flowing out of the remaining two phases or vice versa. By applying 1 Kirchhoff’s law, the DC Bus current is
equal to the current of the phase, which has an opposite direction than the currents of the remaining phases. If
the current of this phase flows to the motor, then it is equal to the DC Bus current, if it flows from the motor then
its inverted value is equal to the DC Bus current.
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
6 / 20

T T T
1 3 5
B Motor
V DC i C
2 4 6
R
DC
RDC
V
ADC
Figure 5. Single-shunt current sensing (DC Bus current sensing) principal topology
A B C A BC
i RDC = i B i RDC = -i C
V3 V2
II.
A B C V4 III. I. V1 A B C
i RDC = -i A IV. VI. i RDC = i A
V.
V5 V6 iRD
Currents
DC BUS
P P P h h h a a a s s s e e e A B C A B C A B C
i RDC = i C i RDC = -i B
Figure 6. SVM active vectors, switching states and current flow
As shown in Figure 6, during each inverter switching state (applies to active voltage vector only!), only one
phase current can be measured. However, all three phase currents need to be known to the control system
to control the motor properly. As obvious from Equation 2 at least two currents need to be measured and the
remaining one can be calculated. Ideally, the two currents are measured simultaneously. Since this cannot be
achieved during one switching state in the case of single-shunt configuration, two phase current readings need
to be acquired from two different consecutive active voltage vectors, preferably within one PWM period.
Figure 7 depicts typical SVM switching patterns for corresponding sectors. For each sector, an example of one
PWM cycle is shown.
The creation of the demanded voltage vector and switching patterns for sector I are displayed in Figure 8. The
rotation of the demanded vector V creates a rotational magnetic field in the motor. One rotation of the vector
represents one electrical rotation of the motor. As per the picture, the demanded vector V can be created by
vector combination of the inverter vectors, which create boundaries of the actual sector in which vector V is
located (that is, vectors V1 and V2 for sector I.).
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
7 / 20

sector I. sector II. sector III. sector IV sector V. sector VI.
0.8
0.6
0.4
0.2
T1
T5
iB
iC
iRDC
Vector V0V1V2 V7 V2V1V0V0V3V2 V7 V2V3V0V0V3V4 V7 V4V3V0V0V5V4 V7 V4V5V0V0V5V6 V7 V6V5V0V0V1V6 V7 V6V1V0
se iRnDsCe iA-iC -iCiA iB-iC -iCiB iB-iA -iAiB iC-iA -iAiC iC-iB -iBiC iA-iB -iBiA
].u.p[
elcyc
ytuD
PWM A
PWM B
PWM C
Figure 7. SVM switching patterns, phase, and DC Bus current waveforms for corresponding SVM sectors
Deadtime
II. V T 3
III. V2
V4 I. V1 5
V1 A
IV. VI. i
B
C
V5 V6 i A1 i A_avg i A2
-i C1-i
C_avg
-i
C2
Vector V0V1V2 V7 V2V1V0
i RDC i A-i C -i C i A
sense
Figure 8. SVM – decomposition of demanded voltage vector, resulting center-aligned switching pattern and
current measurement opportunities
The demanded angle and amplitude of V is obtained by the corresponding mutual ratio of switch-on intervals of
V1 and V2 and by the insertion of zero vectors V0 (all low-side transistors ON) or V7 (all high-side transistors
ON). The resulting center-aligned switching pattern allows for measurement of two motor phase currents in
each PWM period half. Since the current varies throughout the PWM period, better measurement accuracy and
motor control performance can be achieved by measuring the respective current in both of the PWM period
halves and then calculating the average current value. The average values of the two currents are then also
closer to each other timeline-wise compared to the consecutive readings acquired in the first and second half of
the PWM period.
To be able to take valid current readings, the switch-on interval of either of the vectors needs to be equal to
or greater than the ADC conversion time. This cannot be fulfilled close to the sector boundaries and at low
amplitudes of the demanded voltage vector V. As seen in Figure 9 (dead times are neglected for the sake of
picture clarity), while operating close to sector border, one of the active vectors is switched on for times shorter
than ADC sample time (and ultimately it is not switched on at all at the sector border). During the operation with
low voltage amplitude neither of the active vectors is switched on long enough to enable valid current readings.
This results into a “critical zone” where no reliable current measurements can be taken as per Figure 10.
The workaround for being able to take current readings while operating in the critical zone is to deform the
standard SVM pattern in a way that there will be sufficient measurement windows and the average voltage
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
8 / 20

vector produced during the PWM period will be identical to that produced by the standard SVM. This document
introduces the following techniques:
• Phase-shifted PWM
• Double switching
Figure 9. Operation close to the sector border (left) and operation with low voltage amplitude (right)
II.
III. I.
V4 V1
IV. VI.
Critical zone
V5 V6
Figure 10. Demanded vector with valid current readings (green) and demanded vector in critical zone (red)
5.2 Phase-shifted PWM
The principle of phase-shifted PWM is the creation of an appropriate sampling window by shifting one of the
phase patterns, which form an insufficient sampling window. In the case of standard SVM the duty cycles of the
three phases for the particular sector are defined as per Table 2. The phase with the longest duty cycle duration
is shifted to the left. The phase with the shortest duty cycle duration is shifted to the right and the phase with the
duty cycle of mid-length is kept unshifted.
Table 2. Phase duty cycle comparison vs sector
Sector I. II. III. IV. V. VI.
Phase duty cycle
A > B > C B > A > C B > C > A C > B > A C > A > B A > C > B
comparison
The resulting voltage vector of the original SVM pattern and the resulting voltage vector of the phase-shifted
pattern are the same. The situation is illustrated in Figure 11 and Figure 12. If the current sampling windows
are sufficient, the SVM pattern is kept “as is”. In the case of a too narrow sampling window the phase shift is
employed. If the insufficient sampling window occurs between the longest and mid-length phase duty cycles,
then the longest duty cycle phase is shifted to the left. If the insufficient sampling window occurs between the
mid-length and the shortest phase duty cycles, then the shortest duty cycle phase is shifted to the right. In the
case of low demanded voltage both of the shifts (to the left and to the right) may occur.
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
9 / 20

As shown in Figure 11 and Figure 12, phase-shifted PWM does not allow symmetrical current readings.
Therefore, the average current values cannot be calculated. The measured phase currents can be far from
each other timeline-wise what may cause inaccuracies in the case of motors with low electrical time constants
at high speeds, especially in sensorless motor control systems where the motor speed is calculated based on
measured motor currents. As with such motors the current varies rapidly and only a couple of current samples
per electrical revolution can be acquired at high speeds.
The advantage of phase-shifted PWM is the unchanged amount of switching operations, therefore unchanged
switching losses compared to the standard SVM. The method (and the necessary deformation of the switching
patterns) is only applied in the critical zone, otherwise the switching patterns are unchanged.
Figure 11. Phase-shifted PWM – shifting the phase with the shortest duty cycle duration to the right
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
10 / 20

Figure 12. Phase-shifted PWM – shifting the phase with the longest duty cycle duration to the left
5.3 Double switching
5.3.1 The basics of double switching method
The principle of the double switching method is the creation of an appropriate sampling window in two stages:
1. Insertion of zero pulse to the middle of the PWM pattern. This divides the PWM period into two halves and
creates two symmetrical half-pulses per phase per PWM period. The sum of the two half-pulse lengths
needs to be the same as the length of the original pulse. The width of the zero pulse needs to be stipulated
so that the inverter transistors are reliably switched on and off.
2. Shifting the halves of one of the phase patterns (which form an insufficient sampling window) to the sides.
In the case of standard SVM, the duty cycles of the three phases for the particular sector are defined as per
Table 2. The phase with the duty cycle of the shortest length is kept as is and either the halves of the phase
with the longest or mid-length duty cycle are shifted to the sides.
The resulting voltage vector of the original SVM pattern and the resulting voltage vector of the double-switched
pattern are the same. The situation is illustrated in Figure 13 and Figure 14. If the current sampling windows
are sufficient, the SVM pattern is kept only with the zero pulse inserted and no additional shifting occurs. If
there is a too narrow sampling window the phase shift of the half-pulses to the sides occurs. In the case of low
demanded voltage both of the shifts (of the phase with longest and mid-length duty cycle) may be necessary.
Due to the insertion of the zero pulse and moving of the patterns to the sides, the limitation of the output voltage
is necessary. The limit is approximately 93% of the full duty cycle.
The double switching algorithm evaluates the width of the sampling window and calculates the necessary
shifts in multiple stages as per Figure 15, to consider newly shifted mid-length pulse halves when checking the
available sampling window between the longest and mid-length pulse.
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
11 / 20

As shown in Figure 13 and Figure 14, double-switched PWM allows symmetrical current readings. Therefore,
the average current values can be calculated. This gives better performance, especially at high speeds in the
case of motors with low electrical time constants as opposed to phase-shifted PWM.
The disadvantage of the method is double the switching frequency compared to the standard SVM, resulting
into higher switching losses. The impact of higher switching losses can be reduced by modifications of the
double switching method:
• Adaptive double switching
• Adaptive double switching in one phase only
keep the pattern ¨as is¨
2.too narrow? create appropriate sampling window by phase shift
1.Insert zero pulse to the middle
T 1 T 1 T 1
T 3 T 3 T 3
T 5 T 5 T 5
Vector V1 V7 V1 Vector V1 V7 V7 V1 Vector V1V2V7 V7V2 V1
s i e R n D s C e i A i A V0 s i e R n D s C e i A i A V0 s i e R n D s C e i A -i C -i C i A V0
V2 V2 V2 V6
V3 V2 V3 V2
II. II.
III. V2 I. V III. V2 I. V
V4 V1 V4
V1 V1
IV. VI. IV. V6 VI.
V. V.
V5 V6 V5 V6
Sum of the active vectors gives the same resulting vector
Figure 13. Double switching – shifting the phase with the mid-length duty cycle duration to the sides
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
12 / 20

2.too narrow? create appropriate sampling window by phase shift
1.Insert zero pulse to the middle
1 1 1
3 3 3
5 5 5
Vector V2 V7 V2 Vector V2 V7 V7 V2 Vector V1 V2 V7 V7 V2 V1
i V0 i V0 i V0
se R n D s C e -i C -i C se R n D s C e -i C -i C se R n D s C e i A -i C -i C i A
V1 V1 V4
V3 V2 V3 V2 V2
III. V2 I.V III. V2 I.V
V4 V1 V4 V1
V1 V4 V1
IV. VI. IV. VI.
Figure 14. Double switching – shifting the phase with the longest duty cycle duration to the sides
Figure 15. Double switching flowchart
5.3.2 Adaptive double switching
Adaptive double switching is based on applying the double switching method only when the desired voltage
vector is located in the critical zone as explained in the chapter Section 5.1 and in Figure 10. If the desired
voltage vector lies in the zone with valid current readings, then standard SVM PWM patterns are used. Double
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
13 / 20

switching is activated only in the critical zone. The flowchart and switching pattern example are displayed in
Figure 16 and Figure 17.
Figure 16. Adaptive double switching flowchart
Figure 17. Adaptive double switching – voltage vector position vs switching pattern
This approach results into lower switching losses. The dependence between the critical zone (as a percentage
of electrical rotation) and the ratio of demanded vs maximum achievable output voltage (at a given minimum
sampling window) can be derived for sector I as:
• Critical zone time interval at the sector beginning:
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
14 / 20

(3)
• Critical zone time interval at the sector end:
(4)
Where:
• t is the time interval of the critical zone
• W is the minimum width of the current sampling window [p.u. of el. period]
• ω is electrical angular speed
• T is the electrical period
• V is the amplitude of the desired output voltage [p.u.]
• Assumption: 2*W < V; V ≠ 0
Based on Equation 3 and Equation 4 the dependence between the critical zone duration (area where double
switching is active as a percentage of electrical rotation) and the ratio of demanded vs maximum achievable
output voltage (as a percentage of DC bus voltage) can be shown as per Figure 18. It needs to be noted that in
a real system there would be a zone of "uncertainty" due to the alignment of sampling events of the system vs
real time quantities(voltages, currents) which cannot be calculated exactly.
120
100
80
60
40
20
0 20 40 60 80 100 120
]noitator
rotom
.le
fo
%[
ws
elbuoD
Zone of "uncertainty"
Output voltage [% of DC BUS]
Figure 18. Double switching area vs output voltage (example at a constant minimum sampling window)
5.3.3 Adaptive double switching in one phase only
The approach introduced in the chapter 5.3.2. Adaptive double switching can be further modified by performing
the double switching only in the phase where the sampling window needs to be widened. This approach is
depicted in Figure 19 and Figure 20.
Switching in one phase only results into lower switching losses compared to Adaptive double switching (chapter
Section 5.3.2.) However, with certain motors this method can produce slightly more noise compared to Adaptive
double switching(depending on motor construction and quality. The appropriate method needs to be chosen for
the particular motor.
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
15 / 20

too narrow? create appropriate sampling window by moving to the sides
T1 T1 T1
T3 T3 T3
T5 T5 T5
Vector V1 V7 V1 Vector V1 V7 V1 Vector V1V2V7V6V7V2 V1
s i e R n D s C e iA iA V0 s i e R n D s C e iA iA V0 s i e R n D s C e iA-i C -i C iA V0
V2 V2
III. V2 I. V III. V2 I. V
V4 V1 V4
V1 V1
IV. VI. IV. V6 VI.
Figure 19. Adaptive double switching in one phase only - moving the phase with the mid-length duty cycle
too narrow? create appropriate sampling window by moving to the sides
T1 T1 T1
T3 T3 T3
T5 T5 T5
Vector V2 V7 V2 Vector V2 V7 V2 Vector V1 V2 V4 V2 V1
s i e R n D s C e -i C -i C V0 s i e R n D s C e -i C -i C V0 s i e R n D s C e -i C -i C V0
V1 V1 V7
III. V2 I.V III. V2 I.V
V4 V1 V4 V1
V1 V4 V1
IV. VI. IV. VI.
Figure 20. Adaptive double switching in one phase only - moving the phase with the longest duty cycle
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
16 / 20

6 Summary
Various methods of current sensing have been introduced. Each of the methods is suitable for a different type of
application. The main differences among the methods are in the following areas:
• DC Bus utilization
• Bill of material (BOM)
• Redundancy (possible operation with current circuit measurement broken in one phase)
• Switching losses
• Conductive losses
• Control performance with high-speed motors with low electrical time constant
• Algorithm complexity
• Acoustic noise
• Current THD
• EMC
The comparison of the methods is shown in Table 3. However, in the case of acoustic noise and EMC it is
not straightforward to pick a method with better performance as the performance is highly dependent on the
hardware design of the motor and the power stage.
Generally speaking, dual and triple-shunt methods have better acoustic noise performance but a comparable
performance with the single-shunt method is achievable with a properly designed and constructed motor. There
can also be differences in acoustic performance among the different single-shunt methods (generally, double
and adaptive double switching in all phases perform best) but it highly depends on motor construction and
quality.
Also dual, triple-shunt, and phase-shifted PWM techniques have better performance than double switching in
case of EMC (less switching operation). But by choosing adaptive double switching (in all or one phase) and by
adjusting the HW (power transistors switching performance, PCB design,…) a satisfactory level of EMC can be
achieved.
In the end it is up to the user to consider all the trade-offs and pick the right method fit for the purpose.
Table 3. Current sensing method comparison
Method
Triple- Dual-Shunt Single-shunt
shunt
Phase shift Double switching
Non-adaptive (see Adaptive In one phase only
chapter 5.3.1 )
DC Bus Limited
utilization (low-side
Depending
transistors
on the min.
to be
sampling Limited to Limited to Limited to
100% switched
window is approx. 93% approx. 93% approx. 93%
on for at
possible to
least ADC
reach 100%
sample
time)
BOM [1 –
smallest 3 2 1 1 1 1
3 – largest]
Redundancy yes no no no no no
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
17 / 20

Table 3. Current sensing method comparison...continued
Method
Triple- Dual-Shunt Single-shunt
shunt
Phase shift Double switching
Non-adaptive (see Adaptive In one phase only
chapter 5.3.1 )
Switching
losses
1 1 1 4 3 2
[1 – lowest
4 – highest]
Conductive
losses
3 2 1 1 1 1
[1 – lowest
3 – highest]
Control
performance
- high speed,
low el. time
1 1 3 2 2 2
constant
motors
[1 – best
3 – worst]
Algorithm 1
complexity (2 for full
1 3 4 4 4
[1 - simple DC Bus
4 - complex] utilization)
Current THD Higher Higher Higher Higher
best best but but but but
comparable comparable comparable comparable
7 Revision history
Table 4. Revision history
Document ID Release date Description
AN14164 v. 1.0 21 February 2024 Initial release
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
18 / 20

8 Legal information
8.1 Definitions Terms and conditions of commercial sale — NXP Semiconductors
products are sold subject to the general terms and conditions of commercial
sale, as published at http://www.nxp.com/profile/terms, unless otherwise
Draft — A draft status on a document indicates that the content is still agreed in a valid written individual agreement. In case an individual
under internal review and subject to formal approval, which may result agreement is concluded only the terms and conditions of the respective
in modifications or additions. NXP Semiconductors does not give any agreement shall apply. NXP Semiconductors hereby expressly objects to
representations or warranties as to the accuracy or completeness of applying the customer’s general terms and conditions with regard to the
information included in a draft version of a document and shall have no purchase of NXP Semiconductors products by customer.
liability for the consequences of use of such information.
Suitability for use in automotive applications — This NXP product has
been qualified for use in automotive applications. If this product is used
8.2 Disclaimers by customer in the development of, or for incorporation into, products or
services (a) used in safety critical applications or (b) in which failure could
lead to death, personal injury, or severe physical or environmental damage
Limited warranty and liability — Information in this document is believed
(such products and services hereinafter referred to as “Critical Applications”),
to be accurate and reliable. However, NXP Semiconductors does not give
then customer makes the ultimate design decisions regarding its products
any representations or warranties, expressed or implied, as to the accuracy
and is solely responsible for compliance with all legal, regulatory, safety,
or completeness of such information and shall have no liability for the
and security related requirements concerning its products, regardless of
consequences of use of such information. NXP Semiconductors takes no
any information or support that may be provided by NXP. As such, customer
responsibility for the content in this document if provided by an information
assumes all risk related to use of any products in Critical Applications and
source outside of NXP Semiconductors.
NXP and its suppliers shall not be liable for any such use by customer.
In no event shall NXP Semiconductors be liable for any indirect, incidental,
Accordingly, customer will indemnify and hold NXP harmless from any
punitive, special or consequential damages (including - without limitation -
claims, liabilities, damages and associated costs and expenses (including
lost profits, lost savings, business interruption, costs related to the removal
attorneys’ fees) that NXP may incur related to customer’s incorporation of
or replacement of any products or rework charges) whether or not such
any product in a Critical Application.
damages are based on tort (including negligence), warranty, breach of
contract or any other legal theory.
Export control — This document as well as the item(s) described herein
Notwithstanding any damages that customer might incur for any reason may be subject to export control regulations. Export might require a prior
whatsoever, NXP Semiconductors’ aggregate and cumulative liability authorization from competent authorities.
towards customer for the products described herein shall be limited in
accordance with the Terms and conditions of commercial sale of NXP
Translations — A non-English (translated) version of a document, including
Semiconductors.
the legal information in that document, is for reference only. The English
version shall prevail in case of any discrepancy between the translated and
Right to make changes — NXP Semiconductors reserves the right to English versions.
make changes to information published in this document, including without
limitation specifications and product descriptions, at any time and without
Security — Customer understands that all NXP products may be subject to
notice. This document supersedes and replaces all information supplied prior
unidentified vulnerabilities or may support established security standards or
to the publication hereof.
specifications with known limitations. Customer is responsible for the design
and operation of its applications and products throughout their lifecycles
Applications — Applications that are described herein for any of these to reduce the effect of these vulnerabilities on customer’s applications
products are for illustrative purposes only. NXP Semiconductors makes no and products. Customer’s responsibility also extends to other open and/or
representation or warranty that such applications will be suitable for the proprietary technologies supported by NXP products for use in customer’s
specified use without further testing or modification. applications. NXP accepts no liability for any vulnerability. Customer should
Customers are responsible for the design and operation of their regularly check security updates from NXP and follow up appropriately.
applications and products using NXP Semiconductors products, and NXP Customer shall select products with security features that best meet rules,
Semiconductors accepts no liability for any assistance with applications or regulations, and standards of the intended application and make the
customer product design. It is customer’s sole responsibility to determine ultimate design decisions regarding its products and is solely responsible
whether the NXP Semiconductors product is suitable and fit for the for compliance with all legal, regulatory, and security related requirements
customer’s applications and products planned, as well as for the planned concerning its products, regardless of any information or support that may be
application and use of customer’s third party customer(s). Customers should provided by NXP.
provide appropriate design and operating safeguards to minimize the risks
NXP has a Product Security Incident Response Team (PSIRT) (reachable
associated with their applications and products.
at PSIRT@nxp.com) that manages the investigation, reporting, and solution
NXP Semiconductors does not accept any liability related to any default, release to security vulnerabilities of NXP products.
damage, costs or problem which is based on any weakness or default
in the customer’s applications or products, or the application or use by
NXP B.V. — NXP B.V. is not an operating company and it does not distribute
customer’s third party customer(s). Customer is responsible for doing all
or sell products.
necessary testing for the customer’s applications and products using NXP
Semiconductors products in order to avoid a default of the applications
and the products or of the application or use by customer’s third party
customer(s). NXP does not accept any liability in this respect. 8.3 Trademarks
Notice: All referenced brands, product names, service names, and
trademarks are the property of their respective owners.
NXP — wordmark and logo are trademarks of NXP B.V.
AN14164 All information provided in this document is subject to legal disclaimers. © 2024 NXP B.V. All rights reserved.
19 / 20

Contents
1 Introduction .........................................................2
2 Current sensors ..................................................2
3 Current sensing techniques based on
Ohm’s law ............................................................2
4 Low-side current sensing ..................................2
4.1 Triple-shunt ........................................................3
4.2 Dual-shunt ..........................................................5
5 DC Bus current sensing – single shunt ............6
5.1 DC bus current sensing – phase current
reconstruction ....................................................6
5.2 Phase-shifted PWM ...........................................9
5.3 Double switching .............................................11
5.3.1 The basics of double switching method ...........11
5.3.2 Adaptive double switching ...............................13
5.3.3 Adaptive double switching in one phase
only ..................................................................15
6 Summary ............................................................17
7 Revision history ................................................18
8 Legal information ..............................................19
Please be aware that important notices concerning this document and the product(s)
described herein, have been included in section 'Legal information'.
© 2024 NXP B.V. All rights reserved.
For more information, please visit: http://www.nxp.com
Date of release: 21 February 2024
Document identifier: AN14164