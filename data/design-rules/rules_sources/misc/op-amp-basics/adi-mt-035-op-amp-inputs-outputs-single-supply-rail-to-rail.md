---
source: "ADI MT-035 -- Op Amp Inputs, Outputs, Single-Supply, Rail-to-Rail"
url: "https://www.analog.com/media/en/training-seminars/tutorials/MT-035.pdf"
format: "PDF 12pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 20404
---
# Op Amp Inputs, Outputs, Single-Supply, and Rail-to-Rail Issues

## SINGLE-SUPPLY OP AMP ISSUES

Single-supply operation has become an increasingly important requirement because of market demands. Automotive, set-top box, camera/camcorder, PC, and laptop computer applications are demanding IC vendors to supply an array of linear devices that operate on a single-supply rail, with the same performance of dual supply parts. Power consumption is now a key parameter for line or battery operated systems, and in some instances, more important than cost. This makes low-voltage/low supply current operation critical; at the same time, however, accuracy and precision requirements have forced IC manufacturers to meet the challenge of "doing more with less" in their amplifier designs.

In a single-supply application, the most immediate effect on the performance of an amplifier is the reduced input and output signal range. As a result of these lower input and output signal excursions, amplifier circuits become more sensitive to internal and external error sources. Precision amplifier offset voltages on the order of 0.1 mV are less than a 0.04 LSB error source in a 12-bit, 10 V full-scale system. In a single-supply system, however, a "rail-to-rail" precision amplifier with an offset voltage of 1 mV represents a 0.8 LSB error in a 5 V full-scale system (or 1.6 LSB for 2.5 V full-scale).

Gain accuracy in some low voltage single-supply devices is also reduced, so device selection needs careful consideration. Many amplifiers with ~120 dB open-loop gains typically operate on dual supplies -- for example OP07 types. However, many single-supply/rail-to-rail amplifiers for precision applications typically have open-loop gains between 25,000 and 30,000 under light loading (>10 kohm). Selected devices, like the OP113/OP213/OP413 family, do have high open-loop gains (>120 dB), for use in demanding applications. Another example would be the AD855x chopper-stabilized op amp series.

Besides these limitations, many other design considerations that are otherwise minor issues in dual-supply amplifiers now become important. For example, signal-to-noise (SNR) performance degrades as a result of reduced signal swing. "Ground reference" is no longer a simple choice, as one reference voltage may work for some devices, but not others. Amplifier voltage noise increases as operating supply current drops, and bandwidth decreases. Achieving adequate bandwidth and required precision with a somewhat limited selection of amplifiers presents significant system design challenges in single-supply, low-power applications.

Most circuit designers take "ground" reference for granted. Many analog circuits scale their input and output ranges about a ground reference. In dual-supply applications, a reference that splits the supplies (0 V) is very convenient, as there is equal supply headroom in each direction, and 0 V is generally the voltage on the low impedance ground plane. In single-supply/rail-to-rail circuits, however, the ground reference can be chosen anywhere within the supply range of the circuit, since there is no standard to follow. The choice of ground reference depends on the type of signals processed and the amplifier characteristics. For example, choosing the negative rail as the ground reference may optimize the dynamic range of an op amp whose output is designed to swing to 0 V. On the other hand, the signal may require level shifting in order to be compatible with the input of other devices (such as ADCs) that are not designed to operate at 0 V input.

The need for rail-to-rail amplifier output stages is also driven by the need to maintain wide dynamic range in low-supply voltage applications. A single-supply/rail-to-rail amplifier should have output voltage swings that are within at least 100 mV of either supply rail (under a nominal load). The output voltage swing is very dependent on output stage topology and load current.

**Figure 1: Single-Supply Op Amp Design Issues**
- Single Supply Offers: Lower Power, Battery Operated Portable Equipment, Requires Only One Voltage
- Design Tradeoffs: Reduced Signal Swing Increases Sensitivity to Errors, Must Usually Share Noisy Digital Supply, Rail-to-Rail Input and Output Needed, Precision Less than the best Dual Supply Op Amps

## OP AMP INPUT STAGES

It is extremely important to understand input and output structures of op amps in order to properly design the required interfaces. For ease of discussion, the two can be examined separately.

### Bipolar Input Stages

The very common and basic bipolar input stage consists of a "long-tailed pair" built with bipolar transistors (Figure 2). It has a number of advantages: it is simple, has very low offset, the bias currents in the inverting and non-inverting inputs are well-matched and do not vary greatly with temperature. In addition, minimizing the initial offset voltage of a bipolar op amp by laser trimming also minimizes its drift over temperature. This architecture was used in the very earliest monolithic op amps such as the uA709. It is also used with modern high speed types.

**Figure 2: A Bipolar Transistor Input Stage**
- Low Offset: As low as 10 uV
- Low Offset Drift: As low as 0.1 uV/C
- Temperature Stable I_B
- Well-Matched Bias Currents
- Low Voltage Noise: As low as 1 nV/sqrt(Hz)
- High Bias Currents: 50 nA - 10 uA (Except Super-Beta: 50 pA - 5 nA)
- Medium Current Noise: 1 pA/sqrt(Hz)
- Matching source impedances minimizes offset error due to bias current

### Bias Current Compensated Bipolar Input Stage

**Figure 3: A Bias Current Compensated Bipolar Input Stage**
- Low Offset Voltage: As low as 10 uV
- Low Offset Drift: As low as 0.1 uV/C
- Temperature Stable I_bias
- Low Bias Currents: <0.5 - 10 nA
- Low Voltage Noise: As low as 1 nV/sqrt(Hz)
- Poor Bias Current Match (currents may even flow in opposite directions)
- Higher Current Noise
- Not very useful at HF
- Matching source impedances makes offset error due to bias current worse

A simple bipolar input stage exhibits high bias current because the currents seen externally are in fact the base currents of the two input transistors. By providing this necessary bias current via an internal current source (Figure 3), the only external current then flowing in the input terminals is the difference current between the base current and the current source, which can be quite small.

Most modern precision op amps use some means of internal bias current compensation, examples would be the familiar OP07 and OP27 series.

Bias current compensated input stages have many of the good features of the simple bipolar input stage, namely: low voltage noise, low offset, and low drift. Additionally, they have low bias current which is fairly stable with temperature. However, their current noise is not very good, and their bias current matching is poor.

These latter two undesired side effects result from the external bias current being the difference between the compensating current source and the input transistor base current. Both of these currents inevitably have noise. Since they are uncorrelated, the two noises add in a root-sum-of-squares fashion (even though the dc currents subtract). Since the resulting external bias current is the difference between two nearly equal currents, there is no reason why the net current should have a defined polarity. As a result, the bias currents of a bias-compensated op amp may not only be mismatched, they can actually flow in opposite directions.

In many cases, the bias current compensation feature is not mentioned on an op amp data sheet, and a simplified schematic isn't supplied. It is easy to determine if bias current compensation is used by examining the bias current specification. If the bias current is specified as a "+/-" value, the op amp is most likely compensated for bias current.

Note that this can easily be verified, by examining the offset current specification (the difference in the bias currents). If internal bias current compensation exists, the offset current will be of the same magnitude as the bias current. Without bias current compensation, the offset current will generally be at least a factor of 10 smaller than the bias current.

The effects of bias current on the output offset voltage of an op amp can often be cancelled by making the source resistances at the two inputs equal. But, there is an important caveat here. The validity of this practice only holds true for bipolar input op amps without bias current compensation, that is, where the input currents are well matched. In a case of an op amp using internal bias current compensation, adding an extra resistance to either input will usually make the output offset worse!

### FET Input Stages

Field-Effect Transistors (FETs) have much higher input impedance than do bipolar junction transistors (BJTs) and would therefore seem to be ideal devices for op amp input stages. However, they cannot be manufactured on all bipolar IC processes, and when a process does allow their manufacture, they often have their own problems.

FETs have high input impedance, low bias current, and good high frequency performance (in an op amp, the lower g_m of the FET devices allows higher tail currents, thereby increasing the maximum slew rate). FETs also have much lower current noise.

On the other hand, the input offset voltage of FET long-tailed pairs is not as good as the offset of corresponding BJTs, and trimming for minimum offset does not simultaneously minimize drift. A separate trim is needed for drift, and as a result, offset and drift in a JFET op amp, while good, aren't as good as the best BJT ones.

It is possible to make JFET op amps with very low voltage noise, but the devices involved are very large and have quite high input capacitance, which varies with input voltage, and so a trade-off is involved between voltage noise and input capacitance.

The bias current of an FET op amp is the leakage current of the gate diffusion (or the leakage of the gate protection diode, which has similar characteristics for a MOSFET). Such leakage currents double with every 10 C increase in chip temperature so that a FET op amp bias current is one thousand times greater at 125 C than at 25 C. Obviously this can be important when choosing between a bipolar or FET input op amp, especially in high temperature applications where bipolar op amp input bias current actually decreases.

In practice, combined bipolar/JFET technology op amps (i.e., BiFET) achieve better performance than op amps using purely MOSFET or CMOS technology. While ADI and others make high performance op amps with MOS or CMOS input stages, in general these op amps have worse offset and drift, voltage noise, high-frequency performance than the precision bipolar counterparts. The power consumption is usually somewhat lower than that of bipolar op amps with comparable, or even better, performance.

JFET devices require more headroom than do BJTs, since their pinchoff voltage is typically greater than a BJT's base-emitter voltage. Consequently, they are more difficult to operate at very low power supply voltages (1-2 V). In this respect, CMOS has the advantage of requiring less headroom than JFETs.

### Rail-to-Rail Input Stages

Today, there is common demand for op amps with input CM voltage that includes both supply rails, i.e., rail-to-rail CM operation. While such a feature is undoubtedly useful in some applications, engineers should recognize that there are still relatively few applications where it is absolutely essential. These applications should be distinguished from the many more applications where a CM range close to the supplies, or one that includes one supply is necessary, but true input rail-to-rail operation is not.

In many single-supply applications, it is required that the input CM voltage range extend to one of the supply rails (usually ground). High-side or low-side current-sensing applications are examples of this. Many amplifiers can handle 0 V CM inputs, and they are easily designed using PNP (or PMOS) differential pairs (or N-channel JFET pairs) as shown in Figure 4. The input CM range of such an op amp generally extends from about 200 mV below the negative rail (-V_S or ground), to about 1-2 V of the positive rail, +V_S.

An input stage could also be designed with NPN (or NMOS) transistors (or P-channel JFETs), in which case the input CM range would include the positive rail, and go to within about 1-2 V of the negative rail. The OP282/OP482 input stage uses a P-channel JFET input pair whose input CM range includes the positive rail, making it suitable for high-side sensing.

A simplified diagram of a true rail-to-rail input stage is shown in Figure 5. Note that this requires use of two long-tailed pairs, one of PNP bipolar transistors Q1-Q2, the other of NPN transistors Q3-Q4. Similar input stages can also be made with CMOS pairs.

It should be noted that these two pairs will exhibit different offsets and bias currents, so when the applied CM voltage changes, the amplifier input offset voltage and input bias current does also. In fact, when both current sources remain active throughout most of the entire input common-mode range, amplifier input offset voltage is the average offset voltage of the two pairs. In those designs where the current sources are alternatively switched off at some point along the input common-mode voltage, amplifier input offset voltage is dominated by the PNP pair offset voltage for signals near the negative supply, and by the NPN pair offset voltage for signals near the positive supply.

Amplifier input bias current, a function of transistor current gain, is also a function of the applied input common-mode voltage. The result is relatively poor common-mode rejection (CMR), and a changing common-mode input impedance over the CM input voltage range, compared to familiar dual-supply devices. These specifications should be considered carefully when choosing a rail-to-rail input op amp, especially for a non-inverting configuration.

True rail-to-rail amplifier input stage designs must transition from one differential pair to the other differential pair, somewhere along the input CM voltage range. Some devices like the OP191/OP291/OP491 family and the OP279 have a common-mode crossover threshold at approximately 1 V below the positive supply (where signals do not often occur). Op amps like the OP184/OP284/OP484 family utilize a rail-to-rail input stage design where both NPN and PNP transistor pairs are active throughout most of the entire input CM voltage range, with no CM crossover threshold.

In light of the many quirks of true rail-to-rail op amp input stages, applications which do require true rail-to-rail inputs should be carefully evaluated, and an amplifier chosen to ensure that its input offset voltage, input bias current, common-mode rejection, and noise (voltage and current) are suitable.

## OUTPUT STAGES

The earliest IC op amp output stages were NPN emitter followers with NPN current sources or resistive pull-downs (Figure 6A). Naturally, the slew rates were greater for positive-going than they were for negative-going signals.

While all modern op amps have push-pull output stages of some sort, many are still asymmetrical, and have a greater slew rate in one direction than the other. Asymmetry tends to introduce distortion on ac signals and generally results from the use of IC processes with faster NPN than PNP transistors.

**Figure 6: Some Traditional Op Amp Output Stages**
- (A) NPN emitter follower with NPN pull-down
- (B) NPN emitter follower with FET current source
- (C) Complementary emitter follower (NPN + PNP) -- low output impedance, but output only swings within ~1 V_BE of either rail

With modern complementary bipolar (CB) processes, well matched high speed PNP and NPN transistors are readily available. The complementary emitter follower output stage shown in Figure 6C has many advantages, but the most outstanding one is the low output impedance. However, the output voltage of this stage can only swing within about one V_BE drop of either rail. Therefore an output swing of +1 V to +4 V is typical of such a stage, when operated on a single +5 V supply.

**Figure 7: "Almost" Rail-To-Rail Output Structures**
- (A) Complementary common-emitter (BJT): Swings limited by saturation voltage (V_CESAT). For small load currents (<100 uA), V_CESAT may be as low as 5-10 mV, but for higher load currents, can increase to several hundred mV (e.g., 500 mV at 50 mA).
- (B) Complementary common-source (CMOS FET): Can provide nearly true rail-to-rail performance under no-load conditions. If the output must source or sink substantial current, the output voltage swing will be reduced by the I*R drop across the FET's internal "on" resistance (typically ~100 ohm for precision amplifiers, but can be <10 ohm for high current drive CMOS amplifiers).

The complementary common-emitter/common-source output stages allow the op amp output voltage to swing much closer to the rails, but these stages have much higher open-loop output impedance than do the emitter follower-based stages of Figure 6C. In practice, however, the amplifier's high open-loop gain and the applied feedback can still produce an application with low output impedance (particularly at frequencies below 10 Hz). What should be carefully evaluated with this type of output stage is the loop gain within the application, with the load in place. Care should be taken that the application loading doesn't drop lower than the rated load, or gain accuracy may be lost.

For the above basic reasons, it should be apparent that there is no such thing as a true rail-to-rail output stage. The best any op amp output stage can do is an almost rail-to-rail swing, when it is lightly loaded.

## CIRCUIT DESIGN CONSIDERATIONS FOR SINGLE SUPPLY SYSTEMS

Many waveforms are bipolar in nature. This means that the signal naturally swings around the reference level, which is typically ground. This obviously won't work in a single supply environment. What is required is to ac couple the signals.

**Figure 8: Single Supply Biasing** -- Shows ac-coupled input with voltage divider bias (R4, R5) to establish a mid-supply reference point, with input coupling capacitor C_IN and output coupling capacitor C_OUT.

AC coupling is simply applying a high pass filter and establishing a new reference level typically somewhere around the center of the supply voltage range. The series capacitor will block the dc component of the input signal. The corner frequency is:

f_C = 1 / (2*pi*R_EQ*C)  (Eq. 1)

where R_EQ = R4*R5 / (R4 + R5)  (Eq. 2)

If multiple sections are ac coupled, each section will be 3 dB down at the corner frequency. So if there are two sections with the same corner frequency, the total response will be 6 dB down, three sections would be 9 dB down etc.

**Figure 9: Headroom Issues with Single Supply Biasing** -- Shows how duty cycle affects headroom:
- (A) 50% duty cycle: No clipping, symmetric swing about 2.5 V bias point
- (B) Low duty cycle: Positive clipping occurs
- (C) High duty cycle: Negative clipping occurs

In an amplifier circuit, the output bias point will be equal to the dc bias as applied to the op amp's (+) input. For a symmetric (50% duty cycle) waveform of a 2 Vp-p output level, the output signal will swing symmetrically about the bias point. However if the pulsed waveform is of a very high (or low) duty cycle, the ac averaging effect of C_IN and R4||R5 will shift the effective peak level either high or low, dependent upon the duty cycle. This phenomenon has the net effect of reducing the working headroom of the amplifier.

## REFERENCES

1. Hank Zumbahlen, Basic Linear Design, Analog Devices, 2006, ISBN: 0-915550-28-1. Also available as Linear Circuit Design Handbook, Elsevier-Newnes, 2008, ISBN-10: 0750687037, ISBN-13: 978-0750687034. Chapter 1.
2. Walter G. Jung, Op Amp Applications, Analog Devices, 2002, ISBN 0-916550-26-5, Also available as Op Amp Applications Handbook, Elsevier/Newnes, 2005, ISBN 0-7506-7844-5. Chapter 1.
