---
source: "Infineon AN2015-10 -- Transient Thermal Measurements and Thermal Equivalent Circuit Models"
url: "https://www.infineon.com/dgdl/Infineon-AN2015_10_Thermal_equivalent_circuit_models-AN-v01_00-EN.pdf?fileId=db3a30431a5c32f2011aa65358394dd2"
format: "PDF 11pp"
method: "pdfplumber"
extracted: 2026-03-02
chars: 17856
---

AN2015-10
Transient thermal measurements and thermal
equivalent circuit models
Replaces AN2008-03
About this document
Scope and purpose of AN2015-10
The basis of a power electronic design is the interaction of power losses of an IGBT module with the thermal
impedance of the power electronic system.
Using a precise model, the system can be designed for high-output current without exceeding the maximum
junction temperature limit, while remaining reliable in terms of power cycling.
To meet this requirement, Infineon has optimized the measurement method.
This application note AN2015-10 describes how to characterize the thermal properties of a power electronic
system and how to model it for application-oriented investigations.
Application note Please read the Important Notice and Warnings at the end of this document V 1.2
www.infineon.com 2020-04-14

Transient thermal measurements and thermal equivalent circuit
models
TTaitbllee_ ocfo cnotninteunetds
Table of contents
About this document ....................................................................................................................... 1
1 Determination of thermal impedance curves .................................................................... 3
1.1 Principle of measurement – R /Z basics .............................................................................................. 3
th th
1.2 Challenges and optimization of R /Z measurement ........................................................................... 4
2 Thermal equivalent circuit models .................................................................................. 6
2.1 Introduction ............................................................................................................................................. 6
2.2 Taking thermal paste into account......................................................................................................... 8
2.3 Merging the semiconductor module and the heat sink into a system model....................................... 8
2.3.1 Thermal system model based on continued-fraction model ........................................................... 8
2.3.2 Thermal-system model based on partial-fraction model ................................................................ 9
3 References ................................................................................................................... 10
Revision history............................................................................................................................. 10
Application note 2 V 1.2
2020-04-14

DTeittleer_mcoinnattiinoun eodf thermal impedance curves
1 Determination of thermal impedance curves
1.1 Principle of measurement – R /Z basics
The basic principle of measurement is described in IEC 60747-9 Ed. 2.0 (6.3.13.1) [1].The approach of determining thermal
impedance is shown in Figure 1. A constant power P is fed into the IGBT module by a current flow, so that a stationary
L
junction temperature T is reached after a transient period. After turning off the power, the cooling down of the module is
j
recorded.
Thermal resistance R is the difference between two temperatures T and T at t=0, divided by P. For calculating time-
th(x-y) x0 y0 L
dependent thermal impedance Z (t), the recorded temperature curves need to be vertically mirrored, and shifted to the
th(x-y)
origin of the coordinate system. Then Z (t) is calculated by dividing the difference of T(t) and T(t) by P.
th(x-y) x y L
∆𝑇
𝑥𝑦0
𝑅 =
𝑡ℎ(𝑥−𝑦) 𝑃
𝐿
∆𝑇 (𝑡)
𝑥𝑦
𝑍 (𝑡) =
𝑡ℎ(𝑥−𝑦) 𝑃
𝐿
Figure 1 Principle approach of thermal impedance measurement
For determining the junction temperature in the cooling phase, a defined measurement current (I approx. 1/1000 I ) is
ref nom
fed to the module, and the resulting saturation or forward voltage is recorded. The junction temperature T(t) can be
determined from the measured forward voltage with the aid of a calibration curve T = f(V /V @ I ). Its reverse curve V /V
j CE F ref CE F
= f(T @ I ) (see Figure 2) is recorded earlier by means of external, homogenous heating of the tested module.
j ref
Application note 3 V 1.2

Figure 2 Example of a calibration curve used to determine the junction temperature by measuring the
saturation voltage at a defined measuring current
The case temperatures T and the heat-sink temperatures T are determined by means of thermocouples. The
c h
thermocouples are thermally isolated except at the top. This is where they come into contact with the base plate of the
module and the heat sink, respectively (Figure 3, left). In both cases, the projected thermocouple axis is located in the
center of each chip (Figure 3, right).
Figure 3 Determination of case temperature T and heat-sink temperature T and example for the
c h
projected sensor positions based on a 3.3 kV 140x190 mm2 module
1.2 Challenges and optimization of R /Z measurement
Precise measurements are required for determining T and T exactly at the time the cooling phase begins. It should be
j c
pointed out that directly after turn-off, the smallest thermal time constants lead to big changes in the T , so this is a very
vj
important time period to measure. On the other hand, oscillations also occur at this time, which make the measurement
very difficult. The parasitic effects lead to transient disturbances in the measured signals.
In order to overcome the hurdles mentioned above, a modified measurement system (see Figure 4) is being used.
Application note 4 V 1.2

Figure 4 Optimized analog/digital measurement equipment
Owing to advancements in technologies and products, Infineon has reviewed the R /Z measurement method and
simulation approach. R /Z measurements have been modified accordingly. By using the new measurement equipment, it
is now possible to determine more precise R /Z values of IGBT modules. This is depicted in a simplified manner in Figure
5. The difference between T and T at t=0 is larger for the modified measurement system “B” in comparison to the former
j c
measurement system “A”. As seen in Figure 1, this temperature difference is proportional to the thermal resistance R , and
th
also affects the thermal impedance Z .
The modified measurement system is able to determine precise data even at an early stage.
Due to the thermomechanical behavior of modules, the thermal impedance between case and heatsink (Z , but also Z )
thCH thJH
is temperature dependent. Modules are optimized to have best thermal heat transfer to the heat sink for high operating
temperatures at which the semiconductors are typically best used. Therefore, data sheet conditions reflect high
temperature operation only. If the modules run at low case temperatures, the users themselves should measure whether
the specific thermal impedance has increased noticeably.
Figure 5 Comparison of former measurement system (A) and modified one (B)
Application note 5 V 1.2

RTeitfleer_ecnocnest i&n uAebdou t this document
2 Thermal equivalent circuit models
2.1 Introduction
The thermal behavior of semiconductor components can be described using various equivalent circuit models:
Figure 6 Continued-fraction circuit, also known as Cauer model, T-model or ladder network
The continued-fraction circuit (Figure 6) reflects the real, physical setup of the semiconductor based on thermal
capacitances with intermediary thermal resistances. The model can be set up where the material characteristics of the
individual layers are known, whereby, however, the correct mapping of the thermal spreading on the individual layers is
problematic. The individual RC elements can be assigned to the individual layers of the module (chip, chip solder, substrate,
substrate solder, and base plate). The network nodes therefore allow access to the internal temperatures of the layer
sequence.
Figure 7 Partial-fraction circuit, also known as the Foster model or Pi model
In contrast to the continued-fraction circuit, the individual RC elements of the partial-fraction circuit no longer represent
the layer sequence. The network nodes do not have any physical significance. This illustration is used in datasheets, as the
coefficients can be easily extracted from a measured cooling curve of the module. Furthermore, they can be used to make
analytical calculations.
The thermal impedance of a partial fraction model can be expressed as:
t
Z
(t)=∑n
i=1
r
i
(1−e − τi) (1)
whereas,
τ =r c (2)
i i i
As an example in Figure 8, the module datasheet Z (j-c) of an IGBT is specified based on a partial-fraction model. The
corresponding coefficients are provided in tabular form as resistance (r) and time constant () pairs.
Application note 6 V 1.2

Figure 8 Example of how thermal impedance is specified in a datasheet based on a partial-fraction
model
With specific switching and forward losses P (t), and assuming a known case temperature T(t), the junction temperature
L c
T(t) can be determined as follows:
T(t)=P (t)∗Ż (t)+T(t) (3)
j L th(j−c) c
Figure 9 Partial-fraction model for determining T(t) for given semiconductor losses P (t) under the
j L
assumption of a known case temperature T(t)
c
Application note 7 V 1.2

The simplified assumption of a constant case and heat-sink temperature is not always given in practice, as the load duration
is not negligibly short compared to the time constants of the heat sink. For considering non-stationary operating conditions,
either T(t) should be measured, or the IGBT model should be linked to a heat-sink model.
2.2 Taking thermal paste into account
In both models, the use of R instead of the usually unknown Z for thermal paste, is conceivable for a worst-case
assessment. Neglecting the capacitances in the partial fraction model, a fed-in power step causes an immediate
temperature drop across the whole resistor chain. The junction temperature and thermal paste temperature both rise
immediately to a constant value, which does not represent the physical behavior of the system. There are two ways to
bypass this problem:
 If the Z of the heat sink is to be determined by measurement, the case temperature T should be used instead of the
th c
heat-sink temperature T . In this case, the thermal paste is included in the heat-sink measurement and is no longer to
h
be considered separately.
 If an IGBT setup is available, where the fed-in power loss P(t) is known, the case temperature T(t) can be measured
L c
directly, and included in the calculation in accordance with Figure 9.
2.3 Merging the semiconductor module and the heat sink into a system
model
The user often will avoid the expense of measurements, and will create a thermal system model from the existing IGBT/diode
model and the desired heat-sink data. Both the continued-fraction and the partial-fraction model can depict the respective
transfer functions “junction-to-case” of the IGBT and “heat sink-to-ambient” of the heat sink. If the IGBT and heat-sink
models are to be combined, the question arises as to which of the two models should be used, especially if the IGBT and
heat sink have been characterized separately from each other.
2.3.1 Thermal system model based on continued-fraction model
The continued-fraction model and the linking of individual models of this type visualize the physical concept of individual
layers which are sequentially heating one another. The heat flow – the current in the model from Figure 10 – reaches, and
therefore heats, the heat sink with a certain delay. A continued fraction model can be achieved by simulation or
transformation from a measured partial-fraction model.
Figure 10 Merging continued-fraction models to a system model
It is common to set up a model by material analysis and FEM simulation of the individual layers of the entire setup. But this
is only possible if specific heat-sink data is used, as the heat sink has a reverse effect on the thermal spreading within the
semiconductor module, and therefore on the time response and the resulting Z (j-c) of the module. If the heat sink in the
application deviates from the simulated heat sink, the model will not take this into consideration.
Usually the partial-fraction model is used in datasheets, as this is the result of a measurement-related analysis, with the
Z (j-c) being provided advantageously as a closed solution. A mathematical transformation of a partial-fraction model into
a continued-fraction model is possible. This transformation is not unambiguous. Various thermal resistance (R ) and
thermal capacitance (C ) value pairs are possible. Also the individual R and C elements, as well as the node points of the
th th th
Application note 8 V 1.2

new continued-fraction model, do not have any physical significance after the transformation. A merging of continued-
fraction models that are not coordinated with one another can therefore result in many different errors.
2.3.2 Thermal-system model based on partial-fraction model
The semiconductor module, partial-fraction model, as it appears in the datasheet, is based on a measurement in
combination with a specific heat sink. While an air-cooled heat sink results in a wide spread of heat flow in the module, and
therefore leads to better, i.e. lower R (j-c) in the measurement, the limited heat spreading in a water-cooled heat sink results
in a comparably higher R (j-c) value in the measurement. By using a water-cooling bar for the characterization, the partial-
fraction model provided in the Infineon datasheets represents a comparably unfavorable operation mode, which means an
appraisal on the safe side, i.e. in favor of the module.
Due to the connection of networks in series (Figure 11), the power fed into the junction – in the equivalent circuit represented
by the current – reaches the heat sink without delay. Therefore, already at an early stage, the increase of junction
temperature depends on the type of heat sink model.
Figure 11 Merging partial-fraction models to a system model
However, with air-cooled systems, the time constants of the heat sinks range from around 10 s to several 100 s, which is far
above the value for the IGBT itself with only approximately 1 s. In this case the calculated heat-sink temperature rise
distorts the IGBT temperature only to a very small degree. On the other hand, water-cooled systems are critical, since they
have comparably low thermal capacitances, i.e. correspondingly low time constants. For “very fast” water-cooled heat
sinks, i.e. systems with direct water cooling of the semiconductor module base plate, a Z measurement of the complete
system of semiconductor module plus heat sink should be performed.
Because of the reverse effect on the thermal spreading in the module, it is not possible to link the semiconductor module
and the heat sink in a fault-free way, neither in the continued-fraction nor in the partial-fraction model. A way to overcome
this issue is to model or measure the Z of the semiconductor module and the heat sink interdependently. A complete fault-
free thermal system model can only be obtained by measuring the thermal impedance Z (j-a), i.e. with simultaneous
measurement of the complete thermal path - from junction via semiconductor module, thermal grease, heatsink to ambient.
This delivers a partial-fraction model of the entire system, with which the junction temperature can be calculated fault-free.
Application note 9 V 1.2

RTeitfleer_ecnocnest i&n uReedvi sion history
3 References
[1] IEC 60747-9 Ed. 2.0 (6.3.13.1) ‘Semiconductor devices - Discrete devices - Part 9: Insulated-gate bipolar transistors
(IGBTs) [3]
Revision history
Document Date of release Description of changes
version
Rev 1.0 2015-12-08 First release
Rev 1.1 2018-10-16 Horizontal mirrored -> vertically mirrored on page 3
Formula (3) on page 7
V 1.2 2020-04-14 Thermomechanical behavior of modules on page 5
Application note 10 V 1.2

Trademarks
All referenced product or service names and trademarks are the property of their respective owners.
IMPORTANT NOTICE
The information contained in this application note is For further information on the product, technology,
E dition 2020-04-14 given as a hint for the implementation of the product delivery terms and conditions and prices please
o nly and shall in no event be regarded as a contact your nearest Infineon Technologies office
P ublished by description or warranty of a certain functionality, (www.infineon.com).
condition or quality of the product. Before
I n fineon Technologies AG
implementation of the product, the recipient of this
8 1 726 Munich, Germany application note must verify any function and other WARNINGS
technical information given herein in the real Due to technical requirements products may contain
application. Infineon Technologies hereby disclaims dangerous substances. For information on the types
any and all warranties and liabilities of any kind in question please contact your nearest Infineon
© 2020 Infineon Technologies AG.
(including without limitation warranties of non- Technologies office.
AA lNl 2R0ig1h5-t1s0 Roewsneervrse.d . infringement of intellectual property rights of any
third party) with respect to any and all information Except as otherwise explicitly approved by Infineon
Do you have a question about this given in this application note. Technologies in a written document signed by
authorized representatives of Infineon
document?
The data contained in this document is exclusively Technologies, Infineon Technologies’ products may
E mail: erratum@infineon.com intended for technically trained staff. It is the not be used in any applications where a failure of the
D ocument reference
to
es p
ev
o
a
n
l
s
u
ib
at
il
e
it y
t h
f c
su
b
m
ili
y
’ s
f
e c
hn
ic
p
d
m
s p
re
x
q
ed
u e
s u
so
r e
in
ry
.
A N2015-10 intended application and the completeness of the
product information given in this document with
respect to such application.