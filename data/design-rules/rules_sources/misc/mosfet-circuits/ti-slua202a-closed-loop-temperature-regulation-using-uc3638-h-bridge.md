---
source: "TI SLUA202A -- Closed Loop Temperature Regulation Using UC3638 H-Bridge"
url: "https://www.ti.com/lit/an/slua202a/slua202a.pdf"
format: "PDF 6pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 9587
---

Application Report

Closed-Loop Temperature Regulation Using the UC3638
H-Bridge Motor Controller and a Thermoelectric Cooler
Dave Salerno Power Supply Control Products
ABSTRACT
Forced air systems that direct temperature controlled air to a specific area are available, but are
large, cumbersome, and expensive. This application report describes a portable, low cost,
temperature forcing system.
Contents
1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
2 Methodologies . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
3 Operation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
1 Introduction
How can a designer test a device for overtemperature without putting the entire application
circuit in an oven? The designer may need to access critical circuit nodes for troubleshooting, or
observe the effects of temperature on only one component. Freeze sprays and hair dryers may
be good for benchtop troubleshooting, but the temperature (and temperature slew rate) is highly
uncontrolled and may actually damage the part. Forced air systems that direct temperature
controlled air to a specific area are available, but they are large cumbersome, and expensive.
What is needed is a portable, low cost, temperature forcing system.
One solution is to use a thermoelectric cooler. Thermoelectric coolers (TECs) employ the Peltier
effect, acting as small, solid-state heat pumps when a dc current is passed through them. They
are relatively small, flat devices that transfer heat from one side to the other. The direction of
heat transfer can be reversed, for heating or cooling, by simply reversing the direction of the
current. The amount of heat transfer is controlled by the magnitude of the current. A temperature
difference across a TEC of up to 50°C or more can be achieved using a single element if proper
heatsinking is provided on one side of the device. Larger temperature gradients can be
produced by stacking multiple elements. These gradients can be used effectively as part of a
closed-loop temperature regulation system.

2 Methodologies
A number of methods can be used to regulate the magnitude and direction of the TEC current,
since they operate at a relatively low dc voltage (maximum current ranges from 1 A to 10 A,
depending on size). Linear regulation can be used, but would be very inefficient and would
require bipolar supplies, or some other means of switching polarity to reverse the direction of
current flow. Switching techniques, using pulse width modulation, can be used to improve
efficiency. If heat transfer is required in only one direction, for heating or cooling (but not both), a
simple buck topology, operating from a single supply voltage, can be used to regulate the output
current in one direction. However, in this case, to allow both closed-loop heating and cooling
from a single supply, a bridge topology is necessary . A simplified block diagram of the
closed-loop temperature control system is shown in Figure 1.
UDG−97113
Figure 1. Temperature Controller Block Diagram
3 Operation
Pulse width modulation (PWM) minimizes conduction losses in the control electronics, but
requires a sophisticated PWM controller, especially to prevent problems such as bridge
cross-conduction. The building blocks required for closed-loop PWM control, such as a voltage
reference, error amplifier, pulse width modulator, oscillator, current sense amplifier, and FET
drivers, as well as features such as undervoltage lockout (UVLO) and pulse-by-pulse current
limiting, are all contained in the UC3638. The biasing circuitry needed for single supply operation
is also included. A block diagram of the device is shown in Figure 2.

UDG−95048
Figure 2. UC3638 Block Diagram
The circuit in Figure 3 uses the UC3638 H-bridge controller, four FETs, a differential LC filter,
and a TEC to form a closed-loop temperature regulator. A PWM frequency of 100 kHz is set by
R15 and C13. This frequency was chosen as a compromise to limit switching losses in the
bridge while minimizing the size of the LC filter components. The deadtime between
commutation of the bridge switches is set by the voltage on the DB pin, using the divider of
R12−R14. The voltage on PVSET determines the amplitude of the triangle wave oscillator used
in the PWM modulator.
MOSFETs Q1−Q4 form the bridge, while BJTs Q5−Q8 act as high-side FET drivers, since
outputs AOUT1 and BOUT1 of the UC3638 are open collector. AOUT2 and BOUT2 can drive
the low-side MOSFETs directly. Schottky diodes D1 and D2 clamp any ringing below ground due
to stray circuit inductance. Sense resistor R6 is chosen to limit the peak output current to 5 A.
The current sense voltage is amplified by the UC3638, and any noise spikes are filtered by C12
and a 100-Ω resistor internal to the device.
The LC output filter, formed by L1, L2 and C2−C6, is required to convert the PWM output from
the bridge back to a dc voltage. This is necessary because ac ripple is detrimental to the TEC,
and its efficiency drops off rapidly. Less than 10% ripple is recommended. The resulting
architecture is a low-bandwidth class-D amplifier, which can deliver a variable dc voltage up to
±12V at several amplifiers to the TEC. At these currents, no heatsinking of the MOSFETs is
required. If a higher current TEC is used, heatsinking of the MOSFETs may be required,
primarily due to conduction losses. Another alternative is to use MOSFETs with a lower R .
DS(on)
+12 V
12 Vdc +
AT 2.5 A MAX Q7 R1 C1 12 Vdc
− 2N2222 1 kΩ 2200µF FAN
16 V
R2 Q5 Q8
1 kΩ 2N2222 Q2 2N2907
IRF9Z34 BOUT1
Q6
2N2907 Q1
L1
IRF9Z34
100µH R3
AOUT1 C 0. 2 22µF C 2. 4 2µF C 2. 5 2µF C 2. 6 2µF 680Ω T M E E C LCOR
L2 #CP0.8−127−06L
100µH C3 LED1 LED2 +12 V
0.22µF
R10
Q IR 3 FZ44 Q IR 4 FZ44 10 kΩ R 6. 7 8 kΩ RT1
NTC
C15
0.1µF
R4 R5 UC3638 R8
15 Ω 15 Ω C10 1 kΩ
0.1µF 1 AREF
AREFIN 20
C9 C8 LINEAR TAPER
BOUT2 AOUT2
R11
1µF
DB 19
0.1µF R
5
9
kΩ
470 KΩ
2 COMP BOUT1 18 BOUT1
3 INV BOUT2 17 BOUT2
R12
D1
390Ω
4 REF PVE 16 IN5817
C11
5 VEE VCC 15 +12 V
C7
6 CS+
R6A R6
0.1Ω 0.1Ω R13 7 CSOUT AOUT2 14 AOUT2
3W 3W 3.9 kΩ C12 D2
470 pF IN5817
8 CS−
C13 750 pF AOUT1 13 AOUT1
9 CT
SD 12
10 PVSET RT 11
R14 C14 R15
1 kΩ 0.1µF 2.7 kΩ
UDG−01052
Figure 3. Temperature Regulation Application

To dissipate the heat transferred and generated by the TEC losses, a heatsink and 12-Vdc fan
are mounted in close thermal contact with one side of the device. An aluminum cold plate is
mounted on the other side, forming a sandwich with the TEC in the middle. The aluminum plate,
acting as the control surface, adds thermal mass to help stabilize the loop while protecting the
brittle ceramic surface of the TEC. This plate is placed in direct thermal contact with the item to
be temperature controlled.
RT1, an negative temperature coefficient (NTC) thermistor, is placed in a hole in the side of the
aluminum plate to provide good thermal feedback to close the loop. A parallel resistor helps to
linearize the thermistor’s response. This is not critical, since the temperature control pot is
calibrated, compensating for any non-linearities.
The UC3638 error amplifier compensation uses proportional gain, since it can be difficult to
compensate an integral loop due to the long thermal time constant of the mechanical system.
The dc gain of the error amplifier, determined by R10 and R11, is high enough so that a
temperature error of < 1°C produces full output voltage to the TEC. C10 provides a pole to filter
out any noise before reaching the modulator. Note that the amplitude of the triangle wave
oscillator (set by R13 and R14) also affects overall loop gain.
Temperature control potentiometer R9 is calibrated using a thermocouple temporarily mounted
to the aluminum plate. Once calibrated, it is accurate and repeatable to within 1°C. LEDs across
the output of the filter give a visual indication of whether the TEC is heating or cooling,
depending on the polarity of the output voltage.
The entire system, using the TEC shown, operates from a 12-Vdc, 2.5-A power supply and
provides closed-loop temperature regulation of a surface about 1 inch square. The temperature
of the control surface can be varied from 0°C to 80°C in an ambient environment. Hotter and
colder temperatures are possible if multiple devices are stacked and proper heatsinking is
provided. Remember that cooling can only take place if the heat, including that produced by the
efficiency losses in the TEC, can be dissipated on the opposite surface. Note that the maximum
temperature is ultimately limited by the temperature rating of the solder within the TEC. Devices
with ratings of up to 200°C are available.
TECs can be used in many temperature control applications. They are available in a wide variety
of shapes, sizes, power and voltage ratings from a number of manufacturers. Some

manufacturers also supply heatsinks, cold plates and fans. However, low-cost Pentium -style
heatsink and fan combinations can often be adapted.

Pentium is a registered trademark of Intel Corporation.
