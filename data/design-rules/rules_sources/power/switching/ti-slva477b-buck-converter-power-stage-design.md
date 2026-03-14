---
source: "TI SLVA477B -- Buck Converter Power Stage Design"
url: "https://www.ti.com/lit/an/slva477b/slva477b.pdf"
format: "PDF 8pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 13238
---

Application Report

Basic Calculation of a Buck Converter's Power Stage
Brigitte Hauke ....................................................................................... Low Power DC/DC Applications
ABSTRACT
This application report gives the formulas to calculate the power stage of a buck converter built with an
integrated circuit having a integrated switch and operating in continuous conduction mode. It is not
intended to give details on the functionality of a buck converter or how to compensate a converter. For
additional information, see the references at the end of this document.
Appendix A contains the formulas without description.
1 Basic Configuration of a Buck Converter
Figure 1 shows the basic configuration of a buck converter where the switch is integrated in the selected
integrated circuit ( IC). Some converters have the diode replaced by a second switch integrated into the
converter (synchronous converters). If this is the case, all equations in this document apply besides the
power dissipation equation of the diode.
I SW L I
IN OUT
V
IN V
C IN D C OUT OUT
Figure 1. Buck Converter Power Stage
1.1 Necessary Parameters of the Power Stage
The following four parameters are needed to calculate the power stage:
1. Input voltage range: V and V
IN(min) IN(max)
2. Nominal output voltage: V
OUT
3. Maximum output current: I
OUT(max)
4. Integrated circuit used to build the buck converter. This is necessary because some parameters for the
calculations must be derived from the data sheet.
If these parameters are known, the power stage can be calculated.
2 Calculate the Maximum Switch Current
The first step to calculate the switch current is to determine the duty cycle, D, for the maximum input
voltage. The maximum input voltage is used because this leads to the maximum switch current.
Maximum Duty Cycle: D =
V ´ η
IN(max) (1)
V = maximum input voltage
IN(max)
V = output voltage

η = efficiency of the converter, e.g., estimated 90%
The efficiency is added to the duty cycle calculation, because the converter also has to deliver the energy
dissipated. This calculation gives a more realistic duty cycle than just the formula without the efficiency
factor.
Use either an estimated factor, e.g., 90% (which is not unrealistic for a buck converter worst-case
efficiency), or see the Typical Characteristics section of the data sheet of the selected converter.
The next step in calculating the maximum switch current is to determine the inductor ripple current. In the
converter's data sheet; normally, a specific inductor or a range of inductors are named for use with the IC.
So, use the recommended inductor value to calculate the ripple current, an inductor value in the middle of
the recommended range, or if none is given in the data sheet, the one calculated in the Inductor Selection
section of this application report.
( )
V - V ´ D
IN(max) OUT
Inductor Ripple Current: ΔI =
L
f ´ L
S (2)
V = desired output voltage
D = duty cycle calculated in Equation 1
f = minimum switching frequency of the converter
S
L = selected inductor value
It now has to be determined if the selected IC can deliver the maximum output current.
ΔI
Maximum output current of the selected IC: I = I - L
MAXOUT LIM(min)
2 (3)
I = minimum value of the current limit of the integrated switch (given in the data sheet)
LIM(min)
ΔI = inductor ripple current calculated in Equation 2
If the calculated value for the maximum output current of the selected IC, I , is below the system's
MAXOUT
required maximum output current, the switching frequency has to be increased to reduce the ripple current
or another IC with a higher switch current limit has to be used.
Only if the calculated value for I is just a little smaller than the needed one, it is possible to use the
MAXOUT
selected IC with an inductor with higher inductance if it is still in the recommended range. A higher
inductance reduces the ripple current and therefore increases the maximum output current with the
selected IC.
If the calculated value is above the maximum output current of the application, the maximum switch
current in the system is calculated:
Application specific maximum switch current: I = L + I
SW(max) OUT(max)
2 (4)
ΔI = inductor ripple current calculated in Equation 2
I = maximum output current necessary in the application
This is the peak current, the inductor, the integrated switch(es), and the external diode have to withstand.
3 Inductor Selection
Data sheets often give a range of recommended inductor values. If this is the case, choose an inductor
from this range. The higher the inductor value, the higher is the maximum output current because of the
reduced ripple current.
In general, the lower the inductor value, the smaller is the solution size. Note that the inductor must
always have a higher current rating than the maximum current given in Equation 4; this is because the
current increases with decreasing inductance.
For parts where no inductor range is given, the following equation is a good estimation for the right
inductor:
V OUT × (V IN - V OUT )
L =
ΔI L ´ fS ´ V IN (5)

V = typical input voltage
IN
ΔI = estimated inductor ripple current, see the following:
The inductor ripple current cannot be calculated with Equation 1 because the inductor is not known. A
good estimation for the inductor ripple current is 20% to 40% of the output current.
ΔI = (0.2 to 0.4) ´ I
L OUT(max) (6)
ΔI = estimated inductor ripple current
4 Rectifier Diode Selection
To reduce losses, use Schottky diodes. The forward current rating needed is equal to the maximum output
current:
I = I ´(1 - D)
F OUT(max) (7)
I = average forward current of the rectifier diode
F
Schottky diodes have a much higher peak current rating than average rating. Therefore the higher peak
current in the system is not a problem.
The other parameter that has to be checked is the power dissipation of the diode. It has to handle:
P = I ´ V
D F F (8)
I = average forward current of the receiver diode
V = forward voltage of the rectified diode
5 Output Voltage Setting
Almost all converters set the output voltage with a resistive divider network (which is integrated if they are
fixed output voltage converters).
With the given feedback voltage, V , and feedback bias current, I , the voltage divider can be calculated.
FB FB
I
R1/2
R
1
I
FB
R
2
Figure 2. Resistive Divider for Setting the Output Voltage
The current through the resistive divider needs to be at least 100 times as big as the feedback bias
current:
I ³ 100 ´ I
R1/2 FB (9)
I = current through the resistive divider to GND
I = feedback bias current from data sheet

This adds less than 1% inaccuracy to the voltage measurement and for the calculation of the feedback
divider, the current into the feedback pin can be neglected. The current also can be a lot higher. The only
disadvantage of smaller resistor values is a higher power loss in the resistive divider, but the accuracy is
increased a little.
With the preceding assumption, the resistors are calculated as follows:
R = FB
2 I
R1/2 (10)
æ V ö
R 1 = R 2 ´ ç V OUT -1÷
è FB ø (11)
R ,R = resistive divider, see Figure 2.
1 2
V = feedback voltage from the data sheet
I = current through the resistive divider to GND, calculated in Equation 9
6 Input Capacitor Selection
The minimum value for the input capacitor is normally given in the data sheet. This minimum value is
necessary to stabilize the input voltage due to the peak current requirement of a switching power supply.
The best practice is to use low-equivalent series resistance (ESR) ceramic capacitors. The dielectric
material must be X5R or better. Otherwise, the capacitor loses much of its capacitance due to dc bias or
temperature.
The value can be increased if the input voltage is noisy.
7 Output Capacitor Selection
The best practice is to use low-ESR capacitors to minimize the ripple on the output voltage. Ceramic
capacitors are a good choice if the dielectric material is X5R or better.
If the converter has external compensation, any capacitor value above the recommended minimum in the
data sheet can be used, but the compensation has to be adjusted for the used output capacitance.
With internally compensated converters, the recommended inductor and capacitor values must be used,
or the recommendations in the data sheet for adjusting the output capacitors to the application in the data
sheet must be followed for the ratio of L × C.
With external compensation, the following equations can be used to adjust the output capacitor values for
a desired output voltage ripple:
C = L
OUT(min) 8 ´ f × ΔV
S OUT (12)
C = minimum output capacitance
OUT(min)
ΔV = desired output voltage ripple
The ESR of the output capacitor adds some more ripple, given with the equation:
ΔV = ESR ´ ΔI
OUT(ESR) L (13)
ΔV = additional output voltage ripple due to capacitors ESR
OUT(ESR)
ESR = equivalent series resistance of the used output capacitor
ΔI = inductor ripple current from Equation 2 or Equation 6
Often the selection of the output capacitor is not driven by the steady-state ripple, but by the output
transient response. The output voltage deviation is caused by the time it takes the inductor to catch up
with the increased or reduced output current needs.
The following formula can be used to calculate the necessary output capacitance for a desired maximum
overshoot:

ΔI 2 ´ L
C = OUT
OUT(min),OS 2 ´ V ´ V
OUT OS (14)
C = minimum output capacitance for a desired overshoot
OUT(min),OS
ΔI = maximum output current change in the application
V = desired output voltage change due to the overshoot
OS
8 References
1. Understanding Buck Power Stages in Switchmode Power Supplies (SLVA057)
2. Examples of Applications with the Pulse Width Modulator TL5001 (SLVAE05)
3. Understanding Output Voltage Limitations of DC/DC Buck Converters (SLYT293)
4. Designing Ultrafast Loop Response With Type-III Compensation for Current Mode Step-Down
Converters (SLVA352)
5. Robert W. Erickson: Fundamentals of Power Electronics, Kluwer Academic Publishers, 1997
6. Mohan/Underland/Robbins: Power Electronics, John Wiley & Sons Inc., Second Edition, 1995
7. George M. Harayda, Akira Omi, and Axel Yamamoto: Improve Your Designs with Large Capacitance
Value Multi-Layer Ceramic Chip ( MLCC ) Capacitors, Panasonic
8. Jeffrey Cain, Ph.D.: Comparison of Multilayer Ceramic and Tantalum Capacitors, AVX Corporation

Appendix A

Formulas to Calculate the Power State of a Buck
Converter
V ´ η
Maximum Duty Cycle: D = OUT
IN(max) (15)
V = output voltage
η = efficiency of the converter, e.g., estimated 85%
( )
V - V ´ D
IN(max) OUT
Inductor Ripple Current: ΔI =
f ´ L
S (16)
D = duty cycle calculated in Equation 15
L = selected inductor value
Maximum output current of the selected IC: I = I - L
MAXOUT LIM(min)
2 (17)
I = minimum value of the current limit of the integrated switch (given in the data sheet)
LIM(min)
ΔI = inductor ripple current calculated in Equation 16
Application specific maximum switch current: I = L + I
SW(max) OUT(max)
2 (18)
ΔI = inductor ripple current calculated in Equation 16
V ´ (V - V )
Inductor Calculation: L= OUT IN OUT (if no value is recommended in the data sheet)
ΔI ´ f ´ V
L S IN (19)
V = typical input voltage
IN
ΔI = estimated inductor ripple current, see next paragraph
Inductor Ripple Current Estimation: ΔI =(0.2 to 0.4) ´ I
L OUT(max) (20)
Average Forward Current of Rectifier Diode: I = I ´ (1- D)
F OUT(max) (21)
Power Dissipation in Rectifier Diode: P = I ´ V
D F F (22)
I = average forward current of the rectifier diode
V = forward voltage of the rectifier diode
Current through Resistive Divider Network for Output Voltage Setting: I ³ 100 ´ I
R1/2 FB (23)

I = feedback bias current from data sheet
Value of Resistor Between FB Pin and GND: R = FB
2 I
R1/2 (24)
æ V ö
Value of Resistor Between FB Pin and V OUT : R 1 = R 2 ´ ç V OUT -1÷
è FB ø (25)
V = feedback voltage from the data sheet
I = current through the resistive divider to GND, calculated in Equation 23
Minimum Output Capacitance, if not given in Data Sheet: C = L
OUT(min) 8 ´ f × ΔV
S OUT (26)
ΔV = desired output voltage ripple
Additional Output Voltage Ripple due to ESR: ΔV = ESR ´ ΔI
OUT(ESR) L (27)
ESR = equivalent series resistance of the used output capacitor
I = maximum output current of the application
ΔI = inductor ripple current from Equation 16 or Equation 20
ΔI 2 ´ L
Output Voltage Overshoot due to Load Transient: C = OUT
OUT(min),OS 2 × V ´ V
OUT OS (28)
ΔI = maximum output current change in the application
out
V = desired output voltage change due to the overshoot
OS
Revision History
Changes from A Revision (August 2012) to B Revision ................................................................................................ Page
• Changed equation 1 and supporting text in Calculate the Maximum Switch Current section................................... 1
NOTE: Page numbers for previous revisions may differ from page numbers in the current version.
