---
source: "TI SLVA485 -- Pull-up/Pull-down Resistor for Open Drain Outputs"
url: "https://www.ti.com/lit/an/slva485/slva485.pdf"
format: "PDF 9pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 19778
---

Application Report

Choosing an Appropriate Pull-up/Pull-down Resistor for
Open Drain Outputs
Ben Hopf ............................................ PMP-DC/DC Low-Power Converters
ABSTRACT
Many ICs contain digital output pins to indicate certain statuses to the rest of the system. These outputs
fall into two categories: open drain (open collector for bipolar outputs) or push-pull (also known as totem
pole). Open drain outputs are commonly utilized because they offer several advantages when compared
to push-pull outputs. Unlike push-pull outputs, several open drain outputs from different devices can be
connected directly together to create an OR function. Also, open drain outputs provide more flexibility to a
designer as they can be pulled-up to any voltage found in the system, which can be useful when they
serve as inputs to a processor which might require a lower voltage level than the push-pull output would
give. Examples of open drain outputs commonly found on ICs include Power Good (PG) and Low Battery
(LBO) on switching regulators, reset and Power Fail (PFO) on supply voltage supervisors (SVS), and Low
Battery, Power Fail, and reset on power management units. All open drain outputs require the use of an
external pull-up or pull-down resistor to keep the digital output in a defined logic state. This application
report discusses when to use a pull-up or pull-down resistor, the factors that should be considered when
selecting a pull-up or pull-down resistor, and how to calculate a valid range for the value of the resistor.
Contents
1 Introduction ......................................................... 2
2 Calculating the Pull-up Resistor Range ......................................... 2
3 Calculating the Range of R for the TPS62067 ................................... 4
Pull-up
4 Calculating the Pull-down Resistor Range ....................................... 5
5 Calculating the Range of R for the TL7759 .................................... 6
Pull-down
6 Other Selection Considerations .............................................. 7
7 Conclusion .......................................................... 8
List of Figures
1 Typical PG Output Equivalent Circuit (PG Floating High) ............................... 2
2 Typical PG Output Equivalent Circuit (PG Low) .................................... 3
3 Reset Output Equivalent Circuit (Reset Floating Low)................................. 5
4 Reset Output Equivalent Circuit (Reset High)...................................... 6
List of Tables
1 PG Output IC ........................................................ 4
2 EN Input IC ......................................................... 4
3 Reset Output IC ...................................................... 6
4 Typical Reset Input IC ................................................... 7

1 Introduction
An SVS monitors a critical voltage within a system and outputs a reset signal if that voltage drops below a
specified threshold. This reset signal is the open drain output in need of a pull-up or pull-down resistor. An
SVS can also have an open drain PFO output that asserts if some voltage in the system drops below a
specified threshold.
In a power converter, a PG output is routinely used to drive the enable input of a subsequent IC. A PG
output is low if the chip’s output voltage is below a certain percentage of its nominal value. The PG output
is then pulled high by the external pull-up resistor when the voltage has reached the specified level. Power
converters can also contain LBO outputs that are asserted if the LBI pin voltage drops below a specified
threshold.
The first thing to recognize when dealing with an open drain output is whether a pull-up or a pull-down
resistor is needed. This depends on whether the IC drives the output high or low when it wants to assert it.
For example, the TPS62067 step-down converter has a PG output that it drives low if the chip’s output
voltage is not in regulation. Therefore, PG needs a pull-up resistor that pulls the PG pin high when the
chip allows it to float, indicating that power is good. On the other hand, the TL7759 SVS has a reset
output that it drives high when it detects a supply voltage drop below a specific threshold. This reset
output needs a pull-down resistor to pull it low when that voltage is above the specified threshold.
To determine the value of the pull-up or pull-down resistor, several factors need to be taken into
consideration. These include the output pin’s leakage current, the leakage current of the input pin that the
open drain output is connected to, the voltage that the output is being pulled up to, the high or low voltage
logic level of both the output pin and the input pin that the output is connected to, and the test current
used to obtain the high or low voltage logic level. This report analyzes one open drain output and one
open collector output. The first example features the TPS62067 step down converter and demonstrates
when a pull-up resistor is needed and how to calculate a range for it. The second example uses the
TL7759 SVS and demonstrates when a pull-down resistor is needed and how to calculate a range of
values for it.
2 Calculating the Pull-up Resistor Range
Figure 1 shows typical PG output circuitry. The PG output connects to the output voltage, V , through a
out
pull-up resistor, R , and then connects to the EN input of another chip.
V
OUT
I Pull-up R Pull-up
Inside the IC
EN
I LKG PG V PG I EN
Comparator
+
Q1 (OFF)
_
Figure 1. Typical PG Output Equivalent Circuit (PG Floating High)
The circuit in Figure 1 is analyzed to find the maximum value for R , when power is good and Q1 is off.
Although Q1 is off, the datasheet specifies that there is some leakage current through it. This value is
found in the datasheet as I , the leakage current into the PG pin. This leakage current creates a voltage
LKG
drop across the pull-up resistor. Thus, the voltage on the PG pin and on the subsequent EN input is less

than V . For the calculation of the maximum value of R , the maximum value of I is used because it
out Pull-up LKG
would result in the largest voltage drop across R . Also, assuming that the PG output feeds the EN
input on another chip, there will also be a current flowing into that EN input. This value is found in the
datasheet of the subsequent part and is labeled I in Figure 1. Equation 1 shows how to calculate I
EN Pull-up
using Kirchhoff’s Law.
(1)
To calculate the maximum value of the pull-up resistor, Equation 2 sets the voltage at the PG pin, V ,
PG
equal to the subsequent chip’s EN pin’s V . V is the minimum voltage that is specified to be read as a
IH IH
logic high.
(2)
This value is a maximum because choosing a larger resistor would result in a larger voltage drop across
R which would cause V to be lower than the minimum value of V . In other words, the subsequent
Pull-up PG IH
chip would not recognize the PG voltage as being a logic high.
Figure 2 shows the same circuit as analyzed above when Q1 is on and PG is low. This indicates that the
output voltage is below regulation and power is not good.
OUT
I Pull-up R Pull-up
EN
I OL PG V PG I EN
Q1 (ON)
Figure 2. Typical PG Output Equivalent Circuit (PG Low)
When finding the minimum value for R , it is assumed that Q1 is turned on as shown in Figure 2, so
V is shorted to ground. In reality, Q1 has a resistance, R , which will drop some voltage and cause
PG DSon
the PG voltage to be above ground potential. When Q1 is on, the PG voltage must be sufficiently low to
register as a logic low to subsequent circuitry. To calculate the current in the pull-up resistor, the current
labeled I is needed. This value is found in the IC datasheet as the test current for V , the output low
OL OL
voltage level. Setting the maximum current through Q1 equal to the current used in the test condition in
the datasheet gives known performance, meaning V will not exceed its specified maximum voltage at
OL
that current. Currents up to the specified absolute maximum PG sink current can be used, but they could
yield a V higher than its specified maximum. (In the case of the TPS62067 used in the example, its V
test current and its absolute maximum PG sink current are equal, but this is not always the case.)
Equation 3 uses Kirchhoff’s Law, the IC’s test current, and the leakage current of the subsequent EN input
to calculate the current through the pull-up resistor.
(3)
The voltage across the pull-up resistor is equal to V minus V . The datasheet gives a maximum value
out PG
for V (called V and typically 0.3 V or 0.4 V), but it could be 0 V which would result in a higher current
PG OL
flowing through the pull-up resistor than if it were at the maximum specified voltage. Based on this,
Equation 4 calculates the minimum pull-up resistance.
(4)

This calculation results in a minimum value because choosing any value lower for R causes a higher
current than the test condition current to flow in Q1. If a current higher than the test condition current flows
through Q1, the voltage drop across Q1 is higher and no longer ensured. The results of Equation 4 and
Equation 2 yield a range of acceptable values for the pull-up resistor R at the output of the PG pin.
In the case where PG is low, the maximum allowed V voltage depends on whether V is greater than or
PG OL
less than V , the subsequent EN pin’s maximum low-level input voltage. If V is greater than V , then
IL OL IL
specified performance is not possible, because the maximum allowed voltage, V , is less than the
IL
ensured highest voltage on the PG pin, V . In this case, the minimum resistor value calculated in
Equation 4 should be significantly increased to maintain plenty of margin in the PG voltage in order to
achieve a sufficiently low voltage at the PG output to register as a logic low with subsequent circuitry.
Since specified performance is desired, these calculations assume that V is less than V .
OL IL
3 Calculating the Range of R for the TPS62067
Table 1 gives values from the PG output IC’s datasheet (in this case the TPS62067 [SLVS833A]), and
Table 2 gives values for the EN input from that IC’s datasheet (also a TPS62067 [SLVS833A]) that are
used to calculate a range of values for the pull-up resistor at the PG output. For this example, the
TPS62067’s PG output drives the EN input of another TPS62067 chip.
Table 1. PG Output IC
TPS62067 DATASHEET VALUES
PARAMETER VALUE
IC TPS62067
Pin Power Good (PG)
I 1 mA
I 100 nA
LKG(max)
V 0.3 V
OL(max)
Table 2. EN Input IC
TPS62067 DATASHEET VALUES
IC TPS62067
Pin Enable (EN)
V 1.0 V
IH(min)
I 1000 nA
EN(max)
V 0.4 V
IL(max)
First, use I , I , and Equation 1 to find the current through the pull-up resistor, I .
EN LKG Pull-up
(5)
Now that I has been calculated, the maximum value for R is found by using Equation 2. An output
Pull-up Pull-up
voltage, V , of 1.8 V is used as an example.
out
(6)
The next step is to find the minimum pull-up resistor value. Equation 3 is utilized to find the current
through the pull-up resistor.
(7)
With this value, Equation 4 finds the minimum value for R .
(8)

With this final calculation, the range of pull-up resistor values is
(9)
4 Calculating the Pull-down Resistor Range
Figure 3 shows an IC’s reset output connected to ground through a pull-down resistor, R . The reset
pin is then connected to the reset input of a microcontroller or microprocessor.
CC
Q1 (OFF)
I OL RESET V RESET I R uP
reset
I
PDL R
Figure 3. Reset Output Equivalent Circuit (Reset Floating Low)
The circuit in Figure 3 is analyzed to find the maximum value for R , when reset is low and Q1 is off.
Although Q1 is off, the datasheet specifies that there is some leakage current through it. This value is
found in the datasheet as I , the low-level output current for reset, and it creates a voltage drop across
the pull-down resistor. Thus, the voltage on the reset output pin and the subsequent reset input pin is
greater than zero volts. There is also current flowing out of the processor’s reset input, and this value is
found in the datasheet of the processor as the reset input leakage current, labeled I in Figure 3.
R
Equation 10 uses Kirchhoff’s Law to calculate the current through the pull-down resistor, I , when reset
PDL
is pulled down.
(10)
V is found in the datasheet for the processor as the maximum low-level input voltage at its reset pin. This
value represents the maximum voltage that results in the processor recognizing the reset signal as logic
low. Equation 11 implements Ohm’s Law to calculate the maximum value for R .
pull-down
(11)
Figure 4 shows the same circuit as analyzed in Figure 3 when Q1 is on and reset is high. This indicates
that the voltage being monitored by the supervisor is below the specified threshold, and the processor
needs to be in reset.

Q1 (ON)
I OH RESET V RESET I R uP
reset
I
PDH R
Figure 4. Reset Output Equivalent Circuit (Reset High)
Using Figure 4 to find the minimum value for R , it is assumed that Q1 is turned on so that V is
Pull-down RESET
shorted to V . In reality, Q1 has a saturation voltage that will cause V to be lower than V . V
CC RESET CC RESET
must be high enough to be read as a logic high by the connected circuitry’s input. The IC datasheet gives
a value for the reset high-level output voltage, V , at some test current I . This gives known
OH OH
performance, meaning V will not fall below its specified minimum. Currents up to the specified absolute
OH
maximum I can be used, but they could yield a V lower than its specified minimum. Equation 12 uses
OH OH
Kirchhoff’s Law, the IC’s test current, and the leakage current of the subsequent reset input to calculate
the current through the pull-down resistor.
(12)
After calculating the value for I , Equation 13 is used to find the minimum pull-down resistor value.
PDH
(13)
In the case where reset is high, the minimum allowed V voltage depends on whether V is greater
RESET OH
than or less than V , the subsequent reset input pin’s minimum high-level input voltage. If V is lower
IH OH
than V , then specified performance is not possible, because the minimum required voltage, V , is greater
IH IH
than the specified lowest voltage on the reset pin, V . In this case, the minimum resistor value calculated
in Equation 13 should be significantly increased to maintain plenty of margin in the reset voltage in order
to achieve a sufficiently high voltage at the reset output to register as a logic high with the subsequent
circuitry. Since specified performance is desired, these calculations assume that V is greater than V .
OH IH
5 Calculating the Range of R for the TL7759
Table 3 gives values from the reset output IC’s datasheet (in this case the TL7759), while Table 4 gives
typical values for I and V that are found in the reset input IC’s datasheet. The values from both of these
R IL
tables are used to calculate a range of values for the pull-down resistor at the reset output.
Table 3. Reset Output IC
TL7759 DATASHEET VALUES
IC TL7759
Pin Reset (Output)
V 5 V
I 1 µA
OL(max)
I 4 V
OH(min)
I 8 mA

Table 4. Typical Reset Input IC
DATASHEET VALUES
Pin Reset (Input)
V 0.3 V
IL(max)
I 100 nA
R(max)
V 3 V
IH(min)
First, use I , I , and I as well as Equation 10 to find a value for I .
OL R PDL PDL
(14)
Now use Equation 11 to calculate the maximum value for the pull-down resistor.
(15)
The next step is to use Equation 12 to find I .
PDH
(16)
Lastly, Equation 13 is utilized to find the minimum pull-down resistor value.
(17)
This final calculation yields a range for the pull-down resistor of
(18)
6 Other Selection Considerations
The above examples are calculated using parameters from the datasheet that ensure performance, such
as the output low voltage at a certain test current. If the current sunk by the PG pin is lower than the test
condition current, then the voltage drop across the PG pin’s FET is lower and the output low voltage is
lower. If however, the current sunk by the PG pin is higher than the test condition current, then the voltage
at the PG pin could be higher than specified, leading to an unreadable logic voltage level. Therefore, the
test condition current is always used for the maximum allowed current in the above calculations because it
specifies a maximum voltage at the output pin. Currents up to the absolute maximum rating of the output
pin could be used, but then the output voltage at the PG or reset pin is no longer specified to fall in its
specified range. To approximate the output voltage at the PG pin for currents higher than the test
condition current, first the on resistance, or R , of the internal FET is calculated by using the specified
DSon
maximum PG output-low voltage, V , and its test current, I .
(19)
Then the output voltage at the PG pin is just R times the new sink current.
(20)
This voltage should remain below V in order to be read as a logic low. Alternatively, a graph of the PG or
reset voltage versus current may be shown in the datasheet. These graphs show typical performance and,
like the above R calculation, are not specified performance measures.
After establishing the range for the pull-up or pull-down resistor, there are other factors to consider when
selecting a resistor that falls within the established range. One factor that discourages using a resistor
near the low end of the range is the power consumption through the pull-up or pull-down resistor and the
drive circuitry. For example, if the minimum pull-down resistor of 500 Ω is used and the saturation voltage

of the BJT happens to be the maximum value of 1 V, the pull-down resistor drops V – 1 V across it. If
V is 5 V, the 4 V drop across R produces 8 mA of current and a resulting 32 mW power loss in the
CC Pull-down
pull-down resistor plus an additional 8 mW in the IC’s driver BJT. This total power loss, V times I ,
CC sink
might be very significant for some applications, in which case a larger pull-down resistor should be
selected.
However, there are disadvantages to selecting the largest allowed pull-up resistor. Larger resistances
create a higher impedance net which is more susceptible to picking up noise from other nearby signals on
the board that happen to couple to it. This is especially a concern for lengthy open drain outputs routed
over a long distance.
A second concern for large resistor values is from parasitic capacitance on the open drain output. This can
come from other open drain outputs OR’d together, from the downstream input pins, or from nearby traces
that create a capacitor in the board. This high capacitance creates an RC circuit that has an associated
rise time and fall time. Final circuit operation should be validated with these longer than normal rise and
fall times.
7 Conclusion
Open drain outputs found on power devices require pull-up or pull-down resistors to keep the digital output
in a defined logic state. An acceptable range of values for this resistor is calculated using circuit analysis
and some parameters from the part’s datasheet. Choosing an appropriate resistor value within this range
ensures that the output is correctly recognized by the subsequent chip’s input pin. This range of
acceptable values provides flexibility in the actual value selected, which allows, for example, the reuse of
a resistor value already in the Bill of Materials. The methods and equations presented in this application
note can be utilized to find an appropriate range of resistor values and allows the designer to select the
value that best fits the application.
