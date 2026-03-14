---
source: "ADI MT-033 -- Voltage Feedback Op Amp Gain and Bandwidth"
url: "https://www.analog.com/media/en/training-seminars/tutorials/MT-033.pdf"
format: "PDF 8pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 11977
---
# Voltage Feedback Op Amp Gain and Bandwidth

## INTRODUCTION

This tutorial examines the common ways to specify op amp gain and bandwidth. It should be noted that this discussion applies to voltage feedback (VFB) op amps -- current feedback (CFB) op amps are discussed in a later tutorial (MT-034).

## OPEN-LOOP GAIN

Unlike the ideal op amp, a practical op amp has a finite gain. The open-loop dc gain (usually referred to as A_VOL) is the gain of the amplifier without the feedback loop being closed, hence the name "open-loop." For a precision op amp this gain can be very high, on the order of 160 dB (100 million) or more. This gain is flat from dc to what is referred to as the dominant pole corner frequency. From there the gain falls off at 6 dB/octave (20 dB/decade). An octave is a doubling in frequency and a decade is x10 in frequency. If the op amp has a single pole, the open-loop gain will continue to fall at this rate as shown in Figure 1A. A practical op amp will have more than one pole as shown in Figure 1B. The second pole will double the rate at which the open-loop gain falls to 12 dB/octave (40 dB/decade). If the open-loop gain has dropped below 0 dB (unity gain) before it reaches the frequency of the second pole, the op amp will be unconditionally stable at any gain. This will be typically referred to as unity gain stable on the data sheet. If the second pole is reached while the closed-loop gain is greater than 1 (0 dB), then the amplifier may not be stable. Some op amps are designed to be stable only at higher closed-loop gains, and these are referred to as decompensated op amps.

An op amp may have more additional parasitic poles at higher frequencies, however, the first two poles are generally the most important.

**Figure 1: Open-Loop Gain (Bode Plot)**
- (A) Single-Pole Response: Gain falls at 6 dB/octave
- (B) Two-Pole Response: Gain falls at 6 dB/octave then 12 dB/octave

It is important to understand the differences between open-loop gain, closed-loop gain, loop gain, signal gain and noise gain. They are similar in nature, interrelated, but different. We will discuss them all in detail.

The open-loop gain is not a precisely controlled spec. It has a relatively large range and will be given in the specifications as a typical number rather than a min/max number, in most cases. In some cases, typically high precision op amps, the spec will be given a minimum value.

In addition, the open-loop gain can change due to output voltage levels and loading. This is referred to as open-loop gain non-linearity. There is also some dependency on temperature. In general, these effects are of a very minor degree and can, in most cases, be ignored. In fact open-loop gain non-linearity is not always included in the data sheet for some op amps.

## CLOSED-LOOP GAIN

Closed-loop gain is the gain of the amplifier with the feedback loop closed, as opposed to the open-loop gain, which is the gain with the feedback loop opened. Closed-loop gain has two forms: signal gain and noise gain. These are described and differentiated below.

The classic expression for the gain of a closed-loop amplifier involves the open-loop gain. If G is the actual closed-loop gain, NG is the noise gain (see below), and A_VOL is the open-loop gain of the amplifier, it can be shown that:

G = NG / (1 + NG/A_VOL)  (Eq. 1)

From this you can see that if the open-loop gain is very high, which it typically is, the closed-loop gain of the circuit is simply the noise gain.

## SIGNAL GAIN AND NOISE GAIN

Signal gain is the gain applied to the input signal with the feedback loop connected. In Tutorial MT-032, when we talked about the gain of the inverting and non-inverting circuits, we were actually more correctly talking about the closed-loop signal gain. Signal gain can be positive (non-inverting mode) or negative (inverting mode), and can be less than unity for the inverting case. Signal gain is the gain of most interest when we are designing the elements in the signal path. Figure 2 illustrates the various gains in detail.

**Figure 2: Signal Gain and Noise Gain**

- Circuit A (Non-inverting): Signal Gain = 1 + R2/R1, Noise Gain = 1 + R2/R1
- Circuit B (Inverting): Signal Gain = -R2/R1, Noise Gain = 1 + R2/R1
- Circuit C (Inverting with R3): Signal Gain = -R2/R1, Noise Gain = 1 + R2/(R1||R3)

Key points:
- Voltage noise and offset voltage of the op amp are reflected to the output by the Noise Gain.
- Noise Gain, not Signal Gain, is relevant in assessing stability.
- Circuit C has unchanged Signal Gain, but higher Noise Gain, thus better stability, worse noise, and higher output offset voltage.

The signal gain for an inverting amplifier stage is:

Signal Gain = -R2/R1  (Eq. 2)

and for a non-inverting amplifier it is:

Signal Gain = 1 + R2/R1  (Eq. 3)

Noise gain is the gain seen by a noise source (input voltage noise) or voltage source (input offset voltage) connected in series with an op amp input. The noise gain is equal to:

Noise Gain = 1 + R2/R1  (Eq. 4)

Noise gain is equal to the signal gain of a non-inverting amp. Noise gain is also the same for either an inverting or non-inverting stage.

It is the noise gain that is used to determine op amp stability. Noise gain is equal to the closed-loop gain that is used in Bode plots. Resistances were used in the above expressions for noise gain, however, in practical applications they are actually impedances with real and imaginary components.

## LOOP GAIN

The difference between the open-loop gain and the closed-loop gain is known as the loop gain as shown in Figure 3. Loop gain shows you the amount of negative feedback that can be applied to the amplifier at a given frequency.

**Figure 3: Gain Definitions**
- Open-loop gain curve
- Noise gain (closed-loop gain) curve
- Loop gain = Open-loop gain - Noise gain (in dB)
- f_CL = closed-loop bandwidth (intersection point)

## BODE PLOT: ASYMPTOTIC AND ACTUAL RESPONSES

The plot of open-loop gain vs. frequency on a log-log scale is what is known as a Bode plot. It is one of the primary tools in evaluating whether an op amp is suitable for a particular application.

If you plot the open-loop gain and then the noise gain on a Bode plot as shown in Figure 4, the point where they intersect will determine the maximum closed-loop bandwidth of the amplifier system. This is commonly referred to as the closed-loop frequency (F_CL). Remember that the actual response at the intersection is actually 3 dB down from this value. At frequencies beyond one octave above and one octave below F_CL, the difference between the asymptotic response and the real response will be less than 1 dB.

The Bode plot is also useful in determining stability. As stated above, if the closed-loop gain (noise gain) intersects the open-loop gain at a slope of greater than 6 dB/octave (20 dB/decade) the amplifier may be unstable (depending on the phase margin).

**Figure 4: Bode Plot Showing Asymptotic and Actual Response**
- The asymptotic response shows a sharp corner at F_CL
- The actual response is 3 dB down at F_CL

## GAIN-BANDWIDTH PRODUCT

The open-loop gain falls at 6 dB/octave for a single-pole response. This means that if we double the frequency, the gain drops by a factor of two. Conversely, if the frequency is halved, the open-loop gain will double, as shown in Figure 5. This gives rise to what is known as the Gain-Bandwidth Product. If we multiply the open-loop gain by the frequency, the product is always a constant. The caveat for this is that we have to be in the part of the curve that is falling at 6 dB/octave. This gives us a convenient figure of merit with which to determine if a particular op amp is useable in a particular application. Note that the gain-bandwidth product is meaningful only for voltage feedback (VFB) op amps. The discussion of current feedback (CFB) op amp bandwidth can be found in Tutorial MT-034.

**Figure 5: Gain-Bandwidth Product**
- If Gain Bandwidth Product = X, and Noise Gain = Y = 1 + R2/R1
- Then f_CL = X/Y, where f_CL = closed-loop bandwidth

For example, if we have an application which requires a closed-loop gain of 10 and a bandwidth of 100 kHz, we need an op amp with a minimum gain-bandwidth product of 1 MHz. This is a slight oversimplification, however, because of the variability of the gain-bandwidth product and the fact that at the location where the closed-loop gain intersects the open-loop gain, the response is actually down 3 dB. In addition, some extra margin should be allowed.

In the application described above, an op amp with a gain-bandwidth product of 1 MHz would be marginal. A safety factor of at least 5 would be better insurance that the expected performance is achieved, and an op amp with a gain-bandwidth product of 5 MHz would therefore be chosen.

## STABILITY CRITERIA

Feedback stability theory states that the closed-loop gain must intersect the open-loop gain at a slope no greater than 6 dB/octave (single pole response) for the system to be unconditionally stable. If the response is 12 dB/octave (two pole response), the op amp will oscillate. The easiest way to think of this is that each pole adds 90 degrees of phase shift. Two poles yields 180 degrees phase shift, and 180 degrees of phase shift turns negative feedback into positive feedback which means oscillations.

The question could be asked -- why would you want an amplifier that is not unity gain stable? The answer is that for a given amplifier, the bandwidth can be increased at higher gains if the amplifier is not designed to be unity gain stable. This type of op amp is sometimes referred to as a decompensated op amp. However, the stability criteria still must be met. This criteria is that the closed-loop gain must intercept the open-loop gain at a slope of 6 dB/octave (single pole response). If not, the amplifier will oscillate. Decompensated op amps will therefore only be stable at higher gains which are specified on the data sheet.

As an example, compare the open-loop gain graphs in Figure 6. The three parts shown, the AD847, AD848 and AD849, are basically the same design with different internal compensation:

- **AD847**: Unity gain stable, GBW = 50 MHz, G >= 1 (+/-15V)
- **AD848**: Stable for gains of 5 or more, GBW = 175 MHz, G >= 5 (+/-15V)
- **AD849**: Stable for gain of 25 or more, GBW = 725 MHz, G >= 25 (+/-15V)

This illustrates how op amp internal compensation can be modified to yield various gain-bandwidth products as a function of minimum stable gain for the same basic design.

## PHASE MARGIN

One measure of stability is phase margin. Just as the amplitude response doesn't stay flat and then change instantaneously, the phase response will also change gradually, starting approximately a decade before the corner frequency. Phase margin is the amount of phase shift that is left until you reach 180 degrees, measured at the frequency at which the closed-loop gain intersects the open-loop gain.

The result of low phase margin is an increase in gain peaking just before the frequency at which the closed-loop gain intersects the open-loop gain. Figure 7 shows the gain and phase response for the AD8051 op amp. In this case the phase margin is 45 degrees at the frequency of unity gain.

**Figure 7: AD8051 Phase Margin** -- Shows gain and phase response curves

## REFERENCES

1. Hank Zumbahlen, Basic Linear Design, Analog Devices, 2006, ISBN: 0-915550-28-1. Also available as Linear Circuit Design Handbook, Elsevier-Newnes, 2008, ISBN-10: 0750687037, ISBN-13: 978-0750687034. Chapter 1.
2. Walter G. Jung, Op Amp Applications, Analog Devices, 2002, ISBN 0-916550-26-5, Also available as Op Amp Applications Handbook, Elsevier/Newnes, 2005, ISBN 0-7506-7844-5. Chapter 1.
