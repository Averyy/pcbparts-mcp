---
source: "Altium -- The Ultimate Introduction to High-Speed Signal Integrity"
url: "https://resources.altium.com/p/introduction-to-high-speed-signal-integrity-for-pcb-designers"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 8001
---
## Basics of Signal Integrity

Signal integrity refers to the quality and reliability of electrical signals as they travel through a PCB (Printed Circuit Board). In high-speed PCB design, maintaining signal integrity is critical because even minor signal distortions can lead to data corruption, communication errors, and overall system failure. Factors such as impedance mismatches, crosstalk, signal reflections, and power fluctuations can significantly impact signal integrity, necessitating careful design and analysis.

## Understanding Impedance in PCBs

Impedance, in the context of PCB design, is the resistance that an alternating current encounters as it moves through a circuit. This impedance is shaped by various factors, including the width and thickness of the traces, the type of dielectric material used between these traces, and the overall configuration of the PCB's layers. For high-speed PCB applications, maintaining a uniform impedance is critical to avoid signal reflections and to guarantee dependable data transmission.

To ensure impedance consistency in high-speed PCB designs, several strategic techniques are applied:

* **Controlled Impedance Traces:** Engineers design trace geometries—specifically their width and spacing—to achieve target impedance values. Advanced simulation tools are utilized to model and validate these impedance levels before production. For instance, a design requirement might be establishing a 50-ohm impedance for certain signal traces. Through simulations, the trace dimensions are fine-tuned to consistently meet this specification.
* **Differential Pairs:** For robust high-speed signal transmission, signals are often routed as differential pairs, which involve two complementary signals being transmitted simultaneously. This configuration not only stabilizes impedance but also helps mitigate noise. A common application is in USB 3.0 technologies, where differential pairs enhance signal integrity and reduce electromagnetic interference.
* **Material Selection:** The choice of substrate material can significantly affect impedance stability. Selecting materials with consistent dielectric properties ensures that the impedance does not vary across the PCB. For example, standard FR4 material, known for its stable dielectric constant, is often chosen to maintain impedance uniformity throughout the circuit board (for traces that are not too long).

PCB stackup editor in Altium Designer with an integrated electromagnetic field solver

## Reflection and Signal Termination

Signal reflection occurs when a signal encounters an impedance mismatch along its path, causing part of the signal to reflect back toward the source. This reflection can distort the signal, cause data errors, and reduce overall signal integrity. Common causes of impedance mismatches include abrupt changes in trace width, vias, and connectors.

Termination techniques are used to match the impedance of the transmission line with the load, thus minimizing reflections:

* **Series Termination:** This involves placing a resistor in series with the signal near the source. It is simple and effective for short traces. For example, a series resistor of 33 ohms might be used in a high-speed memory interface to match the trace impedance and prevent reflections.
* **Parallel Termination:** A resistor is placed at the end of the trace to match the impedance of the line. This method is commonly used for longer traces and differential pairs. For instance, in long transmission lines within a PCB, a 50-ohm parallel resistor might terminate the trace and eliminate reflections.
* **AC Termination:** This technique combines resistive and capacitive elements to match impedance over various frequencies. For example, an AC termination might use a 50-ohm resistor in parallel with a capacitor to terminate high-speed clock signals, providing broad frequency range matching (with the cutoff frequency (fc) where the impedance of the termination network matches the impedance of the transmission line is given by the following formula: fc=1/2πRC)

Altium Designer Signal Integrity tool enable designers to specify appropriate trace termination

## PCB Material Selection for High-Speed Designs

The dielectric constant (Dk) and loss tangent (Df) of PCB materials are critical factors in maintaining signal integrity. The Dk influences the speed at which signals propagate, while the Df affects signal loss over distance. For high-speed designs, materials with low Dk and low Df are preferred to minimize signal distortion and loss.

Key material properties that affect signal integrity include:

* **Thermal Stability:** Materials with high thermal stability ensure consistent performance under varying temperatures. For example, High-Tg FR4 materials are often used in high-speed designs to ensure stable performance in environments with fluctuating temperatures.
* **Low Moisture Absorption:** Materials that absorb less moisture maintain consistent dielectric properties, crucial for high-speed signals. For instance, materials like Rogers 3003, which have low moisture absorption, are used in high-speed designs to ensure signal integrity is maintained even in humid environments.
* **Mechanical Strength:** Robust materials withstand mechanical stresses during manufacturing and operation, preserving signal paths. Polyimide is an example, and it is often chosen for flexible PCBs due to its excellent mechanical strength and stability.

PCB Material selection in Altium Designer’s advanced Layer Stack Manager

## Power Integrity and Its Impact on Signal Integrity

Power integrity refers to the stable delivery of power to all components on a PCB. Inadequate power integrity can lead to voltage fluctuations, which in turn cause signal integrity problems like jitter, noise, and timing errors. Maintaining robust power integrity is crucial for ensuring overall signal integrity in high-speed designs.

Techniques for Ensuring Power Integrity:

* **Decoupling Capacitors:** These capacitors, placed close to the power pins of ICs, filter out noise and provide a stable power supply. For instance, a 0.1 µF decoupling capacitor placed near the power pin of a high-speed FPGA can filter out high-frequency noise and ensure a stable voltage supply.
* **Power Planes:** Dedicated power planes reduce impedance and provide a stable voltage reference for high-speed signals. For example, a multi-layer PCB might include separate power and ground planes to reduce impedance and ensure consistent power delivery to high-speed components.
* **Proper Grounding:** Ensuring a low-impedance path for return currents reduces noise and improves signal integrity. A continuous ground plane beneath signal layers can provide a low-impedance return path, reducing noise and enhancing signal integrity.

Power Analyzer By Keysight in Altium Designer

## Conclusion

Maintaining high-speed signal integrity in PCB design involves mastering impedance control, signal reflection, material selection, and power integrity. These techniques enable engineers to create reliable high-speed PCBs that ensure accurate data transmission and robust system performance. With careful planning, simulation, and manufacturer collaboration, designers can address high-speed PCB challenges effectively.

Altium Designer's upcoming **Signal Analyzer extension from Keysight** offers advanced analysis tools to help resolve signal integrity issues, providing valuable insights for designing high-speed PCBs with confidence and precision. If you want to know more about this feature, check out our introductory video [here](https://youtu.be/PXR_q95hurM "Achieve Perfect Signal Integrity: Introducing SI Analyzer by Keysight").
