---
source: "Microchip AN682 -- Using Single Supply Op Amps in Embedded Systems"
url: "https://ww1.microchip.com/downloads/en/AppNotes/00682c.pdf"
format: "PDF 10pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 14665
---
# Using Single Supply Operational Amplifiers in Embedded Systems

*Author: Bonnie Baker, Microchip Technology Inc.*

## INTRODUCTION

Beyond the primitive transistor, the operational amplifier is the most basic building block for analog applications. Fundamental functions such as gain, load isolation, signal inversion, level shifting, adding and/or subtracting signals are easily implemented with this building block. More complex circuits can also be implemented, such as the instrumentation amplifier, a current to voltage converter, and filters, to name only a few. Regardless of the level of complexity of the operational amplifier circuit, knowing the fundamental operation and behavior of this building block will save a considerable amount of upfront design time.

Formal classes on this subject can be very comprehensive and useful. However, many times they fall short in terms of experience or common sense. For instance, a common mistake that is made when designing with operational amplifiers is to neglect to include the bypass capacitors in the circuit. Operational amplifier theory often overlooks this practical detail. If the bypass capacitor is missing, the amplifier circuit could oscillate at a frequency that "theoretically" doesn't make sense. If text book solutions are used, this is a difficult problem to solve.

This application note is divided into three sections. The first section will list fundamental amplifier applications with the design equations included. These amplifier circuits were selected with embedded system integration in mind. The second section will use these fundamental circuits to build useful amplifier functions in embedded control applications. The third section will identify the most common single supply operational amplifier (op amp) circuit design mistakes.

## FUNDAMENTAL OPERATIONAL AMPLIFIER CIRCUITS

The op amp is the analog building block that is analogous to the digital gate. By using the op amp in the design, circuits can be configured to modify the signal in the same fundamental way that the inverter, AND, and OR gates do in digital circuits. In this section, fundamental building blocks such as the voltage follower, non-inverting gain and inverting gain circuits will be discussed. This will be followed by a rail splitter, difference amplifier, summing amplifier and current to voltage converter.

### Voltage Follower Amplifier

Starting with the most basic op amp circuit, the buffer amplifier (Figure 1) is used to drive heavy loads, solve impedance matching problems, or isolate high power circuits from sensitive, precise circuitry.

**Figure 1: Buffer Amplifier (voltage follower)**
- V_OUT = V_IN
- Bypass capacitor: 1 uF

The buffer amplifier can be implemented with any single supply, unity gain stable amplifier. In this circuit as with all amplifier circuits, the op amp must be bypassed with a capacitor. For single supply amplifiers that operate in bandwidths from DC to megahertz, a 1 uF capacitor is usually appropriate. Sometimes a smaller bypass capacitor is required for amplifiers that have bandwidths up to the 10s of megahertz. In these cases a 0.1 uF capacitor would be appropriate. If the op amp does not have a bypass capacitor or the wrong value is selected, it may oscillate.

The analog gain of the circuit in Figure 1 is +1 V/V. Notice that this circuit has a positive overall gain but the feedback loop is tied from the output of the amplifier to the inverting input. An all too common error is to assume that an op amp circuit that has a positive gain requires positive feedback. If positive feedback is used, the amplifier will most likely drive to either rail at the output.

This amplifier circuit will give good linear performance across the bandwidth of the amplifier. The only restrictions on the signal will occur as a result of a violation of the input common-mode and output swing limits.

If this circuit is used to drive heavy loads, the amplifier that is actually selected must be specified to provide the required output currents. Another application where this circuit may be used is to drive capacitive loads. Not every amplifier is capable of driving capacitors without becoming unstable. If an amplifier can drive capacitive loads, the product data sheet will highlight this feature. However, if an amplifier can't drive capacitive loads, the product data sheets will not explicitly say.

Another use for the buffer amplifier is to solve impedance matching problems. The input impedance of the non-inverting input of an amplifier can be as high as 10^13 ohm for CMOS amplifiers. In addition, the output impedance of this amplifier configuration is usually less than 10 ohm.

Yet another use of this configuration is to separate a heat source from sensitive precision circuitry (Figure 2). An increase in current drive will cause self heating of the chip which will induce an offset change. An analog buffer can be used to perform the function of driving heavy loads while the front end circuitry can be used to make precision measurements.

### Gaining Analog Signals

**Non-Inverting Gain Circuit (Figure 3):**

V_OUT = (1 + R2/R1) * V_IN

The input signal is presented to the high impedance, non-inverting input of the op amp. Typical values for these resistors in single supply circuits are above 2 kohm for R2. The output swing of the amplifier is restricted as stated in the product data sheet. Most typically, the larger signal at the output of the amplifier causes more signal clipping errors than the smaller signal at the input. If undesirable clipping occurs at the output of the amplifier, the gain should be reduced.

**Inverting Gain Circuit (Figure 4):**

V_OUT = -(R2/R1) * V_IN + (1 + R2/R1) * V_BIAS

In single supply applications, this circuit can easily be misused. For example, let R2 equal 10 kohm, R1 equal 1 kohm, V_BIAS equal 0 V, and the voltage at the input resistor R1 equal to 100 mV. With this configuration, the output voltage would be -1 V. This would violate the output swing range of the operational amplifier. In reality, the output of the amplifier would go as near to ground as possible.

The inclusion of a DC voltage at V_BIAS in this circuit solves this problem. Typically, the average output voltage should be designed to be equal to VDD/2.

### Single Supply Circuits and Supply Splitters

As was shown in the inverting gain circuit, single supply circuits often need a level shift to keep the signal between negative (usually ground) and positive supply pins. This level shift can be designed with a single amplifier and a combination of resistors and capacitors (Figure 5).

**Figure 5: Supply Splitter**

V_OUT = V_DD * (R4 / (R3 + R4))

The circuit has an elaborate compensation scheme to allow for the heavy capacitive load, C1. The benefit of this big capacitor is that it presents a very low AC resistance to the reference pin of the A/D converter. In the AC domain, the capacitor serves as a charge reservoir that absorbs any momentary current surges which are characteristic of sampling A/D converter reference pins.

### The Difference Amplifier

The difference amplifier (Figure 6) combines the non-inverting amplifier and inverting amplifier circuits into a signal block that subtracts two signals.

V_OUT = (V1 - V2) * (R2/R1) + V_REF * (R2/R1)

This circuit configuration will reliably take the difference of two signals as long as the signal source impedances are low. If the signal source impedances are high with respect to R1, there will be a signal loss due to the voltage divider action. Additionally, errors can occur if the two signal source impedances are mismatched.

### Summing Amplifier

Summing amplifiers (Figure 7) are used when multiple signals need to be combined by addition or subtraction.

V_OUT = (V1 + V2 - V3 - V4) * (R2/R1)

Any number of inputs can be used on either the inverting or non-inverting input sides as long as there are an equal number of both with equivalent resistors.

### Current to Voltage Conversion

An operational amplifier can be used to easily convert the signal from a sensor that produces an output current, such as a photodetector, into a voltage. This is implemented with a single resistor and an optional capacitor in the feedback loop (Figure 8).

V_OUT = R2 * I_D1

Two circuits are shown. The top circuit is designed to provide precision sensing from the photodetector. In this circuit the voltage across the detector is nearly zero and equal to the offset voltage of the amplifier. With this configuration, current that appears across the resistor R2 is primarily a result of the light excitation on the photodetector.

The photosensing circuit on the bottom is designed for higher speed sensing. This is done by reverse biasing the photodetector, which reduces the parasitic capacitance of the diode. There is more leakage through the diode which causes a higher DC error.

## USING THE FUNDAMENTALS

### Instrumentation Amplifier

Instrumentation amplifiers are found in a large variety of applications from medical instrumentation to process control. A classic three op amp instrumentation amplifier is illustrated in Figure 9.

V_OUT = (V1 - V2) * (1 + 2*R2/R_G) * (R4/R3) + V_REF * (R4/R3)

With this circuit the two input signals are presented to the high impedance non-inverting inputs of the amplifiers. This is a distinct advantage over the difference amplifier configuration when source impedances are high or mismatched.

A second instrumentation amplifier is shown in Figure 10, using two amplifiers:

V_OUT = (V1 - V2) * (1 + R1/R2 + 2*R1/R_G) + V_REF

### Floating Current Source

A floating current source (Figure 11) can come in handy when driving a variable resistance, like an RTD. This particular configuration produces an appropriate 1 mA source for an RTD type sensor.

I_OUT = V_REF / R_L

### Filters

**Low Pass Filter (Figure 12):** A 2-pole, 10 kHz Sallen-Key filter with Butterworth response. The gain is:

V_OUT/V_IN = 1 + R4/R3

This type of filter is also referred to as an anti-aliasing filter, which is used to eliminate circuit noise in the frequency band above half of Nyquist of the sampling system.

**Bandpass Filter (Figure 13):** Configured with a zero and two poles to accommodate speech applications. The signal gain is:

V_OUT = V_IN * (R3/R4) * (R2/(R1 + R2))

### Putting it Together

The circuit shown in Figure 14 utilizes four operational amplifiers along with a 12-bit A/D converter to implement a complete single supply temperature measurement circuit. The temperature sensor is an RTD which requires current excitation. The current excitation is supplied by the floating current source circuit. The gain and anti-aliasing filter is implemented with the bandpass filter circuit.

The voltage signal from the RTD is sensed by an amplifier that is used in a combination of a non-inverting configuration and inverting configuration. The output is then sent to an amplifier configured as a two pole, low pass filter in a gain of +6 V/V. The A/D converter is a 12-bit Successive Approximation Register (SAR) converter interfaced to a PIC12C509 microcontroller.

## AMPLIFIER DESIGN PITFALLS

### In General

1. Be careful of the supply pins. Don't make them too high per the amplifier specification sheet and don't make them too low.
2. Make sure the negative supply (usually ground) is in fact tied to a low impedance potential. Place a volt meter across the negative and positive supply pins to verify the right relationship.
3. Ground can't be trusted, especially in digital circuits. Plan your grounding scheme carefully. It is very difficult, if not impossible, to remove digital switching noise from an analog signal.
4. Decouple the amplifier power supplies with bypass capacitors as close to the amplifier as possible. For CMOS amplifiers, a 0.1 uF capacitor is usually recommended. Also decouple the power supply with a 10 uF capacitor.
5. Use short lead lengths to the inputs of the amplifier. If you have a tendency to use white perf boards for prototyping, be aware that they can cause noise and oscillation.
6. Amplifiers are static sensitive! If they are damaged, they may fail immediately or exhibit a soft error that will get worse over time.

### Input Stage Problems

1. Know what input range is required from your amplifier. If either input goes beyond the specified input range, the output will typically be driven to one of the power supply rails.
2. If you have a high gain circuit, be aware of the offset voltage of the amplifier. That offset is gained with the rest of your signal and it might dominate the results at the output.
3. Don't use rail-to-rail input stage amplifiers unless it is necessary. They are only needed when a buffer amplifier circuit is used or possibly an instrumentation amplifier configuration. Any circuit with gain will drive the output of the amplifier into the rail before the input has a problem.

### Do You Have the Bandwidth?

1. Account for the bandwidth of the amplifier when sending signals through the circuit. You may have designed an amplifier for a gain of 10 and find that the AC output signal is much lower than expected. If this is the case, you may have to look for an amplifier with a wider bandwidth.
2. Instability problems can usually be solved by adding a capacitor in parallel with the feedback resistor around the amplifier.

### Single Supply Rail-to-Rail

1. Operational Amplifier output drivers are capable of driving a limited amount of current to the load.
2. Capacitive loading an amplifier is risky business. Make sure the amplifier is specified to handle any loads that you may have.
3. It is very rare that a single supply amplifier will truly swing rail-to-rail. In reality, the output of most of these amplifiers can only come within 50 to 200 mV from each rail. Check the product data sheets.

## REFERENCES

- Sergio Franco, "Design with Operational Amplifiers and Analog Integrated Circuits", McGraw Hill
- Frederiksen, Thomas, "Intuitive Operational Amplifiers", McGraw Hill
- Williams, Jim, "Analog Circuit Design", Butterworth-Heinemann
- Baker, Bonnie, "Anti-aliasing Analog Filters for Data Acquisition Systems", AN699, Microchip Technology Inc.
- Baker, Bonnie, "Operational Amplifier Topologies and DC Specifications", AN722, Microchip Technology Inc.
- Baker, Bonnie, "Operational Amplifier AC Specifications and Applications", AN723, Microchip Technology Inc.
