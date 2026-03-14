---
source: "JLCPCB -- PCB Design Rules and Guidelines: Complete Best Practices"
url: "https://jlcpcb.com/blog/pcb-design-rules-best-practices"
format: "HTML"
method: "readability"
extracted: 2026-02-09
chars: 18246
---
A great schematic is just an idea. To turn it into a real, working product, you need to follow a robust set of **Printed Circuit Board Design Rules**. Ignoring these rules leads to costly respins, signal integrity (SI) failures, and boards that are physically impossible to build.

This guide is a technical resource for the entire design process. We'll cover the essential rules for schematics, layout, and manufacturing that every engineer and hobbyist needs to know for a successful design.

---

## **What Are PCB Design Rules**

**PCB design rules** are the "laws of physics" for your board. They are a set of constraints that define everything from trace widths to component spacing.

These mandatory rules are precisely what your fabrication house (e.g., JLCPCB) follows to manufacture and assemble your board. Disregarding them is the primary reason for project delays and manufacturing holds.

The rules fall into three main categories:

1. **Schematic Rules:** Ensuring your design is logical and electrically correct *before* layout.

2. **Layout Rules:** Translating the schematic into a physical layout that performs correctly.

3. **Manufacturing Rules (DFM/DFA):** Ensuring the board you designed can actually be built.

##

## **Schematic Design Rules for a Flawless Handoff**

It is not possible to produce a high-quality layout without a clean schematic/layout. It is essentially your blueprint, and errors here will be amplified later.

### **Key Schematic Practices: Clarity and Verification**

● **Group Circuits by Function:** Use hierarchical sheets (e.g., Power Supply, MCU Core, RF Section). This is going to make the layout process exceedingly easier.

● **Maintain a Clear Signal Path:** For optimal clarity, arrange symbols to illustrate a clear signal path, with inputs on the left and outputs on the right. This organization simplifies understanding the circuit's function.

● **Use Standard Symbols:** Ensure your components are from a trusted and verified PCB library. A symbol with an incorrect footprint is a common and frustrating error.

● **Label Nets Clearly:** Don't just use VCC. Use descriptive names like +5V\_DDR or +3V3\_RF. This is critical for assigning specific layout rules later.

● **Perform an Electrical Rule Check (ERC):** It's best to run your schematic’s ERC before moving into layout. It can detect logical errors, such as unconnected pins or shorted outputs. This is your first defensive step.

● **Annotate and Document:** Add notes identifying specific layout requirements, e.g., "Place C5 as close as possible to U1 pin 6" or "50-ohm impedance" for high-speed traces.

**Learn More:** [Creating High-Quality Schematic Diagram: A Professional and Simplified Workflow](https://jlcpcb.com/blog/creating-high-quality-schematic-diagram-a-professional-and-simplified-workflow)

## **PCB Layout Guidelines: Logic to Physical Reality**

This marks the transition from a logical netlist to a physical circuit of copper. This transition is governed by your EDA (Electronics Design Automation) tools, built-in [Design Rule Check (DRC).](https://jlcpcb.com/blog/how-to-run-a-design-rule-check-for-your-pcbs)

The layout stage is where the complexity rapidly increases, and if you need to verify or tune your design for performance and cost, [JLCPCB Layout Service](http://design.jlcpcb.com) offers that takes care of any 2-layer boards to complex high-density designs.

### **Initial Setup: Board Stackup and Component Placement**

● **Board Outline and Constraints:** Define your board's mechanical outline, incorporate mounting holes, and lock the location of critical parts (e.g., connectors).

● **Understanding PCB Board Layers (The Stackup):** Your layer stackup is a critical decision.

○ **2-Layer Boards:** 2-Layer Boards are the low-cost option for straightforward designs.

○ **4-Layer and Multilayer Boards:** 4-Layer Boards and Multilayer Boards are the default option for most modern designs. As they utilize dedicated inner planes for Ground (GND) and Power (VCC), they have stable reference planes for signals, enhance power integrity, and streamline routing.

| Layer | 4-Layer Stackup (1.6mm) | Purpose | 6-Layer Stackup (1.6mm) | Purpose |
| --- | --- | --- | --- | --- |
| L1 | Signal (Top) | Components & high-speed signals | Signal (Top) | Components & high-speed signals |
| L2 | GND (Plane) | Solid Ground reference, shielding | GND (Plane) | Solid Ground reference, shielding |
| L3 | VCC (Plane) | Power distribution | Signal (Internal) | Low-speed signals, impedance control |
| L4 | Signal (Bottom) | Lower-speed signals, routing | VCC (Plane) | Power distribution |
| L5 | --- | --- | GND (Plane) | Second Ground reference, shielding |
| L6 | --- | --- | Signal (Bottom) | Lower-speed signals, routing |

Comparison table of 4-layer and 6-layer PCB stackups showing layer type, material, and purpose.

### **Strategic Component Placement:**

● When designing a PCB, it's crucial to prioritize the placement of essential components such as connectors, microcontrollers, and power sources.

● Place similar components together to remain organized, for example, the entire power supply section.

● Keep analog, digital, and power sections physically separated to avoid interference.

Decoupling capacitors must be placed right next to the VCC/GND pins of every IC to ensure power integrity. This is an extremely important rule.

### **Routing Basics: Traces, Vias, and Planes**

● **Trace Width and Spacing (Clearance):**

○ **Trace Width:** It is determined by the current it needs to carry.

**Read:** [Track Width v/s Current Capacity: PCB Layout Tips for Power Routing](https://jlcpcb.com/blog/track-width-vs-current-capacity-pcb-layout-tips).

○ **Spacing:** Determined by the voltage difference between traces and the manufacturer's guidelines.

● **Copper Thickness (Weight):** For applications that require higher currents, you may select 2oz (70µm) or thicker copper, which allows much narrower traces for the same current, which saves space. Internal traces will need to be wider than traces that are external for the same current due to heat dissipation in internal layers being less efficient.

| Current | External, 1oz Copper | Internal, 1oz Copper | External, 2oz Copper | Internal, 2oz Copper |
| --- | --- | --- | --- | --- |
| 0.5A | ~5 mil | ~10 mil | ~2 mil | ~5 mil |
| 1.0A | ~10 mil | ~20 mil | ~5 mil | ~12 mil |
| 2.0A | ~30 mil | ~50 mil | ~12 mil | ~30 mil |
| 3.0A | ~50 mil | ~85 mil | ~20 mil | ~45 mil |
| 5.0A | ~100 mil | ~175 mil | ~40 mil | ~90 mil |

Reference table for PCB trace width based on current capacity for internal and external layers**(Approx. 10°C Rise)**.

● **Routing Practices:** Keep traces short and direct. Use 45° angles for turns; **don’t** use 90° angles.

● **Vias:** These are plated holes that connect layers. **Minimize their use on high-speed traces**, as each via adds inductance.

● **Power and Ground Planes:** On a 4+ layer board, your ground plane should be a solid, continuous sheet. **Never** route a high-speed trace over a "split" in your ground plane. This forces the signal's return current to take a massive loop, creating EMI and signal integrity failure.

**Learn More:**

● [The Ultimate Guide to PCB Layout Design](https://jlcpcb.com/blog/guide-to-pcb-layout-design)

● [Comprehensive Layer Stack-Up Design for High-Speed Controlled Impedance PCBs](https://jlcpcb.com/blog/comprehensive-layer-stack-up-design-for-high-speed-controlled-impedance-pcbs)

## **Advanced Layout Rules for High-Performance Design**

This section addresses important rules that apply to modern high-speed designs in which traces are transmission lines.

● [**Signal Integrity**](https://jlcpcb.com/blog/signal-integrity-fundamentals-in-pcb-layout)**(SI) in PCB Layout:** Signal integrity (SI) describes the reception of a signal exactly as it was transmitted. However, high-speed signals often experience degradation, ringing, overshoot, and errors upon reception.

○ **Key Rules:** Keep all traces for high-speed signals short. Route them on top of a solid, unbroken ground plane (the return path). Keep a large distance between every two parallel traces to prevent near-end crosstalk (electromagnetic coupling). The **rule of thumb is the "3W" rule**: The distance from one trace to another must be at least three times the width of one trace.

● [**Impedance Matching**](https://jlcpcb.com/blog/understanding-impedance-matching-for-high-speed-pcb-designs) **in PCB Layout:** For high-frequency signals (e.g., USB, Ethernet, RF, DDR memory), the trace itself has a characteristic impedance. To ensure maximum power transfer and prevent signal reflections (which cause data corruption), the trace's impedance must match the source and load impedance (typically 50Ω for single-ended or **90-100Ω** for differential pairs).

○ **How it's controlled:** This impedance is precisely determined by the trace width, the dielectric (insulating) material of the PCB, and the distance from the trace to its reference ground plane. This is why your layer stackup **(Table 1)** is so critical.

● [**Differential Pairs**](https://jlcpcb.com/blog/pcb-basics-differential-pair-in-pcb-design)**:** A differential pair consists of two traces, such as D+ and D-, that carry equal and opposite signals. This configuration is commonly employed in high-speed communication, like USB, due to its excellent resistance to common-mode noise.

○ **Key Routing Rules:** To ensure signals arrive simultaneously at the receiver, the two traces must be routed parallel, maintaining an identical length (length-matched). It's crucial to keep a consistent, small gap between them and route them symmetrically. Vias should be avoided if possible; if necessary, use them symmetrically on both traces.

For precise impedance control, consider using [JLCPCB's free online impedance calculator tool](https://jlcpcb.com/pcb-impedance-calculator), which can help you design your PCB traces to meet specific impedance requirements.

● **Power Integrity(PI) in PCB Layout:** Power integrity (PI) is important for supplying stable, clean power (smooth DC voltage) to all components. Modern integrated circuits (ICs) switch very quickly and demand current immediately. Poor PI can lead to voltage droop, noise, or ultimately system failure.

○ **Key rules:** To achieve the best possible power distribution with a low-inductance power path, use a **solid power plane** (on 4+ layer boards), and provide [**decoupling (****bypass****) capacitors**](https://jlcpcb.com/blog/the-definitive-guide-to-bypass-capacitor-in-pcb-layout) for each IC with bulk capacitance (1-10uF) for low-frequency power variations, and smaller decoupling capacitors (0.1uF, 0.01uF) at high frequencies that are placed as close as possible to the power pins on each IC.

● **EMI in PCB Layout:** Good EMI management ensures your board neither generates excessive Electromagnetic Interference (EMI) that will disturb other devices (Electromagnetic Compatibility - EMC) nor is exposed to EMI from other devices.

**Learn more:** <https://jlcpcb.com/blog/emivsemc>

○ **Key rules:**

● **Ground Plane:** A solid ground plane serves as the most effective shield.

● **High-Frequency Traces:** Keep high-frequency traces (e.g., clocks) short, minimizing their current loops (trace + return path).

● **Filtering:** Implement filtering components like ferrite beads on power lines and I/O signals.

● **Shielding:** For sensitive RF sections, utilize metal shielding cans when necessary.

**Learn more:** [How to Tackle EMI\_EMC and Signal Integrity Issues in HF PCB Design](https://jlcpcb.com/blog/emi-emc-and-signal-integrity-issues-in-hf-pcb).

## **DFM and DFA: The Rules for Getting Your Board Built**

Even designs that clear all electrical checks can present manufacturing challenges. This is precisely why [Design for Manufacturability (DFM) and Design for Assembly (DFA)](https://jlcpcb.com/blog/design-for-manufacturing-and-assembly) are crucial.

### **DFM in PCB Layout (Design for Manufacturability)**

Rules of [DFM (Design for Manufacturability)](https://jlcpcb.com/blog/design-for-manufacturing-a-comprehensive-guide-for-optimizing-production) are very important to ensure the reliable handling of a bare board. These are rules that the manufacturer provides, and they are very strict. The significant rules are:

● **Minimum Trace/Space:** Minimum size of the width of the trace and gap that your manufacturer can produce consistently (e.g., 5mil/5mil).

● **Minimum Drill Size & Annular Ring:** The **annular ring** is the copper remaining around a drill hole. If this ring is too small, the via may fail.

● **Solder Mask Clearance:** A small clearance is required to allow the pad not to be covered by the solder mask.

For checking your design before ordering, you can use [JLCPCB's free DFM tool](https://jlcdfm.com/).

### **DFA in PCB Layout (Design for Assembly)**

It is important to follow **Design for Assembly (DFA) rules** to ensure that components are soldered to the board for PCBA assembly. The most important considerations to keep in mind are:

● **Component Spacing:** Enough space must be maintained for pick-and-place machines.

● **Footprint Accuracy:** You should always verify PCB library footprints with the relevant component's datasheet.

● **Fiducial Marks:** Fiducial marks are optical markings printed on your boards to assist automated assembly machines during the positional alignment process.

**Component Orientation:** Polarized components (e.g., diodes and LEDs) should be oriented in the same direction as much as possible to simplify assembly

### **Conclusion**

Following this guide, we've traced the path from a logical **Schematic** to a high-performance **Layout** and finally to a board that is ready for manufacturing via **DFM/DFA**. Mastering these **printed circuit board design rules** is the most critical skill for turning your concepts into reliable, real-world hardware.

Many projects encounter delays during the layout process, particularly with complex boards. The challenges of managing high-speed signals, controlling impedance, and arranging dense component placement can be substantial. To expedite your project and guarantee an optimized, manufacturable design, consider utilizing **JLCPCB's professional assistance**.

Our expert layout service transforms your schematic into a production-ready board, handling all the complex details for you. Our "review first, pay later" system offers reliable protection and peace of mind.

[**JLCPCB Layout starts from just $20 now! Register and claim your $360 new-user coupon.** **JLCPCB Layout rate is as low as $0.45 per pin**](https://design.jlcpcb.com/)**!**

## **FAQs about PCB design rules**

### **Q1. What's the difference between PCB design rules and PCB design standards?**

Design standards (like from IPC, ISO) are industry-wide guidelines. Design rules are the specific, measurable constraints you enter into your EDA software, often based on your manufacturer's specific capabilities. For a better understanding, explore [JLCPCB's capabilities](https://jlcpcb.com/capabilities/pcb-capabilities). [**JLCPCB's layout service**](http://design.jlcpcb.com) offers the advantage of ensuring your design adheres to their manufacturing capabilities from the outset, potentially reducing design iterations and speeding up the production process.

### **Q2. What are the most common PCB layout mistakes for beginners?**

The most common errors include:

● Forgetting or placing decoupling capacitors too far from ICs.

● Creating a "broken" or "sliced" ground plane which destroys signal return paths.

● Using incorrect component footprints from an unverified PCB library.

● Violating the manufacturer's DFM rules (e.g., traces too thin or too close).

### **Q3. How do I set up design rules in my software (e.g., EasyEDA, KiCad, Altium, Eagle)?**

If you are using [**EasyEDA**](https://easyeda.com/), the design rules for JLCPCB are built in and can be selected from a simple menu, which makes the process very straightforward. For *other* software like KiCad, Altium, or Eagle, the best practice is to go to your [JLCPCB’s Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) page. There, you will find the definitive values for minimum trace width, spacing, drill size, and other DFM rules. You must then manually enter these values into the Design Rule Checker (DRC) settings to ensure your design matches what your manufacturer can actually produce.

### **Q4. Why shouldn't I use 90-degree (right-angle) traces?**

There are two main reasons:

1. In high-speed designs, the sharp corner causes an impedance discontinuity, which can reflect signals and harm signal integrity.

2. In older manufacturing processes, acid could get trapped in the sharp inner corner ("acid traps"), over-etching the trace and causing a failure.

### **Q5. What is the difference between a thru-hole, blind, and buried via?**

● **Thru-Hole Via:** This is the standard via. It's a hole drilled from the top layer all the way through to the bottom layer.

● **Blind Via:** This via connects an *outer* layer (Top or Bottom) to one or more *internal* layers, but does not go all the way through the board.

● **Buried Via:** This via *only* connects internal layers. It is not visible from the outside of the board. Blind and buried vias save space on dense boards but add significant cost to manufacturing.

### **Q6. What is crosstalk, and how do I prevent it?**

Crosstalk is the unwanted transfer of energy (noise) between parallel traces via electromagnetic coupling. A fast-switching signal on one trace can induce a "ghost" signal on a neighboring trace, causing errors. You prevent it by increasing the spacing between traces (the "3W rule" is a good start) and by using a solid ground plane, which acts as a shield between layers.
