---
source: "LearnEMC -- PCB Decoupling Guidelines (4 sub-pages combined)"
url: "https://learnemc.com/circuit-board-decoupling-information"
format: "HTML"
method: "fetchaller"
extracted: 2026-02-14
chars: 20095
---

# LearnEMC -- PCB Decoupling Guidelines

This document combines four sub-pages from LearnEMC's circuit board decoupling information series by Dr. Todd Hubing.

---

## Part 1: Estimating the Connection Inductance of a Decoupling Capacitor

Source: https://learnemc.com/estimating-connection-inductance

What many people refer to as the *equivalent series inductance* (ESL) of a capacitor is the inductance of the loop formed by current that flows in one terminal and out the other terminal. For SMT capacitors, it is more accurate to call this the *connection inductance*, since it depends much more on the geometry of the connection than on the internal construction of the capacitor. Connection inductance is the most important factor affecting a decoupling capacitor's ability to supply current at high frequencies. By estimating the connection inductance, the effective bandwidth of a decoupling strategy can be determined. The following outlines a method by which the connection inductance of a variety of decoupling capacitors can be estimated.

### Step 1: Identify the Loop

The first step in estimating the inductance of a decoupling capacitor is to identify the decoupling current loop. Two cases will be considered, decoupling capacitors on boards with power routed on traces, and decoupling capacitors on boards with power and return planes.

#### A. Geometries where power is routed on traces

The current loop will consist of the path between the decoupling capacitor and the device that draws charge from the capacitor. The current path forms a loop through the capacitor, along traces, through the IC, and back.

#### B. Decoupling capacitors connected to power planes

The current loop in this configuration will start at the decoupling capacitor, go through a via to one of the power planes, then from one power plane to the other, and finally through a via back to the capacitor. The impedance of the path between the power and return planes, Zboard, is not normally considered to be part of the connection inductance. Zboard can be calculated independent of the inductance of the portion of the loop above the planes. The impedance of the connection to the planes is then given by, Zconn = jωL + Zboard, where L is the inductance of the current path above the power planes.

### Step 2: Identify an Equivalent Geometry

To estimate the inductance for decoupling capacitors, the inductance of an equivalent geometry will be used. This simplification will allow us to use simple closed-form expressions to calculate the inductance.

#### A. Decoupling capacitors where power is routed on traces

**Rectangular Loop:** If the decoupling current loop is short (w < 5h), then use the closed-form expression for a rectangular loop to calculate the inductance.

**Long Rectangular Loop (w > 5h):** If the decoupling current loop is long (w > 5h), then use the expression for the inductance per unit length of two wires and multiply by the length of the loop (w) to calculate the inductance.

#### B. Decoupling capacitors connected to power planes

**Rectangular Loop above a Plane:** If the decoupling loop is short (w < 5h), use the closed-form expression for a rectangular loop with the parameter 'h' equal to 2h1, and then divide the calculated inductance in half. This inductance will be the inductance Labove.

**Long Rectangular Loop above a Plane (w > 5h):** If the decoupling current loop is long (w > 5h), use the expression for the inductance per unit length of a wire above a ground plane and multiply by the length of the loop (w). This inductance will be the inductance Labove.

### Step 3: Estimating the parameters of the closed-form inductance calculations

#### A. Estimating loop width 'w'

The loop width 'w' is the distance over which the current follows through the capacitor. This depends on the pad/via geometry of the capacitor mounting.

#### B. Estimating loop height 'h'

The height of the loop 'h' for a capacitor attached to power planes would be approximately half the height of the decoupling capacitor plus the distance between the capacitor and the closest power plane.

#### C. Estimating wire radius 'a'

The equivalent wire radius of a decoupling capacitor or flat trace can be estimated as 1/4th the width of the capacitor package or trace. Most connections consist of vias, traces, pads and capacitor packages that have different equivalent wire radii. A worst-case estimate of the connection inductance is obtained by using the smallest equivalent radius.

### Example 1: PCB Without Power Planes

Calculate the connection inductance for the capacitor connected to a device through traces. The traces are 1 mm wide.

**Solution:** The connection inductance can be approximated with the use of the rectangular loop equation. The length and width of the rectangle itself is estimated from the current path. The length of the equivalent rectangular loop is estimated to be 8 mm plus half of the length of the triangular portion of the current loop (22 mm / 2 = 11 mm). The equivalent radius of the wire, a, is 1/4th of the trace width.

**Ans. Lconn = 29 nH ≈ 30 nH**

### Example 2: Decoupling Capacitors Connected to Power Planes

Calculate the connection inductance between a capacitor and a device assuming both are connected to power and return planes. The via diameters are 2 mm and the DIP package and capacitor are approximately 3 mm above the surface of the power and return plane pair. Neglect the impedance through the power planes.

**Solution:**

*Inductance of the capacitor connection:*

To calculate the inductance of the decoupling capacitor, Lcap, the formula for the inductance of a 'Rectangular loop above a plane' will be used. The length and width of the equivalent loop for the decoupling capacitor are 10 mm and 3 mm respectively. The equivalent radius of the loop will be the 1 mm radius of the vias.

**Lcap = 3.6 nH ≈ 4 nH**

*Inductance of the DIP package connection:*

The inductance of the DIP package connection to the power planes, LDIP, will be calculated with the 'long rectangular loop above a plane' formula. The length of the loop will be 30 mm, the height of the loop will be 3 mm, and the equivalent radius will be approximated as 0.1 mm.

**LDIP = 24.6 nH ≈ 25 nH**

**Lconn = Lcap + LDIP = 28.2 nH ≈ 28 nH**

### Example 3: The Inductance of a Decoupling Capacitor Loop

Several decoupling capacitor pads on a PCB were measured. The distance between the top layer and the power/return plane pair was 0.02". The inductance of the following pad designs was measured with a network analyzer:

| Case | L (nH) |
| --- | --- |
| A | 0.61 |
| B | 1.32 |
| C | 2.00 |
| D | 7.11 |
| E | 15.7 |
| F | 10.3 |

**Inductance of Case C:**

*Method 1: Using the 'rectangular loop above a plane' algorithm*
w = 0.5", h1 = 0.02", h = 2h1, a = 0.025"
ANS: L = 3.1 nH ≈ 3 nH

*Method 2: Using the 'long rectangular loop above a plane' algorithm*
Length = 0.5", h = 0.02", a = 0.025"
ANS: L = 0.75 nH ≈ 1 nH

(Note: Method 2 ignores the inductance due to the portion of the magnetic flux wrapping the vias. This is a reasonable estimate of the inductance due to the flux wrapping the capacitor body only. Flux wrapping the capacitor body dominates in Case A.)

**Inductance of Case E:**

Method: Using the 'long rectangular loop above a plane' algorithm once for the traces routed to the via, and again for the pad and capacitor package portion of the loop.

*Contribution to loop inductance from the traces:*
Length = 1.0", h = 0.02", a = w/4 = 0.002"
ANS: Lt = 15.24 nH ≈ 15 nH

*Contribution to the loop inductance from the pad and capacitor package:*
Length = 0.5", h = 0.02", a = w/4 = 0.02"
ANS: Lp/c = 0.76 nH ≈ 1 nH

**Total loop inductance: Lt + Lp/c ≈ 16 nH**

---

## Part 2: Power Bus Decoupling for PCBs without Power Planes

Source: https://learnemc.com/decoupling-for-boards-without-power-planes

**Applicable to:** 1- or 2-sided boards or multi-layer boards that do not employ planes for power distribution.

### General Guidelines

- Provide at least one "local" decoupling capacitor for each active device and at least one larger "bulk" decoupling capacitor for each voltage distributed on the board.
- Local decoupling capacitors should be connected between the voltage and ground pins of the active device. The area of the loop formed by the capacitor/device connection should be minimized.
- Local decoupling capacitors typically have nominal values of 0.001, 0.01 or 0.047 microfarads. Some active devices may require several local decoupling capacitors in order to respond to a sudden demand for current.
- Bulk decoupling capacitors should be located near the point where a voltage comes on to the board. If the voltage is generated on the board, the bulk decoupling should be near the location where it is generated.
- Bulk decoupling capacitors should be sized to meet the transient current needs of the entire board. Typically, bulk decoupling capacitors have values equal to 1 - 10 times the sum of the values of the local decoupling capacitors connected to the same bus.
- As a general rule, two local decoupling capacitors with the same nominal value are better than one capacitor with twice the nominal value. Two capacitors have a lower overall connection inductance [1] and provide better high-frequency filtering to the rest of the power bus [2].

### References

[1] C. R. Paul, "Effectiveness of Multiple Decoupling Capacitors," *IEEE Trans. on Electromagnetic Compatibility*, vol. 34, no. 2, May 1992, pp. 130-133.

[2] T. Zeeff, T. Hubing, T. Van Doren and D. Pommerenke, "Analysis of Simple Two-Capacitor Low-Pass Filters," *IEEE Trans. on Electromagnetic Compatibility*, vol. 45, no. 4, Nov. 2003.

---

## Part 3: Power Bus Decoupling for PCBs with Closely Spaced Power Distribution Planes

Source: https://learnemc.com/decoupling-for-boards-with-closely-spaces-power-planes

**Applicable to:** Multi-layer boards with power distribution planes spaced ~0.5 mm or less apart.

### General Guidelines

- Multi-layer boards generally employ two types of decoupling capacitor. Large-valued "bulk" capacitors help to minimize the impedance of the power bus at low frequencies (e.g. below a few hundred kHz). Smaller "high-frequency" capacitors reduce the power bus impedance at higher frequencies (e.g. up to ~100 MHz on boards with closely spaced planes). At even higher frequencies, the power bus impedance is determined by the planes themselves.
- Boards typically have one or two large electrolytic bulk decoupling capacitors or they may employ half a dozen or more bulk decoupling capacitors in smaller packages. Either approach is effective and this decision is normally made based on size, cost and board-area constraints.
- The total value of the bulk decoupling is determined by the transient power requirements of the active devices on the board. Generally, the total bulk decoupling capacitance is 1 - 10 times the total high-frequency decoupling capacitance connected to the power bus.
- The high-frequency capacitors are often called "local" decoupling capacitors, but this is a misnomer. When the power and ground planes are closely spaced, all capacitors mounted on the surface of the board are "global" (i.e. they respond to changes in the voltage on the power planes due to all active device switching and do not favor one device over another). The inductance of their connection to the power distribution planes is far more critical than their nominal capacitance. Generally, smaller package sizes can be connected to the planes with a lower inductance than larger packages. Therefore, high-frequency decoupling capacitors should generally be as small (physically) as possible. The vias connecting these capacitors to the planes should be located as close to one another as possible.
- Choose the largest nominal capacitance available in a given package size. However, do not use capacitors that have a nominal capacitance less than the parallel plate capacitance that naturally occurs between the power and power-return planes [C = εA/d]. A board made with FR-4 material containing one pair of power distribution planes spaced 0.25 mm (10 mils) apart has an interplane capacitance of approximately 16 pF/cm².
- The location of the decoupling capacitors is not critical because their performance is dominated by the inductance of their connection to the planes. At the frequencies where they are effective, they can be located anywhere within the general vicinity of the active devices [1].
- The maximum frequency at which the capacitors will be effective is proportional to the square root of the number of capacitors [1]. Therefore, high-speed circuit boards often have many high-frequency decoupling capacitors for every active device on the board.
- Connection inductance is determined by the loop area formed by the capacitor body, mounting pads, traces and vias (See Part 1: Estimating the Connection Inductance of a Decoupling Capacitor).

### To minimize connection inductance:

- Never use traces! Locate the vias adjacent to the mounting pads and near each other.
- If there is no room for the via adjacent to the pad, then move the whole capacitor. Capacitor location is not so important, but connection inductance is critical.
- Four vias (instead of two) can cut the connection inductance nearly in half when the via diameter is small relative to the mounting pad width.
- Mount all of the high-frequency decoupling capacitors on the face of the board nearest to the planes. Connection inductance is nearly proportional to the distance from the planes.
- Do not let high-frequency decoupling capacitors share a via with an active device.

### References

[1] T. H. Hubing, J. L. Drewniak, T. P. Van Doren, and D. Hockanson, "Power bus decoupling on multilayer printed circuit boards," *IEEE Trans. on Electromagnetic Compatibility*, vol. 37, no. 2, May 1995, pp. 155-166.

[2] M. Xu, T. Hubing, J. Chen, T. Van Doren, J. Drewniak and R. DuBroff, "Power-bus decoupling with embedded capacitance in printed circuit board design," *IEEE Trans. on Electromagnetic Compatibility*, vol. 45, no. 1, Feb. 2003, pp. 22-30.

---

## Part 4: Power Bus Decoupling for PCBs with Widely Spaced Power Distribution Planes

Source: https://learnemc.com/decoupling-for-boards-with-widely-spaced-planes

**Applicable to:** Multi-layer boards with power distribution planes spaced more than 0.5 mm apart.

### Introduction

- In boards with widely-spaced power distribution planes, the inductance due to the loop area between the planes cannot be neglected. In fact, this inductance can be used to enhance the board's power bus decoupling.
- Local decoupling capacitors on boards with widely spaced planes can effectively reduce noise on the power bus at frequencies up to several GHz if they are mounted properly.
- The mutual inductance between closely spaced vias can force current to be drawn from a nearby decoupling capacitor before it is drawn from the power distribution planes [1-3].
- In order to take advantage of this phenomenon, it is important that the connection inductance of the local decoupling capacitors is minimized. It is also important to locate these capacitors very close to the device being decoupled.

### General Guidelines

- Multi-layer boards generally employ two types of decoupling capacitor. Large-valued "bulk" capacitors help to minimize the impedance of the power bus at low frequencies (e.g. below a few hundred kHz). These are "global" decoupling capacitors that respond to the current needs of all active devices on the board. Smaller "high-frequency" capacitors reduce the power bus impedance at higher frequencies. When properly mounted, these are "local" decoupling capacitors that primarily provide current to one active device.
- Boards typically have one or two large electrolytic bulk decoupling capacitors or they may employ half a dozen or more bulk decoupling capacitors in smaller packages. Either approach is effective and this decision is normally made based on size, cost and board-area constraints.
- The total value of the bulk decoupling is determined by the transient power requirements of the active devices on the board. Generally, the total bulk decoupling capacitance is 1 - 10 times the total high-frequency decoupling capacitance connected to the power bus.
- Local decoupling capacitors are intended to be effective at higher frequencies. The inductance of their connection to the power distribution planes is far more critical than their nominal capacitance. Generally, smaller package sizes can be connected to the planes with a lower inductance than larger packages. Therefore, local decoupling capacitors should generally be as small (physically) as possible.
- Choose the largest nominal capacitance available in a given package size. Nominal capacitance values are not nearly as critical as connection inductance. Typically, local decoupling capacitors on boards with widely spaced planes have a nominal value of about 0.01 microfarads.
- The location of the local decoupling capacitors is critical. Local decoupling capacitors should be located as close as possible to the power or ground pins of the active device they are decoupling. To determine near which pin to locate the decoupling capacitor (e.g. Vcc, Vss, Vdd, GND), first determine which power distribution plane is furthest from the active device. Local decoupling should be provided near the pins that connect to the most distant plane. For example, if the components are above Layer 1 on a 4-layer board and Layers 2 and 3 are Vcc and GND respectively, then the decoupling capacitors should be located near the GND pins of the active device. If there are any active devices below Layer 4 on this board, then decoupling for these devices should be located next to the Vcc pins.
- Orient the local decoupling capacitor so that the pin connected to the most distant plane is nearest the active device's pin connecting to the most distant plane. For example, if the active device is above Layer 1, and the decoupling capacitor is below Layer 4, then the Vcc pin of the decoupling capacitor should be located near the GND pin of the active device. Decoupling capacitors should never share a via with an active device when they are located on opposite sides of the board.
- If the decoupling capacitor can be located near enough to the active device to share the same via, this is optimal. However under no circumstances should a trace be used between the decoupling capacitor mounting pads and the vias. Decoupling capacitors should have vias located in or adjacent to the mounting pads to minimize their connection inductance.

### To minimize connection inductance:

- Never use traces on decoupling capacitors! Locate the via adjacent to the mounting pad.
- Locate the two capacitor vias as close together as possible.
- Mount all of the local decoupling capacitors on the face of the board closest to the planes. Connection inductance is nearly proportional to the distance from the planes.

### References

[1] T. H. Hubing, T. P. Van Doren, F. Sha, J. L. Drewniak, and M. Wilhelm, "An Experimental Investigation of 4-Layer Printed Circuit Board Decoupling," *Proceedings of the 1995 IEEE International Symposium on Electromagnetic Compatibility*, Atlanta, GA, August 1995, pp. 308-312.

[2] J. Fan, J. Drewniak, J. Knighten, N. Smith, A. Orlandi, T. Van Doren, T. Hubing and R. DuBroff, "Quantifying SMT Decoupling Capacitor Placement in DC Power-Bus Design for Multilayer PCBs," *IEEE Trans. on Electromagnetic Compatibility*, vol. EMC-43, no. 4, November 2001, pp. 588-599.

[3] J. Fan, W. Cui, J. Drewniak, T. Van Doren, J. Knighten, "Estimating the Noise Mitigation Effect of Local Decoupling in Printed Circuit Boards," *IEEE Trans. on Advanced Packaging*, vol. 25, no. 2, May 2002, pp. 154-165.
