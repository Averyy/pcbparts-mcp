---
source: "TI SLVA372C -- Boost Converter Power Stage Design"
url: "https://www.ti.com/lit/an/slva372c/slva372c.pdf"
format: "PDF 10pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 15071
---

Application Note
Basic Calculation of a Boost Converter's Power Stage
Brigitte Hauke Low Power DC/DC Application
ABSTRACT
This application note gives the equations to calculate the power stage of a boost converter built with an IC
with integrated switch and operating in continuous conduction mode. It is not intended to give details on the
functionality of a boost converter (see Reference 1) or how to compensate a converter. See the references at the
end of this document if more detail is needed.
For the equations without description, See section 8.
Table of Contents
1 Basic Configuration of a Boost Converter...........................................................................................................................2
1.1 Necessary Parameters of the Power Stage.......................................................................................................................2
2 Calculate the Maximum Switch Current...............................................................................................................................2
3 Inductor Selection...................................................................................................................................................................4
4 Rectifier Diode Selection........................................................................................................................................................4
5 Output Voltage Setting...........................................................................................................................................................5
6 Input Capacitor Selection.......................................................................................................................................................6
7 Output Capacitor Selection....................................................................................................................................................6
8 Equations to Calculate the Power Stage of a Boost Converter..........................................................................................7
9 References..............................................................................................................................................................................9
10 Revision History...................................................................................................................................................................9

1 Basic Configuration of a Boost Converter
Figure 1-1 shows the basic configuration of a boost converter where the switch is integrated in the used IC.
Often lower power converters have the diode replaced by a second switch integrated into the converter. If this is
the case, all equations in this document apply besides the power dissipation equation of the diode.
I L D I
IN OUT
V
IN V
C IN SW C OUT OUT
Figure 1-1. Boost Converter Power Stage
1.1 Necessary Parameters of the Power Stage
The following four parameters are needed to calculate the power stage:
1. Input Voltage Range: V and V
IN(min) IN(max)
2. Nominal Output Voltage: V
OUT
3. Maximum Output Current: I
OUT(max)
4. Integrated Circuit used to build the boost converter. This is necessary, because some parameters for the
calculations have to be taken out of the data sheet.
If these parameters are known the calculation of the power stage can take place.
2 Calculate the Maximum Switch Current
The first step to calculate the switch current is to determine the duty cycle, D, for the minimum input voltage. The
minimum input voltage is used because this leads to the maximum switch current.
V ´ η
D=1 - IN(min)
OUT (1)
V = minimum input voltage
IN(min)
V = desired output voltage
η = efficiency of the converter, e.g. estimated 80%
The efficiency is added to the duty cycle calculation, because the converter has to deliver also the energy
dissipated. This calculation gives a more realistic duty cycle than just the equation without the efficiency factor.
Either an estimated factor, e.g. 80% (which is not unrealistic for a boost converter worst case efficiency), can be
used or see the Typical Characteristics section of the selected converter's data sheet
(Reference 3 and 4).
The next step to calculate the maximum switch current is to determine the inductor ripple current. In the
converters data sheet normally a specific inductor or a range of inductors is named to use with the IC. So
either use the recommended inductor value to calculate the ripple current, an inductor value in the middle of the
recommended range or, if none is given in the data sheet, the one calculated in the Inductor Selection section of
this application note.
V ´ D
ΔI =
L f ´ L
S (2)
D = duty cycle calculated in Equation 1
f = minimum switching frequency of the converter
S
L = selected inductor value
2 Basic Calculation of a Boost Converter's Power Stage SLVA372D – NOVEMBER 2009 – REVISED NOVEMBER 2022

Now it has to be determined if the selected IC can deliver the maximum output current.
æ ΔI ö
I
MAXOUT
= çI
LIM(min)
- L ÷´(1-D)
è 2 ø
(3)
I = minimum value of the current limit of the integrated switch (given in the data sheet)
ΔI = inductor ripple current calculated in Equation 2
L
If the calculated value for the maximum output current of the selected IC, I , is below the systems required
maximum output current, another IC with a higher switch current limit has to be used.
Only if the calculate value for I is just a little smaller than the needed one, it is possible to use the
selected IC with an inductor with higher inductance if it is still in the recommended range. A higher inductance
reduces the ripple current and therefore increases the maximum output current with the selected IC.
If the calculated value is above the maximum output current of the application, the maximum switch current in
the system is calculated:
ΔI I
I = L + OUT(max)
SW(max) 2 1-D (4)
ΔI = inductor ripple current calculated in Equation 2
I = maximum output current necessary in the application
This is the peak current, the inductor, the integrated switch(es) and the external diode has to withstand.

3 Inductor Selection
Often data sheets give a range of recommended inductor values. If this is the case, it is recommended to choose
an inductor from this range. The higher the inductor value, the higher is the maximum output current because of
the reduced ripple current.
The lower the inductor value, the smaller is the solution size. Note that the inductor must always have a higher
current rating than the maximum current given in Equation 4 because the current increases with decreasing
inductance.
For parts where no inductor range is given, the following equation is a good estimation for the right inductor:
L = V IN × (V OUT - V IN )
ΔI L ´ f S ´ V OUT (5)
V = typical input voltage
IN
ΔI = estimated inductor ripple current, see below
The inductor ripple current cannot be calculated with Equation 1 because the inductor is not known. A good
estimation for the inductor ripple current is 20% to 40% of the output current.
ΔI =(0.2to0.4) ´ I ´ OUT
L OUT(max)
IN (6)
ΔI = estimated inductor ripple current
4 Rectifier Diode Selection
To reduce losses, Schottky diodes should be used. The forward current rating needed is equal to the maximum
output current:
I = I
F OUT(max) (7)
I = average forward current of the rectifier diode
F
Schottky diodes have a much higher peak current rating than average rating. Therefore the higher peak current
in the system is not a problem.
The other parameter that has to be checked is the power dissipation of the diode. It has to handle:
P = I ´ V
D F F (8)
V = forward voltage of the rectifier diode
4 Basic Calculation of a Boost Converter's Power Stage SLVA372D – NOVEMBER 2009 – REVISED NOVEMBER 2022

5 Output Voltage Setting
Almost all converters set the output voltage with a resistive divider network (which is integrated if they are fixed
output voltage converters).
With the given feedback voltage, V , and feedback bias current, I , the voltage divider can be calculated.
FB FB
R1/2
R
1
FB
R
2
Figure 5-1. Resistive Divider for Setting the Output Voltage
The current through the resistive divider shall be at least 100 times as big as the feedback bias current:
I ³ 100 ´ I
R1/2 FB (9)
I = current through the resistive divider to GND
I = feedback bias current from data sheet
This adds less than 1% inaccuracy to the voltage measurement. The current can also be a lot higher. The only
disadvantage of smaller resistor values is a higher power loss in the resistive divider, but the accuracy will be a
little increased.
With the above assumption, the resistors are calculated as follows:
R = FB
2 I
R1/2 (10)
æV ö
R 1 =R 2 ´ ç V OUT -1÷
è FB ø (11)
R ,R = resistive divider, see Figure 5-1.
1 2
V = feedback voltage from the data sheet
I = current through the resistive divider to GND, calculated in Equation 9

6 Input Capacitor Selection
The minimum value for the input capacitor is normally given in the data sheet. This minimum value is necessary
to stabilize the input voltage due to the peak current requirement of a switching power supply. the best practice
is to use low equivalent series resistance (ESR) ceramic capacitors. The dielectric material should be X5R
or better. Otherwise, the capacitor cane lose much of its capacitance due to DC bias or temperature (see
references 7 and 8).
The value can be increased if the input voltage is noisy.
7 Output Capacitor Selection
Best practice is to use low ESR capacitors to minimize the ripple on the output voltage. Ceramic capacitors are a
good choice if the dielectric material is X5R or better (see reference 7 and 8).
If the converter has external compensation, any capacitor value above the recommended minimum in the data
sheet can be used, but the compensation has to be adjusted for the used output capacitance.
With internally compensated converters, the recommended inductor and capacitor values should be used or the
recommendations in the data sheet for adjusting the output capacitors to the application should be followed for
the ratio of L × C.
With external compensation, the following equations can be used to adjust the output capacitor values for a
desired output voltage ripple:
I ´ D
C =
OUT(min) f ´ ΔV
S OUT (12)
C = minimum output capacitance
OUT(min)
I = maximum output current of the application
D = duty cycle calculated with Equation 1
ΔV = desired output voltage ripple
The ESR of the output capacitor adds some more ripple, given with the equation:
æI ΔI ö
ΔV =ESR ´ ç OUT(max) + L ÷
OUT(ESR) è 1-D 2 ø
(13)
ΔV = additional output voltage ripple due to capacitors ESR
OUT(ESR)
ESR = equivalent series resistance of the used output capacitor
D = duty cycle calculated with Equation 1
ΔI = inductor ripple current from Equation 2 or Equation 6
6 Basic Calculation of a Boost Converter's Power Stage SLVA372D – NOVEMBER 2009 – REVISED NOVEMBER 2022

8 Equations to Calculate the Power Stage of a Boost Converter
V ´ η
Maximum DutyCycle:D=1 - IN(min)
OUT (14)
η = efficiency of the converter, e.g. estimated 85%
V ´ D
Inductor Ripple Current:ΔI =
L f ´ L
S (15)
D = duty cycle calculated in Equation 14
L = selected inductor value
æ ΔI ö
Maximum output current of the selected IC: I
= çI
- L ÷´(1-D)
è 2 ø
(16)
I = minimum value of the current limit of the integrated witch (given in the data sheet)
ΔI = inductor ripple current calculated in Equation 15
ΔI I
Application specificmaximum switch current:I = L + OUT(max)
SW(max) 2 1-D (17)
ΔI = inductor ripple current calculated in Equation 15
V × (V - V )
InductorCalculation:L= IN OUT IN
ΔI ´ f ´ V
L S OUT (18)
V = typical input voltage
IN
ΔI = estimated inductor ripple current, see Equation 19
InductorRippleCurrentEstimation:ΔI =(0.2to0.4) ´ I ´ OUT
L OUT(max)
IN (19)
ΔI = estimated inductor ripple current
AverageForwardCurrentofRectifierDiode:I =I
F OUT(max) (20)
PowerDissipationinRectifierDiode:P =I ´ V
D F F (21)
V = forward voltage of the rectifier diode

CurrentThroughResistiveDividerNewtworkforOutputVoltageSetting:I ³ 100 ´ I
R1/2 FB (22)
I = feedback bias current from data sheet
Value of Resistor Between FB Pin and GND: R = FB
2 I
R1/2 (23)
æV ö
ValueofResistorBetweenFBPinandV OUT :R 1 =R 2 ´ ç V OUT -1÷
è FB ø (24)
V = feedback voltage from the data sheet
I = current through the resistive divider to GND, calculated in Equation 22
I ´ D
Minimum OutputCapacitance,ifnotgiveninthedatasheet:C =
OUT(min) f ´ ΔV
S OUT (25)
ΔV = desired output voltage ripple
æI ΔI ö
AdditionalOutputVoltageRippleduetoESR: ΔV =ESR ´ ç OUT(max) + L ÷
OUT(ESR) è 1-D 2 ø
(26)
ESR = equivalent series resistance of the used output capacitor
ΔI = inductor ripple current from Equation 15 or Equation 19
8 Basic Calculation of a Boost Converter's Power Stage SLVA372D – NOVEMBER 2009 – REVISED NOVEMBER 2022

9 References
1. Understanding Boost Power Stages in Switchmode Power Supplies (SLVA061)
2. Voltage Mode Boost Converter Small Signal Control Loop Analysis Using the TPS61030 (SLVA274)
3. Data sheet of TPS65148 (SLVS904)
4. Data sheet of TPS65130 and TPS65131 (SLVS493)
5. Robert W. Erickson: Fundamentals of Power Electronics, Kluwer Academic Publishers, 1997
6. Mohan/Underland/Robbins: Power Electronics, John Wiley & Sons Inc., Second Edition, 1995
7. Improve Your Designs with Large Capacitance Value Multi-Layer Ceramic Chip (MLCC) Capacitors by
George M. Harayda, Akira Omi, and Axel Yamamoto, Panasonic
8. Comparison of Multilayer Ceramic and Tantalum Capacitors by Jeffrey Cain, Ph.D., AVX Corporation
Spacer
10 Revision History
Changes from Revision C (January 2014) to Revision D (November 2022) Page
• Updated the numbering format for tables, figures, and cross-references throughout the document..................1
Changes from Revision B (July 2010) to Revision C (January 2014) Page
• Changed V to V in Figure 5-1 ....................................................................................................................5
IN OUT
Changes from Revision A (April 2010) to Revision B (July 2010) Page
• Changed I x (1–D) To: I x D in Equation 12 ..............................................................................6
OUT(max) OUT(max)
• Changed I x (1–D) To: I x D in Equation 25 ..............................................................................7
OUT(max) OUT(max)
Changes from Revision * (November 2009) to Revision A (April 2010) Page
• Added V /V (Typical) to Equation 6 ............................................................................................................4
OUT IN
• added V /V (Typical) to Equation 19 ...........................................................................................................7
OUT IN