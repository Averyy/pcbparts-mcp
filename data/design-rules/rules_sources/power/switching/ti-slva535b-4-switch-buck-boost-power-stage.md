---
source: "TI SLVA535B -- 4-Switch Buck-Boost Power Stage"
url: "https://www.ti.com/lit/an/slva535b/slva535b.pdf"
format: "PDF 13pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 18790
---

Application Report

Basic Calculations of a 4 Switch Buck-Boost Power Stage
Hagedorn, Julian
ABSTRACT
This application note gives the equations to calculate the power stage of a non-inverting buck-boost
converter built with an IC with integrated switches and operating in continuous conduction mode. See the
references at the end of this document if more detail is needed.
For a design example without description, see appendix A.
Contents
1 Basic Configuration of a Buck-Boost Converter ......................................................................... 2
2 Duty Cycle Calculation ...................................................................................................... 2
3 Inductor Selection............................................................................................................ 2
4 Calculating Maximum Switch Current..................................................................................... 3
5 Output Voltage Setting ...................................................................................................... 5
6 Input Capacitor Selection ................................................................................................... 5
7 Output Capacitor Selection................................................................................................. 6
8 References ................................................................................................................... 7
Appendix A Design Example Using TPS63802 ............................................................................... 8
Appendix B Formulas to Calculate the Power Stage of a 4-Switch Buck-Boost Converter............................ 10
List of Figures
1 Buck-Boost Converter Schematic ......................................................................................... 2
2 Feedback Circuit ............................................................................................................. 5
List of Tables
1 ................................................................................................................................ 11

1 Basic Configuration of a Buck-Boost Converter
Figure 1, shows the basic configuration of a buck-boost converter where the switches are integrated in the
IC. Many of the Advanced Low Power buck-boost converters (TPS63xxx) have all four switches integrated
in the IC. This reduces solution size and eases the difficultly of the design.
SW 1 SW 2
IIN L IOUT
VIN
VOUT
CIN
SW 3 SW 4
COUT
Figure 1. Buck-Boost Converter Schematic
1.1 Necessary Parameters of the Power Stage
The following four parameters are needed to calculate the power stage:
1. Input voltage range: V and V
IN min IN max
2. Nominal output voltage: V
OUT
3. Maximum output current: I
4. Integrated circuit used to build the buck-boost converter. This is necessary because some parameters
for the calculations must be derived from the data sheet.
If these parameters are known, the power stage can be calculated.
2 Duty Cycle Calculation
The first step after selecting the operating parameters of the converter is to calculate the minimum duty
cycle for buck mode and maximum duty cycle for boost mode. These duty cycles are important because at
these duty cycles the converter is operating at the extremes of its operating range. The duty cycle is
always positive and less than 1.
V
D OUT
Buck V u K
INmax (1)
V u K
D 1 (cid:16) INmax
Boost V
where
• V = maximum input voltage
IN max
• V = minimum input voltage
IN min
• V = desired output voltage
• D = minimum duty cycle for buck mode
Buck
• D = maximum duty cycle for boost mode
Boost
• η = estimated efficiency at calculated V , V , and I (2)
IN OUT OUT
3 Inductor Selection
Data sheets often give a range of recommended inductor values. If this is the case, choose an inductor
from this range. The higher the inductor value, the higher is the possible maximum output current because
of the reduced ripple current.
Normally, the lower the inductor value, the smaller is the solution size. Note that the inductor must always
have a higher current rating than the largest value of current given from Equation 5 and Equation 8; this is
because the peak current increases with decreasing inductance.

For device datasheets where no inductor range is given, an inductor that satisfies both buck and boost
mode conditions must be chosen. Follow both Section 3.1 and Section 3.2 to find the right inductance.
Select the largest value of inductance calculated from either Equation 3 and Equation 4.
3.1 Buck Mode
For buck mode the following equation is a good estimate for the right inductance:
V u (cid:11)V (cid:16) V (cid:12)
L ! OUT INmax OUT
K u F u V u I
ind SW INmax OUT
• I = desired maximum output current
• F = switching frequency of the converter
SW
• K = estimated coefficient that represents the amount of inductor ripple current relative to the
ind
maximum output current. (3)
A good estimation for the inductor ripple current is 20% to 40% of the output current, or 0.2 < K < 0.4.
3.2 Boost Mode
For boost mode the following equation is a good estimate for the right inductance:
V 2 u (cid:11)V (cid:16) V (cid:12)
L ! INmin OUT INmin
F u K u I u V 2
SW ind OUT OUT
maximum output current. (4)
A good estimation for the inductor ripple current is 20% to 40% of the output current, or 0.2 < K < 0.4.
4 Calculating Maximum Switch Current
To calculate the maximum switch current the duty cycle must be derived as done in Section 2 of this
application note. There are two operating cases to consider for these calculations: buck and boost mode.
Derive the maximum switch current for both cases. Use the greater of the two switch currents for
remainder of this application note.
4.1 Buck Mode
In buck mode, the maximum switch current is when the input voltage is at its maximum. Using Equation 5
and Equation 6, the maximum switch current can be calculated.
'I
I max (cid:14) I
SWmax 2 OUT
(5)
(cid:11)V (cid:16) V (cid:12) u D
'I INmax OUT Buck
max F u L

• I = desired output current
• ΔI = maximum ripple current through the inductor
max
• I = maximum switch current
SW max
• L = selected inductor value (6)
To obtain the switching frequency, refer to the datasheet for the given converter.
Before continuing, verify that the converter can deliver the maximum current using Equation 7. I must
max out
be greater than I .
out
'I
I I (cid:16) max
maxout LIM 2
• I = maximum deliverable current through inductor by the converter
• I = switch current limit, specified in converter datasheet
LIM
• ΔI = Ripple current through the inductor calculated in equation 6. (7)
4.2 Boost Mode
In boost mode, the maximum switch current is when the input voltage is at its minimum. Using Equation 8
and Equation 9, the maximum switch current can be calculated.
'I I
I max (cid:14) OUT
SWmax 2 1 (cid:16) D
Boost (8)
V u D
'I INmin Boost
max F u L
• I = desired output current
• ΔI = maximum ripple current through the inductor
• I = maximum switch current
SW max
• L = selected inductor value (9)
To obtain the switching frequency, refer to the datasheet for the given converter.
Before continuing, verify that the converter can deliver the maximum current using Equation 10. I
must be greater than I . I is specified as the maximum output current required be the application.
out max out max
§ 'I ·
I ¨ I (cid:16) max ¸ u (cid:11)1(cid:16) D (cid:12)
maxout ¨ LIM 2 ¸ Boost
© ¹
• I = maximum deliverable current through inductor by the converter
• I = switch current limit, specified in converter datasheet
• ΔI = Ripple current through the inductor calculated in Equation 9. (10)

5 Output Voltage Setting
Most converters set the output voltage with a resistive divider network. This is integrated if the converter is
a fixed output voltage converter. In this case, the external voltage divider described in this section is not
used.
With the given feedback voltage, V , and feedback bias current, I , the voltage divider can be calculated.
FB FB
VOUT
IR1/2
R1
IFB
VFB
R2
GND
Figure 2. Feedback Circuit
The current through the resistive divider must be at least 100 times the size of the feedback bias current.
SLYT469 is also available for a detailed discussion on resistive feedback divider design.
I t 100 u I
R1 2 FB
• I = current through the resistive divider to GND
R1/2
• I = feedback bias current from data sheet (11)
FB
This adds less than 1% inaccuracy to the voltage measurement. For the calculation of the feedback
divider, the current into the feedback pin can be neglected. The disadvantage of using smaller resistor
values than computed from Equation 12 and Equation 13 is a higher power loss in the resistive divider
and thus lower efficiency at light loads, but the accuracy does increase. Again, for a more detailed
discussion on this subject matter see the SLYT469.
Neglecting the current into the FB pin, the resistors are calculated as followed:
V
R2 FB
I
R1 2 (12)
§ V ·
R1 R2 u ¨ OUT (cid:16) 1¸
¨ V ¸
© FB ¹
• R1,R2 = resistive divider values, see Figure 2.
• V = feedback voltage from the datasheet
• I = current through the resistive divider to GND, calculated in Equation 11
• V = desired output voltage (13)
6 Input Capacitor Selection
The minimum value for the input capacitor is normally given in the datasheet. This minimum value is
necessary to stabilize the input voltage due to the peak current requirement of a switching power supply.
The best practice is to use low-equivalent series resistance (ESR) ceramic capacitors. The dielectric
material must be X5R or better. Otherwise, the capacitor loses much of its capacitance due to dc bias or
temperature.
The value can be increased if the input voltage is noisy.

7 Output Capacitor Selection
The best practice is to use low-ESR capacitors to minimize the ripple on the output voltage. Ceramic
capacitors are a good choice if the dielectric material is X5R or better.
If the converter has external compensation, any capacitor value above the recommended minimum in the
datasheet can be used, but the compensation has to be adjusted for the used output capacitance.
With internally compensated converters, the recommended inductor and capacitor values must be used,
or the recommendations in the datasheet for adjusting the output capacitors to the application must be
followed. This usually involves keeping the same ratio of L × C as the recommended values.
With external compensation, a solution that satisfies both buck and boost mode must be chosen. Follow
both Section 7.1 and Section 7.2 to develop minimum output capacitance for both buck and boost mode
operations. Select output capacitance that is larger than both minimum required output capacitance for
buck and boost mode operation. Always account for DC bias capacitance drop and derate the capacitance
of the output capacitors for the design calculations.
7.1 Buck Mode
For buck mode, and Equation 16 are used to calculate the minimum output capacitor value for a desired
output voltage ripple. For the minimum output capacitance use the maximum value from and Equation 16.
K u I
C ind OUT
OUTmin1 8 u F u V
SW OUTripple
• C = minimum output capacitance required
OUT min1
• V = desired output voltage ripple
OUTripple
maximum output current. (14)
The ESR of the output capacitor adds some more ripple, which can be calculated with Equation 15:
'V ESR u K u I
OUTesr ind OUT
• ΔV = additional output voltage ripple due to capacitors ESR
OUTesr
• ESR = equivalent series resistance of the used output capacitor (15)
Often the selection of the output capacitor is not driven by the steady-state ripple, but by the output
transient response. The output voltage deviation is caused by the time it takes the inductor to catch up
with the increased or reduced output current needs.
The following formula can be used to calculate the necessary output capacitance for a desired maximum
overshoot caused by the removal of the load current.
(cid:11) K uI (cid:12)2 uL
C ind OUT
OUTmin2 2 u V u 'V
OUT OUT
• C = minimum output capacitance required for a desired overshoot
OUT min2
maximum output current
• ΔV = desired output voltage change due to the overshoot (16)

7.2 Boost Mode
With external compensation, the following equations can be used to adjust the output capacitor values for
a desired output voltage ripple:
I u D
C OUT Boost
OUTmin F u 'V
SW OUT
• C = minimum output capacitance
OUT min
• I = maximum output current of the application
• D = duty cycle calculated with Equation 7
• ΔV = desired output voltage ripple (17)
The ESR of the output capacitor adds some more ripple, given with the Equation 18. Be sure to account
for this V ESR ripple.
§ I K uI u V ·
'V ESR u ¨ OUT (cid:14) ind OUT OUT ¸
OUTesr ¨1 (cid:16) D 2 u V ¸
© Boost IN ¹
• ΔV = additional output voltage ripple due to capacitors ESR
• ESR = equivalent series resistance of the used output capacitor
• I = maximum output current of the application
out
• D = duty cycle calculated with Equation 7
• K = estimated coefficient that represents the amount of inductor ripple current relative to the (18)
8 References
• Basic Calculation of a Boost Converter's Power Stage (SLVA372B)
• Basic Calculation of a Buck Converter's Power Stage (SLVA477)

Appendix A
Design Example Using TPS63802
A.1 System Requirements
V = 3.3 V
I = 2 A
V = 2.6 V
V = 5.0 V
Efficiency (V = 3.3 V @ V = 5.0 V ) = 93%
OUT IN N
Efficiency (V = 3.3 V @ V = 2.6 V) = 85%
OUT IN
A.2 Duty Cycle
For buck mode duty cycle use Equation 1, D = 0.614. For boost mode duty cycle use Equation 2, D
Buck Boost
= 0.330.
A.3 Inductor Selection
Using Equation 3: Using Equation 4:
• L = 0.881 µH, (assuming K =0.3) • L = 0.341 µH, (assuming K =0.3)
ind ind
Inductor Selected: 1.0 µH
A.4 Maximum Switch Current
Using Equation 5 through Equation 7: Using Equation 8 through Equation 10:
• D = 0.614 • D = 0.330
• ΔI = 492 mA • ΔI = 405 mA
max max
• I = 2.24 A • I = 3.19 A
SW max SW max
• I = 4.25 A which is greater than 2 A • I = 2.88 A which is greater than 2 A
max out max out
A.5 Output Voltage Setting
Using Equation 11 and assuming I = 0.01 µA, I minimum is found to be 1 µA. By assuming 5 µA for
FB R1/2
I , 100 kΩ is calculated from Equation 12 for R2. 91 kΩ is chosen for R2 as per datasheet
recommendation. Equation 13 then yields 509 kΩ for R1 which, 511 kΩ is chosen for R1. The typical
output voltage with these values of resistors is 3.308 V.
A.6 Input Capacitor Selection
A single 10 µF, 6.3 V, X5R ceramic capacitors are chosen for the design.

A.7 Output Capacitor Selection
Using Equation 14, Equation 16, and Equation 17, the minimum capacitance required is calculated by
taking the maximum of these values. Equation 14, Equation 16, and Equation 17 yield 0.71 µF, 0.55 µF,
and 3.11 µF. The maximum was the result from Equation 17, 3.11 µF. A single 22 µF, 6.3 V, X5R, +/-
20% ceramic capacitor, (MuRata, GRM188R60J226MEA0), was chosen for the output capacitance. This
capacitor is commonly chosen in low power DC/DC applications by Texas Instruments due to its
enhanced DC-bias performance. By using the manufacture’s provided information, the derated value of
the output capacitor is 8.2 µF which is sufficient for the minimum output capacitance calculated in
Equation 17.

Appendix B
Formulas to Calculate the Power Stage of a 4-Switch
Buck-Boost Converter
B.1 Formula Summary

Table 1.
Buck Boost Parameter
Duty Cycle Calculation
V V u K • V = minimum input voltage
D OUT D 1 (cid:16) INmax IN min
Buck V u K Boost V • V OUT = desired output voltage
INmax (19) OUT (20) • D = minimum duty cycle for buck mode
• η = estimated efficiency at calculated V , V , and I
IN OUT OUT
Inductor Selection
V u (cid:11)V (cid:16) V (cid:12) V 2 u (cid:11)V (cid:16) V (cid:12) IN min
L ! OUT INmax OUT L ! INmin OUT INmin • V OUT = desired output voltage
K u F u V u I F u K u I u V 2 • I OUT = desired maximum output current
ind SW INmax OUT (21) SW ind OUT OUT (22) • F SW = switching frequency of the converter
• K = estimated coefficient that represents the amount of
inductor ripple current relative to the maximum output
current.
Calculating Maximum Switch Current
'I 'I I where
I max (cid:14) I I max (cid:14) OUT • V = maximum input voltage
SWmax 2 OUT SWmax 2 1 (cid:16) D IN max
(23) Boost (24) • V IN min = minimum input voltage
(cid:11)V (cid:16) V (cid:12) u D V u D • I OUT = desired output current
'I max INmax F O u UT L Buck 'I max IN F m S in W u L Boost (26) • • Δ I O I U m T ax = = m m ax a i x m im um um rip s p w le itc c h u c rr u e r n re t n th t rough the inductor
SW (25) SW max
'I § 'I · SW
I I (cid:16) max I ¨ I (cid:16) max ¸ u (cid:11)1(cid:16) D (cid:12) • L = selected inductor value
maxout LIM 2 (27) maxout ¨ © LIM 2 ¸ ¹ Boost (28) • I b m y ax th ou e t = co m n a ve xi r m te u r m deliverable current through inductor
• I = switch current limit, specified in converter
datasheet

Table 1. (continued)
Buck Boost Parameter
Output Voltage Setting
I t 100 u I
R1 2 FB (29) where
V • I = current through the resistive divider to GND
R2 FB • I = feedback bias current from data sheet
I FB
• R1,R2 = resistive divider values, see Figure 2.
R1 2 (30)
• V = feedback voltage from the datasheet
§ V · • I = current through the resistive divider to GND,
R1 R2 u ¨ OUT (cid:16) 1¸ calculated in Equation 11
¨ V ¸ • V = desired output voltage
© FB ¹ (31) OUT
Output Capacitor Selection
K u I I u D where
C ind OUT C OUT Boost • C = minimum output capacitance
OUTmin1 8 u F u V OUTmin F u 'V OUT min
SW OUTripple (32) SW OUT (33) • C OUT min1 = minimum output capacitance required
• C = minimum output capacitance required for a
OUT min2
§ I K uI u V · desired overshoot
'V OUTesr ESR u K ind u I OUT (34) 'V OUTesr ESR u ¨ ¨ © 1 (cid:16) O D U B T oost (cid:14) ind 2 O u U V T IN OUT ¸ ¸ ¹ • • I D OUT = = m d a u x t i y m c u y m cle ou c t a p l u c t u c la u t r e r d en w t i o th f t E h q e u a a p ti p o l n ica 7 tion
(35) • F = switching frequency of the converter
• ΔV = desired output voltage ripple
• V = desired output voltage ripple
OUTripple
(cid:11) K uI (cid:12)2 uL • K
= estimated coefficient that represents the amount of
C ind OUT inductor ripple current relative to the maximum output
OUTmin2 2 u V u 'V current.
OUT OUT (36) • ΔV = additional output voltage ripple due to
capacitors ESR
• ESR = equivalent series resistance of the used output
capacitor