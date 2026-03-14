---
source: "TI SZZA043 -- CMOS Unbuffered Inverter in Oscillator Circuits"
url: "https://www.ti.com/lit/pdf/szza043"
format: "PDF 25pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 32131
---

Application Report

Use of the CMOS Unbuffered Inverter in Oscillator Circuits
Moshiul Haque and Ernest Cox Standard Linear & Logic
ABSTRACT
CMOS devices have a high input impedance, high gain, and high bandwidth. These
characteristics are similar to ideal amplifier characteristics and, hence, a CMOS buffer or
inverter can be used in an oscillator circuit in conjunction with other passive components.
Now, CMOS oscillator circuits are widely used in high-speed applications because they are
economical, easy to use, and take significantly less space than a conventional oscillator.
Among the CMOS devices, the unbuffered inverter (’U04) is widely used in oscillator
applications. This application report discusses the performance of some TI ’U04 devices in
a typical crystal-oscillator circuit.
Contents
1 Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2 Theory of Oscillators . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2.1 Characteristics of Crystals . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
3 Buffered and Unbuffered CMOS Inverters in Oscillator Circuits . . . . . . . . . . . . . . . . . . . . . . . . . 6
4 Characteristics of a CMOS Unbuffered Inverter . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
4.1 Open-Loop Gain . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
4.2 V vs V . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
O I
4.3 I vs V . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
CC I
4.4 Variation of Duty Cycle With Temperature . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
5 Characteristics of LVC1404 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
6 Practical Oscillator Circuits . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
6.1 Selection of Resistors and Capacitors . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
6.1.1 R . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
F
6.1.2 R . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
S
6.1.3 C and C . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
1 2
7 Practical Design Tips . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
Appendix A. Laboratory Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
A.1 Laboratory Setup to Measure Open-Loop-Gain Characteristics . . . . . . . . . . . . . . . . . . . . . . . . 18
A.2 Laboratory Setup to Measure I vs V Characteristics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
Appendix B. LVC1GU04 in Crystal-Oscillator Applications . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
B.1 LVC1GU04 in 25-MHz Crystal-Oscillator Circuit . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
B.2 LVC1GU04 in 10-MHz Crystal-Oscillator Circuit . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
B.3 LVC1GU04 in 2-MHz Crystal-Oscillator Circuit . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
B.4 LVC1GU04 in 100-kHz Crystal-Oscillator Circuit . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22
Trademarks are the property of their respective owners.
1

SZZA043
Appendix C. LVC1404 in Crystal-Oscillator Applications . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
C.1 LVC1404 in 25-MHz Crystal-Oscillator Circuit . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
C.2 LVC1404 in 100-kHz Crystal-Oscillator Circuit . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
List of Figures
1 Oscillator . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2 Electrical-Equivalent Circuit of a Crystal . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
3 Pierce Oscillator Using CMOS Inverter . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
4 Open-Loop-Gain Characteristics of LVC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
5 Open-Loop-Gain Characteristics of AHC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
6 Open-Loop-Gain Characteristics of AUC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
7 V vs V Characteristics of LVC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
8 V vs V characteristics of AHC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
9 V vs V Characteristics of AUC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
10 I vs V Characteristics of LVC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
11 I vs V Characteristics of AHC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
12 I vs V Characteristics of AUC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
13 Duty-Cycle Variation in LVC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
14 Duty-Cycle Variation in AHC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
15 Duty−Cycle Variation in AUC1GU04 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
16 Pinout Diagram for LVC1404 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
17 Logic Diagram of LVC1404 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
18 Open-Loop-Gain Characteristics of LVC1404 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
19 Pierce Oscillator Circuit Using Unbuffered CMOS Inverter . . . . . . . . . . . . . . . . . . . . . . . . . . 13
20 Effect of R on Oscillator Waveform (No Load) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
21 Effect of R on Oscillator Waveform (R = 1 k(cid:1)) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
S L
22 Effect of R on the Frequency Response of Feedback Network . . . . . . . . . . . . . . . . . . . . . 15
23 Effect of R on the Phase Response of Feedback Network . . . . . . . . . . . . . . . . . . . . . . . . . 15
24 Oscillator Circuit Using a Schmitt-Trigger Input Inverter . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
A-1 Open-Loop-Gain Measurement Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
A-2 I vs V Measurement Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
B-1 Effect of R on Duty Cycle and I (Frequency = 25 MHz) . . . . . . . . . . . . . . . . . . . . . . . . . 19
S CC
B-2 Effect of R on Duty Cycle and I (Frequency = 10 MHz) . . . . . . . . . . . . . . . . . . . . . . . . . 20
B-3 Effect of R on Duty Cycle and I (Frequency = 2 MHz) . . . . . . . . . . . . . . . . . . . . . . . . . . 21
B-4 Effect of R on Duty Cycle and I (Frequency = 100 kHz) . . . . . . . . . . . . . . . . . . . . . . . . 22
C-1 Output Waveform of Oscillator Circuit Using LVC1404 (Frequency = 25 MHz) . . . . . . . . . 23
C-2 Output Waveform of Oscillator Circuit Using LVC1404 (Frequency = 100 kHz) . . . . . . . . 24
List of Tables
B-1 Effect of R on Duty Cycle and I (Frequency = 25 MHz) . . . . . . . . . . . . . . . . . . . . . . . . . 19
B-2 Effect of R on Duty Cycle and I (Frequency = 10 MHz) . . . . . . . . . . . . . . . . . . . . . . . . . 20
B-3 Effect of R on Duty Cycle and I (Frequency = 2 MHz) . . . . . . . . . . . . . . . . . . . . . . . . . . 21
B-4 Effect of R on Duty Cycle and I (Frequency = 100 kHz) . . . . . . . . . . . . . . . . . . . . . . . . 22
2 Use of the CMOS Unbuffered Inverter in Oscillator Circuits

1 Introduction
Resistors, inductors, capacitors, and an amplifier with high gain are the basic components of an
oscillator. In designing oscillators, instead of using discrete passive components (resistors,
inductors, and capacitors), crystal oscillators are a better choice because of their excellent
frequency stability and wide frequency range. A crystal basically is an RLC network that has a
natural frequency of resonance.
2 Theory of Oscillators
In principle, an oscillator can be composed of an amplifier, A, with voltage gain, a, and phase
shift, α, and a feedback network, F, with transfer function, f, and phase shift, β (see Figure 1).
V1 V2
Amplifier, A
a, (cid:1)
Feedback Network, F
f, (cid:2)
Figure 1. Oscillator
For |f|(cid:1)|(cid:1)| (cid:2) 1 the oscillating condition is fulfilled, and the system works as an oscillator.
f and a are complex quantities; consequently, it is possible to derive from equation 1
|f|(cid:1)|(cid:1)|(cid:1)exp (cid:3) j (cid:4)(cid:1)(cid:5)(cid:2)(cid:6) (cid:2) 1 (cid:7) (1)
the amplitude
|f|(cid:1)|(cid:1)| (cid:2) 1 (2)
and the phase
(cid:4)(cid:1)(cid:5)(cid:2)(cid:6) (cid:8) 2(cid:1)(cid:3) (3)
To oscillate, these conditions of amplitude and phase must be met. These conditions are known
as the Barkhausen criterion. The closed-loop gain should be ≥1, and the total phase shift of 360
degrees is to be provided.
2.1 Characteristics of Crystals
Figure 2 is an electrical-equivalent circuit of a quartz crystal.
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 3

C L
R
C0
Figure 2. Electrical-Equivalent Circuit of a Crystal
The quantities C and L are determined by the mechanical characteristics of the crystal; R is the
resistance of the resonant circuit at the series resonance, and C represents the capacitance of
o
the leads and electrodes. C is much larger than C and is affected by the stray capacitances of
the final circuit. Because R is negligible, the impedance of this circuit is given by equation 4.
Z (cid:8) (cid:4) j (cid:1) (C (cid:5) (cid:4) C 2L ) C (cid:9) (cid:9) (cid:4)(cid:4) 1 2LCC (cid:6) (4)
o o
A series-resonance frequency is attained when the impedance, Z, approaches 0, Z→ 0
=
f
ser 2 (cid:1) LC (5)
A parallel-resonance frequency is attained when the impedance, Z, approaches∞, Z → ∞
C
f f 1 +
par ser C (6)
An oscillator circuit using the parallel resonance mode of the crystal is less stable than the
equivalent circuit using the series resonance, because of the dependence on the external circuit
parameter. For series resonance, the crystal appears as a series-resonant resistance, R. For
parallel resonance, the crystal appears as an inductive load.
In the oscillator circuit, the crystal acts as the feedback network. For proper operation, the input
impedance of the amplifier should be well matched to the low series-resonant resistance of the
crystal. For HCMOS devices, because of the high input impedance, a crystal operated in series
resonance would be completely mismatched. The solution is to operate the crystal in
parallel-resonance mode. But, parallel resonance has a poor frequency response compared to
series resonance because of the dependence on C (stray capacitance or circuit capacitance).
Connecting a capacitance in parallel (C ) with the crystal can reduce the influence of C on the
P o
parallel-resonance frequency. From the equation of the parallel-resonance frequency
1 C
f 1 + +
par 2 (cid:1) LC C p C o (7)
4 Use of the CMOS Unbuffered Inverter in Oscillator Circuits

By choosing C > C (C is approximately 3 pF to 5 pF, and C typically is 30 pF).
P o o P
C >> C (C is in the range of femtofarads)
P
≈
f
par (cid:1)
2 LC (8)
Now, the parallel-resonance frequency is approximately equal to the series-resonance
frequency.
A popular application of the parallel-resonance circuit is the Pierce oscillator circuit (see
Figure 3) in which the parallel combination of C and C constitutes C .
1 2 P
CC
C = 1 2
P C + C
(9)
and C
2
form a capacitor voltage divider that determines the degree of feedback. The
feedback factor is given by
f (cid:8) 1 (10)
RF
CMOS Inverter
C1 Crystal C2
Figure 3. Pierce Oscillator Using CMOS Inverter
The optimal value for C determines the quality and frequency stability of the crystal oscillator.
p
Usually, the crystal manufacturer’s data sheet specifies the recommended load for the crystal
(C ). C represents the load for the crystal, and this should be equal to C , as specified in the
L p L
crystal manufacturer’s data sheet.
In an oscillator circuit, the CMOS inverter operates in the linear mode and works as an amplifier.
The phase shift provided by the inverter is 180 degrees. To meet the oscillating condition, the
crystal oscillator must provide an additional 180 degrees of phase shift. If C
= C
, current
through them is identical and 180 degrees out of phase from each other. Hence, for C
= C
, the
crystal provides a phase shift of 180 degrees.
The feedback resistor modifies the input impedance of the CMOS inverter. For an inverter with
an open-loop gain much higher than 1, the input impedance becomes
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 5

Z (cid:8) (cid:1) F (11)
i
The parallel-resonance resistance of the crystal is modified by the load capacitor, C .
p R(cid:2) 2(C + C)2 (12)
o p
R should match the input impedance of the CMOS inverter. For example, if a crystal oscillator
has the following parameters:
C = C = 30 pF
p L
C = 7 pF
R = 80 Ω at 5 MHz
R (cid:8) (cid:3) 1 (cid:7) (13)
80(cid:1)(cid:4) 2(cid:1)(cid:3)(cid:1)5(cid:1)106 (cid:6)2 (cid:1)(cid:4) 30(cid:1)10(cid:9)12(cid:5)7(cid:1)10(cid:9)12 (cid:6)2
From the calculation
R (cid:10) 10 k(cid:5)
R should be equal to Z, i.e.,
p i
Z (cid:8) R (cid:8) 10 k(cid:5)
i p
Z (cid:8) (cid:1) F(cid:8) 10 k(cid:5)
i
Z = F
i a = 10 kΩ
R (cid:8) 10 k(cid:5)(cid:1)(cid:1)
For a CMOS inverter with an open-loop gain, a = 100, the value of the feedback resistor is
calculated as:
R (cid:8) 10000(cid:1)100 (cid:8) 1(cid:1)106 (cid:8) 1 M(cid:5) (14)
By using a feedback resistor of 1 M(cid:1), successful oscillation can be accomplished. In practical
applications, the value of the feedback resistor usually will be greater than 1 M(cid:1) in order to
attain higher input impedance, so the crystal can easily drive the inverter.
3 Buffered and Unbuffered CMOS Inverters in Oscillator Circuits
Unbuffered inverters have a single inverting stage, and the gain of this type of inverter is in the
range of hundreds. Buffered inverters have more than one stage, and the gain is in the range of
several thousand. In the buffered inverter, power consumption usually is less than in the
unbuffered inverter, because the first and the second inverter stages consume significantly less
power-supply current than the output stage. Because the first stage remains in linear mode
during oscillation, a buffered inverter consumes less power than an unbuffered inverter. Both
buffered and unbuffered inverters can be used for oscillator applications, with only slight design
changes. Because the gain of buffered inverters is very high, they are sensitive to parameter
changes in the oscillator circuit and are less stable than unbuffered inverters.
6 Use of the CMOS Unbuffered Inverter in Oscillator Circuits

4 Characteristics of a CMOS Unbuffered Inverter
The choice of a CMOS inverter for oscillator applications depends on various factors, for
example open-loop gain, power consumption, duty-cycle variation with temperature, etc. In the
following paragraphs, some of these characteristics of TI CMOS inverters that are critical in
selecting an inverter for oscillator application are described.
4.1 Open-Loop Gain
A CMOS inverter is used as a linear amplifier in oscillator applications and, similar to a
conventional amplifier, their open-loop gain is a critical characteristic. The bandwidth of an
inverter decreases as the operating voltage decreases. The open-loop gain of the LVC1GU04,
AHC1GU04, and AUC1GU04 is shown in Figures 4, 5, and 6.
VCC = 1.8 V
Frequency − MHz
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 7
VBd
−
niaG
30
25
20
15 VCC = 5 V
10 VCC = 3.3 V
VCC = 2.7 V
5
0 VCC = 2 V
−5
−10
0.1 1 10 100
Figure 4. Open-Loop Gain Characteristics of LVC1GU04
15
10
VCC = 5 V
5 VCC = 3.3 V
0
−5 VCC = 2 V
Figure 5. Open-Loop Gain Characteristics of AHC1GU04

8 Use of the CMOS Unbuffered Inverter in Oscillator Circuits
10 VCC = 2.5 V
VCC = 2 V
VCC = 1.5 V
−10 VCC = 1 V
0.1 1 10 100VCC = 0.8 V
Figure 6. Open-Loop Gain Characteristics of AUC1GU04
4.2 V vs V
V vs V characteristics can be used to determine the bias point of the inverter. In the oscillator
application, the inverter operates in the linear mode or in the transition region. The transition
region is defined as the region where the slope of the curve is maximum. For example, for the
LVC1GU04, the region is between 2 V and 2.5 V for V = 5 V. A device with a higher open-loop
gain will have a narrower transition region compared to the transition region of a device with
lower open-loop gain. V vs V characteristics of the LVC1GU04, AHC1GU04, and AUC1GU04
are shown in Figures 7, 8, and 9.
4
VCC = 3.3 V VCC = 5 V
3 VCC = 2.7 V
0 1 2 3 4
VI − V
V
OV
Figure 7. V vs V Characteristics of LVC1GU04

3
0 1 2 3 4
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 9
VCC = 3 V
Figure 8. V vs V Characteristics of AHC1GU04
2.5
VCC = 2.5 V
1.5
1 VCC = 1 V
0.5
VCC = 0.8 V
0 0.5 1 1.5 2
Figure 9. V vs V Characteristics of AUC1GU04
4.3 I vs V
I vs V characteristics of the LVC1GU04, AHC1GU04, and AUC1GU04 are shown in Figures
10, 11, and 12. This characteristic determines the dynamic power consumption of the inverter in
the oscillator circuit. The setup is shown in Appendix A. Due to the 1-kΩ load, I is high when
V is 0.
I
70
60
50
40
0 1 2 3 4 5
Am
CCI
VCC = 3.3 V
Figure 10. I vs V Characteristics of LVC1GU04

10 Use of the CMOS Unbuffered Inverter in Oscillator Circuits
0 1 2 3 4 5
Figure 11. I vs V Characteristics of AHC1GU04
VCC = 1 V
0 0.5 1 1.5 2
Figure 12. I vs V Characteristics of AUC1GU04
4.4 Variation of Duty Cycle With Temperature
One of the primary concerns in the oscillator application is the variation of duty cycle with
temperature. For example, in the clock-pulse generator circuits, too much variation of the duty
cycle with the temperature is not permitted. Figures 13, 14, and 15 show the variation of duty
cycle with temperature for the LVC1GU04, AHC1GU04, and AUC1GU04.
49
%
elcyC
ytuD
48.5
48 VCC = 3.3 V
47.5
47 VCC = 2.2 V
46.5
46
−50 −25 0 25 50 75 100
Temperature − (cid:1)C
Figure 13. Duty-Cycle Variation in LVC1GU04

51
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 11
50
49
48 VCC = 2.7 V
47
VCC = 2.2 V
Figure 14. Duty-Cycle Variation in AHC1GU04
47
VCC = 2.0 V
46.5 VCC = 1.5 V
VCC = 1.2 V
45.5
45
Figure 15. Duty-Cycle Variation in AUC1GU04
5 Characteristics of LVC1404
The TI LVC1404 is a dual inverter gate that is very suitable for oscillator applications. This
device has a wide V range and can be used for a wide range of frequencies. The device has
both unbuffered and buffered outputs. Figure 16 shows the pinout diagram and Figure 17
shows the logic diagram for LVC1404.
CTRL 1 8 V CC
XOUT 2 7 OSCOUT
XIN 3 6 A
GND 4 5 Y
Figure 16. Pinout Diagram for LVC1404
As shown in Figure 17, XIN is connected to an unbuffered inverter, and the output of this inverter
(XOUT) is connected to the input of another inverter to get a clean rail-to-rail signal and to
provide sufficient drive capability. The crystal is connected between the XIN and XOUT.

CTRL
3 7
XIN OSCOUT
XOUT
6 5
A Y
Figure 17. Logic Diagram of LVC1404
Figure 18 shows the open-loop-gain characteristics of the unbuffered inverter of the LVC1404
(i.e., between XIN and XOUT). The device provides a high gain over a wide range of
frequencies.
12 Use of the CMOS Unbuffered Inverter in Oscillator Circuits
10 VCC = 3.3 V
Figure 18. Open-Loop-Gain Characteristics of LVC1404
6 Practical Oscillator Circuits
Figure 19 shows an example of an oscillator circuit that uses a 16-pF, 25-MHz crystal and an
unbuffered inverter, LVC1GU04. In actual applications, the passive components may require
adjustment to get the desired oscillation. For example, C
and C
can be adjusted to take into
consideration the input and output capacitance of the LVC1GU04 and the desired duty cycle of
oscillation.
Appendixes B and C show the performance of TI’s LVC1GU04 and LVC1404 devices in this
Pierce crystal-oscillator circuit.

~2.2 M(cid:3)
SN74LVC1GU04
RS
~1 k(cid:3)
C1 C2
~32 pF CL ~32 pF
16 pF
Figure 19. Pierce Oscillator Circuit Using Unbuffered CMOS Inverter
6.1 Selection of Resistors and Capacitors
Selection of resistors and capacitors depends on various factors, such as inverter gain,
frequency stability, power consumption, crystal characteristics, startup time, etc. Several
trial-and-error methods may be needed to find optimum values for these resistors and
capacitors. The effects of these components are discussed in the following paragraphs.
6.1.1 R
R is the feedback resistor of the CMOS inverter and it biases the inverter in its linear region.
The chosen value of R is sufficiently large so that the input impedance of the inverter and the
crystal can be matched. Usually, the value chosen is between 1 M(cid:1) and 10 M(cid:1).
6.1.2 R
R isolates the output of the inverter from the crystal and prevents spurious high-frequency
oscillation, so that a clean waveform can be obtained. The optimum value of R depends on the
frequency of operation and the required stability.
The minimum value of R depends on the recommended power consumption of the crystal.
Crystal manufacturers usually specify a recommended value of R in the crystal data sheet.
Using a value lower than that in the crystal data sheet may cause overdriving of the crystal and
result in damage to the crystal or shorten the crystal life.
Acceptable results can be accomplished by choosing the value to be approximately equal to the
capacitive reactance, i.e., R (cid:10) X , provided X is greater than or equal to the manufacturer’s
S C C
2 2
recommended value. Making R (cid:10) X will cause a 50% voltage drop due to voltage-divider
S C
action. This requires that the gain of the inverter be equal to, or greater than, 2. Because the
gain of a CMOS inverter is much higher than 2, the closed-loop gain is still higher than unity. The
gain of a buffered inverter is considerably higher than an unbuffered inverter. If a buffered
inverter is used, R can be increased so that the closed-loop gain of the system is decreased
and stability is improved.
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 13

The effect of R is shown in Figures 20 and 21. Decreasing R results in a faster edge rate and
S S
increased closed-loop gain.
14 Use of the CMOS Unbuffered Inverter in Oscillator Circuits
egatloV
tuptuO
3.5
RS = 1 k(cid:3) (No Load)
RS = 3 k(cid:3) (No Load)
−0.5
20 40 60 80 100
Time − ns
Figure 20. Effect of R on Oscillator Waveform (No Load)
RS = 3 k(cid:3) (RL = 1 k(cid:3)(cid:4)
80 100
RS = 0 (cid:1) (RL = 1 k(cid:3)(cid:4)
−1
20 40 60
Figure 21. Effect of R on Oscillator Waveform (R = 1 k(cid:3))
S L
Figures 22 and 23 show the relative effect of the R on the gain and the phase response of the
feedback network of the oscillator circuit described in Figure 19. R not only reduces the gain,
but also shifts the resonance frequency and introduces additional phase delay.

RS = 240 (cid:3)
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 15
Bd−
−15
−20
RS = 3 k(cid:3)
−25
−30
24.98 24.99 25.00 25.01
Figure 22. Effect of R on the Frequency Response of Feedback Network
geD
esahP
−50
−100
−150
−200
−250
−300
24.98 24.99 25.00 25.01 25.02
Figure 23. Effect of R on the Phase Response of Feedback Network
R also affects the duty cycle and power consumption (I ) of the oscillator circuit. Appendix B
shows the effect of R on duty cycle and the power consumption (I ) in an oscillator circuit
using an LVC1GU04 as the amplifier.
At low frequency, phase shift due to the CMOS inverter is small and can be neglected. Phase
shift is given by equation 15.
Phase shift = Frequency of oscillation × Propagation delay × 360 degrees (15)
If the propagation delay of a CMOS inverter is 5 ns, then, at 25 MHz, the phase shift introduced
by the inverter is 45 degrees. For high frequency, using a series feedback resistor (R ) is not
feasible because it adds additional phase shift. R can be replaced by a capacitor whose value
is approximately equal to the input impedance of the crystal, i.e., C ≈ C .
s 2

6.1.3 C and C
The values of C and C are chosen such that the parallel combination of C and C equals the
1 2 1 2
recommended capacitive load (C ) specified in the crystal data sheet, i.e.:
L
C C
C = 1 2
L C + C
R and C form a low-pass filter and reduce spurious oscillation. The value can be adjusted,
S 2
based on the desired cutoff frequency. Another factor in choosing C is the start-up time. For a
low-gain amplifier, sometimes C
is increased over C
to increase the phase-shift and help in
start-up, but C should be within a limit such that the load capacitance introduced to the crystal
does not exceed the manufacturer’s recommended value of C . Otherwise, the resonance
L
frequency will change.
7 Practical Design Tips
The performance of an oscillator circuit using a CMOS inverter is sensitive to the circuit
components, layout etc. In designing an oscillator circuit, careful attention should be given to
eliminate external effects:
•
The oscillator circuit feedback factor should not be too large; otherwise, there will be
instability, and oscillation will not be determined by the crystal alone.
A CMOS inverter with a Schmitt-trigger input is not suitable for use in the oscillator circuit
described previously. A Schmitt-trigger input device has two different thresholds, and it may
not be possible to bias them properly in the linear region using the circuit described
previously.
At higher frequencies, the ground lead to the central point of connection always should be as
large in area and as short in length as possible. This provides low resistance and low
inductance and, thereby, the effect on oscillation is less. Use of a multilayer board, with one
layer for V and one for ground, is preferable.
An unbuffered inverter itself may not have enough drive for a high-capacitive load. As a
result, the output voltage swing may not be rail to rail. This also will slow down the edge rate
of the output signal. To solve these problems, a buffer or inverter with a Schmitt-trigger input
can be used at the output of the oscillator. Examples of Schmitt-trigger input buffers and
inverters are the LVC1G17 and LVC1G14. Figure 24 shows an example circuit.
16 Use of the CMOS Unbuffered Inverter in Oscillator Circuits

~2.2 M(cid:3)
SN74LVC1GU04
RS
50 pF
~1 k(cid:3)
C1 C2
~32 pF CL ~32 pF
16 pF
Figure 24. Oscillator Circuit Using a Schmitt-Trigger Input Inverter
Good power-supply decoupling is necessary to suppress noise spikes on the supply line.
Low-resonance ceramic capacitors should be used as close to the circuit as possible. The
reference value is 100 nF.
Connections in the layout should be as short as possible to keep the resistance and
inductance low.
To reduce crosstalk, standard PCB design techniques should be used. For example, if the
signal is routed together with other signals, crosstalk can be reduced by a factor of 3 if there
is a ground line between adjacent signal lines.
Without a crystal, the oscillator should not oscillate. To check this, the crystal in a CMOS
oscillator can be replaced by its equivalent parallel-resonant resistance.
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 17

Appendix A. Laboratory Setup
A.1 Laboratory Setup to Measure Open-Loop Gain Characteristics
2.2 M(cid:3)
’U04
1 (cid:5)F
50 mV ~
Peak-to-Peak 50 (cid:3) 1 k(cid:3) 30 pF
Figure A−1. Open-Loop-Gain Measurement Setup
A.2 Laboratory Setup to Measure I vs V Characteristics
2.2 M(cid:3)
’U04
-+
1 k(cid:3)
Figure A−2. I vs V Measurement Setup
18 Use of the CMOS Unbuffered Inverter in Oscillator Circuits

Appendix B. LVC1GU04 in Crystal-Oscillator Applications
B.1 LVC1GU04 in 25-MHz Crystal-Oscillator Circuit
C (cid:10) C (cid:8) 30 pF
X = 200 (cid:5) (capacitive reactance at resonance frequency, i.e., 25 MHz)
V = 3.3 V
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 19
1 RS = 10 k(cid:3)
RS = 2 k(cid:3)
RS = 0
0 20 40 60 80
Figure B−1. Effect of R on Oscillator Waveform (Frequency = 25 MHz)
Table B−1. Effect of R
on Duty Cycle and I
(Frequency = 25 MHz)
RS ICC Positive
((cid:3)) (mA) Duty Cycle
(%)
0 22.2 43
240 11.1 45.9
2 k 7.3 47.3
10 k 8.6 46.7

B.2 LVC1GU04 in 10-MHz Crystal-Oscillator Circuit
C (cid:10) C (cid:8) 30pF
X = 480 (cid:1) (capacitive reactance at resonance frequency, i.e., 10 MHz)
RS = 10 k(cid:3)
20 Use of the CMOS Unbuffered Inverter in Oscillator Circuits
0 RS = 450 (cid:3)
0 50 100 150 200
Figure B−2. Effect of R on Oscillator Waveform (Frequency = 10 MHz)
Table B−2. Effect of R
on Duty Cycle and I
(Frequency = 10 MHz)
Positive
RS ICC
Duty Cycle
((cid:3)) (mA)
450 6.9 40
3 k 8.4 47.6
10 k 15.1 43.9

B.3 LVC1GU04 in 2-MHz Crystal-Oscillator Circuit
X = 2.4 k(cid:1) (capacitive reactance at resonance frequency, i.e., 2 MHz)
RS = 10 k(cid:3)
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 21
0 RS = 2 k(cid:3)
0 200 400 600 800
Figure B−3. Effect of R on Oscillator Waveform (Frequency = 2 MHz)
Table B−3. Effect of R on Duty Cycle and I (Frequency = 2 MHz)
240 11.1 45.9
2 k 7.3 47.3
10 k 8.6 46.7

B.4 LVC1GU04 in 100-kHz Crystal-Oscillator Circuit
X = 48 k(cid:1) (capacitive reactance at resonance frequency, i.e., 100 kHz)
0.5 RS = 220 k(cid:3)
RS = 100 k(cid:3)
0 RS = 50 k(cid:3)
0 5 10 15 20
22 Use of the CMOS Unbuffered Inverter in Oscillator Circuits
Time − (cid:5)s
Figure B−4. Effect of R on Oscillator Waveform (Frequency = 100 kHz)
Table B−4. Effect of R on Duty Cycle and I (Frequency = 100 kHz)
50 k 9 46.4
100 k 9.5 46.1
220 k 13.7 44.3

Appendix C. LVC1404 in Crystal-Oscillator Applications
C.1 LVC1404 in 25-MHz Crystal-Oscillator Circuit
=X = 200 (cid:1) (capacitive reactance at resonance frequency, i.e., 25 MHz)
I = 8.6 mA
Duty cycle = 48.1%
0 10 20 30 40
Use of the CMOS Unbuffered Inverter in Oscillator Circuits 23
50 60 70
Figure C−1. Output Waveform of Oscillator Circuit Using LVC1404 (Frequency = 25 MHz)

C.2 LVC1404 in 100-kHz Crystal-Oscillator Circuit
=X = 48 k(cid:1) (capacitive reactance at resonance frequency, i.e., 100 kHz)
I = 5.7 mA
Duty cycle = 47.4%
0 2 4 6 8
24 Use of the CMOS Unbuffered Inverter in Oscillator Circuits
10 12 14
Time − (cid:5)s
Figure C−2. Output Waveform of Oscillator Circuit Using LVC1404 (Frequency = 100 kHz)
