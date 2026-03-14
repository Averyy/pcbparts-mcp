---
source: "NXP AN1706 -- Microcontroller Oscillator Circuit Design"
url: "https://www.nxp.com/docs/en/application-note/AN1706.pdf"
format: "PDF 12pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 22534
---
# Microcontroller Oscillator Circuit Design Considerations

By Cathy Cox and Clay Merritt, Freescale Semiconductor

## 1. Introduction

The heartbeat of every microcontroller design is the oscillator circuit. Most designs that demand precise timing over a wide temperature range use a crystal oscillator. PCB designers have the task of integrating crystal and microcontroller functions without the help of mating specifications. The objective of this document is to develop a systematic approach to good oscillator design and to point out some common pitfalls.

## 2. Crystal Oscillator Theory

The Pierce-type oscillator circuit is used on most microcontrollers. This circuit consists of two parts: an inverting amplifier that supplies a voltage gain and 180 degree phase shift and a frequency selective feedback path. The crystal combined with Cx and Cy form a tuned PI network that tends to stabilize the frequency and supply 180 degree phase shift feedback path. In steady state, this circuit has an overall loop gain equal to one and an overall phase shift that is an integer multiple of 360 degrees. Upon being energized, the loop gain must be greater than one while the voltage at XTAL grows over multiple cycles. The voltage increases until the NAND gate amplifier saturates. At first glance, the thought of using a digital NAND gate as an analog amplifier is not logical, but this is how an oscillator circuit functions. As can be expected, a significant amount of power is required to keep an amplifier in a linear mode.

A crystal is a small wafer of high grade quartz cut at a certain angle and to a certain size. Thinner cuts give higher frequency crystals, approximately 0.15 mm at 15 MHz. Crystals are designed and manufactured to operate at the rated frequency with a certain load capacitance (CL). Typical load capacitance values are 12 pF, 15 pF, 18 pF, 20 pF, 22 pF and 32 pF. Metal leads are plated to the crystal for electrical connections. As a voltage potential is placed across the crystal element, the force of trapped electrons in the crystalline structure tends to deform the element. This is referred to as the piezoelectric effect. As the element flexes, electrical impedance changes. The crystal acts as an electro-mechanical device and can be modeled as a network of passive electrical components with a very sharp cutoff frequency. The physical properties of quartz make it very stable over both time and temperature.

The usual model of a crystal is a network of two capacitors, an inductor and a resistor. The shunt capacitance (C0) is introduced by the metal plates used for electrical connections to the quartz wafer. Crystals are capable of oscillating at multiple frequencies. These frequencies are commonly referred to as overtones. For each overtone, a series RLC combination is added to the model. At the rated frequency of operation, the impedance of a crystal is inductive. The reactance of the crystal is capacitive up to a series resonant frequency (Fs) and beyond the anti-resonant frequency (Fa), the reactance is also capacitive. This means that the frequency of oscillation is bounded by Fs and Fa. The exact steady state frequency is determined by amplifier gain and load capacitance.

Load capacitors (Cx and Cy) are used to form a tuned LC tank circuit in resonance. The combined capacitive impedance of Cx, Cy and other stray capacitance equals the inductive reactance of the crystal. Frequency of operation can be estimated by:

    f = 1 / [2 * pi * sqrt(L1 * CL)]

In many cases, the voltage at EXTAL and XTAL actually swings outside the ground and supply rails. Changing capacitance values will slightly change the operating frequency and can significantly change the voltage at EXTAL and XTAL. It is important to size these elements correctly and to use quality capacitors with long life, very low ESR, and good stability over temperature.

Mathematically demonstrating how an oscillator circuit starts is very challenging due to non-linear characteristics of the system such as amplifier gain and crystal impedance. In general terms, an external element must effectively commence oscillation by placing a time variant voltage across the crystal. This can happen in a number of ways including injection of power supply noise and the processor negating the STOP signal, but normally this occurs when supply voltage is applied.

The feedback resistance, Rf, tends to keep the input to the NAND gate biased around supply voltage divided by two. Rf must be sized to allow adequate feedback while not unduly loading the circuit. The microcontroller manufacturer normally suggests a range of acceptable values, usually between 100 kOhm and 22 MOhm. For low frequency circuits, the crystal impedance is relatively high and the value for Rf must also be high (10 MOhm for 32 kHz). For higher frequencies, Rf must be lower (100 kOhm for 10-20 MHz).

The voltages at EXTAL and XTAL are usually distorted sine waves approximately 180 degrees out of phase. These sine waves swing symmetrically around the supply voltage/2. Distortion can be attributed to NAND gate amplifier saturation and to intrinsic diodes clipping the signal at EXTAL.

In order for the oscillator circuit to resonate in a stable manner, the absolute gain of the amplifier must be >= 1. This ideally should ensure that the output signal does not decay to zero. In its steady state condition the loop gain is equal to one.

Correct choice of Cx and Cy is paramount to oscillator start-up and steady state conditions. Imbalances in capacitive and inductive impedance can cause phase and amplitude problems in the feedback loop. Normally, Cx and Cy are equal, however, in some cases, if Cx is chosen to be slightly smaller than Cy, the voltage swing at EXTAL can be increased without compromising balance or introducing phase problems.

| Cx     | Cy     | V@EXTAL | Crystal Power Dissipation |
|--------|--------|---------|--------------------------|
| 56 pF  | 56 pF  | 3.3 Vpp | 100 uW                  |
| 33 pF  | 56 pF  | 8.0 Vpp | 199 uW                  |
| 47 pF  | 56 pF  | 6.1 Vpp | 207 uW                  |
| 68 pF  | 68 pF  | 2.8 Vpp | 102 uW                  |

Values shown are for a 4.9 MHz crystal, a typical M68HC11 drive circuit, and Vdd = 5V.

## 3. Amplifier Gain and Crystal Drive

The microcontroller's amplifier gain is a critical element in the start-up of an oscillator. It must be large enough to drive the stabilizing network but if it is too robust there could be deleterious effects; namely, excess power consumption, high RF emissions, and, worst of all, an amplifier that will not start. It is not an easy task to make an amplifier ideal for oscillator operation from 1-10 MHz while keeping the noise and power consumption to a minimum.

A fairly simple experiment can be run to determine actual gain. Pull the EXTAL pin from the circuit board and capacitively couple a 25-50 mV peak-to-peak sine wave at the rated frequency to EXTAL. With power supplied to the board and components inserted, measure the voltage level on the XTAL pin. Calculating the ratio Vout/Vin gives the loaded amplifier gain. This should give a close approximation of the actual small signal value required at start-up. If the loaded gain is under 1.5, it may be a good idea to investigate ways to reduce the amplifier's load by resizing the stabilizing capacitors or possibly choosing a different crystal.

Overdriving a crystal for an extended period of time can physically damage a crystal. Typical drive levels for crystals can vary from 1 uW (for small 32 kHz tuning fork crystals) to 5 mW (for a circular AT-cut type high frequency crystals). By calculating the RMS current flowing through the circuit and being given the maximum series resistance, the power can be calculated using the formula: P = I^2 * R.

### 3.1. Understanding Capacitive Coupling and Inductance of PCB Traces

As PCB and semiconductor geometries get progressively smaller, the understanding and control of capacitive coupling becomes paramount. Capacitance for two parallel plates can be calculated using:

    C (farads) = k * e0 * (A / d)

Where e0 = permitivity of free space = 8.85e-12 C^2/(N*m^2), A = plate area, d = distance between plates, k = dielectric constant of material.

**Example:** Consider a trace 1.0 cm long by 0.1 cm wide sitting directly above a solid ground plane. The board is a two-layer FR4 type with a distance between copper layers being 0.031 cm. The dielectric constant of fiberglass is approximately 3.5.

    C = 3.5 * 8.85e-12 * (0.01m * 0.001m) / 0.00031m = 1e-12 F or 1 pF

With surface-mount devices, the pad area for components can actually increase and for multilayer boards the distance (d) can be very small. These factors can increase the board's stray capacitance values into 5-10 pF range quite easily. For hybrid printed circuit boards, a very thin dielectric is screened between conducting layers. This can sometimes make the distance between layers 1-2 mils (2.5-5 um). The dielectric constant can be between 10-15, giving stray capacitance values between 15-50 pF for even nominal pad and trace sizes.

In regard to inductance, when current flows through any conductor there is some associated self inductance. The measured inductance is dependent on the current loop area. Having a large ground plane can usually guarantee the smallest loop area. Users of single layer boards and two layer boards without ground planes must take special precautions to keep the oscillator trace length as short as possible and with minimal loop area. Care should be taken to ensure the power source to the microcontroller is well decoupled.

## 4. Potential Problem Areas

Increasing the capacitance from either leg of the crystal to ground through stray effects of board layout is not detrimental so long as it is taken into account when selecting the stabilizing capacitors Cx and Cy. Making the traces for Cx and Cy exceedingly long can add unwanted inductance. Inductance is a function of total area enclosed by a current loop. Make certain that the power supply and return paths are as short as possible and, more importantly, that the loop area of this path is as small as possible. Cx, Cy, Rf and the crystal should be placed as close as possible to the microcontroller's oscillator pins.

The following problems have been witnessed by Freescale application engineers:

- **Long trace leads:** Long trace leads and uncontrolled capacitive coupling can cause problems. If inductance in the Cx or Cy paths is significant, the net impedance can be very small, effectively eliminating any feedback voltage. If there is any significant capacitance, the effective loading of the amplifier may be much more than calculated and the gain may not be sufficient. This is probably the number one problem encountered. Multilayer and hybrid PCBs can have substantial coupling to ground.

- **PCB contaminants:** PCB contaminants reducing impedance between nodes such as humidity, flux, and finger prints are problems. When printed circuit boards are manufactured, a flux is applied to the board to promote good solder bonds. Normally, a wash cycle is used to remove the flux. If the board is not cleaned entirely, the residual flux may supply an unwanted impedance path on the board. Take special care to check between the crystal leads and beneath SMT devices.

- **Power supply noise:** Power supply noise can sometimes be greatly amplified by the oscillator's amplifier. If the power supply noise is some harmonic of the crystal frequency, or vice versa, the oscillator may not begin to oscillate. In other cases, a noise element on the power supply actually helped the circuit begin oscillating by supplying a much needed high frequency component. Tying the stabilizing capacitors to +5V sometimes provides a better AC reference point than ground. A good test for this condition is to disable the board's power supply and use a high-quality bench supply to power the board.

- **No operation at high temperature:** The crystal may not start at high temperatures. Usually this is caused by undue loading of the amplifier. Check on-board contaminants and the proper sizing of the stabilizing capacitors.

- **Frequency instability:** Frequency instability is usually caused either by driving the crystal too hard or insufficiently due to incorrectly sized stabilizing capacitors. If prolonged, overdriving the crystal can cause permanent damage. The size of the stabilizing capacitors controls the voltage across the crystal.

- **High frequency issues (>10 MHz):** A CMOS amplifier tends to have a gain attenuation as frequency increases. Feeding auxiliary microprocessors or other digital circuits can add sufficient load to swamp the amplifier and prevent oscillation. Also note that as the frequency becomes very large, the impedance of a capacitor decreases which can make stray capacitance a much greater problem.

- **Low frequency issues (<50 kHz):** At low frequencies the capacitor and crystal impedances are very high and quite often the amplifier is too robust for safe operation. By placing a large resistance in series with the crystal, power dissipation can be reduced.

- **Evaluation board problems:** Introducing a cable to connect a development platform to a target system can greatly change circuit parameters. In most applications, it is better to use the oscillator circuit on the evaluation to eliminate the transmission line effects of a long cable leading to the target board.

- **High-power circuit interference:** Rapidly varying high current or high voltage lines in the vicinity of the crystal circuit can adversely impact the oscillator. If a product seems to be working correctly until a heavy load like a relay or motor is energized, coupling is probably occurring. Check that the decoupling capacitors of the microcontroller are not damaged and are of high quality. Take care to route all power traces as far away from the crystal circuit as can be allowed.

- **Crystal or Resonator Damage:** In rare cases, the hermetic seal on crystal leads can be fractured. This can allow moisture or other contaminants to infiltrate the case and cause sporadic operation. Care should be taken when handling crystals and when forming leads prior to insertion onto a PCB. In applications where the printed circuit board will be subjected to vibration, it is highly recommended that can-type crystals be adhered to the board.

## 5. Testing and Troubleshooting

The oscillator circuit is inherently a very high-impedance, closed-loop feedback system. When a standard oscilloscope probe is connected into the circuit, parameters and performance can change dramatically.

A probe for most scopes has 8-15 pF capacitance that can load the circuit down considerably at high frequencies. An active FET probe can be used to monitor the circuit without adversely affecting circuit parameters. These probes are quite expensive but have a very high input impedance. Typical FET probes have an input capacitance below 2 pF and input resistance above 5 MOhm.

| Frequency | Zin (8 pF) | Zin (15 pF) |
|-----------|------------|-------------|
| 500 kHz   | 39.8 kOhm | 21.2 kOhm  |
| 1 MHz     | 19.9 kOhm | 10.6 kOhm  |
| 4 MHz     | 4.97 kOhm | 2.65 kOhm  |
| 16 MHz    | 1.24 kOhm | 663 Ohm    |
| 50 MHz    | 398 Ohm   | 212 Ohm    |

Different conditions can greatly impact start-up and steady state performance. Here are a few tests that can be performed to measure the robustness of your design:

1. Vary the input voltage from 3 to 5.5 V. The circuit should start oscillating and the frequency should rise slightly as the voltage is increased. If it actually decreases as the voltage is increased, there is a good chance that the crystal is being dangerously overdriven. If no oscillation occurs, the feedback resistor may need to be made smaller.

2. Control the rise time of the power supply. An empirical formula for the frequency content of a rising edge is: fmax ~= 1 / (pi * risetime). Having a very fast-rising power supply might stimulate the crystal at the resonant frequency.

3. Placing a 1k potentiometer in series with the crystal can give some information about amplifier tolerance. With added resistance, the circuit will be less likely to start. Slowly increase the resistance from 0 Ohm. After each increment, remove power from the board and re-energize it. Note the value of the potentiometer when the circuit will not start. The resistance (crystal + potentiometer) should be substantially larger than the worst-case resistance specified by the crystal manufacturer. It is desirable to have the circuit oscillate with two times the maximum crystal resistance.

4. Test under cold, hot, and high humidity conditions. Resistance increases with temperature. Increasing source resistance reduces the effective loop gain. Any time the oscillator will not start or major frequency shifts occur, a problem exists.

5. Run worst-case loading conditions on the power portion of the board. Drive inductive loads such as relays, solenoids and motors under full load conditions.

6. Check board capacitance by measuring the exact frequency of the crystal with a tightly controlled load capacitance on a separate apparatus. Then, measure the frequency on the actual PCB. If the two do not correlate well, unknown stray capacitance may exist on the board and the stabilizing capacitors may need to be reduced.

## 6. Conclusions

This document has given a basic explanation of how and why a crystal oscillator circuit operates. Suggestions have been given on how to size circuit components, and how to test the circuit's robustness. Some of the design and implementation problems experienced by Freescale application engineers have been discussed in the hope of preventing similar problems from occurring in the future.

## Appendix A: Crystal Versus Resonator Issues

Resonators are a lower-cost, less exact alternative to crystals. Instead of a quartz crystal element, resonators make use of other piezoelectric crystalline structures such as barium titanate. This allows the element to be smaller, less expensive, and to have improved start-up times. The surrounding circuitry is identical to that of a crystal with a parallel resistor to help in the start-up phase and with stabilizing capacitors on both legs to ground.

For a given frequency, the required stabilizing capacitors are usually much larger for a resonator. This means that a slightly larger amplifier drive capability is needed which will tend to consume more power. Resonators in general are not offered below 125 kHz but are available up to 20 MHz.

| Characteristic  | Resonator             | Crystal             |
|----------------|-----------------------|---------------------|
| Cost           | Inexpensive           | High                |
| Freq Control   | +/- 0.5%              | +/- 0.002%          |
| Temp. Range    | -40 to 125 C          | -40 to 125 C        |
| Ease of Start  | Easy                  | Hard to analyze     |
| Package        | Both available in thru-hole and SMT        |

## Appendix B: AT-Strip Crystals

The "AT" in AT-cut and AT-strip crystals specifies the angle of cut relative to the Z-axis to be 35 degrees. AT-cut crystals are thin, circular disks of quartz while AT-strip crystals are thin, rectangular pieces of quartz (the width is very small compared to the length). AT-cut crystals will fit in smaller packages and require less quartz which should make them less expensive.

AT-strip crystals function identically to the AT-cut type and the same Pierce oscillator circuit configuration is used. However, the smaller piece of quartz is not as resistant to mechanical shock or to excess electrical drive. Care should be taken to calculate the drive level and ensure stabilizing capacitors are sized appropriately. In general, for any given frequency, the series resistance and the maximum drive of an AT-strip crystal will be lower than that of an AT-cut crystal. (i.e., 4 MHz AT-cut: max ESR = 120 Ohm, max drive = 5 mW; 4 MHz AT-strip: max ESR = 40 Ohm, max drive = 1 mW.)

## Appendix C: 32-kHz Operation Specifics

The basic theory behind the operation of a low-frequency crystal is identical to that listed in earlier sections. The big difference is that relative impedances are much higher for low-frequency operation. In many cases, a resistor needs to be inserted in series with the crystal to keep it from being overdriven. The correct placement of this resistor is very important. Do not place Rs on the amplifier's input side. Also, Rf should feed directly back from XTAL to EXTAL. Rs will range from 100 Ohm to 330 kOhm depending upon Vdd, the crystal frequency, and the amplifier's drive.

Phase-locked loops are control circuits that depend upon negative feedback for stability. This means that the output frequency will always contain small deviations from the desired frequency. In most Freescale microcontrollers using PLLs, separate power and ground pins are supplied for the PLL. These pins need a separate high-quality decoupling capacitor to eliminate any noise for this very sensitive circuit. Even more important is a pin labeled "XFC." This is for connection of a high-quality 0.1 uF capacitor to act as a filter in the PLL's feedback. If nothing is connected, or a capacitor with a high ESR is used, the PLL probably will not lock.

For microprocessors utilizing phase-locked loops (PLLs), a parameter called "jitter" needs to be specified. Jitter, or clock stability, is defined as the variance in maximum frequency over a specified time period. For a 16.7-MHz system, jitter can vary by up to 100 kHz for any given five microsecond window. However, over a longer window of time, say one millisecond, the average frequency can be controlled to +/- 0.05%.

## References

1. Burch, Ken, XTAL. 1992
2. KDS America, KDS Crystal Catalog. 1995
3. Van Doren, Dr. Tom, Grounding and Shielding Electronic Systems.
4. VX Kyocera, Timing Devices.
5. Sears, Francis, University Physics. 1982.
6. Landee, Robert, Electronics Designers' Handbook. McGraw-Hill, 1977
7. Frerking, Marvin, Crystal Oscillator Design and Temperature Compensation. Van Nostrand Reinhold, 1978.
8. Fox Electronics, Frequency Control Products. Volume 15 Number 1994.
