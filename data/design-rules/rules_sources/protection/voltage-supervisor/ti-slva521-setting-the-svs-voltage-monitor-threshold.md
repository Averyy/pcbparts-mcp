---
source: "TI SLVA521 -- Setting the SVS Voltage Monitor Threshold"
url: "https://www.ti.com/lit/an/slva521/slva521.pdf"
format: "PDF 7pp"
method: "pdfplumber"
extracted: 2026-02-16
chars: 13016
---

Application Report

Setting the SVS Voltage Monitor Threshold
William Stokes ............................................. Power Management Products
ABSTRACT
The power supply voltage for powering a microprocessor’s core must fall within a given accuracy range in
order for the processor to perform to its best specifications. If this input supply voltage should drift near to
the operational boundary then the microprocessor will want to gracefully shutdown, or reset, before
presumably losing its data or miss-performing in some way. The following application report will discuss
this issue in some detail in order to arrive at a reasonable approach for adjusting the SENSE, or reset,
threshold of the Supply Voltage Supervisor (SVS) circuit to assure that the microprocessor is reset
properly, while accounting for the various inaccuracies of the voltage monitor/supervisor system. In most
of these systems it is the lower voltage boundary that is of paramount concern and therefore this report
will only focus on the lower trip threshold only.
Contents
1 Introduction ......................................................... 1
2 Typical SVS Application .................................................. 2
3 Setting the SVS Sense Threshold when High Accuracy is Needed ......................... 3
3.1 Example ....................................................... 5
List of Figures
1 Typical Supply Voltage Supervisor Configuration for Protecting a DSP....................... 2
2 Illustration Depicting a Supply Voltage, the Relative SVS Reset Threshold, and Respective Accuracies
Within the Required System Operating Voltage Range ................................ 3
3 SVS Circuit for Monitoring a Supply Voltage for a CPU Core ............................ 4
4 Illustration of a Nominal 1.8-V Power Supply, the Relative SVS Reset Threshold, and the Respective
Accuracy Windows Necessary To Meet A “±5%” CPU Operating Range Requirement.............. 5
1 Introduction
As the system operating voltage ranges narrow the demand for tighter power supply accuracies and SVS
accuracies increases. For tightest accuracies it will likely be necessary to search for a completely
integrated solution containing both an accurately trimmed power supply output voltage as well as a factory
trimmed SVS threshold. One such example would be the TPS75005 dual output LDO with integrated SVS
intended for applications requiring load currents of less than 500 mA. Theoretically the potential accuracy
of an internally trimmed sense threshold is better than one using an external resistor divider to divide
down the monitored voltage to a common reference voltage, but this is not always true in practice.
More typically the power supply and SVS selection will need careful consideration if system operating
voltage boundaries are to be respected. This is an iterative process where the power supply voltage
accuracy, the SVS reference requirement and resistor tolerances are progressively narrowed till the total
system accuracy fits within the prescribed operating window. There must not be any overlaps between the
supply accuracy boundary with the SVS accuracy boundary so as to prevent false resets from non-failing
supply voltages.

2 Typical SVS Application
Figure 1 shows a typical SVS configuration where Voltage Supervisor A monitors the 3.3-V supply voltage
to the DSP’s VI/O input and Voltage Supervisor B monitors the 1.8-V supply voltage to the DSP core at
the V input. In this configuration if the 3.3-V supply rail should fail by falling below the SENSE
CORE
threshold of the TPS3808G33 this will issue a master reset (MR/) to the TPS3808G18 which would then
RESET the DSP. Or if the 1.8-V voltage should fail by falling below the SENSE threshold of the
TPS3808G18 then this would cause a RESET to be issued directly to the DSP.
3.3 V 1.8 V
DD CORE
V
I/O
Voltage Supervisor Voltage Supervisor
A B DSP
CPU
SENSE V DD SENSE V DD FPGA
MR RESET MR RESET GPIO (DSP RESET)
C T GND C T GND
TPS3808G33 TPS3808G18
GND
B0484-01
Figure 1. Typical Supply Voltage Supervisor Configuration for Protecting a DSP
The choice to employ the TPS3808 as the supervisor to monitor the respective supply voltages would
have been made after finding that the DSP requires voltages be maintained within say a ±10% window of
the nominal supply rails, that is, 3.3-V I/O, nominal, and 1.8 V , nominal, to maintain operation. Each
power supply and supervisor will be selected so as to dis-allow the supply voltage from falling outside this
±10% boundary window of operation. Each power supply will have its own specified accuracy and each
supervisor will monitor that supply voltage around a SENSE threshold also having its own accuracy. By
example, Figure 2 illustrates the situation just described where the nominal 1.8-V supply is monitored by
the TPS3808G18. The selected 1.8-V power supply might typically have been selected for its ±5%
accuracy, as shown, enabling the use of the TPS3808 in such a way that the supervisor trip threshold can
dependably respond within the window required by the DSP. The nominal trip, or reset, threshold for the
TPS3808G18 is 1.67 V ±1.5% according to its data sheet, detected at the SENSE input. This means that
this threshold relative to the nominal, 1.8-V supply voltage can be calculated to fall between –5.83% to
–8.61% of that voltage as shown and which is well within the required window of the system operating
voltage range.

V V
Supply Supply
Range (V) Range (%)
1.98 +10.00%
1.96
1.94
1.92
1.90
+5.00%
1.88
1.86
1.84 +5.00%
1.82
1.80 1.8 V Supply 0% Supply Voltage Operating DSP
(Nominal System Accuracy
1.78 Operating
Supply Voltage)
1.76 –5.00% Voltage
1.74 Range
1.72
–5.00%
1.70 Guard Band
–5.83%
1.68 Supply Voltage Supervisor/Monitor - +1.50%
–7.22%
1.66 SENSE Threshold Accuracy –1.50%
1.64 –8.61%
1.62 –10.00%
M0225-01
Figure 2. Illustration Depicting a Supply Voltage, the Relative SVS Reset Threshold, and Respective
Accuracies Within the Required System Operating Voltage Range
3 Setting the SVS Sense Threshold when High Accuracy is Needed
The approach here is to first select a known power supply with a specified accuracy and then decide to
use an adjustable SVS SENSE threshold adjusted to the average between the lowest possible supply
voltage and the minimum allowable system (CPU) voltage. Of course, custom trimmed settings of fixed
SVS SENSE voltage thresholds are available for a price depending on the business case. The lowest
specified supply voltage, V , is calculated from the nominal supply voltage, V , and the known
ss(min) ss(nom)
supply voltage accuracy as a percent, %V , in Equation 1.
Vss
V = V × (1 – %V /100) (1)
ss(min) ss(nom) Vss
The desired nominal SVS SENSE threshold, V , is calculated in Equation 2:
th(nom)
V = [V + Vcpu ] / 2 (2)
th(nom) ss(min) (min)
where V is the minimum allowable system operating voltage.
cpu(min)
The type of highly accurate SVS circuit required here is depicted in Figure 3 where a single channel of the
quad TPS38600 is shown monitoring a 1.8-V core voltage to the system CPU. The TPS38600 was chosen
for it 1% reference accuracy.
Note that in Figure 3 the SVS SENSE threshold, V , is determined by the resistor divider, R1 and R2, and
th
is defined as the failing V voltage that will cause the SVS to reset.

1.8 V 3.3 V
CORE CC
R
Pullup
I/O
V CC V CORE
WDI WDO
SENSE1 Quad Voltage Supervisor V REF C D P S U P
FPGA
MR RESET1
R1
C T1 RESET2
RESET
SENSE2 + Delay
–
R2 + GND
C 0.4 V
T2
– Voltage Supervisor
CH2
(Illustration)
SENSE3 RESET3
C
T3
SENSE4L
RESET4
SENSE4H
C
T4 TPS386000
B0485-01
Figure 3. SVS Circuit for Monitoring a Supply Voltage for a CPU Core
The resistor values to make the nominal SVS SENSE threshold are calculated using Equation 3:
R2 = V × R1 / (V – V ) (3)
ref th(nom) ref
where V is the nominal reference voltage of the SVS device.
ref
The accuracy of the SVS SENSE threshold is considered to be the combined result of errors contributed
by the SVS reference voltage accuracy (read inaccuracy), the tolerance of the divider resistors1 and the
error by the leakage current2 into the SENSE pin of the of the SVS. These errors are depicted by the
series of equations: Equation 4, Equation 5, and Equation 6:
V΄ = V ± V = [V × (1 + R1/R2)] × [1 ± (%Ref / 100)] (4)
th th(nom) error(%ref) ref
Where V is the SVS SENSE voltage threshold error due to the reference error, where %Ref is the
error(%ref)
reference error as a percent.
V΄΄ = V΄ ± V = V × [1 ± (2 × (%R /100) × (1 – V / V )) (5)
th th error(%RTOL) ΄th TOL th(nom) ref
Where V is the voltage error introduced to V due to the tolerances of the resistor divider
error(%RTOL) th(nom)
resistors, R1 and R2.
V΄΄΄ = V΄΄ ± V = V΄ ± I × R1 (6)
th th error(Isense) ΄th SENSE
Where I is the leakage current into the SENSE pin of the SVS device and V is the threshold
SENSE error(Isense)
voltage error caused by I .
SENSE
Of course the tally of all these errors is best kept ordered in a spread sheet.
Setting the SVS Sense Threshold when High Accuracy is Needed

3.1 Example
Use Figure 3 as the starting point to design an SVS circuit and power supply for a CPU requiring a 1.8-V
±5% supply for its core voltage rail. We will also decide right off to use a 1.8-V power supply whose
accuracy is ±2% sense, knowing already that this is typical of what goes for a standard industry best.
Key Specifications:
CPU Core Operating Range: 1.8 V ±5% (1.71V to 1.89V)
Supply Voltage, V : 1.8 V ±2%
ss
Resistors R1 and R2 can have tolerances of 0.1% but 1% is preferred.
TPS38600 Product Characteristics over temp:
Vref = 0.4 V ±1%, I = ±25nAmps
From Equation 1 calculate the minimum specified supply voltage, V , and then use Equation 2 to
ss(min)
calculate the nominal SVS SENSE threshold, V .
th(nom)
V = V × (1 - %VVss/100) = 1.8 V × (1 – 2%/100) = 1.764 V
ss(min) ss(nom)
V = (V + Vcpu ) / 2 = (1.764 V + 1.71 V) / 2 = 1.737 V
th(nom) ss(min) (min)
Note here that the max/min SVS SENSE threshold is required to fit within an accuracy window between
the CPU minimum voltage and the minimum supply voltage, Vss(min) : 1.71 V to 1.764 V
Figure 4 illustrates the nominal supply voltage, the SVS reset, and the respective accuracy ranges that
allow the CPU specifications to be met by the following calculations.
V V
Supply Supply
Range (V) Range (%)
1.90
+5.00%
1.88
1.86
1.84 +2.00% CPU
1.82 Recommended
1.80 1.8 V Supply 0% Supply Voltage Operating Operating
(Nominal Supply Accuracy Voltage
1.78
1.76 Vol μ ta P g C e o fo re r ) the –2.00% Guard Band Range
1.74 Supply Voltage Supervisor/Monitor -
1.72 SENSE Threshold Accuracy
–5.00%
1.70
1.68
1.66
M0226-01
Figure 4. Illustration of a Nominal 1.8-V Power Supply, the Relative SVS Reset Threshold, and the
Respective Accuracy Windows Necessary To Meet A “±5%” CPU Operating Range Requirement
Assume that R1 = 500 kΩ and calculate R2 using Equation 3.
R2 = V × R1 / (V – V ) = 0.4 V × 500 k / (1.737 V – 0.4 V) = 426894 Ω
ref th(nom) ref
Calculate the threshold accuracy error range due to the reference accuracy using Equation 4 as follows:
V΄ = V ± V = [V × (1 + R1/R2)] × (1 ± (%Ref / 100))
th th(nom) error(%ref) ref
V΄ = [0.4 V × (1 + 500 kΩ/426894 Ω)] × (1 ± (1% / 100)) = 1.7196 V (min) to 1.75626 V (max)
Calculate the added threshold accuracy error, added to the range of V΄ above, that is due to the resistor
tolerances using Equation 5:
V΄΄ = V ± V = V΄ × (1 ± (2 × (%R /100) × (1 – V / V ))
th ΄th error(%RTOL) th TOL th(nom) ref
V ΄ = 1.7196 V × (1-(2× 0.001 × (1 – 1.737 V/.4 V)) to 1.75626 V × (1+(2 × 0.001 × (1 – 1.737 V/0.4 V))
V ΄ = 1.7178 V (min) to 1.5626 V (max)
t h
Finally, calculate the total added threshold accuracy error including that from the leakage sense current,
I , using Equation 6:
V΄΄΄ = V΄΄ ± V = V΄΄ ± I × R1 = 1.7178 V – 25 nA × 500 kΩ to 1.5626 V + 25 nA × 500 kΩ
th th error(Isense) th SENSE
V΄΄΄ = 1.7078 V (min) to 1.7663 V (max)

Notice that the lowest possible SVS SENSE threshold, 1.7078 V, is actually lower than the minimum
specified operating voltage of the CPU, which is 1.71 V, and the upper accuracy limit of the same
threshold is above the minimum good supply voltage, V of 1.764 V. This circuit does not meet
ss(min)
requirements. In this case, to meet the CPU specifications all that is needed is to reduce the R1 and R2
resistances (in the same ratio) so as to reduce the error contribution due to the I leakage error
current.
Reduce R1 to 250 kΩ and then, by Equation 3, R2 to 2134447 Ω. Now recalculate the error using
Equation 8 to find that this new SVS SENSE threshold accuracy window does fall within the required
range:
V΄΄΄ = 1.7115 V (min) to 1.7625 V (max)
This is illustrated in Figure 4.
