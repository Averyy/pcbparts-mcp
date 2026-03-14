---
source: "Diodes Inc AN1192 -- Understanding RVP Approaches"
url: "https://www.diodes.com/assets/App-Note-Files/AN1192_App-Note_Automotive-RVP.pdf?v=9"
format: "PDF 8pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 15345
---

Understanding the Different Approaches to Input Reverse Voltage
Protection (RVP)
Eduard Santa, Automotive BU, Diodes Incorporated
The vast majority of motor vehicles being manufactured today still include a low-voltage battery, commonly
either 12V or 24V. These batteries usually are easily accessible for vehicle owners to remove and replace them
when necessary. The problem is that batteries can be reinstalled incorrectly, resulting in reverse polarity
voltages that can damage sensitive vehicle electronics. This application note looks at the two most common
options for providing input reverse polarity protection, along with the advantages and disadvantages for each.
Figure 1: Voltage Polarities and Current Flows
In Figure 1, circuit A shows the system's normal operation, where the current flows from the positive side of the
supply through the protection device and the load towards the negative side. Circuit B illustrates a situation
where the polarity of the supply is reversed in comparison to circuit A. Here, the current flows in the opposite
direction but is stopped by the protection device.
Circuits C1 and C2 show the scenarios where the supply is connected as shown in circuit A, but the positive
side of the load is more positive than the supply (e.g., due to back EMF from a motor). In the case of C1, the
protection device allows current to flow back to the supply. In circuit C2, the protection device blocks the current
flow.
For a device to provide input reverse voltage protection, it must satisfy the conditions presented in circuits A
and B. Different protection methods can satisfy either circuit C1 or C2, selectable according to the requirements
of the specific application
Input reverse voltage protection can be implemented using a simple diode or a MOSFET (with some external
control) as the blocking component. We will take a closer look at these solutions and discuss their advantages
and disadvantages from an engineering point of view.
AN1192 – Rev 1 1 of 8 February 2025
Application Note www.diodes.com © Diodes Incorporated

Input Reverse Voltage Protection with a Blocking Diode
Inserting a blocking diode into the circuit is the simplest solution for input reverse voltage protection to
implement, as it consists of only one component.
Figure 2 shows a simple circuit of a diode connected in series with the load, which allows the current to flow
only in forward bias mode and block the current in reverse bias mode, as shown in Figure 1’s circuits A, B, and
C2.
Figure 2: Input Reverse Voltage Protection Using a Diode
The blocking diode can be any diode or rectifier of an appropriate current and reverse voltage rating. The power
dissipated in a forward-biased diode is:
Where P is the power dissipated, VF is the intrinsi𝑃𝑃c f=or𝑉𝑉w𝐹𝐹a∗rd𝐼𝐼 𝐿𝐿v𝐿𝐿o𝐿𝐿𝐿𝐿ltage drop of the diode, and ILoad is the load
current.
This power is lost as heat to the environment, therefore lowering the efficiency of the circuit and increasing the
device and board temperature. The load current is set by the application and so the only control over the power
dissipation is the selection of a lower VF diode.
It is common practice to choose a diode with low VF, such as a Schottky diode. However, Schottky diodes
exhibit high reverse current leakage at elevated temperatures, making them susceptible to thermal runaway.
Therefore, Schottky diodes may not perform effectively in high-temperature environments and high-power
applications.
Diodes Incorporated (Diodes) provides a variety of rectifiers suitable for industrial and automotive applications,
covering a wide range of load currents. Super Barrier Rectifiers (SBR®) and Trench Super Barrier Rectifiers
(SBRT) have a similarly low forward voltage characteristic to a Schottky diode, but the reverse leakage profile is
lower at elevated temperatures.
The graphs in Figure 3 show the forward and reverse bias characteristics of Diodes’ SBRT20U50SLPQ and a
comparable Schottky diode. Both are rated for the same maximum forward current (20A).
Figure 3: Schottky vs SBRT VF in Forward Polarity (Left) and Leakage Current in Reverse Polarity (Right)
AN1192 – Rev 1 2 of 8 February 2025
Application Note
www.diodes.com © 2025 Copyright Diodes Incorporated. All Rights Reserved.

Example 1 – Diode Input Reverse Voltage Protection Efficiency
This example assesses the efficiency of a Schottky diode versus an SBRT when powering a typical vehicle
infotainment system with 12V and 10A.
Schottky Diodes’ SBRT
V =12V, I =10A V =12V, I =10A
in in in in
P =V *I =120W P =V *I =120W
total in in total in in
V = 0.46V from graph @ I=10A V = 0.37V from graph @ I=10A
F F
P (=V *I =4.6W ) P (=V *I =3.7W )
loss F in loss F in
P -P P -P
total loss total loss
η= =96.16% η= =96.92%
P P
total total
The SBRT shows almost a 20% reduction in power dissipation compared to the Schottky, resulting in better
efficiency and thermal management.
The diode should be selected according to the maximum expected output current in the application, as shown
in Table 1. While the single-component input reverse voltage protection solution will have the smallest footprint
in low-power applications, for high currents, the diode needed is much larger. When conducting high currents,
the diode will also require more heatsinking copper area to ensure it stays within its operating temperature
range.
Footprints to Same Scale
Part Number SBR3A40SAQ SBR10U45SP5Q SBRT20U50SLPQ
Part Footprint Size (mm2) 13.52mm2 25.82mm2 31.67mm2
DC Blocking Voltage (V) 40 45 50
Max. Current @T =25°C (A) 3 10 20
A
V @T =25°C (V) 0.5 0.47 0.52
F A
Max Recommended DC
1.5 5 10
Current (A)
P @Rec Current (W) 0.75 2.35 3.7
D
Table 1: Comparison Between Different Diodes and their Footprints
Using MOSFETs for Input Reverse Voltage Protection
A MOSFET can be used as an ideal diode when placed in series with a load, such that its body diode is facing
current flow in forward polarity, as depicted in Figure 4. By turning the MOSFET fully ON in the forward polarity,
the power loss is equal to:
2
Where ILoad is the load current and RDS(ON) is 𝑃𝑃th 𝑙𝑙𝐿𝐿 e 𝑙𝑙 𝑙𝑙 in=tri𝐼𝐼n 𝐿𝐿 s 𝐿𝐿𝐿𝐿 ic 𝐿𝐿 O∗N𝑅𝑅 r 𝐷𝐷 e 𝐷𝐷 s (𝑂𝑂 is 𝑂𝑂 t ) a nce of the MOSFET.
The current flow is stopped by turning the MOSFET OFF in reverse polarity. This can be achieved with the use
of the right circuitry. Power dissipation can be adjusted through the selection of an adequate MOSFET.
P-channel MOSFETs (pMOS) can be used for input reverse voltage protection.
AN1192 – Rev 1 3 of 8 February 2025

Input Reverse Voltage Protection with Self-Biased MOSFET Circuit
A simple self-biased input reverse voltage protection circuit using a P-channel MOSFET (pMOS) is shown in
Figure 4.
pMOS
Figure 4: Self-Biasing Input Reverse Voltage Protection Circuit Using a pMOS in a High-Side Configuration
*In the circuit above, the Zener diode protects the MOSFET by ensuring that the gate voltage does not exceed
the maximum VGSS rating. However, the Zener’s clamping voltage must be high enough for the MOSFET to be
fully turned ON to minimize losses.
Under normal operation conditions, represented in Figure 1, circuit A, the MOSFET turns ON and allows the
forward current flow with losses determined by the RDS(ON). In the reverse polarity condition, represented in
Figure 1, circuit B, the MOSFET remains OFF, and its body diode prevents the reverse flow of current.
Referring to the conditions represented in Figure 1, circuit C1, the circuit shown in Figure 4 allows the reverse
current to flow back to the supply because the MOSFET remains biased ON.
Input Reverse Voltage Protection with Ideal Diode Controller
Ideal diode controllers are devices that control an external MOSFET to provide a high-side input reverse
voltage protection to the system. Unlike the self-biasing circuit presented in Figure 4, during normal operation
(Figure 1, circuit A), the ideal diode controller actively turns the MOSFET ON. It then turns the MOSFET OFF in
the input reverse polarity scenario (Figure 1, circuit B). Additionally, the ideal diode controller can control the
MOSFET to allow or block reverse current (Figure 1, circuits C1 and C2).
nMOS
AP74700AQ
Figure 5: High-Side Input Reverse Voltage Protection with an nMOS and AP74700AQ Ideal Diode Controller
The circuit shown in Figure 5 features the AP74700AQ ideal diode controller, which includes an internal charge
pump that generates an above input rail voltage to drive the gate of the N-channel MOSFET (nMOS). In forward
conduction (Figure 1, circuit A), the AP74700AQ monitors the voltage differential between the anode and
cathode pins (VDS) and modulates the gate of the nMOS to regulate the VDS voltage drop to 20mV.
If a reverse voltage greater than 10mV is detected across the nMOS, the gate pin is internally connected to the
anode pin, turning the nMOS OFF. This prevents reverse currents from flowing under the conditions shown in
Figure 1, circuits B and C2.
AN1192 – Rev 1 4 of 8 February 2025

Example 2 – MOSFET Input Reverse Voltage Protection Efficiency
Two MOSFETs of different polarity in the same PowerDI®3333 package were chosen for this example: a pMOS
(DMP4013LFGQ) and an nMOS (DMTH43M8LFGQ). These two devices are presently Diodes’ lowest RDS(ON)
40V MOSFETs available in this package.
An nMOS with the same RDS(ON) as a pMOS will have a die area of approximately one-third the size.
Consequently, the nMOS will be smaller and less expensive. The following example compares their
performance under the same conditions as the Schottky diode and SBRT in Example 1.
pMOS nMOS
V =12V, I =10A V =12V, I =10A
in in in in
P =V *I =120W P =V *I =120W
total in in total in in
R =13mΩ @V = 10V R =3mΩ @V =1 0V
DSON GS DS ON GS
P
(
=
)
I 2*R =1.3W P
(
=I
)
2*R =0.3W
loss in DS ON loss in DS ON
P -P ( ) P -P ( )
total loss total loss
η= =98.92% η= =99.75%
P P
total total
As shown in the calculations, the pMOS and the nMOS dissipate significantly less power than the diodes in
Example 1. The nMOS is the most efficient solution of all input reverse voltage protection methods outlined thus
far. Due to the lower power dissipation, the nMOS will have a much lower temperature increase than a diode or
a pMOS of a similar footprint. This, together with the fact that nMOS devices are usually smaller and cheaper
than pMOS, can further reduce the design cost.
In Table 2, small external components are selected for the self-biasing pMOS and the nMOS with the ideal
diode controller methods to show their difference in footprint size. All resistors are in 0402 package sizes, and
the Zener diode in the self-biasing example is in a DFN-1006 package. The charge pump capacitor for the
nMOS ideal diode controller is in a 0805 package to account for the higher voltage rating and capacitance,
which is required to drive the MOSFET.
Self-Biasing Circuit External Ideal Diode Controller +
Components for pMOS External Components for nMOS
Footprints to Same Scale
Footprint Size (mm2) 1.24 12.05
65V or nMOS VDS
Max. Voltage (V) MOSFET VDS
(whichever lowest)
Max. Current (A) MOSFET RDS(ON) nMOS RDS(ON) limited
High-Side Configuration for
Yes Yes
Automotive Applications
Minimum Forward Voltage RDS(ON) limited ~20mV
Reverse Current Protection No Yes
Table 2: MOSFET Biasing Method Footprint Size, Specifications and Features
The AP74700AQ ideal diode controller provides the charge pump functionality, allowing for use of the nMOS on
the high side, as well as controlling the FET to block reverse currents.
AN1192 – Rev 1 5 of 8 February 2025

Diodes Incorporated offers a wide variety of MOSFETs suitable for input reverse voltage protection solutions,
ranging from low currents to more than 40A.
Example solutions using 60V MOSFETs in SOT23, DFN-2020, PowerDI3333, and PowerDI5060 packages are
shown in Table 3.
Solution Footprint
Size (mm2)
pMOS
MOSFET DMPH6250SQ DMP6110SFDFQ DMP6023LFGQ DMP6018LPSQ
8.2 5.24 12.13 32.91
R 155 110 25 18
DS(ON)
Solution
Recommended Max. 1.5 1.75 4.25 10
P @Rec. Max.
D 0.35 0.34 0.45 1.8
Current (W)
MOSFET DMN6075SQ DMTH6016LFDFWQ DMTH6005LFGQ DMTH61M5SPSWQ
19.01 16.05 22.94 43.72
R 85 18 4.1 1.5
DS(ON)
Solution
Recommended Max. 2.2 5 20 40
P @Rec. Max.
D 0.41 0.45 1.64 2.4
Current (W)
Table 3: 60V pMOS & nMOS Comparison Table
The N-channel MOSFET provides the most efficient, power-dense solution and is enabled on the high side by
the ideal diode controller. These factors make the ideal diode controller and N-channel MOSFET a particularly
good choice for use in high-power automotive applications.
Selecting the right MOSFET for the application is key to ensure optimal system performance. See Application
Note AN1193 for a guide in selecting the right MOSFET for use with an ideal diode controller, such as the
AP74700AQ. However, the selection process shown in AN1193 is also valid for selecting a MOSFET for the
self-biasing pMOS circuit.
AN1192 – Rev 1 6 of 8 February 2025

Conclusion
This application note has shown different approaches to providing input reverse voltage protection. There is a
choice to be made, whether to allow or block reverse currents in a positive polarity situation. Table 4 shows a
comparison of three such solutions with similar current and voltage ratings and highlights their advantages and
disadvantages.
Ideal Diode Controller +
Solution Schottky or SBR pMOS + Zener
DMP4006SPSWQ + AP74700AQ +
Part Names SBRT20U50SLPQ
BZT52C15LPQ DMTH43M8LFGQ
Max. Reverse Voltage (V) 50 40* 40*
Max. Forward Current (A) 20 25* 29*
Power Dissipated @I=10A 3.7W 0.52W 0.3W
Circuit
Application circuit
Simplest Simple Simple
complexity
Footprint (same scale)
PCB Footprint area (mm2) 31.67 37.38 28.03
AN1192 – Rev 1 7 of 8 February 2025
serutaeF
Input Reverse
Voltage Protection (A
✔ ✔ ✔
& B)
Allows Reverse
❌ ❌
Current (C1) ✔
Blocks Reverse
❌
Current (C2) ✔ ✔
• Lowest power
dissipation
• Lowest cost at low • Lower power
• Regulates MOSFET
currents dissipation than diode
enhancement
Advantages • SBR – most robust • Simple sizing for
• Fast MOSFET turn-off
• Smallest footprint at different load currents
• MOSFET sizeable to
low currents • Allows reverse current
load current
• Blocks reverse currents
• Highest power
• Allows reverse current • Highest cost at small
dissipation
Disadvantages • More expensive than load currents
• Large temperature
just diode • Blocks reverse currents
increase
Table 4: Solution Comparison for Input Reverse Voltage Protection
*Note: The maximum voltage and current are limited by the VDS and RDS(ON), respectively, of the selected
MOSFET.
The optimum solution for a specific application will depend upon a variety of factors such as cost, solution size,
efficiency, power dissipation, complexity, and features required. Diodes Incorporated offers a large portfolio of
automotive compliant diodes, MOSFETs, and ideal diode controllers to build high-power density, reliable, and
effective input reverse voltage protection solutions.
