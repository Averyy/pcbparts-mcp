---
source: "TI SLOA069 -- How (Not) to Decouple High-Speed Op Amps"
url: "https://www.ti.com/lit/an/sloa069/sloa069.pdf"
format: "PDF 14pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 17236
---
# How (Not) to Decouple High-Speed Operational Amplifiers

Bruce Carter, High Performance Linear Products

## Abstract

Decoupling the power supply pins of high-speed operational amplifier circuits is critical to their operation. Decoupling is also one of the least understood topics in engineering. It is seldom given the time or care required, yet it is relatively simple. This document will explain the pitfalls in decoupling and offer some correct techniques.

## Introduction

Decoupling in high-speed design is usually done with little care. Engineers are so eager to get a prototype operational that they grab a handful of 0.1-uF or 0.01-uF capacitors out of a laboratory bin and assume the job is done. Decoupling is a design task worthy of at least the same degree of analysis as calculating an operational amplifier's gain or filter. Proper decoupling techniques do not have to be any more difficult than other design tasks.

When a capacitor is used for decoupling, it is connected as a shunt element to carry RF energy from a specific point in a circuit, away from a circuit power pin, and to ground. Ideally, the impedance of the capacitor to ground should appear as low as possible to the RF energy that needs to be rejected. It is important to know the frequencies that are causing problems and to select the right capacitor(s) to eliminate those frequencies.

## Know Your Capacitor!

All capacitors are not created equal. A 0.1-uF or 0.01-uF capacitor from a lab bin may or may not be what is expected. Most lab stock is stripped of information that would indicate the part's manufacturer, grade, dielectric used, or its frequency characteristics. At high frequencies, the capacitor may operate quite differently from the brick-wall high-frequency short that the designer wants.

### Capacitor Impedance and Series Self Resonance

**Misconception number 1:** Most designers think that a capacitor's value is independent of frequency. It is not. The published value of capacitance is taken at a frequency the manufacturer specifies. It is relatively constant at low frequencies, but the value can change by more than an order of magnitude at high frequencies.

Capacitors have a series self-resonant frequency due to parasitic inductance. Capacitors also have parallel self-resonances that will be discussed later. As the operating frequency approaches the capacitor's series self-resonant frequency, the capacitance value will appear to increase. This results in an effective capacitance C_E that is larger than the nominal capacitance.

A simplified high-frequency model of a capacitor includes:

- C_O: Nominal capacitance at a frequency defined by the manufacturer
- L_S: Equivalent series inductance
- ESR: Equivalent series resistance
- R_P: Parallel (leakage) resistance

Figure 1. High-Frequency Capacitor Model

The effective capacitance C_E is a function of the reactance developed between the capacitor and its parasitic series inductance L_S:

$$C_{E} = \frac{C_{O}}{1 - (2\pi F_{O})^{2} L_{S} C_{O}}$$

A capacitor's series self-resonant frequency F_SR is defined as:

$$F_{SR} = \frac{1}{2\pi\sqrt{L_{S}C_{O}}}$$

The Q, or sharpness of the resonance characteristic, is given by:

$$Q = \frac{|X_{C} - X_{L}|}{ESR \| R_{P}}$$

At the capacitor's series self-resonant frequency, the reactance from C_O and L_S are equal and opposite, yielding a net reactance of zero. At this self-resonance, the net impedance will be equal to ESR||Rp. The capacitance at the series self-resonance will therefore be undefined, and the capacitor will have the lowest impedance at the series self-resonant frequency when used for decoupling. This impedance is typically in the range of milliohms. At frequencies below series self-resonance, the impedance will be capacitive, and at frequencies above series self-resonance, the impedance will be inductive. The impedance of the capacitor increases rapidly as the frequency is moved away from series self-resonance:

$$Z_{c} = \sqrt{(ESR \| R_{P})^{2} + (X_{L} - X_{c})^{2}}$$

Figure 2. Typical Series Self-Resonances of Capacitors

The series self-resonant frequencies are relatively low. This should be a clue to high-frequency designers that they need to take great care in selecting bypass capacitors. Some hints follow:

- A designer can maximize rejection of an unwanted RF frequency by selecting a capacitor with a series self-resonant frequency corresponding to the unwanted frequency.
- No single capacitor can be expected to properly decouple a system where multiple RF frequencies are present. Capacitors can be placed in parallel to reject different RF frequencies.
- A capacitor becomes a dc blocking inductor above the series self-resonant frequency, which can present high-impedance to the RF interfering frequency, defeating the purpose of having a decoupling capacitor. This is why it is so bad to put the standard 0.1-uF or 0.01-uF capacitor (of questionable vintage) on a PCB. It lulls the designer into a false sense of security.

Figure 3. Bypass Capacitor Selection

It is important to be close: Q values for microwave capacitors can be in the hundreds, meaning that a small error in series self-resonant frequency can change the attenuation by orders of magnitude.

To select the correct capacitor to reject a given frequency, follow the frequency line on the chart over to where it intersects the line on the graph, then go down the chart to the capacitance value. In Figure 3, to reject 1.9 GHz, 15 pF would be the correct value.

**Misconception number 2:** Most designers think that when poor decoupling is suspected, increasing the value of capacitance will produce more attenuation. The exact opposite is true. When poor decoupling of high frequencies is suspected, decrease the value of capacitance (or preferably, do the homework and look up the series self-resonance).

Correctly bypassing a high-speed operational amplifier circuit is as simple as maintaining a prototyping kit of microwave capacitors and looking up the correct value(s) of capacitance on a graph.

### Parallel Self-Resonance

Capacitors also have parallel self-resonance frequencies, related to the way they are manufactured and mounted on a PCB. There is only one series resonant frequency, but there are a series of parallel capacitances. A rough rule of thumb is that the first parallel resonant frequency occurs at about twice the series resonant frequency.

While a capacitor has its lowest impedance at the series self-resonant frequency, it typically has its highest impedance at the parallel self-resonant frequencies. Therefore, while it is possible to take advantage of the series resonant frequency for RF purposes, the capacitor is useless at parallel resonant frequencies.

Figure 4. Capacitor on a PCB

The capacitor is a collection of parallel plates. These plates sum together to produce the effective capacitance C_E, but because all conduction is skin conduction at high frequencies, there is also some parasitic parallel capacitance plate-to-plate. In addition, because most capacitors are mounted horizontally on PCBs, there is also parasitic capacitance from the horizontal plates to the ground and power planes of the PCB.

Figure 5. High-Frequency Capacitor Model with Parallel Capacitance

Figure 6. Response of a High-Frequency Capacitor Above Series Self-Resonance

The first parallel resonant frequency (PRF1) occurs very close to the series self-resonance (SRF). This is a danger sign to the designer that capacitor tolerance could change the attenuation at SRF into transmission at PRF1 very easily. It is very desirable to get rid of PRF1!

Fortunately, there is a very easy way to eliminate PRF1, as well as all odd parallel resonant frequencies. If the capacitor is mounted on its side, the plates inside the capacitor are now perpendicular to the PCB:

Figure 7. Vertical Capacitor Mounting

This will eliminate the parasitic capacitances between the plates of the capacitor and planes on the PCB. The resulting spectrum shows that PRF1, as well as all odd parallel resonances, are eliminated:

Figure 8. Resulting Response from Mounting a Capacitor Vertically

The response curve shows that the capacitor will be usable for a much larger range of frequencies above the SRF, providing that predominately-inductive impedance is acceptable. The first region of high impedance at PRF2 does not occur until almost 2.5 times the SRF frequency.

Mounting a capacitor in this way runs counter to the training of manufacturing and inspection personnel, who will have to revise their thinking for a high-speed PCB.

### Capacitor Dielectric Types

Just as the internal construction and orientation of capacitor plates affect its self-resonant characteristics, the material between the plates, the dielectric, affects the characteristics of the capacitor.

| Dielectric Name | Stability              | EIA Class | TC (Temperature Coefficient) | Range          |
|-----------------|------------------------|-----------|------------------------------|----------------|
| NPO or COG     | Very stable, high Q    | I         | +/- 30 PPM                   | -55 to +125 C  |
| X7R             | Semistable             | II        | +/- 15%                      | -55 to +125 C  |
| Z5U             | Less stable            | III       | +22 / -56%                   | +10 to +85 C   |
| Y5V             | Least stable           | III       | +22 / -82%                   | -30 to +85 C   |

Table 1. Capacitor Dielectric Characteristics

The average bin of laboratory stock capacitors is probably X7R or worse, because these are lower cost than the very desirable NPO (also called COG). 0.1-uF or 0.01-uF value capacitors used as decoupling capacitors are relics of the age of discrete digital design. It is time for designers to adopt a new mindset about decoupling. The smartest decoupling design decision a designer can make would be to take the existing lab stock of supposed decoupling capacitors and dump them into a waste container. High-frequency decoupling requires NPO/COG capacitors.

NPO/COG capacitors tend to get expensive at high values of capacitance. Fortunately for designers, it will seldom be necessary to use high values of capacitance.

### What About Electrolytic Capacitors?

Electrolytic capacitors, whether they are aluminum or tantalum, are very-low-speed devices. Their self-resonant frequency is limited to a range between 100 kHz and 1 MHz. Therefore, they are no good for decoupling high frequencies. The primary purpose of electrolytic decoupling capacitors is to filter power-supply switching noise, which is in this range.

The primary use for electrolytic capacitors is at frequencies below 1 MHz. If a designer is sure that these frequencies are present, then they are necessary. If, however, there is no reason to believe that these frequencies are present, electrolytic capacitors are not necessary.

It is advantageous to omit electrolytic capacitors whenever possible:

- Most electrolytic capacitors are on allocation from manufacturers, with long lead times.
- Electrolytic capacitors are large, and they force other traces in a high-speed design to be correspondingly longer to accommodate them. High-speed design requires that traces be as short as possible to avoid parasitic capacitance and inductance.
- The pads required to support an electrolytic capacitor disrupt the width and placement of traces and vias, creating an opportunity for RF noise to be radiated into the circuit at the point where the capacitor is placed.

### How to Lay Out Decoupling Capacitors on the PC Board

Once the proper capacitor has been selected, it must be applied properly on the PCB, or all of the care in selection will be in vain.

#### Trace Inductance

The worst problem, by far, created by long connections is trace self-inductance. The formula for the inductance of a wire or PCB trace can be approximated by:

$$L(nH) = 2x \cdot \left( ln \left( \frac{2x}{w+h} \right) + 0.2235 \left( \frac{w+h}{x} \right) + 0.5 \right)$$

Where: x = length of the trace (cm), w = width of the trace (cm), h = height of the trace (cm)

The inductance is relatively unaffected by the height of the trace. It is more affected by the width, but it takes a large change in width to substantially affect the inductance. The predominant effect is the length. Common PCB traces have self-inductances that measure between 6 nH and 12 nH per centimeter.

This is very bad news at high frequencies. For example, assume:
- A cell phone application that must decouple 1.9 GHz
- 6 nH/cm trace self inductance
- 1.5 cm of circuit traces to the decoupling capacitor
- A 30-pF capacitor with a C_E of 27.77 pF, and an L_S of 0.23 nH

The SRF of the capacitor will be 1.92 GHz, ideal for cell phones. But inductance adds in series. If 9 nH is added to the L_S of the capacitor, the series self-resonance becomes 314 MHz. This PCB layout is entirely unsuitable. Clearly, trace inductance must be avoided at all costs!

The self-inductance of PCB traces is so large that any trace length negates careful capacitor selection. Fortunately, most high-frequency PCBs are now multilayer and have both power and ground planes. Designers should place vias from the planes as close as possible to the pad of the capacitor. Preferably, they should be incorporated into the copper structure of the pad itself.

Figure 10. Proper Feedthru Method

Even a couple of millimeters adds 1.2 nH to the L_S of the capacitor. Using PCB traces to make connections to decoupling capacitors simply cannot work! The best that the designer can achieve is to minimize trace length by moving the feedthrus as near as possible to the part and making the resulting connection as wide as possible.

#### Via Inductance

Whenever there is a via on a PCB, a parasitic inductor is also formed. At a given diameter (d) the approximate inductance (L) of a via at a height of (h) may be calculated as follows:

$$L \approx \frac{h}{5} \cdot \left(1 + \ln\left(\frac{4h}{d}\right)\right) \text{ nH}$$

A 0.4-mm diameter via through a 1.5-mm thick PCB has an inductance of 1.1 nH.

Three techniques combat via inductance:

- Many PCB manufacturers offer laser drill systems that can create microvias with diameters from 0.15 mm down to 0.025 mm.
- A blind via will reduce via height and, therefore, the inductance.
- Placing multiple vias in parallel can reduce inductance.

Two blind microvias with a diameter of 0.025 mm going to an adjacent layer on a ten-layer board (h = 0.15 mm) reduce the via inductance to 0.063 nH.

Height is the predominant factor, so blind vias are much more important than microvias. One blind microvia with a diameter of 0.15 mm going to an adjacent layer (h = 0.15 mm) reduces the via inductance to 0.072 nH. This may reduce PCB cost significantly, because 0.15 mm is the lower limit of conventional drilling techniques.

#### An Alternative Approach

If blind vias and laser processing are not acceptable for cost reasons, the designer sometimes can borrow layout techniques from RF designers to combat parasitic inductances.

Figure 12. High-Speed Layout with RF Techniques

Key features:

- It is a multilayer board, with internal power and ground planes.
- Multiple connections are made with vias around the outside of the circuit to a ground plane. The parasitic inductance is low because it adds in parallel, reducing the overall value.
- Ground-plane connections to the IC and the decoupling capacitor are made on the top layer with thermal reliefs. Thermal reliefs do act as traces and therefore add a small amount of inductance, but they are necessary for proper soldering.
- Connection to power is made with a via, but the via and trace inductances appear before the capacitor, which is on the same pad as the power pin of the IC. Therefore, the parasitic via and trace inductance do not add to the capacitor's series self-resonance. They actually help, by adding impedance at high frequencies to the power connection.
- The capacitor should be mounted vertically on its side.
- When power and ground planes are used in a multilayer board, they add distributed capacitance to the system, improving broadband noise rejection.

## Conclusions

Decoupling high-speed operational amplifier circuitry requires a little bit of design work. Capacitors should be selected for their high-speed characteristics, including self-resonant frequency. They should be mounted vertically (on the side) to avoid parasitic capacitance with the PCB. Care should be taken when using PCB traces and vias, because both have parasitic inductance that adds to that of the capacitor.

## Bibliography

1. *Capacitors in Bypass Applications*, Richard Fiore, American Technical Ceramics
2. *Effective Capacitance vs Frequency*, Richard Fiore, American Technical Ceramics
3. *Decoupling Basics*, Arch Martin, AVX Corporation
4. *SRF & PRF and Their Relation to RF Capacitor Applications*, Johansen Technology
5. *Ask The Applications Engineer*, James Bryant, Analog Devices
