---
source: "ECS Inc. -- Impact of Load Capacitance on Crystal Designs"
url: "https://ecsxtal.com/news-resources/the-impact-of-load-capacitance-on-crystal-oscillator-designs/"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 17303
---

[Download PDF](/store/pdf/The-Impact-of-Load-Capacitance-on-Crystal-Oscillator-Designs.pdf)

Load capacitance plays a critical role in the design and performance of crystal oscillator circuits, particularly in Pierce Oscillator Loops commonly used in microcontroller (MCU) applications. Properly matching the load capacitance to the crystal’s specifications ensures the crystal operates at its intended frequency and desired operating conditions. However, design oversights regarding load capacitance are common, often leading to frequency deviations, slow start-up/ no start-up or reduced reliability over temperature.

This paper will explore the misconceptions often made when matching oscillator designs, as well as the design aspects impacted by load capacitance in the circuit. It builds on ECS Inc.’s white paper [Oscillator Design Basics](https://ecsxtal.com/store/pdf/oscillator-circuit-design-basics.pdf?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper), which can be found on the ECS Inc. website under [Technical Guides](https://ecsxtal.com/news-resources/electronic-components-technical-guides/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper). Additional resources for design engineers, such as our [Load Capacitance Calculator](https://ecsxtal.com/crystal-load-capacitance-calculator/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper), can be found in the [Design Tools](https://ecsxtal.com/design-tools/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper) section on our website.

### What is Load Capacitance?

Crystal load capacitance (CL ) and the load capacitance of an oscillator circuit are related but distinct concepts in frequency control. Crystal load capacitance (CL ) refers to the specific capacitance value defined by the crystal manufacturer that the external circuit must provide for the crystal to operate at its intended frequency. In contrast, the “load capacitance of an oscillator circuit” represents the total load capacitance experienced by the crystal in the circuit, which includes not only the capacitors designed in to match the specified CL but also stray capacitance from PCB traces and the Cin / Cout of the IC in the oscillator loop.

The goal is to match the total load capacitance of the circuit to the crystal’s specified CL . When this is achieved, and sufficient drive is provided, the oscillator will operate within the specified frequency tolerance at 25°C. This effectively replicates the conditions under which the crystal was manufactured and tested, where the CL was set to a defined value, such as 8pF. Load capacitance refers to the total external capacitance in parallel with the crystal, including both intentional components and stray elements.

### Resonant Frequency and Mode of Resonance

Crystals can operate in fundamental mode, the primary frequency of the crystal or in overtone modes as specified 3rd or 5th overtones. These overtones are odd harmonics. Fundamental frequencies in crystals have increased over the last 5 years, as crystals have got smaller and now can reach 96 MHz.

All crystals have two modes of resonance, series and parallel but are calibrated during manufacturing to only one of the resonance points. You can read more about the differences between series and parallel resonant crystals and guidance on selecting the appropriate type for specific oscillator designs in our technical paper [Choosing Series or Parallel Resonant Crystals Oscillator Design and Load Capacitance](https://ecsxtal.com/choosing-series-or-parallel-resonant-crystals-oscillator-design-and-load-capacitance/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper).

*In Figure 1, we see that the crystal’s parallel-resonance mode is always above the series
resonance frequency (fs) and is characterized by inductive reactance.*

*Figure 2 – Parallel Resonance Mode showing the Capacitive Load Region.*

Figure 2 depicts the reactance curve of a quartz crystal which exhibits two zero-phase frequencies, the series resonant frequency (Fs) where reactance is zero and resistance is minimal, and the anti-resonant frequency (Fa) where resistance peaks. Fa should not govern oscillator circuits. The red-highlighted slope between Fs and Fa represents the inductive reactance slope, defining the capacitive loading (CL) region for parallel resonance crystals in Pierce Oscillators.

So, now we can see how the CL of the crystal operates along the red highlighted slope, increasing from bottom to top in pF as the inductive reactance increases.

### How different CL changes the circuit:

To illustrate this, two examples from ECS Inc.’s product lineup have been selected, both operating at the same frequency (12 MHz) but featuring different load capacitances (CL). Notably, both components share the same package size (3.2 x 2.5 mm) and equivalent series resistance (ESR) of 100 Ω.

ECS-120-**20**-33-AEL-TR features a load capacitance of **20pF**

ECS-120-**8**-33B-CHN-TR features a load capacitance of **8pF**

* What impact does this difference in CL have?
* Why pick one over the other?

Looking back to Figure 2, the two crystals will operate at opposite ends of the capacitive loading region. The 20pF CL will have a higher capacitive reactance (Xc) to balance the higher inductive reactance (Xl), while the 8pF CL will have a lower Xc.

An analogy in mechanical terms is like a heavy pendulum (20pF) and a lighter pendulum (8pF). The heavier mass takes more effort to start to swing and is slower to start. So, the 20pF CL will take more drive to make it start and will have a slower start-up time. The lighter (8pF) will be easier to deflect and change its velocity. Remembering the Piezoelectric properties of crystals, the 20pF CL load will have a larger plated area and more mass.

Both will operate at the same frequency (12 MHz) if matched correctly, but the 8pF CL will be prone to more “Frequency Pulling” than the larger 20pF CL load.

### Frequency Pulling:

As a reminder here is the approximate equation for crystal pulling limits:

The limits of ∆f depend on the crystal Q and stray capacitance of the circuit. If the shunt capacitance, motional capacitance, and load capacitance are known, the average pulling per pF can be found using:

These formulas demonstrate the importance of CL as it plays a significant role in the crystal pulling ratio. In many MCU designs, particularly those utilizing external fixed matching capacitors, a low pulling ratio is desirable and is significantly influenced by crystal CL value. While lower C0 and CL values offer certain advantages, the frequency pulling (ppm per pF) becomes more pronounced as CL decreases. A reasonable balance is typically achieved at CL values of 6pF or higher. For designs where the matching capacitance is integrated within the MCU, the pulling factor remains critical. In these cases, the crystal is often calibrated in pF increments, and the calibration accuracy directly depends on the ppm per pF of the crystal.

### Oscillator Margin:

One of the most important considerations when picking a crystal in a design is whether the oscillator will start. This is where knowledge of the MCU transconductance plays a critical role. This can be seen mathematically in the calculation of the oscillator margin (OM) based on the oscillator transconductance (gm) and the gm\_crit of the crystal.

For an oscillator to start up consistently, you need to consider the transconductance. To ensure oscillation starts and reaches a stable phase, the oscillator must provide enough gain to compensate for the oscillation loop losses and to provide the energy for the oscillation build-up. As outlined in the [Oscillator Circuit Design Basics](https://ecsxtal.com/crystal-oscillator-design-application-note/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper) whitepaper, the oscillator margin ratio (gm / gm\_crit) must be carefully managed.

Simply exceeding a value of 1 can result in prolonged start-up times or even prevent start-up altogether. To ensure reliable performance, designers should aim for an oscillator margin of at least 5, where:

**Oscillator Margin = gm / gm\_crit ≥ 5**

Here, gm is the oscillator transconductance specified in the IC datasheet.

### The Part Played by Gm\_crit:

Assuming the design is using equal CL1 and CL2 values, gm\_crit is expressed as follows:

It’s a critically important notation to define the model of the crystal and frequency in the oscillation loop. ECS Inc. specifies gm\_crit in its [Parametric Search](https://ecsxtal.com/parametric-search/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper).

ECS-120-**20**-33-AEL-TR: gm\_crit = 1.421mA/V, requiring a minimum gm of **7.105mA/V**.

ECS-120-**8**-33B-CHN-TR: gm\_crit = 0.275mA/V, requiring a minimum gm of **1.375mA/V**.

In these examples, both have the same frequency and ESR, both critical factors, but have different C0 and CL values, which significantly influence the gm\_crit calculation.

The results demonstrate that the 8pF CL crystal requires far less drive to meet the minimum gain margin. This is critical in modern ultra-low-power MCUs, which may struggle to drive larger loads and achieve startup under all conditions. Additionally, lower CL values support faster startup times, a key benefit for applications transitioning from sleep modes.

### Crystal Matching:

Now we have made some considerations for the crystal CL, we must make sure we pick the correct value of capacitance to bring the crystal to resonance. Let’s revisit the earlier crystal examples:

ECS-120-**20**-33-AEL-TR
ECS-120-**8**-33B-CHN-TR

In the introduction, I mentioned misconceptions about matching capacitance, the most common include ***the capacitor values are the same as the CL as well as the combined capacitors totaling the CL value.*** While these assumptions may occasionally hold true, relying on them of ten leads to incorrect results. These misconceptions overlook other key factors, such as the Cin and Cout of the inverter within the MCU oscillator and the PCB’s stray capacitance (Cs).

Therefore, to accurately calculate the required capacitance, these additional capacitances must be considered using the following formula:

Example 1: If we consider a real-world example using the MCU **STM32H5**, here the HSE **gm = 7.5mA/V**, and ECS-120-20-33-AEL-TR has a gm\_crit = **1.421mA/V**, allowing an oscillator margin of **5.28**.

To calculate the matching capacitors (CL1 and CL2), using the formula above, we must estimate the stray capacitance (Cs), which typically ranges from 2pF (excellent) to 5pF (less ideal). Since the actual Cs are only determined after testing the PCB, circuit, and oscillator loop, we’ll estimate Cs at 3pF for this example. The Cin and Cout of the STM32H5 are both 5pF.

Using these values and standard capacitor values, the external matching capacitors (CL1 and CL2) would be **30pF when using a 20pF CL.**

Example 2: If we consider another lower drive example using the MCU **STM32L1**, here the HSE **gm = 3.5mA/V**, and ECS-120-**8**-33B-CHN-TR has a gm\_crit = **0.275mA/V**, allowing an oscillator margin of 12.72.

Using the same estimated Cs of 3pF and the Cin and Cout values of 5pF, the external matching capacitors (CL1 and CL2) would be **5.1pF when using an 8pF CL.**

This comparison highlights the significant impact the value of CL makes on the overall impedance in the loop. For instance, pairing the ECS-120-**20**-33-AEL TR with the STM32L1 would yield an oscillator margin of only 2.46—well below the recommended threshold of 5. While oscillation might start, the design would lack robustness and could fail under varying conditions.

### Drive Level Considerations:

Crystals with higher CL automatically require larger matching capacitance values (CL1 and CL2). As shown below, these values are one of the elements influencing the drive level.

The drive level (DL) can be computed using the following formula:

DL= I²QRMS × ESR

Where IQRMS is the RMS AC current.

The RMS voltage is related to the RMS current by the equation:

IQRMS = 2 π F x VRMS x Ctot,

Where:

* F = crystal frequency
* VRMS =  where Vpp is the peak-to-peak voltage measured at **CL1** level
* Ctot = CL1 + (Cs / 2) + Cprobe, where:
  – CL1 is the external load capacitance at the amplifier input
  – Cs is the stray capacitance
  – Cprobe is the probe capacitance

  Therefore,

Let Vpp = 1.5V
Let Cprobe = 1pF

For ECS-120-**20**-33-AEL-TR estimated at: **168uW**, this solution would require a Rs damping resistor, but since the existing oscillator margin is only 5.28, adding an Rs would push this <5.

ECS-120-**8**-33B-CHN-TR estimated at: **9.23uW**
This value must not exceed the drive level specified by the crystal manufacturer.

### Jitter and Phase Noise:

Jitter is created when the period-to-period measurements are inconsistent. This is seen in the duty cycle of the square wave created and is exasperated by poorly optimized oscillator circuit design and impedance mismatches. While controlling noise sources—both emitted and conducted—and using low-noise amplifiers can help reduce jitter, they cannot fully eliminate mismatches.

**Crystal CL:** Crystals with lower CL values have a greater pulling ratio and are more prone to
higher jitter if not properly matched.

**Operating Frequency:** Higher operating frequencies can lead to increased jitter, requiring more careful design considerations to mitigate its effects.

### Modern MCU’s:

Modern microcontrollers (MCUs) are trending toward much lower transconductance (gm), which necessitates the use of lower load capacitance (CL) compared to previous designs. This is particularly relevant for wireless ICs, where clocking frequencies around 48–52 MHz are common. The higher frequency amplifies the impact of drive current, making it harder to reach satisfactory oscillator margins.

### Conclusion:

In conclusion, load capacitance (CL) plays a pivotal role in power-conscious designs by directly impacting the crystal oscillator’s performance, including heat generation, consumption and overall system stability.

Properly selecting and matching CL ensures efficient operation by minimizing the drive level, which in turn reduces the power consumed and the heat generated in the circuit. Lower CL values typically result in faster start-up times and lower drive levels, offering benefits in low-power applications where energy efficiency is crucial. However, this comes with the trade-off of increased frequency pulling.

On the other hand, higher CL values lead to slower start-up times, increased power consumption but can offer greater stability due to the lower frequency pulling. Balancing these factors based on the specific application requirements, such as in modern MCUs with lower transconductance, is essential for optimizing power usage and preventing excessive heat build-up. Therefore, load capacitance not only determines the oscillation characteristics but also contributes to achieving energy-efficient designs that are vital in modern, power-sensitive applications.

For more technical resources, please reference our library of [technical guides](https://ecsxtal.com/news-resources/electronic-components-technical-guides/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper), educational [video library](https://ecsxtal.com/news-resources/video-learning/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper) on frequency control and product information, our [reference design library](https://ecsxtal.com/news-resources/reference-designs/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper) or our current [product catalog](https://ecsxtal.com/news-resources/catalogs/?utm_source=Load-Capacitance-Whitepaper-ECS&utm_medium=Whitepaper&utm_campaign=Load-Capacitance-Whitepaper-ECS&utm_id=Load-Capacitance-Whitepaper-ECS&utm_term=Whitepaper).