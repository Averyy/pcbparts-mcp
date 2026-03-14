---
source: "TI SLOA020A -- Stability Analysis of VFB Op Amps Including Compensation"
url: "https://www.ti.com/lit/an/sloa020a/sloa020a.pdf"
format: "PDF 30pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 21594
---
# Stability Analysis of Voltage-Feedback Op Amps Including Compensation Techniques

Ron Mancini

## ABSTRACT

This report presents an analysis of the stability of voltage-feedback operational amplifiers (op amps) using circuit performance as the criteria to attain a successful design. It discusses several compensation techniques for op amps with and without internal compensation.

## 1 Introduction

Voltage-feedback amplifiers (VFA) have been with us for about 60 years, and they have been a problem for circuit designers since the first day. The feedback that makes them versatile and accurate also has a tendency to make them unstable. The operational-amplifier (op amp) circuit configuration uses a high-gain amplifier whose parameters are determined by external feedback components. The amplifier gain is so high, that without these external feedback components, the slightest input signal would saturate the amplifier output. The op amp is in common usage, so this configuration is examined in detail, but the results are applicable to many other voltage feedback circuits. Current feedback amplifiers (CFA) are similar to VFAs, but the differences are important enough to warrant CFAs being handled in a separate application note.

Stability, as used in electronic circuit terminology, is often defined as achieving a nonoscillatory state. This is a poor, inaccurate definition of the word. Stability is a relative term, and this situation makes people uneasy because relative judgments are exhaustive. It is easy to draw the line between a circuit that oscillates and one that does not oscillate, so we can understand why some people believe that oscillation is a natural boundary between stability and instability.

Feedback circuits exhibit poor phase response, overshoot, and ringing long before oscillation occurs, and these effects are considered undesirable by circuit designers. This application note is not concerned with oscillators; thus, relative stability is defined in terms of performance. By definition, when designers decide what tradeoffs are acceptable they determine what the relative stability of the circuit is. A relative-stability measurement is the damping ratio (zeta) and the damping ratio is discussed in detail in Reference 1. The damping ratio is related to phase margin, hence, phase margin is another measure of relative stability.

The most stable circuits have the longest response times, lowest bandwidth, highest accuracy, and least overshoot. The least stable circuits have the fastest response times, highest bandwidth, lowest accuracy, and some overshoot.

Amplifiers are built with active components such as transistors. Pertinent transistor parameters like transistor gain are subject to drift and initial inaccuracies from many sources. The drift and inaccuracy is minimized or eliminated by using negative feedback. The op-amp circuit configuration employs feedback to make the transfer equation of the circuit independent of the amplifier parameters (well almost), and while doing this, the circuit transfer function is made dependent on external passive components. The external passive components can be purchased to meet almost any drift or accuracy specification.

Once feedback is applied to the op amp, it is possible for the op-amp circuit to become unstable. Certain amplifiers belong to a family called internally compensated op amps; they contain internal capacitors which are sometimes advertised as precluding instabilities. Although internally compensated op amps should not oscillate when operated under specified conditions, many have relative stability problems that manifest themselves as poor phase response, ringing, and overshoot. The only absolutely stable internally compensated op amp is the one lying on the workbench without power applied! All other internally compensated op amps oscillate under some external circuit conditions.

Noninternally compensated or externally compensated op amps are unstable without the addition of external stabilizing components. This situation is a disadvantage in many cases because they require additional components, but the lack of internal compensation enables the top-drawer circuit designer to squeeze the last drop of performance from the op amp. You have two options: op amps internally compensated by the IC manufacturer, or op amps externally compensated by you.

Compensation is achieved by adding external components that modify the circuit transfer function so that it becomes unconditionally stable. There are several different methods of compensating an op amp, and as you might suspect, there are pros and cons associated with each method of compensation.

## 2 Development of the Circuit Equations

A block diagram for a generalized feedback system is shown in Figure 1.

**Figure 1: Feedback System Block Diagram** -- Shows V_IN -> Summing junction (+, -) -> E -> A -> V_OUT, with feedback path beta.

The output and error equations are:

V_OUT = E * A  (Eq. 1)

E = V_IN - beta * V_OUT  (Eq. 2)

Combining equations 1 and 2 and rearranging yields the classic form of the feedback equation:

V_OUT / V_IN = A / (1 + A*beta)  (Eq. 5)

When the term A*beta becomes very large with respect to one, this reduces to the ideal feedback equation:

V_OUT / V_IN = 1 / beta  (Eq. 6)

The quantity A*beta is so important that it has been given a special name: **loop gain**. When the voltage inputs are grounded (current inputs are opened) and the loop is broken, the calculated gain is the loop gain, A*beta.

**Figure 2: Feedback Loop Broken to Calculate Loop Gain** -- V(Return)/V(Test) = A*beta

When the loop gain approaches minus one, or 1 at 180 degrees, equation 5 approaches infinity because 1/0 -> infinity. The circuit output heads for infinity as fast as it can, but it is energy limited by the power supplies.

Active devices in electronic circuits exhibit nonlinear behavior when their output approaches a power supply rail, and the nonlinearity reduces the amplifier gain until the loop gain no longer equals 1 at 180 degrees. The circuit can then either become stable at the power supply limit (**lockup**) or reverse direction and head for the negative power supply rail (**oscillatory**).

The loop gain, A*beta, is the sole factor that determines stability for a circuit or system. Inputs are grounded or disconnected when the loop gain is calculated, so they have no effect on stability.

The error equation is:

E = V_IN / (1 + A*beta)  (Eq. 7)

The error is proportional to the input signal and inversely proportional to the loop gain. Large loop gains decrease error but also decrease stability -- there is always a tradeoff between error and stability.

### Noninverting Op Amp

**Figure 3: Noninverting Op Amp** -- V_IN -> (+) input, Z_F and Z_G in feedback path

The transfer function is:

V_OUT / V_IN = a / (1 + a*Z_G/(Z_G + Z_F))  (Eq. 11)

The loop gain equation for the noninverting op amp:

A*beta = a*Z_G / (Z_G + Z_F)  (Eq. 13)

### Inverting Op Amp

**Figure 4: Inverting Op Amp** -- V_IN through Z_G to (-) input, Z_F in feedback

The transfer function is:

V_OUT / V_IN = (-a*Z_F / (Z_G + Z_F)) / (1 + a*Z_G/(Z_G + Z_F))  (Eq. 16)

The loop gain:

A*beta = a*Z_G / (Z_G + Z_F)  (Eq. 17)

Several important points:
1. The transfer functions for noninverting and inverting equations are different.
2. The loop gain of both circuits is identical -- thus the stability performance of both circuits is identical although their transfer equations are different.
3. Stability is not dependent on the circuit inputs.
4. The A gain block is different for each circuit: A_NONINV = a, A_INV = a*Z_F/(Z_G + Z_F).

## 3 Internal Compensation

Op amps are internally compensated to save external components and to enable their use by less knowledgeable people. Internally compensated op amps normally are stable when used in accordance with the applications instructions. They are multiple pole systems, but they are internally compensated such that they appear as a single pole system over much of the frequency range. The cost of internal compensation is that it severely decreases the closed-loop bandwidth of the op amp.

Internal compensation is accomplished in several ways, but the most common method is to connect a capacitor across the collector-base junction of a voltage gain transistor (**Miller effect compensation**, Figure 6). The Miller effect multiplies the capacitor value by an amount approximately equal to the stage gain, thus using small value capacitors for compensation.

**TL03X Analysis (Figure 7):** When the gain crosses the 0-dB axis, the phase shift is about 100 degrees, yielding a phase margin of phi = 180 - 100 = 80 degrees. The circuit should be very stable. The damping ratio is approximately one and expected overshoot is zero. However, loading capacitance (100 pF vs 25 pF shown on gain/phase plot) accounts for loss of phase margin and ~10% overshoot in pulse response.

**Why does loading capacitance make the op amp unstable?** The radical gain/phase slope change between 1 MHz and 9 MHz proves that several poles are located in this area. The loading capacitance works with the op-amp output impedance to form another pole, and the new pole reacts with the internal op-amp poles. As the loading capacitor value is increased, its pole migrates down in frequency, causing more phase shift at the 0-dB crossover frequency.

**Figure 8: Phase Margin and Percent Overshoot Versus Damping Ratio** -- Shows the relationship between damping ratio (0 to 1), phase margin (0 to 80 degrees), and percent maximum overshoot.

**TL07X Analysis (Figure 9):** Phase shift is 100 degrees at 0-dB axis crossing, yielding 80 degrees phase margin. The pulse response shows approximately 20% overshoot, which is inconsistent with the gain/phase analysis. Comparison with TL08X data (Figure 10, which is identical but lists 100-pF loading capacitor) reveals three lessons: (1) if the data seems wrong it probably is wrong, (2) even the factory people make mistakes, and (3) the loading capacitor makes op amps ring, overshoot, or oscillate.

**TLV277X Analysis (Figures 11 and 12):** More sophisticated data -- phase response given in degrees of phase margin, gain/phase plots done with 600 pF loading. At V_CC = 5 V, phase margin at 0-dB crossover is 60 degrees (expected overshoot 18%). At V_CC = 2.7 V, phase margin is 30 degrees (expected overshoot 28%).

Internally compensated op amps are very desirable because they are easy to use and do not require external compensation components. Their drawback is that the bandwidth is limited by the internal compensation scheme. If the TLV277X were not internally compensated, it could be externally compensated for a lower error at 50 kHz because the gain would be much higher.

## 4 External Compensation, Stability, and Performance

Nobody compensates an op amp because it is there; they have a reason to compensate the op amp, and that reason is usually stability. Other reasons include noise reduction, flat amplitude response, and obtaining the highest bandwidth possible from an op amp.

An op amp generates noise, and noise is generated by the system. When a high-pass filter is incorporated in the signal path, it reduces high-frequency noise. Compensation can be employed to roll off the op amp's high-frequency closed-loop response, causing the op amp to act as a noise filter.

Internally compensated op amps are modeled with a second order equation, meaning the output voltage can overshoot in response to a step input. When this overshoot (or peaking) is undesirable, external compensation can increase the phase margin to 90 degrees where there is no peaking.

An uncompensated op amp has the highest bandwidth possible. External compensation is required to stabilize uncompensated op amps, but the compensation can be tailored to the specific circuit, yielding the highest possible bandwidth consistent with the pulse response requirements.

## 5 Dominant-Pole Compensation

An op amp loaded with an output capacitor is a circuit configuration that must be analyzed. This circuit is called dominant pole compensation because if the pole formed by the op amp output impedance and the loading capacitor is located close to the zero frequency axis, it becomes dominant.

**Figures 13, 14: Capacitively-Loaded Op Amp** -- V_IN -> op amp with Z_O output impedance, C_L load, Z_F and Z_G feedback.

The loop gain with capacitive loading (assuming (Z_F + Z_G) >> Z_O):

A*beta = [a*Z_G / (Z_F + Z_G)] * [1 / (Z_O*C_L*s + 1)]  (Eq. 22)

Modeling the op amp as a second-order system, a = K / ((s + tau_1)(s + tau_2)), the stability equation becomes:

A*beta = [K*Z_G / ((s+tau_1)(s+tau_2)(Z_F+Z_G))] * [1 / (Z_O*C_L*s + 1)]  (Eq. 24)

**Figure 15: Possible Bode Plot** -- Shows a two-pole op amp with only 25 degrees phase margin and approximately 48% overshoot.

When the pole introduced by Z_O and C_L moves towards zero frequency, it comes close to the tau_2 pole, adding phase shift and decreasing stability. In the real world, many loads (especially cables) are capacitive, and an op amp with limited phase margin would ring while driving a capacitive load.

**Figure 16: Dominant-Pole Compensation Plot** -- Shows how adding a dominant pole (omega_D) before the first internal pole rolls off the gain so that tau_1 introduces 45 degrees phase at the 0 dB crossover, yielding 45 degrees phase margin. The op-amp gain is drastically reduced for frequencies higher than omega_D.

As long as the op amp has enough compliance and current to drive the capacitive load and Z_O is small, the circuit functions as though the capacitor was not there. When the capacitor becomes large enough, its pole interacts with the op amp pole causing instability. When the capacitor is huge, it completely kills the op amp's bandwidth, lowering noise while retaining large low-frequency gain.

## 6 Gain Compensation

When the closed-loop gain of an op-amp circuit is related to the loop gain, as it is in voltage feedback op amps, the gain can be used to stabilize the circuit. This type of compensation cannot be used in current feedback op amps because the mathematical relationship between the loop gain and ideal closed-loop gain does not exist.

The loop gain equation:

A*beta = a*Z_G / (Z_G + Z_F)  (Eq. 27)

**Figure 17: Gain Compensation** -- If the closed-loop noninverting gain is changed from 1 to 9, K changes from K/2 to K/10. The loop-gain intercept moves down 14 dB, and the circuit is stabilized.

Gain compensation works for inverting or noninverting op-amp circuits. When the closed-loop gain is increased, the accuracy and bandwidth decrease. As long as the application can stand the higher gain, gain compensation is the best type of compensation to use.

## 7 Lead Compensation

Sometimes lead compensation is forced on the circuit designer because of the parasitic capacitance associated with packaging and wiring op amps.

**Figure 18: Lead-Compensation Circuit** -- Inverting op amp with capacitor C in parallel with R_F.

The loop equation for lead compensation:

A*beta = [R_G / (R_G + R_F)] * [(R_F*C*s + 1) / (R_G || R_F)*C*s + 1)] * [K / ((s+tau_1)(s+tau_2))]  (Eq. 28)

The compensation capacitor introduces a pole and zero into the loop equation. The zero always occurs before the pole because R_F > R_F||R_G. When the zero is properly placed it cancels out the tau_2 pole along with its associated phase shift.

**Figure 19: Lead-Compensation Bode Plot** -- Shows how the R_F*C zero at omega = 1/tau_2 cancels the tau_2 pole, causing the Bode plot to continue on a slope of -20 dB/decade.

The ideal closed-loop gain equation for the inverting case:

V_OUT/V_IN = -(R_F/R_G) * [1/(R_F*C*s + 1)]  (Eq. 31)

Lead compensation sacrifices the bandwidth between the 1/(R_F*C) breakpoint and the forward gain curve. The noninverting case (Eq. 33):

V_OUT/V_IN = [(R_F + R_G)/R_G] * [(R_F || R_G)*C*s + 1] / [R_F*C*s + 1]

Although the forward gain is different in the inverting and noninverting circuits, the closed-loop transfer functions take very similar shapes. This becomes truer as the closed-loop gain increases.

## 8 Compensated Attenuator Applied to Op Amp

Stray capacitance on op-amp inputs is a problem that circuit designers are always trying to get away from because it decreases closed-loop frequency response or causes peaking.

**Figure 22: Op Amp With Stray Capacitance C_G on the Inverting Input**

The loop gain with input capacitance:

A*beta = [R_G / (R_G + R_F)] * [1 / ((R_F||R_G)*C_G*s + 1)] * [K / ((tau_1*s+1)(tau_2*s+1))]  (Eq. 34)

Op amps having high input and feedback resistors are subject to instability caused by stray capacitance on the inverting input. Example: R_F = 1 Mohm, R_G = 1 Mohm, C_G = 10 pF. The resulting pole occurs at 318 kHz, which is lower than the breakpoint of tau_2 for many op amps. This circuit is unstable because of the stray input capacitance.

**Figure 23: Compensated Attenuator Circuit** -- Adding feedback capacitor C_F.

If R_G*C_G = R_F*C_F, the loop gain reduces to:

A*beta = [R_G/(R_G+R_F)] * [K / ((tau_1*s+1)(tau_2*s+1))]  (Eq. 36)

The compensated attenuator is independent of the capacitors. Adding the correct 1/(R_F*C_F) breakpoint cancels the 1/(R_G*C_G) breakpoint.

**Practical tip:** C_F can be formed by running a wide copper strip from the output of the op amp over the ground plane under R_F; do not connect the other end. The circuit is tuned by removing some copper (a razor works well) until all peaking is eliminated. Then measure the copper, and have an identical trace put on the PCB.

When R_F*C_F = R_G*C_G, the closed-loop gain is independent of the breakpoint:

V_OUT/V_IN = -R_F/R_G  (Eq. 38)

This is one of the few occasions when the compensation does not affect the closed-loop gain frequency response.

## 9 Lead-Lag Compensation

Lead-lag compensation stabilizes the circuit without sacrificing the closed-loop gain performance. It is often used with uncompensated op amps and leads to excellent high-frequency performance.

**Figure 25: Lead-Lag Compensated Op Amp** -- Series RC network from V_IN to R_G.

A*beta = [K*R_G / ((tau_1*s+1)(tau_2*s+1))] * [(R*C*s+1) / ((R*R_G+R*R_F+R_G*R_F)/(R_G+R_F))*C*s+1)]  (Eq. 39)

A pole is introduced at omega = 1/(R*C), reducing the gain 3 dB at the breakpoint. When the zero occurs prior to the first op-amp pole it cancels out the phase shift caused by the pole. A*beta is reduced by 3 dB or more, so the loop gain crosses the 0-dB axis at a lower frequency.

**The beauty of lead-lag compensation is that the closed-loop ideal gain is not affected:**

V_OUT/V_IN = -R_F/R_G  (Eq. 42)

This is intuitively obvious because the RC network is placed across a virtual ground. As long as the loop gain (A*beta) is large, the feedback will null out the closed-loop effect of RC, and the circuit will function as if it weren't there.

## 10 Comparison of Compensation Schemes

- **Internally compensated op amps** can, and often do, oscillate under some circuit conditions. They need an external pole to get the oscillation started, and circuit stray capacitances often supply the phase shift required for instability. Loads such as cables often cause internally compensated op amps to ring severely.

- **Dominant pole compensation** is often used in IC design because it is easy to implement. It rolls off the closed-loop gain early; thus, it is seldom used as an external form of compensation unless filtering is required. Large load capacitance can stabilize the op amp because it acts as dominant pole compensation.

- **Gain compensation** is the simplest form. High closed-loop gains are reflected in lower loop gains, which increase stability. If an op-amp circuit can be stabilized by increasing the closed-loop gain, do it.

- **Lead compensation** (stray capacitance across the feedback resistor) tends to stabilize the op amp. This compensation scheme is useful for limiting the circuit bandwidth, but it decreases the closed-loop gain at high frequencies.

- **Compensated attenuator** cancels stray input capacitance with a feedback capacitor. When R_F*C_F = R_G*C_G, the op amp functions as though the stray input capacitance was not there.

- **Lead-lag compensation** stabilizes the op amp and yields the best closed-loop frequency performance. Contrary to some published opinions, no compensation scheme will increase the bandwidth beyond that of the op amp. Lead-lag compensation just gives the best bandwidth for the compensation.

## 11 Conclusion

The stability criteria often is not oscillation, rather, it is circuit performance as exhibited by peaking and ringing.

The circuit bandwidth can often be increased by connecting an external capacitor in parallel with the op amp. Some op amps have hooks which enable a parallel capacitor to be connected in parallel with a portion of the input stages. This increases bandwidth because it shunts high frequencies past the low bandwidth g_m stages, but this method depends on the op amp type and manufacturer.

The compensation techniques given here are adequate for the majority of applications. When the new and challenging application presents itself, use the procedure outlined here to invent your own compensation technique.

## 12 Reference

1. Mancini, Ron, Feedback Amplifier Analysis Tools, SLVA058, Texas Instruments, 1999.
