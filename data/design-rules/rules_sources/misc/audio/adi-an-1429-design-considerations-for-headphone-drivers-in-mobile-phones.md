---
source: "ADI -- AN-1429: Design Considerations for Headphone Drivers in Mobile Phones"
url: "https://www.analog.com/media/en/technical-documentation/application-notes/AN-1429.pdf"
format: "PDF 8pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 21073
---

AN-1429
APPLICATION NOTE
One Technology Way • P.O. Box 9106 • Norwood, MA 02062-9106, U.S.A. • Tel: 781.329.4700 • Fax: 781.461.3113 • www.analog.com
Design Considerations and Solutions for Headphone Drivers in Mobile Phones
By David Guo
INTRODUCTION SIGNAL CHAIN
High fidelity describes the quality of audio equipment. High In this type of application, use high performance and low power
fidelity audio equipment has ideal total harmonic distortion plus audio DACs to deliver a dynamic range (DNR) of up to 127 dB
noise (THD + N) performance and accurate frequency response, and THD + N of −120 dB. Some high performance audio DACs
resulting in excellent subjective test results. can be configured as a voltage output or current output. Configure
current output for better DNR and THD + N.
Portable high fidelity audio equipment brings customers a
higher quality music listening experience. Compared to mobile For a voltage output configuration, the conditioning circuit is a
phones, however, portable high fidelity audio equipment is different amplifier circuit, which converts the differential signal
inconveniently large. Though given increased market demand from the R channel or L channel to a single-ended signal (see
and technical advances, it is now possible to integrate the high Figure 1).
fidelity function into thinner mobile phones. VOLTAGE OUTPUT DIFFERENTIAL TO
SINGLE-END
Typically, audio digital-to-analog converters (DACs) cannot V+
drive low impedance headphones well. However, to reach quality
R
performance, operational amplifiers are used with audio DACs
for signal conditioning, including current to voltage (I to V) V–
conversion, filter, attenuation, and differential to single-ended DAC
conversion. The operational amplifiers must have low noise, low V+
distortion, and strong drive capability. The operational amplifier
L
must also perform well in subjective testing with customers. Many
V–
Analog Devices, Inc., operational amplifiers are reputable with
music fans, like the AD797, OP275, AD8620, and ADA4627-1.
In portable mobile phone applications, the quiescent current and Figure 1. Voltage Output Configuration
package of a device is important. The ADA4841-2, ADA4896-2,
For a current output configuration, implement an I to V circuit
ADA4075-2, ADA4807-2, and AD8397 have ideal noise and
to convert the differential current signal from the R channel and
distortion performances. This application note focuses on the
the L channel to the differential voltage signal, followed by a
circuit discussion and operational amplifier recommend-
difference amplifier circuit (see Figure 2).
dations for this high fidelity headphone driver application.
In mobile phone applications, the power consumption of
devices is key. In this application note, a ±5 V power is chosen
as the example for analysis convenience.
Figure 2. Current Output Configuration
Rev. 0 | Page 1 of 8
100-23051
CURRENT OUTPUT I TO V DIFFERENTIAL TO
SINGLE-END
I+
R
I–
DAC
I+
L
I–
200-23051

AN-1429 Application Note
TABLE OF CONTENTS
Introduction ...................................................................................... 1 Headphone Basics .........................................................................4
Signal Chain ...................................................................................... 1 Output Stage (First-Order Low-Pass Filter) ..............................6
Revision History ............................................................................... 2 Output Stage (Second-Order Low-Pass Filter) .........................6
I to V Stage......................................................................................... 3 Operational Amplifier Recommendations for Output Stage ..6
Operational Amplifier Recommendations for I to V Stage in THD + N vs. V /I Measurement .......................................7
OUT OUT
Mobile Phones .............................................................................. 3
THD + N vs. V /I Result .....................................................7
THD + N vs. V
OUT
Measurement ............................................... 4
Summary ........................................................................................8
THD + N vs. V Result............................................................. 4
REVISION HISTORY
10/2016—Revision 0: Initial Version
Rev. 0 | Page 2 of 8

Application Note AN-1429
I TO V STAGE
An ideal I to V converter for a current output DAC is a resistor Assuming f is 100 kHz, then,
C
to ground. However, most DACs do not operate linearly with
1 1
voltage at the output. It is standard practice to operate an C = = ≈390pF
F 2πR f 2π×4kΩ×100kΩ
operational amplifier as an I to V converter, creating a virtual F C
ground at the inverting input. Normally, the operational amplifier • R is the resistor in series with C. Typically, R = 100 Ω for
S F S
output stage absorbs clock energy and current steps. However, better stability and THD + N performance.
Figure 3 shows the C F capacitor shunts high frequency energy • V is the voltage bias. Typically, audio DACs generate a
BIAS
to ground while correctly reproducing the desired output with
dc offset current. For maximizing the effective output
extremely low THD and intermodulation distortion (IMD).
signal, add a V at the noninverting input terminal to
BIAS
RS Cf cancel the dc voltage by the DAC dc offset current.
OPERATIONAL AMPLIFIER RECOMMENDATIONS
Rf
FOR I TO V STAGE IN MOBILE PHONES
The key specifications of operational amplifiers as the I to V
I+ stage in headphone drivers include power supply, I Q , voltage and
current noise, THD + N, package, common-mode rejection ratio
VBIAS (CMRR), power supply rejection ratio (PSRR), A
OL
, and slew rate.
I TO V The ADA4841-2, ADA4896-2, ADA4075-2, and ADA4807-2 are
Figure 3. I to V Stage recommended for I to V conversion. Key points about these
devices include the following:
There are four components in the circuit:
• R is the feedback resistor. For lowest noise, maximize gain • All devices are low noise, low power, and have a small
F
package.
in the first stage (I to V). However, distortion is related to
the open-loop gain (A OL ) of the operational amplifier. The • ADA4807-2 uses the lowest I Q to achieve low noise and
higher A , the better the distortion performance. Normally, rail-to-rail input/output (RRIO) and it integrates the
A is specified within certain output voltages (see Figure 3). disable function, which can further decrease the power
The ADA4896-2 A must be 100 dB minimum when the consumption.
output is −4 V to 4 V at ±5 V power supply, or when • The ADA4075-2 specified power supply is 9 V minimum, is
distortion increases beyond −4 V to 4 V. Assuming the not a rail-to-rail output (RRO), and has the smallest package.
maximum output current of a DAC is 1 mA, then, • THD + N is the key specification. See Figure 4 and Figure 5
for the test circuit and test result of THD + N, respectively.
V 4V
R = OUT = =4kΩ
F I 1mA
• C is the feedback capacitor in parallel with R. C and R
F F F F
form a pole in the transfer function, therefore the cutoff
frequency (f ) of the low-pass filter is
1
f =
C 2πR C
F F
Figure 4. THD + N Test Without Load
Rev. 0 | Page 3 of 8
300-23051
BNC- SYS-2712 BNC-
UNBALANCE UNBALANCE
1kHz 1kΩ 1kΩ
+5V
–5V
400-23051

THD + N VS. V
MEASUREMENT 0
To determine the maximum output without THD + N degrading,
–20
measure THD + N vs. V .
Typically, an audio DAC current output acts as a resistor in series –40
with a voltage source. That is, the I to V circuit can be considered
an inverting amplifier circuit. For simplicity, gain = −1 to –60
determine the THD + N performance of operational amplifiers
(see Figure 5). The following details the procedure to measure –80
THD + N vs. V using the SYS-2712 from Audio Precision:
• The power supply is ±5 V. –100
• The SYS-2712 analog analyzer generates a 1 kHz sine wave as
–120 the input of the amplifier circuit. The output of the amplifier 0.1 1 4
circuit feeds into the SYS-2712 to obtain THD + N data.
• The bandwidth of the SYS-2712 analyzer is configured as Figure 5. THD + N Result of Recommended Operational Amplifiers
22 kHz. HEADPHONE BASICS
• To find THD + N at the output range in the SYS-2712
The characteristics of load (headphones) determines the output
evaluating software, the input of the analog analyzer is
stage. The headphones have two key specifications: impedance
configured as autorange, that is, the input stage gain of the
and sensitivity.
analyzer increases automatically by the different input signals,
including 40 mV, 160 mV, 300 mV, 600 mV, 1.2 V, 2.5 V, Impedance is typically measured at 1 kHz. Low impedance
and 5 V. Typically, the larger the gain, the worse the noise headphones are in the range of 8 Ω to 32 Ω. High impedance
level of the analyzer and THD + N. headphones are in the range of about 100 Ω to 600 Ω. As the
impedance increases, more voltage (at a given current) is required
RESULT
to drive it. As a result, the loudness of the headphones for a given
Figure 5 shows THD + N vs. V results for the recommended voltage decreases. In recent years, impedance of newer headphones
operational amplifiers. When V is less than 1.2 V rms, THD + N has generally decreased to accommodate lower voltages available
performance of the four operational amplifiers is similar. on battery-powered portable electronics, like mobile phones.
Lower impedance means heavier load to the operational amplifier,
When V is larger than 1.2 V rms, the analog analyzer of the
which requires operational amplifiers to have larger current
SYS-2712 is switched to 2.5 V scale, increasing the gain of internal
drive capabilities without distortion.
programmable gain amplifier (PGA). The noise worsens and
THD + N degrades slightly. The SYS-2712 causes this deg- Sensitivity measures how loud the headphones are for a given
radation. This is not the true performance of the operational electrical drive level. It can be measured in decibels of sound
amplifier because the SYS-2712 has worse noise with a larger pressure level (SPL) per milliwatt (dB/mW) or decibels of SPL
PGA gain. per volt (dB/V).
As V continues to increase, THD + N degrades dramatically at By analyzing the wave file of a live recording, the maximum SPL
the maximum output voltage of the amplifier. For the ADA4841-2, can reach 120 dB. The average SPL is less than 100 dB. Find the
ADA4896-2, and ADA4807-2, the voltage is about 3.5 V rms required peak power using the following formula:
(4.9 V peak). This matches the RRO feature of these devices. For
RequiredSPL−Sensitivity
the ADA4075-2, the voltage is about 2.13 V rms (3.0 V peak). This P=10   
 10 
matches the 2 V output voltage to the rail in the ADA4075-2
data sheet.
Rev. 0 | Page 4 of 8
)%(
N
+
DHT
OUTPUT VOLTAGE (V)
500-23051
ADA4841-2
ADA4896-2
ADA4075-2
ADA4807-2

Table 1 details the key specifications of some headphones. The For low impedance headphones, the required peak current can
impedance ranges from 8 Ω to 600 Ω. The required peak power, reach 80 mA maximum, and THD + N of the current cannot
peak voltage, and peak current are listed. degrade.
The required average power is less than 2 mW. To reproduce the For high impedance headphones, the output voltage must be high.
effect of live recording, the headphone driver must output more For example, using the DT880 from Beyer Dynamic (600 Ω)
power. See Table 1. requires an operational amplifier output of 12 V, which is
impossible in a ±5 V system. If the product targets driving high
impedance headphones, increase the power supply of the amplifier
circuit.
Table 1. Sensitivity, Impedance, Peak Voltage, and Peak Current of Headphones
Peak Peak Peak
Sensitivity Average Power Voltage Current
Manufacturer Model (dB/mW) Impedance (Ω) Frequency (Hz) Power (mW) (mW) (V) (mA)
SONY XBA-4 108 8 3 to 28000 0.158 15.849 0.356 44.510
Audio-Technica ATH-CHX7 100 16 15 to 22000 1.000 100.000 1.265 79.057
Shure SE215 107 20 22 to 17500 0.200 19.953 0.632 31.585
Apple Earpod 109 23 5 to 21000 0.126 12.589 0.538 23.396
Grado Alice M1 100 32 20 to 22000 1.000 100.000 1.789 55.902
Creative AURVANA Air 102 32 20 to 20000 0.631 63.096 1.421 44.404
KOSS PP 101 60 10 to 25000 0.794 79.433 2.183 36.385
Sennheiser HD650 98 300 10 to 39500 1.585 158.489 6.895 22.985
Beyer Dynamic DT880 96 600 5 to 35000 2.512 251.189 12.277 20.461
Rev. 0 | Page 5 of 8

OUTPUT STAGE (FIRST-ORDER LOW-PASS FILTER) Power dissipation (P ) can be 1.274 W at 85°C ambient
D
temperature. Assuming ±5 V is the power supply, the maximum
The output stage converts the differential voltage signal to the
output voltage is 2 V rms. R = 10 Ω, and R is shorted to ground.
single-ended voltage signal. Figure 6 depicts a common difference S S
P per channel of the ADA4807-2 is
amplifier circuit, also known as a subtractor circuit. D
CF P D = ( V S ×I S ) +    V 2 S × V R OUT     − V O R UT2
RF L L
RG P D = 610 mW
RS
Considering the ADA4807-2 is a dual-channel device, the total
RL
P is 1.22 W. The output current in this example is 200 mA. The
D
ADA4807-2 short-circuit current is 80 mA, so R can be smaller
S
to increase the damping factor. For operational amplifiers with a
Figure 6. Differential Single-Ended Circuit
short-circuit current larger than 200 mA, RS must be 10 Ω
R G and R F determine the gain of the circuit, which is normally minimum to avoid operational amplifier damage in output
gain < 1. The resistance of resistors must be small, typically 1 kΩ, short to ground status.
to avoid inducing more noise. R and C forms a pole in the
F F OUTPUT STAGE (SECOND-ORDER LOW-PASS
transfer function. Therefore, f of the low-pass filter is
FILTER)
1
f = Compared to the first-order low-pass filter, the second-order
C 2πR C
F F low-pass filter has a steeper roll-off response, removing more
R determines the output impedance or the damping factor of noise out of the specified band.
the headphone driver. The high damping factor (R L /R S ) improves The two-pole low-pass filter with differential input is easily
the control the source (headphone driver) has over the load designed using the design equations for the single-ended input
(headphone). The impedance of the headphone does not have multiple-feedback low-pass filter. Shown in Figure 8, duplicating
pure resistance and varies by frequency. A higher R S can induce the component results in an equivalent frequency response.
more distortion (especially low frequency distortion) because of Normally, the filter gives a Bessel response, which has a linear
the frequency varied impedance. From a performance perspective, phase.
make R low. Generally, the damping factor remains above one.
From a safety perspective, higher R can attenuate power to protect
the headphone from damaging, while also protecting the amplifier
in case the output shorts to ground. This can happen when hot
plugging the headphones. Figure 7 shows the ADA4807-2 (LFCSP)
maximum power dissipation vs. ambient temperature for a 4-layer
evaluation board.
Figure 8. Second-Order Multiple Feedback (MFB) Filter
OPERATIONAL AMPLIFIER RECOMMENDATIONS
FOR OUTPUT STAGE
The key specifications for the output stage operational amplifier
is similar to the I to V stage. The output stage operational amplifier
must typically have <−100 dB THD + N at 32 Ω load. The
ADA4841-2, ADA4807-2, and AD8397 operational amplifiers
are recommended for the output stage of headphone drivers in
mobile phones. There are four points to consider:
• All of the operational amplifiers are low noise, low power,
and small package devices.
• ADA4807-2 achieves low noise and RRIO by lowest I
Q
. It
Figure 7. ADA4807-2 Maximum Power Dissipation vs. Ambient Temperature also integrates a disable function, which can further
for a 4-Layer Evaluation Board
decrease power consumption.
Rev. 0 | Page 6 of 8
600-23051
4.0
3.5
3.0
2.5
2.0
1.5
1.0
0.5
0
–40 –25 –10 5 20 35 50 65 80 95 110 125
)W(
NOITAPISSID
REWOP
MUMIXAM
AMBIENT TEMPERATURE (°C)
700-23051
C2 R4 C2 R4
C5
R1 R3 R1 R3
R1 R3
C2 R4
SINGLE-ENDED INPUT DIFFERENTIAL INPUT
SINGLE-ENDED OUTPUT SINGLE-ENDED OUTPUT
800-23051

• AD8397 typically has <−100 dB THD + N at 32 Ω load. It
also tests subjectively well. The disadvantage is the AD8397
I is higher, at about 12 mA.
Q
• <−100 dB THD + N at 32 Ω load is a key specification. See
Figure 9 and Figure 10 for the test circuit and test result,
respectively.
See the ADA4841-2, ADA4807-2, and AD8397 data sheets for
relevant specifications.
/I
MEASUREMENT
Figure 9 shows the circuit used to find THD + N at a heavy
load. The following details the THD + N vs. V /I
OUT OUT measurement:
• The power supply is ±3.3 V. The gain of the subtractor is
Figure 11. THD+N vs. IOUT of the ADA4841-2, ADA4807-2, and AD8397
about 0.243.
Table 2 details the maximum current and maximum output
• The SYS-2712 generates a 1 kHz sine wave as the input of
power with parameters set at <−100 dB THD + N at 16 Ω load.
the amplifier circuit. Feed the output of the amplifier circuit
Figure 11 shows the following results:
into the SYS-2712 analog analyzer to determine THD + N.
• Configure the bandwidth of the SYS-2712 analyzer to 22 kHz. • THD + N degrades dramatically when I OUT reaches a
• To measure THD+N vs. V /I , SYS-2712 is configured certain current threshold.
to output a 100 mV rms to 4 V rms signal. • The AD8397 has high current drive capabilities at 16 Ω load.
• The ADA4807-2 maximum output current is 42 mA with
SYS-2712 BNC- only 1.2 mA I Q , which is recommended when prioritizing
BALANCE UNBALANCE
the power consumption budget.
1kHz/1.0V rms 820Ω 200Ω
In most cases, 2 mW output power is enough to drive the
+3.3V
headphones. THD + N, in this case, is important; as detailed in
820Ω Table 2, THD + N at 2 mW of all recommended operational
16Ω
200Ω –3.3V amplifiers is <−100 dB.
Table 2. Maximum Current and Output Power at 16 Ω Load
Figure 9. THD + N Test with 16 Ω Load
Parameter ADA4841-2 ADA4807-2 AD8397
/I
RESULT
Maximum Current at 29.1 mA 42.1 mA 125 mA
Figure 10 and Figure 11 depicts THD + N vs. V /I of the <−100 dB THD + N
recommended operational amplifiers. Output Power at 13.6 mW 28.4 mW 250 mW
<−10 dB THD + N
THD + N at 2 mW −102.7 dB −102.7 dB −101.4 dB
Output Power
DESIGN GUIDELINES
Resistance measured at 1 kΩ induces 4 nV/√Hz noise, which is
more than the voltage noise of most operational amplifiers. In
the circuit, the resistance of the resistors must be chosen carefully
and must not exceed 1 kΩ.
Shielding is very important in mobile phones. To reach <−100 dB
THD + N specifications, the tiniest of interferences can degrade
THD + N performance, particularly when listening to music
and browsing the internet simultaneously. Metal shielding can
help prevent performance degradation.
Figure 10. THD+N vs.VOUT of the ADA4841-2, ADA4807-2, and AD8397
Rev. 0 | Page 7 of 8
900-23051
–40
–60
–80
–100
–120
0.02 0.2
)Bd(
ADA4807-2 = 16Ω
ADA4841-2 = 16Ω
AD8397 = 16Ω
OUTPUT VOLTAGE (V rms)
010-23051
–40
–60
–80
–100
–120 1 10 100
)Bd(
ADA4807-2 = 16Ω
ADA4841-2 = 16Ω
AD8397 = 16Ω
OUTPUT CURRENT (mA)
110-23051

For better heat dissipation, solder the exposed pad of the LFCSP SUMMARY
package to the board pad and connect it to a big solid copper
Table 3 lists the different solutions and different considerations
plane at the opposite side of the board by vias. The copper plane
for voltage output DAC or current output DAC.
can be the ground or power plane of the board, but consult the
There are many things to consider when creating an excellent
ADA4841-2, ADA4807-2, and AD8397 data sheets to specify
product. In real applications, according to different conditions
which plane to use.
(for example, power supply, targeted load resistance, power
Use a low dropout regulator (LDO) as the power supply of
consumption budget, and expected performance), customers
operational amplifiers. Place the decoupling capacitors (0.1 μF
can choose the right solution and design the circuit to achieve
and 4.7 μF) near the operational amplifier power pins.
personal expectations.
The capacitors in the audio path must be an NP0 ceramic type,
as they offer better distortion performance. Use thin film resistors
for optimum THD performance. Metal film resistors are also
suitable, but typically cost more.
Table 3. Recommended Different Solutions
DAC Current Output
Parameter DAC Voltage Output I to V Stage Output Stage
Low Cost ADA4841-2 ADA4841-2 ADA4841-2
High Performance AD8397 ADA4807-2, ADA4896-2, ADA4075-2 AD8397
Quality Performance by Low Power Consumption ADA4807-2 ADA4807-2, ADA4896-2, ADA4075-2 ADA4807-2