---
source: "TI SLVA360 -- Adding Hysteresis to Supply Voltage Supervisor"
url: "https://www.ti.com/lit/pdf/slva360"
format: "PDF 6pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 10553
---

Application Report

Adding Hysteresis to Supply Voltage Supervisor
Sureena Gupta .......................................... PMP - Linear Power Applications
ABSTRACT
Some applications require supply voltage hysteresis to keep a supply voltage
supervisor (SVS) from falsely resetting the system due to voltage dips and glitches.
This application report presents one solution for adding hysteresis to an SVS. The
solution schematic is given along with component selection criteria and equations, such
that readers can appropriately scale the solution to their own requirements. The
document also includes a sample design implementation along with captured
waveforms.
Contents
1 Introduction ............................................. 1
2 Design Solution ........................................... 2
3 Circuit Analysis............................................ 2
4 Design Example .......................................... 3
5 Conclusion.............................................. 5
6 Reference............................................... 5
List of Figures
1 General Schematic for a Supervisor With Increased Hysteresis............... 2
2 Simplified Sensing Schematic With RESET Pin Voltage Set to Zero ............ 2
3 Simplified Sensing Schematic With RESET Pin Voltage Pulled Up to V2 via Rp...... 3
4 Schematic of Supervisor TPS3808 With External Hysteresis Resistor............ 4
5 Output Waveform Indicating Input Voltage and RESET Pin Voltage ............ 5
1 Introduction
As the input voltage to a system dips below the minimum required voltage for operation, the supply
voltage supervisor (SVS) asserts a reset signal to turn off the system. When the system is turned off,
current flow stops, and the voltage to the SVS may rise due to the decreased IR drop. The SVS then
falsely turns the system back on. This erroneous reset lasts as long as the input voltage spikes exceed
the threshold voltage, or the voltage dips fall below the threshold voltage. This condition can be
undesirable for various applications. In order to avoid this undesirable condition due to erratic change in
input voltage caused by a discharging battery or perhaps a noisy power supply, hysteresis can be added
to the SVS circuitry. The addition of hysteresis implies that the SVS is turned off when the input voltage
falls below the threshold voltage, but it is not turned back on until the input voltage rises above another
predetermined threshold voltage. For instance, it can be equivalent to the voltage supplied by a newly
replaced battery for a battery-supplied input voltage source.
For example, the TPS3808 inherently has some internal sensing voltage hysteresis, but the amount of
hysteresis provided is not adequate to avoid the aforementioned erratic condition and needs external
components to further add the required hysteresis. This application report presents the design procedures
to be followed to add hysteresis to a SVS circuitry.

2 Design Solution
The internal hysteresis voltage of a TPS3808 is 6 mV on the sense pin (the hysteresis calculation is
shown in Section 4), and it may not be adequate to meet the customer requirements. Hence, additional
input voltage hysteresis can be added to the SVS.
The required additional input voltage hysteresis can be obtained by adding a feedback/hysteresis resistor
at the sensing voltage node as shown in the solution schematic, Figure 1.
The hysteresis resistor (Rh) helps increase the hysteresis of input voltage by increasing the threshold
voltage when the input voltage is increasing and helps decrease the threshold voltage when the input
voltage is decreasing. This phenomenon is explained with simplified circuits in the next section.
V1 V2
Rh
R1
Rp
RESET
SENSE
Vs
R2
+
- V
t Voltage Detector
or Supervisor
Figure 1. General Schematic for a Supervisor With Increased Hysteresis
Where:
V1 is the input supply voltage;
V2 is the voltage used that the output is pulled up to;
Vs is the voltage at the sense pin;
Vt is the threshold voltage or reference voltage;
Rp is used as a pullup on the RESET output;
Rh is a resistor used to increase the hysteresis.
3 Circuit Analysis
The circuit operates in two conditions. The first condition is when the supplied input voltage (V1) is
increasing, and the second condition is when the supplied input voltage is decreasing. Let the '+' sign
indicate increasing voltage case and the '–' sign indicate decreasing voltage case.
3.1 CASE 1 – Input Voltage Increasing
The supplied input voltage increases during power up and is denoted by V1+. In this case, the supervisor
begins with an active low RESET signal, so the voltage at the RESET pin is close to zero volt. For this
case, assume it is zero volt, so the entire sensing schematic simplifies as shown in Figure 2.
V1+
Vs+
R2 Rh
Figure 2. Simplified Sensing Schematic With RESET Pin Voltage Set to Zero

When Vs+ increases beyond Vt+ (internal reference or threshold voltage), the supervisor lets RESET float.
The equation for the point at which the supervisor stops driving RESET low is:
V 1+ - V s+ Vs+ Vs+
= +
R1 R2 Rh
(1)
3.2 CASE 2 –Input Supply Voltage decreasing
The supplied input voltage decreases when the battery is discharging or due to a droop in supplied
voltage and is denoted by V1–. In this case, the supervisor is not asserting an active low RESET signal,
so the voltage at the RESET pin is pulled up to V2 via Rp, and the sensing schematic simplifies as shown
in Figure 3.
V1- V2
Rp
Rh
Vs-
Figure 3. Simplified Sensing Schematic With RESET Pin Voltage Pulled Up to V2 via Rp
The equation for the trip point in this case is:
V 1- - V s- V 2 - V s - V s-
+ =
R1 Rh + Rp R2
(2)
4 Design Example
The aforementioned cases and equations can be illustrated using the TPS3808 as an example. This
device has some inherent hysteresis; the are two different threshold voltages depend on whether the
supplied input voltage is increasing or decreasing. When the input voltage is increasing, the internal
sensing threshold voltage is denoted by Vs+ and when the input voltage is decreasing, the internal
sensing threshold voltage is denoted by Vs–.
These threshold voltage values are listed in the data sheet (SBVS103). The data sheet indicates that the
internal reference voltage Vt is set to 0.4 V, and the typical hysteresis is set at 1.5% Vt. Hence, the values
can be deduced as:
Vs– = 0.4 V
Vs+ = 0.406 V
The amount of inherent hysteresis provided can be calculated as (Vs+) – (Vs–). For the TPS3808, the
inherent internal hysteresis is approximately 6 mV. The amount of hysteresis (from the battery
perspective) is (V1+) – (V1–), which is simply (Vs+) – (Vs–) gained up through the resistor divider formed
by R1 and R2. This equates to 27 mV of hysteresis on a 1.8-V battery voltage (V1–).
Assume that a system powered by two AA batteries needs to be reset when the battery voltage falls below
1.8 V. Also, assume that the system must not come out of reset until the battery voltage is above 2 V. This
condition requires 200 mV of hysteresis, which is much greater than the 27-mV hysteresis provided by the
TPS3808 device. Hence, additional hysteresis is required. The remaining section demonstrates the
procedure to be followed to implement the required additional hysteresis.

V1 = Vbat V2 = 1.8 V
Rh = 1 M
Rp 100 kW
Vbat
RESET
VDD
Vs SENSE
Ct MR
GND
TPS3808
Figure 4. Schematic of Supervisor TPS3808 With External Hysteresis Resistor
Using the SVS TPS3808, the circuit was connected as shown in Figure 4. The values for different
components were selected as per the requirements and are listed as follows:
V1+ = 2 V
V1– = 1.8 V
V2 = 1.8 V
To solve the design problem, consider the seven variables and two equations. Five of the seven variables
were selected in order to solve the two equations.
V1+ and V1– were selected to create the desired input supply voltage hysteresis as required by the
system.
V2 was selected to pull up the output of the RESET pin to the desired logic voltage levels.
Rp is typically selected in tens of kW .
Any other resistor can be selected out of the remaining three. Usually, Rh is a good choice with values in
single-digit MW . Typically, Rh is a large value.
When designing the resistors Rh and R2, consider that as R2 increases, Rh increases. Typically, Rh is a
large-valued resistor (can be more than 1 MW ). Because resistors larger than 1 MW are uncommon and
cost more than regularly available resistors, it is a good practice to design Rh as 1 MW and then calculate
resistor R1 and R2 values by simultaneously solving Equation 1 and Equation 2. On the other hand,
selecting R2 with a higher resistance can help further reduce the quiescent current, which improves the
device efficiency. However, a higher R2 resistance implies a large-valued resistor Rh (Rh > 1 MW ). For
this example, the following values were selected:
Rp = 100 kW .
Rh = 1 MW
By solving Equation 1 and Equation 2, deduce the values for R1 and R2.
After solving,
R1 = 102 kW
R2 = 26.7 kW

The designed components were implemented on a printed-circuit board, and the output waveform was
recorded as shown in Figure 5. The input voltage V1 is ramped between 1 V and 3 V, so that the
designed operations can be observed. When V1+ = 2 V, (the circuit operation is initialized and after
certain predetermined time delay Td (20 ms in this case), the RESET pin voltage rises from 0 V to 1.8 V
(V2). When the input voltage is decreasing and V1– falls below 1.8 V, the RESET pin voltage falls back to
0 V.
Figure 5. Output Waveform Indicating Input Voltage and RESET Pin Voltage
5 Conclusion
This application report presents a solution schematic for adding external hysteresis to the supply voltage
supervisors, along with the circuit analysis to clarify how to configure an SVS for this kind of application.
Along with the appropriate equations, the design process can assist designers in tailoring a solution based
on the required applications. A sample module using the TPS3808 was designed and implemented to
guide the user through the procedure. A screen shot from the oscilloscope displays the required results.
In summary, this application report helps designers add supply voltage hysteresis to the SVS to meet
customer application requirements.
6 Reference
TPS3808-EP, Low Quiescent Current, Programmable Delay Supervisory Circuit data sheet (SBVS103)
