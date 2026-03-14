---
source: "TI SLVA670A -- Managing Inrush Current"
url: "https://www.ti.com/lit/an/slva670a/slva670a.pdf"
format: "PDF 13pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 15032
---

Application Report

Managing Inrush Current
Alek Kaknevicius and Adam Hoover.................................. Drivers and Load Switches
ABSTRACT
In most systems, capacitors are placed throughout a design to ensure there are no voltage drops on the
supply rails. When power is initially applied to the system, charging these capacitors can result in an
inrush current which can exceed the nominal load current. If left unaddressed, this can cause voltage rails
to fall out of regulation, resulting in the system entering an undesired state. Additionally, the inrush current
can exceed the current carrying capability of board connectors as well as PCB traces, resulting in
damaging the connectors and traces.
These problems can be mitigated by using Texas Instruments load switches. The load switches in the
TPS229xx family are slew rate controlled to minimize inrush current. This application note explores typical
causes of inrush current, problems caused by inrush current, and solutions for inrush current featuring
integrated load switches.
Contents
1 What is Inrush Current?................................................... 2
1.1 Effects of Load Capacitance ........................................... 3
2 Problems Caused by Inrush Current ........................................... 4
3 Methods of Reducing Inrush Current............................................ 5
3.1 "Soft-start” or Voltage Regulators ........................................ 5
3.2 Discrete Implementation .............................................. 5
3.3 Integrated Load Switches.............................................. 6
3.4 Advantages and Disadvantages of these Solutions............................... 6
4 Application Examples .................................................... 7
4.1 Effects of Using a Slew Rate Controlled Load Switch............................. 10
5 Conclusion ......................................................... 12
6 References ......................................................... 12

1 What is Inrush Current?
An example system, shown in Figure 1, uses a power supply – DC/DC, LDO, or external supply – to
supply voltage to a downstream load.
Load
Power Supply Load
Load
Figure 1. Typical Power Distribution
Upon system startup, the power supply will ramp up to the regulated voltage. As the voltage increases,
an inrush of current flows into the uncharged capacitors. Inrush current can also be generated when a
capacitive load is switched onto a power rail and must be charged to that voltage level. The amount of
inrush current into the capacitors is determined by the slope of the voltage ramp as described in
Equation 1:
dV
I = C ´
INRUSH LOAD dt (1)
Where
I = amount of inrush current caused by a capacitance
INRUSH
C = total capacitance
dV = change in voltage during ramp up
dt = rise time (during voltage ramp up)

1.1 Effects of Load Capacitance
Increasing the system capacitance to reduce transient voltage dips comes at the cost of increased inrush
current generated from charging the increased capacitance. The following two figures display inrush
current by showing a power supply starting up into different capacitive loads. Figure 2, below, shows a
scope shot of a 3.3 V power supply starting up into a 47 µF capacitance.
Figure 2. 3.3V Applied to a 47µF Capacitor
In Figure 2, as the power supply turns on and the capacitor charges, over 3.12 A of inrush current is
generated. Figure 3, below, shows the same power supply turning on with a lower capacitance.
Figure 3. 3.3 V Applied to a 22 µF Capacitor
With a reduced capacitance of 22 µF, Figure 3 shows that the inrush current is reduced to 1.6 A.
Reducing the load capacitance decreases inrush current, but it can also decrease voltage rail stability
during transient current events. Certain loads may require specific output capacitance to operate, and
reducing this output capacitance is not an option. Solutions to this scenario are discussed in Section 3.

2 Problems Caused by Inrush Current
There are two key concerns associated with inrush current. The first is exceeding the absolute maximum
current ratings of the traces and components on a PCB. All connectors and terminal blocks have a specific
current rating which, if exceeded, could cause damage to these parts. Likewise, all PCB traces are
designed with a certain current carrying capability in mind and are also at risk to damage. When designing
the PCB traces and selecting connectors, not taking the inrush current peak into account can damage the
power path and lead to system failure; however, appropriately designing for a large inrush current peak
will lead to thicker PCB traces and more durable connectors which can increase the size and cost of the
overall design.
The second problem occurs when a capacitive load switches onto an already stable voltage rail. If the
power supply cannot handle the amount of inrush current needed to charge that capacitor, then the
voltage on that rail will be pulled down. Figure 4 is an example of a 100 µF capacitance being applied to a
voltage supply without any slew rate control. The capacitance generates 6.88 A of inrush current and
forces the voltage rail to drop from 3.3 V down to 960 mV.
Figure 4. Power Supply Dip due to Inrush Current
If other modules are connected to this power rail and the voltage drops, then these modules may reset
themselves and put the rest of the system into an undesired state. If the voltage regulator is unable to
supply enough current at turn-on, the voltage rail could collapse completely leading to system failure.

3 Methods of Reducing Inrush Current
Inrush current can be reduced by increasing the voltage rise time on the load capacitance and slowing
down the rate at which the capacitors charge. Three different solutions to reduce inrush current are shown
below: voltage regulators, discrete components, and integrated load switches. All three of these solutions
center around increasing the voltage rise time which, as shown in Equation 1, leads to reduced inrush
current.
3.1 "Soft-start” or Voltage Regulators
Voltage regulators, DC/DC converters, and LDOs may have an integrated soft-start functionality. With this
feature, the rise time can be increased, thereby reducing the inrush current. With a properly selected
DC/DC converter or LDO, the inrush can be effectively managed to ensure system stability.
3.2 Discrete Implementation
Power switching with a controlled rise time can be accomplished by using discrete circuitry and can be
done in several ways. An example circuit of one solution is shown in Figure 5. This particular solution
requires a minimum of 4 components (2 MOSFETS, 2 resistors) and the slew rate of VOUT can be
controlled by using the resistor R . However, R needs to be very large (in the range of MΩ) to have an
SR SR
effect on the rise time of VOUT. To be able to reduce the value of R , an additional capacitor would need
SR
to be added.
Figure 5. Discrete Load Switch Implementation

3.3 Integrated Load Switches
Integrated load switches can be used in place of the discrete solution discussed in Section 3.2. All Texas
Instruments load switches (TPS229xx products) feature a controlled output slew rate to mitigate inrush
current. Figure 6 below shows the typical application circuit for a load switch.
Figure 6. Typical Load Switch Application Circuit
3.4 Advantages and Disadvantages of these Solutions
While all of these solutions can help to manage inrush current, they all come with their advantages and
disadvantages. The least integrated of all the above solutions is the discrete implementation. When
compared to its integrated counterpart, the load switch, it requires more components and a much larger
solution size. By contrast, the most integrated solution is the DC/DC converter or voltage regulator with
soft-start already built in. Despite its integration, adding load switches may be more beneficial for the
system. If a voltage rail requires multiple capacitive loads which need to be switched individually, then
multiple load switches can be used rather than multiple voltage regulators. This will reduce overall cost
and solution size. Also, if the chosen voltage regulator does not come with an integrated slew rate control,
then a load switch can be used before or after to provide that function. Adding a load switch to a system
for inrush current control may require an additional component, but it can reduce the overall design size
and cost.

4 Application Examples
The following application examples will use the design parameters shown in Table 1:
Table 1. Application Example 1
Design Parameter Example Value
Load Switch input voltage (V ) 3.3 V
IN
Capacitive load (C ) 22 µF
LOAD
Maximum acceptable inrush current 600 mA
Using a V of 3.3 V, a C of 22 µF, and a maximum acceptable inrush current of 600 mA, the required
IN LOAD
rise time for the output can be calculated.
Starting with Equation 2,
dV
I = C ´
INRUSH LOAD dt (2)
The rise time can be calculated as:
C ´ dV 22 µF´ 3.3 V
dt = LOAD = =1 21 µs
I 600 mA
INRUSH (3)
This means that the load switch which is chosen for this application must have a rise time of 121µs or
higher. By visiting www.ti.com/loadswitches, all available Texas Instruments load switches can be sorted
by rise time using the online parametric table. Using this method, an appropriate load switch can be
chosen.
4.0.1 Fixed Rise Time Solution
At V = 3.3 V, the TPS22902B has a typical rise time of 146 µs and can be used to ensure an inrush
IN
current lower than 600 mA. The controlled rise time of the load switch and resulting inrush current are
shown in Figure 7.
Figure 7. TPS22902B Inrush Current
The peak inrush current measured is 392 mA. This is well below the 600 mA design requirement and
much lower than the 1.6 A seen in Figure 3 without any load switches being used. By selecting the
correct load switch, the inrush current is effectively managed.

Several Texas Instruments load switches with a fixed rise time have A, B, C, or D variations. These letters
are used at the end of the part number to denote different rise times. An A version load switch has the
fastest rise time (typically below 10 µs) and a D version load switch has the slowest (several milliseconds).
For example, the TPS22924 load switch has B, C, and D variations with rise times of 96 µs, 800 µs, and
9 ms, respectively. In this application example, a rise time of greater than 121 µs was calculated to limit
the inrush current to 600 mA. The rise time of the B version would be too fast and either the C or D
version could be used.
4.0.2 Adjustable Rise Time Solution
All Texas Instruments load switches feature a controlled rise time, and for some load switches this rise
time can be adjusted. The rise time of these devices can be increased by adding an external capacitor
between the available CT pin and GND. The TPS22965 offers this feature, and its typical application
schematic shown in Figure 8.
VIN VOUT
C IN ON C L
ON CT
OFF
VBIAS GND
TPS22965
Figure 8. TPS22965 Application Circuit
Using the datasheet for this device, the appropriate CT capacitor can be chosen to implement a desired
rise time. Both the equation and table in the Adjustable Rise Time section of the TPS22965 datasheet
can be used to this effect. Figure 9 below shows the datasheet table which allows the user to determine
the appropriate CT capacitor needed for a desired rise time.
Figure 9. TPS22965 Rise Time vs CT Capacitor

If no CT capacitor is used, then the rise time of the load switch may be too fast to limit the inrush current
to the desired peak value. Figure 10 shows the TPS22965 powering up into a 22 µF load without any CT
capacitance.
Figure 10. TPS22965 Scope Capture (CT cap = 0 pF)
With no CT capacitor, the rise time of the TPS22965 is faster than the calculated 121 µs and results in an
inrush current of about 670 mA, larger than the design goal of 600 mA. The below screenshots show the
device powering up into the 22 µF load with different CT capacitors.
Figure 11. TPS22965 Scope Capture (CT cap = 150 pF)

Figure 12. TPS22965 Scope Capture (CT cap = 2200 pF)
Figure 11 was taken with a CT capacitor of 150 pF and Figure 12 with 2200 pF. As the CT capacitor
increases, the rise time of the device also increases and the inrush current is reduced to well below the
design goal of 600 mA. While the CT pin increases the amount of flexibility in design, it does require an
additional component to implement. However, this allows for a single load switch to be used across
multiple designs with varying capacitive loads.
4.1 Effects of Using a Slew Rate Controlled Load Switch
The following example uses a 5 V power supply which is brought down to 1.8 V using a buck converter.
After the 1.8 V rail has powered up, a 100 µF capacitance is applied to the system, as shown in Figure 13.
4.1.1 Response without Slew Rate Control
VOUT
5V Power 1.8V Buck
Supply Converter
66µF
100µF
INRUSH
Figure 13. System Block Diagram without Slew Rate Control

With no controlled rise time, the switch does not provide any inrush current management and the following
results can be observed:
Figure 14. Inrush Current and Voltage Drop without Slew Rate Control
The inrush current generated by the 100 µF capacitor peaks at 6.46 A and brings the 1.8 V rail down to
320 mV. This 82% voltage reduction on the power rail can cause the system to reset or fail.
4.1.2 Response with Slew Rate Control from a Load Switch
Figure 15 shows the same system as before, except the TPS22965 load switch from Texas Instruments
with controlled rise time is used to switch the 100 µF capacitive load.
VIN
5V Power 1.8V Buck
Supply Converter
66µF
VOUT
TPS22965 100µF
INRUSH ON
Figure 15. System Block Diagram utilizing the TPS22965

Using a 150 pF capacitor on the CT pin of the load switch, the following results can be observed:
Figure 16. Inrush Current and Voltage Drop with Slew Rate Control
With the controlled slew rate of the TPS22965, the maximum inrush current drops from 6.46 A to 960 mA.
The 1.8 V output of the buck converter also shows no significant voltage drop.
5 Conclusion
Large capacitance can lead to inrush current resulting in device damage, system instability or undesired
behavior. Using a TI load switch is a size and cost efficient solution for managing inrush current.
The TI load switch portfolio has a wide variety of parts with different slew rates to address the inrush
currents of different system requirements. By using Equation 1 and the parametric search table at
ti.com/loadswitches, inrush current can be effectively managed by using a TI Integrated Load Switch from
the TPS229xx family.
6 References
1. TPS22965, 5.7-V, 6-A, 16-mΩ On-Resistance Load Switch (SLVSBJ0)
2. TPS22902B, 3.6-V, 500-mA, 78-mΩ ON-Resistance Load Switch With Controlled Turnon (SLVS803)
