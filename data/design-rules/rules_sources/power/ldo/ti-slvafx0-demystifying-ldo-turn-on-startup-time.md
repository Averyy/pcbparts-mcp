---
source: "TI SLVAFX0 -- Demystifying LDO Turn-On (Startup) Time"
url: "https://www.ti.com/lit/wp/slvafx0/slvafx0.pdf"
format: "PDF 17pp"
method: "ti-html"
extracted: 2026-02-16
chars: 37856
---

Technical White Paper

# Demystifying LDO Turn-On (startup) Time

# Abstract

This paper provides a comprehensive discussion on
what affects the total turn on time in modern LDO regulators. It describes a new
mathematical foundation to calculate the turn-on ramp time for many modern LDO
regulators which employ either a noise reduction (NR) filter, feedforward (FF)
capacitor (CFF) or both. The designer can use this new analysis set
to perform statistical calculations on LDO regulator turn-on time. This analysis
helps assess the device minimum and maximum turn-on times and also the expected
inrush current. Designs which must meet a maximum slew rate requirement during
turn on (or *rate-of-rise* requirement) can also use this new analysis set
to confirm that an startup ramp rate meets the system requirements.

# 1 Introduction to linear regulator turn-on time

The turn-on time (tON) for
an LDO regulator is a summation of the delay time (tD) and the rise time
(tR) (see [Equation 1](#GUID-5DEC6A79-CB3B-4DBB-A4F4-F06BCAEF5F72) and [Figure 1-1](#FIG_P2P_KVH_JCC)). The delay time is defined as the fixed time delay from when the output voltage
can start to increase with respect to an external stimulus, to when the output
voltage actually begins to increase. If the LDO regulator has an enable pin, the
external stimulus typically occurs when the enable voltage toggles to turn on the
LDO regulator. This behavior assumes that the input voltage has already been applied
to the input of the LDO regulator. For LDO regulators without an EN pin, the input
voltage acts as the external stimulus.

|  |  |
| --- | --- |
| Figure 1-1 Total turn-on time vs input voltage  A. Minimum VOUT regulation | Equation 1.     t  O N =   t  D +   t  R |

Delay time for an LDO regulator is
usually small compared to the rise time. Delay times result from how quickly the
device can energize internal circuitry to begin increasing the output voltage. The
LDO regulator data sheet gives the best estimate of the delay time because after the
device is enabled, external circuitry has little influence on the delay time. The
rise time is the time to increase the output voltage from 0V to the minimum
regulation. Each application requires unique regulation so the minimum regulation
point is application specific. For example, one design may allow a tolerance of ± 3%
while another design may allow a tolerance of ± 5%. Thus, the turn-on time is faster
for a design with wider tolerance requirements.

# 2 What impacts the LDO rise time?

Linear regulator references can use
either a precision voltage source ([Figure 2-1](#FIG_DTW_5H3_JCC)) or a precision current source ([Figure 2-2](#FIG_NHS_VH3_JCC)). The linear regulator turn-on time is affected by either the reference turning
on or the RC time constant formed by the RTOP and CFF in the
feedback loop. Typically, the reference voltage turns on very quickly, however in
modern LDO regulators the reference voltage may also be filtered through a low pass
noise reduction (NR) resistor and capacitor.

Figure 2-1 Precision voltage
reference

Figure 2-2 Precision current
reference

Voltage across the RTOP
resistor ramps in accordance with both the RC time constants on VREF and
RTOP. [Equation 2](#GUID-F05D65D8-D8C3-45BB-8783-2905A8133CAA) represents the NR/SS time constant and [Equation 3](#GUID-84B52261-0D6D-43D6-B5CC-56B90FD8FC68) represents the FF time constant.

Equation 2. τNR/SS=RNR/SS×CNR/SS

Equation 3. τFF=RTOP×CFF

During the turn-on period, the voltage
on the VOUT pin is the summation of the voltage across the RBOTTOM
resistor (or VFB) and the voltage across the RTOP resistor (or
VTOP) as shown in [Equation 4](#GUID-AA3CDBEA-F296-4A16-8C48-CCF3C587C516) :

Equation 4. VOUTt=VTOP(t)+VFB(t)

During the turn-on period, the
reference voltage ramps fast enough for it to approximate an ideal step function
relative to the much longer

τ
NR/SS time constant. [Equation 5](#GUID-60F27195-868D-4007-BBFC-EED18138E986) describes VFB(t) when the LDO regulator reference is a precision
voltage source, but when it is a precision current source, use [Equation 6](#GUID-3CA59EDF-8B0D-4D44-A17F-26A2CB5AC9B7) instead.

Equation 5.

V

F
B

t
=

V

R
E
F
×

1
-

e

-


t

τ

N
R
/
S
S

Equation 6. VFBt=INR/SS×RNR/SS×1-e- tτNR/SS

The voltage across the top set point
resistor is more complex to calculate as VFB(t) is not always a step
function. When

τ
NR/SS and

τ
FF are comparable values, neither time
constant dominates the turn-on calculation. Use Laplace transforms and partial
fraction expansions [[1](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-2C20B127-B0BF-4ADF-98BC-BF15BC5ACAFB)]-[[2](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-C6C7C507-DA26-4406-AB3A-7CE76EB5D5ED)] to derive VTOP(t), shown in [Equation 7](#GUID-66002ED6-3848-470F-A742-5ED987DA14E9).

Equation 7. VTOPt=VREF×RTOPRBOTTOM×1-τNR/SSτNR/SS-τFF×e-tτNR/SS-τFFτFF-τNR/SS×e-tτFF

## 2.1 Simple Use Cases

When

τ
NR ≫

τ
FF, or when the LDO regulator operates in
unity gain feedback (when RTOP = 0Ω), the turn-on time is dominated by

τ
NR and [Equation 8](#GUID-7621F1EB-CEEC-41B0-BE82-308501507714) represents VOUT(t).

Equation 8.

V

O
U
T

t
≅

V

F
B

t
×

R

T
O
P
+

R

B
O
T
T
O
M

R

B
O
T
T
O
M

When

τ
NR ≪

τ
FF, [Equation 7](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-66002ED6-3848-470F-A742-5ED987DA14E9) can be simplified to [Equation 9](#GUID-6CC13928-FD90-4D5A-8A68-336F5C46D8F0) :

Equation 9.

V

T
O
P

t
≅

V

R
E
F
×

R

T
O
P

R

B
O
T
T
O
M
×

1
-

e

-
t

τ

F
F

### 2.1.1 Case 1: LDO with an NR filter but without CFF capacitance

[Figure 2-3](#FIG_WSX_Z2Z_JCC) shows the TPS7A20 [[3](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-99A498D2-24E3-4D8E-834C-A60951C393ED)]. The analysis uses [Equation 5](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-60F27195-868D-4007-BBFC-EED18138E986) and [Equation 8](GUID-581407D3-54DD-4778-B70A-4EE23AF4F58C.html#GUID-7621F1EB-CEEC-41B0-BE82-308501507714) to calculate the turn-on time.

[Equation 10](#GUID-69901D9B-D96D-4678-96E8-806F0702F0AD) calculates the tau of an RC circuit using the 10% to 90% time measurement
(t10%-90%). Use [Equation 5](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-60F27195-868D-4007-BBFC-EED18138E986), [Equation 8](GUID-581407D3-54DD-4778-B70A-4EE23AF4F58C.html#GUID-7621F1EB-CEEC-41B0-BE82-308501507714), and [Equation 10](#GUID-69901D9B-D96D-4678-96E8-806F0702F0AD) to calculate tR for any regulation band requirement in [Figure 1-1](GUID-90969E41-595A-4272-89E2-3B3792A743F9.html#FIG_P2P_KVH_JCC). The measured turn-on time for [Figure 2-3](#FIG_WSX_Z2Z_JCC) is 258.7µs which equates to

τ
= 117µs for the TPS7A20.

|  |  |
| --- | --- |
| Figure 2-3 TPS7A20 turn-on timing | Equation 10.     τ  R C =     t  10 % - 90 %    ln ⁡  9 |

### 2.1.2 Case 2: NR filter with a CFF capacitance

[Figure 2-3](#FIG_Z3N_JZD_KCC) shows the TPS7A49 turn-on analysis versus the physical measurement. The analysis
uses [Equation 4](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-AA3CDBEA-F296-4A16-8C48-CCF3C587C516), [Equation 5](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-60F27195-868D-4007-BBFC-EED18138E986), and [Equation 7](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-66002ED6-3848-470F-A742-5ED987DA14E9) to calculate the turn on time. RTOP = 11.5kΩ, RBOTTOM =
1.02kΩ and CFF = 100nF.

Figure 2-4 Output voltage vs Time

### 2.1.3 Fast-charge circuitry

The NR/SS filter significantly
improves the power supply rejection ratio (PSRR) and noise in LDO regulators.
[[21](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-19054658-09CE-47A0-9E76-D6B4EE621CFA)]

The time constant for the NR/SS filter may result in longer than desired turn-on
times for some applications. Modern LDO regulators may include a *fast charge*
circuit to reduce the turn-on time of the filtered reference supply, and by
extension, the output voltage. The fast-charge circuit operates while
VNR/SS measures less than the changeover voltage (VCO),
when the steady state filter values are used.

[Figure 2-5](#FIG_TLZ_GK2_KCC) shows typical turn-on behavior of an LDO regulator using fast charge.

For LDO regulators that use a voltage
reference, this fast-charge circuit is either a parallel current source or parallel
resistor with the NR/SS resistor as shown in [Figure 2-1](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#FIG_DTW_5H3_JCC). For LDO regulators that use a current reference, the fast-charge circuit
modifies the IREF current to be a larger value as shown in [Figure 2-2](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#FIG_NHS_VH3_JCC). [Equation 11](#GUID-12F8604F-AE8F-4E06-A79F-C6FEB6EF6E8C) calculates the time when the changeover voltage occurs (tCO). Entering

τ
= tCO into [Equation 7](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-66002ED6-3848-470F-A742-5ED987DA14E9) yields the initial condition (VCO\_FF) on VTOP just after
the changeover voltage event.

If a fast-charge current source is
across RNR/SS, use [Equation 12](#GUID-C68A821E-5367-426C-83CC-4B889A92669D) instead of [Equation 11](#GUID-12F8604F-AE8F-4E06-A79F-C6FEB6EF6E8C) to calculate tCO.

|  |  |
| --- | --- |
| Figure 2-5 Changeover voltage vs time | Equation 11.     t  C O = -   τ  N R / S S ×   ln ⁡    1 -     V  C O    V  R E F  Equation 12.     t  C O = -   τ  N R / S S ×   ln ⁡    1 -     V  C O    V  R E F +   I  F C ×   R  N R / S S |

Common values of VCO are
95% to 97% of VREF. Use [Equation 5](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-60F27195-868D-4007-BBFC-EED18138E986) or [Equation 6](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-3CA59EDF-8B0D-4D44-A17F-26A2CB5AC9B7) to calculate VFB(t) during fast-charge operation, but after the
fast-charge function completes, use [Equation 13](#GUID-6DA5F551-6BF6-4DFE-96DA-3802F502C816).

Equation 13.

V

F
B

t
=

V

R
E
F
+

V

C
O
-

V

R
E
F
×

e

-


t
-

t

C
O

τ

N
R
/
S
S

If the LDO uses a precision current
source, (as shown in [Figure 2-2](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#FIG_NHS_VH3_JCC)) use [Equation 14](#EQUATION-BLOCK_FW2_G1Y_4CC).

Equation 14.

V

R
E
F
=

I

N
R
/
S
S

×
R

N
R
/
S
S

Use [Equation 15](#GUID-75071ED1-E2B2-4CDC-B0CD-50B509FA149A) to calculate VTOP after the changeover event. [Equation 13](#GUID-6DA5F551-6BF6-4DFE-96DA-3802F502C816) defines VFB(t).

Equation 15.

V

T
O
P

t
=

V

F
B

t
×

R

T
O
P

R

B
O
T
T
O
M
+

V

C
O
\_
F
F
-

V

F
B

t
×

R

T
O
P

R

B
O
T
T
O
M
×

e

-


t
-

t

C
O

τ

F
F

### 2.1.4 Non-ideal LDO behavior

The following conditions can affect
the total turn-on time of an LDO regulator.

#### 2.1.4.1 Applied voltage bias

In general, applied voltage bias has a
minor impact to the turn-on time. Changes to the effective capacitance of modern
ceramic capacitors due to voltage bias require significant amounts of time [[20](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-690985F8-C1C0-4135-918F-9F6939F6DE9E)]. The typical LDO regulator turn-on times are too short to meaningfully impact
CNR/SS and CFF capacitance due to the change in voltage
bias. Exceptions to this generalization are rare use cases where the LDO regulator
is purposely designed for a long turn-on time while simultaneously operating without
current limit engaged.

#### 2.1.4.2 Fast charge current tolerance

The fast charge current source has a
tolerance which can impact to the soft-start time if the variation is large.
IFC can shift across process tolerances, temperature and different
values of VIN or VBIAS.

[Table 2-1](#TABLE_Q3K_TT2_KCC) lists fast-charge current tolerance from the TPS7A91 data sheet.

Table 2-1 Electrical specifications

| PARAMETER | | TEST CONDITIONS | MIN | TYP | MAX | UNIT |
| --- | --- | --- | --- | --- | --- | --- |
| INR/SS | NR/SS pin charging current | VNR/SS = GND, VSS\_CTRL = GND | 4.0 | 6.2 | 9.0 | µA |
| VNR/SS = GND, VSS\_CTRL = VIN | 65 | 100 | 150 |

#### 2.1.4.3 Internal error amplifier offset voltage

Most LDO regulators are trimmed to
obtain the most accurate reference voltage possible. However, in some cases the
soft-start pin may not be trimmed which results in non-trivial offset voltage
remaining in the system during the turn-on period. In those cases, the turn-on
period completes slightly faster than expected.

Figure 2-6 Measured TPS7A74
VOS during turn-on period

#### 2.1.4.4 Temperature impacts the fast-charge current source

The LDO regulator die temperature
momentarily increases during turn on as a result of transient power dissipation
while the device charges the output capacitor COUT. This temporary
increase in junction temperature can slightly change the proportional to absolute
temperature (PTAT) current source used as the soft-start current source in some
devices. Characterization graphs and associated test conditions such as [Figure 2-7](#FIG_KZ4_PRC_WTB) are usually included in the device data sheet. During initial turn-on, the higher
power dissipation can cause the current source to increase slightly. Near the end of
the turn-on period, the power dissipation decreases, which can cause the current
source to decrease. [Figure 2-8](#FIG_BZ4_CXY_KCC) shows this behavior as a slight curvature in the start-up waveform.

|  |  |  |
| --- | --- | --- |
| CIN = COUT = 10μF | CBIAS = 1μF | CSS = 0nF |
| VBIAS = VIN = 6V | VOUT = 0.65V | VEN = 1.5V |
| IOUT = 0A | from the TPS7A74 data sheet | |

Figure 2-7 Soft-Start Current vs Temperature

|  |  |  |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |

Figure 2-8 TPS7A74 DC output voltage vs time

#### 2.1.4.5 Error amplifier common mode voltage

The non-ideal common mode voltage
(VCM) of the internal error amplifier may induce a sudden step in the
LDO regulator turn-on response in older devices. This response is not as pronounced
in most modern LDO regulators. LDO regulators that include this induced step
response offer a shorter ramp time and longer delay time. The ramp rate of the small
voltage step during the initial turn on is a function of the LDO bandwidth, which is
different for each LDO regulator. To obtain this ramp rate, it is best to capture a
measurement from an EVM after applying the system load. This measurement provides a
more accurate evaluation of the device bandwidth.

Figure 2-9 VCM can affect the turn-on time

#### 2.1.4.6 Reference voltage (VREF) ramp time dominates the turn-on time

The reference voltage of most modern
LDO regulators turns on much faster than the NR/SS and FF time constants. However,
in tracker LDO regulators [[3](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-99A498D2-24E3-4D8E-834C-A60951C393ED)] (where the reference voltage is external to the LDO regulator) this may not be
the case. [Figure 2-11](#FIG_B41_WWW_JCC) and [Figure 2-10](#FIG_ID5_WWW_JCC) show an externally applied reference voltage and the corresponding output voltage
of the device.

|  |  |
| --- | --- |
| tREF ≪ tNR | tREF ≪ tFF |

Figure 2-10 Fast Turn-on Time vs
Voltage

|  |  |
| --- | --- |
| tREF ≫ tNR | tREF ≫ tFF |

Figure 2-11 Slow Turn-on Time vs
Voltage

#### 2.1.4.7 Start-up during dropout mode

When a VIN pin and a VEN pin are tied
together, and the VIN pin voltage increases slowly, the LDO operates in dropout mode
and the output increases at the same rate that the VIN pin voltage increases. There
may be overshoot in the output voltage waveform as a result of turning on while
operating in dropout mode. [[4](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-719DD4CF-A3CA-4A14-9898-1765589DEE83)]

Figure 2-12 Startup with overshoot

#### 2.1.4.8 Large values of COUT induce internal current limit

The turn-on time of an LDO regulator
with a significant capacitive load may induce the device to limit the current. In
general, the current limit protection of an LDO regulator engages after 20µs to 50µs
of operation where the load exceeds the current limit threshold. Thus, the previous
discussion applies until current limit is engaged. After current limit engages the
LDO approximates a current source charging the output capacitor COUT.
[Figure 2-13](#FIG_QHM_GM4_LCC) shows
the TPS7A20 loaded with small (1.4µF) output capacitance. While the device remains
stable during a range between 0.47µF and 200µF load capacitance, operation at higher
values of load capacitance may trigger current limit during startup, slowing down
the turn-on time. (See [Figure 2-14](#FIG_LYY_4S4_LCC))

Figure 2-13 TPS7A20 turn-on
comparison

Figure 2-14 The TPS7A20 current limit
engages at approximately 25µs during turn-on

#### 2.1.4.9 Limitations of large-signal LDO bandwidth

In some LDO regulators, the internal error amplifier bandwidth dominates the turn-on
time. Turn-on time is inherently large signal behavior, and the error amplifiers in
some devices take longer to respond to such behavior. This response time is
especially true of very old devices (such as the LM317 or TLV1117) or of some
devices where an amplifier exists between the reference voltage and the NR/SS filter
(TPS7A47 for example). It is best to consult the device data sheet for expected
turn-on times where the internal bandwidth limits the LDO regulator.

## 2.2 Specific Use Cases and Examples

### 2.2.1 Case 3: Precision voltage reference with RNR/SS and parallel IFC fast charge

If [Figure 2-1](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#FIG_DTW_5H3_JCC) describes the LDO architecture, and the fast-charge circuit uses IFC,
[Equation 6](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-3CA59EDF-8B0D-4D44-A17F-26A2CB5AC9B7) can be rewritten as [Equation 16](#GUID-1A696453-6DB0-4EF2-9A38-5B6A3F7955B1) after t > tCO. Use [Equation 11](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-12F8604F-AE8F-4E06-A79F-C6FEB6EF6E8C) through [Equation 15](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-75071ED1-E2B2-4CDC-B0CD-50B509FA149A) and [Equation 16](#GUID-1A696453-6DB0-4EF2-9A38-5B6A3F7955B1) to calculate the turn-on time for these LDO regulators.

When t ≤ tCO, use [Equation 13](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-6DA5F551-6BF6-4DFE-96DA-3802F502C816) to calculate VFB(t).

When t > tCO, use [Equation 16](#GUID-1A696453-6DB0-4EF2-9A38-5B6A3F7955B1) to calculate VFB(t).

Equation 16. VFBt=VREFt+IFC×RNR/SS×1-e- tτNR/SS

The TPS7A91 uses a precision voltage reference, low pass NR filter, optional external
CFF capacitor across RTOP, and includes a constant current
fast charge circuit. The fast charge current is user selectable using the SS\_CTRL
pin. VCO is 97% of VREF. The EVM was used for the
measurements.

Figure 2-15 TPS7A49 turn-on time

### 2.2.2 Case 4: Precision voltage reference with IFC fast charge and no RNR/SS

If [Figure 2-1](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#FIG_DTW_5H3_JCC) describes the LDO architecture and the fast charge circuit uses only
IFC (that is, RNR/SS disconnects temporarily) then [Equation 5](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-60F27195-868D-4007-BBFC-EED18138E986) can be rewritten as [Equation 17](#GUID-7630D808-2F33-4D64-A71B-010957E23EFF) when t < tCO. [Equation 11](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-12F8604F-AE8F-4E06-A79F-C6FEB6EF6E8C) through [Equation 15](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-75071ED1-E2B2-4CDC-B0CD-50B509FA149A) and [Equation 17](#GUID-7630D808-2F33-4D64-A71B-010957E23EFF) through [Equation 20](#GUID-6C9E3CCC-9ECC-4777-8894-60160812CDED) are used to calculate the turn-on time for these LDO regulators.

When t ≤ tCO, use [Equation 17](#GUID-7630D808-2F33-4D64-A71B-010957E23EFF) and [Equation 18](#GUID-35C1ABBD-6BBE-4963-A926-0C999877A376) to calculate VFB(t) and VTOP(t).

When t > tCO, use [Equation 13](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-6DA5F551-6BF6-4DFE-96DA-3802F502C816), [Equation 15](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-75071ED1-E2B2-4CDC-B0CD-50B509FA149A), [Equation 19](#GUID-5808F1E4-C9A7-40A3-ABE0-B3C8A1D64DFE) and [Equation 20](#GUID-6C9E3CCC-9ECC-4777-8894-60160812CDED) to calculate VFB(t) and VTOP(t).

Equation 17.

V

F
B

t
=

I

F
C

C

N
R
/
S
S
×
t

Equation 18.

V

T
O
P

t
=

V

F
B

t
×

1
-

e

-


t

τ

F
F

Equation 19.

t

C
O
=

C

N
R
/
S
S
×

V

C
O

I

F
C

Equation 20.

V

C
O
\_
F
F
=

V

C
O
×

R

T
O
P

R

B
O
T
T
O
M
×

1
-

e

-

t

C
O

τ

F
F

The TPS7A84A uses a precision voltage
reference, low pass NR filter, external CFF capacitor across
RTOP, and includes a constant current fast charge circuit. [Figure 2-16](#FIG_SBQ_LR5_LCC) from the
TPS7A84A data sheet describes the fast charge current versus input voltage and
temperature. VCO is 97% of VREF. The CNR/SS
capacitor is rated for 50V and the effective capacitance is nearly constant at
9.6nF. The EVM was used for the measurements.

|  |  |
| --- | --- |
| from TPS7A84A data sheet | VBIAS = 0V |

Figure 2-16 Fast-charge current vs input voltage

|  |  |
| --- | --- |
| TPS7A84A EVM | VOUT = 2.4V |

Figure 2-17 DC output voltage vs
time

### 2.2.3 Case 5: Precision current reference

If [Figure 2-2](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#FIG_NHS_VH3_JCC) describes the LDO architecture, VREF can be written as [Equation 21](#GUID-5BE10A98-5764-4370-B274-455C46E93929) or [Equation 22](#EQUATION-BLOCK_K5X_DBJ_4CC). Use [Equation 5](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-60F27195-868D-4007-BBFC-EED18138E986) and [Equation 7](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-66002ED6-3848-470F-A742-5ED987DA14E9) with [Equation 21](#GUID-5BE10A98-5764-4370-B274-455C46E93929) for calculations during the fast charge time. Use [Equation 13](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-6DA5F551-6BF6-4DFE-96DA-3802F502C816), [Equation 15](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-75071ED1-E2B2-4CDC-B0CD-50B509FA149A), [Equation 22](#EQUATION-BLOCK_K5X_DBJ_4CC) and [Equation 23](#GUID-EA185649-FDBF-4EC3-9475-B32D2A817E88) for calculations after the changeover event occurs.

When t ≤ tCO use [Equation 21](#GUID-5BE10A98-5764-4370-B274-455C46E93929) to calculate VREF.

Equation 21.

V

R
E
F
=

I

F
C
(
t
)
×

R

N
R
/
S
S

When t > tCO use [Equation 22](#EQUATION-BLOCK_K5X_DBJ_4CC) to calculate VREF.

Equation 22.

V

R
E
F
=

I

N
R
/
S
S
(
t
)
×

R

N
R
/
S
S

Equation 23.

t

C
O
=
-

τ

N
R
/
S
S
×

ln
⁡

1
-

V

C
O

I

F
C
×

R

N
R
/
S
S

[Figure 2-18](#GUID-DA811072-9FC1-4828-A167-7DB487F47FDB) shows the rise time for the TPS7A96 (and the lower current version, the TPS7A94)
which uses a precision current reference with an NR/SS pin. During startup the LDO
uses a fast charge circuit to rapidly turn on VOUT. The TPS7A94 and
TPS7A96 have a unique feature in that VCO is programmable using the FB\_PG
pin and external resistor dividers. In this test using an EVM, VCO is
programmed using the external FB\_PG resistors and is set to 97% × VOUT =
1.164 V. These LDO regulators operate in unity gain feedback, thus VTOP =
0V.

[Figure 2-19](#GUID-BFCED8B1-175F-4BF7-92AC-50ED5072C69C) shows the rise time for TPS7H1111 which is similar to the TPS7A94 and TPS7A96,
except the TPS7H1111 is optimized for power devices in a space environment. In this
test using an EVM, VCO is programmed using the external FB\_PG resistors
and is set to VOUT = 1.626 V. These LDO regulators operate in unity gain
feedback, thus VTOP = 0V.

[Figure 2-20](#GUID-50D78588-C1C8-4710-87A0-8007D0CF7D50) shows the test using a TPS7A57 EVM. VCO is internally set to 97% ×
VOUT = 1.164 V. These LDO regulators operate in unity gain feedback,
thus VTOP = 0V.

|  |  |
| --- | --- |
| RNR/SS = 8.06kΩ | VOUT = 1.2V |
| IFC = 2.1mA | INR/SS = 150µA |
| CNR/SS = 4.7µF | TPS7A96 EVM |

Figure 2-18 TPS7A96 rise time

|  |  |  |  |
| --- | --- | --- | --- |
|  | RNR/SS = 24kΩ | IFC = 200µA |  |
|  | INR/SS = 50µA | VOUT = 1.2V |  |
|  | CNR/SS = 3.8µF | TPS7A57 |  |

Figure 2-20 TPS7A57 rise time

|  |  |
| --- | --- |
| RNR/SS = 18kΩ | IFC = 2.1mA |
| INR/SS = 100µA | VOUT = 1.8V |
| CNR/SS = 4.7 µF | TPS7H1111 EVM |

Figure 2-19 TPS7H1111 rise
time

### 2.2.4 Case 6: Soft-start timing

Some LDO regulators use a soft-start (SS) pin that is different than the combination
noise reduction and soft-start (NR/SS) pin already discussed. Devices that include a
SS pin include the TPS7A74, TPS74401, and TPS748A. While the SS pin programs the
VOUT rise time, unlike the NR/SS pin it does not reduce the device
noise. Using a soft-start pin, and assuming no CFF is installed, the
output rises linearly by tracking the voltage ramp of the external soft-start
capacitor until the voltage exceeds the internal reference. The same analysis and
equations are used as shown in [Section 2.1.3](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-187B58FE-2CD5-438A-A519-29D139B41D4D), except VCO = VREF in these LDO regulators.

Modern LDO regulators are trimmed to
provide excellent accuracy during steady state. However, any device that includes a
soft-start pin may not be trimmed during turn-on and a non-negligible VOS
may affect the turn-on behavior. This behavior includes slightly faster turn on-time
(positive VOS) than originally anticipated, as well as a small voltage
step in the output voltage during initial turn on.

After t > tCO, VCO\_FF is calculated using [Equation 25](#GUID-409727BB-6CB4-4C75-9A99-5A60532A1A08) while setting t = tCO and VFB(t) = VREF.

When t ≤ tCO, use [Equation 24](#GUID-A4558462-1948-4EF9-A9DE-2F62DEFFF444) and [Equation 25](#GUID-409727BB-6CB4-4C75-9A99-5A60532A1A08).

When t > tCO, use [Equation 15](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-75071ED1-E2B2-4CDC-B0CD-50B509FA149A) and [Equation 19](GUID-91F5953E-1743-4AD6-A55A-FA0ABAC37027.html#GUID-5808F1E4-C9A7-40A3-ABE0-B3C8A1D64DFE).

Equation 24.

V

F
B
=

I

F
C

C

S
S
×
t
+

V

O
S

Equation 25.

V

T
O
P

t
=

V

F
B

t
×

R

T
O
P

R

B
O
T
T
O
M
+

I

F
C

C

S
S
×

R

T
O
P

R

B
O
T
T
O
M
×

τ

F
F
×

e

-
t

τ

F
F
-
1

The TPS7A74 uses a precision voltage
reference with a SS pin. The soft-start current variation with temperature is
described in Figure 6-37 in the TPS7A74 data sheet [[6](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-B889B1D1-ED80-4194-8472-46E2FD787D5A)]. The offset voltage during turn-on is shown in [Figure 2-6](GUID-F90B3A98-CC3E-4CA6-A2B8-07EF018A86F1.html#FIG_T5R_FDZ_KCC). VCO = VREF and [Equation 7](GUID-69A6A443-BD8C-4834-994E-45285DC131BB.html#GUID-66002ED6-3848-470F-A742-5ED987DA14E9), [Equation 11](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#GUID-12F8604F-AE8F-4E06-A79F-C6FEB6EF6E8C) through [Equation 14](GUID-187B58FE-2CD5-438A-A519-29D139B41D4D.html#EQUATION-BLOCK_FW2_G1Y_4CC), [Equation 17](GUID-91F5953E-1743-4AD6-A55A-FA0ABAC37027.html#GUID-7630D808-2F33-4D64-A71B-010957E23EFF) through [Equation 20](GUID-91F5953E-1743-4AD6-A55A-FA0ABAC37027.html#GUID-6C9E3CCC-9ECC-4777-8894-60160812CDED) are used for the analysis. The EVM was used for the measurements with a derated
value of CSS = 825 nF according to the capacitor manufacturer. The
comparison between the analysis and measurement is provided in [Figure 2-8](GUID-CE37DB8B-1301-4BBC-AE9F-4C73CFCF6FF7.html#FIG_BZ4_CXY_KCC) .

# 3 System Considerations

## 3.1 Inrush current calculation

Use the previous sections to determine
the turn-on time for your LDO regulator. Use [Equation 26](#GUID-9336F2AB-C716-4D0C-8EE0-A8C712F51293) to calculate the inrush current using the loading on the output of the LDO
regulator. The inrush current is a function of output current, output voltage rise
time and output capacitance. While quiescent current of the LDO regulator does add
to the inrush current, in practice this is a very small fraction of the total inrush
and can usually be neglected in the analysis.

Equation 26.

I

I
N
R
U
S
H
=

I

Q
+


I

L
O
A
D
+

C

O
U
T

×
V

O
U
T
(
t
)
≅

I

L
O
A
D
+

C

O
U
T

×
V

O
U
T
(
t
)

As inrush current increases the LDO
regulator temperature rise can temporarily also increase. In rare cases, the
internal bond wires can fuse if the inrush current is very high [[16](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-83477732-827D-46D5-92E1-CBAE9C6DFDDD)]. Fortunately, neither prove to be a major concern in modern LDO regulators in
the vast majority of applications. Turn-on times for most LDO regulators are
sufficiently fast such that the junction temperature does not significantly rise and
place the device into thermal shutdown mode. The current limit protection circuit
engages within 20µs to 50µs in most cases, preventing an abnormally high inrush
current from fusing the internal bond wires. If heavy inrush exists before the
current protection circuit can engage, the fusing current can be reviewed by sending
an E2E request to TI. Thus, most concerns regarding inrush current are systematic in
nature, such as possible brownout of input supplies, or voltage droop of the input
capacitance, C­IN, due to excessive inrush current.

[Figure 3-1](#FIG_AJT_V5Z_KCC) shows inrush current measured in three locations (A, B, and C). D describes an
optional damping network.

Figure 3-1 Inrush current probe measurement locations

Location A is a common measurement
point but this may not accurately reflect the true inrush seen through the LDO
regulator. The input capacitor, CIN provides some of the current to the
device, so measurement point A shows less peaking in the current measurement and a
lengthened current pulse.

Location B is the preferred
measurement point if the objective is to capture the entire inrush current through
the LDO regulator. Inductance (LP\_IN) associated with the current probe
measurement typically results in excessive ringing in the measurement. An optional
damping network can be installed to remove most of this ringing and clean up the
measurement significantly.

Location C is the least preferred inrush measurement point. Inductance
(LP\_OUT) associated with the current loop results in excessive
ringing during the turn-on measurement, affecting both the output voltage and the
input voltage measurements. Adding a damping network can improve the measurement,
however the inductance may continue to slow the turn on time of the VOUT pin. Thus,
even when an installed damping network exists, the measurement may not reflect true
device performance when the current probe loop is removed.

## 3.2 Inrush current analysis

We can use the previous equations to
quickly calculate the inrush current through the LDO regulator if we know the output
capacitance and load during the turn-on period. [Figure 3-3](#FIG_RTP_1MQ_LCC) provides an example using the TPS7A20 (recall that this device includes an NR
filter that also controls the turn-on time). Two 1µF capacitors are installed on the
output which provide an effective capacitance of 1.4µF.

[Figure 3-3](#FIG_RTP_1MQ_LCC) provides an example using the TPS7A84A. Recall that the TPS7A84A uses a
fast-charge current source (without an NR resistor in parallel) and switches in the
NR filter for steady state operation. The analysis used COUT = 67µF and
the peak current (IPEAK) is well within the tolerance of the
capacitors.

|  |  |
| --- | --- |
| TPS7A20 | COUT = 1µF || 1µF |
|  | |

Figure 3-2 TPS7A20 turn-on with
inrush current analysis

|  |  |
| --- | --- |
| TPS7A84A | COUT = 47µF || 10µF || 10µF |
| (A.) VCM induced current spike | |

Figure 3-3 TPS7A84A turn-on with
inrush current analysis

## 3.3 Maximum slew rate

In some applications the LDO regulator
must limit the slew rate during the turn-on period [[17](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-E6594D0C-48B3-47DD-B168-C27BF051828B)] , [[18](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-DCD01CC6-4C90-4BC9-B7AF-30865D6A060F)], and [[19](GUID-AB2C6CB6-ECE9-45DE-9EE3-8A25E83EB8BA.html#GUID-A4E9DB89-6AD2-462C-BBCA-39FCDCF79F50)], and the most desirable way to achieve this requirement is to adjust the
CNR/SS or CFF capacitance. These slew rate requirements
may be enforced across a narrow range of turn on, such as between 2V and 4V of a 5V
output, or across the entire voltage range from 0V to steady state. In general, it
may be more challenging to meet these requirements using a device with an
exponentially rising output as shown in [Figure 3-4](#FIG_RTP_1MQ_LCC) than a linear ramp as shown in [Figure 3-3](GUID-83927A4F-81AE-407A-AE94-7BF4B05E3173.html#FIG_RTP_1MQ_LCC). To slow down a fixed output LDO regulator where the NR filter and feedback
resistors are internal to the device, the only option remaining is to increase the
output capacitance, COUT such that the current limit loop engages
approximately 20µs to 50µs into the turn-on period.

Figure 3-4 TPS7A20 output voltage slew
rate

# 4 LDO regulators referenced in this paper

| Case | TI LDO Regulators |
| --- | --- |
| Case 1 | TPS7A20, TPS7A21 |
| Case 2[(1)](#GUID-DC650F68-AD8E-41C4-92D7-98C5C087F05B_li:1;59:88) | TPS7A13, TPS7A14, TPS7A49 |
| Case 3 | TPS7A91, TPS7A92 |
| Case 4 | TLV702, TLV703, TLV755P, TPS7A52, TPS7A53, TPS7A53B, TPS7A54, TPS7A83A, TPS7A84A, TPS7A85A |
| Case 5 | TPS7A57, TPS7A94, TPS7A96, TPS7H1111-SP |
| Case 5b | TPS74401, TPS7A74, TPS74701, TPS74801, TPS74901 |

(1) With very small or unpopulated
feedforward capacitance (CFF), these devices operate using the
analysis for Case 1.

# 5 Conclusion

This paper documents the first of its
kind framework to define a startup analysis of LDO regulators using either NR
filters, feedforward capacitors, or both. The framework includes the impact of fast
charge circuitry, and both types of internal precision references of LDO regulators
are addressed (voltage references and current references). This paper discusses
non-ideal characteristics of modern LDO regulators, and how they impact the LDO
startup times. Designers can use this framework to calculate turn-on ramp times and
LDO inrush current, and they can assess the output voltage slew rate during turn-on
time to confirm that the LDO startup behavior meets their system requirements.

# 6 References

1. Thomas, Roland E., Rosa, Albert
   J. *The analysis and design of linear systems*, 4th ed. ISBN
   978-1118065587
2. Lathi, B.P. *Signal Processing
   & Linear Systems* ISBN 978-0195219173
3. Texas Instruments, data sheet:
   [*TPS7A20 300-mA, Ultra-Low-Noise, Low-IQ, High
   PSRR LDO*](https://www.ti.com/lit/ds/symlink/tps7a20.pdf)
4. Texas Instruments, data sheet:
   [*TPS7A49 36-V, 150-mA, Ultralow-Noise, Positive Linear
   Regulator*](https://www.ti.com/lit/ds/symlink/tps7a49.pdf)
5. Texas Instruments, data sheet:
   [TPS7A91 1-A, High-Accuracy, Low-Noise LDO Voltage
   Regulator](https://www.ti.com/lit/ds/symlink/tps7a91.pdf)
6. Texas Instruments, data sheet:
   [TPS7A74 1.5-A, Low-Dropout Linear Regulator With
   Programmable Soft-Start](https://www.ti.com/lit/ds/symlink/tps7a74.pdf)
7. Texas Instruments, data sheet:
   [TPS7B4250-Q1 50-mA 40-V Voltage-Tracking LDO With 5-mV Tracking
   Tolerance](https://www.ti.com/lit/ds/symlink/tps7b4250-q1.pdf)
8. Liu, Jason. “[Various Applications for Voltage-Tracking LDO](https://www.ti.com/lit/an/slva789/slva789.pdf).” Texas Instruments
   application report, literature No. SLVA789, 2016
9. Texas Instruments, application
   report: Zhang, Penn, and Jason Song. *[Avoid Start-Up Overshoot of LDO](https://www.ti.com/lit/an/sbva060/sbva060.pdf)*.
10. Texas Instruments, data sheet:
    *[TPS7A84A 3-A, High-Accuracy (0.75%), Low-Noise (4.4-µVRMS)
    LDO Regulator](https://www.ti.com/lit/ds/symlink/tps7a84a.pdf)*
11. Texas Instruments, data sheet:
    *[TPS7A96 2-A, Ultra-Low Noise, Ultra-High PSRR, RF Voltage
    Regulator](https://www.ti.com/lit/ds/symlink/tps7a96.pdf)*
12. Texas Instruments, data sheet:
    *[TPS7H1111-SP and TPS7H1111-SEP 1.5-A, Ultra-Low Noise,
    High PSRR Radiation Hardened Low Dropout (LDO) Linear
    Regulator](https://www.ti.com/lit/ds/symlink/tps7h1111-sp.pdf)*
13. Texas Instruments, data sheet:
    *[TPS7A57 5-A, Low-VIN (0.7 V), Low-Noise (2.1
    µVRMS), High-Accuracy (1%), Ultra-Low Dropout (LDO)
    Voltage Regulator](https://www.ti.com/lit/ds/symlink/tps7a57.pdf)*
14. Texas Instruments, data sheet:
    *[TPS74401 3.0-A, Ultra-LDO with Programmable Soft-Start](https://www.ti.com/lit/ds/symlink/tps74401.pdf)*
15. Texas Instruments, data sheet:
    *[TPS748A 1.5-A, Low-Dropout Linear Regulator With Programmable
    Soft-Start](https://www.ti.com/lit/ds/symlink/tps748a.pdf)*
16. G. T. Nobauer and H. Moser, [*Analytical approach to temperature evaluation in bonding
    wires and calculation of allowable current, in IEEE Transactions on
    Advanced Packaging*](https://ieeexplore.ieee.org/document/861557), vol. 23, no. 3, pp. 426-435, Aug.
    2000
17. Renesas, application note:
    *[Overcoming Minimum Vdd Ramp Rate
    Limitation](https://www.renesas.cn/cn/zh/document/apn/an1825-overcoming-minimum-vdd-ramp-rate-limitation-isl25700)*
18. TI E2E [Forum](https://e2e.ti.com/support/microcontrollers/c2000-microcontrollers-group/c2000-microcontrollers---internal/f/c2000-microcontrollers---internal-forum/1348409/tms320f2800157-q1-the-srvd33-about-tms320f2800157?tisearch=e2e-sitesearch&keymatch=%2520user%253A529731)
19. Texas Instruments, data sheet:
    *[AM64x SitaraTM Processors](https://www.ti.com/lit/ds/symlink/am6411.pdf)*, Section 6.10.2.1
20. *DC and AC Bias Dependence of
    Capacitors Including Temperature Dependence*, [DesignCon](https://www.designcon.com/en/home.html) East 2011
21. Stephen Ziel, *[Tips, tricks and advanced applications of linear
    regulators](https://www.ti.com/lit/pdf/slup415)*, Texas Instruments Power Supply Design Seminar
    SEM2600, 2024