---
source: "ADI MT-101 -- Decoupling Techniques"
url: "https://www.analog.com/media/en/training-seminars/tutorials/MT-101.pdf"
format: "PDF 14pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 21076
---
# Decoupling Techniques

## WHAT IS PROPER DECOUPLING AND WHY IS IT NECESSARY?

Most ICs suffer performance degradation of some type if there is ripple and/or noise on the power supply pins. A digital IC will incur a reduction in its noise margin and a possible increase in clock jitter. For high performance digital ICs, such as microprocessors and FPGAs, the specified tolerance on the supply (+/-5%, for example) includes the sum of the dc error, ripple, and noise. The digital device will meet specifications if this voltage remains within the tolerance.

The traditional way to specify the sensitivity of an analog IC to power supply variations is the power supply rejection ratio (PSRR). For an amplifier, PSRR is the ratio of the change in output voltage to the change in power supply voltage, expressed as a ratio (PSRR) or in dB (PSR). PSRR can be referred to the output (RTO) or referred to the input (RTI). The RTI value is equal to the RTO value divided by the gain of the amplifier.

Figure 1 shows how the PSR of a typical high performance amplifier (AD8099) degrades with frequency at approximately 6 dB/octave (20 dB/decade). Curves are shown for both the positive and negative supply. Although 90 dB at dc, the PSR drops rapidly at higher frequencies where more and more unwanted energy on the power line will couple to the output directly. Therefore, it is necessary to keep this high frequency energy from entering the chip in the first place. This is generally done with a combination of electrolytic capacitors (for low frequency decoupling), ceramic capacitors (for high frequency decoupling), and possibly ferrite beads.

Power supply rejection of data converters and other analog and mixed-signal circuits may or may not be specified on the data sheet. However, it is very common to show recommended power supply decoupling circuits in the applications section of the data sheet for practically all linear and mixed-signal ICs. These recommendations should always be followed in order to ensure proper operation of the device.

Figure 1: Power Supply Rejection vs. Frequency for the AD8099 High Performance Op Amp

Low frequency noise requires larger electrolytic capacitors which act as charge reservoirs to transient currents. High frequency power supply noise is best reduced with low inductance surface mount ceramic capacitors connected directly to the power supply pins of the IC. All decoupling capacitors must connect directly to a low impedance ground plane in order to be effective. Short traces or vias are required for this connection to minimize additional series inductance.

Ferrite beads (nonconductive ceramics manufactured from the oxides of nickel, zinc, manganese, or other compounds) are also useful for decoupling in power supply filters. At low frequencies (<100 kHz), ferrites are inductive; thus they are useful in low-pass LC filters. Above 100 kHz, ferrites becomes resistive (high Q). Ferrite impedance is a function of material, operating frequency range, dc bias current, number of turns, size, shape, and temperature.

The ferrite beads may not always be necessary, but they will add extra high frequency noise isolation and decoupling, which is often desirable. Possible caveats here would be to verify that the beads never saturate, especially when op amps are driving high output currents. When a ferrite saturates it becomes nonlinear and loses its filtering properties.

Note that some ferrites, even before full saturation occurs, can be nonlinear. Therefore, if a power stage is required to operate with a low distortion output, the ferrite should be checked in a prototype if it is operating near this saturation region.

The key aspects of proper decoupling are summarized in Figure 2.

- A large electrolytic capacitor (typically 10 uF to 100 uF) no more than 2 in. away from the chip.
  - The purpose of this capacitor is to be a reservoir of charge to supply the instantaneous charge requirements of the circuits locally so the charge need not come through the inductance of the power trace.
- A smaller cap (typ. 0.01 uF to 0.1 uF) as physically close to the power pins of the chip as is possible.
  - The purpose of this capacitor is to short the high frequency noise away from the chip.
- All decoupling capacitors should connect to a large area low impedance ground plane through a via or short trace to minimize inductance.
- Optionally a small ferrite bead in series with the supply pin.
  - Localizes the noise in the system.
  - Keeps external high frequency noise from the IC.
  - Keeps internally generated noise from propagating to the rest of the system.

Figure 2: What Is Proper Decoupling?

## REAL CAPACITORS AND THEIR PARASITICS

Figure 3 shows a model of a non-ideal capacitor. The nominal capacitance, C, is shunted by a resistance, RP, which represents insulation resistance or leakage. A second resistance, RS (equivalent series resistance, or ESR), appears in series with the capacitor and represents the resistance of the capacitor leads and plates.

Figure 3: A Real Capacitor Equivalent Circuit Includes Parasitic Elements

Inductance, L (the equivalent series inductance, or ESL), models the inductance of the leads and plates. Finally, resistance RDA and capacitance CDA together form a simplified model of a phenomenon known as dielectric absorption, or DA. When a capacitor is used in a precision application, such as a sample-and-hold amplifier (SHA), DA can cause errors. In a decoupling application, however, the DA of a capacitor is generally not important.

Figure 4 shows the frequency response of various 100 uF capacitors. Theory tells us that the impedance of a capacitor will decrease monotonically as frequency is increased. In actual practice, the ESR causes the impedance plot to flatten out. As we continue up in frequency, the impedance will start to rise due to the ESL of the capacitor. The location and width of the "knee" will vary with capacitor construction, dielectric and value. This is why we often see larger value capacitors paralleled with smaller values. The smaller value capacitor will typically have lower ESL and continue to "look" like a capacitor higher in frequency. This extends the overall performance of the parallel combination over a wider frequency range.

Figure 4: Impedance of Various 100uF Capacitors

The self-resonant frequency of the capacitor is the frequency at which the reactance of the capacitor (1/wC), is equal to the reactance of the ESL (wESL). Solving this equality for the resonant frequency yields:

$$f_{RESONANCE} = \frac{1}{2\pi\sqrt{ESL \cdot C}}$$

All capacitors will display impedance curves which are similar in general shape to those shown. The exact plots will be different, but the general shape stays the same. The minimum impedance is determined by the ESR, and the high frequency region is determined by the ESL (which in turn is strongly affected by package style).

## TYPES OF DECOUPLING CAPACITORS

Figure 5 shows the various types of popular capacitors suitable for decoupling. The electrolytic family provides an excellent, cost effective low-frequency filter component because of the wide range of values, a high capacitance-to-volume ratio, and a broad range of working voltages. It includes general-purpose aluminum electrolytic switching types, available in working voltages from below 10 V up to about 500 V, and in size from 1 uF to several thousand uF (with proportional case sizes).

| Technology | Advantages | Disadvantages | Applications |
|---|---|---|---|
| Aluminum Electrolytic, Switching Type. Avoid general purpose types | High CV product/cost, Large energy storage, Best for 100V-400V | Temperature related wearout, High ESR/size, High ESR @ low temp | Consumer products, Large bulk storage |
| Solid Tantalum | High CV product/size, Stable @ cold temp, No wearout | Fire hazard with reverse voltage, Expensive, Only rated up to 50V | Popular in military, Concern for tantalum raw material supply |
| Aluminum-Polymer, Special-Polymer, Poscap, Os-Con | Low ESR, Z stable over temp, Relatively small case | Rapid degradation above 105C, Relatively high cost | Newest technology, CPU core regulators |
| Ceramic | Lowest ESR/ESL, High ripple current, X7R good over wide temp | CV product limited, Microphonics, C decreases with increasing voltage | Excellent for HF decoupling, Good to 1GHz |
| Film (Polyester, Teflon, Polypropylene, Polystyrene, etc.) | Hi Q in large sizes, No wearout, High voltage | CV product limited, Not popular in SMT, High cost | High voltage/current, AC, Audio |

Figure 5: Popular Capacitor Types

All electrolytic capacitors are polarized, and thus cannot withstand more than a volt or so of reverse bias without damage. They have relatively high leakage currents (this can be tens of uA) which is strongly dependent upon specific family design, electrical size, and voltage rating versus applied voltage. However, leakage current is not likely to be a major factor for basic decoupling applications.

"General purpose" aluminum electrolytic capacitors are not recommended for most decoupling applications. However, a subset of aluminum electrolytic capacitors is the "switching type," which is designed and specified for handling high pulse currents at frequencies up to several hundred kHz with low losses. This type of capacitor competes directly with the solid tantalum type in high frequency filtering applications and has the advantage of a much broader range of available values.

Solid tantalum electrolytic capacitors are generally limited to voltages of 50 V or less, with capacitance of 500 uF or less. For a given size, tantalums exhibit higher capacitance-to-volume ratios than do the aluminum switching electrolytics, and have both a higher frequency range and lower ESR. They are generally more expensive than aluminum electrolytics and must be carefully applied with respect to surge and ripple currents.

More recently, high performance aluminum electrolytic capacitors using organic or polymer electrolytes have appeared. These families of capacitors feature appreciably lower ESR and higher frequency range than do the other electrolytic types, with an additional feature of minimal low-temperature ESR degradation. They are designated by labels such as aluminum-polymer, special polymer, Poscap, and Os-Con.

Ceramic, or multilayer ceramic (MLCC), is often the capacitor material of choice above a few MHz, due to its compact size and low loss. However, the characteristics of ceramic dielectrics varies widely. Some types are better than others for power supply decoupling applications. Ceramic dielectric capacitors are available in values up to several uF in the high-K dielectric formulations of X7R, Z5U, and Y5V at voltage ratings up to 200 V. The X7R-type is preferred because it has less capacitance change as a function of dc bias voltage than the Z5U and Y5V types.

NP0 (also called COG) types use a lower dielectric constant formulation, and have nominally zero TC, plus a low voltage coefficient (unlike the less stable high-K types). The NP0 types are limited in available values to 0.1 uF or less, with 0.01 uF representing a more practical upper limit.

Multilayer ceramic (MLCC) surface mount capacitors are increasingly popular for bypassing and filtering at 10 MHz or more, because their very low inductance design allows near optimum RF bypassing. In smaller values, ceramic chip caps have an operating frequency range to 1 GHz. For these and other capacitors for high frequency applications, a useful value can be ensured by selecting a capacitor which has a self-resonant frequency above the highest frequency of interest.

In general, film type capacitors are not useful in power supply decoupling applications because they are generally wound, which increases their inductance. They are more often used in audio applications where a very low capacitance vs. voltage coefficient is required.

## LOCALIZED HIGH FREQUENCY DECOUPLING RECOMMENDATIONS

Figure 6 shows how the high frequency decoupling capacitor must be as close to the chip as possible. If it is not, the inductance of the connecting trace will have a negative impact on the effectiveness of the decoupling.

Figure 6: High Frequency Supply Filter(s) Require Decoupling via Short Low-Inductance Path (Ground Plane)

In the left figure, the connection to both the power pin and the ground are a short as possible, so this would be the most effective configuration. In the figure on the right, however, the extra inductance and resistance in the PCB trace will cause a decrease in the effectiveness of the decoupling scheme and may cause interference problems by increasing the enclosed loop.

## RESONANT CIRCUITS FORMED BY LC DECOUPLING NETWORKS

In many decoupling applications, an inductor or ferrite bead is placed in series with the decoupling capacitor as shown in Figure 7. The inductor, L, in series with the decoupling capacitor, C, forms a resonant, or "tuned," circuit, whose key feature is that it shows marked change in impedance at the resonant frequency. The resonant frequency is given by the equation:

$$f = \frac{1}{2\pi\sqrt{LC}}$$

Figure 7: Resonant Circuit Formed by Power Line Decoupling

The overall impedance of the decoupling network may exhibit peaking at the resonant frequency. Just how much peaking depends on the relative Q (quality factor) of the tuned circuit. The Q of a resonant circuit is a measure of its reactance to its resistance. The equation is given by:

$$Q = \frac{2\pi fL}{R}$$

Normal trace inductance and typical decoupling capacitances of 0.01 uF to 0.1 uF will resonate well above a few MHz. For example, 0.1 uF and 1 nH will resonate at 16 MHz.

However, a decoupling network composed of a 100 uF capacitor and a 1 uH inductor resonates at 16 kHz. Left unchecked, this can present a resonance problem if this frequency appears on the power line. The effect can be minimized by lowering the Q of the circuit. This is most easily done by inserting a small resistance (~10 ohm) in the power line close to the IC, as shown in the right case. The resistance should be kept as low as possible to minimize the IR drop across the resistor. An alternative to a resistor is a small ferrite bead which appears primarily resistive at the resonant frequency.

The use of a ferrite bead rather than an inductor minimizes resonance problems because the ferrite bead appears resistive above 100 kHz and will therefore lower the effective Q of the circuit. Typical ferrite bead impedances are shown in Figure 8.

Figure 8: Ferrite Bead Impedance Compared to a 1uH Inductor

The response of simple LRC decoupling networks can be easily simulated using a SPICE-based program such as National Instruments Multisim, Analog Devices' Edition. A typical model of the circuit is shown in Figure 9, and a simulated response in Figure 10.

Figure 9: LC Filter Attenuation Approximation

Figure 10: Simulated Gain of LC Network Using NI Multisim Analog Devices Edition

## EFFECTS OF POOR DECOUPLING TECHNIQUES ON PERFORMANCE

In this section we examine the effects of poor decoupling on two fundamental components: an op amp and an ADC.

Figure 11 shows the pulse response of AD8000, a 1.5 GHz high speed current feedback op amp. Both of the oscilloscope graphs were taken using the evaluation board. The left-hand trace shows the response with proper decoupling, and the right-hand trace shows the same response on the same board with the decoupling capacitors removed. The output load in both cases was 100 ohm.

Figure 11: Effects of Decoupling on Performance of the AD8000 Op Amp

Figure 12 shows the PSRR of the AD8000 as a function of frequency. Note that the PSRR falls to a relatively low value at the higher frequencies. This means that signals on the power line will propagate easily to the output. Figure 13 shows the circuit used to measure the PSRR of the AD8000.

Figure 12: AD8000 Power Supply Rejection Ratio (PSRR)

Figure 13: AD8000 Positive PSRR Test Set

We will now examine the effect of proper and improper decoupling on a high performance data converter, the AD9445 14-bit, 105/125MSPS ADC. While a converter will typically not have a PSRR specification, proper decoupling is still very important. Figure 14 shows the FFT output of a properly designed circuit. In this case, we are using the evaluation board for the AD9445. Note the clean spectrum.

Figure 14: FFT Plot for the AD9445 Evaluation Board with Proper Decoupling

The pinout of the AD9445 is shown in Figure 15. Note that there are multiple power and ground pins. This is done to lower the impedance of the power supply (pins in parallel).

There are 33 analog power pins. 18 pins are connected to AVDD1 (which is +3.3 V +/- 5%) and 15 pins are connected to AVDD2 (which is +5 V +/- 5%). There are four DVDD (which is +5 V +/- 5%) pins. On the evaluation board used in this experiment, each pin has a ceramic decoupling cap. In addition, there are several 10 uF electrolytic capacitors as well.

Figure 15: AD9445 Pinout Diagram

Figure 16 shows the spectrum with the decoupling caps removed from the analog supply. Note the increase in high frequency spurious signals, as well as some intermodulation products (lower frequency components).

The SNR of the signal has obviously decreased.

The only difference between this figure and the last is removal of the decoupling capacitors. Again we used the AD9445 evaluation board to make the measurements.

Figure 16: FFT Plot for an AD9445 Evaluation Board with Caps Removed from the Analog Supply

Figure 17 shows the result of removing the decoupling caps from the digital supply. Again note the increase in spurs. Also note the frequency distribution of the spurs. Not only do these spurs occur at high frequencies, but across the spectrum. This experiment was run with the LVDS version of the converter.

We can assume that the CMOS version would be worse because LVDS is less noisy than saturating CMOS logic.

Figure 17: SNR Plot for an AD9445 Evaluation Board with Caps Removed from the Digital Supply

## References

1. Henry W. Ott, *Noise Reduction Techniques in Electronic Systems, 2nd Edition*, John Wiley, Inc., 1988, ISBN: 0-471-85068-3.
2. Paul Brokaw, "An IC Amplifier User's Guide to Decoupling, Grounding and Making Things Go Right for a Change", Analog Devices, AN-202.
3. Paul Brokaw, "Analog Signal-Handling for High Speed and Accuracy," Analog Devices, AN-342.
4. Jerald Graeme and Bonnie Baker, "Design Equations Help Optimize Supply Bypassing for Op Amps," *Electronic Design, Special Analog Issue*, June 24, 1996, p.9.
5. Jerald Graeme and Bonnie Baker, "Fast Op Amps Demand More Than a Single-Capacitor Bypass," *Electronic Design, Special Analog Issue*, November 18, 1996, p.9.
6. Jeffrey S. Pattavina, "Bypassing PC Boards: Thumb Your Nose at Rules of Thumb," *EDN*, Oct. 22, 1998, p.149.
7. Howard W. Johnson and Martin Graham, *High-Speed Digital Design*, PTR Prentice Hall, 1993, ISBN-10: 0133957241, ISBN-13: 978-0133957242.
8. Ralph Morrison, *Solving Interference Problems in Electronics*, John Wiley, 1995, ISBN-10: 0471127965, ISBN-13: 978-0471127963.
9. C. D. Motchenbacher and J. A. Connelly, *Low Noise Electronic System Design*, John Wiley, 1993, ISBN-10: 0471577421, ISBN-13: 978-0471577423.
10. Mark Montrose, *EMC and the Printed Circuit Board*, Wiley-IEEE Press, 1999, ISBN-10: 078034703X, ISBN-13: 978-0780347038.
11. Bonnie Baker, *A Baker's Dozen: Real Analog Solutions for Digital Designers*, Elsevier/Newnes, 2005, ISBN-10: 0750678194, ISBN-13: 978-0750678193.
12. Jerald Graeme, *Optimizing Op Amp Performance*, McGraw Hill, 1996, ISBN-10: 0070245223, ISBN-13: 978-0070245228.
13. Tamara Schmitz and Mike Wong, Choosing and Using Bypass Capacitors (Part 1 of 3), *Planet Analog*, June 19, 2007.
14. Tamara Schmitz and Mike Wong, Choosing and Using Bypass Capacitors (Part 2 of 3), *Planet Analog*, June 21, 2007.
15. Tamara Schmitz and Mike Wong, Choosing and Using Bypass Capacitors (Part 3 of 3), *Planet Analog*, June 27, 2007.
16. Yun Chase, "Introduction to Choosing MLC Capacitors for Bypass/Decoupling Applications," AVX Corporation, Myrtle Beach, SC.
17. Panasonic SP-Capacitor Technical Guide, Panasonic, Inc.
18. National Instruments Multisim, Analog Devices' Edition.
19. Hank Zumbahlen, *Basic Linear Design*, Analog Devices, 2006, ISBN: 0-915550-28-1. Also available as *Linear Circuit Design Handbook*, Elsevier-Newnes, 2008, ISBN-10: 0750687037, ISBN-13: 978-0750687034. Chapter 12.
20. Walter G. Jung, *Op Amp Applications*, Analog Devices, 2002, ISBN 0-916550-26-5, Chapter 7. Also available as *Op Amp Applications Handbook*, Elsevier/Newnes, 2005, ISBN 0-7506-7844-5. Chapter 7.
21. Walt Kester, *High Speed System Applications*, Analog Devices, 2006, ISBN-10: 1-56619-909-3, ISBN-13: 978-1-56619-909-4, Part 4.
