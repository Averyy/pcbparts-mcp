---
source: "TI SBOA067 -- Op Amps and Comparators: Don't Confuse Them"
url: "https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/14/op-amp-vs-comparators.pdf"
format: "PDF 13pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 15472
---
# Op Amp and Comparators -- Don't Confuse Them!

*Bruce Carter, High Performance Linear*

## ABSTRACT

Operational amplifiers (op amps) and comparators look similar; they even have very similar schematic symbols. This leads a lot of designers to think they are interchangeable. There is a strong temptation to use a spare section of a multiple op amp package as a comparator to save money. This application note will explain why designers should not do this.

## 1 Introduction

The author, as an applications engineer, helps with tough customer inquiries -- the ones the marketing group cannot answer. Increasingly, a new type of inquiry has been heard: how to use an op-amp open loop as a comparator.

## 2 Comparing the Op Amp and the Comparator

The schematic symbol for the two types of parts gives no clue about internal differences. Other than some pin number differences, both have two power supply pins, both have noninverting (+) and inverting (-) inputs, and both have an output. Both can be drawn with the relative position of the two inputs swapped. Are they the same things? Unfortunately, even the internal schematics of the parts give no indication of what is going on.

The input stages look identical, except the inputs are labeled opposite. This will be discussed later. The output stage of the op amp is a bit more complex, which should be a clue that something is different. The output stage of the comparator is obviously different, in that it is a single-open collector. But be careful, many newer comparators have bipolar stages that are very similar in appearance to op-amp output stages.

So, if very little appears to be different in the schematic symbol or the internal workings, what is the difference?

**The difference is in the output stage. An op amp has an output stage that is optimized for linear operation, while the output stage of a comparator is optimized for saturated operation.**

## 3 The Comparator

A comparator is a 1-bit analog-to-digital converter. It has a differential analog input and a digital output. Very few designers make the mistake of using a comparator as an op amp, because most comparators have an open collector output. The output transistor of open collector comparators is characterized by low V_CE for switching heavy loads. The open collector structure depends on external circuitry to make the connection to power and complete the circuit. Some comparators also bring out the emitter pin as well, relying on the designer to complete the circuit by making both collector and emitter connections. Other comparators substitute a FET, having open drain outputs instead of open collector. In all of these classes of devices, the emphasis is on driving heavy loads.

### 3.1 The Comparator Output -- Designed for Digital Operation

Originally it was thought that comparators would drive relays. Later, in the application of these devices, it was discovered that the open collector/drain output was useful for creating a hard-wired NAND gate. Individual outputs of separate ICs, even widely separated on a PC board, can be directly hooked together to form a large NAND gate (see Figure 4).

In normal operation, the output transistors of each individual IC are turned off, creating high impedance. The single pullup resistor for all of the collectors (usually a few hundred to a few thousand ohms) acts as the high leg of a voltage divider, and the single output is therefore pulled high to the power supply. If any individual output transistor is turned on, it then creates low impedance, and the single output will go low. When this technique is used, it is not possible to determine the exact output that went low. This technique is employed when it does not matter which output goes low, only that one of them went low corresponding to a fault condition of some sort.

This open collector strategy, employed for many years in digital logic, is a technique that has all but been abandoned by digital designers. Comparator outputs are one of the last remaining strongholds of this design technique. It has fallen out of favor because it is prone to parasitic capacitance, and therefore it can be slow. Digital logic designers have long favored totem pole outputs, where internal transistors actively pull the output both high and low. While faster, totem pole outputs cannot be connected together in parallel. Therefore, they have not been favored on comparators. The effects of pullup resistors on speed and capacitance are not well understood, and as comparator speeds have become faster, more comparators have featured totem pole outputs. Make no mistake; comparators that have totem pole outputs are still optimized for saturated operation and speed.

### 3.2 The Comparator -- an Open-Loop Device

When applying a comparator, the designer compares the voltage level at two inputs. The comparator produces a digital output that corresponds to the inputs:

- If the voltage on the noninverting (+) input is greater than the voltage on the inverting (-) input, the output of the comparator goes to low impedance on for open collector/drain outputs, and high for totem pole outputs.
- If the voltage on the noninverting (+) input is less than the voltage on the inverting (-) input, the output of the comparator goes to high impedance off for open collector/drain outputs, and low for totem pole outputs.

No other mode of operation is recommended or implied by comparator data sheets. A comparator is usually used to compare a fixed-reference voltage to a varying voltage. In this application, a comparator can be used in an inverting and a noninverting mode (see Figure 5).

The battery symbol is usually a voltage divider off the power supply. There is no reason why it cannot vary.

The inverting and noninverting stages are often combined into a **window comparator** stage, which only has a high output when the voltage is between the low and high limits. The high and low limits are usually produced in a 3-resistor voltage divider (see Figure 6).

A **sine wave to square wave conversion** can be performed by presenting a severely low-passed version of the sine wave to the reference input (see Figure 7). Two supplies must be used, and the input must be ac-coupled, otherwise the circuit will not produce a square wave during the time spent charging the large capacitor to the average dc value of the input. This circuit is almost independent of the amplitude of the sine wave, although very low amplitude sine waves will not produce exactly 50% duty cycle square waves.

Notice that in the cases above the comparator has no feedback loop. The designer should note that a comparator has inputs that are labeled backwards from an op amp. An op amp should not be operated with the output shorted to the noninverting input (positive feedback). The comparator equivalent is to have the output shorted to the inverting input.

**Comparators with hysteresis:** Comparators can be operated in a closed-loop configuration with negative feedback. If the output is fed back to a comparator noninverting input, the resulting circuit is stable and operates with hysteresis (see Figure 8).

The hysteresis voltage is created by R_P and R_H, which create voltage dividers to ground or to the positive voltage rail V_CC. Therefore, the hysteresis voltage is:

V_H = (R_P / (R_H + R_P))

The hysteresis technique is useful to stop chattering on comparator outputs when the input varies slowly. The magnitude of hysteresis is intended to be 1% to 2%. Larger values are neither necessary nor useful.

## 4 The Op Amp

An op amp is an analog component with a differential analog input and an analog output. If an op amp is operated open loop, the output seems to act like a comparator output -- the inverting and noninverting comparator schematics above work (with the input polarity signs swapped).

### 4.1 The Op Amp Output -- Designed for Linear Operation

Figure 9 shows the Bode plot for a typical op amp. A Bode plot is useful for showing the response of op amps and filters, because it gives the output amplitude vs the frequency. When an op amp is operated as a comparator, it is operated as an open-loop device. The open-loop gain of this particular op amp to a dc step is over 50 dB. This is a voltage gain on the order of 500:1. For some op amps, the open-loop voltage gain at dc is 80 dB or more, or 10000:1. Therefore, even a very slight change in input voltage produces a tremendous change in output voltage. The op-amp output cannot swing infinitely; the voltage available from the power supply, minus the voltage rails, limits it. The output attempts to swing to a value that makes the two inputs equal, but it can never reach such a value. It hits a voltage rail, and stays there.

**An op amp, being intended for closed-loop operation, is optimized for closed-loop applications. The results when an op amp is used open loop are unpredictable.** No semiconductor manufacturer, including Texas Instruments, can or will assure the operation of an op amp used in an open-loop application. The analog output transistors used in op amps are designed for the output of analog waveforms, and therefore have large linear regions. The transistors will spend an inordinate amount of time in the linear region before saturation, making the rise and fall times lengthy.

In some cases, the designer may effectively use an op amp as a comparator. One customer indicated that they had been doing this for years with an LM324, a very common, mature technology part. When an LM324 is operated in this fashion, it hits a rail and stays there, but nothing bad happens. However, the situation can change dramatically when another device is substituted. This particular customer had a problem with power consumption, which increased when a different device was used in the circuit. It turns out that he had used a rail-to-rail device, which was consuming a lot of power while attempting to drive the output to the rail.

The case above is not meant as an endorsement of the LM324 (or any other basic op amp) as a comparator. The author has personally had to trash more than one consumer product that attempted this because an LM324 did not switch properly. Telephone answering machines and cassette tape deck servomechanisms are notorious for this misapplication.

The design of an op-amp output stage is bad news for the designer who needs a comparator with fast response time. The transistors used for op-amp output stages are not switching transistors. They are linear devices, designed to output accurate representation of analog waveforms. When saturated, they may not only consume more power than expected, but they may also latch up. Recovery time may be very unpredictable. One batch of devices may recover in microseconds, another batch in 10's of milliseconds. Recovery time is not specified, because it cannot be tested. Depending on the device, it may not recover at all. Runaway destruction of the output transistors is a distinct possibility in some rail-to-rail devices.

### 4.2 Saturated Op Amp Operation Is Not Always Obvious

Even the best designer might produce a saturated or even open-loop op amp circuit without realizing it.

#### 4.2.1 Common Mistake Number 1 -- Improper Termination of Unused Sections

One of the easiest ways to unintentionally misapply an op amp is to misapply unused sections of a multiple section IC. Figure 10 shows the most common ways designers connect unused sections:

- **Brain-dead:** Leaving unused inputs unconnected. This is the worst thing that can be done. An open-loop op amp saturates to one voltage rail or the other. Because the inputs are floating, and picking up noise, the output switches from rail-to-rail, sometimes at unpredictable high frequencies.
- **Never:** Both inputs tied together. Usually, one op amp input is slightly higher than the other due to ground plane gradients, and the best possible scenario is that the op amp saturates at one rail or the other.
- **No:** Output tied to inverting input, non-inverting to ground. All the designer has accomplished is to ensure that the op amp hits a rail, and stays there. This can cause self-heating and increased power consumption.
- **Just-as-bad:** Output tied to inverting input, non-inverting floating. Designers who are designing a board for in-circuit test commonly do this. It still makes the op amp hit a rail.
- **Good:** The noninverting input is tied to a potential between the positive and negative rail, or to ground in a split supply system. The op-amp output is also at virtual ground.
- **Smart:** The smart designer anticipates the possibility of system changes in the future, and lays out the board so that the unused op amp section could be used by changing resistors and jumpering.

#### 4.2.2 Common Mistake Number 2 -- DC Gain

Another way designers create problems is when they forget about dc components on ac signals. When an ac signal source has a dc offset, a coupling capacitor isolates the potential. The dc component is rejected, and the output voltage is as expected. If the coupling capacitor is omitted, the circuit attempts a gain on both the ac and dc components, which would exceed the power supply limits, saturating the output.

#### 4.2.3 Common Mistake Number 3 -- Current Source

One common mistake is the misapplication of op-amp current sources. The op-amp current source circuit must contain the load. Many applications put the load at the end of a cable, and the cable is on a connector. When the cable is unplugged, the op amp has positive feedback and hits the negative voltage rail.

The output of the current source is:

I_OUT = (R3 * V_IN) / (R1 * R5)

Where R3 = R4 + R5, R1 = R2, and R1 through R4 are >> R5, and R5 >> R_LOAD.

## 5 Combination Parts -- the Best of Both Worlds

It is easy to understand the motivation for misapplying op amps as comparators. Designers, who have a product full of op amps in quad packages, quite often end up with one or more spare sections. The temptation is overwhelming to use them as low-cost comparators to save money and board space.

Texas Instruments, recognizing this design need, has an alternative for designers. Low-cost op amps and comparators have been packaged together in a single IC:

| Part | Description |
|------|-------------|
| TLV2302 | Op Amp (1) + Open Collector Comparator (1) Combo IC |
| TLV2304 | Op Amp (2) + Open Collector Comparator (2) Combo IC |
| TLV2702 | Op Amp (1) + Push-Pull Comparator (1) Combo IC |
| TLV2704 | Op Amp (2) + Push-Pull Comparator (2) Combo IC |

Application of these parts is broad. A designer, for example, can use the op amp sections to level shift and apply gain to dc levels, to prepare them for the comparator.

## 6 Conclusions

Comparators and op amps, although similar, are very different components. It is unlikely that a comparator will be used as an op amp. However, Texas Instruments applications have received a number of inquiries about using op amps as comparators in an open loop. The best advice Texas Instruments can give is to not do this. The very best a designer can expect is very poor performance; the worst is a circuit that does not work or even burns out.
