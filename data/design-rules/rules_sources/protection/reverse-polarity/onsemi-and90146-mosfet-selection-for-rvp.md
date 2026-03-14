---
source: "onsemi AND90146 -- MOSFET Selection for RVP"
url: "https://www.onsemi.com/download/application-notes/pdf/and90146-d.pdf"
format: "PDF 11pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 28877
---

APPLICATION NOTE
www.onsemi.com
MOSFET Selection for Reverse Polarity Protection
AND90146/D
OVERVIEW These test pulses come with different negative
When the vehicle’s battery is damaged and needs andpositive voltage levels to stress the DUT to see if it can
replacement the probability of connecting the new battery withstand. For example, Pulse 3b is shown in Figure 1
inreverse is high. Since many electronic control units togive an idea about the type of pulses that are defined in
(ECU) in the vehicle are connected to the vehicle’s battery, thestandard, each pulse will have its own parameters as
such an event could lead to numerous ECU failures. inTable1. Pulse 3b simulates the switching noise in the real
Additionally, automotive standards like ISO (International application, such as relay and switch contact bouncing
Organization for Standardization) defines the testing which can produce a short burst of high frequency pulses.
methods, voltage levels, limits for electromagnetic emission AND8228/D talks in more details about voltage transients
for electrical and electronic devices to ensure the safe and and testing methods.
rugged operation of the system. One such standard related
to reverse polarity protection (RPP) is ISO 7637−2:2011
0.9 US
which replicates the various voltage scenarios like in the real
US
application and the system needs to withstand such voltages
to showcase the robustness against failures. This made 0.1 US
reverse polarity protection a crucial building block that is tr
required by all automotive vehicle manufacturers for any td
battery connected ECU/system.
V
This application note will first address the ISO pulses that t1
are commonly used to replicate the voltage transients that
could appear in real applications. It will then give details
about several protection techniques that could be used,
US
before helping to guide the reader to select an external
N−Channel MOSFET, that will provide RPP and help
UA
reduce the power losses of the system. Finally, a list 0
ofrecommended N−Channel MOSFETs to be used along
t4 t5 t
with an ideal diode controller, based on the battery current
Figure 1. Test Pulse 3b
will be provided.
ISO PULSES
ISO 7637−2:2011 is an international standard which
specifies test methods and procedures to ensure Table 1. PARAMETERS OF TEST PULSE 3b
thecompatibility to conducted electrical transients
Parameters Nominal 12 V System Nominal 24 V System
ofequipment installed on passenger cars and commercial
vehicles fitted with 12 V or 24 V electrical systems. Refer
US +75 V to +150 V +150 V to +300 V
to ISO 7637−2:2011 for detailed information. Ri 50 (cid:2)
Under this standard there are several types of test pulses td 150 ns ±45 ns
that are defined to test the device. Below are few of the test
pulses.
tr 5 ns ±1.5 ns
− Pulse1: Transients due to supply disconnection t1 100 (cid:3)s
ofinductive loads. t4 10 ms
− Pulse2a: Transients due to sudden interruption
t5 90 ms
ofcurrents in a device connected in parallel with the DUT
(Device Under Test), due to the inductance of the wiring
harness.
− Pulse3a&3b: Transients which occur as a result
ofswitching processes. The characteristics of these
transients are influenced by distributed capacitance
andinductance of the wiring harness.
© Semiconductor Components Industries, LLC, 2022 1 Publication Order Number:
July, 2023 − Rev. 1 AND90146/D

REVERSE POLARITY PROTECTION only conduct current when the correct polarity is applied to
TECHNIQUES its terminals (i.e., forward biased). The forward voltage
In the following section the three most common drop, V for a standard diode is around 0.7 V, while for a
F
techniques used for reverse polarity protection are Schottky diode it can be as low as 0.3 V. As a result, most
discussed. applications use a Schottky diode, to reduce system losses.
Diode
The simplest way to protect a system from a reverse
battery is by using a diode. As shown in Figure 2, a diode will
Current Flow Reverse Current
Diode Conductive Diode Nonconductive
+ +
+ −
VBAT Load VBAT Load
− +
− −
GND GND
Figure 2. Reverse Polarity Protection using a Diode
Figure3 shows the typical voltage drop of the increases from 0.35 V to 0.40 V (15% increase) at a junction
NRVBSS24NT3G Schottky diode. If the diode current temperature T of 25°C.
J
(I ) increases from 0.5 A to 1.0 A (100% increase), V
DIODE F
Figure 3. Typical Forward Voltage of NRVBSS24NT3G Schottky Diode
MOSFET battery is properly connected, the intrinsic body diode is
An alternative to a diode is a MOSFET. When a MOSFET conductive till the MOSFET’s channel is turned ON. To turn
is conductive, the voltage drop between the drain−source ON a P−Channel MOSFET, the gate voltage needs to be
V DS is dependent on the drain−source resistance R DS,ON and lower than the source voltage by at least the threshold
the drain−source current I D : V DS = R DS,ON * I D. Compared voltage V T . When the battery is reversely connected, the
to a Schottky diode the voltage drop is generally much body diode is reversed biased, gate and source have the same
lower. voltage thus turning OFF the P−Channel MOSFET. An
additional Zener diode is used to clamp the gate of the
P−Channel MOSFET
P−Channel MOSFET and protect it in the case of a too high
As all MOSFETs, a P−Channel MOSFET has an intrinsic
voltage.
body diode between the source and the drain. When the
2

D S D S
P−ChannelMOSFET P−ChannelMOSFET
G G
+ −
Figure 4. Reverse Polarity Protection using a P−Channel MOSFET
N−Channel MOSFET V by at least V . Hence a dedicated driver is used to drive
BAT T
It is also possible to use an N−Channel MOSFET for the gate voltage of the N−Channel MOSFET higher than the
reverse polarity protection. When the battery is properly source voltage, thus turning ON the N−Channel MOSFET.
connected (source is connected to V ), to turn ON the When the battery is reverse connected, the body diode is
BAT
MOSFET, the gate−source voltage has to be higher than the reversed biased (anode voltage is lower than cathode
threshold voltage (V > V ). Given that the source is voltage) and the driver is disabled (source and gate are
GS TH
connected to V , the gate voltage needs to be higher than shorted), turning the N−Channel MOSFET OFF.
BAT
S D S D
N−Channel MOSFET N−Channel MOSFET
+ Driver − Driver
Figure 5. Reverse Polarity Protection using a N−Channel MOSFET
Comparison of Reverse Polarity Protection Techniques
Table 2. COMPARISON BETWEEN DIFFERENT
Table 2 summarizes the advantages and disadvantages of PROTECTION TECHNIQUES
the different reverse polarity protection techniques. It is
Advantages Disadvantages
worth mentioning that P−Channel MOSFET operation
depends upon the mobility of holes, while an N−Channel Schottky − Low cost − Higher power
MOSFET depends upon the mobility of electrons. Knowing Diode − Simple dissipation
− Higher voltage drop
that the mobility of holes is almost 2.5 times lower than the
mobility of electrons, for the same drain current, a MOSFET − Flexibility (various − High cost for low RDS,ON
P−Channel MOSFET will have a bigger die size and, by MOSFETs with − Higher total solution cost
various RDS,ON) (need of additional
implication, a higher cost compared to that of an N−Channel − Higher power charge pump / controller)
MOSFET to achieve the same on−resistance. This makes dissipation − Higher complexity
N−Channel MOSFETs preferable compared to P−Channel − Lower operating (i.e., gate drive and
voltage drop protection)
MOSFETs in such applications.
3

MOSFET SELECTION NCV68061 IDEAL DIODE CONTROLLER
There are various parameters to consider when selecting The combination of NCV68061 and an external
an N−Channel MOSFET for reverse polarity protection. N−Channel MOSFET replicates an ideal diode which acts
• Maximum Breakdown Voltage of the MOSFET like a perfect conductor when forward biased voltage (anode
V voltage is higher than cathode) is applied and like a perfect
DS,MAX
♦ For 12 V board net (vehicle) V = 40V is insulator when the reverse biased voltage (anode voltage is
preferred lower than cathode) is applied. The NCV68061 is a reverse
♦ For 24 V board net (truck) V = 60 V is polarity protection and ideal diode N−Channel MOSFET
preferred controller intended as a lower loss and lower forward
• voltage replacement for diodes.
Maximum Operating Junction Temperature T
J,MAX
♦ For vehicle and truck applications, 175°C is The main function of the NCV68061 is to control the
ON/OFF state of an external N−Channel MOSFET
recommended given the harsh environment
• according to the source to drain differential voltage polarity.
Gate Level
Depending on the drain pin connection the device can be
♦ Logic Level is preferred over standard level since
configured in two different application modes. With the
they have a lower R for the same gate−source
DS,ON drain pin is connected to the load the application is in ideal
voltage V
GS diode mode, whereas with the drain pin connected to ground
•
Package the NCV68061 is merely in reverse polarity protection
♦ 3.30 ×3.30mm (i.e. LFPAK33/WDFN8/(cid:3)8FL) and mode. In both modes, the controller provides a typical gate
5.00 × 6.00 mm (i.e., SO8−FL/LFPAK56) packages voltage of 11.4 V to external N−Channel MOSFET. Hence
with exposed pad for optimized power dissipation in all the calculations of following sections, R
DS,ON
@ 10 V
are commonly used V
GS
has been used.
Total Gate Charge Q NCV68061 has undergone ISO 7637−2:2011 tests to
G,TOT
♦ Turning ON a MOSFET happens in 3 phases demonstrate the robustness of the device to withstand
− When the gate voltage V GS rises to the plateau voltage stress. The results are shown in the NCV68061
voltage V , charges are mainly used to charge datasheet.
GP
the input capacitance C .
ISS
Ideal Diode Application
− When V GS is at the plateau voltage V GP , charges
Figure 6 shows how the NCV68061 is used in the ideal
are mainly used to charge the reverse transfer
diode configuration. In this configuration, the input voltage
capacitance (gate−to−drain capacitance) C .
RSS
is not allowed to discharge the bulk capacitance C . This
− When V GS rises from V GP to driver supply configuration has two modes: bulk
voltage V , the charges are used to further
GDR − Conduction Mode: Prior to entering the conduction mode,
enhance the channel.
the source voltage is lower than the drain voltage, and
♦ Lower the Q , lesser the gate voltage and
G,TOT both the charge pump and the N−Channel MOSFET are
current needed to turn ON the MOSFET (i.e., faster
disabled. As the source voltage becomes greater than the
turn ON) and vice versa
drain voltage, the forward current flows through the body
♦ More information about MOSFET Gate−Charge
diode of the N−Channel MOSFET. Once this forward
could be found in the following onsemi application
voltage drop exceeds the source to drain gate charge
note.
voltage threshold level (typ. 140 mV), the charge pump is
− https://www.onsemi.com/pub/Collateral/
turned ON and the N−Channel MOSFET becomes fully
AND9083−D.PDF
conductive.
Drain−Source Resistance R
DS,ON − Reverse Current Blocking Mode: When the source
♦ R DS,ON plays a role to limit the power dissipation in voltage becomes less than the drain voltage, reverse
the device. The higher the R DS,ON for a given load current initially flows through the conductive channel of
current, the higher is the power dissipation. Higher the N−Channel MOSFET. This current creates a voltage
losses lead to the increase in T J of the MOSFET. drop across the conductive channel of the N−Channel
Hence it is important to choose the right device with MOSFET which is proportional to its R . When this
required R DS,ON to have optimal performance. voltage drops below the source to drain gate discharge
♦ In the following sections, MOSFETs for thermal voltage threshold (typ. −10mV), the charge pump is
evaluation are chosen in such a way that their disabled, and the external N−Channel MOSFET is turned
R DS,ON will keep power dissipation around 500 mW OFF by an internal P−Channel MOSFET of the controller.
of losses.
4

Battery Protected Battery Battery Protected Battery
S D S D
N−Channel N−Channel
MOSFET MOSFET
S G D S G D
CS
NCV68061
Cbulk CS
NCV68061
Cbulk
EN GND EN GND
Figure 6. NCV68061 Ideal Diode Application Figure 7. NCV68061 Reverse Polarity Protection
Application
Reverse Polarity Protection
By connecting the drain pin to the GND potential, as TEST SETUP
shown in Figure 7, the NCV68061 does not allow a falling A dedicated test board for NCV68061 is used to determine
input voltage to discharge the output below GND potential the power dissipation and thermal performance of the
but does allow the output to follow any positive input various MOSFETs in 3 × 3 and 5 × 6 packages with different
voltage above the under−voltage lockout (UVLO) R DS,ON to help to understand the MOSFET selection for the
threshold. This means that the bulk capacitance C will be ideal diode controller considering various load currents.
bulk
discharged by a falling input voltage.
Schematic
When the source voltage is above the UVLO threshold
Figure 8 shows the schematic of the test board. It is
(typ. 3.3 V), the source/drain and UVLO comparators
designed in such a way that MOSFETs in SO−8FL/LFPAK4
enable the charge pump to provide gate−source voltage to
and (cid:3)8FL/LFPAK33 can be tested. Each MOSFET circuit
the external N−Channel MOSFET, which is fully
has a jumper to enable/disable the NCV68061 to make sure
conductive. When the source voltage is below the UVLO
that only one controller is active at a time. A 3.3 V LDO
threshold (typ. 3.2 V), the charge pump and the N−Channel
NCV4294 is used to supply the enable pin EN of the
MOSFET are disabled, and any load current flows through
controller. The controller will control the N−Channel
the body diode of the N−Channel MOSFET.
MOSFET to act like an ideal diode and also to block reverse
current.
Figure 8. Schematic of NCV68061 Test Board
5

Layout several layers helps to reduce the losses and to have better
The board is a 4−layer printed circuit board (PCB). The thermal performance of the board. Inner2 layer has traces for
input and output currents have been distributed across top, gate signals and for enable signal. Bottom layer is fully
inner1 and inner2 layers. Distributing the current across dedicated for the GND plane.
Figure 9. Top Layer Figure 10. Inner1 Layer
Figure 11. Inner2 Layer Figure 12. Bottom Layer
6

THERMAL MEASUREMENTS
Table 3. MOSFETS UNDER EVALUATION
Battery Maximum RDS,ON @ 10V Maximum Losses
Current Part Number Package VGS (m(cid:2)) PD (mW) R(cid:3)JA ((cid:2)C/W) TCASE ((cid:2)C)
6 A NVTFS5C478NLWFTAG (cid:3)8FL 14.0 504.0 51.0 47.3
NVMFS5C468NLAFT1G SO−8FL 10.3 370.8 43.0 40.1
8A NVTFS5C466NLWFTAG (cid:3)8FL 7.3 467.2 48.0 47.4
NVMFS5C466NLWFT1G SO−8FL 7.3 467.2 43.0 45.3
10A NVTYS005N04CLTWG LFPAK8 4.8 480.0 47.7 52.8
NVMYS4D6N04CLTWG LFPAK4 4.5 450.0 40.0 47.5
Table 3 shows the N−Channel MOSFETs used for thermal performance of the MOSFETs with different output currents
evaluation. MOSFETs with various R
are chosen to (6 A, 8 A and 10 A). MOSFETs in SO−8FL/LFPAK4 (5 ×6)
limit the power dissipation to be around 500mW. and (cid:3)8FL/LFPAK8 (3 × 3) are used for evaluation. Two
Measurements of the MOSFETs top case temperature are measurements are made for each load current, one with 5 ×6
made at 24°C ambient temperature to evaluate the thermal and another with 3 × 3 package.
Figure 13. 6 A with (cid:4)8FL Figure 14. 6 A with SO−8FL
Part Number NVTFS5C478NLWFTAG Part Number NVMFS5C468NLAFT1G
Max. RDS(ON) @ 10 V VGS 14.0 m(cid:2) Max. RDS(ON) @ 10 V VGS 10.3 m(cid:2)
Max. Temperature 47.3°C Max. Temperature 40.1°C
Figure 15. 8 A with (cid:4)8FL Figure 16. 8 A with SO−8FL
Part Number NVTFS5C466NLWFTAG Part Number NVMFS5C466NLWFT1G
Max. RDS(ON) @ 10 V VGS 7.3 m(cid:2) Max. RDS(ON) @ 10 V VGS 7.3 m(cid:2)
Max. Temperature 47.4°C Max. Temperature 45.3°C
7

Figure 17. 10 A with LFPAK8 Figure 18. 10 A with LFPAK4
Part Number NVTYS005N04CLTWG Part Number NVMYS4D6N04CLTWG
Max. RDS(ON) @ 10 V VGS 4.8 m(cid:2) Max. RDS(ON) @ 10 V VGS 4.5 m(cid:2)
Max. Temperature 52.8°C Max. Temperature 45.3°C
With the measured top case temperature from thermal T = Junction temperature of the MOSFET
measurements and calculated power dissipation, the T = Temperature of the package on top measured by
CASE
junction temperature T J can be calculated using equation 1. the thermal camera
T J (cid:2)T CASE (cid:3)P D (cid:4)R(cid:4)JT (eq. 1) P D = Power dissipation of the MOSFET
R(cid:4)JT =Thermal resistance between top case and
junction of the MOSFET
Figure 19. Equivalent Thermal Resistance of the MOSFET
The value of R(cid:4)JT is not fixed, it depends on thermal junction to the top of the MOSFET and one can assume that
boundary conditions such as PCB layout, cooling system of the temperature difference between T
and T
is not
the MOSFET (like exposed pad) and other parameters, significant. For the sake of the application note, the
therefore it is not provided in the datasheet. R(cid:4)JT is a small assumption is that R(cid:4)JT is 1°C/W to determine T
.
number with < 1°C/W, as most of the heat will flow from NOTE: 1°C/W is a very conservative assumption for
junction to the PCB via the exposed pad on the bottom side 3×3 and 5 × 6 packages. Other packages will
of the package. Therefore, not much heat flows from the have a different thermal resistance.
8

Estimation of the Junction Temperature T Theoretical Calculation for T
J J
In the following section, the measured T CASE and actual Theoretical calculations based on specification of the
power dissipation in the MOSFET are used to calculate T J . datasheet are used to determine T J . Assuming losses of
In the next step a theoretical calculation based on 500mW, the equation 3 is used to determine T
of the device.
specifications of the datasheets is done and the result is T (cid:8)T
compared to the calculations made using measured data to P (cid:2) J A
see if both theoretical and practical calculations of T
are D R(cid:4)JA (eq. 3)
matching. All calculations consider MOSFET • Junction temperature of the MOSFET T
NVTFS5C478NLWFTAG in (cid:3)8FL (3 × 3) package. •
Ambient temperature at which the MOSFET will be
Estimation for T J Using Measured T CASE operated T A = 24.0°C
The below calculations are done to estimate T J using Power dissipation of the MOSFET P D = 500.0 mW
values obtained from measurements. •
Thermal resistance between junction and ambient of the
Load current I LOAD = I D = 6.0 A MOSFET R(cid:4)JA = 51.0°C/W (value from the datasheet)
I
T
n
e
p
m
u
t
v
r
o
a
l
u
g
f
i
n
=
1
ca
2
s
.0
T = 47.3°C (obtained
T
(cid:2)P
D
(cid:4)R(cid:4)JA (cid:3)T
A
from the thermal measurement) (cid:2)500.0mW(cid:4)51.0°C(cid:7)W(cid:3)24.0°C(cid:2)49.5°C
• Max. on−resistance R
@ 10.0 V V
GS
= 14.0 m(cid:2) (eq. 4)
• R(cid:4)JT = 1.0°C/W (assumption for 3 × 3 and 5 × 6 This gives 125.5°C headroom for T J,MAX of 175.0°C for
packages) NVTFS5C478NLWFTAG.
The difference between estimated and theoretically
P (cid:2)I2 (cid:4)R
D D DS,ON calculated T ’s is minor at 1.7°C (49.5°C vs. 47.8°C). In
P
(cid:2)(cid:5)
6.0A
(cid:6)2(cid:4)14.0m(cid:2)(cid:2)504.0mW Table 4, as shown in the above calculations, theoretically
D (eq. 2) calculated T
and measured T
, R(cid:4)JT and P
D
are used to
Using Equation 1,
estimate T
for various loads and packages.
T (cid:2)47.3°C(cid:3)(504.0mW(cid:4)1.0°C(cid:7)W)(cid:2)47.8°C
Table 4. CALCULATED T OF THE PROPOSED MOSFETS VS. LOAD CURRENT
TJ ((cid:2)C)
Estimated TJ
(cid:5)TJ
fro
H
e a
M
d
x
i
um
Battery R M 1 D 0 a S x V , i m O V N G u m @ S L M o a s x s i e m s u P m D R(cid:3)JA Measured 2 E 4 s B (cid:2) t C a im s A e a m d te b o d i n e @ nt T C h a e lc o u re la ti t c e a d l T an B h d e e o t S w r c e e a t e i l c n e a d l Me B a 1 a s 7 s u 5 e r d (cid:2) e C m o n e nt
Current Part Number Package (m(cid:2)) (mW) ((cid:2)C/W) TCASE ((cid:2)C) Measurement Value Up Value ((cid:2)C)
6 A NVTFS5C478NLWFTAG (cid:3)8FL 14.0 504.0 51.0 47.3 47.8 49.5 −1.7 127.2
NVMFS5C468NLAFT1G SO−8FL 10.3 370.8 43.0 40.1 40.4 45.5 −5.1 134.6
8 A NVTFS5C466NLWFTAG (cid:3)8FL 7.3 467.2 48.0 47.4 47.8 48.0 +0.2 127.2
NVMFS5C466NLWFT1G SO−8FL 7.3 467.2 43.0 45.3 45.7 45.5 +0.2 129.3
10 A NVTYS005N04CLTWG LFPAK8 4.8 480.0 47.7 52.8 53.2 47.8 +5.4 121.8
NVMYS4D6N04CLTWG LFPAK4 4.5 450.0 40.0 47.5 47.9 44.0 +3.9 127.1
• •
At 6 A load current there is approximately 5.8 % higher Measurement of R(cid:4)JA in the datasheet using 2 oz. copper
head room for T with 5 × 6 than 3 × 3 package. pad with larger area board seems unrealistic from real
• At 8 A load, approximately 1.6 % higher head room with application point of view but looking at the minor
5 × 6 than 3 × 3. Both the devices are having the same die difference in T J as estimated above shows that R(cid:4)JA
in different packages, therefore there is not much matched quite well with 4−layer test board optimized for
difference between T ’s is seen. thermal dissipation.
• At 10 A, approximately 4.3 % higher head room with • The results show that due to the larger package (5 × 6) the
5x6 than with 3 × 3. heat is getting dissipated efficiently and being distributed
• across the whole device hence there is better head room.
Likewise, the difference in theoretical and estimated T
is
not significant except around 5.4°C difference for one of Larger packaged devices are suitable for higher load
current application from thermal point of view as well as
the 10 A MOSFETs. This shows that the R(cid:4)JA in the
for applications with higher ambient temperature.
datasheet is reliable for this specific test setup.
9

Estimation of the Maximum Ambient Temperature T The power dissipation at 175°C junction temperature and
The previous calculations show that R(cid:4)JA of the datasheet 6 A load current is as follows:
matches quite well with the NCV68061 test board.
P
(cid:2)(cid:5)
6.0A
(cid:6)2(cid:4)25.9m(cid:2)(cid:2)932.4mW
Therefore, the maximum ambient temperature above which D
the MOSFET cannot not be operated can be calculated. With R(cid:4)JA = 51.0°C/W, the temperature difference
Figure 20 shows the variation of R in relation to T between junction and ambient can be calculated:
DS,ON J
for NVTFS5C478NLWFTAG. At 175°C junction
temperature, the maximum R is around 1.85 times
Temperaturedifference(cid:5)T(cid:2)51.0°C(cid:7)W (cid:4) 932.4mW(cid:2)47.5°C
higher compared to 25°C junction temperature. This results
in a maximum R
DS, ON
of 1.85 × 14 m(cid:2) = ~25.9 m(cid:2).. MaximumT A (cid:2)T J (cid:8)(cid:5)T
MaximumT (cid:2)175.0°C(cid:8)47.5°C(cid:2)127.5°C
(eq. 5)
From the above example, the MOSFET can be operated
at maximum ambient temperature of 127.5°C. If the ambient
temperature goes above the calculated value, then it would
mean that the T
has reached over 175°C.
The silicon of the MOSFET itself can be operated at above
175°C, but due to the limitation of package mold compound
and to ensure reliability over long−term operation, the
MOSFET datasheet states that maximum T
to be 175°C.
Temperature above maximum T
would lead to
unguaranteed behavior of the device, and it also means that
device is operating out of specification.
Table5 shows the estimated maximum ambient
Figure 20. NVTFS5C478NLWFTAG On−Resistance temperature for various MOSFETS, considering different
Variation with Temperature load currents and a junction temperature of 175°C.
Table 5. ESTIMATED MAXIMUM T
AMB
Estimated
Battery Maximum RDS,ON @ 10V Maximum Losses Maximum
Current Part Number Package VGS @ 175(cid:2)C TJ (m(cid:2)) PD (mW) R(cid:3)JA ((cid:2)C/W) TAMB ((cid:2)C)
6 A NVTFS5C478NLWFTAG (cid:3)8FL 25.9 932.4 51.0 127.5
NVMFS5C468NLAFT1G SO−8FL 19.6 705.6 43.0 144.6
8A NVTFS5C466NLWFTAG (cid:3)8FL 14.4 921.6 48.0 130.7
NVMFS5C466NLWFT1G SO−8FL 13.2 844.8 43.0 138.6
10A NVTYS005N04CLTWG LFPAK8 8.8 880.0 47.7 133.0
NVMYS4D6N04CLTWG LFPAK4 8.3 830.0 40.0 141.8
CONCLUSION
Reverse polarity protection circuits are one of the core a larger die helps to dissipate the heat better than with a
building blocks of any ECU in a vehicle. In this application smaller die. With that said, table 3 shows that the difference
note several reverse polarity protection techniques are in margin for maximum T between 5 × 6 and 3 × 3 is not
discussed including diodes, P−Channel MOSFET and significant. Depending upon the application needs and
N−Channel MOFET. A comparison between all the cooling system used either 5 × 6 or 3 × 3 packaged
techniques is presented highlighting advantages and MOSFETs can be used.
disadvantages of each technique. Moreover, a MOSFET Without significant difference between the theoretically
selection guide is given to support the MOSFET selection calculated and practically estimated junction temperature
process, including a list of recommended devices. Thermal T
, R(cid:4)JA given in the datasheet is a realistic value to perform
measurements with load currents from 6 A to 10 A show that thermal analysis in the real applications. R(cid:4)JA helps to
5 × 6 packages perform well from thermal point of view, due calculate the maximum ambient temperature at which the
to the larger package and bigger die, R will be reduced MOSFET can be operated using the calculations shown in
and power losses are lesser than 3 × 3 package. Additionally, the document earlier.
10

onsemi, , and other names, marks, and brands are registered and/or common law trademarks of Semiconductor Components Industries, LLC dba “onsemi” or its affiliates
and/or subsidiaries in the United States and/or other countries. onsemi owns the rights to a number of patents, trademarks, copyrights, trade secrets, and other intellectual property.
A listing of onsemi’s product/patent coverage may be accessed at www.onsemi.com/site/pdf/Patent−Marking.pdf. onsemi reserves the right to make changes at any time to any
products or information herein, without notice. The information herein is provided “as−is” and onsemi makes no warranty, representation or guarantee regarding the accuracy of the
information, product features, availability, functionality, or suitability of its products for any particular purpose, nor does onsemi assume any liability arising out of the application or use
of any product or circuit, and specifically disclaims any and all liability, including without limitation special, consequential or incidental damages. Buyer is responsible for its products
and applications using onsemi products, including compliance with all laws, regulations and safety requirements or standards, regardless of any support or applications information
provided by onsemi. “Typical” parameters which may be provided in onsemi data sheets and/or specifications can and do vary in different applications and actual performance may
vary over time. All operating parameters, including “Typicals” must be validated for each customer application by customer’s technical experts. onsemi does not convey any license
under any of its intellectual property rights nor the rights of others. onsemi products are not designed, intended, or authorized for use as a critical component in life support systems
or any FDA Class 3 medical devices or medical devices with a same or similar classification in a foreign jurisdiction or any devices intended for implantation in the human body. Should
Buyer purchase or use onsemi products for any such unintended or unauthorized application, Buyer shall indemnify and hold onsemi and its officers, employees, subsidiaries, affiliates,
and distributors harmless against all claims, costs, damages, and expenses, and reasonable attorney fees arising out of, directly or indirectly, any claim of personal injury or death
associated with such unintended or unauthorized use, even if such claim alleges that onsemi was negligent regarding the design or manufacture of the part. onsemi is an Equal
Opportunity/Affirmative Action Employer. This literature is subject to all applicable copyright laws and is not for resale in any manner.
ADDITIONAL INFORMATION
TECHNICAL PUBLICATIONS: ONLINE SUPPORT: www.onsemi.com/support
Technical Library: www.onsemi.com/design/resources/technical−documentation For additional information, please contact your local Sales Representative at
onsemi Website: www.onsemi.com www.onsemi.com/support/sales
◊ www.onsemi.com
11