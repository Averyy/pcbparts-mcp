---
source: "ST AN5241 -- ESD Protection Fundamentals"
url: "https://www.st.com/resource/en/application_note/an5241-esd-protection-fundamentals-stmicroelectronics.pdf"
format: "PDF 19pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 25554
---

Application note
Fundamentals of ESD protection at system level
Introduction
Electrostatic discharge (ESD) are usually known as a sensation of electronic shock when walking across a carpet or opening a
car door. The ESD definition given by https://www.esda.org is “the rapid, spontaneous transfer of electrostatic charge induced
by a high electrostatic field”.
The most common way to charge electrically a material is to rub two materials and to separate them. The electron transfer
between both materials, called triboelectric charge, generates an electrostatic field. The physics related to triboelectric
generation is complex and driven by several parameters: surface roughness, temperature, strain, and other material properties.
It is not very predictable and only broad generalizations can be made. The Table 1 reports typical voltages of static generation
with various means of generation and relative humidity.
Table 1. Examples of static generation - typical voltage levels
Means of generation 10-25% relative humidity 65-90% relative humidity
Walking across carpet 35,000 V 1,500 V
Walking across vinyl tile 12,000 V 250 V
Worker at a bench 6,000 V 100 V
Poly Bag Picked up from Bench 20,000 V 1,200 V
Chair with Urethane Foam 18,000 V 1,500 V
ESD voltages are higher than typical electronics circuits voltages (few volts usually) and electronics circuits are not natively
adapted to support them.
Specific strategies are employed to limit effect of ESD. They are based on ESD control plan development and on ESD control
procedures and materials. These solutions are very efficient on a closed environment where electronics product are exposed to
ESD events (electronics assembly plant, as example). These strategies do not eradicate ESD events but they put under control
events and validate the level compatibilities with sensitive electronics devices. When facing to uncontrolled area (i.e. the real
world), an electronics system without any ESD specific protection, will be faced to catastrophic field failure rate directly induced
by the ESD.

Impact on electronic devices
1 Impact on electronic devices
ESD is critical for electronic devices. As example, integrated circuits (ICs) can be affected at silicon level by ESD.
Three major failure mechanisms are illustrated on Figure 1 :
• Oxide punch-trough: the over-voltage induce by ESD exceed the dielectric breakdown strength. The oxide
layer breakdown can generate a short circuit. Thinner the oxide is and more sensitive to ESD is.
• Junction damage or burn-out: the energy of ESD destroys the silicon p-n junction in short-circuit.
• Metallization / resistor fusing: the high current injection on metallization / resistor during the ESD event
melts metal by joule heating. The results is an open circuit.
These impacts can be combined. As example, a junction damage can lead to metal tracks fuse due to its
consecutive high current.
Figure 1. ESD induced damages (from left to right: oxide punch through, junction burnout and
metallization fusing)
Listed ESD damages are catastrophic (short or open circuits). ESD events can also generate less severe defaults
with as example a leakage current increases without functionality lost. But latent failures can also appear
consecutively to ESD event.
The shrinkage, induced by technological evolutions, increases the IC sensitivity to ESD. Indeed, physical IC
parameter sensitive to ESD are more and more constraint over technological nodes (oxide thicknesses reduction,
metal track widths and thicknesses reduction, …). This is why ESD is becoming more and more critical for
electronics hardware.

Protection against ESD
2 Protection against ESD
At circuit level, human body model (ANSI/ESDA/JEDEC JS-001) describes ESD waveform and test method
approximating the discharge from the fingertip of a typical human being. It is intensively used to guaranty the
robustness of circuits during manufacturing processes. All IOs (inputs/ouputs) of ICs must be protected.
The most common granted value is 2 kV but lower values can be observed for circuits manufactured with
advanced technologies. Indeed, on-chip ESD protections are negatively impacted by scaling effect of
technological node evolution. The dimension reduction trends to increase the sensitivity (oxide breakdown, metal
trace fuse …) while the energy to dissipate is kept constant.
At system level, only IOs of ICs exposed to ESD from external world need to be protected (connectors, touch
sensors, buttons and antenna tracks as example).
IEC 61000-4-2 standard describes test methods to perform ESD. It also defines ranges of test levels as reported
on Table 2:
• In contact discharge, when the test generator is held in contact with the device under test (DUT)
• In air discharge, in which the charged electrode of the test generator is brought close to the DUT, and the
discharge actuated by a spark to the DUT
The level correspond to a functional validation.
Table 2. IEC 61000-4-2 test levels
Contact discharge Air discharge
Level Test voltage Level Test voltage
1 2 kV 1 2 kV
2 4 kV 2 4 kV
3 6 kV 3 8 kV
4 8 kV 4 15 kV
System regulations require various levels, as example, “EN 55024, Information technology equipment - Immunity
characteristics - Limits and methods of measurement” imposes 4 kV contact discharge and 8 kV air discharge.
However, the most common level used on consumer applications is level 4 (8 kV contact – 15 kV air). Sometimes,
more severe discharge level can be used to insure robustness based on use-case information (as example with
hoovers that mechanically generate ESD).
HBM and IEC 61000-4-2 generator simplified schematics are presented on Figure 2.
Figure 2. HBM (left) and IEC 61000-4-2 (right) generator simplified schematics
Basically, they correspond to a capacitor discharge thought a serial resistor that limits the current.

Protection against ESD
The Figure 3 shows the current as function of time of IEC61000-4-2 8 kV ESD and HBM 2 kV ESD, the most
common ESD protection levels.
Figure 3. Current waveforms of IEC61000-4-2 8 kV and HBM 2 kV
The IEC 61000-4-2 8 kV waveform is based on an equation detailed on the standard. It is noticeable that a first
current peak has very short rise time (less than 1ns) and a high current value. This first current peak require a
faster ESD protection for IEC61000-4-2 8 kV than for HBM 2 kV waveform. The second peak of IEC61000-4-2
8kV is much more energetic with maximum current of 18 A than HBM 2 kV with a maximum current of 1.3 A.
These curves illustrate the severity of the 8 kV IEC 61000-4-2 system standard compared to 2 kV HBM
component standard.
However, both standards require ESD protections:
• HBM is related to electronics components on ESD controlled environments for manufacturing. ICs are
protected with integrated on-chip ESD protections on all IOs.
• IEC61000-4-2 is related to electronics system on end-user environment. Only exposed IOs of ICs need to
be protected, thanks to external ESD protections added in parallel to integrated on-chip HBM protections.

External ESD protections
3 External ESD protections
On one hand, an ESD protection must grant system integrity when ESD event is applied. It clamps the ESD
voltage at a value lower than IO destruction value. It is its main feature.
On the other hand, the protection must be transparent when it does not work. Indeed, the ESD protection must
have the less impact as possible on the system performances when system is working (consumption increase,
bandwidth reduction as example).
The selection of an external ESD protection must take into account both constraints.
External ESD protections can be grouped into two families:
• Standard series with a Zener like I/V curve (ESDV5-1BF4, as example)
• Snap-back series with a snap back effect on I/V curve (ESDZV5-1BF4, as example)
Electrical characteristics are presented on Figure 4.
Figure 4. ESD external protection electrical characteristics (left: standard, right: snap-back)
I
PP
R
D
V
I RM
V CL V BR V RM I R R M V V CL V Trig V H V
I I RM V RM V BR V CL I RM
R
PP I
PP
Main common parameters are:
• V : maximal working voltage with associated maximum leakage current (I )
RM rm
• C : line capacitance usually given at 0 V with 30 mV of oscillation voltage at 1 MHz. This value generally
LINE
decreases with applied voltage. It also generally decreases with oscillation frequency.
• I : peak pulse current correspond to maximal current for a given waveform. A clamping voltage (V ) is
PP cl
also associated to obtain P (peak pulse power). Usually, V presented on datasheet is measured with
PP cl
IEC 61000-4-2 8 kV ESD discharge. If several current waveforms are reported, there is no
correspondence between V values.
CL
• R : dynamics resistance, it is obtained with the clamping voltage response when a 100 ns width square
current waveform short pulse is applied.
Standard ESD protection is active at breakdown voltage (V ) usually define at 1 mA DC.
BR
Snap-back ESD protection turns-on at trigger voltage (V ). The protection voltage has a snap-back effect in
Trig
order to lower the clamping voltage. The holding voltage (V ) is the lowest voltage when the protection has
H
turned-on and as consequence a lower voltage induce the turn-off of the protection.
The lower is the holding voltage, the better is clamping voltage with constant R .

Product selection
4 Product selection
4.1 When protection is off: transparency
When protection is off, it must be as transparent as possible.
The first parameter to ensure a good transparency is to determine minimum and maximum voltage signal to be
protected. The V of the ESD protection must be higher than the signal voltage amplitude. If the signal is
rm
negative and positive, the protection must be bi-directional to avoid rectifier phenomenon. If the signal to be
protected is only positive, an unidirectional protection is preferred especially for negative ESD clamping voltage. A
bidirectional protection can also work.
A too high leakage current can, not only, affect the system overall consumption but also, it can change a data line
voltage through a pull-up resistor. Usually, it is below 1 µA at V (as example, ESDZV5-1BF4 and HSP053-4M5
I is 100 nA maximum). This value is much lower than IC consumption, i.e., few order of magnitude lower than
ICs lowest supply current in run mode. Pull-up resistors are usually between few 1 kΩ to few 10 kΩ. With 100 kΩ
pull up resistor, a leakage current of 100 nA induces a line voltage shift of 10 mV. It is acceptable compared to
nominal voltage of standard ICs (3.3 V or 5 V, as example).
The protection line capacitance and the bandwidth are key factors for high speed lines (digital or RF lines).
HSP053-4M5 product has a very low capacitance (0.35 pF at 2.5 GHz).
It presents a -3 dB cut-off frequency of 18 GHz. Analog signal frequency must be lower than this value, for
example, the attenuation at 2.4 GHz is lower than 0.5 dB.
For digital signals, eyes diagram of thru lines with and without protections are reported according the mask given
on the standard. Figure 5 shows measurements of eye diagram for USB 3.1 Gen2 at 10.0 Gbps per channel.
Figure 5. Eye diagram - USB 3.1 Gen2 mask at 10.0 Gbps per channel (Type-C connector, reference cable,
EQ with DC = 6 dB and DFE).Eye diagram without HSP053-4M5 on left and with HSP053-4M5 on right.
The comparison of both images illustrates the negligible impact of HSP053-4M5 on data transmission for USB 3.1
at 10.0 Gbps per channel. This figure of merit shows the protection ability to be transparent from a transmission
point of view. The standard conditions (voltages, rise and fall times …) are then validated with the protection.

When protection is off: transparency
Another numerical parameter is the impedance on a matched line measured with time domain reflectometry
(TDR). Figure 6 presents the mismatch induced by the HSP053-4M5 placed in a 100 Ω line.
Figure 6. TDR measurement induced by induced by the HSP053-4M5 placed in a 100 Ω line with 200 ps
rise time
This figure of merit shows the ability of the protection system to stay transparent from a reflection point of view.
The main driver is protection capacitance but line impedance modification done for protection footprint
implementation is also validated.

When protection is on: efficiency
4.2 When protection is on: efficiency
In order to be close to the worse application conditions, IEC61000-4-2 level 4 (+/-8kV) contact discharge are
applied to the component. The temporal response of ESDZV5-1BF4 is presented on Figure 7.
Figure 7. ESDZV5-1BF4 ESD response to IEC 61000-4-2 (+8 kV contact discharge)
5 V/div
1 Peak clampingvoltage
2 Clampingvoltage at 30 ns
22 V 3 Clampingvoltage at 60 ns
1 4 Clampingvoltage at 100 ns
7 V
6 V
2 3 5 V
4
20 ns/div
A noticeable value is the 30 ns voltage. This is the usual definition of a clamping voltage of an ESD protection.
This key parameter reveals the protection efficiency against an ESD event, indeed, it corresponds to the ability of
the ESD protection to limit the voltage when an ESD event is present and then to protect the IC placed behind the
ESD protection.
The clamping voltage can also be studied using the transmission line pulse (TLP) method. It is a high voltage 50
Ω cable discharge on the ESD protection. The incident current / voltage waveform parameters are described on
ANSI/ESD STM5.5.1: 100 ns square waveform with 10 ns or less rise time (see Figure 8 left as example). The
resulting current / voltage are averages on the 70 ns - 90 ns windows to measure a stabilized current / voltage
before fall (see Figure 8).
Figure 8. ESDZV5-1BF4 TLP (16 A – 100 ns width – 10 ns rise time) time responses (current on left and
voltage on right)

When protection is on: efficiency
TLP time responses with various currents enable the construction of a clamping voltage as a function of the
current (see Figure 9).
Figure 9. TLP response of ESD051-1BF4 (left) and ESDZV5-1BF4 (right)
• V = V + I x R for standard ESD protection (ESD051-1BF4 as example)
cl br pp d
• V = V + I x R for snap-back ESD protection (ESDZV5-1BF4 as example)
cl h pp d
The clamping voltage obtained at 30 ns with a IEC61000-4-2 8 kV discharge corresponds to 16 A TLP response.
Indeed, the current flowing at 30 ns with IEC61000-4-2 8 kV discharge is 16 A (see Figure 3).
ESD overvoltages are always higher than the trigger voltage of snap-back protection, as consequence, snap-back
ESD protections always turn on when an ESD occurs.

Product integration on system
5 Product integration on system
Once the external ESD protection selected in respect to transparency and efficiency, the system integration can
be checked.
5.1 ESD system safe operating area
The ESD system SOA (Safe Operating Area) is critical for snap-back ESD protections. The ESD system SOA
method ensures a return to normal operation after an ESD event (i.e. avoid latch-up).
Latch-up of the external protection is possible when a continuous voltage V is present on the protected line
dd
(power supply or level ‘1’ as example). Left schematic of Figure 10 shows the voltage, V , the serial resistor R ,
dd s
and the external ESD protection D.
Several R values can be consider, as example:
s
• Power supply with a very low R value (usually less than 0.1 Ω)
• Push-pull output at level ‘1’ with low R value (usually few Ω)
• Pull-up resistor with high R value (usually few 10 kΩ)
Figure 10. Schematic representation of protected schematic (left) and graphical representation of the
circuit load line and ESD system SOA (right)
ESD system SOA area is above source load line (see Figure 10 right), on this area the ESD protection is latch-up
free.

ESD system safe operating area
Reporting source load line and ESD protection I/V curve on same graphic (see Figure 11), two cases are
possible:
• Figure 11, (a), (b), (c) and (d) curves cross the source load line only at V . There is only a single solution
that leads to normal state with negligible current on ESD protection.
• Figure 11, (e) curve cross the source load line at V and also at V. Then, two solutions are possible.
dd l
When the protection has not triggered, system voltage is V and leakage current of ESD protection is
negligible. It is the normal state. When, the ESD protection has been triggered by an ESD event, system is
latched at V with a current I. This state is not suitable because a line reset is then required to return to
l l
normal state.
Figure 11. Protected circuit load line with various ESD protection I/V curves
Figure 11 illustrates several cases :
• Curve (a): a non-snap-back ESD protection is latch-up free
• Curve (b): a snap-back ESD protection with a V > V prevents the latch-up phenomena
h dd max
• Curve (c): a snap-back ESD protection with a I > I prevents the latch-up phenomena
hold ss max
• Curve (d): a snap-back ESD protection with a couple (V , I ) located in the safe operating area
hold hold
prevents the latch-up phenomena
• Curve (e): outside the SOA, the ESD protection stay latched after an ESD event
Slope of source load line is a key. As example, deep snap back ESD protections as SCR (i.e. ESD protection with
holding voltage lower than V ) cannot be used with power supply. Nevertheless, these protections are mandatory
for high speed data line that require low clamping voltage. On that case, minimum pull-up resistor and maximum
V must be taken into account to select protection on ESD system SOA (as example, HDMI lines: V =
dd dd_max
3.47 V and R = 45 Ω).
s_min

System efficient ESD design
5.2 System efficient ESD design
System efficient ESD design (SEED) is a method that grants a good co-working of external ESD protection and
ESD protection inside the IC to be protected.
TLP response of external ESD protection has been presented previously. Same kind of curve can be obtain with
IC internal ESD protection. Internal ESD protection is mainly dedicated to HBM and as consequence is much less
robust than external ESD protection.
While reporting TLP responses of internal ESD protection and external ESD protection on same graphic (see
Figure 12), 3 noticeable cases can be reported:
• External ESD protection triggered and failed before internal ESD protection has triggered (curve a). The
system is well protected and the system ESD robustness correspond to the external ESD protection
robustness.
• Internal and external ESD protections have triggered before failure of one protection. The current is shared
between 2 protections. A specific case is noticeable when the failure of internal ESD protection and
external ESD protection (curve b) are reached at same voltage. Then, the maximum current allowed before
destruction is the sum of maximum current of internal and external ESD protection. In other words, the
system robustness is the sum the robustness of both protection. It is an optimal co-working for internal and
external ESD protection.
• Internal ESD protection triggered and failed before external ESD protection has triggered (curve c). The
external ESD protection is not efficient alone to grant the system robustness.
Figure 12. Internal and external ESD protection TLP curves
To solve the last case weakness on ESD system robustness, a serial resistor is placed between the IO to be
protected and the external ESD protection (see Figure 13) to obtain an Z-R-Z structure.
Figure 13. Z-R-Z structure (left) and associated TLP curves (right)

System efficient ESD design
TLP curves are then (Figure 13 right):
• IC internal ESD protection (curve 1)
• External ESD protection (curve c), that does not grant ESD system robustness alone as explained on
previous example
• External ESD protection with the serial resistor R (curve d), the resistor lower the slope compared to the
curve without resistor
The voltage drop between Figure 13 (1) and (2) is only due to the serial resistor R .
The equivalent system seen by the TLP on system input is two protections in parallel:
• The external ESD protection
• The internal ESD protection with the serial resistor R
Thanks to a good selection of R , it is possible to obtain the optimal co-working as presented above when both
protections fails at same time.
The resistor value must be acceptable from a transparency point of view (as example, do not modify too much
line impedance and as consequence the eye diagram).
SEED method allows a prediction and an optimization of the ESD system robustness. Unfortunately, while ESD
external protection datasheets present TLP curves, IOs of IC exposed to external ESD events (GPIOs of
microcontroller, specific IOs of ASIC, connector ports, antenna ports ...) usually do not present TLP curves. Then,
the SEED method can be experimentally adapted with a serial resistor increase to maximize iteratively the system
ESD robustness. Usually, few Ohms are enough with an external ESD protection V selected close to the
maximal system voltage.

Conclusion
6 Conclusion
Technological evolutions inexorably increase electronics devices ESD sensitivity. Silicon manufacturers grant IC
compatibility with assembly plant but IOs exposed to the real world need external ESD protections.
An external ESD protection selection must complies with two mains items:
• The transparency: the external ESD protection must not impact system performances or, at least, impacts
them the less as possible.
• The efficiency: the external ESD protection must protect against system level ESD event.
• Both items have been discussed and impacts on external ESD protection parameters have been detailed.
Then, the external ESD protection integration on the system is also presented because it also affects
product selection.
ESD related choices must be done at early design phase to avoid any complicated fixes on the validation phase
or dramatics solutions when done on the field.

Revision history
Table 3. Document revision history
Date Version Changes
07-Nov-2018 1 Initial release.
12-Oct-2023 2 Updated Section 4.2 When protection is on: efficiency.

Contents
Contents
1 Impact on electronic devices.............................2
2 Protection against ESD ...............................3
3 External ESD protections ..............................5
4 Product selection..................................6
4.1 When protection is off: transparency ........................6
4.2 When protection is on: efficiency..........................8
5 Product integration on system...........................10
5.1 ESD system safe operating area..........................10
5.2 System efficient ESD design ...........................12
6 Conclusion.....................................14
Revision history ....................................15

List of tables
List of tables
Table 1. Examples of static generation - typical voltage levels . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1
Table 2. IEC 61000-4-2 test levels . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
Table 3. Document revision history. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15

List of figures
List of figures
Figure 1. ESD induced damages (from left to right: oxide punch through, junction burnout and metallization fusing) . . . . . 2
Figure 2. HBM (left) and IEC 61000-4-2 (right) generator simplified schematics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
Figure 3. Current waveforms of IEC61000-4-2 8 kV and HBM 2 kV. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
Figure 4. ESD external protection electrical characteristics (left: standard, right: snap-back). . . . . . . . . . . . . . . . . . . . . . 5
Figure 5. Eye diagram - USB 3.1 Gen2 mask at 10.0 Gbps per channel (Type-C connector, reference cable, EQ with DC =
6 dB and DFE).Eye diagram without HSP053-4M5 on left and with HSP053-4M5 on right.. . . . . . . . . . . . . . . . 6
Figure 6. TDR measurement induced by induced by the HSP053-4M5 placed in a 100 Ω line with 200 ps rise time. . . . . . 7
Figure 7. ESDZV5-1BF4 ESD response to IEC 61000-4-2 (+8 kV contact discharge) . . . . . . . . . . . . . . . . . . . . . . . . . . 8
Figure 8. ESDZV5-1BF4 TLP (16 A – 100 ns width – 10 ns rise time) time responses (current on left and voltage on right) 8
Figure 9. TLP response of ESD051-1BF4 (left) and ESDZV5-1BF4 (right). . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
Figure 10. Schematic representation of protected schematic (left) and graphical representation of the circuit load line and
ESD system SOA (right) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
Figure 11. Protected circuit load line with various ESD protection I/V curves . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
Figure 12. Internal and external ESD protection TLP curves . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
Figure 13. Z-R-Z structure (left) and associated TLP curves (right). . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
