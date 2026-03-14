---
source: "Rohm -- Efficiency of Buck Converter (9 Loss Mechanisms)"
url: "https://fscdn.rohm.com/en/products/databook/applinote/ic/power/switching_regulator/buck_converter_efficiency_app-e.pdf"
format: "PDF 16pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 39054
---

Application Note
Switching Regulator IC Series
Efficiency of Buck Converter
Switching regulators are known as being highly efficient power sources. To further improve their efficiency, it is helpful to
understand the basic mechanism of power loss. This application note explains power loss factors and methods for calculating
them. It also explains how the relative importance of power loss factors depends on the specifications of the switching power
source.
Synchronous rectification type
High-side MOSFET
Figure 1 shows the circuit diagram of a synchronous
𝑉
rectification type DC/DC converter. Figure 2 shows the 𝑃 =𝐼 2×𝑅 × 𝑂𝑈𝑇 [𝑊] (1)
𝑂𝑁−𝐻 𝑂𝑈𝑇 𝑂𝑁−𝐻 𝑉
𝐼𝑁
waveforms of the voltage of a switch node and the current
waveform of the inductor. The striped patterns represent the
Low-side MOSFET
areas where the loss occurs.
The following nine factors are the main causes of power loss: 𝑃 =𝐼 2×𝑅 ×(1− 𝑂𝑈𝑇 ) [𝑊] (2)
𝑂𝑁−𝐿 𝑂𝑈𝑇 𝑂𝑁−𝐿 𝑉
1. Conduction loss caused by the on-resistance of the
MOSFET 𝑃
𝑂𝑁−𝐻
,𝑃
𝑂𝑁−𝐿
𝐼
𝑂𝑈𝑇
: Output current [𝐴]
2. Switching-loss in the MOSFET 𝑃 ,𝑃 𝑅 : High-side MOSFET on-resistance [𝛺]
𝑆𝑊−𝐻 𝑆𝑊−𝐿 𝑂𝑁−𝐻
3. Reverse recovery loss in the body diode 𝑃 𝑅 : Low-side MOSFET on-resistance [𝛺]
𝐷𝐼𝑂𝐷𝐸 𝑂𝑁−𝐿
4. Output capacitance loss in the MOSFET 𝑃 𝑉 : Input voltage [𝑉]
𝐶𝑂𝑆𝑆 𝐼𝑁
5. Dead time loss 𝑃 𝑉 : Output voltage [𝑉]
𝐷 𝑂𝑈𝑇
6. Gate charge loss in the MOSFET 𝑃
𝐺
7. Operation loss caused by the IC control circuit 𝑃 In the equations (1) and (2), the output current is used as the
𝐼𝐶
8. Conduction loss in the inductor 𝑃 current value. This is the average current of the inductor. As
𝐿(𝐷𝐶𝑅)
9. Loss in the capacitor 𝑃
𝐶𝐼𝑁
𝐶𝑂𝑈𝑇
shown in the lower part of Figure 2, greater losses are
generated in the actual ramp waveforms. If the current
Conduction loss in the MOSFET waveform is sharper (peak current is higher), the effective
current is obtained by integrating the square of the differential
The conduction loss in the MOSFET is calculated in the A and
between the peak and bottom values of the current. The loss
B sections of the waveform in Figure 2. As the high-side
can then be calculated in more detail.
MOSFET is ON and the low-side MOSFET is OFF in the A
The conduction losses 𝑃 and 𝑃 are calculated with
𝑂𝑁−𝐻 𝑂𝑁−𝐿
section, the conduction loss of the high-side MOSFET can be
the following equations.
estimated from the output current, on-resistance, and on-duty
cycle. As the high-side MOSFET is OFF and the low-side High-side MOSFET
MOSFET is ON in the B section, the conduction loss of the
(𝐼 −𝐼 )2 𝑉
low-side MOSFET can be estimated from the output current, 𝑃 =[𝐼 2+ 𝑃 𝑉 ]×𝑅 × 𝑂𝑈𝑇 [𝑊] (3)
𝑂𝑁−𝐻 𝑂𝑈𝑇 12 𝑂𝑁−𝐻 𝑉
on-resistance, and off-duty cycle.
The conduction losses 𝑃 and 𝑃 are calculated with
𝑂𝑁−𝐻 𝑂𝑁−𝐿
the following equations.
© 2016, 2021, 2022 ROHM Co., Ltd. No. 64AN035E Rev.004
1/15
NOVEMBER 2022

Efficiency of Buck Converter Application Note
When the low-side MOSFET is turned ON by the gate voltage
while the body diode is energized and then the FET is turned
(𝐼 −𝐼 )2 𝑉 OFF by the gate voltage, the load current continues to flow in
𝑃 =[𝐼 2+ 𝑃 𝑉 ]×𝑅 ×(1− 𝑂𝑈𝑇 ) [𝑊] (4)
𝑂𝑁−𝐿 𝑂𝑈𝑇 12 𝑂𝑁−𝐿 𝑉 𝐼𝑁 the same direction through the body diode. Therefore, the
drain voltage becomes equal to the forward direction voltage
𝛥𝐼 = (𝑉 𝐼𝑁 −𝑉 𝑂𝑈𝑇 ) × 𝑉 𝑂𝑈𝑇 [𝐴] and remains low. Then, the resulting switching-loss 𝑃 𝑆𝑊𝐿 is
𝐿 𝑓 𝑆𝑊 ×𝐿 𝑉 𝐼𝑁 very small, as described in the following equation.
Δ𝐼
𝐼 =𝐼 + 𝐿 [𝐴]
𝑃 𝑂𝑈𝑇 2
1
𝑃 = ×𝑉 ×𝐼 ×(𝑡 +𝑡 )×𝑓 [𝑊] (6)
𝑆𝑊−𝐿 2 𝐷 𝑂𝑈𝑇 𝑟−𝐿 𝑓−𝐿 𝑆𝑊
𝐼 =𝐼
𝑃 𝑂𝑈𝑇
𝑉 : Forward direction voltage of
𝐷
low-side MOSFET body diode [𝑉]
𝐼 : Output current [𝐴]
𝐼 : Inductor current peak [𝐴]
𝑃
𝑡 : Low-side MOSFET rise time [𝑠𝑒𝑐]
𝑟−𝐿
𝐼 : Inductor current bottom [𝐴]
𝑡 : Low-side MOSFET rise time [𝑠𝑒𝑐]
𝑓−𝐿
𝑅 : High-side MOSFET on-resistance [𝛺]
𝑓 : Switching frequency [𝐻𝑧]
𝑆𝑊
𝑅 : Low-side MOSFET on-resistance [𝛺]
𝑂𝑁−𝐿
𝑉 : Input voltage [𝑉]
𝐼𝑁 Reverse recovery loss in the body diode
𝑉 : Output voltage [𝑉]
𝛥𝐼 : Ripple current of inductor [𝐴] When the high-side MOSFET is turned ON, the transition of
𝐿
𝑓 : Switching frequency [𝐻𝑧] the body diode of the low-side MOSFET from the forward
𝐿: Inductance value [𝐻] direction to the reverse bias state causes a diode recovery,
which in turn generates a reverse recovery loss in the body
Switching-loss in the MOSFET diode. This loss is determined by the reverse recovery time of
the diode 𝑡 . From the reverse recovery properties of the
𝑅𝑅
The switching-losses are calculated in the C and D sections or
diode, the loss is calculated with the following equation.
in the E and F sections of the waveform in Figure 2. When the
high-side and low-side MOSFETs are turned ON and OFF 1
𝑃 = ×𝑉 ×𝐼 ×𝑡 ×𝑓 [𝑊] (7)
alternately, a loss is generated during the transition of the on- 𝐷𝐼𝑂𝐷𝐸 2 𝐼𝑁 𝑅𝑅 𝑅𝑅 𝑆𝑊
switching. Since the equation for calculating the area of the
two triangles is similar to the equation for calculating the power
𝐼 : Peak value of
losses during the rising and falling transitions, this calculation
body diode reverse recovery current [𝐴]
can be approximated using a simple geometric equation.
𝑡 : Body diode reverse recovery time
The switching-loss 𝑃 is calculated with the following
𝑆𝑊−𝐻
equation.
High-side MOSFET Output capacitance loss in the MOSFET
1 In each switching cycle, the loss is generated because the
𝑃 = ×𝑉 ×𝐼 ×(𝑡 +𝑡 )×𝑓 [𝑊] (5)
𝑆𝑊−𝐻 2 𝐼𝑁 𝑂𝑈𝑇 𝑟−𝐻 𝑓−𝐻 𝑆𝑊 output capacitances of the high-side MOSFETs 𝐶 are
𝑂𝑆𝑆
charged. This loss is calculated with the following equation.
The charge/discharge loss of COSS in the low-side MOSFET is
usually ignored because the charge of COSS is already
𝑡 : High-side MOSFET rise time [𝑠𝑒𝑐]
𝑟−𝐻
discharged by the inductor current when low-side MOSFET
𝑡 : High-side MOSFET rise time [𝑠𝑒𝑐]
𝑓−𝐻
turns on, resulting in ZVS (Zero Voltage Switching).
2/15

𝑄 : Gate charge of low-side MOSFET [𝐶]
𝑔−𝐿
𝑃 𝐶𝑂𝑆𝑆 = 2 ×𝐶 𝑂𝑆𝑆−𝐻 ×𝑉 𝐼 𝑁 2×𝑓 𝑆𝑊 [𝑊] (8) 𝐶 𝐺𝑆−𝐻 : Gate capacitance of high-side MOSFET [𝐹]
𝐶 : Gate capacitance of low-side MOSFET [𝐹]
𝐺𝑆−𝐿
𝐶 =𝐶 +𝐶 [𝐹] 𝑉 : Gate drive voltage [𝑉]
𝑂𝑆𝑆−𝐻 𝐷𝑆−𝐻 𝐺𝐷−𝐻 𝑔𝑠
𝐶 : High-side MOSFET output capacitance [𝐹]
𝑂𝑆𝑆−𝐻
𝐶 : High-side MOSFET
𝐷𝑆−𝐻 Operation loss caused by the IC
drain-source capacitance [𝐹]
𝐶 : High-side MOSFET gate-drain capacitance [𝐹] The consumption power used by the IC control circuit 𝑃 is
𝐺𝐷−𝐻 𝐼𝐶
𝑉 : Input voltage [𝑉] calculated with the following equation.
𝑃 =𝑉 ×𝐼 [𝑊] (12)
𝐼𝐶 𝐼𝑁 𝐶𝐶
Dead time loss
When the high-side and low-side MOSFETs are turned ON
𝐼 : IC current consumption [𝐴]
𝐶𝐶
simultaneously, a short circuit occurs between the VIN and
ground, generating a very large current spike. A period of dead
Conduction loss in the inductor
time is provided for turning OFF both of the MOSFETs to
prevent such current spikes from occurring, while the inductor There are two types of the power loss in the inductor: the
current continues to flow. During the dead time, this inductor conduction loss caused by the resistance and the core loss
current flows to the body diode of the low-side MOSFET. The determined by the magnetic properties. Since the calculation
dead time loss 𝑃 is calculated in the G and H sections of the of the core loss is too complex, it is not described in this article.
waveform in Figure 2 with the following equation. The conduction loss is generated by the DC resistance (DCR)
of the winding that forms the inductor. The DCR increases as
𝑃 =𝑉 ×𝐼 ×(𝑡 +𝑡 )×𝑓 [𝑊] (9) the wire length increases; on the other hand, it decreases as
𝐷 𝐷 𝑂𝑈𝑇 𝐷𝑟 𝐷𝑓 𝑆𝑊
the wire cross-section increases. If this trend is applied to the
𝑉 : Forward direction voltage of inductor parts, the DCR increases as the inductance value
low-side MOSFET body diode [𝑉] increases and decreases as the case size increases.
𝐼 : Output current [𝐴] The conduction loss of the inductor can be estimated with the
𝑡 : Dead time for rising [𝑠𝑒𝑐] following equation. Since the inductor is always energized, it
𝐷𝑟
𝑡 : Dead time for falling [𝑠𝑒𝑐] is not affected by the duty cycle. Since the power loss is
𝐷𝑓
𝑓 : Switching frequency [𝐻𝑧] proportional to the square of the current, a higher output
current results in a greater loss. For this reason, it is important
Gate charge loss to select the appropriate inductors.
The Gate charge loss is the power loss caused by charging
𝑃 =𝐼 2×DCR [𝑊] (13)
𝐿(𝐷𝐶𝑅) 𝑂𝑈𝑇
the gate of the MOSFET. The gate charge loss depends on
the gate charges (or gate capacitances) of the high-side and
low-side MOSFETs. It is calculated with the following
𝐷𝐶𝑅: Inductor direct current resistance [Ω]
equations.
Since the output current is used in this equation, the average
𝑃 =(𝑄 +𝑄 )×𝑉 ×𝑓 [𝑊] (10)
𝐺 𝑔−𝐻 𝑔−𝐿 𝑔𝑠 𝑆𝑊
current of the inductor is used for the calculation. Similar to the
or above-mentioned calculation for the conduction loss of the
MOSFET, the loss can be calculated in more detail by using
𝑃 =(𝐶 +𝐶 )×𝑉 2×𝑓 [𝑊] (11)
𝐺 𝐺𝑆−𝐻 𝐺𝑆−𝐿 𝑔𝑠 𝑆𝑊
the ramp waveform for the inductor current calculation.
𝑄 : Gate charge of high-side MOSFET [𝐶]
𝑔−𝐻
3/15

𝑃 =[𝐼 2+ (𝐼𝑃−𝐼𝑉)2 ]×𝐷𝐶𝑅 [𝑊] (14) 𝑆𝑊
𝐿(𝐷𝐶𝑅) 𝑂𝑈𝑇 12 𝐿: Inductance value [𝐻]
The losses in the input capacitor 𝑃 and the output
𝐼 : Inductor current peak [𝐴]
𝑃
capacitor 𝑃 are calculated by substituting the RMS
𝐼 : Inductor current bottom [𝐴]
current in the equation (15) by those calculated in the
𝐷𝐶𝑅: Inductor direct current resistance [Ω]
equations (16) and (17), respectively.
Loss in the capacitor
Total power loss
Although several losses are generated in the
The power loss of the IC, P, is obtained by adding all the
capacitor―including series resistance, leakage, and dielectric
losses together.
loss―these losses are simplified into a general loss model as
equivalent series resistance (ESR). The power loss in the
𝑃=𝑃 +𝑃 +𝑃 +𝑃 +𝑃 +𝑃 +
𝑂𝑁−𝐻 𝑂𝑁−𝐿 𝑆𝑊−𝐻 𝑆𝑊−𝐿 𝐷𝐼𝑂𝐷𝐸 𝐶𝑂𝑆𝑆
capacitor is calculated by multiplying the ESR by the square
𝑃 +𝑃 +𝑃 +𝑃 +𝑃 +𝑃 [𝑊] (19)
𝐷 𝐺 𝐼𝐶 𝐿(𝐷𝐶𝑅) 𝐶𝐼𝑁 𝐶𝑂𝑈𝑇
of the RMS value of the AC current flowing through the
capacitor.
𝑃 : Conduction loss of high-side MOSFET [𝑊]
𝑃 : Conduction loss of low-side MOSFET [𝑊]
𝑃 =𝐼 2×𝐸𝑆𝑅 [𝑊] (15) 𝑂𝑁−𝐿
𝐶𝐴𝑃(𝐸𝑆𝑅) 𝐶𝐴𝑃(𝑅𝑀𝑆)
𝑃 : Switching-loss of high-side MOSFET [𝑊]
𝑃 : Switching-loss of low-side MOSFET [𝑊]
𝑆𝑊−𝐿
𝐼 : RMS current of capacitor [𝐴]
𝐶𝐴𝑃(𝑅𝑀𝑆)
𝑃 : Reverse recovery loss of body diode [𝑊]
𝐷𝐼𝑂𝐷𝐸
𝐸𝑆𝑅: Equivalent series resistance of capacitor [Ω]
𝑃 : Output capacitance loss of MOSFET [𝑊]
𝐶𝑂𝑆𝑆
𝑃 : Dead time loss [𝑊]
The RMS current in the input capacitor is complex, but it can
𝑃 : Gate charge loss [𝑊]
be estimated with the following equation.
𝑃 : IC operation loss [𝑊]
𝑃 : Conduction loss of inductor [𝑊]
√(𝑉 −𝑉 )×𝑉
𝐼 𝐶𝐼𝑁(𝑅𝑀𝑆) =𝐼 𝑂𝑈𝑇 × 𝐼𝑁 𝑉 𝑂𝑈𝑇 𝑂𝑈𝑇 [𝐴] (16) 𝑃 𝐶𝐼𝑁 : Input capacitor loss [𝑊]
𝑃 : Output capacitor loss [𝑊]
𝐼𝑁 Efficiency
𝐼 : Output current [𝐴] Since the total power loss is obtained, the efficiency can be
calculated with the following equation.
The RMS current in the output capacitor is equal to the RMS
value of the ripple current in the inductor, and calculated with 𝑉 ×𝐼
η＝ 𝑂𝑈𝑇 𝑂𝑈𝑇 (20)
the following equation. 𝑉 𝑂𝑈𝑇 ×𝐼 𝑂𝑈𝑇 +𝑃
𝛥𝐼
𝐼 𝐶𝑂𝑈𝑇(𝑅𝑀𝑆) = 𝐿 [𝐴] (17) 𝐼 𝑂𝑈𝑇 : Output current [𝐴]
2√3
𝑃: Total power loss [𝑊]
𝛥𝐼 : Ripple current of inductor [𝐴]
𝐿
(𝑉 −𝑉 ) 𝑉
𝛥𝐼 = 𝐼𝑁 𝑂𝑈𝑇 × 𝑂𝑈𝑇 [𝐴] (18)
𝐿 𝑓 ×𝐿 𝑉
𝑆𝑊 𝐼𝑁
4/15

V I CC C GD-H High-side MOSFET
IN
D R ON-H
C
G DS-H I
L
S
I
C GS-H V L R DCR OUT
SW
Controller
GD-L Low-side MOSFET C OUT
D R ON-L ESR V OUT R L
G C DS-L
Body-Diode
GS-L
V
D
FB
Figure 1. Circuit diagram of the synchronous rectification type DC/DC converter
t
t t t OFF
r-H ON f-H R ×I
ON-H OUT
0
R ×I
ON-L OUT
t t
Df Dr
L(AVERAGE)
t
5/15
P(PEAK)
V(VALLEY)
t t
r-L f-L
ΔI
Figure 2. Switching waveform and loss

Calculation example (synchronous rectification type)
Calculation formula Parameters Result
1. Conduction loss 𝑉
∶ Input voltage 12 𝑉
𝑃 =[𝐼 2+ (𝐼 𝑃 −𝐼 𝑉 )2 ]×𝑅 × 𝑉 𝑂𝑈𝑇 [𝑊] 𝑉 𝑂𝑈𝑇 ∶Output voltage 5.0 𝑉
𝑂𝑁−𝐻 𝑂𝑈𝑇 12 𝑂𝑁−𝐻 𝑉 𝐼 ∶Output current 3.0 𝐴
𝐼𝑁 𝑂𝑈𝑇
(𝐼 −𝐼 )2 𝑉 𝑅 𝑂𝑁−𝐻 ∶ High-side MOSFET on-resistance 100 𝑚𝛺
𝑃 =[𝐼 2+ 𝑃 𝑉 ]×𝑅 ×(1− 𝑂𝑈𝑇 ) [𝑊]
𝑂𝑁−𝐿 𝑂𝑈𝑇 12 𝑂𝑁−𝐿 𝑉 𝑅 ∶ Low-side MOSFET on-resistance 70 𝑚𝛺
𝐼𝑁 𝑂𝑁−𝐿
376 𝑚𝑊
(𝑉 −𝑉 ) 𝑉 𝐿∶ Inductance value 4.7 𝜇𝐻 369 𝑚𝑊
𝛥𝐼 = 𝐼𝑁 𝑂𝑈𝑇 × 𝑂𝑈𝑇 [𝐴]
𝐿 𝑓 ×𝐿 𝑉 𝑓 ∶ Switching frequency 1.0 𝑀𝐻𝑧
𝑆𝑊 𝐼𝑁 𝑆𝑊
𝐼 =𝐼 + Δ𝐼 𝐿 [𝐴] 𝑡 𝑟−𝐻 ∶ High-side MOSFET rise time 4 𝑛𝑠𝑒𝑐
𝑃 𝑂𝑈𝑇 2 𝑡 ∶ High-side MOSFET fall time 6 𝑛𝑠𝑒𝑐
𝐼 =𝐼 − Δ𝐼 𝐿 [𝐴] 𝑡 𝑟−𝐿 ∶ Low-side MOSFET rise time 2 𝑛𝑠𝑒𝑐
𝑉 𝑂𝑈𝑇 2
𝑡 ∶ Low-side MOSFET fall time 2 𝑛𝑠𝑒𝑐
𝑓−𝐿
2. Switching-loss 𝑉 𝐷 ∶Forward direction voltage of
low-side MOSFET body diode 0.5 𝑉
𝑃 𝑆𝑊−𝐻 = 2 ×𝑉 𝐼𝑁 ×𝐼 𝑂𝑈𝑇 ×(𝑡 𝑟−𝐻 +𝑡 𝑓−𝐻 )×𝑓 𝑆𝑊 [𝑊] 𝐼 𝑅𝑅 ∶Peak value of body diode 180 𝑚𝑊
reverse recovery current 0.3 𝐴 3 𝑚𝑊
𝑃 = ×𝑉 ×𝐼 ×(𝑡 +𝑡 )×𝑓 [𝑊] 𝑡 ∶Body diode reverse recovery time 25 nsec
𝑆𝑊−𝐿 2 𝐷 𝑂𝑈𝑇 𝑟−𝐿 𝑓−𝐿 𝑆𝑊 𝑅𝑅
𝐶 ∶ High-side MOSFET drain-source capacitance
𝐷𝑆−𝐻
40 𝑝𝐹
3. Reverse recovery loss
1 𝐶 𝐺𝐷−𝐻 ∶ High-side MOSFET gate-drain capacitance 45 𝑚𝑊
𝑃 = ×𝑉 ×𝐼 ×𝑡 ×𝑓 [𝑊] 40 𝑝𝐹
𝐷𝐼𝑂𝐷𝐸 2 𝐼𝑁 𝑅𝑅 𝑅𝑅 𝑆𝑊
𝐶 ∶ Low-side MOSFET drain-source
𝐷𝑆−𝐿
capacitance 40 𝑝𝐹
4. Output capacitance loss in the MOSFET
𝐶 ∶ Low-side MOSFET gate-drain
1 𝐺𝐷−𝐿
𝑃 = ×𝐶 ×𝑉 2×𝑓 [𝑊] capacitance 40 𝑝𝐹 5.8 𝑚𝑊
𝐶𝑂𝑆𝑆 2 𝑂𝑆𝑆−𝐻 𝐼𝑁 𝑆𝑊
𝑡 ∶ Dead time for rising 30 𝑛𝑠𝑒𝑐
𝐷𝑟
𝐶 =𝐶 +𝐶 [𝐹]
𝑂𝑆𝑆−𝐻 𝐷𝑆−𝐻 𝐺𝐷−𝐻
𝑡 ∶ Dead time for falling 30 𝑛𝑠𝑒𝑐
𝐷𝑓
5. Dead time loss 𝑄 𝑔−𝐻 ∶ Gate charge of high-side MOSFET 1 𝑛𝐶
90 𝑚𝑊
𝑄 ∶ Gate charge of low-side MOSFET 1 𝑛𝐶
𝑃 =𝑉 ×𝐼 ×(𝑡 +𝑡 )×𝑓 [𝑊] 𝑔−𝐿
𝐷 𝐷 𝑂𝑈𝑇 𝐷𝑟 𝐷𝑓 𝑆𝑊
𝐶 ∶ Gate capacitance of
𝐺𝑆−𝐻
high-side MOSFET 200 𝑝𝐹
6. Gate charge loss
𝐶 ∶ Gate capacitance of
𝐺𝑆−𝐿
𝑃 𝐺 =(𝑄 𝑔−𝐻 +𝑄 𝑔−𝐿 )×𝑉 𝑔𝑠 ×𝑓 𝑆𝑊 low-side MOSFET 200 𝑝𝐹
10 𝑚𝑊
or 𝑉 𝑔𝑠 ∶ Gate drive voltage 5.0𝑉
𝑃 =(𝐶 +𝐶 )×𝑉 2×𝑓 𝐼 𝐶𝐶 ∶ IC current consumption 1.0 𝑚𝐴
𝐺 𝐺𝑆−𝐻 𝐺𝑆−𝐿 𝑔𝑠 𝑆𝑊
𝐷𝐶𝑅∶Inductor direct current resistance 80 𝑚Ω
7. Operation loss caused by the IC 𝐸𝑆𝑅
∶Equivalent series resistance of
input capacitor 3 𝑚𝛺 12 𝑚𝑊
𝑃 =𝑉 ×𝐼
𝐸𝑆𝑅 ∶Equivalent series resistance of
output capacitor 1 𝑚𝛺
8. Conduction loss in the inductor
(𝐼 −𝐼 )2 723 𝑚𝑊
𝑃 =[𝐼 2+ 𝑃 𝑉 ]×𝐷𝐶𝑅 [𝑊]
𝐿(𝐷𝐶𝑅) 𝑂𝑈𝑇 12
6/15

Calculation example (synchronous rectification type) continued
9. Loss in the capacitor
𝑃 =𝐼 2×𝐸𝑆𝑅 [𝑊]
𝐶𝐼𝑁 𝐶𝐼𝑁(𝑅𝑀𝑆) 𝐶𝐼𝑁
√(𝑉 −𝑉 )×𝑉 6.6 𝑚𝑊
𝐼 =𝐼 × 𝐼𝑁 𝑂𝑈𝑇 𝑂𝑈𝑇 [𝐴]
𝐶𝐼𝑁(𝑅𝑀𝑆) 𝑂𝑈𝑇 𝑉
𝐼𝑁 0.5 𝑚𝑊
𝐶𝑂𝑈𝑇 𝐶𝑂𝑈𝑇(𝑅𝑀𝑆) 𝐶𝑂𝑈𝑇
𝐼 = 𝐿 [𝐴]
𝐶𝑂𝑈𝑇(𝑅𝑀𝑆)
𝑃=𝑃 +𝑃 +𝑃 +𝑃 +𝑃 +𝑃 1.82 𝑊
𝑂𝑁−𝐻 𝑂𝑁−𝐿 𝑆𝑊−𝐻 𝑆𝑊−𝐿 𝐷𝐼𝑂𝐷𝐸 𝐶𝑂𝑆𝑆
+𝑃 +𝑃 +𝑃 +𝑃 +𝑃
𝐷 𝐺 𝐼𝐶 𝐿(𝐷𝐶𝑅) 𝐶𝐼𝑁
+𝑃 [𝑊]
Non-synchronous rectification type Conduction loss in the diode
Figure 3 shows the circuit diagram of the non-synchronous While the conduction loss in the MOSFET is determined by
rectification type. In comparison with the synchronous the on-resistance, the conduction loss in the diode is
rectification type in Figure 1, the low-side switch is changed determined by the forward direction voltage of the diode and
from a MOSFET to a diode. Power loss is mainly caused by its value becomes large. Since the diode conducts the current
the 9 factors listed below. There are some differences in how when the high-side MOSFET is OFF, the loss can be
power loss occurs in synchronous and non-synchronous estimated with the following equation.
rectification types. In the synchronous type, conduction loss is
caused by the on-resistance of the low-side MOSFET; in the 𝑃 =𝐼 ×𝑉 ×(1− 𝑉𝑂𝑈𝑇) [𝑊] (21)
𝑂𝑁−𝐷 𝑂𝑈𝑇 𝐹 𝑉𝐼𝑁
non-synchronous type, conduction loss is caused by the on-
resistance of the diode. In the non-synchronous type, there is
no switching-loss in the low-side MOSFET. In the synchronous
𝑉 : Forward direction voltage of diode [𝑉]
type, there is reverse recovery loss in the low-side MOSFET 𝐹
body diode; in the non-synchronous type, reverse recovery 𝐼𝑁
loss occurs in the diode. Finally, in the non-synchronous type, 𝑉 𝑂𝑈𝑇 : Output voltage [𝑉]
output capacitance loss and gate charge loss occur only in the
high-side MOSFET. In the case of a buck converter, the on-time of the diode
becomes longer as the step-down ratio gets higher or as the
1. Conduction loss caused by the on-resistance of the
output voltage gets lower, resulting in a greater contribution to
MOSFET 𝑃
𝑂𝑁−𝐻 the power loss of the diode. Therefore, when the output
2. Conduction loss caused by the on-resistance of the diode
voltage is low, the non-synchronous rectification type is
𝑃 𝑂𝑁−𝐷 typically less efficient than the synchronous rectification type.
3. Switching-loss in the MOSFET 𝑃
4. Reverse recovery loss in the diode 𝑃
𝐷𝐼𝑂𝐷𝐸 Reverse recovery loss in the diode
5. Output capacitance loss in the MOSFET 𝑃
𝐶𝑂𝑆𝑆
6. Gate charge loss in the MOSFET 𝑃 The reverse recovery loss in the diode is calculated in the
7. Operation loss caused by the IC control circuit 𝑃 same way as for the body diode of the low-side MOSFET in
the synchronous rectification type. When the MOSFET is
8. Conduction loss in the inductor 𝑃
turned ON, the transition from the forward direction to the
9. Loss in the capacitor 𝑃
reverse bias state of the diode causes a diode recovery,
The calculations are shown for the factors that are different generating a reverse recovery loss in the diode.
from the synchronous rectification type.
7/15

This loss is determined by the reverse recovery time of the 𝑃 =𝑄 ×𝑉 ×𝑓 [𝑊] (24)
𝐺 𝑔−𝐻 𝑔𝑠 𝑆𝑊
diode 𝑡 𝑅𝑅 . From the reverse recovery properties of the diode, or
the loss is calculated with the following equation. 𝑃 =𝐶 ×𝑉 2×𝑓 [𝑊] (25)
𝐺 𝐺𝑆−𝐻 𝑔𝑠 𝑆𝑊
𝑃 = 1 ×𝑉 ×𝐼 ×𝑡 ×𝑓 [𝑊] (22) 𝑄 𝑔−𝐻 : Gate charge of MOSFET [𝐶]
𝐶 : Gate capacitance of MOSFET [𝐹]
𝑉 𝐼𝑁 : Input voltage [𝑉] 𝑉 𝑔𝑠 : Gate drive voltage [𝑉]
𝐼 𝑅𝑅 : Peak value of diode reverse recovery current [𝐴] 𝑓 𝑆𝑊 : Switching frequency [𝐻𝑧]
𝑡 : Diode reverse recovery time [𝑠𝑒𝑐]
𝑓 : Switching frequency [𝐻𝑧] Total power loss
The power loss of the IC, P, is obtained by adding all the
Output capacitance loss in the MOSFET
losses together.
In each switching cycle, a loss is generated because the
𝑃=𝑃 +𝑃 +𝑃 +𝑃 +𝑃 +𝑃 +𝑃 +
output capacitance of the MOSFET 𝐶 is charged. This loss 𝑂𝑁−𝐻 𝑂𝑁−𝐷 𝑆𝑊−𝐻 𝐷𝐼𝑂𝐷𝐸 𝐶𝑂𝑆𝑆 𝐺 𝐼𝐶
𝑂𝑆𝑆
can be estimated with the following equation. 𝑃 𝐿(𝐷𝐶𝑅) +𝑃 𝐶𝐼𝑁 +𝑃 𝐶𝑂𝑈𝑇 [𝑊] (26)
𝑃 𝐶𝑂𝑆𝑆 = 2 ×(𝐶 𝐷𝑆−𝐻 +𝐶 𝐺𝐷−𝐻 )×𝑉 𝐼 𝑁 2×𝑓 𝑆𝑊 [𝑊] (23) 𝑃 𝑂𝑁−𝐻 : Conduction loss of MOSFET [𝑊]
𝑃 : Conduction loss caused by
𝑂𝑁−𝐷
𝐶 : MOSFET drain-source capacitance [𝐹] on-resistance of diode [𝑊]
𝐶 : MOSFET gate-drain capacitance [𝐹] 𝑃 : Switching-loss of MOSFET [𝑊]
𝐺𝐷−𝐻 𝑆𝑊−𝐻
𝑉 : Input voltage [𝑉] 𝑃 : Reverse recovery loss of diode [𝑊]
𝐼𝑁 𝐷𝐼𝑂𝐷𝐸
𝑓 : Switching frequency [𝐻𝑧] 𝑃 : Output capacitance loss of MOSFET [𝑊]
𝑆𝑊 𝐶𝑂𝑆𝑆
𝑃 : Gate charge loss of MOSFET [𝑊]
Gate charge loss 𝑃 : IC operation loss [𝑊]
𝑃 : Conduction loss of inductor [𝑊]
The Gate charge loss is the power loss caused by charging
𝑃 : Input capacitor loss [𝑊]
the gate of the MOSFET. The gate charge loss depends on 𝐶𝐼𝑁
𝑃 : Output capacitor loss [𝑊]
the gate charge (or gate capacitance) of the MOSFET and is 𝐶𝑂𝑈𝑇
calculated with the following equations.
High-side MOSFET
R
ON-H
I CC C GD-H
G DS-H I
C GS-H V L R DCR OUT
Controller
OUT
Diode V OUT R L
ESR
F
FB
Figure 3. Circuit diagram of the non-synchronous rectification type DC/DC converter
8/15

Calculation example (non-synchronous rectification type)
1. Conduction loss in the MOSFET 𝑉
∶ Input voltage 12 𝑉
𝑃 =[𝐼 2+ (𝐼 𝑃 −𝐼 𝑉 )2 ]×𝑅 × 𝑉 𝑂𝑈𝑇 [𝑊] 𝑉 𝑂𝑈𝑇 ∶Output voltage 5.0 𝑉
𝑂𝑁−𝐻 𝑂𝑈𝑇 12 𝑂𝑁−𝐻 𝑉 𝐼 ∶ Output current 3.0 𝐴
𝐼𝑁 𝑂𝑈𝑇
𝛥𝐼 𝐿 = (𝑉 𝐼 𝑓 𝑁 − × 𝑉 𝑂 𝐿 𝑈𝑇 ) × 𝑉 𝑉 𝑂𝑈𝑇 [𝐴] 𝑅 𝐿 𝑂 ∶ 𝑁 − In 𝐻 d ∶ u c M ta O n S c F e E v T a lu o e n - r 4 e . s 7 is 𝜇 ta 𝐻 n ce 100 𝑚𝛺 376 𝑚𝑊
𝑆𝑊 𝐼𝑁
𝐼 =𝐼 + Δ𝐼 𝐿 [𝐴] 𝑓 𝑆𝑊 ∶ Switching frequency 1.0 𝑀𝐻𝑧
𝑃 𝑂𝑈𝑇 2 𝑉 Forward direction voltage of diode 0.5 𝑉
𝐹
𝐼 =𝐼 − Δ𝐼 𝐿 [𝐴] 𝑡 𝑟−𝐻 ∶ MOSFET rise time 4 𝑛𝑠𝑒𝑐
𝑉 𝑂𝑈𝑇 2
𝑡 ∶ MOSFET fall time 6 𝑛𝑠𝑒𝑐
2. Conduction loss in the diode 𝐼 𝑅𝑅 ∶Peak value of
diode reverse recovery current 0.3 𝐴
𝑉 875 𝑚𝑊
𝑃 =𝐼 ×𝑉 ×(1− 𝑂𝑈𝑇 ) [𝑊] 𝑡 ∶Diode reverse recovery time 25 nsec
𝑂𝑁−𝐷 𝑂𝑈𝑇 𝐹 𝑉 𝑅𝑅
𝐶 ∶ MOSFET drain-source capacitance 40 pF
3. Switching-loss in the MOSFET 𝐶 𝐺𝐷−𝐻 ∶ MOSFET gate-drain capacitance 40 pF
1 𝑄 𝑔−𝐻 ∶ Gate charge of MOSFET 1 𝑛𝐶 180 𝑚𝑊
𝑃 = ×𝑉 ×𝐼 ×(𝑡 +𝑡 )×𝑓 [𝑊]
𝑆𝑊−𝐻 2 𝐼𝑁 𝑂𝑈𝑇 𝑟−𝐻 𝑓−𝐻 𝑆𝑊 𝐶 ∶ Gate capacitance of MOSFET 200 𝑝𝐹
𝑉 ∶ Gate drive voltage 5.0𝑉
𝑔𝑠
4. Reverse recovery loss in the diode
𝐼 ∶ IC current consumption 1.0 𝑚𝐴
𝐶𝐶 45 𝑚𝑊
𝑃 = ×𝑉 ×𝐼 ×𝑡 ×𝑓 [𝑊] 𝐷𝐶𝑅∶Inductor direct current resistance 80 𝑚Ω
𝐸𝑆𝑅 ∶:Equivalent series resistance of
input capacitor 3 𝑚𝛺
5. Output capacitance loss in the MOSFET
1 𝐸𝑆𝑅 𝐶𝑂𝑈𝑇 ∶Equivalent series resistance of 5.8 𝑚𝑊
𝑃 = ×(𝐶 +𝐶 )×𝑉 2×𝑓 [𝑊] output capacitor 1 𝑚𝛺
𝐶𝑂𝑆𝑆 2 𝐷𝑆−𝐻 𝐺𝐷−𝐻 𝐼𝑁 𝑆𝑊
6. Gate charge loss
𝑃 =𝑄 ×𝑉 ×𝑓
𝐺 𝑔−𝐻 𝑔𝑠 𝑆𝑊
5 𝑚𝑊
or
𝑃 =𝐶 ×𝑉 2×𝑓
𝐺 𝐺𝑆−𝐻 𝑔𝑠 𝑆𝑊
7. Operation loss caused by the IC
12 𝑚𝑊
𝑃 =𝑉 ×𝐼
8. Conduction loss in the inductor
(𝐼 −𝐼 )2 723 𝑚𝑊
𝑃 =[𝐼 2+ 𝑃 𝑉 ]×𝐷𝐶𝑅 [𝑊]
𝐿(𝐷𝐶𝑅) 𝑂𝑈𝑇 12
9/15

Calculation example (non-synchronous rectification type) continued
9. Loss in the capacitor
𝐶𝐼𝑁 𝐶𝐼𝑁(𝑅𝑀𝑆) 𝐶𝐼𝑁
√(𝑉 −𝑉 )×𝑉
𝐼 =𝐼 × 𝐼𝑁 𝑂𝑈𝑇 𝑂𝑈𝑇 [𝐴] 6.6 𝑚𝑊
𝐶𝐼𝑁(𝑅𝑀𝑆) 𝑂𝑈𝑇 𝑉
𝐼𝑁 0.5 𝑚𝑊
𝐶𝑂𝑈𝑇 𝐶𝑂𝑈𝑇(𝑅𝑀𝑆) 𝐶𝑂𝑈𝑇
𝐼 = 𝐿 [𝐴]
𝐶𝑂𝑈𝑇(𝑅𝑀𝑆)
2.23 𝑊
𝑃=𝑃 +𝑃 +𝑃 +𝑃 +𝑃 +𝑃 +𝑃
𝑂𝑁−𝐻 𝑂𝑁−𝐷 𝑆𝑊−𝐻 𝐷𝐼𝑂𝐷𝐸 𝐶𝑂𝑆𝑆 𝐺 𝐼𝐶
+𝑃 +𝑃 +𝑃 [𝑊]
𝐿(𝐷𝐶𝑅) 𝐶𝐼𝑁 𝐶𝑂𝑈𝑇
Loss factor to reduce the loss by lowering the switching frequency is
commonly applied when the current is low. The operation loss
Here we follow how the relative importance of the power loss
caused of the IC can be reduced by optimizing the circuit
factors depends on the specification of the switching power
current in the control circuit.
source.
Figure 5 shows the behavior when the switching frequency is
Figure 4 shows the behavior when the output current is varied
varied in the synchronous rectification type. When operating
in the synchronous rectification type. When the current is high,
at high speed, there are increases in the switching-loss in the
the conduction losses in the MOSFET and the inductor play
MOSFET, the reverse recovery loss of the body diode of the
major roles. This is because the power loss is proportional to
MOSFET, the output capacitance loss in the MOSFET, and the
the square of the current, as shown in the equations (3), (4),
dead time loss. Since these MOSFET-related losses increase
and (14). These losses can be reduced by using MOSFETs
in proportion to the switching frequency as shown in the
with a low on-resistance and by selecting inductors with a low
equations (5), (7), and (8), it is necessary to select an element
DCR. Since parts with lower conduction resistance are
that has a low capacitance and that performs switching
generally larger in size, this selection is a trade-off between
operations at high speed. As mentioned above, although the
conduction loss and size. In addition, the parasitic capacitance
capacitance value and the loss can be reduced by using a
describe below typically increases as the MOSFET size
smaller MOSFET, the current capability is also reduced in
increases, causing another trade-off. At low currents, there is
general, causing a trade-off between the output current value
a greater impact from the switching-loss in the MOSFET, the
and the size. To reduce the dead time loss, it is necessary to
output capacitance loss in the MOSFET, the gate charge loss
shorten the dead time by using a design that operates the
in the MOSFET, and the operation loss of the IC. These
control circuit at high speed—i.e., by combining the control
MOSFET-related losses are affected mainly by the parasitic
circuit with a MOSFET that can operate at high speed.
capacitance values based on the equations (5), (8), (10), and
(11). Although the capacitance value and the loss can be Figure 6 shows the behavior when the output voltage is varied
reduced by using a smaller MOSFET, the current capability is in the synchronous rectification type. This figure illustrates the
also reduced in general, causing a trade-off between the change in the duty ratio of the switching. To make it easier to
output current value and the size. In addition, since these understand, the input voltage is set to 10 V, resulting in duty
values are proportional to the switching frequency, the method ratios of 10% and 20% for output voltages of 1 V and 2 V,
10/15

respectively. It is shown that the on-time of the low-side
MOSFET becomes longer with a lower duty ratio, increasing
the conduction loss in the low-side MOSFET, while the on-time
of the high-side MOSFET becomes longer with a higher-duty
ratio, increasing the conduction loss in the high-side MOSFET.
Figure 7 shows the same behavior as in Figure 6, with the
converter replaced by a non-synchronous type. In comparison
with the synchronous type in Figure 6, the conduction loss is
greater in the diode that corresponds to the low-side MOSFET
in the synchronous type. It is also shown that, when the duty
ratio is higher, the difference in the loss between the
synchronous and non-synchronous rectification types is
smaller, since the on-time of the high-side MOSFET becomes
longer. Also, loss in the non-synchronous type become greater
as the duty ratio decreases, since the diode on-time becomes
longer. To reduce such loss, it is necessary to select parts with
diodes that have a lower forward direction voltage.
11/15

100%
90%
80%
出Ou力tpコutン cデapンacサitaのn損ce失 loss
入Inp力utコ cンapデaンcitサanのce損 lo失ss
O
IT 70% イCoンnダduクcタtioのn 伝los導s 損in失 the inductor
A
R IOCpのer動at作ion損 lo失ss caused by the IC
N O 60% ゲGaーteト c電ha荷rg損e 失loss
IT
デDeッaドdタ tiイmムe l損os失s
P 50% MOuOtSpuFtE cTa出pa力ci容tan量ce損 l失oss in the MOSFET
IS
S ロReーveサrsイeド rボecデovィeーryダ loイssオ inー tドhe逆 lo回w復-s損ide失 body diode
ID
40% ロSwーitサchイinドg-MloOssS FinE tTh eス loイwッ-チsidイeン MグO損SF失ET
E
W
ハSwイitサchイinドg-MloOssS FinE tTh eス hイigッhチ-siンdeグ M損O失SFET
O 30% ロCoーnサduイctドioMn OloSsFs EinT th伝e導 lo損w-失side MOSFET
P
ハCoイnサduイctドioMn OloSsFs EinT th伝e導 hi損gh失-side MOSFET
20%
10%
0%
0.1 0.2 0.4 0.7 1 2 4 7 10
OUTPUT CURRENT : I [A]
20 100 VIN = 12V
VOUT = 5V
18 90
fSW = 1MHz
16 80 L = 4.7μH (DCR = 80mΩ)
]
[
d 14 70
High-side MOSFET RON = 100mΩ
:
N
O 12 60
]%
η
Low-side MOSFET RON = 70mΩ
IT :
Y
P 10 50
IS N
8 40
IC
IF
E E
W 6 30
4 20
2 10
0 0
0.1 0.2 0.4 0.7 1 2 4 7 10
OUTPUT CURRENT : I [A]
Figure 4. Change in loss when output current is varied
(Synchronous rectification type)
12/15

O出u力tpコutン cデapンacサitaのn損ce失 loss
70%
I入np力utコ cンapデaンcitサanのce損 lo失ss
Cイoンnダduクcタtioのn 伝los導s 損in 失the inductor
60%
OICpのer動at作ion損 lo失ss caused by the IC
IT Gゲaーteト c電ha荷rg損e 失loss
P 50% Dデeッaドd タtiイmムe l損os失s
OMuOtSpuFtE cTa出pa力ci容tan量ce損 lo失ss in the MOSFET
40% Rロeーveサrsイeド reボcデovィeーry ダloイssオ inー thドe逆 lo回w復-si損de失 body diode
E Sロwーitサchイinドg-MloOssS FinE tTh eス loイwッ-sチidイeン MグO損SF失ET
30% Sハwイitサchイinドg-MloOssS FinE tTh eス hイigッhチ-siンdeグ M損O失SFET
P CロoーndサuイctドioMn OloSssF EinT t h伝e導 lo損w-失side MOSFET
20% CハoイndサuイctドioMn OloSssF EinT t h伝e導 hi損gh失-side MOSFET
SWITCHING FREQUENCY : f [Hz]
2.0 100 VIN = 12V
1.8 90
VOUT = 5V
IO = 1A
1.6 80
] L = 4.7μH (DCR = 80mΩ)
[ d 1.4 70 High-side MOSFET RON = 100mΩ
P ]%
N 1.2 60
O :
IT Y
A 1.0 50 C
P N
IS E
S 0.8 40
ID IF
R E 0.6 30
0.4 20
0.2 10
0.0 0
SWITCHING FREQUENCY : f [Hz]
Figure 5. Change in loss when switching frequency is varied
13/15

入Inp力utコ cンapデaンcitサanのce損 lo失ss
IT 70% イCoンnダduクcタtioのn 伝los導s 損in失 the inductor
R IOCpのer動at作ion損 lo失ss caused by the IC
N O 60% ゲGaーteト c電ha荷rg損e 失loss
デDeッaドdタ tiイmムe l損os失s
P 50% MOuOtSpuFtE cTa出pa力ci容tan量ce損 lo失ss in the MOSFET
S ロReーveサrsイeド reボcデovィeーry ダloイssオ inー tドhe逆 lo回w復-s損ide失 body diode
40% ロSwーitサchイinドg-MloOssS FinE tTh eス loイwッ-sチidイeン MグO損SF失ET
E ハSwイitサchイinドg-MloOssS FinE tTh eス hイigッhチ-siンdeグ M損O失SFET
O 30% ロCoーnサduイctドioMn OloSsFs EinT t h伝e導 lo損w-失side MOSFET
ハCoイnサduイctドioMn OloSsFs EinT t h伝e導 hi損gh失-side MOSFET
1 2 3 4 5 6 7 8 9
OUTPUT VOLTAGE : V [V]
1.0 100 VIN = 10V
0.9 90
0.8 80 L = 4.7μH (DCR = 80mΩ)
] W High-side MOSFET RON = 100mΩ
d
0.
.6
7
6
7
[ η
IT Y
A 0.5 50 C
IS E
S IC
ID 0.4 40 IF
R F
E E
W 0.3 30
0.2 20
0.1 10
Figure 6. Change in loss when output voltage is varied
14/15

IT 70% 入Inp力utコ cンapデaンcitサanのce損 lo失ss
R イCoンnダduクcタtioのn 伝los導s 損in失 the inductor
N 60%
O IOCpのer動at作ion損 lo失ss caused by the IC
A ゲGaーteト c電ha荷rg損e 失loss
P 50%
MOuOtSpuFtE cTa出pa力ci容tan量ce損 l失oss in the MOSFET
40% ダReイvオerーseド r逆ec回ov復er損y l失oss in the diode
MSwOiStcFhEinTg -スloイssッ iチn tンheグ M損O失SFET
O 30% ダCoイnオduーctドion伝 lo導s損s i失n the diode
MCoOnSdFuEctTio 伝n l導os損s i失n the MOSFET
1.0 100 VIN = 10V
0.9 90
L = 4.7μH (DCR = 80mΩ)
0.8 80
MOSFET RON = 100mΩ
]
d
0.7 70
N 0.6 60
O :
A 0.5 50
Y
ID 0.4 40 IF
E 0.3 30
0.2 20
0.1 10
Figure 7. Change in loss when output voltage is varied
(Non-synchronous rectification type)
15/15

Notice
Notes
1) The information contained herein is subject to change without notice.
2) Before you use our Products, please contact our sales representativeand verify the latest specifica-
tions :
3) Although ROHM is continuously working to improve product reliability and quality, semicon-
ductors can break down and malfunction due to various factors.
Therefore, in order to prevent personal injury or fire arising from failure, please take safety
measures such as complying with the derating characteristics, implementing redundant and
fire prevention designs, and utilizing backups and fail-safe procedures. ROHM shall have no
responsibility for any damages arising out of the use of our Poducts beyond the rating specified by
ROHM.
4) Examples of application circuits, circuit constants and any other information contained herein are
provided only to illustrate the standard usage and operations of the Products. The peripheral
conditions must be taken into account when designing circuits for mass production.
5) The technical information specified herein is intended only to show the typical functions of and
examples of application circuits for the Products. ROHM does not grant you, explicitly or implicitly,
any license to use or exercise intellectual property or other rights held by ROHM or any other
parties. ROHM shall have no responsibility whatsoever for any dispute arising out of the use of
such technical information.
6) The Products specified in this document are not designed to be radiation tolerant.
7) For use of our Products in applications requiring a high degree of reliability (as exemplified
below), please contact and consult with a ROHM representative : transportation equipment (i.e.
cars, ships, trains), primary communication equipment, traffic lights, fire/crime prevention, safety
equipment, medical systems, servers, solar cells, and power transmission systems.
8) Do not use our Products in applications requiring extremely high reliability, such as aerospace
equipment, nuclear power control systems, and submarine repeaters.
9) ROHM shall have no responsibility for any damages or injury arising from non-compliance with
the recommended usage conditions and specifications contained herein.
10) ROHM has used reasonable care to ensure the accuracy of the information contained in this
document. However, ROHM does not warrants that such information is error-free, and ROHM
shall have no responsibility for any damages arising from any inaccuracy or misprint of such
information.
11) Please use the Products in accordance with any applicable environmental laws and regulations,
such as the RoHS Directive. For more details, including RoHS compatibility, please contact a
ROHM sales office. ROHM shall have no responsibility for any damages or losses resulting
non-compliance with any applicable laws or regulations.
12) When providing our Products and technologies contained in this document to other countries,
you must abide by the procedures and provisions stipulated in all applicable export laws and
regulations, including without limitation the US Export Administration Regulations and the Foreign
Exchange and Foreign Trade Act.
13) This document, in part or in whole, may not be reprinted or reproduced without prior consent of
ROHM.
Thank you for your accessing to ROHM product informations.
More detail product informations and catalogs are available, please contact us.
ROHM Customer Support System
http://www.rohm.com/contact/
www.rohm.com
R1102B
© 2016 ROHM Co., Ltd. All rights reserved.