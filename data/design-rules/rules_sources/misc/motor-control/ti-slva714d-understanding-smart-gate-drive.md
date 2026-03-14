---
source: "TI SLVA714D -- Understanding Smart Gate Drive"
url: "https://www.ti.com/lit/an/slva714d/slva714d.pdf"
format: "PDF 24pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 39954
---

Application Report
Understanding Smart Gate Drive
Nicholas Oborny, Ashish Ojha
ABSTRACT
The gate driver in a motor system design is an integrated circuit (IC) that primarily deals with enhancing external
power MOSFETs to drive current to a electric motor. The gate driver acts as an intermediate stage between
the logic-level control inputs and the power MOSFETs. The gate driver must be robust and flexible enough to
accommodate a wide variety of external MOSFET selections and external system conditions.
Texas Instrument’s Smart Gate Drive helps system designers solve a variety of common challenges present in
today's motor applications. These challenges include slew rate control and adjustment for optimizing switching
and EMC performance, decreasing bill of material (BOM) count, managing MOSFET and system protections,
and improving driver timing performance for motor control.
This application report describes the theory and methods behind enhancing a power MOSFET, the various
challenges encountered in motor gate driver systems, and the different features implemented in TI Smart Gate
Drivers to help solve these challenges.

Table of Contents
1 Power MOSFET Theory and Operation.................................................................................................................................2
1.1 Basics.................................................................................................................................................................................2
1.2 Parameters.........................................................................................................................................................................3
1.3 Turnon Behavior.................................................................................................................................................................5
1.4 Simple Slew-Rate Calculation............................................................................................................................................5
1.4.1 Example.......................................................................................................................................................................5
1.5 Gate Drive Current.............................................................................................................................................................6
1.5.1 Peak Gate Drive Current.............................................................................................................................................6
1.5.2 Average Gate Drive Current........................................................................................................................................7
2 System Challenges and Smart Gate Drive Features...........................................................................................................8
2.1 Slew Rate Control For EMC and Power Loss Optimization...............................................................................................8
2.1.1 System Challenges......................................................................................................................................................8
2.1.2 I Implementation..................................................................................................................................................8
DRIVE
2.1.3 I Slew Rate Control.............................................................................................................................................9
2.1.4 EMI Optimization Example........................................................................................................................................12
2.1.5 Slew Time Control.....................................................................................................................................................14
2.2 Robust MOSFET Switching Through T State Machine............................................................................................14
2.2.1 MOSFET Handshaking..............................................................................................................................................15
2.2.2 MOSFET Gate-Fault Detection.................................................................................................................................16
2.2.3 dV/dt Turnon Prevention............................................................................................................................................17
2.3 System BOM Reduction...................................................................................................................................................18
2.4 Propagation Delay Optimization.......................................................................................................................................20
2.4.1 System Challenges....................................................................................................................................................20
2.4.2 Propagation Delay Reduction....................................................................................................................................21
3 Revision History...................................................................................................................................................................23

1 Power MOSFET Theory and Operation
1.1 Basics
The metal-oxide-semiconductor field-effect transistor, or MOSFET, is the most common transistor used in
present-day electronic-circuit design. The MOSFET has many properties that make it useful in a variety of
applications. These properties include scalability, low turnon current, high switching speeds, and high OFF-state
impedance. The MOSFET has been used in IC design (analog and digital), switching power applications, motor
control, load switches, and numerous other designs.
The MOSFET consists of four terminals which include the drain (D), source (S), gate (G), and body (B) as shown
in Figure 1-1. Often, the body terminal is short-circuited to the source terminal making it a three terminal device.
Figure 1-1. MOSFET Model
The MOSFET has three basic regions of operation that can be defined with a few simple equations. These
regions and their corresponding equations are listed as follows:
• Cutoff
V ≤ V (1)
GS th
where
– V = Voltage between the gate and source terminals of the MOSFET
GS
– V = MOSFET threshold voltage
th
• Linear
V > V , V ≤ V – V (2)
GS th DS GS th
– V = Voltage between the drain and source terminals of the MOSFET
DS
• Saturation
V > V , V > V – V (3)
GS th DS GS th
In the cutoff region, the MOSFET is OFF and no conduction occurs between the drain and the source. In the
linear region, the MOSFET is ON and the MOSFET behaves similar to a resistor controlled by the gate voltage
with respect to both the source and drain voltages. In the saturation region, the MOSFET is ON and behaves
similar to a current source controlled by the drain and gate-to-source voltages.
2 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

1.2 Parameters
Figure 1-2 shows a common MOSFET model highlighting the terminal-to-terminal capacitances and gate
resistance.
Drain
C
GD
R
G
Gate C
Source
Figure 1-2. MOSFET Circuit Model
While the C capacitance is fairly constant, the C and C capacitances vary heavily with the gate-to-drain
GS GD DS
voltage, drain-to-source voltage, and applied frequency. Table 1-1 lists some typical data sheet parameters of a
power-MOSFET. Review these values to understand how they affect the switching performance of the MOSFET.
Table 1-1. MOSFET Data Sheet Parameters (CSD18532Q5B)
Parameter Test Conditions Min Typ Max Unit
DYNAMIC CHARACTERISTICS
C Input capacitance 3900 5070 pF
iss
C Output capacitance V = 0 V, V = 30 V, ƒ = 1 MHz 470 611 pF
oss GS DS
C Reverse transfer capacitance 13 17 pF
rss
R Series gate resistance 1.2 2.4 Ω
Q Gate charge total (10 V) 44 58 nC
g
Q Gate charge gate-to-drain 6.9 nC
gd
V = 30 V, I = 25 A
DS D
Q Gate charge gate-to-source 10 nC
gs
Q Gate charge at V 6.3 nC
g(th) th
Q Output charge V = 30 V, V = 0 V 52 nC
oss DS GS
t Turnon delay time 5.8 ns
d(on)
t Rise time 7.2 ns
r
V = 30 V, V = 10 V, I = 25 A, R = 0 Ω
DS GS DS G
t Turnoff delay time 22 ns
d(off)
t Fall time 3.1 ns
f
The capacitors and resistor are defined as follows:
C A measure of the input capacitance between the gate and source terminals with the drain and source
ISS
shorted (C = C + C ).
ISS GS GD
C A measure of the output capacitance between the drain and source terminals with the gate and source
OSS
shorted (C = C + C ).
OSS DS GD
C The reverse transfer capacitance measured between the drain and gate terminals with the source
RSS
connected to ground (C = C ).
RSS GD
R The series resistance in line with the gate terminal.

To account for variation in the capacitance value with respect to voltage, a gate charge curve is typically used
to provide more meaningful information. Gate charge values relate to the charge stored within the inter-terminal
capacitances. Gate charge is more useful for system designers because it takes into account the changes in
capacitance with respect to voltage during a switching transient.
10
9
8
7
6
5
4
3
2
1
0
0 5 10 15 20 25 30 35 40 45
Qg Gate Charge (nC)
)V(
egatloV
ecruoS
ot
etaG
SGV
ID = 28A
VDS = 30V
G001
Figure 1-3. MOSFET Gate-Charge Curve
The gate charge parameters are defined as follows:
Q The total gate charge required to raise the gate-to-source voltage to the specified value (4.5 V and 10 V
are commonly used voltages).
Q The charge required from 0 V to the threshold voltage of the MOSFET. Current will start to flow from the
G(th)
drain to the source at the threshold voltage.
Q The charge required from 0 V to the Miller plateau voltage. At the plateau voltage the drain to source
voltage will start to slew.
Q The charge required to move through the Miller region. The Miller region derives its name from the
fact that the gate-to-source voltage stays relatively constant during this period as the reverse transfer
capacitance is charged. The MOSFET V slew occurs during this period as the MOSFET becomes
enhanced.
Note
It should be noted that both Q and in turn Q , while improved figures of merit for MOSFET
GD G
switching versus capacitance, still have a dependency on V and this should be factored when
utilizing these parameters.
4 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

1.3 Turnon Behavior
Based on the information provided in Section 1.2, a specific amount of charge is required to bias the gate to
a certain voltage. With this understanding, how the MOSFET behaves when certain voltages and currents are
applied to it starts to becomes clearer. Figure 1-4 shows the typical turnon response of a MOSFET.
Vth Miller Region
IDS
VGS
VMiller
VDS
QG(th) QGD
QGS
QG
Figure 1-4. MOSFET Turnon Response
The curve starts with the gate-to-source voltage increasing as a charge is supplied to the gate. When the
gate-to-source voltage reaches the MOSFET threshold voltage, current starts to flow from the drain to the
source. The gate-to-source voltage then stays fairly steady as the MOSFET moves through the Miller region.
During the Miller region, the drain-to-source voltage drops. After the Miller region, the gate continues to charge
until it reaches the final drive voltage.
1.4 Simple Slew-Rate Calculation
Unfortunately, calculating precise MOSFET V slew rates from parameters and equations requires specific
knowledge of the MOSFET, the board and package parasitics, and detailed information on the gate drive circuit.
These calculations go beyond the scope of this document. This document just focuses on simple first order
approximations that are compared to lab data.
Because the MOSFET V slew occurs during the Miller region, the Miller charge (Q ) and gate drive strength
DS GD
can be used to approximate the slew rate. The first assumption that should be made is that an ideal, or close to
ideal, constant-current source is being used for the MOSFET gate drive.
1.4.1 Example
Figure 1-5 shows a DRV8701 Smart Gate Driver driving a CSD18532Q5B at 24 V. The DRV8701 device is
configured for the 25-mA source-current setting. The waveform shows an approximately 312-ns slew rate which
matches closely with the first order approximation calculated using Equation 4.

Q
t GD
SLEW I
SOURCE
6.9nC
t 276ns
SLEW 25mA (4)
• Q = 6.9 nC
• I = 25 mA
V
Figure 1-5. Measured MOSFET Slew Rate
1.5 Gate Drive Current
Peak gate drive current and average gate drive current are two key parameters that should be examined when
designing a switching power-MOSFET system, such as a motor drive.
1.5.1 Peak Gate Drive Current
The peak gate drive current is the peak current that the gate driver can source or sink to the power MOSFET
gate during the turnon and turnoff periods. This value is primarily responsible for how fast the MOSFET can
slew.
1.5.1.1 Example
The DRV8701 supports a peak source current of 150 mA and a peak sink current of 300 mA. Using the example
from Section 1.4.1, a rise and fall time can be calculated using Equation 5 and Equation 6 (respectively).
RISE I
t 46ns
RISE 150mA (5)
• I = 150 mA
6 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

FALL I
Sink
t 23ns
FALL 300mA (6)
• I = 300 mA
SINK
1.5.2 Average Gate Drive Current
The average gate drive current is the average current required from the gate driver when switching the power
MOSFETs constantly. As previously described, the amount of charge to switch a power MOSFET is small (44
nC), but when switching the MOSFET in the kHz range, this charge will average into a constant current draw
from the gate driver supply.
Use Equation 7 to calculate the average gate drive current.
I = Q * # MOSFETs Switching * Switching Frequency (7)
AVG G
1.5.2.1 Example
I = 44 nC * 6 * 45 kHz = 11.88 mA (8)
AVG

2 System Challenges and Smart Gate Drive Features
This section describes the various challenges encountered in motor gate driver systems and the different
features implemented in TI Smart Gate Drivers to help solve these challenges.
2.1 Slew Rate Control For EMC and Power Loss Optimization
2.1.1 System Challenges
Adjustment and tuning of the MOSFET V slew rate is often the first and most critical challenge faced in motor
gate driver system design. The MOSFET slew rate directly impacts multiple performance parameters including
but not limited to switching power dissipation, radiated emissions, diode recovery and inductive voltage spikes,
and dV/dt parasitic turnon.
While oftentimes there are multiple methods to tackles these challenges (a topic outside the scope of this paper),
a common variable they all share is a direct dependency on slew rate. Typically the main tradeoff to consider is
that slower slew rates improve performance in radiated emissions, voltage spikes, and parasitic coupling, but will
increase power dissipation. Finding the proper balance for this tradeoff is a consideration for every motor system
designer.
For further understanding on slew rate and its various impacts to MOSFET performance, you can find further
reading in these papers.
• Fundamentals of MOSFET and IGBT Gate Driver Circuits
• Optimizing MOSFET Characteristics by Adjusting Gate Drive Amplitude
• Reduce buck-converter EMI and voltage stress by minimizing inductive parasitics
2.1.2 I Implementation
As described earlier, precisely controlling the current applied to the MOSFET gate lets the user make a
reasonable calculation for and adjust the MOSFET V slew rate. Texas Instruments Smart Gate Drivers
incorporate an adjustable gate drive current scheme in many of the motor gate drivers to easily control the
MOSFET slew rate. The adjustable gate drive current parameter is called I . This section describes how
I is commonly setup and implemented.
The most commonly implemented method is shown in Figure 2-1. In this method, a MOSFET predriver switch is
enabled between the gate and the voltage supply to manage the current directed to the external power MOSFET
gate.
Gate Drive (Internal) MOSFET (External) Gate Drive (Internal) MOSFET (External)
VGATE VGATE
VDRAIN VDRAIN
ON OFF
ISOURCE ISINK
OFF ON
Figure 2-1. Switch IDRIVE Method
To control the current to the gate of the external MOSFET during the V slew, the Smart Gate Driver takes
advantage of several MOSFET properties. If the switch (predriver MOSFET) can be operated in the saturation
region (Section 1.1), the current to the external MOSFET is limited to a fixed value. As the external MOSFET
moves through the Miller region, the gate-to-source voltage plateaus and stays relatively constant (Section 1.3).
Using these two properties, the Smart Gate Driver can make sure the correct voltage bias is applied to the gate
of the predriver switch and the switch is in the saturation region for the duration of the Miller charging period.
8 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

Because the gate of the external MOSFET appears as a short (AC voltage applied to a capacitance) the source
or sink current is limited to the saturation current of the switch.
By using multiple switches (shown in Figure 2-2), the Smart Gate Driver can alternate between different current
levels during normal operation.
Gate Drive (Internal) MOSFET (External)
VGATE VGATE VGATE VGATE
VDRAIN
Am
5.21
52
52
05
001
002
051
003

OFF ON OFF OFF
ISOURCE
OFF OFF OFF OFF
Figure 2-2. Multiple IDRIVE Settings
The second method to implement the IDRIVE feature uses current sources instead of switches. This
implementation occurs in applications that require very precise and consistent control of the external MOSFET
V slew rate across device, voltage, and temperature. While a switch in saturation can be sized appropriately
to act as a simple current source, a variation still exists across the previously described factors. To remove
this variation, a current source is used in place of the switch (see Figure 2-3). This architecture is especially
important in applications that are EMI sensitive and depend on characterizing the system at a specific slew rate.
Gate Drive (Internal) MOSFET (External) Gate Drive (Internal) MOSFET (External)
VGATE
VDRAIN VDRAIN
ISOURCE ISINK
Figure 2-3. Current Source IDRIVE Method
Similar to the switch method (Figure 2-2), multiple current sources can be used to provide adjustable gate drive
levels.
2.1.3 I Slew Rate Control
The I feature lets the V slew rate to be adjusted at any time without adding or removing external
DRIVE DS
components to the system. This capability lets a system designer fine tune the switching performance of the
MOSFET with regards to efficiency, radiated emissions performance, diode recovery inductive spikes, and dV/dt
turnon.
The persistence plot below shows the effect on the V slew rate from adjusting the I setting on a TI Smart
DS DRIVE
Gate Driver. The MOSFET V is slewing from 24 V to 0 V and the slew rate decreases as I is adjusted
across seven levels (10 mA, 20 mA, 30 mA, 40 mA, 50 mA, 60 mA, and 70 mA) of gate source current.

Figure 2-4. V Persistence Plot Across I Settings
The following figures show additional signals of the MOSFET while it is being enhanced. The current from the
Smart Gate Driver and the Miller region of the external MOSFET is clearly shown when the V slews.
V V
DS DS
I I
GATE GATE
GS GS
Figure 2-5. IDRIVE 30-mA Setting Figure 2-6. IDRIVE 60-mA Setting
As mentioned in Section 1.4, if a close-to-ideal current source and an accurate MOSFET Q parameter are
available, an approximate calculation for the V slew rate can be made. In the table below, the calculated V
slew rate is compared to the measured V slew rate for several I settings. In these calculations, assume
that the effects of the series gate resistance and additional non-idealities are minimal.
t = Q / I (9)
SLEW GD SOURCE
Table 2-1. I Slew-Rate Correlation
MOSFET Q Typical Calculated Slew Rate
GD I Setting (mA) Measured Slew Rate (ns) Approximate Error (%)
(nC) DRIVE (ns)
8 10 800 617 23
8 20 400 305 24
8 30 267 206 23
8 40 200 158 21
8 50 160 128 20
8 60 133 109 18
8 70 114 97 15
Although some error exists from the ideal calculation, these values let a system designer design for an
approximate slew rate and then finely tune the system during prototyping. The accuracy of the MOSFET Q
plays a large part in the accuracy of the calculation.
10 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

The following scope plots are for the different I values shown in the table above.
Figure 2-7. 10-mA I Figure 2-8. 20-mA I
DRIVE DRIVE
V GS V GS
Figure 2-9. 30-mA I Figure 2-10. 40-mA I
Figure 2-11. 50-mA I Figure 2-12. 60-mA I

Figure 2-13. 70-mA I
2.1.4 EMI Optimization Example
One of the leading contributors to electromagnetic interference, also known as EMI, is high frequency noise
from the switching of the power MOSFETs. Ideally the square-voltage waveforms generated by the power stage
are clean ground-to-supply signals, but this is seldom the case. Parasitics in the MOSFET package and PCB
layout can cause undershoot and overshoot voltages that can ring on the switching output. This parasitic ringing
can occur at frequencies much greater than 1 MHz, often directly in sensitive spectrum bands. Additionally, the
fundamental edge rate of the MOSFET switching can translate into noise in the high frequency spectrum.
While these parasitics can be tackled with layout improvements, snubbers, and design enhancements, often
the key knob to tune is the switching speed of the power MOSFETs. I provides an ideal way to tune the
motor gate drive system by providing simple control of the MOSFET slew rate through either a register write or
one resistor setting which lets system designers select the optimal setting that minimizes efficiency losses while
keeping an acceptable EMI level.
The data listed in Table 2-2 is an example from an actual application of the Smart Gate Driver I feature.
Table 2-2 shows the peak readings from a CISP 25 EMI engineering scan from 30 to 200 MHz with a Smart Gate
Driver at different I settings. As the I current setting is decreased, the peak scan readings are also
decreased.
Table 2-2. EMI Scan Results
I Setting (mA) 35-MHz Peak (dBµV/m) 65-MHz Peak (dBµV/m) 160-MHz Peak (dBµV/m)
10/20 5 <0 <0
20/40 12 <0 <0
50/100 12 <0 <0
200/400 28 12 2
250/500 30 15 5
Analyzing the output waveforms on an oscilloscope, it can be seen that at the higher I settings, a high-
frequency oscillation is induced on the switch-node. Figure 2-14 shows the high-level oscilloscope capture where
the oscillation is not obvious, but by zooming into the end of the rising edge (Figure 2-15) the 35-MHz signal that
is in the EMI scans is shown. By reducing the I , the oscillation is almost completely removed (Figure 2-16)
which gives an example of how the I architecture would be used in a real-world application. Figure 2-17
through Figure 2-21 show the source EMI scans with the entire 30- to 200-MHz spectrum.
12 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

Figure 2-14. 250/500-mA Switch-Node Waveform Figure 2-15. 250/500-mA Switch-Node Waveform
Zoom
Figure 2-16. 10/20-mA Switch-Node Waveform Zoom
Figure 2-17 through Figure 2-21 show the results from the radiated emissions engineering scans for each of the
IDRIVE settings.
Figure 2-17. 10/20-mA EMI Scan Figure 2-18. 20/40-mA EMI Scan

Figure 2-19. 50/100-mA EMI Scan Figure 2-20. 200/400-mA EMI Scan
Figure 2-21. 250/500-mA EMI Scan
2.1.5 Slew Time Control
On certain TI Smart Gate Drivers, such as DRV8718-Q1 and DRV8714-Q1, an advanced function is provided to
regulate the switch-node slew time with closed loop feedback. While open loop control methods described earlier
are often sufficient for MOSFET slew rate control, occasionally tighter control is required by the system.
This is due to the face that key MOSFET parameters can still vary due to manufacturing and system condition
variances. Parameters such as the MOSFET gate charge will vary from device to device and even on the same
device, changes in the system voltage and temperature will cause these parameters to shift during operation.
In order to solve this challenge a closed loop slew time control loop is required. Closed loop slew time control
works by monitoring the switch-node slew time and adjusting the I current setting continously during
operation of the driver in order to achieve a configured target setting. An example of this is shown in the diagram
below.
Process,
Temperature, Voltage
Target Error
IDRIVE
MOSFET MOSFET
Slew Time Controller Half-Bridge Slew Time
Slew Time
Detection
Figure 2-22. Slew Time Control Loop
2.2 Robust MOSFET Switching Through T State Machine
This sections describes some of the common challenges encountered in ensuring robust switching operation
and the different features implemented in TI Smart Gate Drivers to solve these challenges.
14 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

2.2.1 MOSFET Handshaking
In switching MOSFET systems, it is critical to avoid cross-conduction or "shoot-through" conditions to prevent
damaging the power MOSFETs or system supply. Cross conduction (shown in Figure 2-23) occurs when both
the high-side and low-side MOSFET are enabled at the same time. A low impedance path is introduced between
the power supply and ground. The path lets large current flow, potentially damaging the external MOSFETs or
power supply.
MOSFET Cross Conduction
M
ON
LOAD
ON
Figure 2-23. Cross Conduction Example
Cross conduction, or shoot-through, most commonly occurs when switching from the low-side to high-side (or
high-side to low-side). A delay occurs from when the input signal is received to when the external MOSFET is
off related to the internal propagation delay and slew rate of the MOSFET. If the opposite MOSFET is enabled
before this delay period expires, cross conduction can occur. A simple method to prevent this issue is to add a
period of timing before enabling the opposite MOSFET (shown in Figure 2-24). This period of time is called dead
time. Increased dead time decreases the efficiency of the motor driver because of diode conduction losses.
High-Side ON Dead Time Low-Side ON
VM VM VM
ON OFF OFF
Inductive Load Inductive Load Inductive Load
OFF OFF ON
Figure 2-24. Dead Time Example

TI Smart Gate Drivers, by monitoring the MOSFET V voltage and with an intelligent T state machine, can
GS DRIVE
provide an optimized amount of dead time for the switching MOSFET system. The V monitors make sure the
opposite MOSFET in the half-bridge is disabled before enabling the commanded MOSFET.
In addition to cross conduction protection (shoot-through), this method can provide system performance benefits
by reducing the period of diode conduction. Conduction losses of the MOSFET internal body diode are typically
worse than standard MOSFET conduction losses and decrease the overall system efficiency.
The T state machine incorporates internal handshaking when switching from the low-side to high-side (or
high-side to low-side) external MOSFET. The handshaking is designed to prevent the external MOSFETs from
going to a period of cross conduction, also known as shoot-through.
The internal handshaking uses V monitors of the external MOSFETs (Figure 2-25) to determine when one
MOSFET has been disabled and the other can be enabled. This handshaking lets the system insert an optimized
dead time into the system without the risk of cross conduction.
V Monitor
TDRIVE State
Machine
V Monitor
Figure 2-25. V Monitor Example
2.2.2 MOSFET Gate-Fault Detection
The T state machine lets the Smart Gate Driver detect fault conditions, such as a stuck low or stuck high
condition, on the gate of the external MOSFET. Gate faults could be caused by a defect or failure in the power
MOSFET gate oxide or a pin fault failure on the gate driver itself. By monitoring the voltage and managing the
current to the external power MOSFET, the Smart Gate Driver can detect and report when an abnormal event
(partial short, short circuit) has occurred on the MOSFET gate.
The T gate drive timer makes sure that under abnormal circumstances, such as a short on the MOSFET
gate or the inadvertent turning on of a MOSFET V clamp, the high peak current through the Smart Gate Driver
and MOSFET gate is limited to a fixed duration. Figure 2-26 shows this concept which is outlined as follows:
1. The Smart Gate Driver receives a command to enable the MOSFET gate.
2. A strong current source is then applied to the external MOSFET gate and the gate voltage starts to rise.
3. If the gate voltage has not increased after the t period (indicating a short circuit or overcurrent condition
on the MOSFET gate), the Smart Gate Driver signals a gate drive fault and the gate drive is disabled to
protect the external MOSFET and gate driver.
4. If a gate drive fault does not occur, the Smart Gate Driver enables a small current source after the T
period to keep the correct gate voltage and decrease internal current consumption.
16 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

tDRIVE tDRIVE
4
IGATE IGATE
VGATE 2 VGATE
1
VINPUT VINPUT
3
VFAULT VFAULT
Normal Operation Gate Drive Fault
Figure 2-26. TDRIVE Example
2.2.3 dV/dt Turnon Prevention
In addition to the cross conduction and gate fault protection features, the internal T state machine also
provides a mechanism for preventing dV/dt turnon.
A dV/dt turnon is a system issue that can occur when rapidly slewing the high-side MOSFET. When the switch
node rapidly slews from low to high (Figure 2-27), it can couple into the gate of the low-side MOSFET through
the parasitic gate-to-drain capacitance (C ). The coupling can raise the gate-to-source voltage of the low-side
MOSFET and enable the MOSFET if the voltage crosses the MOSFET threshold voltage (V ). If the low-side
th
MOSFET enables while the high-side MOSFET is on, cross conduction occurs.
OFF :(cid:3) ON
Gate
Driver
I
Figure 2-27. dV/dt Example
The T state machine works to prevent dV/dt turnon which can lead to cross conduction in the external
half-bridge. By enabling a strong pulldown on the low-side MOSFET during high-side V slew, the Smart Gate
Driver can provide a low-impedance path (Figure 2-28) for parasitic charge that couples through the parasitic
capacitance of the low-side MOSFET gate to drain capacitance (C ). This impedance path prevents a rise

in the gate-to-source voltage of the low-side MOSFET, which could potentially enable the MOSFET while it is
supposed to be off.
The TDRIVE state machine disables the strong pulldown after the switching period and moves to a weak
pulldown to decrease the chance of damage to the Smart Gate Driver or system in the scenario of a gate-to-
drain short of the external low-side MOSFET. By limiting the period of high current, the Smart Gate Driver can
prevent damage to itself and limit further damage to the system.
OFF :(cid:3) ON
PULLDOWN
Figure 2-28. TDRIVE Pulldown
2.3 System BOM Reduction
In addition to system flexibility, a Smart Gate Driver provides the ability to decrease the system BOM and
required board area through integration of key components of the motor gate drive system. A typical Smart Gate
Driver block diagram is shown in Figure 2-29.
18 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

VBAT
VVCP
Level GHx
Shifter
P
D
H_
S SHx
Digital Core
RPDSA_LS
DRAIN
VGS_CLAMP
Handshaking
+
VGS±
High-Side Gate Driver
VVCP
IHOLD IDRVP
ISTRONG IDRVN
±
VDRAIN
Overcurrent Detector
Handshaking
VGS±
Low-Side Gate Driver
VGVDD VGVDD
IHOLD IDRVP
Level GLx
Shifter ISTRONG IDRVN
P
D
S
_L
SLx
±
VSHx
GND
Overcurrent Detector
Figure 2-29. Smart Gate Driver Block Diagram
The first key point to note is the adjustable gate drive current sources for the turn on and turn off control of the
external MOSFET. These are adjustable in order to provide the typical slew rate control compensation that would
be done with external components as shown in Figure 2-30. Typically, the R and R resistors manually
SOURCE SINK
adjust the impedance between the gate driver and MOSFET gate. The diode lets the rise and fall V slew rates
to be individually adjusted. In a Smart Gate Driver, the adjustable gate drivers integrate this functionality.
Additionally, the internal pull down resistors replace typical external resistors to implement this functionality. The
R resistor makes sure that the MOSFET stays disabled even when the gate driver is inactive.
PULLDOWN
DD
Gate Drive
R SINK R PULLDOWN
Figure 2-30. Typical Gate Driver Slew Rate External Components

Lastly, integrated V and V comparators are provided for every gate driver output. These comparators
DS GS
manage the overcurrent detection for the external MOSFETs and detect potential gate drive faults. These
comparators and their various settings can be configured directly through the Smart Gate Driver SPI or hardwire
settings.
2.4 Propagation Delay Optimization
This sections describes some of the common challenges encountered in propgation delay optimization and the
different features implemented in TI Smart Gate Drivers to solve these challenges.
2.4.1 System Challenges
Another common challenge in motor gate driver system design is managing propogation delay and its impact
to the switching performance of the system. Propogation delay has two key parameters that impact overall
switching performance. The first is the overall delay from input to out and the second is the mismatch from turn
on to turn off. These two parameters will directly impact the minimum and maximum duty cycle, frequency range,
and duty cycle step resolution. Good switching performance is important to achieve optimal performance from
the motor in regards to speed and torque control.
While most gate drivers will specifiy their delay and mismatch parameters, they are only one part of the overall
input to output system. They other key part is the MOSFET switching delay itself. At high slew rates, the
MOSFET contribution to propagation delay and mismatch will often be minimal as compared to the driver, but at
slow slew rates, as often found in EMC sensitive systems, the MOSFET can be a main contributor.
Looking further at a typical MOSFET datasheet, we can begin to understand how the MOSFET parameters
impact the overall propagation delay. The capacitance parameters across voltage for the CSD18532Q5B are
shown below in Figure 2-31.
Figure 2-31. CSD18532Q5B Capacitance Curves
It is important to understand how these parameters change over voltage as it can be used to determine both the
Q and Q of the MOSFET. Oftentimes the Q and Q will be specified as an electrical characteristic of
GD GS GD GS
the MOSFET, but this is typically specificed at a given V which may not be representative of the actual system
conditions.
20 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

Vth Miller Region
IDS
VGS
VMiller
QG(th) QGD
QGS
QG
Figure 2-32. MOSFET Turnon Response
Refering to the equations below, we can determine a more accurate Q value as a function of C and V .
GD rss DS
This is integrated over V as this is dynamically changing during the Q charging as shown in Figure 2-32.
DS GD
We can then find a more accurate Q as a function of C and V . This is multiplied as V is relatively static
GS iss DS DS
during the Q charging as shown in Figure 2-32.
Figure 2-33. Charge Calculations
From Q and Q we can determine the MOSFET contribution to propagation delay and slew time.
GD GS
Figure 2-34. Timing Calculations
Using the CSD18532Q5B MOSFET example again, we can calcuate an approximate Q and Q . Assuming a
12 V power supply, Q is approximately 1.2 nC and Q is approximately 6.9 nC. Further assuming a 1us slew
time, we can calculate an I of 1.2 mA. From this, we can calcuate the approximate propagation delay
to be 5.75 us. In summary, we can see that Q >> Q and this typically holds true for most MOSFETs. We
GS GD
can also conclude that at slower slew rates the propagation delay time becomes a significant factor in switching
performance. If using a 20kHz PWM signal, a greater than 5 us propagation delay is already more than 10% of
the overall period.
2.4.2 Propagation Delay Reduction
On certain TI Smart Gate Drivers, such as DRV8718-Q1 and DRV8714-Q1, an advanced function is provided
to reduce the propagation delay for the MOSFET charge and discharge by using a dynamic current control

scheme. This scheme reduces propagation delay in order to support a wider PWM duty cycle range and also
to reduce thermal dissipation in the MOSFET as it moves through the residual charging region after the miller
charge region. This is shown in Figure 2-35 and Figure 2-36. The dyanmic current control has several regions
including a pre-charge current (I ) for reducing propagaton delay (t ), a drive current (I ) for
PRE_CHR DON/OFF DRVP/N
slew rate control, and a post-charge current (I ) for residual charging.
PST_CHR
QGD QGD
VGSHx VGSHx
tDRIVE
tDOFF
IPRE_CHR
IPST_CHR
IHOLD IHOLD
tPRE_DCHR tPST_DCHR
IDRVP
IDRVN
tPRE_CHR
tDON tPST_CHR
IGHx
ISTRONG
IGHx IPRE_DCHR
tDRIVE IPST_DCHR ISTRONG
VSHx_H VSHx_H
VSHx_L
VSHx_L
Figure 2-35. Dynamic Pre-Charge Profile Figure 2-36. Dynamic Post-Charge Profile
In order to implement robust dynamic current control, the Smart Gate Driver uses an adaptive scheme to learn
and predict when the switch node is going to enter the slewing region and preemptively adjust the gate drive
current. A predictive scheme is required as the typical delays from using direct feedback with comparators could
impact the slewing region itself.
In this adaptive scheme, the controller modulates the current for a proportion of the programed propagation
delay and then monitors at which point the switch-node slews. Based on whether the switch-node slews early
or late the pre-charge current is then adjusted up or down as shown in Figure 2-37. Every PWM cycle, the pre-
charge current (I ) is updated based on the switch-node (V ) slew timing until the desired propagation
PRE-CHR SH
delay (t ) is reached.
DON
Figure 2-37. Propagation Delay Adaptive Adjustment
22 Understanding Smart Gate Drive SLVA714D – JUNE 2015 – REVISED MARCH 2021

3 Revision History
NOTE: Page numbers for previous revisions may differ from page numbers in the current version.
Changes from Revision C (November 2018) to Revision D (March 2021) Page
• Updated abstract................................................................................................................................................1
• Combined Smart Gate Driver Features and System Benefits sections to improve organization........................8
• Added Slew Time Control section.....................................................................................................................14
• Added Propation Delay Optimization section...................................................................................................21
Changes from Revision B (January 2018) to Revision C (November 2018) Page
• Changed spec values in Table 1-1 .....................................................................................................................3
• Changed "6.9 nC" to "44 nC" in Section 1.5.2 ...................................................................................................7
Changes from Revision A (May 2016) to Revision B (January 2017) Page
• Updated terminology to Smart Gate Driver.........................................................................................................1