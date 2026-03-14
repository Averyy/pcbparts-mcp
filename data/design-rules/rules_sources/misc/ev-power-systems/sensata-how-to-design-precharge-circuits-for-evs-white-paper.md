---
source: "Sensata -- How to Design Precharge Circuits for EVs White Paper"
url: "https://www.sensata.com/sites/default/files/a/sensata-how-to-design-precharge-circuits-evs-whitepaper.pdf"
format: "PDF 10pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 29083
---

HOW TO DESIGN A PRECHARGE CIRCUIT FOR
HYBRID AND ELECTRIC VEHICLE APPLICATIONS
TECHNICAL WHITE PAPER
By
Brian Munari, Business Development Manager - HVOR Electrification, Sensata Technologies
Andrew Schneer, Applications Engineer - HVOR Electrification, Sensata Technologies
CONTENTS
PRECHARGE OVERVIEW Choosing a resistor 6
What is precharging? 2
Testing and validation 10
Why is it necessary? 2
Quick reference table 10
What advantages do precharge circuits
provide? 2 USING A PRECHARGE CIRCUIT
What causes inrush? 3 Order of operation 11
Capacitive inrush 3 How do precharge circuits typically fail? 12
How to measure inrush current 4 What about “wet switching” and “dry
switching” contactors? 12
DESIGNING A PRECHARGE CIRCUIT Conclusion 12
Typical precharge circuit 4
SOLUTIONS
Component requirement specifications 5
Precharge contactors 13
The RC circuit 5
Calculating the resistor value 6
1
www.sensata.com

SUMMARY
Precharge circuits are essential for applications with capacitive loads that can result in high inrush currents during power
up. Current spikes of thousands of amps can easily damage system components such as causing contactors to weld
closed.
This paper will highlight the benefits of using precharge circuits, as well as provide a comprehensive review of how to
design a precharge circuit and select the required components.
PRECHARGE OVERVIEW
What is precharging?
A high voltage system with downstream capacitance can be exposed to damaging inrush current when the system is first
turned on. If this current is not limited and controlled, it can cause significant stress or damage to other components in
the system.
A precharge circuit is used to limit this inrush current to slowly charge the downstream capacitance. It plays a critical role
in the proper operation and protection of components in high voltage applications. Precharging increases the lifespan
of electric components and the reliability of the system as a whole. A precharge circuit allows the current to flow in a
controlled manner until the voltage level rises to very near the source voltage before the main contactors are permitted to
close.
In some applications, such as industrial power supplies or utility power distribution, usage of a precharge circuit is
infrequent. In other applications, such as hybrid or electric vehicles, the precharge circuit may be used every time the
vehicle is turned on. The latter is the subject of this paper.
Why is it necessary?
Welded contacts are one of the most common failure modes of contactors. There are a few common causes for this:
• A short circuit resulting in thousands of amps passing through a closed contactor can cause the contacts to weld
together due to the high heat generated at the junction. This type of failure is not very common and is relatively easy
to diagnose. For example, a short circuit is often accompanied by the clearing of a fuse, and quite possibly a barely
recognizable wrench that happened to fall across the battery terminals just so.
• High shock and vibration can also contribute to contactor welding. An applied shock can jolt the contacts apart while
current is flowing through them, followed by an immediate re-close. The arc that is formed during the momentary
opening can cause localized hot spots that melt. When the contactor re-closes and the hot spots cool and solidify, the
contactor is then welded. Shock and vibration induced welding is also not very common but important to be aware of.
• By far, the most common culprit of contactor welding is inrush currents. The lack of a precharge circuit, a precharge
circuit that is not properly designed, or one that is not being used correctly, can all contribute to welding. The result
is a contactor that will close but will not reopen. This cause of welded contacts is sometimes overlooked and is not
easily recognized or understood.
Quite often the field complaint is, “my contactor welded when I tried to open it.” However, it is far more likely that the
contactor actually welded when it closed. The problem was simply not discovered until the contactor was commanded to
open.
What advantages do precharge circuits provide?
In addition to preventing welded contacts, precharging can also be helpful in detecting faulty circuits, system issues, or
other electrical hazards. For example, trying to precharge into a soft-short will not be successful because the system
will detect that the downstream voltage is not increasing and it will react by automatically terminating the precharge. In
the case of a hard short, the pre-charge resistor will limit the current, which will minimize system damage while the fuse
clears the fault. A fault indicator or alarm code can be used to alert the operator or technician to investigate further.
In some cases, the inrush current may be large enough to trip a circuit breaker or blow a fuse. A precharge circuit can be
used to eliminate nuisance tripping of certain protection devices.
2

When do I need a precharge circuit?
A precharge circuit is required if any of the following are problematic:
• The load downstream of the main contactors has components that may be damaged by the inrush current
• The main fuse or circuit breaker will trip if asked to carry the inrush current
• The inrush current will damage the main contactors and/or will cause them to weld
• The battery cells are not rated for the inrush current
What causes inrush?
The three most common types of circuits that a contactor might switch into are resistive, inductive, or capacitive, or some
combination thereof. In practice, real circuits tend to have all three qualities, but one in particular will typically dominate.
1. RESISTIVE LOADS:
A heating element is a good example of a resistive load and tends to be fairly benign for a contactor to switch
power both ON and OFF. There is no inrush with a resistive load because, by nature, the load is already
restricting current flow.
2. INDUCTIVE LOADS:
Motors are generally inductive (with the exception of a wound-field synchronous motor which makes it appear
capacitive). Contactors that are used to select between “forward” and “reverse” of a series DC motor or
a 3-phase industrial motor must be designed to withstand a highly inductive load. However, most modern
electric drive systems use inverters to control the motor directly, so the need for this type of contactor is
somewhat limited. Closing a contactor into an inductive load is generally not an issue because the inductance
resists rapid changes in current, allowing the current to increase gradually after the contactor is closed. The
challenge with inductive loads is opening while current is flowing. Since the inductance resists rapid changes
in current, it allows the current to continue flowing longer as the contactor opens, increasing the duration and
energy of the arc that the contactor must break.
3. CAPACITIVE LOADS:
Motor inverters and other components connected to the DC link voltage in a hybrid or electric vehicle typically
have input filter capacitors. This paper will take a closer look at this type of circuit. The capacitors are used to
limit voltage drops on the supply rails during momentary loads. This presents a high risk of contactor welding
when the main contactor closes if the capacitance is not properly charged.
Capacitive inrush
When voltage is applied to an uncharged capacitive load it causes the capacitor to start charging. The current initially
starts with an inrush and eventually tapers down to a steady state condition, as shown in the figure below.
Current
Inrush current
Nominal current
Time
Duration of inrush
Figure 1: Example of inrush current without precharge
3

The goal of the precharge circuit is to limit inrush current at system power-up. Depending on the system voltage, the
capacitance value, and the intended design, precharge can take as little as a few milliseconds or as long as several
seconds. In general, the higher the system voltage and the larger the capacitance, the longer the precharge time will be.
Since the system voltage is likely fixed by the engineering manager or the battery supplier, and the system capacitance is
likely fixed by the motor inverter and other connected components, the only remaining parameter left to work with is time.
A resistor acts like a valve, limiting current flow and extending the amount of time there is to work with.
One way to think about this is using a “bucket of water” analogy.
• Capacitance is the size of an empty bucket
• Voltage is how high a water tower is next to the bucket
• Current is how fast the bucket is filled
If a small tube was connected from the water tower to the bucket, it might take a while to the fill bucket. However, if a
firehose was connected instead, it would fill the bucket much faster. In fact, the moment the water valve on the fire hose
is opened, the force of the water might blow the bucket away in the process. This is why contactors weld.
How to measure inrush current
When a contactor closes, the inrush current spike is extremely fast, typically 50 to 100 µs in duration. It happens right
when the contacts start to close, bounce slightly, then re-close. To measure it, a 100MHz or faster oscilloscope is
needed in addition to a compatible current probe that can measure at least 1000A without distortion. It is recommended
to set the scope at 50µs / division and trigger at 500 Amps as a starting point. Having a properly designed precharge
circuit can save cost and time as it eliminates the need for a scope as well as the time required to diagnose welded
contacts.
DESIGNING A PRECHARGE CIRCUIT
Typical precharge circuit
In the traction battery system of an electric vehicle there are typically two main contactors to provide double isolation of
the battery voltage when the system is turned off:
• Main Positive Contactor
• Main Negative Contactor
The precharge circuit usually consists of a separate, smaller contactor connected in series with a resistor. These two
components are then wired in parallel across the main contactor (Figure 2). The precharge circuit is commonly found on
the positive leg, but it could just as easily be installed on the negative leg.
Resistor
Precharge Contactor
+ Positive Contactor
Traction
Motor Motor
Battery
Inverter
-
Negative Contactor
Figure 2: Typical main battery disconnect with precharge circuit
4

Component requirement specifications
Since the precharge circuit is directly connected to the battery, both the contactor and the resistor must be rated for full
battery voltage. The precharge contactor and resistor must also be able to handle the precharge current and power
dissipation.
• The continuous current rating of the precharge contactor is not as critical since the time required to carry the
precharge current is short, usually just a few seconds.
• The ability of the precharge contactor to break under load is also not as critical since it will not be breaking any current
flow during normal operation. However, it does need to be able to make under load thousands of times over the life of
the vehicle, as this happens every time precharging occurs.
• The peak current capability of the precharge contactor is important and should be referenced on the data sheet.
The precharge resistor can be placed before or after the precharge contactor. In most cases, the resistor is placed after
the contactor to reduce the number of connection points that are continuously energized by the battery pack when the
system is off. Placing the precharge and main contactors as close as possible to the battery pack minimizes the potential
points of exposure to high voltage.
The RC circuit
When a resistor is connected in series with a capacitor it forms a simple RC circuit. When voltage is applied, the
capacitor will gradually charge up through the resistor until the voltage equalizes.
• The precharge current will drop to 1/e (36.7%) of its initial value after just one time constant, also known as one Tau,
or 1T.
• Likewise, the precharge voltage across the capacitor will climb to 63.2% of the supply voltage after 1T. Tau can be
found using:
T = Tau (seconds)
R = Resistance (Ohms)
C = Capacitance (Farads)
Five time constants (5T) are needed for a capacitor to fully charge. Note: Since the charge curve for an RC circuit
is exponential, the capacitor never really becomes 100% “fully” charged. For this reason, five time constants (5T) is
considered best practice in circuit design, which results in 99.33% full charge.
The voltage across the capacitor at any moment in time during the precharge period is found using the following formula:
Vc = Voltage across the capacitor (Volts)
Vs = Battery supply voltage (Volts)
t = Time since the supply voltage was applied (seconds)
RC = The time constant of the RC circuit (Ohms, Farads)
e = 2.71828 (mathematical constant)
After four time constants (4T), a capacitor is nearly fully charged and the voltage across it will be about 98% of the battery
supply voltage. The period of time, from 0T through 4T, is known as the Transient Period. The time after 4T is called the
Steady State Period.
5

Likewise, the current flowing into the capacitor at any given time during the precharge period can be found using:
I = Current flowing into the capacitor (Amps)
Vs = Battery supply voltage (Volts)
Vc = Voltage across the capacitor (Volts)
R = Resistor value (Ohms)
The plot in Figure 3 presents all of this information together. It shows the precharge voltage, current, and the other
related points of interest described above for a simple RC circuit. This plot demonstrates why 5T is considered best
practice for the amount of time required to precharge a capacitor.
Figure 3: Precharge current and voltage plot
Calculating the resistor value
The precharge resistor value is determined by the capacitance of the load and the desired precharge time.
EXAMPLE:
Imagine that a 400 Volt battery is connected to an inverter with 6 mF of input capacitance and the system needs to
precharge in 1.5 seconds. Using the formulas above, the required resistor value can be calculated as:
5 Tau = 1.5 seconds (this is the desired precharge time)
Therefore…
1 Tau = 0.3 seconds
Tau = R * C
0.3 seconds = R * .006 Farads
R = 50 Ohms
Choosing a resistor
Depending on the application and requirement specifications, there are a variety of different types of resistors that could
be used as a precharge resistor. These include wire-wound, ceramic and carbon, thin film, and extruded aluminum, just
to name a few.
6

If the precharging time is sufficiently long (>3 time constants), the resistor will dissipate the same amount of energy as the
total energy stored in the fully-charged input capacitors according to the following formula:
E = Energy (Joules)
C = Capacitance (Farads)
V = Voltage (Volts)
Continuing from the example from above, the energy in the charged capacitors, and therefore the energy dissipated
by the precharge resistor, is:
E = ( C * V2) / 2
E = (.006 F * 400V2) / 2
E = 480 Joules
A CLOSER LOOK
Note: The E = (C*V2)/2 formula above is a simplification of the special case where “time” is large. The total energy in
the capacitor, the total energy dissipated by the resistor, and the total energy supplied by the battery all vary over time
during precharging. If charging only lasted for a few time constants (1T, 2T, etc.), the energy through the resistor and
capacitor would not be equal. However, if the precharge circuit is always designed for 3 time constants or longer, then
E = (C*V2)/2 is a fine approximation (98% accurate or better).
The same example is presented below using the long form equation:
The result is the same since the amount of time was sufficiently large.
7

The precharge resistor must be rated to handle the power that will be dissipated during pre-charging.
Note that the power dissipated by the precharge resistor is not constant and not linear during precharge. This is found
using:
P = Power dissipated by precharge resistor (Watts)
I = Current through the resistor (Amps)
R = Resistor value (Ohms)
Figure 4: Example plot of power over time through the precharge resistor
The instantaneous peak power occurs right at the beginning of precharging when the current is highest. This can be
calculated by taking (I^2)*R at t=0, at which time the current is simply the battery voltage divided by the precharge
resistance. This peak power only lasts for a very short amount of time.
After this initial peak power, the precharge resistor will continue dissipating energy until precharging is finished. When
selecting a resistor, it may be sufficient to treat the average power over the entire precharge duration as a peak power
whose duration is the precharging time. This can be found by simply dividing the total energy dissipated by the resistor
by the total precharge time. It is up to the system designer to determine whether average power is an appropriate
approximation to use given the chosen precharge resistor.
P = Power (Watts)
E = Energy (Joules)
T = Time (seconds)
Continued from above:
P = E / T
P = 480 J / 1.5 s
P = 320 Watts
8

Due to the power surge during precharging, the precharge resistor must be
robust in design and rated for high power. Since the duration of the precharge
is relatively short, it is not required to specify a resistor that can handle all of
this power on a continuous basis. In fact, some manufacturers will specify
the peak power dissipation. The datasheet may indicate: “Overload = 5 times
rated wattage for 5 seconds” or something similar. In our example, a 100 Watt
resistor that can handle 500 Watts peak for 5 seconds would easily exceed the
requirement.
In summary, the resistor should be selected such that its power ratings are
sufficient to handle the average and peak power of the circuit. In addition,it is
always a good idea to show the entire power curve (Figure 4) to the resistor
Figure 5: Examples of heat-sinkable
manufacturer and get their recommendation for how best to select a power
resistors
rating.
There may not be a resistor that exactly matches the specifications that have
been calculated. Resistor manufacturers often offer resistors in a series or family with steps in value between each
resistor such as 25, 50, 75, 100 Ohm. Unless a resistor is being designed to meet exact needs, it is likely that an off-the-
shelf resistor will be selected from a catalog and the calculations will need to be run again to determine the impact on the
precharge time.
Continued from above:
• 400 Volt battery
• 6 mF of input capacitance
• 1.5 second precharge time
• 50 ohm resistor
The voltage and current precharge curves will look like the plot in Figure 6. Notice how the peak inrush current is
only 8 Amps using this precharge circuit. Compare this to the initial inrush current and the benefit of using a pre-
charge circuit becomes obvious.
Figure 6: Example voltage and current during precharge
It is recommended to build a spreadsheet for precharge circuit calculations to allow for quick experiments with different
values to determine what is most suitable for a particular application.
9

Figure 7: Example precharge calculation spreadsheet
Testing and validation
Naturally, there are tradeoffs that must be factored in. For example, perhaps the precharge time will be a little slower
or a little faster than originally intended due to the availability of off-the-shelf components, or the tolerance of the
resistor. Perhaps the current will be a little higher or a little lower. One should also factor in the minimum and maximum
ambient temperature of the environment that the precharge circuit will be operating in. Best practice is to design for the
worst-case condition with some safety margin in order to cover any unforeseen corner cases. It is worthwhile to circle
back through the calculations to double check the expected performance once all of the data sheets for the selected
components are available.
With final numbers in hand, a test plan can be created to verify the design. It is essential to test the precharge circuit in
the application under various conditions to confirm all aspects of the design including, but not limited to, voltage, current,
precharge time, and temperature. It is recommended to test at the min and max of each. Creating a test plan matrix
showing all possible combinations of these operating conditions can help ensure the design is properly validated.
Quick reference table
The table in Figure 8 shows a few example values using a 400V and 800V battery connected to both a 4 mF and 6 mF
capacitance, and charging for 5 time constants. The data table demonstrates how the precharge time impacts the resistor
value and average power dissipation requirement.
Figure 8: Quick reference table
10

USING A PRECHARGE CIRCUIT
Order of operation
The sequence of events to precharging a system is typically comprised of the following steps:
1. Close the Main Negative contactor
2. Close the Precharge contactor
3. Monitor the voltage to ensure it is rising as expected
4. When the voltage has equalized (after 5 Tau), close the Main Positive contactor
5. Open the Precharge contactor
6. Power up the main system components
5
2 Resistor
Precharge Contactor
4
3
+ Positive Contactor
Motor Motor
Battery
Inverter
- 6
1
Negative Contactor
Figure 9: Sequence of precharge operation
If the contactors are equipped with auxiliary feedback, and if there is time permitted during the startup sequence, it could
be beneficial to close and open each contactor one at a time to ensure each is functioning properly. This is a quick and
easy way to determine if a contactor is welded, or if a contactor driver circuit is not working, before precharging begins.
In addition, if voltage sensors are connected downstream of the contactors, this is also a good opportunity check them to
ensure nothing is out of range prior to initiating the precharge sequence.
The time required to complete the component functional verification test may not be suitable for all applications.
However, for large commercial or industrial applications where the power-up sequence is only run once per day, or when
power-up time is not that critical, it is ideal to run a quick check at each startup to ensure everything is working properly.
While the Main Positive and Main Negative contactors almost always have auxiliary feedback, most precharge contactors
do not. This is done to help keep costs to a minimum and to simplify the design. If a precharge contactor fails to close,
it is relatively easy to diagnose since the system voltage will not start rising. The possibility of welding a precharge
contactor is low since it is closing into a RC circuit with a known low inrush.
When the precharge contactor is closed as shown in the sequence in Figure 9, it is important to monitor the voltage to
ensure it is rising as expected. If the “voltage rising curve” is well understood, the voltage over time can be measured
during precharge to ensure that it is within an acceptable and expected range. Programming upper and lower bounds
on the curve will help to disengage the precharge circuit if the voltage rises too fast or too slow. Voltage rising too slow
may indicate a soft short, or a downstream load that was left on. Voltage rising too fast may be a result of not all of the
downstream loads being properly connected. This is why it is not a good idea to use a simple timer on a precharge
circuit. There are too many variables and possible failure modes that a timer circuit simply cannot catch.
11

The last step, opening the precharge contactor, is not necessary but is generally considered best practice. Current will
follow the path of least resistance across the main contactor. However, if the precharge circuit were left connected, and
if something were to happen to the main contactor causing it to open, all of the system current during vehicle operation
would then be directed through the precharge resistor which could quickly overheat and fail. Once precharging is
complete, it is best to simply disconnect it from the circuit to minimize risk.
How do precharge circuits typically fail?
Loads on the distribution system must all be switched off during precharge. Trying to precharge a system that is on and
running may never be successful. In fact, the resistor may end up burning out from such an attempt. Smart precharge
circuits include a timer to abort the precharge if the voltage does not reach a certain level within a prescribed period of
time. Some also include a counter so that only a certain number of precharge events can occur within a certain window of
time to prevent the resistor from overheating.
A preferred approach is to use a heat-sinkable resistor that can withstand an unlimited number of precharge cycles in
rapid succession without ever overheating. Naturally, there are cost implications and trade-offs with this design approach,
but it results in a very robust solution.
Consider this example from an actual corner case involving a vehicle driver on their lunch break. Perhaps they like to
fidget by cycling the key from ON to OFF over and over again. The driver may not realize it but each time they turn the key
ON it could be triggering a precharge event which could result in overheating the resistor. If the resistor was sized to take
this abuse, or if the vehicle was designed with a smart precharge counter, there would be no unwanted thermal events to
worry about.
What about “wet switching” and “dry switching” contactors?
When a contactor or relay is opened or closed with no current flowing it is referred to as “dry switching”. In general, this
is usually considered to be anything less than 1mA. “Wet switching”, on the other hand, is switching anything more than
1mA.
Contactors and relays rated for wet service use materials designed to withstand arcing. Some of them actually depend
on arcing as a cleaning mechanism. A relay rated for wet service that gets used in dry service can have its contacts
develop surface contamination that could, over time, interfere with contact closure, resulting in less than optimal contact
resistance. Eventually, they will have a higher voltage drop across the switch leading to increased heating and premature
failure.
Conversely, relays rated for dry switching have very low contact resistance as long as they are never opened or closed
while current is flowing. Gold is commonly used for the contact material in a dry rated switch. Wet switching a dry rated
contactor or relay just once can easily destroy it.
This particular “dry switching” issue is common for open air contactors but it is not a problem for hermetically sealed
contactors like the ones available from GIGAVAC. Hermetically sealed contactors can be switched wet or dry with
little to no impact on the life of the switch. This makes them ideal for use as precharge contactors and main contactors
because they can switch at zero voltage delta and zero current flow without any performance reduction over the life of the
contactor.
Conclusion
To prevent high peak transient currents, it is best to precharge to get the voltage differential as close to zero as possible
before closing the main contactors. This will greatly extend the reliability of the contactors and eliminate contactor
welding.
12

SOLUTIONS
Precharge contactors
GIGAVAC has several hermetically sealed contactors that are ideal for precharge due to their high voltage ratings, high
momentary overcurrent capability, and small form factor.
P195 contactor:
• 1500 Volts
• 80 Amps continuous
• 200 Amps for 10 seconds.
• 12, 24, and 48 Vdc coil options
• 34 x 54 x 82 mm
GV210 contactor:
• 900 Volts
• 150 Amps continuous
• 200 Amps for 3 minutes
• 12, 24, and 48 Vdc coil options
• 41 x 55 x 56 mm
All specifications are valid as of the date of this publication. Please refer to the datasheet for details.
Main Contactors
GIGAVAC has a wide variety of contactors that are suitable for traction battery voltage isolation.
GV350 Series Contactor:
• 1000 Volts
• 500 Amps continuous
• 1500 Amps for 20 seconds
• External PWM coil
• 61 x 81 x 76 mm
GV200 Series Contactor:
• 800 Volts
• 500 Amps continuous
• 2000 Amps for 20 seconds
• 12, 24, 48 Vdc, PWM internal and external coil options
• 56 x 73 x 81 mm
HX460 Series Contactor:
• 1500 Volts
• 1000 Amps continuous
• 12, 24 Vdc coil options
• 114 x 114 x 154 mm
All specifications are valid as of the date of this publication. Please refer to the datasheets for details.
13
WP-00012-Rev. 12/11/2020 EN, AUG 2020 • HOW TO DESIGN A PRECHARGE CIRCUIT FOR HYBRID AND ELECTRIC VEHICLE APPLICATIONS •
Copyright © 2020 Sensata Technologies, Inc. All rights reserved.