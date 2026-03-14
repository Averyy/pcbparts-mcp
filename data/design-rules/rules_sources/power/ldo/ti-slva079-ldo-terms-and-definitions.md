---
source: "TI SLVA079 -- LDO Terms and Definitions"
url: "https://www.ti.com/lit/an/slva079/slva079.pdf"
format: "PDF 13pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 20816
---

Application Report

Understanding the Terms and Definitions of LDO Voltage
Regulators
Bang S. Lee Mixed Signal Products
ABSTRACT
This report provides an understanding of the terms and definitions of low dropout (LDO)
voltage regulators, and describes fundamental concepts including dropout voltage,
quiescent current, standby current, efficiency, transient response, line/load regulation, power
supply rejection, output noise voltage, accuracy, and power dissipation. Each section
includes an example to increase the understandability.
Contents
1 Dropout Voltage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
2 Quiescent Current . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
3 Standby Current . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
4 Efficiency . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
5 Transient Response . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
6 Line Regulation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
7 Load Regulation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
8 Power Supply Rejection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
9 Output Noise Voltage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
10 Instability of LDO Regulator . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
11 Accuracy . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
12 Power Dissipation and Junction Temperature . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
13 Summary. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
List of Figures
1 Typical Application Circuit of LDO Regulator . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
2 Dropout Region of TPS76733 (3.3 V LDO) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
3 Quiescent Current of LDO Regulator . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
4 Standby Current of LDO Regulator . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
5 Transient Response of 1.2-V, 100 mA LDO Regulator . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
6 Transient Response of TPS76933 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
7 TPS76933 Output Voltage With Respect to the Input Voltages . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
8 Load Transient Response of TPS76350 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
9 TPS76350 LDO Regulator Output Voltage With Respect to Output Currents . . . . . . . . . . . . . . . . . . . . 7
10 Power Supply Rejection . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
11 Output Noise Voltage . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
12 Stable Range of CSR. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9
13 LDO Regulator . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
14 Power Dissipation vs Output Current . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
1 Dropout Voltage
Dropout voltage is the input-to-output differential voltage at which the circuit ceases to regulate
against further reductions in input voltage; this point occurs when the input voltage approaches
the output voltage. Figure 1 shows a typical LDO regulator circuit. In the dropout region, the
PMOS pass element is simply a resistor, and dropout is expressed in terms of its on-resistance
(R ).
on
(cid:0)
V I R
dropout o on
+ Vdropout _
Ii Io
IN OUT +
LDO
Co
Vi Vo
GND
CSR Dropout Voltage:
Vdropout =IoXRon
_
Figure 1. Typical Application Circuit of LDO Regulator
For example, Figure 2 shows the input/output characteristics of the TPS76733 3.3-V LDO
regulator. The dropout voltage of the TPS76733 is typically 350 mV at 1 A. Thus, the LDO
regulator begins dropping out at 3.65-V input voltage; the range of the dropout region is between
approximately 2-V and 3.65V input voltage. Below this, the device is nonfunctional. Low dropout
voltage is necessary to maximize the regulator efficiency.
]V[
oV
egatlov
tuptuo
(1)
dropout
region
3.3
off regulation region
region
dropout
voltage
0 2.0 3.6 10
input voltage Vi [V]
Figure 2. Dropout Region of TPS76733 (3.3 V LDO)

2 Quiescent Current
Ii Io
IN OUT
+
CSR _
Quiescent Current::
Iq
Iq= Ii – Io
Figure 3. Quiescent Current of LDO Regulator
Quiescent, or ground current, is the difference between input and output currents. Low quiescent
current is necessary to maximize the current efficiency. Figure 3 shows the quiescent current
that is defined by
I (cid:0) I (cid:0) I (2)
q i o
Quiescent current consists of bias current (such as band-gap reference, sampling resistor, and
error amplifier currents) and the gate drive current of the series pass element, which do not
contribute to output power. The value of quiescent current is mostly determined by the series
pass element, topologies, ambient temperature, etc.
For bipolar transistors, the quiescent current increases proportionally with the output current,
because the series pass element is a current-driven device. In addition, in the dropout region the
quiescent current can increase due to the additional parasitic current path between the emitter
and the base of the bipolar transistor, which is caused by a lower base voltage than that of the
output voltage. For MOS transistors, the quiescent current has a near constant value with
respect to the load current since the device is a voltage-driven device. The only things that
contribute to the quiescent current for MOS transistors are the biasing currents of band–gap,
sampling resistor, and error amplifier. In applications where power consumption is critical, or
where small bias current is needed in comparison with the output current, an LDO voltage
regulator using MOS transistors is essential.
3 Standby Current
Standby current is the input current drawn by a regulator when the output voltage is disabled by
a shutdown signal. The reference and the error amplifier in an LDO regulator are not loaded
during the standby mode, as shown in Figure 4.

EN (high)
Is +
VCC VCC
V i Reference
Vref
– Vo=0[V]
–
Standby current = Is
when output is disabled
Switch positions are shown with EN high (standby mode)
Figure 4. Standby Current of LDO Regulator
4 Efficiency
The efficiency of LDO regulators is limited by the quiescent current and input/output voltages as
follows.
I V
Efficiency (cid:0) o o ×100 (3)
(cid:3)I o(cid:0)I
q
(cid:4)V
i
To have a high efficiency, drop out voltage and quiescent current must be minimized. In addition,
the voltage difference between input and output must be minimized, since the power dissipation
of LDO regulators accounts for the efficiency. (Power Dissipation = (V – V )I ). The input/output
i o o
voltage difference is an intrinsic factor in determining the efficiency, regardless of the load
conditions.
Example:
1. What is the efficiency of the TPS76933 3.3-V LDO regulator with the following operating
conditions? Input voltage range is 3.6 V to 4.5 V. Output current range is 80 mA to
100 mA. The maximum quiescent current is 17 m A. Then, the minimum efficiency is
obtained as follows:
Efficiency (cid:1) (100 1 m 00 A m (cid:0) A 1 (cid:2) 7 3 m .3 A) V 4.5 V ×100 (cid:1)73.3 %
2. What is the efficiency if input voltage range is 3.6 V to 4 V under the same conditions as
the above? The minimum efficiency is improved as follows:
Efficiency (cid:1) (100 10 m 0 A m (cid:0) A(cid:2) 17 3. m 3 A V )4 V ×100 (cid:1)82.5 %
5 Transient Response
The transient response is the maximum allowable output voltage variation for a load current step
change. The transient response is a function of the output capacitor value (C ), the equivalent
o
series resistance (ESR) of the output capacitor, the bypass capacitor (C ) that is usually added
b
to the output capacitor to improve the load transient response, and the maximum load-current
(I ). The maximum transient voltage variation is defined as follows:
o,max
I
(cid:0)V (cid:0) o,max (cid:0)t (cid:0)(cid:0)V
tr,max C (cid:0)C 1 ESR
o b
Where D t corresponds to the closed loop bandwidth of an LDO regulator. D V is the voltage
1 ESR
variation resulting from the presence of the ESR (R ) of the output capacitor. The application
ESR
determines how low this value should be.
Ii
Co=
4.7uF
Vi
daoL
(4)
Io
V
Cb
– D Vtr , max
D t
Figure 5. Transient Response of 1.2-V, 100 mA LDO Regulator
Figure 5 shows the transient response of a 1.2–V, 100-mA LDO regulator with an output
capacitor of 4.7 m F. A step change of load current (near 90 mA) was applied to the regulator,
which is shown in the upper trace of the figure. In the lower trace the output voltage drops
approximately 120 mV and then the voltage control loop of the LDO regulator begins to respond
to the step load change within 1 us (D t = 1 m s). The frequency bandwidth of the LDO regulator
accounts for D t . Finally, the output voltage reaches a stable state within 17 m s.
To obtain a better transient response, a higher bandwidth of the LDO regulator, higher values of
output/bypass capacitors, and low ESR values are recommended, provided they meet the CSR
requirements.
6 Line Regulation
Line regulation is a measure of the circuit’s ability to maintain the specified output voltage with
varying input voltage. Line regulation is defined as
(cid:0)V
Line regulation (cid:1) o (5)

7 3.340
3.320
6
3.300
5 3.280
3.260
egatloV
tupnI
tuptuO
LDO 4.7uF
Vo
Vi GND
D VLR2
0 50 100 150
Time [us]
Change of Input Resultant
Voltage Output Voltage
D VLR1
Figure 6. Line Transient Response of TPS76933
Figure 6 shows the input voltage transient response of the TPS76933 3.3-V LDO regulator. A
step change of input voltage was applied to the regulator, which is shown at the lower left in the
figure. The resultant output voltage has been changed due to the different input voltages as
shown in the right side of the figure. The line regulation is determined by D V and D V since
LR1 LR2
line regulation is a steady-state parameter (i.e., all frequency components are neglected).
Figure 7 shows the circuit performance of the TPS76933 LDO regulator with respect to the input
voltages. The broken line shows the range of the output voltage variation (D V ) resulting from
LR
the input voltage change. Increasing open loop gain improves the line regulation.
18.81mV
1.244mV
}V[
3.3
Output Voltage
Variation
0 2.0 3.5 10
Input Voltage – VI [V]
Figure 7. TPS76933 Output Voltage With Respect to the Input Voltages
7 Load Regulation
Load regulation is a measure of the circuit’s ability to maintain the specified output voltage under
varying load conditions. Load regulation is defined as
o (6)
Load regulation;
(cid:0)I

200 5.2
5.1 100
5.0
0 4.9
4.8
tnerruC
]Am[–
Ii
LDO 4.7uF
Vo
Vi GND
D VLDR
Step Change of Resultant
Load Current Output Voltage
Figure 8. Load Transient Response of TPS76350
The worst case of the output voltage variations occurs as the load current transitions from zero
to its maximum rated value or vice versa, which is illustrated in Figure 8. The load regulation is
determined by the D V since load regulation is a steady-state parameter like the line
LDR
regulation. Figure 9 shows the circuit performance of the TPS76350 5-V LDO regulator with
respect to the output currents. Increasing open loop gain improves the load regulation.
5.0
4.95
0 30 60 90 120 150 180
4.975
Output Current Io [mA]
Figure 9. TPS76350 LDO Regulator Output Voltage With Respect to Output Currents
8 Power Supply Rejection
Power supply rejection ratio (PSRR), also known as ripple rejection, measures the LDO
regulator’s ability to prevent the regulated output voltage fluctuating caused by input voltage
variations. The same relation for line regulation applies to PSRR except that the whole
frequency spectrum is considered.

+ IN OUT +
Vi LDO Vo
Vi,ripple GND
Cb
CSR
0 time 0 time
_ _
Ripple Rejection:
PSRR= atall frequencies
Vi,ripple
0
100 1k 10k 100k 1M 10M
]bd[
RRSP
Vo, ripple
Vo, ripple
–20
–40
–60
10
frequency
Figure 10. Power Supply Rejection
The ripple rejection is defined by
(cid:0) o,ripple (7)
PSRR at all frequencies
i,ripple
For example, supply rejection in the frequency band between 100 kHz and 1 MHz is especially
important in applications where the output of a dc/dc switch mode power supply (SMPS) is used
to power the linear regulator. The output ripple of the SMPS is typically in the aforementioned
frequency span. Thus, the figure above does not seem to show a good PSRR performance for
the SMPS applications over the frequency range (100 kHz to 1 MHz). The worst performance
(maximum point in the graph) occurs when R is large and C is low.
ESR b
The control loop tends to be the dominant contributor of supply rejection. Low ESR value, a
large output capacitor, and added bypass capacitors improve the PSRR performance, provided
they meet the CSR requirement.
9 Output Noise Voltage
Output noise voltage is the RMS output noise voltage over a given range of frequencies (10 Hz
to 100 kHz) under the conditions of a constant output current and a ripple-free input voltage. The
noise generated only by an LDO regulator becomes the output noise voltage.

Vi Co Vo
GND Vnoise,peak
CSR
0 time _ _ 0 time
output noise voltage =Vnoise,rms
tnatsnoC
Constant
input
Figure 11. Output Noise Voltage
Most output noise is caused by the internal voltage reference. Typical specification of output
noise voltage ranges from 100 to 500 m V. TI-TPS764xx devices have an external compensation
pin to enable customers to connect a bypass capacitor to reduce the output noise. A bypass
capacitor, in conjunction with an internal resistor, creates a low-pass filter to further reduce the
noise. TI-TPS764xx exhibits only 50 m V of output voltage noise using 0.01 m F bypass and 4.7 m F
output capacitors.
10 Instability of LDO Regulator
100
IN OUT +
10
LDO Co
Vi Co=4.7uF
GND Vo 1
0.1
_
0.01
0 50 100 150 200 250
noitasnepmoC
RSC
ecnatsiseR
seireS
Out of the TPS763xx Datasheet
W
Region of Instability
RESR
Stable Region
Output
Radd
Capacitor W
Region of Instability
W Compensation Series Resistance:
CSR = RESR + Radd Io– Output Current – mA
Figure 12. Stable Range of CSR
LDO manufacturers typically provide a graph showing the stable range of the compensation
series resistance (CSR) values, since CSR can cause instability with respect to output currents.
The CSR is the sum of the equivalent series resistance (R ) of the output capacitance and the
additional resistor (R ).
add
CSR (cid:0) R (cid:0)R (8)
ESR add
An additional resistor can be used if the R is too small. An example of a typical stable range
of CSR values is shown in Figure 12. This curve is called tunnel of death. The curve shows that
CSR must be between 0.2 W and 9 W so that the LDO regulator is stable. Solid tantalum
electrolytic, aluminum electrolytic, and multilayer ceramic capacitors are all suitable, provided
they meet the CSR requirements.

Q1(b )
+ +
R
Vs Vo
Vi + RL
ga
_ Vref R
_ _
Vref
Figure 13. LDO Regulator
11 Accuracy
The overall accuracy considers the effects of line regulation (D V ), load regulation (D V ),
LR LDR
reference voltage drift (D V ), error amplifier voltage drift (D V ), external sampling resistor
o,ref o,a
tolerance (D V ), and temperature coefficient (D V ). It is defined by
o,r TC
|(cid:0)V LR |(cid:1)|(cid:0)V LDR |(cid:1) (cid:9)(cid:0)V 2 o,ref (cid:1) (cid:0)V 2 o,a(cid:1) (cid:0)V 2 o,r(cid:1) (cid:0)V 2 TC (9)
Accuracy (cid:5) (cid:0)100
The output voltage variation in a regulated power supply is due primarily to temperature variation
of the constant voltage reference source and temperature variation of the difference amplifier
characteristics, as well as the sampling resistor tolerance. Load regulation, line regulation, gain
error, and offsets normally account for 1 to 3% of the overall accuracy.
Example:
What is the total accuracy of the 3.3 V LDO regulator shown in Figure 13 over the temperature
span from 0° to 125° with the following operating characteristics; temperature coefficient is
100 ppm/°C, sampling resistor tolerance is 0.25%, output voltage change resulting from load
regulation and line regulation are ±5 mV, and ±10 mV, respectively. The accuracy of the
reference is 1%.
The output voltage is given by
V o(cid:3)
R(cid:1)
V ref (cid:3)2V ref
Therefore, the reference voltage V is half of the output voltage (i.e., V = 3.3/2[V]), and
ref ref
(cid:0)V TC(cid:3)Temperature Coefficient(cid:4) (cid:7)T max(cid:2)T
min
(cid:8) (cid:4)V
(cid:3)(cid:7)100ppm(cid:6) °C(cid:8)(125°C)(3.3 V) (cid:3)41.2 mV
(cid:0)V o,r (cid:3) (cid:7)0.25% of V o(cid:1)0.25% of V o (cid:8)V ref
(cid:3)
(0.005)(3.3)(cid:7)3.3(cid:8)
(cid:3)27 mV
2
(cid:0)V o,ref (cid:3) 2 R R V d (cid:3)2(cid:7)3 2 .3(cid:8)0.01 (cid:3)33mV, where V d (cid:3)V ref ×0.01 (cid:3) (cid:7)3 2 .3(cid:8)×0.01
Therefore, the overall accuracy of the LDO is obtained as follows:
(cid:6) 2 2 2
10mV(cid:0)5mV(cid:0) (33mV) (cid:0) (27mV) (cid:0) (41.2mV)
Accuracy (cid:3) ×100 (cid:3)2.25%
3.3 V
12 Power Dissipation and Junction Temperature
Most LDO regulators specify a junction temperature to assure their operations; the maximum
junction temperature allowable without damaging the device is also specified. This restriction
limits the power dissipation that the regulator can handle in any given application. To ensure that
the junction temperature is within acceptable limits, calculate the maximum allowable
dissipation, P , and the actual dissipation, P , which must be less than or equal to P .
D(max) D D(max)
The maximum power dissipation limit is determined using the following equation;
T Jmax(cid:1)T
A
P D(max) (cid:2) R
(cid:0)JA
Where
T is the maximum allowable junction temperature.
Jmax
Rq
JA
is the thermal resistance junction-to-ambient for the package, i.e., 285°C/W for the
5-terminal SOT23.
T is the ambient temperature.
A
The regulator power dissipation is calculated using;
P D(cid:2) (cid:4)V i(cid:1)V o (cid:5)×I o
0.44
0.4
0.3
0.2
0 0.05 0.1 0.15
)W(
noitapissiD
rewoP
TPS763xx and TPS764xx
0.44
input/output 7v 6v 5v 4v 3v
voltage 8v 0.4
9v
difference
10V
2v 0.3
0.2
1v
0.3v
0 0.05 0.1
Output Current (A)
)W(
noitapissiD
rewoP
(10)
(11)
TPS761xx and TPS769xx
input/output 9v8v 7v 6v 5v
voltage 4v
difference
10V
3v
2v
1v
0.3v
Output Current (A)
Figure 14. Power Dissipation vs Output Current
Figure 14 shows the safe operating area for several TI LDO regulators in terms of output
current, input/output voltage difference, and dissipation power, which are calculated by using
equation (11). Calculate maximum power dissipation P by using equation (10). The
D(max)
calculated P must not exceed the safe area shown in the figures. The thermal protection
D(max)
shuts the regulator off if the junction temperature rises above 165°C. Recovery is automatic
when the junction temperature drops approximately to 140°C, where regulator operation
resumes.

13 Summary
This application report described the terms and definitions of low dropout (LDO) voltage regulators,
and provided fundamental concepts.
