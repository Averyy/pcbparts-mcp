---
source: "Abracon -- Ferrite Beads: Basic Operations and Key Parameters"
url: "https://abracon.com/uploads/resources/Ferrite-Beads-White-Paper.pdf"
format: "PDF 9pp"
method: "claude-extract"
extracted: 2026-02-15
chars: 13258
---
# Ferrite Beads: Basic Operations and Key Parameters

Ahmed Alamin, Product Engineer, Inductors and Connectivity, Abracon, LLC

## Introduction

To ensure proper operating conditions and communication integrity, multiple standards that restrict noise and radiation levels at both subsystem and intersystem levels have been developed by governmental and professional entities. To meet the standard requirements, designers are tasked with using proper techniques to ensure that noise levels are below the set boundaries. Ferrite beads are one of the many circuit-level passive components used to reduce the EMI noise that propagates within an electronic system. This paper highlights the fundamentals of ferrite beads and the key parameters that must be considered when using them in a design.

## What are Ferrite Beads?

A ferrite bead is a passive electrical component used to suppress high-frequency noise, EMI, and crosstalk in electronic circuits. They come in different shapes and sizes; some beads are available in the form of clamp-on cores, like the ones found at the ends of laptop chargers and digital signal cables. They can also be found as through-hole or SMD components, which are more suitable to be mounted on PCBs. Ferrite beads are composed of a conductor coil, typically copper, that is embedded within a ferrite material core. Ferrite cores are made of iron oxide and oxide composite materials, such as zinc, nickel, manganese, and ceramic material. The type of ferrite used in ferrite beads is soft ferrite, meaning they cannot be permanently magnetized but can conduct magnetic field flux due to their high permeability. Ferrite beads are commonly used in conjunction with other components such as capacitors to build various configurations of passive low-pass filters that block high-frequency noise.

*Figure 1: Different types of ferrite beads*

## How Ferrite Beads Work and Their Differentiation from Inductors

Ferrite beads' fundamental operation is like that of inductors: when there is a change in current, a changing magnetic field is generated in the core of the bead, which induces a voltage across the bead in the opposite direction of the original current, and thus, impedes it. The greater the rate of change of the original current, the greater the induced voltage, resulting in a greater impedance to the current flow.

It is easy to confuse inductors and ferrite beads since both look physically similar and have similar schematic symbols. Therefore, it is important to make a clear distinction between the two. The key difference between beads and inductors is their frequency characteristics and how they are utilized to serve a specific purpose in the circuit. Inductors are designed to efficiently maintain the magnetic field and to minimize the losses of magnetic energy at the operating frequencies, leading to a maximized Quality Factor (Q). High Q is desirable in applications such as impedance matching in RF circuits and different types of resonators, oscillators, filters, and any application where energy transfer is required.

On the other hand, ferrite beads are engineered to have the minimum impedance (inductance) at the operating frequency bands, such that the frequencies of interest in the system are minimally attenuated, and the impedance is maximum at frequency bands where noise is expected. This is achieved by designing the bead such that the resonant frequency is in the same frequency band as the noise to be filtered. Since the resistive component of the impedance dominates at resonance due to the cancellation of the inductive and capacitive components, ferrite beads become lossy, low-Q, inefficient devices within these bands, which allows them to dissipate the noise energy in the form of heat.

## Why and Where are Ferrite Beads Used?

Ferrite beads are relatively inexpensive and are widely used in a variety of electronic devices, including computers, mobile phones, and other electronic gadgets. Clamp-on ferrite beads can be used to reduce common-mode signals propagating through differential cables. They are usually placed near DC supply rails to prevent the noise from traveling between the circuit and the rails. Moreover, the isolation provided by the beads allows mixed-signal circuits to share the same rail while preventing noise from coupling between different circuits. They are also used in signal lines to suppress the high-frequency noise that might cause problems for low-power, low-frequency signals that can be found in many digital communication protocols. In addition, beads can be used along with TVS to suppress the high-voltage transients resulting from electrostatic discharge (ESD) and to protect the sensitive parts of the circuits from damage.

## Key Parameters to Consider When Using a Ferrite Bead

### The Crossover Point

The crossover point is where the reactance (X) curve crosses the resistance (R) curve. The significance behind this point is that it is designated as a barrier between the inductive and resistive bands of the ferrite beads. This allows designers to know what noise frequencies the ferrite beads attenuate the best, as the end goal is to ensure that the noise falls within the resistive band. Figure 2 below shows the frequency characteristics of Abracon's AFBC-Q0805G-102 ferrite bead. The crossover frequency for this part is near 100MHz. This is where the bead starts to display resistive characteristics, which makes this bead good for applications where noise is between 100MHz and 200MHz. However, this graph only tells part of the story, as the operating conditions have a direct influence on the frequency characteristics and will be discussed later in this paper.

*Figure 2: Frequency characteristics of AFBC-Q0805G-102*

In the inductive region, the reactance is equal to the impedance. The inductance of the bead can be calculated by:

L = XL / (2 * pi * f)

Where:
- F: the frequency
- XL: the reactance of the bead

In the resistive region, the impedance of the bead is approximately equal to the resistance of the bead. The bead becomes capacitive as the frequency increases.

### DC Bias

As the DC current through the ferrite bead increases, the magnetic core dives further into saturation, and the permeability of the material drops since the magnetic flux through the material is slowly reaching a limit where it cannot be increased any further. Thus, the inductance starts dropping with increasing current, which drives the impedance to even lower values. This inductance drop alters the impedance characteristics of the bead, which affects two key frequency points: the resonance or peak impedance frequency and the crossover point frequency. Both points shift up to higher frequencies with increasing DC bias, as seen in figure 3 below, resulting in lower impedances at the frequencies where the peak impedance used to exist. The drop in impedance and frequency shift are important to consider when using a ferrite bead since lower impedance means that the noise signals that pass through the bead will be larger than what is anticipated.

For example, figure 3 below shows the shift in impedance curves with increasing DC bias. Notice that when 300mA DC bias is used, the impedance at 100MHz drops from 650 ohm down to approximately 110 ohm. This means that the noise at this frequency increases by a factor of 135.6 dBuV.

*Figure 3: Effects of DC bias on the impedance of the bead*

Ignoring the DC bias effects on ferrite beads during the design phase can lead to a hard-to-diagnose noise sources in systems where controllers switch between different states and draw more current from the power source. Examples include intensive processing, charging peripherals, data transmission and similar applications.

### RDC and Losses

Unlike decoupling capacitors, beads are used in series with the supply rail. Therefore, voltage drop occurs across the bead due to its inherent DC resistance (RDC), which is usually in the 100m ohm to 1000m ohm range. The higher the RDC, the larger the voltage drop across it. This can be problematic in systems where strict voltage tolerances are needed. A faulty condition can happen during the start-up transient state, where inrush current is drawn from the source to feed the capacitive load in the system. The high inrush current spike leads to a high voltage drop across the bead which can cause an undervoltage condition on power rails. The undervoltage condition can cause powering-up sequencing failures as different parts of the system power up. In addition, undervoltage conditions could occur in steady-state operation where the processors or controllers switch from a quiescent to an active state.

*Figure 4: Inrush current and powering-up sequence*

As more cores or peripherals are engaged, more current is required from the same source, which can lead to the same undervoltage condition. Therefore, having knowledge about the different current states in the system and the RDC of the beads is essential to avoiding unwanted scenarios. Moreover, caution must be followed since beads dissipate the voltage drop and noise in the form of heat.

### Temperature Dependence

As the current through the bead rises, the temperature of the bead increases, which can lead to unwanted effects on the electrical characteristics of the bead and thus reduce its effectiveness in reducing the EMI noise. At lower temperatures, the core's permeability typically rises, which increases the inductance of the bead. This can cause a change in the frequency characteristics of the bead. As the temperature increases, the core's permeability decreases - reducing its effectiveness. However, this usually happens at extreme temperatures beyond 400C, which is higher than the temperatures found in typical power electronics applications. In general, it is recommended to operate ferrite beads within their specified temperature range to ensure optimal performance.

## How to Choose a Ferrite Bead

Picking a ferrite bead for an application depends on multiple factors, such as the anticipated noise frequency range, noise amplitude, current levels and ambient temperature range. Different ferrite bead shapes, sizes and core materials provide different characteristics to choose from. A key parameter to account for is the rated current. As highlighted before, when the beads start to saturate the inductance falls from its nominal value causing the resonant frequency (Z-peak) to shift higher. This can lead to a condition where more noise is permitted to pass through if proper precautions are not taken.

*Figure 5: Frequency characteristics of AFBC-Q0603-601*

From Figure 5, the bead will be in the inductive region at lower frequencies up to the point where the reactance (X) curve crosses the resistance (R) curve, approximately 50MHz as shown in figure 5. This is called the crossover point. In this region, the bead becomes more resistive as the frequency increases. The impedance of the bead continues to rise until it peaks at the resonant frequency. From the graph above, the impedance (blue curve) peaks at 170MHz. This is where the impedance is purely composed of its resistive component and the bead is in its most lossy state. Beads should be chosen such that the anticipated noise frequencies in the system fall in the resistive range. At higher frequencies, the impedance rolls off and the bead enters the capacitive region.

Shown in Figure 5, the impedance of the AFBC-Q0603-601 device peaks between 100 and 300 MHz, making it a good fit for applications where noise or interference in this frequency range exists. The noise at these frequencies would experience higher impedance than those at lower frequencies. Generally, the impedance of the device should be as high as possible in the noise frequency band. Consequently, this can cause the impedance at lower frequencies to be higher as well and can affect the integrity of the signals operating at these lower frequencies. Therefore, a bead must be chosen carefully to not adversely affect signaling operation but have enough impedance at higher frequencies to ensure proper EMC compliance. Keep in mind that the impedance characteristics of the bead can change with different operating conditions, such as DC bias and temperature.

## Conclusion

Ferrite beads are passive components that are used to attenuate high-frequency EMI noise. They are designed to be lossy at frequencies where noise is expected and allow low-frequency signals of interest to pass through with minimal attenuation. Choosing a bead for an application requires careful consideration of the bead's frequency characteristics, current levels, ambient temperature, noise frequency, and amplitude.

## References

1. Unconventional2, CC BY-SA 4.0, via Wikimedia Commons
2. "How do ferrite beads work and how do you choose the right one?," Altium, 10-Jan-2023.
3. A. Limjoco and J. Eco, "Ferrite beads demystified," Analog Devices.
4. L. Hill, "All about surface-mount ferrites," EDN, 21-Aug-2008.
