---
source: "ST AN5940 -- Contactor Driver using VNH7100BAS"
url: "https://www.st.com/resource/en/application_note/an5940-contactor-driver-using-the-vnh7100bas-stmicroelectronics.pdf"
format: "PDF 21pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 33166
---

Application note
Contactor driver using the VNH7100BAS
Introduction
There are two types of primary circuits for high voltage contactors: contactors with a two-coil primary, and contactors with a
single coil primary. The dual coil primary contactor has a high current leg for pull-in (or pick-up) and lower current leg for lower
hold currents to minimize steady state power dissipation/consumption in the primary.
The contactors with single coil primaries require a variable drive mechanism that provides a higher current fast pull-in, lower
power hold current, and higher voltage flyback for faster turn-off. These three states of operation combined with a need for safe
actuation (no inadvertent actuations) require something more than a simple high side or low side driver.
This solution needs:
• An independent high side driver to drive the upper end of the primary coil
• An independent low side driver to drive the lower end of the coil separately
• A freewheeling element to recirculate inductive current during steady state PWM operation
• A fast recirculation path to quickly reduce the coil current and disable the contactor rapidly.
Some contactors include an “economizer” circuit that provides all of the above. All that is needed is to provide a voltage on the
primary circuit. For those that do not have an economizer, the VNH7100BAS can accomplish all of these elements with only a
microcontroller.
Figure 1. VNH7100BAS block diagram
There are two ways to accomplish the pull-in and hold currents. One way is somewhat open loop by monitoring the battery
voltage and calculating the desired duty cycles. This is the least expensive while it does take some microcontroller effort. This
method is discussed in detail in the first part of this application note.
The second method monitors the motor current and forces a PWM to regulate the current to the desired levels. This eliminates
the microcontroller requirement while it does add several components to the BOM.

Contactor components
1 Contactor components
The single coil contactor consists of a primary coil, a magnetic core, fixed and movable contacts, and an armature
on some sort of sprung hinge. In a normally open contactor, the spring keeps the contacts apart in the “at
rest” condition. Contact is made when current flows in the primary creating a magnetic field. The magnetic
field overcomes the spring forcing the armature to rotate causing the movable contact to connect with the fixed
contact, completing the circuit.
Figure 2. Single coil contactor construction (simplified)
The current required to pull the armature and close the contacts is greater than the current required to maintain a
reliable connection between the two contacts. The pull-in current requirement can be as high as 5 A. The required
minimum hold current can be in the tens of milliamps.

Application schematics
2 Application schematics
Figure 3. Simplified application circuit, micro controlled
Figure 4. Simplified schematic, micro independent

Sequence of operation
3 Sequence of operation
There are actually four phases of operation:
1. Pull-in
2. Slow recirculation to the hold current
3. Hold current regulation
4. Fast recirculation to remove quickly the coil current at turn-off.
3.1 Pull-in
A high current pull-in to actuate initially the contactor can be as simple as full voltage across the primary coil. In
this example, the pull-in current is flowing from HSA to LSB with no PWM.
Figure 5. Pull-in current flow
During the pull-in phase, the armature moves to close the high voltage contacts. This armature movement may
generate a back EMF effect on the current. There is no BEMF when the armature is stationary (fully closed or fully
open). This is similar to what occurs in a permanent magnet motor. The electrical equivalent circuit looks like the
Figure 6. This figure illustrates the effect of BEMF voltage on the pull-in current and fast recirculation voltage.

Pull-in
Figure 6. Contactor primary electrical model
BEMF appears as a dip in the pull-in current typically as it is still rising (see Figure 7). During pull-in, the SEL0 pin
can be held High so that the current sense pin (CS) reflects the current in HSA. That current can be monitored
to verify that the expected back EMF event occurred. This provides a secondary confirmation that the contactor
behaved as expected.
Figure 7. Contactor voltage and current waveforms
The pull-in current can be regulated as well if desired. The equations provided in the Section 3.3 Hold current
below apply to pull-in current regulation as well.

Slow recirculation
3.2 Slow recirculation
The slow recirculation time between the end of the pull-in cycle and the beginning of the hold current regulation
(see Figure 7) can be determined by knowing the battery voltage, load inductance, and resistance.
Figure 8. Slow recirculation path
During this time both high side drivers (HSA and HSB) are active, and the current is just recirculating.
Off time from pull-in to hold
VBatt (1)
LCoil min ln IHoldRCoil max
The slow recirculation time (t
OF
tO
F
)F Fne V eBdast tto = be shorter tRhCaoni lthmea sxhortest pos 9 s 0 ib % le t
OFF
time. Having a longer than
needed slow recirculation time would allow the coil current to fall below the minimum hold current. This may
cause the contactor to open. Having a shorter slow recirculation time has no harmful effects on the operation and
provides some margin to the system.
To calculate the shortest OFF time, the lowest coil inductance and the highest coil resistance should be used.
This hold time can be calculated based on battery voltage as it impacts the slow recirculation time. Adding the
90% can ensure that the hold current minimum will not be violated.
Alternatively, a simpler solution could be just enabling PWM immediately after pull-in, skipping the “slow
recirculation” time altogether. Doing so just slows the ramp down from the pull-in current to the hold current.

Hold current
3.3 Hold current
During the hold time the low side switch (LSB) is in PWM to reduce the current in the primary windings, see
the Figure 7. The micro, using the coil resistance and the battery voltage, calculates the duty cycle. The coil
inductance is heavily relied upon to regulate the primary current during PWM.
Figure 9. Hold current flow
PWM duty cycle is not as simple as the ratio between the battery voltage and the hold voltage. The rate of change
of current in an inductor is proportional to the voltage across its inductance. So, the duty cycle calculation must
include this difference between the ON and recirculation circuits.
Basic inductor equation
(2)
∆I
VInd=L
∆T

Hold current
3.3.1 Hold current PWM duty cycle calculation
Looking at the Figure 6, the voltage across the coil inductance is affected by the current through the coil
resistance as well. So, V(inductor) is not just the battery voltage. When there is current in the coil, the inductance
sees the battery voltage minus the voltage drop across the internal resistance.
PWM ON time calculation
(3)
When the coil is recirculating, the inductor V sBeaetst − th I eH osladm RCeo vilo = lta L gteO Ndrop across the coil resistance plus the voltage
drop across the recirculating element. In the case of the VNH7100BAS that is the HSB body diode (V = 0.7 V).
f
PWM OFF time equation
(4)
Understanding that the duration in recircula V tifo + n I (Ht
O
o
ld
) R Ciso ijuls = t L thtOeF rFemaining time left in the PWM period after t
ON
.
The relationship between t and t
OFF ON
(5)
1
Putting these three equations together, and a t OliFttFle = hafnPdW wMa − vin tOgN, it is possible to calculate an expected duty cycle:
Duty cycle calculation
(6)
Vf+IHoldRCoil
Duty=
VBatt+Vf−IHoldRHBr
3.3.2 Hold current tolerance
Looking at Eq. (6) it is put in evidence that the duty cycle is independent of frequency (f ), inductance (L), and
PWM
ripple current amplitude (ΔI). There are two parameters that do make a difference in the calculated duty cycle:
they are the supply voltage (V ) and the coil resistance. The supply voltage is typically known and can be
Batt
used when calculating the appropriate duty cycle from Eq. (6). Coil resistance is not dynamically known and may
impact to maintain current error.
3.3.2.1 Coil resistance
The coil resistance is very dependent on the coil temperature. As a result, coil temperature affects the actual coil
current at a given PWM duty cycle. Unfortunately, coil temperature is not so easily determined. Some estimations
can be given if ambient temperature is provided. Also in automotive applications, the charging system voltage is
typically a function of ambient temperature. However, getting to that level of complexity may not be needed.
From the temperature coefficient of copper resistivity, it is possible to estimate what range of coil resistance to
expect. The temperature coefficient of copper resistivity is:
Resistivity of copper
(7)
The equation to calculate the difference in the coαil= re0s.3is9t3a%n/c°eC over temperature is (given that the reference
resistance is at 25 °C):
Coil resistance over temperature
(8)
Variation in the hold current due to cRoCilo riel=sisRtCaonicl@e 2c5a°nC b1e+ cαalcTuCloailte−d2 b5y°C solving Eq. (6) for coil current. Then
varying the coil resistance from -40 °C to 125 °C as well as accommodating for the +/-5% tolerance of the coil
resistance specification. This leads to the worst case variation in coil current.

Fast recirculation
Coil current calculation
(9)
Vf−Duty VBatt+Vf
IHold RCoil =
RCoil+Duty∙RHBr
3.3.3 Ripple current
Frequency and inductance influence the ripple current amplitude. To be sure that the ripple current is not
excessive, it is possible to calculate the ripple current amplitude for a given inductance and PWM frequency.
Ripple current calculation
(10)
VBatt−IHold RCoil+RHBr Duty
∆I=
Most automotive applications require a 20 kHz or grLeCaotielr PWM freqfuPeWncMy to limit audible noise. The worst-case
condition would be at the minimum duty cycle, which would be at max battery (V = 16 V).
batt
Anything less than 10% would be more than sufficient to keep the contactor reliably closed (and quiet) as long as
the current is always above the minimum required.
3.4 Fast recirculation
When the contactor is disabled, the polarity of the primary coil is reversed due to inductive flyback. The simplest
way is to reverse the polarity of the inputs (INA and INB) and set the PWM pin low. This turns off all the low side
drivers and turn-on HSB. The inductance of the coil automatically inverts the polarity across the coil and current
flow from the ground to the supply. This remains as long as there is current due to the coil inductance.
Figure 10. Fast recirculation path
The VNH7100BAS has a cross conduction protection that delays switching polarity between HS and LS switches.
During the cross-conduction delay time (t < 350 µs) the entire bridge is tri-stated. It may be that this
cross
cross-conduction delay time is longer than the fast recirculation time. This does not inhibit the fast recirculation.
During this tri-stated condition, the current just flows through the body diodes of the LSA and HSB switches.
Two trials were implemented to verify the correct behavior of the contactor when driven by the VNH7100BAS.

The contactor that has been used to implement the measurements shows a coil inductance L = 52 mH with a
series resistance R = 11 Ω.
series
In Figure 11 the fast decay after the hold phase is implemented. Setting a hold current of about 500 mA
(modulating the PWM with a duty cycle of 32%), the fast decay time is less than 8 ms: in the Figure 12, CH2 and
CH6 show that the contactor is open before the condition I = 0 A is reached in the primary windings.
coil
Figure 11. Hold phase and fast decay time
Figure 12. Zoom Hold phase and fast decay time
Fast decay phase has been implemented also during the pull-in phase, simulating a worst-case condition where a
fault occurs immediately after contactor closure. In this case, the device drives the contactor with a DC current of
about 1.5 A. This trial is shown in the Figure 13, where it is put in evidence that the device works correctly being
able to sustain the required demagnetization energy. In the Figure 14, it is shown a fast decay time around 10 ms.
Both cases put in evidence that the actual clamping method provided by the VNH7100BAS is more than sufficient
for operating this contactor.

Figure 13. Pull-in phase and worst-case fast decay time
Figure 14. Zoom worst-case fast decay time
3.4.1 Protection against loss of battery
During fast recirculation, the current is flowing from ground to supply. During this time, there needs to be a place
for the current to go. Typically, that means a path back to the battery. If the current path returning to the battery
is interrupted or blocked by a reverse battery protection circuit, then the current finds another path. That usually
means the fast recirculation voltage climbs higher until it finds an alternate path back to ground. There are a few
options for that recirculation path. Fast recirculation current can be shunted to an external component like a bulk
capacitor or a TRANSIL (zener) or it can break the H-Bridge by exceeding the breakdown voltage of the part.
The first line of defense is typically a bulk capacitor. When just using a capacitor, the energy in the primary coil is
dumped or transferred into the bulk capacitor. This energy transfer looks like:
Bulk capacitor energy equation
(11)
1 2 1 2
Where:
2
LCoilICoil=
CBulk∆VBulk
• L = coil inductance
Coil
• I = coil current at loss of battery
Coil
• C = bulk capacitance (see Figure 3)
Bulk
• ∆V = the rise in voltage across the bulk capacitor
Bulk

The upper limit to the voltage on the capacitor is based on the breakdown voltage of the H-Bridge. The
VNH7100BAS absolute maximum supply voltage rating is V = 38 V. So, the range of voltage on the
CC(max)
bulk capacitor starts at the battery voltage and ends at V .
CC(max)
Bulk capacitor max voltage change
(12)
Simplifying the Eq. (11) and inserting the E∆qV.B (u1l2k)< itV isC Cpomsasxibl−e VtoB afitntd the bulk capacitor equation as follows:
Bulk capacitance calculation
(13)
ICoil LCoil
CBulk>
The worst-case condition is where the coil currentV iCsC thmea hxig−heVsBta, tdturing the pull-in phase. The pull-in current is
essentially the battery voltage divided by the coil resistance.
If the bulk capacitance required to protect the H-Bridge is too excessive (too large or expensive), then either
use a sufficiently robust TRANSIL to keep the voltage below 38 V or a combination between a TRANSIL and
capacitance. Bulk capacitance is needed anyway on a module for supply stability.
A TRANSIL has resistance associated with it. So, be careful in choosing a TRANSIL that has an initial clamping
voltage that is above a double battery (jump start) and below the max V of the VNH7100BAS when conducting
CC
the peak coil current.

Controlling the VNH7100BAS using a microcontroller
4 Controlling the VNH7100BAS using a microcontroller
The VNH7100BAS can be controlled entirely by a microcontroller. It takes up to five pins from the micro. 4 digital
I/O and one analog input (ADC). The VNH7100BAS I/O works with either a 5 V or a 3.3 V system. Two pins are
optional depending on the level of monitoring required. These would be the SEL0 pin and the current sense (CS)
pin.
The current sense pin (CS) has two functions. The first is to reflect the selected high side output current reduced
(divided) by a K factor. The second is to report a fault where half of the bridge is latched off.
The current sense feedback output requires a sense resistor (Rsense in Figure 3). The resistor value is based on
the ADC max voltage and the k-factor reduced coil current. Details on how the current sense feedback works and
how to calculate the proper sense resistor size can be found in AN5026.
Fault indication by the current sense pin is further described in detail in the application note AN5026.
The table below summarizes the steps in each phase of contactor operation.
Table 1. VNH7100BAS truth table
State INA INB PWM SEL0 Comment
H
Current flowing from HSA to LSB,
Pull-in H L H
monitoring HSA current
L
Current flowing from HSA to HSB,
H H X
Current flowing from HSA to HSB
(LSB OFF)
Slow recirc
Current flowing from HSA to HSB,
H L L
Current flowing from HSA to HSB
(LSB OFF)
Current flowing from HSA to
H LSB/HSB at PWM frequency,
Hold H L 20 kHz
Current flowing from HSA to
L LSB/HSB at PWM frequency,
monitoring HSB current
Current flowing from LSA to HSB,
Fast recirc. L H L X
only HSB is ON
Related links
See AN5026:VIPower M0-7 H-Bridges for Automotive DC Motor Control

Designing the micro independent solution
5 Designing the micro independent solution
The VNH7100BAS can be used to drive a contactor without the advantage of a microcontroller. There are a few
functions or features that are lost when forgoing the microcontroller. They are:
1. Fault reporting
2. Positive diagnostic feedback such as load integrity checking.
3. Accuracy in both timing and current regulation
The functions that must be recreated are the pull-in timing, the coil voltage control, and the recirculation control
(slow/fast). The current regulation benefits from the current requirements shown in Section 5.2. The current is not
flat over the temperature range. This is mostly due to the change in resistance of the coil.
During pull-in the PWM circuit can either be completely overridden or set to provide a pull-in level of current
regulation. Slow recirculation occurs naturally while fast recirculation is a result of completely tri-stating the
outputs.
Figure 15. Standalone PWM hold current control circuit
The limitations of this standalone circuit include:
• No analog feedback of regulated current for diagnostics.
• No off time between pull in and hold currents. The system switches directly from pull-in mode to hold PWM
mode. This changes the current profile between pull-in and hold considerably.
• The accuracy of the regulated current is limited to the tolerance of the resistors and the stability of V .
IN
5.1 Oscillator
The oscillator is a simple 1/3 – 2/3 oscillator. It generates a simple triangle waveform starting at 1/3 of the supply
and ending at 2/3 of the supply. This keeps the input voltages well within the common-mode range for most
op-amp and the voltage slope to be fairly linear.
Three of the four oscillator resistors are simple 10 kΩ resistors. This makes for the basic 1/3 - 2/3 thresholds.
When the output of the op-amp is low, the voltage on the + terminal is 1/3. When the output in the op-amp is high,
the voltage on the + terminal is 2/3.

Coil voltage control
Figure 16. Simple 1/3-2/3 oscillator
The triangle waveform shown for Vosc (Figure 16) is generated by the basic charge–discharge of C by R .
OSC OSC
The basic equations for the voltage of an RC circuit can be described by:
Charge and discharge CR equations
(14)
−t −t
Using these two equatioVndsi sacnℎadr dgeestcr=ibiVnmga txhee voRltCagoer froVmcℎ a1r/g3e tot 2=/3V amnadx b1a−cke theR oCscillation frequency can be
calculated as follows:
Oscillator frequency equation
(15)
Setting C
OSC
and solving for R
OSC
.
fOSC=
2ROSCCOSCln2
Oscillator frequency
(16)
The frequency equation is simple in both cas R eO SdCue = t2of tOhSeC CsyOmSCmlne2try of the triangular waveform in the oscillator
above, and does not depend on the supply voltage.
5.2 Coil voltage control
The coil driving requirements are voltage centric. This means that this circuit needs to provide a steady voltage
over the operating voltage range.
The voltage control circuit compares the supply voltage with the fixed triangle waveform generator and adjusts the
duty cycle inversely proportional to the battery voltage. It is not a true RMS converter. As a result, the duty cycle is
initially determined by the Eq. (6) while being controlled by the battery voltage.

Coil voltage control
Figure 17. PWM generator circuit
First, it is necessary to find the voltage (Vn) that generates the correct duty cycle at 9 V and at 16 V (by using Eq.
(6)). Having these bounds, it is possible to figure out the resistor values in the Figure 17.
Figure 18. Dissecting the oscillator waveform
V
tr1
tf2
tr2 t1 t2
2/3 VIN
Vn
1/3 VIN
t
The equation for determining duty cycle requires calculating known sections of the theoretical RC waveform and
subtracting other portions of the waveform. For instance, the Figure 18 illustrates that the rising edge duration
above the red dashed line (Vn) can be described as:
Rising edge duration
(17)
And the falling edge duration above the red dashte1d= litnre1 −(Vt nr)2 can be described as:
Falling edge duration
(18)
All of the time above the V
n
line is the ON time fotr2 t=het fP2W−Mt1 generator. Such that the duty cycle decreases as the
battery voltage increases. This can be expressed as:
Duty cycle
(19)
These can all be expressed in terms of the baDsuitcy R=C tr1is+e ta2nfdO fSaCll equations shown in Eq. (14). With that, the duty
cycle generated by a specific V can be described:

Pull-in control
Duty cycle with respect to the voltage at V
(20)
2VIN
V
needs to be translated back to th D e u b ty at V tenry = vo f lOtaSgCe R OaSt Cth COe ScCo ln il. SVon, s − tar 2 ting with a simple nodal equation from
Figure 17 of the control voltage.
PWM control node equation
(21)
VIN−Vn VBat−Vn Vn
+ =
Solving Eq. (21) for V
. R1 R3 R2
V with respect to V
n Bat
(22)
R2R3VIN+R1R2VBat
Between Eq. (20) and Eq. (21), it is possib V len = to gRe1Rn2er+atRe1 aRn3 +eqRu2aRt3ion for the duty cycle as a function of the battery
voltage.
Duty cycle with respect to V
Bat
(23)
2VIN
Duty VBat =fOSCROSCCOSCln
R2R3VIN+R1R2VBat
−2
Setting R
, taking Eq. (22), inserting V
(Duty) for Vn and soRl1vRin2g+ foRr1 RR31 :+R2R3
Calculating R
(24)
R2R3 VIN−Vn Duty
R1=
Setting the Eq. (24) to equal itself, with onRe3 VsnidDe uutsyin−g Rth2eV dBuatty− cVynclDeu ntyeeded at 9 V to generate V
and the other
side using the duty cycle needed for 16 V to generate V (for V (Duty) see Eq. (6)), solving for R and simplifying
n n 3
gets:
Calculating R
3
(25)
R2 Vn Duty9V VIN−16V +Vn Duty16V 9V−VIN +VIN 16V−9V
Where V
IN
= the in R p 3 u = t v − olVtaINge (it is better to havVen thDisu tfyix9eVd −toV an kDnuotwy1n6 Vvalue (5 V)).
5.3 Pull-in control
The pull-in function has two possible parameters: pull-in duration and pull-in current regulation (if desired).
5.3.1 Pull-in duration
The pull-in duration timing is governed by C R , R , and the V of Q shown in the Figure 15. This circuit has a
1, 5 6 BE 1
lot of over temperature variations. However, pull-in time can vary widely (within reason) without adverse effects on
the function or reliability of the contactor. Only the minimum pull-in time needs to be respected.
The current through R is fixed by the V of Q . The current through R is determined by the V and the
6 BE 1 5 BE
charging of C . With that, it is possible to calculate the time it takes to charge up capacitor C to where the V of
1 1 BE
Q is no longer sufficient to keep Q ON. At that point, there is no longer any base current to turn on Q . The Eq.
1 1 1
(6) finds the point where R takes all of the charging current from C .
6 1

Turning off the contactor
Pull-in timing equation
(26)
VBE VIN−VBE e
−tPull−inR5C1
=
Solving Eq. (26) for the pull-in time givRe6s us: R5
Pull-in timing equation
(27)
R6 VBE−VIN
The shortest time to charge the capaci t toPru l(lC−
)in, t = o R w5h C e1r l e n V
BE
R is5 VnBoE longer respected, is when V
is the highest.
That depends on the ambient temperature and transistor used. In the collector current range under consideration
(6 mA-7 mA), a simple BC848B NPN small signal bipolar transistor has a V range of ~450 mV (at hot) to ~850
mV (at cold).
Setting R and R to be equal and solving for R finds the optimum resistance needed to stay within the bounds
5 6 5
of the pull-in time.
Solving for R5
(28)
tPull−in
R5=
VBE−VIN
C1ln
VBE
5.3.2 Pull-in current regulation
The pull in current can be completely unregulated between 10 V and 16 V. A simple pulldown of the voltage at V
can force the PWM generator to work at 100% duty cycle. This makes selecting the value of R simple. It can be
4
0 Ω. However, if you would like to reduce the duty cycle above a certain voltage, then R can be calculated.
Using Eq. (21) keeping R and R fixed and setting V at the peak (1/3 V ) of the oscillator triangle waveform, it
1 2 n IN
is possible to calculate what R needs to be. From that it is put in evidence that this new value for R is a parallel
2 2
of the previously calculated R and the introduced resistor, R .
2 4
PWM control node equation with R and R in parallel
2 4
(29)
R2R4 VINR1R3
=
Solving for R
: R2+R4 3VBmaxR1−VINR1+2VINR2
PWM control node equation for R
(30)
VINR1R2R3
R4=
Using this value for R 4 causes the PW3VMB menagxRin1eR 2to− sVtaINrt PR1WRM2+mRin1gR 3at− V2 B R m2a R x3. or whatever voltage you want to start
PWMming the coil.
5.4 Turning off the contactor
To disable the contactor, the On/Off command pin goes low. This pulls the INA and PWM pin to the ground.
INB is already low so this action completely tristates the bridge and forces the current to flow from LSA to HSB,
generating a fast turn-off.

Turning off the contactor
Figure 19. Fast recirculation at turn-off

Power dissipation
6 Power dissipation
There is a number of ways to determine if the VNH7100BAS can handle the power it dissipates while driving
the contactor. There is a multi-element Foster thermal model in the datasheet illustrating the complexity of
the VNH7100BAS thermal paths. This model can be incorporated into SPICE where the output structures are
emulated either by equation or by schematic.
Figure 20. Foster thermal model for the VNH7100BAS
The above (Figure 20) model is incorporated into a thermal simulation tool provided by STMicroelectronics
called TwisterSIM. TwisterSIM is available by download from the ST.com website. You can download the register
TwisterSIM for free.
Since the pull-in time is short, the thermal time constants play a large role in determining the junction temperature.
At least for pull-in it is recommended that the TwisterSIM be used. It provides the most accurate thermal
modeling. This would also apply to the fast recirculation period.

Figure 21. TwisterSIM
We can spend a lot of time calculating the average power dissipation by the various switching elements in the
different stages of contactor driving. However, the volume of calculations needed is extensive and still doesn't
match the accuracy of TwisterSIM.
The simulator does not emulate the coil perfectly in that there is no BEMF generated by the movement of the
armature. That lack of BEMF does little to hinder the accuracy of the thermal simulation.
Figure 22. Twister thermal simulation results
SPICE model thermal simulation results correlated quite well to the twister model.

Figure 23. SPICE model thermal simulation
In both simulations, the junction temperature rise is minimal. Long-term (SPICE) simulations indicate that the
maximum junction temperature is less than 100 °C, a 15 °C rise.

Revision history
Table 2. Document revision history
Date Revision Changes
27-Mar-2023 1 Initial release.

Contents
Contents
1 Contactor components ............................................................2
2 Application schematics............................................................3
3 Sequence of operation.............................................................4
3.1 Pull-in ........................................................................4
3.2 Slow recirculation ..............................................................6
3.3 Hold current...................................................................7
3.3.1 Hold current PWM duty cycle calculation ......................................8
3.3.2 Hold current tolerance.....................................................8
3.3.3 Ripple current...........................................................9
3.4 Fast recirculation...............................................................9
3.4.1 Protection against loss of battery ........................................... 11
4 Controlling the VNH7100BAS using a microcontroller .............................13
5 Designing the micro independent solution ........................................14
5.1 Oscillator ....................................................................14
5.2 Coil voltage control............................................................15
5.3 Pull-in control.................................................................17
5.3.1 Pull-in duration ......................................................... 17
5.3.2 Pull-in current regulation.................................................. 18
5.4 Turning off the contactor........................................................18
6 Power dissipation ................................................................20
Revision history .......................................................................23
List of figures..........................................................................25

List of figures
List of figures
Figure 1. VNH7100BAS block diagram . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
Figure 2. Single coil contactor construction (simplified) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
Figure 3. Simplified application circuit, micro controlled. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
Figure 4. Simplified schematic, micro independent . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
Figure 5. Pull-in current flow . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
Figure 6. Contactor primary electrical model . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
Figure 7. Contactor voltage and current waveforms . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
Figure 8. Slow recirculation path. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
Figure 9. Hold current flow. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
Figure 10. Fast recirculation path. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
Figure 11. Hold phase and fast decay time . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
Figure 12. Zoom Hold phase and fast decay time. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
Figure 13. Pull-in phase and worst-case fast decay time. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
Figure 14. Zoom worst-case fast decay time . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
Figure 15. Standalone PWM hold current control circuit. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
Figure 16. Simple 1/3-2/3 oscillator. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
Figure 17. PWM generator circuit. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
Figure 18. Dissecting the oscillator waveform. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
Figure 19. Fast recirculation at turn-off . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
Figure 20. Foster thermal model for the VNH7100BAS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
Figure 21. TwisterSIM. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
Figure 22. Twister thermal simulation results . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
Figure 23. SPICE model thermal simulation. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22
