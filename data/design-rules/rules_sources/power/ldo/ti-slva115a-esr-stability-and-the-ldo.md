---
source: "TI SLVA115A -- ESR, Stability, and the LDO"
url: "https://www.ti.com/lit/an/slva115a/slva115a.pdf"
format: "PDF 7pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 8842
---

Application Report

ESR, Stability, and the LDO Regulator
Jeff Falin, John Cummings ............................................................................................... Linear Power
ABSTRACT
Choosing an output capacitor for LDO with PNP or PMOS pass element can be difficult due to
regulators
specific ESR requirements. This application report explains how ESR impacts stability and how to
determine whether or not the regulator is stable.
Contents
1 Introduction ................................................................................................................... 1
2 Conclusion.................................................................................................................... 6
List of Figures
1 Open Loop Response of Typical PMOS or PNP LDO Regulator ..................................................... 2
2 Typical ESR vs Output Current ............................................................................................ 2
3 Load Transient Setup ....................................................................................................... 3
4 TPS76050 Load Transient With 2.2-μF Ceramic Capacitor............................................................ 4
5 TPS76050 Load Transient With 2.2-μF Ceramic Capacitor and 1-Ω ESR........................................... 5
6 Load Transient (0.5 A) With 1-μF Output Capacitor .................................................................... 5
7 TPS7A26 Load Transient Response With a 100-µF Capacitor at the Output ....................................... 6

1 Introduction
As the typical PMOS or PNP open loop gain plot of Figure 1 shows, there are three important poles in a
PMOS or PNP pass element based LDO regulator. The dominant pole, P(DOM), is set in the error
amplifier of the regulator. The load pole, P(LOAD), is formed by the output capacitor and load and
therefore varies with load current. The pass device pole, P(PASS), is formed by the parasitic capacitance
of the pass element. In order for any negative feedback system to be stable, the open loop gain of the
system must be below 0 dB when the phase is 360° (180° of the fed-back signal plus the 180° from the
inverting input of the error amplifier). Stated another way, the system must have sufficient phase margin,
that is,, the amount of phase shift remaining until 360° degree when the gain is at 0 dB. Since each pole
contributes 90° of phase shift and 20 dB/decade (or –1) roll off in gain, a three-pole, high gain system
requires compensation in order to be stable. A regulator is unconditionally stable (that is, has sufficient
phase margin) if the open loop gain curve rolls off at 20 dB/decade (that is, like a single pole system)
before crosses 0 dB. The most common method of compensation is to insert a zero in the system to
cancel the phase shift and roll off of one of the poles. Since an LDO already requires an output capacitor
for normal operation, using the ESR of the output capacitor is typically the simplest and least expensive
method for generating this zero, see f in Figure 1.
Z(ESR)

100
80 Dominant
Pole, P(DOM)
Variation in R(LOAD) × C(LOAD)
d B 60 P(LOAD ) Pole
– f Z(ESR)
n
G
ai
40
p
o
o Variation in C(LOAD) × ESR
L
20
0 P(PASS)
PNP/PMOS
Pass-Device Pole
–20
10 100 1000 10 k 100 k 1 M 10 M
f – Frequency – Hz
Figure 1. Open Loop Response of Typical PMOS or PNP LDO Regulator
The challenge is choosing a capacitor with the correct amount of ESR. The ESR must be high enough to
lower the f frequency so that the gain slope is –20 dB/decade instead of –40 dB/decade (–2) when it
crosses 0 dB, but low enough so that the f frequency is high enough for the gain to be below 0 dB
before P .
(PASS)
In TI’s older regulator data sheets that were designed when tantalum or high-ESR capacitors were more
common, a minimum capacitor value is specified and an ESR vs output current for that output capacitor
(and usually another capacitor) is provided. Figure 2 shows a typical curve for the TPS76050 device.
NOTE: The ESR used in these plots is the minimum ESR of the capacitor as ESR does vary over
frequency.
TYPICAL REGION OF STABILITY
EQUIVALENT SERIES RESISTANCE
vs
OUTPUT CURRENT
20
10
µ
F)
Co = 2.2 µF
e
( TJ = 25°C
c
n
a
st
si
R e 1
s Region of Stability
ri
S
nt
al 0.2
v
ui
0.1
q
E
–
R Region of Instability
S
E
0.01
0 10 20 30 40 50
IO – Output Current – mA
Figure 2. Typical ESR vs Output Current

The curve of this device requires that, for the minimum 2.2-μF of output capacitance, the ESR must be
between 0.1 Ω and 20 Ω. Few capacitors have more than 2 Ω of ESR, so the upper limit on the ESR can
usually be ignored. The lower limit actually sets the maximum value for the f . For the case of 2.2-μF
capacitor referenced in Figure 2, use Equation 1 to calculate the maximum value:
f = 1/ (2 ´ p ´ R ´ C ) = 72.3 kHz
Z(ESR) ESR OUT
where
• R is 0.1 Ω
ESR
• C is 2.2 µF (1)
OUT
For an older LDO which depended on higer ESR for stability like the TPS760 device, a capacitance and
ESR product larger than 0.1 Ω × 2.2 × 10–6F = 2.2 × 10–7 ΩF (but less than 20 × 2.2 × 10–6 ΩF = 4.4 × 10–5
ΩF) is stable, as long as the capacitance is above the minimum required capacitance value.
The TPS760 was designed when tantalum capacitors were common and 1.1 mA was considered low I .
Q
For newer LDOs like the TPS7A25 device which have been designed to be optimized with low ESR or
ceramic capacitors, there is no need to be concerned about ESR unless you wish to use very large
capacitors for hold up.
Performing a load transient test and observing the amount of ringing on the output is the best way to
determine if the capacitor selected is stable. Figure 3 shows a test setup for a load transient test using a
MOSFET switch and function generator. This setup is preferable to most electronic loads because the
simulated transient is much faster.
ON
ENABLE
Current Probe
VIN = VOUT + 1 V LDO Analogic
VIN VOUT Waveform
Generator
DC _ + GND
Voltage Probe
Figure 3. Load Transient Setup

Figure 4 shows the measured results using a TPS76050 device with a 2.2-μF ceramic (low ESR)
capacitor. Figure 5 shows the measured results of a TPS76050 device with a 2.2-μF and a 1-Ω series
resistor. The results in Figure 4 show multiple oscillations or rings after the initial spike, indicating
instability, while the results in Figure 5 shows a stable load transient. Typically, four rings or less indicate
sufficient phase margin for the device to be stable.
Figure 4. TPS76050 Load Transient With 2.2-μF Ceramic Capacitor

Time (µsec)
)A(
tnerruC
tuptuO
AC-Coupled
Output
Voltage
(mV)

Figure 5. TPS76050 Load Transient With 2.2-μF Ceramic Capacitor and 1-Ω ESR
Comparing to the TPS7A25 device which is stable with a minimum of 1.0-µF ceramic capacitor with no
additional ESR, there are no oscillations at the output as Figure 6 shows.
2 200
1.8 100
1.6 0
1.4 -100
1.2 -200
1 -300
0.8 -400
0.6 -500
0.4 -600
0.2 -700
0 -800
I
-0.2 V -900
-0.4 -1000
-100 0 100 200 300 400 500 600
Figure 6. Load Transient (0.5 A) With 1-μF Output Capacitor

Figure 7 shows that the TPS7A26 device is even stable with a capacitor as large as 100 µF.
VIN
IOUT
VOUT
Figure 7. TPS7A26 Load Transient Response With a 100-µF Capacitor at the Output
2 Conclusion
When designing with older linear regulators, ESR is very important to consider when selecting the output
capacitor. As the ESR is a function of frequency, the minimum ESR is used in simulations. Newer LDOs
like the TPS7A26 device are inherently ceramic capacitor stable which helps to improve cost, size, and
performance in the application.
Post ESR and stability questions to TI's E2E Community.
Revision History
NOTE: Page numbers for previous revisions may differ from page numbers in the current version.
Changes from Original (May 2002) to A Revision ........................................................................................................... Page
• Deleted TPS7A25 capability and removed the Example Output Capacitance vs ESR and General Shape of an Impedance
Curve for a Capacitor images............................................................................................................ 3
• Added Load Transient (0.5 A) With 1-μF Output Capacitor image. ................................................................ 5
• Added TPS7A26 Load Transient Response With a 100-µF Capacitor at the Output image. .................................. 6
• Added the Conclusion. ................................................................................................................... 6