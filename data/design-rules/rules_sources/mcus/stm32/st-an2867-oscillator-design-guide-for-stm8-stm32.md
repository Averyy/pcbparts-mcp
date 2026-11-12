---
source: "ST AN2867 Rev 25 (October 2026) -- Guidelines for oscillator design on STM8AF/AL/S and STM32 MCUs/MPUs"
url: "https://www.st.com/resource/en/application_note/an2867-oscillator-design-guide-for-stm8af-al-s-and-stm32-microcontrollers-stmicroelectronics.pdf"
format: "PDF 60pp"
method: "pdf-text"
extracted: 2026-11-10
chars: 106775
note: "Replaces a February 2026 paraphrase of an earlier revision that said to ground a metallic crystal case; Rev 25 p.45 says not to connect it to the oscillator ground."
---
[PDF: 60 pages.]

# **AN2867** **Application note**
#### Guidelines for oscillator design on STM8AF/AL/S and STM32 MCUs/MPUs

##### **Introduction**

Many designers know oscillators based on Pierce-Gate topology (Pierce oscillators), but not
all of them really understand how they operate, and only a few master their design. In
practice, limited attention is paid to the oscillator design, until it is found that it does not
operate properly (usually when the final product is already in production). A crystal not
working as intended results in project delays, if not overall failure.


The oscillator must get the proper amount of attention during the design phase, well before
moving to manufacturing, to avoid the nightmare scenario of products failing in application.


This document introduces the Pierce oscillator basics, and provides guidelines for its
design. It also shows how to determine the external components, and provides guidelines
for correct PCB design and for selecting crystals and external components.


To speed up the application development, the recommended crystals (HSE and LSE) for the
products listed in _Table 1_ are detailed in _Section 5: Recommended resonators for STM32_
_MCUs/MPUs_ and _Section 6: Recommended crystals for STM8AF/AL/S MCUs_ .


**Table 1. Applicable products**


**Type** **Product categories**


STM8S series, STM8AF series and STM8AL series

STM32 32-bit Arm [®] Cortex [®] MCUs


Microcontrollers


STM32 Wireless MCUs


STM32 Ultra Low Power MCUs


STM32 High Performance MCUs


Microprocessors STM32 Arm [®] Cortex [®] MPUs


October 2026 AN2867 Rev 25 1/60


_[www.st.com](http://www.st.com)_



**Contents** **AN2867**

## **Contents**


**1** **Quartz crystal properties and model ... 6**


**2** **Oscillator theory ... 8**


2.1 Negative resistance ... 8


2.2 Transconductance ... 9


2.3 Negative-resistance oscillator principles ... 10


**3** **Pierce oscillator design ... 11**


3.1 Introduction to Pierce oscillators ... 11


3.2 Feedback resistor ... 11


3.3 Load capacitance ... 12


3.4 Oscillator transconductance ... 13


3.5 Drive level and external resistor calculation ... 14


3.5.1 Calculating the drive level ... 14


3.5.2 Another drive level measurement method ... 16


3.5.3 Calculating the external resistor ... 16


3.6 Startup time ... 17


3.7 Crystal pullability ... 17


3.8 Safety factor ... 18


3.8.1 Definition ... 18


3.8.2 Measurement methodology ... 19


3.8.3 Safety factor for STM32 and STM8 oscillators ... 19


3.9 Oscillation modes ... 20


3.9.1 What are fundamental and overtone modes? ... 20


3.9.2 Third overtone mode: pros and cons ... 21


3.9.3 Considerations for crystals interfaced with STM32 products ... 22


**4** **Guidelines to select a suitable crystal**
**and external components ... 23**


4.1 Low-speed oscillators embedded in STM32 MCUs/MPUs ... 23


4.2 How to select an STM32-compatible crystal ... 26


**5** **Recommended resonators for STM32 MCUs/MPUs ... 29**


2/60 AN2867 Rev 25


**AN2867** **Contents**


5.1 STM32-compatible high-speed resonators ... 29


5.2 STM32-compatible low-speed resonators ... 29


**6** **Recommended crystals for STM8AF/AL/S MCUs ... 43**


6.1 Part numbers of recommended crystal oscillators ... 43


6.2 Recommended ceramic resonators ... 44


**7** **Tips for improving oscillator stability ... 45**


7.1 PCB design guidelines ... 45


7.2 PCB design examples ... 47


7.3 Soldering guidelines ... 51


7.4 LSE sensitivity to PC13 activity ... 51


**8** **Reference documents ... 53**


**9** **FAQs ... 54**


**10** **Conclusion ... 55**


**11** **Revision history ... 56**


AN2867 Rev 25 3/60



**List of tables** **AN2867**

## **List of tables**


Table 1. Applicable products ... 1
Table 2. Example of equivalent circuit parameters... 7
Table 3. Typical feedback resistor values for given frequencies ... 12
Table 4. Safety factor (Sf) for STM32 and STM8 oscillators... 19
Table 5. LSE oscillators embedded into STM32 MCUs/MPUs... 25
Table 6. HSE oscillators embedded in STM32 MCUs/MPUs ... 29
Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products... 31
Table 8. KYOCERA compatible crystals (not exhaustive list)... 43
Table 9. NDK compatible crystals (not exhaustive list)... 43
Table 10. Recommended conditions (for consumer) ... 44
Table 11. Recommended conditions (for CAN-BUS) ... 44
Table 12. Document revision history ... 56


4/60 AN2867 Rev 25


**AN2867** **List of figures**

## **List of figures**


Figure 1. Quartz crystal model... 6
Figure 2. Impedance in the frequency domain... 6
Figure 3. I-V curve of a dipole showing a negative trans-resistance area ... 9
Figure 4. Block diagram of a typical oscillation loop based on a crystal resonator ... 10
Figure 5. Pierce oscillator circuitry ... 11
Figure 6. Inverter transfer function... 12
Figure 7. Current drive measurement with a current probe ... 15
Figure 8. Negative resistance measurement methodology description ... 19
Figure 9. Fundamental and overtone frequencies of an AT-cut quartz crystal ... 20
Figure 10. Quartz crystal theoretical model with third overtone... 21
Figure 11. Oscillator implementation for third overtone ... 21
Figure 12. Classification of low-speed crystal resonators ... 23
Figure 13. Recommended layout for an oscillator circuit ... 46
Figure 14. PCB with separated GND plane and guard ring around the oscillator ... 47
Figure 15. GND plane ... 47
Figure 16. Signals around the oscillator... 47
Figure 17. Preliminary design (PCB design guidelines not respected) ... 48
Figure 18. Final design (following guidelines) ... 49
Figure 19. GND plane ... 49
Figure 20. Top layer view... 49
Figure 21. PCB guidelines not respected ... 50
Figure 22. PCB guidelines respected ... 51


AN2867 Rev 25 5/60



**Quartz crystal properties and model** **AN2867**

### **1 Quartz crystal properties and model**


A quartz crystal is a piezoelectric device converting electric energy into mechanical energy,
and vice versa. The transformation occurs at the resonant frequency. The quartz crystal can
be modeled as shown in _Figure 1_ .


**Figure 1. Quartz crystal model**


C0


Q

Lm
Rm Cm


MS36117V1

- C0 represents the shunt capacitance resulting from the capacitor formed by the
electrodes

- Lm (motional inductance) represents the vibrating mass of the crystal

- Cm (motional capacitance) represents the elasticity of the crystal

- Rm (motional resistance) represents the circuit losses

The impedance of the crystal (assuming that Rm is negligible) is


(1)


j w [2] × Lm × Cm      - 1
Z = × ---------------------------------------------------------------------------------------- **-**
w [--] **[-]**

( C0 + Cm )       - w [2] × Lm × Cm × C0


_Figure 2_ shows the impedance in the frequency domain.


**Figure 2. Impedance in the frequency domain**

###### Impedance

Area of parallel
resonance: Fp

Inductive behavior:
the quartz oscillates


###### Frequency Frequency

ai15834c


Capacitive behavior:
no oscillation

###### Phase (deg)


+90


–90


Fs Fa


6/60 AN2867 Rev 25


**AN2867** **Quartz crystal properties and model**


Fs is the series resonant frequency when Z = 0. Its expression can be deduced from
equation _(1)_ as follows:


(2)


1
Fs = ----------------------------2 π LmCm


Fa is the antiresonant frequency when Z tends to infinity. Using equation _(1)_, it is expressed
as follows:


(3)


Cm
Fa = Fs 1 + ------- **-**
C0


The region delimited by Fs and Fa (shaded area in _Figure 2_ ) is the area of parallel
resonance. In this region, the crystal operates in parallel resonance and behaves as an
inductance that adds an additional 180° phase to the loop. Its frequency Fp (or FL: load
frequency) has the following expression:


(4)


⎛ Cm ⎞
Fp = Fs ⎜⎝ 1 + 2 ------------------------------( C0 + CL )⎟⎠


According to this equation, the oscillation frequency of the crystal can be tuned by varying
the load capacitance CL. This is why, in their datasheets, crystal manufacturers indicate the
exact CL required to make the crystal oscillate at the nominal frequency.

_Table 2_ gives an example of equivalent crystal circuit component values for an 8 MHz
nominal frequency.


**Table 2. Example of equivalent circuit parameters**


**Equivalent component** **Value**


Rm 8 Ω

Lm 14.7 mH

Cm 0.027 pF

C0 5.57 pF


Using equations _(2)_, _(3)_, and _(4)_, it is possible to calculate Fs, Fa, and Fp of this crystal:

- Fs = 7988768 Hz

- Fa = 8008102 Hz

If the load capacitance CL is equal to 10 pF, the crystal oscillates at Fp = 7995695 Hz.

To have an oscillation frequency of exactly 8 MHz, CL must be 4.02 pF.


AN2867 Rev 25 7/60



**Oscillator theory** **AN2867**

### **2 Oscillator theory**


Oscillators are among the backbone components of modern digital ICs. They can be
classified into different subfamilies, depending upon their topology and operating principles.
For each subfamily there is a mathematical model that can be used to study the oscillator
behavior, and theoretically determine its performance.


This section deals only with harmonic oscillators (relaxation oscillators are out of the scope
of this document), with particular focus (see _Section 3_ ) on Pierce oscillators. This is
because all the oscillators requiring external passive components (resonator, load
capacitors, etc.) covered by this document are of the previously mentioned type and
topology.


The harmonic oscillator family can be divided into two main subfamilies:

- negative-resistance oscillators

- positive-feedback oscillators.


These two subfamilies of oscillators are similar for what concerns the output waveform.
They deliver an oscillating waveform at the desired frequency. This waveform is typically
composed of a fundamental sine wave of the desired frequency, plus a sum of overtone
harmonics (at frequencies multiple of the fundamental one), due to the nonlinearity of
components of the oscillation loop.


The two subfamilies differ in their operating principles. A specific mathematical model
describes and analyzes each of them.


Positive-feedback oscillators are usually modeled using the Barkhausen model, where an
oscillator must fulfill the Barkhausen criterion to maintain a stable oscillation at the desired
frequency.


The Barkhausen model is not fully adequate to describe negative-resistance oscillators: the
most suitable approach is to use the negative-resistance model described in _[1]_ .

STM32 microcontrollers and microprocessors (based on Arm [®(a)] cores) feature low-speed
external (LSE) and high-speed external (HSE) oscillators designed according to the
negative-resistance principle, hence this section focuses on the presentation of this model.

##### **2.1 Negative resistance**


Theoretically speaking, a negative resistance is a dipole that absorbs heat and converting it
in electrical current, proportional to the applied voltage, but flowing in the opposite direction
(the opposite mechanism of an electrical resistance). In the real world, such a dipole does
not exist.


a. Arm and Cortex are registered trademarks of Arm Limited (or its subsidiaries or affiliates) in the US and/or
elsewhere.
The Arm word and logo are trademarks of Arm Limited (or its subsidiaries) in the US and/or elsewhere.
All rights reserved..


8/60 AN2867 Rev 25


**AN2867** **Oscillator theory**


The term negative resistance is a misnomer of negative transresistance, defined as the ratio
between a given voltage variation (∆V) and the induced current variation (∆I). Unlike the
resistance, always positive, the transresistance (also known as differential resistance) can
be either positive or negative. _Figure 3_ shows the current-voltage curve for a dipole with a
negative transresistance region. It is obvious that the V/I ratio is always positive, this is not
the case for the ∆V/∆I ratio.


The portion of the I-V curve in purple shows a negative transresistance:

Δ V V ( D )                  - V ( C )
------ **-** = ------------------------------- **-** < 0
Δ I I ( D )                  - I ( C )


The portions in blue feature a positive transresistance:

Δ V V ( B )                  - V ( A )
------ **-** = ------------------------------ **-**                                                      - 0
Δ I I ( B )                  - I ( A )


**Figure 3. I-V curve of a dipole showing a negative trans-resistance area**

##### **2.2 Transconductance**


Similarly to the conductance, defined as the inverse of the resistance, the transconductance
is defined as the inverse of the transresistance. Transconductance can also be defined as
the differential conductance, expressed as ∆I / ∆V.


AN2867 Rev 25 9/60



**Oscillator theory** **AN2867**

##### **2.3 Negative-resistance oscillator principles**


An oscillation loop is made of two branches (see _Figure 4_ ):

- The active branch, composed by the oscillator itself, provides the energy to make the
oscillation start and build up until it reaches a stable phase. When a stable oscillation is
reached, this branch provides the energy to compensate for the losses of the passive
branch.

- The passive branch is mainly composed by the resonator, the two load capacitors and
all the parasitic capacitances.


**Figure 4. Block diagram of a typical oscillation loop based on a crystal resonator**


**Passive branch** **Active branch**


Xtal


STM32


C


MSv36188V1


According to the small signals theory, when the active branch (oscillator part) is correctly
biased, to maintain a stable oscillation around the oscillator biasing voltage the latter must
have its transconductance equal to the passive branch conductance.


However, at startup, the oscillator transconductance must be higher than (multiple of) the
conductance of the passive part of the oscillation loop, to maximize the possibility to build up
the oscillation from the inherent noise of the loop. An excessive oscillator transconductance
compared to the oscillation loop passive branch conductance can saturate the oscillation
loop, and cause a startup failure.


To ensure the successful oscillator start, and to maintain stable oscillation, the ratio between
the negative resistance of the loop and the crystal maximal equivalent series resistance
(ESR) is specified for STM32 and STM8 products. It is recommended to have a ratio higher
than 5 for the HSE oscillators, and higher than 3 for the LSE oscillators.


10/60 AN2867 Rev 25


**AN2867** **Pierce oscillator design**

### **3 Pierce oscillator design**


This section describes the different parameters, and how to determine their values to be
compliant with the Pierce oscillator design.

##### **3.1 Introduction to Pierce oscillators**


Pierce oscillators are variants of Colpitts oscillators, widely used with crystal resonators. A
Pierce oscillator (see _Figure 5_ ) requires a reduced set of external components, this results
in a lower final design cost. In addition, the Pierce oscillator is known for its stable oscillation
frequency when paired with a crystal resonator, in particular a quartz-crystal resonator.


**Figure 5. Pierce oscillator circuitry**


Microcontroller


R F


In v


OSC_IN OSC_OUT


R Ext

Q


C L1 C s C L2


- Inv: the internal inverter that works as an amplifier

- Q: crystal quartz or a ceramic resonator

- RF: internal feedback resistor

- RExt: external resistor to limit the inverter output current

- CL1 and CL2: are the two external load capacitances


ai15836b


- Cs: stray capacitance, sum of the device pin (OSC_IN and OSC_OUT) and the PCB (a
parasitic) capacitances.

##### **3.2 Feedback resistor**


In most MCUs/MPUs manufactured by ST, RF is embedded in the oscillator circuitry. Its role
is to make the inverter act as an amplifier. The feedback resistor is connected between Vin
and Vout to bias the amplifier at Vout = Vin, and force it to operate in the linear region (shaded


AN2867 Rev 25 11/60



**Pierce oscillator design** **AN2867**


area in _Figure 6_ ). The noise (for example, the thermal noise of the crystal) is amplified within
the range of serial to parallel frequency (Fa, Fp), thus starting the oscillation.


**Figure 6. Inverter transfer function**


Linear area: the inverter acts as an amplifier


Vout


VDD


Saturation
region


_Table 3_ provides typical values of RF.


Saturation
region


~VDD/2 VDD


Vin


ai15837b


**Table 3. Typical feedback resistor values for given frequencies**


**Frequency** **Feedback resistor range**


32.768 kHz 10 to 25 MΩ


1 MHz 5 to 10 MΩ


10 MHz 1 to 5 MΩ


20 MHz 470 kΩ to 5 MΩ

##### **3.3 Load capacitance**


The load capacitance is the terminal capacitance of the circuit connected to the crystal
oscillator. This value is determined by the external capacitors CL1 and CL2, and the stray
capacitance of the printed circuit board and connections (Cs). The CL value is specified by
the crystal manufacturer. For the frequency to be accurate, the oscillator circuit must show
the same load capacitance to the crystal as the one the crystal was adjusted for. Frequency
stability requires that the load capacitance be constant. The external capacitors CL1 and CL2
are used to tune the desired value of CL, to reach the value specified by the crystal
manufacturer.


The following equation gives the expression of CL:


CL1 × CL2
CL = ---------------------------- CL1 + CL2 **-** + Cs


12/60 AN2867 Rev 25


**AN2867** **Pierce oscillator design**


For example, with CL = 15 pF and Cs = 5 pF,

CL1 × CL2
CL               - Cs = ---------------------------- CL1 + CL2 **-** = 10 pF


hence CL1 = CL2 = 20 pF.

##### **3.4 Oscillator transconductance**


Theoretically, to make the oscillation start and reach a stable phase, the oscillator must
provide sufficient gain to compensate for the loop losses and to provide the energy for the
oscillation buildup. When the oscillation becomes stable, the power provided to the oscillator
and the one it dissipates in the loop are equal.


Practically, because of tolerances on passive component values and their dependency upon
environmental parameters (such as temperature), the ratio between oscillator gain and
oscillation loop critical gain cannot just exceed 1. This would induce a too long oscillator
startup time, and even prevent the oscillator from starting up.


This section describes the two approaches that can be used to check if an STM32 oscillator
can be paired with a given resonator, to ensure that the oscillation is started and maintained
under the specified conditions for both resonator and oscillator. The approach depends on
how the oscillator parameters are specified in the device datasheet:

- If the oscillation loop maximum critical transconductance parameter (Gm_crit_max) is
specified, ensure that it is greater than the oscillation loop critical crystal gain (gmcrit,
see the formula below). Note that the maximum critical crystal transconductance can
be named either Gm_crit_max or Gm, depending on the STM32 product documentation.

- If the oscillator transconductance parameter (gm) is specified, make sure that the gain
margin ratio (gainmargin) is bigger than 5.

The gain margin ratio is determined by the formula gainmargin = gm / gmcrit, where

- gm is the oscillator transconductance specified in the STM32 datasheet. The HSE
oscillator transconductance is in the range of a dozen of mA/V, while the LSE oscillator
transconductance ranges from a few to a few dozens of µA/V, depending upon the
product.

- gmcrit is defined as the minimal transconductance required to maintain a stable
oscillation when it is a part of the oscillation loop for which this parameter is relevant.
gmcrit is computed from oscillation loop passive components parameters.

Assuming CL1 = CL2, and that the crystal sees the same CL on its pads as the value given
by the crystal manufacturer, gmcrit is expressed as follows:

gmcrit = 4 × ESR × ( 2 π F ) [2] × ( C0 + CL ) [2]


where:

- ESR is the equivalent series resistance

- C0 is the crystal shunt capacitance

- CL is the crystal nominal load capacitance.

- F is the crystal nominal oscillation frequency


AN2867 Rev 25 13/60



**Pierce oscillator design** **AN2867**


For example, to design the oscillation loop for the HSE oscillator embedded in an STM32F1
microcontroller with a transconductance value (gm) of 25 mA/V, we choose a quartz crystal
from Fox, with the following characteristics:

- Frequency = 8 MHz

- C0 = 7 pF

- CL = 10 pF

- ESR = 80 Ω


To check if this crystal oscillates, let us calculate gmcrit:

6 2                     - 12                     - 12 2
gmcrit = 4 × 80 × ( 2 × π × 8 × 10 ) × ( 7 × 10 + 10 × 10 ) = 0.23 mA ⁄ V


Calculating the gain margin gives:

gm 25
gainm arg in = ----------------- gmcrit = ----------- 0.23 = 107


The gain margin is sufficient to start the oscillation and the gainmargin > 5 condition is met.
The oscillator is expected to reach stable oscillation after the typical delay specified in the
datasheet.


If an insufficient gain margin is found (gainmargin < 5), the oscillation can start when
designing and testing the final application, but this does not guarantee that the oscillation
starts in operating conditions. It is highly recommended that the selected crystal has a gain
margin higher than or equal to 5 (try to select a crystal with a lower ESR and/or a lower CL).

In a second example of the case where the maximal critical crystal transconductance is
given, the HSE oscillator embedded in STM32G0 microcontrollers has Gm = 1.5 mA/V. gmcrit
for the implemented oscillator must stay below this value. The Fox quartz crystal described
above respects this condition.


The conversion between the oscillator transconductance (gm) and the oscillation loop
maximal critical transconductance (Gm_crit_max) is given by Gm_crit_max = gm / 5.

_Note:_ _Before any verification, the crystal chosen must vibrate at a frequency that respects the_
_oscillator frequency range given in the STM32 datasheet._

##### **3.5 Drive level and external resistor calculation**


The drive level (DL) and external resistor value (RExt) are closely related, and are
addressed in the same section.


**3.5.1** **Calculating the drive level**


The drive level is the power dissipated in the crystal. It must be limited, otherwise the quartz
crystal can fail because of excessive mechanical vibrations. The maximum drive level is
specified by the crystal manufacturer, usually in mW. Exceeding this value can lead to
crystal damage, or to a shorter device lifetime.


14/60 AN2867 Rev 25


**AN2867** **Pierce oscillator design**


The drive level is given by the formula: DL = ESR × IQ, where:

- ESR is the equivalent series resistor (specified by the crystal manufacturer):

⎛ C0 ⎞ [2]
ESR = Rm × ⎝ 1 + ----- CL **-** ⎠

- IQ is the current flowing through the crystal in RMS. This current can be displayed on
an oscilloscope as a sine wave. The current value can be read as the peak-to-peak
value (IPP). When using a current probe (as shown in _Figure 7_ ), the voltage scale of an
oscilloscope may be converted into 1 mA / 1 mV.


**Figure 7. Current drive measurement with a current probe**


Crystal

To oscilloscope


Current probe


ai15838b


So, as described previously, when tuning the current with the potentiometer, the current
through the crystal (assuming it is sinusoidal) does not exceed IQmax RMS, given by:

IQmaxRMS = DL ----------------- ESRmax = ---------------------- IQmax2 2PP **-**


Therefore, the current through the crystal (peak-to-peak value read on the oscilloscope)
should not exceed a maximum peak-to-peak (IQmaxPP) equal to:


2 × DLmax
IQmaxPP = 2 × -------------------------- ESR **-**


Hence, the need for an external resistor RExt (refer to _Section 3.5.3_ ) when IQ exceeds
IQmaxPP. The addition of RExt becomes mandatory, and is added to ESR in the expression
of IQmax.


AN2867 Rev 25 15/60



**Pierce oscillator design** **AN2867**


**3.5.2** **Another drive level measurement method**


The drive level can be computed as DL= I²QRMS × ESR (IQRMS is the RMS AC current).

This current can be calculated by measuring the voltage swing at the amplifier input with a
low-capacitance oscilloscope probe (no more than 1 pF). The amplifier input current is
negligible with respect to the current through CL1, so we can assume that the current
through the crystal is equal to the current flowing through CL1. Therefore, the RMS voltage
at this point is related to the RMS current by IQRMS = 2 π F x VRMS x Ctot, with:

- F = crystal frequency

Vpp

- VRMS = --------- **-**, where Vpp is the peak-to-peak voltage measured at CL1 level

2 2


- Ctot = CL1 + (Cs / 2) + Cprobe where:

- CL1 is the external load capacitance at the amplifier input

- Cs is the stray capacitance

- Cprobe is the probe capacitance


ESR × (π × F × Ctot ) [2] × ( Vpp ) [2]


Therefore, DL = --------------------------------------------------------------------------------------- **-** .


= --------------------------------------------------------------------------------------- **-**
2


This value must not exceed the drive level specified by the crystal manufacturer.


_Note:_ _Use special care when measuring voltage swing at LSE input, as it is very sensitive to load_
_capacitance. It is recommended to use a 0.1 pF input capacitance probe._


**3.5.3** **Calculating the external resistor**


The role of this resistor is to limit the drive level of the crystal. With CL2, it forms a low-pass
filter that forces the oscillator to start at the fundamental frequency and not at overtones
(prevents the oscillator from vibrating at the odd harmonics of the fundamental frequency). If
the power dissipated in the crystal is higher than the value specified by the crystal
manufacturer, the external resistor RExt becomes mandatory to avoid overdriving the crystal.
If the power dissipated in the selected quartz is lower than the drive level specified by the
crystal manufacturer, the insertion of RExt is not recommended, and its value is then 0 Ω.

An initial estimation of RExt is obtained by considering the voltage divider formed by RExt
and CL2. Thus, the value of RExt is equal to the reactance of CL2.

Therefore, RExt = 1 / (2 π F CL2), and so, with an oscillation frequency of 8 MHz and
CL2 = 15 pF, we have RExt = 1326 Ω .

The recommended way for optimizing RExt is to first choose CL1 and CL2 as explained
before, and to connect a potentiometer in the place of RExt. The potentiometer should be
initially set to be approximately equal to the capacitive reactance of CL2. It should then be
adjusted as required, until an acceptable output and crystal drive level are obtained.


**Caution:** After calculating RExt, it is recommended to recalculate the gain margin (refer to _Section 3.4_ )
to make sure that the addition of RExt has no effect on the oscillation condition. The value of
RExt must be added to ESR in the expression of gmcrit, and gm » gmcrit must also remain true:

gm » gmcrit = 4 × (ESR + RExt) × (2 π F)² × (C0 + CL)²

_Note:_ _If RExt is too low, there is a considerable increase of the power dissipation by the crystal. If,_
_on the other hand, RExt is too high, there is no oscillation._


16/60 AN2867 Rev 25


**AN2867** **Pierce oscillator design**

##### **3.6 Startup time**


This is the time required by the oscillation to start and then build up, until it reaches a stable
oscillation phase. The startup time depends, among other factors, on the Q-factor of the
resonator used. If the oscillator is paired with a quartz-crystal resonator characterized by its
high Q-factor, the startup time is higher when ceramic resonators are used (these are known
for their poor Q-factor, compared to quartz-crystal resonators). The startup time also
depends upon the external components, CL1 and CL2, and on the crystal frequency. The
higher the crystal nominal frequency, the lower the startup time. In addition, startup
problems usually arise because the gain margin is not properly dimensioned (as explained
previously). This is caused either by CL1 and CL2 being too small or too large, or by the ESR
being too high.


As an example, an oscillator paired with a few MHz nominal frequency crystal resonator
typically starts up after a delay of a few ms.


The startup time of a 32.768 kHz crystal ranges between 1 and 5 s.

##### **3.7 Crystal pullability**


Crystal pullabilty, also known as crystal sensitivity, measures the impact of small variations
of the load capacitance seen by the crystal on the oscillation frequency shifting. This
parameter has more importance when dealing with low-speed oscillators, as they are used
to clock time-keeping functions (such as real-time clock).


When the final application is still in the design stage, the influence of this parameter on the
low-speed oscillator accuracy (and consequently on all the time-keeping functions clocked
by this oscillator) is not obvious. This is because the designer fine tunes the load capacitors
until the desired oscillation frequency is obtained. When the design reaches production
stage it is frozen, and all the passive components including the load capacitors have their
values well defined. Any change of the load capacitance induces a shift of the oscillation
frequency.


Changes in the capacitive load (CL) seen by the crystal can be thought of as due to
inadequate operation environment, and only happening when the final design is not properly
operated. In practice, this is not true since changes of the load capacitance are rather
frequent and must be taken into account by the designer. The main contributors to the
capacitive load (CL) seen by the oscillator are

- the capacitance of the load capacitors CL1 and CL2

- the stray capacitance of the PCB paths

- the parasitic capacitance of the oscillator pins.


Any change on the capacitances listed above directly shifts the oscillation frequency. When
the design is in production stage, many of these capacitance values cannot be accurately
controlled. Selecting a crystal with low pullability limits the influence of such production
uncertainties on the final oscillation frequency accuracy.


Generally speaking, the higher the load capacitance of a crystal, the lower its pullability. As
an example, let us consider a crystal with a pullability of 45 PPM/pF. To fine-tune the
oscillation frequency, this crystal is loaded by two C0G ceramic capacitors (with a ± 5%
tolerance of their nominal value), CL1 and CL2, with the same 7 pF capacitance.

From the crystal point of view, the two load capacitors are mounted in series, which means
that their contribution to CL is (CL1 = CL2) / 2. The tolerance on their contribution to CL


AN2867 Rev 25 17/60



**Pierce oscillator design** **AN2867**


remains the same, and is equal to ± 5%. If we consider that all the remaining contributors to
the CL are maintained to their nominal values at design stage (to assess the frequency shift
magnitude induced only by load capacitor tolerances), then the load capacitance seen by
the crystal (CL) either decreases by 0.175 pF, or increases by the same value. This induces
an oscillation shift of:


0.175 pF × 45 PPM / pF = ~7.8 PPM (~0.7 s/day for a time-keeping function such as RTC)


The above example shows that lower pullability results in lower impact of small load
capacitance deviation on the frequency shifting. Crystal pullability is an important factor
when defining the final application PPM budget.

6
Cm × 10
Pullability = --------------------------------------- **-**
( PPM ⁄ pF )

2 × ( C0 + CL ) [2]


where

- Cm is the crystal motional capacitance (in pF)

- C0 is the crystal shunt capacitance (in pF)

- CL is the crystal nominal load capacitance (in pF)

The following sections give a more detailed description on how to calibrate the oscillation
frequency, and how to estimate the final accuracy uncertainty (PPM) budget.

##### **3.8 Safety factor**


**3.8.1** **Definition**


Resonators (such as crystal resonators) undergo aging effects that manifest themselves
over time in deviations of resonator parameters from the values defined by the
specifications. Among the impacted parameters there is the resonator ESR, whose value
depends upon the environment conditions, such as moisture and temperature. The
oscillator transconductance depends upon the power supply voltage and upon the
temperature.


The safety factor parameter enables to determine the oscillator safe operation under the
operating conditions and during the application life. It measures the ability of the oscillator
not to fail under operating conditions.


The safety factor is defined as the ratio between the oscillator negative resistance and its
ESR:


+ Crystal ESR
Oscillator negative resistance RADD
Sf = ---------------------------------------------------------------------------- Crystal ESR **-** = ------------------------------------------------------- Crystal ESR **-**


18/60 AN2867 Rev 25


**AN2867** **Pierce oscillator design**


**3.8.2** **Measurement methodology**


To measure the oscillator negative resistance, a resistance is added in series to the
resonator, as indicated in _Figure 8_ .


**Figure 8. Negative resistance measurement methodology description**


**STM32**


Q RADD


CL1


CL2


MSv37268V1


The oscillator negative resistance is the value of the smallest series resistance RADD
preventing the oscillator from starting up successfully.


In practice, this value is set by conducting a series of experiments in which the value of the
series resistance is slightly increased compared to the previous experiment. The sequence
stops when the oscillator is unable to start correctly. The oscillator negative resistance is
equal to the value of the added series resistance.


**3.8.3** **Safety factor for STM32 and STM8 oscillators**


_Table 4_ summarizes the safety factor (Sf) for oscillators embedded in STM32 and STM8
devices. For the LSE oscillator, the oscillation is considered safe for Sf ≥ 3, while for the
HSE oscillator this is true when Sf ≥ 5.


**Table 4. Safety factor (Sf) for STM32 and STM8 oscillators** **[(1)]**

**Assurance level**
**Safety factor (Sf)**

**HSE** **LSE**


Sf ≥ 5 Safe Very safe


3 ≤ Sf < 5


Not safe


Safe


Sf < 3 Not safe


1. Safe and very safe oscillations are shown in green, unsafe oscillation in yellow.


AN2867 Rev 25 19/60



**Pierce oscillator design** **AN2867**

##### **3.9 Oscillation modes**


**3.9.1** **What are fundamental and overtone modes?**


Equation _(4)_ gives the oscillation frequency Fp of a crystal, which depends on the series
resonant frequency Fs for which the crystal impedance is null. The oscillator is said to
operate in fundamental mode when vibrating around Fp.

Fs (and hence Fp) depend upon the parameters of the crystal theoretical model illustrated in
_Figure 1_ . These parameters, given by the crystal manufacturer, define the frequency for
which the crystal is designed to oscillate around the fundamental frequency.


In real life, an AT-cut quartz crystal impedance reaches a zero value for several frequencies,
which correspond to the odd multiples of its fundamental vibration frequency. A crystal can
also vibrate around one of those odd multiples, these are the overtone oscillation modes.
_Figure 9_ represents the cancellation of an AT-cut crystal impedance for the fundamental
frequency, its following odd multiples (third and fifth overtones are represented), as well as
some spurious frequencies.


**Figure 9. Fundamental and overtone frequencies of an AT-cut quartz crystal**


_Note:_ _AT-cut quartz corresponds to most of the crystals to use with HSE. For LSE, tuning fork_
_crystals can be used, but they do not show the same oscillation mode possibilities (Figure 9_
_is not valid for them). In this part, we consider an AT-cut quartz crystal when referring to a_
_crystal._


This multiple-time cancellation is because a more accurate quartz crystal theoretical model
shows an RLC branch for each one of its overtone modes, as illustrated in _Figure 10_ .


20/60 AN2867 Rev 25


**AN2867** **Pierce oscillator design**


**Figure 10. Quartz crystal theoretical model with third overtone**


C0

=


Lm


Rm


Cm


Q m m m
Fundamental mode


Third overtone mode


Lm3OT


Rm3OT


Cm3OT


= Lm                 - Rm = Cm / 9 MS55485V2


For example, it is possible to use the third overtone mode by implementing the oscillator as
shown in _Figure 11_, to suppress the fundamental frequency (theoretically each overtone
mode can be selected by suppressing the previous ones).


**Figure 11. Oscillator implementation for third overtone**


Microcontroller


RF


Inv


OSC_IN OSC_OUT


RExt

Q


CL1


LL1 CS CL2


MS55484V1


**3.9.2** **Third overtone mode: pros and cons**


Because of the thickness, the crystals designed for a high frequency fundamental mode are
very expensive, requiring high-end cutting technologies and a lot of caution for
implementation. Practically, it becomes impossible to operate in fundamental mode for a
frequency above 50 MHz. This is why most of the high frequency crystals are designed to
work in the third overtone mode (it is possible to cut the crystal for a frequency three times
lower than the one it oscillates at).


AN2867 Rev 25 21/60



**Pierce oscillator design** **AN2867**


The model for a crystal operating in third overtone mode ( _Figure 11_ ) shows a resistance Rm
approximately three times higher and a capacitance Cm nine times lower than those
associated with the fundamental mode.


For the third overtone mode, these differences mean a higher Q-factor since the quality
factor for an RC series circuit is 1 / ωRC (less energy loss, more stable performances, better
jitter, and lower pullability, see _Section 3.7_ ). A lower pullability means a lower frequency shift
when the application is deployed in the field, at the expense of lower tunability of the
oscillation frequency.


**3.9.3** **Considerations for crystals interfaced with STM32 products**


The oscillators integrated in the STM32 products have been validated for use in the
fundamental mode, respecting the implementation of _Figure 5_ . If a third overtone crystal is
used with this implementation, the theory indicates that it does not start vibrating at the third
harmonic frequency, but at the fundamental one.


_Note:_ _The startup mode of an oscillator can even involuntarily balance between the two modes if_
_its external components have not been chosen according to what indicated in this_
_document._


22/60 AN2867 Rev 25


**AN2867** **Guidelines to select a suitable crystal and external components**

### **4 Guidelines to select a suitable crystal** **and external components**

##### **4.1 Low-speed oscillators embedded in STM32 MCUs/MPUs**


The low-speed resonator market provides a wide range of crystal resonators. Selecting the
most adequate one for a given design depends on many parameters. The most important
parameters to be taken into account (only technical factors are listed) are:

- Crystal size or footprint

- Crystal load capacitance (CL)

- Oscillation frequency offset (PPM)

- Startup time


A trade-off between the above parameters must be found, depending on the key design
criteria. _Figure 12_ shows that the resonators available on the market can be divided into two
categories, depending upon the above-mentioned factors and trade-offs.


**Figure 12. Classification of low-speed crystal resonators**


High
(12.5 pF)


Medium
(7 pF)


Low
(�������


Low drift


Incresed robustness against noisy
environments


Low power


Low Medium High


LSE drive level / Gm_crit_max


MSv36189V3


A resonator with a relatively high load-capacitance (such as 12.5 pF) requires more power
for the oscillator to drive the oscillation loop at the resonator nominal frequency. Designs
targeting low power consumption (for example, RTC application powered by coin-batteries
requiring very long autonomy) are consequently more likely to use resonators with relatively
small load capacitance. On the other side, big load capacitance resonators have a much
smaller pullabilty compared to resonators with small load capacitance. As a result, designs
without severe constraints on power consumption tend to use big load capacitance crystals
to reduce pullability.


One of the key areas where crystal resonators are massively used is the hand-held and
wearable appliance consumer market (such as smartphones, Bluetooth [®] kits). For this


AN2867 Rev 25 23/60



**Guidelines to select a suitable crystal and external components** **AN2867**


market segment, the crystal size is of critical importance. However, it is widely known that
small-footprint crystals come with high crystal ESR. The choice may be harder if the target
design has severe constraints in terms of power consumption (the usual scenario). In this
case, choose a crystal with a load capacitance as small as possible to optimize power
consumption even if this compromises pullabilty. In addition, crystals with high ESR may
have a slightly longer startup time. If there are no constraints on crystal size, then it is
recommended to choose a crystal with the smallest possible ESR.


In noisy environments (almost always the case for industrial applications), if there are no
constraints on power consumption, it is recommended to choose crystals with high load
capacitance. These crystals require a high-drive current from the oscillator, but are more
robust against noise and external perturbations. Another advantage is that the design
pullability is minimized.


Depending on the device used, all the resonator families listed below can be compatible
with your design, or only some of them. STM32 devices embed two types of low-speed
oscillator (LSE):

- Constant gain

This type of LSE oscillator features a constant gain, which makes them compatible only
with a few crystal groups mentioned above. For example, LSE oscillators embedded in
STM32F2 and STM32L1 MCUs target designs with severe power consumption
constraints. The selected crystal should consequently have a low load capacitance and
a moderate ESR. LSE oscillators embedded in STM32F1 MCUs target crystal
resonators with moderate ESR and moderate load capacitance.

- Configurable gain

The main advantage of LSE oscillators belonging to this family is the compatibility with
a large number of crystals. Almost no constraint comes by the device embedding this
kind of oscillator. The large list of compatible resonator crystals allows the designer to
focus on design constraints (such as power consumption, footprint) when selecting a
compatible resonator. These oscillators are divided into two categories:

- Dynamically (on-the-fly) modifiable gain LSE oscillators

The gain of this type of LSE oscillators can be changed either before starting the
oscillator or after enabling it.

- Statically modifiable gain LSE oscillators

The gain can be changed only when the LSE oscillator is turned off. If the
oscillator transconductance has to be increased or decreased, the LSE must be
turned off first.


_Table 5_ gives the list of low-speed oscillators (LSE) embedded in STM32 devices.


**Caution:** When the gain is modified statically or on-the-fly, the calibration of the oscillation frequency
must be readjusted to estimate the final accuracy uncertainty (PPM) budget.


**Caution:** In STM32F0 and STM32F3 MCUs, High drive mode (gm = 25 µA/V) must be used only with
12.5 pF crystals, to avoid saturating the oscillation loop and causing a startup failure. When
used with a low CL crystal (for example 6 pF), the oscillation frequency jitters and duty cycle
can be distorted.


24/60 AN2867 Rev 25


**AN2867** **Guidelines to select a suitable crystal and external components**


**Table 5. LSE oscillators embedded into STM32 MCUs/MPUs** **[(1)]**


**Series** **Drive level** **gm (min)** **Gm_crit_max** **Unit**


C0


F0, F3


Medium high 8.5 1.7


High 13.5 2.7


Low 5 1.0


Medium low 8 1.6


Medium high 15 3


High 25 5


µA/V


F1, T


Not available


Not available µA/V

F2, F4_g1 [(2)] 2.8 0.56


2.8 0.56


5 1


F4_g2 [(3)]


F7


Low 2.4 0.48


Medium low 3.75 0.75
µA/V

Medium high 8.5 1.7


High 13.5 2.7


Low 2.8 0.56

µA/V
High 7.5 1.5


L1 Not available 3 0.6 µA/V


G0, G4
H7
L0, L4, L4+, L5
MP1, MP2
N6
U0, U3, U5 [(4)]
WB, WB0, WBA [(5)], WL


C5, H5, G5, H7P


Low 2.5 0.5


Medium low 3.75 0.75


Medium high 8.5 1.7


High 13.5 2.7


Medium low 3.75 0.75


Medium high 8.5 1.7


High 13.5 2.7


µA/V


1. Color code:

  - Light blue: LSE oscillators with transconductance modifiable on the fly (dynamically)

  - Yellow: LSE oscillators with non-modifiable transconductance

  - Gray: LSE oscillators with statically-modifiable transconductance


2. STM32F4 series with LSE generation 1 (STM32F401/405/407/415/417/427/429/437/439xx MCUs
featuring LSE oscillators with non modifiable transconductance).


3. STM32F4 series with LSE generation 2 (STM32F410/411/412/413/423/446/469/479xx MCUs featuring
LSE oscillators with statically modifiable transconductance).


4. STM32U575/585 rev. X devices do not support low drive mode.


5. STM32WBA devices do not support low drive mode.


AN2867 Rev 25 25/60



**Guidelines to select a suitable crystal and external components** **AN2867**

##### **4.2 How to select an STM32-compatible crystal**


This section describes the procedure recommended to select suitable crystal/external
components. The procedure is based on the following steps:


**Step 0: Choose a fundamental mode designed resonator**


Choose a fundamental mode designed resonator (as explained in _Section 3.9_, the STM32
oscillators are validated to work with resonator vibrating in fundamental mode and while
using the Pierce oscillator circuitry presented in _Figure 5_ ), and make sure that the resonator
chosen is designed to work in fundamental mode.


**Step 1: Check the resonator compatibility with the selected STM32**


To check the compatibility between the selected crystal and the STM32 MCU/MPU, first
identify the procedure to follow among the two described in _Section 3.4_ . The decision must
be made based on the oscillator specification provided in the datasheet.

- If the oscillator transconductance parameter is specified, then apply the second
procedure. Ensure that the gain margin ratio is higher than five (x5) to make sure that
the crystal is compatible with the selected STM32 part.

- If Gm_crit_max is specified instead, make sure that gmcrit for the oscillation loop is
smaller than the specified Gm_crit_max value.


**Step 2: Determine the capacitance value of the load capacitors CL1 and CL2**

To determine the correct capacitance values for CL1 and CL2 load capacitors, apply the
formula specified in _Section 3.3_ . The values obtained are approximations of the exact
capacitances to be used. In a second phase, to fine-tune the values of the load capacitors,
go through a series of experimental iterations, until the right capacitance values are found.


During the experimental phase, use a standard crystal, one whose PPM drift is well known
when it is loaded by the crystal nominal load capacitance (CL). This kind of crystal can be
provided by the manufacturer upon request. After this crystal has been chosen, calculate its
oscillation frequency (Fstandard) when the crystal is loaded by its nominal load capacitance.
This frequency is given by the formula:


⎛ ⎞
= × ⁄ 10 [6]
Fs tandard Fnominal ⎝ PPMs tandard ⎠


where:

- Fstandard is the standard crystal oscillation frequency when it is loaded by its nominal
load capacitance

- Fnominal is the oscillation nominal frequency specified in the crystal datasheet

- PPMstandard is the oscillation frequency drift of the standard crystal, as characterized by
the crystal manufacturer


26/60 AN2867 Rev 25


**AN2867** **Guidelines to select a suitable crystal and external components**


When Fstandard is computed, go through the following sequence:

1. Make the first experimental iteration with CL1 and CL2 capacitance values determined
by calculation:

- If the oscillation frequency is equal to Fstandard, CL1 and CL2 are the correct
capacitances. The user can therefore skip substeps _2_ and _3_ .

- If the oscillation frequency is slower than Fstandard go to substep _2_, otherwise
execute substep _3_ .

2. For this experimental iteration, decrease CL1 and CL2 capacitance values, measure
again the oscillation frequency, and compare it to Fstandard:

- If the oscillation frequency is slower than Fstandard, execute substep _2_, otherwise
execute substep _3_ .

- If the oscillation frequency is almost equal to Fstandard, use the latter CL1 and CL2
capacitance values.

3. For this experimental iteration, increase CL1 and CL2 capacitance values, measure
again the oscillation frequency, and compare it to Fstandard:

- If the oscillation frequency is slower than Fstandard, execute substep _2_, otherwise
execute substep _3_ .

- If the oscillation frequency is almost equal to Fstandard, use the latter CL1 and CL2
capacitance values.


**Step 3: Check the safety factor of the oscillation loop**


The safety factor must be assessed as described in _Section 3.8_ to ensure a safe oscillation
of the oscillator under operating conditions.


_Note:_ _Many crystal manufacturers can check device/crystal pairing compatibility upon request. If_
_the pairing is judged valid, they can provide a report including the recommended CL1 and_
_CL2 values, as well as the oscillator negative resistance measurement. In this case steps 2_
_and 3 can be skipped._


**Step 4: Calculate the drive level and external resistor**


Compute the drive level (DL) (see _Section 3.5_ ) and check if it is greater or lower than
DLcrystal:

- If DL < DLcrystal, no need for an external resistor (a suitable crystal has been found).

- If DL > DLcrystal, the user should calculate RExt to have: DL < DLcrystal. The user should
then recalculate the gain margin taking RExt into account.
If gain margin > 5, a suitable crystal has been found. If not, then this crystal does not
work, another one must be chosen. Return to _Step 1: Check the resonator compatibility_
_with the selected STM32_ to run the procedure for the new crystal.


**Step 5 (optional): Calculate the PPM accuracy budget**


Use the following formula to estimate the PPM accuracy budget for the application:


PPMBudget = PPMcrystal + Deviation ( CL ) × Pullabilitycrystal


where:

- PPMBudget is the estimated accuracy for the oscillation frequency

- PPMcrystal is the crystal PPM accuracy specified in the datasheet


AN2867 Rev 25 27/60



**Guidelines to select a suitable crystal and external components** **AN2867**


Deviation (CL) is expressed in pF. It measures the deviation of the load capacitance (CL)
due to tolerances on load capacitor values and the variation of the stray capacitance (CS)
due to PCB manufacturing process deviation.


Pullabilty is expressed in PPM / pF (refer to _Section 3.7_ ).


_Note:_ _The PPM budget calculated above does not take into account the temperature variation,_
_which can make the PPM budget bigger._


28/60 AN2867 Rev 25


**AN2867** **Recommended resonators for STM32 MCUs/MPUs**

### **5 Recommended resonators for STM32 MCUs/MPUs**

##### **5.1 STM32-compatible high-speed resonators**

The high-speed oscillator (HSE) embedded into STM32 products [(a)] is compatible with
almost all the resonators available on the market. The recommended resonators are
provided by a wide range of manufacturers, including:

- ABRACON

- ECS (www.ecsxtal.com)

- EPSON (http://www5.epsondevice.com)

- KYOCERA

- Micro Crystal

- muRata (www.murata.com)

- NDK (http://www.ndk.com)

- RIVER (http://www.river-ele.co.jp)


Several KDS tools are available to select the more recent and high-demand crystals, among
them the STM32 Crystal Selection Tool from ECS, the IC Matching Information provided by
NDK, and IC manufacture Information of KDS.


Compatible resonators come with various frequencies and technologies (ceramic
resonators and quartz-crystal resonators working in fundamental mode are all compatible
with the HSE oscillator embedded in STM32 MCUs/MPUs). _Table 6_ summarizes the
supported frequency ranges.


**Table 6. HSE oscillators embedded in STM32 MCUs/MPUs**


**F0** **F1**
**Series** **F2** **F4** **F7** **L0** **L1**
**F3** **T**


**C0**
**L4, L4+**
**L5**
**H7**
**G0, G4**
**MP1**
**U0**


**G5**
**H7P**
**C5**
**H5**
**U3**
**U5**


**MP2** **N6** **Unit**


Frequency
4 - 32 4 - 16 4 - 25 4 - 26 4 - 26 1 - 25 1 - 24 4 - 48 4 - 50 16 - 48 16 - 48 MHz
range


gm (min) 10 25 5 5 5 3.5 3.5 7.5 7.5 9.75 9.57
mA/V
Gm_crit_max 2 5 1 1 1 0.7 0.7 1.5 1.5 1.95 1.95

##### **5.2 STM32-compatible low-speed resonators**


_Table 7_ contains a not exhaustive list (only the compatible resonator part numbers checked
by ST are included) of low-speed quartz-crystal 32.768 kHz resonators that are either
compatible with the whole STM32 portfolio, or with a subset.


a. This is not applicable for STM32WB, STM32WB0, STM32WBA and STM32WL series due to the RF
constraints. For information about HSE oscillator compatibility with these devices, refer to _Precise HSE_
_frequency and startup time tuning for STM32 wireless MCUs_ (AN5042), available on _www.st.com_ .


AN2867 Rev 25 29/60



**Recommended resonators for STM32 MCUs/MPUs** **AN2867**


Different footprints are provided to facilitate crystal selection, even if there are geometric
constraints for the final application.


30/60 AN2867 Rev 25


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products**


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


**ESR**
**max**
**(kΩ)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


RIVER TFX-05X 90 1.5


SII SC-12S (2 terminals) 90 1.4


ECS-.327-6-1210-TR


C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
5 0.6447
U3, U5


C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
7 1.1026
U5


9 1.6824 C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.9910 F0, F3


C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.8356
U3, U5


C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
7 1.0768
U5


9 1.6506 C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.9484 F0, F3


C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.7692
U3, U5


1.2 x 1.0
mm [2]


C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
ECS-.327-7-1210-TR 7 1.0012
U5

90 1.1

ECS-.327-9-1210-TR 9 1.5567 C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ECS-.327-12.5-121012.5 2.8225 F0, F3
TR


ECS


Würth
Elektronik


90 1.4 C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,

830108211801 7 1.0767
U3, U5


830108091501 12.5 2.9484 F0, F3


ECS-.327-5-1210B-NTR


C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
5 0.5731
U3, U5


ECS-.327-7-1210B-N- C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.9800
TR U3, U5

80 1.5

ECS-.327-9-1210B-N- C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
9 1.4955
TR U5


ECS-.327-12.5-1210B12.5 2.6587 C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
N-TR


830107834801


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.8356
U3, U5


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2,
4 0.4103
U0, U3, U5


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


ABS04W-32.768 KHz 4
pF


**ESR**
**max**
**(kΩ)**


1.2 x 1.0
ABRACON
mm [2]


ABS04W-32.768 KHz 6 C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.7630
pF U3, U5

80 1.5

ABS04W-32.768 KHz 9 C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
9 1.4955
pF U5


ABS04W-32.768 KHz
12.5 2.6587 C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
12.5 pF


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
4 0.4449
U3, U5


CM9V-T1A / CM9VMicro Crystal
T1A 0.3


ECS-.327-6-16-TR3



1.4


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.8356
U3, U5


7 1.0768 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


9 1.6506 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.9484 F0, F3


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.8132
U3, U5


NX1610SE 32.768 kHz C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.7437
EXS00A-MU01500 U3, U5

60 [(4)] 1.55

NX1610SE 32.768 kHz C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
9 1.1323
EXS00A-MU01499 U5


NX1610SE 32.768 kHz
12.5 2.0083 C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
EXS00A-MU01498


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-7-16-C-TR 7 1.0513

1.3 U3, U5


ECS-.327-9-16-TR 9 1.6190 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


1.6 x 1.0
mm [2]


ECS


NDK


ECS-.327-12.5-16-TR 12.5 2.9062 F0, F3


NX1610SA 32.768 kHz
EXS00A-MU00658
1.3


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.8132
U3, U5


NX1610SA 32.768 kHz
12.5 2.9062 F0, F3
EXS00A-MU01367


NX1610SE 32.768 kHz
EXS00A-MU01501


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2,
6 0.5799
U0, U3, U5


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.7910
U3, U5


12.5 2.8642 F0, F3


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


SII SC-16S


**ESR**
**max**
**(kΩ)**


EPSON


FC1610AN 32.768000 9 1.5877
C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
kHz 9


FC1610AN 32.768000 12.5 2.8642
F0, F3
kHz 12.5 90 1.2


6 0.7910 C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
U3, U5


CITIZEN CM1610H


7 1.0261 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


9 1.5877 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.8642 F0, F3


1.6 x 1.0
mm [2]


ECS


Würth
Elektronik


ABRACON


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2,
ECS-.327-4-16R-TR 60 1,5 4 0,3077
U0, U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-6-16R-TR 6 0,5722
U3, U5


C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
ECS-.327-9-16R-TR 9 1,1216
U5


ECS-.327-12.5-16R-TR 12,5 1,994 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2,
830108214001 90 1,2 4 0.4126
U0, U3, U5


C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
830066431 7 1.0261
U5


830066198 9 1.5876 C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


830065253 12,5 2.8641 F0, F3


ABS05-32.768 kHz 12.5 2.9062 F0, F3


ABS05W-32.768 kHz-D 70 2 4 0.4272 C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
U3, U5


ABS05-32.768 kHz 9
pF 90 1.3


9 1.6190
C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


**ESR**
**max**
**(kΩ)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
5 0.6056
U3, U5


7 1.0513 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


9 1.6190 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.9062 F0, F3


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
5 0.4298
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.7350
U3, U5


9 1.1216 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 1.9940 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


1.6 x 1.0
RIVER
mm [2]


TFX-04 90 1.3


TFX-04C 60 1.5


ABS06-107- C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ABRACON 80 1.5 4 0.4103
32.768kHz-T U3, U5


ECS-.327-6-12-TR


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.8312
U3, U5


ECS-.327-7-12-TR 7 1.0513 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5

90 1.3


ECS-.327-9-12-TR 9 1.6190 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ECS-.327-12.5-12-TR 12.5 2.9062 F0, F3


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-CDX-1082 80 1.5 4 0.4103
U3, U5


2.0 x 1.2
mm [2]


ECS


ECS-.327-6-12RR-TR


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.7372
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-7-12RR-TR 7 0.8983

1.7 U3, U5


ECS-.327-9-12RR-TR 9 1.3589 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ECS-.327-12.5-12R-TR 70 12.5 2.3933 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ECS-.327-6-12R-TR


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.4517
U3, U5


1.3 C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,

ECS-.327-9-12R-TR 9 0.8994
U3, U5


ECS-.327-12.5-12R-TR 12.5 1.6145 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


**ESR**
**max**
**(kΩ)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


FC-12D 32.768000kHz

75 0.8 9 1.2213 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


FC-12D 32.768000kHz
12.5 2.2495 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
12.5


CM8V-T1A 0.3 90


CC8V-T1A 80


CM8V-T1A 70


1.2


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
4 0.4126
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.7910
U3, U5


7 1.0261 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


9 1.5877 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.8642 F0, F3


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
4 0.3667
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.7031
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.9120
U3, U5


9 1.4113 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.5460 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
4 0.3209
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.6152
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.7980
U3, U5


9 1.2349 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.2277 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


2.0 x 1.2
mm [2]


Micro Crystal


EPSON


FC-12M 32.768000kHz
90 1.3 12.5 2.9062 F0, F3
12.5


FC-12D 32.768000kHz
7


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.7737
U3, U5


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


**ESR**
**max**
**(kΩ)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
5 0.6447
U3, U5


7 1.0513 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


9 1.6190 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.9062 F0, F3


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
5 0.4704
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.7878
U3, U5


9 1.1866 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.0804 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.7228
U3, U5


2.0 x 1.2
mm [2]


RIVER TFX-03 90 1.3


RIVER TFX-03C 60 1.8


NX2012SA 32.768 kHz
EXS00A-MU00527


NX2012SA 32.768 kHz C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,

80 1.3 7 0.9344

EXS00A-MU00524 U3, U5


NX2012SA 32.768 kHz
12.5 2.5833 C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
EXS00A-MU00528


C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.5026
U3, U5


NDK


NX2012SE 32.768 kHz
EXS00A-MU01260


NX2012SE 32.768 kHz C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.6416
EXS00A-MU01259 U3, U5

50 [(4)] 1.7

NX2012SE 32.768 kHz C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
9 0.9706
EXS00A-MU01611 U3, U5


NX2012SE 32.768 kHz
12.5 1.7095 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
EXS00A-MU01612


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


**ESR**
**max**
**(kΩ)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


SC-20T 75 1


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.6231
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.8138
U3, U5


9 1.2717 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.3177 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


SII


2.0 x 1.2
mm [2]


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.6325
U3, U5
SC-20S 70 1.3

12.5 2.2604 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.6325
U3, U5


CITIZEN CM2012H 70 1.3


830106545501


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.8176
U3, U5


9 1.2592 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.2604 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.9047
U3, U5


Würth
Elektronik


90 1,7

830105946101 7 1.155 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


830050789 12.5 3.077 F0, F3


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.9751
U3, U5


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


ABS07L-32.768kHz
7pF


**ESR**
**max**
**(kΩ)**


ABS07L-32.768kHz 80 1.4
9 1.6472 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
9pF


ABS07L-32.768kHz 12.5 2.6208 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ABS07-32.768kHz 6pF


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.5815
U3, U5


ABRACON


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ABS07-32.768kHz 7pF 7 0.7596
U3, U5


ABS07-32.768kHz 9pF 70 1.1 9 1.1869 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ABS07 32.768kHz 12.5 2.1631 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ABS07-166- C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.7596
32.768kHz-T U3, U5


ABS07-120- C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
60 1.2 6 0.5273
32.768kHz-T U3, U5


ABS07-LR-32.768 kHz- C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
50 1.3 6 0.4517
6 U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.5733
U3, U5


3.2 x 1.5
mm [2]


CITIZEN CM315D 70 0,95


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.7501
U3, U5


9 1.1751 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.1471 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


**ESR**
**max**
**(kΩ)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
4 0.2678
U3, U5


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.5407
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
8 0.9087
U3, U5


9 1.1283 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 2.0838 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.4517
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.5840
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
9 0.8994
U3, U5


12.5 1.6145 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.5815
U3, U5


3.2 x 1.5
mm [2]


CITIZEN CM315E 0,70 0,75


CITIZEN CM315DL 50 1,3


830054236


Würth
Elektronik


C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
830009709 7 0.7596

70 1 U3, U5


830009706 9 1.1869 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


830009678 12.5 2.1631 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


**ESR**
**max**
**(kΩ)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.6152
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.7980
U3, U5


C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
9 1.2349
U5


12.5 2.2277 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F2, F3, F4, L0, L1, L4, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
6 0.5571
U5


7 0.7178 C0, F0, F1, F3, F4_g2, L0, L4, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


9 1.1004 C0, F0, F3, F4_g2, L0, L4, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


12.5 1.9656 C0, F0, F3, L0, L4, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F2, F3, F4, L0, L1,L4, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
6 0.4517
U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.5840
U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
9 0.8994
U3, U5


12.5 1.6145 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
7 0.7596
U3, U5


CC7V-T1A
70 1,2
CM7V-T1A (low profile)


CM7V-T1A 0.3 60 1,4


CM7V-T1A 50 1,3


FC-135 32.768000 kHz
7


FC-135 32.768000 kHz

1.0 9 1.1869 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


FC-135 32.768000 kHz

70 12.5 2.1631 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5

12.5


3.2 x 1.5
mm [2]


Micro Crystal


EPSON


FC-13A 32.768000 kHz
9
0.9


9 1.1633 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


FC-13A 32.768000 kHz
12.5 2.1312 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
12.5


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


C0, F0, F1, F3, F4_g2, L0, L1, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2,
7 0.5562
U0, U3, U5


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


FC-135R 32.768000
kHz 7


**ESR**
**max**
**(kΩ)**


FC-135R 32.768000 C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,

50 1.1 9 0.8648

kHz 9 U3, U5


FC-135R 32.768000
12.5 1.5681 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
kHz 12.5


SC-32S 70


1.0


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0,5815
U3, U5


12.5 2.1631 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0,4154
U3, U5
SC-32P 50


ECS-.327-6-34QS-TR


12.5 1.5451 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.5983
U3, U5


3.2 x 1.5
mm [2]


EPSON


SII


ECS


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-7-34QS-TR 7 0.7787
U3, U5

1,1

ECS-.327-9-34QS-TR 9 1.2108 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ECS-.327-12.5-34QS12.5 2.1953 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
TR


ECS-.327-6-34G-TR


0,75


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.5407
U3, U5


ECS-.327-12.5-34G12.5 2.0838 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
TR 70



ECS-.327-6-34S-TR


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.5899
U3, U5


ECS-.327-12.5-34S12.5 2.1792 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
TR


ECX-.327-CDX-1293 12.5 2.1792 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5

1,05

C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-7-34B-TR 7 0.7691
U3, U5


ECS-.327-9-34B-TR 9 1.1988 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ECS-.327-12.5-34B-TR 12.5 2.1792 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-CDX-1128 60 2 6 0.6511
U3, U5


**Table 7. Recommended crystal / MEMS resonators for the LSE oscillator in STM32 products (continued)**


**C0** **CL** **gmcrit(1)** **STM32 series compatibility** **[(2)(3)]**
**(pF)** **(pF)** **(µA/V)**


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.4517
U3, U5


**Package** **Quartz reference**
**Manufacturer**
**size** **Part number**


ECS ECS-.327-6-34R-TR


**ESR**
**max**
**(kΩ)**


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-7-34R-TR 7 0.5840
U3, U5

C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-9-34R-TR 9 0.8994
U3, U5


ECS-.327-12.5-34R-TR 1,3 12.5 1.6145 C0, F0, F3, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5


ECS-.327-6-34RR-TR


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
6 0.3614
U3, U5


3.2 x 1.5
mm [2]


C0, F0, F1, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,
ECS-.327-9-34RR-TR 40 9 0.7195
U3, U5


ECS-.327-12.5-34RR12.5 1.2916 C0, F0, F3, F4_g2, L0, L4, L4+,L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
TR


NX3215SA 32.768 kHz
EXS00A-MU00525


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2,
6 0.5815
U0, U3, U5


NDK


NX3215SA 32.768 kHz C0, F0, F1, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0,

70 1.0 7 0.7596

EXS00A-MU00523 U3, U5


NX3215SA 32.768 kHz
12.5 2.1631 C0, F0, F3, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3, U5
EXS00A-MU00526


NX3215SE 32.768 KHz
EXS00A-MU00990
40 1.3


C0, F0, F1, F2, F3, F4, L0, L1, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2,
6 0.3323
U0, U3, U5


NX3215SE 32.768 KHz C0, F0, F3, F4_g2, L0, L4, L4+, L5, G0, G4, F7, C5, H5, G5, H7P, H7, N6, WB, WB0, WBA, WL, MP1, MP2, U0, U3,
12.5 1.2361
EXS00A-MU00989 U5


1. As defined in _Section 3.4: Oscillator transconductance_ .


2. F4_g1: STM32F4 series with LSE generation 1, corresponds to STM32F401/405/ 407/415/417/427/429/437/439xx MCUs featuring LSE oscillators with non-modifiable transconductance.


3. F4_g2: STM32F4 series with LSE generation 2, corresponds to STM32F410/411/412/413/423/446/469/479xx MCUs, featuring LSE oscillators with statically-modifiable transconductance.


4. Low_ESR: -40 to +85 °C.


_Note:_ _STM32U575/585 rev. X devices do not support crystal/MEMS resonators with CL ≤ 6 pF._


**AN2867** **Recommended crystals for STM8AF/AL/S MCUs**

### **6 Recommended crystals for STM8AF/AL/S MCUs**

##### **6.1 Part numbers of recommended crystal oscillators**


**Table 8. KYOCERA compatible crystals (not exhaustive list)**


**Part number** **Frequency** **ESR max** **CL** **Drive level (DL)**


CX3225GA8000D0PTVCC
8 MHz 500 Ω

CX3225SA8000D0PTVCC 200 µW max


CX2016SA16000D0GSSCC


200 Ω


CX2016GR16000D0GTVCC 300 Ω 300 µW max

8 pF


CX2016GR16000D0GTVCC 300 Ω 300 µW max

8 pF

CX3225CA16000D0PSVCC

16 MHz 100 Ω 200 µW max

CX3225GA16000D0PTVCC


CX3225SB16000D0GSSCC 80 Ω 100 µW max


CX3225CA16000D0PSVCC

16 MHz 100 Ω 200 µW max

CX3225GA16000D0PTVCC


CX3225SA16000D0PTVCC 60 Ω 200 µW max


_Note:_ _Contact provider regarding recommended crystals for new designs._


**Table 9. NDK compatible crystals (not exhaustive list)**


**Part number** **Frequency** **ESR max** **CL** **Drive level (DL)**


NX3225GD 8MHz
8 MHz 500 Ω
EXS00A-CG04874


NX3225GA 16MHz
EXS00A-CG04815
16 MHz


80 Ω


8 pF


NX2016SA 16MHz
200 Ω
EXS00A-CS07826


NX3225GA 24MHz
EXS00A-CG04818
24 MHz


50 Ω 8 pF


NX2016SA 24MHz
80 Ω 6 pF
EXS00A-CS10820


200 µW max


NX3225GA 25MHz
EXS00A-CG06750
25 MHz


50 Ω 8 pF


NX2016SA 25MHz
80 Ω 6 pF
EXS00A-CS11321


NX2016SA32MHz
32 MHz 80 Ω 6 pF
EXS00A-CS10925


NX1612SA 40MHz
40 MHz
EXS00A-CS13836


80 Ω


6 pF


80 Ω 100 µW max

NX1612SA 48MHz
48 MHz 7 pF
EXS00A-CS13734


AN2867 Rev 25 43/60



**Recommended crystals for STM8AF/AL/S MCUs** **AN2867**

##### **6.2 Recommended ceramic resonators**

_Table 10_ and _Table 11_ give the references of recommended CERALOCK [®] ceramic
resonators for the STM8A microcontrollers provided and certified by muRata.


**Table 10. Recommended conditions (for consumer)**


**Part number** **Frequency** **CL**


CSTCR4M00G55-R0 4 MHz CL1 = CL2 = 39 pF

CSTNE8M00G550000R0 8 MHz CL1 = CL2 = 33 pF

CSTNE16M0V530000R0 16 MHz CL1 = CL2 = 15 pF


**Table 11. Recommended conditions (for CAN-BUS)**


**Part number** **Frequency** **CL**


CSTCR4M00G55B-R0 4 MHz CL1 = CL2 = 39 pF

CSTNE8M00G55A000R0 8 MHz CL1 = CL2 = 33 pF

CSTNE16M0V53C000R0 16 MHz CL1 = CL2 = 15 pF


44/60 AN2867 Rev 25


**AN2867** **Tips for improving oscillator stability**

### **7 Tips for improving oscillator stability**

##### **7.1 PCB design guidelines**


Keeping the signal-to-noise ratio (SNR) below acceptable limits for a perfect operation of the
oscillator means more severe constraints on the oscillator PCB design to reduce its
sensitivity to noise.


Therefore, great care must be taken when designing the PCB to reduce as much as
possible the SNR. A non exhaustive list of precautions to take when designing the oscillator
PCB is provided below:

- Avoid high values of stray capacitance and inductances, as they can lead to
uncontrollable oscillation (the oscillator can resonate at overtones or harmonic
frequencies). Reducing the stray capacitance also decreases startup time and
improves oscillation frequency stability.

- To reduce high frequency noise propagation across the board, the MCU/MPU must
have a stable power supply source, to ensure noiseless crystal oscillations. This means
that well-sized decoupling capacitor must be used for powering the device.

- Mount the crystal as close as possible to the MCU/MPU, to keep tracks short, and to
reduce inductive and capacitive effects. A guard ring around these connections,
connected to the ground, is essential to avoid capturing unwanted noise, which can
affect oscillation stability.

Long tracks/paths behave as antennas for a given frequency spectrum, generating
oscillation issues when passing EMI certification tests. Refer to _Figure 14_ and
_Figure 16_ .

- Any path conveying high-frequency signals must be routed away from the oscillator
paths and components. Refer to _Figure 14_ .

- The oscillator PCB must be underlined with a dedicated underneath ground plane,
distinct from the application PCB ground plane. The oscillator ground plane should be
connected to the nearest MCU/MPU ground. It prevents interferences between the
oscillator components and other application components (for example, crosstalk
between paths). If a crystal in a metallic package is used, do not connect it to the
oscillator ground. Refer to _Figure 13_, _Figure 14_, and _Figure 15_ .

- Leakage current can increase startup time and even prevent the oscillator start. If the
device operates in a severe environment (high moisture/humidity ratio), an external
coating is recommended.


AN2867 Rev 25 45/60



**Tips for improving oscillator stability** **AN2867**


**Figure 13. Recommended layout for an oscillator circuit**


VSS paths


C L1
Ground shield


Microcontroller


OSC_IN

Quartz


OSC_OUT


R Ex t(1)
C L2


Local ground plane (other layer)


ai15839b


**Warning:** **It is highly recommended to apply conformal coatings to the**
**PCB area shown in** _**Figure 13**_ **, especially for the LSE quartz,**
**CL1, CL2, and paths to the OSC_IN and OSC_OUT pads as a**
**protection against moisture, dust, humidity, and temperature**
**extremes that may lead to startup problems.**


46/60 AN2867 Rev 25


**AN2867** **Tips for improving oscillator stability**

##### **7.2 PCB design examples**


**Example 1**


**Figure 14. PCB with separated GND plane and guard ring around the oscillator**


**e**


**e**
**e**


**Figure 15. GND plane** **Figure 16. Signals around the oscillator**


**e**


**e**


AN2867 Rev 25 47/60



**Tips for improving oscillator stability** **AN2867**


**Example 2**


_Figure 17_ is an example of a PCB that does not respect the guidelines provided in
_Section 7.1_, for the following reasons:

- no ground planes around the oscillator component

- too long paths

- no symmetry between oscillator capacitances

- high crosstalk / coupling between paths

- too many test points.


**Figure 17. Preliminary design (PCB design guidelines not respected)**


48/60 AN2867 Rev 25


**AN2867** **Tips for improving oscillator stability**


The PCB design has been improved according to the guidelines (see _Figure 18_ ):

- guard ring connected to the GND plane around the oscillator

- symmetry between oscillator capacitances

- less test points

- no coupling between paths.


**Figure 18. Final design (following guidelines)**


**e**


**Figure 19. GND plane** **Figure 20. Top layer view**


AN2867 Rev 25 49/60



**Tips for improving oscillator stability** **AN2867**


**Example 3**


_Figure 21_ is another example of PCB that does not respect the guidelines provided in
_Section 7.1_ (EMC tests likely to fail):

- no guard ring around oscillator components

- long paths.


**Figure 21. PCB guidelines not respected**


**e**


50/60 AN2867 Rev 25


**AN2867** **Tips for improving oscillator stability**


The layout has been improved to respect the guidelines (see _Figure 22_ ), EMC tests are
likely to be passed:

- ground planes around the oscillator component

- short paths that link the STM32 to the oscillator

- symmetry between oscillator capacitances.


**Figure 22. PCB guidelines respected**


**e**


**e**

##### **7.3 Soldering guidelines**


In general, soldering is a sensitive process, especially for low-frequency crystals. To reduce
the impact of such process on the crystal parameters user should consider that

- Exposing crystals to temperatures above their maximum ratings can damage the
crystal and affect their ESR value. Refer to the crystal datasheet for the right reflow
temperature curve (if not provided, ask the manufacturer).

- PCB cleaning is recommended to obtain the maximum performance by removing flux
residuals from the board after assembly (even when using “no-clean” products in
ultra-low power applications).

##### **7.4 LSE sensitivity to PC13 activity**


The OSC32_IN is sensitive to PC 13 activity, When PC13 is active (toggling) the LSE clock
may shift, depending upon the LSE drive configuration. For example, using PC_13 as
RTC_OUT calibration for 512 Hz or 1 Hz can disturb the LSE oscillation loop, hence shift the
calibration frequency.


AN2867 Rev 25 51/60



**Tips for improving oscillator stability** **AN2867**


On products having the possibility to remap RTC_OUT on another pin (for example PB2), it
is recommended to use this remapping to avoid LSE disturbances.


52/60 AN2867 Rev 25


**AN2867** **Reference documents**

### **8 Reference documents**


[1] E. Vittoz _High-Performance Crystal Oscillator Circuits: Theory and Application_
IEEE Journal of solid State Circuits, Vol 23, No 3, June 1988 pp 774 - 783.


AN2867 Rev 25 53/60



**FAQs** **AN2867**

### **9 FAQs**


**Question**


How can I know if my crystal is compatible with a given STM32 part?


**Answer**


Refer to _Section 4: Guidelines to select a suitable crystal and external components_ .


**Question**


Can I use a 32.768 kHz crystal compatible with STM32 parts but not mentioned in _Table 7_ ?


**Answer**


Yes, you can. _Table 7_ is not exhaustive, it is given as a reference for some selected crystal
manufacturers, footprint size, and crystal load capacitance.


**Question**


In my application, 32.768 kHz frequency very-low drift and high accuracy are mandatory to
obtain an accurate clock without calibration. Which crystal load capacitance (CL) should I
choose?


**Answer**


First, you must be sure that your crystal is compatible with the selected STM32 LSE. Then,
it is highly recommended to use a crystal with low pullability, that is with CL ≥ 6 pF:

- 7 pF is a good compromise between low drift and moderate power consumption

- 9 and 12.5 pF can be used in noisy environments, but impact the power consumption.


54/60 AN2867 Rev 25


**AN2867** **Conclusion**

### **10 Conclusion**


The most important parameter is the gain margin of the oscillator, which determines if the
oscillator starts up or not. This parameter must be calculated at the beginning of the design
phase, to choose a crystal suitable for the application. The second parameter is the value of
the external load capacitors, to select in accordance with the CL specification of the crystal
(provided by the manufacturer). This determines the frequency accuracy. The third
parameter is the value of the external resistor used to limit the drive level. In the 32 kHz
oscillator part, however, it is not recommended to use an external resistor.


Because of the number of variables involved, in the experimentation phase it is
recommended to select components that have exactly the same properties as those that will
be used in production, and operate with the same oscillator layout and in the same
environment, to avoid unexpected behavior.


Recently, MEMS oscillators have emerged on the market. They are a good alternative to
resonators-based oscillators, thanks to their reduced power consumption, small size (they
do not require additional passive components such as external load capacitors), and cost.
This kind of oscillator is compatible with all STM32 MCUs/MPUs, except for the STM32F1
and STM32L1 series. When a MEMS oscillator is paired with an STM32 embedded
oscillator, configure the latter in bypass mode.


AN2867 Rev 25 55/60



**Revision history** **AN2867**

### **11 Revision history**


**Table 12. Document revision history**


**Date** **Revision** **Changes**


20-Jan-2009 1 Initial release.


10-Nov-2009 2


DL formula corrected in _Section 3.5.2: Another drive level measurement_
_method_ .
Package column added to all tables in _Section 6: Some recommended_
_crystals for STM32 microcontrollers_ .
Recommended part numbers updated in _Section 5.1: STM32-compatible_
_high-speed resonators_ .


Added _Section 7: Some recommended crystals for STM8A/S_
27-Apr-2010 3
_microcontrollers_ .


25-Nov-2010 4


30-Mar-2011 5


Updated _Section 5.1: STM32-compatible high-speed resonators_ :
removed _Table 7: Recommendable condition (for consumer)_ and
_Table 8: Recommendable condition (for CAN bus)_ ; added _Table 8:_
_Recommendable conditions (for consumer)_ ; updated Murata resonator
link.
Updated _Section 5.1: STM32-compatible high-speed resonators_ :
removed _Table 13: EPSON TOYOCOM_, _Table 14: JFVNY_ _[®]_, and
_Table 15: KDS_ ; Added _Table 6: Recommendable crystals_ .
Added _Warning:_ after _Figure 13_ .


_Section 5.1: STM32-compatible high-speed resonators_ : updated
“STM32” with “STM8”.
_Table 16: Recommendable conditions (for consumer)_ : replaced ceramic
resonator part number “CSTSE16M0G55A-R0” by
“CSTCE16M0V53-R0”.


17-Jul-2012 6 Whole document restricted to STM32 devices.


19-Sep-2014 7


19-Dec-2014 8


Changed STM32F1 into STM32 throughout the document.
Added STM8AL series in _Table 1: Applicable products_ .
Replace STM8 by STM32 in _Section :_ and updated hyperlink.
Added _Section 7: Tips for improving oscillator stability_ .
Remove section _Some PCB hints_ .


Updated _Section 2: Oscillator theory_ .
Updated _Section 3: Pierce oscillator design_ . Renamed section “Gain
margin of the oscillator” into _Section 3.4: Oscillator transconductance_
and content updated. Updated _Section 3.6: Startup time_ . Updated
_Section 3.7: Crystal pullability_ .
Updated _Section 4: Guidelines to select a suitable crystal and external_
_components_ .
Updated _Section 5: Recommended resonators for STM32 MCUs/MPUs_ .
Added _Section 8: Reference documents_ .
Updated _Section 10: Conclusion_ .


56/60 AN2867 Rev 25


**AN2867** **Revision history**


**Table 12. Document revision history (continued)**


**Date** **Revision** **Changes**


19-Feb-2015 9


17-Aug-2015 10


31-May-2017 11


21-Jan-2020 12


Updated _Section 2.3: Negative-resistance oscillator principles_ to specify
the ratio between negative resistance and crystal ESR for STM8 and
STM32 microcontrollers.
Added _Section 3.8: Safety factor_ .
Added _Check the Safety Factor of the oscillation loop_ step in _Section 4.2:_
_How to select an STM32-compatible crystal_ . Note moved from step 2 to
3 and updated.
Renamed _Table 7: Recommended crystal / MEMS resonators for the_
_LSE oscillator in STM32 products_ .


Updated _Figure 12: Classification of low-speed crystal resonators_ .
Added caution notes in _Section 4.1: Low-speed oscillators embedded in_
_STM32 MCUs/MPUs_ .
Added STM32F7, STM32F446xx, STM32F469/479xx and STM32L4
microcontrollers in _Table 5: LSE oscillators embedded into STM32_
_MCUs/MPUs_ .
Added STM32F411xx, STM32F446xx, STM32F469/479xx and
STM32L4xx microcontrollers in _Table 6: HSE oscillators embedded in_
_STM32 MCUs/MPUs_ .
Updated _Table 7: Recommended crystal / MEMS resonators for the LSE_
_oscillator in STM32 products_ .
Added _Section 9: FAQs_ .


Updated document title, _Introduction_, _Section 9: FAQs_, _Section 10:_
_Conclusion_, title of _Section 6: Recommended crystals for STM8AF/AL/S_
_MCUs_, and revision of text across the whole document.
Updated _Table 5: LSE oscillators embedded into STM32 MCUs/MPUs_,
_Table 6: HSE oscillators embedded in STM32 MCUs/MPUs_ and _Table 7:_
_Recommended crystal / MEMS resonators for the LSE oscillator in_
_STM32 products_ .
Updated caption of _Table 8: KYOCERA compatible crystals (not_
_exhaustive list)_, and added _Table 9: NDK compatible crystals (not_
_exhaustive list)_ .
Updated _Figure 12: Classification of low-speed crystal resonators_ .


Updated document title, _Section 2: Oscillator theory_, _Section 5.1:_
_STM32-compatible high-speed resonators_ and _Section 5.2: STM32-_
_compatible low-speed resonators_ .
Updated _Table 1: Applicable products_, _Table 5: LSE oscillators_
_embedded into STM32 MCUs/MPUs_, _Table 6: HSE oscillators_
_embedded in STM32 MCUs/MPUs_, _Table 7: Recommended crystal /_
_MEMS resonators for the LSE oscillator in STM32 products_, _Table 8:_
_KYOCERA compatible crystals (not exhaustive list)_, _Table 9: NDK_
_compatible crystals (not exhaustive list)_, _Table 10: Recommended_
_conditions (for consumer)_ and _Table 11: Recommended conditions (for_
_CAN-BUS)_ .
Minor text edits across the whole document.


AN2867 Rev 25 57/60



**Revision history** **AN2867**


**Table 12. Document revision history (continued)**


**Date** **Revision** **Changes**


04-Dec-2020 13


27-Jul-2021 14


05-Oct-2021 15


22-Aug-2022 16


19-Jan-2023 17


25-Jan-2023 18


03-Apr-2023 19


Updated _Table 7: Recommended crystal / MEMS resonators for the LSE_
_oscillator in STM32 products_ and its footnotes _2_ and _3_ .
Updated footnotes of _Table 5: LSE oscillators embedded into STM32_
_MCUs/MPUs_ .
Added _Section 7.4: LSE sensitivity to PC13 activity_ .
Minor text edits across the whole document.


Updated _Section 2.2: Transconductance_, _Section 3.4: Oscillator_
_transconductance_, _Section 4.2: How to select an STM32-compatible_
_crystal_ and _Section 5.1: STM32-compatible high-speed resonators_
Added _Section 3.9: Oscillation modes_ and its subsections.
Updated _Table 7: Recommended crystal / MEMS resonators for the LSE_
_oscillator in STM32 products_ .
Minor text edits across the whole document.


Added notes in _Section 3.5.2: Another drive level measurement method_,
_Section 5.2: STM32-compatible low-speed resonators_ and _Section 6.1:_
_Part numbers of recommended crystal oscillators_ .
Added footnote _4_ to _Table 5: LSE oscillators embedded into STM32_
_MCUs/MPUs_ .
Updated _Table 6: HSE oscillators embedded in STM32 MCUs/MPUs_,
_Table 7: Recommended crystal / MEMS resonators for the LSE oscillator_
_in STM32 products_ and _Table 9: NDK compatible crystals (not_
_exhaustive list)_ .
Minor text edits across the whole document.


Updated _Table 1: Applicable products_, _Table 5: LSE oscillators_
_embedded into STM32 MCUs/MPUs_, _Table 7: Recommended crystal /_
_MEMS resonators for the LSE oscillator in STM32 products_, and _Table 9:_
_NDK compatible crystals (not exhaustive list)_ .
Updated _Section 6.1: Part numbers of recommended crystal oscillators_ .
Minor text edits across the whole document.


Updated _Table 5: LSE oscillators embedded into STM32 MCUs/MPUs_,
_Table 6: HSE oscillators embedded in STM32 MCUs/MPUs_, and _Table 7:_
_Recommended crystal / MEMS resonators for the LSE oscillator in_
_STM32 products_ .
Minor text edits across the whole document.


Updated _Table 5: LSE oscillators embedded into STM32 MCUs/MPUs_,
_Table 6: HSE oscillators embedded in STM32 MCUs/MPUs_, and _Table 7:_
_Recommended crystal / MEMS resonators for the LSE oscillator in_
_STM32 products_ .
Minor text edits across the whole document.


Updated _Table 5: LSE oscillators embedded into STM32 MCUs/MPUs_
and _Table 7: Recommended crystal / MEMS resonators for the LSE_
_oscillator in STM32 products_ .
Updated _Note:_ in _Section 5.2: STM32-compatible low-speed resonators_ .


58/60 AN2867 Rev 25


**AN2867** **Revision history**


**Table 12. Document revision history (continued)**


**Date** **Revision** **Changes**


21-Mar-2024 20


14-May-2024 21


12-Nov-2024 22


28-Jan-2025 23


Updated document title.
Updated _Table 5: LSE oscillators embedded into STM32 MCUs/MPUs_,
_Table 6: HSE oscillators embedded in STM32 MCUs/MPUs_, and _Table 7:_
_Recommended crystal / MEMS resonators for the LSE oscillator in_
_STM32 products_ .
Updated footnote _a_ .
Updated _Section 7.1: PCB design guidelines_ .
Minor text edits across the whole document.


Updated _Section 5.1: STM32-compatible high-speed resonators_ and
footnote _a_ .
Updated _Table 5: LSE oscillators embedded into STM32 MCUs/MPUs_
and _Table 7: Recommended crystal / MEMS resonators for the LSE_
_oscillator in STM32 products_ .
Updated _Figure 10: Quartz crystal theoretical model with third overtone._
Minor text edits across the whole document.


Updated _Section 3.5.3: Calculating the external resistor_ .
Updated _Table 5: LSE oscillators embedded into STM32 MCUs/MPUs_,
_Table 6: HSE oscillators embedded in STM32 MCUs/MPUs_, and _Table 7:_
_Recommended crystal / MEMS resonators for the LSE oscillator in_
_STM32 products_ .


Introduced STM32U3 series, hence updated _Table 5: LSE oscillators_
_embedded into STM32 MCUs/MPUs_, _Table 6: HSE oscillators_
_embedded in STM32 MCUs/MPUs_, and _Table 7: Recommended crystal /_
_MEMS resonators for the LSE oscillator in STM32 products_ .


02-Feb-2026 24 Introduced STM32C5 series.


13-Oct-2026 25


Introduced STM32G5 series.
Introduced STM32H7P series.
Updated _Table 7: Recommended crystal / MEMS resonators for the LSE_
_oscillator in STM32 products_


AN2867 Rev 25 59/60



**AN2867**


**IMPORTANT NOTICE – READ CAREFULLY**


STMicroelectronics NV and its subsidiaries (“ST”) reserve the right to make changes, corrections, enhancements, modifications, and
improvements to ST products and/or to this document at any time without notice.


In the event of any conflict between the provisions of this document and the provisions of any contractual arrangement in force between the
purchasers and ST, the provisions of such contractual arrangement shall prevail.


The purchasers should obtain the latest relevant information on ST products before placing orders. ST products are sold pursuant to ST’s
terms and conditions of sale in place at the time of order acknowledgment.


The purchasers are solely responsible for the choice, selection, and use of ST products and ST assumes no liability for application
assistance or the design of the purchasers’ products.


No license, express or implied, to any intellectual property right is granted by ST herein.


Resale of ST products with provisions different from the information set forth herein shall void any warranty granted by ST for such product.


If the purchasers identify an ST product that meets their functional and performance requirements but that is not designated for the
purchasers' market segment, the purchasers shall contact ST for more information.


ST and the ST logo are trademarks of ST. For additional information about ST trademarks, refer to www.st.com/trademarks. All other product
or service names are the property of their respective owners.


Information in this document supersedes and replaces information previously supplied in any prior versions of this document.


© 2026 STMicroelectronics – All rights reserved


60/60 AN2867 Rev 25
