---
source: "ADI -- Staying Well Grounded (Hank Zumbahlen, Analog Dialogue)"
url: "https://www.analog.com/en/resources/analog-dialogue/articles/staying-well-grounded.html"
format: "HTML"
method: "readability"
extracted: 2026-03-02
chars: 32627
---

Grounding is undoubtedly one of the most difficult subjects in system design. While the basic concepts are relatively simple, implementation is very involved. Unfortunately, there is no “cookbook” approach that will guarantee good results, and there are a few things that, if not done well, will probably cause headaches.

For linear systems, the ground is the reference against which we base our signal. Unfortunately, it has also become the return path for the power-supply current in unipolar supply systems. Improper application of grounding strategies can cripple performance in high-accuracy linear systems.

Grounding is an issue for all analog designs, and it is a fact that proper implementation is no less essential in PCB-based circuits. Fortunately, certain principles of quality grounding, especially the use of ground planes, are intrinsic to the PCB environment. Since this factor is one of the more significant advantages to PCB-based analog designs, appreciable discussion here is focused on it.

Some other aspects of grounding that must be managed include the control of spurious ground and signal return voltages that can degrade performance. These voltages can be due to external signal coupling, common currents, or, simply, excessive IR drops in ground conductors. Proper conductor routing and sizing, as well as differential signal handling and ground isolation techniques, enable control of such parasitic voltages.

An important topic to be discussed is grounding techniques appropriate for a mixed-signal, analog/digital environment. Indeed, the single issue of quality grounding can—and must— influence the entire layout philosophy of a high-performance mixed-signal PCB design.

Today’s signal processing systems generally require mixed-signal devices, such as analog-to-digital converters (ADCs) and digital-to-analog converters (DACs), as well as fast digital signal processors (DSPs). Requirements for processing analog signals that have a wide dynamic range impose the need to use high-performance ADCs and DACs. Maintaining a wide dynamic range with low noise in a hostile digital environment is dependent upon using good high-speed circuit design techniques, including proper signal routing, decoupling, and grounding.

In the past, “high-precision, low-speed” circuits have generally been viewed differently than so-called “high-speed” circuits. With respect to ADCs and DACs, the sampling (or update) frequency has generally been used as the distinguishing speed criterion. However, the following two examples show that, in practice, most of today’s signal processing ICs are really “high-speed,” and must, therefore, be treated as such in order to maintain high performance. While certainly true of DSPs, it is also true for ADCs and DACs.

All sampling ADCs (those employing an internal sample-and-hold circuit) suitable for signal processing applications operate with relatively high-speed clocks with fast rise and fall times (generally a few nanoseconds), so they must be treated as high-speed devices, even though throughput rates may appear low. For example, a medium-speed 12-bit successive-approximation (SAR) ADC may operate from a 10-MHz internal clock, while the sampling rate is only 500 kSPS.

Sigma-delta (Σ-Δ) ADCs also require high-speed clocks because of their high oversampling ratios. Even high resolution, so-called “low frequency” industrial measurement ADCs (such as the AD77xx-series), with throughputs of 10 Hz to 7.5 kHz, operate on 5-MHz or higher-frequency clocks and offer resolutions to 24 bits.

To further complicate the issue, mixed-signal ICs have both analog and digital ports, adding to the confusion with respect to proper grounding techniques. In addition, some mixed-signal ICs have relatively low digital currents, while others have high digital currents. In many cases, these two types require different treatment for optimum grounding.

Digital and analog design engineers tend to view mixed-signal devices from different perspectives, so the purpose of this article is to describe a general grounding philosophy that will work for most mixed-signal devices, without the need to know the specific details of their internal circuits.

From the above, it should be clear that the issue of grounding cannot be handled in a “cookbook” approach. Unfortunately, we cannot provide a list of things to do that will guarantee success. We can say that not doing certain things will probably lead to difficulties. And what works in one frequency range may not necessarily work in another frequency range. And, often, there are competing requirements. The key to handling grounding is to understand how the currents flow.

### Star Ground

The “star” ground philosophy builds on the theory that all voltages in a circuit are referred to a single ground point, known as the *star ground* point. This can be better understood by a visual analogy—the multiple conductors extending radially from the common schematic ground to resemble a star. The star point need not look like a star—it may be a point on a ground plane—but the key feature of the star ground system is that all voltages are measured with respect to a particular point in the ground network, not just to an undefined “ground” (wherever one can clip a probe).

The star grounding philosophy, while reasonable theoretically, is difficult to implement in practice. For example, if we design a star ground system, drawing out all signal paths to minimize signal interaction and the effects of high impedance signal or ground paths, implementation problems arise. When the power supplies are added to the circuit diagram, they either add unwanted ground paths, or their supply currents flowing in the existing ground paths are large enough, or noisy enough (or both), to corrupt the signal transmission. This particular problem can often be avoided by having separate power supplies (and, thus, separate ground returns) for the various portions of the circuit. For example, separate analog and digital supplies with separate analog and digital grounds, joined at the star point, are common in mixed-signal applications.

### Separate Analog and Digital Grounds

It is a fact of life that digital circuitry is noisy. Saturating logic, such as TTL and CMOS, draws large, fast current spikes from its supply during switching. Logic stages, with hundreds of millivolts (or more) of noise immunity, usually have little need for high levels of supply decoupling. On the other hand, analog circuitry is quite vulnerable to noise—on both power supply rails and grounds—so it is sensible to separate analog and digital circuitry to prevent digital noise from corrupting analog performance. Such separation involves separation of both ground returns *and* power rails—which can be inconvenient in a mixed-signal system.

Nevertheless, if a high-accuracy mixed-signal system is to deliver full performance, it is essential to have separate analog and digital grounds and separate power supplies. The fact that some analog circuitry will “operate” (function) from a single +5-V supply does not mean that it may optimally be operated from the same noisy +5-V supply as the microprocessor, dynamic RAM, electric fan, and other high-current devices! The analog portion must *operate at full performance from such a supply*, not just be functional. By necessity, this distinction will require very careful attention to both the supply rails and the ground interfacing.

Note that the analog and digital grounds in a system must be joined at some point to allow signals to be referred to a common potential. This *star point*, or analog/digital common point, is carefully chosen so as not to introduce digital currents into the ground of the analog part of the system—it is often convenient to make the connection at the power supplies.

Many ADCs and DACs have separate *analog ground* (AGND) and *digital ground* (DGND) pins. On the device data sheets, users are often advised to connect these pins together at the package. This seems to conflict with the advice to connect analog and digital ground at the power supplies, and, in systems with more than one converter, with the advice to join the analog and digital ground at a single point.

There is, in fact, no conflict. The labels, “analog ground” and “digital ground,” on these pins refer to the internal parts of the converter to which the pins are connected and not to the system grounds to which they must go. For an ADC, these two pins should generally be joined together and to the *analog* ground of the system. It is not possible to join the two pins within the IC package because the analog part of the converter cannot tolerate the voltage drop resulting from the digital current flowing in the bond wire to the chip. But they can be tied together *externally*.

Figure 1 illustrates this concept of ground connections for an ADC. If these pins are connected in this way, the digital noise immunity of the converter is diminished, somewhat, by the amount of common-mode noise between the digital and analog system grounds. However, since digital noise immunity is often of the order of hundreds or thousands of millivolts, this factor is unlikely to be important.

The analog noise immunity is diminished only by the external digital currents of the converter itself flowing in the analog ground. These currents should be kept quite small, and they can be minimized by ensuring that the converter outputs don’t see heavy loads. A good way to do this is to use a low input current buffer at the ADC output, such as a CMOS buffer-register IC.

Figure 1. Analog (AGND) and digital ground (DGND) pins of a data converter should be returned to system analog ground.

If the logic supply to the converter is isolated with a small resistance, and decoupled to analog ground with a local 0.1-μF (100-nF) capacitor, all the fast-edge digital currents of the converter will return to ground through the capacitor and will not appear in the external ground circuit. If a low-impedance analog ground is maintained—as it should be for adequate analog performance— additional noise due to the external digital ground current should rarely present a problem.

### Ground Planes

Related to the star ground system discussed earlier is the use of a *ground plane*. To implement a ground plane, one side of a double-sided PCB (or one layer of a multilayer one) is made of continuous copper and used as ground. The theory behind this is that the large amount of metal will have as low a resistance as is possible. Because of the large flattened conductor pattern, it will also have as low an inductance as possible. It then offers the best possible conduction, in terms of minimizing spurious ground difference voltages, across the conducting plane.

Note that the ground plane concept can also be extended to include *voltage planes*. A voltage plane offers advantages similar to a ground plane— a very low impedance conductor—but is dedicated to one (or more) of the system supply voltages. A system can thus have more than one voltage plane, as well as a ground plane.

While ground planes solve many ground impedance problems, they aren’t a panacea. Even a continuous sheet of copper foil has residual resistance and inductance; in some circumstances, these can be enough to prevent proper circuit function. Designers should be wary of injecting very high currents in a ground plane because they can produce voltage drops that interfere with sensitive circuitry.

Maintaining a low impedance, large area ground plane is of critical importance to all analog circuits today. The ground plane not only acts as a low impedance return path for decoupling high-frequency currents (caused by fast digital logic) but also minimizes EMI/RFI emissions. Because of the shielding action of the ground plane, the circuit’s susceptibility to external EMI/RFI is also reduced.

Ground planes also allow the transmission of high-speed digital or analog signals using transmission line techniques (microstrip or stripline), where controlled impedances are required.

The use of “bus wire” is totally unacceptable as a “ground” because of its impedance at the equivalent frequency of most logic transitions. For instance, #22 gauge wire has about 20 nH/in inductance. A transient current having a slew-rate of 10 mA/ns created by a logic signal would develop an unwanted voltage drop of 200 mV when flowing through one inch of this wire:

|  |  |  |
| --- | --- | --- |
|  |  | (1) |

For a signal having a 2-V peak-to-peak range, this translates into an error of about 200 mV, or 10% (approximately “3.5-bit accuracy”). Even in all-digital circuits, this error would result in considerable degradation of the logic noise-margins.

Figure 2 shows a situation where the digital return current modulates the analog return current (top figure). The ground return wire inductance and resistance is shared between the analog and digital circuits; this causes the interaction and resulting error. A possible solution is to make the digital return current path directly to the GND REF, as shown in the bottom figure. This illustrates the fundamental concept of a “star,” or single-point ground system. Implementing the true single-point ground in a system that contains multiple high-frequency return paths is difficult. The physical length of the individual return current wires will introduce parasitic resistance and inductance, making it difficult to obtain a low-impedance ground at high frequencies. In practice, the current returns must consist of large area ground planes to obtain low impedance to high-frequency currents. Without a low-impedance ground plane, it is almost impossible to avoid these shared impedances, especially at high frequencies.

All integrated circuit ground pins should be soldered directly to the low-impedance ground plane to minimize series inductance and resistance. The use of traditional IC sockets is not recommended with high-speed devices. The extra inductance and capacitance of even “low profile” sockets may corrupt the device performance by introducing unwanted shared paths. If sockets must be used with DIP packages, as in prototyping, individual “pin sockets” or “cage jacks” may be acceptable. Both capped and uncapped versions of these pin sockets are available. They have spring-loaded gold contacts, which make good electrical and mechanical connection to the IC pins. However, multiple insertions may degrade their performance.

Figure 2. Digital currents flowing in analog return path create error voltages.

Power supply pins should be decoupled directly to the ground plane using low-inductance, ceramic surface-mount capacitors. If through-hole mounted ceramic capacitors must be used, their lead length should be less than 1 mm. The ceramic capacitors should be as close as possible to the IC power pins. Ferrite beads may also be required for noise filtering.

So, the more ground the better—right? Ground planes solve many ground impedance problems, but not all. Even a continuous sheet of copper foil has residual resistance and inductance, and in some circumstances, these can be enough to prevent proper circuit function. Figure 3 shows such a problem—and a possible solution.

Figure 3. A slit in the ground plane can reconfigure current flow for better accuracy.

Due to the realities of the mechanical design, the power input connector is on one side of the board, and the power output section—which needs to be near the heat sink—is on the other side. The board has a 100-mm wide ground plane and a power amplifier that draws 15 A. If the ground plane is 0.038-mm thick and 15 A flows in it, there will be a voltage drop of 68 μV/mm. This voltage drop would cause serious problems for the ground-referenced precision analog circuitry sharing the PCB. The ground plane can be slit so that high current does not flow in the precision circuitry region; instead, it is forced to flow around the slit. This can prevent a grounding problem (which in this case it does), even though the voltage gradient increases in those parts of the ground plane where the current flows.

One thing to definitely avoid in multiple ground plane systems is overlapping the ground planes, especially analog and digital grounds. This will cause capacitive coupling of noise from one (probably digital ground) into the other. Remember that a capacitor is made up of two conductors (the two ground planes) separated by an insulator (the PC board material).

### Grounding and Decoupling Mixed-Signal ICs with Low Digital Currents

Sensitive analog components, such as amplifiers and voltage references, are always referenced and decoupled to the *analog* ground plane. The ADCs and DACs (and other mixed-signal ICs) with low digital currents should generally be treated as analog components and also grounded and decoupled to the analog ground plane. At first glance, this may seem somewhat contradictory since a converter has analog and digital interfaces and usually has pins designated *analog ground* (AGND) and *digital ground* (DGND). Figure 4 will help to explain this apparent dilemma.

Figure 4. Proper grounding of mixed-signal ICs with low internal digital currents.

Inside an IC that has both analog and digital circuits (an ADC or a DAC, for example), the grounds are usually kept separate to avoid coupling digital signals into the analog circuits. Figure 4 shows a simple model of a converter. There is nothing the IC designer can do about the wire bond inductance and resistance associated with connecting the bond pads on the chip to the package pins, except to realize it’s there. The rapidly changing digital currents produce a voltage at Point B that will inevitably couple into Point A of the analog circuits through the stray capacitance, CSTRAY. In addition, there is approximately 0.2 pF of unavoidable stray capacitance between every adjacent pin-pair of the IC package! It’s the IC designer’s job to make the chip work in spite of this. However, in order to prevent additional coupling, the AGND and DGND pins should be joined together externally to the *analog* ground plane with minimum lead lengths. Any extra impedance in the DGND connection will cause more digital noise to be developed at Point B which will, in turn, couple more digital noise into the analog circuit through the stray capacitance. Note that connecting DGND to the digital ground plane applies VNOISE across the AGND and DGND pins, inviting disaster!

The name “DGND” tells us that this pin connects to the digital ground of the IC. This does not imply that this pin must be connected to the digital ground of the system. It could be better described as the IC’s internal “Digital Return.”

It is true that the grounding arrangement described may inject a small amount of digital noise onto the analog ground plane, but these currents should be quite small and can be minimized by ensuring that the converter’s output does not drive a large fanout (they normally can’t, by design). Minimizing the fanout on the converter’s digital port (which, in turn, means lower currents) also keeps the converter’s logic transition waveforms relatively free of ringing, minimizes digital switching currents, and thereby reduces any coupling into the analog port of the converter. The logic supply pin (VD) can be further isolated from the analog supply by the insertion of a small lossy ferrite bead, as shown in Figure 4. The internal transient digital currents of the converter will flow in the small loop from VD through the decoupling capacitor and to DGND (this path is shown in red on the diagram). The transient digital currents will, therefore, not appear on the external analog ground plane but are confined to the loop. The VD pin decoupling capacitor should be mounted as close to the converter as possible to minimize parasitic inductance. The decoupling capacitors should be low inductance ceramic types, typically between 0.01 μF (10 nF) and 0.1 μF (100 nF).

Again, no single grounding scheme is appropriate for all applications. However, by understanding the options and planning ahead, problems can be minimized.

### Treat the ADC Digital Outputs with Care

It is always a good idea to place a data buffer adjacent to the converter to isolate the digital output from data bus noise (Figure 4). The data buffer also serves to minimize loading on the converter’s digital outputs and acts as a Faraday shield between the digital outputs and the data bus (Figure 5). Even though many converters have three-state outputs/inputs, these registers are on the die; they allow data pin signals to couple into sensitive areas, so the isolation buffer still represents good design practice. In some cases, it may even be desirable to provide an additional data buffer on the analog ground plane next to the converter output to provide greater isolation.

Figure 5. A high-speed ADC using a buffer/latch at the output shows enhanced immunity to digital data bus noise.

The series resistors (labeled “R” in Figure 4) between the ADC output and the buffer register input help to minimize the digital transient currents, which may affect converter performance. The resistors isolate the digital output drivers from the capacitance of the buffer register inputs. In addition, the RC network formed by the series resistor and the buffer register’s input capacitance acts as a low-pass filter to slow down the fast edges.

A typical CMOS gate, combined with PCB trace and a throughhole, will create a load of approximately 10 pF. A logic output slew rate of 1 V/ns will produce 10 mA of dynamic current if there is no isolation resistor:



|  |  |  |
| --- | --- | --- |
|  |  | (2) |

A 500 Ω series resistor will minimize the transient output current and result in rise- and fall-times of approximately 11 ns when driving the 10 pF input capacitance of the register:

|  |  |  |
| --- | --- | --- |
|  |  | (3) |



Figure 6. Grounding and decoupling points.

TTL registers should be avoided; they can appreciably add to the dynamic switching currents because of their higher input capacitance.

The buffer register and other digital circuits should be grounded and decoupled to the *digital* ground plane of the PC board. Notice that any noise between the analog and digital ground planes reduces the noise margin at the converter digital interface. Since digital noise immunity is of the order of hundreds or thousands of millivolts, this is unlikely to matter. The analog ground plane will generally not be very noisy, but if the noise on the digital ground plane (relative to the analog ground plane) exceeds a few hundred millivolts, then steps should be taken to reduce the digital ground plane impedance to maintain the digital noise margins at an acceptable level. Under no circumstances should the voltage between the two ground planes exceed 300 mV, or the ICs may be damaged.

Separate power supplies for analog and digital circuits are also highly desirable. The analog supply should be used to power the converter. If the converter has a pin designated as a digital supply pin (VD), it should either be powered from a separate analog supply or filtered, as shown in Figure 6. All converter power pins should be decoupled to the analog ground plane, and all logic circuit power pins should be decoupled to the digital ground plane, as shown in Figure 6. If the digital power supply is relatively quiet, it may be possible to use it to supply analog circuits as well, but *be very cautious*.

In some cases, it may not be possible to connect VD to the analog supply. Some high-speed ICs may have their analog circuits powered by +5 V, but the digital interface is powered by +3.3 V or less, to interface to external logic. In this case, the +3.3-V pin of the IC should be decoupled directly to the analog ground plane. It is also advisable to connect a ferrite bead in series with the power trace that connects the pin to the +3.3-V digital logic supply.

The sampling clock-generation circuitry should be treated like analog circuitry and also be grounded and heavily decoupled to the analog ground plane. Phase noise on the sampling clock degrades system signal-to-noise ratio (SNR); this will be discussed shortly.

### Sampling Clock Considerations

In a high-performance sampled-data system, a low-phase-noise crystal oscillator should be used to generate the ADC (or DAC) sampling clock, because sampling clock jitter modulates the analog input/output signal and raises the noise-and-distortion floor. The sampling clock generator should be isolated from noisy digital circuits and grounded and decoupled to the analog ground plane, along with the op amp and the ADC.

The effect of sampling clock jitter on ADC SNR is given approximately by Equation 4:

|  |  |  |
| --- | --- | --- |
|  |  | (4) |

where *f* is the analog input frequency, SNR is that of a perfect ADC of infinite resolution, and the only source of noise is rms sampling clock jitter, *tj*. Working through a simple example, if *tj* = 50 ps (rms), and *f* = 100 kHz, then SNR = 90 dB, equivalent to approximately 15-bit dynamic range.

It should be noted that *tj* in the above example is actually the root-sum-square (rss) value of the external clock jitter *and* the internal ADC clock jitter (called *aperture jitter*). However, in most high-performance ADCs, the internal aperture jitter is negligible compared to the jitter on the sampling clock.

Since degradation in SNR is primarily due to external clock jitter, steps must be taken to render the sampling clock as noise-free as possible with the lowest possible phase jitter. This requires that a crystal oscillator be used. There are several manufacturers of small crystal oscillators with low-jitter (less than 5 ps rms) CMOS-compatible outputs.

Ideally, the sampling clock crystal oscillator should be referenced to the analog ground plane in a split-ground system. However, system constraints may not permit this. In many cases, the sampling clock must be derived from a higher frequency multipurpose system clock that is generated on the digital ground plane. It must then pass from its origin on the digital ground plane to the ADC on the analog ground plane. Ground noise between the two planes adds directly to the clock signal and will produce excess jitter. The jitter can cause degradation in the signal-to-noise ratio and produce unwanted harmonics.

This can be relieved somewhat by transmitting the sampling clock signal as a differential signal, using either a small RF transformer—as shown in Figure 7—or a high-speed differential driver and receiver. If the latter are used, they should be ECL to minimize phase jitter. In a single +5-V supply system, ECL logic can be connected between ground and +5 V (PECL), with the outputs ac-coupled into the ADC sampling clock input. In either case, the original master system clock must be generated from a low-phase-noise crystal oscillator.

Figure 7. Sampling clock distribution from digital to analog ground planes.

### The Origins of the Confusion About Mixed-Signal Grounding

Most data sheets for ADCs, DACs, and other mixed-signal devices discuss grounding relative to a single PCB, usually the manufacturer’s own evaluation board. This has been a source of confusion when trying to apply these principles to multicard or multi-ADC/DAC systems. The recommendation is usually to split the PCB ground plane into an analog plane and a digital plane, with the further recommendation that the AGND and DGND pins of a converter be tied together and that the analog ground plane and digital ground planes be connected at that same point, as shown in Figure 8. This essentially creates the system “star” ground at the mixed-signal device. All noisy digital currents flow through the digital power supply to the digital ground plane and back to the digital supply; they are isolated from the sensitive analog portion of the board. The system star ground occurs where the analog and digital ground planes are joined together at the mixed-signal device.

While this approach will generally work in a simple system, with a single PCB and a single ADC/DAC, it is not optimum for multicard mixed-signal systems. In systems having several ADCs or DACs on different PCBs (or even on the same PCB), the analog and digital ground planes become connected at several points, creating the possibility of ground loops and making a singlepoint “star” ground system impossible. For these reasons, this grounding approach is not recommended for multicard systems; the approach discussed earlier should be used for mixed-signal ICs with low digital currents.

Figure 8. Grounding mixed-signal ICs: single PCB (typical evaluation/test board).

### Grounding for High-Frequency Operation

The “ground plane” layer is often advocated as the best return for power and signal currents, while providing a reference node for converters, references, and other subcircuits. However, even extensive use of a ground plane does not ensure a high-quality ground reference for an ac circuit.

The simple circuit of Figure 9, built on a two-layer printed circuit board, has an ac + dc current source on the top layer connected to Via 1 at one end and to Via 2 by way of a single U-shaped copper trace. Both vias go through the circuit board and connect to the ground plane. Ideally, the impedance in the top connector and in the ground return betw

## References

Barrow, Jeff. “Avoiding Ground Problems in High Speed Circuits.” *RF Design*, July 1989.

Barrow, Jeff. “[Reducing Ground Bounce in DC-to-DC Converters—Some Grounding Essentials.](/en/resources/analog-dialogue/articles/reducing-ground-bounce-in-dc-to-dc-converters.html)” *Analog Dialogue*. Vol. 41, No. 2, pp. 3-7, 2007.

Bleaney, B & B.I. *Electricity and Magnetism*. Oxford at the Clarendon Press, 1957: pp. 23, 24, and 52.

Brokaw, Paul. AN-202 Application Note. *An IC Amplifier User’s Guide to Decoupling, Grounding and Making Things Go Right for a Change*. Analog Devices, 2000.

Brokaw, Paul and Jeff Barrow. AN-345 Application Note. *Grounding for Low- and High-Frequency Circuits*. Analog Devices.

[The Data Conversion Handbook](https://www.amazon.com/Data-Conversion-Handbook-Analog-Devices/dp/0750678410/190-4718663-3375248?ie=UTF8&n=507846&qid=1107208688&redirect=true&ref_=pd_bbs_1&s=books&sr=8-1&v=glance). Edited by Walt Kester. [Newnes](http://store.elsevier.com/categoryController.jsp?categoryId=EST_IMP-73), 2005. ISBN 0-7506-7841-0.

Johnson, Howard W. and Martin Graham. *High-Speed Digital Design*. PTR Prentice Hall, 1993. ISBN: 0133957241.

Kester, Walt. “A Grounding Philosophy for Mixed-Signal Systems.” *Electronic Design Analog Applications Issue*, June 23, 1997: pp. 29.

Kester, Walt and James Bryant. “Grounding in High Speed Systems.” *High Speed Design Techniques. Analog Devices*, 1996: Chapter 7, pp. 7-27.

[Linear Circuit Design Handbook](http://store.elsevier.com/product.jsp?isbn=9780750687034&ref=CWS1). Edited by Hank Zumbahlen. [Newnes](http://store.elsevier.com/categoryController.jsp?categoryId=EST_IMP-73), February 2008. ISBN 978-0-7506-8703-4.

Montrose, Mark. *EMC and the Printed Circuit Board*. IEEE Press, 1999 (IEEE Order Number PC5756).

Morrison, Ralph. *Grounding and Shielding Techniques*. 4th Edition. John Wiley & Sons, Inc., 1998. ISBN: 0471245186.

Morrison, Ralph. *Solving Interference Problems in Electronics*. John Wiley & Sons, Inc., 1995.

Motchenbacher, C. D. and J. A. Connelly. *Low Noise Electronic System Design*. John Wiley & Sons, Inc., 1993.

[Op Amp Applications Handbook](http://store.elsevier.com/product.jsp?isbn=9780750678445&pagename=search). Edited by Walt Jung. [Newnes](http://store.elsevier.com/categoryController.jsp?categoryId=EST_IMP-73), 2005. ISBN 0-7506-7844-5.

Ott, Henry W. *Noise Reduction Techniques in Electronic Systems*. 2nd Edition. John Wiley & Sons, Inc., 1988. ISBN: 0-471-85068-3.

Rempfer, William C. “Get All the Fast ADC Bits You Pay For.” *Electronic Design*. Special Analog Issue, June 24, 1996: pp. 44.

Rich, Alan. “[Shielding and Guarding](/en/resources/analog-dialogue/articles/shielding-and-guarding.html).” *Analog Dialogue*. Vol. 17, No. 1, pp. 8, 1983.

Sauerwald, Mark. “Keeping Analog Signals Pure in a Hostile Digital World.” *Electronic Design*. Special Analog Issue, June 24, 1996: pp. 57.

## Acknowledgements

The material presented in this article was compiled from many contributors, including James Bryant, Mike Byrne, Walt Jung, Walt Kester, Ray Stata, and the engineering staff at Analog Devices.